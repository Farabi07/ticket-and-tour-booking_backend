# from distutils.command.upload import upload
# import imp
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from PIL import Image
import requests
from io import BytesIO
from django.utils.text import slugify
import re
from tour.utils import sync_cms_tour_content
from django.db import transaction
from member.models import Member
# from payments.models import Traveller,Currency
from django.contrib.postgres.fields import JSONField

class TourContent(models.Model):
    # booking = models.ForeignKey("TourBooking", on_delete=models.CASCADE, related_name='tour_contents', null=True, blank=True)
    agent = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='tour_booking_agent', null=True, blank=True)
    name = models.CharField(max_length=1000, unique=False, null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    thumbnail_image = models.ImageField(upload_to='tour/ThumbnailImage/', null=True, blank=True)
    thumbnail_cloudflare_image_url = models.URLField(max_length=500, null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    languages = models.CharField(max_length=500, null=True, blank=True)
    reviews = models.CharField(max_length=5000, null=True, blank=True)
    additional_info = models.CharField(max_length=5000, null=True, blank=True)
    knw_before_go = models.CharField(max_length=5000, null=True, blank=True)
    group_size = models.CharField(max_length=5000, null=True, blank=True)
    location = models.CharField(max_length=500, null=True, blank=True)
    tag = models.CharField(max_length=500, null=True, blank=True)
    inclution = models.TextField(null=True, blank=True)
    exclusion = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=10000, null=True, blank=True)
    trip_url = models.CharField(max_length=10000, null=True, blank=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    adult_price = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)  
    youth_price = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    child_price = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    published = models.BooleanField(default=False, null=True, blank=True)
    free_cancellation = models.BooleanField(default=False, null=True, blank=True)
    select_bus = models.CharField(max_length=50, null=True, blank=True)
    is_bokun_url = models.BooleanField(default=True, null=True, blank=True)
    
    available_dates = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'TourContents'
        ordering = ('id',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        skip_sync = kwargs.pop("skip_sync", False)

        if self.thumbnail_image:
            try:
                self.thumbnail_cloudflare_image_url = self.upload_to_cloudflare(self.thumbnail_image)
                print("Cloudflare thumbnail image URL:", self.thumbnail_cloudflare_image_url)
            except Exception as e:
                print(f"Error uploading thumbnail image to Cloudflare: {str(e)}")

        if self.name:
            if self.type == 'Tours':
                # Replace special characters (except hyphens) with hyphens
                clean_name = re.sub(r'[^\w\s-]', '-', self.name)

                # Replace spaces with hyphens
                clean_name = re.sub(r'\s+', '-', clean_name)

                # Convert to lowercase
                clean_name = clean_name.lower()

                # Replace multiple consecutive hyphens with a single hyphen
                clean_name = re.sub(r'-{2,}', '-', clean_name)

                # Strip leading and trailing hyphens
                clean_name = clean_name.strip('-')

                slug = clean_name
                counter = 1

                # Ensure slug uniqueness
                while TourContent.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                    slug = f"{clean_name}-{counter}"
                    counter += 1

                self.slug = slug

        # Handle updated_by and created_by fields
        if not self.pk:  # If it's a new record
            self.created_by = kwargs.pop('user', None)
        else:
            self.updated_by = kwargs.pop('user', None)

        # Call the parent class save method
        super().save(*args, **kwargs)

        # self.sync_cms_tour_content(bus_id=self.select_bus)
        if not skip_sync and self.select_bus:
            self.sync_cms_tour_content(bus_id=self.select_bus)

    def upload_to_cloudflare(self, image):
        """
        Upload an image to Cloudflare and return the URL of the uploaded image.
        """
        endpoint = 'https://api.cloudflare.com/client/v4/accounts/f8b413899d5239382d13a2665326b04e/images/v1'
        headers = {
            'Authorization': 'Bearer Ook1HC9KydDm4YfqkmVH5KnoNsSugDDqgLFj4QHi',
        }
        files = {
            'file': image.file
        }
        response = requests.post(endpoint, headers=headers, files=files)
        response.raise_for_status()
        json_data = response.json()
        variants = json_data.get('result', {}).get('variants', [])
        if variants:
            cloudflare_image = variants[0]  # Use the first variant URL
            print("Cloudflare image URL from response:", cloudflare_image)
            return cloudflare_image
        else:
            print("No variants found in the Cloudflare response")
            return None

    # if direct provide bus id 
    def sync_cms_tour_content(self, bus_id=None):
        if not bus_id:
            print("⚠️ No bus ID provided, skipping sync.")
            return  # Prevent unnecessary API calls

        bus_details_url = f"http://192.168.68.104:8000/bus/api/v1/bus/{bus_id}"
        print(f"Fetching details for Bus: {bus_details_url}")

        try:
            response = requests.get(bus_details_url, timeout=10)
            response.raise_for_status()
            bus_details = response.json()

            available_dates = bus_details.get("available_dates", [])
            print(f" Available Dates for Bus {bus_id}: {available_dates}")

            # Update without calling `save()` again to prevent recursion
            TourContent.objects.filter(pk=self.pk).update(available_dates=available_dates)

        except requests.exceptions.RequestException as e:
            print(f" Error fetching bus details: {e}")

class TourContentImage(models.Model):
    tour_content = models.ForeignKey(TourContent, on_delete=models.CASCADE, related_name='tour_content_images',null=True, blank=True)
    image = models.ImageField(upload_to='tour/ContentImage/',null=True, blank=True)
    cloudflare_image = models.URLField(max_length=500, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    

    class Meta:
        verbose_name_plural = 'TourContentImages'
        ordering = ('-id', )

    def __str__(self):
        return f"(self.id)"
        
    def save(self, *args, **kwargs):
        if self.image:
            try:
                self.cloudflare_image = self.upload_cloudflare()
                print("Cloudflare image URL:", self.cloudflare_image)
            except Exception as e:
                print(f"Error uploading image to Cloudflare: {str(e)}")
        super().save(*args, **kwargs)
    def upload_cloudflare(self):
        endpoint = 'https://api.cloudflare.com/client/v4/accounts/f8b413899d5239382d13a2665326b04e/images/v1'
        headers = {
            'Authorization': 'Bearer Ook1HC9KydDm4YfqkmVH5KnoNsSugDDqgLFj4QHi',
        }
        files = {
            'file': self.image.file
        }
        response = requests.post(endpoint, headers=headers, files=files)
        response.raise_for_status()
        json_data = response.json()
        variants = json_data.get('result', {}).get('variants', [])
        if variants:
            cloudflare_image = variants[0]  # Use the first variant URL
            print("Cloudflare image URL from response:", cloudflare_image)
            return cloudflare_image
        else:
            print("No variants found in the Cloudflare response")
            return None


class TourBooking(models.Model):
    from payments.models import Traveller, Currency
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('unpaid','Unpaid')
    ]
    invoice_no = models.CharField(max_length=255, null=True, blank=True)
    agent = models.ForeignKey("member.Member", on_delete=models.CASCADE, related_name='tour_bookings', null=True, blank=True)
    tour = models.ForeignKey(TourContent, on_delete=models.CASCADE, related_name="bookings", null=True, blank=True)
    traveller = models.ForeignKey("payments.Traveller", on_delete=models.CASCADE, related_name="bookings", null=True, blank=True)
    adult_price = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)  
    youth_price = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    child_price = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    total_discount_amount = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_type = models.CharField(max_length=20, choices=(('percentage', 'Percentage'), ('value', 'Value')), default='percentage',blank=True,null=True)
    participants = models.JSONField(null=True, blank=True)
    selected_date = models.DateField(null=True, blank=True)
    selected_time = models.TimeField(null=True, blank=True)
    payWithCash = models.BooleanField(default=False, null=True, blank=True,db_default=False)
    payWithStripe = models.BooleanField(default=False, null=True, blank=True,db_default=False)
    duration = models.CharField(max_length=50,null=True, blank=True)
    is_agent = models.BooleanField(default=False, null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        # default='pending',
        null=False, blank=False
    )
    email_pdf = models.FileField(upload_to='tour_booking_pdf/', null=True, blank=True)
    booking_invoice_pdf = models.FileField(upload_to='tour_booking_invoice/', null=True, blank=True)
    url = models.CharField(max_length=10000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'TourBooking'
        ordering = ('-id',)
    def __str__(self):
        agent_name = self.agent.id if self.agent else "No Agent"
        tour_name = self.tour.name if self.tour else "No Tour"
        # currency_symbol = self.currency.symbol if self.currency else "No Currency"
        return f"Booking for {tour_name} by {agent_name} -  {self.total_price}"