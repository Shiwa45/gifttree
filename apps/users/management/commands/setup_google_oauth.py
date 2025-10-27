"""
Management command to set up Google OAuth configuration.
This command:
1. Creates/updates the Site object with the correct domain
2. Shows the authorized redirect URIs to add in Google Cloud Console
"""

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = 'Sets up Google OAuth by configuring Site for production'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Google OAuth Configuration Setup'))
        self.stdout.write(self.style.SUCCESS('='*60))

        # Step 1: Create or update Site
        self.stdout.write('\nStep 1: Configuring Django Site...')
        try:
            site = Site.objects.get(id=settings.SITE_ID)
            
            # Determine the correct domain based on environment
            if hasattr(settings, 'SITE_DOMAIN'):
                domain = settings.SITE_DOMAIN
            else:
                domain = 'localhost:8000'
            
            old_domain = site.domain
            site.domain = domain
            site.name = getattr(settings, 'SITE_NAME', 'MyGiftTree')
            site.save()
            
            self.stdout.write(self.style.SUCCESS(f'  ✅ Updated Site (ID: {site.id})'))
            if old_domain != domain:
                self.stdout.write(f'     Old Domain: {old_domain}')
                self.stdout.write(f'     New Domain: {site.domain}')
            else:
                self.stdout.write(f'     Domain: {site.domain}')
            self.stdout.write(f'     Name: {site.name}')
        except Site.DoesNotExist:
            # Determine the correct domain
            if hasattr(settings, 'SITE_DOMAIN'):
                domain = settings.SITE_DOMAIN
            else:
                domain = 'localhost:8000'
                
            site = Site.objects.create(
                id=settings.SITE_ID,
                domain=domain,
                name=getattr(settings, 'SITE_NAME', 'MyGiftTree')
            )
            self.stdout.write(self.style.SUCCESS(f'  ✅ Created Site (ID: {site.id})'))
            self.stdout.write(f'     Domain: {site.domain}')
            self.stdout.write(f'     Name: {site.name}')

        # Step 2: Check Google credentials
        self.stdout.write('\nStep 2: Checking Google OAuth credentials...')
        google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
        google_client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')
        
        if not google_client_id or not google_client_secret:
            self.stdout.write(self.style.WARNING('  ⚠️ Google OAuth credentials not configured!'))
            self.stdout.write('     Please add the following to your .env file:')
            self.stdout.write('     GOOGLE_CLIENT_ID=your_client_id_here')
            self.stdout.write('     GOOGLE_CLIENT_SECRET=your_client_secret_here')
        else:
            self.stdout.write(self.style.SUCCESS('  ✅ Google OAuth credentials found'))
            self.stdout.write(f'     Client ID: {google_client_id[:30]}...')

        # Step 3: Show authorized redirect URIs
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Django Site configuration complete!'))
        self.stdout.write('='*60)
        self.stdout.write('\n📋 NEXT STEP: Add these Authorized Redirect URIs')
        self.stdout.write('   in your Google Cloud Console:')
        self.stdout.write('\n   https://console.cloud.google.com/apis/credentials')
        self.stdout.write('\n' + '-'*60)
        
        if hasattr(settings, 'SITE_DOMAIN'):
            domain = settings.SITE_DOMAIN
        else:
            domain = 'localhost:8000'
        
        if 'localhost' in domain:
            self.stdout.write(f'  • http://{domain}/accounts/google/login/callback/')
        else:
            self.stdout.write(f'  • https://{domain}/accounts/google/login/callback/')
            self.stdout.write(f'  • https://www.{domain}/accounts/google/login/callback/')
        
        self.stdout.write('-'*60)
        self.stdout.write('\n⚠️  IMPORTANT: The trailing slash (/) is REQUIRED!')
        self.stdout.write('='*60 + '\n')

