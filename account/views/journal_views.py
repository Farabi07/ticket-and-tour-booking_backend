from django.core.exceptions import ObjectDoesNotExist
from authentication.models import Branch

from rest_framework import status
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sequences import get_next_value

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import LedgerAccount, Journal, AccountLog
from account.serializers import AccountLogSerializer, JournalListCustomSerializer, JournalSerializer, JournalListSerializer, AccountLogListSerializer

from account.filters import JournalFilter

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
	request=JournalSerializer,
	responses=JournalSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAllJournal(request):
	journals = Journal.objects.all().order_by('invoice_no').distinct('invoice_no')
	total_elements = journals.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	journals = pagination.paginate_data(journals)

	serializer = JournalListCustomSerializer(journals, many=True)

	response = {
		'journals': serializer.data,
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
	request=JournalSerializer,
	responses=JournalSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAllJournalByInvoiceNo(request, invoice_no):
	response_data = dict()
	response_data['items'] = list()

	journals = Journal.objects.filter(invoice_no=invoice_no)
	journals = journals.reverse()
	print('contras: ', journals)

	if len(journals):
		response_data['invoice_no'] = journals[0].invoice_no

		if journals[0].branch:
			response_data['branch'] = {"id": journals[0].branch.id, "name": journals[0].branch.name}
		else:
			response_data['branch'] = None
		response_data['journal_date'] = journals[0].journal_date
		response_data['details'] = journals[0].details

		for contra in journals:
			serializer = JournalListSerializer(contra)
			response_data['items'].append(serializer.data)

		print('items: ', response_data['items'])

		return Response(response_data, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"Invoice_no {invoice_no} has no journals"})




@extend_schema(request=JournalSerializer, responses=JournalSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DETAILS.name])
def getAJournal(request, pk):
	try:
		journal = Journal.objects.get(pk=pk)
		serializer = JournalListSerializer(journal)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Journal id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=JournalSerializer, responses=JournalSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchJournal(request):
	invoice_no = request.query_params.get('invoice_no', None)

	journals = JournalFilter(request.GET, queryset=Journal.objects.all().order_by('invoice_no').distinct('invoice_no'))
	journals = journals.qs

	print('searched_products: ', journals)

	total_elements = journals.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	journals = pagination.paginate_data(journals)

	serializer = JournalListCustomSerializer(journals, many=True)

	response = {
		'journals': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	if len(journals) > 0:
		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"There are no journals matching your search"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=JournalSerializer, responses=JournalSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_CREATE.name])
def createJournal(request):
	data = request.data
	items = data.get('items', None)
	print('data: ', data)

	response_data = {}

	details = data.get('details', None)
	branch = data.get('branch', None)
	journal_date = data.get('journal_date', None)
	journal_datetime =  str(journal_date) + 'T' + str(datetime.now().time()) + 'Z'
	print('journal_datetime: ', journal_datetime)

	current_date = date.today()
	current_date = str(current_date)
	current_date = current_date.replace('-', '')
	journal_current_date = 'JOURNAL' + current_date
	print('current_date: ', current_date, type(current_date))

	_num = get_next_value(journal_current_date)
	print('get_next_value: ', _num)

	invoice = 'JO' + current_date + '00' + str(_num)
	print('invoice: ', invoice)

	branch_obj = None
	if branch:
		branch_obj = Branch.objects.get(pk=branch)

	for journal in items:
		ledger_id = int(journal.get('ledger', None))
		debit_amount = journal.get('debit_amount', None)
		credit_amount = journal.get('credit_amount', None)

		ledger_acc_obj = LedgerAccount.objects.get(pk=ledger_id)

		journal_obj = Journal.objects.create(
		ledger = ledger_acc_obj,
		invoice_no = invoice,
		branch = branch_obj,
		journal_date = journal_datetime,
		debit_amount = debit_amount,
		credit_amount = credit_amount,
		details = details
		)

		account_log_obj = AccountLog.objects.create(
		log_type = 'journal',
		ledger = ledger_acc_obj,
		reference_no = invoice,
		branch = branch_obj,
		log_date = journal_datetime,
		debit_amount = debit_amount,
		credit_amount = credit_amount,
		details = details
		)

	print('response_data: ', response_data)

	journal_objs = Journal.objects.filter(invoice_no=invoice)
	journal_serializer = JournalListSerializer(journal_objs, many=True)

	account_log_objs = AccountLog.objects.filter(reference_no=invoice)
	account_log_serializer = AccountLogListSerializer(account_log_objs, many=True)

	response_data['journals'] = journal_serializer.data
	response_data['account_logs'] = account_log_serializer.data

	return Response(response_data, status=status.HTTP_201_CREATED)




