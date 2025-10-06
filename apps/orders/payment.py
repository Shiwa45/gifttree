# Complete Payment Webhook Handlers
# Replace the webhook handler section in apps/orders/payment.py

import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

def handle_razorpay_webhook(request):
    """
    Handle Razorpay webhook events
    """
    try:
        # Get webhook data
        webhook_body = request.body.decode('utf-8')
        webhook_signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE', '')
        
        # Verify webhook signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        try:
            client.utility.verify_webhook_signature(
                webhook_body,
                webhook_signature,
                settings.RAZORPAY_WEBHOOK_SECRET
            )
        except razorpay.errors.SignatureVerificationError:
            logger.error('Razorpay webhook signature verification failed')
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)
        
        # Parse webhook data
        data = json.loads(webhook_body)
        event = data.get('event')
        
        logger.info(f'Received Razorpay webhook: {event}')
        
        # Handle different events
        if event == 'payment.captured':
            return handle_payment_captured(data)
        
        elif event == 'payment.failed':
            return handle_payment_failed(data)
        
        elif event == 'payment.authorized':
            return handle_payment_authorized(data)
        
        elif event == 'refund.created':
            return handle_refund_created(data)
        
        elif event == 'refund.processed':
            return handle_refund_processed(data)
        
        elif event == 'refund.failed':
            return handle_refund_failed(data)
        
        else:
            logger.info(f'Unhandled webhook event: {event}')
            return JsonResponse({'status': 'success'}, status=200)
    
    except Exception as e:
        logger.error(f'Error processing webhook: {str(e)}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def handle_payment_captured(data):
    """
    Handle successful payment capture
    """
    try:
        payment = data['payload']['payment']['entity']
        payment_id = payment['id']
        order_id = payment['order_id']
        amount = payment['amount'] / 100  # Convert paise to rupees
        
        logger.info(f'Payment captured: {payment_id} for order: {order_id}')
        
        # Find the order
        try:
            order = Order.objects.get(order_number=order_id)
        except Order.DoesNotExist:
            logger.error(f'Order not found: {order_id}')
            return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
        
        # Update order status
        order.payment_status = 'paid'
        order.status = 'confirmed'
        order.save()
        
        # Create order tracking entry
        OrderTracking.objects.create(
            order=order,
            status='confirmed',
            message=f'Payment successful. Payment ID: {payment_id}',
            location='Online'
        )
        
        # Send confirmation email
        send_payment_confirmation_email(order, payment_id, amount)
        
        # Optional: Send SMS notification
        # send_payment_confirmation_sms(order)
        
        logger.info(f'Order {order_id} marked as paid and confirmed')
        
        return JsonResponse({
            'status': 'success',
            'message': 'Payment captured successfully',
            'order_id': order_id
        }, status=200)
    
    except Exception as e:
        logger.error(f'Error handling payment.captured: {str(e)}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def handle_payment_failed(data):
    """
    Handle failed payment
    """
    try:
        payment = data['payload']['payment']['entity']
        payment_id = payment['id']
        order_id = payment.get('order_id', 'Unknown')
        error_code = payment.get('error_code', 'UNKNOWN')
        error_description = payment.get('error_description', 'Payment failed')
        
        logger.warning(f'Payment failed: {payment_id} for order: {order_id}. Error: {error_description}')
        
        # Try to find the order
        try:
            order = Order.objects.get(order_number=order_id)
            
            # Update order status
            order.payment_status = 'failed'
            order.status = 'cancelled'
            order.save()
            
            # Create order tracking entry
            OrderTracking.objects.create(
                order=order,
                status='cancelled',
                message=f'Payment failed. Reason: {error_description}',
                location='Online'
            )
            
            # Send payment failure email
            send_payment_failure_email(order, error_description)
            
            logger.info(f'Order {order_id} marked as payment failed')
        
        except Order.DoesNotExist:
            logger.error(f'Order not found for failed payment: {order_id}')
        
        return JsonResponse({
            'status': 'success',
            'message': 'Payment failure recorded',
            'order_id': order_id,
            'error': error_description
        }, status=200)
    
    except Exception as e:
        logger.error(f'Error handling payment.failed: {str(e)}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def handle_payment_authorized(data):
    """
    Handle payment authorization (before capture)
    """
    try:
        payment = data['payload']['payment']['entity']
        payment_id = payment['id']
        order_id = payment['order_id']
        
        logger.info(f'Payment authorized: {payment_id} for order: {order_id}')
        
        try:
            order = Order.objects.get(order_number=order_id)
            
            # Update order status to processing
            order.payment_status = 'pending'
            order.status = 'processing'
            order.save()
            
            # Create order tracking entry
            OrderTracking.objects.create(
                order=order,
                status='processing',
                message=f'Payment authorized and being processed. Payment ID: {payment_id}',
                location='Online'
            )
            
            logger.info(f'Order {order_id} marked as payment authorized')
        
        except Order.DoesNotExist:
            logger.error(f'Order not found: {order_id}')
        
        return JsonResponse({
            'status': 'success',
            'message': 'Payment authorization recorded'
        }, status=200)
    
    except Exception as e:
        logger.error(f'Error handling payment.authorized: {str(e)}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def handle_refund_created(data):
    """
    Handle refund creation
    """
    try:
        refund = data['payload']['refund']['entity']
        refund_id = refund['id']
        payment_id = refund['payment_id']
        amount = refund['amount'] / 100
        
        logger.info(f'Refund created: {refund_id} for payment: {payment_id}')
        
        # Find order by payment_id (you may need to store payment_id in Order model)
        # For now, log the refund
        logger.info(f'Refund of ₹{amount} created for payment {payment_id}')
        
        return JsonResponse({
            'status': 'success',
            'message': 'Refund creation recorded'
        }, status=200)
    
    except Exception as e:
        logger.error(f'Error handling refund.created: {str(e)}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def handle_refund_processed(data):
    """
    Handle processed refund
    """
    try:
        refund = data['payload']['refund']['entity']
        refund_id = refund['id']
        payment_id = refund['payment_id']
        amount = refund['amount'] / 100
        status = refund['status']
        
        logger.info(f'Refund processed: {refund_id} for payment: {payment_id}. Status: {status}')
        
        # Update order status if found
        # You may need to add a payment_id field to Order model to find the order
        
        # Send refund confirmation email
        # send_refund_confirmation_email(order, amount)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Refund processed'
        }, status=200)
    
    except Exception as e:
        logger.error(f'Error handling refund.processed: {str(e)}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def handle_refund_failed(data):
    """
    Handle failed refund
    """
    try:
        refund = data['payload']['refund']['entity']
        refund_id = refund['id']
        payment_id = refund['payment_id']
        error = refund.get('error_description', 'Refund failed')
        
        logger.error(f'Refund failed: {refund_id} for payment: {payment_id}. Error: {error}')
        
        # Notify admin about failed refund
        send_mail(
            subject=f'Refund Failed - {refund_id}',
            message=f'Refund {refund_id} for payment {payment_id} failed.\nError: {error}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Refund failure recorded'
        }, status=200)
    
    except Exception as e:
        logger.error(f'Error handling refund.failed: {str(e)}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# Email notification functions

def send_payment_confirmation_email(order, payment_id, amount):
    """Send payment confirmation email to customer"""
    try:
        subject = f'Payment Confirmed - Order #{order.order_number}'
        
        # Render email template
        html_message = render_to_string('emails/payment_confirmation.html', {
            'order': order,
            'payment_id': payment_id,
            'amount': amount,
            'site_name': settings.SITE_NAME,
        })
        
        send_mail(
            subject=subject,
            message=f'Your payment of ₹{amount} has been confirmed for order #{order.order_number}',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.billing_email],
            fail_silently=True,
        )
        
        logger.info(f'Payment confirmation email sent for order {order.order_number}')
    
    except Exception as e:
        logger.error(f'Error sending payment confirmation email: {str(e)}', exc_info=True)


def send_payment_failure_email(order, error_description):
    """Send payment failure email to customer"""
    try:
        subject = f'Payment Failed - Order #{order.order_number}'
        
        html_message = render_to_string('emails/payment_failed.html', {
            'order': order,
            'error': error_description,
            'site_name': settings.SITE_NAME,
            'retry_url': f'{settings.SITE_DOMAIN}/orders/{order.order_number}/retry-payment/',
        })
        
        send_mail(
            subject=subject,
            message=f'Your payment for order #{order.order_number} failed. Reason: {error_description}',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.billing_email],
            fail_silently=True,
        )
        
        logger.info(f'Payment failure email sent for order {order.order_number}')
    
    except Exception as e:
        logger.error(f'Error sending payment failure email: {str(e)}', exc_info=True)