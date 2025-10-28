#!/usr/bin/env python
"""
Test email configuration
Run this to verify Gmail SMTP is working correctly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gifttree.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    """Send a test email"""
    print("="*60)
    print("Testing Email Configuration")
    print("="*60)
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"ADMIN_EMAIL: {settings.ADMIN_EMAIL}")
    print("="*60)
    
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("❌ ERROR: Email credentials not configured!")
        print("Please set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env file")
        return
    
    # Test 1: Send to admin
    try:
        print("\n📧 Sending test email to admin...")
        send_mail(
            subject='Test Email - MyGiftTree Email System',
            message='This is a test email. If you received this, your email configuration is working! 🎉',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        print(f"✅ Test email sent successfully to: {settings.ADMIN_EMAIL}")
        print("Check your inbox (and spam folder)")
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        print("\nCommon issues:")
        print("1. Using regular Gmail password instead of App Password")
        print("2. 2-Step Verification not enabled")
        print("3. Incorrect credentials in .env file")
        print("4. Firewall blocking SMTP connection")
        return
    
    # Test 2: Send to a custom email if provided
    import sys
    if len(sys.argv) > 1:
        test_recipient = sys.argv[1]
        try:
            print(f"\n📧 Sending test email to: {test_recipient}...")
            send_mail(
                subject='Test Email - MyGiftTree',
                message='This is a test email to verify your email address.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_recipient],
                fail_silently=False,
            )
            print(f"✅ Test email sent successfully to: {test_recipient}")
        except Exception as e:
            print(f"❌ Error sending to {test_recipient}: {str(e)}")
    
    print("\n" + "="*60)
    print("✅ Email configuration test completed!")
    print("="*60)

if __name__ == '__main__':
    test_email()

