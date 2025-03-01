
from django.urls import path
from account.views import sub_ledger_account_views as views


urlpatterns = [
	path('api/v1/sub_ledger_account/all/', views.getAllSubLedgerAccount),

	path('api/v1/sub_ledger_account/without_pagination/all/', views.getAllSubLedgerAccountWithoutPagination),

	path('api/v1/sub_ledger_account/<int:pk>', views.getASubLedgerAccount),

	path('api/v1/sub_ledger_account/search/', views.searchSubLedgerAccount),

	path('api/v1/sub_ledger_account/create/', views.createSubLedgerAccount),

	path('api/v1/sub_ledger_account/update/<int:pk>', views.updateSubLedgerAccount),

	path('api/v1/sub_ledger_account/delete/<int:pk>', views.deleteSubLedgerAccount),

	path('api/v1/sub_ledger_account/delete_multiple/', views.deleteMultipleSubLedgerAccount),


]