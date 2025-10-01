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