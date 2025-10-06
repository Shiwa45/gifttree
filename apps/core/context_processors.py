from apps.products.models import Category, Product, Occasion, MenuCategory
from django.core.cache import cache


class MenuSection:
    def __init__(self, name, items, section_type='by_type'):
        self.name = name
        self.items = items
        self.section_type = section_type


class MenuItem:
    def __init__(self, name, slug=None, badges=None):
        self.name = name
        self.slug = slug or name.lower().replace(' ', '-').replace('&', 'and').replace("'", "")
        self.badges = badges or []


def global_context(request):
    """
    Global context processor to provide common data to all templates
    """
    # Cache main menu categories with their related data for better performance
    cache_key = 'main_menu_categories_nav_full'
    main_categories = cache.get(cache_key)
    
    if main_categories is None:
        try:
            main_categories = MenuCategory.objects.filter(
                is_active=True,
                show_in_mega_menu=True
            ).order_by('sort_order')[:10]  # Get all 10 main categories
            
            # For each category, build the EXACT menu structure as specified
            for category in main_categories:
                if category.slug == 'flowers':
                    category.menu_sections = _build_flowers_menu()
                elif category.slug == 'cakes':
                    category.menu_sections = _build_cakes_menu()
                elif category.slug == 'combos':
                    category.menu_sections = _build_combos_menu()
                elif category.slug == 'personalised':
                    category.menu_sections = _build_personalised_menu()
                elif category.slug == 'birthday':
                    category.menu_sections = _build_birthday_menu()
                elif category.slug == 'anniversary':
                    category.menu_sections = _build_anniversary_menu()
                elif category.slug == 'plants':
                    category.menu_sections = _build_plants_menu()
                elif category.slug == 'gifts':
                    category.menu_sections = _build_gifts_menu()
                elif category.slug == 'international':
                    category.menu_sections = _build_international_menu()
                elif category.slug == 'occasions':
                    category.menu_sections = _build_occasions_menu()
                else:
                    category.menu_sections = []
                
                # Get featured products for this category
                try:
                    old_category = Category.objects.filter(
                        slug=category.slug,
                        is_active=True
                    ).first()
                    
                    if old_category:
                        category.featured_products = old_category.products.filter(
                            is_featured=True,
                            is_active=True
                        )[:3]
                    else:
                        category.featured_products = []
                except:
                    category.featured_products = []
            
            # Cache for 1 hour
            cache.set(cache_key, main_categories, 3600)
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
    
    # Get cart count from database or session
    cart_count = 0
    try:
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Database cart for logged-in users
            from apps.cart.models import Cart
            try:
                cart = Cart.objects.get(user=request.user)
                cart_count = cart.total_items
            except Cart.DoesNotExist:
                cart_count = 0
        elif hasattr(request, 'session') and 'cart' in request.session:
            # Session cart for anonymous users
            cart_count = sum(item.get('quantity', 0) for item in request.session['cart'].values())
    except:
        cart_count = 0
    
    return {
        'main_categories': main_categories,
        'main_occasions': main_occasions,
        'cart_count': cart_count,
    }


