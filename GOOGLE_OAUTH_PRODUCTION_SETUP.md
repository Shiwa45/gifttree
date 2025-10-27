# 🔐 Google OAuth Setup for Production (https://mygiftstree.com/)

## ✅ **Step 1: Get Google OAuth Credentials**

### A. Create Google Cloud Project

1. **Visit Google Cloud Console:**
   - Go to: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project:**
   - Click the project dropdown at the top
   - Click "**New Project**"
   - **Project Name:** `MyGiftTree Production`
   - **Organization:** (leave default or select if you have one)
   - Click "**Create**"
   - Wait for the project to be created (takes a few seconds)

3. **Enable APIs:**
   - Click on "**APIs & Services**" in the left sidebar
   - Click "**+ ENABLE APIS AND SERVICES**" at the top
   - Search for "**Google+ API**"
   - Click on it and click "**Enable**"
   - Also search for "**People API**" and enable it

---

### B. Configure OAuth Consent Screen

1. **Go to OAuth Consent Screen:**
   - Click "**APIs & Services**" → "**OAuth consent screen**" (left sidebar)

2. **Select User Type:**
   - Choose "**External**" (for public users)
   - Click "**Create**"

3. **Fill App Information:**

   **App Information:**
   ```
   App name: MyGiftTree
   User support email: support@mygiftstree.com
   ```

   **App logo (optional):** Upload your logo (120x120px recommended)

   **App domain:**
   ```
   Application home page: https://mygiftstree.com
   Application privacy policy link: https://mygiftstree.com/privacy-policy/
   Application terms of service link: https://mygiftstree.com/terms-of-service/
   ```

   **Authorized domains:**
   ```
   mygiftstree.com
   ```

   **Developer contact information:**
   ```
   Email addresses: support@mygiftstree.com
   ```

   - Click "**SAVE AND CONTINUE**"

4. **Scopes:**
   - Click "**ADD OR REMOVE SCOPES**"
   - Select these scopes:
     - ✅ `.../auth/userinfo.email` - See your primary Google Account email address
     - ✅ `.../auth/userinfo.profile` - See your personal info
     - ✅ `openid` - Associate you with your personal info on Google
   - Click "**UPDATE**"
   - Click "**SAVE AND CONTINUE**"

5. **Test Users (Optional for testing):**
   - Click "**+ ADD USERS**"
   - Add your email: `shiwansh@gmail.com`
   - Click "**ADD**"
   - Click "**SAVE AND CONTINUE**"

6. **Summary:**
   - Review everything
   - Click "**BACK TO DASHBOARD**"

---

### C. Create OAuth Credentials

1. **Go to Credentials:**
   - Click "**APIs & Services**" → "**Credentials**" (left sidebar)
   - Click "**+ CREATE CREDENTIALS**" at the top
   - Select "**OAuth client ID**"

2. **Configure Application Type:**
   - **Application type:** Web application
   - **Name:** `MyGiftTree Production Client`

3. **Add Authorized Origins:**
   Click "**+ ADD URI**" under "Authorized JavaScript origins":
   ```
   https://mygiftstree.com
   ```

4. **Add Redirect URIs:**
   Click "**+ ADD URI**" under "Authorized redirect URIs":
   ```
   https://mygiftstree.com/users/google-auth/
   https://mygiftstree.com/accounts/google/login/callback/
   ```

   ⚠️ **Important:** Add BOTH URLs - one is your custom implementation, the other is if you switch to Django allauth.

5. **Create:**
   - Click "**CREATE**"
   - A popup will show your credentials:

   ```
   Your Client ID: 1234567890-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com
   Your Client Secret: GOCSPX-AbCdEf1234567890GhIjKlMnOp
   ```

   📋 **COPY THESE IMMEDIATELY!** 

   - Click "**DOWNLOAD JSON**" (optional, for backup)
   - Click "**OK**"

---

## ✅ **Step 2: Add Credentials to Your AWS Server**

### A. SSH into Your AWS Server

```bash
ssh -i "your-key.pem" ubuntu@your-server-ip
# OR
ssh ubuntu@mygiftstree.com
```

### B. Navigate to Your Project Directory

```bash
cd /path/to/your/gifttree/project
# Example: cd /home/ubuntu/gifttree
```

### C. Create/Edit .env File

```bash
nano .env
```

### D. Add Google OAuth Credentials

Add these lines to your `.env` file:

```env
# Google OAuth Credentials
GOOGLE_CLIENT_ID=1234567890-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-AbCdEf1234567890GhIjKlMnOp

# Production Settings
DEBUG=False
ALLOWED_HOSTS=mygiftstree.com,www.mygiftstree.com
ENABLE_HTTPS=True

# Secret Key (generate a new one for production)
SECRET_KEY=your-secret-key-here-make-it-long-and-random

# Database (if using PostgreSQL)
DB_ENGINE=postgresql
DB_NAME=gifttree_db
DB_USER=gifttree_user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Razorpay (your existing keys)
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret

# Email (if configured)
EMAIL_HOST_USER=noreply@mygiftstree.com
EMAIL_HOST_PASSWORD=your-email-password
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## ✅ **Step 3: Update Django Settings**

### A. Update base.py to Load Google Credentials

SSH into your server and edit the settings file:

```bash
cd /path/to/your/gifttree
nano gifttree/settings/base.py
```

Find the Google OAuth section (around line 181) and update it:

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

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

### B. Update production.py to Set Correct Domain

```bash
nano gifttree/settings/production.py
```

Add/Update these settings:

```python
# Site Configuration for Production
SITE_DOMAIN = 'mygiftstree.com'
SITE_NAME = 'MyGiftTree'

