from django.urls import path
from account.views import account_log_report_views as views




urlpatterns = [

	path('api/v1/account_log_report/general/', views.getAccountLogReportGeneral),

	path('api/v1/account_log_report/by_ledger_type/', views.getAccountLogReportByAccountType),

	path('api/v1/account_log_report/get_total_cash_dr_cr_bank_dr_cr/', views.getTotalCashDrCrBankDrCr),


	# frontend implementation not done yet
	path('api/v1/account_log_report/for_cash_ledger/', views.getAccountLogReportForCashLedger),

	path('api/v1/account_log_report/for_bank_ledger_or_bank_account_group/', views.getAccountLogReportForBankAccountGroup),

	path('api/v1/account_log_report/for_person_or_company_ledger/', views.getAccountLogReportForPersonOrCompanyLedger),

	path('api/v1/account_log_report/for_passenger/', views.getAccounLogReportForPassenger),

	path('api/v1/account_log_report/for_sub_ledger/', views.getAccounLogReportForSubLedger),

]