def _build_flowers_menu():
    """Build exact flowers menu as specified"""
    return [
        MenuSection("By Type", [
            MenuItem("Roses"),
            MenuItem("Lilies"),
            MenuItem("Orchids"),
            MenuItem("Carnations"),
            MenuItem("Tuberose"),
            MenuItem("Gerberas"),
            MenuItem("Sunflowers", badges=[{"name": "Must Try", "background_color": "#4CAF50", "color": "#FFFFFF"}]),
            MenuItem("Mixed Flowers"),
            MenuItem("Hydrangea", badges=[{"name": "New", "background_color": "#FF4444", "color": "#FFFFFF"}]),
            MenuItem("Exotic Flowers", badges=[{"name": "Premium", "background_color": "#9C27B0", "color": "#FFFFFF"}]),
        ], section_type='by_type'),
        MenuSection("Collection", [
            MenuItem("Bestseller"),
            MenuItem("Korean Paper Bouquets", badges=[{"name": "New", "background_color": "#FF4444", "color": "#FFFFFF"}]),
            MenuItem("Crochet Flowers", badges=[{"name": "New", "background_color": "#FF4444", "color": "#FFFFFF"}]),
            MenuItem("MFT Signature Boxes"),
            MenuItem("Floral Bouquets", badges=[{"name": "Hot Selling", "background_color": "#FF6600", "color": "#FFFFFF"}]),
            MenuItem("Premium Basket Arrangements"),
            MenuItem("Floral Hampers", badges=[{"name": "New", "background_color": "#FF4444", "color": "#FFFFFF"}]),
            MenuItem("Premium Vases"),
            MenuItem("All Flowers"),
        ], section_type='collection'),
        MenuSection("Flowers For", [
            MenuItem("Girlfriend"),
            MenuItem("Wife"),
            MenuItem("Husband"),
            MenuItem("Parents"),
            MenuItem("Corporate"),
            MenuItem("Boyfriend"),
            MenuItem("Brother"),
            MenuItem("Sister"),
        ], section_type='for_whom'),
        MenuSection("Flowers By Occasion", [
            MenuItem("Birthday"),
            MenuItem("Anniversary"),
            MenuItem("Condolence"),
            MenuItem("Congratulations"),
            MenuItem("Love & Romance"),
            MenuItem("Get Well Soon"),
            MenuItem("I Am Sorry"),
            MenuItem("Thank You"),
            MenuItem("New Born"),
        ], section_type='by_occasion'),
        MenuSection("Flowers to", [
            MenuItem("Delhi"),
            MenuItem("Mumbai"),
            MenuItem("Bangalore"),
            MenuItem("Chennai"),
            MenuItem("Kolkata"),
            MenuItem("Hyderabad"),
            MenuItem("Pune"),
            MenuItem("Gurgaon"),
            MenuItem("Noida"),
            MenuItem("Jaipur"),
            MenuItem("Lucknow"),
            MenuItem("All Cities"),
        ], section_type='deliver_to'),
    ]


def _build_cakes_menu():
    """Build exact cakes menu as specified"""
    return [
        MenuSection("By Flavour", [
            MenuItem("All Cakes"),
            MenuItem("Chocolate Cakes"),
            MenuItem("Blackforest Cakes"),
            MenuItem("Truffle Cakes", badges=[{"name": "Bestseller", "background_color": "#2196F3", "color": "#FFFFFF"}]),
            MenuItem("Butterscotch Cakes"),
            MenuItem("Vanilla Cakes"),
            MenuItem("Red Velvet Cakes", badges=[{"name": "Must Try", "background_color": "#4CAF50", "color": "#FFFFFF"}]),
            MenuItem("Pineapple Cakes"),
            MenuItem("Fruit Cakes"),
            MenuItem("Coffee Cakes"),
            MenuItem("Strawberry Cakes"),
            MenuItem("Cheese Cakes", badges=[{"name": "Premium", "background_color": "#9C27B0", "color": "#FFFFFF"}]),
        ], section_type='by_type'),
        MenuSection("By Type", [
            MenuItem("Eggless Cakes", badges=[{"name": "Must Try", "background_color": "#4CAF50", "color": "#FFFFFF"}]),
            MenuItem("Sugarfree Cakes", badges=[{"name": "Hot Selling", "background_color": "#FF6600", "color": "#FFFFFF"}]),
            MenuItem("Regular Cakes"),
            MenuItem("Photo Cakes", badges=[{"name": "Trending", "background_color": "#FF9800", "color": "#FFFFFF"}]),
            MenuItem("Premium Cakes"),
            MenuItem("Cup Cakes"),
            MenuItem("Tier Cakes"),
            MenuItem("Cake Jars"),
            MenuItem("Exotic Cakes"),
        ], section_type='by_type'),
        MenuSection("By Design", [
            MenuItem("Cartoon Cakes", badges=[{"name": "New", "background_color": "#FF4444", "color": "#FFFFFF"}]),
            MenuItem("Pinata Cakes", badges=[{"name": "Hot Selling", "background_color": "#FF6600", "color": "#FFFFFF"}]),
            MenuItem("Pull Up Cakes", badges=[{"name": "Trending", "background_color": "#FF9800", "color": "#FFFFFF"}]),
            MenuItem("Bombshell Cakes"),
            MenuItem("Spider Man Cakes"),
            MenuItem("Bento Cakes", badges=[{"name": "Trending", "background_color": "#FF9800", "color": "#FFFFFF"}]),
            MenuItem("Mickey Mouse Cakes"),
            MenuItem("Heart Shaped"),
            MenuItem("Barbie Cakes"),
            MenuItem("Theme Cakes", badges=[{"name": "Must Try", "background_color": "#4CAF50", "color": "#FFFFFF"}]),
        ], section_type='by_type'),
        MenuSection("By Occasion", [
            MenuItem("Anniversary"),
            MenuItem("Birthday"),
            MenuItem("Appreciation"),
            MenuItem("Congratulations"),
            MenuItem("Get Well Soon"),
            MenuItem("I Am Sorry"),
            MenuItem("Love & Affection"),
            MenuItem("Thank You"),
            MenuItem("New Born"),
        ], section_type='by_occasion'),
        MenuSection("By City", [
            MenuItem("Delhi"),
            MenuItem("Mumbai"),
            MenuItem("Bangalore"),
            MenuItem("Chennai"),
            MenuItem("Kolkata"),
            MenuItem("Hyderabad"),
            MenuItem("Pune"),
            MenuItem("Gurgaon"),
            MenuItem("Noida"),
            MenuItem("Ahmedabad"),
            MenuItem("Jalandhar"),
            MenuItem("Kanpur"),
            MenuItem("Allahabad"),
            MenuItem("Jaipur"),
        ], section_type='deliver_to'),
    ]


