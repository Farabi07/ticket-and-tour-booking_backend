from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from donation.models import CauseContent
from donation.serializers import CauseContentSerializer, CauseContentListSerializer

from commons.pagination import Pagination
from commons.enums import PermissionEnum

import datetime


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=CauseContentListSerializer,
    responses=CauseContentListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCauseContent(request):
    cause_contents = CauseContent.objects.all()
    total_elements = cause_contents.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    cause_contents = pagination.paginate_data(cause_contents)

    serializer = CauseContentListSerializer(cause_contents, many=True)

    response = {
        'cause_contents': serializer.data,
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
    request=CauseContentListSerializer,
    responses=CauseContentListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCauseContentByCauseId(request, cause_id):
    # cause_contents = CauseContent.objects.filter(cms_menu=cms_menu_id)

    with connection.cursor() as cursor:
        cursor.execute('''
						SELECT 
							cause_id AS cause,
							json_object_agg(name, value) AS data
						FROM donation_causecontent WHERE cause_id=%s
						GROUP BY cause_id
						ORDER BY cause_id;
						''', [cause_id])
        row = cursor.fetchone()
        print('row: ', row)
        print('row type: ', type(row))

    my_data = row[1]
    print("my_data:", my_data)

    response = {
        'cause_contents': my_data,

    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=CauseContentSerializer, responses=CauseContentSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getACauseContent(request, pk):
    try:
        cause_content = CauseContent.objects.get(pk=pk)
        serializer = CauseContentSerializer(cause_content)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"CauseContent id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=CauseContentSerializer, responses=CauseContentSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createCauseContent(request):
    data = request.data
    print('data: ', data)
    print('content_type: ', request.content_type)

    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0' and value != 'undefined':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    serializer = CauseContentSerializer(data=filtered_data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors)


@extend_schema(request=CauseContentSerializer, responses=CauseContentSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
def updateCauseContent(request, pk):
    data = request.data

    try:
        cause_content = CauseContent.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response({'detail': f"CauseContent id - {pk} doesn't exists"})

    serializer = CauseContentSerializer(cause_content, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors)


@extend_schema(request=CauseContentSerializer, responses=CauseContentSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DELETE.name])
def deleteCauseContent(request, pk):
    try:
        cause_content = CauseContent.objects.get(pk=pk)
        cause_content.delete()
        return Response({'detail': f'CauseContent id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"CauseContent id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)
