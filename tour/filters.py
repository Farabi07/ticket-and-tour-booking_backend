from django_filters import rest_framework as filters
from tour.models import *
from .models import TourBooking
import django_filters
from .models import TourBooking

class TourBookingFilter(django_filters.FilterSet):
    agent = filters.CharFilter(field_name="agent__id", lookup_expr='exact')
    tour = filters.CharFilter(field_name="tour__id", lookup_expr='exact')
    date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = TourBooking
        fields = ['agent', 'tour', 'date_after', 'date_before']



# class BookingSummaryFilter(filters.FilterSet):
#     member = filters.CharFilter(field_name="member__id", lookup_expr='exact')
#     bus = filters.CharFilter(field_name="bus__id", lookup_expr='exact')
#     date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
#     date_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')

#     class Meta:
#         model = BookingSummary
#         fields = ['member', 'bus', 'date_after', 'date_before']