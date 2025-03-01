import re
from statistics import mode

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.db import models
from django.conf import settings

from rest_framework.serializers import BaseSerializer

from authentication.models import Branch


# Create your models here.

class PrimaryGroup(models.Model):
    name = models.CharField(max_length=100)

    is_deletable = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'PrimaryGroups'
        ordering = ['-id', ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     if self.is_deletable == False:
    #         raise ValidationError("Primary group is not deletable!")
    #     else:
    #         super().delete(*args, **kwargs)


class Group(models.Model):
    name = models.CharField(max_length=200)

    head_group = models.ForeignKey('self', on_delete=models.RESTRICT, null=True, blank=True, related_name='children')
    head_primarygroup = models.ForeignKey(PrimaryGroup, on_delete=models.RESTRICT, null=True, blank=True)

    is_deletable = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        ordering = ['-id', ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        if not self.head_group and not self.head_primarygroup:
            raise ValidationError('Must provide either head_group_self or head_group_primarygroup.')
        if self.head_group and self.head_primarygroup:
            raise ValidationError('Select head_group_self or head_group_primarygroup, but not both.')
        super().save(*args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     if self.is_deletable == False:
    #         raise ValidationError("This group is not deletable!")
    #     else:
    #         super().delete(*args, **kwargs)


class LedgerAccount(models.Model):
    name = models.CharField(max_length=100)

    ledger_type = models.CharField(max_length=30, null=True, blank=True)
    reference_id = models.CharField(max_length=255, null=True, blank=True)

    head_group = models.ForeignKey(Group, on_delete=models.RESTRICT, null=True, blank=True)
    head_primarygroup = models.ForeignKey(PrimaryGroup, on_delete=models.RESTRICT, null=True, blank=True)

    is_deletable = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'LedgerAccounts'
        ordering = ['-id', ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        if self.ledger_type:
            self.ledger_type = self.ledger_type.replace(' ', '_').lower()
        super().save(*args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     if self.is_deletable == False:
    #         raise ValidationError("This ledger account is not deletable!")
    #     else:
    #         super().delete(*args, **kwargs)


class SubLedgerAccount(models.Model):
    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'SubLedgerAccounts'
        ordering = ['-id', ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.replace(' ', '_').lower()
        super().save(*args, **kwargs)


class PaymentVoucher(models.Model):
    ledger = models.ForeignKey(LedgerAccount, on_delete=models.RESTRICT)
    sub_ledger = models.ForeignKey(SubLedgerAccount, on_delete=models.RESTRICT, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.RESTRICT, null=True, blank=True)

    invoice_no = models.CharField(max_length=255, null=True, blank=True)
    ref_invoice_no = models.CharField(max_length=255, null=True, blank=True)

    debit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    credit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)

    payment_date = models.DateTimeField(null=True, blank=True)

    file = models.FileField(upload_to='account/PaymentVoucherFile/', null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'PaymentVouchers'
        ordering = ['-id', ]

    def __str__(self):
        return str(self.id)


class ReceiptVoucher(models.Model):
    ledger = models.ForeignKey(LedgerAccount, on_delete=models.RESTRICT)
    sub_ledger = models.ForeignKey(SubLedgerAccount, on_delete=models.RESTRICT, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.RESTRICT, null=True, blank=True)

    invoice_no = models.CharField(max_length=255, null=True, blank=True)
    ref_invoice_no = models.CharField(max_length=255, null=True, blank=True)

    debit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    credit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)

    receipt_date = models.DateTimeField(null=True, blank=True)

    file = models.FileField(upload_to='account/ReceiptVoucherFile/', null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'ReceiptVouchers'
        ordering = ['-id', ]

    def __str__(self):
        return str(self.id)


class Sales(models.Model):
    ledger = models.ForeignKey(LedgerAccount, on_delete=models.RESTRICT)
    sub_ledger = models.ForeignKey(SubLedgerAccount, on_delete=models.RESTRICT, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.RESTRICT, null=True, blank=True)

    invoice_no = models.CharField(max_length=255, null=True, blank=True)

    debit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    credit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)

    npcheck = models.BooleanField(default=False, null=True, blank=True)
    sales_date = models.DateTimeField(null=True, blank=True)

    file = models.FileField(upload_to='account/SalesFile/', null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'Sales'
        ordering = ['-id', ]

    def __str__(self):
        return str(self.id)


class Purchase(models.Model):
    ledger = models.ForeignKey(LedgerAccount, on_delete=models.RESTRICT)
    sub_ledger = models.ForeignKey(SubLedgerAccount, on_delete=models.RESTRICT, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.RESTRICT, null=True, blank=True)

    invoice_no = models.CharField(max_length=255, null=True, blank=True)

    debit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    credit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)

    pcheck = models.BooleanField(default=False, null=True, blank=True)
    purchase_date = models.DateTimeField(null=True, blank=True)

    file = models.FileField(upload_to='account/PurchaseFile/', null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        ordering = ['-id', ]

    def __str__(self):
        return str(self.id)


class Contra(models.Model):
    ledger = models.ForeignKey(LedgerAccount, on_delete=models.RESTRICT)
    branch = models.ForeignKey(Branch, on_delete=models.RESTRICT, null=True, blank=True)

    invoice_no = models.CharField(max_length=255, null=True, blank=True)

    debit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    credit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)

    contra_date = models.DateTimeField(null=True, blank=True)

    details = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        ordering = ['-id', ]

    def __str__(self):
        return str(self.id)


class Journal(models.Model):
    ledger = models.ForeignKey(LedgerAccount, on_delete=models.RESTRICT)
    branch = models.ForeignKey(Branch, on_delete=models.RESTRICT, null=True, blank=True)

    invoice_no = models.CharField(max_length=255, null=True, blank=True)

    debit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    credit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)

    journal_date = models.DateTimeField(null=True, blank=True)

    details = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        ordering = ['-id', ]

    def __str__(self):
        return str(self.id)


class IDJournal(models.Model):
    invoice_no = models.CharField(max_length=255, null=True, blank=True)

    debit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    credit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)

    journal_date = models.DateTimeField(null=True, blank=True)

    details = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'IDJournals'
        ordering = ['-id', ]

    def __str__(self):
        return str(self.id)


class AccountLog(models.Model):
    ledger = models.ForeignKey(LedgerAccount, on_delete=models.RESTRICT)
    sub_ledger = models.ForeignKey(SubLedgerAccount, on_delete=models.RESTRICT, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.RESTRICT, null=True, blank=True)

    reference_no = models.CharField(max_length=255, null=True, blank=True)
    log_type = models.CharField(max_length=20, null=True, blank=True)

    debit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    credit_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)

    log_date = models.DateTimeField(null=True, blank=True)

    details = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'AccountLogs'
        ordering = ['-id', ]

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if self.log_type:
            self.log_type = self.log_type.replace(' ', '_').lower()
        super().save(*args, **kwargs)
