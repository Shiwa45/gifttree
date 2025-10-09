# 🚀 MyGiftTree Deployment Guide

Complete guide for deploying MyGiftTree e-commerce platform to production.

## 📋 Pre-Deployment Checklist

### Environment Setup
- [ ] Python 3.11+ installed on server
- [ ] PostgreSQL database created
- [ ] Redis server running (for caching)
- [ ] Domain name configured
- [ ] SSL certificate obtained
- [ ] SMTP email service configured
- [ ] Razorpay account in live mode

### Code Preparation
- [ ] All tests passing
- [ ] Debug mode disabled
- [ ] Secret key updated
- [ ] Allowed hosts configured
- [ ] Static files collected
- [ ] Media files backed up

## 🔧 Server Requirements

### Minimum Specifications
- **CPU:** 2 cores
- **RAM:** 4GB
- **Storage:** 20GB SSD
- **OS:** Ubuntu 22.04 LTS or higher
- **Python:** 3.11+
- **PostgreSQL:** 14+
- **Redis:** 6.0+

### Recommended Specifications
- **CPU:** 4 cores
- **RAM:** 8GB
- **Storage:** 50GB SSD
- **Bandwidth:** 100 Mbps

## 1️⃣ Server Setup

### Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Install Dependencies

```bash
# Python and pip
sudo apt install python3.11 python3.11-venv python3-pip -y

# PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Redis
sudo apt install redis-server -y

# Nginx
sudo apt install nginx -y

# System utilities
sudo apt install git build-essential libpq-dev python3-dev -y
```

## 2️⃣ Database Setup

### Create PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE gifttree;
CREATE USER gifttree_user WITH PASSWORD 'your_strong_password';
ALTER ROLE gifttree_user SET client_encoding TO 'utf8';
ALTER ROLE gifttree_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE gifttree_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE gifttree TO gifttree_user;
\q
```

### Configure PostgreSQL

```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Add line:
# local   gifttree   gifttree_user   md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

## 3️⃣ Application Deployment

### Clone Repository

```bash
# Create application directory
sudo mkdir -p /var/www/gifttree
sudo chown $USER:$USER /var/www/gifttree
cd /var/www/gifttree

# Clone repository
git clone https://github.com/yourusername/gifttree.git .
```

### Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Configure Environment Variables

```bash
nano .env
```

```env
# Django Settings
SECRET_KEY=generate-a-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=mygifttree.com,www.mygifttree.com

# Database
DB_NAME=gifttree
DB_USER=gifttree_user
DB_PASSWORD=your_strong_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://127.0.0.1:6379/1

# Razorpay (LIVE MODE)
RAZORPAY_KEY_ID=your_live_key_id
RAZORPAY_KEY_SECRET=your_live_key_secret

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Site Configuration
SITE_NAME=MyGiftTree
SITE_DOMAIN=mygifttree.com
DEFAULT_FROM_EMAIL=noreply@mygifttree.com

# Security
DJANGO_SETTINGS_MODULE=gifttree.settings.production
```

### Run Migrations

```bash
python manage.py migrate
python manage.py createcachetable
```

### Create Superuser

```bash
python manage.py createsuperuser
```

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Populate Initial Data

```bash
python manage.py populate_countries
python manage.py create_wallets
```

### Create Media Directories

```bash
mkdir -p media/products media/banners media/countries media/reviews
chmod -R 755 media
```

## 4️⃣ Gunicorn Configuration

### Create Gunicorn Service

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
[Unit]
Description=Gunicorn daemon for MyGiftTree
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/gifttree
Environment="PATH=/var/www/gifttree/venv/bin"
EnvironmentFile=/var/www/gifttree/.env
ExecStart=/var/www/gifttree/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/gifttree/gunicorn.sock \
          --timeout 120 \
          gifttree.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Start Gunicorn

```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

## 5️⃣ Nginx Configuration

### Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/gifttree
```

```nginx
server {
    listen 80;
    server_name mygifttree.com www.mygifttree.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mygifttree.com www.mygifttree.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/mygifttree.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mygifttree.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 10M;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias /var/www/gifttree/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/gifttree/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # robots.txt
    location /robots.txt {
        alias /var/www/gifttree/static/robots.txt;
    }

    # Proxy to Gunicorn
    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://unix:/var/www/gifttree/gunicorn.sock;
    }
}
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/gifttree /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 6️⃣ SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d mygifttree.com -d www.mygifttree.com

# Auto-renewal
sudo certbot renew --dry-run
```

## 7️⃣ Celery Setup (Optional)

### Create Celery Service

```bash
sudo nano /etc/systemd/system/celery.service
```

