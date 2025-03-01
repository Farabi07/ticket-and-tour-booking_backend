from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from member.models import ExecutiveMember
from member.serializers import ExecutiveMemberSerializer, ExecutiveMemberListSerializer

from commons.pagination import Pagination
from commons.enums import PermissionEnum

import datetime




# Create your views here.

@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=ExecutiveMemberListSerializer,
	responses=ExecutiveMemberListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllExecutiveMember(request):
	executive_members = ExecutiveMember.objects.all()
	total_elements = executive_members.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	executive_members = pagination.paginate_data(executive_members)

	serializer = ExecutiveMemberListSerializer(executive_members, many=True)

	response = {
		'executive_members': serializer.data,
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
	request=ExecutiveMemberListSerializer,
	responses=ExecutiveMemberListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllExecutiveMemberWithoutPagination(request):
	executive_members = ExecutiveMember.objects.all()

	serializer = ExecutiveMemberListSerializer(executive_members, many=True)

	response = {
		'executive_members': serializer.data,
	}

	return Response(response, status=status.HTTP_200_OK)




@extend_schema(request=ExecutiveMemberSerializer, responses=ExecutiveMemberSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getAExecutiveMember(request, pk):
	try:
		executive_member = ExecutiveMember.objects.get(pk=pk)
		serializer = ExecutiveMemberSerializer(executive_member)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"ExecutiveMember id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=ExecutiveMemberSerializer, responses=ExecutiveMemberSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createExecutiveMember(request):
	data = request.data
	print('data: ', data)
	
	serializer = ExecutiveMemberSerializer(data=data)

	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data)
	else:
		return Response(serializer.errors)




@extend_schema(request=ExecutiveMemberSerializer, responses=ExecutiveMemberSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
def updateExecutiveMember(request, pk):
	data = request.data

	try:
		executive_member = ExecutiveMember.objects.get(pk=pk)
	except ObjectDoesNotExist:
		return Response({'detail': f"ExecutiveMember id - {pk} doesn't exists"})

	serializer = ExecutiveMemberSerializer(executive_member, data=data)
	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)
	else:
		return Response(serializer.errors)
	




@extend_schema(request=ExecutiveMemberSerializer, responses=ExecutiveMemberSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DELETE.name])
def deleteExecutiveMember(request, pk):
	try:
		executive_member = ExecutiveMember.objects.get(pk=pk)
		executive_member.delete()
		return Response({'detail': f'ExecutiveMember id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"ExecutiveMember id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


