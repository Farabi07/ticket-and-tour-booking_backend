from django.urls import path
from donation.views import member_account_log_views as views


urlpatterns = [
    path('api/v1/member_account_log/all/', views.getAllMemberAccountLog),

    path('api/v1/member_account_log/without_pagination/all/',
         views.getAllMemberAccountLogWithoutPagination),

    path('api/v1/member_account_log/<int:pk>', views.getAMemberAccountLog),

    path('api/v1/member_account_log/create/', views.createMemberAccountLog),

    path('api/v1/member_account_log/update/<int:pk>',
         views.updateMemberAccountLog),

    path('api/v1/member_account_log/delete/<int:pk>',
         views.deleteMemberAccountLog),

]
