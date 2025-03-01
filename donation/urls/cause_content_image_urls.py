
from django.urls import path

from donation.views import cause_content_image_views as views


urlpatterns = [

	path('api/v1/cause_content_image/all/', views.getAllCauseContentImage),

	path('api/v1/cause_content_image/without_pagination/all/', views.getAllCauseContentImageWithoutPagination),

	path('api/v1/get_all_cause_content_image_by_cause_id/<int:cause_id>', views.getAllCauseContentImageByCauseId),

	path('api/v1/cause_content_image/<int:pk>', views.getACauseContentImage),

	path('api/v1/cause_content_image/create/', views.createCauseContentImage),

	path('api/v1/cause_content_image/update/<int:pk>', views.updateCauseContentImage),
	
	path('api/v1/cause_content_image/delete/<int:pk>', views.deleteCauseContentImage),

]