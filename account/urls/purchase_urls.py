
from django.urls import path
from account.views import purchase_views as views


urlpatterns = [
	path('api/v1/purchase/all/', views.getAllPurchase),

	path('api/v1/purchase/purchase_by_invoice_no/<str:invoice_no>', views.getAllPurchaseByInvoiceNo),

	path('api/v1/purchase/<int:pk>', views.getAPurchase),

	path('api/v1/purchase/search/', views.searchPurchase),

	path('api/v1/purchase/create/', views.createPurchase),

	path('api/v1/purchase/update/', views.updatePurchase),
	
	path('api/v1/purchase/delete/<int:pk>', views.deletePurchase),

	path('api/v1/purchase/delete_multiple/', views.deleteMultiplePurchase),

]