from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Order, OrderItem, OrderTracking
from .forms import (
    CheckoutAddressForm, 
    CheckoutDeliveryForm, 
    CheckoutPaymentForm,
    CouponForm
)
from apps.cart.models import Cart, CartItem
from apps.users.models import Address
from apps.core.models import SiteSettings


def checkout_view(request):
    """Main checkout page"""
    cart_items = []
    addresses = []
    default_address = None
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.select_related('product', 'variant').prefetch_related('product__images').all()
        except Cart.DoesNotExist:
            messages.warning(request, 'Your cart is empty')
            return redirect('cart:cart')

        if not cart_items.exists():
            messages.warning(request, 'Your cart is empty')
            return redirect('cart:cart')
            
        addresses = Address.objects.filter(user=request.user, is_active=True)
        default_address = addresses.filter(is_default=True).first()
    else:
        messages.info(request, 'Please login to proceed with checkout')
        return redirect('users:login')

    subtotal = sum(item.total_price for item in cart_items)
    delivery_charge = Decimal('0.00')
    total = subtotal + delivery_charge

    context = {
        'cart_items': cart_items,
        'addresses': addresses,
        'default_address': default_address,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'total': total,
        'today': datetime.now().date(),
        'razorpay_key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
        'site_settings': {
            'free_delivery_above': 500,
            'delivery_charge': delivery_charge,
        }
    }

    return render(request, 'orders/checkout.html', context)


@login_required
def checkout_address(request):
    """Step 1: Address selection/entry"""
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product', 'variant').all()
    
    # Check if cart is empty
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty. Add some items before checkout.')
        return redirect('cart:cart')
    
    if request.method == 'POST':
        form = CheckoutAddressForm(user=request.user, data=request.POST)
        if form.is_valid():
            # Store address data in session
            if form.cleaned_data['use_existing']:
                address = form.cleaned_data['existing_address']
                request.session['checkout_address'] = {
                    'full_name': address.full_name,
                    'phone': address.phone,
                    'address_line_1': address.address_line_1,
                    'address_line_2': address.address_line_2,
                    'city': address.city,
                    'state': address.state,
                    'pincode': address.pincode,
                }
            else:
                request.session['checkout_address'] = {
                    'full_name': form.cleaned_data['full_name'],
                    'phone': form.cleaned_data['phone'],
                    'address_line_1': form.cleaned_data['address_line_1'],
                    'address_line_2': form.cleaned_data['address_line_2'],
                    'city': form.cleaned_data['city'],
                    'state': form.cleaned_data['state'],
                    'pincode': form.cleaned_data['pincode'],
                }
                
                # Save address if requested
                if form.cleaned_data.get('save_address'):
                    Address.objects.create(
                        user=request.user,
                        title='Home',
                        full_name=form.cleaned_data['full_name'],
                        phone=form.cleaned_data['phone'],
                        address_line_1=form.cleaned_data['address_line_1'],
                        address_line_2=form.cleaned_data['address_line_2'],
                        city=form.cleaned_data['city'],
                        state=form.cleaned_data['state'],
                        pincode=form.cleaned_data['pincode'],
                    )
            
            return redirect('orders:checkout_delivery')
    else:
        # Pre-fill with default address if available
        default_address = Address.objects.filter(
            user=request.user, 
            is_default=True, 
            is_active=True
        ).first()
        
        initial_data = {}
        if default_address:
            initial_data = {
                'use_existing': True,
                'existing_address': default_address,
            }
        
        form = CheckoutAddressForm(user=request.user, initial=initial_data)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'cart': cart,
        'step': 1,
    }
    return render(request, 'orders/checkout_address.html', context)


@login_required
def checkout_delivery(request):
    """Step 2: Delivery options"""
    # Check if address is in session
    if 'checkout_address' not in request.session:
        messages.warning(request, 'Please enter your delivery address first.')
        return redirect('orders:checkout_address')
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product', 'variant').all()
    
    if request.method == 'POST':
        form = CheckoutDeliveryForm(request.POST)
        if form.is_valid():
            # Store delivery data in session
            request.session['checkout_delivery'] = {
                'delivery_option': form.cleaned_data['delivery_option'],
                'delivery_date': form.cleaned_data.get('delivery_date').isoformat() if form.cleaned_data.get('delivery_date') else None,
                'delivery_time_slot': form.cleaned_data.get('delivery_time_slot', ''),
                'special_instructions': form.cleaned_data.get('special_instructions', ''),
            }
            
            # Calculate delivery charge
            delivery_charge = Decimal('0.00')
            if form.cleaned_data['delivery_option'] == 'midnight':
                delivery_charge = Decimal('99.00')
            elif form.cleaned_data['delivery_option'] == 'fixed_time':
                delivery_charge = Decimal('49.00')
            
            request.session['delivery_charge'] = str(delivery_charge)
            
            return redirect('orders:checkout_payment')
    else:
        # Pre-fill with session data if available
        initial_data = request.session.get('checkout_delivery', {})
        if initial_data.get('delivery_date'):
            initial_data['delivery_date'] = datetime.fromisoformat(initial_data['delivery_date']).date()
        form = CheckoutDeliveryForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'cart': cart,
        'step': 2,
    }
    return render(request, 'orders/checkout_delivery.html', context)


