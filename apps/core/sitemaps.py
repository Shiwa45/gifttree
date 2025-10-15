from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from apps.products.models import Product, Category, ProductType, Collection, Occasion, Recipient, DeliveryLocation
from apps.blog.models import BlogPost
from apps.core.models import Country


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return [
            'core:home',
            'core:about_us',
            'core:contact_us',
            'core:faq',
            'core:privacy_policy',
            'core:terms_conditions',
            'products:product_list',
            'blog:blog_list',
            'users:login',
            'users:register',
        ]
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return timezone.now()


class ProductSitemap(Sitemap):
    """Sitemap for all products"""
    changefreq = 'daily'
    priority = 0.9
    
    def items(self):
        return Product.objects.filter(
            is_active=True,
            published=True
        ).select_related('category')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    """Sitemap for product categories"""
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):
        return Category.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class ProductTypeSitemap(Sitemap):
    """Sitemap for product types"""
    changefreq = 'weekly'
    priority = 0.7
    
    def items(self):
        return ProductType.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class CollectionSitemap(Sitemap):
    """Sitemap for product collections"""
    changefreq = 'weekly'
    priority = 0.7
    
    def items(self):
        return Collection.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class OccasionSitemap(Sitemap):
    """Sitemap for occasions"""
    changefreq = 'monthly'
    priority = 0.6
    
    def items(self):
        return Occasion.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class RecipientSitemap(Sitemap):
    """Sitemap for recipients"""
    changefreq = 'monthly'
    priority = 0.6
    
    def items(self):
        return Recipient.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class DeliveryLocationSitemap(Sitemap):
    """Sitemap for delivery locations"""
    changefreq = 'monthly'
    priority = 0.6
    
    def items(self):
        return DeliveryLocation.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class CountrySitemap(Sitemap):
    """Sitemap for worldwide delivery countries"""
    changefreq = 'monthly'
    priority = 0.5
    
    def items(self):
        return Country.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return reverse('core:country_products', kwargs={'country_code': obj.code.lower()})


class BlogSitemap(Sitemap):
    """Sitemap for blog posts"""
    changefreq = 'weekly'
    priority = 0.6
    
    def items(self):
        return BlogPost.objects.filter(status='published')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


# Sitemap index
sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'product_types': ProductTypeSitemap,
    'collections': CollectionSitemap,
    'occasions': OccasionSitemap,
    'recipients': RecipientSitemap,
    'delivery_locations': DeliveryLocationSitemap,
    'countries': CountrySitemap,
    'blog': BlogSitemap,
}
