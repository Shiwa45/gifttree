from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Cart, CartItem
from apps.products.models import Product, ProductVariant
from decimal import Decimal
import json


@login_required
def cart_view(request):
    """Display cart contents"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product', 'variant').all()
    
    # Calculate totals
    cart_subtotal = sum(item.total_price for item in cart_items)
    cart_total = cart_subtotal  # Add delivery charges if needed
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'cart_total': cart_total,
        'recommended_products': Product.objects.filter(
            is_active=True, 
            is_featured=True
        ).exclude(
            id__in=[item.product.id for item in cart_items]
        )[:4]
    }
    return render(request, 'cart/cart.html', context)


@require_POST
@login_required
def add_to_cart(request):
    """Add product to cart via Ajax"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        quantity = int(data.get('quantity', 1))
        
        # Validate product
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Handle variant if provided
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
        
        # Check if item already in cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not item_created:
            # Update quantity if item exists
            cart_item.quantity += quantity
            cart_item.save()
        
        # Calculate cart totals
        cart_count = cart.total_items
        cart_total = float(cart.total_price)
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart',
            'cart_count': cart_count,
            'cart_total': cart_total,
            'item': {
                'id': cart_item.id,
                'name': product.name,
                'quantity': cart_item.quantity,
                'price': float(cart_item.unit_price),
                'total': float(cart_item.total_price)
            }
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Product not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_POST
@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        
        cart_item = get_object_or_404(
            CartItem, 
            id=item_id, 
            cart__user=request.user
        )
        
        if quantity <= 0:
            cart_item.delete()
            message = 'Item removed from cart'
        else:
            cart_item.quantity = quantity
            cart_item.save()
            message = 'Cart updated'
        
        cart = cart_item.cart if quantity > 0 else Cart.objects.get(user=request.user)
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_count': cart.total_items,
            'cart_total': float(cart.total_price),
            'item_total': float(cart_item.total_price) if quantity > 0 else 0
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_POST
@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        cart_item = get_object_or_404(
            CartItem, 
            id=item_id, 
            cart__user=request.user
        )
        
        product_name = cart_item.product.name
        cart_item.delete()
        
        cart = Cart.objects.get(user=request.user)
        
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed from cart',
            'cart_count': cart.total_items,
            'cart_total': float(cart.total_price)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
def get_cart_data(request):
    """Get cart data for Ajax requests"""
    try:
        cart = Cart.objects.get(user=request.user)
        items = []
        
        for item in cart.items.select_related('product', 'variant').all():
            items.append({
                'id': item.id,
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'slug': item.product.slug,
                    'image': item.product.primary_image.image.url if item.product.primary_image else None
                },
                'variant': {
                    'id': item.variant.id,
                    'name': item.variant.name
                } if item.variant else None,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price)
            })
        
        return JsonResponse({
            'success': True,
            'cart': {
                'items': items,
                'total_items': cart.total_items,
                'total_price': float(cart.total_price)
            }
        })
        
    except Cart.DoesNotExist:
        return JsonResponse({
            'success': True,
            'cart': {
                'items': [],
                'total_items': 0,
                'total_price': 0
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_POST
@login_required
def clear_cart(request):
    """Clear all items from cart"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Cart cleared',
            'cart_count': 0,
            'cart_total': 0
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)