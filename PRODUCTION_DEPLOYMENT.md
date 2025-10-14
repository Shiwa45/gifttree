# GiftTree - Production Deployment Guide

This guide will help you deploy GiftTree to production using the **same configuration as development** (SQLite database).

## Table of Contents
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Environment Configuration](#environment-configuration)
- [Deployment Steps](#deployment-steps)
- [Post-Deployment Tasks](#post-deployment-tasks)
- [Upgrading to PostgreSQL (Optional)](#upgrading-to-postgresql-optional)

---

## Pre-Deployment Checklist

Before deploying to production, ensure you have:

- [ ] A server with Python 3.8+ installed
- [ ] Domain name configured (optional)
- [ ] SSL certificate (optional, for HTTPS)
- [ ] Backup of your development database
- [ ] Updated `.env` file with production values

---

## Environment Configuration

### 1. Update `.env` File

Copy your `.env` file to the production server and update these settings:

```bash
# Django Settings
SECRET_KEY=your-strong-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

# Database Configuration (Using SQLite - Same as Development)
DB_ENGINE=sqlite3

# HTTPS Configuration
ENABLE_HTTPS=False  # Set to True if you have SSL/HTTPS

# Email Configuration (for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Razorpay Configuration
RAZORPAY_KEY_ID=your_live_key_id
RAZORPAY_KEY_SECRET=your_live_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# Cache Configuration
CACHE_BACKEND=db

# Site Configuration
SITE_NAME=GiftTree
SITE_DOMAIN=yourdomain.com
```

### 2. Generate a Strong SECRET_KEY

```python
# Run this Python command to generate a secure secret key:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Deployment Steps

### Step 1: Install Dependencies

```bash
# On your production server
cd /path/to/gifttree

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt
```

### Step 2: Transfer Files

Transfer these files/folders to your production server:
- All project files
- `db.sqlite3` (your development database)
- `media/` folder (uploaded images)
- `.env` file (with production settings)

```bash
# Example using rsync
rsync -avz --exclude='venv' --exclude='__pycache__' \
  /local/path/gifttree/ user@server:/path/to/gifttree/
```

### Step 3: Configure Django Settings

Set the Django settings module to production:

```bash
# Set environment variable
export DJANGO_SETTINGS_MODULE=gifttree.settings.production

# Or add to your .bashrc or .profile
echo "export DJANGO_SETTINGS_MODULE=gifttree.settings.production" >> ~/.bashrc
```

### Step 4: Run Django Management Commands

```bash
# Create cache table (for database caching)
python manage.py createcachetable

# Collect static files
python manage.py collectstatic --noinput

# Run migrations (if any)
python manage.py migrate

# Create a superuser if needed
python manage.py createsuperuser
```

### Step 5: Test the Application

```bash
# Test with Django development server first
python manage.py runserver 0.0.0.0:8000

# Visit: http://your-server-ip:8000
```

### Step 6: Deploy with Gunicorn

#### Create Gunicorn configuration file:

Create `gunicorn_config.py`:

```python
# gunicorn_config.py
bind = "0.0.0.0:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
errorlog = "logs/gunicorn-error.log"
accesslog = "logs/gunicorn-access.log"
loglevel = "info"
```

#### Create logs directory:

```bash
mkdir -p logs
```

#### Run Gunicorn:

```bash
gunicorn gifttree.wsgi:application -c gunicorn_config.py
```

### Step 7: Create Systemd Service (Linux)

Create `/etc/systemd/system/gifttree.service`:

```ini
[Unit]
Description=GiftTree Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/gifttree
Environment="DJANGO_SETTINGS_MODULE=gifttree.settings.production"
Environment="PATH=/path/to/gifttree/venv/bin"
ExecStart=/path/to/gifttree/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/path/to/gifttree/gifttree.sock \
    --access-logfile /path/to/gifttree/logs/gunicorn-access.log \
    --error-logfile /path/to/gifttree/logs/gunicorn-error.log \
    gifttree.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gifttree
sudo systemctl start gifttree
sudo systemctl status gifttree
```

### Step 8: Configure Nginx (Recommended)

Create `/etc/nginx/sites-available/gifttree`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    location /static/ {
        alias /path/to/gifttree/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/gifttree/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://unix:/path/to/gifttree/gifttree.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/gifttree /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Post-Deployment Tasks

### 1. Set Up SSL/HTTPS (Recommended)

Using Let's Encrypt (free SSL):

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

After SSL is configured, update `.env`:
```bash
ENABLE_HTTPS=True
```

Restart the application:
```bash
sudo systemctl restart gifttree
```

### 2. Set Up Database Backups

Create a backup script `backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_PATH="/path/to/gifttree/db.sqlite3"

# Create backup
cp "$DB_PATH" "$BACKUP_DIR/db_backup_$DATE.sqlite3"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "db_backup_*.sqlite3" -mtime +7 -delete
```

Add to crontab:
```bash
crontab -e
# Add: Daily backup at 2 AM
0 2 * * * /path/to/backup_db.sh
```

### 3. Monitor Logs

```bash
# View Gunicorn logs
tail -f logs/gunicorn-error.log
tail -f logs/gunicorn-access.log

# View Django logs (if configured)
tail -f logs/django.log

# View Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### 4. Test Payment Gateway

- Test Razorpay integration with live keys
- Verify webhook endpoints are accessible
- Test order flow end-to-end

---

## Upgrading to PostgreSQL (Optional)

If your site grows and you need better performance, you can upgrade to PostgreSQL later:

### 1. Install PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib
```

### 2. Create Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE gifttree_db;
CREATE USER gifttree_user WITH PASSWORD 'your_secure_password';
ALTER ROLE gifttree_user SET client_encoding TO 'utf8';
ALTER ROLE gifttree_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE gifttree_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE gifttree_db TO gifttree_user;
\q
```

### 3. Install PostgreSQL Driver

```bash
pip install psycopg2-binary==2.9.9
```

### 4. Update `.env`

```bash
DB_ENGINE=postgresql
DB_NAME=gifttree_db
DB_USER=gifttree_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Migrate Data

```bash
# Dump SQLite data
python manage.py dumpdata --natural-foreign --natural-primary \
  --exclude contenttypes --exclude auth.Permission \
  --output data.json

# Update settings to use PostgreSQL
# Then load data
python manage.py migrate
python manage.py loaddata data.json
```

### 6. Restart Application

```bash
sudo systemctl restart gifttree
```

---

## Troubleshooting

### Issue: Static files not loading

```bash
# Re-collect static files
python manage.py collectstatic --clear --noinput

# Check permissions
sudo chown -R www-data:www-data /path/to/gifttree/staticfiles
```

### Issue: Database permission errors

```bash
# Fix SQLite permissions
sudo chown www-data:www-data db.sqlite3
sudo chmod 664 db.sqlite3
sudo chown www-data:www-data .  # Parent directory must be writable
```

### Issue: Media uploads not working

```bash
# Fix media folder permissions
sudo chown -R www-data:www-data /path/to/gifttree/media
sudo chmod -R 775 /path/to/gifttree/media
```

### Issue: 502 Bad Gateway

```bash
# Check if Gunicorn is running
sudo systemctl status gifttree

# Check socket file permissions
ls -la /path/to/gifttree/gifttree.sock

# View Gunicorn logs
tail -f logs/gunicorn-error.log
```

---

## Performance Optimization

### Enable Redis Cache (Optional)

```bash
# Install Redis
sudo apt install redis-server

# Install Python Redis client
pip install redis django-redis

# Update .env
CACHE_BACKEND=redis
REDIS_URL=redis://127.0.0.1:6379/1

# Restart application
sudo systemctl restart gifttree
```

### Compress and Optimize Images

```bash
# Install optimization tools
sudo apt install jpegoptim optipng

# Optimize existing media
find media/ -name "*.jpg" -exec jpegoptim --strip-all {} \;
find media/ -name "*.png" -exec optipng -o7 {} \;
```

---

## Security Checklist

- [x] DEBUG=False in production
- [x] Strong SECRET_KEY generated
- [x] ALLOWED_HOSTS configured correctly
- [ ] HTTPS enabled (if possible)
- [x] Database backups scheduled
- [ ] Firewall configured (allow only 80, 443, SSH)
- [ ] Regular security updates
- [x] Secure file permissions
- [ ] Rate limiting configured (optional)
- [ ] Failed login monitoring (optional)

---

## Maintenance Commands

```bash
# View active sessions
python manage.py clearsessions

# Clear cache
python manage.py cache_clear  # If using django-extensions

# Database backup
cp db.sqlite3 backups/db_$(date +%Y%m%d).sqlite3

# Update application
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gifttree
```

---

## Support and Contact

For deployment issues or questions:
- Check logs in `logs/` directory
- Review Django documentation: https://docs.djangoproject.com/
- Gunicorn documentation: https://docs.gunicorn.org/

---

**Congratulations!** Your GiftTree application is now running in production with the same SQLite configuration as development. You can upgrade to PostgreSQL anytime your site grows.
