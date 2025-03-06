# payments/models.py
from django.db import models
from django.conf import settings
from pyrsistent import b


class Traveller(models.Model):
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    passport_number = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.nationality})"
        
class Currency(models.Model):
    currency_code = models.CharField(max_length=3, unique=True,null=True, blank=True)# "USD", "EUR", "GBP"
    name = models.CharField(max_length=100,null=True, blank=True) # "United States Dollar"
    symbol = models.CharField(max_length=5,null=True, blank=True) # "$"
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.currency_code})"

class Payment(models.Model):
    from tour.models import  TourContent
    payment_key = models.CharField(max_length=100, unique=True, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    payment_url = models.URLField(null=True, blank=True)
    agent_ref_no = models.CharField(max_length=255, null=True, blank=True)
    traveller = models.ForeignKey(Traveller, on_delete=models.CASCADE, related_name='payments')
    # tour_booking = models.ForeignKey("tour.TourBooking", on_delete=models.CASCADE, related_name='book_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True,blank=True)
    payment_method = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='success')
    email_pdf = models.FileField(upload_to='tour_booking_pdf/', null=True, blank=True)
    booking_invoice = models.FileField(upload_to='tour_booking_invoice/', null=True, blank=True)
    tour = models.ForeignKey("tour.TourContent", on_delete=models.SET_NULL, null=True, blank=True) 
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True) 
    stripe_payment_method_id = models.CharField(max_length=255, null=True, blank=True)
    transaction_reference = models.CharField(max_length=255,null=True, blank=True)
    payWithCash = models.BooleanField(null=True, blank=True,default=False)
    payWithStripe = models.BooleanField(null=True, blank=True,default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True)

    def __str__(self):
        return f"Payment of {self.amount} {self.currency} (Status: {self.payment_status}) - {self.created_by or 'Unknown User'}"

