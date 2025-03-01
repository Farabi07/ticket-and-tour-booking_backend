
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
from bbms.models import Bus
from authentication.decorators import has_permissions
from authentication.models import User

from commons.pagination import Pagination
from bbms.serializers import *
from bbms.models import Bus, BookingSummary,AvailableDates
from bbms.utils import generate_seat_name
from member.serializers import MemberSerializer
from bbms.filters import BookingSummaryFilter
from rest_framework import viewsets, filters
from django_filters import rest_framework as django_filters

# Create your views here.

# @extend_schema(
#     parameters=[
#         OpenApiParameter("page"),
#         OpenApiParameter("size"),
#   ],
#     request=BusSerializer,
#     responses=BusSerializer
# )
# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # @has_permissions([AuthPermEnum.DESIGNATION_LIST.name])
# def getAllBus(request):
#     try:
#         buses = Bus.objects.all()
#         bus_data = []
        
#         for bus in buses:
#             serializer = BusSerializer(bus).data
            
#             available_dates = AvailableDates.objects.filter(bus_data=bus.id)
#             available_dates_serializer_data = AvailableDatesSerializer(available_dates, many=True).data
#             available_datas = [item['date'] for item in available_dates_serializer_data]
            
#             serializer['available_dates'] = available_datas
#             bus_data.append(serializer)
        
#         return Response(bus_data, status=status.HTTP_200_OK)
    
#     except ObjectDoesNotExist:
#         return Response({'detail': 'No buses found'}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# def getAllBus(request):
#     buses = Bus.objects.all()
#     total_elements = buses.count()

#     page = request.query_params.get('page')
#     size = request.query_params.get('size')

#     # Pagination
#     pagination = Pagination()
#     pagination.page = page
#     pagination.size = size
#     buses = pagination.paginate_data(buses)

#     serializer = BusSerializer(buses, many=True)

#     response = {
#         'buses': serializer.data,
#         'page': pagination.page,
#         'size': pagination.size,
#         'total_pages': pagination.total_pages,
#         'total_elements': total_elements,
#     }

#     return Response(response, status=status.HTTP_200_OK)


# @extend_schema(
#     request=BusSerializer,
#     responses=BusSerializer
# )
# @api_view(['GET'])
# def getAllBusWithoutPagination(request):
#     bus = Bus.objects.all()
#     serializer = BusSerializer(bus, many=True)
#     response = {
#         'bus': serializer.data,
#     }
#     return Response(response, status=status.HTTP_200_OK)

#------------work this----------
# @extend_schema(request=BusSerializer, responses=BusSerializer)
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def getBookingSummery(request, pk):
#     try:
#         # Retrieve all BookingSummary objects for the given member_id
#         booking_summaries = BookingSummary.objects.filter(member_id=pk)
#         serializer = BookingSummarySerializer(booking_summaries, many=True).data

#         # Retrieve the member data
#         member = Member.objects.get(pk=pk)
#         member_serializer_data = MemberSerializer(member).data

#         # Append member data to each booking summary in the serializer response
#         for booking_summary in serializer:
#             booking_summary['member'] = member_serializer_data

#         return Response(serializer, status=status.HTTP_200_OK)
#     except ObjectDoesNotExist:
#         return Response({'detail': f"Member id - {pk} doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def getBookingSummery(request):
    try:
        # Apply filters using BookingSummaryFilter
        queryset = BookingSummaryFilter(request.GET, queryset=BookingSummary.objects.all()).qs


        # Serialize filtered queryset
        serializer = BookingSummaryListSerializer(queryset, many=True).data

        # Retrieve the member data


        return Response(serializer, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Member id - {pk} doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
    
@extend_schema(
    request=BookingSummarySerializer,
    responses=BookingSummarySerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])

def getBookingSummaryReportWP(request):
    bus_booking_queryset = BookingSummaryFilter(request.GET, queryset=BookingSummary.objects.all()).qs
    
    member_tickets_count = bus_booking_queryset.values('member').annotate(total_tickets=Count('member'))
    print("member ticket",member_tickets_count)
    total_elements = bus_booking_queryset.count()
    print("-------------------------------------")
    print("farabi ticket",total_elements)


    serializer = BookingSummaryMinimalListSerializer(bus_booking_queryset, many=True)
   
    response = {
        'bus_bookings': serializer.data,
        'total_seats': len(member_tickets_count),
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)

# def getABus(request, pk):
#     try:
#         bus = Bus.objects.filter(bus_data=pk)
#         serializer = BusSerializer(bus)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     except ObjectDoesNotExist:
#         return Response({'detail': f"Bus id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)



# @extend_schema(request=BusSerializer, responses=BusSerializer)
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# # @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_CREATE.name])

# def createBus(request):
#     data = request.data
#     print('data: ', data)
#     dates_data = data.pop('available_dates', []) 
#     filtered_data = {}

#     print("dates_data", dates_data)

#     for key, value in data.items():
#         if value != '' and value != 0 and value != '0' and key!= 'available_dates':
#             filtered_data[key] = value

#     try:
#         serializer = BusSerializer(data=filtered_data)
#         if serializer.is_valid():
#             bus_instance = serializer.save()
#             # instance.dates.set(dates)
#             for date_str in dates_data:
#                 # date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
#                 # AvailableDates.objects.get_or_create(bus_data=bus_instance, date=date_str)
#                 AvailableDates.objects.get_or_create(bus_data=bus_instance,date=date_str)

#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         # transaction.set_rollback(True)
#         return Response(f"Error: {str(e)}", status=status.HTTP_400_BAD_REQUEST)
# def createBus(request):
#     data = request.data
#     filtered_data = {}
    
