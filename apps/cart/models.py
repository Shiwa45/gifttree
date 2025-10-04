from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from apps.products.models import Product, ProductVariant

User = get_user_model()


class Cart(BaseModel):
    """Shopping cart for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    session_key = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return f"Cart for {self.user.email if self.user else self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(BaseModel):
    """Individual items in the cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    # Customization fields
    custom_message = models.TextField(blank=True, null=True, help_text="Custom message/text on product")
    custom_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name to be written (e.g., on cake)")
    custom_date = models.DateField(blank=True, null=True, help_text="Custom date (e.g., delivery date)")
    custom_flavor = models.CharField(max_length=100, blank=True, null=True, help_text="Flavor preference")
    custom_data = models.JSONField(blank=True, null=True, help_text="Additional customization data")

    class Meta:
        unique_together = []  # Removed unique_together to allow same product with different customizations

    def __str__(self):
        variant_name = f" ({self.variant.name})" if self.variant else ""
        custom_info = f" - Custom: {self.custom_name}" if self.custom_name else ""
        return f"{self.product.name}{variant_name}{custom_info} x {self.quantity}"

    @property
    def unit_price(self):
        if self.variant:
            return self.variant.final_price
        return self.product.current_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    @property
    def has_customization(self):
        """Check if item has any customization"""
        return bool(self.custom_message or self.custom_name or self.custom_date or self.custom_flavor or self.custom_data)