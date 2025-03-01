
from django.urls import path
from account.views import sales_views as views


urlpatterns = [
	path('api/v1/sales/all/', views.getAllSales),

	path('api/v1/sales/receipt_voucher_by_invoice_no/<str:invoice_no>', views.getAllSalesByInvoiceNo),

	path('api/v1/sales/<int:pk>', views.getASales),

	path('api/v1/sales/search/', views.searchSales),

	path('api/v1/sales/create/', views.createSales),

	path('api/v1/sales/update/', views.updateSales),
	
	path('api/v1/sales/delete/<int:pk>', views.deleteSales),

	path('api/v1/sales/delete_multiple/', views.deleteMultipleSales),

]