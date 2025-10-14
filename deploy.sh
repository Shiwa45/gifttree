#!/bin/bash

###############################################################################
# GiftTree Production Deployment Script
# This script helps deploy GiftTree to production using SQLite
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}GiftTree Production Deployment${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/Update requirements
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo "Please create .env file with production settings"
    exit 1
fi

# Set Django settings
export DJANGO_SETTINGS_MODULE=gifttree.settings.production

# Create logs directory if it doesn't exist
mkdir -p logs

# Create cache table
echo -e "${YELLOW}Creating cache table...${NC}"
python manage.py createcachetable

# Run migrations
echo -e "${YELLOW}Running migrations...${NC}"
python manage.py migrate --noinput

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Set correct permissions for SQLite database
if [ -f "db.sqlite3" ]; then
    echo -e "${YELLOW}Setting database permissions...${NC}"
    chmod 664 db.sqlite3
    # Set parent directory writable (needed for SQLite)
    chmod 775 .
fi

# Set media folder permissions
if [ -d "media" ]; then
    echo -e "${YELLOW}Setting media folder permissions...${NC}"
    chmod -R 775 media
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Test the application:"
echo "   python manage.py runserver 0.0.0.0:8000"
echo ""
echo "2. Start with Gunicorn:"
echo "   gunicorn gifttree.wsgi:application -c gunicorn_config.py"
echo ""
echo "3. Or start systemd service:"
echo "   sudo systemctl start gifttree"
echo ""
echo -e "${YELLOW}View logs:${NC}"
echo "   tail -f logs/gunicorn-error.log"
echo ""
