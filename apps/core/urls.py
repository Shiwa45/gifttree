from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('offers/', views.offers_view, name='offers'),
    path('worldwide-delivery/<slug:country_code>/', views.country_products_view, name='country_products'),
    path('about-us/', views.about_us_view, name='about_us'),
    path('terms-conditions/', views.terms_conditions_view, name='terms_conditions'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('contact-us/', views.contact_us_view, name='contact_us'),
    path('faq/', views.faq_view, name='faq'),
    path('sitemap.xml', views.sitemap_view, name='sitemap'),
]