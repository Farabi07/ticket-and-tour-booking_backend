from django.urls import path

from ..views import bus_booking_views as views


urlpatterns = [
	path('api/v1/bus_booking/all/', views.getAllBusBooking),
    
	path('api/v1/bus_booking/booked_data/', views.getAllBookedBusBooking),
 
    path('api/v1/bus_booking/all/without_pagination/', views.getAllBusBookingWithoutPagination),

	path('api/v1/bus_booking/<int:pk>', views.getABusBooking),

	path('api/v1/bus_booking/create/', views.createBusBooking),

	path('api/v1/bus_booking/update/<int:pk>', views.updateBusBooking),
	
	path('api/v1/bus_booking/delete/<int:pk>', views.deleteBusBooking),
 
    path('api/v1/bus_booking/report/', views.getBusBookingReport),
     
    path('api/v1/bus_booking/report/wp/', views.getBusBookingReportWP),
    
	path('api/v1/bus_booking/agent_commission/', views.getAgentCommission),
    
	path('api/v1/bus_booking/check_bus_availability/', views.checkBusAvailability),

] 