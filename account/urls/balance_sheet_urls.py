from django.urls import path
from account.views import balance_sheet_views as views




urlpatterns = [

	path('api/v1/balance_sheet/trial_balance/', views.getTrialBalance),

	path('api/v1/balance_sheet/profit_loss/', views.getProfitLoss),

	path('api/v1/balance_sheet/balance_sheet/', views.getBalanceSheet),

]
