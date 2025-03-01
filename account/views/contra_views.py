from django.core.exceptions import ObjectDoesNotExist
from authentication.models import Branch

from rest_framework import status
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sequences import get_next_value

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import LedgerAccount, Contra, AccountLog
from account.serializers import AccountLogSerializer, ContraListCustomSerializer, ContraSerializer, ContraListSerializer, AccountLogListSerializer

from account.filters import ContraFilter

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
    request=ContraSerializer,
    responses=ContraSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAllContra(request):
    contras = Contra.objects.all().order_by('invoice_no').distinct('invoice_no')
    total_elements = contras.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    contras = pagination.paginate_data(contras)

    serializer = ContraListCustomSerializer(contras, many=True)

    response = {
        'contras': serializer.data,
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
    request=ContraSerializer,
    responses=ContraListSerializer
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAllContraByInvoiceNo(request, invoice_no):
    response_data = dict()
    response_data['items'] = list()

    contras = Contra.objects.filter(invoice_no=invoice_no)
    contras = contras.reverse()
    print('contras: ', contras)

    if len(contras):
        response_data['invoice_no'] = contras[0].invoice_no

        if contras[0].branch:
            response_data['branch'] = {
                "id": contras[0].branch.id, "name": contras[0].branch.name}
        else:
            response_data['branch'] = None
        response_data['contra_date'] = contras[0].contra_date
        response_data['details'] = contras[0].details

        for contra in contras:
            serializer = ContraListSerializer(contra)
            response_data['items'].append(serializer.data)

        print('items: ', response_data['items'])

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"Invoice_no {invoice_no} has no contras"})


@extend_schema(request=ContraSerializer, responses=ContraSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DETAILS.name])
def getAContra(request, pk):
    try:
        contra = Contra.objects.get(pk=pk)
        serializer = ContraListSerializer(contra)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Contra id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=ContraSerializer, responses=ContraSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchContra(request):
    contras = ContraFilter(request.GET, queryset=Contra.objects.all().order_by(
        'invoice_no').distinct('invoice_no'))
    contras = contras.qs

    print('searched_products: ', contras)

    total_elements = contras.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    contras = pagination.paginate_data(contras)

    serializer = ContraListSerializer(contras, many=True)

    response = {
        'contras': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    if len(contras) > 0:
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"There are no contras matching your search"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=ContraSerializer, responses=ContraSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_CREATE.name])
def createContra(request):
    data = request.data
    items = data.get('items', None)
    print('data: ', data)

    response_data = {}

    branch = data.get('branch', None)
    details = data.get('details', None)
    contra_date = data.get('contra_date', None)
    contra_datetime = str(contra_date) + 'T' + str(datetime.now().time()) + 'Z'
    print('contra_datetime: ', contra_datetime)

    current_date = date.today()
    current_date = str(current_date)
    current_date = current_date.replace('-', '')
    contra_current_date = 'CONTRA' + current_date
    print('current_date: ', current_date, type(current_date))

    _num = get_next_value(contra_current_date)
    print('get_next_value: ', _num)

    invoice = 'CO' + current_date + '00' + str(_num)
    print('invoice: ', invoice)

    branch_obj = None
    if branch:
        branch_obj = Branch.objects.get(pk=branch)

    for contra in items:
        ledger_id = int(contra.get('ledger', None))
        debit_amount = contra.get('debit_amount', None)
        credit_amount = contra.get('credit_amount', None)

        ledger_acc_obj = LedgerAccount.objects.get(id=ledger_id)

        contra_voucher_obj = Contra.objects.create(
            branch=branch_obj,
            ledger=ledger_acc_obj,
            invoice_no=invoice,
            contra_date=contra_datetime,
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            details=details
        )

        account_log_obj = AccountLog.objects.create(
            log_type='contra',
            branch=branch_obj,
            ledger=ledger_acc_obj,
            reference_no=invoice,
            log_date=contra_datetime,
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            details=details
        )

    print('response_data: ', response_data)

    contra_voucher_objs = Contra.objects.filter(invoice_no=invoice)
    contra_voucher_serializer = ContraListSerializer(
        contra_voucher_objs, many=True)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice)
    account_log_serializer = AccountLogListSerializer(
        account_log_objs, many=True)

    response_data['contras'] = contra_voucher_serializer.data
    response_data['account_logs'] = account_log_serializer.data

    return Response(response_data, status=status.HTTP_201_CREATED)


@extend_schema(request=ContraSerializer, responses=ContraSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_UPDATE.name])
def updateContra(request):
    data = request.data
    items = data.get('items', None)
    print('data: ', data)

    branch = data.get('branch', None)
    invoice_no = data.get('invoice_no', None)
    contra_date = str(data.get('contra_date', None))
    details = data.get('details', None)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice_no)
    print('account_log_objs: ', account_log_objs)

    contra_datetime = ""
    if 'T' in contra_date:
        contra_datetime = contra_date
        print('contra_datetime if: ', contra_datetime)
    else:
        contra_datetime = str(contra_date) + 'T' + str(datetime.now().time())
        print('contra_datetime else: ', contra_datetime)

    index = 0
    response_data = {}

    for contra in items:
        contra_dict = {}
        contra_id = contra.get('id', None)
        print('contra_id: ', contra_id)

        contra_dict['ledger'] = contra['ledger']
        contra_dict['debit_amount'] = contra['debit_amount']
        contra_dict['credit_amount'] = contra['credit_amount']

        contra_dict['branch'] = branch
        contra_dict['invoice_no'] = invoice_no
        contra_dict['contra_date'] = contra_datetime
        contra_dict['details'] = details

        contra_dict['reference_no'] = invoice_no
        contra_dict['log_type'] = 'Contra'
        contra_dict['log_date'] = contra_datetime

        if contra_id:
            contra_obj = Contra.objects.get(pk=contra_id)
            contra_serializer = ContraSerializer(contra_obj, data=contra_dict)
            if contra_serializer.is_valid():
                print('validated_data: ', contra_serializer.validated_data)
                contra_serializer.save()
            account_log_serializer = AccountLogSerializer(
                account_log_objs[index], data=contra_dict)
            if account_log_serializer.is_valid():
                account_log_serializer.save()
            index += 1
        else:
            new_contra_serializer = ContraSerializer(data=contra_dict)
            if new_contra_serializer.is_valid():
                new_contra_serializer.save()
            new_account_log_serializer = AccountLogSerializer(data=contra_dict)
            if new_account_log_serializer.is_valid():
                new_account_log_serializer.save()

    contra_objs = Contra.objects.filter(invoice_no=invoice_no)
    contra_serializer = ContraListSerializer(contra_objs, many=True)

    account_log_objs = AccountLog.objects.filter(reference_no=invoice_no)
    account_log_serializer = AccountLogListSerializer(
        account_log_objs, many=True)

    response_data['contras'] = contra_serializer.data
    response_data['account_logs'] = account_log_serializer.data

    return Response({'data': response_data, 'detail': "Payment voucher(s) updated successfully"})


@extend_schema(request=ContraSerializer, responses=ContraSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DELETE.name])
def deleteContra(request, pk):
    try:
        contra = Contra.objects.get(pk=pk)
        contra.delete()
        return Response({'detail': f'Contra id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Contra id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=ContraSerializer, responses=ContraSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DELETE.name])
def deleteMultipleContra(request):
    ids = request.data['ids']
    try:
        contras = Contra.objects.filter(pk__in=ids)
        contras.delete()
        return Response({'detail': f'Contra ids - {ids} deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Contra ids - {ids} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
