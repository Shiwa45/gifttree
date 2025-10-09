from django.core.management.base import BaseCommand
from apps.core.models import Country


class Command(BaseCommand):
    help = 'Populate countries data for international delivery'

    def handle(self, *args, **options):
        countries_data = [
            {'name': 'United Kingdom', 'code': 'UK', 'is_featured': True, 'sort_order': 1},
            {'name': 'United States', 'code': 'USA', 'is_featured': True, 'sort_order': 2},
            {'name': 'Canada', 'code': 'CAN', 'is_featured': True, 'sort_order': 3},
            {'name': 'Australia', 'code': 'AUS', 'is_featured': True, 'sort_order': 4},
            {'name': 'United Arab Emirates', 'code': 'UAE', 'is_featured': True, 'sort_order': 5},
            {'name': 'Singapore', 'code': 'SGP', 'is_featured': True, 'sort_order': 6},
            {'name': 'Japan', 'code': 'JPN', 'is_featured': False, 'sort_order': 7},
            {'name': 'Germany', 'code': 'DEU', 'is_featured': False, 'sort_order': 8},
            {'name': 'France', 'code': 'FRA', 'is_featured': False, 'sort_order': 9},
            {'name': 'India', 'code': 'IND', 'is_featured': True, 'sort_order': 0},
        ]

        created_count = 0
        updated_count = 0

        for data in countries_data:
            country, created = Country.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {country.name} ({country.code})')
                )
            else:
                # Update existing
                for key, value in data.items():
                    setattr(country, key, value)
                country.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated: {country.name} ({country.code})')
                )

        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'Summary: {created_count} created, {updated_count} updated')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total countries: {Country.objects.count()}')
        )
