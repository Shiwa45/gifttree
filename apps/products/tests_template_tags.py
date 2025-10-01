from django.test import TestCase
from django.template import Context, Template
from decimal import Decimal
from apps.products.models import Product, Category, ProductVariant
from apps.products.templatetags.pricing_tags import (
    get_product_price, get_variant_price, currency_format, has_discount
)


class ProductTemplateTagsTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name="Test Category",
            slug="test-category"
        )
        
        # Product with base price only
        self.product_no_discount = Product.objects.create(
            name="No Discount Product",
            slug="no-discount-product",
            category=self.category,
            description="Test product without discount",
            base_price=Decimal('100.00'),
            sku="TEST001"
        )
        
        # Product with discount
        self.product_with_discount = Product.objects.create(
            name="Discount Product",
            slug="discount-product",
            category=self.category,
            description="Test product with discount",
            base_price=Decimal('100.00'),
            discount_price=Decimal('80.00'),
            sku="TEST002"
        )
        
        # Product variant
        self.variant = ProductVariant.objects.create(
            product=self.product_no_discount,
            name="Large",
            price_adjustment=Decimal('20.00'),
            sku_suffix="L"
        )

    def test_get_product_price_no_discount(self):
        """Test getting price for product without discount"""
        price = get_product_price(self.product_no_discount)
        self.assertEqual(price, Decimal('100.00'))

    def test_get_product_price_with_discount(self):
        """Test getting price for product with discount"""
        price = get_product_price(self.product_with_discount)
        self.assertEqual(price, Decimal('80.00'))

    def test_get_variant_price(self):
        """Test getting variant price with adjustment"""
        price = get_variant_price(self.variant)
        self.assertEqual(price, Decimal('120.00'))  # 100 + 20

    def test_currency_format_filter(self):
        """Test currency formatting filter"""
        self.assertEqual(currency_format(100), "₹100")
        self.assertEqual(currency_format(1000), "₹1,000")
        self.assertEqual(currency_format(None), "Price not available")
        self.assertEqual(currency_format("invalid"), "Price not available")

    def test_has_discount_filter(self):
        """Test discount detection filter"""
        self.assertFalse(has_discount(self.product_no_discount))
        self.assertTrue(has_discount(self.product_with_discount))

    def test_display_price_template_tag_no_discount(self):
        """Test price display template tag without discount"""
        template = Template(
            "{% load pricing_tags %}"
            "{% display_price product %}"
        )
        context = Context({'product': self.product_no_discount})
        rendered = template.render(context)
        
        self.assertIn('₹100', rendered)
        self.assertNotIn('OFF', rendered)
        self.assertNotIn('You save', rendered)

    def test_display_price_template_tag_with_discount(self):
        """Test price display template tag with discount"""
        template = Template(
            "{% load pricing_tags %}"
            "{% display_price product %}"
        )
        context = Context({'product': self.product_with_discount})
        rendered = template.render(context)
        
        self.assertIn('₹80', rendered)  # Current price
        self.assertIn('₹100', rendered)  # Original price
        self.assertIn('20% OFF', rendered)  # Discount badge
        self.assertIn('You save ₹20', rendered)  # Savings

    def test_display_price_template_tag_hide_discount(self):
        """Test price display template tag with discount hidden"""
        template = Template(
            "{% load pricing_tags %}"
            "{% display_price product show_discount=False %}"
        )
        context = Context({'product': self.product_with_discount})
        rendered = template.render(context)
        
        self.assertIn('₹80', rendered)  # Current price
        self.assertNotIn('₹100', rendered)  # Original price hidden
        self.assertNotIn('OFF', rendered)  # No discount badge

    def test_display_price_template_tag_hide_savings(self):
        """Test price display template tag with savings hidden"""
        template = Template(
            "{% load pricing_tags %}"
            "{% display_price product show_savings=False %}"
        )
        context = Context({'product': self.product_with_discount})
        rendered = template.render(context)
        
        self.assertIn('₹80', rendered)  # Current price
        self.assertIn('₹100', rendered)  # Original price
        self.assertNotIn('You save', rendered)  # No savings text

    def test_display_price_with_css_class(self):
        """Test price display with custom CSS class"""
        template = Template(
            "{% load pricing_tags %}"
            "{% display_price product css_class='custom-price' %}"
        )
        context = Context({'product': self.product_no_discount})
        rendered = template.render(context)
        
        self.assertIn('custom-price', rendered)

    def test_product_with_missing_fields(self):
        """Test handling of products with missing price fields"""
        # Create a mock product-like object with missing fields
        class MockProduct:
            def __init__(self):
                self.base_price = Decimal('50.00')
        
        mock_product = MockProduct()
        price = get_product_price(mock_product)
        self.assertEqual(price, Decimal('50.00'))

    def test_zero_price_handling(self):
        """Test handling of zero prices"""
        zero_price_product = Product.objects.create(
            name="Free Product",
            slug="free-product",
            category=self.category,
            description="Free test product",
            base_price=Decimal('0.00'),
            sku="FREE001"
        )
        
        price = get_product_price(zero_price_product)
        self.assertEqual(price, Decimal('0.00'))
        
        formatted = currency_format(price)
        self.assertEqual(formatted, "₹0")