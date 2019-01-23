from ambition_ae.constants import AE_TMG_ACTION
from ambition_auth.group_names import TMG
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import m2m_changed
from django.dispatch.dispatcher import receiver
from edc_notification.models import Notification


@receiver(m2m_changed, weak=False, dispatch_uid="update_ae_notifications_for_tmg_group")
def update_ae_notifications_for_tmg_group(
    action, instance, reverse, model, pk_set, using, **kwargs
):

    try:
        instance.userprofile
    except AttributeError:
        pass
    else:
        try:
            tmg_ae_notification = Notification.objects.get(name=AE_TMG_ACTION)
        except ObjectDoesNotExist:
            pass
        else:
            try:
                instance.groups.get(name=TMG)
            except ObjectDoesNotExist:
                instance.userprofile.email_notifications.remove(tmg_ae_notification)
            else:
                instance.userprofile.email_notifications.add(tmg_ae_notification)
