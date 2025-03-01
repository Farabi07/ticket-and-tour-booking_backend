
from django.urls import path

from member.views import adviser_member_views as views


urlpatterns = [
	path('api/v1/adviser_member/all/', views.getAllAdviserMember),

	path('api/v1/adviser_member/without_pagination/', views.getAllAdviserMemberWithoutPagination),

	path('api/v1/adviser_member/<int:pk>', views.getAAdviserMember),

	path('api/v1/adviser_member/create/', views.createAdviserMember),

	path('api/v1/adviser_member/update/<int:pk>', views.updateAdviserMember),
	
	path('api/v1/adviser_member/delete/<int:pk>', views.deleteAdviserMember),
]