from django.urls import path
from . import views
from . import razorpay_handler

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

    # Razorpay payment endpoints
    path('payment/create-razorpay-order/', razorpay_handler.create_razorpay_order, name='create_razorpay_order'),
    path('payment/verify/', razorpay_handler.verify_payment, name='verify_payment'),
    path('payment/failed/', razorpay_handler.payment_failed, name='payment_failed'),
]