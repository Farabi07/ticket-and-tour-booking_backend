
import datetime
from decimal import Decimal
import pytz
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from authentication.models import  Permission
from django.db.models import Count
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from sequences import get_next_value
from drf_spectacular.utils import  extend_schema, OpenApiParameter
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from authentication.decorators import has_permissions
from bbms.filters import BusBookingFilter
from django.http import HttpResponse
# from weasyprint import HTML
import os
from commons.pagination import Pagination
from bbms.serializers import BusBookingMinimalListSerializer, BusBookingSerializer, PassengerSerializer,BookingSummarySerializer,BusBookingListSerializer,BusListSerializer
from bbms.models import Bus, BusBooking, Passenger,BookingSummary,AvailableDates
from member.models import Member
from member.serializers import MemberListSerializer
from site_settings.models import GeneralSetting
from start_project import settings
from django.db.models import Count, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.core.exceptions import ObjectDoesNotExist
import segno
from decimal import Decimal, ROUND_DOWN
import tempfile
from datetime import timezone
from rest_framework import status

from django.core.mail import EmailMessage
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from weasyprint import HTML
from django.template.loader import render_to_string
from decimal import Decimal
import datetime
import pytz
from django.db import transaction
from decimal import Decimal, ROUND_DOWN
from django.db import IntegrityError
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
import bleach


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=BusBookingSerializer,
    responses=BusBookingSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([AuthPermEnum.DESIGNATION_LIST.name])
def getAllBusBooking(request):
    bus_bookings = BusBooking.objects.all()
    total_elements = bus_bookings.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    bus_bookings = pagination.paginate_data(bus_bookings)

    serializer = BusBookingListSerializer(bus_bookings, many=True)

    response = {
        'bus_bookings': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    request=BusBookingListSerializer,
    responses=BusBookingListSerializer
)
@api_view(['GET'])
def getAllBusBookingWithoutPagination(request):
    bus_booking = BusBooking.objects.all()
    serializer = BusBookingListSerializer(bus_booking, many=True)
    response = {
        'bus_booking': serializer.data,
    }
    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=BusBookingListSerializer, responses=BusBookingListSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
