from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order


@login_required
def order_list(request):
    """Display user's orders"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_number):
    """Display order details"""
    order = Order.objects.get(order_number=order_number, user=request.user)
    context = {
        'order': order,
        'order_items': order.items.all(),
        'tracking': order.tracking.all(),
    }
    return render(request, 'orders/order_detail.html', context)