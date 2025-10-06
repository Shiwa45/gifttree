from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # User's reviews
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    
    # ✅ NEW: Review submission and management
    path('submit/<int:product_id>/', views.submit_review, name='submit_review'),
    path('edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('delete-image/<int:image_id>/', views.delete_review_image, name='delete_review_image'),
    
    # Public review views
    path('product/<int:product_id>/', views.product_reviews, name='product_reviews'),
    path('can-review/<int:product_id>/', views.can_review_product, name='can_review_product'),
]