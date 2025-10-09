from django.core.management.base import BaseCommand
from apps.cart.models import Cart, CartItem
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Check cart contents and add-ons for debugging'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='User email to check cart for')

    def handle(self, *args, **options):
        email = options.get('email')

        if email:
            try:
                user = User.objects.get(email=email)
                carts = Cart.objects.filter(user=user)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with email {email} not found'))
                return
        else:
            carts = Cart.objects.all()

        if not carts.exists():
            self.stdout.write(self.style.WARNING('No carts found'))
            return

        for cart in carts:
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS(f'Cart for: {cart.user.email}'))
            self.stdout.write(f'Total items: {cart.total_items}')
            self.stdout.write(f'Total price: Rs.{cart.total_price}')
            self.stdout.write('-'*60)

            items = cart.items.all()
            if not items.exists():
                self.stdout.write(self.style.WARNING('  Cart is empty'))
                continue

            for item in items:
                self.stdout.write(f'\n  Product: {item.product.name}')
                if item.variant:
                    self.stdout.write(f'  Variant: {item.variant.name}')
                self.stdout.write(f'  Quantity: {item.quantity}')
                self.stdout.write(f'  Unit Price: Rs.{item.unit_price}')

                # Check add-ons
                addons = item.addons.all()
                if addons.exists():
                    self.stdout.write(self.style.SUCCESS(f'  Add-ons ({addons.count()}):'))
                    for addon in addons:
                        self.stdout.write(f'    - {addon.name} (+Rs.{addon.price})')
                    self.stdout.write(f'  Add-ons Total: Rs.{item.addons_price}')
                else:
                    self.stdout.write(self.style.WARNING('  No add-ons'))

                self.stdout.write(f'  Item Total: Rs.{item.total_price}')
                self.stdout.write('-'*60)
