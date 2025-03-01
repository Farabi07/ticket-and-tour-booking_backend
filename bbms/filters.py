from cgitb import lookup
from dataclasses import field
from bbms.models import BusBooking,BookingSummary
from django_filters import rest_framework as filters
from rest_framework import serializers

class BusBookingFilter(filters.FilterSet):
    member = filters.CharFilter(field_name="member", lookup_expr='exact')
    passenger = filters.CharFilter(field_name="passenger", lookup_expr='exact')
    bus = filters.CharFilter(field_name="bus", lookup_expr='exact')
    booking_time = filters.CharFilter(field_name="booking_time", lookup_expr='exact')
    date_after = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_before = filters.DateFilter(field_name='date', lookup_expr='lte')
   
    class Meta:
        model = BusBooking
        fields = ['member', 'date_after', 'date_before', 'passenger', 'bus','booking_time',]

class BookingSummaryFilter(filters.FilterSet):
    member = filters.CharFilter(field_name="member__id", lookup_expr='exact')
    bus = filters.CharFilter(field_name="bus__id", lookup_expr='exact')
    date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = BookingSummary
        fields = ['member', 'bus', 'date_after', 'date_before']