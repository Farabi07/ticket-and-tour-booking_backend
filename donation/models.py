import this
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.db.models import Sum, signals
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
from unicodedata import decimal
from authentication.models import User

from member.models import Member


class Cause(models.Model):
    name = models.CharField(max_length=255)
    goal_amount = models.DecimalField(
        default=0, max_digits=100, decimal_places=2)
    raised_amount = models.DecimalField(
        default=0, max_digits=100, decimal_places=2, null=True, blank=True)

    image = models.ImageField(
        upload_to='donation/Cause/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'Causes'
        ordering = ['-id', ]

    def __str__(self):
        return str(self.name)

    @property
    def process(self):
        process_count = Decimal(self.raised_amount / self.goal_amount) * 100
        process_count = str(process_count)[:5]
        print("process_count:", process_count)
        return process_count

    @property
    def contributor(self):
        for cause in Cause.objects.filter():
            return cause.cause.count()


class CauseContent(models.Model):
    cause = models.ForeignKey(
        Cause, on_delete=models.PROTECT, related_name='cause_contents')
    name = models.TextField()
    value = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'CauseContents'
        ordering = ['-id', ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class CauseContentImage(models.Model):
    cause = models.ForeignKey(
        Cause, on_delete=models.PROTECT, related_name='cause_content_images')
    head = models.CharField(max_length=500)
    image = models.ImageField(upload_to='donation/CauseContentImage/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'CauseContentImages'
        ordering = ('-id',)

    def __str__(self):
        return self.head

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class PaymentMethod(models.Model):
    class Method(models.TextChoices):
        CARD = 'card', _('Card')
        MOBILE = 'mobile', _('Mobile')
        CASH = 'cash', _('Cash')
        OFFLINE = 'offline', _('Offline'),

    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to='donation/PaymentMethodImage/', null=True, blank=True)
    type = models.CharField(
        max_length=7, choices=Method.choices, default=Method.CARD)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'PaymentMethods'
        ordering = ('-id',)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.replace(' ', '_').lower()
        super().save(*args, **kwargs)


class PaymentMethodDetail(models.Model):
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.RESTRICT)
    cause = models.ForeignKey(
        Cause, on_delete=models.CASCADE, null=True, blank=True)
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, null=True, blank=True)
    offline = models.CharField(max_length=50, null=True, blank=True)
    card_number = models.CharField(max_length=50, null=True, blank=True)
    card_holder = models.CharField(max_length=50, null=True, blank=True)
    cvc_code = models.CharField(max_length=20, null=True, blank=True)
    expiry_date = models.CharField(max_length=20, null=True, blank=True)
    payment_number = models.CharField(max_length=14, null=True, blank=True)

    bkash = models.CharField(max_length=15, null=True, blank=True)
    rocket = models.CharField(max_length=15, null=True, blank=True)
    nagad = models.CharField(max_length=15, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'PaymentMethodDetails'
        ordering = ('-id',)

    def __str__(self):
        return str(self.payment_method)


class Donation(models.Model):
    cause = models.ForeignKey(
        Cause, on_delete=models.PROTECT, null=True, blank=True, related_name='cause')
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, null=True, blank=True)
    payment_method_detail = models.ForeignKey(
        PaymentMethodDetail, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=255, decimal_places=2)
    message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'Donations'
        ordering = ('-id',)

    def __str__(self):
        return self.cause.name + ': ' + str(self.amount)


class MonthlySubscription(models.Model):
    member = models.ForeignKey('member.Member', on_delete=models.PROTECT, related_name='member_subscriptions',
                               null=True, blank=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2)

    subscription_date = models.DateTimeField(null=True, blank=True)

    note = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'MonthlySubscriptions'
        ordering = ('-id',)

    def __str__(self):
        return str(self.id)


class Collection(models.Model):
    user = models.ForeignKey(
        Member, on_delete=models.PROTECT,  null=True, blank=True)
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.CASCADE, null=True, blank=True)
    payment_method_detail = models.ForeignKey(
        PaymentMethodDetail, on_delete=models.CASCADE, null=True, blank=True)
    payment_number = models.CharField(max_length=14, null=True, blank=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    date = models.CharField(max_length=20, null=True, blank=True)
    invoice_no = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'Collections'
        ordering = ('-id',)

    def __str__(self):
        return self.user.username


class Level(models.Model):
    class CommisionType(models.TextChoices):
        PERCENTAGE = 'percentage', _('Percentage')
        TAKA = 'taka', _('Taka')

    name = models.CharField(max_length=30, null=True, blank=True)
    commission_type = models.CharField(
        max_length=15, choices=CommisionType.choices, default=CommisionType.TAKA)
    commission_amount = models.IntegerField(
        null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'Levels'
        ordering = ('id',)

    def __str__(self):
        return str(self.name)


class Gift(models.Model):
    level = models.ForeignKey(
        Level, on_delete=models.CASCADE,  null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Gifts'

        ordering = ('id',)

    def __str__(self):
        return str(self.id)


class MemberAccountLog(models.Model):
    class LogType(models.TextChoices):
        COMMISSION = 'commission', _('Commission')
        GIFT = 'gift', _('Gift')
        WITHDRAW = 'withdraw', _('Withdraw')

    log_type = models.CharField(
        max_length=15, choices=LogType.choices, default=LogType.COMMISSION)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,  null=True, blank=True)
    date = models.CharField(max_length=20, null=True, blank=True)

    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.CASCADE, null=True, blank=True)
    payment_number = models.CharField(max_length=14, null=True, blank=True)
    debit_amount = models.DecimalField(max_digits=100, decimal_places=2)
    credit_amount = models.DecimalField(max_digits=100, decimal_places=2)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Member Account Log'
        ordering = ('id',)

    def __str__(self):
        return str(self.id)


class GiftLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,  null=True, blank=True)
    level = models.ForeignKey(
        Level, on_delete=models.CASCADE,  null=True, blank=True)
    gift_amount = models.IntegerField(null=True, blank=True)
    date = models.CharField(max_length=20, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'GiftLog'
        ordering = ('id',)

    def __str__(self):
        return str(self.id)


class Withdraw(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,  null=True, blank=True)
    date = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=14, null=True, blank=True)
    invoice = models.CharField(max_length=14, null=True, blank=True)
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.CASCADE, null=True, blank=True)
    payment_number = models.CharField(max_length=14, null=True, blank=True)
    withdraw_amount = models.IntegerField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Withdraws'
        ordering = ('id',)

    def __str__(self):
        return str(self.id)
