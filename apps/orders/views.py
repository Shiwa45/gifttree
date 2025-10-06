from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.conf import settings
from .models import Order, OrderItem, OrderTracking
from apps.cart.models import Cart, CartItem
from apps.users.models import Address
from apps.products.models import Product, ProductVariant
from decimal import Decimal
import json
from datetime import datetime, timedelta
import razorpay
import hmac
import hashlib


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
    context = {
        'order': order,
        'order_items': order.items.all(),
        'tracking': order.tracking.all(),
    }
    return render(request, 'orders/order_detail.html', context)


def checkout_view(request):
    """Checkout page"""
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
@require_POST
@transaction.atomic
def process_checkout(request):
    """Process checkout and create order"""
    try:
        data = json.loads(request.body)
        
        # Get cart
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product', 'variant').all()
        
        if not cart_items.exists():
            return JsonResponse({
                'success': False,
                'message': 'Your cart is empty'
            }, status=400)
        
        # Get or create address
        address_id = data.get('address_id')
        if address_id:
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            # Create new address from data
            address = Address.objects.create(
                user=request.user,
                title=data.get('address_title', 'Home'),
                full_name=data.get('full_name'),
                phone=data.get('phone'),
                address_line_1=data.get('address_line_1'),
                address_line_2=data.get('address_line_2', ''),
                city=data.get('city'),
                state=data.get('state'),
                pincode=data.get('pincode'),
                is_default=data.get('is_default', False)
            )
        
        # Calculate totals
        subtotal = sum(item.total_price for item in cart_items)
        delivery_charge = Decimal(data.get('delivery_charge', '0.00'))
        total_amount = subtotal + delivery_charge
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            status='pending',
            payment_status='pending',
            
            # Billing info (same as shipping for now)
            billing_name=address.full_name,
            billing_email=request.user.email,
            billing_phone=address.phone,
            billing_address_line_1=address.address_line_1,
            billing_address_line_2=address.address_line_2,
            billing_city=address.city,
            billing_state=address.state,
            billing_pincode=address.pincode,
            
            # Shipping info
            shipping_name=address.full_name,
            shipping_phone=address.phone,
            shipping_address_line_1=address.address_line_1,
            shipping_address_line_2=address.address_line_2,
            shipping_city=address.city,
            shipping_state=address.state,
            shipping_pincode=address.pincode,
            
            # Pricing
            subtotal=subtotal,
            delivery_charge=delivery_charge,
            total_amount=total_amount,
            
            # Delivery details
            special_instructions=data.get('special_instructions', ''),
            delivery_date=data.get('delivery_date'),
            delivery_time_slot=data.get('delivery_time_slot', ''),
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
                total_price=cart_item.total_price
            )
        
        # Create initial tracking entry
        OrderTracking.objects.create(
            order=order,
            status='pending',
            message='Order placed successfully',
            location=address.city
        )
        
        # Clear cart
        cart_items.delete()
        
        # Send order confirmation email (TODO)
        # send_order_confirmation_email(order)
        
        return JsonResponse({
            'success': True,
            'message': 'Order placed successfully',
            'order_number': order.order_number,
            'redirect': f'/orders/{order.order_number}/'
        })
        
    except Cart.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Cart not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_POST
