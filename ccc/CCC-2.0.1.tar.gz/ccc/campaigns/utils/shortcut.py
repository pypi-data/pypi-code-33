from datetime import timedelta
from uuid import uuid4

import pendulum
from apiclient.discovery import \
    build  # Same issue on the CCC Old version #Todo Investigate #Fixme
from django.conf import settings
from django.core.files import File
from django.utils.timezone import now
from pydub import AudioSegment


def shorten_url(longUrl):
    service = build('urlshortener', 'v1',
                    developerKey=settings.GOOGLE_DEVELOPER_KEY,
                    cache_discovery=False)
    url = service.url()
    body = {'longUrl': longUrl}
    resp = url.insert(body=body).execute()
    return resp.get('id')


def url_analytics(shortUrl):
    service = build('urlshortener', 'v1',
                    developerKey=settings.GOOGLE_DEVELOPER_KEY,
                    cache_discovery=False)
    url = service.url()
    resp = url.get(
        shortUrl=shortUrl,
        projection="ANALYTICS_CLICKS"
    ).execute()
    if resp and resp.get('analytics', None):
        return resp.get('longUrl'), resp.get('analytics')


def url_all_time_clicks(shortUrl):
    long_url, analytics = url_analytics(shortUrl)
    if analytics:
        allTime = analytics.get("allTime")
        if allTime:
            return long_url, allTime.get("shortUrlClicks")


def save_or_update_premium_template(campaign, template_design, template_type):
    """Save or Update binding between premium email and landing with campaign"""

    if template_type == 'email':
        camp_temp_design = campaign.campaigntemplatedesign_set.filter(template_type=template_type).first()
    else:
        camp_temp_design = template_design.campaigntemplatedesign_set.filter(template_type=template_type).first()
    if camp_temp_design:
        camp_temp_design.template = template_design
        camp_temp_design.campaign = campaign
    else:
        from ccc.template_design.models import CampaignTemplateDesign
        camp_temp_design = CampaignTemplateDesign(
            template=template_design,
            campaign=campaign,
            template_type=template_type)
    camp_temp_design.save()


def remove_time_zone(date_time):
    """remove time zone from date time object"""
    return date_time.replace(tzinfo=None)


def get_task_eta(timezone, campaign_trigger_date=None, seconds=None):
    """get estimated time as per timezone"""
    timezone = timezone or 'US/Arizona'
    tz = pendulum.timezone(timezone)
    if campaign_trigger_date:
        return tz.convert(remove_time_zone(campaign_trigger_date))
    else:
        return now() + timedelta(seconds=seconds)


def audio_conversion(voice_greeting):
    sound = AudioSegment.from_file(voice_greeting)
    return File(sound.export("{0}.mp3".format(uuid4().hex), format="mp3"))
