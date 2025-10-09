from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from apps.products.models import Product, ProductVariant

User = get_user_model()


class Order(BaseModel):
    """Customer orders"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('ready_to_ship', 'Ready to Ship'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    # Multi-tenant: Assigned seller
    assigned_seller = models.ForeignKey('users.Seller', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    assigned_location = models.ForeignKey('users.SellerLocation', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')

    # Billing Information
    billing_name = models.CharField(max_length=100)
    billing_email = models.EmailField()
    billing_phone = models.CharField(max_length=15)
    billing_address_line_1 = models.CharField(max_length=255)
    billing_address_line_2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_pincode = models.CharField(max_length=10)

    # Shipping Information
    shipping_name = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=15)
    shipping_address_line_1 = models.CharField(max_length=255)
    shipping_address_line_2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_pincode = models.CharField(max_length=10)

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Coupon fields
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Razorpay Payment Integration
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='cod', help_text="cod, razorpay, wallet")

    # Wallet payment
    wallet_coins_used = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Wallet coins used for this order")

    # Feedback email tracking
    feedback_email_sent = models.BooleanField(default=False)
    feedback_email_sent_at = models.DateTimeField(blank=True, null=True)

    # Special Instructions
    special_instructions = models.TextField(blank=True)
    delivery_date = models.DateField(blank=True, null=True)
    delivery_time_slot = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            import uuid
            self.order_number = f"GT{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(BaseModel):
    """Individual items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    product_name = models.CharField(max_length=200)  # Store name at time of order
    variant_name = models.CharField(max_length=100, blank=True)  # Store variant name at time of order
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Multi-tenant: Track which seller inventory this came from (disabled for now)
    # seller_inventory = models.ForeignKey('products.SellerInventory', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')

    def __str__(self):
        variant_str = f" ({self.variant_name})" if self.variant_name else ""
        return f"{self.product_name}{variant_str} x {self.quantity}"


class OrderTracking(BaseModel):
    """Order tracking information"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    message = models.TextField()
    location = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"
    


# Add to apps/orders/models.py (at the end)

from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Coupon(BaseModel):
    """Discount coupons for promotional campaigns"""
    
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Validity
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Total number of times this coupon can be used. Leave blank for unlimited."
    )
    usage_per_user = models.PositiveIntegerField(
        default=1,
        help_text="Number of times each user can use this coupon"
    )
    times_used = models.PositiveIntegerField(default=0, editable=False)
    
    # Restrictions
    minimum_order_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Minimum order value required to use this coupon"
    )
    maximum_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum discount amount (only for percentage discounts)"
    )
    
    # Category restrictions (optional - can be added later)
    # applicable_categories = models.ManyToManyField('products.Category', blank=True)
    
    # User restrictions
    first_order_only = models.BooleanField(
        default=False,
        help_text="Can only be used on first order"
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.get_discount_display()}"
    
    def get_discount_display(self):
        """Display discount in readable format"""
        if self.discount_type == 'percentage':
            return f"{self.discount_value}%"
        return f"₹{self.discount_value}"
    
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = timezone.now()
        
        # Check if active
        if not self.is_active:
            return False, "Coupon is not active"
        
        # Check date validity
        if now < self.valid_from:
            return False, f"Coupon will be valid from {self.valid_from.strftime('%d %B %Y')}"
        
        if now > self.valid_to:
            return False, "Coupon has expired"
        
        # Check usage limit
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False, "Coupon usage limit reached"
        
        return True, "Valid"
    
    def can_be_used_by_user(self, user, order_value):
        """Check if user can use this coupon"""
        # Check if coupon is valid
        is_valid, message = self.is_valid()
        if not is_valid:
            return False, message
        
        # Check minimum order value
        if order_value < self.minimum_order_value:
            return False, f"Minimum order value of ₹{self.minimum_order_value} required"
        
        # Check first order restriction
        if self.first_order_only:
            previous_orders = Order.objects.filter(
                user=user,
                status__in=['delivered', 'confirmed']
            ).exists()
            if previous_orders:
                return False, "This coupon is only valid for first orders"
        
        # Check user usage limit
        user_usage = CouponUsage.objects.filter(
            coupon=self,
            user=user
        ).count()
        
        if user_usage >= self.usage_per_user:
            return False, f"You have already used this coupon {self.usage_per_user} time(s)"
        
        return True, "Valid"
    
    def calculate_discount(self, order_value):
        """Calculate discount amount for given order value"""
        if self.discount_type == 'percentage':
            discount = (order_value * self.discount_value) / 100
            
            # Apply maximum discount cap if set
            if self.maximum_discount and discount > self.maximum_discount:
                discount = self.maximum_discount
            
            return discount
        else:
            # Fixed discount
            # Don't allow discount to exceed order value
            return min(self.discount_value, order_value)


class CouponUsage(BaseModel):
    """Track coupon usage by users"""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} used {self.coupon.code}"


# Update Order model to include coupon fields
# Add these fields to the existing Order model:
"""
Add to Order model:

    # Coupon fields
    coupon = models.ForeignKey(
        'Coupon', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='orders'
    )
    coupon_discount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
"""