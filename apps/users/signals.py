from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def create_user_wallet(sender, instance, created, **kwargs):
    """Auto-create wallet with 200 coins for new users"""
    if created:
        from apps.wallet.models import Wallet
        Wallet.objects.create(user=instance, balance=200.00)
