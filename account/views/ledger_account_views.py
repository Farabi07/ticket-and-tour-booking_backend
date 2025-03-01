from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import LedgerAccount
from account.serializers import LedgerAccountSerializer, LedgerAccountListSerializer

from account.filters import LedgerAccountFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination




# Create your views here.

@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=LedgerAccountSerializer,
	responses=LedgerAccountSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_LIST.name])
def getAllLedgerAccount(request):
	ledger_accounts = LedgerAccount.objects.all()
	total_elements = ledger_accounts.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	ledger_accounts = pagination.paginate_data(ledger_accounts)

	serializer = LedgerAccountListSerializer(ledger_accounts, many=True)

	response = {
		'ledger_accounts': serializer.data,
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
	request=LedgerAccountSerializer,
	responses=LedgerAccountSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_LIST.name])
def getAllLedgerAccountWithoutPagination(request):
	ledger_accounts = LedgerAccount.objects.all()

	serializer = LedgerAccountListSerializer(ledger_accounts, many=True)

	response = {
		'ledger_accounts': serializer.data,
	}

	return Response(response, status=status.HTTP_200_OK)




@extend_schema(request=LedgerAccountSerializer, responses=LedgerAccountSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_DETAILS.name])
def getALedgerAccount(request, pk):
	try:
		ledger_account = LedgerAccount.objects.get(pk=pk)
		serializer = LedgerAccountListSerializer(ledger_account)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"LedgerAccount id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=LedgerAccountSerializer, responses=LedgerAccountSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchLedgerAccount(request):
	ledger_accounts = LedgerAccountFilter(request.GET, queryset=LedgerAccount.objects.all())
	ledger_accounts = ledger_accounts.qs

	print('ledger_accounts: ', ledger_accounts)

	total_elements = ledger_accounts.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	ledger_accounts = pagination.paginate_data(ledger_accounts)

	serializer = LedgerAccountListSerializer(ledger_accounts, many=True)

	response = {
		'ledger_accounts': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	if len(ledger_accounts) > 0:
		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"There are no ledger_accounts matching your search"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=LedgerAccountSerializer, responses=LedgerAccountSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_CREATE.name])
def createLedgerAccount(request):
	data = request.data
	print('data: ', data)
	serializer = LedgerAccountSerializer(data=data)

	if serializer.is_valid():
		print('validated_data: ', serializer.validated_data)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=LedgerAccountSerializer, responses=LedgerAccountSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_UPDATE.name])
def updateLedgerAccount(request,pk):
	try:
		ledger_account = LedgerAccount.objects.get(pk=pk)
		data = request.data
		serializer = LedgerAccountSerializer(ledger_account, data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	except ObjectDoesNotExist:
		return Response({'detail': f"LedgerAccount id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=LedgerAccountSerializer, responses=LedgerAccountSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_DELETE.name])
def deleteLedgerAccount(request, pk):
	try:
		ledger_account = LedgerAccount.objects.get(pk=pk)
		ledger_account.delete()
		return Response({'detail': f'LedgerAccount id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"LedgerAccount id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=LedgerAccountSerializer, responses=LedgerAccountSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_DELETE.name])
def deleteMultipleLedgerAccount(request):
	ids = request.data['ids']
	try:
		ledger_accounts = LedgerAccount.objects.filter(pk__in=ids)
		ledger_accounts.delete()
		return Response({'detail': f'LedgerAccount ids - {ids} deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"LedgerAccount ids - {ids} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


