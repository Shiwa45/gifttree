from django.core.management.base import BaseCommand
from apps.products.models import ProductAddOn


class Command(BaseCommand):
    help = 'Populate sample product add-ons with descriptions'

    def handle(self, *args, **options):
        addons_data = [
            {
                'name': 'Premium Dairy Milk Chocolate',
                'description': 'Delicious Cadbury Dairy Milk chocolate bar (100g) - Perfect sweet companion',
                'price': 120.00,
            },
            {
                'name': 'Personalized Greeting Card',
                'description': 'Beautiful greeting card with custom message and elegant design',
                'price': 80.00,
            },
            {
                'name': 'Cute Teddy Bear (Small)',
                'description': 'Adorable soft teddy bear (6 inches) - Makes every gift more special',
                'price': 250.00,
            },
            {
                'name': 'Ferrero Rocher (5 pcs)',
                'description': 'Premium Ferrero Rocher chocolates - 5 pieces in elegant packaging',
                'price': 299.00,
            },
            {
                'name': 'Scented Candles Set',
                'description': 'Set of 3 aromatic scented candles for a relaxing ambiance',
                'price': 350.00,
            },
            {
                'name': 'Decorative Gift Wrap',
                'description': 'Premium gift wrapping with ribbons and decorative elements',
                'price': 100.00,
            },
            {
                'name': 'Heart-Shaped Cushion',
                'description': 'Soft heart-shaped cushion with "Love You" message',
                'price': 399.00,
            },
            {
                'name': 'Small Photo Frame',
                'description': 'Elegant photo frame (6x4 inches) - Capture memories forever',
                'price': 199.00,
            },
        ]

        created_count = 0
        updated_count = 0

        for data in addons_data:
            addon, created = ProductAddOn.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {addon.name} - Rs.{addon.price}')
                )
            else:
                # Update existing
                for key, value in data.items():
                    setattr(addon, key, value)
                addon.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated: {addon.name} - Rs.{addon.price}')
                )

        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(f'Summary: {created_count} created, {updated_count} updated')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total add-ons: {ProductAddOn.objects.count()}')
        )
        self.stdout.write('\n' + self.style.WARNING('Note: Add-on images should be uploaded via Django Admin'))
        self.stdout.write(self.style.WARNING('      or placed in media/addons/ directory'))
