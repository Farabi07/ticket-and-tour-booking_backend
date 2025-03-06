from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import  extend_schema, OpenApiParameter
from drf_spectacular.utils import extend_schema
from decimal import Decimal
from tour.models import TourBooking, TourContent
from tour.serializers import TourBookingSerializer, TourContentSerializer,TourContentListSerializer
from member.models import Member
from tour.serializers import TourBookingListSerializer,TourBookingMinimalSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from commons.pagination import Pagination
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from payments.models import Traveller,Currency
from datetime import datetime
from dateutil import parser
from tour.filters import TourBookingFilter
@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=TourBookingSerializer,
    responses=TourBookingSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([AuthPermEnum.DESIGNATION_LIST.name])
def getAllTourBooking(request):
    tour_bookings = TourBooking.objects.all()
    total_elements = tour_bookings.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    tour_bookings = pagination.paginate_data(tour_bookings)

    serializer = TourBookingListSerializer(tour_bookings, many=True)

    response = {
        'tour_bookings': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    request=TourBookingListSerializer,
    responses=TourBookingListSerializer
)
@api_view(['GET'])
def getAllTourBookingWithoutPagination(request):
    tour_booking = TourBooking.objects.all()
    serializer = TourBookingListSerializer(tour_booking, many=True)
    response = {
        'tour_booking': serializer.data,
    }
    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=TourBookingListSerializer, responses=TourBookingListSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
