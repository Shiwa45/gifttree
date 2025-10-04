# apps/products/management/commands/import_products.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.services.csv_importer import CSVImporter
from apps.products.models import Product
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Import products from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file'
        )
        parser.add_argument(
            '--type',
            type=str,
            default='auto',
            choices=['auto', 'shopify', 'gift_tree'],
            help='CSV format type (default: auto)'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset database before importing'
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        file_type = options['type']
        reset = options['reset']

        # Check if file exists
        if not os.path.exists(csv_file_path):
            self.stdout.write(
                self.style.ERROR(f'❌ File not found: {csv_file_path}')
            )
            return

        # Reset database if requested
        if reset:
            self.stdout.write(self.style.WARNING('⚠️  Resetting database...'))
            confirm = input('Type "yes" to confirm database reset: ')
            if confirm.lower() == 'yes':
                Product.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('✓ Database reset complete'))
            else:
                self.stdout.write(self.style.WARNING('Database reset cancelled'))
                return

        # Get or create a system user for imports
        user, _ = User.objects.get_or_create(
            username='system_import',
            defaults={
                'is_staff': True,
                'email': 'system@gifttree.com'
            }
        )

        # Open and import file
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('📁 Importing from: ' + csv_file_path))
        self.stdout.write(self.style.HTTP_INFO(f'📋 Format: {file_type}'))
        self.stdout.write('')

        with open(csv_file_path, 'rb') as f:
            importer = CSVImporter(
                user=user,
                file_obj=f,
                file_type=file_type
            )
            result = importer.import_csv()

        # Display results
        self.stdout.write('')
        self.stdout.write('=' * 60)
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✓ Import completed successfully!')
            )
            self.stdout.write('')
            self.stdout.write(f"  📦 Products created: {result['created']}")
            self.stdout.write(f"  🔄 Products updated: {result['updated']}")
            self.stdout.write(f"  📊 Total products: {Product.objects.count()}")
            
            if result['errors']:
                self.stdout.write('')
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  {len(result['errors'])} errors occurred:"
                    )
                )
                for error in result['errors'][:10]:  # Show first 10 errors
                    self.stdout.write(f"  • {error}")
                if len(result['errors']) > 10:
                    self.stdout.write(
                        self.style.WARNING(f"  ... and {len(result['errors']) - 10} more errors")
                    )
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Import failed: {result["error"]}')
            )
        self.stdout.write('=' * 60)
        self.stdout.write('')


# Usage examples in comments:
"""
USAGE EXAMPLES:

# Import with auto-detection
python manage.py import_products "path/to/products.csv"

# Import Shopify format
python manage.py import_products "path/to/shopify_export.csv" --type shopify

# Import Gift Tree format
python manage.py import_products "path/to/gifttree_export.csv" --type gift_tree

# Reset database and import
python manage.py import_products "path/to/products.csv" --reset

# Import your actual CSV files:
python manage.py import_products "My Gift Tree  Exported Products 1.csv" --type gift_tree
python manage.py import_products "products_export_1 5.csv" --type shopify
python manage.py import_products "products_export_1 1.csv" --type shopify
"""