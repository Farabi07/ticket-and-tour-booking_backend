
from django.urls import path
from donation.views import donation_views as views


urlpatterns = [
	
	path('api/v1/donation/all/', views.getAllDonation),

	path('api/v1/donation/<int:pk>', views.getADonation),

	path('api/v1/donation/search/', views.searchDonation),

	path('api/v1/donation/create/', views.createDonation),

	path('api/v1/donation/update/<int:pk>', views.updateDonation),

	path('api/v1/donation/delete/<int:cause_id>/<int:pk>', views.deleteDonation),

]