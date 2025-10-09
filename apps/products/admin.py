# apps/products/admin.py - COMPLETE FINAL VERSION

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from .models import (
    Category, Occasion, Product, ProductImage, ProductVariant, CSVImportLog,
    MenuBadge, MenuCategory, MenuSection, ProductType, Collection,
    Recipient, DeliveryLocation, MenuConfiguration, SellerInventory, ProductAddOn
)


# ============================================
# INLINE ADMINS
# ============================================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'image_url', 'alt_text', 'is_primary', 'sort_order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.image.url)
        elif obj.image_url:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.image_url)
        return "No image"
    image_preview.short_description = 'Preview'


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ['name', 'price_adjustment', 'stock_quantity', 'sku_suffix', 'sort_order']


class SellerInventoryInline(admin.TabularInline):
    model = SellerInventory
    extra = 0
    fields = ['seller_location', 'variant', 'stock_quantity', 'reserved_quantity', 'seller_price', 'is_active']
    raw_id_fields = ['seller_location', 'variant']


# ============================================
# MENU MODEL ADMINS
# ============================================

@admin.register(MenuBadge)
class MenuBadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'badge_preview', 'sort_order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['sort_order', 'is_active']
    
    def badge_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            obj.background_color, obj.color, obj.name
        )
    badge_preview.short_description = 'Preview'


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'show_in_mega_menu', 'show_in_mobile_menu', 'sort_order', 'is_active']
    list_filter = ['show_in_mega_menu', 'show_in_mobile_menu', 'is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['show_in_mega_menu', 'show_in_mobile_menu', 'sort_order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'parent', 'icon', 'image', 'description')
        }),
        ('Menu Settings', {
            'fields': ('show_in_mega_menu', 'show_in_mobile_menu', 'menu_columns', 'featured_products_count')
        }),
        ('Status', {
            'fields': ('is_active', 'sort_order')
        }),
    )


@admin.register(MenuSection)
class MenuSectionAdmin(admin.ModelAdmin):
    list_display = ['category', 'name', 'section_type', 'sort_order', 'is_active']
    list_filter = ['section_type', 'is_active', 'category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['sort_order', 'is_active']


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'badges_display', 'sort_order', 'is_active']
    list_filter = ['category', 'is_active', 'badges']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['badges']
    list_editable = ['sort_order', 'is_active']
    
    def badges_display(self, obj):
        badges = obj.badges.all()
        if badges:
            badge_html = []
            for badge in badges:
                badge_html.append(
                    f'<span style="background-color: {badge.background_color}; color: {badge.color}; '
                    f'padding: 1px 6px; border-radius: 3px; font-size: 10px; margin-right: 2px;">{badge.name}</span>'
                )
            return format_html(''.join(badge_html))
        return '-'
    badges_display.short_description = 'Badges'


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'categories_display', 'badges_display', 'is_featured', 'sort_order', 'is_active']
    list_filter = ['is_featured', 'is_active', 'categories', 'badges']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['categories', 'badges']
    list_editable = ['is_featured', 'sort_order', 'is_active']
    
    def categories_display(self, obj):
        categories = obj.categories.all()[:3]
        if categories:
            return ', '.join([cat.name for cat in categories])
        return '-'
    categories_display.short_description = 'Categories'
    
    def badges_display(self, obj):
        badges = obj.badges.all()
        if badges:
            badge_html = []
            for badge in badges:
                badge_html.append(
                    f'<span style="background-color: {badge.background_color}; color: {badge.color}; '
                    f'padding: 1px 6px; border-radius: 3px; font-size: 10px; margin-right: 2px;">{badge.name}</span>'
                )
            return format_html(''.join(badge_html))
        return '-'
    badges_display.short_description = 'Badges'


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'sort_order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['sort_order', 'is_active']


@admin.register(DeliveryLocation)
class DeliveryLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'country', 'is_major_city', 'is_metro', 'sort_order', 'is_active']
    list_filter = ['is_major_city', 'is_metro', 'is_active', 'state', 'country']
    search_fields = ['name', 'state', 'country']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_major_city', 'is_metro', 'sort_order', 'is_active']


