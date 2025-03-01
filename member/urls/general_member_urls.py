
from django.urls import path

from member.views import general_member_views as views


urlpatterns = [
	path('api/v1/general_member/all/', views.getAllGeneralMember),

	path('api/v1/general_member/without_pagination/', views.getAllGeneralMemberWithoutPagination),

	path('api/v1/general_member/<int:pk>', views.getAGeneralMember),

	path('api/v1/general_member/create/', views.createGeneralMember),

	path('api/v1/general_member/update/<int:pk>', views.updateGeneralMember),
	
	path('api/v1/general_member/delete/<int:pk>', views.deleteGeneralMember),
]