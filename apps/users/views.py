from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from .models import CustomUser, Address


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