def _build_combos_menu():
    """Build exact combos menu as specified"""
    return [
        MenuSection("Collection", [
            MenuItem("Chocolate Combo"),
            MenuItem("Cake Combo"),
            MenuItem("Gift Combos"),
            MenuItem("Express Combo"),
            MenuItem("Birthday"),
            MenuItem("Anniversary"),
            MenuItem("All Combo"),
        ], section_type='collection'),
        MenuSection("Flower Combos", [
            MenuItem("With Cake"),
            MenuItem("With Chocolate"),
            MenuItem("With Teddy"),
            MenuItem("With Plant"),
            MenuItem("With Greeting Card"),
        ], section_type='collection'),
        MenuSection("By City", [
            MenuItem("Delhi NCR"),
            MenuItem("Bangalore"),
            MenuItem("Chennai"),
            MenuItem("Mumbai"),
            MenuItem("Hyderabad"),
            MenuItem("Pune"),
            MenuItem("Kolkata"),
            MenuItem("Ahmedabad"),
            MenuItem("Lucknow"),
        ], section_type='deliver_to'),
    ]


def _build_personalised_menu():
    """Build exact personalised menu as specified"""
    return [
        MenuSection("By Type", [
            MenuItem("Mugs"),
            MenuItem("Cushions"),
            MenuItem("Photo Frames"),
            MenuItem("Clocks"),
            MenuItem("Photo Lamps"),
            MenuItem("Personalised Jewellery", badges=[{"name": "New", "background_color": "#FF4444", "color": "#FFFFFF"}]),
            MenuItem("Travel Accessories"),
            MenuItem("Same Day Delivery"),
            MenuItem("Handbags"),
            MenuItem("Chocolates"),
            MenuItem("Caricature"),
            MenuItem("Keychains"),
            MenuItem("All Personalised Gifts"),
        ], section_type='by_type'),
    ]


