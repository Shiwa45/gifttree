from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.wallet.models import Wallet

User = get_user_model()


class Command(BaseCommand):
    help = 'Create wallets for existing users who don\'t have one'

    def handle(self, *args, **options):
        self.stdout.write('Creating wallets for existing users...\n')

        # Get all users without wallets
        users_without_wallets = User.objects.filter(wallet__isnull=True)

        created_count = 0
        error_count = 0

        for user in users_without_wallets:
            try:
                wallet = Wallet.objects.create(
                    user=user,
                    balance=200.00  # Initial bonus
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created wallet for {user.email} with 200 coins bonus')
                )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Error creating wallet for {user.email}: {str(e)}')
                )

        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'Summary: {created_count} wallets created')
        )
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'Errors: {error_count}')
            )
        self.stdout.write(
            self.style.SUCCESS(f'Total users with wallets: {Wallet.objects.count()}')
        )
