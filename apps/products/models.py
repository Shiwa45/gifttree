# apps/products/models.py - COMPLETE FINAL VERSION

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel

User = get_user_model()


class Category(BaseModel):
    """Product categories with hierarchy"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    image = models.ImageField(upload_to='categories/', blank=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})

    @property
    def product_count(self):
        return self.products.filter(is_active=True).count()


class Occasion(BaseModel):
    """Special occasions for products"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='occasions/', blank=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:occasion_detail', kwargs={'slug': self.slug})


class MenuBadge(BaseModel):
    """Badges for menu items (New, Hot Selling, Premium, etc.)"""
    name = models.CharField(max_length=50)  # "New", "Hot Selling", "Must Try", "Premium"
    color = models.CharField(max_length=7, default='#FFFFFF')  # Text color (hex)
    background_color = models.CharField(max_length=7, default='#FF0000')  # Background color (hex)
    css_class = models.CharField(max_length=50, blank=True)  # Additional CSS class
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class MenuCategory(BaseModel):
    """Enhanced categories for advanced menu system"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    icon = models.CharField(max_length=50, blank=True)  # Font Awesome icon class
    image = models.ImageField(upload_to='menu_categories/', blank=True)
    description = models.TextField(blank=True)
    
    # Menu display settings
    is_active = models.BooleanField(default=True)
    show_in_mega_menu = models.BooleanField(default=True)
    show_in_mobile_menu = models.BooleanField(default=True)
    menu_columns = models.PositiveIntegerField(default=4)  # Columns in mega menu
    featured_products_count = models.PositiveIntegerField(default=3)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Menu Categories"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:menu_category_detail', kwargs={'slug': self.slug})


class MenuSection(BaseModel):
    """Sections within menu categories (By Type, Collection, For Whom, etc.)"""
    SECTION_TYPES = [
        ('by_type', 'By Type'),
        ('collection', 'Collection'),
        ('for_whom', 'For Whom'),
        ('by_occasion', 'By Occasion'),
        ('deliver_to', 'Deliver To'),
        ('price_range', 'Price Range'),
        ('custom', 'Custom'),
    ]
    
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=100)  # "By Type", "Collection", etc.
    slug = models.SlugField()
    section_type = models.CharField(max_length=50, choices=SECTION_TYPES)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']
        unique_together = ['category', 'slug']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductType(BaseModel):
    """Product types for filtering (Roses, Lilies, Orchids, etc.)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_types')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='product_types/', blank=True)
    badges = models.ManyToManyField(MenuBadge, blank=True, related_name='product_types')
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product_type_detail', kwargs={'slug': self.slug})


class Collection(BaseModel):
    """Product collections (Bestseller, Signature Boxes, etc.)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='collections/', blank=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='collections')
    badges = models.ManyToManyField(MenuBadge, blank=True, related_name='collections')
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:collection_detail', kwargs={'slug': self.slug})


class Recipient(BaseModel):
    """Recipients for gift filtering (Girlfriend, Wife, Parents, etc.)"""
    RECIPIENT_CATEGORIES = [
        ('personal', 'Personal'),
        ('family', 'Family'),
        ('professional', 'Professional'),
        ('special', 'Special'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=50, choices=RECIPIENT_CATEGORIES, default='personal')
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:recipient_detail', kwargs={'slug': self.slug})


class DeliveryLocation(BaseModel):
    """Delivery locations for filtering (Delhi, Mumbai, etc.)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    is_major_city = models.BooleanField(default=False)
    is_metro = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f"{self.name}, {self.state}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:location_detail', kwargs={'slug': self.slug})


class MenuConfiguration(BaseModel):
    """Configuration settings for menu system"""
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['key']

    def __str__(self):
        return self.key


