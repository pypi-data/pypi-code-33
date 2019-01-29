import os
from logging import getLogger

import pygeoip
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files import File
from gcloud_tasks.decorators import task

from ccc.campaigns.models import Campaign
from ccc.contacts.serializers import ContactListSerializer
from ccc.template_design.models import EmailAndWebAnalytics, TemplateDesign
from ccc.users.models import UserProfile

log = getLogger(__name__)


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def email_and_web_analytics(request, **kwargs):
    """Analytics task for web and email"""
    ip_address = kwargs.get('ip_address')
    if ip_address:
        GEOIP = pygeoip.GeoIP(settings.GEOIP_DATABASE, pygeoip.MEMORY_CACHE)
        data = GEOIP.record_by_name(ip_address)
        kwargs.update(data)
    EmailAndWebAnalytics.objects.create(data=kwargs)


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def save_email_template(request, **kwargs):
    HOSTNAME = Site.objects.get_current().domain
    temp_design = TemplateDesign.objects.get(id=kwargs.get('id'))
    analytics_image = """<img src="https://{}/emailandwebanalytics/?{}"
                            style="max-height: 0px; font-size: 0px; display:none;
                            overflow: hidden; mso-hide: all; width:0px; height:0px"> </img>
                        """.format(HOSTNAME, '{{ analytic_data }}')
    temp_design.email_body = analytics_image + temp_design.email_body
    temp_design.save()


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def save_contact(request, user_id, campaign_id, data):
    log.info("contacts request data = {}".format(data))
    user = UserProfile.objects.get(pk=user_id)
    if data.get("phone"):
        data["phone"] = str(data["phone"]).replace("-", "").strip()
    serializer = ContactListSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        serializer.instance.lead_type = 5
        serializer.instance.user = user
        serializer.instance.campaigns.add(Campaign.objects.get(pk=campaign_id))
