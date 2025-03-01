import hashlib
import os

from coreschema import Null
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from psycopg2 import IntegrityError

from authentication.models import User
from authentication.serializers import AdminUserSerializer

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sequences import get_next_value

from drf_spectacular.utils import extend_schema, OpenApiParameter

from account.models import AccountLog, Group, LedgerAccount, ReceiptVoucher
from authentication.decorators import has_permissions

from donation.models import Donation, PaymentMethod, PaymentMethodDetail, Cause
from donation.serializers import DonationSerializer, DonationListSerializer
from donation.filters import DonationFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination

import datetime
from decimal import Decimal

# Create your views here.
from member.models import Member


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=DonationSerializer,
    responses=DonationSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_LIST.name])
def getAllDonation(request):
    donations = Donation.objects.all()
    total_elements = donations.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    donations = pagination.paginate_data(donations)

    serializer = DonationListSerializer(donations, many=True)

    response = {
        'donations': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=DonationSerializer, responses=DonationSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DETAILS.name])
def getADonation(request, pk):
    try:
        donation = Donation.objects.get(pk=pk)
        serializer = DonationListSerializer(donation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Donation id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=DonationSerializer, responses=DonationSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchDonation(request):
    donations = DonationFilter(request.GET, queryset=Donation.objects.all())
    donations = donations.qs

    print('searched_products: ', donations)

    total_elements = donations.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    donations = pagination.paginate_data(donations)

    serializer = DonationListSerializer(donations, many=True)

    response = {
        'donations': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    if len(donations) > 0:
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"There are no donations matching your search"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=DonationSerializer, responses=DonationSerializer)
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_CREATE.name])
def createDonation(request):
    data = request.data
    print('data: ', data)
    filtered_data = {}
    restricted_values = ('', ' ', 0, '0', 'undefined')
    member_obj = None

    for key, value in data.items():
        if value not in restricted_values:
            filtered_data[key] = value

    first_name = filtered_data.get('first_name', '')
    last_name = filtered_data.get('last_name', '')
    email = filtered_data.get('email', '')
    country_code = filtered_data.get('country_code', '')
    phone_number = filtered_data.get('phone_number', '')
    message = filtered_data.get('message', '')
    address = filtered_data.get('address', '')

    member_id = filtered_data.get('member_id', None)
    cause_id = filtered_data.get('cause', None)
    amount = Decimal(filtered_data.get('amount', 0))
    payment_method_id = filtered_data.get("payment_method", None)
    card_holder = filtered_data.get('card_holder', '')
    card_number = filtered_data.get('card_number', '')
    cvc_code = filtered_data.get('cvc_code', '')
    expiry_date = filtered_data.get('expiry_date', '')
    payment_number = filtered_data.get('payment_number', '')
    offline = filtered_data.get('offline', '')
    full_number = country_code + phone_number
    print('amount: ', amount, type(amount))

    if member_id:
        print("member_id:", member_id)
        member_obj = Member.objects.get(id=member_id)
    else:
        try:
            member_obj = Member.objects.get(email=email)
        except User.DoesNotExist:
            try:
                member_obj = Member.objects.get(primary_phone=full_number)
            except User.DoesNotExist:
                full_number = country_code + phone_number
                password = hashlib.md5(os.urandom(32)).hexdigest()
                member_obj = Member.objects.create_user(first_name=first_name, last_name=last_name, email=email, password=password)
                member_obj.street_address_one = address
                member_obj.primary_phone = full_number
                member_obj.is_active = True
                member_obj.save()

    payment_method_obj = PaymentMethod.objects.get(id=payment_method_id)
    cause_obj = Cause.objects.get(id=cause_id)

    payment_method_detail_obj = PaymentMethodDetail.objects.create(payment_method=payment_method_obj, cause=cause_obj, member=member_obj,
                                        offline=offline, card_number=card_number, card_holder=card_holder,
                                        cvc_code=cvc_code, expiry_date=expiry_date, payment_number=payment_number)
    
    donation_obj = Donation.objects.create(cause=cause_obj, member=member_obj, payment_method_detail=payment_method_detail_obj,
                                            amount=amount, message=message)

    cause_obj.raised_amount += amount
    cause_obj.save()
    print('raised_amount:', cause_obj.raised_amount)

    group_obj = Group.objects.get(name='Sundry Creditors')
    user_id = member_obj.id
    user_ledger, created = LedgerAccount.objects.get_or_create(reference_id=user_id,
                                                                defaults={'name': first_name,
                                                                "head_group": group_obj,
                                                                'ledger_type': 'user_ledger'}
                                                            )
    current_datetime = str(timezone.now())

    current_date = datetime.date.today()
    current_date = str(current_date)
    current_date = current_date.replace('-', '')
    rv_current_date = 'RV' + current_date
    print('current_date: ', current_date, type(current_date))

    _num = get_next_value(rv_current_date)
    print('get_next_value: ', _num)

    invoice = 'RV' + current_date + '00' + str(_num)
    print('invoice: ', invoice)

    cash_ledger, clcreated = LedgerAccount.objects.get_or_create(name='Cash')
    ReceiptVoucher.objects.create(ledger=cash_ledger, invoice_no=invoice, debit_amount=amount,
                                    receipt_date=current_datetime)
    ReceiptVoucher.objects.create(ledger=user_ledger, invoice_no=invoice, credit_amount=amount,
                                    receipt_date=current_datetime)

    AccountLog.objects.create(ledger=cash_ledger, reference_no=invoice, debit_amount=amount,
                                log_date=current_datetime, log_type='receipt_voucher')
    AccountLog.objects.create(ledger=user_ledger, reference_no=invoice, credit_amount=amount,
                                log_date=current_datetime, log_type='receipt_voucher')

    serializer = DonationSerializer(donation_obj, data=filtered_data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)




@extend_schema(request=DonationSerializer, responses=DonationSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_UPDATE.name])
def updateDonation(request, pk):
    data = request.data
    print('data: ', data)
    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0' and value != 'undefined':
            filtered_data[key] = value

    try:
        donation = Donation.objects.get(pk=pk)

        serializer = DonationSerializer(donation, data=filtered_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'detail': f"Donation id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=DonationSerializer, responses=DonationSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DELETE.name])
def deleteDonation(request, cause_id, pk):
    try:
        donation = Donation.objects.get(pk=pk)
        donation.delete()
        cause_obj = Cause.objects.get(id=cause_id)
        cause_obj.raised_amount -= donation.amount
        cause_obj.save() 
        return Response({'detail': f'Donation id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Donation id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)

