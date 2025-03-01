import hashlib
import os
import random
import string
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view, permission_classes
from authentication.models import User
from donation.models import MemberAccountLog, PaymentMethod, Withdraw
from commons.pagination import Pagination
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from donation.serializers import WithdrawListSerializer, WithdrawSerializer
import datetime
from django.contrib.auth.hashers import make_password
from sequences import get_next_value
from decimal import Decimal
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from donation.serializers import WithdrawMinimalListSerializer
from member.models import Member
from django.utils.translation import gettext_lazy as _
from django.db.models import Q


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=WithdrawSerializer,
    responses=WithdrawSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_LIST.name])
def getAllWithdraw(request):
    withdraws = Withdraw.objects.all().order_by('-created_at')
    total_elements = withdraws.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    withdraws = pagination.paginate_data(withdraws)

    serializer = WithdrawListSerializer(withdraws, many=True)

    response = {
        'withdraws': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=WithdrawSerializer, responses=WithdrawSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DETAILS.name])
def getAWithdraw(request, pk):
    try:
        withdraw = Withdraw.objects.get(pk=pk)
        serializer = WithdrawListSerializer(withdraw)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Withdraw id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=WithdrawSerializer, responses=WithdrawSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createWithdraw(request):
    data = request.data
    date = data.get('date')
    withdraw_amount = data.get('withdraw_amount')
    payment_method_id = data.get('payment_method')
    payment_number = data.get('payment_number')

    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)
    current_date = datetime.date.today()
    current_date = str(current_date)
    current_date = current_date.replace('-', '')
    cv_current_date = 'WI' + current_date
    _num = get_next_value(cv_current_date)
    invoice = 'WI' + current_date + '00' + str(_num)
    filtered_data['invoice'] = invoice
    serializer = WithdrawSerializer(data=filtered_data)

    if serializer.is_valid():
        serializer.save()
        user = request.user
        credit_amount = 0
        payment_method_obj = PaymentMethod.objects.get(id=payment_method_id)
        MemberAccountLog.objects.create(user=user, payment_number=payment_number, date=date, payment_method=payment_method_obj,
                                        debit_amount=withdraw_amount, credit_amount=credit_amount)
        return Response(serializer.data)
    else:
        return Response(serializer.errors)


@extend_schema(request=WithdrawSerializer, responses=WithdrawSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
def updateWithdraw(request, pk):
    data = request.data
    print('data :', data)
    filtered_data = {}

    try:
        withdraw_obj = Withdraw.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response({'detail': f"Withdraw id - {pk} doesn't exists"})

    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    serializer = WithdrawSerializer(withdraw_obj, data=filtered_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors)


@extend_schema(request=WithdrawSerializer, responses=WithdrawSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DELETE.name])
def deleteWithdraw(request, pk):
    try:
        withdraw = Withdraw.objects.get(pk=pk)
        withdraw.delete()
        return Response({'detail': f'withdraw id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"withdraw id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=WithdrawSerializer, responses=WithdrawSerializer)
@api_view(['GET'])
def getAllIWithdrawByInvoice(request):
    keyword = request.query_params.get('keyword')
    if keyword:
        withdrws = Withdraw.objects.filter(Q(invoice__icontains=keyword))
    else:
        withdrws = Withdraw.objects.all()
    serializer = WithdrawMinimalListSerializer(withdrws, many=True)

    response = {
        'withdraws': serializer.data,
    }

    if len(withdrws) > 0:
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"There are no invoices matching your search"}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(request=WithdrawSerializer, responses=WithdrawSerializer)
@api_view(['GET'])
def getAllIWithdrawByUserId(request, user_id):
    keyword = []
    try:
        withdraw_obj = Withdraw.objects.filter(user=user_id)
        serializer = WithdrawMinimalListSerializer(withdraw_obj, many=True)

        for obj in serializer.data:
            keyword.append(obj)
        response = {
            "withdraws": keyword
        }
        return Response(response, status=status.HTTP_200_OK)
    except Withdraw.DoesNotExist:
        return Response({'detail': f"Item {user_id} doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
