import imp
from django.contrib import admin

from member.models import *


# Register your models here.


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Member._meta.fields]
    list_max_show_all = 10000

@admin.register(Promoter)
class PromoterAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Promoter._meta.fields]
    list_max_show_all = 10000

