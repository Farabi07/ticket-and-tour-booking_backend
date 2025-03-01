import imp
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
from django.db.models.query_utils import PathInfo

from rest_framework import status
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from authentication.models import Branch

from sequences import get_next_value

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import LedgerAccount, Sales, AccountLog, SubLedgerAccount
from account.serializers import AccountLogSerializer, SalesListCustomSerializer, SalesSerializer, SalesListSerializer, AccountLogListSerializer

from account.filters import SalesFilter

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
	request=SalesSerializer,
	responses=SalesSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAllSales(request):
	sales = Sales.objects.filter(ledger__name='Company Sales').order_by('-invoice_no').distinct('invoice_no')
	total_elements = sales.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	sales = pagination.paginate_data(sales)

	response_list = []

	if len(sales) > 0:
		for sale in sales:
			sale_dict = {}
			invoice_no = sale.invoice_no
			sale_serializer = SalesListCustomSerializer(sale)
			for key, value in sale_serializer.data.items():
				sale_dict[key] = value
			related_sales = Sales.objects.filter(invoice_no=invoice_no).exclude(pk=sale.id)
			print('related_sales: ', related_sales)
			if len(related_sales) == 1:
				related_sale = related_sales[0]
				sale_dict['related_ledgers'] = str(related_sale.ledger.name)
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
def getAllSalesByInvoiceNo(request, invoice_no):
	response_data = {}
	response_data['items'] = []

	sales = Sales.objects.filter(invoice_no=invoice_no)

	if len(sales) > 0:
		response_data['invoice_no'] = sales[0].invoice_no
		if sales[0].sub_ledger:
			response_data['sub_ledger'] = {'id': sales[0].sub_ledger.id, 'name': sales[0].sub_ledger.name}
		else:	
			response_data['sub_ledger'] = None
		if sales[0].branch:
			response_data['branch'] = {'id': sales[0].branch.id, 'name': sales[0].branch.name}
		else:
			response_data['branch'] = None
		response_data['sales_date'] = sales[0].sales_date
		response_data['details'] = sales[0].details

		for sale in sales:
			serializer = SalesListSerializer(sale)
			response_data['items'].append(serializer.data)

		return Response(response_data, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"Invoice no {invoice_no} has no"})




@extend_schema(request=SalesSerializer, responses=SalesSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DETAILS.name])
def getASales(request, pk):
	try:
		sale = Sales.objects.get(pk=pk)
		serializer = SalesListSerializer(sale)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Sales id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=SalesSerializer, responses=SalesSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchSales(request):
	invoice_no = request.query_params.get('invoice_no', None)
	sales = Sales.objects.filter(ledger__name='Company Sales', invoice_no=invoice_no)

	print('sales: ', sales)

	total_elements = sales.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	sales = pagination.paginate_data(sales)

	response_list = []

	if len(sales) > 0:
		for sale in sales:
			sale_dict = {}
			invoice_no = sale.invoice_no
			sale_serializer = SalesListCustomSerializer(sale)
			for key, value in sale_serializer.data.items():
				sale_dict[key] = value
			related_sales = Sales.objects.filter(invoice_no=invoice_no).exclude(pk=sale.id)
			print('related_sales: ', related_sales)
			if len(related_sales) == 1:
				related_sale = related_sales[0]
				sale_dict['related_ledgers'] = str(related_sale.ledger.name)
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




@extend_schema(request=SalesSerializer, responses=SalesSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_CREATE.name])
def createSales(request):
	data = request.data
	print('data: ', data)

	sub_ledger = data.get('sub_ledger', None)
	branch = data.get('branch', None)
	file = data.get('file', None)
	details = data.get('details', None)
	sales_date = data.get('sales_date', None)
	sales_datetime =  str(sales_date) + 'T' + str(datetime.now().time())
	print('sales_datetime: ', sales_datetime)

	branch_obj = None
	sub_ledger_obj = None
	if branch:
		branch_obj = Branch.objects.get(pk=branch)
	if sub_ledger:
		sub_ledger_obj = SubLedgerAccount.objects.get(pk=sub_ledger)

	current_date = date.today()
	current_date = str(current_date)
	current_date = current_date.replace('-', '')
	sa_current_date = 'SA' + current_date
	print('current_date: ', current_date, type(current_date))

	_num = get_next_value(sa_current_date)
	print('get_next_value: ', _num)

	invoice = 'SA' + current_date + '00' + str(_num)
	print('invoice: ', invoice)

	items = []
	for i in range(int(len(data) / 3)):
		ledger = data.get(f'items[{i}][ledger]', None)
		debit_amount = data.get(f'items[{i}][debit_amount]', None)
		credit_amount = data.get(f'items[{i}][credit_amount]', None)
		if ledger is not None and debit_amount is not None and credit_amount is not None:
			items.append({'ledger': ledger, 'debit_amount': debit_amount, 'credit_amount': credit_amount})
	
	print('items', items)

	for sale in items:
		print('sale: ', sale)
		ledger = sale.get('ledger', None)
		debit_amount = Decimal(sale.get('debit_amount', None))
		credit_amount = Decimal(sale.get('credit_amount', None))

		ledger_obj = None
		if ledger:
			ledger_obj = LedgerAccount.objects.get(pk=ledger)

		sale_obj = Sales.objects.create(
		ledger = ledger_obj,
		sub_ledger = sub_ledger_obj,
		branch = branch_obj,
		file = file,
		invoice_no = invoice,
		sales_date = sales_datetime,
		debit_amount = debit_amount,
		credit_amount = credit_amount,
		details = details
		)

		account_log_obj = AccountLog.objects.create(
		log_type = 'sales',
		ledger = ledger_obj,
		sub_ledger = sub_ledger_obj,
		branch = branch_obj,
		reference_no = invoice,
		log_date = sales_datetime,
		debit_amount = debit_amount,
		credit_amount = credit_amount,
		details = details
		)

	sale_objs = Sales.objects.filter(invoice_no=invoice)
	sale_serializer = SalesListSerializer(sale_objs, many=True)
	print('sale_objs: ', sale_objs)

	account_log_objs = AccountLog.objects.filter(reference_no=invoice)
	account_log_serializer = AccountLogListSerializer(account_log_objs, many=True)

	response = {
	'sales': sale_serializer.data,
	'account_logs': account_log_serializer.data
	}

	return Response(response, status=status.HTTP_201_CREATED)




