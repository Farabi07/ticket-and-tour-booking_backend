from django.urls import path

from donation.views import collection_views as views


urlpatterns = [
    path('api/v1/collection/all/', views.getAllCollection),

    path('api/v1/collection/without_pagination/all/',
         views.getAllCollectionWithoutPagination),

    path('api/v1/collection/<int:pk>', views.getACollection),

    path('api/v1/collection/create/', views.createCollection),

    path('api/v1/collection/update/<int:pk>', views.updateCollection),

    path('api/v1/collection/delete/<int:pk>', views.deleteCollection),
]
