from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out

from django_currentuser.middleware import get_current_authenticated_user
from member.models import  Member

from support.models import *

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




# TicketDepartment signals
post_save.connect(created_by_signals, sender=Member)
post_save.connect(updated_by_signals, sender=Member)


# # TicketPriority signals
# post_save.connect(created_by_signals, sender=ExecutiveMember)
# post_save.connect(updated_by_signals, sender=ExecutiveMember)


# # TicketStatus signals
# post_save.connect(created_by_signals, sender=AdviserMember)
# post_save.connect(updated_by_signals, sender=AdviserMember)


# # Ticket signals
# post_save.connect(created_by_signals, sender=GeneralMember)
# post_save.connect(updated_by_signals, sender=GeneralMember)



