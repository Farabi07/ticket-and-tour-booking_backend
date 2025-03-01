
from django.urls import path
from account.views import contra_views as views


urlpatterns = [

	path('api/v1/contra/all/', views.getAllContra),

	path('api/v1/contra/contra_by_invoice_no/<str:invoice_no>', views.getAllContraByInvoiceNo),

	path('api/v1/contra/<int:pk>', views.getAContra),

	path('api/v1/contra/search/', views.searchContra),

	path('api/v1/contra/create/', views.createContra),

	path('api/v1/contra/update/', views.updateContra),

	path('api/v1/contra/delete/<int:pk>', views.deleteContra),
	
	path('api/v1/contra/delete_multiple/', views.deleteMultipleContra),

]