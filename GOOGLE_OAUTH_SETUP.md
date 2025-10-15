# Google OAuth Setup Guide

## 🔐 **Google OAuth Configuration Complete!**

I've successfully removed Facebook login and set up Google OAuth functionality for your Django website.

## ✅ **What Was Implemented:**

### **1. Removed Facebook Login**
- ✅ Removed Facebook login button from login page
- ✅ Cleaned up Facebook-specific CSS
- ✅ Updated template to show only Google login

### **2. Installed Django Allauth**
- ✅ Added `django-allauth==0.52.0` to requirements.txt
- ✅ Configured allauth in Django settings
- ✅ Added allauth URLs to main URL configuration
- ✅ Applied allauth database migrations

### **3. Google OAuth Configuration**
- ✅ Added Google OAuth provider settings
- ✅ Created Google login view and URL
- ✅ Updated login template with functional Google button
- ✅ Created management command for OAuth setup

## 🚀 **Setup Google OAuth Credentials**

### **Step 1: Create Google OAuth App**

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create a new project** or select existing one
3. **Enable Google+ API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
4. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8000/accounts/google/login/callback/` (for development)
     - `https://yourdomain.com/accounts/google/login/callback/` (for production)

### **Step 2: Configure Django**

Run this command with your Google OAuth credentials:

```bash
python manage.py setup_google_oauth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

**Example:**
```bash
python manage.py setup_google_oauth --client-id "123456789-abcdefg.apps.googleusercontent.com" --client-secret "GOCSPX-abcdefghijklmnop"
```

### **Step 3: Test Google Login**

1. **Start your Django server**:
   ```bash
   python manage.py runserver
   ```

2. **Visit login page**: http://localhost:8000/account/login/
3. **Click "Continue with Google"** button
4. **Complete Google OAuth flow**

## 📁 **Files Modified:**

### **1. `templates/users/login.html`**
- ✅ Removed Facebook login button
- ✅ Updated Google button to be functional
- ✅ Cleaned up CSS (removed Facebook styles)
- ✅ Made Google button full-width

### **2. `gifttree/settings/base.py`**
- ✅ Added allauth apps to INSTALLED_APPS
- ✅ Added allauth middleware
- ✅ Added authentication backends
- ✅ Added allauth configuration settings
- ✅ Added Google OAuth provider settings

### **3. `gifttree/urls.py`**
- ✅ Added allauth URLs (`accounts/`)

### **4. `apps/users/views.py`**
- ✅ Added `google_login_view` function

### **5. `apps/users/urls.py`**
- ✅ Added Google login URL

### **6. `requirements.txt`**
- ✅ Added `django-allauth==0.52.0`

### **7. `apps/core/management/commands/setup_google_oauth.py`**
- ✅ Created management command for OAuth setup

## 🔧 **Google OAuth Settings**

The following settings are configured in `gifttree/settings/base.py`:

```python
# Django Allauth Settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'

# Social Account Settings
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True

# Google OAuth Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}
```

## 🌐 **URLs Available:**

- **Login Page**: `/account/login/`
- **Google Login**: `/account/google-login/`
- **Allauth URLs**: `/accounts/` (includes all OAuth flows)

## 🎯 **Next Steps:**

1. **Get Google OAuth Credentials** from Google Cloud Console
2. **Run the setup command** with your credentials
3. **Test Google login** functionality
4. **Deploy to production** with production OAuth credentials

## 🔒 **Security Notes:**

- ✅ **PKCE Enabled**: Enhanced security for OAuth flow
- ✅ **Email Verification**: Optional but recommended
- ✅ **Auto Signup**: Users are automatically created on first login
- ✅ **Session Management**: Proper session handling

## 🚀 **Production Deployment:**

For production, update these settings:

1. **Update Site Domain**:
   ```python
   SITE_DOMAIN = 'yourdomain.com'
   ```

2. **Add Production OAuth Credentials**:
   ```bash
   python manage.py setup_google_oauth --client-id PROD_CLIENT_ID --client-secret PROD_CLIENT_SECRET
   ```

3. **Update Google Cloud Console**:
   - Add production redirect URI
   - Update authorized domains

## ✅ **Ready to Use!**

Your Google OAuth login is now fully configured! Users can:
- ✅ **Login with Google** using their Google account
- ✅ **Auto-register** if they don't have an account
- ✅ **Seamless experience** with proper redirects
- ✅ **Secure OAuth flow** with PKCE protection

Just get your Google OAuth credentials and run the setup command! 🎉🔐✨
