from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import SubLedgerAccount
from account.serializers import SubLedgerAccountSerializer, SubLedgerAccountListSerializer

from account.filters import SubLedgerAccountFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination




# Create your views here.

@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=SubLedgerAccountSerializer,
	responses=SubLedgerAccountSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_LIST.name])
def getAllSubLedgerAccount(request):
	sub_ledgers = SubLedgerAccount.objects.all()
	total_elements = sub_ledgers.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	sub_ledgers = pagination.paginate_data(sub_ledgers)

	serializer = SubLedgerAccountListSerializer(sub_ledgers, many=True)

	response = {
		'sub_ledgers': serializer.data,
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
	request=SubLedgerAccountSerializer,
	responses=SubLedgerAccountSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_LIST.name])
def getAllSubLedgerAccountWithoutPagination(request):
	sub_ledgers = SubLedgerAccount.objects.all()

	serializer = SubLedgerAccountListSerializer(sub_ledgers, many=True)

	response = {
		'sub_ledgers': serializer.data,
	}

	return Response(response, status=status.HTTP_200_OK)




@extend_schema(request=SubLedgerAccountSerializer, responses=SubLedgerAccountSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_DETAILS.name])
def getASubLedgerAccount(request, pk):
	try:
		sub_ledger = SubLedgerAccount.objects.get(pk=pk)
		serializer = SubLedgerAccountListSerializer(sub_ledger)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"SubLedgerAccount id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=SubLedgerAccountSerializer, responses=SubLedgerAccountSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchSubLedgerAccount(request):
	sub_ledgers = SubLedgerAccountFilter(request.GET, queryset=SubLedgerAccount.objects.all())
	sub_ledgers = sub_ledgers.qs

	print('searched_products: ', sub_ledgers)

	total_elements = sub_ledgers.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	sub_ledgers = pagination.paginate_data(sub_ledgers)

	serializer = SubLedgerAccountListSerializer(sub_ledgers, many=True)

	response = {
		'sub_ledgers': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	if len(sub_ledgers) > 0:
		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"There are no sub_ledgers matching your search"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=SubLedgerAccountSerializer, responses=SubLedgerAccountSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_CREATE.name])
def createSubLedgerAccount(request):
	data = request.data
	print('data: ', data)
	serializer = SubLedgerAccountSerializer(data=data)

	if serializer.is_valid():
		print('validated_data: ', serializer.validated_data)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=SubLedgerAccountSerializer, responses=SubLedgerAccountSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_UPDATE.name])
def updateSubLedgerAccount(request,pk):
	try:
		sub_ledger = SubLedgerAccount.objects.get(pk=pk)
		data = request.data
		serializer = SubLedgerAccountSerializer(sub_ledger, data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	except ObjectDoesNotExist:
		return Response({'detail': f"SubLedgerAccount id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=SubLedgerAccountSerializer, responses=SubLedgerAccountSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_DELETE.name])
def deleteSubLedgerAccount(request, pk):
	try:
		sub_ledger = SubLedgerAccount.objects.get(pk=pk)
		sub_ledger.delete()
		return Response({'detail': f'SubLedgerAccount id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"SubLedgerAccount id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=SubLedgerAccountSerializer, responses=SubLedgerAccountSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_DELETE.name])
def deleteMultipleSubLedgerAccount(request):
	ids = request.data['ids']
	try:
		ledger_accounts = SubLedgerAccount.objects.filter(pk__in=ids)
		ledger_accounts.delete()
		return Response({'detail': f'SubLedgerAccount ids - {ids} deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"SubLedgerAccount ids - {ids} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




