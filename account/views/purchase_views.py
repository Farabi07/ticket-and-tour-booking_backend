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

from account.models import LedgerAccount, Purchase, AccountLog, SubLedgerAccount
from account.serializers import AccountLogSerializer, PurchaseListCustomSerializer, PurchaseSerializer, PurchaseListSerializer, AccountLogListSerializer

from account.filters import PurchaseFilter

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
    request=PurchaseSerializer,
    responses=PurchaseSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAllPurchase(request):
    purchases = Purchase.objects.filter(ledger__name='Company Purchase').order_by(
        '-invoice_no').distinct('invoice_no')
    total_elements = purchases.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    purchases = pagination.paginate_data(purchases)

    response_list = []

    if len(purchases) > 0:
        for purchase in purchases:
            purchase_dict = {}
            invoice_no = purchase.invoice_no
            purchase_serializer = PurchaseListCustomSerializer(purchase)
            for key, value in purchase_serializer.data.items():
                purchase_dict[key] = value
            related_purchases = Purchase.objects.filter(
                invoice_no=invoice_no).exclude(pk=purchase.id)
            print('related_purchases: ', related_purchases)
            if len(related_purchases) == 1:
                related_purchase = related_purchases[0]
                purchase_dict['related_ledgers'] = str(
                    related_purchase.ledger.name)
            elif len(related_purchases) > 0:
                name_list = []
                for related_purchase in related_purchases:
                    name_list.append(str(related_purchase.ledger.name))
                purchase_dict['related_ledgers'] = name_list
            response_list.append(purchase_dict)

    response = {
        'purchases': response_list,
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
    request=PurchaseSerializer,
    responses=PurchaseSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAllPurchaseByInvoiceNo(request, invoice_no):
    response_data = {}
    response_data['items'] = []

    purchases = Purchase.objects.filter(invoice_no=invoice_no)
    purchase = purchases.reverse()

    if len(purchases) > 0:
        response_data['invoice_no'] = purchases[0].invoice_no
        if purchases[0].sub_ledger:
            response_data['sub_ledger'] = {
                'id': purchases[0].sub_ledger.id, 'name': purchases[0].sub_ledger.name}
        else:
            response_data['sub_ledger'] = None
        if purchases[0].branch:
            response_data['branch'] = {
                'id': purchases[0].branch.id, 'name': purchases[0].branch.name}
        else:
            response_data['branch'] = None
        response_data['purchase_date'] = purchases[0].purchase_date
        response_data['details'] = purchases[0].details

        for purchase in purchases:
            serializer = PurchaseListSerializer(purchase)
            response_data['items'].append(serializer.data)

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"Invoice no {invoice_no} has no Purchases"})


@extend_schema(request=PurchaseSerializer, responses=PurchaseSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DETAILS.name])
def getAPurchase(request, pk):
    try:
        purchase = Purchase.objects.get(pk=pk)
        serializer = PurchaseListSerializer(purchase)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Purchase id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PurchaseSerializer, responses=PurchaseSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchPurchase(request):
    invoice_no = request.query_params.get('invoice_no', None)
    purchases = Purchase.objects.filter(
        ledger__name='Company Purchase', invoice_no=invoice_no)

    print('purchases: ', purchases)

    total_elements = purchases.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    purchases = pagination.paginate_data(purchases)

    response_list = []

    if len(purchases) > 0:
        for purchase in purchases:
            purchase_dict = {}
            invoice_no = purchase.invoice_no
            purchase_serializer = PurchaseListCustomSerializer(purchase)
            for key, value in purchase_serializer.data.items():
                purchase_dict[key] = value
            related_purchases = Purchase.objects.filter(
                invoice_no=invoice_no).exclude(pk=purchase.id)
            print('related_purchases: ', related_purchases)
            if len(related_purchases) == 1:
                related_purchase = related_purchases[0]
                purchase_dict['related_ledgers'] = str(
                    related_purchase.ledger.name)
            elif len(related_purchases) > 0:
                name_list = []
                for related_purchase in related_purchases:
                    name_list.append(str(related_purchase.ledger.name))
                purchase_dict['related_ledgers'] = name_list
            response_list.append(purchase_dict)

    response = {
        'purchases': response_list,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=PurchaseSerializer, responses=PurchaseSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_CREATE.name])
