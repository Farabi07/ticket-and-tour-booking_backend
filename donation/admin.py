from django.contrib import admin

from donation.models import *


# Register your models here.

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PaymentMethod._meta.fields]


@admin.register(PaymentMethodDetail)
class PaymentMethodDetailAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PaymentMethodDetail._meta.fields]


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Donation._meta.fields]


@admin.register(Cause)
class CauseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Cause._meta.fields]


@admin.register(CauseContent)
class CauseContentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CauseContent._meta.fields]


@admin.register(CauseContentImage)
class CauseContentImageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CauseContentImage._meta.fields]


@admin.register(MonthlySubscription)
class MonthlySubscriptionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MonthlySubscription._meta.fields]


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Collection._meta.fields]


@admin.register(Level)
class CommissionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Level._meta.fields]


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Gift._meta.fields]


@admin.register(MemberAccountLog)
class MemberAccountLogAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MemberAccountLog._meta.fields]


@admin.register(GiftLog)
class GiftLogAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GiftLog._meta.fields]


@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Withdraw._meta.fields]
