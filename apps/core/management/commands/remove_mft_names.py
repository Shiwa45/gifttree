from django.core.management.base import BaseCommand
from apps.products.models import Category


class Command(BaseCommand):
    help = 'Remove MFT prefix from category names'

    def handle(self, *args, **options):
        categories = Category.objects.filter(name__icontains='MFT')

        count = 0
        for category in categories:
            old_name = category.name
            new_name = category.name.replace('MFT', '').replace('mft', '').strip()

            if old_name != new_name:
                category.name = new_name
                category.save()
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Updated: "{old_name}" → "{new_name}"')
                )

        if count == 0:
            self.stdout.write(
                self.style.WARNING('No categories with MFT found')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {count} categories')
            )
