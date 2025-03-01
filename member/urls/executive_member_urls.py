
from django.urls import path

from member.views import executive_member_views as views


urlpatterns = [
	path('api/v1/executive_member/all/', views.getAllExecutiveMember),

	path('api/v1/executive_member/without_pagination/', views.getAllExecutiveMemberWithoutPagination),

	path('api/v1/executive_member/<int:pk>', views.getAExecutiveMember),

	path('api/v1/executive_member/create/', views.createExecutiveMember),

	path('api/v1/executive_member/update/<int:pk>', views.updateExecutiveMember),
	
	path('api/v1/executive_member/delete/<int:pk>', views.deleteExecutiveMember),
]
