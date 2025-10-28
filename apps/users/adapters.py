from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter for allauth"""
    
    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        user = super().save_user(request, user, form, commit=False)
        
        # Generate unique username if not provided
        if not user.username or user.username == '':
            base_username = user.email.split('@')[0]
            username = base_username
            counter = 1
            
            # Keep trying until we find a unique username
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user.username = username
        
        if commit:
            user.save()
        
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter for Google OAuth"""
    
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed.
        
        This is used to check if a user with that email already exists
        and link the social account to it.
        """
        # If the user is already logged in, do nothing
        if sociallogin.is_existing:
            return
        
        # Try to find an existing user with the same email
        try:
            email = sociallogin.account.extra_data.get('email', '').lower()
            if email:
                user = User.objects.get(email=email)
                # Connect this social account to the existing user
                sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass
    
    def populate_user(self, request, sociallogin, data):
        """
        Hook that can be used to further populate the user instance.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Generate a unique username from email or Google ID
        if not user.username or user.username == '':
            email = data.get('email', '')
            if email:
                base_username = email.split('@')[0]
            else:
                # Fallback to a random username
                base_username = f"user_{uuid.uuid4().hex[:8]}"
            
            username = base_username
            counter = 1
            
            # Keep trying until we find a unique username
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user.username = username
        
        return user

