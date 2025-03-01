from django.urls import path
from donation_report.views import ledger_report_views as views

urlpatterns = [
    path('api/v1/ledger_report/all', views.getLedgerReport),
    path('api/v1/ledger_report/without_pagination',
         views.getLedgerReportWithoutPagination)

]
