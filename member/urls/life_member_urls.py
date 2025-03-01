from django.urls import path

from member.views import life_member_views as views

urlpatterns = [
    path('api/v1/life_member/all/', views.getAllLifeMember),

    path('api/v1/life_member/<int:pk>', views.getALifeMember),

    path('api/v1/life_member/create/', views.createLifeMember),

    path('api/v1/life_member/update/<int:pk>', views.updateLifeMember),

    path('api/v1/life_member/delete/<int:pk>', views.deleteLifeMember),

    path('api/v1/life_member/without_pagination/all/', views.getAllLifeMemberWithoutPagination),

    path('api/v1/life_member/search/', views.searchLifeMember)
]