from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from authentication.serializers import UserSerializer
from django.db.models import Q
from commons.pagination import Pagination

from donation.models import Collection, MemberAccountLog
from donation.serializers import DonationSerializer, MemberAccountLogSerializer, PaymentMethodSerializer
from donation_report.filters import CollectionFilter


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=DonationSerializer,
    responses=DonationSerializer
)
@api_view(['GET'])
def getCollectionReport(request):
    user_id = request.query_params.get('user')
    payment_methods = request.query_params.get('payment_method')
    collection_reports = CollectionFilter(
        request.GET, queryset=Collection.objects.filter(
            Q(amount__gt=0.0)))
    collection_reports = collection_reports.qs
    if user_id:
        collection_reports = collection_reports.filter(user=user_id)
    if payment_methods:
        collection_reports = collection_reports.filter(
            payment_method=payment_methods)
    total_elements = collection_reports.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    collection_reports = pagination.paginate_data(collection_reports)
    previous_balance = 0
    data = []
    if len(collection_reports) > 0:
        for collection_report in collection_reports:
            date = collection_report.date
            user = collection_report.user
            payment_method = collection_report.payment_method
            payment_number = collection_report.payment_number
            amount = collection_report.amount

            user_serializer = UserSerializer(user)
            payment_method_serializer = PaymentMethodSerializer(payment_method)
            user_data = user_serializer.data
            payment_method_data = payment_method_serializer.data

            data.append({
                "user": user_data,
                "date": date,
                "payment_method": payment_method_data,
                "payment_number": payment_number,
                "amount": amount,
            })

    response = {
        "collections": data,
        "total_elements": total_elements,
        "size": size,
        "page": page,
        'total_pages': pagination.total_pages,
        'previous_balance': previous_balance
    }
    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    request=DonationSerializer,
    responses=DonationSerializer
)
@api_view(['GET'])
def getCollectionReportWithoutPagination(request):
    user_id = request.query_params.get('user')
    payment_methods = request.query_params.get('payment_method')
    collection_reports = CollectionFilter(
        request.GET, queryset=Collection.objects.filter(
            Q(amount__gt=0.0)))
    collection_reports = collection_reports.qs
    if user_id:
        collection_reports = collection_reports.filter(user=user_id)
    if payment_methods:
        collection_reports = collection_reports.filter(
            payment_method=payment_methods)

    previous_balance = 0
    data = []
    if len(collection_reports) > 0:
        for collection_report in collection_reports:
            date = collection_report.date
            user = collection_report.user
            payment_method = collection_report.payment_method
            payment_number = collection_report.payment_number
            amount = collection_report.amount

            user_serializer = UserSerializer(user)
            payment_method_serializer = PaymentMethodSerializer(payment_method)
            user_data = user_serializer.data
            payment_method_data = payment_method_serializer.data

            data.append({
                "user": user_data,
                "date": date,
                "payment_method": payment_method_data,
                "payment_number": payment_number,
                "amount": amount,
            })

    response = {
        "collections": data,
        'previous_balance': previous_balance
    }
    return Response(response, status=status.HTTP_200_OK)
