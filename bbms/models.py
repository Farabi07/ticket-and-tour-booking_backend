from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from member.models import Member

# Create your models here.
 
class Bus(models.Model):
    name =  models.CharField(max_length=255, null=True, blank=True)
    email_body =  models.CharField(max_length=50000, null=True, blank=True)
    tour_type = models.CharField(max_length=255, null=True, blank=True)
    group_size = models.CharField(max_length=255, null=True, blank=True)
    seat_quantity =  models.IntegerField(null=True, blank=True)
    itinerary =  models.CharField(max_length=20000, null=True, blank=True)
    price = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    adult_seat_price = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    child_seat_price = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    youth_seat_price = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='bbms/BusImage/', null=True, blank=True)
    type =  models.CharField(max_length=255, null=True, blank=True)
    starting_point = models.CharField(max_length=5000, null=True, blank=True)
    end_point = models.CharField(max_length=5000, null=True, blank=True)
    seat_plan = models.CharField(max_length=255, null=True, blank=True)
    owner_name = models.CharField(max_length=255, null=True, blank=True)
    primary_phone = models.CharField(max_length=255, null=True, blank=True)
    # bus_disable = models.BooleanField(default=False,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'Bus'
        ordering = ['-id',]
        
    def __str__(self):
        return self.name if self.name else f'Bus {self.id}'  


class Passenger(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='passenger_member', null=True, blank=True)
    first_name =  models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    primary_phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'Passengers'
        ordering = ['-id',]
        
    def __str__(self):
        return f'{self.first_name} {self.last_name}' if self.first_name and self.last_name else f'Passenger {self.id}' 

          
class BusBooking(models.Model):
    class TicketStatus(models.TextChoices):
        BOOKED = 'booked', _('Booked')
        AVAILABLE = 'available', _('Available')
        CANCELLED = 'cancelled', _('Cancelled')

    class PaymentType(models.TextChoices):
        BANK = 'bank', _('Bank')
        CASH = 'cash', _('Cash')

    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='buses')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='member')
    seat_no =  models.CharField(max_length=255, null=True, blank=True)
    reference_no = models.CharField(max_length=255, null=True, blank=True)
    date =  models.DateField(null=True, blank=True)
    pickup_time =  models.CharField(max_length=255, null=True, blank=True)
    meeting_point =  models.CharField(max_length=1000, null=True, blank=True)
    booking_time =  models.CharField(max_length=500, null=True, blank=True)
    number_of_travellers =  models.CharField(max_length=500, null=True, blank=True)
    booking_invoice = models.FileField(upload_to='booking_invoice/', null=True, blank=True)
    email_pdf = models.FileField(upload_to='booking_pdf/', null=True, blank=True)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='passenger', null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    total_discount_amount = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    total_seat_count = models.IntegerField(blank=True,null=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_type = models.CharField(max_length=20, choices=(('percentage', 'Percentage'), ('value', 'Value')), default='percentage',blank=True,null=True)
    payment_type = models.CharField(
        max_length=15, choices=PaymentType.choices, default=PaymentType.BANK,null=True, blank=True)
    account_holder_name =  models.CharField(max_length=1000, null=True, blank=True)
    bank_name =  models.CharField(max_length=1500, null=True, blank=True)
    txn_no = models.CharField(max_length=500, null=True, blank=True)
    paid_amount = models.CharField(max_length=500, null=True, blank=True)
    ticket_number = models.CharField(max_length=20, unique=True, null=True, blank=True) 
    status = models.CharField(
        max_length=15, choices=TicketStatus.choices, default=TicketStatus.AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Bus Booking'
        ordering = ['-id',]
        # unique_together = ['bus', 'passenger', 'seat_no', 'status']

    def __str__(self):
        return f'Booking {self.id} for Bus {self.bus}'      
   
   
class AvailableDates(models.Model): 
    date = models.CharField(max_length=255, blank=True,null =True) 
    # date =  models.DateField(null=True, blank=True)
    bus_data = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='available_dates', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'AvailableTimes'
        ordering = ['-id',]
        
    def __str__(self):
        return self.date 
    

class BookingSummary(models.Model):
    # bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bus_summery',null=True,blank=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='member_details', null=True, blank=True)
    bus_booking = models.ForeignKey(BusBooking, on_delete=models.CASCADE, related_name='bus_booking',null=True,blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_seat_count = models.IntegerField()
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_type = models.CharField(max_length=20, choices=(('percentage', 'Percentage'), ('value', 'Value')), default='percentage')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'Agent Commission'
        ordering = ['-id',]

    def __str__(self):
        return f"BookingSummary {self.id}"