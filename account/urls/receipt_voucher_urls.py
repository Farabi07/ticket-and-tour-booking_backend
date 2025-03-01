
from django.urls import path
from account.views import receipt_voucher_views as views


urlpatterns = [
	path('api/v1/receipt_voucher/all/', views.getAllReceiptVoucher),

	path('api/v1/receipt_voucher/receipt_voucher_by_invoice_no/<str:invoice_no>', views.getAllReceiptVoucherByInvoiceNo),

	# path('api/v1/receipt_voucher/receipt_voucher_with_id_name_dict_by_invoice_no/<str:invoice_no>', views.getAllReceiptVoucherWithIdNameDictAgainstForeignKeyByInvoiceNo),

	path('api/v1/receipt_voucher/<int:pk>', views.getAReceiptVoucher),

	path('api/v1/receipt_voucher/search/', views.searchReceiptVoucher),

	path('api/v1/receipt_voucher/create/', views.createReceiptVoucher),

	path('api/v1/receipt_voucher/update/', views.updateReceiptVoucher),
	
	path('api/v1/receipt_voucher/delete/<int:pk>', views.deleteReceiptVoucher),

	path('api/v1/receipt_voucher/delete_multiple/', views.deleteMultipleReceiptVoucher),

]