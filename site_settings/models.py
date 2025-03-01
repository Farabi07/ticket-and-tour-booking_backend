from enum import unique
from PIL import Image
from django.db import models
from django.conf import settings
from django.db.models.fields import NullBooleanField

from authentication.models import Role
from phonenumber_field.modelfields import PhoneNumberField
# from .signals import contact_created,subscription_created



# Create your models here.

class MenuItem(models.Model):
	parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
	position = models.IntegerField(unique=True, null=True, blank=True)
	menu_id = models.CharField(max_length=100, null=True, blank=True)
	title = models.CharField(max_length=500, null=True, blank=True)
	translate = models.CharField(max_length=100, null=True, blank=True)
	type = models.CharField(max_length=100, null=True, blank=True)
	icon = models.CharField(max_length=100, null=True, blank=True)
	url = models.CharField(max_length=1000, null=True, blank=True)
	exact = models.BooleanField(default=True, null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

	class Meta:
		verbose_name_plural = 'MenuItems'
		ordering = ['position']

	def __str__(self):
		return self.title


	def save(self, *args, **kwargs):
		if self.title:
			self.title = self.title.title()
		if self.translate:
			self.translate = self.translate.title()
		super().save(*args, **kwargs)

class RoleMenu(models.Model):
	role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
	menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

	class Meta:
		verbose_name_plural = 'RoleMenus'
		ordering = ('-id', )

	def __str__(self):
		return str(self.id)

class GeneralSetting(models.Model):
	title = models.CharField(max_length=100, null=True, blank=True)
	site_name = models.CharField(max_length=100, null=True, blank=True)
	site_address = models.CharField(max_length=500, null=True, blank=True)
	email = models.EmailField(null=True, blank=True)
	phone = PhoneNumberField(null=True, blank=True)

	favicon = models.ImageField(upload_to='favicons/', null=True, blank=True)
	logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
	footer_logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
	google_url = models.CharField(max_length=500, null=True, blank=True)
	address = models.TextField(null=True, blank=True)

	facebook_url = models.CharField(max_length=500, null=True, blank=True) 
	twitter_url = models.CharField(max_length=500, null=True, blank=True) 
	instagram_url = models.CharField(max_length=500, null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

	class Meta:
		get_latest_by = 'created_at'
		verbose_name_plural = 'GeneralSettings'
		ordering = ('-id', )
	
	def __str__(self):
		return str(self.id)


class HomePageSlider(models.Model):
	title = models.CharField(max_length=500, null=True, blank=True)
	link = models.CharField(max_length=500, null=True, blank=True)
	subtitle = models.CharField(max_length=500, null=True, blank=True)
	serial_number = models.IntegerField(null=True, blank=True)

	image = models.ImageField(upload_to='homepage_slider_images/', null=True, blank=True)

	details = models.TextField( null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

	class Meta:
		verbose_name_plural = 'HomepageSliders'
		get_latest_by = 'created_at'
		ordering = ('-id', )
	
	def __str__(self):
		return str(self.id)

class Contact(models.Model):
	full_name = models.CharField(max_length=255,null=True, blank=True)
	email = models.EmailField(max_length=100, null=True, blank=True)
	phone_num = models.CharField(blank=True, max_length=50, null=True)
	subject = models.CharField(max_length=255,null=True, blank=True)
	message = models.TextField( null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

	class Meta:
		verbose_name_plural = 'Contacts'
		ordering = ('-id', )
	
	def __str__(self):
		return str(self.email)
	def save(self, *args, **kwargs):
		created = not self.pk
		super().save(*args, **kwargs)
		# if created:
		# 	contact_created.send(sender=self.__class__, instance=self, created=created)

class Subscription(models.Model):
    email = models.EmailField(null=False, blank=False)
    class Meta:
        verbose_name_plural = 'Subscribers'
        ordering = ('-id', )

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        # if created:
        #     subscription_created.send(sender=self.__class__, instance=self, created=created)