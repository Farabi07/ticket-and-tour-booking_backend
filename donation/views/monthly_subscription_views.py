

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from donation.models import MonthlySubscription
from donation.serializers import MonthlySubscriptionSerializer, MonthlySubscriptionListSerializer
from donation.filters import MonthlySubscriptionFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=MonthlySubscriptionSerializer,
    responses=MonthlySubscriptionSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_LIST.name])
def getAllMonthlySubscription(request):
    monthly_subscriptions = MonthlySubscription.objects.all()
    total_elements = monthly_subscriptions.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    monthly_subscriptions = pagination.paginate_data(monthly_subscriptions)

    serializer = MonthlySubscriptionListSerializer(monthly_subscriptions, many=True)

    response = {
        'monthly_subscriptions': serializer.data,
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
    request=MonthlySubscriptionSerializer,
    responses=MonthlySubscriptionSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_LIST.name])
def getAllMonthlySubscriptionByMember(request):
    monthly_subscriptions = MonthlySubscription.objects.filter(member=request.user)
    total_elements = monthly_subscriptions.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    monthly_subscriptions = pagination.paginate_data(monthly_subscriptions)

    serializer = MonthlySubscriptionSerializer(monthly_subscriptions, many=True)

    response = {
        'monthly_subscriptions': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=MonthlySubscriptionSerializer, responses=MonthlySubscriptionSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DETAILS.name])
def getAMonthlySubscription(request, pk):
    try:
        monthly_subscription = MonthlySubscription.objects.get(pk=pk)
        serializer = MonthlySubscriptionListSerializer(monthly_subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"MonthlySubscription id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=MonthlySubscriptionSerializer, responses=MonthlySubscriptionSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchMonthlySubscription(request):
    monthly_subscriptions = MonthlySubscriptionFilter(request.GET, queryset=MonthlySubscription.objects.all())
    monthly_subscriptions = monthly_subscriptions.qs

    print('searched_products: ', monthly_subscriptions)

    total_elements = monthly_subscriptions.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    monthly_subscriptions = pagination.paginate_data(monthly_subscriptions)

    serializer = MonthlySubscriptionListSerializer(monthly_subscriptions, many=True)

    response = {
        'monthly_subscriptions': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    if len(monthly_subscriptions) > 0:
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"There are no monthly_subscriptions matching your search"},
                        status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=MonthlySubscriptionSerializer, responses=MonthlySubscriptionSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_CREATE.name])
def createMonthlySubscription(request):
    data = request.data
    print('data: ', data)
    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0' and value != 'undefined':
            filtered_data[key] = value

    filtered_data['subscription_date'] = str(timezone.now())
    print('filtered_data: ', filtered_data)

    members = filtered_data.get('member')
    for member_id in members:
        filtered_data['member'] = member_id
        serializer = MonthlySubscriptionSerializer(data=filtered_data)
        if serializer.is_valid():
            print('validated_data: ', serializer.validated_data)
            serializer.save()
    return Response(status=status.HTTP_201_CREATED)


@extend_schema(request=MonthlySubscriptionSerializer, responses=MonthlySubscriptionSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_UPDATE.name])
def updateMonthlySubscription(request, pk):
    data = request.data
    print('data: ', data)

    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0':
            filtered_data[key] = value

    try:
        monthly_subscription = MonthlySubscription.objects.get(pk=pk)

        serializer = MonthlySubscriptionSerializer(monthly_subscription, data=filtered_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'detail': f"MonthlySubscription id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=MonthlySubscriptionSerializer, responses=MonthlySubscriptionSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DELETE.name])
def deleteMonthlySubscription(request, pk):
    try:
        monthly_subscription = MonthlySubscription.objects.get(pk=pk)
        monthly_subscription.delete()
        return Response({'detail': f'MonthlySubscription id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"MonthlySubscription id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
