from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from authentication.models import Branch

from sequences import get_next_value

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import LedgerAccount, ReceiptVoucher, AccountLog, SubLedgerAccount
from account.serializers import AccountLogSerializer, PaymentVoucherListCustomSerializer, ReceiptVoucherListCustomSerializer, ReceiptVoucherSerializer, ReceiptVoucherListSerializer, AccountLogListSerializer

from account.filters import ReceiptVoucherFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination

from datetime import date
from datetime import datetime


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=ReceiptVoucherSerializer,
    responses=ReceiptVoucherSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAllReceiptVoucher(request):
    receipt_vouchers = ReceiptVoucher.objects.filter(
        ledger__name__in=['Cash', 'Bank']).order_by('-invoice_no').distinct('invoice_no')
    total_elements = receipt_vouchers.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    receipt_vouchers = pagination.paginate_data(receipt_vouchers)

    response_list = []

    if len(receipt_vouchers) > 0:
        for receipt_voucher in receipt_vouchers:
            receipt_voucher_dict = {}
            invoice_no = receipt_voucher.invoice_no
            receipt_voucher_serializer = ReceiptVoucherListCustomSerializer(
                receipt_voucher)
            for key, value in receipt_voucher_serializer.data.items():
                receipt_voucher_dict[key] = value
            related_receipt_vouchers = ReceiptVoucher.objects.filter(
                invoice_no=invoice_no).exclude(pk=receipt_voucher.id)
            print('related_receipt_vouchers: ', related_receipt_vouchers)
            if len(related_receipt_vouchers) == 1:
                related_receipt_voucher = related_receipt_vouchers[0]
                receipt_voucher_dict['related_ledgers'] = str(
                    related_receipt_voucher.ledger.name)
            elif len(related_receipt_vouchers) > 0:
                name_list = []
                for related_receipt_voucher in related_receipt_vouchers:
                    name_list.append(str(related_receipt_voucher.ledger.name))
                receipt_voucher_dict['related_ledgers'] = name_list
            response_list.append(receipt_voucher_dict)

    response = {
        'receipt_vouchers': response_list,
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
    request=ReceiptVoucherSerializer,
    responses=ReceiptVoucherSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAllReceiptVoucherByInvoiceNo(request, invoice_no):
    response_data = {}
    response_data['items'] = []

    receipt_vouchers = ReceiptVoucher.objects.filter(invoice_no=invoice_no)
    receipt_vouchers = receipt_vouchers.reverse()

    if len(receipt_vouchers) > 0:
        response_data['invoice_no'] = receipt_vouchers[0].invoice_no

        if receipt_vouchers[0].file and not str(receipt_vouchers[0].file).startswith('/media/'):
            response_data['file'] = '/media/' + str(receipt_vouchers[0].file)
        else:
            response_data['file'] = str(receipt_vouchers[0].file)

        if receipt_vouchers[0].sub_ledger:
            response_data['sub_ledger'] = {
                'id': receipt_vouchers[0].sub_ledger.id, 'name': receipt_vouchers[0].sub_ledger.name}
        else:
            response_data['sub_ledger'] = None
        if receipt_vouchers[0].branch:
            response_data['branch'] = {
                'id': receipt_vouchers[0].branch.id, 'name': receipt_vouchers[0].branch.name}
        else:
            response_data['branch'] = None
        response_data['receipt_date'] = receipt_vouchers[0].receipt_date
        response_data['details'] = receipt_vouchers[0].details

        for receipt_voucher in receipt_vouchers:
            serializer = ReceiptVoucherListSerializer(receipt_voucher)
            response_data['items'].append(serializer.data)

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"Invoice no {invoice_no} has no ReceiptVouchers"})


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=ReceiptVoucherSerializer,
    responses=ReceiptVoucherSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAllReceiptVoucherWithIdNameDictAgainstForeignKeyByInvoiceNo(request, invoice_no):
    response_data = {}
    response_data['items'] = []

    receipt_vouchers = ReceiptVoucher.objects.filter(invoice_no=invoice_no)
    receipt_vouchers = receipt_vouchers.reverse()

    response_data['invoice_no'] = receipt_vouchers[0].invoice_no

    if receipt_vouchers[0].file and not str(receipt_vouchers[0].file).startswith('/media/'):
        response_data['file'] = '/media/' + str(receipt_vouchers[0].file)
    else:
        response_data['file'] = str(receipt_vouchers[0].file)

    if receipt_vouchers[0].sub_ledger:
        response_data['sub_ledger'] = {
            'id': receipt_vouchers[0].sub_ledger.id, 'name': receipt_vouchers[0].sub_ledger.name}
    else:
        response_data['sub_ledger'] = None
    if receipt_vouchers[0].branch:
        response_data['branch'] = {
            'id': receipt_vouchers[0].branch.id, 'name': receipt_vouchers[0].branch.name}
    else:
        response_data['branch'] = None
    response_data['receipt_date'] = receipt_vouchers[0].receipt_date
    response_data['details'] = receipt_vouchers[0].details

    for receipt_voucher in receipt_vouchers:
        serializer = ReceiptVoucherListSerializer(receipt_voucher)
        response_data['items'].append(serializer.data)

    return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(request=ReceiptVoucherSerializer, responses=ReceiptVoucherSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DETAILS.name])
