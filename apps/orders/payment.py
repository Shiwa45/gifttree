"""
Razorpay Payment Gateway Integration
Install: pip install razorpay
"""

import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Order, OrderTracking
import json
import hmac
import hashlib


class RazorpayClient:
    """Razorpay payment handler"""
    
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    
    def create_order(self, amount, currency='INR', receipt=None):
        """
        Create Razorpay order
        Amount should be in paise (multiply by 100)
        """
        data = {
            'amount': int(amount * 100),  # Convert to paise
            'currency': currency,
            'receipt': receipt or f'order_{receipt}',
            'payment_capture': 1  # Auto capture payment
        }
        
        try:
            order = self.client.order.create(data=data)
            return {
                'success': True,
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment_signature(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """Verify payment signature for security"""
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except:
            return False
    
    def fetch_payment(self, payment_id):
        """Fetch payment details"""
        try:
            payment = self.client.payment.fetch(payment_id)
            return {
                'success': True,
                'payment': payment
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Initialize Razorpay client
razorpay_client = RazorpayClient()


@require_POST
def initiate_payment(request):
    """Initiate payment for an order"""
    try:
        data = json.loads(request.body)
        order_number = data.get('order_number')
        
        # Get order
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        
        # Check if order is already paid
        if order.payment_status == 'paid':
            return JsonResponse({
                'success': False,
                'message': 'Order is already paid'
            }, status=400)
        
        # Create Razorpay order
        razorpay_order = razorpay_client.create_order(
            amount=float(order.total_amount),
            receipt=order.order_number
        )
        
        if not razorpay_order['success']:
            return JsonResponse({
                'success': False,
                'message': 'Failed to initiate payment'
            }, status=400)
        
        # Return payment details for frontend
        return JsonResponse({
            'success': True,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order['order_id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency'],
            'order_number': order.order_number,
            'customer': {
                'name': order.billing_name,
                'email': order.billing_email,
                'phone': order.billing_phone
            }
        })
        
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Order not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_POST
def payment_callback(request):
    """Handle payment callback from Razorpay"""
    try:
        data = json.loads(request.body)
        
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        order_number = data.get('order_number')
        
        # Verify payment signature
        is_valid = razorpay_client.verify_payment_signature(
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature
        )
        
        if not is_valid:
            return JsonResponse({
                'success': False,
                'message': 'Invalid payment signature'
            }, status=400)
        
        # Get order
        order = get_object_or_404(Order, order_number=order_number)
        
        # Fetch payment details
        payment_details = razorpay_client.fetch_payment(razorpay_payment_id)
        
        if payment_details['success']:
            payment = payment_details['payment']
            
            # Update order payment status
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()
            
            # Create tracking entry
            OrderTracking.objects.create(
                order=order,
                status='confirmed',
                message='Payment received successfully. Order confirmed.',
            )
            
            # TODO: Send confirmation email
            # send_order_confirmation_email(order)
            
            return JsonResponse({
                'success': True,
                'message': 'Payment successful',
                'order_number': order.order_number,
                'redirect': f'/orders/{order.order_number}/'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Payment verification failed'
            }, status=400)
            
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Order not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_POST
def payment_webhook(request):
    """
    Webhook handler for Razorpay events
    Configure this URL in Razorpay Dashboard
    """
    try:
        # Verify webhook signature
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        
        # Verify signature
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            request.body,
            hashlib.sha256
        ).hexdigest()
        
        if webhook_signature != expected_signature:
            return JsonResponse({
                'success': False,
                'message': 'Invalid signature'
            }, status=400)
        
        # Process webhook event
        data = json.loads(request.body)
        event = data.get('event')
        
        if event == 'payment.captured':
            # Payment was captured successfully
            payment = data['payload']['payment']['entity']
            # Handle payment captured event
            pass
        
        elif event == 'payment.failed':
            # Payment failed
            payment = data['payload']['payment']['entity']
            # Handle payment failed event
            pass
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)