from django_filters import rest_framework as filters

from tour.models import *


# class BlogFilter(filters.FilterSet):
#     title = filters.CharFilter(field_name="title", lookup_expr='icontains')

#     class Meta:
#         model = Blog
#         fields = ['title', ]

# class BlogCommentsFilter(filters.FilterSet):
#     title = filters.CharFilter(field_name="title", lookup_expr='icontains')

#     class Meta:
#         model = BlogComments
#         fields = ['title', ]

# class MetaDataFilter(filters.FilterSet):
#     meta_title = filters.CharFilter(field_name="meta_title", lookup_expr='icontains')

#     class Meta:
#         model = MetaData
#         fields = ['meta_title', ]

# class BlogCategoryFilter(filters.FilterSet):
#     title = filters.CharFilter(field_name="name", lookup_expr='icontains')

#     class Meta:
#         model = BlogCategory
#         fields = ['name', ]

# class TagFilter(filters.FilterSet):
#     title = filters.CharFilter(field_name="name", lookup_expr='icontains')

#     class Meta:
#         model = Tag
#         fields = ['name', ]
