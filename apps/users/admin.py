from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, Address, Wishlist


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