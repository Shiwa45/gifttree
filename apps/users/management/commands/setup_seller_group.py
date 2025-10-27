from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Create Seller user group with limited permissions'

    def handle(self, *args, **kwargs):
        # Create or get Seller group
        seller_group, created = Group.objects.get_or_create(name='Seller')
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created Seller group'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Seller group already exists, updating permissions...'))

        # Clear existing permissions
        seller_group.permissions.clear()

        # Define permissions for sellers
        permissions_to_add = []

        # Order permissions - VIEW and CHANGE only (no delete)
        from apps.orders.models import Order, OrderItem, OrderTracking
        order_ct = ContentType.objects.get_for_model(Order)
        permissions_to_add.extend([
            Permission.objects.get(content_type=order_ct, codename='view_order'),
            Permission.objects.get(content_type=order_ct, codename='change_order'),
        ])

        order_item_ct = ContentType.objects.get_for_model(OrderItem)
        permissions_to_add.extend([
            Permission.objects.get(content_type=order_item_ct, codename='view_orderitem'),
        ])

        order_tracking_ct = ContentType.objects.get_for_model(OrderTracking)
        permissions_to_add.extend([
            Permission.objects.get(content_type=order_tracking_ct, codename='view_ordertracking'),
            Permission.objects.get(content_type=order_tracking_ct, codename='add_ordertracking'),
            Permission.objects.get(content_type=order_tracking_ct, codename='change_ordertracking'),
        ])

        # Product permissions - VIEW only
        from apps.products.models import Product, ProductVariant
        product_ct = ContentType.objects.get_for_model(Product)
        permissions_to_add.extend([
            Permission.objects.get(content_type=product_ct, codename='view_product'),
        ])

        variant_ct = ContentType.objects.get_for_model(ProductVariant)
        permissions_to_add.extend([
            Permission.objects.get(content_type=variant_ct, codename='view_productvariant'),
        ])

        # Seller profile - VIEW and CHANGE their own
        from apps.users.models import Seller, SellerLocation
        seller_ct = ContentType.objects.get_for_model(Seller)
        permissions_to_add.extend([
            Permission.objects.get(content_type=seller_ct, codename='view_seller'),
            Permission.objects.get(content_type=seller_ct, codename='change_seller'),
        ])

        location_ct = ContentType.objects.get_for_model(SellerLocation)
        permissions_to_add.extend([
            Permission.objects.get(content_type=location_ct, codename='view_sellerlocation'),
            Permission.objects.get(content_type=location_ct, codename='change_sellerlocation'),
        ])

        # Add all permissions to the group
        seller_group.permissions.set(permissions_to_add)

        self.stdout.write(self.style.SUCCESS(f'✅ Added {len(permissions_to_add)} permissions to Seller group:'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('   📦 Orders:'))
        self.stdout.write('      - View orders')
        self.stdout.write('      - Update order status')
        self.stdout.write('      - Add/update order tracking')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('   📦 Products:'))
        self.stdout.write('      - View products and variants')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('   👤 Seller Profile:'))
        self.stdout.write('      - View and update own profile')
        self.stdout.write('      - Manage locations')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Seller group setup complete!'))

