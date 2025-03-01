from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from authentication.serializers import UserSerializer
from django.db.models import Q
from commons.pagination import Pagination

from donation.models import MemberAccountLog
from donation.serializers import DonationSerializer, MemberAccountLogSerializer, PaymentMethodSerializer
from donation_report.filters import MemberAccountLogFilter


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=MemberAccountLogSerializer,
    responses=MemberAccountLogSerializer
)
@api_view(['GET'])
def getwithdrawReport(request):
    user_id = request.query_params.get('user')

    payment_methods = request.query_params.get('payment_method')
    withdraw_reports = MemberAccountLogFilter(
        request.GET, queryset=MemberAccountLog.objects.filter(
            Q(debit_amount__gt=0.0)))
    withdraw_reports = withdraw_reports.qs
    if user_id:
        withdraw_reports = withdraw_reports.filter(user=user_id)
    if payment_methods:
        withdraw_reports = withdraw_reports.filter(
            payment_method=payment_methods)
    total_elements = withdraw_reports.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    withdraw_reports = pagination.paginate_data(withdraw_reports)
    previous_balance = 0
    data = []
    if len(withdraw_reports) > 0:
        for withdraw_report in withdraw_reports:
            date = withdraw_report.date
            user = withdraw_report.user
            payment_method = withdraw_report.payment_method
            payment_number = withdraw_report.payment_number
            amount = withdraw_report.debit_amount

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
        "withdraws": data,
        "total_elements": total_elements,
        "size": size,
        "page": page,
        'total_pages': pagination.total_pages,
        'previous_balance': previous_balance
    }
    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    request=MemberAccountLogSerializer,
    responses=MemberAccountLogSerializer
)
@api_view(['GET'])
def getwithdrawReportWithoutPagination(request):
    user_id = request.query_params.get('user')
    payment_methods = request.query_params.get('payment_method')
    withdraw_reports = MemberAccountLogFilter(
        request.GET, queryset=MemberAccountLog.objects.filter(
            Q(debit_amount__gt=0.0)))
    withdraw_reports = withdraw_reports.qs
    if user_id:
        withdraw_reports = withdraw_reports.filter(user=user_id)
    if payment_methods:
        withdraw_reports = withdraw_reports.filter(
            payment_method=payment_methods)
    previous_balance = 0
    data = []
    if len(withdraw_reports) > 0:
        for withdraw_report in withdraw_reports:
            date = withdraw_report.date
            user = withdraw_report.user
            payment_method = withdraw_report.payment_method
            payment_number = withdraw_report.payment_number
            amount = withdraw_report.debit_amount

            user_serializer = UserSerializer(user)
            payment_method_serializer = PaymentMethodSerializer(payment_method)
            user_data = user_serializer.data
            payment_method_data = payment_method_serializer.data
            if amount:
                data.append({
                    "user": user_data,
                    "date": date,
                    "payment_method": payment_method_data,
                    "payment_number": payment_number,
                    "amount": amount,
                })

    response = {
        "withdraws": data,
        'previous_balance': previous_balance
    }
    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    request=MemberAccountLogSerializer,
    responses=MemberAccountLogSerializer
)
@api_view(['GET'])
def getwithdrawReportByUserID(request, user_id):

    withdraw_reports = MemberAccountLogFilter(
        request.GET, queryset=MemberAccountLog.objects.filter(
            Q(debit_amount__gt=0.0)))
    withdraw_reports = withdraw_reports.qs
    if user_id:
        withdraw_reports = withdraw_reports.filter(user=user_id)

    previous_balance = 0
    data = []
    if len(withdraw_reports) > 0:
        for withdraw_report in withdraw_reports:
            date = withdraw_report.date
            user = withdraw_report.user
            payment_method = withdraw_report.payment_method
            payment_number = withdraw_report.payment_number
            amount = withdraw_report.debit_amount

            user_serializer = UserSerializer(user)
            payment_method_serializer = PaymentMethodSerializer(payment_method)
            user_data = user_serializer.data
            payment_method_data = payment_method_serializer.data
            if amount:
                data.append({
                    "user": user_data,
                    "date": date,
                    "payment_method": payment_method_data,
                    "payment_number": payment_number,
                    "amount": amount,
                })

    response = {
        "withdraws": data,
        'previous_balance': previous_balance
    }
    return Response(response, status=status.HTTP_200_OK)
