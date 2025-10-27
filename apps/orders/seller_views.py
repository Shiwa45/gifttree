"""
Seller-specific views for order management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta

from .models import Order, OrderTracking
from apps.users.models import Seller


def is_seller(user):
    """Check if user is a seller"""
    return hasattr(user, 'seller_profile') and user.seller_profile.is_active


@login_required
@user_passes_test(is_seller, login_url='/admin/')
def seller_dashboard(request):
    """Seller dashboard showing assigned orders and statistics"""
    seller = request.user.seller_profile
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    # Base queryset - only orders assigned to this seller
    orders = Order.objects.filter(assigned_seller=seller).select_related(
        'user', 'assigned_location'
    ).prefetch_related('items__product')
    
    # Apply filters
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(shipping_name__icontains=search_query) |
            Q(shipping_phone__icontains=search_query)
        )
    
    # Order by newest first
    orders = orders.order_by('-created_at')
    
    # Calculate statistics
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    stats = {
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='pending').count(),
        'processing_orders': orders.filter(status__in=['confirmed', 'processing', 'ready_to_ship']).count(),
        'shipped_orders': orders.filter(status__in=['shipped', 'out_for_delivery']).count(),
        'delivered_orders': orders.filter(status='delivered').count(),
        'today_orders': orders.filter(created_at__date=today).count(),
        'month_orders': orders.filter(created_at__date__gte=last_30_days).count(),
        'total_revenue': orders.filter(
            payment_status='paid',
            status='delivered'
        ).aggregate(total=Sum('total_amount'))['total'] or 0,
    }
    
    context = {
        'seller': seller,
        'orders': orders[:50],  # Limit to 50 for performance
        'stats': stats,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'orders/seller_dashboard.html', context)


@login_required
@user_passes_test(is_seller, login_url='/admin/')
def seller_order_detail(request, order_number):
    """Detailed view of a specific order for seller"""
    seller = request.user.seller_profile
    
    order = get_object_or_404(
        Order.objects.select_related('user', 'assigned_seller', 'assigned_location').prefetch_related(
            'items__product',
            'items__variant',
            'tracking'
        ),
        order_number=order_number,
        assigned_seller=seller
    )
    
    context = {
        'seller': seller,
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'orders/seller_order_detail.html', context)


@login_required
@user_passes_test(is_seller, login_url='/admin/')
@require_POST
def seller_update_order_status(request, order_number):
    """Update order status by seller"""
    seller = request.user.seller_profile
    
    order = get_object_or_404(
        Order,
        order_number=order_number,
        assigned_seller=seller
    )
    
    new_status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    
    # Validate status
    valid_statuses = dict(Order.STATUS_CHOICES).keys()
    if new_status not in valid_statuses:
        messages.error(request, 'Invalid status')
        return redirect('orders:seller_order_detail', order_number=order_number)
    
    # Update order status
    old_status = order.status
    order.status = new_status
    order.save()
    
    # Create tracking entry
    OrderTracking.objects.create(
        order=order,
        status=new_status,
        message=notes or f'Order status changed from {order.get_status_display()} to {dict(Order.STATUS_CHOICES)[new_status]}',
        updated_by=request.user
    )
    
    messages.success(request, f'Order status updated to {dict(Order.STATUS_CHOICES)[new_status]}')
    
    # Check if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Order status updated to {dict(Order.STATUS_CHOICES)[new_status]}',
            'new_status': new_status,
            'new_status_display': dict(Order.STATUS_CHOICES)[new_status]
        })
    
    return redirect('orders:seller_order_detail', order_number=order_number)


@login_required
@user_passes_test(is_seller, login_url='/admin/')
@require_POST
def seller_add_tracking(request, order_number):
    """Add tracking information to an order"""
    seller = request.user.seller_profile
    
    order = get_object_or_404(
        Order,
        order_number=order_number,
        assigned_seller=seller
    )
    
    message = request.POST.get('message')
    tracking_number = request.POST.get('tracking_number', '')
    courier_name = request.POST.get('courier_name', '')
    
    if not message:
        messages.error(request, 'Tracking message is required')
        return redirect('orders:seller_order_detail', order_number=order_number)
    
    # Create tracking entry
    tracking = OrderTracking.objects.create(
        order=order,
        status=order.status,
        message=message,
        tracking_number=tracking_number if tracking_number else None,
        courier_name=courier_name if courier_name else None,
        updated_by=request.user
    )
    
    messages.success(request, 'Tracking information added successfully')
    
    # Check if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Tracking information added successfully',
            'tracking': {
                'id': tracking.id,
                'message': tracking.message,
                'tracking_number': tracking.tracking_number,
                'courier_name': tracking.courier_name,
                'created_at': tracking.created_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
    
    return redirect('orders:seller_order_detail', order_number=order_number)

