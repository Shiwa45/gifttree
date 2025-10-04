# apps/products/services/csv_importer.py

import csv
import io
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils import timezone
from apps.products.models import Product, ProductImage, ProductVariant, Category, CSVImportLog


class CSVImporter:
    """
    Handles CSV import for both Shopify and Gift Tree formats
    Integrated with GiftTree project structure
    """
    
    def __init__(self, user, file_obj, file_type='auto'):
        self.user = user
        self.file_obj = file_obj
        self.file_type = file_type
        self.errors = []
        self.products_created = 0
        self.products_updated = 0
        self.import_log = None
    
    def detect_csv_type(self, headers):
        """Detect CSV type based on column headers"""
        headers_lower = [h.lower().strip() for h in headers]
        
        if 'handle' in headers_lower and 'body (html)' in headers_lower:
            return 'shopify'
        elif 'sku' in headers_lower and 'common product id' in headers_lower:
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
                raise ValueError("Unable to detect CSV format. Please specify format manually.")
            
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
                    self.errors.append(f"Row {idx}: Missing SKU")
                    continue
                
                # Try to find existing product by SKU
                product = None
                created = False
                
                try:
                    product = Product.objects.get(sku=sku)
                    created = False
                except Product.DoesNotExist:
                    # Create new product with unique slug
                    product_name = row.get('Name', '').strip()
                    
                    # Generate unique slug from name
                    from django.utils.text import slugify
                    base_slug = slugify(product_name)
                    unique_slug = base_slug
                    counter = 1
                    
                    # Check if slug exists, if yes add number
                    while Product.objects.filter(slug=unique_slug).exists():
                        unique_slug = f"{base_slug}-{counter}"
                        counter += 1
                    
                    product = Product(
                        sku=sku,
                        name=product_name,
                        slug=unique_slug  # Unique slug
                    )
                    created = True
                
                # Update product fields
                product.common_product_id = row.get('Common Product Id', '')
                product.name = row.get('Name', '').strip()
                product.description = row.get('Description', '')
                product.summary = row.get('Summary', '')
                
                # Pricing
                product.sale_price = self.safe_decimal(row.get('Sale Price'))
                product.base_price = product.sale_price  # Sync with base_price
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
                product.stock_quantity = product.quantity  # Sync with stock_quantity
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
                product.meta_title = row.get('SEO Title', '')  # Sync
                product.seo_description = row.get('SEO Description', '')
                product.meta_description = row.get('SEO Description', '')  # Sync
                product.video_url = row.get('Video Url', '')
                
                # Status
                product.show_online = self.safe_bool(row.get('Show Online'), True)
                product.published = self.safe_bool(row.get('Show Online'), True)
                product.is_active = True
                product.status = 'active'
                
                product.save()
                
                # Handle images
                self._process_gift_tree_images(product, row)
                
                if created:
                    self.products_created += 1
                else:
                    self.products_updated += 1
                    
            except Exception as e:
                self.errors.append(f"Row {idx} (SKU: {row.get('SKU', 'N/A')}): {str(e)}")
    
    def _process_gift_tree_images(self, product, row):
        """Process images for Gift Tree format"""
        # Clear existing images if reimporting
        product.images.all().delete()
        
        # Process Image1 to Image6
        for i in range(1, 7):
            image_url = row.get(f'Image{i}', '').strip()
            if image_url:
                ProductImage.objects.create(
                    product=product,
                    image_url=image_url,
                    position=i,
                    sort_order=i,
                    is_primary=(i == 1),
                    is_active=True
                )
    
    @transaction.atomic
    def import_shopify_csv(self, csv_reader):
        """Import Shopify format CSV"""
        rows = list(csv_reader)
        self.import_log.total_rows = len(rows)
        self.import_log.save()
        
        # Group rows by Handle (each product can have multiple rows for variants/images)
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
                
                # Use SKU or generate one from handle
                sku = main_row.get('Variant SKU', '').strip()
                if not sku:
                    sku = f"SHOPIFY-{handle}"
                
                # Try to find existing product by SKU
                product = None
                created = False
                
                try:
                    product = Product.objects.get(sku=sku)
                    created = False
                except Product.DoesNotExist:
                    # Create new product
                    product_name = main_row.get('Title', '').strip()
                    
                    # Generate unique slug from handle
                    base_slug = handle
                    unique_slug = base_slug
                    counter = 1
                    
                    # Check if slug exists, if yes add number
                    while Product.objects.filter(slug=unique_slug).exists():
                        unique_slug = f"{base_slug}-{counter}"
                        counter += 1
                    
                    # Create product with unique slug
                    product = Product(
                        sku=sku,
                        name=product_name,
                        handle=handle,
                        slug=unique_slug  # This will be unique
                    )
                    created = True
                
                # Update product fields (don't change slug once set!)
                product.handle = handle
                product.name = main_row.get('Title', '').strip()
                product.body_html = main_row.get('Body (HTML)', '')
                product.description = main_row.get('Body (HTML)', '')  # Sync
                product.vendor = main_row.get('Vendor', '')
                product.product_type = main_row.get('Type', '')
                product.tags = main_row.get('Tags', '')
                
                # Category
                category_name = main_row.get('Type', '').strip()
                if category_name:
                    product.category = self.get_or_create_category(category_name)
                
                # Pricing (use first row's prices)
                product.sale_price = self.safe_decimal(main_row.get('Variant Price'))
                product.base_price = product.sale_price  # Sync
                product.compare_at_price = self.safe_decimal(main_row.get('Variant Compare At Price'), None)
                product.discount_price = product.compare_at_price  # Sync
                product.cost_per_item = self.safe_decimal(main_row.get('Cost per item'), None)
                
                # Weight
                product.weight = self.safe_decimal(main_row.get('Variant Grams'), 0) / 1000  # Convert to kg
                product.weight_unit = main_row.get('Variant Weight Unit', 'kg')
                
                # Inventory
                product.quantity = self.safe_int(main_row.get('Variant Inventory Qty'))
                product.stock_quantity = product.quantity  # Sync
                product.inventory_policy = main_row.get('Variant Inventory Policy', 'deny')
                
                # Other attributes
                product.barcode = main_row.get('Variant Barcode', '')
                product.requires_shipping = self.safe_bool(main_row.get('Variant Requires Shipping'), True)
                product.taxable = self.safe_bool(main_row.get('Variant Taxable'), True)
                
                # SEO
                product.seo_title = main_row.get('SEO Title', '')
                product.meta_title = main_row.get('SEO Title', '')  # Sync
                product.seo_description = main_row.get('SEO Description', '')
                product.meta_description = main_row.get('SEO Description', '')  # Sync
                
                # Status
                product.published = self.safe_bool(main_row.get('Published'), True)
                product.show_online = product.published  # Sync
                product.status = main_row.get('Status', 'active')
                product.is_active = product.status == 'active'
                
                # Regional pricing
                product.included_india = self.safe_bool(main_row.get('Included / India'), True)
                product.price_india = self.safe_decimal(main_row.get('Price / India'), None)
                product.included_international = self.safe_bool(main_row.get('Included / International'), False)
                product.price_international = self.safe_decimal(main_row.get('Price / International'), None)
                
                # Save product (with force_insert if new to avoid slug conflicts)
                if created:
                    product.save(force_insert=True)
                    self.products_created += 1
                else:
                    product.save()
                    self.products_updated += 1
                
                # Process variants and images
                images_before = ProductImage.objects.filter(product=product).count()
                self._process_shopify_variants_and_images(product, data['rows'])
                images_after = ProductImage.objects.filter(product=product).count()
                
                # Debug: Log if no images were added
                if images_after == 0 and len(data['rows']) > 0:
                    # Check if Image Src exists in the rows
                    has_image_src = any(row.get('Image Src', '').strip() for row in data['rows'])
                    if has_image_src:
                        self.errors.append(f"Warning: Product {product.sku} has Image Src in CSV but no images were created")
                
                if created:
                    self.products_created += 1
                else:
                    self.products_updated += 1
                    
            except Exception as e:
                self.errors.append(f"Row {idx} (Handle: {handle}): {str(e)}")
    
    def _process_shopify_variants_and_images(self, product, rows):
        """Process variants and images for Shopify format"""
        # Clear existing variants and images if reimporting
        product.variants.all().delete()
        product.images.all().delete()
        
        processed_images = set()
        image_position = 1
        
        for row in rows:
            # Process image if present
            image_src = row.get('Image Src', '').strip()
            if image_src and image_src not in processed_images:
                try:
                    ProductImage.objects.create(
                        product=product,
                        image_url=image_src,
                        position=image_position,
                        sort_order=image_position,
                        alt_text=row.get('Image Alt Text', ''),
                        is_primary=(image_position == 1),
                        is_active=True
                    )
                    processed_images.add(image_src)
                    image_position += 1
                except Exception as e:
                    self.errors.append(f"Error adding image for {product.sku}: {str(e)}")
            
            # Process variant if it has variant-specific data
            variant_sku = row.get('Variant SKU', '').strip()
            option1_value = row.get('Option1 Value', '').strip()
            
            # Only create variant if it's not "Default Title" or has unique attributes
            if option1_value and option1_value != 'Default Title':
                # Generate variant name
                variant_name_parts = []
                if row.get('Option1 Value'):
                    variant_name_parts.append(row.get('Option1 Value'))
                if row.get('Option2 Value'):
                    variant_name_parts.append(row.get('Option2 Value'))
                if row.get('Option3 Value'):
                    variant_name_parts.append(row.get('Option3 Value'))
                
                variant_name = ' / '.join(variant_name_parts) if variant_name_parts else 'Default'
                
                try:
                    ProductVariant.objects.create(
                        product=product,
                        name=variant_name,
                        variant_sku=variant_sku,
                        option1_name=row.get('Option1 Name', ''),
                        option1_value=option1_value,
                        option2_name=row.get('Option2 Name', ''),
                        option2_value=row.get('Option2 Value', ''),
                        option3_name=row.get('Option3 Name', ''),
                        option3_value=row.get('Option3 Value', ''),
                        price=self.safe_decimal(row.get('Variant Price')),
                        additional_price=Decimal('0'),
                        compare_at_price=self.safe_decimal(row.get('Variant Compare At Price'), None),
                        cost_per_item=self.safe_decimal(row.get('Cost per item'), None),
                        inventory_quantity=self.safe_int(row.get('Variant Inventory Qty')),
                        inventory_policy=row.get('Variant Inventory Policy', 'deny'),
                        image_url=row.get('Variant Image', ''),
                        weight=self.safe_decimal(row.get('Variant Grams'), 0) / 1000,
                        barcode=row.get('Variant Barcode', ''),
                        requires_shipping=self.safe_bool(row.get('Variant Requires Shipping'), True),
                        taxable=self.safe_bool(row.get('Variant Taxable'), True),
                        is_active=True
                    )
                except Exception as e:
                    self.errors.append(f"Error adding variant for {product.sku}: {str(e)}")