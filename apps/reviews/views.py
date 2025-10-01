from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Review


@login_required
def my_reviews(request):
    """Display user's reviews"""
    reviews = Review.objects.filter(user=request.user).select_related('product')
    context = {
        'reviews': reviews,
    }
    return render(request, 'reviews/my_reviews.html', context)