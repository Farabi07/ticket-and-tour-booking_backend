from django.contrib import admin
from .models import Payment, Traveller, Currency

# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Payment._meta.fields]
	
@admin.register(Traveller)
class TravellerAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Traveller._meta.fields]

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Currency._meta.fields]