class Product(BaseModel):
    """
    Enhanced Product model - supports both manual entry and CSV import
    Combines original GiftTree fields + CSV import fields
    """
    # ============================================
    # IDENTIFIERS
    # ============================================
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(unique=True)
    handle = models.SlugField(max_length=255, blank=True, db_index=True)  # For CSV import (Shopify)
    common_product_id = models.CharField(max_length=100, blank=True, null=True)  # CSV field
    
    # ============================================
    # BASIC INFORMATION
    # ============================================
    name = models.CharField(max_length=500)
    description = models.TextField()
    body_html = models.TextField(blank=True, null=True)  # Shopify HTML description
    summary = models.TextField(blank=True, null=True)  # CSV field
    care_instructions = models.TextField(blank=True)
    
    # ============================================
    # CATEGORIZATION
    # ============================================
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    sub_category = models.CharField(max_length=200, blank=True, null=True)  # CSV field
    occasions = models.ManyToManyField(Occasion, blank=True, related_name='products')
    product_type = models.CharField(max_length=200, blank=True, null=True)  # CSV field
    tags = models.CharField(max_length=500, blank=True, null=True)  # CSV field
    
    # ============================================
    # ADVANCED MENU RELATIONSHIPS
    # ============================================
    product_types = models.ManyToManyField(ProductType, blank=True, related_name='products')
    collections = models.ManyToManyField(Collection, blank=True, related_name='products')
    recipients = models.ManyToManyField(Recipient, blank=True, related_name='products')
    delivery_locations = models.ManyToManyField(DeliveryLocation, blank=True, related_name='products')
    
    # Menu-specific flags
    is_signature = models.BooleanField(default=False, help_text="Part of signature collection")
    is_premium = models.BooleanField(default=False, help_text="Premium product")
    is_hot_selling = models.BooleanField(default=False, help_text="Hot selling product")
    is_must_try = models.BooleanField(default=False, help_text="Must try product")
    is_new_arrival = models.BooleanField(default=False, help_text="New arrival product")

    # Phase 4: Personalization & Delivery
    is_personalized = models.BooleanField(default=False, help_text="Product can be personalized")
    delivery_days = models.PositiveIntegerField(default=1, help_text="Number of days for delivery")
    
    # ============================================
    # PRICING
    # ============================================
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # CSV field
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # CSV field
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Shopify
    cost_per_item = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # CSV field
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # CSV field
    
    # ============================================
    # TAX
    # ============================================
    sale_price_tax_included = models.BooleanField(default=True)  # CSV field
    purchase_price_tax_included = models.BooleanField(default=True)  # CSV field
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # CSV field
    taxable = models.BooleanField(default=True)  # CSV field
    hsn = models.CharField(max_length=50, blank=True, null=True)  # CSV field
    
    # ============================================
    # INVENTORY
    # ============================================
    stock_quantity = models.PositiveIntegerField(default=0)
    quantity = models.IntegerField(default=0)  # CSV field (synced with stock_quantity)
    min_quantity = models.IntegerField(default=0)  # CSV field
    max_quantity = models.IntegerField(default=0)  # CSV field
    inventory_policy = models.CharField(max_length=50, default='deny')  # CSV field
    
    # ============================================
    # PHYSICAL ATTRIBUTES
    # ============================================
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # CSV field
    weight_unit = models.CharField(max_length=10, default='kg')  # CSV field
    size = models.CharField(max_length=100, blank=True, null=True)  # CSV field
    color = models.CharField(max_length=100, blank=True, null=True)  # CSV field
    material = models.CharField(max_length=200, blank=True, null=True)  # CSV field
    
    # ============================================
    # BRAND & VENDOR
    # ============================================
    brand = models.CharField(max_length=200, blank=True, null=True)  # CSV field
    vendor = models.CharField(max_length=200, blank=True, null=True)  # CSV field
    
    # ============================================
    # SHIPPING & PRODUCT DETAILS
    # ============================================
    requires_shipping = models.BooleanField(default=True)  # CSV field
    barcode = models.CharField(max_length=100, blank=True, null=True)  # CSV field
    gtin = models.CharField(max_length=100, blank=True, null=True)  # CSV field
    mpn = models.CharField(max_length=100, blank=True, null=True)  # CSV field
    
    # ============================================
    # SEO
    # ============================================
    meta_title = models.CharField(max_length=160, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    seo_title = models.CharField(max_length=255, blank=True, null=True)  # CSV field
    seo_description = models.TextField(blank=True, null=True)  # CSV field
    
    # ============================================
    # STATUS & VISIBILITY
    # ============================================
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    show_online = models.BooleanField(default=True)  # CSV field
    published = models.BooleanField(default=True)  # CSV field
    status = models.CharField(max_length=20, default='active')  # CSV field (active/draft/archived)

    # ============================================
    # CUSTOMIZATION OPTIONS
    # ============================================
    allow_customization = models.BooleanField(default=False, help_text="Allow customers to customize this product")
    allow_name_customization = models.BooleanField(default=False, help_text="Allow name on product (e.g., cake)")
    allow_message_customization = models.BooleanField(default=False, help_text="Allow custom message")
    allow_flavor_selection = models.BooleanField(default=False, help_text="Allow flavor selection")
    customization_note = models.TextField(blank=True, help_text="Instructions for customization")
    
    # ============================================
    # REGIONAL PRICING (Shopify)
    # ============================================
    included_india = models.BooleanField(default=True)
    price_india = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    included_international = models.BooleanField(default=False)
    price_international = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # ============================================
    # MEDIA
    # ============================================
    video_url = models.URLField(max_length=500, blank=True, null=True)  # CSV field

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['slug']),
            models.Index(fields=['handle']),
            models.Index(fields=['status', 'published']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Always ensure slug is unique, even if set by importer
        if not self.slug:
            base_slug = slugify(self.name) if self.name else 'product'
        else:
            base_slug = self.slug
        unique_slug = base_slug
        counter = 1
        # Exclude self from uniqueness check if updating
        qs = Product.objects.all()
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        while qs.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = unique_slug

        # Set handle from slug if not already set
        if not self.handle:
            self.handle = self.slug
        
        # Sync stock_quantity with quantity (for CSV import compatibility)
        if self.quantity != self.stock_quantity:
            self.stock_quantity = max(self.quantity, self.stock_quantity)
        
        # Sync sale_price with base_price if not set
        if not self.sale_price and self.base_price:
            self.sale_price = self.base_price
        elif not self.base_price and self.sale_price:
            self.base_price = self.sale_price
        elif not self.base_price and not self.sale_price:
            self.base_price = 0
            self.sale_price = 0
        
        # Sync SEO fields
        if not self.meta_title and self.seo_title:
            self.meta_title = self.seo_title[:160]
        elif not self.seo_title and self.meta_title:
            self.seo_title = self.meta_title
        
        if not self.meta_description and self.seo_description:
            self.meta_description = self.seo_description[:320]
        elif not self.seo_description and self.meta_description:
            self.seo_description = self.meta_description
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    @property
    def current_price(self):
        """Return the current selling price"""
        if self.discount_price:
            return self.discount_price
        elif self.sale_price and self.sale_price > 0:
            return self.sale_price
        return self.base_price

    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        # Try MRP first (from CSV)
        if self.mrp and self.mrp > 0:
            current = self.current_price
            if current < self.mrp:
                return int(((self.mrp - current) / self.mrp) * 100)
        
        # Fall back to base_price comparison
        if self.discount_price and self.discount_price < self.base_price:
            return int(((self.base_price - self.discount_price) / self.base_price) * 100)
        
        return 0

    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0 or self.quantity > 0

    @property
    def primary_image(self):
        """Get the primary image for the product"""
        primary = self.images.filter(is_primary=True, is_active=True).first()
        if not primary:
            primary = self.images.filter(is_active=True).first()
        return primary

    @property
    def all_images(self):
        """Get all images for the product"""
        return self.images.filter(is_active=True).order_by('sort_order', 'position')

    def get_available_addons(self):
        """Get available add-ons for this product"""
        return ProductAddOn.objects.filter(is_active=True)[:6]


class ProductImage(BaseModel):
    """Multiple images for products - supports both local files and external URLs"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # Local file
    image_url = models.URLField(max_length=1000, blank=True, null=True)  # External URL (CSV)
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    position = models.IntegerField(default=0)  # CSV field

    class Meta:
        ordering = ['sort_order', 'position']
        indexes = [
            models.Index(fields=['product', 'sort_order']),
            models.Index(fields=['product', 'position']),
        ]

    def __str__(self):
        return f"{self.product.name} - Image {self.sort_order or self.position}"

    def save(self, *args, **kwargs):
        # If this is set as primary, unset all other primary images for this product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        
        # Sync sort_order with position if not set
        if not self.sort_order and self.position:
            self.sort_order = self.position
        elif not self.position and self.sort_order:
            self.position = self.sort_order
        
        super().save(*args, **kwargs)

    @property
    def get_image_url(self):
        """Get image URL - prioritize local file, fallback to external URL"""
        if self.image:
            return self.image.url
        return self.image_url or ''


class ProductVariant(BaseModel):
    """Product variants (size, color, etc.) - supports both manual and CSV import"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    
    # Original fields
    name = models.CharField(max_length=100)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Original field
    stock_quantity = models.PositiveIntegerField(default=0)
    sku_suffix = models.CharField(max_length=20, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    # CSV/Shopify fields
    variant_sku = models.CharField(max_length=100, blank=True, null=True)
    option1_name = models.CharField(max_length=100, blank=True, null=True)
    option1_value = models.CharField(max_length=100, blank=True, null=True)
    option2_name = models.CharField(max_length=100, blank=True, null=True)
    option2_value = models.CharField(max_length=100, blank=True, null=True)
    option3_name = models.CharField(max_length=100, blank=True, null=True)
    option3_value = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_item = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    inventory_quantity = models.IntegerField(default=0)
    inventory_policy = models.CharField(max_length=50, default='deny')
    image_url = models.URLField(max_length=1000, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    requires_shipping = models.BooleanField(default=True)
    taxable = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.product.name} - {self.display_name}"

    def save(self, *args, **kwargs):
        # Sync inventory_quantity with stock_quantity
        if self.inventory_quantity != self.stock_quantity:
            self.stock_quantity = self.inventory_quantity
        
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        """Calculate final price"""
        if self.price and self.price > 0:
            return self.price + self.additional_price
        base_price = self.product.current_price
        return base_price + self.price_adjustment + self.additional_price

    @property
    def full_sku(self):
        """Generate full SKU"""
        if self.variant_sku:
            return self.variant_sku
        return f"{self.product.sku}-{self.sku_suffix}" if self.sku_suffix else self.product.sku

    @property
    def display_name(self):
        """Generate display name from options"""
        # Try Shopify option format first
        options = []
        if self.option1_value:
            options.append(self.option1_value)
        if self.option2_value:
            options.append(self.option2_value)
        if self.option3_value:
            options.append(self.option3_value)
        
        if options:
            return " / ".join(options)
        
        # Fall back to name field
        return self.name or "Default"


class CSVImportLog(models.Model):
    """Track CSV import history and errors"""
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)  # 'shopify' or 'gift_tree'
    total_rows = models.IntegerField(default=0)
    products_created = models.IntegerField(default=0)
    products_updated = models.IntegerField(default=0)
    errors = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='processing')  # processing/completed/failed
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'CSV Import Log'
        verbose_name_plural = 'CSV Import Logs'
    
    def __str__(self):
        return f"Import: {self.filename} - {self.status}"