@extend_schema(request=JournalSerializer, responses=JournalSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_UPDATE.name])
def updateJournal(request):
	data = request.data
	items = data.get('items', None)
	print('data: ', data)
	print('items', items)

	branch = data.get('branch', None)
	invoice_no = data.get('invoice_no', None)
	journal_date = str(data.get('journal_date', None))
	details = data.get('details', None)

	account_log_objs = AccountLog.objects.filter(reference_no=invoice_no)
	print('account_log_objs: ', account_log_objs)

	journal_datetime = ""
	if 'T' in journal_date:
			journal_datetime = journal_date
			print('journal_datetime if: ', journal_datetime)
	else:
		journal_datetime =  str(journal_date) + 'T' + str(datetime.now().time())
		print('journal_datetime else: ', journal_datetime)

	index = 0
	response_data = {}

	for journal in items:
		journal_dict = {}
		journal_id = journal.get('id', None)
		print('contra_id: ', journal_id)
		
		journal_dict['ledger'] = journal['ledger']
		journal_dict['debit_amount'] = journal['debit_amount']
		journal_dict['credit_amount'] = journal['credit_amount']

		journal_dict['branch'] = branch
		journal_dict['invoice_no'] = invoice_no
		journal_dict['journal_date'] = journal_datetime
		journal_dict['details'] = details

		journal_dict['reference_no'] = invoice_no
		journal_dict['log_type'] = 'Contra'
		journal_dict['log_date'] = journal_datetime

		if journal_id:
			journal_obj = Journal.objects.get(pk=journal_id)
			journal_serializer = JournalSerializer(journal_obj, data=journal_dict)
			if journal_serializer.is_valid():
				print('validated_data: ', journal_serializer.validated_data)
				journal_serializer.save()
			account_log_serializer = AccountLogSerializer(account_log_objs[index], data=journal_dict)
			if account_log_serializer.is_valid():
				account_log_serializer.save()
			index += 1
		else:
			new_journal_serializer = JournalSerializer(data=journal_dict)
			if new_journal_serializer.is_valid():
				print('validated_data: ', new_journal_serializer.validated_data)
				new_journal_serializer.save()
			new_account_log_serializer = AccountLogSerializer(data=journal_dict)
			if new_account_log_serializer.is_valid():
				new_account_log_serializer.save()
		
	contra_objs = Journal.objects.filter(invoice_no=invoice_no)
	journal_serializer = JournalListSerializer(contra_objs, many=True)

	account_log_objs = AccountLog.objects.filter(reference_no=invoice_no)
	account_log_serializer = AccountLogListSerializer(account_log_objs, many=True)

	response_data['journals'] = journal_serializer.data
	response_data['account_logs'] = account_log_serializer.data

	return Response({'data':response_data, 'detail':"Payment voucher(s) updated successfully"})




@extend_schema(request=JournalSerializer, responses=JournalSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DELETE.name])
def deleteJournal(request, pk):
	try:
		journal = Journal.objects.get(pk=pk)
		journal.delete()
		return Response({'detail': f'Journal id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Journal id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=JournalSerializer, responses=JournalSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_DELETE.name])
def deleteMultipleJournal(request):
	ids = request.data['ids']
	try:
		journals = Journal.objects.filter(pk__in=ids)
		journals.delete()
		return Response({'detail': f'Journal ids - {ids} deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Journal ids - {ids} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
