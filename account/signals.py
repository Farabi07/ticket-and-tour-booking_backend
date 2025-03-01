from django.contrib.auth import get_user_model
from django.db.models.deletion import SET_NULL
from django.db.models.signals import pre_save ,post_save, pre_delete
from django_currentuser.middleware import get_current_authenticated_user
from django.core.exceptions import ValidationError

from account.models import *

User = get_user_model()


def created_by_signals(sender, instance, created, **kwargs):
	if created:
		user = get_current_authenticated_user()
		if user is not None:
			sender.objects.filter(id=instance.id).update(created_by=user)


def updated_by_signals(sender, instance, created, **kwargs):
	if not created:
		user = get_current_authenticated_user()
		if user is not None:
			sender.objects.filter(id=instance.id).update(updated_by=user)
		

def user_signals(sender, instance, created, **kwargs):
	if created:
		user = get_current_authenticated_user()
		if user is not None:
			sender.objects.filter(id=instance.id).update(user=user)


def pre_save_signals_for_group(sender, instance, using, **kwargs):
	if not instance.head_group and not instance.head_primarygroup:
		raise ValidationError('Must provide either head_group_self or head_group_primarygroup.')
	if instance.head_group and instance.head_primarygroup:
		raise ValidationError('Select head_group_self or head_group_primarygroup, but not both.')


def pre_delete_signals(sender, instance, using, **kwargs):
	if instance.is_deletable == False:
		raise ValidationError('This object is not deletable!')
	else:
		pass



# PrimaryGroup signals
post_save.connect(created_by_signals, sender=PrimaryGroup)
post_save.connect(updated_by_signals, sender=PrimaryGroup)
pre_delete.connect(pre_delete_signals, sender=PrimaryGroup)


# Group signals
pre_save.connect(pre_save_signals_for_group, sender=Group)
post_save.connect(created_by_signals, sender=Group)
post_save.connect(updated_by_signals, sender=Group)
pre_delete.connect(pre_delete_signals, sender=Group)


# LedgerAccount signals
post_save.connect(created_by_signals, sender=LedgerAccount)
post_save.connect(updated_by_signals, sender=LedgerAccount)
pre_delete.connect(pre_delete_signals, sender=LedgerAccount)


# SubLedgerAccount signals
post_save.connect(created_by_signals, sender=SubLedgerAccount)
post_save.connect(updated_by_signals, sender=SubLedgerAccount)


# PaymentVoucher signals
post_save.connect(created_by_signals, sender=PaymentVoucher)
post_save.connect(updated_by_signals, sender=PaymentVoucher)


# ReceiptVoucher signals
post_save.connect(created_by_signals, sender=ReceiptVoucher)
post_save.connect(updated_by_signals, sender=ReceiptVoucher)


# Sales signals
post_save.connect(created_by_signals, sender=Sales)
post_save.connect(updated_by_signals, sender=Sales)


# Purchase signals
post_save.connect(created_by_signals, sender=Purchase)
post_save.connect(updated_by_signals, sender=Purchase)


# Contra signals
post_save.connect(created_by_signals, sender=Contra)
post_save.connect(updated_by_signals, sender=Contra)


# Journal signals
post_save.connect(created_by_signals, sender=Journal)
post_save.connect(updated_by_signals, sender=Journal)


# IDJournal signals
post_save.connect(created_by_signals, sender=IDJournal)
post_save.connect(updated_by_signals, sender=IDJournal)


# AccountLog signals
post_save.connect(created_by_signals, sender=AccountLog)
post_save.connect(updated_by_signals, sender=AccountLog)


