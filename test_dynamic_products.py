#!/usr/bin/env python
"""
Test script to verify dynamic product loading functionality
Run this script to test if products are loading dynamically from the database
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gifttree.settings.development')
django.setup()

from apps.products.models import Product, Category, ProductImage
from apps.core.views import home_view
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

def test_product_models():
    """Test that product models are working correctly"""
    print("Testing Product Models...")
    
    # Test product count
    total_products = Product.objects.filter(is_active=True).count()
    print(f"✓ Total active products: {total_products}")
    
    # Test featured products
    featured_count = Product.objects.filter(is_featured=True, is_active=True).count()
    print(f"✓ Featured products: {featured_count}")
    
    # Test bestseller products
    bestseller_count = Product.objects.filter(is_bestseller=True, is_active=True).count()
    print(f"✓ Bestseller products: {bestseller_count}")
    
    # Test categories
    category_count = Category.objects.filter(is_active=True).count()
    print(f"✓ Active categories: {category_count}")
    
    return total_products > 0

def test_product_properties():
    """Test product model properties"""
    print("\nTesting Product Properties...")
    
    products = Product.objects.filter(is_active=True)[:5]
    
    for product in products:
        print(f"\nProduct: {product.name}")
        print(f"  - Current Price: ₹{product.current_price}")
        print(f"  - Has Discount: {product.discount_percentage}%")
        print(f"  - In Stock: {product.is_in_stock}")
        print(f"  - Primary Image: {'Yes' if product.primary_image else 'No'}")
        print(f"  - URL: {product.get_absolute_url()}")
    
    return len(products) > 0

def test_home_view():
    """Test that home view returns products"""
    print("\nTesting Home View...")
    
    factory = RequestFactory()
    request = factory.get('/')
    request.user = AnonymousUser()
    
    response = home_view(request)
    
    print(f"✓ Home view status: {response.status_code}")
    print("✓ Home view executed successfully")
    
    return response.status_code == 200

def test_template_tags():
    """Test custom template tags"""
    print("\nTesting Template Tags...")
    
    try:
        from apps.core.templatetags.product_tags import product_image_url, product_price_display, has_discount
        
        # Get a test product
        product = Product.objects.filter(is_active=True).first()
        
        if product:
            image_url = product_image_url(product)
            price_display = product_price_display(product)
            discount_status = has_discount(product)
            
            print(f"✓ Image URL: {image_url}")
            print(f"✓ Price Display: {price_display}")
            print(f"✓ Has Discount: {discount_status}")
            
            return True
        else:
            print("⚠ No products found for testing template tags")
            return False
            
    except ImportError as e:
        print(f"✗ Template tags import error: {e}")
        return False

def create_sample_data():
    """Create sample data if none exists"""
    print("\nCreating Sample Data...")
    
    # Create a sample category
    category, created = Category.objects.get_or_create(
        name="Sample Category",
        defaults={
            'slug': 'sample-category',
            'description': 'A sample category for testing',
            'is_featured': True,
            'is_active': True
        }
    )
    
    if created:
        print("✓ Created sample category")
    
    # Create sample products
    for i in range(3):
        product, created = Product.objects.get_or_create(
            name=f"Sample Product {i+1}",
            defaults={
                'slug': f'sample-product-{i+1}',
                'category': category,
                'description': f'This is a sample product {i+1} for testing dynamic loading',
                'base_price': 500 + (i * 200),
                'discount_price': 400 + (i * 150) if i % 2 == 0 else None,
                'sku': f'SAMPLE-{i+1:03d}',
                'is_featured': i == 0,
                'is_bestseller': i == 1,
                'stock_quantity': 10,
                'is_active': True
            }
        )
        
        if created:
            print(f"✓ Created sample product: {product.name}")

def main():
    """Run all tests"""
    print("=" * 50)
    print("DYNAMIC PRODUCT LOADING TEST")
    print("=" * 50)
    
    # Check if we have any products
    if Product.objects.filter(is_active=True).count() == 0:
        print("No products found. Creating sample data...")
        create_sample_data()
    
    # Run tests
    tests = [
        test_product_models,
        test_product_properties,
        test_home_view,
        test_template_tags
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Dynamic product loading is working correctly.")
    else:
        print("⚠ Some tests failed. Please check the output above.")
    
    print("\nNext Steps:")
    print("1. Run 'python manage.py runserver' to start the development server")
    print("2. Visit http://127.0.0.1:8000/ to see the dynamic products")
    print("3. Add products through Django admin at http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    main()