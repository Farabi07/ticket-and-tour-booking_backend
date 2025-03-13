from django_filters import rest_framework as filters

from tour.models import *

import django_filters
from .models import TourBooking



class TourBookingFilter(django_filters.FilterSet):

    agent = django_filters.CharFilter(field_name="agent__id", lookup_expr='exact')
    tour = django_filters.CharFilter(field_name="tour__id", lookup_expr='exact')
    # Date filters for 'created_at'
    date_after = django_filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='created_at__date', lookup_expr='lte')
    is_agent = django_filters.BooleanFilter(field_name="is_agent", lookup_expr='exact', method='filter_is_agent')
    class Meta:
        model = TourBooking
        fields = ['agent', 'tour','date_after', 'date_before','is_agent']  # Ensure only valid model fields


# class BookingSummaryFilter(filters.FilterSet):
#     member = filters.CharFilter(field_name="member__id", lookup_expr='exact')
#     bus = filters.CharFilter(field_name="bus__id", lookup_expr='exact')
#     date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
#     date_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')

#     class Meta:
#         model = BookingSummary
#         fields = ['member', 'bus', 'date_after', 'date_before']