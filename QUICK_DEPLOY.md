# Quick Deployment Guide - GiftTree

## For Same Configuration as Development (SQLite)

### 1️⃣ Prepare .env File

```bash
SECRET_KEY=generate-new-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,your-server-ip
DB_ENGINE=sqlite3
ENABLE_HTTPS=False
CACHE_BACKEND=db
```

### 2️⃣ Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3️⃣ Deploy

```bash
# Set Django settings
export DJANGO_SETTINGS_MODULE=gifttree.settings.production

# Run deployment commands
python manage.py createcachetable
python manage.py migrate
python manage.py collectstatic --noinput
```

### 4️⃣ Run Application

**Option A: Quick Test**
```bash
python manage.py runserver 0.0.0.0:8000
```

**Option B: Production (Gunicorn)**
```bash
gunicorn gifttree.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### 5️⃣ Set Up Systemd Service (Linux)

```bash
sudo nano /etc/systemd/system/gifttree.service
```

Add:
```ini
[Unit]
Description=GiftTree
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/gifttree
Environment="DJANGO_SETTINGS_MODULE=gifttree.settings.production"
ExecStart=/path/to/gifttree/venv/bin/gunicorn gifttree.wsgi:application --bind 0.0.0.0:8000 --workers 3

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gifttree
sudo systemctl start gifttree
```

### 6️⃣ Configure Nginx (Optional)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/gifttree/staticfiles/;
    }

    location /media/ {
        alias /path/to/gifttree/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

---

## Important Settings Summary

| Setting | Development | Production (SQLite) |
|---------|------------|---------------------|
| DEBUG | True | False |
| ALLOWED_HOSTS | ['*'] | Your domains |
| Database | SQLite | SQLite (same) |
| Cache | Dummy | Database |
| HTTPS | Not required | Optional |
| Static Files | Django serves | WhiteNoise |

---

## File Permissions (Important!)

```bash
# Database
chmod 664 db.sqlite3
chmod 775 . # Parent directory

# Media folder
chmod -R 775 media/
chown -R www-data:www-data media/
```

---

## Troubleshooting

**Static files not loading?**
```bash
python manage.py collectstatic --clear --noinput
```

**Database locked?**
```bash
sudo chown www-data:www-data db.sqlite3
```

**502 Bad Gateway?**
```bash
sudo systemctl status gifttree
tail -f logs/gunicorn-error.log
```

---

## Backup Command

```bash
# Daily backup (add to crontab)
cp db.sqlite3 backups/db_$(date +%Y%m%d).sqlite3
```

---

See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for detailed instructions.
