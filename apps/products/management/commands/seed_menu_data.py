from django.core.management.base import BaseCommand
from django.db import transaction
from apps.products.models import (
    MenuBadge, MenuCategory, MenuSection, ProductType, Collection, 
    Recipient, DeliveryLocation, MenuConfiguration, Category, Occasion
)


class Command(BaseCommand):
    help = 'Seed initial data for advanced menu system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting menu data seeding...'))
        
        with transaction.atomic():
            self.create_menu_badges()
            self.create_menu_categories()
            self.create_menu_sections()
            self.create_product_types()
            self.create_collections()
            self.create_recipients()
            self.create_delivery_locations()
            self.create_occasions_data()
            self.create_milestones_data()
            self.create_menu_configurations()
        
        self.stdout.write(self.style.SUCCESS('Menu data seeding completed successfully!'))

    def create_menu_badges(self):
        """Create menu badges"""
        badges = [
            {'name': 'New', 'color': '#FFFFFF', 'background_color': '#FF4444', 'sort_order': 1},
            {'name': 'Hot Selling', 'color': '#FFFFFF', 'background_color': '#FF6600', 'sort_order': 2},
            {'name': 'Must Try', 'color': '#FFFFFF', 'background_color': '#4CAF50', 'sort_order': 3},
            {'name': 'Premium', 'color': '#FFFFFF', 'background_color': '#9C27B0', 'sort_order': 4},
            {'name': 'Bestseller', 'color': '#FFFFFF', 'background_color': '#2196F3', 'sort_order': 5},
            {'name': 'Trending', 'color': '#FFFFFF', 'background_color': '#FF9800', 'sort_order': 6},
        ]
        
        for badge_data in badges:
            badge, created = MenuBadge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                self.stdout.write(f'Created badge: {badge.name}')

    def create_menu_categories(self):
        """Create the 10 main menu categories as specified"""
        main_categories = [
            {'name': 'Flowers', 'slug': 'flowers', 'sort_order': 1, 'icon': 'fas fa-seedling'},
            {'name': 'Cakes', 'slug': 'cakes', 'sort_order': 2, 'icon': 'fas fa-birthday-cake'},
            {'name': 'Combos', 'slug': 'combos', 'sort_order': 3, 'icon': 'fas fa-gift'},
            {'name': 'Personalised', 'slug': 'personalised', 'sort_order': 4, 'icon': 'fas fa-heart'},
            {'name': 'Birthday', 'slug': 'birthday', 'sort_order': 5, 'icon': 'fas fa-birthday-cake'},
            {'name': 'Anniversary', 'slug': 'anniversary', 'sort_order': 6, 'icon': 'fas fa-ring'},
            {'name': 'Plants', 'slug': 'plants', 'sort_order': 7, 'icon': 'fas fa-leaf'},
            {'name': 'Gifts', 'slug': 'gifts', 'sort_order': 8, 'icon': 'fas fa-gift'},
            {'name': 'International', 'slug': 'international', 'sort_order': 9, 'icon': 'fas fa-globe'},
            {'name': 'Occasions', 'slug': 'occasions', 'sort_order': 10, 'icon': 'fas fa-calendar'},
        ]
        
        for category_data in main_categories:
            menu_category, created = MenuCategory.objects.get_or_create(
                name=category_data['name'],
                slug=category_data['slug'],
                defaults={
                    'icon': category_data['icon'],
                    'sort_order': category_data['sort_order'],
                    'show_in_mega_menu': True,
                    'show_in_mobile_menu': True,
                    'menu_columns': 4,
                    'featured_products_count': 3,
                }
            )
            if created:
                self.stdout.write(f'Created menu category: {menu_category.name}')

    def create_menu_sections(self):
        """Create menu sections for each category"""
        sections = [
            {'name': 'By Type', 'section_type': 'by_type', 'sort_order': 1},
            {'name': 'Collection', 'section_type': 'collection', 'sort_order': 2},
            {'name': 'For Whom', 'section_type': 'for_whom', 'sort_order': 3},
            {'name': 'By Occasion', 'section_type': 'by_occasion', 'sort_order': 4},
            {'name': 'Deliver To', 'section_type': 'deliver_to', 'sort_order': 5},
        ]
        
        menu_categories = MenuCategory.objects.all()
        
        for menu_category in menu_categories:
            for section_data in sections:
                section, created = MenuSection.objects.get_or_create(
                    category=menu_category,
                    name=section_data['name'],
                    defaults={
                        'slug': section_data['name'].lower().replace(' ', '_'),
                        'section_type': section_data['section_type'],
                        'sort_order': section_data['sort_order'],
                    }
                )
                if created:
                    self.stdout.write(f'Created section: {section.name} for {menu_category.name}')

    def create_product_types(self):
        """Create product types for different menu categories as specified"""
        # Get badges
        new_badge = MenuBadge.objects.filter(name='New').first()
        hot_badge = MenuBadge.objects.filter(name='Hot Selling').first()
        premium_badge = MenuBadge.objects.filter(name='Premium').first()
        must_try_badge = MenuBadge.objects.filter(name='Must Try').first()
        bestseller_badge = MenuBadge.objects.filter(name='Bestseller').first()
        trending_badge = MenuBadge.objects.filter(name='Trending').first()
        
        # Get or create a default category for menu items
        default_category, _ = Category.objects.get_or_create(
            name='Menu Items',
            defaults={'slug': 'menu-items', 'description': 'Items for menu system'}
        )
        
        # Flowers - By Type
        flower_types = [
            {'name': 'Roses', 'badges': []},
            {'name': 'Lilies', 'badges': []},
            {'name': 'Orchids', 'badges': []},
            {'name': 'Carnations', 'badges': []},
            {'name': 'Tuberose', 'badges': []},
            {'name': 'Gerberas', 'badges': []},
            {'name': 'Sunflowers', 'badges': [must_try_badge]},
            {'name': 'Mixed Flowers', 'badges': []},
            {'name': 'Hydrangea', 'badges': [new_badge]},
            {'name': 'Exotic Flowers', 'badges': [premium_badge]},
        ]
        
        # Cakes - By Flavour
        cake_flavours = [
            {'name': 'All Cakes', 'badges': []},
            {'name': 'Chocolate Cakes', 'badges': []},
            {'name': 'Blackforest Cakes', 'badges': []},
            {'name': 'Truffle Cakes', 'badges': [bestseller_badge]},
            {'name': 'Butterscotch Cakes', 'badges': []},
            {'name': 'Vanilla Cakes', 'badges': []},
            {'name': 'Red Velvet Cakes', 'badges': [must_try_badge]},
            {'name': 'Pineapple Cakes', 'badges': []},
            {'name': 'Fruit Cakes', 'badges': []},
            {'name': 'Coffee Cakes', 'badges': []},
            {'name': 'Strawberry Cakes', 'badges': []},
            {'name': 'Cheese Cakes', 'badges': [premium_badge]},
        ]
        
        # Cakes - By Type
        cake_types = [
            {'name': 'Eggless Cakes', 'badges': [must_try_badge]},
            {'name': 'Sugarfree Cakes', 'badges': [hot_badge]},
            {'name': 'Regular Cakes', 'badges': []},
            {'name': 'Photo Cakes', 'badges': [trending_badge]},
            {'name': 'Premium Cakes', 'badges': []},
            {'name': 'Cup Cakes', 'badges': []},
            {'name': 'Tier Cakes', 'badges': []},
            {'name': 'Cake Jars', 'badges': []},
            {'name': 'Exotic Cakes', 'badges': []},
        ]
        
        # Cakes - By Design
        cake_designs = [
            {'name': 'Cartoon Cakes', 'badges': [new_badge]},
            {'name': 'Pinata Cakes', 'badges': [hot_badge]},
            {'name': 'Pull Up Cakes', 'badges': [trending_badge]},
            {'name': 'Bombshell Cakes', 'badges': []},
            {'name': 'Spider Man Cakes', 'badges': []},
            {'name': 'Bento Cakes', 'badges': [trending_badge]},
            {'name': 'Mickey Mouse Cakes', 'badges': []},
            {'name': 'Heart Shaped', 'badges': []},
            {'name': 'Barbie Cakes', 'badges': []},
            {'name': 'Theme Cakes', 'badges': [must_try_badge]},
        ]
        
        # Personalised - By Type
        personalised_types = [
            {'name': 'Mugs', 'badges': []},
            {'name': 'Cushions', 'badges': []},
            {'name': 'Photo Frames', 'badges': []},
            {'name': 'Clocks', 'badges': []},
            {'name': 'Photo Lamps', 'badges': []},
            {'name': 'Personalised Jewellery', 'badges': [new_badge]},
            {'name': 'Travel Accessories', 'badges': []},
            {'name': 'Same Day Delivery', 'badges': []},
            {'name': 'Handbags', 'badges': []},
            {'name': 'Chocolates', 'badges': []},
            {'name': 'Caricature', 'badges': []},
            {'name': 'Keychains', 'badges': []},
            {'name': 'All Personalised Gifts', 'badges': []},
        ]
        
        # Plants
        plant_types = [
            {'name': 'All Plants', 'badges': []},
            {'name': 'Air Purifying Plants', 'badges': []},
            {'name': 'Lucky Bamboo', 'badges': []},
            {'name': 'Bonsai Plants', 'badges': []},
            {'name': 'Indoor Plants', 'badges': []},
            {'name': 'Outdoor Plants', 'badges': []},
            {'name': 'Terrarium Plants', 'badges': []},
            {'name': 'Money Plants', 'badges': []},
            {'name': 'Planters', 'badges': []},
            {'name': 'Same Day Plants', 'badges': []},
        ]
        
        # Create all product types
        all_types = [
            ('flowers', flower_types),
            ('cakes-flavour', cake_flavours),
            ('cakes-type', cake_types),
            ('cakes-design', cake_designs),
            ('personalised', personalised_types),
            ('plants', plant_types),
        ]
        
        for category_prefix, types_list in all_types:
            for i, type_data in enumerate(types_list):
                product_type, created = ProductType.objects.get_or_create(
                    name=type_data['name'],
                    category=default_category,
                    defaults={
                        'slug': f"{category_prefix}-{type_data['name'].lower().replace(' ', '-').replace('&', 'and')}",
                        'sort_order': i + 1,
                    }
                )
                
                if created:
                    # Add badges
                    for badge in type_data['badges']:
                        if badge:
                            product_type.badges.add(badge)
                    
                    self.stdout.write(f'Created product type: {product_type.name}')

    def create_collections(self):
        """Create product collections as specified"""
        # Get badges
        new_badge = MenuBadge.objects.filter(name='New').first()
        hot_badge = MenuBadge.objects.filter(name='Hot Selling').first()
        premium_badge = MenuBadge.objects.filter(name='Premium').first()
        
        # Flowers Collections
        flower_collections = [
            {'name': 'Bestseller', 'badges': []},
            {'name': 'Korean Paper Bouquets', 'badges': [new_badge]},
            {'name': 'Crochet Flowers', 'badges': [new_badge]},
            {'name': 'MFT Signature Boxes', 'badges': []},
            {'name': 'Floral Bouquets', 'badges': [hot_badge]},
            {'name': 'Premium Basket Arrangements', 'badges': []},
            {'name': 'Floral Hampers', 'badges': [new_badge]},
            {'name': 'Premium Vases', 'badges': []},
            {'name': 'All Flowers', 'badges': []},
        ]
        
        # Combos Collections
        combo_collections = [
            {'name': 'Chocolate Combo', 'badges': []},
            {'name': 'Cake Combo', 'badges': []},
            {'name': 'Gift Combos', 'badges': []},
            {'name': 'Express Combo', 'badges': []},
            {'name': 'Birthday', 'badges': []},
            {'name': 'Anniversary', 'badges': []},
            {'name': 'All Combo', 'badges': []},
            {'name': 'Flower Combos', 'badges': []},
            {'name': 'With Cake', 'badges': []},
            {'name': 'With Chocolate', 'badges': []},
            {'name': 'With Teddy', 'badges': []},
            {'name': 'With Plant', 'badges': []},
            {'name': 'With Greeting Card', 'badges': []},
        ]
        
        # Birthday Collections
        birthday_collections = [
            {'name': 'Bestsellers', 'badges': []},
            {'name': 'Cakes', 'badges': []},
            {'name': 'Flowers', 'badges': []},
            {'name': 'Chocolates', 'badges': []},
            {'name': 'Flowers & Cakes', 'badges': []},
            {'name': 'Flowers & Chocolate', 'badges': []},
            {'name': 'Cakes & Plants', 'badges': []},
            {'name': 'Plants', 'badges': []},
            {'name': 'Personalised Gifts', 'badges': []},
            {'name': 'Hampers', 'badges': []},
            {'name': 'Travel Accessories', 'badges': []},
            {'name': 'Perfumes', 'badges': []},
            {'name': 'All Gifts', 'badges': []},
        ]
        
        # Anniversary Collections
        anniversary_collections = [
            {'name': 'Bestsellers', 'badges': []},
            {'name': 'Same Day Delivery', 'badges': []},
            {'name': 'Cakes', 'badges': []},
            {'name': 'Photo Cakes', 'badges': []},
            {'name': 'Flowers', 'badges': []},
            {'name': 'Combos', 'badges': []},
            {'name': 'Personalised Gifts', 'badges': []},
            {'name': 'Hampers', 'badges': []},
            {'name': 'Plants', 'badges': []},
            {'name': 'Beauty & Grooming', 'badges': []},
            {'name': 'Jewellery', 'badges': []},
            {'name': 'Chocolates', 'badges': []},
            {'name': 'Perfumes', 'badges': []},
            {'name': 'Travel Accessories', 'badges': []},
            {'name': 'All Gifts', 'badges': []},
        ]
        
        # Gifts Collections
        gift_collections = [
            {'name': 'Bestsellers', 'badges': []},
            {'name': 'Photo Gifts', 'badges': []},
            {'name': 'Gift Hampers', 'badges': []},
            {'name': 'Grooming Kits', 'badges': []},
            {'name': 'Beauty & Cosmetics', 'badges': []},
            {'name': 'All Gifts', 'badges': []},
            {'name': 'Mugs', 'badges': []},
            {'name': 'Handbags', 'badges': []},
            {'name': 'Cushions', 'badges': []},
            {'name': 'Jewellery', 'badges': []},
            {'name': 'Perfumes', 'badges': []},
            {'name': 'Soft Toys', 'badges': []},
            {'name': 'Home Decor', 'badges': []},
            {'name': 'Spiritual Gifts', 'badges': []},
            {'name': 'Personalised Gifts', 'badges': []},
            {'name': 'Photo Frames', 'badges': []},
            {'name': 'Plants', 'badges': []},
            {'name': 'Chocolates', 'badges': []},
        ]
        
        # Express Gifts
        express_collections = [
            {'name': 'Chocolate Bouquet', 'badges': []},
            {'name': 'Plants', 'badges': []},
            {'name': 'Cakes', 'badges': []},
            {'name': 'Flowers', 'badges': []},
            {'name': 'Hampers', 'badges': []},
            {'name': 'Combos', 'badges': []},
            {'name': 'Personalised', 'badges': []},
        ]
        
        # Create all collections
        all_collections = [
            ('flowers', flower_collections),
            ('combos', combo_collections),
            ('birthday', birthday_collections),
            ('anniversary', anniversary_collections),
            ('gifts', gift_collections),
            ('express', express_collections),
        ]
        
        for category_prefix, collections_list in all_collections:
            for i, collection_data in enumerate(collections_list):
                collection, created = Collection.objects.get_or_create(
                    name=collection_data['name'],
                    defaults={
                        'slug': f"{category_prefix}-{collection_data['name'].lower().replace(' ', '-').replace('&', 'and')}",
                        'sort_order': i + 1,
                        'is_featured': i < 5,  # First 5 are featured
                    }
                )
                
                if created:
                    # Add badges
                    for badge in collection_data['badges']:
                        if badge:
                            collection.badges.add(badge)
                    
                    self.stdout.write(f'Created collection: {collection.name}')

    def create_recipients(self):
        """Create recipient categories as specified"""
        # Flowers For
        flower_recipients = [
            {'name': 'Girlfriend', 'category': 'personal'},
            {'name': 'Wife', 'category': 'personal'},
            {'name': 'Husband', 'category': 'personal'},
            {'name': 'Parents', 'category': 'family'},
            {'name': 'Corporate', 'category': 'professional'},
            {'name': 'Boyfriend', 'category': 'personal'},
            {'name': 'Brother', 'category': 'family'},
            {'name': 'Sister', 'category': 'family'},
        ]
        
        # Birthday Gifts For
        birthday_recipients = [
            {'name': 'Him', 'category': 'personal'},
            {'name': 'Her', 'category': 'personal'},
            {'name': 'Wife', 'category': 'personal'},
            {'name': 'Husband', 'category': 'personal'},
            {'name': 'Friend', 'category': 'special'},
            {'name': 'Brother', 'category': 'family'},
            {'name': 'Girlfriend', 'category': 'personal'},
            {'name': 'Boyfriend', 'category': 'personal'},
            {'name': 'Mother', 'category': 'family'},
            {'name': 'Father', 'category': 'family'},
            {'name': 'Kids', 'category': 'special'},
        ]
        
        # Anniversary Gifts For
        anniversary_recipients = [
            {'name': 'Her', 'category': 'personal'},
            {'name': 'Him', 'category': 'personal'},
            {'name': 'Wife', 'category': 'personal'},
            {'name': 'Husband', 'category': 'personal'},
            {'name': 'Parents', 'category': 'family'},
            {'name': 'Friends', 'category': 'special'},
        ]
        
        # General Gifts For
        gift_recipients = [
            {'name': 'Gifts For Sister', 'category': 'family'},
            {'name': 'Gifts For Brother', 'category': 'family'},
            {'name': 'Gifts For Boyfriend', 'category': 'personal'},
            {'name': 'Gifts For Girlfriend', 'category': 'personal'},
            {'name': 'Gifts For Him', 'category': 'personal'},
            {'name': 'Gifts For Her', 'category': 'personal'},
            {'name': 'Gifts For Husband', 'category': 'personal'},
            {'name': 'Gifts For Wife', 'category': 'personal'},
            {'name': 'Gifts For Friends', 'category': 'special'},
            {'name': 'Gifts for Father', 'category': 'family'},
            {'name': 'Gifts For Mother', 'category': 'family'},
        ]
        
        # Create all recipients
        all_recipients = [
            ('flowers', flower_recipients),
            ('birthday', birthday_recipients),
            ('anniversary', anniversary_recipients),
            ('gifts', gift_recipients),
        ]
        
        for category_prefix, recipients_list in all_recipients:
            for i, recipient_data in enumerate(recipients_list):
                recipient, created = Recipient.objects.get_or_create(
                    name=recipient_data['name'],
                    defaults={
                        'slug': f"{category_prefix}-{recipient_data['name'].lower().replace(' ', '-')}",
                        'category': recipient_data['category'],
                        'sort_order': i + 1,
                    }
                )
                if created:
                    self.stdout.write(f'Created recipient: {recipient.name}')

    def create_delivery_locations(self):
        """Create delivery locations as specified"""
        # Common cities for all categories
        common_cities = [
            {'name': 'Delhi', 'state': 'Delhi', 'is_major_city': True, 'is_metro': True},
            {'name': 'Mumbai', 'state': 'Maharashtra', 'is_major_city': True, 'is_metro': True},
            {'name': 'Bangalore', 'state': 'Karnataka', 'is_major_city': True, 'is_metro': True},
            {'name': 'Chennai', 'state': 'Tamil Nadu', 'is_major_city': True, 'is_metro': True},
            {'name': 'Kolkata', 'state': 'West Bengal', 'is_major_city': True, 'is_metro': True},
            {'name': 'Hyderabad', 'state': 'Telangana', 'is_major_city': True, 'is_metro': True},
            {'name': 'Pune', 'state': 'Maharashtra', 'is_major_city': True, 'is_metro': True},
            {'name': 'Gurgaon', 'state': 'Haryana', 'is_major_city': True, 'is_metro': False},
            {'name': 'Noida', 'state': 'Uttar Pradesh', 'is_major_city': True, 'is_metro': False},
            {'name': 'Jaipur', 'state': 'Rajasthan', 'is_major_city': True, 'is_metro': False},
            {'name': 'Lucknow', 'state': 'Uttar Pradesh', 'is_major_city': True, 'is_metro': False},
        ]
        
        # Additional cities for cakes
        cake_cities = common_cities + [
            {'name': 'Ahmedabad', 'state': 'Gujarat', 'is_major_city': True, 'is_metro': False},
            {'name': 'Jalandhar', 'state': 'Punjab', 'is_major_city': True, 'is_metro': False},
            {'name': 'Kanpur', 'state': 'Uttar Pradesh', 'is_major_city': True, 'is_metro': False},
            {'name': 'Allahabad', 'state': 'Uttar Pradesh', 'is_major_city': True, 'is_metro': False},
        ]
        
        # Combos cities (Delhi NCR specified separately)
        combo_cities = [
            {'name': 'Delhi NCR', 'state': 'Delhi', 'is_major_city': True, 'is_metro': True},
        ] + [city for city in common_cities if city['name'] != 'Delhi']
        
        # International locations
        international_locations = [
            {'name': 'India', 'state': 'All States', 'country': 'India', 'is_major_city': True, 'is_metro': False},
            {'name': 'USA', 'state': 'All States', 'country': 'United States', 'is_major_city': True, 'is_metro': False},
        ]
        
        # Create all locations
        all_locations = [
            ('flowers', common_cities + [{'name': 'All Cities', 'state': 'All', 'is_major_city': False, 'is_metro': False}]),
            ('cakes', cake_cities),
            ('combos', combo_cities),
            ('gifts', common_cities),
            ('international', international_locations),
        ]
        
        for category_prefix, locations_list in all_locations:
            for i, location_data in enumerate(locations_list):
                location, created = DeliveryLocation.objects.get_or_create(
                    name=location_data['name'],
                    state=location_data['state'],
                    defaults={
                        'slug': f"{category_prefix}-{location_data['name'].lower().replace(' ', '-')}",
                        'country': location_data.get('country', 'India'),
                        'is_major_city': location_data['is_major_city'],
                        'is_metro': location_data['is_metro'],
                        'sort_order': i + 1,
                    }
                )
                if created:
                    self.stdout.write(f'Created delivery location: {location.name}')

    def create_occasions_data(self):
        """Create occasions data as specified"""
        # Flowers By Occasion
        flower_occasions = [
            'Birthday', 'Anniversary', 'Condolence', 'Congratulations',
            'Love & Romance', 'Get Well Soon', 'I Am Sorry', 'Thank You', 'New Born'
        ]
        
        # Cake By Occasion
        cake_occasions = [
            'Anniversary', 'Birthday', 'Appreciation', 'Congratulations',
            'Get Well Soon', 'I Am Sorry', 'Love & Affection', 'Thank You', 'New Born'
        ]
        
        # Festivals (Occasions menu)
        festivals = [
            {'name': 'Rakhi', 'date': '28th Aug'},
            {'name': 'Janmashtami', 'date': '4th Sep'},
            {'name': 'Dussehra', 'date': '2nd Oct'},
            {'name': 'Karwa Chauth', 'date': '9th Oct'},
            {'name': 'Dhanteras', 'date': '18th Oct'},
            {'name': 'Diwali', 'date': '21st Oct'},
            {'name': 'Bhai Dooj', 'date': '23rd Oct'},
            {'name': 'Lohri', 'date': '13th Jan'},
            {'name': 'Holi', 'date': '14th Mar'},
        ]
        
        # Special Occasions
        special_occasions = [
            {'name': "Mother's Day", 'date': '10th May'},
            {'name': "Father's Day", 'date': '21st June'},
            {'name': 'Parents Day', 'date': '26th July'},
            {'name': 'Friendship Day', 'date': '2nd Aug'},
            {'name': "Teacher's Day", 'date': '05th Sep'},
            {'name': 'Grandparents Day', 'date': '07th Sep'},
            {'name': "Daughter's Day", 'date': '28th Sep'},
            {'name': 'Boss Day', 'date': '16th Oct'},
            {'name': "Children's Day", 'date': '14th Nov'},
            {'name': 'Christmas', 'date': '25th Dec'},
            {'name': 'New Year', 'date': '01st Jan'},
            {'name': "Valentine's Day", 'date': '14th Feb'},
            {'name': "Women's Day", 'date': '08th Mar'},
        ]
        
        # Sentiments
        sentiments = [
            'Congratulations', 'I Am Sorry', 'Thank You', 'Sympathy',
            'Love n Romance', 'Get Well Soon'
        ]
        
        # Create occasions in the existing Occasion model
        all_occasions = []
        all_occasions.extend(flower_occasions)
        all_occasions.extend(cake_occasions)
        all_occasions.extend([f['name'] for f in festivals])
        all_occasions.extend([s['name'] for s in special_occasions])
        all_occasions.extend(sentiments)
        
        # Remove duplicates
        unique_occasions = list(set(all_occasions))
        
        for i, occasion_name in enumerate(unique_occasions):
            # Create URL-safe slug
            safe_slug = occasion_name.lower().replace(' ', '-').replace("'", '').replace('&', 'and').replace('n', 'n')
            
            occasion, created = Occasion.objects.get_or_create(
                name=occasion_name,
                defaults={
                    'slug': safe_slug,
                    'sort_order': i + 1,
                }
            )
            if created:
                self.stdout.write(f'Created occasion: {occasion.name}')

    def create_milestones_data(self):
        """Create milestone data for birthdays and anniversaries"""
        # Birthday Milestones
        birthday_milestones = [
            '1st Birthday', '5th Birthday', 'Teen Birthday', '18th Birthday',
            '21st Birthday', '25th Birthday', '30th Birthday', '40th Birthday', '50th Birthday'
        ]
        
        # Anniversary Milestones
        anniversary_milestones = [
            '1st Anniversary', '5th Anniversary', '10th Anniversary', '15th Anniversary',
            '25th Anniversary', '50th Anniversary', '75th Anniversary'
        ]
        
        # Create as special collections
        for i, milestone in enumerate(birthday_milestones):
            collection, created = Collection.objects.get_or_create(
                name=milestone,
                defaults={
                    'slug': f"birthday-{milestone.lower().replace(' ', '-')}",
                    'sort_order': i + 100,  # Higher sort order to separate from main collections
                }
            )
            if created:
                self.stdout.write(f'Created birthday milestone: {collection.name}')
        
        for i, milestone in enumerate(anniversary_milestones):
            collection, created = Collection.objects.get_or_create(
                name=milestone,
                defaults={
                    'slug': f"anniversary-{milestone.lower().replace(' ', '-')}",
                    'sort_order': i + 200,  # Higher sort order
                }
            )
            if created:
                self.stdout.write(f'Created anniversary milestone: {collection.name}')

    def create_menu_configurations(self):
        """Create menu configuration settings"""
        configurations = [
            {'key': 'mega_menu_columns', 'value': 4, 'description': 'Number of columns in mega menu'},
            {'key': 'featured_products_per_category', 'value': 3, 'description': 'Featured products shown per category in mega menu'},
            {'key': 'mobile_menu_animation_speed', 'value': 300, 'description': 'Animation speed for mobile menu in milliseconds'},
            {'key': 'menu_cache_timeout', 'value': 3600, 'description': 'Menu cache timeout in seconds'},
            {'key': 'show_product_count_in_menu', 'value': True, 'description': 'Show product count in menu items'},
            {'key': 'enable_menu_analytics', 'value': True, 'description': 'Enable menu click analytics'},
        ]
        
        for config_data in configurations:
            config, created = MenuConfiguration.objects.get_or_create(
                key=config_data['key'],
                defaults={
                    'value': config_data['value'],
                    'description': config_data['description'],
                }
            )
            if created:
                self.stdout.write(f'Created menu configuration: {config.key}')