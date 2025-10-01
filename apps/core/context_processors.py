from apps.products.models import Category, Product, Occasion
from django.core.cache import cache


def global_context(request):
    """
    Global context processor to provide common data to all templates
    """
    # Cache main categories with their related data for better performance
    cache_key = 'main_categories_nav_full'
    main_categories = cache.get(cache_key)
    
    if main_categories is None:
        try:
            main_categories = Category.objects.filter(
                parent=None,
                is_active=True
            ).prefetch_related(
                'children',
                'products__images',  # Prefetch product images
                'products__occasions'  # Prefetch product occasions
            ).select_related()[:6]
            
            # For each category, get its featured products and occasions
            for category in main_categories:
                # Get featured products for this category
                category.featured_products = category.products.filter(
                    is_featured=True,
                    is_active=True
                )[:3]
                
                # Get occasions related to products in this category
                category.category_occasions = Occasion.objects.filter(
                    products__category=category,
                    is_active=True
                ).distinct()[:6]
            
            # Cache for 1 hour
            cache.set(cache_key, main_categories, 3600)
        except Exception as e:
            print(f"Error loading categories: {e}")
            main_categories = []
    
    # Cache general occasions for fallback
    cache_key_occasions = 'occasions_nav'
    main_occasions = cache.get(cache_key_occasions)
    
    if main_occasions is None:
        try:
            main_occasions = Occasion.objects.filter(
                is_active=True,
                is_featured=True
            )[:6]
            cache.set(cache_key_occasions, main_occasions, 3600)
        except:
            main_occasions = []
    
    # Get cart count from session or localStorage
    cart_count = 0
    try:
        if hasattr(request, 'session') and 'cart' in request.session:
            cart_count = sum(item.get('quantity', 0) for item in request.session['cart'].values())
    except:
        cart_count = 0
    
    return {
        'main_categories': main_categories,
        'main_occasions': main_occasions,
        'cart_count': cart_count,
    }