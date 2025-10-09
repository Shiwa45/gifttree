from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Order


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """
    Signal handler for order status changes
    Schedules feedback email when order is delivered
    """
    if not created:
        # Check if order was just marked as delivered
        if instance.status == 'delivered' and not instance.feedback_email_sent:
            # Import here to avoid circular imports
            from .tasks import send_feedback_request_email

            # Schedule feedback email to be sent after 1 day
            send_feedback_request_email.apply_async(
                args=[instance.id],
                countdown=86400  # 24 hours in seconds
            )


@receiver(post_save, sender=Order)
def order_confirmed(sender, instance, created, **kwargs):
    """
    Signal handler when order is confirmed
    Send confirmation email and update wallet if coins were used
    """
    if not created:
        # Check if order was just confirmed
        if instance.status == 'confirmed' and instance.payment_status == 'paid':
            # Import here to avoid circular imports
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            from django.conf import settings

            try:
                # Send order confirmation email
                subject = f'Order Confirmed - #{instance.order_number}'

                html_message = render_to_string('emails/order_confirmation.html', {
                    'order': instance,
                    'site_name': getattr(settings, 'SITE_NAME', 'GiftTree'),
                })

                send_mail(
                    subject=subject,
                    message=f'Your order #{instance.order_number} has been confirmed.',
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.billing_email],
                    fail_silently=True,
                )

            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error sending order confirmation email: {str(e)}', exc_info=True)


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