def getAReceiptVoucher(request, pk):
    try:
        receipt_voucher = ReceiptVoucher.objects.get(pk=pk)
        serializer = ReceiptVoucherListSerializer(receipt_voucher)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"ReceiptVoucher id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=ReceiptVoucherSerializer, responses=ReceiptVoucherSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchReceiptVoucher(request):
    invoice_no = request.query_params.get('invoice_no', None)
    receipt_vouchers = ReceiptVoucher.objects.filter(
        ledger__name__in=['Cash', 'Bank'], invoice_no=invoice_no)

    print('receipt_vouchers: ', receipt_vouchers)

    total_elements = receipt_vouchers.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    receipt_vouchers = pagination.paginate_data(receipt_vouchers)

    response_list = []

    if len(receipt_vouchers) > 0:
        for receipt_voucher in receipt_vouchers:
            receipt_voucher_dict = {}
            invoice_no = receipt_voucher.invoice_no
            receipt_voucher_serializer = ReceiptVoucherListCustomSerializer(
                receipt_voucher)
            for key, value in receipt_voucher_serializer.data.items():
                receipt_voucher_dict[key] = value
            related_receipt_vouchers = ReceiptVoucher.objects.filter(
                invoice_no=invoice_no).exclude(pk=receipt_voucher.id)
            print('related_receipt_vouchers: ', related_receipt_vouchers)
            if len(related_receipt_vouchers) == 1:
                related_receipt_voucher = related_receipt_vouchers[0]
                receipt_voucher_dict['related_ledgers'] = str(
                    related_receipt_voucher.ledger.name)
            elif len(related_receipt_vouchers) > 0:
                name_list = []
                for related_receipt_voucher in related_receipt_vouchers:
                    name_list.append(str(related_receipt_voucher.ledger.name))
                receipt_voucher_dict['related_ledgers'] = name_list
            response_list.append(receipt_voucher_dict)

    response = {
        'receipt_vouchers': response_list,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=ReceiptVoucherSerializer, responses=ReceiptVoucherSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_CREATE.name])
