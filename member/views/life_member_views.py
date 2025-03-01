from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from commons.pagination import Pagination
from member.filters import LifeMemberFilter
from member.models import LifeMember
from member.serializers import LifeMemberListSerializer, LifeMemberSerializer


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=LifeMemberListSerializer,
    responses=LifeMemberListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllLifeMember(request):
    life_members = LifeMember.objects.all()
    total_elements = life_members.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    life_members = pagination.paginate_data(life_members)

    serializer = LifeMemberListSerializer(life_members, many=True)

    response = {
        'life_members': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=LifeMemberListSerializer, responses=LifeMemberListSerializer)
@api_view(['GET'])
def getAllLifeMemberWithoutPagination(request):
    life_members = LifeMember.objects.all()
    serializer = LifeMemberListSerializer(life_members, many=True)

    response = {
        "life_members": serializer.data
    }
    return Response(response, status=status.HTTP_200_OK)


@extend_schema(parameters=[OpenApiParameter('page'), OpenApiParameter('size')], request=LifeMemberListSerializer,
               responses=LifeMemberListSerializer)
@api_view(['GET'])
def getALifeMember(request, pk):
    try:
        life_member = LifeMember.objects.get(pk=pk)
        serializer = LifeMemberSerializer(life_member)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'details:'f"Life Member ID {pk} Doesnt exist"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=LifeMemberSerializer, responses=LifeMemberSerializer)
@api_view(['GET'])
def searchLifeMember(request):
    life_members = LifeMemberFilter(request.GET, queryset=LifeMember.objects.all())
    life_members = life_members.qs

    print('life_members: ', life_members)

    total_elements = life_members.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    life_members = pagination.paginate_data(life_members)

    serializer = LifeMemberListSerializer(life_members, many=True)

    response = {
        'life_members': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    if len(life_members) > 0:
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"There are no life_members matching your search"},
                        status=status.HTTP_400_BAD_REQUEST)

@extend_schema(request=LifeMemberSerializer, responses=LifeMemberSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createLifeMember(request):
    data = request.data
    print('data: ', data)
    print('content_type: ', request.content_type)

    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    serializer = LifeMemberSerializer(data=filtered_data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors)


@extend_schema(request=LifeMemberSerializer, responses=LifeMemberSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
def updateLifeMember(request, pk):
    data = request.data
    print('data :', data)
    filtered_data = {}

    try:
        life_member_obj = LifeMember.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response({'detail': f"Life Member id - {pk} doesn't exists"})

    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    logo = filtered_data.get('logo', None)
    favicon = filtered_data.get('favicon', None)

    if logo is not None and type(logo) == str:
        popped_logo = filtered_data.pop('logo')
    if favicon is not None and type(favicon) == str:
        popped_favicon = filtered_data.pop('favicon')

    serializer = LifeMemberSerializer(life_member_obj, data=filtered_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors)


@extend_schema(request=LifeMemberSerializer, responses=LifeMemberSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DELETE.name])
def deleteLifeMember(request, pk):
    try:
        life_member = LifeMember.objects.get(pk=pk)
        life_member.delete()
        return Response({'detail': f'Life Member id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f" Life Member id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)
