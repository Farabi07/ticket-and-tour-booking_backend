from tracemalloc import start
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from account.models import AccountLog, Group, LedgerAccount, PaymentVoucher
from account.serializers import AccountLogListSerializer, GroupTreeSerializer, PaymentVoucherListSerializer, PaymentVoucherSerializer
from account.filters import PaymentVoucherFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination

from decimal import Decimal
from datetime import datetime




# Create your views here.

@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=AccountLogListSerializer,
	responses=AccountLogListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getTrialBalance(request):
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    date_range = (start_date, end_date)
    print('start_date: ', start_date)
    print('end_date: ', end_date)
    print('date_range: ', date_range)
    response_dict = {'assets': {}, 'expenses': {}, 'incomes': {}, 'liabilities': {}}
    groups_under_pg_assets = Group.objects.filter(head_primarygroup__name='Assets')
    print('groups_under_pg_assets: ', groups_under_pg_assets)
    assets_total = 0
    for agroup1 in groups_under_pg_assets:
        assets_dict = {}
        agroup1_total = 0
        ledgers = LedgerAccount.objects.filter(head_group=agroup1)
        if len(ledgers) > 0:
            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
            total = sum(account_log_dr_list)
            agroup1_total += total
        agroups = Group.objects.filter(head_group=agroup1)
        for agroup2 in agroups:
            agroup2_total = 0
            ledgers = LedgerAccount.objects.filter(head_group=agroup2)
            if len(ledgers) > 0:
                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                print('account_log_dr_list: ', account_log_dr_list)
                total = sum(account_log_dr_list)
                agroup2_total += total
            agroups = Group.objects.filter(head_group=agroup2)
            for agroup3 in agroups:
                ledgers = LedgerAccount.objects.filter(head_group=agroup3)
                if len(ledgers) > 0:
                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                    total = sum(account_log_dr_list)
                    agroup2_total += total
                agroups = Group.objects.filter(head_group=agroup2)
                for agroup4 in agroups:
                    ledgers = LedgerAccount.objects.filter(head_group=agroup4)
                    if len(ledgers) > 0:
                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                        total = sum(account_log_dr_list)
                        agroup2_total += total
                    agroups = Group.objects.filter(head_group=agroup4)
                    for agroup5 in agroups:
                        ledgers = LedgerAccount.objects.filter(head_group=agroup5)
                        if len(ledgers) > 0:
                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                            total = sum(account_log_dr_list)
                            agroup2_total += total
                        agroups = Group.objects.filter(head_group=agroup5)
                        for agroup6 in agroups:
                            ledgers = LedgerAccount.objects.filter(head_group=agroup6)
                            if len(ledgers) > 0:
                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                total = sum(account_log_dr_list)
                                agroup2_total += total
                            agroups = Group.objects.filter(head_group=agroup6)
                            for agroup7 in agroups:
                                ledgers = LedgerAccount.objects.filter(head_group=agroup7)
                                if len(ledgers) > 0:
                                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                    total = sum(account_log_dr_list)
                                    agroup2_total += total
                                agroups = Group.objects.filter(head_group=agroup7)
                                for agroup8 in agroups:
                                    ledgers = LedgerAccount.objects.filter(head_group=agroup8)
                                    if len(ledgers) > 0:
                                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                        total = sum(account_log_dr_list)
                                        agroup2_total += total
                                    agroups = Group.objects.filter(head_group=agroup8)
                                    for agroup9 in agroups:
                                        ledgers = LedgerAccount.objects.filter(head_group=agroup9)
                                        if len(ledgers) > 0:
                                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                            total = sum(account_log_dr_list)
                                            agroup2_total += total
                                        agroups = Group.objects.filter(head_group=agroup9)
                                        for agroup10 in agroups:
                                            ledgers = LedgerAccount.objects.filter(head_group=agroup10)
                                            if len(ledgers) > 0:
                                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                                total = sum(account_log_dr_list)
                                                agroup2_total += total
            agroup1_total += agroup2_total
            assets_dict[agroup2.name] = agroup2_total
        assets_total += agroup1_total
        response_dict['assets']['assets_total'] = assets_total
        response_dict['assets'][agroup1.name] = assets_dict
        response_dict['assets'][agroup1.name]['total'] = agroup1_total


    groups_under_pg_expenses = Group.objects.filter(head_primarygroup__name='Expenses')
    print('groups_under_pg_expenses: ', groups_under_pg_expenses)
    expenses_total = 0
    for egroup1 in groups_under_pg_expenses:
        expenses_dict = {}
        egroup1_total = 0
        ledgers = LedgerAccount.objects.filter(head_group=egroup1)
        if len(ledgers) > 0:
            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
            total = sum(account_log_dr_list)
            egroup1_total += total
        egroups = Group.objects.filter(head_group=egroup1)
        for egroup2 in egroups:
            egroup2_total = 0
            ledgers = LedgerAccount.objects.filter(head_group=egroup2)
            if len(ledgers) > 0:
                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                total = sum(account_log_dr_list)
                egroup2_total += total
            egroups = Group.objects.filter(head_group=egroup2)
            for egroup3 in egroups:
                ledgers = LedgerAccount.objects.filter(head_group=egroup3)
                if len(ledgers) > 0:
                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                    total = sum(account_log_dr_list)
                    egroup2_total += total
                egroups = Group.objects.filter(head_group=egroup2)
                for egroup4 in egroups:
                    ledgers = LedgerAccount.objects.filter(head_group=egroup4)
                    if len(ledgers) > 0:
                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                        total = sum(account_log_dr_list)
                        egroup2_total += total
                    egroups = Group.objects.filter(head_group=egroup4)
                    for egroup5 in egroups:
                        ledgers = LedgerAccount.objects.filter(head_group=egroup5)
                        if len(ledgers) > 0:
                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                            total = sum(account_log_dr_list)
                            egroup2_total += total
                        egroups = Group.objects.filter(head_group=egroup5)
                        for egroup6 in egroups:
                            ledgers = LedgerAccount.objects.filter(head_group=egroup6)
                            if len(ledgers) > 0:
                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                total = sum(account_log_dr_list)
                                egroup2_total += total
                            egroups = Group.objects.filter(head_group=egroup6)
                            for egroup7 in egroups:
                                ledgers = LedgerAccount.objects.filter(head_group=egroup7)
                                if len(ledgers) > 0:
                                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                    total = sum(account_log_dr_list)
                                    egroup2_total += total
                                egroups = Group.objects.filter(head_group=egroup7)
                                for egroup8 in egroups:
                                    ledgers = LedgerAccount.objects.filter(head_group=egroup8)
                                    if len(ledgers) > 0:
                                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                        total = sum(account_log_dr_list)
                                        egroup2_total += total
                                    egroups = Group.objects.filter(head_group=egroup8)
                                    for egroup9 in egroups:
                                        ledgers = LedgerAccount.objects.filter(head_group=egroup9)
                                        if len(ledgers) > 0:
                                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                            total = sum(account_log_dr_list)
                                            egroup2_total += total
                                        egroups = Group.objects.filter(head_group=egroup9)
                                        for egroup10 in egroups:
                                            ledgers = LedgerAccount.objects.filter(head_group=egroup10)
                                            if len(ledgers) > 0:
                                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                                total = sum(account_log_dr_list)
                                                egroup2_total += total
            egroup1_total += egroup2_total
            expenses_dict[egroup2.name] = egroup2_total
        expenses_total += egroup1_total
        response_dict['expenses']['expenses_total'] = expenses_total
        response_dict['expenses'][egroup1.name] = expenses_dict
        response_dict['expenses'][egroup1.name]['total'] = egroup1_total


    groups_under_pg_incomes = Group.objects.filter(head_primarygroup__name='Incomes')
    print('groups_under_pg_incomes: ', groups_under_pg_incomes)
    incomes_total = 0
    for igroup1 in groups_under_pg_incomes:
        incomes_dict = {}
        igroup1_total = 0
        ledgers = LedgerAccount.objects.filter(head_group=igroup1)
        if len(ledgers) > 0:
            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
            total = sum(account_log_dr_list)
            igroup1_total += total
        igroups = Group.objects.filter(head_group=igroup1)
        for igroup2 in igroups:
            igroup2_total = 0
            ledgers = LedgerAccount.objects.filter(head_group=igroup2)
            if len(ledgers) > 0:
                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                total = sum(account_log_dr_list)
                igroup2_total += total
            igroups = Group.objects.filter(head_group=igroup2)
            for igroup3 in igroups:
                ledgers = LedgerAccount.objects.filter(head_group=igroup3)
                if len(ledgers) > 0:
                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                    total = sum(account_log_dr_list)
                    igroup2_total += total
                igroups = Group.objects.filter(head_group=igroup2)
                for igroup4 in igroups:
                    ledgers = LedgerAccount.objects.filter(head_group=igroup4)
                    if len(ledgers) > 0:
                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                        total = sum(account_log_dr_list)
                        igroup2_total += total
                    igroups = Group.objects.filter(head_group=igroup4)
                    for igroup5 in igroups:
                        ledgers = LedgerAccount.objects.filter(head_group=igroup5)
                        if len(ledgers) > 0:
                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                            total = sum(account_log_dr_list)
                            igroup2_total += total
                        igroups = Group.objects.filter(head_group=igroup5)
                        for igroup6 in igroups:
                            ledgers = LedgerAccount.objects.filter(head_group=igroup6)
                            if len(ledgers) > 0:
                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                total = sum(account_log_dr_list)
                                igroup2_total += total
                            igroups = Group.objects.filter(head_group=igroup6)
                            for igroup7 in igroups:
                                ledgers = LedgerAccount.objects.filter(head_group=igroup7)
                                if len(ledgers) > 0:
                                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                    total = sum(account_log_dr_list)
                                    igroup2_total += total
                                igroups = Group.objects.filter(head_group=igroup7)
                                for igroup8 in igroups:
                                    ledgers = LedgerAccount.objects.filter(head_group=igroup8)
                                    if len(ledgers) > 0:
                                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                        total = sum(account_log_dr_list)
                                        igroup2_total += total
                                    igroups = Group.objects.filter(head_group=igroup8)
                                    for igroup9 in igroups:
                                        ledgers = LedgerAccount.objects.filter(head_group=igroup9)
                                        if len(ledgers) > 0:
                                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                            total = sum(account_log_dr_list)
                                            igroup2_total += total
                                        igroups = Group.objects.filter(head_group=igroup9)
                                        for igroup10 in igroups:
                                            ledgers = LedgerAccount.objects.filter(head_group=igroup10)
                                            if len(ledgers) > 0:
                                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                                total = sum(account_log_dr_list)
                                                igroup2_total += total
            igroup1_total += igroup2_total
            incomes_dict[igroup2.name] = igroup2_total
        incomes_total += igroup1_total
        response_dict['incomes']['incomes_total'] = incomes_total
        response_dict['incomes'][igroup1.name] = incomes_dict
        response_dict['incomes'][igroup1.name]['total'] = igroup1_total


    groups_under_pg_liabilities = Group.objects.filter(head_primarygroup__name='Liabilities')
    print('groups_under_pg_liabilities: ', groups_under_pg_liabilities)

    liabilities_total = 0

    # ledger_accounts_under_pg_liabilities = LedgerAccount.objects.filter(head_primarygroup__name='Liabilities')
    # if len(ledger_accounts_under_pg_liabilities) > 0:
    #     account_log_dr_list = AccountLog.objects.filter(ledger__in=ledger_accounts_under_pg_liabilities).values_list('debit_amount', flat=True)
    #     total = sum(account_log_dr_list)
    #     liabilities_total += total

    for lgroup1 in groups_under_pg_liabilities:
        liabilities_dict = {}
        lgroup1_total = 0
        ledgers = LedgerAccount.objects.filter(head_group=lgroup1)
        if len(ledgers) > 0:
            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
            total = sum(account_log_dr_list)
            lgroup1_total += total
        lgroups = Group.objects.filter(head_group=lgroup1)
        for lgroup2 in lgroups:
            lgroup2_total = 0
            ledgers = LedgerAccount.objects.filter(head_group=lgroup2)
            if len(ledgers) > 0:
                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                total = sum(account_log_dr_list)
                lgroup2_total += total
            lgroups = Group.objects.filter(head_group=lgroup2)
            for lgroup3 in lgroups:
                ledgers = LedgerAccount.objects.filter(head_group=lgroup3)
                if len(ledgers) > 0:
                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                    total = sum(account_log_dr_list)
                    lgroup2_total += total
                lgroups = Group.objects.filter(head_group=lgroup2)
                for lgroup4 in lgroups:
                    ledgers = LedgerAccount.objects.filter(head_group=lgroup4)
                    if len(ledgers) > 0:
                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                        total = sum(account_log_dr_list)
                        lgroup2_total += total
                    lgroups = Group.objects.filter(head_group=lgroup4)
                    for lgroup5 in lgroups:
                        ledgers = LedgerAccount.objects.filter(head_group=lgroup5)
                        if len(ledgers) > 0:
                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                            total = sum(account_log_dr_list)
                            lgroup2_total += total
                        lgroups = Group.objects.filter(head_group=lgroup5)
                        for lgroup6 in lgroups:
                            ledgers = LedgerAccount.objects.filter(head_group=lgroup6)
                            if len(ledgers) > 0:
                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledger, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                total = sum(account_log_dr_list)
                                lgroup2_total += total
                            lgroups = Group.objects.filter(head_group=lgroup6)
                            for lgroup7 in lgroups:
                                ledgers = LedgerAccount.objects.filter(head_group=lgroup7)
                                if len(ledgers) > 0:
                                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                    total = sum(account_log_dr_list)
                                    lgroup2_total += total
                                lgroups = Group.objects.filter(head_group=lgroup7)
                                for lgroup8 in lgroups:
                                    ledgers = LedgerAccount.objects.filter(head_group=lgroup8)
                                    if len(ledgers) > 0:
                                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                        total = sum(account_log_dr_list)
                                        lgroup2_total += total
                                    lgroups = Group.objects.filter(head_group=lgroup8)
                                    for lgroup9 in lgroups:
                                        ledgers = LedgerAccount.objects.filter(head_group=lgroup9)
                                        if len(ledgers) > 0:
                                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                            total = sum(account_log_dr_list)
                                            lgroup2_total += total
                                        lgroups = Group.objects.filter(head_group=lgroup9)
                                        for lgroup10 in lgroups:
                                            ledgers = LedgerAccount.objects.filter(head_group=lgroup10)
                                            if len(ledgers) > 0:
                                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                                total = sum(account_log_dr_list)
                                                lgroup2_total += total
            lgroup1_total += lgroup2_total
            liabilities_dict[lgroup2.name] = lgroup2_total
        liabilities_total += lgroup1_total
        response_dict['liabilities']['liabilities_total'] = liabilities_total
        response_dict['liabilities'][lgroup1.name] = liabilities_dict
        response_dict['liabilities'][lgroup1.name]['total'] = lgroup1_total


    total_assets = response_dict['assets']['assets_total']
    total_expenses = response_dict['expenses']['expenses_total']
    total_incomes = response_dict['incomes']['incomes_total']
    total_liabilities = response_dict['liabilities']['liabilities_total']

    total_debit_amount = total_assets + total_expenses
    total_credit_amount = total_incomes + total_liabilities

    response_dict['total_debit_amount'] = total_debit_amount
    response_dict['total_credit_amount'] = total_credit_amount

    response = {
        'trial_balance': response_dict,
    }

    return Response(response, status=status.HTTP_200_OK)




