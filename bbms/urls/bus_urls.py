from django.urls import path

from ..views import bus_views as views

urlpatterns = [
	path('api/v1/bus/all/', views.getAllBus, name="getAllBus"),
 
    path('api/v1/bus/all/without_pagination/', views.getAllBusWithoutPagination, name ="getAllBusWithoutPagination"),

	path('api/v1/bus/<int:pk>', views.getABus, name="getABus"),

	path('api/v1/bus/create/', views.createBus, name = "createBus"),

	path('api/v1/bus/update/<int:pk>', views.updateBus, name = "updateBus"),
	
	path('api/v1/bus/delete/<int:pk>', views.deleteBus, name = "deleteBus"),
 
     path('api/v1/bus/search/', views.searchBus, name = "searchBus"),
     
     path('api/v1/bus/<int:pk>/<str:date>/<str:time>', views.getABusWithDateAndTime, name = "getABusWithDateAndTime"),
] 