from django.urls import path

from cms.views import cms_menu_content_image_views as views

urlpatterns = [

    path('api/v1/cms_menu_content_image/all/', views.getAllCMSMenuContentImage),

    path('api/v1/cms_menu_content_image/without_pagination/all/', views.getAllCMSMenuContentImageWithoutPagination),

    path('api/v1/get_all_cms_menu_content_image_list_by_cms_menu_id/<int:menu_id>',
         views.getAllContentImageListByMenuId),

    path('api/v1/get_all_cms_menu_content_image_by_cms_menu_id/<int:menu_id>', views.getAllCMSMenuContentImageByMenuId),

    path('api/v1/cms_menu_content_image/<int:pk>', views.getACMSMenuContentImage),

    path('api/v1/cms_menu_content_image/create/', views.createCMSMenuContentImage),

    path('api/v1/cms_menu_content_image/update/<int:pk>', views.updateCMSMenuContentImage),

    path('api/v1/cms_menu_content_image/delete/<int:pk>', views.deleteCMSMenuContentImage),


]