@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=AccountLogListSerializer,
	responses=AccountLogListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getProfitLoss(request):
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    date_range = (start_date, end_date)
    print('start_date: ', start_date)
    print('end_date: ', end_date)
    print('date_range: ', date_range)

    response_dict = {'debit_side': {'inner': {} }, 'credit_side': {'inner': {} }}

    purchase_accounts_group = Group.objects.filter(name='Purchase Accounts')
    direct_expenses_group = Group.objects.filter(name='Direct Expenses')
    indirect_expenses_group = Group.objects.filter(name='Indirect Expenses')
    sales_accounts_group = Group.objects.filter(name='Sales Accounts')
    direct_incomes_group = Group.objects.filter(name='Direct Incomes')
    indirect_incomes_group = Group.objects.filter(name='Indirect Incomes')

    purchase_accounts_total = 0
    for pagroup1 in purchase_accounts_group:
        ledgers = LedgerAccount.objects.filter(head_group=pagroup1)
        if len(ledgers) > 0:
            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
            total = sum(account_log_dr_list)
            purchase_accounts_total += total
        pagroups = Group.objects.filter(head_group=pagroup1)
        for pagroup2 in pagroups:
            ledgers = LedgerAccount.objects.filter(head_group=pagroup2)
            if len(ledgers) > 0:
                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                total = sum(account_log_dr_list)
                purchase_accounts_total += total
            pagroups = Group.objects.filter(head_group=pagroup2)
            for pagroup3 in pagroups:
                ledgers = LedgerAccount.objects.filter(head_group=pagroup3)
                if len(ledgers) > 0:
                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                    total = sum(account_log_dr_list)
                    purchase_accounts_total += total
                pagroups = Group.objects.filter(head_group=pagroup3)
                for pagroup4 in pagroups:
                    ledgers = LedgerAccount.objects.filter(head_group=pagroup4)
                    if len(ledgers) > 0:
                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                        total = sum(account_log_dr_list)
                        purchase_accounts_total += total
                    pagroups = Group.objects.filter(head_group=pagroup4)
                    for pagroup5 in pagroups:
                        ledgers = LedgerAccount.objects.filter(head_group=pagroup5)
                        if len(ledgers) > 0:
                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                            total = sum(account_log_dr_list)
                            purchase_accounts_total += total
                        pagroups = Group.objects.filter(head_group=pagroup5)
                        for pagroup6 in pagroups:
                            ledgers = LedgerAccount.objects.filter(head_group=pagroup6)
                            if len(ledgers) > 0:
                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                total = sum(account_log_dr_list)
                                purchase_accounts_total += total
                            pagroups = Group.objects.filter(head_group=pagroup6)
                            for pagroup7 in pagroups:
                                ledgers = LedgerAccount.objects.filter(head_group=pagroup7)
                                if len(ledgers) > 0:
                                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                    total = sum(account_log_dr_list)
                                    purchase_accounts_total += total
                                pagroups = Group.objects.filter(head_group=pagroup7)
                                for pagroup8 in pagroups:
                                    ledgers = LedgerAccount.objects.filter(head_group=pagroup8)
                                    if len(ledgers) > 0:
                                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                        total = sum(account_log_dr_list)
                                        purchase_accounts_total += total
                                    for pagroup9 in pagroups:
                                        ledgers = LedgerAccount.objects.filter(head_group=pagroup9)
                                        if len(ledgers) > 0:
                                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                            total = sum(account_log_dr_list)
                                            purchase_accounts_total += total

    response_dict['debit_side']['purchase_accounts'] = purchase_accounts_total


    direct_expenses_total = 0
    for degroup1 in direct_expenses_group:
        ledgers = LedgerAccount.objects.filter(head_group=degroup1)
        if len(ledgers) > 0:
            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
            total = sum(account_log_dr_list)
            direct_expenses_total += total
        degroups = Group.objects.filter(head_group=degroup1)
        for degroup2 in degroups:
            ledgers = LedgerAccount.objects.filter(head_group=degroup2)
            if len(ledgers) > 0:
                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                total = sum(account_log_dr_list)
                direct_expenses_total += total
            degroups = Group.objects.filter(head_group=degroup2)
            for degroup3 in degroups:
                ledgers = LedgerAccount.objects.filter(head_group=degroup3)
                if len(ledgers) > 0:
                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                    total = sum(account_log_dr_list)
                    direct_expenses_total += total
                degroups = Group.objects.filter(head_group=degroup3)
                for degroup4 in degroups:
                    ledgers = LedgerAccount.objects.filter(head_group=degroup4)
                    if len(ledgers) > 0:
                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                        total = sum(account_log_dr_list)
                        direct_expenses_total += total
                    degroups = Group.objects.filter(head_group=degroup4)
                    for degroup5 in degroups:
                        ledgers = LedgerAccount.objects.filter(head_group=degroup5)
                        if len(ledgers) > 0:
                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                            total = sum(account_log_dr_list)
                            direct_expenses_total += total
                        degroups = Group.objects.filter(head_group=degroup5)
                        for degroup6 in degroups:
                            ledgers = LedgerAccount.objects.filter(head_group=degroup6)
                            if len(ledgers) > 0:
                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                total = sum(account_log_dr_list)
                                direct_expenses_total += total
                            degroups = Group.objects.filter(head_group=degroup6)
                            for degroup7 in degroups:
                                ledgers = LedgerAccount.objects.filter(head_group=degroup7)
                                if len(ledgers) > 0:
                                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                    total = sum(account_log_dr_list)
                                    direct_expenses_total += total
                                degroups = Group.objects.filter(head_group=degroup7)
                                for degroup8 in degroups:
                                    ledgers = LedgerAccount.objects.filter(head_group=degroup8)
                                    if len(ledgers) > 0:
                                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                        total = sum(account_log_dr_list)
                                        direct_expenses_total += total
                                    for degroup9 in degroups:
                                        ledgers = LedgerAccount.objects.filter(head_group=degroup9)
                                        if len(ledgers) > 0:
                                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                            total = sum(account_log_dr_list)
                                            direct_expenses_total += total

    response_dict['debit_side']['direct_expenses'] = direct_expenses_total


    indirect_expenses_total = 0
    for iegroup1 in indirect_expenses_group:
        ledgers = LedgerAccount.objects.filter(head_group=iegroup1)
        if len(ledgers) > 0:
            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
            total = sum(account_log_dr_list)
            indirect_expenses_total += total
        iegroups = Group.objects.filter(head_group=iegroup1)
        for iegroup2 in iegroups:
            ledgers = LedgerAccount.objects.filter(head_group=iegroup2)
            if len(ledgers) > 0:
                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                total = sum(account_log_dr_list)
                indirect_expenses_total += total
            iegroups = Group.objects.filter(head_group=iegroup2)
            for iegroup3 in iegroups:
                ledgers = LedgerAccount.objects.filter(head_group=iegroup3)
                if len(ledgers) > 0:
                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                    total = sum(account_log_dr_list)
                    indirect_expenses_total += total
                iegroups = Group.objects.filter(head_group=iegroup3)
                for iegroup4 in iegroups:
                    ledgers = LedgerAccount.objects.filter(head_group=iegroup4)
                    if len(ledgers) > 0:
                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                        total = sum(account_log_dr_list)
                        indirect_expenses_total += total
                    iegroups = Group.objects.filter(head_group=iegroup4)
                    for iegroup5 in iegroups:
                        ledgers = LedgerAccount.objects.filter(head_group=iegroup5)
                        if len(ledgers) > 0:
                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                            total = sum(account_log_dr_list)
                            indirect_expenses_total += total
                        iegroups = Group.objects.filter(head_group=iegroup5)
                        for iegroup6 in iegroups:
                            ledgers = LedgerAccount.objects.filter(head_group=iegroup6)
                            if len(ledgers) > 0:
                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                total = sum(account_log_dr_list)
                                indirect_expenses_total += total
                            iegroups = Group.objects.filter(head_group=iegroup6)
                            for iegroup7 in iegroups:
                                ledgers = LedgerAccount.objects.filter(head_group=iegroup7)
                                if len(ledgers) > 0:
                                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                    total = sum(account_log_dr_list)
                                    indirect_expenses_total += total
                                iegroups = Group.objects.filter(head_group=iegroup7)
                                for iegroup8 in iegroups:
                                    ledgers = LedgerAccount.objects.filter(head_group=iegroup8)
                                    if len(ledgers) > 0:
                                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                        total = sum(account_log_dr_list)
                                        indirect_expenses_total += total
                                    iegroups = Group.objects.filter(head_group=iegroup8)
                                    for iegroup9 in iegroups:
                                        ledgers = LedgerAccount.objects.filter(head_group=iegroup9)
                                        if len(ledgers) > 0:
                                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                            total = sum(account_log_dr_list)
                                            indirect_expenses_total += total

    response_dict['debit_side']['inner']['indirect_expenses'] = indirect_expenses_total


    sales_accounts_total = 0
    for sagroup1 in sales_accounts_group:
        ledgers = LedgerAccount.objects.filter(head_group=sagroup1)
        if len(ledgers) > 0:
            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
            total = sum(account_log_dr_list)
            sales_accounts_total += total
        sagroups = Group.objects.filter(head_group=sagroup1)
        for sagroup2 in sagroups:
            ledgers = LedgerAccount.objects.filter(head_group=sagroup2)
            if len(ledgers) > 0:
                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                total = sum(account_log_dr_list)
                sales_accounts_total += total
            sagroups = Group.objects.filter(head_group=sagroup2)
            for sagroup3 in sagroups:
                ledgers = LedgerAccount.objects.filter(head_group=sagroup3)
                if len(ledgers) > 0:
                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                    total = sum(account_log_dr_list)
                    sales_accounts_total += total
                sagroups = Group.objects.filter(head_group=sagroup3)
                for sagroup4 in sagroups:
                    ledgers = LedgerAccount.objects.filter(head_group=sagroup4)
                    if len(ledgers) > 0:
                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                        total = sum(account_log_dr_list)
                        sales_accounts_total += total
                    sagroups = Group.objects.filter(head_group=sagroup4)
                    for sagroup5 in sagroups:
                        ledgers = LedgerAccount.objects.filter(head_group=sagroup5)
                        if len(ledgers) > 0:
                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                            total = sum(account_log_dr_list)
                            sales_accounts_total += total
                        sagroups = Group.objects.filter(head_group=sagroup5)
                        for sagroup6 in sagroups:
                            ledgers = LedgerAccount.objects.filter(head_group=sagroup6)
                            if len(ledgers) > 0:
                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                                total = sum(account_log_dr_list)
                                sales_accounts_total += total
                            sagroups = Group.objects.filter(head_group=sagroup6)
                            for sagroup7 in sagroups:
                                ledgers = LedgerAccount.objects.filter(head_group=sagroup7)
                                if len(ledgers) > 0:
                                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                                    total = sum(account_log_dr_list)
                                    sales_accounts_total += total
                                sagroups = Group.objects.filter(head_group=sagroup7)
                                for sagroup8 in sagroups:
                                    ledgers = LedgerAccount.objects.filter(head_group=sagroup8)
                                    if len(ledgers) > 0:
                                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                                        total = sum(account_log_dr_list)
                                        sales_accounts_total += total
                                    for sagroup9 in sagroups:
                                        ledgers = LedgerAccount.objects.filter(head_group=sagroup9)
                                        if len(ledgers) > 0:
                                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                                            total = sum(account_log_dr_list)
                                            sales_accounts_total += total

    response_dict['credit_side']['sales_accounts'] = sales_accounts_total


    direct_incomes_total = 0
    for digroup1 in direct_incomes_group:
        ledgers = LedgerAccount.objects.filter(head_group=digroup1)
        if len(ledgers) > 0:
            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
            total = sum(account_log_dr_list)
            direct_incomes_total += total
        digroups = Group.objects.filter(head_group=digroup1)
        for digroup2 in digroups:
            ledgers = LedgerAccount.objects.filter(head_group=digroup2)
            if len(ledgers) > 0:
                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                total = sum(account_log_dr_list)
                direct_incomes_total += total
            digroups = Group.objects.filter(head_group=digroup2)
            for digroup3 in digroups:
                ledgers = LedgerAccount.objects.filter(head_group=digroup3)
                if len(ledgers) > 0:
                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                    total = sum(account_log_dr_list)
                    direct_incomes_total += total
                digroups = Group.objects.filter(head_group=digroup3)
                for digroup4 in digroups:
                    ledgers = LedgerAccount.objects.filter(head_group=digroup4)
                    if len(ledgers) > 0:
                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                        total = sum(account_log_dr_list)
                        direct_incomes_total += total
                    digroups = Group.objects.filter(head_group=digroup4)
                    for digroup5 in digroups:
                        ledgers = LedgerAccount.objects.filter(head_group=digroup5)
                        if len(ledgers) > 0:
                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                            total = sum(account_log_dr_list)
                            direct_incomes_total += total
                        digroups = Group.objects.filter(head_group=digroup5)
                        for digroup6 in digroups:
                            ledgers = LedgerAccount.objects.filter(head_group=digroup6)
                            if len(ledgers) > 0:
                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                                total = sum(account_log_dr_list)
                                direct_incomes_total += total
                            digroups = Group.objects.filter(head_group=digroup6)
                            for digroup7 in digroups:
                                ledgers = LedgerAccount.objects.filter(head_group=digroup7)
                                if len(ledgers) > 0:
                                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                                    total = sum(account_log_dr_list)
                                    direct_incomes_total += total
                                digroups = Group.objects.filter(head_group=digroup7)
                                for digroup8 in digroups:
                                    ledgers = LedgerAccount.objects.filter(head_group=digroup8)
                                    if len(ledgers) > 0:
                                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                                        total = sum(account_log_dr_list)
                                        direct_incomes_total += total
                                    for digroup9 in digroups:
                                        ledgers = LedgerAccount.objects.filter(head_group=digroup9)
                                        if len(ledgers) > 0:
                                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                                            total = sum(account_log_dr_list)
                                            direct_incomes_total += total

    response_dict['credit_side']['direct_incomes'] = direct_incomes_total


    indirect_incomes_total = 0
    for iigroup1 in indirect_incomes_group:
        ledgers = LedgerAccount.objects.filter(head_group=iigroup1)
        if len(ledgers) > 0:
            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
            total = sum(account_log_dr_list)
            indirect_incomes_total += total
        iigroups = Group.objects.filter(head_group=iigroup1)
        for iigroup2 in iigroups:
            ledgers = LedgerAccount.objects.filter(head_group=iigroup2)
            if len(ledgers) > 0:
                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                total = sum(account_log_dr_list)
                indirect_incomes_total += total
            iigroups = Group.objects.filter(head_group=iigroup2)
            for iigroup3 in iigroups:
                ledgers = LedgerAccount.objects.filter(head_group=iigroup3)
                if len(ledgers) > 0:
                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                    total = sum(account_log_dr_list)
                    indirect_incomes_total += total
                iigroups = Group.objects.filter(head_group=iigroup3)
                for iigroup4 in iigroups:
                    ledgers = LedgerAccount.objects.filter(head_group=iigroup4)
                    if len(ledgers) > 0:
                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                        total = sum(account_log_dr_list)
                        indirect_incomes_total += total
                    iigroups = Group.objects.filter(head_group=iigroup4)
                    for iigroup5 in iigroups:
                        ledgers = LedgerAccount.objects.filter(head_group=iigroup5)
                        if len(ledgers) > 0:
                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                            total = sum(account_log_dr_list)
                            indirect_incomes_total += total
                        iigroups = Group.objects.filter(head_group=iigroup5)
                        for iigroup6 in iigroups:
                            ledgers = LedgerAccount.objects.filter(head_group=iigroup6)
                            if len(ledgers) > 0:
                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                                total = sum(account_log_dr_list)
                                indirect_incomes_total += total
                            iigroups = Group.objects.filter(head_group=iigroup6)
                            for iigroup7 in iigroups:
                                ledgers = LedgerAccount.objects.filter(head_group=iigroup7)
                                if len(ledgers) > 0:
                                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                                    total = sum(account_log_dr_list)
                                    indirect_incomes_total += total
                                iigroups = Group.objects.filter(head_group=iigroup7)
                                for iigroup8 in iigroups:
                                    ledgers = LedgerAccount.objects.filter(head_group=iigroup8)
                                    if len(ledgers) > 0:
                                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                                        total = sum(account_log_dr_list)
                                        indirect_incomes_total += total
                                    for iigroup9 in iigroups:
                                        ledgers = LedgerAccount.objects.filter(head_group=iigroup9)
                                        if len(ledgers) > 0:
                                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('credit_amount', flat=True)
                                            total = sum(account_log_dr_list)
                                            indirect_incomes_total += total

    response_dict['credit_side']['inner']['indirect_incomes'] = indirect_incomes_total

    debit_side_outer_total = response_dict['debit_side']['purchase_accounts'] + response_dict['debit_side']['direct_expenses']
    credit_side_outer_total = response_dict['credit_side']['sales_accounts'] + response_dict['credit_side']['direct_incomes']

    print('debit_side_outer_total: ', debit_side_outer_total)
    print('credit_side_outer_total: ', credit_side_outer_total)

    gross_profit_loss_amount = credit_side_outer_total - debit_side_outer_total

    if credit_side_outer_total > debit_side_outer_total:
        response_dict['debit_side']['gross_profit_cf'] = gross_profit_loss_amount
        response_dict['credit_side']['inner']['gross_profit_bf'] = gross_profit_loss_amount 
    elif credit_side_outer_total < debit_side_outer_total:
        response_dict['credit_side']['gross_loss_cf'] = (-1 * gross_profit_loss_amount)
        response_dict['debit_side']['inner']['gross_loss_bf'] = (-1 * gross_profit_loss_amount)

    debit_inner_items = (response_dict['debit_side']['inner']).items()
    credit_inner_items = (response_dict['credit_side']['inner']).items()

    debit_inner_total = 0
    credit_inner_total = 0
    for k, v in debit_inner_items:
        debit_inner_total += v
    for k, v in credit_inner_items:
        credit_inner_total += v

    print('debit_inner_total: ', debit_inner_total)
    print('credit_inner_total: ', credit_inner_total)
    
    net_profit_loss_amount = credit_inner_total - debit_inner_total

    if credit_inner_total > debit_inner_total:
        response_dict['debit_side']['inner']['net_profit'] = net_profit_loss_amount
    elif credit_inner_total < debit_inner_total:
        response_dict['credit_side']['inner']['net_loss'] = (-1 * net_profit_loss_amount)
        

    return Response(response_dict)




