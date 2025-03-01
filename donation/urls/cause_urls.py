
from django.urls import path

from donation.views import cause_views as views


urlpatterns = [
	path('api/v1/cause/all/', views.getAllCause),

	path('api/v1/cause/without_pagination/all/', views.getAllCauseWithoutPagination),

	path('api/v1/cause/get_all_content_and_image_by_cause_id/<int:cause_id>', views.getAllCauseContentAndImageByCauseId),

	path('api/v1/cause/<int:pk>', views.getACause),

	path('api/v1/cause/create/', views.createCause),

	path('api/v1/cause/update/<int:pk>', views.updateCause),
	
	path('api/v1/cause/delete/<int:pk>', views.deleteCause),
]