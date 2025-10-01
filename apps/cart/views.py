from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem


@login_required
def cart_view(request):
    """Display cart contents"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product', 'variant').all()
    }
    return render(request, 'cart/cart.html', context)