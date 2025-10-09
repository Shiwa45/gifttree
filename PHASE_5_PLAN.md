# Phase 5: Final Polish, SEO & Deployment Prep
Timeline: Day 10-12
Priority: MEDIUM

## Overview
Update banners, setup SEO, optimize performance, final testing, and prepare for deployment.

## Task 5.1: Update Banners for Diwali Special

Issue: Need to update homepage banners with Diwali theme

Files to Modify:
- templates/core/home.html
- Create/upload banner images

Step 1: Create Banner Model (if not exists)

In apps/core/models.py, add:

class BannerImage(BaseModel):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    mobile_image = models.ImageField(upload_to='banners/mobile/', blank=True)
    link_url = models.URLField(blank=True)
    button_text = models.CharField(max_length=50, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['sort_order']
    
    def __str__(self):
        return self.title

Step 2: Register in Admin

In apps/core/admin.py:

from .models import BannerImage

@admin.register(BannerImage)
class BannerImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'sort_order', 'is_active', 'created_at']
    list_editable = ['sort_order', 'is_active']
    list_filter = ['is_active']

Step 3: Update Home View

In apps/core/views.py:

def home_view(request):
    # existing code...
    
    banner_images = BannerImage.objects.filter(is_active=True)
    
    context = {
        # existing context...
        'banner_images': banner_images,
    }
    return render(request, 'core/home.html', context)

Step 4: Update Home Template

In templates/core/home.html, find slider section and update:

<div class="mobile-slider">
    <div class="slider-container" id="sliderContainer">
        {% for banner in banner_images %}
        <div class="slide slide-{{ forloop.counter }}" 
             {% if banner.link_url %}onclick="window.location.href='{{ banner.link_url }}'"{% endif %}
             style="background-image: url('{{ banner.image.url }}');">
            {% if banner.button_text %}
            <div class="banner-content">
                <h2>{{ banner.title }}</h2>
                <button class="banner-btn">{{ banner.button_text }}</button>
            </div>
            {% endif %}
        </div>
        {% empty %}
        <!-- Fallback static banners -->
        <div class="slide" style="background-image: url('{% static 'images/banner/diwali-special.jpg' %}');"></div>
        {% endfor %}
    </div>
</div>

Banner Images Needed:
Upload to static/images/banner/:
- diwali-special.jpg (1200x400px)
- chocolate-special.jpg (1200x400px)
- unique-gifts.jpg (1200x400px)
- new-arrivals.jpg (1200x400px)

Mobile versions (optional):
- diwali-special-mobile.jpg (800x600px)

## Task 5.2: Create Featured Products Banners

Issue: Need chocolate and 25 unique gifts banners

Files to Modify:
- templates/core/home.html
- Create category showcase sections

Step 1: Add Featured Sections to Home Template

In templates/core/home.html, add after quick actions:

<!-- Featured: Chocolate Gifts -->
<section class="featured-section">
    <div class="container">
        <div class="featured-banner" 
             style="background-image: url('{% static 'images/banners/chocolate-banner.jpg' %}');"
             onclick="window.location.href='{% url 'products:product_list' %}?category=chocolates'">
            <div class="banner-overlay">
                <h2>🍫 Premium Chocolate Collection</h2>
                <p>Indulge in luxury chocolates for every occasion</p>
                <button class="explore-btn">Explore Chocolates</button>
            </div>
        </div>
    </div>
</section>

<!-- Featured: 25 Unique Gifts -->
<section class="featured-section">
    <div class="container">
        <div class="featured-banner"
             style="background-image: url('{% static 'images/banners/unique-gifts-banner.jpg' %}');"
             onclick="window.location.href='{% url 'products:product_list' %}?filter=unique'">
            <div class="banner-overlay">
                <h2>🎁 25 Unique Gift Ideas</h2>
                <p>Discover one-of-a-kind gifts they'll never forget</p>
                <button class="explore-btn">Browse Unique Gifts</button>
            </div>
        </div>
    </div>
</section>

Add CSS:

<style>
.featured-section {
    padding: 40px 0;
}

.featured-banner {
    height: 300px;
    border-radius: 16px;
    background-size: cover;
    background-position: center;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: transform 0.3s;
    overflow: hidden;
    position: relative;
}

.featured-banner:hover {
    transform: scale(1.02);
}

.banner-overlay {
    text-align: center;
    color: white;
    padding: 40px;
    background: rgba(0,0,0,0.5);
    border-radius: 12px;
}

.banner-overlay h2 {
    font-size: 2.5rem;
    margin-bottom: 15px;
}

.banner-overlay p {
    font-size: 1.2rem;
    margin-bottom: 20px;
}