#     for key, value in data.items():
#         if value != '' and value != '0':
#             filtered_data[key] = value
        
   
#     serializer = BusSerializer(data=filtered_data)
#     if serializer.is_valid():
#         serializer.save()
      
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @extend_schema(request=BusSerializer, responses=BusSerializer)
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# # @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
# def updateBus(request, pk):
#     try:
#         bus_instance = Bus.objects.get(pk=pk)
#         data = request.data
#         dates_data = data.pop('available_dates', [])

#         # Update bus instance fields
#         for key, value in data.items():
#             if key in ['created_by', 'updated_by'] and value:
#                 try:
#                     user_instance = User.objects.get(pk=value)
#                     setattr(bus_instance, key, user_instance)
#                 except User.DoesNotExist:
#                     return Response({'detail': f"User id - {value} doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 setattr(bus_instance, key, value)

#         # Save the updated bus instance
#         bus_instance.save()

#         # Get current available dates
#         current_dates = AvailableDates.objects.filter(bus_data=bus_instance)
#         current_dates_str = set(current_dates.values_list('date', flat=True))
#         new_dates_str = set(dates_data)

#         # Remove dates that are no longer available
#         dates_to_remove = current_dates_str - new_dates_str
#         AvailableDates.objects.filter(bus_data=bus_instance, date__in=dates_to_remove).delete()

#         # Add or update dates that are in the new list
#         for date_str in new_dates_str:
#             AvailableDates.objects.update_or_create(bus_data=bus_instance, date=date_str)

#         # Serialize the updated bus instance and return response
#         serializer = BusSerializer(bus_instance)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     except ObjectDoesNotExist:
#         return Response({'detail': f"Bus id - {pk} doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# def updateBus(request,pk):
    
#     try:
#         data = request.data.copy()
#         bus = Bus.objects.get(pk=pk)
     
#         image = data.get('image', None)
#         if image is not None and type(image) == str:
#             popped_image = data.pop('image')


#         serializer = BusSerializer(bus, data=data)
#         if serializer.is_valid():
#             serializer.save()
         
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     except ObjectDoesNotExist:
#         return Response({'detail': f"Bus id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)



# @extend_schema(request=BusSerializer, responses=BusSerializer)
# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])

# def deleteBus(request, pk):
#     try:
#         buses = Bus.objects.get(pk=pk)
#         buses.delete()
#         return Response({'detail': f'Bus  id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
#     except ObjectDoesNotExist:
#         return Response({'detail': f"Bus  id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)



# @extend_schema(request=BusSerializer, responses=BusSerializer)
# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_DETAILS.name])
# def searchBus(request):
# 	keyword = request.query_params.get('key', None)
# 	print('keyword: ', keyword)
# 	if keyword:
# 		bus = Bus.objects.filter(Q(name__icontains=keyword)|Q(type__icontains=keyword)|
#                            Q(owner_name__icontains=keyword)|Q(primary_phone__exact=keyword))
# 	else:
# 		return Response({'detail':f"Please enter Bus to search."})
# 	serializer = BusSerializer(bus, many=True)
# 	response = {
# 		'buses': serializer.data,
# 	}
# 	if len(bus) > 0:
# 		return Response(response, status=status.HTTP_200_OK)
# 	else:
# 		return Response({'detail': f"There are no bus matching your search"}, status=status.HTTP_400_BAD_REQUEST)
	

# @extend_schema(request=BusSerializer, responses=BusSerializer)
# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
    
# def getABusWithDateAndTime(request, pk, date, time,):
#     try:
#         bus = Bus.objects.get(id=pk)
#         seat_quantity = bus.seat_quantity
#         # total_seats = seat_quantity // 4 * 4 
        
        
#         booked_seats = BookingSummary.objects.filter(bus=bus, date=date, booking_time=time)
#         print("booked_seats", booked_seats)
#         booked_seat_numbers = booked_seats.values_list('seat_no', flat=True)
#         booked_seats_count = len(booked_seat_numbers)
#         available_seats_count = max(seat_quantity - booked_seats_count, 0)
#         rows = (seat_quantity) // 4 
#         last_row_seats = seat_quantity % 4 
        
#         # Generate seats for the last row
#         last_row = [generate_seat_name(rows, col, bus.seat_plan) for col in range(last_row_seats)]
#         all_seats = [generate_seat_name(row, col, bus.seat_plan) for row in range(rows) for col in range(4)]
#         all_seats += last_row
        
#         available_seats = [seat for seat in all_seats if seat not in booked_seat_numbers][:available_seats_count]
        
#         bus_data = BusSerializer(bus).data
#         seat_info = []
#         for seat in all_seats:
#             booking = booked_seats.filter(seat_no=seat).first()
#             if booking:
#                 booking_info = {
#                     'bus_booking_id': booking.id, 
#                     'seat_no': booking.seat_no,
#                     'passenger': PassengerSerializer(booking.passenger).data if booking.passenger else None,
#                     'member': MemberSerializer(booking.member).data if booking.member else None,
#                 }
#                 seat_info.append(booking_info)
#             else:
#                 seat_info.append({'seat_no': seat, 'bus_booking_id': None, 'passenger_first_name': None, 'passenger_last_name': None, 'passenger_primary_phone': None, 'member': None})

#         bus_data['date'] = date
#         bus_data['time'] = time
#         bus_data['available_seats'] = len(available_seats)
#         bus_data['seat_info'] = seat_info
        
#         return Response(bus_data)
#     except Bus.DoesNotExist:
#         return Response({"message": "Bus not found"}, status=status.HTTP_404_NOT_FOUND)