def createReceiptVoucher(request):
    data = request.data
    print('data: ', data)

    sub_ledger = data.get('sub_ledger', None)
    branch = data.get('branch', None)
    file = data.get('file', None)
    details = data.get('details', None)
    receipt_date = data.get('receipt_date', None)
    receipt_datetime = str(receipt_date) + 'T' + str(datetime.now().time())
    print('receipt_datetime: ', receipt_datetime)

    branch_obj = None
    sub_ledger_obj = None
    if branch:
        branch_obj = Branch.objects.get(pk=branch)
    if sub_ledger:
        sub_ledger_obj = SubLedgerAccount.objects.get(pk=sub_ledger)

    current_date = date.today()
    current_date = str(current_date)
    current_date = current_date.replace('-', '')
    rv_current_date = 'RV' + current_date
    print('current_date: ', current_date, type(current_date))

    _num = get_next_value(rv_current_date)
    print('get_next_value: ', _num)

    invoice = 'RV' + current_date + '00' + str(_num)
    print('invoice: ', invoice)

    items = []
    for i in range(int(len(data) / 3)):
        ledger = data.get(f'items[{i}][ledger]', None)
        debit_amount = data.get(f'items[{i}][debit_amount]', None)
        credit_amount = data.get(f'items[{i}][credit_amount]', None)
        if ledger is not None and debit_amount is not None and credit_amount is not None:
            items.append(
                {'ledger': ledger, 'debit_amount': debit_amount, 'credit_amount': credit_amount})

    for receipt_voucher in items:
        print('receipt_voucher: ', receipt_voucher)
        ledger = receipt_voucher.get('ledger', None)
        debit_amount = Decimal(receipt_voucher.get('debit_amount', None))
        credit_amount = Decimal(receipt_voucher.get('credit_amount', None))

        ledger_obj = None
        if ledger:
            ledger_obj = LedgerAccount.objects.get(pk=ledger)

        receipt_voucher_obj = ReceiptVoucher.objects.create(
            ledger=ledger_obj,
            sub_ledger=sub_ledger_obj,
            branch=branch_obj,
            file=file,
            invoice_no=invoice,
            receipt_date=receipt_datetime,
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            details=details
        )

        account_log_obj = AccountLog.objects.create(
            log_type='receipt_voucher',
            ledger=ledger_obj,
            sub_ledger=sub_ledger_obj,
            branch=branch_obj,
            reference_no=invoice,
            log_date=receipt_datetime,
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            details=details
        )

    receipt_voucher_objs = ReceiptVoucher.objects.filter(invoice_no=invoice)
    receipt_voucher_serializer = ReceiptVoucherListSerializer(
        receipt_voucher_objs, many=True)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice)
    account_log_serializer = AccountLogListSerializer(
        account_log_objs, many=True)

    response = {
        'receipt_vouchers': receipt_voucher_serializer.data,
        'account_logs': account_log_serializer.data
    }

    return Response(response, status=status.HTTP_201_CREATED)


@extend_schema(request=ReceiptVoucherSerializer, responses=ReceiptVoucherSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_UPDATE.name])
def updateReceiptVoucher(request):
    data = request.data
    print('data: ', data)

    branch = data.get('branch', None)
    file = data.get('file', None)
    sub_ledger = data.get('sub_ledger', None)
    invoice_no = data.get('invoice_no', None)
    receipt_date = str(data.get('receipt_date', None))
    details = data.get('details', None)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice_no)
    print('account_log_objs: ', account_log_objs)

    receipt_datetime = ""
    if 'T' in receipt_date:
        receipt_datetime = receipt_date
        print('receipt_datetime if: ', receipt_datetime)
    else:
        receipt_datetime = str(receipt_date) + 'T' + str(datetime.now().time())
        print('receipt_datetime else: ', receipt_datetime)

    items = []
    for i in range(int(len(data) / 3)):
        id = data.get(f'items[{i}][id]', None)
        ledger = data.get(f'items[{i}][ledger]', None)
        debit_amount = data.get(f'items[{i}][debit_amount]', None)
        credit_amount = data.get(f'items[{i}][credit_amount]', None)
        if ledger is not None and debit_amount is not None and credit_amount is not None:
            items.append({'id': id, 'ledger': ledger,
                         'debit_amount': debit_amount, 'credit_amount': credit_amount})

    index = 0
    response_data = {}
    for receipt_voucher in items:
        receipt_voucher_dict = {}
        receipt_voucher_id = receipt_voucher.get('id', None)
        print('receipt_voucher_id: ', receipt_voucher_id)

        receipt_voucher_dict['ledger'] = receipt_voucher['ledger']
        receipt_voucher_dict['debit_amount'] = receipt_voucher['debit_amount']
        receipt_voucher_dict['credit_amount'] = receipt_voucher['credit_amount']

        receipt_voucher_dict['branch'] = branch
        if not type(file) is str:
            receipt_voucher_dict['file'] = file
        receipt_voucher_dict['sub_ledger'] = sub_ledger
        receipt_voucher_dict['invoice_no'] = invoice_no
        receipt_voucher_dict['receipt_date'] = receipt_datetime
        receipt_voucher_dict['details'] = details

        receipt_voucher_dict['reference_no'] = invoice_no
        receipt_voucher_dict['log_type'] = 'Receipt Voucher'
        receipt_voucher_dict['log_date'] = receipt_datetime

        if receipt_voucher_id is not None:
            receipt_voucher_obj = ReceiptVoucher.objects.get(
                pk=receipt_voucher_id)
            receipt_voucher_serializer = ReceiptVoucherSerializer(
                receipt_voucher_obj, data=receipt_voucher_dict)
            if receipt_voucher_serializer.is_valid():
                receipt_voucher_serializer.save()
            account_log_serializer = AccountLogSerializer(
                account_log_objs[index], data=receipt_voucher_dict)
            if account_log_serializer.is_valid():
                account_log_serializer.save()
            index += 1
        else:
            new_receipt_voucher_serializer = ReceiptVoucherSerializer(
                data=receipt_voucher_dict)
            if new_receipt_voucher_serializer.is_valid():
                new_receipt_voucher_serializer.save()
            new_account_log_serializer = AccountLogSerializer(
                data=receipt_voucher_dict)
            if new_account_log_serializer.is_valid():
                new_account_log_serializer.save()

    receipt_voucher_objs = ReceiptVoucher.objects.filter(invoice_no=invoice_no)
    receipt_voucher_serializer = ReceiptVoucherListSerializer(
        receipt_voucher_objs, many=True)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice_no)
    account_log_serializer = AccountLogListSerializer(
        account_log_objs, many=True)

    response_data['receipt_vouchers'] = receipt_voucher_serializer.data
    response_data['account_logs'] = account_log_serializer.data

    return Response({'data': response_data, 'detail': "Receipt voucher(s) updated successfully"})


