from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

from authentication.serializers import AdminUserMinimalListSerializer
from cms.models import CMSMenu

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from donation.models import Cause, CauseContentImage, CauseContentImage
from donation.serializers import CauseContentImageSerializer, CauseContentImageListSerializer, CauseContentImageMinimalSerializer

from commons.pagination import Pagination
from commons.enums import PermissionEnum

import datetime


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=CauseContentImageSerializer,
    responses=CauseContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCauseContentImage(request):
    content_images = CauseContentImage.objects.all()
    print('content_images: ', content_images)

    total_elements = content_images.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    content_images = pagination.paginate_data(content_images)

    serializer = CauseContentImageListSerializer(content_images, many=True)

    response = {
        'content_images': serializer.data,
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
    request=CauseContentImageSerializer,
    responses=CauseContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCauseContentImageWithoutPagination(request):
    content_images = CauseContentImage.objects.all()
    print('content_images: ', content_images)

    serializer = CauseContentImageMinimalSerializer(content_images, many=True)

    response = {
        'content_images': serializer.data,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=CauseContentImageSerializer,
    responses=CauseContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCauseContentImageByCauseId(request, cause_id):

    with connection.cursor() as cursor:
        cursor.execute('''
			select
			json_object_agg(
				head,
				case
				when array_length(image,1)=1 then to_json(image[1])
				else to_json(image)
				end)
			from (
			select head, array_agg(image) as image
			from donation_causecontentimage where cause_id=%s
			group by head) as x;
						''', [cause_id])
        row = cursor.fetchone()
        print('row: ', row)
        print('row type: ', type(row))
    my_data = row[0]

    response = {
        'content_images': my_data,
    }
    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=CauseContentImageSerializer, responses=CauseContentImageSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getACauseContentImage(request, pk):
    try:
        content_images = CauseContentImage.objects.get(pk=pk)
        serializer = CauseContentImageSerializer(content_images)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"CauseContentImage id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=CauseContentImageSerializer, responses=CauseContentImageSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createCauseContentImage(request):
    data = request.data
    print('data: ', data)
    print('content_type: ', request.content_type)

    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)
    cause_id = data.get('cause')
    head = data.get('head')

    try:
        cause_obj = Cause.objects.get(pk=cause_id)
    except Cause.DoesNotExist:
        return Response({'detail': "Cause id {cause_id} doesn't exist."}, status=status.HTTP_400_BAD_REQUEST)

    for i in range(len(filtered_data) - 2):
        try:
            image = filtered_data[f'images[0][{i}]']
            print('image: ', image)
            print('image type: ', type(image))
            CauseContentImage.objects.create(
                cause=cause_obj, head=head, image=image)
        except KeyError:
            pass
    content_images = CauseContentImage.objects.filter(cause=cause_obj)
    serializer = CauseContentImageListSerializer(content_images, many=True)
    if content_images.count() > 0:
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


@extend_schema(request=CauseContentImageSerializer, responses=CauseContentImageSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
# @parser_classes([MultiPartParser, FormParser])
def updateCauseContentImage(request, pk):
    data = request.data
    print('data :', data)
    filtered_data = {}

    try:
        menu_obj = CauseContentImage.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response({'detail': f"Product id - {pk} doesn't exists"})

    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    image = filtered_data.get('image', None)

    if image is not None and type(image) == str:
        popped_image = filtered_data.pop('image')

    serializer = CauseContentImageSerializer(menu_obj, data=filtered_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors)


@extend_schema(request=CauseContentImageSerializer, responses=CauseContentImageSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DELETE.name])
def deleteCauseContentImage(request, pk):
    try:
        content_images = CauseContentImage.objects.get(pk=pk)
        content_images.delete()
        return Response({'detail': f'CauseContentImage id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"CauseContentImage id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)
