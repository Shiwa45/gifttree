from django.core.management.base import BaseCommand
from django.contrib.sitemaps import Sitemap
from django.test import RequestFactory
from django.contrib.sitemaps.views import sitemap, index
from apps.core.sitemaps import sitemaps
import requests
from django.conf import settings


class Command(BaseCommand):
    help = 'Generate and test sitemap'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test sitemap URLs',
        )
        parser.add_argument(
            '--count',
            action='store_true',
            help='Count URLs in each sitemap section',
        )

    def handle(self, *args, **options):
        if options['test']:
            self.test_sitemap()
        elif options['count']:
            self.count_urls()
        else:
            self.generate_sitemap()

    def generate_sitemap(self):
        """Generate sitemap and show statistics"""
        self.stdout.write(self.style.SUCCESS('Generating sitemap...'))
        
        factory = RequestFactory()
        request = factory.get('/sitemap.xml')
        
        # Generate main sitemap index
        response = index(request, sitemaps)
        self.stdout.write(f"Sitemap index generated: {response.status_code}")
        
        # Generate individual sitemaps
        for name, sitemap_class in sitemaps.items():
            try:
                sitemap_instance = sitemap_class()
                items = sitemap_instance.items()
                count = len(items) if hasattr(items, '__len__') else 'N/A'
                self.stdout.write(f"  {name}: {count} URLs")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  {name}: Error - {e}"))
        
        self.stdout.write(self.style.SUCCESS('Sitemap generation completed!'))

    def count_urls(self):
        """Count URLs in each sitemap section"""
        self.stdout.write(self.style.SUCCESS('Counting URLs in sitemap sections...'))
        
        total_urls = 0
        for name, sitemap_class in sitemaps.items():
            try:
                sitemap_instance = sitemap_class()
                items = sitemap_instance.items()
                count = len(items) if hasattr(items, '__len__') else 'N/A'
                total_urls += count if isinstance(count, int) else 0
                self.stdout.write(f"  {name}: {count} URLs")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  {name}: Error - {e}"))
        
        self.stdout.write(self.style.SUCCESS(f'Total URLs: {total_urls}'))

    def test_sitemap(self):
        """Test sitemap URLs"""
        self.stdout.write(self.style.SUCCESS('Testing sitemap URLs...'))
        
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        
        # Test main sitemap
        try:
            response = requests.get(f"{base_url}/sitemap.xml", timeout=10)
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✓ Main sitemap.xml accessible'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Main sitemap.xml returned {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Main sitemap.xml error: {e}'))
        
        # Test individual sitemaps
        for name in sitemaps.keys():
            try:
                response = requests.get(f"{base_url}/sitemap-{name}.xml", timeout=10)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f'✓ sitemap-{name}.xml accessible'))
                else:
                    self.stdout.write(self.style.ERROR(f'✗ sitemap-{name}.xml returned {response.status_code}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ sitemap-{name}.xml error: {e}'))
        
        # Test robots.txt
        try:
            response = requests.get(f"{base_url}/robots.txt", timeout=10)
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✓ robots.txt accessible'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ robots.txt returned {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ robots.txt error: {e}'))