@admin.register(MenuConfiguration)
class MenuConfigurationAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_preview', 'is_active']
    list_filter = ['is_active']
    search_fields = ['key', 'description']
    list_editable = ['is_active']
    
    def value_preview(self, obj):
        value_str = str(obj.value)
        if len(value_str) > 50:
            return value_str[:50] + '...'
        return value_str
    value_preview.short_description = 'Value'


# ============================================
# MODEL ADMINS
# ============================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_featured', 'sort_order', 'product_count', 'is_active']
    list_filter = ['is_featured', 'is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured', 'sort_order']
    
    def product_count(self, obj):
        return obj.product_count
    product_count.short_description = 'Products'


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_featured', 'sort_order', 'is_active']
    list_filter = ['is_featured', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured', 'sort_order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'base_price', 'discount_price', 
        'stock_quantity', 'is_featured', 'is_bestseller', 'is_active', 'primary_image_preview'
    ]
    list_filter = [
        'category', 'occasions', 'is_featured', 'is_bestseller', 
        'is_active', 'published', 'status', 'created_at'
    ]
    search_fields = ['name', 'sku', 'description', 'vendor', 'brand']
    filter_horizontal = ['occasions', 'product_types', 'collections', 'recipients', 'delivery_locations']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['base_price', 'discount_price', 'stock_quantity', 'is_featured', 'is_bestseller']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'handle', 'sku', 'category', 'occasions')
        }),
        ('Advanced Menu Categorization', {
            'fields': ('product_types', 'collections', 'recipients', 'delivery_locations'),
            'classes': ('collapse',)
        }),
        ('Content', {
            'fields': ('description', 'body_html', 'summary', 'care_instructions')
        }),
        ('Pricing', {
            'fields': (
                'base_price', 'sale_price', 'discount_price', 'mrp', 
                'compare_at_price', 'cost_per_item', 'purchase_price'
            )
        }),
        ('Tax', {
            'fields': ('taxable', 'tax_rate', 'hsn', 'sale_price_tax_included', 'purchase_price_tax_included')
        }),
        ('Inventory & Stock', {
            'fields': (
                'stock_quantity', 'quantity', 'min_quantity', 'max_quantity', 'inventory_policy'
            )
        }),
        ('Physical Attributes', {
            'fields': ('weight', 'weight_unit', 'size', 'color', 'material', 'requires_shipping')
        }),
        ('Brand & Vendor', {
            'fields': ('brand', 'vendor', 'product_type', 'tags')
        }),
        ('Product Identifiers', {
            'fields': ('barcode', 'gtin', 'mpn', 'common_product_id'),
            'classes': ('collapse',)
        }),
        ('Marketing & Features', {
            'fields': ('is_featured', 'is_bestseller', 'is_signature', 'is_premium', 'is_hot_selling', 'is_must_try', 'is_new_arrival')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'seo_title', 'seo_description', 'video_url'),
            'classes': ('collapse',)
        }),
        ('Regional Pricing', {
            'fields': ('included_india', 'price_india', 'included_international', 'price_international'),
            'classes': ('collapse',)
        }),
        ('Status & Visibility', {
            'fields': ('is_active', 'published', 'show_online', 'status')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [ProductImageInline, ProductVariantInline, SellerInventoryInline]

    actions = ['mark_as_published', 'mark_as_draft', 'mark_as_archived']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category').prefetch_related('images')
    
    def primary_image_preview(self, obj):
        primary_image = obj.primary_image
        if primary_image:
            img_url = primary_image.get_image_url
            if img_url:
                return format_html('<img src="{}" style="max-width: 50px; max-height: 50px;" />', img_url)
        return "No image"
    primary_image_preview.short_description = 'Image'
    
    def mark_as_published(self, request, queryset):
        queryset.update(status='active', published=True, is_active=True)
        self.message_user(request, f"{queryset.count()} products marked as published")
    mark_as_published.short_description = "Mark selected as published"
    
    def mark_as_draft(self, request, queryset):
        queryset.update(status='draft', published=False)
        self.message_user(request, f"{queryset.count()} products marked as draft")
    mark_as_draft.short_description = "Mark selected as draft"
    
    def mark_as_archived(self, request, queryset):
        queryset.update(status='archived', published=False, is_active=False)
        self.message_user(request, f"{queryset.count()} products marked as archived")
    mark_as_archived.short_description = "Mark selected as archived"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_primary', 'sort_order', 'position', 'is_active', 'image_preview']
    list_filter = ['is_primary', 'is_active']
    search_fields = ['product__name', 'alt_text']
    list_editable = ['is_primary', 'sort_order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        img_url = obj.get_image_url
        if img_url:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px;" />', img_url)
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'name', 'display_name', 'price_adjustment', 
        'stock_quantity', 'sort_order', 'is_active'
    ]
    list_filter = ['product__category', 'is_active']
    search_fields = ['product__name', 'name', 'variant_sku']
    list_editable = ['price_adjustment', 'stock_quantity', 'sort_order']
    readonly_fields = ['display_name', 'final_price', 'full_sku']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product', 'name', 'variant_sku', 'sku_suffix')
        }),
        ('Shopify Options', {
            'fields': (
                'option1_name', 'option1_value',
                'option2_name', 'option2_value',
                'option3_name', 'option3_value'
            ),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('price', 'price_adjustment', 'additional_price', 'compare_at_price', 'cost_per_item', 'final_price')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'inventory_quantity', 'inventory_policy')
        }),
        ('Physical Attributes', {
            'fields': ('weight', 'barcode', 'image_url')
        }),
        ('Settings', {
            'fields': ('requires_shipping', 'taxable', 'is_active', 'sort_order')
        }),
    )


