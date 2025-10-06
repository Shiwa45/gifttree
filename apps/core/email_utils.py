"""
Email utility functions for sending emails
File: apps/core/email_utils.py
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site


def send_template_email(subject, template_name, context, recipient_list, from_email=None):
    """
    Send email using HTML template
    
    Args:
        subject: Email subject line
        template_name: Path to email template (without .html)
        context: Context dictionary for template
        recipient_list: List of recipient email addresses
        from_email: Sender email (optional, uses DEFAULT_FROM_EMAIL if not provided)
    
    Returns:
        Number of successfully sent emails
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    # Add site URL to context
    if 'site_url' not in context:
        context['site_url'] = settings.SITE_DOMAIN or 'http://localhost:8000'
    
    # Render HTML email
    html_content = render_to_string(f'emails/{template_name}.html', context)
    
    # Create email message
    email = EmailMultiAlternatives(
        subject=subject,
        body='Please view this email in an HTML-compatible email client.',
        from_email=from_email,
        to=recipient_list
    )
    
    email.attach_alternative(html_content, "text/html")
    
    try:
        return email.send()
    except Exception as e:
        print(f"Error sending email: {e}")
        return 0


# ============================================
# ORDER RELATED EMAILS
# ============================================

def send_order_confirmation_email(order):
    """Send order confirmation email to customer"""
    subject = f'Order Confirmation #{order.order_number} - GiftTree'
    
    context = {
        'order': order,
        'site_url': settings.SITE_DOMAIN or 'http://localhost:8000',
    }
    
    return send_template_email(
        subject=subject,
        template_name='order_confirmation',
        context=context,
        recipient_list=[order.billing_email]
    )


def send_order_status_email(order, tracking_number=None, courier_name=None, estimated_delivery=None, tracking_url=None):
    """Send order status update email to customer"""
    status_display = order.get_status_display()
    subject = f'Order #{order.order_number} - {status_display} - GiftTree'
    
    context = {
        'order': order,
        'status_display': status_display,
        'tracking_number': tracking_number,
        'courier_name': courier_name,
        'estimated_delivery': estimated_delivery,
        'tracking_url': tracking_url,
        'site_url': settings.SITE_DOMAIN or 'http://localhost:8000',
    }
    
    return send_template_email(
        subject=subject,
        template_name='order_status_update',
        context=context,
        recipient_list=[order.billing_email]
    )


def send_order_shipped_email(order, tracking_number, courier_name=None, estimated_delivery=None, tracking_url=None):
    """Send order shipped notification"""
    return send_order_status_email(
        order=order,
        tracking_number=tracking_number,
        courier_name=courier_name,
        estimated_delivery=estimated_delivery,
        tracking_url=tracking_url
    )


def send_order_delivered_email(order):
    """Send order delivered notification"""
    return send_order_status_email(order=order)


# ============================================
# USER RELATED EMAILS
# ============================================

def send_welcome_email(user):
    """Send welcome email to new user"""
    subject = 'Welcome to GiftTree! 🎉'
    
    context = {
        'user': user,
        'site_url': settings.SITE_DOMAIN or 'http://localhost:8000',
    }
    
    return send_template_email(
        subject=subject,
        template_name='welcome',
        context=context,
        recipient_list=[user.email]
    )


def send_password_reset_email(user, reset_url):
    """Send password reset email"""
    subject = 'Reset Your Password - GiftTree'
    
    context = {
        'user': user,
        'reset_url': reset_url,
        'site_url': settings.SITE_DOMAIN or 'http://localhost:8000',
    }
    
    return send_template_email(
        subject=subject,
        template_name='password_reset',
        context=context,
        recipient_list=[user.email]
    )


# ============================================
# PROMOTIONAL EMAILS
# ============================================

def send_promotional_email(subject, template_name, recipient_list, context=None):
    """Send promotional/marketing email"""
    if context is None:
        context = {}
    
    context['site_url'] = settings.SITE_DOMAIN or 'http://localhost:8000'
    
    return send_template_email(
        subject=subject,
        template_name=template_name,
        context=context,
        recipient_list=recipient_list
    )


def send_newsletter_email(subject, content, recipient_list):
    """Send newsletter email to subscribers"""
    context = {
        'content': content,
        'site_url': settings.SITE_DOMAIN or 'http://localhost:8000',
    }
    
    return send_template_email(
        subject=subject,
        template_name='newsletter',
        context=context,
        recipient_list=recipient_list
    )


# ============================================
# NOTIFICATION EMAILS
# ============================================

def send_low_stock_alert(product, admin_email):
    """Send low stock alert to admin"""
    subject = f'Low Stock Alert: {product.name}'
    
    context = {
        'product': product,
        'site_url': settings.SITE_DOMAIN or 'http://localhost:8000',
    }
    
    return send_template_email(
        subject=subject,
        template_name='admin/low_stock_alert',
        context=context,
        recipient_list=[admin_email]
    )


def send_new_review_notification(review, admin_email):
    """Send new review notification to admin"""
    subject = f'New Review for {review.product.name}'
    
    context = {
        'review': review,
        'product': review.product,
        'site_url': settings.SITE_DOMAIN or 'http://localhost:8000',
    }
    
    return send_template_email(
        subject=subject,
        template_name='admin/new_review',
        context=context,
        recipient_list=[admin_email]
    )


# ============================================
# BULK EMAIL FUNCTIONS
# ============================================

def send_bulk_email(subject, template_name, recipient_list, context=None):
    """
    Send bulk emails (for newsletters, announcements, etc.)
    Uses BCC to hide recipients from each other
    """
    if context is None:
        context = {}
    
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    context['site_url'] = settings.SITE_DOMAIN or 'http://localhost:8000'
    
    html_content = render_to_string(f'emails/{template_name}.html', context)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body='Please view this email in an HTML-compatible email client.',
        from_email=from_email,
        bcc=recipient_list  # Use BCC for bulk emails
    )
    
    email.attach_alternative(html_content, "text/html")
    
    try:
        return email.send()
    except Exception as e:
        print(f"Error sending bulk email: {e}")
        return 0


# ============================================
# HELPER FUNCTIONS
# ============================================

def validate_email_settings():
    """Validate that email settings are configured correctly"""
    required_settings = [
        'EMAIL_HOST',
        'EMAIL_PORT',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'DEFAULT_FROM_EMAIL',
    ]
    
    missing_settings = []
    for setting in required_settings:
        if not hasattr(settings, setting) or not getattr(settings, setting):
            missing_settings.append(setting)
    
    if missing_settings:
        print(f"Warning: Missing email settings: {', '.join(missing_settings)}")
        print("Emails will be logged to console instead of being sent.")
        return False
    
    return True


def test_email_configuration():
    """Test email configuration by sending a test email"""
    from django.core.mail import send_mail
    
    try:
        send_mail(
            'Test Email - GiftTree',
            'This is a test email from GiftTree.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        print("✅ Test email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Test email failed: {e}")
        return False