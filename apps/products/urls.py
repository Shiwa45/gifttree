from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('search/', views.product_search, name='search'),
    path('search/suggestions/', views.product_autocomplete_api, name='search_suggestions'),
    path('quick-view/<int:product_id>/', views.quick_view, name='quick_view'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('occasion/<slug:slug>/', views.OccasionDetailView.as_view(), name='occasion_detail'),
    
    # New menu-based filtering URLs
    path('menu-category/<slug:slug>/', views.MenuCategoryDetailView.as_view(), name='menu_category_detail'),
    path('product-type/<slug:slug>/', views.ProductTypeDetailView.as_view(), name='product_type_detail'),
    path('collection/<slug:slug>/', views.CollectionDetailView.as_view(), name='collection_detail'),
    path('recipient/<slug:slug>/', views.RecipientDetailView.as_view(), name='recipient_detail'),
    path('location/<slug:slug>/', views.LocationDetailView.as_view(), name='location_detail'),
    
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]