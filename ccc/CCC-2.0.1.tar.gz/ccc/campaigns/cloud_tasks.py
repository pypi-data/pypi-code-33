import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.template import Template, Context
from django.urls import reverse
from gcloud_tasks.decorators import task
from sorl.thumbnail import get_thumbnail
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioRestClient

from ccc.campaigns.models import (OMMS, OSMS, Campaign, IVoiceCall,
                                  OVoiceCall, MMSCampaign, SMSCampaign)
from ccc.contacts.models import Contact

ACCOUNT_SID = settings.TWILIO_SID
AUTH_TOKEN = settings.TWILIO_TOKEN

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

logger = logging.getLogger(__name__)


@task(queue=settings.GOOGLE_TASK_QUEUE_TWILIO)
def celery_update_call_attempts():
    """ Wrapper function to use the @retry decorator, executing the logic with
    expinential backoff """

    incoming = IVoiceCall.objects.filter(charged=False)

    if incoming:
        for call in incoming:
            if call.call_sid:
                data = client.calls.get(call.call_sid)
                data = data.fetch()
                if data.status == 'completed':
                    call.duration = data.duration
                    call.status = data.status
                    call.price = data.price or 0
                    call.forwarded_from = data.forwarded_from
                    call.start_time = data.start_time
                    call.caller_name = data.caller_name
                    call.charged = True
                    call.save()

    outgoing = OVoiceCall.objects.filter(charged=False)

    if outgoing:
        for call in outgoing:
            if call.call_sid:
                data = client.calls.get(call.call_sid)
                data = data.fetch()
                if data.status == 'completed':
                    call.duration = data.duration
                    call.status = data.status
                    call.price = data.price or 0
                    call.forwarded_from = data.forwarded_from
                    call.start_time = data.start_time
                    call.caller_name = data.caller_name
                    call.charged = True
                    call.save()

        # @periodic_task(run_every=crontab(hour="*", minute="*", day_of_week="*"))
        # def celery_update_call():
        """ Celery periodic task for updating in and out voicecall objects.
        Hits twilio api for the status of 'uncharged' calls and refresh them in
        our database
        """
    #   celery_update_call_attempts()


@task(queue=settings.GOOGLE_TASK_QUEUE_VOICE)
def voice_call(request, url, to_phone, from_phone, o_voice_id=None, **kwargs):
    """Do a voice call, using twilio API"""
    logger.info("Making call to %s" % to_phone)
    try:
        call = client.calls.create(url=url, to=to_phone, from_=from_phone, **kwargs)
        OVoiceCall.objects.filter(pk=o_voice_id).update(call_sid=call.sid)
    except TwilioRestException as e:
        logger.exception(e)


@task(queue=settings.GOOGLE_TASK_QUEUE_SMS)
def send_mms(request, omms_id):
    """Sending MMS message using Twilio API"""
    # TODO #FIXME Replace bad legacy code and Implement twilio copilot for automatic scaling
    from ccc.campaigns.utils.twilio import get_obj_from_twilio_number

    omms = OMMS.objects.get(pk=omms_id)

    logger.info("Sending MMS to {}".format(omms.to))

    try:
        twilio_number = omms.from_no
        original_twilio_no_obj = get_obj_from_twilio_number(twilio_number)
        twilio_no_obj = original_twilio_no_obj  # todo wk. configure instance with caching and rater

        msg_text = u"{}".format(omms.text)

        if original_twilio_no_obj.user.balance.get('mms', 0) >= 0:
            # TODO Here use Copilot
            response = client.messages.create(
                body=msg_text, to=omms.to, from_=twilio_no_obj.twilio_number, media_url=omms.media_absolute_urls()
            )
        else:
            title_msg = "MMS limit exhausted for {}. Email={}".format(twilio_no_obj.user.full_name,
                                                                      twilio_no_obj.user.email)

            logging.info(title_msg)
            message = "MMS Remaining={} To_number={} From_no={} media_url={} body={}"

            message = message.format(
                twilio_no_obj.user.balance.get('mms', 0),
                omms.to, omms.from_no,
                omms.media_absolute_urls(),  # TODO gcloud storage
                msg_text
            )
            logging.info(message)
            omms.status = 'Insufficient MMS credits'
            omms.save()
            # todo #fixme send and email or notification
            return

    except TwilioRestException as exception:
        message = exception.__dict__.get('msg')
        omms.status = message if len(message) <= 255 else 'Failed: Error occurred while sending'
        omms.save()
        raise exception

    else:
        logger.info("MMS send successfully from={} | to={} ".format(twilio_no_obj.twilio_number, omms.to))
        omms.message_sid = response.sid
        omms.status = response.status
        omms.save()


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def task_send_sms(request, output_sms_id):
    """Send SMS now..."""
    from ccc.campaigns.models import OSMS
    try:
        sms = OSMS.objects.get(id=output_sms_id)
        sms.send()
    except ObjectDoesNotExist:
        err_msg = "Outgoing SMS. OSM Obj Doesn't exists pk:{}".format(output_sms_id)
        logger.error(err_msg)
        raise Exception(err_msg)


