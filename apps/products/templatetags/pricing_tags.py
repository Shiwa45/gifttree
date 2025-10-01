from django import template
from django.utils.safestring import mark_safe
from decimal import Decimal

register = template.Library()


@register.inclusion_tag('products/includes/price_display.html')
def display_price(product, show_discount=True, show_savings=True, css_class=""):
    """Display product price with discount information"""
    current_price = product.current_price if hasattr(product, 'current_price') else product.base_price
    base_price = product.base_price
    discount_price = getattr(product, 'discount_price', None)
    
    # Calculate if there's a discount
    has_discount = bool(discount_price and discount_price < base_price)
    
    # Calculate discount percentage
    discount_percentage = 0
    savings_amount = Decimal('0')
    if has_discount:
        discount_percentage = int(((base_price - discount_price) / base_price) * 100)
        savings_amount = base_price - discount_price
    
    return {
        'product': product,
        'show_discount': show_discount,
        'show_savings': show_savings,
        'css_class': css_class,
        'current_price': current_price,
        'base_price': base_price,
        'discount_price': discount_price,
        'discount_percentage': discount_percentage,
        'savings_amount': savings_amount,
        'has_discount': has_discount
    }


@register.simple_tag
def get_product_price(product):
    """Get the current price of a product safely"""
    if hasattr(product, 'current_price'):
        return product.current_price
    elif hasattr(product, 'base_price'):
        return product.base_price
    return 0


@register.simple_tag
def get_variant_price(variant):
    """Get the final price of a product variant"""
    if hasattr(variant, 'final_price'):
        return variant.final_price
    elif hasattr(variant, 'product') and hasattr(variant, 'price_adjustment'):
        base_price = get_product_price(variant.product)
        return base_price + variant.price_adjustment
    return 0


@register.filter
def currency_format(value):
    """Format price with currency symbol"""
    try:
        if value is None:
            return "Price not available"
        return f"₹{value:,.0f}"
    except (ValueError, TypeError):
        return "Price not available"


@register.filter
def has_discount(product):
    """Check if product has a discount"""
    if not hasattr(product, 'discount_price') or not hasattr(product, 'base_price'):
        return False
    return bool(product.discount_price and product.discount_price < product.base_price)