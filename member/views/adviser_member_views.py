from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from member.models import AdviserMember
from member.serializers import AdviserMemberSerializer, AdviserMemberListSerializer

from commons.pagination import Pagination
from commons.enums import PermissionEnum

import datetime


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=AdviserMemberListSerializer,
    responses=AdviserMemberListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllAdviserMember(request):
    adviser_members = AdviserMember.objects.all()
    total_elements = adviser_members.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    adviser_members = pagination.paginate_data(adviser_members)

    serializer = AdviserMemberListSerializer(adviser_members, many=True)

    response = {
        'adviser_members': serializer.data,
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
    request=AdviserMemberListSerializer,
    responses=AdviserMemberListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllAdviserMemberWithoutPagination(request):
    adviser_members = AdviserMember.objects.all()

    serializer = AdviserMemberListSerializer(adviser_members, many=True)

    response = {
        'adviser_members': serializer.data,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=AdviserMemberSerializer, responses=AdviserMemberSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getAAdviserMember(request, pk):
    try:
        adviser_member = AdviserMember.objects.get(pk=pk)
        serializer = AdviserMemberSerializer(adviser_member)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"AdviserMember id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=AdviserMemberSerializer, responses=AdviserMemberSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createAdviserMember(request):
    data = request.data
    print('data: ', data)
    print('content_type: ', request.content_type)

    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    serializer = AdviserMemberSerializer(data=filtered_data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors)


@extend_schema(request=AdviserMemberSerializer, responses=AdviserMemberSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
def updateAdviserMember(request, pk):
    data = request.data
    filtered_data = {}

    try:
        ticket_obj = AdviserMember.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response({'detail': f"AdviserMember id - {pk} doesn't exists"})

    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    image = data.get('image', None)

    if image is not None and type(image) == str:
        popped_image = filtered_data.pop('image')

    serializer = AdviserMemberSerializer(ticket_obj, data=filtered_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors)


@extend_schema(request=AdviserMemberSerializer, responses=AdviserMemberSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DELETE.name])
def deleteAdviserMember(request, pk):
    try:
        adviser_member = AdviserMember.objects.get(pk=pk)
        adviser_member.delete()
        return Response({'detail': f'AdviserMember id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"AdviserMember id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)
