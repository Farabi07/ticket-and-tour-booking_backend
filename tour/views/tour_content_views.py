
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import Q
import os
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from tour.models import TourContent, TourContentImage
from tour.serializers import TourContentSerializer, TourContentListSerializer,TourContentImageSerializer

from commons.pagination import Pagination
from commons.enums import PermissionEnum

import datetime

# Create your views here.

@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=TourContentListSerializer,
	responses=TourContentListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])

def getAllTourContent(request):
	tour_contents = TourContent.objects.all()
	total_elements = tour_contents.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	tour_contents = pagination.paginate_data(tour_contents)

	serializer = TourContentListSerializer(tour_contents, many=True)

	response = {
		'tour_contents': serializer.data,
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
	request=TourContentListSerializer,
	responses=TourContentListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllTourContentWithoutPagination(request):
	tour_contents = TourContent.objects.all()

	serializer = TourContentListSerializer(tour_contents, many=True)

	response = {
		'tour_contents': serializer.data,
	}
	return Response(response, status=status.HTTP_200_OK)


@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=TourContentListSerializer,
	responses=TourContentListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllTourContentByTourId(request, menu_id):

	with connection.cursor() as cursor:
		cursor.execute('''
						SELECT
						cms_menu_id AS cms_menu,
							json_object_agg(name, value) AS data
						FROM cms_cmsmenucontent WHERE cms_menu_id=%s
						GROUP BY cms_menu_id
						ORDER BY cms_menu_id;
						''', [menu_id])
		row = cursor.fetchone()
		print('row: ', row)
		print('row type: ', type(row))

	if type(row) == tuple:
		my_data = row[1]

		response = {
		'tour_contents': my_data,
		}

		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': "No content found."}, status=status.HTTP_204_NO_CONTENT)



@extend_schema(request=TourContentSerializer, responses=TourContentSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getATourContent(request,pk):
	
	try:
		menu_item = TourContent.objects.get(pk=pk)
		serializer = TourContentSerializer(menu_item)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"TourContent name - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=TourContentSerializer, responses=TourContentSerializer)
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createTourContent(request):
    data = request.data
    print('data: ', data)

    # Process images and clean up the input data
    my_images = []
    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value

        # Collect images separately
        if key.startswith('images'):
            my_images.append(value)
    
    print("farabi images:", my_images)

    # Create the TourContent object and validate the data
    serializer = TourContentSerializer(data=filtered_data)
    
    if serializer.is_valid():
        # Save the TourContent object
        tour_content_obj = serializer.save()

        # Handle the images by passing the primary key (ID) of the tour_content object
        for image in my_images:
            if image:
                image_data = {'tour_content': tour_content_obj.id, 'image': image}
                image_serializer = TourContentImageSerializer(data=image_data)
                if image_serializer.is_valid():
                    image_serializer.save()
                else:
                    return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Return the created object data
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# @extend_schema(request=TourContentSerializer, responses=TourContentSerializer)
# @api_view(['PUT'])
# def updateTourContent(request, pk):
#     try:
#         tour_content = TourContent.objects.get(id=pk)
#     except TourContent.DoesNotExist:
#         return Response({"error": "TourContent not found"}, status=status.HTTP_404_NOT_FOUND)

#     data = request.data.copy()  # Copy request data to avoid modifying the original

#     print("Update data:", data)

#     # Preserve existing thumbnail if no new file is uploaded
#     if 'thumbnail_image' in request.FILES:
#         data['thumbnail_image'] = request.FILES['thumbnail_image']
#     else:
#         data.pop('thumbnail_image', None)  # Remove key so it doesn't overwrite existing file

#     # Process additional images separately
#     my_images = []
#     filtered_data = {}

#     for key, value in data.items():
#         if value not in ('', '0'):
#             filtered_data[key] = value

#         # Collect multiple image uploads
#         if key.startswith('images'):
#             my_images.append(value)

#     print("Updated images:", my_images)

#     # Update the TourContent object
#     serializer = TourContentSerializer(tour_content, data=filtered_data, partial=True)
    
#     if serializer.is_valid():
#         serializer.save()

#         # Handle images (Delete old images if necessary and add new ones)
#         existing_images = TourContentImage.objects.filter(tour_content=tour_content)
#         existing_images_list = [img.image.url for img in existing_images]

#         # Remove images that are no longer in the request
#         for image_obj in existing_images:
#             if image_obj.image.url not in my_images:
#                 image_obj.delete()

#         # Add new images
#         for image in request.FILES.getlist('images'):  # Handle multiple file uploads
#             if image and image.name not in existing_images_list:
#                 TourContentImage.objects.create(tour_content=tour_content, image=image)

#         return Response(serializer.data, status=status.HTTP_200_OK)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(request=TourContentSerializer, responses=TourContentSerializer)
@api_view(['PUT'])
def updateTourContent(request, pk):
    try:
        tour_content = TourContent.objects.get(id=pk)
    except TourContent.DoesNotExist:
        return Response({"error": "TourContent not found"}, status=status.HTTP_404_NOT_FOUND)

    # Preserve existing thumbnail if no new file is uploaded
    thumbnail_image = request.FILES.get('thumbnail_image', tour_content.thumbnail_image)

    # Separate images and other fields
    filtered_data = {}
    uploaded_images = []

    for key, value in request.data.items():
        if value and value not in ('', '0'):
            if key.startswith('images'):
                uploaded_images.append(value)
            else:
                filtered_data[key] = value

    filtered_data['thumbnail_image'] = thumbnail_image

    # Update the TourContent object
    serializer = TourContentSerializer(tour_content, data=filtered_data, partial=True)
    
    if serializer.is_valid():
        serializer.save()

        # Fetch existing images
        existing_images = TourContentImage.objects.filter(tour_content=tour_content)
        existing_image_urls = {img.image.url for img in existing_images}

        # Remove images that are not in the updated list
        existing_images.exclude(image__in=uploaded_images).delete()

        # Add new images
        new_images = [img for img in uploaded_images if img not in existing_image_urls]
        for image in new_images:
            TourContentImage.objects.create(tour_content=tour_content, image=image)

        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(request=TourContentSerializer, responses=TourContentSerializer)
@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DELETE.name])
def deleteTourContent(request, pk):
	try:
		menu_item = TourContent.objects.get(pk=pk)
		menu_item.delete()
		return Response({'detail': f'TourContent id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"TourContent id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)




# @extend_schema(request=TourContentSerializer, responses=TourContentSerializer)
# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
# def getTourContentByCMSMenyID(request, pk):
# 	try:
# 		main_menu = Tour.objects.get(pk=pk)
# 		tour_contents = TourContent.objects.filter(cms_menu=main_menu)
# 		serializer = TourContentSerializer(tour_contents, many=True)
# 		return Response(serializer.data, status=status.HTTP_200_OK)
# 	except ObjectDoesNotExist:
# 		return Response({'detail': f"TourContent id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


# @extend_schema(request=TourContentSerializer, responses=TourContentSerializer)
# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
# def get_tour_content_by_name(request,content_name,menu_name='Home'):
#     try:
#         menu = Tour.objects.get(name=menu_name)
#         tour_content = TourContent.objects.filter(slug=content_name, cms_menu=menu).first()

#         if tour_content:
#             serializer = TourContentSerializer(tour_content)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response({'detail': f"TourContent with name '{content_name}' not found for menu '{menu_name}'"},
#                             status=status.HTTP_404_NOT_FOUND)
#     except ObjectDoesNotExist:
#         return Response({'detail': f"Tour with name '{menu_name}' does not exist"}, status=status.HTTP_404_NOT_FOUND)




# import stripe
# from django.conf import settings
# from rest_framework.response import Response
# from rest_framework.decorators import api_view

# stripe.api_key = settings.STRIPE_SECRET_KEY

# @api_view(["POST"])
# def create_checkout_session(request):
#     try:
#         session = stripe.checkout.Session.create(
#             payment_method_types=["card"],
#             line_items=[
#                 {
#                     "price_data": {
#                         "currency": "usd",
#                         "product_data": {"name": "Test Product"},
#                         "unit_amount": 1000,  # $10.00
#                     },
#                     "quantity": 1,
#                 }
#             ],
#             mode="payment",
#             success_url="http://localhost:3000/success",
#             cancel_url="http://localhost:3000/cancel",
#         )
#         return Response({"sessionId": session.id, "url": session.url})
#     except Exception as e:
#         return Response({"error": str(e)}, status=500)
