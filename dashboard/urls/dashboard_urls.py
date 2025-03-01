from django.urls import path

from dashboard.views import dashboard_views as views


urlpatterns = [

    path('api/v1/dashboard/total_amount_of_first_generation/',
         views.getTotalAmountOfFirstLevelUser),

    path('api/v1/dashboard/total_amount_of_second_generation/',
         views.getTotalAmountOfSecondLevelUser),

    path('api/v1/dashboard/total_amount_of_third_generation/',
         views.getTotalAmountOfThirdLevelUser),


    path('api/v1/dashboard/total_amount_of_fourth_generation/',
         views.getTotalAmountOfFourthLevelUser),

    path('api/v1/dashboard/total_amount_of_fifth_generation/',
         views.getTotalAmountOfFifthLevelUser),

    path('api/v1/dashboard/total_amount_of_donation/',
         views.getTotalCollectionAmount),

    path('api/v1/dashboard/third_level_amount_of_bonus/',
         views.getThirdBonusAmount),


    path('api/v1/dashboard/fourth_level_amount_of_bonus/',
         views.getFourthBonusAmount),

    path('api/v1/dashboard/fifth_level_amount_of_bonus/',
         views.getFifthBonusAmount),

    path('api/v1/dashboard/distribution_amount/',
         views.getDistributionAmount),

    path('api/v1/dashboard/current_amount/',
         views.getCurrentAmount),
    path('api/v1/dashboard/user_total_amount/<int:user_id>',
         views.getUserTotalAmount),

]
