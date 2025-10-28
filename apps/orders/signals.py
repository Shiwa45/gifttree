from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Order
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    """
    Signal handler when new order is created
    Send order confirmation email to customer and notification to admin
    """
    if created:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.conf import settings

        try:
            # 1. Send order confirmation to CUSTOMER
            subject_customer = f'Order Placed Successfully - #{instance.order_number}'
            html_message_customer = render_to_string('emails/order_confirmation.html', {
                'order': instance,
                'site_name': getattr(settings, 'SITE_NAME', 'GiftTree'),
                'site_url': getattr(settings, 'SITE_DOMAIN', 'https://mygiftstree.com'),
            })

            send_mail(
                subject=subject_customer,
                message=f'Thank you for your order! Order Number: #{instance.order_number}',
                html_message=html_message_customer,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.billing_email],
                fail_silently=False,
            )
            logger.info(f'Order confirmation email sent to customer: {instance.billing_email}')

            # 2. Send new order notification to ADMIN
            subject_admin = f'🎁 New Order Received - #{instance.order_number}'
            admin_message = f"""
New Order Alert!

Order Number: #{instance.order_number}
Customer: {instance.billing_name}
Email: {instance.billing_email}
Phone: {instance.billing_phone}
Total Amount: ₹{instance.total_amount}
Payment Method: {instance.payment_method.upper()}
Payment Status: {instance.payment_status.upper()}

Delivery Address:
{instance.shipping_address_line_1}
{instance.shipping_address_line_2 or ''}
{instance.shipping_city}, {instance.shipping_state} - {instance.shipping_pincode}

Please log in to the admin panel to process this order:
https://mygiftstree.com/admin/orders/order/{instance.id}/change/

---
MyGiftTree Admin System
"""

            send_mail(
                subject=subject_admin,
                message=admin_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            logger.info(f'New order notification sent to admin: {settings.ADMIN_EMAIL}')

        except Exception as e:
            logger.error(f'Error sending order creation emails: {str(e)}', exc_info=True)


@receiver(pre_save, sender=Order)
def track_status_change(sender, instance, **kwargs):
    """
    Track if order status has changed to send status update email
    """
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """
    Signal handler for order status changes
    Send status update email to customer
    Schedules feedback email when order is delivered
    """
    if not created and hasattr(instance, '_old_status'):
        old_status = instance._old_status
        new_status = instance.status

        # If status actually changed
        if old_status != new_status:
            from django.core.mail import send_mail
            from django.conf import settings

            try:
                # Send status update email to customer
                status_messages = {
                    'pending': 'Your order is pending confirmation.',
                    'confirmed': '✅ Your order has been confirmed and is being processed!',
                    'processing': '📦 Your order is being prepared for shipment.',
                    'shipped': '🚚 Great news! Your order has been shipped.',
                    'delivered': '🎉 Your order has been delivered! Enjoy your purchase!',
                    'cancelled': '❌ Your order has been cancelled.',
                }

                status_message = status_messages.get(new_status, f'Your order status has been updated to {new_status}.')

                subject = f'Order Status Update - #{instance.order_number}'
                message = f"""
Hi {instance.billing_name},

{status_message}

Order Number: #{instance.order_number}
Status: {new_status.upper()}
{'Tracking Number: ' + instance.tracking_number if instance.tracking_number else ''}

View your order: https://mygiftstree.com/orders/{instance.order_number}/

Thank you for shopping with MyGiftTree!

Best regards,
MyGiftTree Team
"""

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.billing_email],
                    fail_silently=False,
                )
                logger.info(f'Status update email sent for order {instance.order_number}: {old_status} → {new_status}')

            except Exception as e:
                logger.error(f'Error sending status update email: {str(e)}', exc_info=True)

        # Check if order was just marked as delivered for feedback email
        if new_status == 'delivered' and not instance.feedback_email_sent:
            try:
                from .tasks import send_feedback_request_email
                # Schedule feedback email to be sent after 1 day
                send_feedback_request_email.apply_async(
                    args=[instance.id],
                    countdown=86400  # 24 hours in seconds
                )
            except Exception as e:
                logger.error(f'Error scheduling feedback email: {str(e)}', exc_info=True)


@receiver(post_save, sender=Order)
def order_delivered(sender, instance, created, **kwargs):
    """
    Signal handler when order is delivered
    Add bonus wallet coins for successful delivery
    """
    if not created:
        # Check if order was just marked as delivered
        if instance.status == 'delivered':
            try:
                # Give 10% of order value as bonus coins (max 50 coins)
                bonus_coins = min(int(instance.total_amount * 0.1), 50)

                if bonus_coins > 0:
                    wallet = instance.user.wallet
                    wallet.add_coins(
                        amount=bonus_coins,
                        description=f"Bonus coins for order #{instance.order_number}"
                    )

            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error adding bonus coins for order {instance.order_number}: {str(e)}', exc_info=True)
