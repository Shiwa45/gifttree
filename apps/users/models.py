from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import BaseModel


class CustomUser(AbstractUser):
    """Custom user model with email as username"""
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(BaseModel):
    """Extended user profile information"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='users/avatars/', blank=True)
    bio = models.TextField(blank=True)
    preferred_language = models.CharField(max_length=10, default='en')

    def __str__(self):
        return f"{self.user.email}'s Profile"


class Address(BaseModel):
    """User delivery addresses"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=50)  # Home, Office, etc.
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.title} - {self.full_name}"

    def save(self, *args, **kwargs):
        # If this is set as default, unset all other default addresses for this user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)




# Add this to the existing apps/users/models.py file

from apps.products.models import Product

class Wishlist(BaseModel):
    """User wishlist for products"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"


class Seller(BaseModel):
    """Seller/Vendor model for multi-tenant system"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='seller_profile')
    business_name = models.CharField(max_length=200)
    business_email = models.EmailField()
    business_phone = models.CharField(max_length=15)

    # Business details
    gst_number = models.CharField(max_length=15, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)

    # Bank details
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=30, blank=True)
    ifsc_code = models.CharField(max_length=11, blank=True)

    # Commission
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)

    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['business_name']

    def __str__(self):
        return self.business_name


class SellerLocation(BaseModel):
    """Physical locations/warehouses of sellers"""
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=100, help_text="Warehouse/Store name")

    # Address
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)

    # Contact
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField(blank=True)

    # Service area - pincodes this location can deliver to
    serviceable_pincodes = models.ManyToManyField('Pincode', related_name='serviced_by_locations', blank=True)

    # Settings
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-is_primary', 'name']
        unique_together = ['seller', 'name']

    def __str__(self):
        return f"{self.seller.business_name} - {self.name}"

    def save(self, *args, **kwargs):
        # If this is set as primary, unset all other primary locations for this seller
        if self.is_primary:
            SellerLocation.objects.filter(seller=self.seller, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class Pincode(BaseModel):
    """Indian Pincode database"""
    pincode = models.CharField(max_length=6, unique=True, db_index=True)
    area = models.CharField(max_length=200, blank=True)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    # Delivery settings
    is_serviceable = models.BooleanField(default=True)
    delivery_days = models.PositiveIntegerField(default=3, help_text="Standard delivery days")

    class Meta:
        ordering = ['pincode']

    def __str__(self):
        return f"{self.pincode} - {self.city}, {self.state}"