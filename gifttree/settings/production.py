"""
Production settings for GiftTree project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Get allowed hosts from environment variable
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Database Configuration - Flexible (SQLite or PostgreSQL)
# If DB_ENGINE is not set or is 'sqlite3', use SQLite (same as development)
# Otherwise, use the configured database (PostgreSQL, MySQL, etc.)
DB_ENGINE = config('DB_ENGINE', default='sqlite3')

if DB_ENGINE == 'sqlite3':
    # Use SQLite (same as development)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Use PostgreSQL or other configured database
    DATABASES = {
        'default': {
            'ENGINE': f'django.db.backends.{DB_ENGINE}',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }

# Security Settings - Configurable for different deployment scenarios
# For HTTPS deployments (recommended), set ENABLE_HTTPS=True in .env
ENABLE_HTTPS = config('ENABLE_HTTPS', default=False, cast=bool)

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# HTTPS-specific security (only if HTTPS is enabled)
if ENABLE_HTTPS:
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    # For HTTP deployments (development-like on production server)
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Session security (always enabled)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Remove debug toolbar from INSTALLED_APPS in production
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']

# Remove debug toolbar middleware from production
MIDDLEWARE = [m for m in MIDDLEWARE if 'debug_toolbar' not in m]

# Static files for production - Use WhiteNoise for serving static files
# Insert WhiteNoise middleware after SecurityMiddleware
security_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
MIDDLEWARE.insert(security_index + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email backend for production
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# Cache Configuration - Flexible (Database or Redis)
CACHE_BACKEND = config('CACHE_BACKEND', default='db')

if CACHE_BACKEND == 'redis':
    # Use Redis if available
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'gifttree',
            'TIMEOUT': 300,
        }
    }
else:
    # Use database cache (same as development, but more efficient)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
            'TIMEOUT': 300,
            'OPTIONS': {
                'MAX_ENTRIES': 1000
            }
        }
    }

# Logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'ERROR',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}