@extend_schema(request=SalesSerializer, responses=SalesSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_UPDATE.name])
def updateSales(request):
	data = request.data
	print('data: ', data)

	branch = data.get('branch', None)
	file = data.get('file', None)
	sub_ledger = data.get('sub_ledger', None)
	invoice_no = data.get('invoice_no', None)
	sales_date = str(data.get('sales_date', None))
	details = data.get('details', None)

	account_log_objs = AccountLog.objects.filter(reference_no=invoice_no)
	print('account_log_objs: ', account_log_objs)

	sales_datetime = ""
	if 'T' in sales_date:
			sales_datetime = sales_date
			print('sales_datetime if: ', sales_datetime)
	else:
		sales_datetime =  str(sales_date) + 'T' + str(datetime.now().time())
		print('sales_datetime else: ', sales_datetime)

	items = []
	for i in range(int(len(data) / 3)):
		id = data.get(f'items[{i}][id]', None)
		ledger = data.get(f'items[{i}][ledger]', None)
		debit_amount = data.get(f'items[{i}][debit_amount]', None)
		credit_amount = data.get(f'items[{i}][credit_amount]', None)
		if ledger is not None and debit_amount is not None and credit_amount is not None:
			items.append({'id': id, 'ledger': ledger, 'debit_amount': debit_amount, 'credit_amount': credit_amount})

	index = 0
	response_data = {}
	for sale in items:
		sale_dict = {}
		sale_id = sale.get('id', None)
		print('sale_id: ', sale_id)

		sale_dict['ledger'] = sale['ledger']
		sale_dict['debit_amount'] = sale['debit_amount']
		sale_dict['credit_amount'] = sale['credit_amount']

		sale_dict['branch'] = branch
		if not type(file) is str:
			sale_dict['file'] = file
		sale_dict['sub_ledger'] = sub_ledger
		sale_dict['invoice_no'] = invoice_no
		sale_dict['sales_date'] = sales_datetime
		sale_dict['details'] = details

		sale_dict['reference_no'] = invoice_no
		sale_dict['log_type'] = 'Sales'
		sale_dict['log_date'] = sales_datetime

		if sale_id is not None:
			sale_obj = Sales.objects.get(pk=sale_id)
			sale_serializer = SalesSerializer(sale_obj, data=sale_dict)
			if sale_serializer.is_valid():
				sale_serializer.save()
			account_log_serializer = AccountLogSerializer(account_log_objs[index], data=sale_dict)
			if account_log_serializer.is_valid():
				account_log_serializer.save()
			index += 1
		else:
			new_sale_serializer = SalesSerializer(data=sale_dict)
			if new_sale_serializer.is_valid():
				new_sale_serializer.save()
			new_account_log_serializer = AccountLogSerializer(data=sale_dict)
			if new_account_log_serializer.is_valid():
				new_account_log_serializer.save()
		
	sale_objs = Sales.objects.filter(invoice_no=invoice_no)
	sale_serializer = SalesListSerializer(sale_objs, many=True)

	account_log_objs = AccountLog.objects.filter(reference_no=invoice_no)
	account_log_serializer = AccountLogListSerializer(account_log_objs, many=True)

	response_data['sales'] = sale_serializer.data
	response_data['account_logs'] = account_log_serializer.data

	return Response({'data':response_data, 'detail':"Sales(s) updated successfully"})




@extend_schema(request=SalesSerializer, responses=SalesSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DELETE.name])
def deleteSales(request, pk):
	try:
		sale = Sales.objects.get(pk=pk)
		sale.delete()
		return Response({'detail': f'Sales id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Sales id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=SalesSerializer, responses=SalesSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DELETE.name])
def deleteMultipleSales(request):
	ids = request.data['ids']
	try:
		sales = Sales.objects.filter(pk__in=ids)
		sales.delete()
		return Response({'detail': f'Sales ids - {ids} deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Sales ids - {ids} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
