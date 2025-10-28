"""Razorpay payment integration views"""
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.conf import settings
from decimal import Decimal
import json
import razorpay

from .models import Order, OrderItem, OrderTracking
from apps.cart.models import Cart
from apps.users.models import Address


@login_required
@require_POST
def create_razorpay_order(request):
    """Create Razorpay order for payment"""
    try:
        data = json.loads(request.body)

        # Get cart
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()

        if not cart_items.exists():
            return JsonResponse({
                'success': False,
                'message': 'Your cart is empty'
            }, status=400)

        # Calculate total
        subtotal = sum(item.total_price for item in cart_items)
        delivery_charge = Decimal(data.get('delivery_charge', '0.00'))
        total_amount = subtotal + delivery_charge

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create Razorpay order
        razorpay_order = client.order.create({
            'amount': int(total_amount * 100),  # Amount in paise
            'currency': 'INR',
            'payment_capture': 1,  # Auto capture
            'notes': {
                'user_id': request.user.id,
                'email': request.user.email,
            }
        })

        return JsonResponse({
            'success': True,
            'order_id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency'],
            'key_id': settings.RAZORPAY_KEY_ID,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_POST
@transaction.atomic
def verify_razorpay_payment(request):
    """Verify Razorpay payment and create order"""
    try:
        data = json.loads(request.body)

        # Verify payment signature
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')

        # Verify signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({
                'success': False,
                'message': 'Payment verification failed'
            }, status=400)

        # Payment verified, create order
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product', 'variant').all()

        if not cart_items.exists():
            return JsonResponse({
                'success': False,
                'message': 'Your cart is empty'
            }, status=400)

        # Get address
        address_id = data.get('address_id')
        if address_id:
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            # Create new address
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
            status='confirmed',
            payment_status='paid',
            payment_method='razorpay',
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,

            # Billing info
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

        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status='confirmed',
            message='Order confirmed and payment received',
            location=address.city
        )

        # Clear cart
        cart_items.delete()

        return JsonResponse({
            'success': True,
            'message': 'Payment successful and order created',
            'order_number': order.order_number,
            'redirect': f'/orders/confirmation/{order.order_number}/'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_POST
@transaction.atomic
def process_cod_order(request):
    """Process Cash on Delivery order"""
    try:
        data = json.loads(request.body)

        # Get cart
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product', 'variant').prefetch_related('addons').all()

        if not cart_items.exists():
            return JsonResponse({
                'success': False,
                'message': 'Your cart is empty'
            }, status=400)

        # Get address
        address_id = data.get('address_id')
        if address_id:
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            # Create new address
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
            payment_method='cod',

            # Billing info
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
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                product_name=cart_item.product.name,
                variant_name=cart_item.variant.name if cart_item.variant else '',
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.total_price
            )
            # Add addons to order item if any
            if cart_item.addons.exists():
                order_item.addons.set(cart_item.addons.all())

        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status='pending',
            message='Order placed successfully - Cash on Delivery',
            location=address.city
        )

        # Clear cart
        cart_items.delete()

        return JsonResponse({
            'success': True,
            'message': 'Order placed successfully! Pay when you receive your order.',
            'order_number': order.order_number,
            'redirect': f'/orders/confirmation/{order.order_number}/'
        })

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error processing COD order: {str(e)}', exc_info=True)
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
