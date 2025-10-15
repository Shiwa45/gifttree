"""
WSGI config for gifttree project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use development settings by default, production settings can be set via environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gifttree.settings.development')

application = get_wsgi_application()