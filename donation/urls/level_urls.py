from django.urls import path

from donation.views import level_views as views


urlpatterns = [
    path('api/v1/level/all/', views.getAllLevel),

    path('api/v1/level/without_pagination/all/',
         views.getAllLevelWithoutPagination),

    path('api/v1/level/<int:pk>', views.getALevel),

    path('api/v1/level/create/', views.createLevel),

    path('api/v1/level/update/<int:pk>', views.updateLevel),

    path('api/v1/level/delete/<int:pk>', views.deleteLevel),

    path('api/v1/level/get_all_user_by_level_name/<int:level_name>',
         views.getAllUserInformationByLevel),

    path('api/v1/level/get_all_level_by_user_id/<int:user_id>/<str:level_name>',
         views.getAllLevelByUser),

]
