from django_filters import rest_framework as filters

from account.models import *


class PrimaryGroupFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = PrimaryGroup
        fields = ['name',]


class GroupFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = Group
        fields = ['name',]


class LedgerAccountFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = LedgerAccount
        fields = ['name', ]


class SubLedgerAccountFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = SubLedgerAccount
        fields = ['name', ]


class PaymentVoucherFilter(filters.FilterSet):
    ledger = filters.NumberFilter(field_name="ledger", lookup_expr='exact')
    sub_ledger = filters.NumberFilter(
        field_name="sub_ledger", lookup_expr='exact')
    branch = filters.NumberFilter(field_name="branch", lookup_expr='exact')
    invoice_no = filters.CharFilter(
        field_name="invoice_no", lookup_expr='icontains')
    date_after = filters.DateFilter(
        field_name='payment_date', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='payment_date', lookup_expr='lte')

    class Meta:
        model = PaymentVoucher
        fields = ['ledger', 'sub_ledger', 'branch',
                  'invoice_no', 'date_after', 'date_before']


class ReceiptVoucherFilter(filters.FilterSet):
    ledger = filters.NumberFilter(field_name="ledger", lookup_expr='exact')
    sub_ledger = filters.NumberFilter(
        field_name="sub_ledger", lookup_expr='exact')
    branch = filters.NumberFilter(field_name="branch", lookup_expr='exact')
    invoice_no = filters.CharFilter(
        field_name="invoice_no", lookup_expr='icontains')
    date_after = filters.DateFilter(
        field_name='receipt_date', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='receipt_date', lookup_expr='lte')

    class Meta:
        model = ReceiptVoucher
        fields = ['ledger', 'sub_ledger', 'branch',
                  'invoice_no', 'date_after', 'date_before']


class SalesFilter(filters.FilterSet):
    sub_ledger = filters.NumberFilter(
        field_name="sub_ledger", lookup_expr='exact')
    branch = filters.NumberFilter(field_name="branch", lookup_expr='exact')
    invoice_no = filters.CharFilter(
        field_name="invoice_no", lookup_expr='icontains')
    date_after = filters.DateFilter(field_name='sales_date', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='sales_date', lookup_expr='lte')

    class Meta:
        model = Sales
        fields = ['sub_ledger', 'branch',
                  'invoice_no', 'date_after', 'date_before']


class PurchaseFilter(filters.FilterSet):
    sub_ledger = filters.NumberFilter(
        field_name="sub_ledger", lookup_expr='exact')
    branch = filters.NumberFilter(field_name="branch", lookup_expr='exact')
    invoice_no = filters.CharFilter(
        field_name="invoice_no", lookup_expr='icontains')
    date_after = filters.DateFilter(
        field_name='purchase_date', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='purchase_date', lookup_expr='lte')

    class Meta:
        model = Purchase
        fields = ['sub_ledger', 'branch',
                  'invoice_no', 'date_after', 'date_before']


class ContraFilter(filters.FilterSet):
    ledger = filters.NumberFilter(field_name="ledger", lookup_expr='exact')
    invoice_no = filters.CharFilter(
        field_name="invoice_no", lookup_expr='icontains')
    date_after = filters.DateFilter(
        field_name='purchase_date', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='purchase_date', lookup_expr='lte')

    class Meta:
        model = Contra
        fields = ['ledger', 'invoice_no', 'date_after', 'date_before']


class JournalFilter(filters.FilterSet):
    invoice_no = filters.CharFilter(
        field_name="invoice_no", lookup_expr='icontains')

    class Meta:
        model = Journal
        fields = ['invoice_no',]


class IDJournalFilter(filters.FilterSet):
    invoice_no = filters.CharFilter(
        field_name="invoice_no", lookup_expr='icontains')

    class Meta:
        model = IDJournal
        fields = ['invoice_no',]


class AccountLogFilter(filters.FilterSet):
    reference_no = filters.CharFilter(
        field_name="reference_no", lookup_expr='exact')
    date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = AccountLog
        fields = ['reference_no', 'date_after', 'date_before',]


class AccountLogFilterForDateAndSubLedgerOnly(filters.FilterSet):
    sub_ledger = filters.NumberFilter(
        field_name='sub_ledger__id', lookup_expr='exact')
    date_after = filters.DateFilter(
        field_name='log_date__date', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='log_date__date', lookup_expr='lte')

    class Meta:
        model = AccountLog
        fields = ['sub_ledger', 'date_after', 'date_before',]


class AccountLogFilterGeneral(filters.FilterSet):
    ledger = filters.NumberFilter(field_name="ledger", lookup_expr='exact')
    sub_ledger = filters.NumberFilter(
        field_name="sub_ledger", lookup_expr='exact')
    date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = AccountLog
        fields = ['ledger', 'sub_ledger', 'date_after', 'date_before',]


class AccountLogFilterForCashLedger(filters.FilterSet):
    ledger = filters.NumberFilter(field_name="ledger", lookup_expr='exact')
    date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = AccountLog
        fields = ['ledger', 'date_after', 'date_before',]


class AccountLogFilterForBankAccountGroup(filters.FilterSet):
    reference_no = filters.CharFilter(
        field_name="reference_no", lookup_expr='exact')
    date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = AccountLog
        fields = ['reference_no', 'date_after', 'date_before',]


class AccountLogFilterForPersonOrCompanyLedger(filters.FilterSet):
    ledger = filters.NumberFilter(field_name='ledger', lookup_expr='exact')
    reference_no = filters.CharFilter(
        field_name="reference_no", lookup_expr='exact')
    date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = AccountLog
        fields = ['ledger', 'reference_no', 'date_after', 'date_before',]


class AccountLogFilterForPassenger(filters.FilterSet):
    passenger = filters.NumberFilter(
        field_name='passenger', lookup_expr='exact')
    date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = AccountLog
        fields = ['passenger', 'date_after', 'date_before',]


class AccountLogFilterForSubLedger(filters.FilterSet):
    sub_ledger = filters.NumberFilter(
        field_name='sub_ledger', lookup_expr='exact')
    date_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = filters.DateFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = AccountLog
        fields = ['sub_ledger', 'date_after', 'date_before',]
