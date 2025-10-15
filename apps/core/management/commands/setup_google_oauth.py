from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Set up Google OAuth for social login'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            help='Google OAuth Client ID',
        )
        parser.add_argument(
            '--client-secret',
            type=str,
            help='Google OAuth Client Secret',
        )

    def handle(self, *args, **options):
        client_id = options.get('client_id')
        client_secret = options.get('client_secret')
        
        if not client_id or not client_secret:
            self.stdout.write(
                self.style.WARNING(
                    'Please provide Google OAuth credentials:\n'
                    'python manage.py setup_google_oauth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET'
                )
            )
            return
        
        # Get or create the site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': 'localhost:8000',
                'name': 'GiftTree'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created site: GiftTree'))
        else:
            self.stdout.write(self.style.SUCCESS('Using existing site: GiftTree'))
        
        # Create or update Google social app
        social_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': client_secret,
            }
        )
        
        if not created:
            social_app.client_id = client_id
            social_app.secret = client_secret
            social_app.save()
            self.stdout.write(self.style.SUCCESS('Updated Google OAuth app'))
        else:
            self.stdout.write(self.style.SUCCESS('Created Google OAuth app'))
        
        # Add site to social app
        social_app.sites.add(site)
        
        self.stdout.write(
            self.style.SUCCESS(
                'Google OAuth setup complete!\n'
                'You can now use Google login on your site.'
            )
        )