def _build_birthday_menu():
    """Build exact birthday menu as specified"""
    return [
        MenuSection("Gift Type", [
            MenuItem("Bestsellers"),
            MenuItem("Cakes"),
            MenuItem("Flowers"),
            MenuItem("Chocolates"),
            MenuItem("Flowers & Cakes"),
            MenuItem("Flowers & Chocolate"),
            MenuItem("Cakes & Plants"),
            MenuItem("Plants"),
            MenuItem("Personalised Gifts"),
            MenuItem("Hampers"),
            MenuItem("Travel Accessories"),
            MenuItem("Perfumes"),
            MenuItem("All Gifts"),
        ], section_type='collection'),
        MenuSection("Gift By Milestone", [
            MenuItem("1st Birthday"),
            MenuItem("5th Birthday"),
            MenuItem("Teen Birthday"),
            MenuItem("18th Birthday"),
            MenuItem("21st Birthday"),
            MenuItem("25th Birthday"),
            MenuItem("30th Birthday"),
            MenuItem("40th Birthday"),
            MenuItem("50th Birthday"),
        ], section_type='by_occasion'),
        MenuSection("Gifts For", [
            MenuItem("Him"),
            MenuItem("Her"),
            MenuItem("Wife"),
            MenuItem("Husband"),
            MenuItem("Friend"),
            MenuItem("Brother"),
            MenuItem("Girlfriend"),
            MenuItem("Boyfriend"),
            MenuItem("Mother"),
            MenuItem("Father"),
            MenuItem("Kids"),
        ], section_type='for_whom'),
        MenuSection("Cakes", [
            MenuItem("Bento Cakes"),
            MenuItem("Photo Cakes"),
            MenuItem("Tier Cakes"),
            MenuItem("Sugarfree Cakes"),
            MenuItem("Fruit Cakes"),
            MenuItem("Ferrero Rocher Cakes"),
            MenuItem("Trend Cakes"),
        ], section_type='by_type'),
    ]


def _build_anniversary_menu():
    """Build exact anniversary menu as specified"""
    return [
        MenuSection("By Choice", [
            MenuItem("Bestsellers"),
            MenuItem("Same Day Delivery"),
            MenuItem("Cakes"),
            MenuItem("Photo Cakes"),
            MenuItem("Flowers"),
            MenuItem("Combos"),
            MenuItem("Personalised Gifts"),
            MenuItem("Hampers"),
            MenuItem("Plants"),
            MenuItem("Beauty & Grooming"),
            MenuItem("Jewellery"),
            MenuItem("Chocolates"),
            MenuItem("Perfumes"),
            MenuItem("Travel Accessories"),
            MenuItem("All Gifts"),
        ], section_type='collection'),
        MenuSection("Gift By Milestone", [
            MenuItem("1st Anniversary"),
            MenuItem("5th Anniversary"),
            MenuItem("15th Anniversary"),
            MenuItem("10th Anniversary"),
            MenuItem("25th Anniversary"),
            MenuItem("50th Anniversary"),
            MenuItem("75th Anniversary"),
        ], section_type='by_occasion'),
        MenuSection("Gifts For", [
            MenuItem("Her"),
            MenuItem("Him"),
            MenuItem("Wife"),
            MenuItem("Husband"),
            MenuItem("Parents"),
            MenuItem("Friends"),
        ], section_type='for_whom'),
        MenuSection("Cakes", [
            MenuItem("Wife"),
            MenuItem("Husband"),
            MenuItem("Couple"),
            MenuItem("Parents"),
        ], section_type='by_type'),
    ]


def _build_plants_menu():
    """Build exact plants menu as specified"""
    return [
        MenuSection("Plants", [
            MenuItem("All Plants"),
            MenuItem("Air Purifying Plants"),
            MenuItem("Lucky Bamboo"),
            MenuItem("Bonsai Plants"),
            MenuItem("Indoor Plants"),
            MenuItem("Outdoor Plants"),
            MenuItem("Terrarium Plants"),
            MenuItem("Money Plants"),
            MenuItem("Planters"),
            MenuItem("Same Day Plants"),
        ], section_type='collection'),
    ]


