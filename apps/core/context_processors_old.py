from apps.products.models import Category, Product, Occasion
from apps.products.services.menu_builder import menu_builder
from django.core.cache import cache


def global_context(request):
    """
    Global context processor to provide common data to all templates
    """
    # Use Menu Builder Service for better performance and caching
    try:
        main_categories = menu_builder.build_mega_menu()
        
        # Convert to objects for template compatibility
        menu_objects = []
        for category_data in main_categories:
            # Create a simple object to hold the data
            class MenuCategoryObject:
                def __init__(self, data):
                    self.id = data['id']
                    self.name = data['name']
                    self.slug = data['slug']
                    self.icon = data['icon']
                    self.sort_order = data['sort_order']
                    self.menu_sections = []
                    self.featured_products = []
                    
                    # Convert sections
                    for section_data in data['sections']:
                        section_obj = type('MenuSection', (), {})()
                        section_obj.id = section_data['id']
                        section_obj.name = section_data['name']
                        section_obj.slug = section_data['slug']
                        section_obj.section_type = section_data['section_type']
                        section_obj.sort_order = section_data['sort_order']
                        section_obj.items = []
                        
                        # Convert items
                        for item_data in section_data['items']:
                            item_obj = type('MenuItem', (), {})()
                            item_obj.id = item_data['id']
                            item_obj.name = item_data['name']
                            item_obj.slug = item_data['slug']
                            
                            # Add badges if present
                            if 'badges' in item_data:
                                badge_objects = []
                                for badge_data in item_data['badges']:
                                    badge_obj = type('MenuBadge', (), {})()
                                    badge_obj.name = badge_data['name']
                                    badge_obj.color = badge_data['color']
                                    badge_obj.background_color = badge_data['background_color']
                                    badge_obj.css_class = badge_data.get('css_class', '')
                                    badge_objects.append(badge_obj)
                                
                                # Create a mock queryset-like object
                                class BadgeQuerySet:
                                    def __init__(self, badges):
                                        self._badges = badges
                                    
                                    def all(self):
                                        return self._badges
                                
                                item_obj.badges = BadgeQuerySet(badge_objects)
                            else:
                                item_obj.badges = type('EmptyQuerySet', (), {'all': lambda: []})()
                            
                            section_obj.items.append(item_obj)
                        
                        self.menu_sections.append(section_obj)
                    
                    # Convert featured products
                    for product_data in data['featured_products']:
                        product_obj = type('FeaturedProduct', (), {})()
                        product_obj.id = product_data['id']
                        product_obj.name = product_data['name']
                        product_obj.slug = product_data['slug']
                        product_obj.current_price = product_data['current_price']
                        product_obj.discount_percentage = product_data['discount_percentage']
                        
                        # Mock primary_image
                        if product_data['image_url']:
                            primary_image = type('PrimaryImage', (), {})()
                            primary_image.get_image_url = product_data['image_url']
                            product_obj.primary_image = primary_image
                        else:
                            product_obj.primary_image = None
                        
                        # Mock get_absolute_url method
                        product_obj.get_absolute_url = lambda url=product_data['absolute_url']: url
                        
                        self.featured_products.append(product_obj)
            
            menu_objects.append(MenuCategoryObject(category_data))
        
        main_categories = menu_objects
        
    except Exception as e:
        print(f"Error loading menu categories: {e}")
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