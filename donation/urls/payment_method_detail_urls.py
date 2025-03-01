
from django.urls import path
from donation.views import payment_method_detail_views as views


urlpatterns = [
	
	path('api/v1/payment_method_detail/all/', views.getAllPaymentMethodDetail),

	path('api/v1/payment_method_detail/<int:pk>', views.getAPaymentMethodDetail),

	path('api/v1/payment_method_detail/search/', views.searchPaymentMethodDetail),

	path('api/v1/payment_method_detail/create/', views.createPaymentMethodDetail),

	path('api/v1/payment_method_detail/update/<int:pk>', views.updatePaymentMethodDetail),

	path('api/v1/payment_method_detail/delete/<int:pk>', views.deletePaymentMethodDetail),

]