@admin.register(CSVImportLog)
class CSVImportLogAdmin(admin.ModelAdmin):
    list_display = [
        'filename', 'file_type', 'status', 'total_rows',
        'products_created', 'products_updated', 'uploaded_by', 'created_at'
    ]
    list_filter = ['status', 'file_type', 'created_at']
    search_fields = ['filename', 'uploaded_by__username']
    readonly_fields = [
        'uploaded_by', 'filename', 'file_type', 'total_rows',
        'products_created', 'products_updated', 'errors',
        'status', 'created_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Import Information', {
            'fields': ('filename', 'file_type', 'uploaded_by', 'status')
        }),
        ('Statistics', {
            'fields': ('total_rows', 'products_created', 'products_updated')
        }),
        ('Errors', {
            'fields': ('errors',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )
    
    def has_add_permission(self, request):
        return False


# ============================================
# CUSTOM ADMIN URLS
# ============================================

def get_admin_urls(urls):
    """Add custom URLs to admin"""
    from django.urls import path
    from apps.products import views
    
    custom_urls = [
        path('import-csv/', views.import_csv_view, name='import_csv'),
        path('reset-database/', views.reset_database_view, name='reset_database'),
    ]
    return custom_urls + urls

admin_urls = admin.site.get_urls
admin.site.get_urls = lambda: get_admin_urls(admin_urls())


# ============================================
# MULTI-TENANT INVENTORY ADMIN
# ============================================

@admin.register(SellerInventory)
class SellerInventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'variant', 'seller_location', 'stock_quantity', 'reserved_quantity', 'available_quantity_display', 'seller_price', 'is_active']
    list_filter = ['seller_location__seller', 'seller_location__state', 'seller_location__city', 'is_active']
    search_fields = ['product__name', 'product__sku', 'seller_location__name', 'seller_location__seller__business_name']
    list_editable = ['stock_quantity', 'seller_price', 'is_active']
    raw_id_fields = ['product', 'variant', 'seller_location']
    readonly_fields = ['available_quantity_display', 'needs_reorder_display', 'created_at', 'updated_at']

    fieldsets = (
        ('Product & Location', {
            'fields': ('product', 'variant', 'seller_location')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'reserved_quantity', 'available_quantity_display', 'reorder_level', 'needs_reorder_display')
        }),
        ('Pricing', {
            'fields': ('seller_price',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product', 'variant', 'seller_location', 'seller_location__seller'
        )

    def available_quantity_display(self, obj):
        avail = obj.available_quantity
        if avail > 0:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', avail)
        return format_html('<span style="color: red; font-weight: bold;">0</span>', avail)
    available_quantity_display.short_description = 'Available'

    def needs_reorder_display(self, obj):
        if obj.needs_reorder:
            return format_html('<span style="color: orange; font-weight: bold;">⚠ Yes</span>')
        return format_html('<span style="color: green;">✓ No</span>')
    needs_reorder_display.short_description = 'Needs Reorder'


@admin.register(ProductAddOn)
class ProductAddOnAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'image_preview', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_active']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 50px; max-height: 50px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image'