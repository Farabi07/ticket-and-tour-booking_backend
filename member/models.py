from django.conf import settings
from django.db import models

from authentication.models import User


# Create your models here.

class Member(User):
    class CouponType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Percentage'
        VALUE = 'value', 'Value'

    father_name = models.CharField(max_length=255, null=True, blank=True)
    mother_name = models.CharField(max_length=255, null=True, blank=True)
    spouse_name = models.CharField(max_length=255, null=True, blank=True)
    village = models.CharField(max_length=255, null=True, blank=True)
    post_office = models.CharField(max_length=255, null=True, blank=True)
    union = models.CharField(max_length=255, null=True, blank=True)
    profession = models.CharField(max_length=255, null=True, blank=True)
    religion = models.CharField(max_length=255, null=True, blank=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,default=50.00)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_type = models.CharField(max_length=20, choices=(('percentage', 'Percentage'), ('value', 'Value')), default='percentage')
    last_bus_id = models.IntegerField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ref_no =  models.CharField(max_length=255, null=True, blank=True)

    coupon_start_date = models.DateField(null=True, blank=True)
    coupon_end_date = models.DateField(null=True, blank=True)
    coupon_text = models.CharField(max_length=255, null=True, blank=True,unique=True)
    coupon_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    coupon_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coupon_type = models.CharField(max_length=20, choices=CouponType.choices, default=CouponType.PERCENTAGE)

    class Meta:
        verbose_name_plural = 'agent'
        ordering = ['-id', ]

    def __str__(self):
        return self.first_name 
    # if self.last_name else self.username

class Promoter(User):
    agent = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='promoter_member', null=True, blank=True) 
    father_name = models.CharField(max_length=255, null=True, blank=True)
    mother_name = models.CharField(max_length=255, null=True, blank=True)
    spouse_name = models.CharField(max_length=255, null=True, blank=True)
    village = models.CharField(max_length=255, null=True, blank=True)
    post_office = models.CharField(max_length=255, null=True, blank=True)
    union = models.CharField(max_length=255, null=True, blank=True)
    profession = models.CharField(max_length=255, null=True, blank=True)
    religion = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Promoters'
        ordering = ['-id', ]

    def __str__(self):
        return self.father_name if self.father_name else self.username
    
# class AgentComission():
#     member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='agent_member', null=True, blank=True) 
#     discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,default=50.00)
#     discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     discount_type = models.CharField(max_length=20, choices=(('percentage', 'Percentage'), ('value', 'Value')), default='percentage')
#     total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     total_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
#     total_seat_count = models.IntegerField(blank=True,null=True)
    
#     class Meta:
#         verbose_name_plural = 'Agent Comission'
#         ordering = ['-id', ]

#     def __str__(self):
#         return self.id