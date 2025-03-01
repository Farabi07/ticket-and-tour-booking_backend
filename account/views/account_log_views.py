from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import AccountLog
from account.serializers import AccountLogSerializer, AccountLogListSerializer

from account.filters import AccountLogFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination



# Create your views here.

@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=AccountLogSerializer,
	responses=AccountLogSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_LIST.name])
def getAllAccountLog(request):
	account_logs = AccountLog.objects.all()
	total_elements = account_logs.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	account_logs = pagination.paginate_data(account_logs)

	serializer = AccountLogListSerializer(account_logs, many=True)

	response = {
		'account_logs': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	return Response(response, status=status.HTTP_200_OK)




@extend_schema(request=AccountLogSerializer, responses=AccountLogSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DETAILS.name])
def getAAccountLog(request, pk):
	try:
		account_log = AccountLog.objects.get(pk=pk)
		serializer = AccountLogListSerializer(account_log)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"AccountLog id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=AccountLogSerializer, responses=AccountLogSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchAccountLog(request):
	payment_methods = AccountLogFilter(request.GET, queryset=AccountLog.objects.all())
	payment_methods = payment_methods.qs

	print('searched_products: ', payment_methods)

	total_elements = payment_methods.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	payment_methods = pagination.paginate_data(payment_methods)

	serializer = AccountLogListSerializer(payment_methods, many=True)

	response = {
		'payment_methods': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	if len(payment_methods) > 0:
		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"There are no payment_methods matching your search"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=AccountLogSerializer, responses=AccountLogSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_CREATE.name])
def createAccountLog(request):
	data = request.data
	serializer = AccountLogSerializer(data=data)

	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=AccountLogSerializer, responses=AccountLogSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_UPDATE.name])
def updateAccountLog(request,pk):
	try:
		account_log = AccountLog.objects.get(pk=pk)
		data = request.data
		serializer = AccountLogSerializer(account_log, data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	except ObjectDoesNotExist:
		return Response({'detail': f"AccountLog id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=AccountLogSerializer, responses=AccountLogSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DELETE.name])
def deleteAccountLog(request, pk):
	try:
		account_log = AccountLog.objects.get(pk=pk)
		account_log.delete()
		return Response({'detail': f'AccountLog id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"AccountLog id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=AccountLogSerializer, responses=AccountLogSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DELETE.name])
def deleteMultipleAccountLog(request):
	ids = request.data['ids']
	try:
		account_logs = AccountLog.objects.filter(pk__in=ids)
		account_logs.delete()
		return Response({'detail': f'AccountLog ids - {ids} deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"AccountLog ids - {ids} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)

