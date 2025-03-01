from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from authentication.serializers import UserSerializer
from django.db.models import Q
from commons.pagination import Pagination

from donation.models import Collection, MemberAccountLog
from donation.serializers import DonationSerializer, PaymentMethodSerializer
from donation_report.filters import CollectionFilter, LedgerFilter, MemberAccountLogFilter


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=DonationSerializer,
    responses=DonationSerializer
)
@api_view(['GET'])
def getLedgerReport(request):
    user_id = request.query_params.get('user')
    payment_methods = request.query_params.get('payment_method')
    date_before = request.query_params.get('date_before')
    date_after = request.query_params.get('date_after')
    ledger_reports = LedgerFilter(
        request.GET, queryset=MemberAccountLog.objects.filter(
            Q(credit_amount__gt=0.0) | Q(debit_amount__gt=0.0)))
    ledger_reports = ledger_reports.qs
    if user_id:
        ledger_reports = ledger_reports.filter(user=user_id)
    if payment_methods:
        ledger_reports = ledger_reports.filter(
            payment_method=payment_methods)
    if date_before:
        ledger_reports = ledger_reports.filter(
            date__gt=date_before)
    if date_after:
        ledger_reports = ledger_reports.filter(
            date__lt=date_after)

    total_elements = ledger_reports.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    ledger_reports = pagination.paginate_data(ledger_reports)
    previous_balance = 0
    data = []

    if date_before:
        previous_balance = sum(
            log.credit_amount - log.debit_amount for log in ledger_reports)
    else:
        previous_balance = 0
    print('previous_balance: ', previous_balance)
    if len(ledger_reports) > 0:
        for ledger_report in ledger_reports:
            date = ledger_report.date
            user = ledger_report.user
            payment_method = ledger_report.payment_method
            payment_number = ledger_report.payment_number
            debit_amount = ledger_report.debit_amount
            credit_amount = ledger_report.credit_amount

            user_serializer = UserSerializer(user)
            payment_method_serializer = PaymentMethodSerializer(payment_method)
            user_data = user_serializer.data
            payment_method_data = payment_method_serializer.data

            data.append({
                "user": user_data,
                "date": date,
                "payment_method": payment_method_data,
                "payment_number": payment_number,
                "debit_amount": debit_amount,
                "credit_amount": credit_amount
            })

    response = {
        "account_logs": data,
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
def getLedgerReportWithoutPagination(request):
    user_id = request.query_params.get('user')
    payment_methods = request.query_params.get('payment_method')
    ledger_reports = LedgerFilter(
        request.GET, queryset=MemberAccountLog.objects.filter(
            Q(credit_amount__gt=0.0) | Q(debit_amount__gt=0.0)))
    ledger_reports = ledger_reports.qs
    if user_id:
        ledger_reports = ledger_reports.filter(user=user_id)
    if payment_methods:
        ledger_reports = ledger_reports.filter(
            payment_method=payment_methods)

    previous_balance = 0
    data = []

    date_before = request.query_params.get('date_before')
    ledger_reports_date_before = LedgerFilter(
        request.GET, queryset=MemberAccountLog.objects.filter(
            Q(credit_amount__gt=0.0) | Q(debit_amount__gt=0.0) | Q(date=date_before)))
    ledger_reports_date_before = ledger_reports_date_before.qs
    previous_balance = sum(
        log.credit_amount - log.debit_amount for log in ledger_reports_date_before)

    if len(ledger_reports) > 0:
        for ledger_report in ledger_reports:
            date = ledger_report.date
            user = ledger_report.user
            payment_method = ledger_report.payment_method
            payment_number = ledger_report.payment_number
            debit_amount = ledger_report.debit_amount
            credit_amount = ledger_report.credit_amount

            user_serializer = UserSerializer(user)
            payment_method_serializer = PaymentMethodSerializer(payment_method)
            user_data = user_serializer.data
            payment_method_data = payment_method_serializer.data

            data.append({
                "user": user_data,
                "date": date,
                "payment_method": payment_method_data,
                "payment_number": payment_number,
                "debit_amount": debit_amount,
                "credit_amount": credit_amount
            })

    response = {
        "account_logs": data,
        'previous_balance': previous_balance
    }
    return Response(response, status=status.HTTP_200_OK)
