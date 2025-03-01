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
# from donation.models import Gift, Level, MemberAccountLog

from member.models import Member
from member.serializers import MemberSerializer, MemberListSerializer

from utils.login_logout import get_all_logged_in_users

from commons.pagination import Pagination

from commons.enums import PermissionEnum

from datetime import datetime


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=MemberSerializer,
    responses=MemberListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllMember(request):
    members = Member.objects.all()
    total_elements = members.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    members = pagination.paginate_data(members)

    serializer = MemberListSerializer(members, many=True)

    response = {
        'members': serializer.data,
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
    request=MemberSerializer,
    responses=MemberListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllMemberWithoutPagination(request):
    members = Member.objects.all()

    serializer = MemberListSerializer(members, many=True)

    response = {
        'members': serializer.data,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=MemberSerializer, responses=MemberSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getAMember(request, pk):
    try:
        member = Member.objects.get(pk=pk)
        # member_account_logs = MemberAccountLog.objects.filter(
        #     user=member.head_user)
        # debit_amount_sum = 0
        # credit_amount_sum = 0
        # for member_account in member_account_logs:
        #     debit_amount_sum = debit_amount_sum + member_account.debit_amount
        #     credit_amount_sum = credit_amount_sum + member_account.credit_amount

        # total_amount_of_user = credit_amount_sum - debit_amount_sum

        # member.total_amount = total_amount_of_user
        # member.save()
        serializer = MemberListSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Member id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=MemberSerializer, responses=MemberSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchMember(request):
    keyword = request.query_params.get('keyword')
    members = Member.objects.filter(
        Q(username__icontains=keyword) | Q(email__icontains=keyword))

    print('searched_menbers: ', members)

    total_elements = members.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    members = pagination.paginate_data(members)

    serializer = MemberListSerializer(members, many=True)

    response = {
        'members': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    if len(members) > 0:
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"There are no members matching your search"}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(request=MemberSerializer, responses=MemberSerializer)
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])

def createMember(request):
    data = request.data
    print('data: ', data)
    
    filtered_data = {
        key: value for key, value in data.items() 
        if value not in ['', '0', 0, 'undefined', 'Please Select Thana', 'Please Select City', 'Please Select Country']
    }
    
    filtered_data['last_login'] = timezone.now()
    filtered_data['user_type'] = 'member'
    
    password = filtered_data.get('password')
    filtered_data['password'] = make_password(password) if password else make_password(hashlib.md5(os.urandom(32)).hexdigest())

    serializer = MemberSerializer(data=filtered_data)

    if serializer.is_valid():
        member_instance = serializer.save()
        
        # Generate `ref_no` based on the newly created member ID
        member_instance.ref_no = generate_reference_number(member_instance.id)
        member_instance.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def generate_reference_number(member_id):
    current_year = datetime.now().year
    return f"Re-{current_year}-00-{member_id}"
    
@extend_schema(request=MemberSerializer, responses=MemberSerializer)
@api_view(['PUT'])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
def updateMember(request, pk):
    data = request.data
    print('data:', data)
    
    try:
        member_instance = Member.objects.get(pk=pk)
    except Member.DoesNotExist:
        return Response({'detail': f"Member id - {pk} doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    filtered_data = {}
    restricted_values = ['', ' ', '0', 'undefined', None]
    
    for key, value in data.items():
        if key == "file" and isinstance(value, str):
            continue  
        
        if value not in restricted_values:
            filtered_data[key] = value
        else:
            filtered_data[key] = None
    
    # Handle file data (rename and save)
    file_data = data.get("file", None)
    if file_data and not isinstance(file_data, str):  
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        file_extension = os.path.splitext(file_data.name)[1]
        new_filename = f"member_{current_date}{file_extension}"
        filtered_data["file"] = file_data
        filtered_data["file"].name = new_filename

    print('filtered_data:', filtered_data)

    # Remove 'image' if it is a string (assuming it's a URL that doesn't need updating)
    if 'image' in filtered_data and isinstance(filtered_data['image'], str):
        filtered_data.pop('image')

    serializer = MemberSerializer(member_instance, data=filtered_data, partial=True)
    
    if serializer.is_valid():
        updated_member = serializer.save()

        # Generate `ref_no` if missing
        if not updated_member.ref_no:
            updated_member.ref_no = generate_reference_number(updated_member.id)
            updated_member.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(request=MemberSerializer, responses=MemberSerializer)
@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DELETE.name])
def deleteMember(request, pk):
    try:
        member = Member.objects.get(pk=pk)
        member.delete()
        return Response({'detail': f'Member id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Member id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=MemberSerializer, responses=MemberSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.USER_DELETE.name])
def checkReferIDWhenCreate(request):
    refer_id = request.query_params.get('refer_id', None)
    print("refer_id: ", refer_id)
    response_data = {}

    if refer_id is not None:
        member_objs = Member.objects.filter(refer_id=refer_id)
    else:
        return Response({'detail': "Refer Id can't be null."})

    if len(member_objs) > 0:
        response_data['refer_id_exists'] = False
    else:
        response_data['refer_id_exists'] = True

    return Response(response_data)
