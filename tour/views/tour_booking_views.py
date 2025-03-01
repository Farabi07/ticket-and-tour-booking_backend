from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import  extend_schema, OpenApiParameter
from drf_spectacular.utils import extend_schema
from decimal import Decimal
from tour.models import TourBooking, TourContent
from tour.serializers import TourBookingSerializer, TourContentSerializer
from member.models import Member
from tour.serializers import TourBookingListSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from commons.pagination import Pagination
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from payments.models import Traveller
from datetime import datetime
from dateutil import parser
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
    
@extend_schema(request=TourContentSerializer, responses=TourBookingSerializer)
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def createTourBooking(request):
    data = request.data
    print("createTourBooking data:", data)

    # Filter out empty and '0' values
    filtered_data = {key: value for key, value in data.items() if value not in ('', '0')}
    
    agent_ref_no = filtered_data.get('agentRef')
    tour_id = filtered_data.get('tourID')
    print("agentRef:", agent_ref_no)
    print("tourID:", tour_id)

    # ✅ Validate agentRef and tourID
    if not agent_ref_no:
        return Response({"error": "Missing agent_ref_no"}, status=400)
    
    if not tour_id:
        return Response({"error": "Missing tour_id"}, status=400)

    # ✅ Find the Agent
    agent = Member.objects.filter(ref_no=agent_ref_no).first()
    if not agent:
        return Response({"error": f"Agent with ref_no '{agent_ref_no}' not found"}, status=404)

    # # ✅ Find the Tour
    # try:
    #     tour_id = int(tour_id)
    # except ValueError:
    #     return Response({"error": "Invalid tour_id, must be an integer"}, status=400)

    tour = TourContent.objects.filter(select_bus=tour_id).first()
    if not tour:
        return Response({"error": f"Tour with select_tour '{tour_id}' not found"}, status=404)

    # ✅ Extract Traveller Data from the request
    traveller_data = {
        "first_name": filtered_data.get('firstName'),
        "last_name": filtered_data.get('lastName'),
        "email": filtered_data.get('email'),
        "phone": filtered_data.get('phone'),
        "gender": filtered_data.get('gender'),
        "nationality": filtered_data.get('nationality'),
        "passport_number": filtered_data.get('passportId'),
    }

    # ✅ Convert date_of_birth from "DD/MM/YY" to "YYYY-MM-DD"
        # Handle dateOfBirth conversion
        # Handle dateOfBirth conversion        # Handle dateOfBirth conversion
    date_of_birth = data.get('dateOfBirth')
    print("date_of_birth:", date_of_birth)
    if date_of_birth:
        try:
            traveller_data["date_of_birth"] = parser.parse(date_of_birth).strftime("%Y-%m-%d")
        except ValueError:
            return Response({"error": "Invalid date format for dateOfBirth."}, status=400)

    print("Traveller Data:", traveller_data)

    # ✅ Find or Create the Traveller
    traveller, created = Traveller.objects.get_or_create(
        email=traveller_data["email"],
        defaults=traveller_data,
    )

    # Update Traveller if already exists
    if not created:
        for key, value in traveller_data.items():
            setattr(traveller, key, value)
        traveller.save()

    print(f"Traveller {'created' if created else 'updated'}: {traveller}")

    # ✅ Create Tour Booking
    booking_data = {
        "agent": agent.id,
        "tour": tour.id,
        "traveller": traveller.id,
    }

    serializer = TourBookingSerializer(data=booking_data)
    if serializer.is_valid():
        booking = serializer.save()
        return Response({"success": True, "tour_booking_id": booking.id})

    print("Serializer Errors:", serializer.errors)
    return Response(serializer.errors, status=400)


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
    serializer = TourBookingListSerializer(bookings, many=True)
    print("booking_data",serializer.data)
    return Response(serializer.data, status=status.HTTP_200_OK,)
