from django.shortcuts import render
from django.views.generic import TemplateView
from .models import SiteSettings
from apps.products.models import Product, Category, Occasion


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Site settings
        context['site_settings'] = SiteSettings.get_settings()
        
        # Featured products with optimized queries
        context['featured_products'] = Product.objects.filter(
            is_featured=True, 
            is_active=True
        ).select_related('category').prefetch_related('images')[:8]
        
        # Bestseller products with optimized queries
        context['bestseller_products'] = Product.objects.filter(
            is_bestseller=True, 
            is_active=True
        ).select_related('category').prefetch_related('images')[:8]
        
        # Quick categories for action grid with product count
        context['quick_categories'] = Category.objects.filter(
            is_featured=True,
            is_active=True
        ).prefetch_related('products')[:8]
        
        # Banner images (if you have a banner model, otherwise will use defaults)
        # context['banner_images'] = BannerImage.objects.filter(is_active=True)[:4]
        
        return context


def home_view(request):
    """Simple home view with enhanced context and error handling"""
    try:
        # Featured products with optimized queries
        featured_products = Product.objects.filter(
            is_featured=True, 
            is_active=True
        ).select_related('category').prefetch_related('images')[:8]
    except:
        featured_products = Product.objects.none()
    
    try:
        # Bestseller products with optimized queries
        bestseller_products = Product.objects.filter(
            is_bestseller=True, 
            is_active=True
        ).select_related('category').prefetch_related('images')[:8]
    except:
        bestseller_products = Product.objects.none()
    
    try:
        # Quick categories for action grid with product count
        quick_categories = Category.objects.filter(
            is_featured=True,
            is_active=True
        ).prefetch_related('products')[:8]
    except:
        quick_categories = Category.objects.none()
    
    try:
        site_settings = SiteSettings.get_settings()
    except:
        site_settings = None
    
    context = {
        'site_settings': site_settings,
        'featured_products': featured_products,
        'bestseller_products': bestseller_products,
        'quick_categories': quick_categories,
        'has_featured_products': featured_products.exists(),
        'has_bestseller_products': bestseller_products.exists(),
        'has_categories': quick_categories.exists(),
    }
    return render(request, 'core/home.html', context)