# payments/urls.py
from django.urls import path
from payments.views import payments_views as views

urlpatterns = [
    path('api/v1/create_payment/create/', views.CreatePayment),
    path('api/v1/payment_success/', views.PaymentSuccess),
    path('api/v1/payment_cancel/', views.PaymentCancel),
    path('api/v1/payment-failed/', views.PaymentFailed),
    path('api/v1/get-payment-status/<str:payment_id>/', views.getPaymentStatus),
    path('api/v1/stripe-webhook/', views.stripe_webhook),
    path('api/v1/stripe/payment/checkout/', views.CreateCheckout),
    path('api/v1/success-full/payment_details/<str:payment_key>/',views.getPaymentDetails),
    path("api/v1/customers/", views.get_customers),
    path('api/v1/balance-transactions/', views.get_balance_transactions),
    # path('api/v1/payment/all/', views.getAllPayment),

	# path('api/v1/payment/without_pagination/all/', views.getAllPaymentyWithoutPagination),

	path('api/v1/payment/<int:pk>', views.getAPayment),
]
