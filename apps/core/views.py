from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q
from django.http import HttpResponse
from django.template import loader
from .models import SiteSettings, BannerImage
from apps.products.models import Product, Category, Occasion
from apps.blog.models import BlogPost


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

        # Banner images for homepage slider
        context['banner_images'] = BannerImage.objects.filter(is_active=True)[:5]

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
        # Quick occasions for action grid with product count
        quick_occasions = Occasion.objects.filter(
            is_featured=True,
            is_active=True
        ).prefetch_related('products')[:9]
    except:
        quick_occasions = Occasion.objects.none()
    
    try:
        site_settings = SiteSettings.get_settings()
    except:
        site_settings = None

    # Get category-specific products for "Send X" sections
    try:
        # Cakes - Get products from Cakes category
        cake_products = Product.objects.filter(
            Q(category__name__icontains='cake') | Q(name__icontains='cake'),
            is_active=True,
            published=True
        ).select_related('category').prefetch_related('images').distinct()[:8]
    except:
        cake_products = Product.objects.none()

    try:
        # Flowers - Get products from Flowers category
        flower_products = Product.objects.filter(
            Q(category__name__icontains='flower') | Q(name__icontains='flower') | Q(name__icontains='rose') | Q(name__icontains='bouquet'),
            is_active=True,
            published=True
        ).select_related('category').prefetch_related('images').distinct()[:8]
    except:
        flower_products = Product.objects.none()

    try:
        # Plants - Get products from Plants category
        plant_products = Product.objects.filter(
            Q(category__name__icontains='plant') | Q(name__icontains='plant') | Q(name__icontains='bamboo') | Q(name__icontains='bonsai'),
            is_active=True,
            published=True
        ).select_related('category').prefetch_related('images').distinct()[:8]
    except:
        plant_products = Product.objects.none()

    try:
        # Gifts - Get products from various gift categories
        gift_products = Product.objects.filter(
            Q(category__name__icontains='gift') | Q(category__name__icontains='personalized') |
            Q(category__name__icontains='chocolate') | Q(category__name__icontains='hamper') |
            Q(name__icontains='personalized') | Q(name__icontains='mug') | Q(name__icontains='cushion'),
            is_active=True,
            published=True
        ).select_related('category').prefetch_related('images').distinct()[:8]
    except:
        gift_products = Product.objects.none()

    try:
        # Recent blog posts for homepage
        recent_blog_posts = BlogPost.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('tags')[:3]
    except:
        recent_blog_posts = BlogPost.objects.none()

    context = {
        'site_settings': site_settings,
        'featured_products': featured_products,
        'bestseller_products': bestseller_products,
        'quick_occasions': quick_occasions,
        'has_featured_products': featured_products.exists(),
        'has_bestseller_products': bestseller_products.exists(),
        'has_occasions': quick_occasions.exists(),
        # Category-specific products
        'cake_products': cake_products,
        'flower_products': flower_products,
        'plant_products': plant_products,
        'gift_products': gift_products,
        # Blog posts
        'recent_blog_posts': recent_blog_posts,
    }
    return render(request, 'core/home.html', context)


def offers_view(request):
    """Display current offers and promotions"""

    # Get products with discounts
    featured_offers = Product.objects.filter(
        is_featured=True,
        discount_price__isnull=False,
        is_active=True,
        stock_quantity__gt=0
    ).select_related('category').prefetch_related('images')[:12]

    bestseller_offers = Product.objects.filter(
        is_bestseller=True,
        discount_price__isnull=False,
        is_active=True,
        stock_quantity__gt=0
    ).select_related('category').prefetch_related('images')[:12]

    all_offers = Product.objects.filter(
        discount_price__isnull=False,
        is_active=True,
        stock_quantity__gt=0
    ).select_related('category').prefetch_related('images')[:24]

    total_savings = sum([
        (p.base_price - p.discount_price) for p in all_offers
    ])

    context = {
        'featured_offers': featured_offers,
        'bestseller_offers': bestseller_offers,
        'all_offers': all_offers,
        'total_savings': total_savings,
        'offers_count': all_offers.count(),
    }

    return render(request, 'core/offers.html', context)


def sitemap_view(request):
    """Generate XML sitemap for SEO"""
    template = loader.get_template('sitemap.xml')

    # Get all active categories and products
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True, published=True)[:500]  # Limit to 500 products

    context = {
        'categories': categories,
        'products': products,
        'domain': request.get_host(),
        'scheme': request.scheme,
    }

    return HttpResponse(
        template.render(context, request),
        content_type='application/xml'
    )