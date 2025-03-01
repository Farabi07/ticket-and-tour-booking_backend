from django.contrib.auth import get_user_model
from django.db.models import signals
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from django_currentuser.middleware import get_current_authenticated_user

from donation.models import *

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


# Cause signals
post_save.connect(created_by_signals, sender=Cause)
post_save.connect(updated_by_signals, sender=Cause)

# CauseContent signals
post_save.connect(created_by_signals, sender=CauseContent)
post_save.connect(updated_by_signals, sender=CauseContent)

# MonthlySubscription signals
post_save.connect(created_by_signals, sender=MonthlySubscription)
post_save.connect(updated_by_signals, sender=MonthlySubscription)

# CauseContentImage signals
post_save.connect(created_by_signals, sender=CauseContentImage)
post_save.connect(updated_by_signals, sender=CauseContentImage)
