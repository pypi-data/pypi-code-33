"""
This module contains only the Google Cloud tasks related to Users/Customers models and flow operations.
"""
import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from gcloud_tasks.decorators import task

logger = logging.getLogger(__name__)


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def task_send_email_invite_team(request, member_id):
    """Send email invitation to joinning to the team"""
    from ccc.teams.models import TeamMember
    try:
        member = TeamMember.objects.get(id=member_id)
        member.send_email_invite_team()
    except ObjectDoesNotExist:
        err_msg = 'Member doesnt exists pk{}'.format(member_id)
        logger.error(err_msg)
        raise Exception(err_msg)


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def task_send_sms_invite_team(request, member_id):
    """Send SMS invitation to joinning to the team"""
    from ccc.teams.models import TeamMember
    try:
        member = TeamMember.objects.get(id=member_id)
        member.send_sms_invite_team()
    except ObjectDoesNotExist:
        err_msg = 'Member doesnt exists pk{}'.format(member_id)
        logger.error(err_msg)
        raise Exception(err_msg)
