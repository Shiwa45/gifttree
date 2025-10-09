from django.core.management.base import BaseCommand
from django.db import transaction
from apps.products.models import DeliveryLocation


class Command(BaseCommand):
    help = 'Update international delivery locations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Updating international delivery locations...'))

        with transaction.atomic():
            # Delete existing international locations
            DeliveryLocation.objects.filter(slug__startswith='international-').delete()
            self.stdout.write('Deleted old international locations')

            # Create new international locations
            international_locations = [
                {'name': 'USA', 'state': 'All States', 'country': 'United States', 'is_major_city': True, 'is_metro': False},
                {'name': 'UK', 'state': 'All Regions', 'country': 'United Kingdom', 'is_major_city': True, 'is_metro': False},
                {'name': 'UAE', 'state': 'All Emirates', 'country': 'United Arab Emirates', 'is_major_city': True, 'is_metro': False},
                {'name': 'Australia', 'state': 'All States', 'country': 'Australia', 'is_major_city': True, 'is_metro': False},
                {'name': 'Canada', 'state': 'All Provinces', 'country': 'Canada', 'is_major_city': True, 'is_metro': False},
                {'name': 'France', 'state': 'All Regions', 'country': 'France', 'is_major_city': True, 'is_metro': False},
                {'name': 'Singapore', 'state': 'All Districts', 'country': 'Singapore', 'is_major_city': True, 'is_metro': False},
                {'name': 'Malaysia', 'state': 'All States', 'country': 'Malaysia', 'is_major_city': True, 'is_metro': False},
                {'name': 'Qatar', 'state': 'All Municipalities', 'country': 'Qatar', 'is_major_city': True, 'is_metro': False},
                {'name': 'South Africa', 'state': 'All Provinces', 'country': 'South Africa', 'is_major_city': True, 'is_metro': False},
                {'name': 'Sweden', 'state': 'All Regions', 'country': 'Sweden', 'is_major_city': True, 'is_metro': False},
            ]

            for i, location_data in enumerate(international_locations):
                location = DeliveryLocation.objects.create(
                    name=location_data['name'],
                    slug=f"international-{location_data['name'].lower().replace(' ', '-')}",
                    state=location_data['state'],
                    country=location_data['country'],
                    is_major_city=location_data['is_major_city'],
                    is_metro=location_data['is_metro'],
                    sort_order=i + 1,
                )
                self.stdout.write(f'Created: {location.name}')

        self.stdout.write(self.style.SUCCESS('International locations updated successfully!'))
