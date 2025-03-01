from re import A

from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from authentication.models import Branch

from sequences import get_next_value

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import LedgerAccount, PaymentVoucher, AccountLog, SubLedgerAccount
from account.serializers import PaymentVoucherListCustomSerializer, PaymentVoucherSerializer, PaymentVoucherListSerializer, AccountLogSerializer, AccountLogListSerializer

from account.filters import AccountLogFilter, PaymentVoucherFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination

from datetime import date
from datetime import datetime
from decimal import Decimal


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=PaymentVoucherSerializer,
    responses=PaymentVoucherSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_ITEM_LIST.name])
def getAllPaymentVoucher(request):
    distinct_payment_vouchers = PaymentVoucher.objects.filter(
        ledger__name__in=['Cash', 'Bank']).order_by('-invoice_no').distinct('invoice_no')
    total_elements = distinct_payment_vouchers.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    payment_vouchers = distinct_payment_vouchers
    print('payment_vouchers: ', payment_vouchers)
    payment_vouchers = pagination.paginate_data(distinct_payment_vouchers)

    response_list = []

    if len(payment_vouchers) > 0:
        for payment_voucher in payment_vouchers:
            payment_voucher_dict = {}
            invoice_no = payment_voucher.invoice_no
            payment_voucher_serializer = PaymentVoucherListCustomSerializer(
                payment_voucher)
            for key, value in payment_voucher_serializer.data.items():
                payment_voucher_dict[key] = value
            related_payment_vouchers = PaymentVoucher.objects.filter(
                invoice_no=invoice_no).exclude(pk=payment_voucher.id)
            print('related_payment_vouchers: ', related_payment_vouchers)
            if len(related_payment_vouchers) == 1:
                related_payment_voucher = related_payment_vouchers[0]
                payment_voucher_dict['related_ledgers'] = str(
                    related_payment_voucher.ledger.name)
            elif len(related_payment_vouchers) > 0:
                name_list = []
                for related_payment_voucher in related_payment_vouchers:
                    name_list.append(str(related_payment_voucher.ledger.name))
                payment_voucher_dict['related_ledgers'] = name_list
            response_list.append(payment_voucher_dict)

    response = {
        'payment_vouchers': response_list,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=PaymentVoucherSerializer,
    responses=PaymentVoucherSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_ITEM_LIST.name])
def getAllPaymentVoucherByInvoiceNo(request, invoice_no):
    response_data = {}
    response_data['items'] = []

    payment_vouchers = PaymentVoucher.objects.filter(invoice_no=invoice_no)
    payment_vouchers = payment_vouchers.reverse()
    print('payment_vouchers: ', payment_vouchers)

    if len(payment_vouchers):
        response_data['invoice_no'] = payment_vouchers[0].invoice_no

        if payment_vouchers[0].file and not str(payment_vouchers[0].file).startswith('/media/'):
            response_data['file'] = '/media/' + str(payment_vouchers[0].file)
        else:
            response_data['file'] = str(payment_vouchers[0].file)

        if payment_vouchers[0].sub_ledger:
            response_data['sub_ledger'] = {
                "id": payment_vouchers[0].sub_ledger.id, "name": payment_vouchers[0].sub_ledger.name}
        else:
            response_data['sub_ledger'] = None
        if payment_vouchers[0].branch:
            response_data['branch'] = {
                "id": payment_vouchers[0].branch.id, "name": payment_vouchers[0].branch.name}
        else:
            response_data['branch'] = None
        response_data['payment_date'] = payment_vouchers[0].payment_date
        response_data['details'] = payment_vouchers[0].details

        for payment_voucher in payment_vouchers:
            serializer = PaymentVoucherListSerializer(payment_voucher)
            response_data['items'].append(serializer.data)

        print('items: ', response_data['items'])

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"Invoice no {invoice_no} has no PaymentVouchers"})


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=PaymentVoucherSerializer,
    responses=PaymentVoucherSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_ITEM_LIST.name])
def getAllPaymentVoucherWithIdNameDictAgainstForeignKeyByInvoiceNo(request, invoice_no):
    response_data = {}
    response_data['items'] = []

    payment_vouchers = PaymentVoucher.objects.filter(invoice_no=invoice_no)
    payment_vouchers = payment_vouchers.reverse()
    print('payment_vouchers: ', payment_vouchers)

    response_data['invoice_no'] = payment_vouchers[0].invoice_no

    if payment_vouchers[0].file and not str(payment_vouchers[0].file).startswith('/media/'):
        response_data['file'] = '/media/' + str(payment_vouchers[0].file)
    else:
        response_data['file'] = str(payment_vouchers[0].file)

    if payment_vouchers[0].sub_ledger:
        response_data['sub_ledger'] = {
            "id": payment_vouchers[0].sub_ledger.id, "name": payment_vouchers[0].sub_ledger.name}
    else:
        response_data['sub_ledger'] = None
    if payment_vouchers[0].branch:
        response_data['branch'] = {
            "id": payment_vouchers[0].branch.id, "name": payment_vouchers[0].branch.name}
    else:
        response_data['branch'] = None
    response_data['payment_date'] = payment_vouchers[0].payment_date
    response_data['details'] = payment_vouchers[0].details

    for payment_voucher in payment_vouchers:
        serializer = PaymentVoucherListSerializer(payment_voucher)
        response_data['items'].append(serializer.data)

    print('items: ', response_data['items'])

    return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(request=PaymentVoucherSerializer, responses=PaymentVoucherSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_ITEM_DETAILS.name])
