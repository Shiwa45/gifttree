from django.urls import path
from . import views
from . import razorpay_handler
from . import razorpay_views
from . import seller_views

app_name = 'orders'

urlpatterns = [
    # Main checkout page
    path('checkout/', views.checkout_view, name='checkout'),

    # Checkout process
    path('checkout/address/', views.checkout_address, name='checkout_address'),
    path('checkout/delivery/', views.checkout_delivery, name='checkout_delivery'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout/place-order/', views.place_order, name='place_order'),
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),

    # Order management
    path('', views.order_list, name='order_list'),
    path('detail/<str:order_number>/', views.order_detail, name='order_detail'),
    path('cancel/<str:order_number>/', views.cancel_order, name='cancel_order'),

    # AJAX endpoints
    path('ajax/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('ajax/remove-coupon/', views.remove_coupon, name='remove_coupon'),

    # Razorpay payment endpoints (using razorpay_views which works with cart directly)
    path('payment/create-razorpay-order/', razorpay_views.create_razorpay_order, name='create_razorpay_order'),
    path('payment/verify/', razorpay_views.verify_razorpay_payment, name='verify_payment'),
    path('payment/failed/', razorpay_handler.payment_failed, name='payment_failed'),
    
    # COD order processing
    path('payment/process-cod/', razorpay_views.process_cod_order, name='process_cod_order'),
    
    # Seller portal URLs
    path('seller/dashboard/', seller_views.seller_dashboard, name='seller_dashboard'),
    path('seller/order/<str:order_number>/', seller_views.seller_order_detail, name='seller_order_detail'),
    path('seller/order/<str:order_number>/update-status/', seller_views.seller_update_order_status, name='seller_update_order_status'),
    path('seller/order/<str:order_number>/add-tracking/', seller_views.seller_add_tracking, name='seller_add_tracking'),
]