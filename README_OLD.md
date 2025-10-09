# GiftTree - E-commerce Platform

GiftTree is a Django-based e-commerce platform for sending flowers, cakes, and gifts online. This project is inspired by MyFlowerTree and features a pink-themed, mobile-first responsive design.

## Features

- **Product Management**: Categories, products with variants, and inventory management
- **User Management**: Custom user model with profile and address management
- **Shopping Cart**: Session-based and user-based cart functionality
- **Order Management**: Complete order lifecycle with tracking
- **Review System**: Product reviews with ratings and images
- **Admin Interface**: Enhanced Django admin with inline editing
- **Responsive Design**: Mobile-first Bootstrap 5 implementation

## Project Structure

```
gifttree/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
├── gifttree/
│   ├── settings/          # Split settings for different environments
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/              # Core functionality and base models
│   ├── users/             # User management with custom user model
│   ├── products/          # Product catalog with categories and variants
│   ├── cart/              # Shopping cart functionality
│   ├── orders/            # Order management and tracking
│   └── reviews/           # Product review system
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploaded files
└── templates/             # HTML templates
```

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository** (if applicable)
   ```bash
   cd gifttree
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env` file and update values as needed
   - Generate a new SECRET_KEY for production

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data** (optional)
   ```bash
   python manage.py create_sample_data
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Frontend: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Settings

The project uses split settings:

- `base.py`: Common settings for all environments
- `development.py`: Development-specific settings
- `production.py`: Production-specific settings

Default environment is development. For production, set:
```bash
export DJANGO_SETTINGS_MODULE=gifttree.settings.production
```

## Database Models

### Core Models
- **BaseModel**: Abstract model with common fields (created_at, updated_at, is_active)
- **SiteSettings**: Global site configuration

### User Models
- **CustomUser**: Extended user model with email as username
- **UserProfile**: Additional user profile information
- **Address**: User delivery addresses

### Product Models
- **Category**: Hierarchical product categories
- **Occasion**: Special occasions for products
- **Product**: Main product model with pricing and inventory
- **ProductImage**: Multiple images per product
- **ProductVariant**: Product variations (size, color, etc.)

### Cart Models
- **Cart**: User shopping cart
- **CartItem**: Individual cart items

### Order Models
- **Order**: Customer orders with billing/shipping info
- **OrderItem**: Individual order items
- **OrderTracking**: Order status tracking

### Review Models
- **Review**: Product reviews with ratings
- **ReviewImage**: Images attached to reviews

## Admin Interface

Access the admin interface at `/admin/` with your superuser credentials.

Features:
- Enhanced product management with inline images and variants
- User management with addresses
- Order management with tracking
- Category and occasion management
- Site settings configuration

## API Endpoints

The project is ready for API integration. URL patterns are organized by app:

- `/` - Core/Home
- `/products/` - Product catalog
- `/cart/` - Shopping cart
- `/orders/` - Order management
- `/account/` - User account
- `/reviews/` - Review system

## Management Commands

### create_sample_data

Creates sample data for development:

```bash
python manage.py create_sample_data

# Clear existing data and create new
python manage.py create_sample_data --clear
```

Creates:
- Categories and subcategories
- Occasions
- Sample products with variants
- Sample users
- User addresses

## Development

### Running Tests

```bash
python manage.py test
```

### Code Quality

The project follows Django best practices:
- Split settings for different environments
- Custom user model
- Proper model relationships
- Admin customization
- Static file organization

### Adding New Features

1. Create migrations for model changes:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. Update admin configurations in `admin.py`
3. Add URL patterns in app `urls.py`
4. Create/update templates
5. Add static files as needed

## Deployment

### Production Checklist

1. Set `DEBUG = False`
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure email backend
5. Set up SSL/HTTPS
6. Configure caching (Redis recommended)
7. Set up logging
8. Configure backup strategy

### Environment Variables for Production

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost/gifttree
REDIS_URL=redis://localhost:6379/1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes.

## Support

For support or questions, please contact the development team.