@extend_schema(request=ReceiptVoucherSerializer, responses=ReceiptVoucherSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DELETE.name])
def deleteReceiptVoucher(request, pk):
    try:
        receipt_voucher = ReceiptVoucher.objects.get(pk=pk)
        receipt_voucher.delete()
        return Response({'detail': f'ReceiptVoucher id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"ReceiptVoucher id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=ReceiptVoucherSerializer, responses=ReceiptVoucherSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DELETE.name])
def deleteMultipleReceiptVoucher(request):
    ids = request.data['ids']
    try:
        receipt_vouchers = ReceiptVoucher.objects.filter(pk__in=ids)
        receipt_vouchers.delete()
        return Response({'detail': f'ReceiptVoucher ids - {ids} deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"ReceiptVoucher ids - {ids} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


# THIS WAS PREVIOUS VERSION-----------------------------------------------

@extend_schema(request=ReceiptVoucherSerializer, responses=ReceiptVoucherSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_CREATE.name])
def createReceiptVoucherPREV(request):
    data = request.data
    print('data: ', data)

    response_data = {}

    current_date = date.today()
    current_date = str(current_date)
    current_date = current_date.replace('-', '')
    rv_current_date = 'RV' + current_date
    print('current_date: ', current_date, type(current_date))

    _num = get_next_value(rv_current_date)
    print('get_next_value: ', _num)

    invoice = 'RV' + current_date + '00' + str(_num)
    print('invoice: ', invoice)

    for receipt_voucher in data:
        ledger_id = int(receipt_voucher.get('ledger', None))
        receipt_date = receipt_voucher.get('receipt_date', None)
        debit_amount = receipt_voucher.get('debit_amount', None)
        credit_amount = receipt_voucher.get('credit_amount', None)
        details = receipt_voucher.get('details', None)

        ledger_acc_obj = LedgerAccount.objects.get(id=ledger_id)

        receipt_datetime = str(receipt_date) + 'T' + \
            str(datetime.now().time()) + 'Z'
        print('receipt_datetime: ', receipt_datetime)

        if request.user.is_authenticated:
            receipt_voucher_obj = ReceiptVoucher.objects.create(
                ledger=ledger_acc_obj,
                invoice_no=invoice,
                receipt_date=receipt_datetime,
                debit_amount=debit_amount,
                credit_amount=credit_amount,
                details=details
            )

            account_log_obj = AccountLog.objects.create(
                log_type='Receipt Voucher',
                ledger=ledger_acc_obj,
                reference_no=invoice,
                log_date=receipt_datetime,
                debit_amount=debit_amount,
                credit_amount=credit_amount,
                details=details
            )
        else:
            return Response({'detail': 'User is not authenticated.'}, status=status.HTTP_400_BAD_REQUEST)
    print('response_data: ', response_data)

    receipt_voucher_objs = ReceiptVoucher.objects.filter(invoice_no=invoice)
    receipt_voucher_serializer = ReceiptVoucherListSerializer(
        receipt_voucher_objs, many=True)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice)
    account_log_serializer = AccountLogListSerializer(
        account_log_objs, many=True)

    response_data['receipt_vouchers'] = receipt_voucher_serializer.data
    response_data['account_logs'] = account_log_serializer.data

    return Response(response_data, status=status.HTTP_201_CREATED)


# THIS WAS PREVIOUS VERSION-----------------------------------------------

@extend_schema(request=ReceiptVoucherSerializer, responses=ReceiptVoucherSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_UPDATE.name])
def updateReceiptVoucherPREV(request):
    data = request.data
    receipt_datetime = ""
    invoice = data[0]['invoice_no']
    account_log_objs = AccountLog.objects.filter(reference_no=invoice)
    print('account_log_objs: ', account_log_objs)

    print('data: ', data)

    response_data = {}
    i = 0
    for receipt_voucher in data:
        ledger_id = int(receipt_voucher.get('ledger', None))
        receipt_voucher_id = int(receipt_voucher.get('id', None))
        invoice_no = receipt_voucher.get('invoice_no', None)
        receipt_date = receipt_voucher.get('receipt_date', None)
        debit_amount = receipt_voucher.get('debit_amount', None)
        credit_amount = receipt_voucher.get('credit_amount', None)
        details = receipt_voucher.get('details', None)

        if 'T' in receipt_date:
            receipt_datetime = receipt_date
            print('receipt_datetime if: ', receipt_datetime)
        else:
            receipt_datetime = str(receipt_date) + 'T' + \
                str(datetime.now().time()) + 'Z'
            print('receipt_datetime else: ', receipt_datetime)

        ledger_acc_obj = LedgerAccount.objects.get(id=ledger_id)

        receipt_voucher_obj = ReceiptVoucher.objects.get(id=receipt_voucher_id)

        if request.user.is_authenticated:
            receipt_voucher_obj.ledger = ledger_acc_obj
            receipt_voucher_obj.invoice_no = invoice_no
            receipt_voucher_obj.receipt_date = receipt_datetime
            receipt_voucher_obj.debit_amount = debit_amount
            receipt_voucher_obj.credit_amount = credit_amount
            receipt_voucher_obj.details = details
            receipt_voucher_obj.save()

            account_log_obj = account_log_objs[i]

            account_log_obj.ledger = ledger_acc_obj
            account_log_obj.log_type = 'Updated Receipt Voucher'
            account_log_obj.reference_no = invoice_no
            account_log_obj.log_date = receipt_datetime
            account_log_obj.debit_amount = debit_amount
            account_log_obj.credit_amount = credit_amount
            account_log_obj.details = details
            account_log_obj.save()

            i += 1

        else:
            return Response({'detail': 'User is not authenticated.'}, status=status.HTTP_400_BAD_REQUEST)

    receipt_voucher_objs = ReceiptVoucher.objects.filter(invoice_no=invoice)
    receipt_voucher_serializer = ReceiptVoucherListSerializer(
        receipt_voucher_objs, many=True)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice)
    account_log_serializer = AccountLogListSerializer(
        account_log_objs, many=True)

    response_data['receipt_vouchers'] = receipt_voucher_serializer.data
    response_data['account_logs'] = account_log_serializer.data

    return Response({'data': response_data, 'detail': "Receipt voucher(s) updated successfully"})