def getAPaymentVoucher(request, pk):
    try:
        payment_voucher = PaymentVoucher.objects.get(pk=pk)
        serializer = PaymentVoucherListSerializer(payment_voucher)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"PaymentVoucher id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PaymentVoucherSerializer, responses=PaymentVoucherSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchPaymentVoucher(request):
    invoice_no = request.query_params.get('invoice_no', None)
    payment_vouchers = PaymentVoucher.objects.filter(
        ledger__name__in=['Cash', 'Bank'], invoice_no=invoice_no)

    print('payment_vouchers: ', payment_vouchers)

    total_elements = payment_vouchers.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    payment_vouchers = pagination.paginate_data(payment_vouchers)

    response_list = []

    if len(payment_vouchers) > 0:
        for payment_voucher in payment_vouchers:
            payment_voucher_dict = {}
            invoice_no = payment_voucher.invoice_no
            payment_voucher_serializer = PaymentVoucherListCustomSerializer(
                payment_voucher)
            for key, value in payment_voucher_serializer.data.items():
                payment_voucher_dict[key] = value
            related_payment_vouchers = PaymentVoucher.objects.filter(
                invoice_no=invoice_no).exclude(pk=payment_voucher.id)
            print('related_payment_vouchers: ', related_payment_vouchers)
            if len(related_payment_vouchers) == 1:
                related_payment_voucher = related_payment_vouchers[0]
                payment_voucher_dict['related_ledgers'] = str(
                    related_payment_voucher.ledger.name)
            elif len(related_payment_vouchers) > 0:
                name_list = []
                for related_payment_voucher in related_payment_vouchers:
                    name_list.append(str(related_payment_voucher.ledger.name))
                payment_voucher_dict['related_ledgers'] = name_list
            response_list.append(payment_voucher_dict)

    response = {
        'payment_vouchers': response_list,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=PaymentVoucherSerializer, responses=PaymentVoucherSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_ITEM_CREATE.name])
def createPaymentVoucher(request):
    data = request.data
    print('data: ', data)

    file = data.get('file', None)
    branch = data.get('branch', None)
    sub_ledger = data.get('sub_ledger', None)
    details = data.get('details', None)
    payment_date = data.get('payment_date', None)
    payment_datetime = str(payment_date) + 'T' + str(datetime.now().time())
    print('payment_datetime: ', payment_datetime)

    branch_obj = None
    sub_ledger_obj = None
    if branch:
        branch_obj = Branch.objects.get(pk=branch)
    if sub_ledger:
        sub_ledger_obj = SubLedgerAccount.objects.get(pk=sub_ledger)

    current_date = date.today()
    current_date = str(current_date)
    current_date = current_date.replace('-', '')
    pv_current_date = 'PV' + current_date
    print('current_date: ', current_date, type(current_date))

    _num = get_next_value(pv_current_date)
    print('get_next_value: ', _num)

    invoice = 'PV' + current_date + '00' + str(_num)
    print('invoice: ', invoice)

    items = []
    for i in range(int(len(data) / 3)):
        ledger = data.get(f'items[{i}][ledger]', None)
        debit_amount = data.get(f'items[{i}][debit_amount]', None)
        credit_amount = data.get(f'items[{i}][credit_amount]', None)
        if ledger is not None and debit_amount is not None and credit_amount is not None:
            items.append(
                {'ledger': ledger, 'debit_amount': debit_amount, 'credit_amount': credit_amount})

    for payment_voucher in items:
        print('payment_voucher: ', payment_voucher)
        ledger = payment_voucher.get('ledger', None)
        debit_amount = Decimal(payment_voucher.get('debit_amount', None))
        credit_amount = Decimal(payment_voucher.get('credit_amount', None))

        ledger_obj = None
        if ledger:
            ledger_obj = LedgerAccount.objects.get(pk=ledger)

        payment_voucher_obj = PaymentVoucher.objects.create(
            ledger=ledger_obj,
            sub_ledger=sub_ledger_obj,
            branch=branch_obj,
            file=file,
            invoice_no=invoice,
            payment_date=payment_datetime,
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            details=details
        )

        account_log_obj = AccountLog.objects.create(
            log_type='payment_voucher',
            ledger=ledger_obj,
            sub_ledger=sub_ledger_obj,
            branch=branch_obj,
            reference_no=invoice,
            log_date=payment_datetime,
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            details=details
        )

    payment_voucher_objs = PaymentVoucher.objects.filter(invoice_no=invoice)
    payment_voucher_serializer = PaymentVoucherListSerializer(
        payment_voucher_objs, many=True)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice)
    account_log_serializer = AccountLogListSerializer(
        account_log_objs, many=True)

    response = {
        'payment_vouchers': payment_voucher_serializer.data,
        'account_logs': account_log_serializer.data
    }

    return Response(response, status=status.HTTP_201_CREATED)


