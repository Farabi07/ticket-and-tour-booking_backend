from django.urls import path
from donation_report.views import donation_report_views as views

urlpatterns = [
    path('api/v1/donation_report/all', views.getDonationReport),
    path('api/v1/donation_report/<int:cause_id>', views.getADonationReport)

]
