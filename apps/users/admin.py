from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, Address, Wishlist, Seller, SellerLocation, Pincode


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class WishlistInline(admin.TabularInline):
    model = Wishlist
    extra = 0
    readonly_fields = ['created_at']


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_active', 'is_verified', 'date_joined']
    list_filter = ['is_active', 'is_verified', 'date_joined', 'is_staff']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone', 'date_of_birth', 'is_verified')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'phone', 'date_of_birth')
        }),
    )

    inlines = [UserProfileInline, AddressInline, WishlistInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_language', 'created_at']
    search_fields = ['user__email', 'user__username']
    list_filter = ['preferred_language', 'created_at']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'full_name', 'city', 'state', 'is_default']
    list_filter = ['city', 'state', 'is_default', 'created_at']
    search_fields = ['user__email', 'full_name', 'city', 'state']


# ✅ NEW: Wishlist Admin
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at', 'is_active']
    list_filter = ['created_at', 'is_active']
    search_fields = ['user__email', 'product__name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'product']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'product')


# Multi-tenant Seller Management
class SellerLocationInline(admin.TabularInline):
    model = SellerLocation
    extra = 0
    fields = ['name', 'city', 'state', 'pincode', 'is_primary', 'is_active']


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'business_email', 'business_phone', 'is_verified', 'is_active', 'created_at']
    list_filter = ['is_verified', 'is_active', 'created_at']
    search_fields = ['business_name', 'user__email', 'business_email', 'gst_number']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SellerLocationInline]

    fieldsets = (
        ('Business Information', {
            'fields': ('user', 'business_name', 'business_email', 'business_phone')
        }),
        ('Business Details', {
            'fields': ('gst_number', 'pan_number')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'account_number', 'ifsc_code')
        }),
        ('Commission & Status', {
            'fields': ('commission_percentage', 'is_verified', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SellerLocation)
class SellerLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller', 'city', 'state', 'pincode', 'is_primary', 'is_active']
    list_filter = ['is_primary', 'is_active', 'state', 'city']
    search_fields = ['name', 'seller__business_name', 'city', 'state', 'pincode']
    filter_horizontal = ['serviceable_pincodes']

    fieldsets = (
        ('Basic Information', {
            'fields': ('seller', 'name', 'is_primary', 'is_active')
        }),
        ('Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'pincode')
        }),
        ('Contact', {
            'fields': ('contact_person', 'contact_phone', 'contact_email')
        }),
        ('Service Area', {
            'fields': ('serviceable_pincodes',)
        }),
    )


@admin.register(Pincode)
class PincodeAdmin(admin.ModelAdmin):
    list_display = ['pincode', 'area', 'city', 'district', 'state', 'delivery_days', 'is_serviceable', 'is_active']
    list_filter = ['state', 'is_serviceable', 'is_active', 'delivery_days']
    search_fields = ['pincode', 'area', 'city', 'district', 'state']
    list_editable = ['is_serviceable', 'delivery_days']

    fieldsets = (
        ('Location Details', {
            'fields': ('pincode', 'area', 'district', 'city', 'state')
        }),
        ('Delivery Settings', {
            'fields': ('is_serviceable', 'delivery_days')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )