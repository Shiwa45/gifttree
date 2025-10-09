# Phase 4: Advanced Features - Wallet, Payment & Automation
Timeline: Day 7-9
Priority: HIGH

## Overview
Implement wallet system, payment gateway, cart abandonment, country section, and automated emails.

## Task 4.1: Wallet System with 200 Coins

Issue: Need wallet system where new users get 200 coins

Files to Create:
- apps/wallet/ (NEW APP)
- apps/wallet/models.py
- apps/wallet/views.py
- apps/wallet/urls.py
- apps/wallet/admin.py
- apps/users/signals.py (NEW)
- templates/wallet/wallet_dashboard.html (NEW)

Step 1: Create Wallet App

python manage.py startapp wallet
mv wallet apps/

Step 2: Create Wallet Models in apps/wallet/models.py

from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel

User = get_user_model()

class Wallet(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=200.00)
    
    def __str__(self):
        return f"{self.user.email} - Balance: {self.balance}"
    
    def add_coins(self, amount, description=""):
        self.balance += amount
        self.save()
        WalletTransaction.objects.create(
            wallet=self,
            transaction_type='credit',
            amount=amount,
            description=description
        )
    
    def deduct_coins(self, amount, description=""):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            WalletTransaction.objects.create(
                wallet=self,
                transaction_type='debit',
                amount=amount,
                description=description
            )
            return True
        return False

class WalletTransaction(BaseModel):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.wallet.user.email} - {self.transaction_type} - {self.amount}"

Step 3: Auto-create Wallet on User Registration

Create apps/users/signals.py:

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from apps.wallet.models import Wallet

@receiver(post_save, sender=CustomUser)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance, balance=200.00)

Step 4: Connect Signals in apps/users/apps.py

from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    
    def ready(self):
        import apps.users.signals

Step 5: Create Wallet Views in apps/wallet/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wallet, WalletTransaction

@login_required
def wallet_dashboard(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = WalletTransaction.objects.filter(wallet=wallet)[:20]
    
    context = {
        'wallet': wallet,
        'transactions': transactions,
    }
    return render(request, 'wallet/wallet_dashboard.html', context)

Step 6: Create Wallet URLs in apps/wallet/urls.py

from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('', views.wallet_dashboard, name='dashboard'),
]

Step 7: Register in Admin - apps/wallet/admin.py

from django.contrib import admin
from .models import Wallet, WalletTransaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at']
    search_fields = ['user__email']

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'transaction_type', 'amount', 'created_at']
    list_filter = ['transaction_type', 'created_at']

Step 8: Add to INSTALLED_APPS in settings/base.py

INSTALLED_APPS = [
    # ... existing apps ...
    'apps.wallet',
]

Step 9: Include Wallet URLs in main urls.py

urlpatterns = [
    # ... existing patterns ...
    path('wallet/', include('apps.wallet.urls')),
]

Step 10: Display Wallet in Header

Update templates/includes/desktop_header.html:

{% if user.is_authenticated %}
<div class="wallet-display" onclick="window.location.href='{% url 'wallet:dashboard' %}'">
    <i class="fas fa-coins"></i>
    <span>{{ user.wallet.balance|floatformat:0 }} Coins</span>
</div>
{% endif %}

Add CSS:
.wallet-display {
    display: flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #FFD700, #FFA500);
    padding: 8px 16px;
    border-radius: 20px;
    color: #333;
    font-weight: 600;
    cursor: pointer;
}

## Task 4.2: Send by Country Section

Issue: Add country section to homepage footer

Files to Modify:
- apps/core/models.py
- templates/includes/footer.html (or base.html)
- apps/core/management/commands/populate_countries.py (NEW)

Step 1: Create Country Model in apps/core/models.py