@login_required
def checkout_payment(request):
    """Step 3: Payment and review"""
    # Check if previous steps are completed
    if 'checkout_address' not in request.session:
        messages.warning(request, 'Please enter your delivery address first.')
        return redirect('orders:checkout_address')
    
    if 'checkout_delivery' not in request.session:
        messages.warning(request, 'Please select delivery options.')
        return redirect('orders:checkout_delivery')
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product', 'variant').all()
    
    # Calculate totals
    subtotal = cart.total_price
    delivery_charge = Decimal(request.session.get('delivery_charge', '0.00'))
    discount = Decimal(request.session.get('discount_amount', '0.00'))
    total_amount = subtotal + delivery_charge - discount
    
    if request.method == 'POST':
        form = CheckoutPaymentForm(request.POST)
        if form.is_valid():
            # Store payment data in session
            request.session['checkout_payment'] = {
                'payment_method': form.cleaned_data['payment_method'],
                'billing_same_as_shipping': form.cleaned_data['billing_same_as_shipping'],
            }
            
            # Store billing address if different
            if not form.cleaned_data['billing_same_as_shipping']:
                request.session['checkout_billing'] = {
                    'billing_name': form.cleaned_data['billing_name'],
                    'billing_email': form.cleaned_data['billing_email'],
                    'billing_phone': form.cleaned_data['billing_phone'],
                    'billing_address_line_1': form.cleaned_data['billing_address_line_1'],
                    'billing_address_line_2': form.cleaned_data['billing_address_line_2'],
                    'billing_city': form.cleaned_data['billing_city'],
                    'billing_state': form.cleaned_data['billing_state'],
                    'billing_pincode': form.cleaned_data['billing_pincode'],
                }
            else:
                # Use shipping address as billing
                shipping_address = request.session['checkout_address']
                request.session['checkout_billing'] = {
                    'billing_name': shipping_address['full_name'],
                    'billing_email': request.user.email,
                    'billing_phone': shipping_address['phone'],
                    'billing_address_line_1': shipping_address['address_line_1'],
                    'billing_address_line_2': shipping_address['address_line_2'],
                    'billing_city': shipping_address['city'],
                    'billing_state': shipping_address['state'],
                    'billing_pincode': shipping_address['pincode'],
                }
            
            # Process order - call place_order directly
            return place_order(request)
    else:
        # Pre-fill with user data
        initial_data = {
            'billing_same_as_shipping': True,
            'billing_email': request.user.email,
        }
        form = CheckoutPaymentForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'cart': cart,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'discount': discount,
        'total_amount': total_amount,
        'step': 3,
        'address': request.session.get('checkout_address'),
        'delivery': request.session.get('checkout_delivery'),
    }
    return render(request, 'orders/checkout_payment.html', context)


