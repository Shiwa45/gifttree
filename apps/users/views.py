# Add this to apps/users/views.py

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import CustomUser, Address, Wishlist,UserProfile
from apps.products.models import Product



def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get form data
                email = request.POST.get('email')
                username = request.POST.get('username') or email.split('@')[0]
                first_name = request.POST.get('first_name', '')
                last_name = request.POST.get('last_name', '')
                phone = request.POST.get('phone', '')
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                
                # Validate passwords match
                if password1 != password2:
                    messages.error(request, 'Passwords do not match')
                    return render(request, 'users/register.html')
                
                # Check if email already exists
                if CustomUser.objects.filter(email=email).exists():
                    messages.error(request, 'Email already registered')
                    return render(request, 'users/register.html')
                
                # Create user
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone
                )
                
                # Create user profile
                UserProfile.objects.create(user=user)
                
                # Log the user in
                login(request, user)
                
                messages.success(request, 'Account created successfully!')
                return redirect('core:home')
                
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'users/register.html')
    
    return render(request, 'users/register.html')


@login_required
def profile_view(request):
    """User profile view"""
    user_addresses = Address.objects.filter(user=request.user, is_active=True)
    context = {
        'user_addresses': user_addresses,
    }
    return render(request, 'users/profile.html', context)


class CustomLoginView(auth_views.LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(auth_views.LogoutView):
    next_page = '/'


# ============================================
# ✅ WISHLIST VIEWS
# ============================================

@login_required
def wishlist_view(request):
    """Display user's wishlist"""
    wishlist_items = Wishlist.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('product').prefetch_related('product__images')
    
    context = {
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_items.count(),
    }
    return render(request, 'users/wishlist.html', context)


@login_required
@require_POST
def toggle_wishlist(request):
    """Add or remove product from wishlist (AJAX)"""
    try:
        product_id = request.POST.get('product_id')
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Product ID is required'
            }, status=400)
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check if item already in wishlist
        wishlist_item = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).first()
        
        if wishlist_item:
            # Remove from wishlist
            wishlist_item.delete()
            message = f'{product.name} removed from wishlist'
            is_wishlisted = False
        else:
            # Add to wishlist
            Wishlist.objects.create(
                user=request.user,
                product=product
            )
            message = f'{product.name} added to wishlist'
            is_wishlisted = True
        
        # Get updated wishlist count
        wishlist_count = Wishlist.objects.filter(user=request.user, is_active=True).count()
        
        return JsonResponse({
            'success': True,
            'message': message,
            'is_wishlisted': is_wishlisted,
            'wishlist_count': wishlist_count
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Product not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
def get_wishlist_data(request):
    """Get wishlist data as JSON (for AJAX requests)"""
    wishlist_items = Wishlist.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('product').prefetch_related('product__images')
    
    data = []
    for item in wishlist_items:
        product = item.product
        data.append({
            'id': item.id,
            'product_id': product.id,
            'product_name': product.name,
            'product_slug': product.slug,
            'product_price': float(product.current_price),
            'product_image': product.primary_image.url if product.primary_image else None,
            'is_in_stock': product.is_in_stock,
            'created_at': item.created_at.isoformat(),
        })
    
    return JsonResponse({
        'success': True,
        'wishlist_items': data,
        'wishlist_count': len(data)
    })


@login_required
@require_POST
def clear_wishlist(request):
    """Clear all items from wishlist"""
    try:
        deleted_count = Wishlist.objects.filter(user=request.user).delete()[0]
        
        return JsonResponse({
            'success': True,
            'message': f'Removed {deleted_count} items from wishlist',
            'wishlist_count': 0
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# ============================================
# ✅ ADDRESS MANAGEMENT VIEWS
# ============================================

@login_required
def add_address(request):
    """Add new address"""
    if request.method == 'POST':
        try:
            address = Address.objects.create(
                user=request.user,
                title=request.POST.get('title'),
                full_name=request.POST.get('full_name'),
                phone=request.POST.get('phone'),
                address_line_1=request.POST.get('address_line_1'),
                address_line_2=request.POST.get('address_line_2', ''),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                pincode=request.POST.get('pincode'),
                is_default=request.POST.get('is_default') == 'on'
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Address added successfully',
                    'address_id': address.id
                })
            else:
                return redirect('users:profile')
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=500)
            else:
                return render(request, 'users/add_address.html', {
                    'error': str(e)
                })
    
    return render(request, 'users/add_address.html')


@login_required
def edit_address(request, address_id):
    """Edit existing address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        try:
            address.title = request.POST.get('title')
            address.full_name = request.POST.get('full_name')
            address.phone = request.POST.get('phone')
            address.address_line_1 = request.POST.get('address_line_1')
            address.address_line_2 = request.POST.get('address_line_2', '')
            address.city = request.POST.get('city')
            address.state = request.POST.get('state')
            address.pincode = request.POST.get('pincode')
            address.is_default = request.POST.get('is_default') == 'on'
            address.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Address updated successfully'
                })
            else:
                return redirect('users:profile')
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=500)
    
    context = {
        'address': address
    }
    return render(request, 'users/edit_address.html', context)


@login_required
@require_POST
def delete_address(request, address_id):
    """Delete address"""
    try:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address_title = address.title
        address.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{address_title} address deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_POST
def set_default_address(request, address_id):
    """Set address as default"""
    try:
        # Unset all default addresses
        Address.objects.filter(user=request.user).update(is_default=False)
        
        # Set new default
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.is_default = True
        address.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{address.title} set as default address'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)