# Create new file: apps/core/email_utils.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_order_confirmation_email(order):
    """Send order confirmation email to customer"""
    try:
        subject = f'Order Confirmation - {order.order_number}'
        
        # Render HTML email template
        html_content = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'order_items': order.items.all(),
            'site_url': settings.SITE_DOMAIN,
        })
        
        # Create plain text version
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.billing_email]
        )
        
        # Attach HTML version
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send(fail_silently=False)
        
        return True
        
    except Exception as e:
        print(f"Error sending order confirmation email: {e}")
        return False


def send_order_status_update_email(order, status_message):
    """Send order status update email"""
    try:
        subject = f'Order Update - {order.order_number}'
        
        html_content = render_to_string('emails/order_status_update.html', {
            'order': order,
            'status_message': status_message,
            'site_url': settings.SITE_DOMAIN,
        })
        
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.billing_email]
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        return True
        
    except Exception as e:
        print(f"Error sending status update email: {e}")
        return False


def send_welcome_email(user):
    """Send welcome email to new users"""
    try:
        subject = 'Welcome to GiftTree!'
        
        html_content = render_to_string('emails/welcome.html', {
            'user': user,
            'site_url': settings.SITE_DOMAIN,
        })
        
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        return True
        
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


def send_password_reset_email(user, reset_link):
    """Send password reset email"""
    try:
        subject = 'Password Reset Request - GiftTree'
        
        html_content = render_to_string('emails/password_reset.html', {
            'user': user,
            'reset_link': reset_link,
            'site_url': settings.SITE_DOMAIN,
        })
        
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        return True
        
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False


def send_shipping_notification_email(order, tracking_info):
    """Send shipping notification with tracking details"""
    try:
        subject = f'Your Order is On The Way - {order.order_number}'
        
        html_content = render_to_string('emails/shipping_notification.html', {
            'order': order,
            'tracking_info': tracking_info,
            'site_url': settings.SITE_DOMAIN,
        })
        
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.billing_email]
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        return True
        
    except Exception as e:
        print(f"Error sending shipping notification: {e}")
        return False


def send_delivery_confirmation_email(order):
    """Send delivery confirmation email"""
    try:
        subject = f'Order Delivered - {order.order_number}'
        
        html_content = render_to_string('emails/delivery_confirmation.html', {
            'order': order,
            'site_url': settings.SITE_DOMAIN,
        })
        
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.billing_email]
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        return True
        
    except Exception as e:
        print(f"Error sending delivery confirmation: {e}")
        return False