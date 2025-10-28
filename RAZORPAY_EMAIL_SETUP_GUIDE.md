# 🚀 Razorpay & Email Configuration Guide

## 📦 Part 1: Razorpay Setup

### Step 1: Get API Credentials from Razorpay Dashboard

You're logged into Razorpay. Now get your credentials:

#### For Testing (Test Mode):
1. Go to **Settings** (gear icon) → **API Keys**
2. Make sure **"Test Mode"** is selected (toggle at top)
3. Click **"Generate Test Key"** if you don't have one
4. Copy:
   - **Key ID**: `rzp_test_XXXXXXXXXXXX`
   - **Key Secret**: Click "Show" to reveal it

#### For Live Production (Live Mode):
1. Toggle to **"Live Mode"** at the top
2. Click **"Generate Live Key"**
3. Copy:
   - **Key ID**: `rzp_live_XXXXXXXXXXXX`
   - **Key Secret**: Click "Show" to reveal it

⚠️ **IMPORTANT**: Keep these credentials secret! Never commit them to Git.

---

## 📧 Part 2: Gmail SMTP Setup

### Step 1: Enable 2-Step Verification

You MUST have 2-Step Verification to create App Passwords:

1. Go to: https://myaccount.google.com/security
2. Find **"2-Step Verification"**
3. Click **"Get Started"**
4. Follow the setup (use your phone number)

### Step 2: Generate Gmail App Password

Regular Gmail passwords don't work with SMTP. You need an App Password:

1. Go to: https://myaccount.google.com/apppasswords
   - Or: Google Account → Security → 2-Step Verification → App Passwords

2. Create new app password:
   - **App name**: `Django GiftTree` (or any name)
   - **Device**: Select "Other (Custom name)"
   - Type: `Django Mail Server`

3. Click **"Generate"**

4. **Copy the 16-character password**:
   ```
   Example: abcd efgh ijkl mnop
   ```

5. **Remove all spaces**:
   ```
   Final: abcdefghijklmnop
   ```

6. **Save this password** - Google won't show it again!

---

## 🔧 Part 3: Add Credentials to Server

### On Production Server (.env file):

SSH into your server and edit the `.env` file:

```bash
cd ~/apps/gifttree
nano .env
```

Add these lines (replace with your actual values):

```env
# Razorpay Credentials
RAZORPAY_KEY_ID=rzp_live_XXXXXXXXXXXX
RAZORPAY_KEY_SECRET=your_razorpay_secret_key_here

# Gmail SMTP Credentials
EMAIL_HOST_USER=your-client-email@gmail.com
EMAIL_HOST_PASSWORD=your_16_char_app_password

# Admin Email (who receives order notifications)
ADMIN_EMAIL=admin@mygiftstree.com
```

Save: `Ctrl+X` → `Y` → `Enter`

---

## ✅ Part 4: Email Notifications

Once configured, the system will automatically send emails for:

### Customer Emails:
- ✉️ **Order Placed** - Immediate confirmation
- ✉️ **Order Confirmed** - When admin confirms
- ✉️ **Order Shipped** - With tracking details
- ✉️ **Order Delivered** - Delivery confirmation
- ✉️ **Payment Success** - Razorpay payment confirmation
- ✉️ **Payment Failed** - If payment fails

### Admin Emails:
- ✉️ **New Order Alert** - Every time someone places an order
- ✉️ **Payment Success** - When payment is received

---

## 🧪 Testing

### Test Razorpay (Test Mode):
1. Use Razorpay test card: `4111 1111 1111 1111`
2. CVV: Any 3 digits (e.g., `123`)
3. Expiry: Any future date (e.g., `12/25`)
4. OTP: `123456`

### Test Email:
- Place a test order
- Check customer email inbox
- Check admin email inbox

---

## 🔐 Security Notes

1. **Never commit credentials to Git**
2. **Use Test Mode keys for development**
3. **Use Live Mode keys only on production**
4. **Regenerate App Password if compromised**
5. **Keep .env file permissions restricted**: `chmod 600 .env`

---

## 🆘 Troubleshooting

### Emails not sending:
- ❌ Check Gmail App Password (not regular password)
- ❌ Check 2-Step Verification is enabled
- ❌ Check email in spam folder
- ❌ Check Gunicorn logs: `sudo journalctl -u gunicorn -n 100`

### Razorpay not working:
- ❌ Check you're using correct mode keys (Test vs Live)
- ❌ Check keys have no extra spaces
- ❌ Check Razorpay account is activated
- ❌ Check browser console for JavaScript errors

---

## 📞 Support

If you need help:
1. Check Django logs: `sudo journalctl -u gunicorn -n 100`
2. Check email backend: `python manage.py shell` → Test email
3. Contact Razorpay support for payment issues

