from django.contrib import admin
from .models import Category, Occasion, Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'sort_order']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ['name', 'price_adjustment', 'stock_quantity', 'sku_suffix', 'sort_order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_featured', 'product_count', 'sort_order', 'is_active']
    list_filter = ['is_featured', 'is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['sort_order', 'is_featured']


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_featured', 'is_active']
    list_filter = ['is_featured', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_price', 'discount_price', 'stock_quantity', 'is_featured', 'is_bestseller', 'is_active']
    list_filter = ['category', 'occasions', 'is_featured', 'is_bestseller', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'description']
    filter_horizontal = ['occasions']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['base_price', 'discount_price', 'stock_quantity', 'is_featured', 'is_bestseller']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'occasions', 'sku')
        }),
        ('Content', {
            'fields': ('description', 'care_instructions')
        }),
        ('Pricing & Stock', {
            'fields': ('base_price', 'discount_price', 'stock_quantity')
        }),
        ('Marketing', {
            'fields': ('is_featured', 'is_bestseller')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ['collapse']
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    inlines = [ProductImageInline, ProductVariantInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_primary', 'sort_order', 'is_active']
    list_filter = ['is_primary', 'is_active']
    search_fields = ['product__name', 'alt_text']
    list_editable = ['is_primary', 'sort_order']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'price_adjustment', 'stock_quantity', 'sort_order']
    list_filter = ['product__category']
    search_fields = ['product__name', 'name']
    list_editable = ['price_adjustment', 'stock_quantity', 'sort_order']