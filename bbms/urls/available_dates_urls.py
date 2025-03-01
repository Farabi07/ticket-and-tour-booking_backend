from django.urls import path

from ..views import available_dates_views as views

urlpatterns = [
	path('api/v1/available_dates/all/', views.getAllAvailableDates),
 
    path('api/v1/available_dates/all/without_pagination/', views.getAllAvailableDatesWithoutPagination),

	path('api/v1/getA_available_dates/<int:pk>', views.getAAvailableDates),

	path('api/v1/available_dates/create/', views.createAvailableDates),

	path('api/v1/available_dates/update/<int:pk>', views.updateAvailableDates),
	
	path('api/v1/available_dates/delete/<int:pk>', views.deleteAvailableDates),
 
    path('api/v1/available_dates/search/', views.searchAvailableDates),
     
    #  path('api/v1/available_dates/<int:pk>/<str:date>/<str:time>', views.getAavailable_datesWithDateAndTime, name = "getAavailable_datesWithDateAndTime"),
] 