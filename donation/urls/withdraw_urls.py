from django.urls import path
from donation.views import withdraw_views as views


urlpatterns = [
    path('api/v1/withdraw/all/', views.getAllWithdraw),

    path('api/v1/withdraw/<int:pk>', views.getAWithdraw),

    path('api/v1/withdraw/create/', views.createWithdraw),

    path('api/v1/withdraw/update/<int:pk>', views.updateWithdraw),

    path('api/v1/withdraw/delete/<int:pk>', views.deleteWithdraw),

    path('api/v1/withdraw_by_invoice/',
         views.getAllIWithdrawByInvoice),

    path('api/v1/withdraw_by_user_id/<int:user_id>',
         views.getAllIWithdrawByUserId),
]