# CSRF and CORS Settings
CSRF_TRUSTED_ORIGINS = [
    'https://mygiftstree.com',
    'https://www.mygiftstree.com',
]

# Allowed hosts
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='mygiftstree.com,www.mygiftstree.com').split(',')
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## ✅ **Step 4: Update Your Google Auth View**

Your project has a custom Google auth implementation. Let's verify it's using the credentials:

```bash
nano apps/users/views.py
```

Find the `google_auth_view` function and make sure it uses:

```python
def google_auth_view(request):
    """Handle Google OAuth authentication"""
    if request.method == 'POST':
        import json
        import requests
        from django.conf import settings
        
        try:
            data = json.loads(request.body)
            credential = data.get('credential')
            
            if not credential:
                return JsonResponse({'success': False, 'message': 'No credential provided'})
            
            # Verify the credential with Google
            google_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}"
            response = requests.get(google_url)
            
            if response.status_code == 200:
                user_info = response.json()
                
                # Verify the token is for your app
                if user_info.get('aud') != settings.GOOGLE_CLIENT_ID:
                    return JsonResponse({'success': False, 'message': 'Invalid token'})
                
                # Extract user information
                email = user_info.get('email')
                name = user_info.get('name')
                google_id = user_info.get('sub')
                
                # ... rest of your code
```

---

## ✅ **Step 5: Update Frontend Google Sign-In**

Your frontend needs to load the Google Sign-In library with your Client ID. 

Check your login template (`templates/users/login.html`):

```bash
nano templates/users/login.html
```

Make sure it has:

```html
<!-- Google Sign-In Script -->
<script src="https://accounts.google.com/gsi/client" async defer></script>

<script>
function handleCredentialResponse(response) {
    // Send the credential to your server
    fetch('{% url "users:google_auth" %}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            credential: response.credential
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect_url || '/';
        } else {
            alert(data.message || 'Login failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during login');
    });
}

// Initialize Google Sign-In
window.onload = function () {
    google.accounts.id.initialize({
        client_id: '{{ GOOGLE_CLIENT_ID }}',  // Or hardcode it
        callback: handleCredentialResponse
    });
    
    google.accounts.id.renderButton(
        document.getElementById('google-signin-button'),
        { theme: 'outline', size: 'large', text: 'continue_with' }
    );
};
</script>

<!-- Button where Google Sign-In will render -->
<div id="google-signin-button"></div>
```

---

## ✅ **Step 6: Restart Your Application**

After making all changes:

```bash
# Restart Gunicorn (or your WSGI server)
sudo systemctl restart gunicorn

# Restart Nginx
sudo systemctl restart nginx

# Or if using PM2, supervisor, etc.
pm2 restart gifttree
# OR
sudo supervisorctl restart gifttree
```

---

## ✅ **Step 7: Test Google OAuth**

1. **Open your site:** https://mygiftstree.com/
2. **Go to login page:** https://mygiftstree.com/users/login/
3. **Click "Sign in with Google"**
4. **Select your Google account**
5. **You should be redirected back and logged in!**

---

## 🔍 **Troubleshooting**

### Error: "redirect_uri_mismatch"
**Solution:** Check that your redirect URIs in Google Cloud Console EXACTLY match:
```
https://mygiftstree.com/users/google-auth/
https://mygiftstree.com/accounts/google/login/callback/
```

### Error: "Invalid token" or "Unauthorized"
**Solution:** 
1. Make sure your `.env` file has the correct `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
2. Restart your application after changing `.env`
3. Clear browser cache and try again

### Google button doesn't appear
**Solution:**
1. Check browser console for errors
2. Make sure Google Sign-In script is loaded
3. Verify your `client_id` is correct in the frontend JavaScript

### "This app isn't verified"
**Solution:** This is normal for new apps. Users can click "Advanced" → "Go to MyGiftTree (unsafe)" to continue. To remove this warning, you need to verify your app with Google (requires filling out a form and waiting for approval).

---

## 📝 **Quick Checklist**

- [ ] Created Google Cloud Project
- [ ] Enabled Google+ API and People API
- [ ] Configured OAuth Consent Screen
- [ ] Created OAuth Client ID
- [ ] Added authorized origins: `https://mygiftstree.com`
- [ ] Added redirect URIs: `https://mygiftstree.com/users/google-auth/`
- [ ] Copied Client ID and Client Secret
- [ ] Added credentials to `.env` file on server
- [ ] Updated `base.py` with Google credentials
- [ ] Updated `production.py` with domain settings
- [ ] Updated frontend with correct Client ID
- [ ] Restarted application
- [ ] Tested Google login on production site

---

## 🎉 **Success!**

Once completed, users can now:
- ✅ Sign in with Google on https://mygiftstree.com/
- ✅ Register using their Google account
- ✅ One-click login (no password needed)
- ✅ Secure OAuth 2.0 authentication

---

## 📚 **Additional Resources**

- Google OAuth 2.0 Documentation: https://developers.google.com/identity/protocols/oauth2
- Google Sign-In for Websites: https://developers.google.com/identity/gsi/web
- Django Settings for Google OAuth: Already configured in your project!

---

**Need Help?** 

Common issues are usually:
1. Wrong redirect URIs (must match exactly)
2. Forgot to restart application after changing .env
3. Client ID not loaded in frontend JavaScript
4. HTTPS not properly configured

Double-check the checklist above and you should be good to go! 🚀

