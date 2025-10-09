from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('offers/', views.offers_view, name='offers'),
    path('sitemap.xml', views.sitemap_view, name='sitemap'),
]