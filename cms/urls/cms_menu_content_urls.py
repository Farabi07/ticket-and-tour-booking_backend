
from django.urls import path

from cms.views import cms_menu_content_views as views


urlpatterns = [

	path('api/v1/cms_menu_content/all/', views.getAllCMSMenuContent),

	path('api/v1/cms_menu_content/without_pagination/all/', views.getAllCMSMenuContentWithoutPagination),

	path('api/v1/get_all_cms_menu_content_by_cms_menu_id/<int:menu_id>', views.getAllCMSMenuContentByCMSMenuId),

	path('api/v1/cms_menu_content/<int:pk>', views.getACMSMenuContent),

	path('api/v1/cms_menu_content/create/', views.createCMSMenuContent),

	path('api/v1/cms_menu_content/update/<int:pk>', views.updateCMSMenuContent),
	
	path('api/v1/cms_menu_content/delete/<int:pk>', views.deleteCMSMenuContent),


]