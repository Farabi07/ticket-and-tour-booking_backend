
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from authentication.models import  Permission
from django.db.models import Q
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from commons.pagination import Pagination
from bbms.serializers import PassengerSerializer
from bbms.models import Bus, Passenger
from start_project import settings


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=PassengerSerializer,
    responses=PassengerSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([AuthPermEnum.DESIGNATION_LIST.name])
def getAllPassenger(request):
    passengers = Passenger.objects.all()
    total_elements = passengers.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    passengers = pagination.paginate_data(passengers)

    serializer = PassengerSerializer(passengers, many=True)

    response = {
        'passengers': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    request=PassengerSerializer,
    responses=PassengerSerializer
)
@api_view(['GET'])
def getAllPassengerWithoutPagination(request):
    passenger = Passenger.objects.all()
    serializer = PassengerSerializer(passenger, many=True)
    response = {
        'passenger': serializer.data,
    }
    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=PassengerSerializer, responses=PassengerSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
def getAPassenger(request, pk):
    try:
        passenger = Passenger.objects.get(pk=pk)
        serializer = PassengerSerializer(passenger)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Bus id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(request=PassengerSerializer, responses=PassengerSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
def getAPassengerByPrimaryNumber(request):
    try:
        primary_phone = request.query_params.get('primary_phone', None)
        passenger = Passenger.objects.get(primary_phone=primary_phone)
        serializer = PassengerSerializer(passenger)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Passenger number- {primary_phone} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(request=PassengerSerializer, responses=PassengerSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_CREATE.name])
def createPassenger(request):
    data = request.data
    filtered_data = {}
    
    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value
        
   
    serializer = PassengerSerializer(data=filtered_data)
    if serializer.is_valid():
        serializer.save()
      
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PassengerSerializer, responses=PassengerSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_UPDATE.name])
def updatePassenger(request,pk):
    try:
        bus_booking = Passenger.objects.get(pk=pk)
        data = request.data
     
      
        
        serializer = PassengerSerializer(bus_booking, data=data)
        if serializer.is_valid():
            serializer.save()
         
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'detail': f"Bus id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(request=PassengerSerializer, responses=PassengerSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])

def deletePassenger(request, pk):
    try:
        passenger = Passenger.objects.get(pk=pk)
        passenger.delete()
      
        return Response({'detail': f'Bus  id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Bus  id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(request=PassengerSerializer, responses=PassengerSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([SiteSettingPermEnum.GENERAL_SETTING_DETAILS.name])
def searchPassenger(request):
    keyword = request.query_params.get('key', None)
    print('keyword: ', keyword)
    if keyword:
        passenger = Passenger.objects.filter(Q(first_name__icontains=keyword)|Q(last_name__icontains=keyword)|
                           Q(primary_phone__icontains=keyword)|Q(email__exact=keyword))
    else:
        return Response({'detail':f"Please enter Passengers to search."})
    serializer = PassengerSerializer(passenger, many=True)
    response = {
        'passengers': serializer.data,
    }
    if len(passenger) > 0:
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"There are no passengers matching your search"}, status=status.HTTP_400_BAD_REQUEST)
    


@extend_schema(request=PassengerSerializer, responses=PassengerSerializer)
# @api_view(['POST'])
# def send_email_member_to_passenger(request):
    # sender_email = request.data.get('member_email')
    # recipient_email = request.data.get('passemger_email')
    # subject = request.data.get('subject')
    # message = request.data.get('message')

    # try:
    #     # Sending the email
    #     s = send_mail(subject, message, sender_email, [recipient_email])
    #     print('message: ', s)
    #     if s == 1:
    #         return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
    #     else:
    #         return Response({'message': 'Email not sent. Check your email configuration.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # except Exception as e:
    #     print('Error:', str(e))
    #     return Response({'message': f'Error sending email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
# @extend_schema(request=OrderSerializer, responses=OrderSerializer)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def send_email_member_to_passenger(request):

    data = request.data
    passenger_id = data.get('passenger')
    passenger_obj = Passenger.objects.get(pk=passenger_id)
    passenger_id = int(passenger_id)
    fullname = passenger_obj.first_name 
    print('fullname: ', fullname)
    primary_phone = passenger_obj.primary_phone
    print('primary_phone: ', primary_phone)
    email = passenger_obj.email
    print('email: ', email)

    
    
    context = {'passenger': passenger_obj,  'primary_phone': primary_phone,'email': email, 'fullname': fullname}
    subject = 'invoice'
    from_email = settings.EMAIL_HOST_USER
    to_email = email
    html_message = render_to_string('bbms/passenger_email.html', context)
    plain_message = strip_tags(html_message)
    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False
            )
        print("after send mail")
    except Exception as e:
        print('mail exception: ', e)
        return Response({'detail': f"Something went wrong. May be your email address is invalid or the mail server is temporarily down."})

    return Response({'detail': f"Mail sent for invoice {passenger_obj.first_name}"}, status=status.HTTP_200_OK)


from django.shortcuts import render

def my_view(request):
    return render(request, 'bbms/passenger_confirm.html')