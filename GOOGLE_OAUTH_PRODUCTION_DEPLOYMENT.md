# Google OAuth Production Deployment Guide

This guide walks you through deploying Google OAuth on your AWS production server at `https://mygiftstree.com/`.

## 📋 Overview

Your Django app now includes Google OAuth login via django-allauth. To make it work on production, you need to:
1. Get Google OAuth credentials from Google Cloud Console
2. Add credentials to your production server
3. Configure the Django Site domain
4. Add Authorized Redirect URIs in Google Cloud Console

---

## Step 1: Get Google OAuth Credentials

### 1.1 Go to Google Cloud Console
Visit: [https://console.cloud.google.com/](https://console.cloud.google.com/)

### 1.2 Create or Select a Project
- If you don't have a project, click **"Create Project"**
- Give it a name like "MyGiftTree OAuth"
- Click **"Create"**

### 1.3 Configure OAuth Consent Screen
1. In the left sidebar, go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** (unless you have a Google Workspace)
3. Click **"Create"**
4. Fill in the required fields:
   - **App name**: MyGiftTree
   - **User support email**: your email
   - **Developer contact**: your email
5. Click **"Save and Continue"**
6. On the **Scopes** page, click **"Add or Remove Scopes"**
   - Add: `./auth/userinfo.email`
   - Add: `./auth/userinfo.profile`
   - Add: `openid`
7. Click **"Save and Continue"**
8. Add test users if in testing mode (or publish the app)
9. Click **"Save and Continue"** and then **"Back to Dashboard"**

### 1.4 Create OAuth Client ID
1. Go to **APIs & Services** → **Credentials**
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. Choose **"Web application"**
4. Give it a name: "MyGiftTree Web Client"
5. Under **"Authorized redirect URIs"**, click **"+ Add URI"** and add:
   ```
   https://mygiftstree.com/accounts/google/login/callback/
   https://www.mygiftstree.com/accounts/google/login/callback/
   ```
   ⚠️ **CRITICAL**: The trailing slash `/` is **required**!

6. Click **"Create"**
7. You'll see a popup with your credentials:
   - **Client ID**: Something like `1234567890-abc123...apps.googleusercontent.com`
   - **Client Secret**: Something like `GOCSPX-abc123...`
8. **SAVE THESE CREDENTIALS** - you'll need them for the next step

---

## Step 2: Add Credentials to Production Server

### 2.1 SSH into your AWS server
```bash
ssh ubuntu@your-server-ip
# Or ssh ubuntu@mygiftstree.com if DNS is configured
```

### 2.2 Navigate to your project directory
```bash
cd ~/apps/gifttree
```

### 2.3 Edit your production environment file
```bash
nano .env.production
# Or
nano .env
```

### 2.4 Add these lines (replace with your actual credentials):
```bash
# Google OAuth Credentials
GOOGLE_CLIENT_ID=1234567890-abc123def456...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123def456...

# Production Domain
SITE_DOMAIN=mygiftstree.com
```

Save and exit (Ctrl+X, then Y, then Enter)

---

## Step 3: Configure Django Site on Production

### 3.1 Activate your virtual environment
```bash
source venv/bin/activate
```

### 3.2 Run the Django shell
```bash
python manage.py shell
```

### 3.3 Configure the Site (run these Python commands):
```python
from django.contrib.sites.models import Site

# Get or create the site with ID=1
site = Site.objects.get_or_create(id=1)[0]

# Set the production domain
site.domain = 'mygiftstree.com'
site.name = 'MyGiftTree'
site.save()

# Verify
print(f"Site configured: {site.domain}")

# Exit the shell
exit()
```

---

## Step 4: Restart Gunicorn

### 4.1 Restart your Django application
```bash
sudo systemctl restart gunicorn
# Or
sudo supervisorctl restart gifttree
```

### 4.2 Check the logs to ensure no errors
```bash
sudo journalctl -u gunicorn -f
# Or
sudo tail -f /var/log/gunicorn/error.log
```

---

## Step 5: Test Google OAuth

### 5.1 Visit your site
Go to: [https://mygiftstree.com/account/login/](https://mygiftstree.com/account/login/)

### 5.2 Click "Sign in with Google"
You should be redirected to Google's login page.

### 5.3 Grant permissions
After logging in with your Google account, you'll be asked to grant permissions.

### 5.4 You should be redirected back
After granting permissions, you should be redirected back to your site and logged in!

---

## 🐛 Troubleshooting

### Error: "400. That's an error. The server cannot process the request because it is malformed."

**Cause**: Redirect URI mismatch or incorrect OAuth configuration.

**Solutions**:
1. **Check Authorized Redirect URIs in Google Cloud Console**:
   - Make sure you have BOTH:
     - `https://mygiftstree.com/accounts/google/login/callback/`
     - `https://www.mygiftstree.com/accounts/google/login/callback/`
   - Ensure the trailing slash `/` is present
   - URIs are case-sensitive

2. **Check Django Site configuration**:
   ```bash
   python manage.py shell
   ```
   ```python
   from django.contrib.sites.models import Site
   site = Site.objects.get(id=1)
   print(f"Site domain: {site.domain}")
   # Should be: mygiftstree.com (NOT www.mygiftstree.com)
   ```

3. **Check environment variables**:
   ```bash
   python manage.py shell
   ```
   ```python
   from django.conf import settings
   print(f"GOOGLE_CLIENT_ID: {settings.GOOGLE_CLIENT_ID[:20]}...")
   print(f"SITE_DOMAIN: {settings.SITE_DOMAIN}")
   ```

### Error: "Social account not found"

**Cause**: The social app is not configured in the database.

**Solution**: The credentials in `settings.py` should be automatically used. If not, you may need to create a SocialApp entry in the Django admin.

---

## 📝 Important Notes

1. **HTTPS is Required**: Google OAuth requires HTTPS in production. Make sure your site is using SSL/TLS (which it should be with `https://mygiftstree.com/`).

2. **Domain Consistency**: 
   - Django Site domain: `mygiftstree.com` (no www, no https)
   - Authorized Redirect URIs: Include both `https://mygiftstree.com/...` and `https://www.mygiftstree.com/...`

3. **Security**:
   - Never commit your `.env` file or expose your `GOOGLE_CLIENT_SECRET`
   - Keep your OAuth credentials secure
   - Use environment variables for all sensitive data

4. **OAuth Consent Screen**:
   - If your app is in "Testing" mode, only added test users can sign in
   - To allow anyone to sign in, publish your OAuth consent screen (in Google Cloud Console)

---

## ✅ Summary Checklist

- [ ] Created Google Cloud project
- [ ] Configured OAuth consent screen
- [ ] Created OAuth client ID and secret
- [ ] Added authorized redirect URIs with trailing slashes
- [ ] Added credentials to `.env.production` on server
- [ ] Configured Django Site domain to `mygiftstree.com`
- [ ] Restarted Gunicorn/application server
- [ ] Tested Google login on production site

---

## 🎉 Success!

Once you see the "Sign in with Google" button working and can successfully log in, your Google OAuth is fully set up!

Your users can now:
- Sign in with their Google account
- Register using Google
- Link their existing account to Google

---

## 📚 Additional Resources

- [Django-allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)

---

**Need Help?** If you encounter any issues, check the error logs and compare against the troubleshooting section above.