@extend_schema(request=PaymentVoucherSerializer, responses=PaymentVoucherSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_ITEM_UPDATE.name])
def updatePaymentVoucher(request):
    data = request.data
    print('data: ', data)

    branch = data.get('branch', None)
    file = data.get('file', None)
    sub_ledger = data.get('sub_ledger', None)
    invoice_no = data.get('invoice_no', None)
    payment_date = str(data.get('payment_date', None))
    details = data.get('details', None)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice_no)
    print('account_log_objs: ', account_log_objs)

    payment_datetime = ""
    if 'T' in payment_date:
        payment_datetime = payment_date
        print('payment_datetime if: ', payment_datetime)
    else:
        payment_datetime = str(payment_date) + 'T' + str(datetime.now().time())
        print('payment_datetime else: ', payment_datetime)

    items = []
    for i in range(int(len(data) / 3)):
        id = data.get(f'items[{i}][id]', None)
        ledger = data.get(f'items[{i}][ledger]', None)
        debit_amount = data.get(f'items[{i}][debit_amount]', None)
        credit_amount = data.get(f'items[{i}][credit_amount]', None)
        if ledger is not None and debit_amount is not None and credit_amount is not None:
            items.append({'id': id, 'ledger': ledger,
                         'debit_amount': debit_amount, 'credit_amount': credit_amount})

    print('items: ', items)

    index = 0
    response_data = {}
    for payment_voucher in items:
        payment_voucher_dict = {}
        payment_voucher_id = payment_voucher.get('id', None)
        print('payment_voucher_id: ', payment_voucher_id)

        payment_voucher_dict['ledger'] = payment_voucher['ledger']
        payment_voucher_dict['debit_amount'] = payment_voucher['debit_amount']
        payment_voucher_dict['credit_amount'] = payment_voucher['credit_amount']

        payment_voucher_dict['branch'] = branch
        if not type(file) is str:
            payment_voucher_dict['file'] = file
        payment_voucher_dict['sub_ledger'] = sub_ledger
        payment_voucher_dict['invoice_no'] = invoice_no
        payment_voucher_dict['payment_date'] = payment_datetime
        payment_voucher_dict['details'] = details

        payment_voucher_dict['reference_no'] = invoice_no
        payment_voucher_dict['log_type'] = 'Payment Voucher'
        payment_voucher_dict['log_date'] = payment_datetime

        if payment_voucher_id:
            payment_voucher_obj = PaymentVoucher.objects.get(
                pk=payment_voucher_id)
            payment_voucher_serializer = PaymentVoucherSerializer(
                payment_voucher_obj, data=payment_voucher_dict)
            if payment_voucher_serializer.is_valid():
                print('validated_data: ',
                      payment_voucher_serializer.validated_data)
                payment_voucher_serializer.save()
            account_log_serializer = AccountLogSerializer(
                account_log_objs[index], data=payment_voucher_dict)
            if account_log_serializer.is_valid():
                account_log_serializer.save()
            index += 1
        else:
            new_payment_voucher_serializer = PaymentVoucherSerializer(
                data=payment_voucher_dict)
            if new_payment_voucher_serializer.is_valid():
                print('validated_data else block: ',
                      payment_voucher_serializer.validated_data)
                new_payment_voucher_serializer.save()
            new_account_log_serializer = AccountLogSerializer(
                data=payment_voucher_dict)
            if new_account_log_serializer.is_valid():
                new_account_log_serializer.save()

    payment_voucher_objs = PaymentVoucher.objects.filter(invoice_no=invoice_no)
    payment_voucher_serializer = PaymentVoucherListSerializer(
        payment_voucher_objs, many=True)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice_no)
    account_log_serializer = AccountLogListSerializer(
        account_log_objs, many=True)

    response_data['payment_vouchers'] = payment_voucher_serializer.data
    response_data['account_logs'] = account_log_serializer.data

    return Response({'data': response_data, 'detail': "Payment voucher(s) updated successfully"})


@extend_schema(request=PaymentVoucherSerializer, responses=PaymentVoucherSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_ITEM_DELETE.name])
def deletePaymentVoucher(request, pk):
    try:
        payment_voucher = PaymentVoucher.objects.get(pk=pk)
        payment_voucher.delete()
        return Response({'detail': f'PaymentVoucher id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"PaymentVoucher id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PaymentVoucherSerializer, responses=PaymentVoucherSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_ITEM_DELETE.name])
def deleteMultiplePaymentVoucher(request):
    ids = request.data['ids']
    try:
        payment_vouchers = PaymentVoucher.objects.filter(pk__in=ids)
        payment_vouchers.delete()
        return Response({'detail': f'PaymentVoucher ids - {ids} deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"PaymentVoucher ids - {ids} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
