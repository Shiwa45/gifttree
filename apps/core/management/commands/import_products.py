"""
Django management command to import products from CSV files
Usage: python manage.py import_products <csv_file_path>
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.products.models import Product, Category, ProductImage, ProductVariant
from apps.core.models import SiteSettings
import csv
import requests
from decimal import Decimal
from django.utils.text import slugify
from django.core.files.base import ContentFile
import os
from urllib.parse import urlparse


class Command(BaseCommand):
    help = 'Import products from CSV file (supports Shopify and MyGiftTree formats)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument(
            '--format',
            type=str,
            choices=['shopify', 'mygifttree', 'auto'],
            default='auto',
            help='CSV format (auto-detect by default)'
        )
        parser.add_argument(
            '--download-images',
            action='store_true',
            help='Download product images from URLs'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        file_format = options['format']
        download_images = options['download_images']

        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Starting import from: {csv_file}'))

        # Auto-detect format
        if file_format == 'auto':
            file_format = self.detect_format(csv_file)
            self.stdout.write(f'Detected format: {file_format}')

        # Import based on format
        if file_format == 'shopify':
            self.import_shopify_format(csv_file, download_images)
        elif file_format == 'mygifttree':
            self.import_mygifttree_format(csv_file, download_images)
        else:
            self.stdout.write(self.style.ERROR('Unknown format'))

    def detect_format(self, csv_file):
        """Auto-detect CSV format"""
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            if 'Handle' in headers and 'Vendor' in headers:
                return 'shopify'
            elif 'Common Product Id' in headers and 'Show Online' in headers:
                return 'mygifttree'
            
        return 'unknown'

    @transaction.atomic
    def import_shopify_format(self, csv_file, download_images):
        """Import Shopify format CSV"""
        self.stdout.write('Importing Shopify format...')
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            current_product = None
            products_created = 0
            products_updated = 0
            images_added = 0
            
            for row in reader:
                try:
                    # Get or create category
                    category_name = row.get('Type', 'Uncategorized').strip()
                    if not category_name:
                        category_name = 'Uncategorized'
                    
                    category, _ = Category.objects.get_or_create(
                        name=category_name,
                        defaults={
                            'slug': slugify(category_name),
                            'description': f'{category_name} products'
                        }
                    )

                    # Check if this is a new product row or variant row
                    handle = row.get('Handle', '').strip()
                    title = row.get('Title', '').strip()
                    
                    if handle and title:  # New product
                        # Get price
                        try:
                            price = Decimal(str(row.get('Variant Price', 0) or 0))
                            compare_price = row.get('Variant Compare At Price', '')
                            compare_price = Decimal(str(compare_price)) if compare_price else None
                        except:
                            price = Decimal('0.00')
                            compare_price = None

                        # Create or update product
                        product, created = Product.objects.update_or_create(
                            sku=row.get('Variant SKU', f'SKU-{handle}') or f'SKU-{handle}',
                            defaults={
                                'name': title,
                                'slug': slugify(title),
                                'category': category,
                                'description': self.clean_html(row.get('Body (HTML)', '')),
                                'base_price': compare_price or price,
                                'discount_price': price if compare_price and price < compare_price else None,
                                'stock_quantity': int(row.get('Variant Inventory Qty', 0) or 0),
                                'is_active': row.get('Status', 'active').lower() == 'active',
                                'meta_title': title[:160],
                                'meta_description': self.clean_html(row.get('Body (HTML)', ''))[:320],
                            }
                        )
                        
                        current_product = product
                        
                        if created:
                            products_created += 1
                            self.stdout.write(f'Created: {title}')
                        else:
                            products_updated += 1
                            self.stdout.write(f'Updated: {title}')

                        # Handle tags/occasions
                        tags = row.get('Tags', '').strip()
                        if tags:
                            self.process_tags(product, tags)

                        # Handle product image
                        image_src = row.get('Image Src', '').strip()
                        if image_src and download_images:
                            if self.download_product_image(product, image_src, 1):
                                images_added += 1

                    elif current_product:  # Variant or additional image
                        # Check for variant option
                        option1_value = row.get('Option1 Value', '').strip()
                        if option1_value:
                            # Create product variant
                            self.create_variant(current_product, option1_value, row)

                        # Check for additional images
                        image_src = row.get('Image Src', '').strip()
                        if image_src and download_images:
                            image_position = int(row.get('Image Position', 1) or 1)
                            if self.download_product_image(current_product, image_src, image_position):
                                images_added += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing row: {str(e)}'))
                    continue

        self.stdout.write(self.style.SUCCESS(
            f'\nImport complete!\n'
            f'Products created: {products_created}\n'
            f'Products updated: {products_updated}\n'
            f'Images added: {images_added}'
        ))

    @transaction.atomic
    def import_mygifttree_format(self, csv_file, download_images):
        """Import MyGiftTree format CSV"""
        self.stdout.write('Importing MyGiftTree format...')
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            products_created = 0
            products_updated = 0
            images_added = 0
            
            for row in reader:
                try:
                    # Skip if not to show online
                    show_online = str(row.get('Show Online', 'FALSE')).upper()
                    if show_online != 'TRUE':
                        continue

                    # Get or create category
                    category_name = row.get('Category', 'Uncategorized').strip()
                    if not category_name:
                        category_name = 'Uncategorized'
                    
                    category, _ = Category.objects.get_or_create(
                        name=category_name,
                        defaults={
                            'slug': slugify(category_name),
                            'description': f'{category_name} products'
                        }
                    )

                    # Get prices
                    try:
                        sale_price = Decimal(str(row.get('Sale Price', 0) or 0))
                        mrp = Decimal(str(row.get('MRP', 0) or 0))
                    except:
                        sale_price = Decimal('0.00')
                        mrp = Decimal('0.00')

                    # Get product name
                    name = row.get('Name', '').strip()
                    if not name:
                        continue

                    # Create or update product
                    sku = row.get('SKU', f'SKU-{slugify(name)}').strip()
                    
                    product, created = Product.objects.update_or_create(
                        sku=sku,
                        defaults={
                            'name': name,
                            'slug': slugify(name),
                            'category': category,
                            'description': row.get('Description', name) or name,
                            'base_price': mrp or sale_price,
                            'discount_price': sale_price if mrp and sale_price < mrp else None,
                            'stock_quantity': int(float(row.get('Quantity', 0) or 0)),
                            'is_active': True,
                            'meta_title': name[:160],
                            'meta_description': (row.get('SEO Description') or name)[:320],
                        }
                    )
                    
                    if created:
                        products_created += 1
                        self.stdout.write(f'Created: {name}')
                    else:
                        products_updated += 1
                        self.stdout.write(f'Updated: {name}')

                    # Handle variants (Size, Color)
                    size = row.get('Size', '').strip()
                    if size:
                        self.create_simple_variant(product, 'Size', size)

                    # Handle images
                    if download_images:
                        for i in range(1, 7):
                            image_url = row.get(f'Image{i}', '').strip()
                            if image_url:
                                if self.download_product_image(product, image_url, i):
                                    images_added += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing row: {str(e)}'))
                    continue

        self.stdout.write(self.style.SUCCESS(
            f'\nImport complete!\n'
            f'Products created: {products_created}\n'
            f'Products updated: {products_updated}\n'
            f'Images added: {images_added}'
        ))

    def create_variant(self, product, option_value, row):
        """Create product variant"""
        try:
            price_adjustment = Decimal('0.00')
            stock = int(row.get('Variant Inventory Qty', 0) or 0)
            
            ProductVariant.objects.get_or_create(
                product=product,
                name=option_value,
                defaults={
                    'price_adjustment': price_adjustment,
                    'stock_quantity': stock,
                    'sku_suffix': slugify(option_value)[:20],
                }
            )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error creating variant: {str(e)}'))

    def create_simple_variant(self, product, variant_type, variant_value):
        """Create simple variant"""
        try:
            ProductVariant.objects.get_or_create(
                product=product,
                name=f'{variant_type}: {variant_value}',
                defaults={
                    'price_adjustment': Decimal('0.00'),
                    'stock_quantity': product.stock_quantity,
                    'sku_suffix': slugify(variant_value)[:20],
                }
            )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error creating variant: {str(e)}'))

    def download_product_image(self, product, image_url, position):
        """Download and save product image"""
        try:
            # Check if image already exists
            if ProductImage.objects.filter(product=product, sort_order=position).exists():
                return False

            # Download image
            response = requests.get(image_url, timeout=10, stream=True)
            if response.status_code == 200:
                # Get filename from URL
                filename = os.path.basename(urlparse(image_url).path)
                if not filename:
                    filename = f'{product.slug}-{position}.jpg'

                # Create ProductImage
                product_image = ProductImage.objects.create(
                    product=product,
                    alt_text=product.name,
                    is_primary=(position == 1),
                    sort_order=position
                )

                # Save image
                product_image.image.save(
                    filename,
                    ContentFile(response.content),
                    save=True
                )

                return True
        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f'Error downloading image for {product.name}: {str(e)}'
            ))
        
        return False

    def process_tags(self, product, tags_string):
        """Process tags and create occasions"""
        from apps.products.models import Occasion
        
        tags = [tag.strip() for tag in tags_string.split(',')]
        for tag in tags:
            if tag:
                occasion, _ = Occasion.objects.get_or_create(
                    name=tag,
                    defaults={
                        'slug': slugify(tag),
                        'description': f'{tag} products'
                    }
                )
                product.occasions.add(occasion)

    def clean_html(self, html_text):
        """Clean HTML tags from text"""
        if not html_text:
            return ''
        
        import re
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', str(html_text))
        # Remove extra whitespace
        clean_text = ' '.join(clean_text.split())
        return clean_text[:1000]  # Limit length