class Country(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)
    flag_image = models.ImageField(upload_to='countries/', blank=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name

Step 2: Create Management Command

Create apps/core/management/commands/populate_countries.py:

from django.core.management.base import BaseCommand
from apps.core.models import Country

class Command(BaseCommand):
    help = 'Populate countries data'

    def handle(self, *args, **options):
        countries_data = [
            {'name': 'United Kingdom', 'code': 'UK', 'is_featured': True, 'sort_order': 1},
            {'name': 'United States', 'code': 'USA', 'is_featured': True, 'sort_order': 2},
            {'name': 'Canada', 'code': 'CAN', 'is_featured': True, 'sort_order': 3},
            {'name': 'Japan', 'code': 'JPN', 'is_featured': True, 'sort_order': 4},
            {'name': 'United Arab Emirates', 'code': 'UAE', 'is_featured': True, 'sort_order': 5},
        ]
        
        for data in countries_data:
            country, created = Country.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created: {country.name}'))

Step 3: Update Context Processor in apps/core/context_processors.py

def global_context(request):
    # existing code...
    
    from apps.core.models import Country
    featured_countries = Country.objects.filter(is_featured=True, is_active=True)
    
    return {
        'main_categories': main_categories,
        'cart_count': cart_count,
        'site_settings': SiteSettings.get_settings(),
        'featured_countries': featured_countries,  # ADD THIS
    }

Step 4: Add to Footer Template

In templates/includes/footer.html or templates/base.html footer:

<div class="footer-countries">
    <h4>We Deliver Worldwide</h4>
    <div class="country-flags">
        {% for country in featured_countries %}
        <a href="#" class="country-item" title="Send to {{ country.name }}">
            {% if country.flag_image %}
            <img src="{{ country.flag_image.url }}" alt="{{ country.name }}">
            {% else %}
            <img src="{% static 'images/countries/' %}{{ country.code|lower }}.png" alt="{{ country.name }}">
            {% endif %}
            <span>{{ country.code }}</span>
        </a>
        {% endfor %}
    </div>
</div>

Add CSS:
.footer-countries {
    text-align: center;
    padding: 30px 0;
    border-top: 1px solid rgba(255,255,255,0.1);
}

.country-flags {
    display: flex;
    justify-content: center;
    gap: 30px;
    flex-wrap: wrap;
}

.country-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: white;
}

.country-item img {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    object-fit: cover;
}

## Task 4.3: Payment Gateway Integration

Issue: Integrate Razorpay for payments

Files to Create/Modify:
- apps/orders/payment.py (NEW)
- apps/orders/views.py
- templates/orders/checkout.html (NEW)

Step 1: Install Razorpay

pip install razorpay

Add to requirements.txt:
razorpay==1.4.1

Step 2: Create Payment Handler in apps/orders/payment.py

import razorpay
from django.conf import settings

class RazorpayPayment:
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    
    def create_order(self, amount, order_number):
        data = {
            'amount': int(amount * 100),
            'currency': 'INR',
            'receipt': order_number,
        }
        return self.client.order.create(data=data)
    
    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        try:
            self.client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
            return True
        except:
            return False

Step 3: Add Checkout View in apps/orders/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .payment import RazorpayPayment
from .models import Order

@login_required
def checkout_view(request):
    # Get cart items
    cart = request.user.cart
    if not cart.items.exists():
        return redirect('cart:cart')
    
    if request.method == 'POST':
        # Create order
        order = Order.objects.create(
            user=request.user,
            subtotal=cart.total_price,
            total_amount=cart.total_price,
            # ... other fields from form
        )
        
        # Create Razorpay order
        payment = RazorpayPayment()
        razorpay_order = payment.create_order(
            amount=order.total_amount,
            order_number=order.order_number
        )
        
        context = {
            'order': order,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
        }
        return render(request, 'orders/payment.html', context)
    
    context = {
        'cart': cart,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def payment_callback(request):
    if request.method == 'POST':
        payment = RazorpayPayment()
        
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        if payment.verify_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
            # Update order status
            order = Order.objects.get(order_number=request.POST.get('order_number'))
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()
            
            return redirect('orders:order_detail', order_number=order.order_number)
    
    return redirect('cart:cart')

Step 4: Add URLs in apps/orders/urls.py

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('<str:order_number>/', views.order_detail, name='order_detail'),
]

## Task 4.4: Cart Abandonment System

Issue: Send email to users with abandoned carts

Files to Create/Modify:
- apps/cart/models.py
- apps/cart/tasks.py (NEW - requires Celery)
- templates/cart/emails/cart_abandonment.html (NEW)

Step 1: Update Cart Model in apps/cart/models.py

class Cart(BaseModel):
    # existing fields...
    
    abandonment_email_sent = models.BooleanField(default=False)
    abandonment_email_sent_at = models.DateTimeField(null=True, blank=True)
    
    def is_abandoned(self):
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.items.exists():
            return False
        
        time_threshold = timezone.now() - timedelta(hours=24)
        return self.updated_at < time_threshold and not self.abandonment_email_sent

Step 2: Install Celery (Optional - can use cron)

pip install celery redis django-celery-beat

Step 3: Create Celery Config in gifttree/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gifttree.settings.development')

app = Celery('gifttree')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

Step 4: Create Cart Task in apps/cart/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Cart

@shared_task
def send_cart_abandonment_emails():
    abandoned_carts = Cart.objects.filter(
        abandonment_email_sent=False,
        user__email__isnull=False
    )
    
    for cart in abandoned_carts:
        if cart.is_abandoned():
            context = {
                'user': cart.user,
                'cart': cart,
                'items': cart.items.all()
            }
            
            html_message = render_to_string(
                'cart/emails/cart_abandonment.html',
                context
            )
            
            send_mail(
                subject='You left items in your cart!',
                message='',
                from_email='support@mygifttree.com',
                recipient_list=[cart.user.email],
                html_message=html_message,
                fail_silently=True
            )
            
            cart.abandonment_email_sent = True
            cart.save()