def convert_duration_to_seconds(duration, unit):
    unit = unit.lower()
    if unit == 'days':
        return duration * 24 * 60 * 60
    if unit == 'hours':
        return duration * 60 * 60
    if unit == 'minutes':
        return duration * 60
    if unit == 'seconds':
        return duration
    return duration


@task(queue=settings.GOOGLE_TASK_QUEUE_EMAIL)
def send_email(request, subject, email_body, from_, to, context, attachments=None):
    from cloud_tools.contrib.mail.send import send_templated_email

    send_templated_email(
        subject=subject, email_body=email_body, sender=from_, recipients=to, email_context=context,
        files=attachments
    )


@task(queue=settings.GOOGLE_TASK_QUEUE_EMAIL)
def campaign_send_email(request, campaign_id, contact_id):
    """Campaign send email wrapper"""
    from ccc.campaigns.utils.sending import campaign_send_email
    from ccc.contacts.models import Contact

    campaign = Campaign.objects.get(id=campaign_id)
    contact = Contact.objects.get(id=contact_id)
    campaign_send_email('Campaign', campaign, contact)


@task(queue=settings.GOOGLE_TASK_QUEUE_VOICE)
def campaign_make_call(request, campaign_id, call_url, to, twilio_number):
    campaign = Campaign.objects.get(pk=campaign_id)
    if campaign.user.balance.get('talktime', 0) > 0:
        o_voice = OVoiceCall.objects.create(caller_name=campaign.user.full_name, from_no=twilio_number, to=to,
                                            charged=True)
        voice_call(url=call_url, to_phone=to, from_phone=twilio_number, o_voice_id=o_voice.id).execute()
        return "Sent voice for campaign {} from {} to {}".format(campaign.name, twilio_number, to)
    return "Do not have balance for voice campaign {} from {} to {}".format(campaign.name, twilio_number, to)


@task(queue=settings.GOOGLE_TASK_QUEUE_SMS)
def campaign_send_sms(request, campaign_id, contact_id, twilio_number, sms_id):
    campaign = Campaign.objects.get(pk=campaign_id)
    contact = Contact.objects.get(pk=contact_id)
    sms = SMSCampaign.objects.get(pk=sms_id)
    if campaign.user.balance.get('sms', 0) > 0:
        text = Template(sms.text).render(Context(contact.template_context))
        OSMS.objects.create(from_no=twilio_number, text=text, campaign=campaign, to=contact.phone, )
        return "Sent sms for campaign {} from {} to {}".format(campaign.name, twilio_number, contact.phone)
    return "Do not have balance for sms campaign {} from {} to {}".format(campaign.name, twilio_number, contact.phone)


