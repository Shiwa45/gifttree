from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel

User = get_user_model()


class Wallet(BaseModel):
    """User wallet for storing coins"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=200.00)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'

    def __str__(self):
        return f"{self.user.email} - Balance: ₹{self.balance}"

    def add_coins(self, amount, description=""):
        """Add coins to wallet"""
        self.balance += amount
        self.save()
        WalletTransaction.objects.create(
            wallet=self,
            transaction_type='credit',
            amount=amount,
            description=description
        )
        return True

    def deduct_coins(self, amount, description=""):
        """Deduct coins from wallet if sufficient balance"""
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            WalletTransaction.objects.create(
                wallet=self,
                transaction_type='debit',
                amount=amount,
                description=description
            )
            return True
        return False


class WalletTransaction(BaseModel):
    """Transaction history for wallet"""
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Wallet Transaction'
        verbose_name_plural = 'Wallet Transactions'

    def __str__(self):
        return f"{self.wallet.user.email} - {self.transaction_type} - ₹{self.amount}"

    def save(self, *args, **kwargs):
        # Store balance after transaction
        self.balance_after = self.wallet.balance
        super().save(*args, **kwargs)
