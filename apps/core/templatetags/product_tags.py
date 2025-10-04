from django import template
from django.templatetags.static import static
import os

register = template.Library()


@register.filter
def product_image_url(product, default_image='images/products/default.jpg'):
    """
    Get the product image URL with fallback handling
    Supports both uploaded images (image field) and external URLs (image_url field)
    """
    if product and hasattr(product, 'primary_image') and product.primary_image:
        try:
            # First check for image_url (CSV imported products)
            if hasattr(product.primary_image, 'image_url') and product.primary_image.image_url:
                return product.primary_image.image_url
            # Then check for uploaded image file
            elif hasattr(product.primary_image, 'image') and product.primary_image.image:
                return product.primary_image.image.url
        except (ValueError, AttributeError):
            pass

    # Fallback to first image if primary doesn't exist
    if product and hasattr(product, 'all_images'):
        first_image = product.all_images.first()
        if first_image:
            try:
                # Check image_url first (CSV imports)
                if hasattr(first_image, 'image_url') and first_image.image_url:
                    return first_image.image_url
                # Then check uploaded image
                elif hasattr(first_image, 'image') and first_image.image:
                    return first_image.image.url
            except (ValueError, AttributeError):
                pass

    # Final fallback to static default image
    return static(default_image)


@register.filter
def product_price_display(product):
    """
    Get the product price with proper formatting
    """
    if not product:
        return "₹0"
    
    try:
        current_price = getattr(product, 'current_price', None)
        if current_price is not None:
            return f"₹{current_price:,.0f}"
        
        base_price = getattr(product, 'base_price', None)
        if base_price is not None:
            return f"₹{base_price:,.0f}"
            
    except (AttributeError, TypeError, ValueError):
        pass
    
    return "₹0"


@register.filter
def has_discount(product):
    """
    Check if product has a discount
    """
    if not product:
        return False
    
    try:
        discount_price = getattr(product, 'discount_price', None)
        base_price = getattr(product, 'base_price', None)
        
        return (discount_price is not None and 
                base_price is not None and 
                discount_price < base_price)
    except (AttributeError, TypeError):
        return False


@register.simple_tag
def product_url(product):
    """
    Get the product URL safely
    """
    if product and hasattr(product, 'get_absolute_url'):
        try:
            return product.get_absolute_url()
        except (AttributeError, ValueError):
            pass
    
    # Fallback URL pattern
    if product and hasattr(product, 'id'):
        return f"/products/{product.id}/"
    
    return "#"