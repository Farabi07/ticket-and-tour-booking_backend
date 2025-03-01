
from django.urls import path
from donation.views import cause_donation_views as views


urlpatterns = [

	path('api/v1/cause_donation/create/', views.createCauseDonation),

	# path('api/v1/cause_donation/update/<int:pk>', views.updateCauseDonation),


]