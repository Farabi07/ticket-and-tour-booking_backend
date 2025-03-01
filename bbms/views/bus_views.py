
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
from bbms.models import Bus, BusBooking,AvailableDates
from bbms.utils import generate_seat_name
from member.serializers import MemberSerializer


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=BusSerializer,
    responses=BusSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([AuthPermEnum.DESIGNATION_LIST.name])
def getAllBus(request):
    buses = Bus.objects.all()  # Fetch all buses
    bus_data = []

    # Get all FIT bus bookings and their corresponding booked dates, grouped by bus
    fit_buses = Bus.objects.filter(tour_type='FIT')
    fit_booked_dates = {}
    
    # Get booked dates for each FIT bus
    for fit_bus in fit_buses:
        booked_dates = BusBooking.objects.filter(bus=fit_bus).values_list('date', flat=True)
        fit_booked_dates[fit_bus.id] = [date.strftime('%m/%d/%Y') for date in booked_dates]
    
    print("FIT buses and their booked dates:", fit_booked_dates)

    for bus in buses:
        serializer = BusSerializer(bus).data
        
        # Fetch available dates for the current bus
        available_dates = AvailableDates.objects.filter(bus_data=bus.id)
        available_dates_serializer_data = AvailableDatesSerializer(available_dates, many=True).data
        available_datas = [item['date'] for item in available_dates_serializer_data]
        print(f"Available dates for bus {bus.id} before filtering:", available_datas)

        # For FIT buses, remove dates booked by other FIT buses
        if bus.tour_type == 'FIT':
            # Get all booked dates from other FIT buses, excluding this bus's booked dates
            other_fit_booked_dates = [
                date for fit_bus_id, dates in fit_booked_dates.items() 
                if fit_bus_id != bus.id 
                for date in dates
            ]

            # Only keep available dates not booked by other FIT buses
            available_datas = [
                date for date in available_datas 
                if date not in other_fit_booked_dates
            ]
            print(f"Filtered available dates for FIT bus {bus.id}:", available_datas)

        # Add available dates (filtered for FIT buses) to the serialized bus data
        serializer['available_dates'] = available_datas
        bus_data.append(serializer)
    
    return Response(bus_data, status=status.HTTP_200_OK)



@extend_schema(
    request=BusSerializer,
    responses=BusSerializer
)
@api_view(['GET'])
def getAllBusWithoutPagination(request):
    bus = Bus.objects.all()
    serializer = BusSerializer(bus, many=True)
    response = {
        'bus': serializer.data,
    }
    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([AuthPermEnum.DESIGNATION_LIST.name])
