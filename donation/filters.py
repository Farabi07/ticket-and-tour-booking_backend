from fileinput import filename
from unicodedata import category
from django.forms import fields
from django_filters import rest_framework as filters

from donation.models import *





class PaymentMethodFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = PaymentMethod
        fields = ['name', ]




class PaymentMethodDetailFilter(filters.FilterSet):
    order_no = filters.CharFilter(field_name="order__order_no", lookup_expr='icontains')

    class Meta:
        model = PaymentMethodDetail
        fields = ['order_no', ]




class DonationFilter(filters.FilterSet):
    first_name = filters.CharFilter(field_name="first_name", lookup_expr='icontains')
    last_name = filters.CharFilter(field_name="last_name", lookup_expr='icontains')

    class Meta:
        model = Donation
        fields = ['first_name', 'last_name', ]




class MonthlySubscriptionFilter(filters.FilterSet):
    member = filters.NumberFilter(field_name="member__pk", lookup_expr='exact')

    class Meta:
        model = MonthlySubscription
        fields = ['member', ]


