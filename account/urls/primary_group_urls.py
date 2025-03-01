
from django.urls import path
from account.views import primary_group_views as views


urlpatterns = [

	path('api/v1/primary_group/all/', views.getAllPrimaryGroup),

	path('api/v1/primary_group/without_pagination/all/', views.getAllPrimaryGroupWithoutPagination),

	path('api/v1/primary_group/search/', views.searchPrimaryGroup),

	path('api/v1/primary_group/delete/<int:pk>', views.deletePrimaryGroup),

]