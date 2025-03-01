from django.urls import path

from tour.views import tour_content_image_views as views


urlpatterns = [

	path('api/v1/tour_content_image/all/', views.getAllTourContentImage),

	path('api/v1/tour_content_image/without_pagination/all/', views.getAllContentImageWP),

	path('api/v1/get_all_tour_content_image_by_cms_menu_id/<int:menu_id>', views.getAllContentImageByMenuId),

	path('api/v1/get_all_tour_content_image_list_by_cms_menu_id/<int:menu_id>', views.getAllContentImageListByMenuId),

	path('api/v1/tour_content_image/<str:image_name>', views.getATourContentImageByContentTitle),

	path('api/v1/tour_content_image/create/', views.createTourContentImage),

	path('api/v1/tour_content_image/update/<int:pk>', views.updateTourContentImage),

	path('api/v1/tour_content_image/delete/<int:pk>', views.deleteTourContentImage),
    
	path('api/v1/get_all_tour_content_image_list_by_menu_name/<str:menu_name>', views.getContentImageListByMenuName),
    
	path('api/v1/get_content_and_images_by_menu_id/<int:menu_id>/', views.get_content_and_images_by_menu_id, name='get_content_and_images_by_menu_id'),

]