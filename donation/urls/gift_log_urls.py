from django.urls import path
from donation.views import gift_log_views as views


urlpatterns = [
    path('api/v1/gift_log/all/', views.getAllGiftLog),

    path('api/v1/gift_log/without_pagination/all/',
         views.getAllGiftLogWithoutPagination),

    path('api/v1/gift_log/<int:pk>', views.getAGiftLog),

    path('api/v1/gift_log/create/', views.createGiftLog),

    path('api/v1/gift_log/update/<int:pk>', views.updateGiftLog),

    path('api/v1/gift_log/delete/<int:pk>', views.deleteGiftLog),

]
