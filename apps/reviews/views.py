from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Review, ReviewImage
from apps.products.models import Product
from apps.orders.models import Order, OrderItem


@login_required
def my_reviews(request):
    """Display user's reviews"""
    reviews = Review.objects.filter(user=request.user).select_related('product')
    context = {
        'reviews': reviews,
    }
    return render(request, 'reviews/my_reviews.html', context)


# ============================================
# ✅ NEW: REVIEW SUBMISSION VIEWS
# ============================================

@login_required
def submit_review(request, product_id):
    """Submit a new review for a product"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Check if user already reviewed this product
    existing_review = Review.objects.filter(user=request.user, product=product).first()
    if existing_review:
        messages.warning(request, 'You have already reviewed this product. Edit your existing review instead.')
        return redirect('reviews:edit_review', review_id=existing_review.id)
    
    # Check if user has purchased this product (optional verification)
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status='delivered'
    ).exists()
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        title = request.POST.get('title', '').strip()
        comment = request.POST.get('comment', '').strip()
        
        # Validation
        if not (1 <= rating <= 5):
            messages.error(request, 'Please select a rating between 1 and 5 stars.')
            return render(request, 'reviews/submit_review.html', {
                'product': product,
                'has_purchased': has_purchased
            })
        
        if not title or not comment:
            messages.error(request, 'Please provide both a title and comment for your review.')
            return render(request, 'reviews/submit_review.html', {
                'product': product,
                'has_purchased': has_purchased
            })
        
        # Create review
        review = Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            title=title,
            comment=comment,
            is_verified_purchase=has_purchased
        )
        
        # Handle image uploads
        images = request.FILES.getlist('images')
        for image in images[:5]:  # Max 5 images
            ReviewImage.objects.create(
                review=review,
                image=image
            )
        
        messages.success(request, 'Thank you! Your review has been submitted successfully.')
        return redirect('products:product_detail', slug=product.slug)
    
    context = {
        'product': product,
        'has_purchased': has_purchased
    }
    return render(request, 'reviews/submit_review.html', context)


@login_required
def edit_review(request, review_id):
    """Edit an existing review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        title = request.POST.get('title', '').strip()
        comment = request.POST.get('comment', '').strip()
        
        # Validation
        if not (1 <= rating <= 5):
            messages.error(request, 'Please select a rating between 1 and 5 stars.')
        elif not title or not comment:
            messages.error(request, 'Please provide both a title and comment for your review.')
        else:
            # Update review
            review.rating = rating
            review.title = title
            review.comment = comment
            review.save()
            
            # Handle new image uploads
            new_images = request.FILES.getlist('images')
            for image in new_images:
                if review.images.count() < 5:  # Max 5 images
                    ReviewImage.objects.create(
                        review=review,
                        image=image
                    )
            
            messages.success(request, 'Your review has been updated successfully.')
            return redirect('reviews:my_reviews')
    
    context = {
        'review': review,
        'product': review.product
    }
    return render(request, 'reviews/edit_review.html', context)


@login_required
@require_POST
def delete_review(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_name = review.product.name
    review.delete()
    
    messages.success(request, f'Your review for "{product_name}" has been deleted.')
    return redirect('reviews:my_reviews')


@login_required
@require_POST
def delete_review_image(request, image_id):
    """Delete a review image"""
    image = get_object_or_404(ReviewImage, id=image_id, review__user=request.user)
    image.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Image deleted successfully'
    })


# ============================================
# PUBLIC REVIEW VIEWS (No login required)
# ============================================

def product_reviews(request, product_id):
    """Display all reviews for a product"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Get approved reviews
    reviews = Review.objects.filter(
        product=product,
        is_approved=True,
        is_active=True
    ).select_related('user').prefetch_related('images').order_by('-created_at')
    
    # Filter by rating if specified
    rating_filter = request.GET.get('rating')
    if rating_filter:
        reviews = reviews.filter(rating=int(rating_filter))
    
    # Sort reviews
    sort_by = request.GET.get('sort', 'recent')
    if sort_by == 'helpful':
        # If you have a helpful votes system
        reviews = reviews.order_by('-created_at')  # Fallback
    elif sort_by == 'rating_high':
        reviews = reviews.order_by('-rating', '-created_at')
    elif sort_by == 'rating_low':
        reviews = reviews.order_by('rating', '-created_at')
    else:  # recent (default)
        reviews = reviews.order_by('-created_at')
    
    # Calculate rating statistics
    total_reviews = reviews.count()
    avg_rating = 0
    rating_distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    
    if total_reviews > 0:
        all_ratings = reviews.values_list('rating', flat=True)
        avg_rating = sum(all_ratings) / total_reviews
        
        for rating in all_ratings:
            rating_distribution[rating] += 1
    
    context = {
        'product': product,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'rating_distribution': rating_distribution,
        'rating_filter': rating_filter,
        'sort_by': sort_by,
    }
    
    return render(request, 'reviews/product_reviews.html', context)


@login_required
def can_review_product(request, product_id):
    """Check if user can review a product (AJAX endpoint)"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if already reviewed
    has_reviewed = Review.objects.filter(
        user=request.user,
        product=product
    ).exists()
    
    # Check if purchased
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status='delivered'
    ).exists()
    
    return JsonResponse({
        'can_review': not has_reviewed,
        'has_reviewed': has_reviewed,
        'has_purchased': has_purchased
    })