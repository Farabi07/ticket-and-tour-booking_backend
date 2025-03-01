from django.urls import path

from ..views import booking_summery_views as views

urlpatterns = [

	path('api/v1/booking_summery/', views.getBookingSummery),


] 