from django_filters import rest_framework as filters

from account.models import *
from authentication.models import User
from donation.models import Collection, MemberAccountLog


class MemberAccountLogFilter(filters.FilterSet):
    payment_method = filters.CharFilter(
        field_name="payment_method", lookup_expr='exact')
    user = filters.NumberFilter(field_name="user", lookup_expr='exact')
    date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='created_at', lookup_expr='lte')
    debit_amount = filters.CharFilter(
        field_name="debit_amount", lookup_expr='exact')

    class Meta:
        model = MemberAccountLog
        fields = ['payment_method', 'user',
                  'date_after', 'date_before', 'debit_amount']


class CollectionFilter(filters.FilterSet):
    payment_method = filters.CharFilter(
        field_name="payment_method", lookup_expr='exact')
    user = filters.NumberFilter(field_name="user", lookup_expr='exact')
    date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='created_at', lookup_expr='lte')
    amount = filters.CharFilter(
        field_name="debit_amount", lookup_expr='exact')

    class Meta:
        model = Collection
        fields = ['payment_method', 'user',
                  'amount']


class LedgerFilter(filters.FilterSet):
    payment_method = filters.CharFilter(
        field_name="payment_method", lookup_expr='exact')
    user = filters.NumberFilter(field_name="user", lookup_expr='exact')
    date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='created_at', lookup_expr='lte')
    debit_amount = filters.CharFilter(
        field_name="debit_amount", lookup_expr='exact')
    credit_amount = filters.CharFilter(
        field_name="debit_amount", lookup_expr='exact')

    class Meta:
        model = MemberAccountLog
        fields = ['payment_method', 'user',
                  'date_after', 'date_before', 'debit_amount', 'credit_amount']


class UserFilter(filters.FilterSet):

    date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='created_at', lookup_expr='lte')
    current_level = filters.CharFilter(
        field_name="current_level", lookup_expr='exact')
    refer_id = filters.CharFilter(
        field_name="head_user", lookup_expr='exact')

    class Meta:
        model = User
        fields = ['created_at', 'current_level', 'head_user'
                  ]