def _build_gifts_menu():
    """Build exact gifts menu as specified"""
    return [
        MenuSection("Favourites", [
            MenuItem("Bestsellers"),
            MenuItem("Photo Gifts"),
            MenuItem("Gift Hampers"),
            MenuItem("Grooming Kits"),
            MenuItem("Beauty & Cosmetics"),
            MenuItem("All Gifts"),
        ], section_type='collection'),
        MenuSection("Collection", [
            MenuItem("Mugs"),
            MenuItem("Handbags"),
            MenuItem("Cushions"),
            MenuItem("Jewellery"),
            MenuItem("Perfumes"),
            MenuItem("Soft Toys"),
            MenuItem("Home Decor"),
            MenuItem("Spiritual Gifts"),
            MenuItem("Personalised Gifts"),
            MenuItem("Photo Frames"),
            MenuItem("Plants"),
            MenuItem("Chocolates"),
        ], section_type='collection'),
        MenuSection("Gifts For", [
            MenuItem("Gifts For Sister"),
            MenuItem("Gifts For Brother"),
            MenuItem("Gifts For Boyfriend"),
            MenuItem("Gifts For Girlfriend"),
            MenuItem("Gifts For Him"),
            MenuItem("Gifts For Her"),
            MenuItem("Gifts For Husband"),
            MenuItem("Gifts For Wife"),
            MenuItem("Gifts For Friends"),
            MenuItem("Gifts for Father"),
            MenuItem("Gifts For Mother"),
        ], section_type='for_whom'),
        MenuSection("Express Gifts", [
            MenuItem("Chocolate Bouquet"),
            MenuItem("Plants"),
            MenuItem("Cakes"),
            MenuItem("Flowers"),
            MenuItem("Hampers"),
            MenuItem("Combos"),
            MenuItem("Personalised"),
        ], section_type='collection'),
        MenuSection("Gifts to", [
            MenuItem("Delhi"),
            MenuItem("Mumbai"),
            MenuItem("Bangalore"),
            MenuItem("Chennai"),
            MenuItem("Kolkata"),
            MenuItem("Hyderabad"),
            MenuItem("Pune"),
            MenuItem("Gurgaon"),
            MenuItem("Noida"),
            MenuItem("Jaipur"),
            MenuItem("Lucknow"),
        ], section_type='deliver_to'),
    ]


def _build_international_menu():
    """Build exact international menu as specified"""
    return [
        MenuSection("Countries", [
            MenuItem("India"),
            MenuItem("USA"),
        ], section_type='deliver_to'),
    ]


def _build_occasions_menu():
    """Build exact occasions menu as specified"""
    return [
        MenuSection("Festivals", [
            MenuItem("Rakhi - 28th Aug"),
            MenuItem("Janmashtami - 4th Sep"),
            MenuItem("Dussehra - 2nd Oct"),
            MenuItem("Karwa Chauth - 9th Oct"),
            MenuItem("Dhanteras - 18th Oct"),
            MenuItem("Diwali - 21st Oct"),
            MenuItem("Bhai Dooj - 23rd Oct"),
            MenuItem("Lohri - 13th Jan"),
            MenuItem("Holi - 14th Mar"),
        ], section_type='by_occasion'),
        MenuSection("Special Occasions", [
            MenuItem("Mother's Day - 10th May"),
            MenuItem("Father's Day - 21st June"),
            MenuItem("Parents Day - 26th July"),
            MenuItem("Friendship Day - 2nd Aug"),
            MenuItem("Teacher's Day - 05th Sep"),
            MenuItem("Grandparents Day - 07th Sep"),
            MenuItem("Daughter's Day - 28th Sep"),
            MenuItem("Boss Day - 16th Oct"),
            MenuItem("Children's Day - 14th Nov"),
            MenuItem("Christmas - 25th Dec"),
            MenuItem("New Year - 01st Jan"),
            MenuItem("Valentine's Day - 14th Feb"),
            MenuItem("Women's Day - 08th Mar"),
        ], section_type='by_occasion'),
        MenuSection("Sentiments", [
            MenuItem("Congratulations"),
            MenuItem("I Am Sorry"),
            MenuItem("Thank You"),
            MenuItem("Sympathy"),
            MenuItem("Love n Romance"),
            MenuItem("Get Well Soon"),
        ], section_type='by_occasion'),
    ]