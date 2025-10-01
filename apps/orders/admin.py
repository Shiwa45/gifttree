from django.contrib import admin
from .models import Order, OrderItem, OrderTracking


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__email', 'billing_name', 'shipping_name']
    readonly_fields = ['order_number', 'subtotal', 'total_amount']

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Billing Information', {
            'fields': ('billing_name', 'billing_email', 'billing_phone', 'billing_address_line_1', 'billing_address_line_2', 'billing_city', 'billing_state', 'billing_pincode')
        }),
        ('Shipping Information', {
            'fields': ('shipping_name', 'shipping_phone', 'shipping_address_line_1', 'shipping_address_line_2', 'shipping_city', 'shipping_state', 'shipping_pincode')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_charge', 'total_amount')
        }),
        ('Delivery Details', {
            'fields': ('special_instructions', 'delivery_date', 'delivery_time_slot')
        }),
    )

    inlines = [OrderItemInline, OrderTrackingInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'variant_name', 'quantity', 'unit_price', 'total_price']
    list_filter = ['order__status']
    search_fields = ['product_name', 'order__order_number']


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'message', 'location', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'message']