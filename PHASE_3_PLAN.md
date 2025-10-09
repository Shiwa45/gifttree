# Phase 3: Content Updates & Product Enhancements
Timeline: Day 5-6
Priority: MEDIUM-HIGH

## Overview
Fix missing images, create cakes page, add-ons system, and real reviews display.

## Task 3.1: Update Home Page Category Images

Issue: Category images not showing on homepage

Files to Modify:
- templates/core/home.html

Solution: Verify image paths and add fallback

Images Needed in static/images/category/:
- birthday.png
- anniversary.jpg
- flowers.webp
- cakes.webp
- gifts.webp
- plants.webp

## Task 3.2: Create Send Cakes Category Page

Files to Create/Modify:
1. templates/products/cakes_category.html (NEW)
2. apps/products/views.py
3. apps/products/urls.py

Step 1: Add CakeCategoryView to apps/products/views.py

Add this class:

class CakeCategoryView(TemplateView):
    template_name = 'products/cakes_category.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            cakes_category = Category.objects.get(slug='cakes', is_active=True)
        except Category.DoesNotExist:
            cakes_category = None
        
        context['cakes_category'] = cakes_category
        
        if cakes_category:
            context['cake_subcategories'] = Category.objects.filter(
                parent=cakes_category,
                is_active=True
            ).order_by('sort_order')
        
        context['featured_cakes'] = Product.objects.filter(
            is_featured=True,
            is_active=True
        )[:8]
        
        return context

Step 2: Add URL pattern to apps/products/urls.py

Add this line in urlpatterns:
path('cakes/', views.CakeCategoryView.as_view(), name='cakes_category'),

Step 3: Create templates/products/cakes_category.html
This is a new template file - create it with basic structure

## Task 3.3: Add-ons System

Step 1: Create ProductAddOn model in apps/products/models.py

class ProductAddOn(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='addons/', blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - Rs {self.price}"

Step 2: Update Product model with method

def get_available_addons(self):
    return ProductAddOn.objects.filter(is_active=True)[:6]

Step 3: Update ProductDetailView in apps/products/views.py

Add to get_context_data:
context['available_addons'] = self.object.get_available_addons()

Step 4: Register in apps/products/admin.py

from .models import ProductAddOn
admin.site.register(ProductAddOn)

## Task 3.4: Display Real Reviews

Update ProductDetailView in apps/products/views.py

Add to get_context_data:

from apps.reviews.models import Review

reviews = Review.objects.filter(
    product=self.object,
    is_approved=True,
    is_active=True
).select_related('user')[:10]

context['product_reviews'] = reviews
context['reviews_count'] = reviews.count()

if reviews.exists():
    avg = sum([r.rating for r in reviews]) / reviews.count()
    context['average_rating'] = round(avg, 1)

## Migration Steps

After making model changes:

python manage.py makemigrations products
python manage.py migrate

Create sample add-ons:

python manage.py shell

from apps.products.models import ProductAddOn
ProductAddOn.objects.create(name="Chocolate Cake", price=299, is_active=True)
ProductAddOn.objects.create(name="Teddy Bear", price=199, is_active=True)
ProductAddOn.objects.create(name="Greeting Card", price=149, is_active=True)

## Testing Checklist

Desktop:
- Home page category images display
- /products/cakes/ page loads
- Add-ons show on product pages
- Reviews display from database

Mobile:
- 2-column layout on mobile
- Add-ons scrollable
- Reviews readable

## Files Modified

Python:
1. apps/products/models.py - Add ProductAddOn
2. apps/products/views.py - CakeCategoryView, reviews
3. apps/products/urls.py - Add cakes URL
4. apps/products/admin.py - Register ProductAddOn

Templates:
1. templates/core/home.html - Fix images
2. templates/products/cakes_category.html - NEW
3. templates/products/product_detail.html - Add-ons, reviews

Assets Needed:
- Category images
- Cake category images
- Add-on images

Estimated Time: 8-10 hours
Risk Level: MEDIUM
Migrations: YES