# 🎁 MyGiftTree - E-Commerce Platform

A feature-rich Django-based e-commerce platform for flowers, cakes, and gifts with same-day delivery, wallet system, and advanced features.

![Django](https://img.shields.io/badge/Django-5.x-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-Proprietary-red)

## 🌟 Features

### Core E-Commerce
- 🛍️ **Product Catalog** - Browse flowers, cakes, gifts, and more
- 🛒 **Shopping Cart** - Add products, variants, and add-ons
- 💳 **Secure Checkout** - Multi-step checkout with validation
- 📦 **Order Management** - Track orders from placement to delivery
- 🔍 **Advanced Search** - Filter by category, price, occasion, recipient
- ⭐ **Product Reviews** - Customer ratings and reviews with images

### Payment & Wallet
- 💰 **Wallet System** - Earn and redeem coins on purchases
  - 200 coins welcome bonus on signup
  - 10% cashback on orders (max 50 coins)
  - 25 coins for sharing feedback
- 💳 **Razorpay Integration** - Secure online payments
- 🎫 **Coupon System** - Discount codes and promotions
- 📊 **Transaction History** - Complete wallet transaction log

### User Features
- 👤 **User Accounts** - Registration, login, profile management
- 📍 **Multiple Addresses** - Save delivery addresses
- 📧 **Email Notifications** - Order updates, feedback requests
- 🔔 **Cart Abandonment** - Automated reminder emails after 24hrs
- 🌍 **International Delivery** - Ship to 10+ countries

### Admin Features
- 📊 **Comprehensive Dashboard** - Manage products, orders, users
- 🎨 **Banner Management** - Homepage slider with images
- 🏷️ **Category Management** - Organize products hierarchically
- 📈 **Analytics** - Track sales, revenue, popular products
- 🎁 **Product Add-ons** - Chocolates, greeting cards, etc.
- 🌐 **Multi-Tenant Ready** - Seller location management

### SEO & Performance
- 🔍 **SEO Optimized** - Sitemap, robots.txt, structured data
- ⚡ **Performance** - Database caching, GZip compression
- 📱 **Mobile Responsive** - Optimized for all devices
- 🖼️ **Lazy Loading** - Fast page load times
- 🎯 **Schema.org Markup** - Rich snippets for search engines

### Advanced Features
- 🎂 **Product Personalization** - Custom messages, names, dates
- 📝 **Blog System** - Content marketing with categories and tags
- 🎨 **Featured Sections** - Chocolate gifts, unique gifts, bestsellers
- 📧 **Auto Feedback Emails** - Sent 24hrs after delivery
- 🔒 **Security Hardened** - HTTPS, HSTS, XSS protection

## 🛠️ Tech Stack

### Backend
- **Framework:** Django 5.x
- **Language:** Python 3.11+
- **Database:** SQLite (dev) / PostgreSQL (production)
- **Cache:** Database cache / Redis (production)
- **Task Queue:** Celery (optional)

### Frontend
- **CSS Framework:** Bootstrap 5
- **Icons:** Font Awesome 6
- **JavaScript:** Vanilla JS
- **Templates:** Django Templates

### Integrations
- **Payment Gateway:** Razorpay
- **Email:** SMTP (configurable)
- **Storage:** Local / Cloud (configurable)

## 📋 Requirements

- Python 3.11 or higher
- pip (Python package manager)
- virtualenv or venv
- Git

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/gifttree.git
cd gifttree
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL for production)
DB_NAME=gifttree
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# Razorpay
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Site Configuration
SITE_NAME=MyGiftTree
SITE_DOMAIN=localhost:8000
DEFAULT_FROM_EMAIL=noreply@mygifttree.com
```

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create cache table
python manage.py createcachetable

# Create superuser
python manage.py createsuperuser

# Populate initial data
python manage.py populate_countries
python manage.py create_wallets
```

### 6. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000

## 📁 Project Structure

```
gifttree/
├── apps/
│   ├── core/              # Core functionality, site settings
│   ├── users/             # User authentication, profiles
│   ├── products/          # Product catalog, categories
│   ├── cart/              # Shopping cart management
│   ├── orders/            # Order processing, checkout
│   ├── reviews/           # Product reviews and ratings
│   ├── blog/              # Blog posts and content
│   └── wallet/            # Wallet system and transactions
├── gifttree/
│   ├── settings/
│   │   ├── base.py        # Base settings
│   │   ├── development.py # Development settings
│   │   └── production.py  # Production settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── templates/             # HTML templates
│   ├── base.html
│   ├── core/
│   ├── products/
│   ├── cart/
│   ├── orders/
│   ├── emails/            # Email templates
│   └── includes/          # Reusable components
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   ├── images/
│   └── robots.txt
├── media/                 # User uploaded files
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🎯 Key Commands

```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Create cache table
python manage.py createcachetable

# Populate countries
python manage.py populate_countries

# Create wallets for existing users
python manage.py create_wallets

# Run tests
python manage.py test

# Check deployment readiness
python manage.py check --deploy
```

## 🔧 Configuration

### Admin Panel
Access at: http://localhost:8000/admin

Configure:
- Site Settings (contact info, delivery charges)
- Banner Images (homepage slider)
- Categories and Products
- Coupons and Discounts
- Countries for delivery

### Payment Gateway

1. Sign up for Razorpay account
2. Get API keys (test/live mode)
3. Add to `.env` file
4. Test with Razorpay test cards

### Email Configuration

Configure SMTP settings in `.env` for:
- Order confirmations
- Cart abandonment reminders
- Feedback requests
- Password resets

## 📊 Features by Phase

### Phase 1: Foundation ✅
- Project setup and structure
- Multi-tenant architecture
- Site settings management

### Phase 2: Bug Fixes ✅
- Mobile menu improvements
- Responsive design fixes
- Performance optimizations

### Phase 3: Content & Features ✅
- Blog system
- Advanced menu system
- Product reviews

### Phase 4: Advanced Features ✅
- Wallet system (200 coins bonus)
- International delivery
- Razorpay integration
- Cart abandonment tracking
- Auto feedback emails

### Phase 5: Final Polish ✅
- Banner management
- SEO optimization
- Performance tuning
- Security hardening
- Documentation

## 🔒 Security Features

- HTTPS enforcement in production
- HSTS headers
- XSS protection
- CSRF protection
- SQL injection protection
- Secure session cookies
- Content Security Policy
- Secure password hashing

## 🌐 SEO Features

- Dynamic sitemap.xml
- robots.txt configuration
- Schema.org structured data
- Meta tags optimization
- Image alt text
- Clean URL structure
- Page load optimization

## 📱 Mobile Features

- Responsive design
- Touch-optimized UI
- Bottom navigation bar
- Mobile-friendly forms
- Fast loading times
- Progressive Web App ready

## 🤝 Contributing

This is a proprietary project. For access or collaboration:
- Contact: support@mygifttree.com

## 📄 License

Proprietary - All Rights Reserved
© 2024 MyGiftTree

## 🆘 Support

- **Email:** support@mygifttree.com
- **Phone:** +91-9351221905
- **Documentation:** See DEPLOYMENT.md
- **Issues:** Contact support team

## 🎉 Acknowledgments

- Django Framework
- Bootstrap Team
- Font Awesome
- Razorpay Payment Gateway
- All contributors and testers

---

**Built with ❤️ by MyGiftTree Team**

Last Updated: January 2025
Version: 1.0.0
