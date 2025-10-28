# 🚀 Deployment Steps: Email & Razorpay Configuration

## ✅ What We've Done:

1. ✅ Changed email backend from console to SMTP
2. ✅ Added admin email notifications
3. ✅ Added automatic emails for:
   - Order placed (customer + admin)
   - Order status changes (customer)
   - All status updates (confirmed, shipped, delivered, etc.)
4. ✅ Razorpay configuration ready
5. ✅ Test email script created

---

## 📋 STEP-BY-STEP DEPLOYMENT GUIDE

### STEP 1: Get Razorpay Credentials

🔗 **Already logged into Razorpay Dashboard?** Follow these steps:

1. **For Production (Live Mode)**:
   - Go to: Settings → API Keys
   - Toggle to **"Live Mode"**
   - Click **"Generate Live Key"** (if not already done)
   - Copy:
     - `Key ID`: starts with `rzp_live_`
     - `Key Secret`: Click "Show" to reveal

2. **Save these somewhere safe** (you'll need them in Step 3)

---

### STEP 2: Set Up Gmail App Password

Your client's Gmail account needs an App Password (NOT regular password):

#### 2a. Enable 2-Step Verification
1. Go to: https://myaccount.google.com/security
2. Find **"2-Step Verification"**
3. Click **"Get Started"** and complete setup

#### 2b. Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. App name: `MyGiftTree Django`
3. Click **"Generate"**
4. **Copy the 16-character password** (example: `abcd efgh ijkl mnop`)
5. **Remove all spaces**: `abcdefghijklmnop`
6. **Save this** - you can't see it again!

---

### STEP 3: SSH into Production Server

```bash
ssh -i "C:\AWSkeys\mygift.pem" ubuntu@16.171.250.30
```

---

### STEP 4: Pull Latest Code

```bash
cd ~/apps/gifttree
git pull origin main
```

---

### STEP 5: Update .env File

```bash
nano .env
```

**Add/Update these lines** (replace with actual values):

```env
# Razorpay Live Credentials
RAZORPAY_KEY_ID=rzp_live_XXXXXXXXXXXX
RAZORPAY_KEY_SECRET=your_razorpay_secret_key

# Gmail SMTP (use App Password, not regular password!)
EMAIL_HOST_USER=your-client-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=MyGiftTree <your-client-email@gmail.com>

# Admin Email (who receives order notifications)
ADMIN_EMAIL=admin-email@gmail.com
```

**Save**: `Ctrl+X` → `Y` → `Enter`

---

### STEP 6: Test Email Configuration

```bash
source venv/bin/activate
python test_email.py
```

**Expected output:**
```
✅ Test email sent successfully to: admin-email@gmail.com
```

**If it fails:**
- Check you used App Password (not regular password)
- Check 2-Step Verification is enabled
- Check for typos in email/password

**Test sending to a specific email:**
```bash
python test_email.py customer-email@gmail.com
```

---

### STEP 7: Restart Gunicorn

```bash
sudo systemctl restart gunicorn
```

**Check status:**
```bash
sudo systemctl status gunicorn
```

Should show: `Active: active (running)`

---

### STEP 8: Test on Live Site

#### Test Email Notifications:

1. **Place a test order** on https://mygiftstree.com

2. **Check Customer Email**:
   - Should receive "Order Placed Successfully" email
   - Check inbox and spam folder

3. **Check Admin Email**:
   - Admin should receive "New Order Received" email
   - Contains order details and link to admin panel

4. **Test Status Change**:
   - Go to Admin Panel: https://mygiftstree.com/admin/
   - Find the test order
   - Change status from "Pending" to "Confirmed"
   - Customer should receive "Order Status Update" email

#### Test Razorpay Payment:

1. **Go to checkout page**
2. **Select "Online Payment"**
3. **Complete test payment** with:
   - Card: `4111 1111 1111 1111`
   - CVV: `123`
   - Expiry: Any future date
   - OTP: `123456`

4. **Check emails**:
   - Customer gets order confirmation
   - Admin gets new order notification

---

### STEP 9: Monitor Logs

**Watch for any errors:**
```bash
sudo journalctl -u gunicorn -f
```

**Press `Ctrl+C` to stop watching**

---

## 📧 Email Notifications Summary

### Customer Receives:
- ✉️ **Order Placed** - Immediate confirmation when order is created
- ✉️ **Order Confirmed** - When admin confirms the order
- ✉️ **Order Processing** - When being prepared
- ✉️ **Order Shipped** - With tracking number (if added)
- ✉️ **Order Delivered** - Delivery confirmation
- ✉️ **Payment Success** - Razorpay payment confirmation

### Admin Receives:
- ✉️ **New Order Alert** - Every time someone places an order
  - Includes customer details, order amount, items, delivery address
  - Direct link to admin panel to process order

---

## 🔐 Security Checklist

- ✅ Using Gmail App Password (not regular password)
- ✅ Razorpay Live keys (not test keys)
- ✅ `.env` file permissions restricted: `chmod 600 ~/apps/gifttree/.env`
- ✅ Credentials not committed to Git
- ✅ HTTPS enabled on mygiftstree.com

---

## 🧪 Testing Checklist

Before going live:

- [ ] Test email sent successfully
- [ ] Customer receives order placed email
- [ ] Admin receives new order notification
- [ ] Status change emails work
- [ ] Razorpay test payment works
- [ ] Order created after successful payment
- [ ] Email delivery to spam folder (move to inbox if needed)

---

## 🆘 Troubleshooting

### "SMTPAuthenticationError"
**Problem**: Wrong Gmail credentials
**Solution**: 
- Make sure you're using App Password, not regular password
- Check 2-Step Verification is enabled
- Regenerate App Password if needed

### "Connection refused" or "Timeout"
**Problem**: Firewall blocking SMTP
**Solution**:
```bash
# Check if port 587 is open
telnet smtp.gmail.com 587
```

### Emails going to spam
**Solution**:
- Mark as "Not Spam" in Gmail
- Ask client to add sender to contacts
- Consider setting up SPF/DKIM records (advanced)

### Emails not sending (no error)
**Solution**:
```bash
# Check Django logs
sudo journalctl -u gunicorn -n 100 | grep email

# Test in Django shell
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@gmail.com', ['to@gmail.com'])
```

### Razorpay key error
**Problem**: Keys have spaces or newlines
**Solution**: Re-copy keys, ensure no extra characters

---

## 📞 Need Help?

1. **Check server logs**: `sudo journalctl -u gunicorn -n 100`
2. **Test email manually**: `python test_email.py`
3. **Check .env file**: `cat ~/apps/gifttree/.env`
4. **Restart Gunicorn**: `sudo systemctl restart gunicorn`

---

## ✅ Success Indicators

You'll know everything is working when:
1. ✅ Test email arrives in admin inbox
2. ✅ New order triggers emails to both customer and admin
3. ✅ Status changes send customer emails
4. ✅ Razorpay payment completes successfully
5. ✅ No errors in Gunicorn logs

---

**🎉 Once all tests pass, your system is fully configured!**

