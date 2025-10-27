# Google OAuth Quick Start Guide 🚀

A quick reference for setting up Google OAuth on your production server.

---

## 📍 **Step 1: Get Google Credentials**

1. Go to: [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project
3. Navigate to: **APIs & Services** → **Credentials**
4. Click **"+ Create Credentials"** → **"OAuth client ID"**
5. Choose **"Web application"**
6. Add Authorized Redirect URIs:
   ```
   https://mygiftstree.com/accounts/google/login/callback/
   https://www.mygiftstree.com/accounts/google/login/callback/
   ```
   ⚠️ **Don't forget the trailing slash!**

7. Save your Client ID and Client Secret

---

## 📍 **Step 2: Configure Production Server**

SSH into your server and run:

```bash
# Navigate to project
cd ~/apps/gifttree

# Edit environment file
nano .env.production

# Add these lines (replace with your actual credentials):
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
SITE_DOMAIN=mygiftstree.com

# Save and exit (Ctrl+X, Y, Enter)
```

---

## 📍 **Step 3: Configure Django Site**

```bash
# Activate virtual environment
source venv/bin/activate

# Open Django shell
python manage.py shell
```

In the Python shell, run:

```python
from django.contrib.sites.models import Site
site = Site.objects.get_or_create(id=1)[0]
site.domain = 'mygiftstree.com'
site.name = 'MyGiftTree'
site.save()
print(f"✅ Site configured: {site.domain}")
exit()
```

---

## 📍 **Step 4: Restart Server**

```bash
# Restart Gunicorn
sudo systemctl restart gunicorn

# Or if using Supervisor:
# sudo supervisorctl restart gifttree

# Check logs for errors
sudo journalctl -u gunicorn -f
```

---

## 🧪 **Step 5: Test**

1. Visit: [https://mygiftstree.com/account/login/](https://mygiftstree.com/account/login/)
2. Click "Sign in with Google"
3. Grant permissions
4. You should be logged in! ✅

---

## ⚡ **Troubleshooting**

### Error 400: "Request is malformed"

**Check these:**
- ✅ Redirect URIs in Google Console have trailing slashes
- ✅ You added BOTH `mygiftstree.com` and `www.mygiftstree.com`
- ✅ Django Site domain is set to `mygiftstree.com` (no www, no https)
- ✅ Environment variables are loaded (restart server after changing .env)

### Still not working?

**Verify configuration:**
```bash
python manage.py shell
```

```python
# Check credentials
from django.conf import settings
print(f"Client ID: {settings.GOOGLE_CLIENT_ID[:20]}...")
print(f"Site Domain: {settings.SITE_DOMAIN}")

# Check Django Site
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
print(f"Django Site: {site.domain}")
```

---

## 📋 **Quick Checklist**

- [ ] Created OAuth client in Google Cloud Console
- [ ] Added redirect URIs with trailing slashes
- [ ] Added credentials to `.env.production`
- [ ] Configured Django Site domain
- [ ] Restarted Gunicorn
- [ ] Tested Google login

---

## 📚 **Full Documentation**

For detailed setup instructions, see:
- `GOOGLE_OAUTH_PRODUCTION_DEPLOYMENT.md` - Complete deployment guide
- `GOOGLE_OAUTH_SETUP_SUMMARY.md` - Summary of all changes

---

## 🎉 **Success!**

Once working, your users can:
- Sign in with Google
- Register with Google
- Link existing accounts to Google

**That's it! You're done!** 🚀

