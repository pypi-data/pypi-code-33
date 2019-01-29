import logging

from django.conf import settings
from gcloud_tasks.decorators import task

logger = logging.getLogger(__name__)


@task(queue=settings.GOOGLE_TASK_QUEUE_TWILIO)
def task_update_twilio_urls(request, tw_id):
    """
    Async task: update the callback urls for a number at twilio.
    """
    from ccc.packages.models import TwilioNumber
    tw_number = TwilioNumber.objects.get(id=tw_id)
    tw_number.update_twilio_urls()


@task(queue=settings.GOOGLE_TASK_QUEUE_TWILIO)
def task_release_twilio_number(request, tw_id):
    """
    Async task: release/delete a phone number from twilio account.
    """
    from ccc.packages.models import TwilioNumber
    tw_number = TwilioNumber.objects.get(id=tw_id)
    tw_number.delete()


@task(queue=settings.GOOGLE_TASK_QUEUE_TWILIO)
def task_update_number_attemps(request, number, voice_url, sms_url):
    """ This function tries to call twilio api to update the handler urls.
    If fails, it retries with exponential backoff, max 5 times
    (0s,2s,4s,8s,16s) then rerises the exception
    (to see and catch it with sentry or anything else)"""
    # TODO #IMPORTANT REVIEW THIS ASYNC TASK
    pass
