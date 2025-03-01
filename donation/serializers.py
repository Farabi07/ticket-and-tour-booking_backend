from django.conf import settings

from authentication.models import User
from authentication.serializers import AdminUserMinimalListSerializer

from rest_framework import serializers

from django_currentuser.middleware import get_current_authenticated_user

from rest_framework_recursive.fields import RecursiveField

from donation.models import *
from member.serializers import LevelMinimalListSerializer, MemberMinimalListSerializer, MemberMinimalSerializer


class CauseListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    process = serializers.ReadOnlyField()
    contributor = serializers.ReadOnlyField()

    class Meta:
        model = Cause
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


class UserMinimalSerializer(serializers.ModelSerializer):
    current_level = LevelMinimalListSerializer()

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name",
                  "image", "refer_id", "current_level"]


class CauseMinimalSerializer(serializers.ModelSerializer):
    created_by = UserMinimalSerializer()
    process = serializers.ReadOnlyField()
    contributor = serializers.ReadOnlyField()

    class Meta:
        model = Cause
        fields = "__all__"


class CauseSerializer(serializers.ModelSerializer):
    process = serializers.ReadOnlyField()
    contributor = serializers.ReadOnlyField()

    class Meta:
        model = Cause
        fields = ['id', 'name', 'goal_amount',
                  'image', 'process', 'contributor']

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


class CauseContentListSerializer(serializers.ModelSerializer):
    cause = CauseMinimalSerializer()
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CauseContent
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


class CauseContentMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CauseContent
        fields = ('id', 'cause', 'name', 'value')


class CauseContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CauseContent
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


class CauseContentImageListSerializer(serializers.ModelSerializer):
    cause = CauseMinimalSerializer()
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CauseContentImage
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


class CauseContentImageMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CauseContent
        fields = ('id', 'cause', 'head', 'image')


class CauseContentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CauseContentImage
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


class PaymentMethodMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'


class PaymentMethodListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PaymentMethod
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


class PaymentMethodMinimalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name']
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


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
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


class PaymentMethodDetailMinimalSerializer(serializers.ModelSerializer):
    payment_method = PaymentMethodMinimalSerializer()

    class Meta:
        model = PaymentMethodDetail
        fields = '__all__'


class PaymentMethodDetailListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PaymentMethodDetail
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


class PaymentMethodDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentMethodDetail
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


class DonationListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    cause = CauseMinimalSerializer()
    member = MemberMinimalSerializer()
    payment_method_detail = PaymentMethodDetailMinimalSerializer()

    class Meta:
        model = Donation
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


class DonationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Donation
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


class MonthlySubscriptionListSerializer(serializers.ModelSerializer):
    member = MemberMinimalListSerializer()
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MonthlySubscription
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


class MonthlySubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlySubscription
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


class CollectionListSerializer(serializers.ModelSerializer):
    # children = RecursiveField(many=True)

    class Meta:
        model = Collection
        fields = '__all__'


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
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


class LevelMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
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


class LevelListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Level
        fields = '__all__'


class GiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gift
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


class GiftListSerializer(serializers.ModelSerializer):
    # level = LevelMinimalSerializer()

    class Meta:
        model = Gift
        fields = '__all__'


class GiftListMinimalSerializer(serializers.ModelSerializer):
    level = LevelMinimalSerializer()

    class Meta:
        model = Gift
        fields = '__all__'


class MemberAccountLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberAccountLog
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


class MemberAccountLogListSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer()

    class Meta:
        model = MemberAccountLog
        fields = '__all__'


class GiftLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftLog
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


class GiftLogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftLog
        fields = '__all__'


class WithdrawMinimalListSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer()
    payment_method = PaymentMethodListSerializer()

    class Meta:
        model = Withdraw

        fields = ['id', 'invoice', 'date', 'payment_number', 'status', 'withdraw_amount',
                  'created_at', 'user', 'payment_method', 'created_by']


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
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


class WithdrawListSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer()
    payment_method = PaymentMethodListSerializer()

    class Meta:
        model = Withdraw
        fields = '__all__'


class UserDetailsSerializer(serializers.ModelSerializer):
    head_user = UserMinimalSerializer()

    class Meta:
        model = Member
        fields = ['id', 'first_name', 'username', 'refer_id', 'nid', 'primary_phone',
                  'street_address_one', 'collection_amount', 'head_user', 'total_amount']