## Task 4.5: Auto Feedback Email After Delivery

Issue: Send feedback email 2 hours after order delivered

Files to Create:
- apps/orders/signals.py (NEW)
- apps/orders/tasks.py (NEW)
- templates/orders/emails/feedback_request.html (NEW)

Step 1: Create Order Signals in apps/orders/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def send_feedback_request(sender, instance, created, **kwargs):
    if not created and instance.status == 'delivered':
        if not hasattr(instance, '_feedback_sent'):
            from datetime import timedelta
            from django.utils import timezone
            from apps.orders.tasks import send_order_feedback_email
            
            eta = timezone.now() + timedelta(hours=2)
            send_order_feedback_email.apply_async(
                args=[instance.id],
                eta=eta
            )
            instance._feedback_sent = True

Step 2: Create Feedback Task in apps/orders/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Order

@shared_task
def send_order_feedback_email(order_id):
    try:
        order = Order.objects.get(id=order_id)
        
        context = {
            'order': order,
            'user': order.user,
            'feedback_url': f'https://mygifttree.com/feedback/{order.order_number}/'
        }
        
        html_message = render_to_string(
            'orders/emails/feedback_request.html',
            context
        )
        
        send_mail(
            subject=f'How was your order #{order.order_number}?',
            message='',
            from_email='support@mygifttree.com',
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False
        )
        
    except Order.DoesNotExist:
        pass

Step 3: Connect Signals in apps/orders/apps.py

from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
    
    def ready(self):
        import apps.orders.signals

## Task 4.6: Personalized Gifts Delivery Time

Files to Modify:
- apps/products/models.py
- templates/products/product_detail.html

Step 1: Add Fields to Product Model

class Product(BaseModel):
    # existing fields...
    
    is_personalized = models.BooleanField(default=False)
    delivery_days = models.PositiveIntegerField(default=1)
    
    def get_delivery_text(self):
        if self.is_personalized:
            return f"{self.delivery_days} days delivery"
        elif self.stock_quantity > 0:
            return "Same day delivery available"
        return f"{self.delivery_days} days delivery"

Step 2: Update Product Detail Template

Add delivery badge in templates/products/product_detail.html:

<div class="delivery-badge">
    <i class="fas fa-shipping-fast"></i>
    <span>{{ product.get_delivery_text }}</span>
    {% if product.is_personalized %}
    <span class="personalized-tag">Personalized</span>
    {% endif %}
</div>

## Migration Commands

python manage.py makemigrations wallet
python manage.py makemigrations core
python manage.py makemigrations cart
python manage.py makemigrations products
python manage.py migrate

## Post-Migration Commands

# Populate countries
python manage.py populate_countries

# Create wallets for existing users
python manage.py shell
from apps.users.models import CustomUser
from apps.wallet.models import Wallet
for user in CustomUser.objects.all():
    Wallet.objects.get_or_create(user=user, defaults={'balance': 200.00})
exit()

## Testing Checklist

Desktop:
- User registration creates wallet with 200 coins
- Wallet balance shows in header
- Can view wallet dashboard
- Countries display in footer
- Payment gateway works
- Checkout flow complete

Mobile:
- Wallet display responsive
- Countries section responsive
- Payment form mobile-friendly

Admin:
- Can view/edit wallets
- Can view transactions
- Can manage countries

## Files Modified/Created Summary

New Apps:
- apps/wallet/

New Files:
1. apps/wallet/models.py
2. apps/wallet/views.py
3. apps/wallet/urls.py
4. apps/wallet/admin.py
5. apps/users/signals.py
6. apps/orders/payment.py
7. apps/orders/tasks.py
8. apps/orders/signals.py
9. apps/cart/tasks.py
10. apps/core/management/commands/populate_countries.py
11. gifttree/celery.py

Modified Files:
1. apps/core/models.py - Country model
2. apps/core/context_processors.py - Add countries
3. apps/cart/models.py - Abandonment fields
4. apps/products/models.py - Personalized fields
5. apps/orders/views.py - Checkout
6. apps/users/apps.py - Connect signals
7. apps/orders/apps.py - Connect signals
8. gifttree/settings/base.py - Add wallet app
9. gifttree/urls.py - Wallet URLs
10. templates/includes/desktop_header.html - Wallet display
11. templates/includes/footer.html - Countries section

Templates to Create:
- templates/wallet/wallet_dashboard.html
- templates/orders/checkout.html
- templates/cart/emails/cart_abandonment.html
- templates/orders/emails/feedback_request.html

Estimated Time: 12-15 hours
Risk Level: HIGH
Complexity: HIGH
Migrations: YES (multiple)
External Services: Razorpay, Celery/Redis