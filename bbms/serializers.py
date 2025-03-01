from rest_framework import serializers
from django_currentuser.middleware import get_current_authenticated_user
from authentication.serializers import AdminUserMinimalListSerializer
from member.serializers import MemberSerializer,MemberListSerializer,MemberMinimalListSerializer
from .models import *
from django.utils import timezone
from django.db import transaction
import re
class BusMinimalListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bus
        fields =['id','name']



class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = '__all__'
    
    def create(self, validated_data):
        modelObject = super().create(validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.created_by = user
        modelObject.save()
        return modelObject
    
    def update(self, instance, validated_data):
        modelObject = super().update(instance=instance, validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.updated_by = user
        modelObject.save()
        return modelObject


class BusListSerializer(serializers.ModelSerializer):
    created_by = AdminUserMinimalListSerializer()


    class Meta:
        model = Bus
   
        exclude =['itinerary']
        extra_kwargs = {
            'created_at': {
                'read_only': True,
            },
            'updated_at': {
                'read_only': True,
            },
            'created_by': {
                'read_only': True,
            },
            'updated_by': {
                'read_only': True,
            },
        }
class PassengerMinimalListSerializer(serializers.ModelSerializer):
   class Meta:
      model = Passenger
      fields = ['first_name','last_name']


class PassengerListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Passenger
        fields = '__all__'
        extra_kwargs = {
            'created_at': {
                'read_only': True,
            },
            'updated_at': {
                'read_only': True,
            },
            'created_by': {
                'read_only': True,
            },
            'updated_by': {
                'read_only': True,
            },
        }

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else obj.created_by

    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else obj.updated_by

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = '__all__'
    
    def create(self, validated_data):
        modelObject = super().create(validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.created_by = user
        modelObject.save()
        return modelObject
    
    def update(self, instance, validated_data):
        modelObject = super().update(instance=instance, validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.updated_by = user
        modelObject.save()
        return modelObject

class BusBookingMinimalListSerializer(serializers.ModelSerializer):
    bus = BusListSerializer()
    passenger = PassengerMinimalListSerializer()
    # booking_summery = BookingSummaryMinimalListSerializer()
    member = MemberListSerializer()
    class Meta:
        model = BusBooking
        fields = ['bus','passenger','member','total_seat_count','total_discount_amount','total_cost','discount_type','discount_value','discount_percent','date','booking_time','seat_no','status'] 


class BusBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusBooking
        fields = '__all__'
    
    def create(self, validated_data):
        modelObject = super().create(validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.created_by = user
        modelObject.save()
        return modelObject
    
    def update(self, instance, validated_data):
        modelObject = super().update(instance=instance, validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.updated_by = user
        modelObject.save()
        return modelObject
   
class BusBookingListSerializer(serializers.ModelSerializer):
    bus = BusListSerializer()
    passenger = PassengerListSerializer()
    # booking_summery = BookingSummaryMinimalListSerializer()
    member = MemberListSerializer()
    class Meta:
        model = BusBooking
        fields = '__all__'
        extra_kwargs = {
            'created_at': {
                'read_only': True,
            },
            'updated_at': {
                'read_only': True,
            },
            'created_by': {
                'read_only': True,
            },
            'updated_by': {
                'read_only': True,
            },
        }

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else obj.created_by

    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else obj.updated_by
    def get_member(self, obj):
        # Import the MemberListSerializer inside the method to avoid circular import
        from member.serializers import MemberListSerializer
        return MemberListSerializer(obj.member).data
#
class AvailableDatesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableDates
        fields = '__all__'
        extra_kwargs = {
            'created_at': {
                'read_only': True,
            },
            'updated_at': {
                'read_only': True,
            },
            'created_by': {
                'read_only': True,
            },
            'updated_by': {
                'read_only': True,
            },
        }

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else obj.created_by

    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else obj.updated_by

class AvailableDatesMinimalListSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = AvailableDates
        fields =['id','name']




class AvailableDatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableDates
        fields = '__all__'
    
    def create(self, validated_data):
        modelObject = super().create(validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.created_by = user
        modelObject.save()
        return modelObject
    
    def update(self, instance, validated_data):
        modelObject = super().update(instance=instance, validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.updated_by = user
        modelObject.save()
        return modelObject

###########vsummery
class BookingSummaryMinimalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingSummary
        fields = '__all__'

class BookingSummaryMinimalListSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = BookingSummary
        fields =['id','name']




class BookingSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = BookingSummary
        fields = '__all__'
    
    def create(self, validated_data):
        modelObject = super().create(validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.created_by = user
        modelObject.save()
        return modelObject
    
    def update(self, instance, validated_data):
        modelObject = super().update(instance=instance, validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.updated_by = user
        modelObject.save()
        return modelObject
    



class BookingSummaryListSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()
    bus_booking = BusBookingSerializer

    class Meta:
        model = BookingSummary
        fields = '__all__'
        extra_kwargs = {
            'created_at': {
                'read_only': True,
            },
            'updated_at': {
                'read_only': True,
            },
            'created_by': {
                'read_only': True,
            },
            'updated_by': {
                'read_only': True,
            },
        }

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else obj.created_by

    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else obj.updated_by
    def get_member(self, obj):
        # Import the MemberListSerializer inside the method to avoid circular import
        from member.serializers import MemberListSerializer
        return MemberListSerializer(obj.member).data
    
class BookingSummaryMinimalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingSummary
        fields = '__all__'