def cancel_order(request, order_number):
    """Cancel an order"""
    try:
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        
        # Check if order can be cancelled
        if order.status in ['shipped', 'delivered', 'cancelled']:
            return JsonResponse({
                'success': False,
                'message': f'Cannot cancel order with status: {order.get_status_display()}'
            }, status=400)
        
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        # Add tracking entry
        OrderTracking.objects.create(
            order=order,
            status='cancelled',
            message='Order cancelled by customer',
        )
        
        # TODO: Process refund if payment was made
        
        return JsonResponse({
            'success': True,
            'message': 'Order cancelled successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_POST
def reorder(request, order_number):
    """Reorder items from a previous order"""
    try:
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Add order items to cart
        added_count = 0
        for order_item in order.items.all():
            # Check if product is still available
            if order_item.product.is_active and order_item.product.is_in_stock:
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=order_item.product,
                    variant=order_item.variant,
                    defaults={'quantity': order_item.quantity}
                )
                
                if not created:
                    cart_item.quantity += order_item.quantity
                    cart_item.save()
                
                added_count += 1
        
        if added_count == 0:
            return JsonResponse({
                'success': False,
                'message': 'No items could be added to cart'
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'message': f'{added_count} item(s) added to cart',
            'cart_count': cart.total_items,
            'redirect': '/cart/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
def track_order(request, order_number):
    """Track order status"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    tracking_history = order.tracking.all()
    
    context = {
        'order': order,
        'tracking_history': tracking_history,
    }
    
    return render(request, 'orders/track_order.html', context)


@login_required
@require_POST
def apply_coupon(request):
    """Apply coupon code to cart"""
    coupon_code = request.POST.get('coupon_code', '').strip().upper()
    
    if not coupon_code:
        return JsonResponse({
            'success': False,
            'message': 'Please enter a coupon code'
        })
    
    # For now, simulate coupon validation
    # TODO: Implement actual coupon system
    valid_coupons = {
        'SAVE10': {'type': 'percentage', 'value': 10, 'min_order': 500},
        'FLOWER20': {'type': 'percentage', 'value': 20, 'min_order': 1000},
        'FIRST15': {'type': 'percentage', 'value': 15, 'min_order': 300},
    }
    
    if coupon_code not in valid_coupons:
        return JsonResponse({
            'success': False,
            'message': 'Invalid coupon code'
        })
    
    # Get user's cart
    try:
        cart = Cart.objects.get(user=request.user)
        cart_total = cart.total_price
    except Cart.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Your cart is empty'
        })
    
    coupon = valid_coupons[coupon_code]
    
    # Check minimum order value
    if cart_total < coupon['min_order']:
        return JsonResponse({
            'success': False,
            'message': f'Minimum order value ₹{coupon["min_order"]} required for this coupon'
        })
    
    # Calculate discount
    if coupon['type'] == 'percentage':
        discount_amount = (cart_total * coupon['value']) / 100
        discount_display = f'{coupon["value"]}% OFF'
    else:
        discount_amount = coupon['value']
        discount_display = f'₹{coupon["value"]} OFF'
    
    # Store coupon in session
    request.session['applied_coupon'] = {
        'code': coupon_code,
        'discount_amount': float(discount_amount),
        'discount_display': discount_display,
    }
    
    return JsonResponse({
        'success': True,
        'message': f'Coupon "{coupon_code}" applied successfully!',
        'coupon': {
            'code': coupon_code,
            'discount_display': discount_display,
            'discount_amount': float(discount_amount),
        }
    })


@login_required
@require_POST
def remove_coupon(request):
    """Remove applied coupon from cart"""
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
        request.session.modified = True
    
    return JsonResponse({
        'success': True,
        'message': 'Coupon removed'
    })



# Create: apps/orders/coupon_views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from .models import Coupon, CouponUsage
from apps.cart.models import Cart


@login_required
@require_POST
def apply_coupon(request):
    """
    Apply coupon code to cart
    """
    coupon_code = request.POST.get('coupon_code', '').strip().upper()
    
    if not coupon_code:
        return JsonResponse({
            'success': False,
            'message': 'Please enter a coupon code'
        })
    
    # Get user's cart
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Your cart is empty'
        })
    
    # Calculate cart total
    cart_total = cart.total_price
    
    if cart_total == 0:
        return JsonResponse({
            'success': False,
            'message': 'Your cart is empty'
        })
    
    # Check if coupon exists
    try:
        coupon = Coupon.objects.get(code=coupon_code)
    except Coupon.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Invalid coupon code'
        })
    
    # Check if user can use this coupon
    can_use, message = coupon.can_be_used_by_user(request.user, cart_total)
    
    if not can_use:
        return JsonResponse({
            'success': False,
            'message': message
        })
    
    # Calculate discount
    discount_amount = coupon.calculate_discount(cart_total)
    
    # Store coupon in session
    request.session['applied_coupon'] = {
        'code': coupon.code,
        'id': coupon.id,
        'discount_type': coupon.discount_type,
        'discount_value': float(coupon.discount_value),
        'discount_amount': float(discount_amount),
    }
    
    # Calculate new total
    new_total = cart_total - discount_amount
    
    return JsonResponse({
        'success': True,
        'message': f'Coupon "{coupon.code}" applied successfully!',
        'coupon': {
            'code': coupon.code,
            'discount_display': coupon.get_discount_display(),
            'discount_amount': float(discount_amount),
        },
        'cart_subtotal': float(cart_total),
        'discount_amount': float(discount_amount),
        'new_total': float(new_total),
    })


@login_required
@require_POST
def remove_coupon(request):
    """
    Remove applied coupon from cart
    """
    # Remove coupon from session
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
        request.session.modified = True
    
    # Get cart total
    try:
        cart = Cart.objects.get(user=request.user)
        cart_total = cart.total_price
    except Cart.DoesNotExist:
        cart_total = 0
    
    return JsonResponse({
        'success': True,
        'message': 'Coupon removed',
        'cart_total': float(cart_total),
    })


@login_required
def validate_coupon(request):
    """
    Validate coupon without applying (for real-time feedback)
    """
    coupon_code = request.GET.get('code', '').strip().upper()
    
    if not coupon_code:
        return JsonResponse({
            'valid': False,
            'message': 'Please enter a coupon code'
        })
    
    try:
        coupon = Coupon.objects.get(code=coupon_code)
    except Coupon.DoesNotExist:
        return JsonResponse({
            'valid': False,
            'message': 'Invalid coupon code'
        })
    
    # Check if coupon is valid
    is_valid, message = coupon.is_valid()
    
    if not is_valid:
        return JsonResponse({
            'valid': False,
            'message': message
        })
    
    # Get cart total
    try:
        cart = Cart.objects.get(user=request.user)
        cart_total = cart.total_price
    except Cart.DoesNotExist:
        cart_total = 0
    
    # Check if user can use coupon
    can_use, user_message = coupon.can_be_used_by_user(request.user, cart_total)
    
    if not can_use:
        return JsonResponse({
            'valid': False,
            'message': user_message
        })
    
    # Calculate potential discount
    discount_amount = coupon.calculate_discount(cart_total)
    
    return JsonResponse({
        'valid': True,
        'message': 'Valid coupon!',
        'coupon': {
            'code': coupon.code,
            'description': coupon.description,
            'discount_display': coupon.get_discount_display(),
            'discount_amount': float(discount_amount),
            'minimum_order_value': float(coupon.minimum_order_value),
        }
    })


def get_available_coupons(request):
    """
    Get list of currently available coupons
    """
    from django.utils import timezone
    
    # Get active coupons
    coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_to__gte=timezone.now()
    ).exclude(
        usage_limit__isnull=False,
        times_used__gte=models.F('usage_limit')
    )
    
    # If user is authenticated, filter by user eligibility
    if request.user.is_authenticated:
        # Get cart total
        try:
            cart = Cart.objects.get(user=request.user)
            cart_total = cart.total_price
        except Cart.DoesNotExist:
            cart_total = 0
        
        coupon_list = []
        for coupon in coupons:
            can_use, message = coupon.can_be_used_by_user(request.user, cart_total)
            
            coupon_list.append({
                'code': coupon.code,
                'description': coupon.description,
                'discount_display': coupon.get_discount_display(),
                'minimum_order_value': float(coupon.minimum_order_value),
                'can_use': can_use,
                'message': message if not can_use else None,
                'valid_to': coupon.valid_to.strftime('%d %b %Y'),
            })
    else:
        coupon_list = [
            {
                'code': coupon.code,
                'description': coupon.description,
                'discount_display': coupon.get_discount_display(),
                'minimum_order_value': float(coupon.minimum_order_value),
                'valid_to': coupon.valid_to.strftime('%d %b %Y'),
            }
            for coupon in coupons
        ]
    
    return JsonResponse({
        'success': True,
        'coupons': coupon_list
    })


# Helper function to record coupon usage after order
def record_coupon_usage(order, coupon, user, discount_amount):
    """
    Record that a coupon was used in an order
    Call this after order confirmation
    """
    # Create usage record
    CouponUsage.objects.create(
        coupon=coupon,
        user=user,
        order=order,
        discount_amount=discount_amount
    )
    
    # Increment usage count
    coupon.times_used += 1
    coupon.save()