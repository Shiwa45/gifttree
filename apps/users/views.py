# Add this to apps/users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from .models import CustomUser, Address, UserProfile
from django.db import transaction


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
    
    if request.method == 'POST':
        try:
            # Update user profile
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.phone = request.POST.get('phone', '')
            user.save()
            
            # Update profile bio if exists
            if hasattr(user, 'profile'):
                user.profile.bio = request.POST.get('bio', '')
                user.profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    context = {
        'user_addresses': user_addresses,
    }
    return render(request, 'users/profile.html', context)


class CustomLoginView(auth_views.LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return '/'


class CustomLogoutView(auth_views.LogoutView):
    next_page = '/'



# Add these to existing apps/users/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Wishlist
from apps.products.models import Product
import json


@login_required
def wishlist_view(request):
    """Display user's wishlist"""
    wishlist_items = Wishlist.objects.filter(
        user=request.user, 
        is_active=True
    ).select_related('product__category').prefetch_related('product__images')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'users/wishlist.html', context)


@require_POST
@login_required
def toggle_wishlist(request):
    """Add or remove product from wishlist via Ajax"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check if already in wishlist
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
        }, status=400)


@login_required
def get_wishlist_data(request):
    """Get wishlist data for Ajax requests"""
    try:
        wishlist_items = Wishlist.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('product')
        
        items = []
        for item in wishlist_items:
            items.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_slug': item.product.slug,
            })
        
        return JsonResponse({
            'success': True,
            'wishlist': {
                'items': items,
                'count': len(items)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
    

# Add these to existing apps/users/views.py

from django.contrib.auth import login, authenticate
from django.shortcuts import redirect
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def register_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email', '').strip().lower()
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        # Validation
        errors = []
        
        if not email:
            errors.append('Email is required')
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append('Invalid email format')
            
            if CustomUser.objects.filter(email=email).exists():
                errors.append('Email already registered')
        
        if not username:
            errors.append('Username is required')
        elif CustomUser.objects.filter(username=username).exists():
            errors.append('Username already taken')
        
        if not password:
            errors.append('Password is required')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters')
        elif password != password_confirm:
            errors.append('Passwords do not match')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'users/register.html', {
                'email': email,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone
            })
        
        # Create user
        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Log the user in
            login(request, user)
            
            messages.success(request, 'Registration successful! Welcome to GiftTree.')
            return redirect('core:home')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'users/register.html')
    
    return render(request, 'users/register.html')


@require_POST
def register_ajax(request):
    """Handle registration via Ajax"""
    try:
        data = json.loads(request.body)
        
        email = data.get('email', '').strip().lower()
        username = data.get('username', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not email or not username or not password:
            return JsonResponse({
                'success': False,
                'message': 'All fields are required'
            }, status=400)
        
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid email format'
            }, status=400)
        
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'Email already registered'
            }, status=400)
        
        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'message': 'Username already taken'
            }, status=400)
        
        if len(password) < 8:
            return JsonResponse({
                'success': False,
                'message': 'Password must be at least 8 characters'
            }, status=400)
        
        # Create user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Log the user in
        login(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Registration successful!',
            'redirect': '/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)