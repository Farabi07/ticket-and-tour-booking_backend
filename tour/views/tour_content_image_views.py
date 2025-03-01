from random import randrange
from time import process_time_ns
from urllib import response
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

from authentication.serializers import AdminUserMinimalListSerializer

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from tour.models import TourContent,TourContentImage, TourContentImage
from tour.serializers import TourContentImageSerializer, TourContentImageListSerializer, TourContentImageMinimalSerializer,TourContentListSerializer

from commons.pagination import Pagination
from commons.enums import PermissionEnum

import datetime




# Create your views here.

@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=TourContentImageSerializer,
	responses=TourContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllTourContentImage(request):
	content_images = TourContentImage.objects.all()
	print('content_images: ', content_images)

	total_elements = content_images.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	content_images = pagination.paginate_data(content_images)

	serializer = TourContentImageListSerializer(content_images, many=True)

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
	request=TourContentImageSerializer,
	responses=TourContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllContentImageWP(request):
	content_images = TourContentImage.objects.all()
	print('content_images: ', content_images)

	serializer = TourContentImageMinimalSerializer(content_images, many=True)

	response = {
		'content_images': serializer.data,
	}

	return Response(response, status=status.HTTP_200_OK)





@extend_schema(request=TourContentImageSerializer, responses=TourContentImageSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getAllContentImageByMenuId(request, menu_id):
	content_images = TourContentImage.objects.filter(cms_menu=menu_id)
	serializer = TourContentImageListSerializer(content_images, many=True)

	if content_images.count() > 0:
		response = {
			'content_images': serializer.data,
		}
		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"TourContentImage with menu {menu_id} does't exist"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=TourContentImageSerializer,
	responses=TourContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllContentImageListByMenuId(request, menu_id):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT
                head AS menu_item_name,
                json_agg(
                    CASE
                        WHEN cloudflare_image IS NOT NULL THEN cloudflare_image
                        ELSE image
                    END
                ) AS images
            FROM cms_cmsmenucontentimage
            WHERE cms_menu_id = %s
            GROUP BY head;
        ''', [menu_id])
        rows = cursor.fetchall()

    content_images = {}
    for row in rows:
        content_images[row[0]] = row[1]

    if content_images:
        return Response({'content_images': content_images}, status=status.HTTP_200_OK)
    else:
        return Response({'detail': "No content found."}, status=status.HTTP_204_NO_CONTENT)



@extend_schema(request=TourContentImageSerializer, responses=TourContentImageSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getATourContentImageByContentTitle(request, image_name):
    try:
      
        content_image = TourContentImage.objects.get(image_name=image_name)
        
      
        serializer = TourContentImageSerializer(content_image)
        
       
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except ObjectDoesNotExist:
        
        return Response({'detail': f"TourContentImage with image_name '{image_name}' does not exist"}, 
                        status=status.HTTP_404_NOT_FOUND)


@extend_schema(request=TourContentImageSerializer, responses=TourContentImageSerializer)
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createTourContentImage(request):
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
			TourContentImage.objects.create(cms_menu=cms_menu_obj, head=head, image=image)
		except KeyError:
			pass
	content_images = TourContentImage.objects.filter(cms_menu=cms_menu_obj)
	serializer = TourContentImageListSerializer(content_images, many=True)
	if content_images.count() > 0:
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	else:
		return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)




@extend_schema(request=TourContentImageSerializer, responses=TourContentImageSerializer)
@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
# @parser_classes([MultiPartParser, FormParser])
def updateTourContentImage(request, pk):
	data = request.data
	print('data :', data)
	filtered_data = {}

	try:
		menu_obj = TourContentImage.objects.get(pk=pk)
	except ObjectDoesNotExist:
		return Response({'detail': f"Product id - {pk} doesn't exists"})

	for key, value in data.items():
		if value != '' and value != '0':
			filtered_data[key] = value

	print('filtered_data: ', filtered_data)

	image = filtered_data.get('image', None)

	if image is not None and type(image) == str:
		popped_image = filtered_data.pop('image')

	serializer = TourContentImageSerializer(menu_obj, data=filtered_data)
	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=TourContentImageSerializer, responses=TourContentImageSerializer)
@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DELETE.name])
def deleteTourContentImage(request, pk):
	try:
		content_images = TourContentImage.objects.get(pk=pk)
		content_images.delete()
		return Response({'detail': f'TourContentImage id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"TourContentImage id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=TourContentImageSerializer, responses=TourContentImageSerializer)
@api_view(['GET'])
def getContentImageListByMenuName(request, menu_name):
    try:
        
        matching_menus = CMSMenu.objects.filter(name__icontains=menu_name)
        
        if matching_menus.exists():
            
            content_images_dict = {}
            
            
            for cms_menu in matching_menus:
                
                content_images = TourContentImage.objects.filter(cms_menu=cms_menu)
                
                
                for image in content_images:
                    menu_item_name = image.head
                    if image.cloudflare_image:
                        image_url = image.cloudflare_image
                    else:
                        image_url = image.image
                    
                    if menu_item_name in content_images_dict:
                        content_images_dict[menu_item_name].append(image_url)
                    else:
                        content_images_dict[menu_item_name] = [image_url]
            
            
            return Response({'content_images': content_images_dict}, status=status.HTTP_200_OK)
        else:
            
            return Response({'detail': f"No menus found matching '{menu_name}'"}, status=status.HTTP_404_NOT_FOUND)
    
    except ObjectDoesNotExist:
        
        return Response({'detail': f"No content images found for menu '{menu_name}'"}, status=status.HTTP_404_NOT_FOUND)
	

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def get_content_and_images_by_menu_id(request, menu_id):
    try:
        cms_content_obj = TourContent.objects.filter(cms_menu=menu_id)

        serializer = TourContentListSerializer(cms_content_obj, many=True)
		
        return Response(serializer.data, status=status.HTTP_200_OK)

    except TourContent.DoesNotExist:
        return Response({'detail': f"No content found for menu_id={menu_id}"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)