```ini
[Unit]
Description=Celery Service for MyGiftTree
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/gifttree
Environment="PATH=/var/www/gifttree/venv/bin"
EnvironmentFile=/var/www/gifttree/.env
ExecStart=/var/www/gifttree/venv/bin/celery -A gifttree worker -l info

[Install]
WantedBy=multi-user.target
```

### Create Celery Beat Service

```bash
sudo nano /etc/systemd/system/celerybeat.service
```

```ini
[Unit]
Description=Celery Beat Service for MyGiftTree
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/gifttree
Environment="PATH=/var/www/gifttree/venv/bin"
EnvironmentFile=/var/www/gifttree/.env
ExecStart=/var/www/gifttree/venv/bin/celery -A gifttree beat -l info

[Install]
WantedBy=multi-user.target
```

### Start Services

```bash
sudo systemctl start celery celerybeat
sudo systemctl enable celery celerybeat
```

## 8️⃣ Monitoring & Logging

### Create Log Directory

```bash
sudo mkdir -p /var/log/gifttree
sudo chown www-data:www-data /var/log/gifttree
```

### Configure Logrotate

```bash
sudo nano /etc/logrotate.d/gifttree
```

```
/var/log/gifttree/*.log {
    daily
    missingok
    rotate 14
    compress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

## 9️⃣ Backup Strategy

### Database Backup Script

```bash
sudo nano /usr/local/bin/backup-gifttree-db.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/gifttree"
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U gifttree_user gifttree | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/gifttree/media

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
sudo chmod +x /usr/local/bin/backup-gifttree-db.sh
```

### Setup Cron Job

```bash
sudo crontab -e
```

```cron
# Backup database daily at 2 AM
0 2 * * * /usr/local/bin/backup-gifttree-db.sh
```

## 🔟 Post-Deployment Tasks

### 1. Configure Google Search Console

1. Visit https://search.google.com/search-console
2. Add property: mygifttree.com
3. Verify ownership (DNS or HTML file)
4. Submit sitemap: https://mygifttree.com/sitemap.xml
5. Request indexing for main pages
6. Monitor coverage and performance

### 2. Test Payment Gateway

1. Switch Razorpay to live mode
2. Test with real payment methods
3. Verify webhook endpoints
4. Check order confirmation emails

### 3. Configure Email Service

1. Test order confirmation emails
2. Test cart abandonment emails
3. Test feedback request emails
4. Set up email templates

### 4. Security Scan

```bash
# Run Django security checks
python manage.py check --deploy

# Check for security updates
pip list --outdated
```

### 5. Performance Testing

- Test page load times
- Verify caching works
- Check mobile responsiveness
- Run Lighthouse audit

## 🔄 Update Procedure

### Pull Latest Code

```bash
cd /var/www/gifttree
git pull origin main
```

### Update Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Run Migrations

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### Restart Services

```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery celerybeat
sudo systemctl reload nginx
```

## 🆘 Troubleshooting

### Check Logs

```bash
# Gunicorn logs
sudo journalctl -u gunicorn -n 100

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Application logs
tail -f /var/log/gifttree/django.log
```

### Common Issues

**500 Internal Server Error**
- Check Gunicorn logs
- Verify static files collected
- Check database connection

**Static Files Not Loading**
- Run collectstatic again
- Check Nginx configuration
- Verify file permissions

**Payment Gateway Failing**
- Check Razorpay keys (live mode)
- Verify webhook URLs
- Check SSL certificate

## 📊 Monitoring Tools

### Recommended Services
- **Uptime:** UptimeRobot, Pingdom
- **Error Tracking:** Sentry
- **Performance:** New Relic, DataDog
- **Log Management:** Papertrail, Loggly

## 🎯 Performance Optimization

### Enable Redis Caching

Update production settings to use Redis instead of database cache:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Enable CDN (Optional)

- Configure CloudFlare or AWS CloudFront
- Update static file URLs
- Enable caching headers

## 📝 Maintenance Schedule

### Daily
- Check error logs
- Monitor uptime
- Review failed payments

### Weekly
- Database backup verification
- Security updates check
- Performance metrics review

### Monthly
- Full system backup
- SSL certificate check
- Code dependencies update
- User analytics review

---

## 🎉 Deployment Complete!

Your MyGiftTree platform is now live!

**Next Steps:**
1. Monitor for the first 24 hours
2. Set up alerts for errors
3. Configure analytics
4. Train admin staff
5. Start marketing campaigns

**Support:**
- Technical Issues: support@mygifttree.com
- Emergency: +91-9351221905

---

Last Updated: January 2025
Deployment Guide Version: 1.0.0
