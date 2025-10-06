from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from .forms import AddToCartForm
from apps.products.models import Product, ProductVariant
from decimal import Decimal
import json


def cart_view(request):
    """Display cart contents - supports both logged-in users and session cart"""
    cart_items = []
    cart_subtotal = 0
    excluded_product_ids = []
    
    if request.user.is_authenticated:
        # Database cart for logged-in users
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.select_related('product', 'variant').all()
        cart_subtotal = sum(item.total_price for item in cart_items)
        excluded_product_ids = [item.product.id for item in cart_items]
    else:
        # Session cart for anonymous users
        session_cart = request.session.get('cart', {})
        
        for item_key, item_data in session_cart.items():
            try:
                product = Product.objects.get(id=item_data['product_id'], is_active=True)
                variant = None
                if item_data.get('variant_id'):
                    variant = ProductVariant.objects.get(id=item_data['variant_id'])
                
                # Create a cart item-like object for template compatibility
                class SessionCartItem:
                    def __init__(self, product, variant, quantity, custom_data):
                        self.product = product
                        self.variant = variant
                        self.quantity = quantity
                        self.custom_name = custom_data.get('custom_name')
                        self.custom_message = custom_data.get('custom_message')
                        self.custom_flavor = custom_data.get('custom_flavor')
                        self.custom_date = custom_data.get('custom_date')
                        self.unit_price = variant.final_price if variant else product.current_price
                        self.total_price = self.unit_price * quantity
                        self.id = item_key  # Use item_key as ID for session items
                
                cart_item = SessionCartItem(product, variant, item_data['quantity'], item_data)
                cart_items.append(cart_item)
                cart_subtotal += cart_item.total_price
                excluded_product_ids.append(product.id)
                
            except (Product.DoesNotExist, ProductVariant.DoesNotExist):
                # Remove invalid items from session
                del session_cart[item_key]
                request.session.modified = True
    
    cart_total = cart_subtotal  # Add delivery charges if needed
    
    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'cart_total': cart_total,
        'cart_count': len(cart_items),
        'recommended_products': Product.objects.filter(
            is_active=True, 
            is_featured=True
        ).exclude(id__in=excluded_product_ids)[:4]
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def add_to_cart(request):
    """Add product to cart - supports both form POST and AJAX"""

    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'

    # Check if this is a "buy now" action
    action = request.POST.get('action', 'add')

    # Parse data from either JSON or POST
    if is_ajax and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    else:
        data = request.POST

    # Create form with the data
    form = AddToCartForm(data)

    if not form.is_valid():
        error_msg = ' '.join([f"{k}: {v[0]}" for k, v in form.errors.items()])
        if is_ajax:
            return JsonResponse({'success': False, 'message': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))

    # Get cleaned data
    product_id = form.cleaned_data['product_id']
    variant_id = form.cleaned_data.get('variant_id')
    quantity = form.cleaned_data['quantity']
    custom_name = form.cleaned_data.get('custom_name', '').strip()
    custom_message = form.cleaned_data.get('custom_message', '').strip()
    custom_flavor = form.cleaned_data.get('custom_flavor', '').strip()
    custom_date = form.cleaned_data.get('custom_date')

    # Get product and variant
    product = get_object_or_404(Product, id=product_id, is_active=True)
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

    # Add to cart logic
    try:
        if request.user.is_authenticated:
            # Database cart for logged-in users
            cart, created = Cart.objects.get_or_create(user=request.user)

            # Create cart item
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                variant=variant,
                quantity=quantity,
                custom_name=custom_name if custom_name else None,
                custom_message=custom_message if custom_message else None,
                custom_flavor=custom_flavor if custom_flavor else None,
                custom_date=custom_date if custom_date else None
            )

            # Calculate cart totals
            cart_count = cart.total_items
            cart_total = float(cart.total_price)
        else:
            # Session cart for anonymous users
            if 'cart' not in request.session:
                request.session['cart'] = {}

            cart_session = request.session['cart']

            # Create unique key for cart item (including customizations)
            item_key = f"{product_id}"
            if variant_id:
                item_key += f"_v{variant_id}"
            if custom_name or custom_message or custom_flavor:
                item_key += f"_c{hash(f'{custom_name}{custom_message}{custom_flavor}')}"

            # Add to session cart
            if item_key in cart_session:
                cart_session[item_key]['quantity'] += quantity
            else:
                price = float(variant.final_price if variant else product.current_price)
                cart_session[item_key] = {
                    'product_id': product_id,
                    'variant_id': variant_id,
                    'quantity': quantity,
                    'price': price,
                    'custom_name': custom_name,
                    'custom_message': custom_message,
                    'custom_flavor': custom_flavor,
                    'custom_date': custom_date,
                    'name': product.name
                }

            request.session.modified = True

            # Calculate session cart totals
            cart_count = sum(item['quantity'] for item in cart_session.values())
            cart_total = sum(item['quantity'] * item['price'] for item in cart_session.values())

        success_message = f'{product.name} added to cart successfully!'

        # Return appropriate response
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': success_message,
                'cart_count': cart_count,
                'cart_total': cart_total,
                'item': {
                    'name': product.name,
                    'quantity': quantity,
                    'price': float(variant.final_price if variant else product.current_price),
                    'total': float((variant.final_price if variant else product.current_price) * quantity)
                }
            })
        else:
            # Regular form submission
            messages.success(request, success_message)

            # If "buy now" was clicked, redirect to cart, otherwise go back to product
            if action == 'buy_now':
                return redirect('cart:cart')
            else:
                return redirect(request.META.get('HTTP_REFERER', 'cart:cart'))

    except Exception as e:
        error_message = f'Error adding to cart: {str(e)}'
        if is_ajax:
            return JsonResponse({'success': False, 'message': error_message}, status=400)
        messages.error(request, error_message)
        return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))


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