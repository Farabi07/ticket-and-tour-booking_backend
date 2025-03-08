from rest_framework import serializers

from tour.serializers import TourBookingMinimalSerializer
from .models import Payment, Currency
from django_currentuser.middleware import get_current_authenticated_user
from authentication.serializers import AdminUserMinimalListSerializer


class CurrencyListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Currency
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'created_by': {'read_only': True},
            'updated_by': {'read_only': True},
        }

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else None

    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else None


class CurrencyMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

    def create(self, validated_data):
        model_object = super().create(validated_data=validated_data)
        user = get_current_authenticated_user()
        if user:
            model_object.created_by = user
        model_object.save()
        return model_object

    def update(self, instance, validated_data):
        model_object = super().update(instance=instance, validated_data=validated_data)
        user = get_current_authenticated_user()
        if user:
            model_object.updated_by = user
        model_object.save()
        return model_object


class PaymentListSerializer(serializers.ModelSerializer):
    agent_id = serializers.CharField(required=False, allow_null=True, write_only=True)  # Optional field
    created_by = AdminUserMinimalListSerializer()
    updated_by = AdminUserMinimalListSerializer()
    traveller = serializers.SerializerMethodField()
    tour = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    currency = CurrencyListSerializer()

    class Meta:
        model = Payment
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'created_by': {'read_only': True},
            'updated_by': {'read_only': True},
        }

    def get_traveller(self, obj):
        return obj.traveller.first_name + " " + obj.traveller.last_name

    def get_tour(self, obj):
        return obj.tour.name

    def get_currency(self, obj):
        return obj.currency.currency_code

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else None


class PaymentMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    agent_id = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Payment
        fields = '__all__'

    def create(self, validated_data):
        model_object = super().create(validated_data=validated_data)
        user = get_current_authenticated_user()
        if user:
            model_object.created_by = user
        # Check if agent_id is provided and set it
        agent_id = validated_data.get('agent_id', None)
        if agent_id:
            model_object.agent_ref_no = agent_id  # Assuming agent_ref_no is being used as agent_id
        model_object.save()
        return model_object

    def update(self, instance, validated_data):
        model_object = super().update(instance=instance, validated_data=validated_data)
        user = get_current_authenticated_user()
        if user:
            model_object.updated_by = user
        # Update agent_id if it's provided
        agent_id = validated_data.get('agent_id', None)
        if agent_id:
            model_object.agent_ref_no = agent_id  # Again assuming this is the right field
        model_object.save()
        return model_object

