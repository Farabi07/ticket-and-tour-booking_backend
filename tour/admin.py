from django.contrib import admin

from tour.models import *

# Register your models here.
# @admin.register(CMSMenu)
# class CMSMenuAdmin(admin.ModelAdmin):
# 	list_display = [field.name for field in CMSMenu._meta.fields]
@admin.register(TourContent)
class TourContentAdmin(admin.ModelAdmin):
	list_display = [field.name for field in TourContent._meta.fields]

@admin.register(TourContentImage)
class TourContentImageAdmin(admin.ModelAdmin):
	list_display = [field.name for field in TourContentImage._meta.fields]

@admin.register(TourBooking)
class TourBookingAdmin(admin.ModelAdmin):
	list_display = [field.name for field in TourBooking._meta.fields]

