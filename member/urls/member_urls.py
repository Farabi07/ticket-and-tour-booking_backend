from django.urls import path

from member.views import member_views as views

urlpatterns = [

    path('api/v1/member/all/', views.getAllMember),

    path('api/v1/member/without_pagination/all/', views.getAllMemberWithoutPagination),

    path('api/v1/member/<int:pk>', views.getAMember),

    path('api/v1/member/search/', views.searchMember),

    path('api/v1/member/create/', views.createMember),

    path('api/v1/member/update/<int:pk>', views.updateMember),

    path('api/v1/member/delete/<int:pk>', views.deleteMember),

    path('api/v1/member/check_refer_id_when_create/',views.checkReferIDWhenCreate),

    path('api/v1/member/apply_coupon/',views.applyCoupon),

]
