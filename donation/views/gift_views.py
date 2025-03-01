import faulthandler
import hashlib
from multiprocessing import Value
from django.db.models import F
from django.db.models import OuterRef
import os
import random
import string
from django.forms import IntegerField
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view, permission_classes
from authentication.models import User
from donation.models import Cause, Collection, Gift, GiftLog, Level, MemberAccountLog, PaymentMethod, PaymentMethodDetail
from commons.pagination import Pagination
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from donation.serializers import CollectionListSerializer, CollectionSerializer, GiftListMinimalSerializer, GiftListSerializer, GiftSerializer
import datetime
from django.contrib.auth.hashers import make_password
from sequences import get_next_value
from decimal import Decimal
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from member.models import Member
from django.utils.translation import gettext_lazy as _


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=GiftSerializer,
    responses=GiftSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_LIST.name])
def getAllGift(request):
    gifts = Gift.objects.all()
    total_elements = gifts.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    gifts = pagination.paginate_data(gifts)

    serializer = GiftListMinimalSerializer(gifts, many=True)

    response = {
        'gifts': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=GiftSerializer, responses=GiftSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllGiftWithoutPagination(request):
    gifts = Gift.objects.all()
    print('gifts: ', gifts)

    serializer = GiftListMinimalSerializer(gifts, many=True)

    response = {
        'gifts': serializer.data,

    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=GiftSerializer, responses=GiftSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DETAILS.name])
def getAGift(request, pk):
    try:
        gift = Gift.objects.get(pk=pk)
        serializer = GiftListSerializer(gift)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Gift id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=GiftSerializer, responses=GiftSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createGift(request):
    data = request.data
    level = data.get('level')
    amount = data.get('amount')
    print('data: ', data)
    print('content_type: ', request.content_type)

    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    serializer = GiftSerializer(data=filtered_data)

    if serializer.is_valid():
        serializer.save()
        level_obj = Level.objects.get(id=level)
        level_of_gift = Level.objects.get(id__gte=3)
        current_date = datetime.date.today()
        debit_amount = 0
        if level == level_of_gift:
            GiftLog.objects.create(
                level=level_obj, gift_amount=amount, date=current_date)
            MemberAccountLog.objects.create(
                date=current_date, debit_amount=debit_amount, credit_amount=amount)
        return Response(serializer.data)
    else:
        return Response(serializer.errors)


@extend_schema(request=GiftSerializer, responses=GiftSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
def updateGift(request, pk):
    data = request.data
    print('data :', data)
    filtered_data = {}

    try:
        gift_obj = Gift.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response({'detail': f"Gift id - {pk} doesn't exists"})

    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    serializer = GiftSerializer(gift_obj, data=filtered_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors)


@extend_schema(request=GiftSerializer, responses=GiftSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DELETE.name])
def deleteGift(request, pk):
    try:
        gift = Gift.objects.get(pk=pk)
        gift.delete()
        return Response({'detail': f'gift id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"gift id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=GiftSerializer, responses=GiftSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DETAILS.name])
def ListAllChildrenofParent(request, parent_id):
    results = []
    user_obj = User.objects.filter(head_user=parent_id)
    for obj in user_obj:
        result = User.objects.values(
            'first_name', 'last_name', "current_level")
        results.append(result)
    return Response(results)
