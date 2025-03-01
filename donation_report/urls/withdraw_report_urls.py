from django.urls import path
from donation_report.views import withdraw_report_views as views

urlpatterns = [
    path('api/v1/withdraw_report/all', views.getwithdrawReport),
    path('api/v1/withdraw_report_without_pagination',
         views.getwithdrawReportWithoutPagination),
    path('api/v1/withdraw_report_by_user_id/<int:user_id>',
         views.getwithdrawReportByUserID),
]
