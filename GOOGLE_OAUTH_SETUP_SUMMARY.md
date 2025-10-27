# Google OAuth Setup - Summary of Changes

This document summarizes all changes made to implement Google OAuth login in your Django application.

## 📦 Dependencies Added

### requirements.txt
- Added `django-allauth==0.52.0` - Provides Google OAuth integration

```bash
# To install on production:
pip install django-allauth==0.52.0
```

---

## 🔧 Configuration Changes

### 1. gifttree/settings/base.py

#### Added to `INSTALLED_APPS`:
```python
DJANGO_APPS = [
    # ... existing apps ...
    'django.contrib.sites',  # Required for allauth
]

THIRD_PARTY_APPS = [
    # ... existing apps ...
    # Django Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]
```

#### Added Google OAuth Settings:
```python
# Google OAuth Settings
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
            'key': ''
        },
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

### 2. gifttree/settings/production.py

#### Added Site Configuration:
```python
# Site Configuration for Production
SITE_DOMAIN = config('SITE_DOMAIN', default='mygiftstree.com')
SITE_NAME = 'MyGiftTree'

# CSRF and CORS Settings for production domain
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://mygiftstree.com,https://www.mygiftstree.com'
).split(',')
```

### 3. gifttree/urls.py

#### Added Allauth URLs:
```python
urlpatterns = [
    # ... existing URLs ...
    
    # Django Allauth (Google OAuth)
    path('accounts/', include('allauth.urls')),
    
    # ... rest of URLs ...
]
```

---

## 📝 New Files Created

### 1. apps/users/management/commands/setup_google_oauth.py
A management command to help configure the Django Site for production.

**Usage:**
```bash
python manage.py setup_google_oauth
```

This command:
- Configures the Django Site object with the correct domain
- Shows the authorized redirect URIs to add in Google Cloud Console
- Verifies that Google OAuth credentials are configured

### 2. env.production.example
Example environment file showing required variables for production:

```bash
# Google OAuth Credentials
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET

# Production Domain
SITE_DOMAIN=mygiftstree.com
```

### 3. GOOGLE_OAUTH_PRODUCTION_DEPLOYMENT.md
Complete step-by-step guide for deploying Google OAuth on production server.

### 4. GOOGLE_OAUTH_SETUP_SUMMARY.md (this file)
Summary of all changes made to implement Google OAuth.

---

## 🗄️ Database Changes

### Migrations Applied:
- `sites.0001_initial` - Creates `django_site` table
- `sites.0002_alter_domain_unique` - Makes domain unique
- `account.0001_initial` - Creates allauth account tables
- `account.0002_email_max_length` - Updates email field
- `socialaccount.0001_initial` - Creates social account tables
- `socialaccount.0002_token_max_lengths` - Updates token fields
- `socialaccount.0003_extra_data_default_dict` - Updates extra_data field

### New Tables Created:
- `django_site` - Stores site domain configuration
- `account_emailaddress` - Stores user email addresses
- `account_emailconfirmation` - Stores email confirmation tokens
- `socialaccount_socialaccount` - Stores social authentication accounts
- `socialaccount_socialapp` - Stores social app configurations
- `socialaccount_socialtoken` - Stores OAuth tokens

---

## 🌐 URLs Added

The following URLs are now available:

### For Users:
- `/accounts/login/` - Login page (now includes "Sign in with Google" button)
- `/accounts/signup/` - Signup page (includes "Sign up with Google" option)
- `/accounts/google/login/` - Initiates Google OAuth login flow
- `/accounts/google/login/callback/` - Google OAuth callback URL (configured in Google Cloud Console)

### For Admin:
- `/admin/sites/site/` - Configure site domain
- `/admin/socialaccount/socialapp/` - Manage social authentication apps (if needed)
- `/admin/socialaccount/socialaccount/` - View user social accounts

---

## 🔐 Environment Variables Required

### Development (.env):
```bash
GOOGLE_CLIENT_ID=your_development_client_id
GOOGLE_CLIENT_SECRET=your_development_client_secret
SITE_DOMAIN=localhost:8000
```

### Production (.env.production):
```bash
GOOGLE_CLIENT_ID=your_production_client_id
GOOGLE_CLIENT_SECRET=your_production_client_secret
SITE_DOMAIN=mygiftstree.com
CSRF_TRUSTED_ORIGINS=https://mygiftstree.com,https://www.mygiftstree.com
```

---

## ✅ Deployment Steps for Production

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Configure Django Site**:
   ```bash
   python manage.py shell
   ```
   ```python
   from django.contrib.sites.models import Site
   site = Site.objects.get_or_create(id=1)[0]
   site.domain = 'mygiftstree.com'
   site.name = 'MyGiftTree'
   site.save()
   ```

4. **Add Google OAuth credentials to `.env.production`**:
   ```bash
   GOOGLE_CLIENT_ID=your_actual_client_id
   GOOGLE_CLIENT_SECRET=your_actual_client_secret
   SITE_DOMAIN=mygiftstree.com
   ```

5. **Configure Google Cloud Console**:
   - Add Authorized Redirect URIs:
     - `https://mygiftstree.com/accounts/google/login/callback/`
     - `https://www.mygiftstree.com/accounts/google/login/callback/`

