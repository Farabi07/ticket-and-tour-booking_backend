from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from account.filters import AccountLogFilterForCashLedger, AccountLogFilterForBankAccountGroup, AccountLogFilterForDateAndSubLedgerOnly, AccountLogFilterForPassenger, AccountLogFilterForPersonOrCompanyLedger, AccountLogFilterForSubLedger, AccountLogFilterGeneral

from sequences import get_next_value

from drf_spectacular.utils import extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import Group, LedgerAccount, Contra, AccountLog
from account.serializers import AccountLogSerializer, AccountLogListSerializer

from commons.enums import PermissionEnum
from commons.pagination import Pagination

from itertools import chain
import datetime


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=AccountLogSerializer,
    responses=AccountLogSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAccountLogReportGeneral(request):
    date_after = request.query_params.get('date_after', None)
    ledger = request.query_params.get('ledger', None)

    total_prev_balance = 0
    if date_after and ledger:
        account_log_dr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger=ledger).values_list('debit_amount', flat=True)
        account_log_cr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger=ledger).values_list('credit_amount', flat=True)
        print('account_log_dr_list: ', account_log_dr_list)
        print('account_log_cr_list: ', account_log_cr_list)
        total_prev_balance = sum(account_log_dr_list) - \
            sum(account_log_cr_list)
        print('total_prev_balance: ', total_prev_balance)

    account_logs = AccountLogFilterGeneral(
        request.GET, queryset=AccountLog.objects.all())
    account_logs = account_logs.qs
    total_elements = account_logs.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    account_logs = pagination.paginate_data(account_logs)
    print('account_logs: ', account_logs)

    response_list = []

    if len(account_logs) > 0:
        for account_log in account_logs:
            account_log_dict = {}
            reference_no = account_log.reference_no
            account_log_serializer = AccountLogListSerializer(account_log)
            for key, value in account_log_serializer.data.items():
                account_log_dict[key] = value
            related_account_logs = AccountLog.objects.filter(
                reference_no=reference_no).exclude(pk=account_log.id)
            print('related_account_logs: ', related_account_logs)
            if len(related_account_logs) == 1:
                related_account_log = related_account_logs[0]
                account_log_dict['related_ledger'] = str(
                    related_account_log.ledger.name)
                pass
            elif len(related_account_logs) > 0:
                name_list = []
                for related_account_log in related_account_logs:
                    name_list.append(str(related_account_log.ledger.name))
                account_log_dict['related_ledgers'] = name_list
            response_list.append(account_log_dict)

    response = {
        'account_logs': response_list,
        'previous_balance': total_prev_balance,
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
    request=AccountLogSerializer,
    responses=AccountLogSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAccountLogReportByAccountType(request):
    date_after = request.query_params.get('date_after', None)
    date_before = request.query_params.get('date_before', None)
    account_type = request.query_params.get('account_type', None)
    ledger = request.query_params.get('ledger', None)

    total_prev_balance = 0
    if date_after and account_type == 'Cash':
        account_log_dr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger__name=account_type).values_list('debit_amount', flat=True)
        account_log_cr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger__name=account_type).values_list('credit_amount', flat=True)
        print('account_log_dr_list for cash: ', account_log_dr_list)
        print('account_log_cr_list for cash: ', account_log_cr_list)
        total_prev_balance = sum(account_log_dr_list) - \
            sum(account_log_cr_list)
        print('total_prev_balance: ', total_prev_balance)
    elif date_after and account_type == 'Bank':
        bank_accounts_group = Group.objects.filter(name='Bank Accounts')
        ledgers_under_bank_accounts = LedgerAccount.objects.filter(
            head_group=bank_accounts_group)
        account_log_dr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger__in=ledgers_under_bank_accounts).values_list('debit_amount', flat=True)
        account_log_cr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger__in=ledgers_under_bank_accounts).values_list('credit_amount', flat=True)
        print('account_log_dr_list for bank: ', account_log_dr_list)
        print('account_log_cr_list for bank: ', account_log_cr_list)
        total_prev_balance = sum(account_log_dr_list) - \
            sum(account_log_cr_list)
        print('total_prev_balance: ', total_prev_balance)
    if date_after and ledger and not account_type:
        account_log_dr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger__id=ledger).values_list('debit_amount', flat=True)
        account_log_cr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger__id=ledger).values_list('credit_amount', flat=True)
        print('account_log_dr_list for ledger: ', account_log_dr_list)
        print('account_log_cr_list for ledger: ', account_log_cr_list)
        total_prev_balance = sum(account_log_dr_list) - \
            sum(account_log_cr_list)
    print('total_prev_balance: ', total_prev_balance)

    account_logs = []

    if not ledger and account_type == 'Cash':
        account_logs = AccountLog.objects.filter(ledger__name='Cash')
        account_logs = AccountLogFilterForDateAndSubLedgerOnly(
            request.GET, queryset=account_logs)
        account_logs = account_logs.qs
        account_logs = account_logs.order_by('log_date')
        print('account_logs for cash: ', account_logs)
    elif not ledger and account_type == 'Bank':
        bank_accounts_group = Group.objects.filter(name='Bank Accounts')
        ledgers_under_bank_accounts = LedgerAccount.objects.filter(
            head_group__in=bank_accounts_group)
        account_logs = AccountLog.objects.filter(
            ledger__in=ledgers_under_bank_accounts)
        account_logs = AccountLogFilterForDateAndSubLedgerOnly(
            request.GET, queryset=account_logs)
        account_logs = account_logs.qs
        account_logs = account_logs.order_by('log_date')
        print('account_logs for bank: ', account_logs)
    else:
        account_logs = AccountLogFilterGeneral(
            request.GET, queryset=AccountLog.objects.all())
        account_logs = account_logs.qs
        account_logs = account_logs.order_by('log_date')
        print('account_logs for general: ', account_logs)

    total_elements = len(account_logs)

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    account_logs = pagination.paginate_data(account_logs)
    print('account_logs: ', account_logs)

    response_list = []

    if len(account_logs) > 0:
        for account_log in account_logs:
            account_log_dict = {}
            reference_no = account_log.reference_no
            account_log_serializer = AccountLogListSerializer(account_log)
            for key, value in account_log_serializer.data.items():
                account_log_dict[key] = value
            related_account_logs = AccountLog.objects.filter(
                reference_no=reference_no).exclude(pk=account_log.id)
            if len(related_account_logs) == 1:
                related_account_log = related_account_logs[0]
                account_log_dict['related_ledgers'] = str(
                    related_account_log.ledger.name)
            elif len(related_account_logs) > 0:
                name_list = []
                for related_account_log in related_account_logs:
                    name_list.append(str(related_account_log.ledger.name))
                account_log_dict['related_ledgers'] = name_list
            response_list.append(account_log_dict)

    response = {
        'account_logs': response_list,
        'previous_balance': total_prev_balance,
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
    request=AccountLogSerializer,
    responses=AccountLogSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getTotalCashDrCrBankDrCr(request):
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)

    if start_date and end_date:
        date_range = (start_date, end_date)

        # alternative date_range
        # start_date = str(start_date).split('-')
        # end_date = str(end_date).split('-')
        # date_range = (datetime.date(int(start_date[0]), int(start_date[1]), int(start_date[2])), datetime.date(int(end_date[0]), int(end_date[1]), int(end_date[2])))

        print('date_range: ', date_range)

        response_dict = dict()
        account_log_cash_dr_list = AccountLog.objects.filter(
            log_date__date__range=date_range, ledger__name='Cash').values_list('debit_amount', flat=True)
        account_log_cash_cr_list = AccountLog.objects.filter(
            log_date__date__range=date_range, ledger__name='Cash').values_list('credit_amount', flat=True)

        print('account_log_cash_dr_list for cash: ',
              account_log_cash_dr_list, account_log_cash_dr_list.count())
        print('account_log_cash_cr_list for cash: ',
              account_log_cash_cr_list, account_log_cash_cr_list.count())

        cash_dr_total = sum(account_log_cash_dr_list)
        cash_cr_total = sum(account_log_cash_cr_list)
        response_dict['cash_dr_total'] = cash_dr_total
        response_dict['cash_cr_total'] = cash_cr_total

        print('cash_dr_total: ', cash_dr_total)
        print('cash_cr_total: ', cash_cr_total)

        groups_under_bank_accounts = Group.objects.filter(
            head_group__name='Bank Accounts')
        child_groups = Group.objects.filter(
            head_group__in=groups_under_bank_accounts)
        chained_group_objs = list(
            chain(groups_under_bank_accounts, child_groups))
        print('chained_group_objs: ', chained_group_objs)

        ledger_account_objs = LedgerAccount.objects.filter(
            head_group__in=chained_group_objs)
        print('ledger_account_objs: ', ledger_account_objs)

        account_log_bank_dr_list = AccountLog.objects.filter(
            log_date__date__range=date_range, ledger__in=ledger_account_objs).values_list('debit_amount', flat=True)
        account_log_bank_cr_list = AccountLog.objects.filter(
            log_date__date__range=date_range, ledger__in=ledger_account_objs).values_list('credit_amount', flat=True)

        bank_dr_total = sum(account_log_bank_dr_list)
        bank_cr_total = sum(account_log_bank_cr_list)
        response_dict['bank_dr_total'] = bank_dr_total
        response_dict['bank_cr_total'] = bank_cr_total

        print('bank_dr_total: ', bank_dr_total)
        print('bank_cr_total: ', bank_cr_total)

    else:
        return Response({'detail': f"Please provide both 'start_date' and 'end_date' at a time."})

    return Response(response_dict, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=AccountLogSerializer,
    responses=AccountLogSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAccountLogReportForCashLedger(request):
    date_after = request.query_params.get('date_after', None)

    total_prev_balance = 0
    if date_after:
        account_log_dr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger__name='Cash').values_list('debit_amount', flat=True)
        account_log_cr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger__name='Cash').values_list('credit_amount', flat=True)
        print('account_log_dr_list: ', account_log_dr_list)
        print('account_log_cr_list: ', account_log_cr_list)
        total_prev_balance = sum(account_log_dr_list) - \
            sum(account_log_cr_list)
        print('total_prev_balance: ', total_prev_balance)

    account_logs = AccountLogFilterForCashLedger(
        request.GET, queryset=AccountLog.objects.filter(ledger__name='Cash'))
    account_logs = account_logs.qs
    total_elements = account_logs.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    account_logs = pagination.paginate_data(account_logs)
    print('account_logs: ', account_logs)

    response_list = []

    if len(account_logs) > 0:
        for account_log in account_logs:
            account_log_dict = {}
            reference_no = account_log.reference_no
            account_log_serializer = AccountLogListSerializer(account_log)
            for key, value in account_log_serializer.data.items():
                account_log_dict[key] = value
            related_account_logs = AccountLog.objects.filter(
                reference_no=reference_no).exclude(pk=account_log.id)
            print('related_account_logs: ', related_account_logs)
            if len(related_account_logs) == 1:
                related_account_log = related_account_logs[0]
                account_log_dict['related_ledger'] = str(
                    related_account_log.ledger.name)
                pass
            elif len(related_account_logs) > 0:
                name_list = []
                for related_account_log in related_account_logs:
                    name_list.append(str(related_account_log.ledger.name))
                account_log_dict['related_ledgers'] = name_list
            response_list.append(account_log_dict)

    response = {
        'account_logs': response_list,
        'previous_balance': total_prev_balance,
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
    request=AccountLogSerializer,
    responses=AccountLogSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAccountLogReportForBankAccountGroup(request):
    date_after = request.query_params.get('date_after', None)

    ledger_account_objs = LedgerAccount.objects.filter(
        head_group__name='Bank Accounts')

    total_prev_balance = 0
    if date_after:
        account_log_dr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger__in=ledger_account_objs).values_list('debit_amount', flat=True)
        account_log_cr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger__in=ledger_account_objs).values_list('credit_amount', flat=True)
        print('account_log_dr_list: ', account_log_dr_list)
        print('account_log_cr_list: ', account_log_cr_list)
        total_prev_balance = sum(account_log_dr_list) - \
            sum(account_log_cr_list)
        print('total_prev_balance: ', total_prev_balance)

    account_log_objs = AccountLog.objects.filter(
        ledger__in=ledger_account_objs)
    account_logs = AccountLogFilterForBankAccountGroup(
        request.GET, queryset=account_log_objs)

    account_logs = account_logs.qs
    total_elements = account_logs.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    account_logs = pagination.paginate_data(account_logs)
    print('account_logs: ', account_logs)

    response_list = []

    if len(account_logs) > 0:
        for account_log in account_logs:
            account_log_dict = {}
            reference_no = account_log.reference_no
            account_log_serializer = AccountLogListSerializer(account_log)
            for key, value in account_log_serializer.data.items():
                account_log_dict[key] = value
            related_account_logs = AccountLog.objects.filter(
                reference_no=reference_no).exclude(pk=account_log.id)
            print('related_account_logs: ', related_account_logs)
            if len(related_account_logs) == 1:
                related_account_log = related_account_logs[0]
                account_log_dict['related_ledger'] = str(
                    related_account_log.ledger.name)
                pass
            elif len(related_account_logs) > 0:
                name_list = []
                for related_account_log in related_account_logs:
                    name_list.append(str(related_account_log.ledger.name))
                account_log_dict['related_ledgers'] = name_list
            response_list.append(account_log_dict)

    response = {
        'account_logs': response_list,
        'previous_balance': total_prev_balance,
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
    request=AccountLogSerializer,
    responses=AccountLogSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAccountLogReportForPersonOrCompanyLedger(request):
    date_after = request.query_params.get('date_after', None)
    ledger = request.query_params.get('ledger', None)

    total_prev_balance = 0
    if date_after and ledger:
        account_log_dr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger=ledger).values_list('debit_amount', flat=True)
        account_log_cr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, ledger=ledger).values_list('credit_amount', flat=True)
        print('account_log_dr_list: ', account_log_dr_list)
        print('account_log_cr_list: ', account_log_cr_list)
        total_prev_balance = sum(account_log_dr_list) - \
            sum(account_log_cr_list)
        print('total_prev_balance: ', total_prev_balance)

    account_logs = AccountLogFilterForPersonOrCompanyLedger(
        request.GET, queryset=AccountLog.objects.all())
    account_logs = account_logs.qs
    total_elements = account_logs.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    account_logs = pagination.paginate_data(account_logs)
    print('account_logs: ', account_logs)

    response_list = []

    if len(account_logs) > 0:
        for account_log in account_logs:
            account_log_dict = {}
            reference_no = account_log.reference_no
            account_log_serializer = AccountLogListSerializer(account_log)
            for key, value in account_log_serializer.data.items():
                account_log_dict[key] = value
            related_account_logs = AccountLog.objects.filter(
                reference_no=reference_no).exclude(pk=account_log.id)
            print('related_account_logs: ', related_account_logs)
            if len(related_account_logs) == 1:
                related_account_log = related_account_logs[0]
                account_log_dict['related_ledger'] = str(
                    related_account_log.ledger.name)
                pass
            elif len(related_account_logs) > 0:
                name_list = []
                for related_account_log in related_account_logs:
                    name_list.append(str(related_account_log.ledger.name))
                account_log_dict['related_ledgers'] = name_list
            response_list.append(account_log_dict)

    response = {
        'account_logs': response_list,
        'previous_balance': total_prev_balance,
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
    request=AccountLogSerializer,
    responses=AccountLogSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAccounLogReportForPassenger(request):
    date_after = request.query_params.get('date_after', None)
    passenger = request.query_params.get('passenger', None)

    total_prev_balance = 0
    if date_after and passenger:
        account_log_dr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, passenger=passenger).values_list('debit_amount', flat=True)
        account_log_cr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, passenger=passenger).values_list('credit_amount', flat=True)
        print('account_log_dr_list: ', account_log_dr_list)
        print('account_log_cr_list: ', account_log_cr_list)
        total_prev_balance = sum(account_log_dr_list) - \
            sum(account_log_cr_list)
        print('total_prev_balance: ', total_prev_balance)

    account_logs = AccountLogFilterForPassenger(
        request.GET, queryset=AccountLog.objects.all())
    account_logs = account_logs.qs
    total_elements = account_logs.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    account_logs = pagination.paginate_data(account_logs)
    print('account_logs: ', account_logs)

    response_list = []

    if len(account_logs) > 0:
        for account_log in account_logs:
            account_log_dict = {}
            reference_no = account_log.reference_no
            account_log_serializer = AccountLogListSerializer(account_log)
            for key, value in account_log_serializer.data.items():
                account_log_dict[key] = value
            related_account_logs = AccountLog.objects.filter(
                reference_no=reference_no).exclude(pk=account_log.id)
            print('related_account_logs: ', related_account_logs)
            if len(related_account_logs) == 1:
                related_account_log = related_account_logs[0]
                account_log_dict['related_ledger'] = str(
                    related_account_log.ledger.name)
                pass
            elif len(related_account_logs) > 0:
                name_list = []
                for related_account_log in related_account_logs:
                    name_list.append(str(related_account_log.ledger.name))
                account_log_dict['related_ledgers'] = name_list
            response_list.append(account_log_dict)

    response = {
        'account_logs': response_list,
        'previous_balance': total_prev_balance,
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
    request=AccountLogSerializer,
    responses=AccountLogSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getAccounLogReportForSubLedger(request):
    date_after = request.query_params.get('date_after', None)
    sub_ledger = request.query_params.get('sub_ledger', None)

    total_prev_balance = 0
    if date_after and sub_ledger:
        account_log_dr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, sub_ledger=sub_ledger).values_list('debit_amount', flat=True)
        account_log_cr_list = AccountLog.objects.filter(
            log_date__date__lt=date_after, sub_ledger=sub_ledger).values_list('credit_amount', flat=True)
        print('account_log_dr_list: ', account_log_dr_list)
        print('account_log_cr_list: ', account_log_cr_list)
        total_prev_balance = sum(account_log_dr_list) - \
            sum(account_log_cr_list)
        print('total_prev_balance: ', total_prev_balance)

    account_logs = AccountLogFilterForSubLedger(
        request.GET, queryset=AccountLog.objects.all())
    account_logs = account_logs.qs
    total_elements = account_logs.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    account_logs = pagination.paginate_data(account_logs)
    print('account_logs: ', account_logs)

    response_list = []

    if len(account_logs) > 0:
        for account_log in account_logs:
            account_log_dict = {}
            reference_no = account_log.reference_no
            account_log_serializer = AccountLogListSerializer(account_log)
            for key, value in account_log_serializer.data.items():
                account_log_dict[key] = value
            related_account_logs = AccountLog.objects.filter(
                reference_no=reference_no).exclude(pk=account_log.id)
            print('related_account_logs: ', related_account_logs)
            if len(related_account_logs) == 1:
                related_account_log = related_account_logs[0]
                account_log_dict['related_ledger'] = str(
                    related_account_log.ledger.name)
                pass
            elif len(related_account_logs) > 0:
                name_list = []
                for related_account_log in related_account_logs:
                    name_list.append(str(related_account_log.ledger.name))
                account_log_dict['related_ledgers'] = name_list
            response_list.append(account_log_dict)

    response = {
        'account_logs': response_list,
        'previous_balance': total_prev_balance,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)