def getABus(request, pk):
    try:
        # Retrieve the bus based on the provided primary key (pk)
        bus = Bus.objects.get(pk=pk)
        serializer = BusSerializer(bus).data

        # Fetch all booked dates for FIT buses
        fit_buses = Bus.objects.filter(tour_type='FIT')
        fit_booked_dates = {}

        # Get booked dates for each FIT bus
        for fit_bus in fit_buses:
            booked_dates = BusBooking.objects.filter(bus=fit_bus).values_list('date', flat=True)
            fit_booked_dates[fit_bus.id] = [date.strftime('%m/%d/%Y') for date in booked_dates]

        print("FIT buses and their booked dates:", fit_booked_dates)

        # Fetch available dates for the current bus
        available_dates = AvailableDates.objects.filter(bus_data=pk)
        available_dates_serializer_data = AvailableDatesSerializer(available_dates, many=True).data

        # Extract the available dates into a list
        available_datas = [item['date'] for item in available_dates_serializer_data]
        print(f"Available dates for bus {bus.id} before filtering:", available_datas)

        # Check if the bus is of type 'FIT'
        if bus.tour_type == 'FIT':
            # Get all booked dates from other FIT buses, excluding this bus's booked dates
            other_fit_booked_dates = [
                date for fit_bus_id, dates in fit_booked_dates.items() 
                if fit_bus_id != bus.id 
                for date in dates
            ]

            # Get all canceled bookings for FIT buses
            canceled_dates = BusBooking.objects.filter(bus__tour_type='FIT', status=BusBooking.TicketStatus.CANCELLED).values_list('date', flat=True)
            canceled_dates_list = [date.strftime('%m/%d/%Y') for date in canceled_dates]

            # Print debug info for canceled dates
            print("Cancellations found, adding to available dates:", canceled_dates_list)

            # If there are canceled bookings, add those dates to available_datas
            available_datas.extend(canceled_dates_list)

            # Remove duplicates from available_datas
            available_datas = list(set(available_datas))
            print("Available dates after adding cancellations:", available_datas)

            # Exclude dates that are booked by other FIT buses, 
            # but ensure canceled dates are always available
            available_datas = [
                date for date in available_datas 
                if date not in other_fit_booked_dates or date in canceled_dates_list
            ]
            print(f"Filtered available dates for FIT bus {bus.id}:", available_datas)

        # Add available dates to the serialized bus data
        serializer['available_dates'] = available_datas

        # Return the serialized bus data with available dates
        return Response(serializer, status=status.HTTP_200_OK)

    except Bus.DoesNotExist:
        return Response({'detail': f"Bus id - {pk} doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)







# def getABus(request, pk):
#     try:
#         bus = Bus.objects.filter(bus_data=pk)
#         serializer = BusSerializer(bus)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     except ObjectDoesNotExist:
#         return Response({'detail': f"Bus id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


def generate_reference_number(member_id):
    current_year = datetime.now().year
    return f"Re-{current_year}-00-{member_id}"
@extend_schema(request=BusSerializer, responses=BusSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_CREATE.name])

def createBus(request):
    data = request.data
    print('data: ', data)
    dates_data = data.pop('available_dates', []) 
    filtered_data = {}

    print("dates_data", dates_data)

    for key, value in data.items():
        if value != '' and value != 0 and value != '0' and key!= 'available_dates':
            filtered_data[key] = value

    try:
        serializer = BusSerializer(data=filtered_data)
        if serializer.is_valid():
            bus_instance = serializer.save()
            # instance.dates.set(dates)
            for date_str in dates_data:
                # date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
                # AvailableDates.objects.get_or_create(bus_data=bus_instance, date=date_str)
                AvailableDates.objects.get_or_create(bus_data=bus_instance,date=date_str)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # transaction.set_rollback(True)
        return Response(f"Error: {str(e)}", status=status.HTTP_400_BAD_REQUEST)

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


@extend_schema(request=BusSerializer, responses=BusSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
def updateBus(request, pk):
    try:
        bus_instance = Bus.objects.get(pk=pk)
        data = request.data
        dates_data = data.pop('available_dates', [])

        # Update bus instance fields
        for key, value in data.items():
            if key in ['created_by', 'updated_by'] and value:
                try:
                    user_instance = User.objects.get(pk=value)
                    setattr(bus_instance, key, user_instance)
                except User.DoesNotExist:
                    return Response({'detail': f"User id - {value} doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                setattr(bus_instance, key, value)

        # Save the updated bus instance
        bus_instance.save()

        # Get current available dates
        current_dates = AvailableDates.objects.filter(bus_data=bus_instance)
        current_dates_str = set(current_dates.values_list('date', flat=True))
        new_dates_str = set(dates_data)

        # Remove dates that are no longer available
        dates_to_remove = current_dates_str - new_dates_str
        AvailableDates.objects.filter(bus_data=bus_instance, date__in=dates_to_remove).delete()

        # Add or update dates that are in the new list
        for date_str in new_dates_str:
            AvailableDates.objects.update_or_create(bus_data=bus_instance, date=date_str)

        # Serialize the updated bus instance and return response
        serializer = BusSerializer(bus_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return Response({'detail': f"Bus id - {pk} doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
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



@extend_schema(request=BusSerializer, responses=BusSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])

def deleteBus(request, pk):
    try:
        buses = Bus.objects.get(pk=pk)
        buses.delete()
        return Response({'detail': f'Bus  id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Bus  id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(request=BusSerializer, responses=BusSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_DETAILS.name])
def searchBus(request):
	keyword = request.query_params.get('key', None)
	print('keyword: ', keyword)
	if keyword:
		bus = Bus.objects.filter(Q(name__icontains=keyword)|Q(type__icontains=keyword)|
                           Q(owner_name__icontains=keyword)|Q(primary_phone__exact=keyword))
	else:
		return Response({'detail':f"Please enter Bus to search."})
	serializer = BusSerializer(bus, many=True)
	response = {
		'buses': serializer.data,
	}
	if len(bus) > 0:
		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"There are no bus matching your search"}, status=status.HTTP_400_BAD_REQUEST)
	

@extend_schema(request=BusSerializer, responses=BusSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
    
def getABusWithDateAndTime(request, pk, date, time,):
    try:
        bus = Bus.objects.get(id=pk)
        seat_quantity = bus.seat_quantity
        # total_seats = seat_quantity // 4 * 4 
        booked_seats = BusBooking.objects.filter(bus=bus, date=date, booking_time=time)
        print("booked_seats", booked_seats)
        booked_seat_numbers = booked_seats.values_list('seat_no', flat=True)
        booked_seats_count = len(booked_seat_numbers)
        available_seats_count = max(seat_quantity - booked_seats_count, 0)
        rows = (seat_quantity) // 4 
        last_row_seats = seat_quantity % 4 
        
        # Generate seats for the last row
        last_row = [generate_seat_name(rows, col, bus.seat_plan) for col in range(last_row_seats)]
        all_seats = [generate_seat_name(row, col, bus.seat_plan) for row in range(rows) for col in range(4)]
        all_seats += last_row
        
        available_seats = [seat for seat in all_seats if seat not in booked_seat_numbers][:available_seats_count]
        
        bus_data = BusSerializer(bus).data
        seat_info = []
        for seat in all_seats:
            booking = booked_seats.filter(seat_no=seat).first()
            if booking:
                booking_info = {
                    'bus_booking_id': booking.id, 
                    'seat_no': booking.seat_no,
                    'passenger': PassengerSerializer(booking.passenger).data if booking.passenger else None,
                    'member': MemberSerializer(booking.member).data if booking.member else None,
                    'status': 'booked' if booking.status == BusBooking.TicketStatus.BOOKED else 'available',
                }
                seat_info.append(booking_info)
            else:
                seat_info.append({'seat_no': seat, 'bus_booking_id': None, 'passenger_first_name': None, 'passenger_last_name': None, 'passenger_primary_phone': None, 'member': None, 'status': 'available'})

        bus_data['date'] = date
        bus_data['time'] = time
        bus_data['available_seats'] = len(available_seats)
        bus_data['seat_info'] = seat_info
        
        return Response(bus_data)
    except Bus.DoesNotExist:
        return Response({"message": "Bus not found"}, status=status.HTTP_404_NOT_FOUND)