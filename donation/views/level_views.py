from typing import Collection
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from authentication.models import User
from authentication.serializers import UserSerializer
from donation.models import Level
from commons.pagination import Pagination
from donation.serializers import LevelListSerializer, LevelSerializer, UserDetailsSerializer, UserMinimalSerializer
from member.models import Member
from member.serializers import MemberListSerializer, MemberSerializer
from django.db.models import Sum


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=LevelSerializer,
    responses=LevelSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_LIST.name])
def getAllLevel(request):
    levels = Level.objects.all()
    total_elements = levels.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    levels = pagination.paginate_data(levels)

    serializer = LevelListSerializer(levels, many=True)

    response = {
        'levels': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=LevelSerializer, responses=LevelSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllLevelWithoutPagination(request):
    levels = Level.objects.all()
    print('levels: ', levels)

    serializer = LevelListSerializer(levels, many=True)

    response = {
        'levels': serializer.data,

    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=LevelSerializer, responses=LevelSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DETAILS.name])
def getALevel(request, pk):
    try:
        level = Level.objects.get(pk=pk)
        serializer = LevelListSerializer(level)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"level id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=LevelSerializer, responses=LevelSerializer)
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_CREATE.name])
def createLevel(request):
    data = request.data
    print('data: ', data)
    filtered_data = {}
    restricted_values = ('', ' ', 0, '0', 'undefined')

    for key, value in data.items():
        if value not in restricted_values:
            filtered_data[key] = value
    serializer = LevelSerializer(data=filtered_data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(request=LevelSerializer, responses=LevelSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_UPDATE.name])
def updateLevel(request, pk):
    data = request.data
    print('data: ', data)
    filtered_data = {}
    restricted_values = ('', ' ', 0, '0', 'undefined')

    for key, value in data.items():
        if value not in restricted_values:
            filtered_data[key] = value
    try:
        level = Level.objects.get(pk=pk)

        serializer = LevelListSerializer(level, data=filtered_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'detail': f"level id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=LevelListSerializer, responses=LevelListSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DELETE.name])
def deleteLevel(request, pk):
    try:
        level = Level.objects.get(pk=pk)
        level.delete()
        return Response({'detail': f'level id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"level id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=LevelSerializer, responses=LevelSerializer)
@api_view(['GET'])
def getAllUserInformationByLevel(request, level_name):
    user_by_level_name = []
    level_obj = Level.objects.filter(id=level_name)
    level_quantity = level_obj[0].quantity
    all_level = Level.objects.all()
    min_level = Level.objects.filter(quantity__lt=level_quantity)
    if len(min_level) == 0:
        previous_level_quantity = 0
    else:
        previous_level_quantity = int(min_level[len(min_level)-1].quantity)
    user_obj = User.objects.all()
    for user_details in user_obj:
        user_id = user_details.id
        user_head = User.objects.filter(head_user=user_id)
        user_head_len = len(user_head)
        for level_details in all_level:
            quantity = level_details.quantity

            if int(quantity) == int(level_quantity):
                if level_name == 1 and int(user_head_len) <= int(quantity) and int(user_head_len) > 0:
                    user_by_level_name.append(user_details)
                    break
                elif int(user_head_len) <= int(quantity) and int(user_head_len) > int(previous_level_quantity):
                    user_by_level_name.append(user_details)
                    break
    serializer = MemberListSerializer(user_by_level_name, many=True)
    response = {
        "user_by_level_name": serializer.data
    }
    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
@api_view(['GET'])
def getAllLevelByUser(request, user_id, level_name):
    final_level = None
    level_one = None
    level_two = None
    level_three = None
    level_four = None
    level_five = None
    level_one_users = User.objects.filter(head_user__id=user_id)
    if level_name == "Level 1":
        level_one = User.objects.filter(head_user=user_id)
        final_level = level_one
    if level_name == "Level 2":
        level_one = User.objects.filter(head_user=user_id)
        level_two = User.objects.filter(head_user__in=level_one)
        final_level = level_two
    if level_name == "Level 3":
        level_one = User.objects.filter(head_user=user_id)
        level_two = User.objects.filter(head_user__in=level_one)
        level_three = User.objects.filter(head_user__in=level_two)
        final_level = level_three
    if level_name == "Level 4":
        level_one = User.objects.filter(head_user=user_id)
        level_two = User.objects.filter(head_user__in=level_one)
        level_three = User.objects.filter(head_user__in=level_two)
        level_four = User.objects.filter(head_user__in=level_three)
        final_level = level_four
    if level_name == "Level 5":
        level_one = User.objects.filter(head_user=user_id)
        level_two = User.objects.filter(head_user__in=level_one)
        level_three = User.objects.filter(head_user__in=level_two)
        level_four = User.objects.filter(head_user__in=level_three)
        level_five = User.objects.filter(head_user__in=level_four)
        final_level = level_five
    serializer = UserDetailsSerializer(final_level, many=True)
    response = {
        "final_level": serializer.data
    }
    return Response(response, status=status.HTTP_200_OK)
# def getAllLevelByUser(request, user_id, level_name):
#     final_level = None
#     level_one = None
#     level_two = None
#     level_three = None
#     level_four = None
#     level_five = None
#     level_one_users = User.objects.filter(head_user__id=user_id)
#     if level_name == "Level 1":
#         level_one = User.objects.filter(head_user__in=level_one_users)
#         final_level = level_one
#     print('level: ', level_name)
#     if level_name == "Level 2":
#         level_two = User.objects.filter(head_user__in=level_one)
#         final_level = level_two
#         print('level: ', level_name)
#     if level_name == "Level 3":
#         level_three = User.objects.filter(head_user__in=level_two)
#         final_level = level_three
#     if level_name == "Level 4":
#         level_four = User.objects.filter(head_user__in=level_three)
#         final_level = level_four
#     if level_name == "Level 5":
#         level_five = User.objects.filter(head_user__in=level_four)
#         final_level = level_five
#     serializer = UserDetailsSerializer(final_level, many=True)
#     response = {
#         "final_level": serializer.data
#     }
#     return Response(response, status=status.HTTP_200_OK)
# def getAllLevelByUser(request, user_id, level_name):
#     final_level = None
#     level_one = None
#     level_two = None
#     level_three = None
#     level_four = None
#     level_five = None
#     level_one_users = Member.objects.filter(head_user__id=user_id)
#     if level_name == "Level 1":
#         level_one = Member.objects.filter(head_user__in=level_one_users)
#         final_level = level_one
#         print('final_level: ', final_level)
#     elif level_name == "Level 2":
#         if level_one:
#             level_two = Member.objects.filter(head_user__in=level_one)
#             final_level = level_two
#             print('final_level: ', final_level)
#         else:
#             final_level = Member.objects.none()
#     elif level_name == "Level 3":
#         if level_two:
#             level_three = Member.objects.filter(head_user__in=level_two)
#             final_level = level_three
#             print('final_level: ', final_level)
#         else:
#             final_level = Member.objects.none()
#     elif level_name == "Level 4":
#         if level_three:
#             level_four = Member.objects.filter(head_user__in=level_three)
#             final_level = level_four
#         else:
#             final_level = Member.objects.none()
#     elif level_name == "Level 5":
#         if level_four:
#             level_five = Member.objects.filter(head_user__in=level_four)
#             final_level = level_five
#         else:
#             final_level = Member.objects.none()
#     serializer = UserDetailsSerializer(final_level, many=True)
#     response = {
#         "final_level": serializer.data
#     }
#     return Response(response, status=status.HTTP_200_OK)
