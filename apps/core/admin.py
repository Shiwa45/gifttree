from django.contrib import admin
from .models import SiteSettings, Country, BannerImage, WorldwideDeliveryProduct


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'contact_email', 'contact_phone', 'delivery_charge', 'free_delivery_above']
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'site_logo', 'copyright_text')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Social Media Links', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url')
        }),
        ('Delivery Settings', {
            'fields': ('delivery_charge', 'free_delivery_above')
        }),
    )

    def has_add_permission(self, request):
        # Prevent adding more than one instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the settings
        return False


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_featured', 'sort_order', 'is_active']
    list_filter = ['is_featured', 'is_active']
    search_fields = ['name', 'code']
    list_editable = ['is_featured', 'sort_order', 'is_active']


@admin.register(BannerImage)
class BannerImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'sort_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'button_text']
    list_editable = ['sort_order', 'is_active']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Banner Content', {
            'fields': ('title', 'image', 'mobile_image', 'button_text')
        }),
        ('Navigation', {
            'fields': ('link_url',)
        }),
        ('Display Settings', {
            'fields': ('sort_order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorldwideDeliveryProduct)
class WorldwideDeliveryProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'estimated_delivery_days', 'international_shipping_charge', 'is_featured', 'sort_order', 'is_active']
    list_filter = ['is_featured', 'is_active', 'created_at']
    search_fields = ['product__name', 'delivery_note']
    list_editable = ['is_featured', 'sort_order', 'is_active']
    filter_horizontal = ['countries']
    autocomplete_fields = ['product']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Product Information', {
            'fields': ('product', 'delivery_note')
        }),
        ('Delivery Details', {
            'fields': ('countries', 'estimated_delivery_days', 'international_shipping_charge')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'sort_order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )