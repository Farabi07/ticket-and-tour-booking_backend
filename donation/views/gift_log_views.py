import hashlib
import os
import random
import string
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view, permission_classes
from authentication.models import User
from donation.models import Cause, Collection, Gift, GiftLog, Level, PaymentMethod, PaymentMethodDetail
from commons.pagination import Pagination
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from donation.serializers import CollectionListSerializer, CollectionSerializer, GiftListSerializer, GiftLogListSerializer, GiftLogSerializer, GiftSerializer
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
    request=GiftLogSerializer,
    responses=GiftLogSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_LIST.name])
def getAllGiftLog(request):
    gift_logs = GiftLog.objects.all()
    total_elements = gift_logs.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    gift_logs = pagination.paginate_data(gift_logs)

    serializer = GiftLogListSerializer(gift_logs, many=True)

    response = {
        'gift_logs': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=GiftLogSerializer, responses=GiftLogSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllGiftLogWithoutPagination(request):
    gift_logs = GiftLog.objects.all()
    print('gifts_log: ', gift_logs)

    serializer = GiftLogListSerializer(gift_logs, many=True)

    response = {
        'gifts_log': serializer.data,

    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=GiftLogSerializer, responses=GiftLogSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DETAILS.name])
def getAGiftLog(request, pk):
    try:
        gift_log = Gift.objects.get(pk=pk)
        serializer = GiftLogListSerializer(gift_log)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Gift Log id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=GiftLogSerializer, responses=GiftLogSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createGiftLog(request):
    data = request.data
    print('data: ', data)
    print('content_type: ', request.content_type)

    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    serializer = GiftLogSerializer(data=filtered_data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors)


@extend_schema(request=GiftLogSerializer, responses=GiftLogSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
def updateGiftLog(request, pk):
    data = request.data
    print('data :', data)
    filtered_data = {}

    try:
        gift_log_obj = GiftLog.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response({'detail': f"Gift Log id - {pk} doesn't exists"})

    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    serializer = GiftLogSerializer(gift_log_obj, data=filtered_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors)


@extend_schema(request=GiftLogSerializer, responses=GiftLogSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DELETE.name])
def deleteGiftLog(request, pk):
    try:
        gift_log = GiftLog.objects.get(pk=pk)
        gift_log.delete()
        return Response({'detail': f'gift log id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"gift log id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
