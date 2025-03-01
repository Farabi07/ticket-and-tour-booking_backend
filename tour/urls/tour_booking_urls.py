from django.urls import path

from tour.views import tour_booking_views as views




urlpatterns = [
	path('api/v1/tour_booking/all/', views.getAllTourBooking),
    path('api/v1/tour_booking_list_by_agent/all/<str:agent_ref_no>/', views.tour_booking_list_by_agent),
    
	# path('api/v1/tour_booking/booked_data/', views.getAllBookedTourBooking),
 
    path('api/v1/tour_booking/all/without_pagination/', views.getAllTourBookingWithoutPagination),

	path('api/v1/tour_booking/<int:pk>', views.getATourBooking),

	path('api/v1/tour_booking/create/', views.createTourBooking),

	path('api/v1/tour_booking/update/<int:pk>', views.updateTourBooking),
	
	path('api/v1/tour_booking/delete/<int:pk>', views.deleteTourBooking),

] 
