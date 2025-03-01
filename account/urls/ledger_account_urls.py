
from django.urls import path
from account.views import ledger_account_views as views


urlpatterns = [
	path('api/v1/ledger_account/all/', views.getAllLedgerAccount),
	
	path('api/v1/ledger_account/without_pagination/all/', views.getAllLedgerAccountWithoutPagination),

	path('api/v1/ledger_account/<int:pk>', views.getALedgerAccount),

	path('api/v1/ledger_account/search/', views.searchLedgerAccount),

	path('api/v1/ledger_account/create/', views.createLedgerAccount),

	path('api/v1/ledger_account/update/<int:pk>', views.updateLedgerAccount),

	path('api/v1/ledger_account/delete/<int:pk>', views.deleteLedgerAccount),

	path('api/v1/ledger_account/delete_multiple/', views.deleteMultipleLedgerAccount),

]