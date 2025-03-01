
from urllib import response
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import Group, PrimaryGroup
from account.serializers import GroupListSerializer, GroupSerializer

from account.filters import GroupFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination



# Create your views here.

@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=GroupSerializer,
	responses=GroupSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.SHIPPING_ADDRESS_LIST.name])
def getAllGroup(request):
	groups = Group.objects.all()
	total_elements = groups.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	groups = pagination.paginate_data(groups)

	serializer = GroupListSerializer(groups, many=True)

	response = {
		'groups': serializer.data,
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
	request=GroupSerializer,
	responses=GroupSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.SHIPPING_ADDRESS_LIST.name])
def getAllGroupWithoutPagination(request):
	groups = Group.objects.all()

	serializer = GroupListSerializer(groups, many=True)

	response = {
		'groups': serializer.data,
	}

	return Response(response, status=status.HTTP_200_OK)




@extend_schema(request=GroupSerializer, responses=GroupSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.SHIPPING_ADDRESS_DETAILS.name])
def getAGroup(request, pk):

	try:
		group_obj = Group.objects.get(id=pk)
		serializer = GroupListSerializer(group_obj)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Group with order id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=GroupSerializer, responses=GroupSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchGroup(request):
	groups = GroupFilter(request.GET, queryset=Group.objects.all())
	groups = groups.qs

	print('searched_products: ', groups)

	total_elements = groups.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	groups = pagination.paginate_data(groups)

	serializer = GroupListSerializer(groups, many=True)

	response = {
		'groups': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	if len(groups) > 0:
		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"There are no groups matching your search"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=GroupSerializer, responses=GroupSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.SHIPPING_ADDRESS_CREATE.name])
def createGroup(request):
	data = request.data
	serializer = GroupSerializer(data=data)

	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=GroupSerializer, responses=GroupSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.SHIPPING_ADDRESS_UPDATE.name])
def updateGroup(request,pk):
	try:
		group = Group.objects.get(pk=pk)
		data = request.data
		serializer = GroupSerializer(group, data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	except ObjectDoesNotExist:
		return Response({'detail': f"Group id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=GroupSerializer, responses=GroupSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.SHIPPING_ADDRESS_DELETE.name])
def deleteGroup(request, pk):
	try:
		group = Group.objects.get(pk=pk)
		group.delete()
		return Response({'detail': f'Group id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Group id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=GroupSerializer, responses=GroupSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.SHIPPING_ADDRESS_DELETE.name])
def deleteMultipleGroup(request):
	ids = request.data['ids']
	try:
		groups = Group.objects.filter(pk__in=ids)
		groups.delete()
		return Response({'detail': f'Group ids - {ids} deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Group ids - {ids} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)







# Test Case
def serialize(self, root):
        """Encodes a tree to a single string.  
        :type root: Node
        :rtype: str
        """
        def dfs(node, vals):
            if not node.children_set:
                return
            vals.append(str(node.val))
            for child in node.children:
                dfs(child, vals)
            vals.append("#")
        
        vals = []
        dfs(root, vals)
        return " ".join(vals)

@extend_schema(request=GroupSerializer, responses=GroupSerializer)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.SHIPPING_ADDRESS_DELETE.name])
def testGroup(request):
	primary_groups = PrimaryGroup.objects.all()
	groups = Group.objects.filter(head_primarygroup__in=primary_groups)

	total_elements = groups.count()
	page = request.query_params.get('page')
	size = request.query_params.get('size')
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	groups = pagination.paginate_data(groups)


	serializer = GroupListSerializer(groups, many=True)

	response = {
		'groups': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages, 
		'total_elements' : total_elements
	}
	return Response(response)