6. **Restart application server**:
   ```bash
   sudo systemctl restart gunicorn
   ```

---

## 🎨 Frontend Integration

### Login Template Changes
The existing login template should automatically show a "Sign in with Google" button when django-allauth is installed.

If you need to manually add the button, use:
```html
{% load socialaccount %}

<a href="{% provider_login_url 'google' %}" class="btn btn-google">
    <i class="fab fa-google"></i> Sign in with Google
</a>
```

---

## 🧪 Testing

### Development Testing:
1. Get Google OAuth credentials for `http://localhost:8000`
2. Add authorized redirect URI: `http://localhost:8000/accounts/google/login/callback/`
3. Set environment variables in `.env`
4. Run server: `python manage.py runserver`
5. Visit: `http://localhost:8000/account/login/`
6. Click "Sign in with Google"

### Production Testing:
1. Follow the deployment guide in `GOOGLE_OAUTH_PRODUCTION_DEPLOYMENT.md`
2. Visit: `https://mygiftstree.com/account/login/`
3. Click "Sign in with Google"
4. Verify successful login and redirect

---

## 🐛 Common Issues & Solutions

### Issue 1: "400. That's an error. The server cannot process the request because it is malformed."
**Solution**: Check that:
- Authorized Redirect URIs in Google Cloud Console match exactly (including trailing slash)
- Django Site domain is configured correctly
- Environment variables are loaded properly

### Issue 2: "Social account authentication failed"
**Solution**: 
- Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
- Check that the OAuth consent screen is published (or you're added as a test user)

### Issue 3: "No module named 'allauth'"
**Solution**: 
- Install django-allauth: `pip install django-allauth==0.52.0`
- Restart your Django application

---

## 📊 Security Considerations

1. **Environment Variables**: Never commit `.env` files with real credentials
2. **HTTPS**: Google OAuth requires HTTPS in production
3. **Secret Key**: Keep `GOOGLE_CLIENT_SECRET` confidential
4. **CSRF Protection**: The `CSRF_TRUSTED_ORIGINS` setting ensures proper CSRF protection
5. **Scope**: We only request `profile` and `email` - minimal necessary permissions

---

## 🎯 Features Now Available

✅ Users can sign in with their Google account  
✅ Users can register using Google  
✅ Existing users can link their account to Google  
✅ Email addresses are automatically verified via Google  
✅ Secure OAuth 2.0 authentication flow  
✅ Works on both desktop and mobile browsers  

---

## 📚 Next Steps (Optional)

1. **Customize Templates**: Create custom allauth templates in `templates/account/` and `templates/socialaccount/`
2. **Add More Providers**: Add Facebook, GitHub, etc. by installing additional allauth providers
3. **Email Notifications**: Configure email backend for password reset and email verification
4. **User Profile**: Extend user profile to store additional information from Google
5. **Analytics**: Track social login usage via Google Analytics or similar

---

## 💡 Tips

- **Multiple Domains**: If you have multiple domains (dev, staging, prod), create separate OAuth clients for each
- **Testing Mode**: Use Google OAuth's testing mode during development
- **Scopes**: Only request the permissions you actually need
- **User Experience**: Provide clear messaging about what data you're accessing from Google

---

## 📞 Support

If you encounter issues:
1. Check the logs: `sudo journalctl -u gunicorn -f`
2. Verify environment variables are loaded
3. Check Google Cloud Console audit logs
4. Review `GOOGLE_OAUTH_PRODUCTION_DEPLOYMENT.md` for detailed troubleshooting

---

**Last Updated**: October 27, 2025
**Django Version**: 5.0.7
**Django-allauth Version**: 0.52.0

