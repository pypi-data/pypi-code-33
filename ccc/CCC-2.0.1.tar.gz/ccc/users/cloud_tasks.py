"""
This module contains only the Google Cloud tasks related to Users/Customers models and flow operations.
"""
import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from gcloud_tasks.decorators import task

logger = logging.getLogger(__name__)


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def task_send_activation_email(request, activation_id):
    """This task specifically send a email activation to new customers"""
    from ccc.users.models import ActivationCode
    try:
        activation = ActivationCode.objects.get(id=activation_id)
        activation.send_instructions_to_user()

    except ObjectDoesNotExist:
        logger.error("Activation code. Doesn't exists pk:{}".format(activation_id))

        raise ObjectDoesNotExist


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def task_send_email_reset_password(request, reset_code_id):
    """Send email to user with instructions for reset password"""
    from ccc.users.models import ResetCode
    try:
        reset_code = ResetCode.objects.get(id=reset_code_id)
        reset_code.send_email_reset_password()
    except ObjectDoesNotExist:
        logger.error("Reset code. Doesn't exists pk:{}".format(reset_code_id))
        raise
