from django.conf import settings

from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from django_currentuser.middleware import get_current_authenticated_user

from authentication.serializers import AdminUserMinimalListSerializer
from member.serializers import MemberListSerializer, MemberMinimalSerializer,MemberMinimalListSerializer
from tour.models import *
from payments.models import Traveller

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
		fields = ('id','name',)




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
    agent = MemberListSerializer(read_only=True)  # Show full agent details when retrieving
    agent_id = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(), source="agent", write_only=True
    )  # Accept agent ID when saving

    tour = TourContentListSerializer(read_only=True)  # Show full tour details when retrieving
    tour_id = serializers.PrimaryKeyRelatedField(
        queryset=TourContent.objects.all(), source="tour", write_only=True
    )  # Accept tour ID when saving

    # traveler = serializers.PrimaryKeyRelatedField(queryset=Traveller.objects.all())

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

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else None

    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else None



 



# class TourBookingMinimalSerializer(serializers.ModelSerializer):
# 	agent = MemberMinimalListSerializer
# 	tour = TourContentMinimalSerializer
# 	class Meta:
# 		model = TourBooking
# 		fields = ('id','adult_price', 'youth_price','child_price','total_price','total_discount_amount','discount_percent','discount_value',
# 			'discount_type','participants','selected_date','selected_time','payWithCash','payWithStripe','duration','is_agent','status',
# 			'agent')


class TourBookingMinimalSerializer(serializers.ModelSerializer):
    agent = MemberMinimalListSerializer(read_only=True)  # Nested Serializer for Agent
    tour = TourContentMinimalSerializer(read_only=True)  # Nested Serializer for Tour
    traveler = serializers.SerializerMethodField()
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

    def get_traveler(self, obj):
        """Returns traveler name if available."""
        return obj.traveller.first_name if obj.traveller else None

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else None

    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else None


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
	


