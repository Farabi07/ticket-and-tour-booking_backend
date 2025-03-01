from random import randrange
from time import process_time_ns
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

from authentication.serializers import AdminUserMinimalListSerializer

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from cms.models import CMSMenu, CMSMenuContentImage, CMSMenuContentImage
from cms.serializers import CMSMenuContentImageSerializer, CMSMenuContentImageListSerializer, \
    CMSMenuContentImageMinimalSerializer

from commons.pagination import Pagination
from commons.enums import PermissionEnum

import datetime


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=CMSMenuContentImageSerializer,
    responses=CMSMenuContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCMSMenuContentImage(request):
    content_images = CMSMenuContentImage.objects.all()
    print('content_images: ', content_images)

    total_elements = content_images.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    content_images = pagination.paginate_data(content_images)

    serializer = CMSMenuContentImageListSerializer(content_images, many=True)

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
    request=CMSMenuContentImageSerializer,
    responses=CMSMenuContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCMSMenuContentImageWithoutPagination(request):
    content_images = CMSMenuContentImage.objects.all()
    print('content_images: ', content_images)

    serializer = CMSMenuContentImageMinimalSerializer(content_images, many=True)

    response = {
        'content_images': serializer.data,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=CMSMenuContentImageSerializer,
    responses=CMSMenuContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCMSMenuContentImageByMenuId(request, menu_id):
    content_images = CMSMenuContentImage.objects.filter(cms_menu=menu_id)
    serializer = CMSMenuContentImageListSerializer(content_images, many=True)

    if content_images.count() > 0:
        response = {
            'content_images': serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"CMSMenuContentImage with menu {menu_id} does't exist"},
                        status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=CMSMenuContentImageSerializer,
	responses=CMSMenuContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllContentImageListByMenuId(request, menu_id):

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
			from cms_cmsmenucontentimage where cms_menu_id=%s
			group by head) as x;
						''', [menu_id])
		row = cursor.fetchone()
		print('row: ', row)
		print('row type: ', type(row))

	if type(row) == tuple:
		my_data = row[0]

		response = {
		'content_images': my_data,
		}

		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': "No content found."}, status=status.HTTP_204_NO_CONTENT)



@extend_schema(request=CMSMenuContentImageSerializer, responses=CMSMenuContentImageSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getACMSMenuContentImage(request, pk):
    try:
        content_images = CMSMenuContentImage.objects.get(pk=pk)
        serializer = CMSMenuContentImageSerializer(content_images)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"CMSMenuContentImage id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=CMSMenuContentImageSerializer, responses=CMSMenuContentImageSerializer)
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createCMSMenuContentImage(request):
    data = request.data
    print('data: ', data)
    print('content_type: ', request.content_type)

    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    menu_id = data.get('cms_menu')
    head = data.get('head')

    try:
        cms_menu_obj = CMSMenu.objects.get(pk=menu_id)
    except CMSMenu.DoesNotExist:
        return Response({'detail': "CMSMenu id {menu_id} doesn't exist."}, status=status.HTTP_400_BAD_REQUEST)

    for i in range(len(filtered_data) - 2):
        try:
            image = filtered_data[f'images[0][{i}]']
            print('image: ', image)
            print('image type: ', type(image))
            CMSMenuContentImage.objects.create(cms_menu=cms_menu_obj, head=head, image=image)
        except KeyError:
            pass
    content_images = CMSMenuContentImage.objects.filter(cms_menu=cms_menu_obj)
    serializer = CMSMenuContentImageListSerializer(content_images, many=True)
    if content_images.count() > 0:
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


@extend_schema(request=CMSMenuContentImageSerializer, responses=CMSMenuContentImageSerializer)
@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
# @parser_classes([MultiPartParser, FormParser])
def updateCMSMenuContentImage(request, pk):
    data = request.data
    print('data :', data)
    filtered_data = {}

    try:
        menu_obj = CMSMenuContentImage.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response({'detail': f"Product id - {pk} doesn't exists"})

    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    image = filtered_data.get('image', None)

    if image is not None and type(image) == str:
        popped_image = filtered_data.pop('image')

    serializer = CMSMenuContentImageSerializer(menu_obj, data=filtered_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=CMSMenuContentImageSerializer, responses=CMSMenuContentImageSerializer)
@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DELETE.name])
def deleteCMSMenuContentImage(request, pk):
    try:
        content_images = CMSMenuContentImage.objects.get(pk=pk)
        content_images.delete()
        return Response({'detail': f'CMSMenuContentImage id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"CMSMenuContentImage id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)
