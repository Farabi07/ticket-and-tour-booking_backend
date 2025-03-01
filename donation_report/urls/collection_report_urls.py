from django.urls import path
from donation_report.views import collection_report_views as views

urlpatterns = [
    path('api/v1/collection_report/all', views.getCollectionReport),
    path('api/v1/collection_report/without_pagination',
         views.getCollectionReportWithoutPagination),

]