def getABusBooking(request, pk):
    try:
        bus_booking = BusBooking.objects.get(pk=pk)
        serializer = BusBookingListSerializer(bus_booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Bus id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
    
# @silk_profile(name='Bus Booking Creation')   
@extend_schema(request=BusBookingSerializer, responses=BusBookingSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createBusBooking(request):
    data = request.data
    filtered_data = {key: value for key, value in data.items() if value not in ('', '0')}
    number_of_travellers = filtered_data.get('number_of_travellers', 1)
    paid_amount = filtered_data.get('paid_amount', '0')
    pickup_time = filtered_data.get('pickup_time')
    meeting_point = filtered_data.get('meeting_point')
    
    
    try:
        paid_amount = Decimal(paid_amount)  # Convert to Decimal for consistency
    except (ValueError, TypeError):
        paid_amount = Decimal('0.00')  # Default to 0.00 if invalid
    booking_data = {}
    # Add 'paid_amount' to the booking data for FIT or GIT booking
    booking_data['paid_amount'] = paid_amount
    # booking_data['ticket_number'] = ticket_number
    # Initialize seat_no based on the bus type
    try:
        bus_instance = Bus.objects.get(pk=filtered_data['bus'])
    except Bus.DoesNotExist:
        return Response({'error': 'Bus not found'}, status=status.HTTP_404_NOT_FOUND)
    seat_no = filtered_data.get('seat_no', [])
    ticket_number = generate_unique_ticket_number(bus_instance.tour_type)
    try:
        group_size = int(bus_instance.group_size)  # Convert to integer
    except (ValueError, TypeError):
        group_size = 0  # Set a default value if conversion fails

    if group_size > 0:  # Ensure group_size is not zero to avoid division by zero
        per_person = Decimal(bus_instance.price) / Decimal(group_size)  # Calculate as Decimal
    else:
        per_person = Decimal('0.00')  # Default value when group size is zero

    # To display with two decimal places later
    formatted_per_person = format(per_person, ".2f")

    # If the bus is of type 'FIT', set seat_no to [0] (or another placeholder) to indicate no specific seat selection.
    if bus_instance.tour_type == 'FIT':
        seat_no = []  # Set seat_no to empty since seat selection is not needed

    ###########################
    # print("seat_no",seat_no)
    # Count seat numbers, if any
    seat_no_count = len(seat_no)
    # print("seat_no_count",seat_no_count)

    # If the bus is not of type 'FIT', we need to handle seat_no normally
    if bus_instance.tour_type != 'FIT' and not isinstance(seat_no, list):
        seat_no = [0]  # Default to [0] if seat_no is not provided or not a list

    filtered_data.pop('seat_no', None)  # Safely pop 'seat_no' if it exists
    primary_phone = filtered_data.get('primary_phone')

    # Check for existing passenger
    existing_passenger = Passenger.objects.filter(primary_phone=primary_phone).first()
    # Update or create passenger
    if existing_passenger:
        # Update existing passenger details
        passenger_serializer = PassengerSerializer(existing_passenger, data=filtered_data, partial=True)
        if passenger_serializer.is_valid():
            passenger_instance = passenger_serializer.save()
            filtered_data['passenger'] = passenger_instance.id
        else:
            return Response(passenger_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Create new passenger entry
        passenger_serializer = PassengerSerializer(data=filtered_data)
        if passenger_serializer.is_valid():
            passenger_instance = passenger_serializer.save()
            filtered_data['passenger'] = passenger_instance.id
        else:
            return Response(passenger_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # Retrieve the member associated with the authenticated user
    member_id = filtered_data.get('member')
    if not member_id:
        return Response({'error': 'Member ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        member = Member.objects.get(pk=member_id)
    except Member.DoesNotExist:
        return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

    booking_date = filtered_data.get('date')  # Ensure date is provided

        # Check if any bus has already been booked for the same date
    # if booking_date:
    #     existing_booking_on_date = BusBooking.objects.filter(date=booking_date).exists()
    #     if existing_booking_on_date:
    #         return Response({"error": "A bus has already been booked for this date. No more buses can be booked today."}, status=status.HTTP_400_BAD_REQUEST)


    # Check if a FIT bus has already been booked for the same date
    if bus_instance.tour_type == 'FIT' and booking_date:
        existing_fit_booking = BusBooking.objects.filter(bus__tour_type='FIT', date=booking_date).exclude(bus=bus_instance).exists()
        if existing_fit_booking:
            return Response({"error": "Another FIT bus has already been booked for this date."}, status=status.HTTP_400_BAD_REQUEST)

    # Initialize total_cost and total_discount_amount
    # total_cost = Decimal('0.00')
    # total_discount_amount = Decimal('0.00')
    total_seat_count = seat_no_count
    # paid_amount = Decimal('0.00')  # Example paid amount
    # due_amount = total_cost - paid_amount  # Calculate the due amount
    # print("total_cost",total_cost)
    # print("paid_amount",paid_amount)
    # print("due_amount",due_amount)

    if bus_instance.tour_type == 'GIT':  # Group Inclusive Tour
        adult_seat_count = int(filtered_data.get('adult_seat_count', 0))
        child_seat_count = int(filtered_data.get('child_seat_count', 0))
        youth_seat_count = int(filtered_data.get('youth_seat_count', 0))
        total_seat_count = adult_seat_count + child_seat_count + youth_seat_count

        adult_seat_price = Decimal(bus_instance.adult_seat_price)
        child_seat_price = Decimal(bus_instance.child_seat_price)
        youth_seat_price = Decimal(bus_instance.youth_seat_price)

        total_cost = (
            (adult_seat_price * adult_seat_count) +
            (child_seat_price * child_seat_count) +
            (youth_seat_price * youth_seat_count)
        )
        due_amount = total_cost - paid_amount
        # Calculate discount for GIT (percentage or value-based)
        adult_discount_amount = calculate_discount(adult_seat_price, adult_seat_count, member)
        child_discount_amount = calculate_discount(child_seat_price, child_seat_count, member)
        youth_discount_amount = calculate_discount(youth_seat_price, youth_seat_count, member)
        total_discount_amount = adult_discount_amount + child_discount_amount + youth_discount_amount

    elif bus_instance.tour_type == 'FIT':  # Fully Inclusive Tour
        # Extract total price sent from the frontend
        total_cost = Decimal(bus_instance.price)
        # Calculate the discount based on the total cost
        total_discount_amount = fit_calculate_discount(total_cost, member)
        due_amount = total_cost - paid_amount
    total_discount_amount = total_discount_amount.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
    reference_no = generate_reference_number()

    # Create a booking for each seat number (if it's a GIT booking)
    bookings = []
    if bus_instance.tour_type == 'GIT':
        for seat_number in seat_no:
            booking_data = filtered_data.copy()
            booking_data['seat_no'] = seat_number
            booking_data['reference_no'] = reference_no
            booking_data['ticket_number'] = ticket_number
            booking_data['date'] = booking_date  # Include booking date
            booking_data['number_of_travellers'] = number_of_travellers 
            # Add calculated values to the booking data
            booking_data['total_cost'] = total_cost.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
            booking_data['total_discount_amount'] = total_discount_amount
            booking_data['total_seat_count'] = total_seat_count
            booking_data['discount_percent'] = member.discount_percent
            booking_data['discount_value'] = member.discount_value
            booking_data['discount_type'] = member.discount_type
            booking_data['status'] = BusBooking.TicketStatus.BOOKED

            serializer = BusBookingSerializer(data=booking_data)
            if serializer.is_valid():
                booking_instance=serializer.save()
                bus_booking_id = booking_instance.id
                bookings.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:  # For FIT, create a single booking
        booking_data = filtered_data.copy()
        booking_data['seat_no'] = 0  # Set a placeholder seat number for FIT
        booking_data['reference_no'] = reference_no
        booking_data['date'] = booking_date  # Include booking date
        booking_data['ticket_number'] = ticket_number
        # Add calculated values to the booking data
        booking_data['total_cost'] = total_cost.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        booking_data['total_discount_amount'] = total_discount_amount
        booking_data['total_seat_count'] = total_seat_count
        booking_data['discount_percent'] = member.discount_percent
        booking_data['discount_value'] = member.discount_value
        booking_data['discount_type'] = member.discount_type
        booking_data['status'] = BusBooking.TicketStatus.BOOKED

        serializer = BusBookingSerializer(data=booking_data)
        if serializer.is_valid():
            booking_instance = serializer.save()
            bookings.append(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # print("total_cost",total_cost)
    # print("paid_amount",paid_amount)
    # print("due_amount",due_amount)
    # print(" number_of_travellers", number_of_travellers)

    passenger_id = filtered_data.get('passenger')
    passenger_obj = Passenger.objects.get(pk=passenger_id)
    bus_id = filtered_data.get('bus')
    bus_obj = Bus.objects.get(pk=bus_id)
    formatted_travel_date = ''
    created_at_date = ''
    if bookings:
        member_id = bookings[0].get('member', None)
        if member_id:
            member_instance = Member.objects.get(id=member_id)
            company_email = member_instance.email

        reference_no = bookings[0].get('reference_no', '')
        created_at_str = bookings[0].get('created_at', '')

        format_str = '%Y-%m-%dT%H:%M:%S.%f%z'
        try:
            created_at_datetime = datetime.datetime.strptime(created_at_str, format_str).astimezone(pytz.UTC)
            created_at_date = created_at_datetime.date()
        except ValueError:
            created_at_date = ''
        travel_date = datetime.datetime.strptime(created_at_str, format_str).astimezone(pytz.UTC).date()
        formatted_travel_date = ''
        date_str = bookings[0].get('date', '') 
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            formatted_travel_date = date.strftime('%B %d, %Y')
        except ValueError:
            formatted_travel_date = ''
        booking_time = bookings[0].get('booking_time', '')

        bus_id = bookings[0].get('bus', None)
        if bus_id:
            bus_instance = Bus.objects.get(pk=bus_id)
            bus_name = bus_instance.name
        else:
            bus_name = ''
    else:
        reference_no = ''
        travel_date = ''
        booking_time = ''
        bus_name = ''
        date_str = ''

    support_id = GeneralSetting.objects.first()
    support_number = support_id.phone
    site_title = support_id.title
    support_email = support_id.email
    print("formatted_travel_date",formatted_travel_date)
    def generate_qr_code(data, filename):
        qr = segno.make_qr(data)
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        qr.save(file_path, scale=10)
        return os.path.join(settings.MEDIA_URL, filename)

    qr_code_url = generate_qr_code(reference_no, f"qr{reference_no}.png")

    context = {
        'passenger': passenger_obj,
        'primary_phone': passenger_obj.primary_phone,
        'email': passenger_obj.email,
        'fullname': passenger_obj.first_name,
        'bookings': bookings,
        'bus_name': bus_instance.name,
        'itinerary': bus_obj.itinerary,
        'seat_quantity': bus_obj.seat_quantity,
        'starting_point': bus_obj.starting_point,
        'end_point': bus_obj.end_point,
        'owner_name': bus_obj.owner_name,
        'seat_plan': bus_obj.seat_plan,
        'bus_type': bus_obj.type,
        'group_size': bus_obj.group_size,
        'price': bus_obj.price,
        'primary_phone': bus_obj.primary_phone,
        'reference_number': reference_no,
        'travel_date': travel_date,
        'booking_time': booking_time,
        'pickup_time': pickup_time,
        'bus_name': bus_name,
        'seat_numbers': ", ".join(seat_no),
        'total_cost': total_cost,
        'support_number': support_number,
        'site_title': site_title,
        'support_email': support_email,
        'seat_no_count': seat_no_count,
        'total_cost': total_cost,
        'booking_time': booking_time,
        'travel_date': formatted_travel_date,
        'created_at': created_at_date,
        'qrcode': qr_code_url,
        'per_person' : formatted_per_person,
        'number_of_travellers': number_of_travellers,
        'email_body':bus_obj.email_body,
        'paid_amount':paid_amount,
        'due_amount':due_amount,
        'meeting_point':meeting_point,
        'seat_no':seat_no,
        'ticket_number': ticket_number
    
        
    }
    # print("number_of_travellers",number_of_travellers)

    # Add seat counts to context if the bus type is GIT
    if bus_instance.tour_type == 'GIT':
        context.update({
            'adult_seat_count': adult_seat_count,
            'youth_seat_count': youth_seat_count,
            'child_seat_count': child_seat_count,
            'adult_seat_price': adult_seat_price,
            'youth_seat_price': youth_seat_price,
            'child_seat_price': child_seat_price,
        })

    # print('this is itinerary',bus_obj.itinerary)

    # Generate PDF
    pdf_html = render_to_string('bbms/pdf_template.html', context)
    
    pdf_file = HTML(string=pdf_html).write_pdf()
    # Save PDF to BusBooking instance
    bus_booking_id = bookings[0]['id']  # Assuming you have the bus_booking instance ID
    bus_booking = get_object_or_404(BusBooking, id=bus_booking_id)
    pdf_filename = f"{bus_instance.name}_Booking_Confirmation.pdf"
    bus_booking.email_pdf.save(pdf_filename, ContentFile(pdf_file), save=True)

    invoice_html = render_to_string('bbms/bus-booking-invoice.html', context)
    invoice_file = HTML(string=invoice_html).write_pdf()
    pdf_invoice = f"{bus_instance.name}_Booking_Invoice.pdf"
    bus_booking.booking_invoice.save(pdf_invoice, ContentFile(invoice_file), save=True)


    # Generate Email
    email_html = render_to_string('bbms/email_template.html', context)
    email_cleaned_html = bleach.clean(email_html, tags=[], strip=True)
    email_text = strip_tags(email_cleaned_html)
    # email_text = strip_tags(email_html)
    
    email = EmailMessage(
        subject= bus_name + ' - Booking Confirmation',
        body=email_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        # from_email= "farhadkabir1212@gmail.com",
        to=[passenger_obj.email],
        bcc = ["farhadkabir1212@gmail.com"]
    )
    # print("email object",passenger_obj.email)
    email.attach('Booking_Confirmation.pdf', pdf_file, 'application/pdf')

    email.send()
    # print('email',email)
    # print('email_text',email_text)

    # Return response with the bookings
    return Response({"message": "Booking created successfully", "data": bookings}, status=status.HTTP_201_CREATED)

# Function to calculate discount


def fit_calculate_discount(total_cost, member):
    discount_amount = Decimal(0)
    # Check if the member has a discount type and apply the corresponding discount
    if member.discount_type == 'percentage':
        discount_amount = total_cost * (member.discount_percent / 100)
    elif member.discount_type == 'value':
        discount_amount = member.discount_value  # Fixed discount for the total price
    
    # Round the discount to 2 decimal places
    return discount_amount.quantize(Decimal('0.00'), rounding=ROUND_DOWN)

def calculate_discount(price, seat_count, member):
    discount_amount = Decimal(0)
    
    # Check if the member has a discount type and apply the corresponding discount
    if member.discount_type == 'percentage':
        discount_amount = (Decimal(price) * seat_count) * (member.discount_percent / 100)
    elif member.discount_type == 'value':
        discount_amount = member.discount_value * seat_count
    
    # Round the discount to 2 decimal places
    return discount_amount.quantize(Decimal('0.00'), rounding=ROUND_DOWN)

# Function to generate reference number
import random
import string

def generate_reference_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_ticket_number(tour_type):
    """
    Generate a unique ticket number in the format: {TOUR_TYPE}-{RANDOM_NUMBER}{RANDOM_LETTERS}.
    """
    random_number = random.randint(100, 999)  # 3-digit random number
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))  # 3 random uppercase letters
    return f"{tour_type.upper()}-{random_number}{random_letters}"

def generate_unique_ticket_number(tour_type):
    """
    Ensure the generated ticket number is unique by checking the database.
    """
    while True:
        ticket_number = generate_ticket_number(tour_type)
        if not BusBooking.objects.filter(ticket_number=ticket_number).exists():
            return ticket_number

# @extend_schema(request=BusBookingSerializer, responses=BusBookingSerializer)
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# #@has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
# def updateBusBooking(request,pk):
#     try:
#         bus_booking = BusBooking.objects.get(pk=pk)
#         data = request.data
        
#         serializer = BusBookingSerializer(bus_booking, data=data)
#         if serializer.is_valid():
#             serializer.save()
         
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     except ObjectDoesNotExist:
#         return Response({'detail': f"Bus id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(request=BusBookingSerializer, responses=BusBookingSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
#@has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
def updateBusBooking(request,pk):
    try:
        bus_booking = BusBooking.objects.get(pk=pk)
        data = request.data
        
        serializer = BusBookingSerializer(bus_booking, data=data)
        if serializer.is_valid():
            serializer.save()
         
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'detail': f"Bus id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
    
@extend_schema(request=BusBookingSerializer, responses=BusBookingSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])

def deleteBusBooking(request, pk):
    try:
        bus_booking = BusBooking.objects.get(pk=pk)
        bus_booking.delete()
      
        return Response({'detail': f'Bus Booking  id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Bus Booking id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=BusBookingSerializer,
    responses=BusBookingSerializer
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])

def getBusBookingReport(request):
    bus_booking_queryset = BusBookingFilter(request.GET, queryset=BusBooking.objects.all()).qs
    
    # Perform the aggregation before pagination
    member_tickets_count = bus_booking_queryset.values('member').annotate(total_tickets=Count('member'))
    # member_tickets_count_dict = {entry['member']: entry['total_tickets'] for entry in member_tickets_count}
    total_elements = bus_booking_queryset.count()
    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    bus_booking_instances = pagination.paginate_data(bus_booking_queryset)

    serializer = BusBookingMinimalListSerializer(bus_booking_instances, many=True)
   
    response = {
        'bus_bookings': serializer.data,
        'total_seats': len(member_tickets_count),
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)



@extend_schema(
    request=BusBookingSerializer,
    responses=BusBookingSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])

def getBusBookingReportWP(request):
    bus_booking_queryset = BusBookingFilter(request.GET, queryset=BusBooking.objects.all()).qs
    
    member_tickets_count = bus_booking_queryset.values('member').annotate(total_tickets=Count('member'))
    print("member ticket",member_tickets_count)
    total_elements = bus_booking_queryset.count()
    print("-------------------------------------")
    print("farabi ticket",total_elements)


    serializer = BusBookingMinimalListSerializer(bus_booking_queryset, many=True)
   
    response = {
        'bus_bookings': serializer.data,
        'total_seats': len(member_tickets_count),
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)

@extend_schema(
    request= BookingSummarySerializer,
    responses=BookingSummarySerializer
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAgentCommission(request):
    # Use request.query_params to get the query parameters from the GET request
    filtered_data = request.query_params

    # Retrieve and validate bus_id
    bus_id = filtered_data.get('bus')
    if not bus_id:
        return Response({'error': 'Bus ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        bus_obj = Bus.objects.get(pk=bus_id)
    except Bus.DoesNotExist:
        return Response({'error': 'Bus not found'}, status=status.HTTP_404_NOT_FOUND)
    

    # Retrieve seat counts and prices
    adult_seat_count = int(filtered_data.get('adult_seat_count', 0))
    child_seat_count = int(filtered_data.get('child_seat_count', 0))
    youth_seat_count = int(filtered_data.get('youth_seat_count', 0))
    
    total_seat_count = adult_seat_count + child_seat_count + youth_seat_count
    
    adult_seat_price = Decimal(bus_obj.adult_seat_price)
    child_seat_price = Decimal(bus_obj.child_seat_price)
    youth_seat_price = Decimal(bus_obj.youth_seat_price)

    # Calculate total cost
    total_cost = (
        adult_seat_price * adult_seat_count +
        child_seat_price * child_seat_count +
        youth_seat_price * youth_seat_count
    )

    # Retrieve and validate member_id
    member_id = filtered_data.get('member')
    if not member_id:
        return Response({'error': 'Member ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        member = Member.objects.get(pk=member_id)
    except Member.DoesNotExist:
        return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

    # Calculate discounts based on member's discount type
    adult_discount_amount = 0
    if member.discount_type == 'percentage':
        adult_discount_amount = (adult_seat_price * adult_seat_count) * (member.discount_percent / 100)
    elif member.discount_type == 'value':
        adult_discount_amount = member.discount_value * adult_seat_count

    child_discount_amount = 0
    if member.discount_type == 'percentage':
        child_discount_amount = (child_seat_price * child_seat_count) * (member.discount_percent / 100)
    elif member.discount_type == 'value':
        child_discount_amount = member.discount_value * child_seat_count

    youth_discount_amount = 0
    if member.discount_type == 'percentage':
        youth_discount_amount = (youth_seat_price * youth_seat_count) * (member.discount_percent / 100)
    elif member.discount_type == 'value':
        youth_discount_amount = member.discount_value * youth_seat_count

    total_discount_amount = adult_discount_amount + child_discount_amount + youth_discount_amount

    # Save the booking summary
    BookingSummary.objects.create(
        bus_id=bus_obj.id,
        total_cost=total_cost,
        total_discount_amount=total_discount_amount,
        total_seat_count=total_seat_count
    )

    return Response({
        'bus_id': bus_obj.id,
        'total_cost': total_cost,
        'total_discount_amount': total_discount_amount,
        'total_seat_count': total_seat_count
    }, status=status.HTTP_200_OK)


# @extend_schema(
#     request=BusBookingSerializer,
#     responses=BusBookingSerializer
# )
# @api_view(['GET'])
# def getAllBookedeBusBooking(request):
#     # Fetch all bookings with status 'booked'
#     bus_bookings = BusBooking.objects.filter(status=BusBooking.TicketStatus.BOOKED)

#     serializer = BusBookingListSerializer(bus_bookings, many=True)

#     response = {
#         'bus_bookings': serializer.data,
#         'total_elements': bus_bookings.count(),
#     }

#     return Response(response, status=status.HTTP_200_OK)


######################

@extend_schema(
    request=BusBookingListSerializer,
    responses=BusBookingListSerializer
)
@api_view(['GET'])
def getAllBookedBusBooking(request):
    # Filter bus bookings by status
    bus_booking_queryset = BusBookingFilter(
        request.GET,
        queryset=BusBooking.objects.filter(status=BusBooking.TicketStatus.BOOKED)
    ).qs

    # Initialize a dictionary to hold aggregated data
    aggregated_data = {}

    # Loop through the queryset and aggregate data
    for booking in bus_booking_queryset:
        bus_id = booking.bus.id  # Assuming there is a ForeignKey to Bus model
        bus_instance = booking.bus  # Fetch the entire bus instance
        member_id = booking.member.id  # Assuming there is a ForeignKey to Member model
        member_name = booking.member.first_name  # Assuming there is a name field in the Member model

        # Initialize if bus_id is not in the aggregated data
        if bus_id not in aggregated_data:
            # Serialize bus data
            bus_serializer = BusListSerializer(bus_instance).data  # Assuming you have a serializer for the bus

            aggregated_data[bus_id] = {
                'bus': bus_serializer,  # Add the serialized bus object
                'total_cost': 0,
                'total_discount_amount': 0,
                'total_seat_count': 0,
                'discount_percent': 0,
                'discount_value': 0,
                'booking_count': 0,  # Common field for both FIT and GIT
                'members': [],  # To hold member details
            }

        # Common aggregation logic for both GIT and FIT
        aggregated_data[bus_id]['total_cost'] += booking.total_cost or 0
        aggregated_data[bus_id]['total_discount_amount'] += booking.total_discount_amount or 0
        aggregated_data[bus_id]['total_seat_count'] += booking.total_seat_count or 0
        aggregated_data[bus_id]['discount_percent'] = max(aggregated_data[bus_id]['discount_percent'], booking.discount_percent or 0)  # Use the maximum discount
        aggregated_data[bus_id]['discount_value'] += booking.discount_value or 0

        # Increase booking count
        aggregated_data[bus_id]['booking_count'] += 1

        # Add member details if not already included
        if member_id not in [member['id'] for member in aggregated_data[bus_id]['members']]:
            aggregated_data[bus_id]['members'].append({
                'id': member_id,
                'name': member_name,  # Include other member fields as necessary
            })

    # Convert aggregated data back to a list
    result = list(aggregated_data.values())

    response = {
        'bus_bookings': result,
        'total_elements': len(result),  # Total number of unique buses
    }

    return Response(response, status=status.HTTP_200_OK)




@extend_schema(request=BusBookingSerializer, responses=BusBookingSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkBusAvailability(request):
    bus_id = request.data.get('bus_id')
    date = request.data.get('date')

    if not bus_id or not date:
        return Response({"error": "bus_id and date are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Check if the bus exists
        bus_instance = Bus.objects.get(pk=bus_id)
    except Bus.DoesNotExist:
        return Response({"error": "Bus not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check for any bookings for this bus on the specified date, excluding canceled bookings
    bookings = BusBooking.objects.filter(bus=bus_instance, date=date).exclude(status=BusBooking.TicketStatus.CANCELLED)

    # If any bookings exist that are not canceled
    if bookings.exists():
        return Response({
            "message": f"{bus_instance.name} is already booked for this date ({date})",
            "is_booked": True,
            "bookings": bookings.count()
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            "message": "Bus is available for booking",
            "is_booked": False,
            "bookings": 0
        }, status=status.HTTP_200_OK)
