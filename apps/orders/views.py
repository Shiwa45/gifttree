from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import Order, OrderItem, OrderTracking
from apps.cart.models import Cart, CartItem
from apps.users.models import Address
from apps.products.models import Product
from decimal import Decimal
import json
from datetime import datetime, timedelta


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


@login_required
def checkout_view(request):
    """Checkout page"""
    # Get user's cart
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product', 'variant').all()
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty')
        return redirect('cart:cart')
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('cart:cart')
    
    # Get user's addresses
    addresses = Address.objects.filter(user=request.user, is_active=True)
    default_address = addresses.filter(is_default=True).first()
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    delivery_charge = Decimal('0.00')  # Can be dynamic based on location
    total = subtotal + delivery_charge
    
    context = {
        'cart_items': cart_items,
        'addresses': addresses,
        'default_address': default_address,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'total': total,
        'min_delivery_date': datetime.now().date() + timedelta(days=1),
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