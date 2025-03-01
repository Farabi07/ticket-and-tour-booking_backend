from django.urls import path

from ..views import passenger_views as views


urlpatterns = [
	path('api/v1/passenger/all/', views.getAllPassenger),
 
     path('api/v1/passenger/all/without_pagination/', views.getAllPassengerWithoutPagination),

	path('api/v1/passenger/<int:pk>', views.getAPassenger),
 
     path('api/v1/passenger_by_phone_number/', views.getAPassengerByPrimaryNumber),

	path('api/v1/passenger/create/', views.createPassenger),

	path('api/v1/passenger/update/<int:pk>', views.updatePassenger),
	
	path('api/v1/passenger/delete/<int:pk>', views.deletePassenger),
 
     path('api/v1/passenger/search/', views.searchPassenger),
     
   
     path('my-view/', views.my_view, name='my-view'),
    
     path('api/v1/sent_email_member_to_passenger/', views.send_email_member_to_passenger),
] 