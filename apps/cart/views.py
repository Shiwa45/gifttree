from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from apps.products.models import Product, ProductVariant, ProductAddOn


@login_required
def cart_view(request):
    """Display cart contents"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product', 'variant').prefetch_related('addons').all()
    
    # Get recommended products (products from same categories)
    if cart_items.exists():
        categories = [item.product.category for item in cart_items]
        recommended_products = Product.objects.filter(
            category__in=categories,
            is_active=True,
            stock_quantity__gt=0
        ).exclude(
            id__in=[item.product.id for item in cart_items]
        ).select_related('category').prefetch_related('images')[:6]
    else:
        # Show featured products if cart is empty
        recommended_products = Product.objects.filter(
            is_featured=True,
            is_active=True,
            stock_quantity__gt=0
        ).select_related('category').prefetch_related('images')[:6]
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'cart_subtotal': cart.total_price,
        'cart_total': cart.total_price,
        'recommended_products': recommended_products,
    }
    return render(request, 'cart/cart.html', context)


@login_required
def add_to_cart(request):
    """Add item to cart"""
    # Handle GET requests (from login redirect) - redirect to cart
    if request.method == 'GET':
        from django.contrib import messages
        messages.info(request, 'Please add items to your cart from the product page.')
        return redirect('cart:cart')
    
    # Handle POST requests (actual add to cart)
    if request.method != 'POST':
        from django.contrib import messages
        messages.error(request, 'Invalid request method.')
        return redirect('cart:cart')
    
    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))
    addon_ids = request.POST.getlist('addon_ids[]')  # Get list of addon IDs
    buy_now = request.POST.get('buy_now', '0')  # Check if it's a "Buy Now" action

    # Debug: Print all POST data
    print("\n" + "="*60)
    print("ADD TO CART REQUEST RECEIVED")
    print("="*60)
    print(f"Product ID: {product_id}")
    print(f"Variant ID: {variant_id}")
    print(f"Quantity: {quantity}")
    print(f"Buy Now: {buy_now}")
    print(f"Addon IDs received: {addon_ids}")
    print(f"Addon IDs type: {type(addon_ids)}")
    print(f"Number of addons: {len(addon_ids)}")
    print(f"Full POST data: {dict(request.POST)}")
    print("="*60 + "\n")

    try:
        product = Product.objects.get(id=product_id, is_active=True)
        variant = None

        if variant_id:
            variant = ProductVariant.objects.get(id=variant_id, product=product)

        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if item already exists in cart
        existing_item = None
        if variant:
            existing_item = cart.items.filter(product=product, variant=variant).first()
        else:
            existing_item = cart.items.filter(product=product, variant__isnull=True).first()

        if existing_item:
            # Update quantity if item exists
            existing_item.quantity += quantity
            existing_item.save()
            cart_item = existing_item
        else:
            # Create new cart item
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                variant=variant,
                quantity=quantity
            )

        # Add selected add-ons to the cart item
        if addon_ids:
            print(f"\n🎁 Processing {len(addon_ids)} addon IDs: {addon_ids}")
            addons = ProductAddOn.objects.filter(id__in=addon_ids, is_active=True)
            print(f"🔍 Found {addons.count()} active addons in database")
            for addon in addons:
                print(f"   - {addon.name} (ID: {addon.id}, Price: ₹{addon.price})")
            
            cart_item.addons.add(*addons)
            
            # Verify addons were saved
            saved_addons = cart_item.addons.all()
            print(f"✅ Cart item now has {saved_addons.count()} addons:")
            for addon in saved_addons:
                print(f"   - {addon.name} (₹{addon.price})")
            print(f"💰 Addons total price: ₹{cart_item.addons_price}")
            print(f"💰 Cart item total price: ₹{cart_item.total_price}\n")
        else:
            print("⚠️ No addon IDs received in request\n")

        # Check if it's an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart!',
                'cart_count': cart.total_items,
                'cart_total': float(cart.total_price),
            })
        else:
            # Regular form submission - redirect to cart
            from django.contrib import messages
            if buy_now == '1':
                messages.success(request, f'{product.name} added to cart! Proceed to checkout.')
            else:
                messages.success(request, f'{product.name} added to cart!')
            return redirect('cart:cart')

    except Product.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Product not found.',
            }, status=404)
        else:
            from django.contrib import messages
            messages.error(request, 'Product not found.')
            return redirect('products:product_list')
    except Exception as e:
        print(f"Error in add_to_cart: {str(e)}")  # Debug
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error adding item to cart: {str(e)}',
            }, status=500)
        else:
            from django.contrib import messages
            messages.error(request, f'Error adding item to cart.')
            return redirect('products:product_list')


@login_required
@require_POST
def update_cart(request, item_id):
    """Update cart item quantity (AJAX)"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        
        action = request.POST.get('action')
        
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            cart_item.quantity -= 1
        else:
            # Set specific quantity
            quantity = int(request.POST.get('quantity', 1))
            cart_item.quantity = max(1, quantity)
        
        if cart_item.quantity <= 0:
            cart_item.delete()
            return JsonResponse({
                'success': True,
                'message': 'Item removed from cart.',
                'cart_count': cart.total_items,
                'cart_total': float(cart.total_price),
            })
        else:
            cart_item.save()
            return JsonResponse({
                'success': True,
                'message': 'Cart updated.',
                'item_total': float(cart_item.total_price),
                'cart_count': cart.total_items,
                'cart_total': float(cart.total_price),
            })
    except CartItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Cart item not found.',
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error updating cart.',
        }, status=500)


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart (AJAX)"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        
        product_name = cart_item.product.name
        cart_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed from cart.',
            'cart_count': cart.total_items,
            'cart_total': float(cart.total_price),
        })
    except CartItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Cart item not found.',
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error removing item.',
        }, status=500)


@login_required
@require_POST
def clear_cart(request):
    """Clear all items from cart"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Cart cleared.',
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error clearing cart.',
        }, status=500)