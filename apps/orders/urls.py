from django.urls import path
from . import views
from . import razorpay_views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    path('<str:order_number>/cancel/', views.cancel_order, name='cancel_order'),
    path('<str:order_number>/track/', views.track_order, name='track_order'),
    path('<str:order_number>/reorder/', views.reorder, name='reorder'),
    path('<str:order_number>/', views.order_detail, name='order_detail'),

    # Razorpay payment endpoints
    path('payment/create-order/', razorpay_views.create_razorpay_order, name='create_razorpay_order'),
    path('payment/verify/', razorpay_views.verify_razorpay_payment, name='verify_razorpay_payment'),
]