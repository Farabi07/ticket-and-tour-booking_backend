from django.urls import path
from account.views import account_report_views as views




urlpatterns = [

	path('api/v1/account_report/report_for_payment_voucher/', views.getAccountReportForPaymentVoucher),
	path('api/v1/account_report/summary_for_payment_voucher/', views.getAccountSummaryForPaymentVoucher),

	path('api/v1/account_report/report_for_receipt_voucher/', views.getAccountReportForReceiptVoucher),
	path('api/v1/account_report/summary_for_receipt_voucher/', views.getAccountSummaryForReceiptVoucher),

	path('api/v1/account_report/report_for_sales/', views.getAccountReportForSales),
	path('api/v1/account_report/summary_for_sales/', views.getAccountSummaryForSales),

	path('api/v1/account_report/report_for_purchase/', views.getAccountReportForPurchase),
	path('api/v1/account_report/summary_for_purchase/', views.getAccountSummaryForPurchase),

	path('api/v1/account_report/report_for_contra/', views.getAccountReportForContra),

]
