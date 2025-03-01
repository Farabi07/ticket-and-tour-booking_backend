
from django.urls import path
from account.views import account_log_views as views


urlpatterns = [
	
	path('api/v1/account_log/all/', views.getAllAccountLog),

	path('api/v1/account_log/<int:pk>', views.getAAccountLog),

	path('api/v1/account_log/search/', views.searchAccountLog),

	# path('api/v1/account_log/create/', views.createAccountLog),

	# path('api/v1/account_log/update/<int:pk>', views.updateAccountLog),

	path('api/v1/account_log/delete/<int:pk>', views.deleteAccountLog),

	path('api/v1/account_log/delete_multiple/', views.deleteMultipleAccountLog),

]