.explore-btn {
    background: white;
    color: #E91E63;
    border: none;
    padding: 12px 32px;
    border-radius: 25px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
}

.explore-btn:hover {
    background: #E91E63;
    color: white;
    transform: scale(1.05);
}

@media (max-width: 768px) {
    .featured-banner {
        height: 200px;
    }
    
    .banner-overlay h2 {
        font-size: 1.5rem;
    }
    
    .banner-overlay p {
        font-size: 0.9rem;
    }
}
</style>

Step 2: Create Banner Images

Create these banners:
- chocolate-banner.jpg - Image of premium chocolates
- unique-gifts-banner.jpg - Collage of unique gift items

## Task 5.3: Google Search Console Setup

Issue: Setup Google Search Console for SEO

Files to Create:
- templates/sitemap.xml
- static/robots.txt
- Add structured data to product pages

Step 1: Create Sitemap

Create templates/sitemap.xml:

<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://mygifttree.com/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    {% for category in categories %}
    <url>
        <loc>https://mygifttree.com{{ category.get_absolute_url }}</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    {% endfor %}
    {% for product in products %}
    <url>
        <loc>https://mygifttree.com{{ product.get_absolute_url }}</loc>
        <lastmod>{{ product.updated_at|date:"Y-m-d" }}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.6</priority>
    </url>
    {% endfor %}
</urlset>

Step 2: Create Sitemap View

In apps/core/views.py:

from django.http import HttpResponse
from django.template import loader
from apps.products.models import Product, Category

def sitemap_view(request):
    template = loader.get_template('sitemap.xml')
    
    context = {
        'categories': Category.objects.filter(is_active=True),
        'products': Product.objects.filter(is_active=True)[:500],
    }
    
    return HttpResponse(
        template.render(context, request),
        content_type='application/xml'
    )

Step 3: Add Sitemap URL

In apps/core/urls.py:

urlpatterns = [
    path('', views.home_view, name='home'),
    path('offers/', views.offers_view, name='offers'),
    path('sitemap.xml', views.sitemap_view, name='sitemap'),
]

Step 4: Create robots.txt

Create static/robots.txt:

User-agent: *
Allow: /
Disallow: /admin/
Disallow: /cart/
Disallow: /checkout/
Disallow: /account/
Disallow: /wallet/

Sitemap: https://mygifttree.com/sitemap.xml

Step 5: Add Structured Data to Products

In templates/products/product_detail.html, add in head:

<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": "{{ product.name }}",
  "image": "{{ request.scheme }}://{{ request.get_host }}{{ product.primary_image.url }}",
  "description": "{{ product.description|truncatewords:50 }}",
  "brand": {
    "@type": "Brand",
    "name": "MyGiftTree"
  },
  "offers": {
    "@type": "Offer",
    "url": "{{ request.build_absolute_uri }}",
    "priceCurrency": "INR",
    "price": "{{ product.current_price }}",
    "availability": "{% if product.is_in_stock %}https://schema.org/InStock{% else %}https://schema.org/OutOfStock{% endif %}"
  }
  {% if product_reviews %}
  ,
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "{{ average_rating }}",
    "reviewCount": "{{ reviews_count }}"
  }
  {% endif %}
}
</script>

Manual Steps for Google Search Console:
1. Go to https://search.google.com/search-console
2. Add property: mygifttree.com
3. Verify ownership (HTML file or DNS)
4. Submit sitemap: https://mygifttree.com/sitemap.xml
5. Request indexing for main pages
6. Set up URL inspection
7. Monitor coverage and performance

## Task 5.4: Performance Optimization

Files to Modify:
- gifttree/settings/base.py
- templates/base.html

Step 1: Enable Caching

In settings/base.py:

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# Template Caching
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

Create cache table:
python manage.py createcachetable

Step 2: Optimize Images

Add to base.html:

<!-- Preload critical images -->
<link rel="preload" as="image" href="{% static 'images/logo.png' %}">

<!-- Lazy loading for images -->
<img src="..." loading="lazy" alt="...">

Step 3: Add Compression

In settings/base.py:

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',  # ADD THIS FIRST
    # ... existing middleware ...
]

Step 4: Static File Optimization

# Collect and compress static files
python manage.py collectstatic --noinput

# Enable compression in production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

## Task 5.5: Security Hardening

Files to Modify:
- gifttree/settings/production.py

Step 1: Update Production Settings

In settings/production.py:

# Security Settings
DEBUG = False
ALLOWED_HOSTS = ['mygifttree.com', 'www.mygifttree.com']

# HTTPS Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Additional Security
SECURE_REFERRER_POLICY = 'same-origin'

