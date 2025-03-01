
from django.urls import path
from donation.views import monthly_subscription_views as views


urlpatterns = [

	path('api/v1/monthly_subscription/all/', views.getAllMonthlySubscription),

	path('api/v1/monthly_subscription/get_all_by_member/', views.getAllMonthlySubscriptionByMember),

	path('api/v1/monthly_subscription/<int:pk>', views.getAMonthlySubscription),

	path('api/v1/monthly_subscription/search/', views.searchMonthlySubscription),

	path('api/v1/monthly_subscription/create/', views.createMonthlySubscription),

	path('api/v1/monthly_subscription/update/<int:pk>', views.updateMonthlySubscription),

	path('api/v1/monthly_subscription/delete/<int:pk>', views.deleteMonthlySubscription),

]