@task(queue=settings.GOOGLE_TASK_QUEUE_SMS)
def campaign_send_mms(request, campaign_id, contact_id, twilio_number, mms_campaign_id):
    campaign = Campaign.objects.get(pk=campaign_id)
    contact = Contact.objects.get(pk=contact_id)
    mms_campaign = MMSCampaign.objects.get(pk=mms_campaign_id)
    """campaign send MMS"""
    if campaign.user.balance.get('mms', 0) > 0:
        media = []
        """This line is needed to prevent an OSError when dealing with GIF"""
        from sorl.thumbnail import base
        import os

        def get_image_thumbail(obj):
            name, extension = os.path.splitext(obj.url)
            image_format = extension.lstrip('.').upper()
            if image_format == 'JPG':
                image_format = 'JPEG'
            if image_format == 'GIF':
                base.EXTENSIONS.update({'GIF': 'gif'})
            return get_thumbnail(obj, '300x200', quality=99, format=image_format)

        if mms_campaign.image1:
            # TODO integrate this with Gcloud storage.
            thumbnail = get_image_thumbail(mms_campaign.image1)
            media.append(thumbnail.url)

        if mms_campaign.image2:
            thumbnail = get_image_thumbail(mms_campaign.image2)
            media.append(thumbnail.url)

        if mms_campaign.video:
            media.append(mms_campaign.video.url)

        text = Template(mms_campaign.text).render(Context(contact.template_context))

        OMMS.objects.create(from_no=twilio_number, to=contact.phone, campaign=campaign,
                            text=text, media=media)
        return "Sent mms for fu campaign {} from {} to {}".format(campaign.name, twilio_number, contact.phone)

    return "Do not have balance for mms fu campaign {} from {} to {}".format(campaign.name, twilio_number,
                                                                             contact.phone)


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def campaign_convert_audio_format(request, campaign_id):
    """Campaign convert audio format"""

    from ccc.campaigns.utils.shortcut import audio_conversion

    try:
        campaign = Campaign.objects.get(pk=campaign_id)
    except Campaign.DoesNotExist:
        logger.info("Invalid campaign id: {}".format(campaign_id))
        return
    if not campaign.voice_greeting:
        logger.info("No voice file found. Campaign id: {}".format(campaign.id))
        return

    voice_greeting = campaign.voice_greeting_original

    voice_greeting_converted = audio_conversion(voice_greeting)

    campaign.voice_greeting_converted = voice_greeting_converted
    campaign.save()
    logger.info("Voice converted successfully. Campaign id {}".format(campaign.id))


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def voice_campaign_convert_audio(request, voice_campaign_id):
    from ccc.campaigns.utils.shortcut import audio_conversion
    from ccc.campaigns.models import VoiceCampaign
    voice_campaign = VoiceCampaign.objects.get(pk=voice_campaign_id)
    audio_to_convert = voice_campaign.audio
    converted = audio_conversion(audio_to_convert)
    voice_campaign.audio = converted
    voice_campaign.voice_greeting_converted = converted
    voice_campaign.save()
    logger.info('Voice campaign {} audio conversion complete'.format(voice_campaign.id))