@login_required
@transaction.atomic
def place_order(request):
    """Process and create the order"""
    # Validate all checkout data
    required_session_keys = ['checkout_address', 'checkout_delivery', 'checkout_payment', 'checkout_billing']
    for key in required_session_keys:
        if key not in request.session:
            messages.error(request, 'Checkout session expired. Please start again.')
            return redirect('orders:checkout_address')
    
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.select_related('product', 'variant').all()
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart')
    
    # Get data from session
    shipping_address = request.session['checkout_address']
    delivery_data = request.session['checkout_delivery']
    billing_data = request.session['checkout_billing']
    payment_data = request.session['checkout_payment']
    
    # Calculate amounts
    subtotal = cart.total_price
    delivery_charge = Decimal(request.session.get('delivery_charge', '0.00'))
    total_amount = subtotal + delivery_charge
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        status='pending',
        payment_status='pending',
        # Billing info
        billing_name=billing_data['billing_name'],
        billing_email=billing_data['billing_email'],
        billing_phone=billing_data['billing_phone'],
        billing_address_line_1=billing_data['billing_address_line_1'],
        billing_address_line_2=billing_data.get('billing_address_line_2', ''),
        billing_city=billing_data['billing_city'],
        billing_state=billing_data['billing_state'],
        billing_pincode=billing_data['billing_pincode'],
        # Shipping info
        shipping_name=shipping_address['full_name'],
        shipping_phone=shipping_address['phone'],
        shipping_address_line_1=shipping_address['address_line_1'],
        shipping_address_line_2=shipping_address.get('address_line_2', ''),
        shipping_city=shipping_address['city'],
        shipping_state=shipping_address['state'],
        shipping_pincode=shipping_address['pincode'],
        # Pricing
        subtotal=subtotal,
        delivery_charge=delivery_charge,
        total_amount=total_amount,
        # Delivery details
        special_instructions=delivery_data.get('special_instructions', ''),
        delivery_date=datetime.fromisoformat(delivery_data['delivery_date']).date() if delivery_data.get('delivery_date') else None,
        delivery_time_slot=delivery_data.get('delivery_time_slot', ''),
    )
    
    # Create order items
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            variant=cart_item.variant,
            product_name=cart_item.product.name,
            variant_name=cart_item.variant.name if cart_item.variant else '',
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price,
            total_price=cart_item.total_price,
        )
    
    # Create initial tracking entry
    OrderTracking.objects.create(
        order=order,
        status='pending',
        message='Order placed successfully',
        location=shipping_address['city'],
    )
    
    # Clear cart
    cart_items.delete()
    
    # Clear checkout session
    for key in ['checkout_address', 'checkout_delivery', 'checkout_payment', 'checkout_billing', 'delivery_charge', 'discount_amount']:
        if key in request.session:
            del request.session[key]
    
    # Handle payment
    if payment_data['payment_method'] == 'online':
        # Redirect to payment gateway (implement based on your payment provider)
        # For now, we'll simulate successful payment
        order.payment_status = 'paid'
        order.status = 'confirmed'
        order.save()
        
        OrderTracking.objects.create(
            order=order,
            status='confirmed',
            message='Payment successful. Order confirmed.',
            location=shipping_address['city'],
        )
        
        messages.success(request, 'Payment successful! Your order has been confirmed.')
    else:
        # Cash on Delivery
        messages.success(request, 'Order placed successfully! Pay when you receive your order.')
    
    return redirect('orders:order_confirmation', order_number=order.order_number)


@login_required
def order_confirmation(request, order_number):
    """Order confirmation page"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'orders/order_confirmation.html', context)


@login_required
def order_list(request):
    """Display user's orders"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_number):
    """Display order details"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = order.items.all()
    tracking = order.tracking.all()
    
    context = {
        'order': order,
        'order_items': order_items,
        'tracking': tracking,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
@require_POST
def cancel_order(request, order_number):
    """Cancel an order"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Only allow cancellation for pending or confirmed orders
    if order.status in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save()
        
        OrderTracking.objects.create(
            order=order,
            status='cancelled',
            message='Order cancelled by customer',
        )
        
        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    
    return redirect('orders:order_detail', order_number=order_number)


@login_required
@require_POST
def apply_coupon(request):
    """Apply coupon code (AJAX)"""
    coupon_code = request.POST.get('coupon_code', '').strip().upper()
    
    # Dummy coupon validation - implement your coupon logic here
    valid_coupons = {
        'SAVE10': {'discount': 10, 'type': 'percent'},
        'FLOWER20': {'discount': 20, 'type': 'percent'},
        'FIRST15': {'discount': 15, 'type': 'percent'},
        'FLAT100': {'discount': 100, 'type': 'fixed'},
    }
    
    if coupon_code in valid_coupons:
        coupon = valid_coupons[coupon_code]
        cart = Cart.objects.get(user=request.user)
        subtotal = cart.total_price
        
        if coupon['type'] == 'percent':
            discount = (subtotal * Decimal(coupon['discount'])) / Decimal('100')
        else:
            discount = Decimal(coupon['discount'])
        
        # Store in session
        request.session['coupon_code'] = coupon_code
        request.session['discount_amount'] = str(discount)
        
        return JsonResponse({
            'success': True,
            'message': f'Coupon "{coupon_code}" applied successfully!',
            'discount': float(discount),
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Invalid coupon code.',
        })


@login_required
@require_POST
def remove_coupon(request):
    """Remove applied coupon (AJAX)"""
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    if 'discount_amount' in request.session:
        del request.session['discount_amount']
    
    return JsonResponse({
        'success': True,
        'message': 'Coupon removed.',
    })