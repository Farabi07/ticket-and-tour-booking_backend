from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from donation.models import PaymentMethodDetail
from donation.serializers import PaymentMethodDetailSerializer, PaymentMethodDetailListSerializer
from donation.filters import PaymentMethodDetailFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=PaymentMethodDetailSerializer,
    responses=PaymentMethodDetailSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_LIST.name])
def getAllPaymentMethodDetail(request):
    paymentmethods = PaymentMethodDetail.objects.all()
    total_elements = paymentmethods.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    paymentmethods = pagination.paginate_data(paymentmethods)

    serializer = PaymentMethodDetailSerializer(paymentmethods, many=True)

    response = {
        'paymentmethods': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=PaymentMethodDetailSerializer, responses=PaymentMethodDetailSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DETAILS.name])
def getAPaymentMethodDetail(request, pk):
    try:
        payment_method_detail = PaymentMethodDetail.objects.get(pk=pk)
        serializer = PaymentMethodDetailSerializer(payment_method_detail)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"PaymentMethodDetail id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PaymentMethodDetailSerializer, responses=PaymentMethodDetailSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchPaymentMethodDetail(request):
    payment_method_details = PaymentMethodDetailFilter(request.GET, queryset=PaymentMethodDetail.objects.all())
    payment_method_details = payment_method_details.qs

    print('searched_products: ', payment_method_details)

    total_elements = payment_method_details.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    payment_method_details = pagination.paginate_data(payment_method_details)

    serializer = PaymentMethodDetailListSerializer(payment_method_details, many=True)

    response = {
        'payment_method_details': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    if len(payment_method_details) > 0:
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"There are no payment_method_details matching your search"},
                        status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PaymentMethodDetailSerializer, responses=PaymentMethodDetailSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_CREATE.name])
def createPaymentMethodDetail(request):
    data = request.data
    print('data: ', data)
    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0':
            filtered_data[key] = value

    serializer = PaymentMethodDetailSerializer(data=filtered_data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PaymentMethodDetailSerializer, responses=PaymentMethodDetailSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_UPDATE.name])
def updatePaymentMethodDetail(request, pk):
    data = request.data
    print('data: ', data)
    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0':
            filtered_data[key] = value
    try:
        payment_method_detail = PaymentMethodDetail.objects.get(pk=pk)

        serializer = PaymentMethodDetailSerializer(payment_method_detail, data=filtered_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'detail': f"PaymentMethodDetail id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PaymentMethodDetailSerializer, responses=PaymentMethodDetailSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DELETE.name])
def deletePaymentMethodDetail(request, pk):
    try:
        payment_method_detail = PaymentMethodDetail.objects.get(pk=pk)
        payment_method_detail.delete()
        return Response({'detail': f'PaymentMethodDetail id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"PaymentMethodDetail id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