def createPurchase(request):
    data = request.data
    print('data: ', data)

    sub_ledger = data.get('sub_ledger', None)
    branch = data.get('branch', None)
    file = data.get('file', None)
    details = data.get('details', None)
    purchase_date = data.get('purchase_date', None)
    purchase_datetime = str(purchase_date) + 'T' + str(datetime.now().time())
    print('purchase_datetime: ', purchase_datetime)

    branch_obj = None
    sub_ledger_obj = None
    if branch:
        branch_obj = Branch.objects.get(pk=branch)
    if sub_ledger:
        sub_ledger_obj = SubLedgerAccount.objects.get(pk=sub_ledger)

    current_date = date.today()
    current_date = str(current_date)
    current_date = current_date.replace('-', '')
    pu_current_date = 'PU' + current_date
    print('current_date: ', current_date, type(current_date))

    _num = get_next_value(pu_current_date)
    print('get_next_value: ', _num)

    invoice = 'PU' + current_date + '00' + str(_num)
    print('invoice: ', invoice)

    items = []
    for i in range(int(len(data) / 3)):
        ledger = data.get(f'items[{i}][ledger]', None)
        debit_amount = data.get(f'items[{i}][debit_amount]', None)
        credit_amount = data.get(f'items[{i}][credit_amount]', None)
        if ledger is not None and debit_amount is not None and credit_amount is not None:
            items.append(
                {'ledger': ledger, 'debit_amount': debit_amount, 'credit_amount': credit_amount})

    for purchase in items:
        print('purchase: ', purchase)
        ledger = purchase.get('ledger', None)
        debit_amount = Decimal(purchase.get('debit_amount', None))
        credit_amount = Decimal(purchase.get('credit_amount', None))

        ledger_obj = None
        if ledger:
            ledger_obj = LedgerAccount.objects.get(pk=ledger)

        purchase_obj = Purchase.objects.create(
            ledger=ledger_obj,
            sub_ledger=sub_ledger_obj,
            branch=branch_obj,
            file=file,
            invoice_no=invoice,
            purchase_date=purchase_datetime,
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            details=details
        )

        account_log_obj = AccountLog.objects.create(
            log_type='purchase',
            ledger=ledger_obj,
            sub_ledger=sub_ledger_obj,
            branch=branch_obj,
            reference_no=invoice,
            log_date=purchase_datetime,
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            details=details
        )

    purchase_objs = Purchase.objects.filter(invoice_no=invoice)
    purchase_serializer = PurchaseListSerializer(purchase_objs, many=True)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice)
    account_log_serializer = AccountLogListSerializer(
        account_log_objs, many=True)

    response = {
        'purchases': purchase_serializer.data,
        'account_logs': account_log_serializer.data
    }

    return Response(response, status=status.HTTP_201_CREATED)


@extend_schema(request=PurchaseSerializer, responses=PurchaseSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_UPDATE.name])
def updatePurchase(request):
    data = request.data
    print('data: ', data)

    branch = data.get('branch', None)
    file = data.get('file', None)
    sub_ledger = data.get('sub_ledger', None)
    invoice_no = data.get('invoice_no', None)
    purchase_date = str(data.get('purchase_date', None))
    details = data.get('details', None)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice_no)
    print('account_log_objs: ', account_log_objs)

    purchase_datetime = ""
    if 'T' in purchase_date:
        purchase_datetime = purchase_date
        print('purchase_datetime if: ', purchase_datetime)
    else:
        purchase_datetime = str(purchase_date) + 'T' + \
            str(datetime.now().time())
        print('purchase_datetime else: ', purchase_datetime)

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
    for purchase in items:
        purchase_dict = {}
        purchase_id = purchase.get('id', None)
        print('purchase_id: ', purchase_id)

        purchase_dict['ledger'] = purchase['ledger']
        purchase_dict['debit_amount'] = purchase['debit_amount']
        purchase_dict['credit_amount'] = purchase['credit_amount']

        purchase_dict['branch'] = branch
        if not type(file) is str:
            purchase_dict['file'] = file
        purchase_dict['sub_ledger'] = sub_ledger
        purchase_dict['invoice_no'] = invoice_no
        purchase_dict['purchase_date'] = purchase_datetime
        purchase_dict['details'] = details

        purchase_dict['reference_no'] = invoice_no
        purchase_dict['log_type'] = 'Purchase'
        purchase_dict['log_date'] = purchase_datetime

        if purchase_id:
            purchase_obj = Purchase.objects.get(pk=purchase_id)
            purchase_serializer = PurchaseSerializer(
                purchase_obj, data=purchase_dict)
            if purchase_serializer.is_valid():
                purchase_serializer.save()
            account_log_serializer = AccountLogSerializer(
                account_log_objs[index], data=purchase_dict)
            if account_log_serializer.is_valid():
                account_log_serializer.save()
            index += 1
        else:
            new_purchase_serializer = PurchaseSerializer(data=purchase_dict)
            if new_purchase_serializer.is_valid():
                new_purchase_serializer.save()
            new_account_log_serializer = AccountLogSerializer(
                data=purchase_dict)
            if new_account_log_serializer.is_valid():
                new_account_log_serializer.save()

    purchase_objs = Purchase.objects.filter(invoice_no=invoice_no)
    purchase_serializer = PurchaseListSerializer(purchase_objs, many=True)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice_no)
    account_log_serializer = AccountLogListSerializer(
        account_log_objs, many=True)

    response_data['purchases'] = purchase_serializer.data
    response_data['account_logs'] = account_log_serializer.data

    return Response({'data': response_data, 'detail': "Purchase voucher(s) updated successfully"})


@extend_schema(request=PurchaseSerializer, responses=PurchaseSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DELETE.name])
def deletePurchase(request, pk):
    try:
        purchase = Purchase.objects.get(pk=pk)
        purchase.delete()
        return Response({'detail': f'Purchase id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Purchase id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PurchaseSerializer, responses=PurchaseSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DELETE.name])
def deleteMultiplePurchase(request):
    ids = request.data['ids']
    try:
        purchases = Purchase.objects.filter(pk__in=ids)
        purchases.delete()
        return Response({'detail': f'Purchase ids - {ids} deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Purchase ids - {ids} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
