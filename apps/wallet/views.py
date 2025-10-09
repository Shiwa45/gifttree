from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wallet, WalletTransaction


@login_required
def wallet_dashboard(request):
    """Wallet dashboard showing balance and transactions"""
    wallet, created = Wallet.objects.get_or_create(
        user=request.user,
        defaults={'balance': 200.00}
    )

    transactions = WalletTransaction.objects.filter(wallet=wallet).select_related('wallet')[:50]

    # Calculate stats
    total_credits = WalletTransaction.objects.filter(
        wallet=wallet,
        transaction_type='credit'
    ).count()

    total_debits = WalletTransaction.objects.filter(
        wallet=wallet,
        transaction_type='debit'
    ).count()

    context = {
        'wallet': wallet,
        'transactions': transactions,
        'total_credits': total_credits,
        'total_debits': total_debits,
    }
    return render(request, 'wallet/wallet_dashboard.html', context)
