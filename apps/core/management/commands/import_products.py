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
                    # Get or create category with smart categorization
                    category_name = row.get('Type', '').strip()

                    # Smart categorization based on product name if category is empty
                    if not category_name and title:
                        name_lower = title.lower()

                        # Cake-related keywords
                        if any(word in name_lower for word in ['cake', 'pastry', 'truffle', 'fondant', 'cupcake', 'bento', 'pinata']):
                            category_name = 'Cakes'
                        # Plant-related keywords
                        elif any(word in name_lower for word in ['plant', 'bamboo', 'bonsai', 'terrarium', 'succulent', 'indoor', 'fern', 'palm', 'jade', 'money plant']):
                            category_name = 'Plants'
                        # Flower-related keywords
                        elif any(word in name_lower for word in ['flower', 'rose', 'orchid', 'lily', 'tulip', 'bouquet', 'carnation', 'gerbera', 'chrysanthemum']):
                            category_name = 'Flowers'
                        # Chocolate and sweets
                        elif any(word in name_lower for word in ['chocolate', 'ferrero', 'cadbury', 'lindt', 'toblerone', 'candy', 'sweet']):
                            category_name = 'Chocolates & Sweets'
                        # Gift hampers and combos
                        elif any(word in name_lower for word in ['hamper', 'combo', 'basket', 'gift box', 'gift set']):
                            category_name = 'Gift Hampers'
                        # Personalized items
                        elif any(word in name_lower for word in ['personalized', 'customized', 'custom', 'photo', 'name', 'engraved']):
                            category_name = 'Personalized Gifts'
                        # Home decor
                        elif any(word in name_lower for word in ['showpiece', 'decor', 'decorative', 'figurine', 'statue', 'wall', 'frame']):
                            category_name = 'Home Decor'
                        # Jewelry and accessories
                        elif any(word in name_lower for word in ['jewellery', 'jewelry', 'bracelet', 'necklace', 'ring', 'earring', 'pendant']):
                            category_name = 'Jewelry & Accessories'
                        # Clothing and apparel
                        elif any(word in name_lower for word in ['t-shirt', 'tshirt', 'shirt', 'hoodie', 'sweatshirt', 'jacket', 'cap', 'dress']):
                            category_name = 'Clothing & Apparel'
                        # Mugs and drinkware
                        elif any(word in name_lower for word in ['mug', 'cup', 'sipper', 'bottle', 'flask', 'tumbler']):
                            category_name = 'Mugs & Drinkware'
                        # Toys and games
                        elif any(word in name_lower for word in ['toy', 'teddy', 'soft toy', 'plush', 'game', 'puzzle']):
                            category_name = 'Toys & Games'
                        else:
                            category_name = 'Uncategorized'
                    elif not category_name:
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
        """Import MyGiftTree format CSV with variant support"""
        self.stdout.write('Importing MyGiftTree format...')

        # Read all rows
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)

        # Group rows by Common Product Id
        products_data = {}
        for row in all_rows:
            common_id = row.get('Common Product Id', '').strip()
            if common_id and row.get('Show Online', '').upper() == 'TRUE':
                if common_id not in products_data:
                    products_data[common_id] = []
                products_data[common_id].append(row)

        products_created = 0
        products_updated = 0
        images_added = 0
        variants_created = 0

        # Process each unique product
        for common_id, product_rows in products_data.items():
            try:
                # Use first row as master data
                master_row = product_rows[0]

                name = master_row.get('Name', '').strip()
                if not name:
                    continue

                # Get or create category with smart categorization
                category_name = master_row.get('Category', '').strip()

                # Smart categorization based on product name if category is empty
                if not category_name:
                    name_lower = name.lower()

                    # Cake-related keywords
                    if any(word in name_lower for word in ['cake', 'pastry', 'truffle', 'fondant', 'cupcake', 'bento', 'pinata']):
                        category_name = 'Cakes'
                    # Plant-related keywords
                    elif any(word in name_lower for word in ['plant', 'bamboo', 'bonsai', 'terrarium', 'succulent', 'indoor', 'fern', 'palm', 'jade', 'money plant']):
                        category_name = 'Plants'
                    # Flower-related keywords
                    elif any(word in name_lower for word in ['flower', 'rose', 'orchid', 'lily', 'tulip', 'bouquet', 'carnation', 'gerbera', 'chrysanthemum']):
                        category_name = 'Flowers'
                    # Chocolate and sweets
                    elif any(word in name_lower for word in ['chocolate', 'ferrero', 'cadbury', 'lindt', 'toblerone', 'candy', 'sweet']):
                        category_name = 'Chocolates & Sweets'
                    # Gift hampers and combos
                    elif any(word in name_lower for word in ['hamper', 'combo', 'basket', 'gift box', 'gift set']):
                        category_name = 'Gift Hampers'
                    # Personalized items
                    elif any(word in name_lower for word in ['personalized', 'customized', 'custom', 'photo', 'name', 'engraved']):
                        category_name = 'Personalized Gifts'
                    # Home decor
                    elif any(word in name_lower for word in ['showpiece', 'decor', 'decorative', 'figurine', 'statue', 'wall', 'frame']):
                        category_name = 'Home Decor'
                    # Jewelry and accessories
                    elif any(word in name_lower for word in ['jewellery', 'jewelry', 'bracelet', 'necklace', 'ring', 'earring', 'pendant']):
                        category_name = 'Jewelry & Accessories'
                    # Clothing and apparel
                    elif any(word in name_lower for word in ['t-shirt', 'tshirt', 'shirt', 'hoodie', 'sweatshirt', 'jacket', 'cap', 'dress']):
                        category_name = 'Clothing & Apparel'
                    # Mugs and drinkware
                    elif any(word in name_lower for word in ['mug', 'cup', 'sipper', 'bottle', 'flask', 'tumbler']):
                        category_name = 'Mugs & Drinkware'
                    # Toys and games
                    elif any(word in name_lower for word in ['toy', 'teddy', 'soft toy', 'plush', 'game', 'puzzle']):
                        category_name = 'Toys & Games'
                    else:
                        category_name = 'Uncategorized'

                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={
                        'slug': slugify(category_name),
                        'description': f'{category_name} products'
                    }
                )

                # Get base prices (use first variant's prices as base)
                try:
                    sale_price = Decimal(str(master_row.get('Sale Price', 0) or 0))
                    mrp = Decimal(str(master_row.get('MRP', 0) or 0))
                except:
                    sale_price = Decimal('0.00')
                    mrp = Decimal('0.00')

                # Create or update product by Common Product Id
                product, created = Product.objects.get_or_create(
                    common_product_id=common_id,
                    defaults={
                        'sku': master_row.get('SKU', f'SKU-{slugify(name)}').strip(),
                        'name': name,
                        'slug': slugify(name),
                        'category': category,
                        'description': master_row.get('Description', name) or name,
                        'base_price': mrp or sale_price,
                        'discount_price': sale_price if mrp and sale_price < mrp else None,
                        'stock_quantity': int(float(master_row.get('Quantity', 0) or 0)),
                        'is_active': True,
                        'meta_title': name[:160],
                        'meta_description': (master_row.get('SEO Description') or name)[:320],
                    }
                )

                if created:
                    products_created += 1
                    self.stdout.write(f'Created: {name}')
                else:
                    products_updated += 1

                # Handle images (only once per product, not per variant)
                if created or product.images.count() == 0:
                    for i in range(1, 7):
                        image_url = master_row.get(f'Image{i}', '').strip()
                        if image_url:
                            if not ProductImage.objects.filter(product=product, image_url=image_url).exists():
                                ProductImage.objects.create(
                                    product=product,
                                    image_url=image_url,
                                    position=i,
                                    sort_order=i,
                                    is_primary=(i == 1),
                                    is_active=True
                                )
                                images_added += 1

                # Create variants for each row (Size/Weight options)
                for variant_row in product_rows:
                    size = variant_row.get('Size', '').strip()
                    sku = variant_row.get('SKU', '').strip()

                    if size:
                        try:
                            variant_price = Decimal(str(variant_row.get('Sale Price', 0) or 0))
                            variant_mrp = Decimal(str(variant_row.get('MRP', 0) or 0))
                            variant_stock = int(float(variant_row.get('Quantity', 0) or 0))
                        except:
                            variant_price = Decimal('0.00')
                            variant_mrp = Decimal('0.00')
                            variant_stock = 0

                        # Create or update variant
                        variant, variant_created = ProductVariant.objects.get_or_create(
                            product=product,
                            variant_sku=sku,
                            defaults={
                                'name': size,
                                'option1_name': 'Size',
                                'option1_value': size,
                                'price': variant_price,
                                'compare_at_price': variant_mrp if variant_mrp > variant_price else None,
                                'inventory_quantity': variant_stock,
                                'stock_quantity': variant_stock,
                                'is_active': True,
                            }
                        )

                        if variant_created:
                            variants_created += 1
                            print(f"  ✓ Added variant: {size} - Rs.{variant_price}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing product {common_id}: {str(e)}'))
                import traceback
                traceback.print_exc()
                continue

        self.stdout.write(self.style.SUCCESS(
            f'\nImport complete!\n'
            f'Products created: {products_created}\n'
            f'Products updated: {products_updated}\n'
            f'Variants created: {variants_created}\n'
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