def schedule_or_execute_campaign_task(task_method, params, campaign, timezone=settings.TIME_ZONE):
    """campaign could be VoiceCampaign, SMSCampaign, MMSCampaign, EmailCampaign, but since they share common abstract
    model 'CampaignChannelModelMixin', we can call the delay attributes from here instead of repeating logic"""
    if campaign.delay_type and campaign.delay_value:
        seconds = convert_duration_to_seconds(campaign.delay_value, campaign.get_delay_type_display())
        task_method(**params).execute(seconds=seconds)
    elif campaign.trigger_date:
        task_method(**params).execute(trigger_date=campaign.trigger_date, timezone=timezone)
    else:
        task_method(**params).execute()


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def campaign_trigger(request, contact_ids, campaign_id, recurring_interval=None):
    """Recurring interval is if the campaign is to continue, format is 'interval_intervalunit'
    enter value in format 1_1 for 1 day, 2_2 for 2 hours  30_3 for 30 minutes, as stated in
    ccc.constants.DURATION_CHOICES"""
    from ccc.campaigns.models import Campaign
    from ccc.contacts.models import LEAD_TYPE, Contact
    # Retrieve the contacts but remove the contacts added through survey

    def filter_lead_types(entries_to_delete):
        return [x for x, y in list(filter(lambda a: a[0] not in entries_to_delete, LEAD_TYPE))]

    contacts = Contact.objects.filter(pk__in=contact_ids, lead_type__in=filter_lead_types(['7']))
    campaign = Campaign.objects.get(pk=campaign_id)
    fu_campaigns = campaign.campaign_set.all()
    sms = campaign.smscampaign_set.last()
    mms = campaign.mmscampaign_set.last()
    voice = campaign.voicecampaign_set.last()
    email = campaign.emailcampaign_set.last()
    balance = campaign.user.balance
    hostname = Site.objects.get_current().domain
    protocol = "https"
    # Retrieve contacts that do no have empty phone numbers, and leadtype is not survey/voice
    voice_recipients = contacts.filter(phone__isnull=False, lead_type__in=filter_lead_types(['3']))
    # Retrieve contacts that do no have empty phone numbers, and leadtype is not survey
    mobile_message_recipients = contacts.filter(phone__isnull=False)
    email_recipients = contacts.filter(email__isnull=False)

    next_trigger_date = None
    user = campaign.user
    if recurring_interval:
        from ccc.constants import DURATION_CHOICES
        from datetime import datetime, timedelta
        import pytz
        interval, unit = recurring_interval.split('_')
        unit = dict(DURATION_CHOICES).get(unit).lower()
        timedelta_ = timedelta(**{unit: interval})
        next_trigger_date = datetime.now(tz=pytz.timezone(user.time_zone or settings.TIME_ZONE)) + timedelta_

    if campaign.use_voice and voice:
        call_relative_url = reverse('srm:api_marketing:campaigns:get-voice-call-content',
                                    kwargs={'pk': voice.id})
        call_url = '%s://%s%s' % (protocol, hostname, call_relative_url)
        if balance.get('talktime', 0) >= mobile_message_recipients.count():
            for contact in voice_recipients:
                params = {'campaign_id': campaign_id, 'call_url': call_url, 'to': contact.phone.as_e164,
                          'twilio_number': campaign.phone.twilio_number}
                schedule_or_execute_campaign_task(campaign_make_call, params, voice, user.time_zone)
    if campaign.use_mms and mms:
        if balance.get('mms', 0) >= mobile_message_recipients.count():
            for contact in mobile_message_recipients:
                params = {'campaign_id': campaign_id, 'contact_id': contact.id,
                          'twilio_number': campaign.phone.twilio_number, 'mms_campaign_id': mms.id}
                schedule_or_execute_campaign_task(campaign_send_mms, params, mms, user.time_zone)
    if campaign.use_sms and sms:
        if balance.get('sms', 0) >= mobile_message_recipients.count():
            for contact in mobile_message_recipients:
                params = {'campaign_id': campaign_id, 'contact_id': contact.id,
                          'twilio_number': campaign.phone.twilio_number, 'sms_id': sms.id}
                schedule_or_execute_campaign_task(campaign_send_sms, params, sms, user.time_zone)
    if campaign.use_email and email:
        if balance.get('email', 0) >= email_recipients.count():
            for contact in email_recipients:
                params = {'campaign_id': campaign_id, 'contact_id': contact.id}
                schedule_or_execute_campaign_task(campaign_send_email, params, email, user.time_zone)
    for follow_up in fu_campaigns:
        follow_up_campaign_trigger(campaign_id=follow_up.id).execute()
    if campaign.is_follow_up and next_trigger_date:
        """For recurring campaigns, schedule and trigger again"""
        follow_up_campaign_trigger(campaign_id=campaign_id).execute(trigger_date=next_trigger_date,
                                                                    timezone=user.time_zone or settings.TIME_ZONE)


@task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
def follow_up_campaign_trigger(request, campaign_id, trigger_source='parent_campaign_trigger'):
    campaign = Campaign.objects.get(pk=campaign_id)
    follow_up_detail = campaign.followupdetail
    parent_campaign = campaign.parent_campaign
    contacts = list(set(parent_campaign.contact_set.all().values_list('id', flat=True)))
    if follow_up_detail.onleadcapture and trigger_source == 'parent_campaign_trigger':
        campaign_trigger(contact_ids=contacts, campaign_id=campaign_id).execute()
    if follow_up_detail.custom and trigger_source == 'parent_campaign_trigger':
        delay = follow_up_detail.custom_delay
        delay_unit = follow_up_detail.get_custom_delay_unit_display().lower()
        delay_in_seconds = convert_duration_to_seconds(delay, delay_unit)
        campaign_trigger(contact_ids=contacts,
                         campaign_id=campaign_id).execute(seconds=delay_in_seconds)
    if follow_up_detail.specific:
        campaign_trigger(contact_ids=contacts,
                         campaign_id=campaign_id).execute(trigger_date=follow_up_detail.sp_date,
                                                          timezone=campaign.user.time_zone or settings.TIME_ZONE)
    if follow_up_detail.recur:
        campaign_trigger(contact_ids=contacts, campaign_id=campaign_id, recurring_interval='{}_{}'
                         .format(follow_up_detail.recur_interval,
                                 follow_up_detail.get_recur_interval_unit_display()[:1].lower())).execute()
    if follow_up_detail.now4leads:
        campaign_trigger(contact_ids=contacts, campaign_id=campaign_id).execute()
