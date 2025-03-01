from django.urls import path
from donation.views import payment_method_views as views

urlpatterns = [

    path('api/v1/payment_method/all/', views.getAllPaymentMethod),

    path('api/v1/payment_method/<int:pk>', views.getAPaymentMethod),

    path('api/v1/payment_method/search/', views.searchPaymentMethod),

    path('api/v1/payment_method/create/', views.createPaymentMethod),

    path('api/v1/payment_method/update/<int:pk>', views.updatePaymentMethod),

    path('api/v1/payment_method/delete/<int:pk>', views.deletePaymentMethod),

    path('api/v1/payment_method_by_type/<str:type_id>', views.getAllPaymentMethodByTypeId),

    path('api/v1/payment_method_without_pagination/', views.getPaymentMethodWithoutPagination),

]
