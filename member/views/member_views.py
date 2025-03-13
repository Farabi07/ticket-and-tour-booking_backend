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

# @api_view(['POST'])
# def createMember(request):
#     data = request.data
#     print('data: ', data)
    
#     filtered_data = {
#         key: value for key, value in data.items() 
#         if value not in ['', '0', 0, 'undefined', 'Please Select Thana', 'Please Select City', 'Please Select Country']
#     }
    
#     filtered_data['last_login'] = timezone.now()
#     filtered_data['user_type'] = 'member'
    
#     password = filtered_data.get('password')
#     filtered_data['password'] = make_password(password) if password else make_password(hashlib.md5(os.urandom(32)).hexdigest())

#     # Validate coupon dates
#     coupon_start_date = filtered_data.get('coupon_start_date')
#     coupon_end_date = filtered_data.get('coupon_end_date')
#     if coupon_start_date and coupon_end_date and coupon_start_date > coupon_end_date:
#         return Response({"error": "Coupon start date cannot be later than coupon end date."}, status=status.HTTP_400_BAD_REQUEST)

#     print('filtered_data: ', filtered_data)  # Add this line to log the filtered data

#     serializer = MemberSerializer(data=filtered_data)

#     if serializer.is_valid():
#         member_instance = serializer.save()
        
#         # Generate `ref_no` based on the newly created member ID
#         member_instance.ref_no = generate_reference_number(member_instance.id)
#         member_instance.save()

#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     else:
#         print('serializer.errors: ', serializer.errors)  # Add this line to log serializer errors
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# def generate_reference_number(member_id):
#     current_year = datetime.now().year
#     return f"Re-{current_year}-00-{member_id}"

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

# @extend_schema(request=MemberSerializer, responses=MemberSerializer)
# @api_view(['PUT'])
# def updateMember(request, pk):
#     data = request.data
#     print('data:', data)
    
#     try:
#         member_instance = Member.objects.get(pk=pk)
#     except Member.DoesNotExist:
#         return Response({'detail': f"Member id - {pk} doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

#     filtered_data = {}
#     restricted_values = ['', ' ', '0', 'undefined', None]
    
#     for key, value in data.items():
#         if key == "file" and isinstance(value, str):
#             continue  
        
#         if value not in restricted_values:
#             filtered_data[key] = value
#         else:
#             filtered_data[key] = None
    
#     # Handle file data (rename and save)
#     file_data = data.get("file", None)
#     if file_data and not isinstance(file_data, str):  
#         current_date = datetime.now().strftime("%Y%m%d")
#         file_extension = os.path.splitext(file_data.name)[1]
#         new_filename = f"member_{current_date}{file_extension}"
#         filtered_data["file"] = file_data
#         filtered_data["file"].name = new_filename

#     print('filtered_data:', filtered_data)

#     # Remove 'image' if it is a string (assuming it's a URL that doesn't need updating)
#     if 'image' in filtered_data and isinstance(filtered_data['image'], str):
#         filtered_data.pop('image')

#     # Validate coupon dates
#     coupon_start_date = filtered_data.get('coupon_start_date')
#     coupon_end_date = filtered_data.get('coupon_end_date')
#     if coupon_start_date and coupon_end_date and coupon_start_date > coupon_end_date:
#         return Response({"error": "Coupon start date cannot be later than coupon end date."}, status=status.HTTP_400_BAD_REQUEST)

#     serializer = MemberSerializer(member_instance, data=filtered_data, partial=True)
    
#     if serializer.is_valid():
#         updated_member = serializer.save()

#         # Generate `ref_no` if missing
#         if not updated_member.ref_no:
#             updated_member.ref_no = generate_reference_number(updated_member.id)
#             updated_member.save()

#         return Response(serializer.data, status=status.HTTP_200_OK)
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# def generate_reference_number(member_id):
#     current_year = datetime.now().year
#     return f"Re-{current_year}-00-{member_id}"

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



