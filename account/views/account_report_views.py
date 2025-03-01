from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from account.filters import ContraFilter, PaymentVoucherFilter, PurchaseFilter, ReceiptVoucherFilter, SalesFilter
from authentication.serializers import CountryListSerializer

from sequences import get_next_value

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import Contra, PaymentVoucher, Purchase, ReceiptVoucher, Sales
from account.serializers import AccountLogSerializer, AccountLogListSerializer, ContraSerializer, PaymentVoucherListSerializer, PaymentVoucherSerializer, PurchaseListSerializer, PurchaseSerializer, ReceiptVoucherListSerializer, ReceiptVoucherSerializer, SalesListSerializer, SalesSerializer

from commons.enums import PermissionEnum
from commons.pagination import Pagination

from decimal import Decimal
import datetime


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
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAccountReportForPaymentVoucher(request):
    payment_vouchers = PaymentVoucherFilter(
        request.GET, queryset=PaymentVoucher.objects.exclude(debit_amount=0))
    payment_vouchers = payment_vouchers.qs
    total_elements = payment_vouchers.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    payment_vouchers = pagination.paginate_data(payment_vouchers)
    print('payment_vouchers: ', payment_vouchers)

    response_list = []

    if len(payment_vouchers) > 0:
        for payment_voucher in payment_vouchers:
            payment_voucher_dict = {}
            invoice_no = payment_voucher.invoice_no
            payment_voucher_serializer = PaymentVoucherListSerializer(
                payment_voucher)
            for key, value in payment_voucher_serializer.data.items():
                payment_voucher_dict[key] = value
            related_payment_vouchers = PaymentVoucher.objects.filter(
                invoice_no=invoice_no).exclude(pk=payment_voucher.id)
            print('related_payment_vouchers: ', related_payment_vouchers)
            if len(related_payment_vouchers) == 1:
                related_payment_voucher = related_payment_vouchers[0]
                payment_voucher_dict['related_ledger'] = str(
                    related_payment_voucher.ledger.name)
                pass
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
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAccountSummaryForPaymentVoucher(request):
    payment_vouchers = PaymentVoucherFilter(
        request.GET, queryset=PaymentVoucher.objects.all())
    payment_vouchers = payment_vouchers.qs
    total_elements = payment_vouchers.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    payment_vouchers = pagination.paginate_data(payment_vouchers)
    print('payment_vouchers: ', payment_vouchers)

    payment_voucher_dict = {}

    if len(payment_vouchers) > 0:
        for payment_voucher in payment_vouchers:
            if payment_voucher.sub_ledger:
                sub_ledger = str(payment_voucher.sub_ledger.name)
                if sub_ledger not in payment_voucher_dict.keys():
                    payment_voucher_dict[sub_ledger] = 0
                dr = payment_voucher.debit_amount
                cr = payment_voucher.credit_amount
                amount = cr + dr
                payment_voucher_dict[sub_ledger] += Decimal(amount)

    response = {
        'payment_voucher_summary': payment_voucher_dict,
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
def getAccountReportForReceiptVoucher(request):
    receipt_vouchers = ReceiptVoucherFilter(
        request.GET, queryset=ReceiptVoucher.objects.exclude(credit_amount=0))
    receipt_vouchers = receipt_vouchers.qs
    total_elements = receipt_vouchers.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    receipt_vouchers = pagination.paginate_data(receipt_vouchers)
    print('receipt_vouchers: ', receipt_vouchers)

    response_list = []

    if len(receipt_vouchers) > 0:
        for receipt_voucher in receipt_vouchers:
            receipt_voucher_dict = {}
            invoice_no = receipt_voucher.invoice_no
            receipt_voucher_serializer = ReceiptVoucherListSerializer(
                receipt_voucher)
            for key, value in receipt_voucher_serializer.data.items():
                receipt_voucher_dict[key] = value
            related_receipt_vouchers = ReceiptVoucher.objects.filter(
                invoice_no=invoice_no).exclude(pk=receipt_voucher.id)
            print('related_receipt_vouchers: ', related_receipt_vouchers)
            if len(related_receipt_vouchers) == 1:
                related_receipt_voucher = related_receipt_vouchers[0]
                receipt_voucher_dict['related_ledger'] = str(
                    related_receipt_voucher.ledger.name)
                pass
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
def getAccountSummaryForReceiptVoucher(request):
    receipt_vouchers = ReceiptVoucherFilter(
        request.GET, queryset=ReceiptVoucher.objects.all())
    receipt_vouchers = receipt_vouchers.qs
    total_elements = receipt_vouchers.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    receipt_vouchers = pagination.paginate_data(receipt_vouchers)
    print('receipt_vouchers: ', receipt_vouchers)

    receipt_voucher_dict = {}

    if len(receipt_vouchers) > 0:
        for receipt_voucher in receipt_vouchers:
            if receipt_voucher.sub_ledger:
                sub_ledger = str(receipt_voucher.sub_ledger.name)
                if sub_ledger not in receipt_voucher_dict.keys():
                    receipt_voucher_dict[sub_ledger] = 0
                dr = receipt_voucher.debit_amount
                cr = receipt_voucher.credit_amount
                amount = cr + dr
                receipt_voucher_dict[sub_ledger] += Decimal(amount)

    response = {
        'receipt_voucher_summary': receipt_voucher_dict,
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
    request=SalesSerializer,
    responses=SalesSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAccountReportForSales(request):
    sales_objs = Sales.objects.filter(ledger__name='Company Sales')
    sales = SalesFilter(request.GET, queryset=sales_objs)
    sales = sales.qs
    total_elements = sales.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    sales = pagination.paginate_data(sales)
    print('sales: ', sales)

    response_list = []

    if len(sales) > 0:
        for sale in sales:
            sale_dict = {}
            invoice_no = sale.invoice_no
            sale_serializer = SalesListSerializer(sale)
            for key, value in sale_serializer.data.items():
                sale_dict[key] = value
            related_sales = Sales.objects.filter(
                invoice_no=invoice_no).exclude(pk=sale.id)
            print('related_sales: ', related_sales)
            if len(related_sales) == 1:
                related_sale = related_sales[0]
                sale_dict['related_ledger'] = str(related_sale.ledger.name)
                pass
            elif len(related_sales) > 0:
                name_list = []
                for related_sale in related_sales:
                    name_list.append(str(related_sale.ledger.name))
                sale_dict['related_ledgers'] = name_list
            response_list.append(sale_dict)

    response = {
        'sales': response_list,
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
    request=SalesSerializer,
    responses=SalesSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAccountSummaryForSales(request):
    sales_objs = Sales.objects.filter(ledger__name='Company Sales')
    sales = SalesFilter(request.GET, queryset=sales_objs)
    sales = sales.qs
    total_elements = sales.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    sales = pagination.paginate_data(sales)
    print('sales: ', sales)

    sale_dict = {}

    if len(sales) > 0:
        for sale in sales:
            if sale.sub_ledger:
                sub_ledger = str(sale.sub_ledger.name)
                if sub_ledger not in sale_dict.keys():
                    sale_dict[sub_ledger] = 0
                dr = sale.debit_amount
                cr = sale.credit_amount
                amount = cr + dr
                sale_dict[sub_ledger] += Decimal(amount)

    response = {
        'sale_summary': sale_dict,
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
def getAccountReportForPurchase(request):
    purchases_objs = Purchase.objects.filter(ledger__name='Company Purchase')
    purchases = PurchaseFilter(request.GET, queryset=purchases_objs)
    purchases = purchases.qs
    total_elements = purchases.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    purchases = pagination.paginate_data(purchases)
    print('purchases: ', purchases)

    response_list = []

    if len(purchases) > 0:
        for purchase in purchases:
            purchase_dict = {}
            invoice_no = purchase.invoice_no
            purchase_serializer = PurchaseListSerializer(purchase)
            for key, value in purchase_serializer.data.items():
                purchase_dict[key] = value
            related_purchases = Sales.objects.filter(
                invoice_no=invoice_no).exclude(pk=purchase.id)
            print('related_purchases: ', related_purchases)
            if len(related_purchases) == 1:
                related_purchase = related_purchases[0]
                purchase_dict['related_ledger'] = str(
                    related_purchase.ledger.name)
                pass
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
def getAccountSummaryForPurchase(request):
    purchases_objs = Purchase.objects.filter(ledger__name='Company Purchase')
    purchases = PurchaseFilter(request.GET, queryset=purchases_objs)
    purchases = purchases.qs
    total_elements = purchases.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    purchases = pagination.paginate_data(purchases)
    print('purchases: ', purchases)

    purchase_dict = {}

    if len(purchases) > 0:
        for purchase in purchases:
            if purchase.sub_ledger:
                sub_ledger = str(purchase.sub_ledger.name)
                if sub_ledger not in purchase_dict.keys():
                    purchase_dict[sub_ledger] = 0
                dr = purchase.debit_amount
                cr = purchase.credit_amount
                amount = cr + dr
                purchase_dict[sub_ledger] += Decimal(amount)

    response = {
        'purchase_summary': purchase_dict,
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
    responses=ContraSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAccountReportForContra(request):
    contras = ContraFilter(request.GET, queryset=Contra.objects.all())
    contras = contras.qs
    total_elements = contras.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    contras = pagination.paginate_data(contras)
    print('contras: ', contras)

    response_list = []

    if len(contras) > 0:
        for contra in contras:
            contra_dict = {}
            invoice_no = contra.invoice_no
            contra_serializer = CountryListSerializer(contra)
            for key, value in contra_serializer.data.items():
                contra_dict[key] = value
            related_contras = Sales.objects.filter(
                invoice_no=invoice_no).exclude(pk=contra.id)
            print('related_contras: ', related_contras)
            if len(related_contras) == 1:
                related_contra = related_contras[0]
                contra_dict['related_ledger'] = str(related_contra.ledger.name)
                pass
            elif len(related_contras) > 0:
                name_list = []
                for related_contra in related_contras:
                    name_list.append(str(related_contra.ledger.name))
                contra_dict['related_ledgers'] = name_list
            response_list.append(contra_dict)

    response = {
        'contras': response_list,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)