Step 2: Create Security Checklist

Run Django security check:
python manage.py check --deploy

Fix any warnings shown.

## Task 5.6: Final Testing & Bug Fixes

Testing Checklist:

Desktop Testing:
- [ ] All pages load without errors
- [ ] All images display correctly
- [ ] Navigation works on all pages
- [ ] Forms submit correctly
- [ ] Payment flow works end-to-end
- [ ] Wallet system functional
- [ ] Add-ons work on products
- [ ] Reviews display correctly
- [ ] Search works
- [ ] Filters work on product list
- [ ] Cart functions properly
- [ ] Checkout completes successfully

Mobile Testing:
- [ ] All pages responsive
- [ ] Bottom navigation works
- [ ] Touch targets are large enough
- [ ] Forms are mobile-friendly
- [ ] Images load properly
- [ ] No horizontal scroll
- [ ] Payment works on mobile
- [ ] Product cards sized correctly

SEO Testing:
- [ ] All pages have unique titles
- [ ] Meta descriptions present
- [ ] Images have alt text
- [ ] Structured data validates
- [ ] Sitemap accessible
- [ ] Robots.txt accessible
- [ ] No broken links

Performance Testing:
- [ ] Page load time < 3 seconds
- [ ] Images optimized
- [ ] No console errors
- [ ] No 404 errors
- [ ] Caching working

Security Testing:
- [ ] HTTPS working
- [ ] Forms have CSRF tokens
- [ ] Login required where needed
- [ ] SQL injection protected
- [ ] XSS protected

## Task 5.7: Create Documentation

Files to Create:
- README.md
- DEPLOYMENT.md
- API_DOCUMENTATION.md (if applicable)

Step 1: Update README.md

# MyGiftTree - E-commerce Platform

Online gift shop for flowers, cakes, and gifts with same-day delivery.

## Features
- Product catalog with categories
- Shopping cart and checkout
- Payment integration (Razorpay)
- Wallet system (200 coins on signup)
- Product reviews and ratings
- Mobile responsive design
- Admin panel
- SEO optimized

## Tech Stack
- Django 5.x
- PostgreSQL/SQLite
- Bootstrap 5
- Razorpay Payment Gateway
- Celery (optional)

## Installation

1. Clone repository
2. Create virtual environment
3. Install dependencies: pip install -r requirements.txt
4. Run migrations: python manage.py migrate
5. Create superuser: python manage.py createsuperuser
6. Run server: python manage.py runserver

## Environment Variables

DJANGO_SECRET_KEY=your-secret-key
DEBUG=False
RAZORPAY_KEY_ID=your-key
RAZORPAY_KEY_SECRET=your-secret
DATABASE_URL=your-db-url

## Project Structure

gifttree/
├── apps/
│   ├── core/
│   ├── products/
│   ├── cart/
│   ├── orders/
│   ├── users/
│   ├── reviews/
│   └── wallet/
├── templates/
├── static/
└── gifttree/

## Contributing
Contact: support@mygifttree.com

Step 2: Create DEPLOYMENT.md with deployment instructions

## Migration Commands for Phase 5

python manage.py makemigrations core
python manage.py migrate
python manage.py createcachetable
python manage.py collectstatic --noinput

## Post-Deployment Checklist

- [ ] All environment variables set
- [ ] Database migrations run
- [ ] Static files collected
- [ ] Cache table created
- [ ] Superuser created
- [ ] Sample data populated
- [ ] Google Search Console setup
- [ ] SSL certificate installed
- [ ] Domain DNS configured
- [ ] Email service configured
- [ ] Payment gateway in live mode
- [ ] Backup strategy in place
- [ ] Monitoring tools setup

## Files Modified/Created Summary

New Files:
1. apps/core/models.py - BannerImage model
2. templates/sitemap.xml
3. static/robots.txt
4. README.md
5. DEPLOYMENT.md

Modified Files:
1. apps/core/admin.py - Register BannerImage
2. apps/core/views.py - Sitemap view, banners
3. apps/core/urls.py - Sitemap URL
4. templates/core/home.html - Banner sections
5. templates/products/product_detail.html - Structured data
6. gifttree/settings/base.py - Caching, compression
7. gifttree/settings/production.py - Security settings

Banner Images Needed:
- static/images/banner/diwali-special.jpg
- static/images/banner/chocolate-special.jpg
- static/images/banner/unique-gifts.jpg
- static/images/banners/chocolate-banner.jpg
- static/images/banners/unique-gifts-banner.jpg

Estimated Time: 8-10 hours
Risk Level: LOW
Complexity: MEDIUM
Migrations: YES (if BannerImage is new)
SEO Setup: Manual steps required