# @extend_schema(request=MemberListSerializer, responses=MemberListSerializer)
# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
# def applyCoupon(request):
#     # Get data from query parameters
#     coupon_text = request.GET.get('coupon_text')
#     total_price = request.GET.get('total_price')
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')
#     coupon_percentage = request.GET.get('coupon_percentage')
#     coupon_value = request.GET.get('coupon_value')
#     coupon_type = request.GET.get('coupon_type')

#     # Check if all required parameters are provided
#     if not coupon_text or not total_price or not coupon_type:
#         return Response({"message": "Coupon text, total price, and coupon type are required"}, status=400)

#     # Check if the coupon exists in any Member using coupon_text
#     member = Member.objects.filter(coupon_text=coupon_text).first()
#     if not member:
#         return Response({"message": "Coupon does not exist"}, status=404)

#     # Validate date range
#     today = datetime.today().date()
#     if start_date and end_date:
#         start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
#         end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
#         if not (start_date <= today <= end_date):
#             return Response({"message": "Coupon is expired or not yet valid"}, status=400)

#     # Apply discount based on coupon type
#     discount_amount = 0
#     if coupon_type == "percentage":
#         if not coupon_percentage:
#             return Response({"message": "Coupon percentage is required for percentage type"}, status=400)
#         discount_amount = (float(total_price) * (float(coupon_percentage) / 2)) / 100
#         coupon_value = None  # Ignore coupon_value if coupon_type is percentage
#     elif coupon_type == "value":
#         if not coupon_value:
#             return Response({"message": "Coupon value is required for value type"}, status=400)
#         discount_amount = float(coupon_value)
#         coupon_percentage = None  # Ignore coupon_percentage if coupon_type is value
#     else:
#         return Response({"message": "Invalid coupon type"}, status=400)

#     final_price = float(total_price) - discount_amount

#     return Response({
#         "message": "Coupon applied successfully",
#         "original_price": total_price,
#         "discount_amount": discount_amount,
#         "final_price": final_price,
#         "applied_coupon_type": coupon_type,
#         "coupon_percentage": coupon_percentage,
#         "coupon_value": coupon_value
#     })

@extend_schema(request=MemberListSerializer, responses=MemberListSerializer)
@api_view(['GET'])
def applyCoupon(request):
    # Get data from query parameters
    coupon_text = request.GET.get('coupon_text')
    total_price = request.GET.get('total_price')

    # Check if all required parameters are provided
    if not coupon_text or not total_price:
        return Response({"message": "Coupon text and total price are required"}, status=400)

    # Check if the coupon exists in any Member using coupon_text
    member = Member.objects.filter(coupon_text=coupon_text).first()
    if not member:
        return Response({"message": "Coupon does not exist"}, status=404)

    # Validate date range
    today = datetime.today().date()
    if member.coupon_start_date and member.coupon_end_date:
        if not (member.coupon_start_date <= today <= member.coupon_end_date):
            return Response({"message": "Coupon is expired or not yet valid"}, status=400)

    # Apply discount based on coupon type
    discount_amount = 0
    if member.coupon_type == "percentage":
        if not member.coupon_percentage:
            return Response({"message": "Coupon percentage is required for percentage type"}, status=400)
        discount_amount = (float(total_price) * (float(member.coupon_percentage) / 2)) / 100
        
        coupon_value = None  # Ignore coupon_value if coupon_type is percentage
    elif member.coupon_type == "value":
        if not member.coupon_value:
            return Response({"message": "Coupon value is required for value type"}, status=400)
        discount_amount = float(member.coupon_value)
        coupon_percentage = None  # Ignore coupon_percentage if coupon_type is value
    else:
        return Response({"message": "Invalid coupon type"}, status=400)

    final_price = float(total_price) - discount_amount

    return Response({
        "message": f"Coupon applied successfully. Discount amount: {discount_amount}",
        "original_price": total_price,
        "coupon_discount": discount_amount,
        "final_price": final_price,
        "applied_coupon_type": member.coupon_type,
        "coupon_percentage": member.coupon_percentage,
        "coupon_value": member.coupon_value,
        "member_id": member.id,
        "coupon_text": member.coupon_text

    })
