from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import reset_queries
from django.utils import tree

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, OR
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import PrimaryGroup
from account.serializers import PrimaryGroupListSerializer, PrimaryGroupSerializer

from account.filters import PrimaryGroupFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=PrimaryGroupSerializer,
    responses=PrimaryGroupSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_LIST.name])
def getAllPrimaryGroup(request):
    primary_groups = PrimaryGroup.objects.all()
    total_elements = primary_groups.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    primary_groups = pagination.paginate_data(primary_groups)

    serializer = PrimaryGroupListSerializer(primary_groups, many=True)

    response = {
        'primary_groups': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    request=PrimaryGroupSerializer,
    responses=PrimaryGroupSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_LIST.name])
def getAllPrimaryGroupWithoutPagination(request):
    primary_groups = PrimaryGroup.objects.all()
    total_elements = primary_groups.count()

    serializer = PrimaryGroupListSerializer(primary_groups, many=True)

    response = {
        'primary_groups': serializer.data,
        'total_elements': total_elements
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=PrimaryGroupSerializer, responses=PrimaryGroupSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchPrimaryGroup(request):
    primary_groups = PrimaryGroupFilter(
        request.GET, queryset=PrimaryGroup.objects.all())
    primary_groups = primary_groups.qs

    print('searched_products: ', primary_groups)

    total_elements = primary_groups.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    primary_groupes = pagination.paginate_data(primary_groups)

    serializer = PrimaryGroupListSerializer(primary_groupes, many=True)

    response = {
        'primary_groups': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    if len(primary_groups) > 0:
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"There are no primary_groupes matching your search"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PrimaryGroupSerializer, responses=PrimaryGroupSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def deletePrimaryGroup(request, pk):
    pg = PrimaryGroup.objects.get(id=pk)
    try:
        pg.delete()
        return Response(f'primary group {pk} deleted successfully')
    except ValidationError:
        return Response("Primary Group can't be deleted!")