class SellerInventory(BaseModel):
    """Product inventory at seller locations"""
    seller_location = models.ForeignKey('users.SellerLocation', on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='seller_inventory')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='seller_inventory')

    # Stock
    stock_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0, help_text="Quantity in pending orders")
    reorder_level = models.PositiveIntegerField(default=5, help_text="Minimum stock before reorder")

    # Pricing (seller can have different pricing)
    seller_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Leave empty to use product base price")

    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['seller_location', 'product']
        unique_together = ['seller_location', 'product', 'variant']
        verbose_name = 'Seller Inventory'
        verbose_name_plural = 'Seller Inventories'

    def __str__(self):
        variant_str = f" ({self.variant.display_name})" if self.variant else ""
        return f"{self.seller_location.name} - {self.product.name}{variant_str} ({self.available_quantity} available)"

    @property
    def available_quantity(self):
        """Calculate available quantity after reserved"""
        return max(0, self.stock_quantity - self.reserved_quantity)

    @property
    def is_in_stock(self):
        """Check if product is in stock at this location"""
        return self.available_quantity > 0

    @property
    def needs_reorder(self):
        """Check if stock is below reorder level"""
        return self.stock_quantity <= self.reorder_level

    def get_price(self):
        """Get seller price or fall back to product price"""
        if self.seller_price:
            return self.seller_price
        if self.variant:
            return self.variant.final_price
        return self.product.current_price


class ProductAddOn(BaseModel):
    """Add-on products that can be purchased with main products"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='addons/', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Product Add-On'
        verbose_name_plural = 'Product Add-Ons'

    def __str__(self):
        return f"{self.name} - ₹{self.price}"