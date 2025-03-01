
from django.contrib import admin

from bbms.models import BusBooking, Passenger, Bus,AvailableDates,BookingSummary

# Register your models here.





# Register your models here.

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Bus._meta.fields]
    
    
@admin.register(BusBooking)
class BusBookingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BusBooking._meta.fields]
    

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Passenger._meta.fields]

@admin.register(AvailableDates)
class AvailableDatesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AvailableDates._meta.fields]

@admin.register(BookingSummary)
class BookingSummaryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BookingSummary._meta.fields]