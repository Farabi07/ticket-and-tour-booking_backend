from django_filters import rest_framework as filters

from member.models import *





class MemberFilter(filters.FilterSet):
    first_name = filters.CharFilter(field_name="first_name", lookup_expr='icontains')
    last_name = filters.CharFilter(field_name="last_name", lookup_expr='icontains')
    username = filters.CharFilter(field_name="username", lookup_expr='icontains')
    email = filters.CharFilter(field_name="email", lookup_expr='icontains')

    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'username', 'email', ]


class LifeMemberFilter(filters.FilterSet):
    first_name = filters.CharFilter(field_name="first_name", lookup_expr='icontains')
    last_name = filters.CharFilter(field_name="last_name", lookup_expr='icontains')
    username = filters.CharFilter(field_name="username", lookup_expr='icontains')
    email = filters.CharFilter(field_name="email", lookup_expr='icontains')

    class Meta:
        model = LifeMember
        fields = ['first_name', 'last_name', 'username', 'email', ]



