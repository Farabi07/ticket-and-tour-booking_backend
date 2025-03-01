
from django.urls import path
from account.views import payment_voucher_views as views


urlpatterns = [

	path('api/v1/payment_voucher/all/', views.getAllPaymentVoucher),

	path('api/v1/payment_voucher/payment_voucher_by_invoice_no/<str:invoice_no>', views.getAllPaymentVoucherByInvoiceNo),

	# path('api/v1/payment_voucher/payment_voucher_with_id_name_dict_by_invoice_no/<str:invoice_no>', views.getAllPaymentVoucherWithIdNameDictAgainstForeignKeyByInvoiceNo),

	path('api/v1/payment_voucher/<int:pk>', views.getAPaymentVoucher),

	path('api/v1/payment_voucher/search/', views.searchPaymentVoucher),

	path('api/v1/payment_voucher/create/', views.createPaymentVoucher),

	path('api/v1/payment_voucher/update/', views.updatePaymentVoucher),

	path('api/v1/payment_voucher/delete/<int:pk>', views.deletePaymentVoucher),

	path('api/v1/payment_voucher/delete_multiple/', views.deleteMultiplePaymentVoucher),

]