from django.contrib import admin
from django.utils.html import format_html
from .models import Wallet, WalletTransaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'balance_display', 'transaction_count', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    list_filter = ['created_at', 'is_active']
    readonly_fields = ['created_at', 'updated_at']

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'

    def balance_display(self, obj):
        color = 'green' if obj.balance > 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">₹{}</span>',
            color, obj.balance
        )
    balance_display.short_description = 'Balance'

    def transaction_count(self, obj):
        return obj.transactions.count()
    transaction_count.short_description = 'Transactions'


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet_user', 'transaction_type_badge', 'amount_display', 'balance_after', 'description_short', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['wallet__user__email', 'description']
    readonly_fields = ['created_at', 'updated_at', 'balance_after']
    date_hierarchy = 'created_at'

    def wallet_user(self, obj):
        return obj.wallet.user.email
    wallet_user.short_description = 'User'

    def transaction_type_badge(self, obj):
        if obj.transaction_type == 'credit':
            return format_html(
                '<span style="background: #4CAF50; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px;">✓ CREDIT</span>'
            )
        else:
            return format_html(
                '<span style="background: #F44336; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px;">✗ DEBIT</span>'
            )
    transaction_type_badge.short_description = 'Type'

    def amount_display(self, obj):
        color = '#4CAF50' if obj.transaction_type == 'credit' else '#F44336'
        symbol = '+' if obj.transaction_type == 'credit' else '-'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ₹{}</span>',
            color, symbol, obj.amount
        )
    amount_display.short_description = 'Amount'

    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'
