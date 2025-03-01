from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sequences import get_next_value

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import LedgerAccount, IDJournal, AccountLog
from account.serializers import IDJournalSerializer, IDJournalListSerializer, AccountLogListSerializer

from account.filters import IDJournalFilter

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
	request=IDJournalSerializer,
	responses=IDJournalSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAllIDJournal(request):
	idjournals = IDJournal.objects.all()
	total_elements = idjournals.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	idjournals = pagination.paginate_data(idjournals)

	serializer = IDJournalListSerializer(idjournals, many=True)

	response = {
		'idjournals': serializer.data,
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
	request=IDJournalSerializer,
	responses=IDJournalSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAllIDJournalByInvoiceNo(request, invoice_no):
	idjournals = IDJournal.objects.filter(invoice_no=invoice_no)
	total_elements = idjournals.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	idjournals = pagination.paginate_data(idjournals)

	serializer = IDJournalListSerializer(idjournals, many=True)

	response = {
		'idjournals': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	return Response(response, status=status.HTTP_200_OK)




@extend_schema(request=IDJournalSerializer, responses=IDJournalSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DETAILS.name])
def getAIDJournal(request, pk):
	try:
		idjournal = IDJournal.objects.get(pk=pk)
		serializer = IDJournalListSerializer(idjournal)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"IDJournal id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=IDJournalSerializer, responses=IDJournalSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchIDJournal(request):
	idjournals = IDJournalFilter(request.GET, queryset=IDJournal.objects.all())
	idjournals = idjournals.qs

	print('searched_products: ', idjournals)

	total_elements = idjournals.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	idjournals = pagination.paginate_data(idjournals)

	serializer = IDJournalListSerializer(idjournals, many=True)

	response = {
		'idjournals': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	if len(idjournals) > 0:
		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"There are no idjournals matching your search"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=IDJournalSerializer, responses=IDJournalSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_CREATE.name])
def createIDJournal(request):
	data = request.data
	print('data: ', data)

	response_data = {}

	current_date = date.today()
	current_date = str(current_date)
	current_date = current_date.replace('-', '')
	journal_current_date = 'JOURNAL' + current_date
	print('current_date: ', current_date, type(current_date))

	_num = get_next_value(journal_current_date)
	print('get_next_value: ', _num)

	invoice = 'JOURNAL' + current_date + '00' + str(_num)
	print('invoice: ', invoice)

	for idjournal in data:
		ledger_id = int(idjournal.get('ledger', None))
		journal_date = idjournal.get('journal_date', None)
		debit_amount = idjournal.get('debit_amount', None)
		credit_amount = idjournal.get('credit_amount', None)
		details = idjournal.get('details', None)
	

		ledger_acc_obj = LedgerAccount.objects.get(id=ledger_id)

		journal_datetime =  str(journal_date) + 'T' + str(datetime.now().time()) + 'Z'
		print('journal_datetime: ', journal_datetime)

		if request.user.is_authenticated:
			journal_obj = IDJournal.objects.create(
			ledger = ledger_acc_obj,
			invoice_no = invoice,
			journal_date = journal_datetime,
			debit_amount = debit_amount,
			credit_amount = credit_amount,
			details = details
			)

			account_log_obj = AccountLog.objects.create(
			log_type = 'Receipt Voucher',
			ledger = ledger_acc_obj,
			reference_no = invoice,
			log_date = journal_datetime,
			debit_amount = debit_amount,
			credit_amount = credit_amount,
			details = details
			)
		else:
			return Response({'detail': 'User is not authenticated.'}, status=status.HTTP_400_BAD_REQUEST)
	print('response_data: ', response_data)

	journal_objs = IDJournal.objects.filter(invoice_no=invoice)
	journal_serializer = IDJournalListSerializer(journal_objs, many=True)

	account_log_objs = AccountLog.objects.filter(reference_no=invoice)
	account_log_serializer = AccountLogListSerializer(account_log_objs, many=True)

	response_data['idjournals'] = journal_serializer.data
	response_data['account_logs'] = account_log_serializer.data

	return Response(response_data, status=status.HTTP_201_CREATED)




@extend_schema(request=IDJournalSerializer, responses=IDJournalSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_UPDATE.name])
def updateIDJournal(request):
	data = request.data
	journal_datetime = ""
	invoice = data[0]['invoice_no']
	account_log_objs = AccountLog.objects.filter(reference_no=invoice)
	print('account_log_objs: ', account_log_objs)

	print('data: ', data)

	response_data = {}
	i = 0
	for idjournal in data:
		ledger_id = int(idjournal.get('ledger', None))
		journal_id = int(idjournal.get('id', None))
		invoice_no = idjournal.get('invoice_no', None)
		journal_date = idjournal.get('journal_date', None)
		debit_amount = idjournal.get('debit_amount', None)
		credit_amount = idjournal.get('credit_amount', None)
		details = idjournal.get('details', None)

		if 'T' in journal_date:
			journal_datetime = journal_date
			print('journal_datetime if: ', journal_datetime)
		else:
			journal_datetime =  str(journal_date) + 'T' + str(datetime.now().time()) + 'Z'
			print('journal_datetime else: ', journal_datetime)
		
		ledger_acc_obj = LedgerAccount.objects.get(id=ledger_id)

		journal_obj = IDJournal.objects.get(id=journal_id)

		if request.user.is_authenticated:
			journal_obj.ledger = ledger_acc_obj
			journal_obj.invoice_no = invoice_no
			journal_obj.journal_date = journal_datetime
			journal_obj.debit_amount = debit_amount
			journal_obj.credit_amount = credit_amount
			journal_obj.details = details
			journal_obj.save()

			account_log_obj = account_log_objs[i]

			account_log_obj.ledger = ledger_acc_obj
			account_log_obj.log_type = 'Updated Receipt Voucher'
			account_log_obj.reference_no = invoice_no
			account_log_obj.log_date = journal_datetime
			account_log_obj.debit_amount = debit_amount
			account_log_obj.credit_amount = credit_amount
			account_log_obj.details = details
			account_log_obj.save()

			i += 1

		else:
			return Response({'detail':'User is not authenticated.'}, status=status.HTTP_400_BAD_REQUEST)
		
	journal_objs = IDJournal.objects.filter(invoice_no=invoice)
	journal_serializer = IDJournalListSerializer(journal_objs, many=True)

	account_log_objs = AccountLog.objects.filter(reference_no=invoice)
	account_log_serializer = AccountLogListSerializer(account_log_objs, many=True)

	response_data['idjournals'] = journal_serializer.data
	response_data['account_logs'] = account_log_serializer.data

	return Response({'data':response_data, 'detail':"Receipt voucher(s) updated successfully"})




@extend_schema(request=IDJournalSerializer, responses=IDJournalSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DELETE.name])
def deleteIDJournal(request, pk):
	try:
		idjournal = IDJournal.objects.get(pk=pk)
		idjournal.delete()
		return Response({'detail': f'IDJournal id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"IDJournal id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=IDJournalSerializer, responses=IDJournalSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DELETE.name])
def deleteMultipleIDJournal(request):
	ids = request.data['ids']
	try:
		idjournals = IDJournal.objects.filter(pk__in=ids)
		idjournals.delete()
		return Response({'detail': f'IDJournal ids - {ids} deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"IDJournal ids - {ids} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
