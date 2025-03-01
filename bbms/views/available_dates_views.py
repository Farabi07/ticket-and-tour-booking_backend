
import os
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from authentication.models import  Permission
from django.db.models import Q
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions


from commons.pagination import Pagination
from bbms.serializers import AvailableDatesSerializer, PassengerSerializer
from bbms.models import AvailableDates, BusBooking
from bbms.utils import generate_seat_name
from member.serializers import MemberSerializer


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=AvailableDatesSerializer,
    responses=AvailableDatesSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([AuthPermEnum.DESIGNATION_LIST.name])
def getAllAvailableDates(request):
    availabledateses = AvailableDates.objects.all()
    total_elements = availabledateses.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    availabledateses = pagination.paginate_data(availabledateses)

    serializer = AvailableDatesSerializer(availabledateses, many=True)

    response = {
        'availabledateses': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    request=AvailableDatesSerializer,
    responses=AvailableDatesSerializer
)
@api_view(['GET'])
def getAllAvailableDatesWithoutPagination(request):
    availabledates = AvailableDates.objects.all()
    serializer = AvailableDatesSerializer(availabledates, many=True)
    response = {
        'availabledates': serializer.data,
    }
    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=AvailableDatesSerializer, responses=AvailableDatesSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
def getAAvailableDates(request, pk):
    try:
        availabledates = AvailableDates.objects.get(pk=pk)
        serializer = AvailableDatesSerializer(availabledates)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"AvailableDates id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(request=AvailableDatesSerializer, responses=AvailableDatesSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_CREATE.name])
def createAvailableDates(request):
    data = request.data
    filtered_data = {}
    
    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value
        
   
    serializer = AvailableDatesSerializer(data=filtered_data)
    if serializer.is_valid():
        serializer.save()
      
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=AvailableDatesSerializer, responses=AvailableDatesSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
def updateAvailableDates(request,pk):
    
    try:
        data = request.data.copy()
        availabledates = AvailableDates.objects.get(pk=pk)
     
        image = data.get('image', None)
        if image is not None and type(image) == str:
            popped_image = data.pop('image')


        serializer = AvailableDatesSerializer(availabledates, data=data)
        if serializer.is_valid():
            serializer.save()
         
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'detail': f"AvailableDates id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(request=AvailableDatesSerializer, responses=AvailableDatesSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])

def deleteAvailableDates(request, pk):
    try:
        availabledateses = AvailableDates.objects.get(pk=pk)
        availabledateses.delete()
        return Response({'detail': f'AvailableDates  id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"AvailableDates  id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(request=AvailableDatesSerializer, responses=AvailableDatesSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_DETAILS.name])
def searchAvailableDates(request):
	keyword = request.query_params.get('key', None)
	print('keyword: ', keyword)
	if keyword:
		availabledates = AvailableDates.objects.filter(Q(name__icontains=keyword)|Q(type__icontains=keyword)|
                           Q(owner_name__icontains=keyword)|Q(primary_phone__exact=keyword))
	else:
		return Response({'detail':f"Please enter AvailableDates to search."})
	serializer = AvailableDatesSerializer(availabledates, many=True)
	response = {
		'availabledateses': serializer.data,
	}
	if len(availabledates) > 0:
		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"There are no availabledates matching your search"}, status=status.HTTP_400_BAD_REQUEST)
	

# @extend_schema(request=AvailableDatesSerializer, responses=AvailableDatesSerializer)
# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
    
# def getAAvailableDatesWithDateAndTime(request, pk, date, time):
#     try:
#         availabledates = AvailableDates.objects.get(id=pk)
#         seat_quantity = availabledates.seat_quantity
#         # total_seats = seat_quantity // 4 * 4 
        
        
#         booked_seats = AvailableDatesBooking.objects.filter(availabledates=availabledates, date=date, booking_time=time)
#         booked_seat_numbers = booked_seats.values_list('seat_no', flat=True)
#         booked_seats_count = len(booked_seat_numbers)
#         available_seats_count = max(seat_quantity - booked_seats_count, 0)
#         rows = (seat_quantity) // 4 
#         last_row_seats = seat_quantity % 4 
        
#         # Generate seats for the last row
#         last_row = [generate_seat_name(rows, col, availabledates.seat_plan) for col in range(last_row_seats)]
#         all_seats = [generate_seat_name(row, col, availabledates.seat_plan) for row in range(rows) for col in range(4)]
#         all_seats += last_row
        
#         available_seats = [seat for seat in all_seats if seat not in booked_seat_numbers][:available_seats_count]
        
#         availabledates_data = AvailableDatesSerializer(availabledates).data
#         seat_info = []
#         for seat in all_seats:
#             booking = booked_seats.filter(seat_no=seat).first()
#             if booking:
#                 booking_info = {
#                     'availabledates_booking_id': booking.id, 
#                     'seat_no': booking.seat_no,
#                     'passenger': PassengerSerializer(booking.passenger).data if booking.passenger else None,
#                     'member': MemberSerializer(booking.member).data if booking.member else None,
#                 }
#                 seat_info.append(booking_info)
#             else:
#                 seat_info.append({'seat_no': seat, 'availabledates_booking_id': None, 'passenger_first_name': None, 'passenger_last_name': None, 'passenger_primary_phone': None, 'member': None})

#         availabledates_data['date'] = date
#         availabledates_data['time'] = time
#         availabledates_data['available_seats'] = len(available_seats)
#         availabledates_data['seat_info'] = seat_info
        
#         return Response(availabledates_data)
#     except AvailableDates.DoesNotExist:
#         return Response({"message": "AvailableDates not found"}, status=status.HTTP_404_NOT_FOUND)