from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.test import RequestFactory
from apps.products.models import Product, Category
from apps.core.views import home_view


class Command(BaseCommand):
    help = 'Test dynamic product loading functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-sample',
            action='store_true',
            help='Create sample products for testing',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Dynamic Product Loading...'))
        
        if options['create_sample']:
            self.create_sample_data()
        
        self.test_products()
        self.test_home_view()
        self.test_template_rendering()
        
        self.stdout.write(self.style.SUCCESS('All tests completed!'))

    def create_sample_data(self):
        """Create sample data for testing"""
        self.stdout.write('Creating sample data...')
        
        # Create sample category
        category, created = Category.objects.get_or_create(
            name="Test Category",
            defaults={
                'slug': 'test-category',
                'description': 'A test category for dynamic loading',
                'is_featured': True,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'Created category: {category.name}')
        
        # Create sample products
        for i in range(5):
            product, created = Product.objects.get_or_create(
                name=f"Test Product {i+1}",
                defaults={
                    'slug': f'test-product-{i+1}',
                    'category': category,
                    'description': f'Test product {i+1} for dynamic loading verification',
                    'base_price': 299 + (i * 100),
                    'discount_price': 199 + (i * 80) if i % 2 == 0 else None,
                    'sku': f'TEST-{i+1:03d}',
                    'is_featured': i < 2,
                    'is_bestseller': i >= 2,
                    'stock_quantity': 10,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Created product: {product.name}')

    def test_products(self):
        """Test product model functionality"""
        self.stdout.write('Testing product models...')
        
        total_products = Product.objects.filter(is_active=True).count()
        featured_products = Product.objects.filter(is_featured=True, is_active=True).count()
        bestseller_products = Product.objects.filter(is_bestseller=True, is_active=True).count()
        
        self.stdout.write(f'Total active products: {total_products}')
        self.stdout.write(f'Featured products: {featured_products}')
        self.stdout.write(f'Bestseller products: {bestseller_products}')
        
        if total_products == 0:
            self.stdout.write(
                self.style.WARNING('No products found! Run with --create-sample to create test data.')
            )

    def test_home_view(self):
        """Test home view functionality"""
        self.stdout.write('Testing home view...')
        
        factory = RequestFactory()
        request = factory.get('/')
        
        try:
            response = home_view(request)
            self.stdout.write(f'Home view status: {response.status_code}')
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✓ Home view working correctly'))
            else:
                self.stdout.write(self.style.ERROR('✗ Home view returned error'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Home view error: {e}'))

    def test_template_rendering(self):
        """Test template rendering with products"""
        self.stdout.write('Testing template rendering...')
        
        try:
            # Test product card rendering
            product = Product.objects.filter(is_active=True).first()
            
            if product:
                context = {
                    'product': product,
                    'card_type': 'mobile',
                    'show_wishlist': False,
                    'show_rating': False
                }
                
                rendered = render_to_string('includes/product_card.html', context)
                
                if rendered and len(rendered) > 100:
                    self.stdout.write(self.style.SUCCESS('✓ Product card template rendering correctly'))
                else:
                    self.stdout.write(self.style.WARNING('⚠ Product card template may have issues'))
            else:
                self.stdout.write(self.style.WARNING('⚠ No products available for template testing'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Template rendering error: {e}'))