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
    list_display = ['order_number', 'user', 'assigned_seller_display', 'status', 'payment_status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_status', 'assigned_seller', 'created_at']
    search_fields = ['order_number', 'user__email', 'billing_name', 'shipping_name', 'assigned_seller__business_name']
    readonly_fields = ['order_number', 'subtotal', 'total_amount', 'created_at', 'updated_at']
    list_editable = []  # Can be ['assigned_seller'] for quick assignment
    
    # Actions
    actions = ['assign_to_seller', 'mark_as_confirmed', 'mark_as_processing']

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'created_at', 'updated_at')
        }),
        ('🏪 Seller Assignment', {
            'fields': ('assigned_seller', 'assigned_location'),
            'description': 'Assign this order to a seller/vendor for fulfillment'
        }),
        ('Billing Information', {
            'fields': ('billing_name', 'billing_email', 'billing_phone', 'billing_address_line_1', 'billing_address_line_2', 'billing_city', 'billing_state', 'billing_pincode'),
            'classes': ('collapse',)
        }),
        ('Shipping Information', {
            'fields': ('shipping_name', 'shipping_phone', 'shipping_address_line_1', 'shipping_address_line_2', 'shipping_city', 'shipping_state', 'shipping_pincode')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_charge', 'coupon', 'coupon_discount', 'wallet_coins_used', 'total_amount')
        }),
        ('Delivery Details', {
            'fields': ('special_instructions', 'delivery_date', 'delivery_time_slot'),
            'classes': ('collapse',)
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'razorpay_order_id', 'razorpay_payment_id'),
            'classes': ('collapse',)
        }),
    )

    inlines = [OrderItemInline, OrderTrackingInline]
    
    def assigned_seller_display(self, obj):
        """Display assigned seller with styling"""
        if obj.assigned_seller:
            return f"✅ {obj.assigned_seller.business_name}"
        return "⚠️ Unassigned"
    assigned_seller_display.short_description = 'Assigned Seller'
    
    def assign_to_seller(self, request, queryset):
        """Bulk action to assign multiple orders to a seller"""
        # This would open a form to select seller
        # For now, just show a message
        self.message_user(request, f"Selected {queryset.count()} orders. Please assign sellers individually from the order detail page.")
    assign_to_seller.short_description = "Assign selected orders to seller"
    
    def mark_as_confirmed(self, request, queryset):
        """Bulk action to mark orders as confirmed"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"Successfully marked {updated} order(s) as confirmed.")
    mark_as_confirmed.short_description = "Mark as Confirmed"
    
    def mark_as_processing(self, request, queryset):
        """Bulk action to mark orders as processing"""
        updated = queryset.update(status='processing')
        self.message_user(request, f"Successfully marked {updated} order(s) as processing.")
    mark_as_processing.short_description = "Mark as Processing"


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