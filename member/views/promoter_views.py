import hashlib
import os
import random
import string
from ast import keyword

import requests
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

# from account.models import Group, LedgerAccount
from authentication.models import User

from authentication.serializers import AdminUserMinimalListSerializer
from authentication.decorators import has_permissions
# from donation.models import Gift, Level, PromoterAccountLog

from member.models import *
from member.serializers import *

from utils.login_logout import get_all_logged_in_users

from commons.pagination import Pagination

from commons.enums import PermissionEnum

import datetime


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request= PromoterSerializer,
    responses=PromoterListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllPromoter(request):
    promoters = Promoter.objects.all()
    total_elements = promoters.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    promoters = pagination.paginate_data(promoters)

    serializer = PromoterListSerializer(promoters, many=True)

    response = {
        'promoters': serializer.data,
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
    request=PromoterSerializer,
    responses=PromoterListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllPromoterWithoutPagination(request):
    promoters = Promoter.objects.all()

    serializer = PromoterListSerializer(promoters, many=True)

    response = {
        'promoters': serializer.data,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=PromoterSerializer, responses=PromoterSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getAPromoter(request, pk):
    try:
        promoter = Promoter.objects.get(pk=pk)
        # promoter_account_logs = PromoterAccountLog.objects.filter(
        #     user=promoter.head_user)
        # debit_amount_sum = 0
        # credit_amount_sum = 0
        # for promoter_account in promoter_account_logs:
        #     debit_amount_sum = debit_amount_sum + promoter_account.debit_amount
        #     credit_amount_sum = credit_amount_sum + promoter_account.credit_amount

        # total_amount_of_user = credit_amount_sum - debit_amount_sum

        # promoter.total_amount = total_amount_of_user
        # promoter.save()
        serializer = PromoterListSerializer(promoter)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Promoter id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PromoterSerializer, responses=PromoterSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchPromoter(request):
    keyword = request.query_params.get('keyword')
    promoters = Promoter.objects.filter(
        Q(username__icontains=keyword) | Q(email__icontains=keyword))

    print('searched_menbers: ', promoters)

    total_elements = promoters.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    promoters = pagination.paginate_data(promoters)

    serializer = PromoterListSerializer(promoters, many=True)

    response = {
        'promoters': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    if len(promoters) > 0:
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"There are no promoters matching your search"}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(request=PromoterSerializer, responses=PromoterSerializer)
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])

def createPromoter(request):
    data = request.data
    print('data: ', data)
    print('content_type: ', request.content_type)

    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0' and value != 'undefined' \
                and value != "Please Select Thana" and value != 'Please Select City' and value != 'Please Select Country':
            filtered_data[key] = value
    filtered_data['last_login'] = timezone.now()
    filtered_data['user_type'] = 'promoter'
    
    password = filtered_data.get('password')
    random_password = hashlib.md5(os.urandom(32)).hexdigest()
    filtered_data['password'] = make_password(password)

    print('filtered_data: ', filtered_data)

    serializer = PromoterSerializer(data=filtered_data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
@extend_schema(request=PromoterSerializer, responses=PromoterSerializer)
@api_view(['PUT'])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
def updatePromoter(request, pk):
    data = request.data
    print('data:', data)
    
    try:
        promoter_instance = Promoter.objects.get(pk=pk)
    except Promoter.DoesNotExist:
        return Response({'detail': f"Promoter id - {pk} doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

   
    filtered_data = {}
    restricted_values = ['', ' ', '0', 'undefined', None]
    
    for key, value in data.items():
        if key == "file" and isinstance(value, str):
            continue  
        
        if value not in restricted_values:
            filtered_data[key] = value
        else:
            filtered_data[key] = None
    
   
    file_data = data.get("file", None)
    if file_data and not isinstance(file_data, str):  
        
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        file_extension = os.path.splitext(file_data.name)[1]
        new_filename = f"promoter_{current_date}{file_extension}"
        
       
        filtered_data["file"] = file_data
        filtered_data["file"].name = new_filename

    print('filtered_data:', filtered_data)

   
    if 'image' in filtered_data and isinstance(filtered_data['image'], str):
        filtered_data.pop('image')  

    serializer = PromoterSerializer(promoter_instance, data=filtered_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@extend_schema(request=PromoterSerializer, responses=PromoterSerializer)
@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DELETE.name])
def deletePromoter(request, pk):
    try:
        promoter = Promoter.objects.get(pk=pk)
        promoter.delete()
        return Response({'detail': f'Promoter id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Promoter id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PromoterSerializer, responses=PromoterSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.USER_DELETE.name])
def checkReferIDWhenCreate(request):
    refer_id = request.query_params.get('refer_id', None)
    print("refer_id: ", refer_id)
    response_data = {}

    if refer_id is not None:
        promoter_objs = Promoter.objects.filter(refer_id=refer_id)
    else:
        return Response({'detail': "Refer Id can't be null."})

    if len(promoter_objs) > 0:
        response_data['refer_id_exists'] = False
    else:
        response_data['refer_id_exists'] = True

    return Response(response_data)
