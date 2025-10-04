# apps/products/services/csv_importer_fixed.py
# FIXED VERSION - handles images properly

import csv
import io
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from apps.products.models import Product, ProductImage, ProductVariant, Category, CSVImportLog


class CSVImporter:
    """Handles CSV import for both Shopify and Gift Tree formats"""

    def __init__(self, user, file_obj, file_type='auto'):
        self.user = user
        self.file_obj = file_obj
        self.file_type = file_type
        self.errors = []
        self.products_created = 0
        self.products_updated = 0
        self.images_added = 0
        self.import_log = None

    def detect_csv_type(self, headers):
        """Detect CSV type based on column headers"""
        headers_lower = [h.lower().strip() for h in headers]

        if 'handle' in headers_lower and 'image src' in headers_lower:
            return 'shopify'
        elif 'sku' in headers_lower and 'image1' in headers_lower:
            return 'gift_tree'
        else:
            return 'unknown'

    def safe_decimal(self, value, default=0):
        """Safely convert value to Decimal"""
        if value is None or value == '':
            return Decimal(default)
        try:
            return Decimal(str(value).strip())
        except (InvalidOperation, ValueError):
            return Decimal(default)

    def safe_int(self, value, default=0):
        """Safely convert value to integer"""
        if value is None or value == '':
            return default
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return default

    def safe_bool(self, value, default=False):
        """Safely convert value to boolean"""
        if value is None or value == '':
            return default
        if isinstance(value, bool):
            return value
        value_str = str(value).lower().strip()
        return value_str in ['true', '1', 'yes', 'y', 't']

    def get_or_create_category(self, category_name):
        """Get or create category by name"""
        if not category_name:
            return None
        category, _ = Category.objects.get_or_create(
            name=category_name.strip()
        )
        return category

    def import_csv(self):
        """Main import method"""
        try:
            # Read CSV file
            content = self.file_obj.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))

            # Get headers and detect type
            headers = csv_reader.fieldnames
            if self.file_type == 'auto':
                self.file_type = self.detect_csv_type(headers)

            if self.file_type == 'unknown':
                raise ValueError("Unable to detect CSV format")

            # Create import log
            self.import_log = CSVImportLog.objects.create(
                uploaded_by=self.user,
                filename=getattr(self.file_obj, 'name', 'unknown.csv'),
                file_type=self.file_type,
                status='processing'
            )

            # Process based on type
            if self.file_type == 'shopify':
                self.import_shopify_csv(csv_reader)
            elif self.file_type == 'gift_tree':
                self.import_gift_tree_csv(csv_reader)

            # Update import log
            self.import_log.products_created = self.products_created
            self.import_log.products_updated = self.products_updated
            self.import_log.errors = "\n".join(self.errors) if self.errors else None
            self.import_log.status = 'completed'
            self.import_log.completed_at = timezone.now()
            self.import_log.save()

            return {
                'success': True,
                'created': self.products_created,
                'updated': self.products_updated,
                'images_added': self.images_added,
                'errors': self.errors,
                'import_log_id': self.import_log.id
            }

        except Exception as e:
            if self.import_log:
                self.import_log.status = 'failed'
                self.import_log.errors = str(e)
                self.import_log.completed_at = timezone.now()
                self.import_log.save()

            return {
                'success': False,
                'error': str(e),
                'created': self.products_created,
                'updated': self.products_updated,
                'errors': self.errors
            }

    @transaction.atomic
    def import_gift_tree_csv(self, csv_reader):
        """Import Gift Tree format CSV"""
        rows = list(csv_reader)
        self.import_log.total_rows = len(rows)
        self.import_log.save()

        for idx, row in enumerate(rows, 1):
            try:
                sku = row.get('SKU', '').strip()
                if not sku:
                    continue

                # Use Common Product Id as unique identifier (multiple SKUs per product for variants)
                common_product_id = row.get('Common Product Id', '').strip()
                product_name = row.get('Name', '').strip()

                # Generate unique slug
                base_slug = slugify(product_name) if product_name else sku.lower()
                unique_slug = base_slug
                counter = 1

                # Check slug uniqueness (exclude products with same common_product_id)
                while Product.objects.filter(slug=unique_slug).exists():
                    existing = Product.objects.filter(slug=unique_slug).first()
                    if existing and common_product_id and existing.common_product_id == common_product_id:
                        break
                    unique_slug = f"{base_slug}-{counter}"
                    counter += 1

                # Get or create product by Common Product Id
                if common_product_id:
                    product, created = Product.objects.get_or_create(
                        common_product_id=common_product_id,
                        defaults={
                            'sku': sku,
                            'name': product_name,
                            'slug': unique_slug,
                        }
                    )
                else:
                    # No common_product_id, use SKU
                    product, created = Product.objects.get_or_create(
                        sku=sku,
                        defaults={
                            'name': product_name,
                            'slug': unique_slug,
                        }
                    )

                if created:
                    print(f"Created: {product_name}")
                    self.products_created += 1
                else:
                    self.products_updated += 1

                # Update product fields
                product.name = product_name
                product.description = row.get('Description', '')
                product.summary = row.get('Summary', '')

                # Pricing
                product.sale_price = self.safe_decimal(row.get('Sale Price'))
                product.base_price = product.sale_price
                product.mrp = self.safe_decimal(row.get('MRP'))
                product.purchase_price = self.safe_decimal(row.get('Purchase Price'))
                product.sale_price_tax_included = self.safe_bool(row.get('Sale Price Tax Included'), True)
                product.purchase_price_tax_included = self.safe_bool(row.get('Purchase Price Tax Included'), True)
                product.tax_rate = self.safe_decimal(row.get('Tax'), None)

                # Category
                category_name = row.get('Category', '').strip()
                if category_name:
                    product.category = self.get_or_create_category(category_name)
                product.sub_category = row.get('Sub Category', '')

                # Inventory
                product.quantity = self.safe_int(row.get('Quantity'))
                product.stock_quantity = product.quantity
                product.min_quantity = self.safe_int(row.get('Min Quantity'))
                product.max_quantity = self.safe_int(row.get('Max Quantity'))

                # Physical attributes
                product.weight = self.safe_decimal(row.get('Shipping Weight'))
                product.size = row.get('Size', '')
                product.color = row.get('Color', '')
                product.material = row.get('Material', '')
                product.brand = row.get('Brand', '')

                # Other attributes
                product.barcode = row.get('Barcode', '')
                product.hsn = row.get('HSN', '')
                product.gtin = row.get('GTIN', '')
                product.mpn = row.get('MPN', '')

                # SEO
                product.seo_title = row.get('SEO Title', '')
                product.meta_title = row.get('SEO Title', '')
                product.seo_description = row.get('SEO Description', '')
                product.meta_description = row.get('SEO Description', '')
                product.video_url = row.get('Video Url', '')

                # Status
                product.show_online = self.safe_bool(row.get('Show Online'), True)
                product.published = self.safe_bool(row.get('Show Online'), True)
                product.is_active = True
                product.status = 'active'

                product.save()

                print(f"  Processing images for: {product.name}")
                # Handle images - ADD THEM!
                self._process_gift_tree_images(product, row)

            except Exception as e:
                import traceback
                error_msg = f"Row {idx}: {str(e)}\n{traceback.format_exc()}"
                print(f"ERROR: {error_msg}")
                self.errors.append(error_msg)

    def _process_gift_tree_images(self, product, row):
        """Process images for Gift Tree format"""
        print(f"    _process_gift_tree_images called for product: {product.id}")

        # Get existing image URLs to avoid duplicates
        existing_urls = set(product.images.values_list('image_url', flat=True))
        print(f"    Existing images: {len(existing_urls)}")

        # Process Image1 to Image6
        for i in range(1, 7):
            image_url = row.get(f'Image{i}', '').strip()
            print(f"    Image{i} = '{image_url[:80] if image_url else 'EMPTY'}'")

            if image_url and image_url not in existing_urls:
                # Add new image
                existing_count = product.images.count()
                print(f"    Creating ProductImage: position={existing_count + 1}, is_primary={existing_count == 0}")

                ProductImage.objects.create(
                    product=product,
                    image_url=image_url,
                    position=existing_count + 1,
                    sort_order=existing_count + 1,
                    is_primary=(existing_count == 0),
                    is_active=True
                )
                existing_urls.add(image_url)
                self.images_added += 1
                print(f"    ✓ Added image {i}: {image_url[:60]}")
            elif image_url and image_url in existing_urls:
                print(f"    ⊗ Skipped (duplicate): {image_url[:60]}")

    @transaction.atomic
    def import_shopify_csv(self, csv_reader):
        """Import Shopify format CSV - with images"""
        rows = list(csv_reader)
        self.import_log.total_rows = len(rows)
        self.import_log.save()

        # Group rows by Handle
        products_data = {}
        for row in rows:
            handle = row.get('Handle', '').strip()
            if not handle:
                continue

            if handle not in products_data:
                products_data[handle] = {
                    'main': row,
                    'rows': []
                }
            products_data[handle]['rows'].append(row)

        # Process each product
        for idx, (handle, data) in enumerate(products_data.items(), 1):
            try:
                main_row = data['main']
                product_name = main_row.get('Title', '').strip()

                # SKU
                sku = main_row.get('Variant SKU', '').strip()
                if not sku:
                    sku = f"SHOPIFY-{handle}"

                # Generate unique slug
                base_slug = handle
                unique_slug = base_slug
                counter = 1
                while Product.objects.filter(slug=unique_slug).exists():
                    existing = Product.objects.filter(slug=unique_slug).first()
                    if existing and existing.handle == handle:
                        break
                    unique_slug = f"{base_slug}-{counter}"
                    counter += 1

                # Get or create
                product, created = Product.objects.get_or_create(
                    handle=handle,
                    defaults={
                        'sku': sku,
                        'name': product_name,
                        'slug': unique_slug,
                    }
                )

                if created:
                    print(f"Created: {product_name}")
                    self.products_created += 1
                else:
                    self.products_updated += 1

                # Update fields
                product.name = product_name
                product.body_html = main_row.get('Body (HTML)', '')
                product.description = main_row.get('Body (HTML)', '')
                product.vendor = main_row.get('Vendor', '')
                product.product_type = main_row.get('Type', '')
                product.tags = main_row.get('Tags', '')

                # Category
                category_name = main_row.get('Type', '').strip()
                if category_name:
                    product.category = self.get_or_create_category(category_name)

                # Pricing
                product.sale_price = self.safe_decimal(main_row.get('Variant Price'))
                product.base_price = product.sale_price
                product.compare_at_price = self.safe_decimal(main_row.get('Variant Compare At Price'), None)
                product.cost_per_item = self.safe_decimal(main_row.get('Cost per item'), None)

                # Inventory
                product.quantity = self.safe_int(main_row.get('Variant Inventory Qty'))
                product.stock_quantity = product.quantity

                # Status
                product.published = self.safe_bool(main_row.get('Published'), True)
                product.status = main_row.get('Status', 'active')
                product.is_active = product.status == 'active'

                product.save()

                # Process images
                self._process_shopify_images(product, data['rows'])

            except Exception as e:
                import traceback
                error_msg = f"Handle {handle}: {str(e)}\n{traceback.format_exc()}"
                print(f"ERROR: {error_msg}")
                self.errors.append(error_msg)

    def _process_shopify_images(self, product, rows):
        """Process images for Shopify format"""
        existing_urls = set(product.images.values_list('image_url', flat=True))

        for row in rows:
            image_src = row.get('Image Src', '').strip()
            if image_src and image_src not in existing_urls:
                existing_count = product.images.count()
                ProductImage.objects.create(
                    product=product,
                    image_url=image_src,
                    position=existing_count + 1,
                    sort_order=existing_count + 1,
                    alt_text=row.get('Image Alt Text', ''),
                    is_primary=(existing_count == 0),
                    is_active=True
                )
                existing_urls.add(image_src)
                self.images_added += 1
                print(f"  ✓ Added image: {image_src[:60]}")
