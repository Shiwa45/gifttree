from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import SiteSettings
from apps.products.models import Category, Occasion, Product, ProductImage, ProductVariant
from apps.users.models import Address
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new sample data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Creating sample data...')

        # Create site settings
        self.create_site_settings()

        # Create categories
        categories = self.create_categories()

        # Create occasions
        occasions = self.create_occasions()

        # Create sample users
        users = self.create_users()

        # Create products
        self.create_products(categories, occasions)

        # Create addresses for users
        self.create_addresses(users)

        self.stdout.write(
            self.style.SUCCESS('Sample data created successfully!')
        )

    def clear_data(self):
        """Clear existing data"""
        Product.objects.all().delete()
        Category.objects.all().delete()
        Occasion.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write('Existing data cleared.')

    def create_site_settings(self):
        """Create or update site settings"""
        settings, created = SiteSettings.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'GiftTree',
                'contact_email': 'info@gifttree.com',
                'contact_phone': '+91-9876543210',
                'delivery_charge': Decimal('50.00'),
                'free_delivery_above': Decimal('999.00'),
            }
        )
        if created:
            self.stdout.write('Site settings created.')
        else:
            self.stdout.write('Site settings already exist.')

    def create_categories(self):
        """Create sample categories"""
        categories_data = [
            {'name': 'Flowers', 'description': 'Beautiful fresh flowers for all occasions', 'is_featured': True},
            {'name': 'Roses', 'description': 'Classic roses in various colors', 'parent_name': 'Flowers'},
            {'name': 'Lilies', 'description': 'Elegant lilies for special moments', 'parent_name': 'Flowers'},
            {'name': 'Orchids', 'description': 'Exotic orchids for sophisticated taste', 'parent_name': 'Flowers'},

            {'name': 'Cakes', 'description': 'Delicious cakes for celebrations', 'is_featured': True},
            {'name': 'Birthday Cakes', 'description': 'Special cakes for birthdays', 'parent_name': 'Cakes'},
            {'name': 'Wedding Cakes', 'description': 'Elegant cakes for weddings', 'parent_name': 'Cakes'},
            {'name': 'Anniversary Cakes', 'description': 'Romantic cakes for anniversaries', 'parent_name': 'Cakes'},

            {'name': 'Gifts', 'description': 'Thoughtful gifts for loved ones', 'is_featured': True},
            {'name': 'Chocolates', 'description': 'Premium chocolates and sweets', 'parent_name': 'Gifts'},
            {'name': 'Teddy Bears', 'description': 'Cute teddy bears for all ages', 'parent_name': 'Gifts'},
            {'name': 'Jewelry', 'description': 'Beautiful jewelry pieces', 'parent_name': 'Gifts'},
        ]

        categories = {}

        # Create parent categories first
        for cat_data in categories_data:
            if 'parent_name' not in cat_data:
                category, created = Category.objects.get_or_create(
                    name=cat_data['name'],
                    defaults={
                        'description': cat_data['description'],
                        'is_featured': cat_data.get('is_featured', False),
                        'sort_order': len(categories) + 1
                    }
                )
                categories[cat_data['name']] = category
                if created:
                    self.stdout.write(f'Created category: {category.name}')

        # Create child categories
        for cat_data in categories_data:
            if 'parent_name' in cat_data:
                parent = categories.get(cat_data['parent_name'])
                if parent:
                    category, created = Category.objects.get_or_create(
                        name=cat_data['name'],
                        defaults={
                            'parent': parent,
                            'description': cat_data['description'],
                            'sort_order': len(categories) + 1
                        }
                    )
                    categories[cat_data['name']] = category
                    if created:
                        self.stdout.write(f'Created subcategory: {category.name}')

        return categories

    def create_occasions(self):
        """Create sample occasions"""
        occasions_data = [
            {'name': 'Birthday', 'description': 'Celebrate special birthdays', 'is_featured': True},
            {'name': 'Anniversary', 'description': 'Mark special anniversaries', 'is_featured': True},
            {'name': 'Valentine\'s Day', 'description': 'Express love on Valentine\'s Day', 'is_featured': True},
            {'name': 'Mother\'s Day', 'description': 'Honor mothers everywhere'},
            {'name': 'Father\'s Day', 'description': 'Celebrate fathers'},
            {'name': 'Wedding', 'description': 'Wedding celebrations'},
            {'name': 'Graduation', 'description': 'Congratulate graduates'},
            {'name': 'Get Well Soon', 'description': 'Wish someone a speedy recovery'},
            {'name': 'Congratulations', 'description': 'Celebrate achievements'},
            {'name': 'Sympathy', 'description': 'Express condolences'},
        ]

        occasions = {}
        for occ_data in occasions_data:
            occasion, created = Occasion.objects.get_or_create(
                name=occ_data['name'],
                defaults={
                    'description': occ_data['description'],
                    'is_featured': occ_data.get('is_featured', False),
                }
            )
            occasions[occ_data['name']] = occasion
            if created:
                self.stdout.write(f'Created occasion: {occasion.name}')

        return occasions

    def create_users(self):
        """Create sample users"""
        users_data = [
            {
                'email': 'john.doe@example.com',
                'username': 'johndoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+91-9876543210'
            },
            {
                'email': 'jane.smith@example.com',
                'username': 'janesmith',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone': '+91-9876543211'
            },
            {
                'email': 'mike.johnson@example.com',
                'username': 'mikejohnson',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'phone': '+91-9876543212'
            }
        ]

        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['username'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'phone': user_data['phone'],
                    'is_verified': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                users.append(user)
                self.stdout.write(f'Created user: {user.email}')

        return users

    def create_products(self, categories, occasions):
        """Create sample products"""
        products_data = [
            {
                'name': 'Red Rose Bouquet',
                'category': 'Roses',
                'description': 'Beautiful bouquet of fresh red roses, perfect for expressing love and affection.',
                'care_instructions': 'Keep in fresh water and trim stems regularly.',
                'base_price': Decimal('899.00'),
                'discount_price': Decimal('749.00'),
                'is_featured': True,
                'is_bestseller': True,
                'stock_quantity': 50,
                'occasions': ['Valentine\'s Day', 'Anniversary', 'Birthday']
            },
            {
                'name': 'White Lily Arrangement',
                'category': 'Lilies',
                'description': 'Elegant white lilies arranged in a beautiful vase.',
                'care_instructions': 'Place in indirect sunlight and change water every 2-3 days.',
                'base_price': Decimal('1299.00'),
                'stock_quantity': 30,
                'occasions': ['Wedding', 'Sympathy']
            },
            {
                'name': 'Purple Orchid Plant',
                'category': 'Orchids',
                'description': 'Exotic purple orchid plant in decorative pot.',
                'care_instructions': 'Water weekly and keep in bright, indirect light.',
                'base_price': Decimal('1999.00'),
                'discount_price': Decimal('1699.00'),
                'is_featured': True,
                'stock_quantity': 20,
                'occasions': ['Birthday', 'Congratulations']
            },
            {
                'name': 'Chocolate Birthday Cake',
                'category': 'Birthday Cakes',
                'description': 'Rich chocolate cake with chocolate frosting, perfect for birthday celebrations.',
                'base_price': Decimal('999.00'),
                'is_bestseller': True,
                'stock_quantity': 25,
                'occasions': ['Birthday']
            },
            {
                'name': 'Vanilla Wedding Cake',
                'category': 'Wedding Cakes',
                'description': 'Three-tier vanilla cake with elegant white frosting and decorations.',
                'base_price': Decimal('4999.00'),
                'stock_quantity': 10,
                'occasions': ['Wedding']
            },
            {
                'name': 'Premium Chocolate Box',
                'category': 'Chocolates',
                'description': 'Assorted premium chocolates in elegant gift box.',
                'base_price': Decimal('799.00'),
                'discount_price': Decimal('649.00'),
                'stock_quantity': 40,
                'occasions': ['Birthday', 'Anniversary', 'Valentine\'s Day']
            },
            {
                'name': 'Large Teddy Bear',
                'category': 'Teddy Bears',
                'description': 'Soft and cuddly large teddy bear, perfect gift for all ages.',
                'base_price': Decimal('1499.00'),
                'is_featured': True,
                'stock_quantity': 35,
                'occasions': ['Birthday', 'Valentine\'s Day']
            },
        ]

        for prod_data in products_data:
            category = categories.get(prod_data['category'])
            if not category:
                continue

            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'category': category,
                    'description': prod_data['description'],
                    'care_instructions': prod_data.get('care_instructions', ''),
                    'base_price': prod_data['base_price'],
                    'discount_price': prod_data.get('discount_price'),
                    'sku': f"GT{random.randint(1000, 9999)}",
                    'is_featured': prod_data.get('is_featured', False),
                    'is_bestseller': prod_data.get('is_bestseller', False),
                    'stock_quantity': prod_data['stock_quantity'],
                    'meta_title': f"{prod_data['name']} - GiftTree",
                    'meta_description': prod_data['description'][:160],
                }
            )

            if created:
                # Add occasions
                for occasion_name in prod_data.get('occasions', []):
                    occasion = occasions.get(occasion_name)
                    if occasion:
                        product.occasions.add(occasion)

                # Create variants for some products
                if 'Cake' in product.name:
                    self.create_product_variants(product, [
                        {'name': '1 Kg', 'price_adjustment': Decimal('0.00'), 'sku_suffix': '1KG'},
                        {'name': '2 Kg', 'price_adjustment': Decimal('500.00'), 'sku_suffix': '2KG'},
                        {'name': '3 Kg', 'price_adjustment': Decimal('1000.00'), 'sku_suffix': '3KG'},
                    ])
                elif 'Bouquet' in product.name:
                    self.create_product_variants(product, [
                        {'name': '12 Roses', 'price_adjustment': Decimal('0.00'), 'sku_suffix': '12R'},
                        {'name': '24 Roses', 'price_adjustment': Decimal('400.00'), 'sku_suffix': '24R'},
                        {'name': '50 Roses', 'price_adjustment': Decimal('1000.00'), 'sku_suffix': '50R'},
                    ])

                self.stdout.write(f'Created product: {product.name}')

    def create_product_variants(self, product, variants_data):
        """Create product variants"""
        for variant_data in variants_data:
            ProductVariant.objects.create(
                product=product,
                name=variant_data['name'],
                price_adjustment=variant_data['price_adjustment'],
                sku_suffix=variant_data['sku_suffix'],
                stock_quantity=random.randint(10, 30),
                sort_order=len(variants_data)
            )

    def create_addresses(self, users):
        """Create sample addresses for users"""
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Pune', 'Hyderabad']
        states = ['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'West Bengal', 'Telangana']

        for user in users:
            Address.objects.create(
                user=user,
                title='Home',
                full_name=user.get_full_name(),
                phone=user.phone,
                address_line_1=f'{random.randint(1, 999)} Main Street',
                city=random.choice(cities),
                state=random.choice(states),
                pincode=f'{random.randint(100000, 999999)}',
                is_default=True
            )
            self.stdout.write(f'Created address for user: {user.email}')