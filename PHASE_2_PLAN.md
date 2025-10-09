# Phase 2: Bug Fixes & Product Enhancements
**Timeline:** Day 3-4  
**Priority:** HIGH

---

## Overview
Fix critical bugs: recommended products not showing, mobile styling issues, and offers button not working.

---

## Task 2.1: Fix Recommended Products Not Showing

**Issue:** Product detail page shows empty "Similar Products" section

**Files to Modify:**
- apps/products/views.py
- templates/products/product_detail.html

**Solution:**

Update ProductDetailView in apps/products/views.py:

```python
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from django.db import models
from .models import Product, Category

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True
        ).select_related('category').prefetch_related('images', 'variants')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # FIX: Get related products from same category
        related_products = Product.objects.filter(
            category=self.object.category,
            is_active=True,
            stock_quantity__gt=0
        ).exclude(
            pk=self.object.pk
        ).select_related('category').prefetch_related('images')[:6]
        
        # DEBUG logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Found {related_products.count()} related products for {self.object.name}")
        
        context['related_products'] = related_products
        
        # BONUS: recommended products
        context['recommended_products'] = Product.objects.filter(
            category=self.object.category,
            is_active=True,
            stock_quantity__gt=0
        ).filter(
            models.Q(is_bestseller=True) | models.Q(is_featured=True)
        ).exclude(pk=self.object.pk)[:4]
        
        return context
```

---

## Task 2.2: Fix Related Products Mobile Styling

**Issue:** Related products too large on mobile, breaking layout

**Files to Modify:**
- templates/products/product_detail.html

**Solution:**

Add this CSS in the {% block extra_css %} section of templates/products/product_detail.html:

```css
/* Mobile Related Products Fix */
@media (max-width: 768px) {
    .similar-products {
        padding: 20px 12px;
        margin: 16px 0;
        background: white;
    }
    
    .similar-title {
        font-size: 18px;
        padding: 0 8px 12px;
        margin-bottom: 12px;
    }
    
    .similar-scroll {
        padding: 0 4px;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
    }
    
    .similar-scroll::-webkit-scrollbar {
        display: none;
    }
    
    .similar-row {
        display: flex;
        gap: 12px;
        padding: 4px 0;
    }
    
    .similar-card {
        width: 130px !important;
        min-width: 130px;
        max-width: 130px;
        flex-shrink: 0;
        margin: 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-radius: 12px;
        overflow: hidden;
        background: white;
        cursor: pointer;
        transition: transform 0.2s ease;
    }
    
    .similar-card:active {
        transform: scale(0.95);
    }
    
    .similar-image {
        width: 100%;
        height: 130px !important;
        object-fit: cover;
    }
    
    .similar-info {
        padding: 8px;
    }
    
    .similar-name {
        font-size: 12px;
        line-height: 1.3;
        margin-bottom: 4px;
        font-weight: 500;
        color: #333;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }
    
    .similar-price {
        font-size: 13px;
        font-weight: 600;
        color: var(--primary-color);
    }
}

/* Tablet */
@media (min-width: 769px) and (max-width: 991px) {
    .similar-card {
        width: 160px !important;
        min-width: 160px;
    }
    
    .similar-image {
        height: 160px !important;
    }
}

/* Desktop */
@media (min-width: 992px) {
    .similar-products {
        padding: 30px 40px;
    }
    
    .similar-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
}
```

---

## Task 2.3: Fix Offers Button Not Working

**Issue:** Offers button doesn't navigate anywhere

**Files to Create/Modify:**
1. apps/core/views.py - Add offers_view
2. apps/core/urls.py - Add offers URL
3. templates/core/offers.html - CREATE NEW
4. templates/includes/mobile_navigation.html - Update link

**Solution:**

### Step 1: Add offers_view to apps/core/views.py

Add this function:

```python
from django.shortcuts import render
from apps.products.models import Product

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
```

### Step 2: Update apps/core/urls.py

Add this URL pattern:

```python
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('offers/', views.offers_view, name='offers'),  # ADD THIS
]
```

### Step 3: Create templates/core/offers.html

CREATE THIS NEW FILE with complete content.

### Step 4: Update Navigation Links

In templates/includes/mobile_navigation.html, find offers link and change to:

```html
<a href="{% url 'core:offers' %}" class="nav-item">
    <i class="fas fa-percent"></i>
    <span>Offers</span>
</a>
```

---

## Testing Checklist

### Desktop:
- [ ] Product detail shows 4-6 related products
- [ ] Related products have images and prices
- [ ] Clicking product navigates correctly
- [ ] Offers page loads at /offers/
- [ ] All products clickable

### Mobile:
- [ ] Product cards are 130px wide
- [ ] Horizontal scroll works smoothly
- [ ] No page overflow
- [ ] Offers button in bottom nav works
- [ ] Offers page responsive (2 columns)

### Console:
- [ ] No JavaScript errors
- [ ] No 404 errors
- [ ] Debug log shows product count

---

## Success Criteria

Phase 2 complete when:
1. Related products show on all product pages
2. Mobile cards properly sized (130px)
3. Offers page functional at /offers/
4. Zero console errors
5. All navigation working

---

## Files Modified Summary

Python:
1. apps/products/views.py
2. apps/core/views.py
3. apps/core/urls.py

Templates:
1. templates/products/product_detail.html
2. templates/core/offers.html (NEW)
3. templates/includes/mobile_navigation.html

---

## Important Notes

- No database migrations needed
- All changes are view/template only
- Performance optimized with select_related()
- Graceful handling of missing data
- Mobile-first CSS approach

---

Estimated Time: 6-8 hours
Risk Level: LOW-MEDIUM
No downtime required