from django.conf import settings
from authentication.serializers import AdminUserMinimalListSerializer
# from bbms.serializers import BusBookingMinimalListSerializer
from rest_framework import serializers

from django_currentuser.middleware import get_current_authenticated_user
from support.models import *
from member.models import *


class MemberMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'first_name', 
                  'primary_phone', 'username']



class MemberListSerializer(serializers.ModelSerializer):
    # bus_booking = BusBookingMinimalListSerializer
    created_by = MemberMinimalSerializer()
    updated_by = MemberMinimalSerializer()

    class Meta:
        model = Member
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



class MemberMinimalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'first_name', 'last_name', 'email','username','ref_no']


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
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


# Promoter

class PromoterMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promoter
        fields = ['id', 'first_name', 
                  'primary_phone', 'username']



class PromoterListSerializer(serializers.ModelSerializer):
 
    created_by = PromoterMinimalSerializer()
    updated_by = PromoterMinimalSerializer()

    class Meta:
        model = Promoter
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


class PromoterMinimalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promoter
        fields = ['id', 'agent','first_name', 'last_name', 'email', 'profession', 'primary_phone', 'father_name', 'mother_name',
                  'username', 'image', 'street_address_one', 'street_address_two']


class PromoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promoter
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
