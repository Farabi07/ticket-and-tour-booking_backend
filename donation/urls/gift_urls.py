from django.urls import path
from donation.views import gift_views as views


urlpatterns = [
    path('api/v1/gift/all/', views.getAllGift),

    path('api/v1/gift/without_pagination/all/',
         views.getAllGiftWithoutPagination),

    path('api/v1/gift/<int:pk>', views.getAGift),

    path('api/v1/gift/create/', views.createGift),

    path('api/v1/gift/update/<int:pk>', views.updateGift),

    path('api/v1/gift/delete/<int:pk>', views.deleteGift),

    path('api/v1/list_all_children_of_parent/<int:parent_id>',
         views.ListAllChildrenofParent),


]
