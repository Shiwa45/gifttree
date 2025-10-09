from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_feedback_request_email(order_id):
    """
    Send feedback request email after order is delivered
    Celery task to be scheduled 24 hours after delivery
    """
    from .models import Order

    try:
        order = Order.objects.get(id=order_id)

        # Check if feedback email already sent
        if order.feedback_email_sent:
            logger.info(f'Feedback email already sent for order {order.order_number}')
            return

        # Check if order is delivered
        if order.status != 'delivered':
            logger.info(f'Order {order.order_number} not delivered yet, skipping feedback email')
            return

        # Render email template
        subject = f'How was your experience? - Order #{order.order_number}'

        html_message = render_to_string('emails/feedback_request.html', {
            'order': order,
            'user': order.user,
            'site_name': getattr(settings, 'SITE_NAME', 'GiftTree'),
            'feedback_url': f"{getattr(settings, 'SITE_DOMAIN', '')}/orders/{order.order_number}/feedback/",
        })

        # Send email
        send_mail(
            subject=subject,
            message=f'We would love to hear about your experience with order #{order.order_number}.',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.billing_email],
            fail_silently=False,
        )

        # Mark feedback email as sent
        order.feedback_email_sent = True
        order.feedback_email_sent_at = timezone.now()
        order.save(update_fields=['feedback_email_sent', 'feedback_email_sent_at'])

        logger.info(f'Feedback email sent for order {order.order_number}')

    except Order.DoesNotExist:
        logger.error(f'Order with id {order_id} not found')
    except Exception as e:
        logger.error(f'Error sending feedback email for order {order_id}: {str(e)}', exc_info=True)
        raise


@shared_task
def check_abandoned_carts():
    """
    Check for abandoned carts and send reminder emails
    Should be run periodically (e.g., every 1 hour via Celery Beat)
    """
    from apps.cart.models import Cart

    try:
        # Find carts that:
        # 1. Have items
        # 2. Haven't been updated in last 24 hours
        # 3. Haven't received abandonment email yet
        # 4. Belong to authenticated users

        cutoff_time = timezone.now() - timedelta(hours=24)

        abandoned_carts = Cart.objects.filter(
            abandonment_email_sent=False,
            last_activity__lt=cutoff_time,
            user__isnull=False,
            items__isnull=False
        ).distinct()

        count = 0
        for cart in abandoned_carts:
            # Check if cart has items
            if cart.items.exists():
                send_cart_abandonment_email.delay(cart.id)
                count += 1

        logger.info(f'Scheduled cart abandonment emails for {count} carts')
        return f'Processed {count} abandoned carts'

    except Exception as e:
        logger.error(f'Error checking abandoned carts: {str(e)}', exc_info=True)
        raise


@shared_task
def send_cart_abandonment_email(cart_id):
    """
    Send cart abandonment reminder email
    """
    from apps.cart.models import Cart

    try:
        cart = Cart.objects.get(id=cart_id)

        # Check if email already sent
        if cart.abandonment_email_sent:
            logger.info(f'Abandonment email already sent for cart {cart_id}')
            return

        # Check if cart still has items
        if not cart.items.exists():
            logger.info(f'Cart {cart_id} is empty, skipping abandonment email')
            return

        # Check if user exists
        if not cart.user:
            logger.info(f'Cart {cart_id} has no user, skipping abandonment email')
            return

        # Render email template
        subject = "You left something behind! Complete your order"

        html_message = render_to_string('emails/cart_abandonment.html', {
            'cart': cart,
            'user': cart.user,
            'items': cart.items.all()[:5],  # Show first 5 items
            'site_name': getattr(settings, 'SITE_NAME', 'GiftTree'),
            'cart_url': f"{getattr(settings, 'SITE_DOMAIN', '')}/cart/",
        })

        # Send email
        send_mail(
            subject=subject,
            message=f'You have {cart.total_items} items waiting in your cart!',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cart.user.email],
            fail_silently=False,
        )

        # Mark email as sent
        cart.abandonment_email_sent = True
        cart.abandonment_email_sent_at = timezone.now()
        cart.save(update_fields=['abandonment_email_sent', 'abandonment_email_sent_at'])

        logger.info(f'Cart abandonment email sent for cart {cart_id}')

    except Cart.DoesNotExist:
        logger.error(f'Cart with id {cart_id} not found')
    except Exception as e:
        logger.error(f'Error sending cart abandonment email for cart {cart_id}: {str(e)}', exc_info=True)
        raise


@shared_task
def send_order_status_update_email(order_id, status, message):
    """
    Send order status update email to customer
    """
    from .models import Order

    try:
        order = Order.objects.get(id=order_id)

        # Render email template
        subject = f'Order Update - #{order.order_number}'

        html_message = render_to_string('emails/order_status_update.html', {
            'order': order,
            'status': status,
            'status_display': dict(Order.STATUS_CHOICES).get(status, status),
            'message': message,
            'site_name': getattr(settings, 'SITE_NAME', 'GiftTree'),
            'track_url': f"{getattr(settings, 'SITE_DOMAIN', '')}/orders/{order.order_number}/",
        })

        # Send email
        send_mail(
            subject=subject,
            message=message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.billing_email],
            fail_silently=False,
        )

        logger.info(f'Status update email sent for order {order.order_number}: {status}')

    except Order.DoesNotExist:
        logger.error(f'Order with id {order_id} not found')
    except Exception as e:
        logger.error(f'Error sending status update email for order {order_id}: {str(e)}', exc_info=True)
        raise
