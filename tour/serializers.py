from django.conf import settings

from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from django_currentuser.middleware import get_current_authenticated_user

from authentication.serializers import AdminUserMinimalListSerializer
from tour.models import *
from payments.serializers import PaymentListSerializer
class TourContentListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    cloudflare_image = serializers.SerializerMethodField()
    class Meta:
        model = TourContent
        fields = '__all__'
        extra_kwargs = {
            'created_at':{
                'read_only': True,
            },
            'updated_at':{
                'read_only': True,
            },
            'created_by':{
                'read_only': True,
            },
            'updated_by':{
                'read_only': True,
            },
        }

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else obj.created_by
        
    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else obj.updated_by
 
    def get_cloudflare_image(self, obj):
        images = TourContentImage.objects.filter(tour_content= obj.id)
        return [
			{ 	"image " :image.image.url if image.image else None,
                'cloudflare_image': image.cloudflare_image if image.cloudflare_image else None}
				for image in images
				]


class TourContentMinimalSerializer(serializers.ModelSerializer):
	class Meta:
		model = TourContent
		fields = ('id','name', 'value','order')




class TourContentSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = TourContent
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
	



class TourContentImageListSerializer(serializers.ModelSerializer):
	created_by = serializers.SerializerMethodField(read_only=True)
	updated_by = serializers.SerializerMethodField(read_only=True)
	class Meta:
		model = TourContentImage
		fields = '__all__'
		extra_kwargs = {
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}

	def get_created_by(self, obj):
		return obj.created_by.email if obj.created_by else obj.created_by
		
	def get_updated_by(self, obj):
		return obj.updated_by.email if obj.updated_by else obj.updated_by

class TourContentImageMinimalSerializer(serializers.ModelSerializer):
	class Meta:
		model = TourContentImage
		fields = ('id','head', 'image')

class TourContentImageSerializer(serializers.ModelSerializer):
	class Meta:
		model = TourContentImage
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

# TourBooking
class TourBookingListSerializer(serializers.ModelSerializer):
    agent = serializers.SerializerMethodField()
    tour = serializers.SerializerMethodField()
    traveler = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    payment = PaymentListSerializer()  # Fix instantiation
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TourBooking
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'created_by': {'read_only': True},
            'updated_by': {'read_only': True},
        }

    def get_agent(self, obj):
        """Returns agent reference number if available."""
        return obj.agent.ref_no if obj.agent else None

    def get_tour(self, obj):
        """Returns tour name if available."""
        return obj.tour.name if obj.tour else None

    def get_traveler(self, obj):
        """Returns traveler name if available."""
        return obj.traveller.first_name if obj.traveller else None  # Fix field name

    def get_currency(self, obj):
        """Returns currency code if available."""
        return obj.currency.currency_code if obj.currency else None  

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else None

    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else None




 



class TourBookingMinimalSerializer(serializers.ModelSerializer):
	class Meta:
		model = TourBooking
		fields = ('id','name', 'value','order')


class TourBookingSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = TourBooking
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
	