def getATourBooking(request, pk):
    try:
        tour_booking = TourBooking.objects.get(pk=pk)
        serializer = TourBookingListSerializer(tour_booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Tour id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
    
# @extend_schema(request=TourContentSerializer, responses=TourBookingSerializer)
# @api_view(['POST'])
# # @permission_classes([IsAuthenticated])
# def createTourBooking(request):
#     data = request.data
#     print("createTourBooking data:", data)

#     # Filter out empty and '0' values
#     filtered_data = {key: value for key, value in data.items() if value not in ('', '0')}
    
#     agent_ref_no = filtered_data.get('agentRef')
#     tour_id = filtered_data.get('tourID')
#     print("agentRef:", agent_ref_no)
#     print("tourID:", tour_id)

#     # ✅ Validate agentRef and tourID
#     if not agent_ref_no:
#         return Response({"error": "Missing agent_ref_no"}, status=400)
    
#     if not tour_id:
#         return Response({"error": "Missing tour_id"}, status=400)

#     # ✅ Find the Agent
#     agent = Member.objects.filter(ref_no=agent_ref_no).first()
#     if not agent:
#         return Response({"error": f"Agent with ref_no '{agent_ref_no}' not found"}, status=404)

#     # # ✅ Find the Tour
#     # try:
#     #     tour_id = int(tour_id)
#     # except ValueError:
#     #     return Response({"error": "Invalid tour_id, must be an integer"}, status=400)

#     tour = TourContent.objects.filter(select_bus=tour_id).first()
#     if not tour:
#         return Response({"error": f"Tour with select_tour '{tour_id}' not found"}, status=404)

#     # ✅ Extract Traveller Data from the request
#     traveller_data = {
#         "first_name": filtered_data.get('firstName'),
#         "last_name": filtered_data.get('lastName'),
#         "email": filtered_data.get('email'),
#         "phone": filtered_data.get('phone'),
#         "gender": filtered_data.get('gender'),
#         "nationality": filtered_data.get('nationality'),
#         "passport_number": filtered_data.get('passportId'),
#     }

#     # ✅ Convert date_of_birth from "DD/MM/YY" to "YYYY-MM-DD"
#         # Handle dateOfBirth conversion
#         # Handle dateOfBirth conversion        # Handle dateOfBirth conversion
#     date_of_birth = data.get('dateOfBirth')
#     print("date_of_birth:", date_of_birth)
#     if date_of_birth:
#         try:
#             traveller_data["date_of_birth"] = parser.parse(date_of_birth).strftime("%Y-%m-%d")
#         except ValueError:
#             return Response({"error": "Invalid date format for dateOfBirth."}, status=400)

#     print("Traveller Data:", traveller_data)

#     # ✅ Find or Create the Traveller
#     traveller, created = Traveller.objects.get_or_create(
#         email=traveller_data["email"],
#         defaults=traveller_data,
#     )

#     # Update Traveller if already exists
#     if not created:
#         for key, value in traveller_data.items():
#             setattr(traveller, key, value)
#         traveller.save()

#     print(f"Traveller {'created' if created else 'updated'}: {traveller}")

#     # ✅ Create Tour Booking
#     booking_data = {
#         "agent": agent.id,
#         "tour": tour.id,
#         "traveller": traveller.id,
#     }

#     serializer = TourBookingSerializer(data=booking_data)
#     if serializer.is_valid():
#         booking = serializer.save()
#         return Response({"success": True, "tour_booking_id": booking.id})

#     print("Serializer Errors:", serializer.errors)
#     return Response(serializer.errors, status=400)


@extend_schema(request=TourBookingSerializer, responses=TourBookingSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
#@has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
def updateTourBooking(request,pk):
    try:
        tour_booking = TourBooking.objects.get(pk=pk)
        data = request.data
        
        serializer = TourBookingSerializer(tour_booking, data=data)
        if serializer.is_valid():
            serializer.save()
         
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'detail': f"Tour id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
    
@extend_schema(request=TourBookingSerializer, responses=TourBookingSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])

def deleteTourBooking(request, pk):
    try:
        tour_booking = TourBooking.objects.get(pk=pk)
        tour_booking.delete()
      
        return Response({'detail': f'Tour Booking  id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Tour Booking id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(request=TourBookingListSerializer, responses=TourBookingListSerializer)
@api_view(['GET'])
def tour_booking_list_by_agent(request, agent_ref_no):
    """
    Retrieve all tour bookings for a given agent based on their reference number.
    """

    # Fetch the agent by reference number
    agent = Member.objects.filter(ref_no=agent_ref_no).first()

    if not agent:
        return Response({"error": f"Agent with ref_no '{agent_ref_no}' not found."}, status=status.HTTP_404_NOT_FOUND)

    # Fetch all bookings for the agent
    bookings = TourBooking.objects.filter(agent=agent)

    if not bookings.exists():  # Use `.exists()` to avoid unnecessary query execution
        return Response({"message": "No bookings found for this agent."}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the data
    serializer = TourBookingMinimalSerializer(bookings, many=True)
    print("booking_data",serializer.data)
    return Response(serializer.data, status=status.HTTP_200_OK,)










@extend_schema(request=TourContentSerializer, responses=TourBookingSerializer)
@api_view(['POST'])
# # @permission_classes([IsAuthenticated])
@api_view(['POST'])
def createTourBooking(request):
    try:
        checkout_data = request.data

        required_keys = ['firstName', 'lastName', 'email', 'phone', 'gender', 'nationality', 'tourID']
        if not all(key in checkout_data for key in required_keys):
            return Response({"error": "Traveller data is incomplete. Ensure all fields are provided."}, status=400)

        date_of_birth = checkout_data.get('dateOfBirth')
        if date_of_birth:
            try:
                date_of_birth = parser.parse(date_of_birth).strftime("%Y-%m-%d")
            except ValueError:
                return Response({"error": "Invalid date format for dateOfBirth."}, status=400)
        else:
            date_of_birth = None

        # Currency data validation
        current_currency = checkout_data.get('currentCurrency', {})
        currency_code = current_currency.get('currency')
        currency_name = current_currency.get('name')
        currency_symbol = current_currency.get('symbol')

        if not currency_code or not currency_name or not currency_symbol:
            return Response({"error": "Currency data is incomplete."}, status=400)

        # Create or get currency
        currency, _ = Currency.objects.get_or_create(
            currency_code=currency_code,
            name=currency_name,
            symbol=currency_symbol
        )

        # Create or get traveller
        traveller, _ = Traveller.objects.get_or_create(
            first_name=checkout_data['firstName'],
            last_name=checkout_data['lastName'],
            email=checkout_data['email'],
            phone=checkout_data['phone'],
            gender=checkout_data['gender'],
            nationality=checkout_data['nationality'],
            passport_number=checkout_data.get('passportId'),
            date_of_birth=date_of_birth
        )

        # Get tour by ID
        tour_id = checkout_data.get('tourID')
        try:
            tour = TourContent.objects.get(id=tour_id)
        except TourContent.DoesNotExist:
            return Response({"error": "No matching tour found."}, status=404)

        # Price calculation
        participants = checkout_data.get('participants', {})
        adult_count = participants.get('adult', 0)
        youth_count = participants.get('youth', 0)
        child_count = participants.get('child', 0)

        adult_price = Decimal(str(checkout_data.get('adultPrice', 0)))
        youth_price = Decimal(str(checkout_data.get('youthPrice', 0)))
        child_price = Decimal(str(checkout_data.get('childPrice', 0)))

        total_adult_price = adult_count * adult_price
        total_youth_price = youth_count * youth_price
        total_child_price = child_count * child_price
        total_price = total_adult_price + total_youth_price + total_child_price

        # Update tour with prices
        tour.adult_price = adult_price
        tour.youth_price = youth_price
        tour.child_price = child_price
        tour.save()

        # Agent Discount Calculation
        agent_ref_no = checkout_data.get('agentRef')
        agent = None
        total_discount_amount = Decimal(0)
        if agent_ref_no:
            agent = Member.objects.filter(ref_no=agent_ref_no).first()
            if not agent:
                return Response({"error": f"Agent with ref_no '{agent_ref_no}' not found"}, status=404)
            # Calculate discount based on the agent
            total_discount_amount = calculate_discount(total_price, agent_ref_no)

            # Update the total discount amount for the agent
            agent.total_discount_amount = total_discount_amount
            agent.save()

        # Booking data preparation
        selected_date = datetime.strptime(checkout_data.get('selectedDate'), "%Y-%m-%d").date()
        selected_time = datetime.strptime(checkout_data.get('selectedTime'), "%I:%M %p").time()

        booking_data = {
            "agent": agent.id if agent else None,
            "tour": tour.id,
            "traveller": traveller.id,
            "adult_count": adult_count,
            "youth_count": youth_count,
            "child_count": child_count,
            "adult_price": total_adult_price,
            "youth_price": total_youth_price,
            "child_price": total_child_price,
            "total_price": total_price,
            "participants": checkout_data.get('participants', {}),
            "payWithCash": checkout_data.get('payWithCash'),
            "payWithStripe": checkout_data.get('payWithStripe'),
            "selected_date": selected_date,
            "selected_time": selected_time,
            "duration": tour.duration,
            "is_agent": checkout_data.get('is_agent'),
            "status": "pending",  # Assuming pending until payment is made
        }

        booking_serializer = TourBookingSerializer(data=booking_data)
        if booking_serializer.is_valid():
            booking = booking_serializer.save()
        else:
            return Response(booking_serializer.errors, status=400)

        # Return booking response
        return Response({
            "booking_id": booking.id,
            "total_discount_amount": total_discount_amount,
            "total_price_after_discount": total_price - total_discount_amount,
            "success": "Booking created successfully"
        }, status=201)

    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

def calculate_discount(total_price, ref_no):
    """Calculate discount based on ref_no from the Member model."""
    discount_amount = Decimal(0)
    
    # Find the member by ref_no (which is the agent's reference number)
    member = Member.objects.filter(ref_no=ref_no).first()
    
    if member:
        # Retrieve the discount information from the member
        discount_type = member.discount_type
        discount_value = member.discount_value
        discount_percent = member.discount_percent
        
        if discount_type == "percentage":
            # Calculate discount based on percentage
            discount_amount = (total_price * discount_percent) / 100
        elif discount_type == "value":
            # Use fixed discount value
            discount_amount = discount_value
    
    return discount_amount




@api_view(['GET'])
def getAllBookedTourBooking(request):
    # Apply filters using TourBookingFilter
    tour_booking_queryset = TourBookingFilter(
        request.GET,
        queryset=TourBooking.objects.all()
    ).qs

    # Dictionary to store aggregated results
    aggregated_data = {}

    for booking in tour_booking_queryset:
        tour_instance = booking.tour
        if not tour_instance:
            continue

        tour_id = tour_instance.id
        tour_name = tour_instance.name

        member_id = booking.agent.id if booking.agent else None
        member_name = booking.agent.first_name if booking.agent else "No Agent"

        # **Group by (Tour ID & Discount Percent)**
        discount_percent = booking.discount_percent or 0
        group_key = (tour_id, discount_percent)  # Now considering discount percent

        if group_key not in aggregated_data:
            aggregated_data[group_key] = {
                'tour_name': tour_name,
                'total_price': 0,
                'total_discount_amount': 0,
                'discount_percent': discount_percent,
                'discount_value': 0,
                'booking_count': 0,
                'members': [],
            }

        # Update Aggregated Data
        aggregated_data[group_key]['total_price'] += booking.total_price or 0
        aggregated_data[group_key]['total_discount_amount'] += booking.total_discount_amount or 0
        aggregated_data[group_key]['discount_value'] += booking.discount_value or 0
        aggregated_data[group_key]['booking_count'] += 1

        # Add unique members
        if member_id not in [member['id'] for member in aggregated_data[group_key]['members']]:
            aggregated_data[group_key]['members'].append({
                'id': member_id,
                'name': member_name,
            })

    # Convert dictionary to list
    result = list(aggregated_data.values())

    response = {
        'tour_bookings': result,
        'total_elements': len(result),
    }

    return Response(response, status=status.HTTP_200_OK)




