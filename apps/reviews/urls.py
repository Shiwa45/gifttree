from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('my-reviews/', views.my_reviews, name='my_reviews'),
]