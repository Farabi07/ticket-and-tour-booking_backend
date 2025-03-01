
from django.urls import path
from account.views import group_views as views


urlpatterns = [

	path('api/v1/group/all/', views.getAllGroup),

	path('api/v1/group/without_pagination/all/', views.getAllGroupWithoutPagination),

	path('api/v1/group/<int:pk>', views.getAGroup),

	path('api/v1/group/search/', views.searchGroup),

	path('api/v1/group/create/', views.createGroup),

	path('api/v1/group/update/<int:pk>', views.updateGroup),

	path('api/v1/group/delete/<int:pk>', views.deleteGroup),

	path('api/v1/group/delete_multiple/', views.deleteMultipleGroup),

	path('api/v1/group/test/', views.testGroup),

]