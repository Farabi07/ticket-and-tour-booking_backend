
from django.urls import path

from donation.views import cause_content_views as views


urlpatterns = [
	path('api/v1/cause_content/all/', views.getAllCauseContent),

	path('api/v1/get_all_cause_content_by_cause_id/<str:cause_id>', views.getAllCauseContentByCauseId),

	path('api/v1/cause_content/<int:pk>', views.getACauseContent),

	path('api/v1/cause_content/create/', views.createCauseContent),

	path('api/v1/cause_content/update/<int:pk>', views.updateCauseContent),
	
	path('api/v1/cause_content/delete/<int:pk>', views.deleteCauseContent),
]