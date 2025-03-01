import hashlib
import os
import random
import string
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view, permission_classes
from authentication.models import User
from donation.models import Cause, Collection, Gift, Level, MemberAccountLog, PaymentMethod, PaymentMethodDetail
from commons.pagination import Pagination
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from donation.serializers import CollectionListSerializer, CollectionSerializer, GiftListSerializer, GiftSerializer, MemberAccountLogListSerializer, MemberAccountLogSerializer
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
    request=MemberAccountLogSerializer,
    responses=MemberAccountLogSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_LIST.name])
def getAllMemberAccountLog(request):
    member_account_logs = MemberAccountLog.objects.all()
    total_elements = member_account_logs.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    member_account_logs = pagination.paginate_data(member_account_logs)

    serializer = MemberAccountLogListSerializer(member_account_logs, many=True)

    response = {
        'member_account_logs': serializer.data,
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
def getAllMemberAccountLogWithoutPagination(request):
    member_account_logs = MemberAccountLog.objects.all()
    print('member_account_logs: ', member_account_logs)

    serializer = MemberAccountLogListSerializer(member_account_logs, many=True)

    response = {
        'member_account_logs': serializer.data,

    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=GiftSerializer, responses=GiftSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DETAILS.name])
def getAMemberAccountLog(request, pk):
    try:
        member_account_log = MemberAccountLog.objects.get(pk=pk)
        serializer = MemberAccountLogListSerializer(member_account_log)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"MemberAccountLog id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=MemberAccountLogSerializer, responses=MemberAccountLogSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createMemberAccountLog(request):
    data = request.data
    print('data: ', data)
    print('content_type: ', request.content_type)

    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    serializer = MemberAccountLogSerializer(data=filtered_data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors)


@extend_schema(request=MemberAccountLogSerializer, responses=MemberAccountLogSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
def updateMemberAccountLog(request, pk):
    data = request.data
    print('data :', data)
    filtered_data = {}

    try:
        member_account_log = MemberAccountLog.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response({'detail': f"member_account_log id - {pk} doesn't exists"})

    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    serializer = MemberAccountLogSerializer(
        member_account_log, data=filtered_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors)


@extend_schema(request=MemberAccountLogSerializer, responses=MemberAccountLogSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DELETE.name])
def deleteMemberAccountLog(request, pk):
    try:
        member_account_log = MemberAccountLog.objects.get(pk=pk)
        member_account_log.delete()
        return Response({'detail': f'member_account_log id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"member_account_log id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
