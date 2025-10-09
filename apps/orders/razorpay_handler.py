import razorpay
import json
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Order, OrderTracking

logger = logging.getLogger(__name__)


class RazorpayHandler:
    """Handler for Razorpay payment operations"""

    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

    def create_order(self, amount, order_number, currency='INR'):
        """
        Create a Razorpay order

        Args:
            amount: Amount in rupees (will be converted to paise)
            order_number: Your order reference number
            currency: Currency code (default: INR)

        Returns:
            dict: Razorpay order response
        """
        try:
            # Convert amount to paise (Razorpay expects amount in smallest currency unit)
            amount_in_paise = int(amount * 100)

            order_data = {
                'amount': amount_in_paise,
                'currency': currency,
                'receipt': order_number,
                'notes': {
                    'order_number': order_number
                }
            }

            razorpay_order = self.client.order.create(data=order_data)
            logger.info(f'Razorpay order created: {razorpay_order["id"]} for order {order_number}')

            return {
                'success': True,
                'razorpay_order_id': razorpay_order['id'],
                'amount': amount_in_paise,
                'currency': currency
            }

        except Exception as e:
            logger.error(f'Error creating Razorpay order: {str(e)}', exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def verify_payment_signature(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Verify Razorpay payment signature

        Args:
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Signature to verify

        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            self.client.utility.verify_payment_signature(params_dict)
            logger.info(f'Payment signature verified for payment {razorpay_payment_id}')
            return True

        except razorpay.errors.SignatureVerificationError:
            logger.error(f'Payment signature verification failed for payment {razorpay_payment_id}')
            return False
        except Exception as e:
            logger.error(f'Error verifying payment signature: {str(e)}', exc_info=True)
            return False

    def fetch_payment(self, payment_id):
        """Fetch payment details from Razorpay"""
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logger.error(f'Error fetching payment {payment_id}: {str(e)}', exc_info=True)
            return None

    def refund_payment(self, payment_id, amount=None):
        """
        Refund a payment

        Args:
            payment_id: Razorpay payment ID
            amount: Amount to refund in paise (None for full refund)

        Returns:
            dict: Refund response
        """
        try:
            if amount:
                refund = self.client.payment.refund(payment_id, amount)
            else:
                refund = self.client.payment.refund(payment_id)

            logger.info(f'Refund initiated for payment {payment_id}: {refund["id"]}')
            return {
                'success': True,
                'refund_id': refund['id']
            }
        except Exception as e:
            logger.error(f'Error refunding payment {payment_id}: {str(e)}', exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }


@csrf_exempt
@require_http_methods(["POST"])
def verify_payment(request):
    """
    Verify Razorpay payment after successful payment on frontend

    POST data expected:
    - razorpay_order_id
    - razorpay_payment_id
    - razorpay_signature
    - order_number
    """
    try:
        data = json.loads(request.body)

        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        order_number = data.get('order_number')

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature, order_number]):
            return JsonResponse({
                'success': False,
                'message': 'Missing required parameters'
            }, status=400)

        # Verify signature
        handler = RazorpayHandler()
        is_valid = handler.verify_payment_signature(
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature
        )

        if not is_valid:
            return JsonResponse({
                'success': False,
                'message': 'Invalid payment signature'
            }, status=400)

        # Find and update order
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Order not found'
            }, status=404)

        # Update order with payment details
        order.razorpay_order_id = razorpay_order_id
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.payment_status = 'paid'
        order.payment_method = 'razorpay'
        order.status = 'confirmed'
        order.save()

        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status='confirmed',
            message=f'Payment successful via Razorpay. Payment ID: {razorpay_payment_id}',
            location='Online'
        )

        logger.info(f'Order {order_number} payment verified and confirmed')

        return JsonResponse({
            'success': True,
            'message': 'Payment verified successfully',
            'order_number': order_number,
            'redirect_url': f'/orders/{order.id}/confirmation/'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)

    except Exception as e:
        logger.error(f'Error verifying payment: {str(e)}', exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Payment verification failed'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def payment_failed(request):
    """
    Handle failed payment callback from frontend

    POST data expected:
    - order_number
    - error_code (optional)
    - error_description (optional)
    """
    try:
        data = json.loads(request.body)
        order_number = data.get('order_number')
        error_code = data.get('error_code', 'PAYMENT_FAILED')
        error_description = data.get('error_description', 'Payment failed')

        if not order_number:
            return JsonResponse({
                'success': False,
                'message': 'Order number required'
            }, status=400)

        # Find and update order
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Order not found'
            }, status=404)

        # Update order status
        order.payment_status = 'failed'
        order.status = 'cancelled'
        order.save()

        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status='cancelled',
            message=f'Payment failed. Error: {error_description} (Code: {error_code})',
            location='Online'
        )

        logger.warning(f'Order {order_number} payment failed: {error_description}')

        return JsonResponse({
            'success': True,
            'message': 'Payment failure recorded'
        })

    except Exception as e:
        logger.error(f'Error handling payment failure: {str(e)}', exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Error recording payment failure'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_razorpay_order(request):
    """
    Create a Razorpay order for payment

    POST data expected:
    - order_number
    - amount
    """
    try:
        data = json.loads(request.body)
        order_number = data.get('order_number')
        amount = data.get('amount')

        if not all([order_number, amount]):
            return JsonResponse({
                'success': False,
                'message': 'Order number and amount required'
            }, status=400)

        # Verify order exists
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Order not found'
            }, status=404)

        # Create Razorpay order
        handler = RazorpayHandler()
        result = handler.create_order(float(amount), order_number)

        if result['success']:
            # Update order with Razorpay order ID
            order.razorpay_order_id = result['razorpay_order_id']
            order.save()

            return JsonResponse({
                'success': True,
                'razorpay_order_id': result['razorpay_order_id'],
                'amount': result['amount'],
                'currency': result['currency'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID
            })
        else:
            return JsonResponse({
                'success': False,
                'message': result.get('error', 'Failed to create order')
            }, status=500)

    except Exception as e:
        logger.error(f'Error creating Razorpay order: {str(e)}', exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Error creating payment order'
        }, status=500)
