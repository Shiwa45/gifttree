from django.db import models


class BaseModel(models.Model):
    """Abstract base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class SiteSettings(models.Model):
    """Global site configuration"""
    site_name = models.CharField(max_length=100, default="GiftTree")
    site_logo = models.ImageField(upload_to='site/', blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    free_delivery_above = models.DecimalField(max_digits=10, decimal_places=2, default=999)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('Only one SiteSettings instance is allowed')
        return super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get the site settings instance, create if doesn't exist"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'GiftTree',
                'contact_email': 'info@gifttree.com',
                'contact_phone': '+91-9876543210',
                'delivery_charge': 50.00,
                'free_delivery_above': 999.00,
            }
        )
        return settings