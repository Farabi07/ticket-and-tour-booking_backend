from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sequences import get_next_value

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import AccountLog, LedgerAccount, ReceiptVoucher, Sales
from donation.models import Cause

from commons.enums import PermissionEnum
from commons.pagination import Pagination

import datetime


# Create your views here.

@extend_schema()
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_CREATE.name])
def createCauseDonation(request):
    data = request.data
    print('data: ', data)
    user = request.user
    cause_id = data['cause']
    amount = Decimal(data['amount'])

    cash_ledger = LedgerAccount.objects.get(name='Cash')
    user_ledger = LedgerAccount.objects.get(reference_id=user.id)

    ref_invoice_no = Sales.objects.get(
        ledger__reference_id=cause_id).invoice_no

    cause_obj = Cause.objects.get(pk=cause_id)
    cause_obj.raised_amount += amount
    cause_obj.save()

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

    ReceiptVoucher.objects.create(ledger=cash_ledger, invoice_no=invoice,
                                  ref_invoice_no=ref_invoice_no, debit_amount=amount, receipt_date=current_datetime)
    ReceiptVoucher.objects.create(ledger=user_ledger, invoice_no=invoice,
                                  ref_invoice_no=ref_invoice_no, credit_amount=amount, receipt_date=current_datetime)

    AccountLog.objects.create(ledger=cash_ledger, reference_no=invoice,
                              debit_amount=amount, log_date=current_datetime, log_type='receipt_voucher')
    AccountLog.objects.create(ledger=user_ledger, reference_no=invoice,
                              credit_amount=amount, log_date=current_datetime, log_type='receipt_voucher')

    return Response(status=status.HTTP_201_CREATED)


@extend_schema()
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_UPDATE.name])
def updateCauseDonation(request, pk):
    data = request.data
    print('data: ', data)

    return Response(status=status.HTTP_200_OK)
