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
    site_name = models.CharField(max_length=100, default="MyGiftTree")
    site_logo = models.ImageField(upload_to='site/', blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    free_delivery_above = models.DecimalField(max_digits=10, decimal_places=2, default=999)
    copyright_text = models.CharField(max_length=200, default="© 2014-2025 MyGiftTree. All rights reserved.")
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
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
                'site_name': 'MyGiftTree',
                'contact_email': 'support@mygifttree.com',
                'contact_phone': '+91-9351221905',
                'delivery_charge': 50.00,
                'free_delivery_above': 999.00,
                'copyright_text': '© 2014-2025 MyGiftTree. All rights reserved.',
            }
        )
        return settings


class Country(BaseModel):
    """Countries for international delivery"""
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


class BannerImage(BaseModel):
    """Homepage banner/slider images"""
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    mobile_image = models.ImageField(upload_to='banners/mobile/', blank=True, null=True, help_text="Optional mobile-optimized image")
    link_url = models.URLField(blank=True, help_text="URL to navigate when banner is clicked")
    button_text = models.CharField(max_length=50, blank=True, help_text="Text for call-to-action button")
    sort_order = models.PositiveIntegerField(default=0, help_text="Lower number = higher priority")

    class Meta:
        ordering = ['sort_order', '-created_at']
        verbose_name = "Banner Image"
        verbose_name_plural = "Banner Images"

    def __str__(self):
        return self.title