from django.urls import path
from donation_report.views import user_report_views as views

urlpatterns = [
    path('api/v1/user_report/all', views.getUserReport),
    path('api/v1/user_report/without_pagination',
         views.getUserReportWithoutPagination)

]
