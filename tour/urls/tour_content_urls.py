
from django.urls import path

from tour.views import tour_content_views as views

urlpatterns = [
    # path('stripe/test-payment/', views.create_checkout_session),

	path('api/v1/tour_content/all/', views.getAllTourContent),

	path('api/v1/tour_content/without_pagination/all/', views.getAllTourContentWithoutPagination),

	# path('api/v1/get_all_tour_content_by_cms_menu_id/<str:menu_id>', views.getAllTourContentByCMSMenuId),

	path('api/v1/tour_content/<int:pk>', views.getATourContent),

	path('api/v1/tour_content/create/', views.createTourContent),

	path('api/v1/tour_content/update/<int:pk>', views.updateTourContent),
	
	path('api/v1/tour_content/delete/<int:pk>', views.deleteTourContent),

	# path('api/v1/cms_tour_content/get_cms_tour_content_by_cms_menu_id/<int:pk>', views.getTourContentByCMSMenyID),
    
    # path('api/v1/cms_tour_content/<str:menu_name>/<str:content_name>/', views.get_tour_content_by_name),
    
	# path('api/v1/cms_tour_content/<str:content_name>/', views.get_tour_content_by_name),

]