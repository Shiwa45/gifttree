# 🚀 Google OAuth Quick Reference

## 📋 **Quick Setup (5 Minutes)**

### 1️⃣ **Get Google Credentials**

**Google Cloud Console:** https://console.cloud.google.com/

1. Create Project → "MyGiftTree Production"
2. Enable APIs: "Google+ API" and "People API"
3. OAuth Consent Screen:
   - Type: External
   - App name: MyGiftTree
   - Domain: `mygiftstree.com`
   - Scopes: email, profile, openid
4. Create Credentials → OAuth Client ID → Web Application:
   - **Authorized JavaScript origins:** `https://mygiftstree.com`
   - **Redirect URIs:** 
     ```
     https://mygiftstree.com/users/google-auth/
     https://mygiftstree.com/accounts/google/login/callback/
     ```
5. Copy **Client ID** and **Client Secret**

---

### 2️⃣ **Add to Your Server**

SSH into your AWS server:

```bash
ssh ubuntu@mygiftstree.com
cd /path/to/gifttree
nano .env
```

Add these lines:

```env
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
ALLOWED_HOSTS=mygiftstree.com,www.mygiftstree.com
CSRF_TRUSTED_ORIGINS=https://mygiftstree.com,https://www.mygiftstree.com
ENABLE_HTTPS=True
```

---

### 3️⃣ **Restart Application**

```bash
# If using Gunicorn + Nginx
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# If using PM2
pm2 restart gifttree

# If using Supervisor
sudo supervisorctl restart gifttree
```

---

### 4️⃣ **Test**

1. Visit: https://mygiftstree.com/users/login/
2. Click "Sign in with Google"
3. Select your Google account
4. ✅ You should be logged in!

---

## ⚙️ **Important URLs**

### Google Console URLs:
- **Main Console:** https://console.cloud.google.com/
- **OAuth Consent:** https://console.cloud.google.com/apis/credentials/consent
- **Credentials:** https://console.cloud.google.com/apis/credentials

### Your Application URLs:
- **Login Page:** https://mygiftstree.com/users/login/
- **Google Auth Endpoint:** https://mygiftstree.com/users/google-auth/
- **Admin Panel:** https://mygiftstree.com/admin/

---

## 🔧 **Redirect URIs (Copy & Paste)**

Add these **EXACTLY** in Google Cloud Console:

```
https://mygiftstree.com/users/google-auth/
https://mygiftstree.com/accounts/google/login/callback/
```

⚠️ **No trailing slash on origin, yes on callbacks!**

---

## 🐛 **Common Issues**

### Error: "redirect_uri_mismatch"
✅ **Fix:** Redirect URI in Google Console must EXACTLY match your app URL  
Check: https://console.cloud.google.com/apis/credentials

### Error: "Invalid client ID"
✅ **Fix:** 
1. Check `.env` file has correct `GOOGLE_CLIENT_ID`
2. Restart application
3. Clear browser cache

### Google button doesn't appear
✅ **Fix:** 
1. Check browser console (F12) for JavaScript errors
2. Verify Google Sign-In script is loaded
3. Make sure `client_id` is set in frontend

### "This app isn't verified" warning
✅ **Normal for new apps.** Users can click "Advanced" → Continue  
To remove: Verify your app with Google (takes 1-2 weeks)

---

## 📱 **Frontend Integration**

Make sure your login template has:

```html
<script src="https://accounts.google.com/gsi/client" async defer></script>

<script>
google.accounts.id.initialize({
    client_id: '{{ GOOGLE_CLIENT_ID }}',
    callback: handleCredentialResponse
});
</script>

<div id="google-signin-button"></div>
```

---

## 🔒 **Security Checklist**

- [x] Added Google credentials to `.env` (not hardcoded)
- [x] Set `DEBUG=False` in production
- [x] Set `ENABLE_HTTPS=True`
- [x] Set `ALLOWED_HOSTS` to your domain only
- [x] Generated strong `SECRET_KEY`
- [x] Verified redirect URIs match exactly
- [x] Enabled HTTPS on server
- [x] Tested login flow

---

## 📞 **Support**

**Google OAuth Documentation:**  
https://developers.google.com/identity/protocols/oauth2

**Django OAuth Settings:**  
Already configured in `gifttree/settings/base.py`

**Full Guide:**  
See `GOOGLE_OAUTH_PRODUCTION_SETUP.md`

---

## ✅ **Success Indicators**

When working correctly, you should see:

1. ✅ Google Sign-In button appears on login page
2. ✅ Clicking button opens Google account selector
3. ✅ After selecting account, redirects back to your site
4. ✅ User is logged in automatically
5. ✅ User details saved in your database
6. ✅ No console errors in browser

---

**Last Updated:** October 2025  
**Your Domain:** https://mygiftstree.com/  
**Status:** ✅ Settings files updated, ready for credentials!

