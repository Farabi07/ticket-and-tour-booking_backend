from django.urls import path

from member.views import promoter_views as views

urlpatterns = [

    path('api/v1/promoter/all/', views.getAllPromoter),

    path('api/v1/promoter/without_pagination/all/', views.getAllPromoterWithoutPagination),

    path('api/v1/promoter/<int:pk>', views.getAPromoter),

    path('api/v1/promoter/search/', views.searchPromoter),

    path('api/v1/promoter/create/', views.createPromoter),

    path('api/v1/promoter/update/<int:pk>', views.updatePromoter),

    path('api/v1/promoter/delete/<int:pk>', views.deletePromoter),

    path('api/v1/promoter/check_refer_id_when_create/',
         views.checkReferIDWhenCreate),

]