@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=AccountLogListSerializer,
	responses=AccountLogListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ORDER_STATUS_LIST.name])
def getBalanceSheet(request):
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    date_range = (start_date, end_date)
    print('start_date: ', start_date)
    print('end_date: ', end_date)
    print('date_range: ', date_range)

    response_dict = {'liabilities': {}, 'assets': {} }
    groups_under_pg_assets = Group.objects.filter(head_primarygroup__name='Assets')
    print('groups_under_pg_assets: ', groups_under_pg_assets)
    assets_total = 0

    for agroup1 in groups_under_pg_assets:
        assets_dict = {}
        agroup1_total = 0
        ledgers = LedgerAccount.objects.filter(head_group=agroup1)
        if len(ledgers) > 0:
            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
            total = sum(account_log_dr_list)
            agroup1_total += total
        agroups = Group.objects.filter(head_group=agroup1)
        for agroup2 in agroups:
            agroup2_total = 0
            ledgers = LedgerAccount.objects.filter(head_group=agroup2)
            if len(ledgers) > 0:
                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                total = sum(account_log_dr_list)
                agroup2_total += total
            agroups = Group.objects.filter(head_group=agroup2)
            for agroup3 in agroups:
                ledgers = LedgerAccount.objects.filter(head_group=agroup3)
                if len(ledgers) > 0:
                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                    total = sum(account_log_dr_list)
                    agroup2_total += total
                agroups = Group.objects.filter(head_group=agroup2)
                for agroup4 in agroups:
                    ledgers = LedgerAccount.objects.filter(head_group=agroup4)
                    if len(ledgers) > 0:
                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                        total = sum(account_log_dr_list)
                        agroup2_total += total
                    agroups = Group.objects.filter(head_group=agroup4)
                    for agroup5 in agroups:
                        ledgers = LedgerAccount.objects.filter(head_group=agroup5)
                        if len(ledgers) > 0:
                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                            total = sum(account_log_dr_list)
                            agroup2_total += total
                        agroups = Group.objects.filter(head_group=agroup5)
                        for agroup6 in agroups:
                            ledgers = LedgerAccount.objects.filter(head_group=agroup6)
                            if len(ledgers) > 0:
                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                total = sum(account_log_dr_list)
                                agroup2_total += total
                            agroups = Group.objects.filter(head_group=agroup6)
                            for agroup7 in agroups:
                                ledgers = LedgerAccount.objects.filter(head_group=agroup7)
                                if len(ledgers) > 0:
                                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                    total = sum(account_log_dr_list)
                                    agroup2_total += total
                                agroups = Group.objects.filter(head_group=agroup7)
                                for agroup8 in agroups:
                                    ledgers = LedgerAccount.objects.filter(head_group=agroup8)
                                    if len(ledgers) > 0:
                                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                        total = sum(account_log_dr_list)
                                        agroup2_total += total
                                    agroups = Group.objects.filter(head_group=agroup8)
                                    for agroup9 in agroups:
                                        ledgers = LedgerAccount.objects.filter(head_group=agroup9)
                                        if len(ledgers) > 0:
                                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                            total = sum(account_log_dr_list)
                                            agroup2_total += total
                                        agroups = Group.objects.filter(head_group=agroup9)
                                        for agroup10 in agroups:
                                            ledgers = LedgerAccount.objects.filter(head_group=agroup10)
                                            if len(ledgers) > 0:
                                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                                total = sum(account_log_dr_list)
                                                agroup2_total += total
            agroup1_total += agroup2_total
            assets_dict[agroup2.name] = agroup2_total
        assets_total += agroup1_total
        response_dict['assets']['assets_total'] = assets_total
        response_dict['assets'][agroup1.name] = assets_dict
        response_dict['assets'][agroup1.name]['total'] = agroup1_total


    groups_under_pg_liabilities = Group.objects.filter(head_primarygroup__name='Liabilities')
    print('groups_under_pg_liabilities: ', groups_under_pg_liabilities)

    liabilities_total = 0

    # ledger_accounts_under_pg_liabilities = LedgerAccount.objects.filter(head_primarygroup__name='Liabilities')
    # if len(ledger_accounts_under_pg_liabilities) > 0:
    #     account_log_dr_list = AccountLog.objects.filter(ledger__in=ledger_accounts_under_pg_liabilities).values_list('debit_amount', flat=True)
    #     total = sum(account_log_dr_list)
    #     liabilities_total += total

    for lgroup1 in groups_under_pg_liabilities:
        liabilities_dict = {}
        lgroup1_total = 0
        ledgers = LedgerAccount.objects.filter(head_group=lgroup1)
        if len(ledgers) > 0:
            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
            total = sum(account_log_dr_list)
            lgroup1_total += total
        lgroups = Group.objects.filter(head_group=lgroup1)
        for lgroup2 in lgroups:
            lgroup2_total = 0
            ledgers = LedgerAccount.objects.filter(head_group=lgroup2)
            if len(ledgers) > 0:
                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                total = sum(account_log_dr_list)
                lgroup2_total += total
            lgroups = Group.objects.filter(head_group=lgroup2)
            for lgroup3 in lgroups:
                ledgers = LedgerAccount.objects.filter(head_group=lgroup3)
                if len(ledgers) > 0:
                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                    total = sum(account_log_dr_list)
                    lgroup2_total += total
                lgroups = Group.objects.filter(head_group=lgroup2)
                for lgroup4 in lgroups:
                    ledgers = LedgerAccount.objects.filter(head_group=lgroup4)
                    if len(ledgers) > 0:
                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                        total = sum(account_log_dr_list)
                        lgroup2_total += total
                    lgroups = Group.objects.filter(head_group=lgroup4)
                    for lgroup5 in lgroups:
                        ledgers = LedgerAccount.objects.filter(head_group=lgroup5)
                        if len(ledgers) > 0:
                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                            total = sum(account_log_dr_list)
                            lgroup2_total += total
                        lgroups = Group.objects.filter(head_group=lgroup5)
                        for lgroup6 in lgroups:
                            ledgers = LedgerAccount.objects.filter(head_group=lgroup6)
                            if len(ledgers) > 0:
                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                total = sum(account_log_dr_list)
                                lgroup2_total += total
                            lgroups = Group.objects.filter(head_group=lgroup6)
                            for lgroup7 in lgroups:
                                ledgers = LedgerAccount.objects.filter(head_group=lgroup7)
                                if len(ledgers) > 0:
                                    account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                    total = sum(account_log_dr_list)
                                    lgroup2_total += total
                                lgroups = Group.objects.filter(head_group=lgroup7)
                                for lgroup8 in lgroups:
                                    ledgers = LedgerAccount.objects.filter(head_group=lgroup8)
                                    if len(ledgers) > 0:
                                        account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                        total = sum(account_log_dr_list)
                                        lgroup2_total += total
                                    lgroups = Group.objects.filter(head_group=lgroup8)
                                    for lgroup9 in lgroups:
                                        ledgers = LedgerAccount.objects.filter(head_group=lgroup9)
                                        if len(ledgers) > 0:
                                            account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                            total = sum(account_log_dr_list)
                                            lgroup2_total += total
                                        lgroups = Group.objects.filter(head_group=lgroup9)
                                        for lgroup10 in lgroups:
                                            ledgers = LedgerAccount.objects.filter(head_group=lgroup10)
                                            if len(ledgers) > 0:
                                                account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers, log_date__date__range=date_range).values_list('debit_amount', flat=True)
                                                total = sum(account_log_dr_list)
                                                lgroup2_total += total
            lgroup1_total += lgroup2_total
            liabilities_dict[lgroup2.name] = lgroup2_total
        liabilities_total += lgroup1_total
        response_dict['liabilities']['liabilities_total'] = liabilities_total
        response_dict['liabilities'][lgroup1.name] = liabilities_dict
        response_dict['liabilities'][lgroup1.name]['total'] = lgroup1_total
    
    total_assets = response_dict['assets']['assets_total']
    total_liabilities = response_dict['liabilities']['liabilities_total']
    profit_loss_amt = total_assets - total_liabilities

    if total_assets > total_liabilities:
        response_dict['liabilities']['profit_loss_ac'] = {'current_period': profit_loss_amt }
    elif total_assets < total_liabilities:
        response_dict['assets']['profit_loss_ac'] = {'current_period': (-1 * profit_loss_amt) }

    return Response(response_dict)
