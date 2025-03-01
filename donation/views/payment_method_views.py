from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from donation.models import PaymentMethod
from donation.serializers import PaymentMethodSerializer, PaymentMethodListSerializer
from donation.filters import PaymentMethodFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=PaymentMethodSerializer,
    responses=PaymentMethodSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_LIST.name])
def getAllPaymentMethod(request):
    paymentmethods = PaymentMethod.objects.all()
    total_elements = paymentmethods.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    paymentmethods = pagination.paginate_data(paymentmethods)

    serializer = PaymentMethodSerializer(paymentmethods, many=True)

    response = {
        'paymentmethods': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=PaymentMethodSerializer, responses=PaymentMethodSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DETAILS.name])
def getAPaymentMethod(request, pk):
    try:
        paymentmethod = PaymentMethod.objects.get(pk=pk)
        serializer = PaymentMethodSerializer(paymentmethod)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"PaymentMethod id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PaymentMethodSerializer, responses=PaymentMethodSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchPaymentMethod(request):
    payment_methods = PaymentMethodFilter(request.GET, queryset=PaymentMethod.objects.all())
    payment_methods = payment_methods.qs

    print('searched_products: ', payment_methods)

    total_elements = payment_methods.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    payment_methods = pagination.paginate_data(payment_methods)

    serializer = PaymentMethodListSerializer(payment_methods, many=True)

    response = {
        'payment_methods': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    if len(payment_methods) > 0:
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"There are no payment_methods matching your search"},
                        status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PaymentMethodSerializer, responses=PaymentMethodSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_CREATE.name])
def createPaymentMethod(request):
    data = request.data
    print('data: ', data)
    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0' and value != "undefined":
            filtered_data[key] = value

    serializer = PaymentMethodSerializer(data=filtered_data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PaymentMethodSerializer, responses=PaymentMethodSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_UPDATE.name])
def updatePaymentMethod(request, pk):
    data = request.data
    print('data: ', data)
    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0':
            filtered_data[key] = value
    image = filtered_data.get('image', None)
    if image is not None and type(image) == str:
        image = filtered_data.pop('image')
    try:
        paymentmethod = PaymentMethod.objects.get(pk=pk)

        serializer = PaymentMethodSerializer(paymentmethod, data=filtered_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'detail': f"PaymentMethod id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=PaymentMethodSerializer, responses=PaymentMethodSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DELETE.name])
def deletePaymentMethod(request, pk):
    try:
        paymentmethod = PaymentMethod.objects.get(pk=pk)
        paymentmethod.delete()
        return Response({'detail': f'PaymentMethod id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"PaymentMethod id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=PaymentMethodSerializer,
    responses=PaymentMethodSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_LIST_VIEW.name])
def getAllPaymentMethodByTypeId(request, type_id):
    payment_method = PaymentMethod.objects.filter(type=type_id)

    serializer = PaymentMethodSerializer(payment_method, many=True)

    return Response({'payment_method': serializer.data}, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=PaymentMethodSerializer,
    responses=PaymentMethodSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getPaymentMethodWithoutPagination(request):
    payment_method = PaymentMethod.objects.all()
    print('payment_method: ', payment_method)
    serializer = PaymentMethodSerializer(payment_method, many=True)
    response = {
        'payment_method': serializer.data,
    }
    return Response(response, status=status.HTTP_200_OK)