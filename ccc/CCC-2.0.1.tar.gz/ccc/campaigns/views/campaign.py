import json
import logging
import os
import random
import re
import string
import tempfile
import time
import uuid
from base64 import b64decode
from datetime import datetime

import pendulum
from annoying.functions import get_object_or_None
from anymail.signals import inbound, tracking
from cloud_tools.contrib.mail.send import send_templated_email
from dateutil import parser
from django.apps import apps as django_app
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.db.models import Q
from django.dispatch import receiver
from django.forms.formsets import formset_factory
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView
from django.views.generic.edit import BaseFormView, DeleteView, FormView
from google.cloud import storage
from premailer import transform
from twilio.base.exceptions import TwilioException
from twilio.rest import Client as TwilioRestClient
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from ccc.campaigns.cloud_tasks import (campaign_convert_audio_format)
from ccc.campaigns.forms import CampaignFormNew as CampaignCreationForm
from ccc.campaigns.forms import (CampaignMMSImagesFormset,
                                 FollowUpCampaignForm, PreviewEmailForm,
                                 SupportEmailForm, attachment_formset_factory,
                                 make_attachment_form)
from ccc.campaigns.models import (IMMS, ISMS, OMMS, OSMS, Campaign,
                                  CampaignEmailTemplate, EmailCampaign,
                                  IEmail, IVoiceCall,
                                  MappedKeywords, MMSCampaign, OEmail,
                                  OVoiceCall, RedirectNumber, RejectedNumber,
                                  SampleVoiceCall, SMSCampaign, VoiceCampaign)
from ccc.campaigns.utils.shortcut import (save_or_update_premium_template,
                                          shorten_url)
from ccc.common.decorators import login_required_ajax
from ccc.common.mixins import (AjaxableResponseMixin, LoginRequiredAjaxMixin,
                               LoginRequiredMixin)
from ccc.constants import schedular_mapping
from ccc.contacts.models import Contact
from ccc.digital_assets.models import *
from ccc.packages.models import TwilioNumber
from ccc.packages.utils import get_phone_number
from ccc.teams.models import Team, TeamMember
from ccc.template_design.models import EmailAndWebAnalytics, TemplateDesign
from ccc.users.models import UserProfile

logger = logging.getLogger(__name__)

TIMEZONE_LIST = [(tz, tz) for tz in pendulum.timezones]

SHA1_RE = re.compile('^[a-f0-9]{40}$')

ACCOUNT_SID = settings.TWILIO_SID
AUTH_TOKEN = settings.TWILIO_TOKEN
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

# ^^^ Just look at the imports above. I mean what kind of mindless
# developer does this?

PROTOCOL = 'https://'


def check_mms_capability(client, phone):
    numbers = client.incoming_phone_numbers.list(phone_number=phone)
    if numbers:
        number_detail = numbers[0]
        if number_detail.capabilities.get("mms", False):
            return True
    return False


def get_mms_data_from_request(request):
    mms_data_dict = {}
    mms_data_dict["mms_text"] = request.POST.get("mms_text", None)
    mms_data_dict["sample_mms_number"] = request.POST.get("sample_mms", None)
    mms_data_dict["mms_image_1"] = request.FILES.get("mms_image_1", None)
    mms_data_dict["mms_image_2"] = request.FILES.get("mms_image_2", None)
    mms_data_dict["send_mms_immediately"] = request.POST.get(
        'mms_immediately', None)
    mms_data_dict["mms_schedular_step"] = request.POST.get(
        'mms_schedular_step', None)
    mms_data_dict["use_mms_campaign"] = request.POST.get(
        "use_mms_campaign", None)
    return mms_data_dict


@login_required
def archive_campaign(request, id):
    if request.is_ajax():
        campaign = get_object_or_404(Campaign, pk=id, user=request.user)
        phone = None
        if campaign.phone:
            phone = campaign.phone.twilio_number
            campaign.phone.in_use = False
            campaign.phone.save()
            campaign.phone.update_twilio_urls_to_default()

        campaign.active = False
        campaign.phone = None
        campaign.save()

        for recurring_fu in campaign.fucampaign_set.filter(recur=True):
            recurring_fu.unschedule_from_celery()

        message = 'Campaign "%s" has been archived successfully.' % (
            campaign.name)
        if phone:
            message += " Phone Number %s is released now" % phone

        messages.info(
            request,
            message
        )

        return HttpResponse("Campaign archived successfully.")
    return HttpResponseRedirect(reverse('campaigns'))


@login_required
def CreateVoiceCampaign(request):
    if request.method == 'POST':
        red_number = request.POST.get('redirect_no', None)
        interval = request.POST.get('interval', None)

        audio = request.FILES.get('audio_once', None)
        text = request.POST.get('text', None)
        campaign = request.POST.get('campaign', None)
        tz = request.POST.get('tz', None)

        if campaign:
            campaign = Campaign.objects.get(id=int(campaign))
        else:
            data = json.dumps(
                {'success': 'false', 'message': 'No campaign Found, Create one first'})
            return HttpResponse(data)

        from datetime import datetime

        # date_object = datetime.strptime('28 November 2012 - 03:15 AM', '%d %B %Y - %I:%M %p')
        if interval:
            date_object = datetime.strptime(interval, '%d %B %Y - %I:%M %p')
            mytime = pendulum.timezone(tz).convert(date_object)
        else:
            date_object = datetime.now()
            mytime = pendulum.timezone(tz).convert(date_object)
        VoiceCampaign.objects.create(campaign=campaign, audio=audio, user=request.user, send_at=mytime,
                                     voice_to_text=text)
        return HttpResponse(json.dumps({'success': 'true', 'message': 'Voice campaign added to your campaign'}))

    phones = TwilioNumber.objects.filter(user=request.user)

    return render(request, 'campaigns/new_voice.html', locals())


@login_required
def CreateSMSCampaign(request):
    if request.method == 'POST':
        send_sample = request.POST.get('send_sample', None)
        auto_r_active = request.POST.get('active', None)
        interval = request.POST.get('interval', None)
        text = request.POST.get('text', None)
        campaign = request.POST.get('campaign', None)
        tz = request.POST.get('tz', None)
        sample_no = request.POST.get('sample_no', None)

        if campaign:
            campaign = Campaign.objects.get(id=int(campaign))

        else:
            return HttpResponse(
                json.dumps({'success': 'false', 'message': 'No Campaign Found! Choose one first or create it'}))

        if auto_r_active:
            auto_r_active = True
        else:
            auto_r_active = False

        # date_object = datetime.strptime('28 November 2012 - 03:15 AM', '%d %B %Y - %I:%M %p')
        if interval:

            date_object = datetime.strptime(interval, '%d %B %Y - %I:%M %p')
            mytime = pendulum.timezone(tz).convert(date_object)
        else:
            date_object = datetime.now()
            mytime = pendulum.timezone(tz).convert(date_object)

        SMSCampaign.objects.create(
            text=text, user=request.user, campaign=campaign, send_at=mytime, sample_no=sample_no)

        if send_sample == 'on' and sample_no:
            try:
                client.sms.messages.create(
                    body=text, to=sample_no, from_=campaign.phone.twilio_number)
            except TwilioException as e:
                logging.error(e)

        return HttpResponse(json.dumps({'success': 'true', 'message': 'SMS Campaign added to your campaign'}))

    phones = TwilioNumber.objects.filter(user=request.user)

    return render(request, 'campaigns/new_sms.html', locals())


@csrf_exempt
@login_required
def CreateMMSCampaign(request):
    data = json.dumps({'success': 'false'})

    if request.method == 'POST':

        campaign = request.POST['campaign']
        send_sample = request.POST.get('send_sample', None)
        auto_r_active = request.POST.get('active', None)
        image = request.FILES.get('image', None)
        image1 = request.FILES.get('image1', None)
        request.POST.get('tz', None)
        if auto_r_active:
            auto_r_active = True
        else:
            auto_r_active = False

        sample_no = request.POST['sample_no']

        text = request.POST['text']

        cp = Campaign.objects.get(id=int(campaign))

        if campaign and text:

            MMSCampaign.objects.create(campaign=cp, image=image, image1=image1, text=text,
                                       sample_no=sample_no, user=request.user)

            try:
                if send_sample == 'on':
                    # message = client.messages.create(to=sample_no,from_=number[0].twilio_number,
                    # body="Hello there!",
                    # media_url=['https://demo.twilio.com/owl.png',
                    # 'https://demo.twilio.com/logo.png'])
                    client.sms.messages.create(
                        body=text, to=sample_no, from_=cp.phone)

            except BaseException:

                pass
            data = json.dumps(
                {'message': 'MMS Campaign Created', 'success': 'true'})

        else:
            data = json.dumps(
                {'success': 'false', 'message': 'Hey No campaign Found'})
    return HttpResponse(data)


@login_required
def OutgoingSms(request):
    cp_list = []
    numbers = TwilioNumber.objects.filter(user=request.user)

    if numbers:
        for i in numbers:
            cp_list.append(i.twilio_number)

    sms = OSMS.objects.filter(from_no__in=cp_list).order_by('-date_created')

    return render(request, 'ccc/campaigns/osms.html', locals())


@login_required
def OutgoingMms(request):
    cp_list = []
    campaigns = MMSCampaign.objects.filter(user=request.user)
    if campaigns:
        for i in campaigns:
            cp_list.append(i.id)
    mms = OMMS.objects.filter(campaign__in=cp_list)

    return render(request, 'ccc/campaigns/omms.html', locals())


@login_required
def OutGoingEmail(request):
    email = OEmail.objects.filter(user=request.user)

    return render(request, 'ccc/campaigns/oemail.html', locals())


@login_required
def IncomingEmail(request):
    cp_list = []
    campaigns = EmailCampaign.objects.filter(user=request.user)
    if campaigns:
        for i in campaigns:
            cp_list.append(i.id)

    email = IEmail.objects.filter(from_email__in=cp_list)
    open_email_data = EmailAndWebAnalytics.get_all_email(user_id=request.user.id).order_by('-id')
    data = []
    remove_duplicate = []
    for email_statics in open_email_data:
        to_email = email_statics.data.get('to_email')
        if to_email not in remove_duplicate:
            remove_duplicate.append(to_email)
            obj_data = email_statics.data
            obj_data.update({'created_date': parser.parse(obj_data.get('created_date'))})
            data.append(obj_data)
    open_email_data = data
    sent_email_data = OEmail.objects.filter(user=request.user, campaign__active=True).exclude(campaign=None)
    return render(request, 'ccc/campaigns/iemail.html', locals())


@login_required
def IncomingMms(request):
    cp_list = []
    campaigns = Campaign.objects.filter(user=request.user)
    if campaigns:
        for i in campaigns:
            cp_list.append(i.id)

    sms = IMMS.objects.filter(to__in=cp_list)

    return render(request, 'ccc/campaigns/imms.html', locals())


@login_required
def IncomingSms(request):
    #     cp_list = []
    #     numbers = TwilioNumber.objects.filter(user=request.user)
    #     if numbers:
    #         for i in numbers:
    #             if i.twilio_number:
    #                 cp_list.append(i.twilio_number)
    #
    #     sms = ISMS.objects.filter(to__in=cp_list).order_by('-date_created')

    return render(request, 'ccc/campaigns/isms.html', locals())


@login_required
def CreateEmailCampaign(request):
    if request.method == 'POST':

        att1 = request.FILES.get('att1', None)
        att2 = request.FILES.get('att2', None)
        att3 = request.FILES.get('att3', None)
        att4 = request.FILES.get('att4', None)
        att5 = request.FILES.get('att6', None)
        att6 = request.FILES.get('att6', None)
        interval = request.POST.get('interval', None)
        subject = request.POST.get('subject', None)
        sample_email = request.POST.get('sample_email', None)
        body = request.POST.get('body', None)
        cp = request.POST.get('campaign', None)
        tpl = request.POST.get('tpl', None)

        tz = request.POST.get('tz', None)
        if tpl:
            tpl = CampaignEmailTemplate.objects.get(id=int(tpl))
        else:
            template_name = 'default'

        # date_object = datetime.strptime('28 November 2012 - 03:15 AM', '%d %B %Y - %I:%M %p')
        if interval:
            interval = datetime.strptime(interval, '%d %B %Y - %I:%M %p')
            mytime = pendulum.timezone(tz).convert(interval)
        else:
            interval = datetime.now()
            mytime = pendulum.timezone(tz).convert(interval)

        if cp:
            campaign = Campaign.objects.filter(id=int(cp))
            if campaign:
                campaign = campaign[0]

            cp = EmailCampaign.objects.create(user=request.user, campaign=campaign, att1=att1, att2=att2, att3=att3,
                                              att4=att4, att5=att5, att6=att6, send_at=mytime, body=body,
                                              subject=subject,
                                              email_for_sample=sample_email, template=tpl,
                                              )
            if sample_email:
                mytime = pendulum.timezone('UTC').convert(datetime.now())
                user = UserProfile.objects.get(id=campaign.user.id)
                if user.balance.get('email', 0) > 0:
                    OEmail.objects.create(to_email=sample_email, body=body,
                                          subject=subject, template=template_name,
                                          send_at=mytime, campaign=cp, from_email=campaign.from_email,
                                          company=campaign.company, user=campaign.user
                                          )
                    send_templated_email(
                        subject=subject,
                        email_body=tpl.email_body,
                        sender=campaign.from_email,
                        recipients=sample_email,
                        email_context={
                            'logo': campaign.logo.url,
                            'attachment': campaign.attachment.url,
                            'body': body,
                            'company': campaign.company,

                        }
                    )
            return HttpResponse(json.dumps({'success': 'true', 'message': 'email campaign created'}))

    return HttpResponse(json.dumps({'success': 'false', 'message': 'Email Campaign Creation Error. Try again'}))


@login_required
def MyEmailCampaign(request):
    tpl = CampaignEmailTemplate.objects.all()
    campaigns = EmailCampaign.objects.filter(user=request.user.id)

    return render(request, 'ccc/campaigns/my_email_campaigns.html', locals())


@login_required
def MyMMSCampaign(request):
    campaigns = MMSCampaign.objects.filter(user=request.user.id)
    phones = TwilioNumber.objects.filter(user=request.user)

    return render(request, 'ccc/campaigns/my_mms_campaigns.html', locals())


@login_required
def MySMSCampaign(request):
    phones = TwilioNumber.objects.filter(user=request.user)

    campaigns = SMSCampaign.objects.filter(user=request.user.id)

    return render(request, 'ccc/campaigns/my_sms_campaigns.html', locals())


@login_required
def MyVoiceCampaign(request):
    phones = TwilioNumber.objects.filter(user=request.user)

    campaigns = VoiceCampaign.objects.filter(user=request.user.id)

    return render(request, 'ccc/campaigns/my_voice_campaigns.html', locals())


@login_required
def MyTeam(request):
    # campaigns = VoiceCampaign.objects.filter(user=request.user.id)

    return render(request, 'ccc/campaigns/my_teams.html', locals())


@login_required
def MyContact(request):
    campaigns = Contact.objects.filter(user=request.user.id)

    return render(request, 'ccc/campaigns/my_contacts.html', locals())


@csrf_exempt
def VoiceCall(request):
    """ This function is the handler of incoming calls for campagins.
    This is called by twilio. """

    resp = VoiceResponse()
    to = request.POST.get("To", None)
    from_no = request.POST.get("From", None)
    is_reject = False
    reject_numbers = RejectedNumber.objects.filter(reject_number=from_no)
    if reject_numbers.exists():
        reject_number = reject_numbers[0]
        if reject_number.reject_for_all:
            is_reject = True
        elif reject_number.twilio_numbers.filter(twilio_number=to).exists():
            is_reject = True

    if is_reject:
        resp.reject("busy")
        return HttpResponse(resp, content_type='application/xml')

    # check if number if for team
    team_no = Team.objects.filter(phone__twilio_number=to).exists()

    if team_no:
        # redirect to appropriate guy
        team = Team.objects.get(phone__twilio_number=to)
        mbr = TeamMember.objects.get(id=team.available.id)
        mbr.repeat = mbr.repeat + 1
        mbr.save()

        resp.dial(mbr.phone.twilio_number)

        return HttpResponse(resp, content_type='application/xml')

    else:
        num = TwilioNumber.objects.filter(twilio_number=to)
        if num:
            phone = num[0]

            # Incase the nunber has a redirect
            if phone.redirectnumber_set.exists():

                red_no = RedirectNumber.objects.filter(from_no=phone)
                if red_no:
                    red_no = red_no[0]

                    resp.dial(red_no.to_no)
                resp.say('Goodbye')

                return HttpResponse(resp, content_type='application/xml')
            cp = Campaign.objects.filter(phone=num[0].id, active=True).first()
            if cp:
                if cp.voice_greeting:
                    url = 'http://' + Site.objects.get_current().domain

                    url = url + cp.voice_greeting.url

                    resp.play(url)
                    resp.record(maxLength="120", action="/handle-recording/")
                    # resp.gather(numDigits=1, action="/handle-key/", method="POST")

                elif cp.greeting_text:

                    resp.say(cp.greeting_text)
                    # resp.gather(numDigits=1, action="/handle-key/", method="POST")
                    resp.record(maxLength="120", action="/handle-recording/")
                else:

                    resp.say("Thankyou. Leave a message after the tone")
                    resp.record(maxLength="120", action="/handle-recording/")
            else:
                resp.say("Thankyou. Leave a message after the tone. ")
                resp.record(maxLength="120", action="/handle-recording/")

        else:

            resp.say("Thankyou. Leave a message after the tone. ")
            resp.record(maxLength="120", action="/handle-recording/")

        """Save back the caller's call."""
        from_no = request.POST.get("From", '+254712026507')
        raw_data = dict(request.POST)
        call_sid = request.POST.get("CallSid", 12344)
        caller_city = request.POST.get("FromCity", None)
        caller_country = request.POST.get("FromCountry", None)
        from_state = request.POST.get("FromState", None)
        to_country = request.POST.get("ToCountry", None)
        to_zip = request.POST.get("ToZip", None)
        from_zip = request.POST.get("FromZip", None)

        if from_no:
            if not TwilioNumber.objects.filter(twilio_number=to).exists():
                return HttpResponse(resp, content_type='application/xml')

            num = TwilioNumber.objects.get(twilio_number=to)
            user = num.user

            Contact = django_app.get_model('contacts', 'Contact')
            try:
                contact = Contact.objects.get(phone=from_no, user=user)
            except Contact.DoesNotExist:
                contact = Contact(phone=from_no, user=user)
            except Contact.MultipleObjectsReturned:
                contact = Contact.objects.filter(
                    phone=from_no, user=user).first()

            contact.country = caller_country
            contact.state = from_state
            contact.zip = from_zip
            contact.lead_type = '3'
            contact.save()

            campaign = None
            if num:
                campaigns = num.campaign_set.all()
                if campaigns:
                    campaign = campaigns.first()

            calls = IVoiceCall.objects.filter(call_sid=call_sid)
            if not calls:
                # get campaign
                IVoiceCall.objects.create(raw_data=raw_data, campaign=campaign,
                                          from_no=from_no, to=to,
                                          call_sid=call_sid, from_city=caller_city, from_country=caller_country,
                                          from_state=from_state, to_country=to_country, to_zip=to_zip,
                                          from_zip=from_zip)

            if campaign:
                # This will trigger the "new lead aquired action"
                # 'contacts.signals.contact_for_campaign_created' function
                # as the m2m_changes signal.
                contact.campaigns.add(cp)
                contact.save()

            return HttpResponse(resp, content_type='application/xml')


@csrf_exempt
def HandleKey(request):
    resp = VoiceResponse()

    if request.method == "POST":
        digit_pressed = request.POST.get('Digits')

    else:
        digit_pressed = '1'

    if digit_pressed == "2":
        resp.say("One moment Please as we connect you")
        owner = 1

        resp.dial(owner)

    else:
        resp.say("Leave a message after the tone.")

        resp.record(maxLength="60", action="/handle-recording/")

    return HttpResponse(resp, content_type='application/xml')


@csrf_exempt
def VoiceMessage(request):
    """ Update call! Ths user left a message """

    recording_url = request.POST.get("RecordingUrl", None)
    dict(request.POST)
    record_sid = request.POST.get("RecordingSid", None)
    call_sid = request.POST.get("CallSid", None)
    duration = request.POST.get("RecordingDuration", None)

    calls = IVoiceCall.objects.filter(call_sid=call_sid)
    if calls:
        call = calls[0]
        call.recording_url = recording_url
        if recording_url:
            call.recording_short_url = shorten_url(recording_url + ".mp3")
        call.recording_duration = duration
        call.recording_sid = record_sid
        call.completed = True
        call.save()
    resp = VoiceResponse()
    resp.say("Goodbye")
    return HttpResponse(resp, content_type='application/xml')


@login_required
def ovoice_reports(request):
    num_list = []
    numbers = TwilioNumber.objects.filter(user=request.user.id)

    if numbers:
        for i in numbers:
            num_list.append(i.twilio_number)
    vcr = OVoiceCall.objects.filter(
        from_no__in=num_list).order_by('-date_created')

    return render(request, 'ccc/campaigns/vco.html', locals())


class IVoiceQuerysetMixin(object):
    """ A reusable mixin for getting the IVoiceCall objects currently tied to
    the current user.

    TODO: Due to an earlier bad architectural decision, IVoiceCall is not tied
    to the user itself, only through a TwilioNumber. After that TwilioNumber
    was released/deleted, the related IVoiceCall objects are not tied to the
    user, so it will not be listed.
    They will be floating in the system forever without being displayed."""

    def get_queryset(self):
        num_list = TwilioNumber.objects.filter(user=self.request.user.id) \
            .values_list('twilio_number', flat=True)
        return IVoiceCall.objects.filter(to__in=num_list).order_by('-date_created')


class IVoiceListView(LoginRequiredMixin, IVoiceQuerysetMixin, ListView):
    """ View for listing IVoiceCall objects fo the current user.
    Reuses IVoiceQuerysetMixin for the filtering(access control). """
    template_name = 'ccc/campaigns/vcr.html'


class IVoiceCallDeleteView(LoginRequiredMixin, AjaxableResponseMixin, IVoiceQuerysetMixin, DeleteView):
    """ View for deleting IVoiceCall objects fo the current user.
    Reuses IVoiceQuerysetMixin for the filtering(access control). """

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return self.render_to_json_response({'status': "deleted"}, status=204)


@csrf_exempt
def HandleIncomingSms(request):
    """ This function is the handler of incoming SMS-es for campagins.
    This is called by twilio. """
    request_data = request.GET
    if request.method == "POST":
        request_data = request.POST
    from_no = request_data.get("From", None)
    from_zip = request_data.get("FromZip", None)
    from_country = request_data.get("FromCountry", None)
    from_city = request_data.get("FromCity", None)
    to = request_data.get("To", None)
    from_state = request_data.get("FromState", None)
    message_sid = request_data.get("SmsMessageSid", None)
    message_body = request_data.get("Body", None)
    to_zip = request_data.get("ToZip", None)
    to_country = request_data.get("ToCountry", None)
    request_data.get("ToState", None)
    raw_data = dict(request_data)
    resp = MessagingResponse()
    reject_numbers = RejectedNumber.objects.filter(reject_number=from_no)
    is_reject = False
    if reject_numbers.exists():
        reject_number = reject_numbers[0]
        if reject_number.reject_for_all:
            is_reject = True
        elif reject_number.twilio_numbers.filter(twilio_number=to).exists():
            is_reject = True

    if is_reject:
        resp = VoiceResponse()
        resp.reject("busy")
        return HttpResponse(resp, content_type='application/xml')
    messages = message_body.strip().split()

    if not TwilioNumber.objects.filter(twilio_number=to).exists():
        return HttpResponse(resp, content_type='application/xml')

    num = TwilioNumber.objects.get(twilio_number=to)
    user = num.user

    Contact = django_app.get_model('contacts', 'Contact')
    try:
        contact = Contact.objects.get(phone=from_no, user=user)
    except Contact.DoesNotExist:
        contact = Contact(phone=from_no, user=user)
    except Contact.MultipleObjectsReturned:
        contact = Contact.objects.filter(phone=from_no, user=user).first()

    sender_email = None

    # TODO: Imrpove this logic
    if '@' in message_body:
        if len(messages) == 3:

            sender_fname = messages[0].strip()
            sender_lname = messages[1].strip()
            sender_email = messages[2].strip()
            contact.first_name = sender_fname
            contact.last_name = sender_lname
            contact.email = sender_email

        elif len(messages) == 2:
            sender_fname = messages[0].strip()
            sender_email = messages[1].strip()
            contact.first_name = sender_fname
            contact.email = sender_email
        else:
            contact.note = message_body
    else:
        contact.note = message_body

    campaign = None
    if num:
        campaigns = num.campaign_set.all()
        if campaigns:
            mapped_keyword = MappedKeywords.objects.filter(
                campaign__in=campaigns,
                keyword__iexact=str(message_body).lower().strip(),
                is_active=True)
            if mapped_keyword.exists():
                campaign = mapped_keyword[0].campaign
            else:
                campaign = campaigns.first()
        contact.user = num.user
        contact.country = from_country
        contact.state = from_state
        contact.zip = from_zip
        contact.lead_type = 1

    contact.save()

    if campaign:
        # This will trigger the "new lead aquired action"
        # 'contacts.signals.contact_for_campaign_created' function
        # as the m2m_changes signal.
        contact.campaigns.remove(campaign)
        contact.campaigns.add(campaign)

    # Handle if MMS
    num_media = int(request_data.get('NumMedia', 0))

    if request_data.get('MediaUrl0', None):
        media_files = [(request_data.get('MediaUrl{}'.format(i), ''),
                        request_data.get('MediaContentType{}'.format(i), ''))
                       for i in range(0, num_media)]

        IMMS.objects.create(
            from_no=from_no, from_city=from_city, from_state=from_state, to_zip=to_zip,
            to_country=to_country, to=to, campaign=campaign, message_sid=message_sid,
            raw_data=raw_data, media_list=json.dumps(media_files)
        )

    else:
        ISMS.objects.create(
            from_no=from_no, raw_data=raw_data, to=to, campaign=campaign,
            text=message_body, from_city=from_city, message_sid=message_sid,
            from_state=from_state, from_country=from_country, to_zip=to_zip,
            from_zip=from_zip, to_country=to_country)

    return HttpResponse(resp, content_type='application/xml')


@csrf_exempt
def MakeCall(request, c_id):
    resp = VoiceResponse()

    vc = Campaign.objects.filter(id=int(c_id), active=True)
    if vc:
        vc = vc[0]
        if vc.voice_greeting:
            url = 'http://' + Site.objects.get_current().domain + vc.voice_greeting.url
            resp.play(url)
        elif vc.greeting_text:
            resp.say(vc.greeting_text)

        else:
            resp.say(" Thankyou for calling Cloud Custom Connections."
                     "You will receice more information as soon as is available. Goodbye.")

    else:
        resp.say("Hello and welcome to cloud custom connections")

    return HttpResponse(resp, content_type='application/xml')
#
#
# @csrf_exempt
# def FUMakeCall(request, fuc_id):
#     resp = VoiceResponse()
#
#     fuc = FUCampaign.objects.filter(id=int(fuc_id))
#     if fuc:
#         fuc = fuc[0]
#         if fuc.voice:
#             url = 'http://%s%s' % (Site.objects.get_current().domain, fuc.voice.url)
#             resp.play(url)
#         elif fuc.voice_text.strip():
#             resp.say(fuc.voice_text.strip())
#
#         else:
#             resp.say(" Thankyou for calling Cloud Custom Connections."
#                      "You will receice more information as soon as is available. Goodbye.")
#     else:
#         resp.say("Hello and welcome to cloud custom connections")
#     return HttpResponse(resp, content_type='application/xml')


@csrf_exempt
def CallStatus(request):
    resp = VoiceResponse()
    request.POST.get("To", "+14806669202")
    """Save back the caller's call."""
    request.POST.get("From", None)
    request.POST.get("To", None)
    dict(request.POST)
    request.POST.get("CallSid", None)
    request.POST.get("Digits", None)
    request.POST.get("FromCity", None)
    request.POST.get("FromCountry", None)
    request.POST.get("FromState", None)
    request.POST.get("ToCountry", None)
    request.POST.get("ToZip", None)
    request.POST.get("FromZip", None)
    return HttpResponse(resp, content_type='application/xml')


@receiver(tracking)
def handle_bounce(sender, event, esp_name, **kwargs):
    data = event.esp_event
    if event.event_type == 'hard_bounce' or event.event_type == 'soft_bounce':
        print("Message to %s bounced: %s" % (
            data['msg']['email'],
            data['msg']['bounce_description']
        ))
        ISMS.objects.create(raw_data=data)


@receiver(inbound)
def handle_inbound(sender, event, esp_name, **kwargs):
    data = event.esp_event
    if event.event_type == 'inbound':
        print("Inbound message from %s: %s" % (
            data['msg']['from_email'],
            data['msg']['subject']
        ))
    ISMS.objects.create(raw_data=data)


@csrf_exempt
def CampaignForm(request):
    # dd/mm/yyyy format
    my_date = time.strftime("%d/%m/%Y")
    data = my_date.split('/')
    day, month, year = data[0], data[1], data[2]

    phones = TwilioNumber.objects.filter(user=request.user, in_use=False)
    teams = Team.objects.filter(creator=request.user)
    return render(request, 'modals/campaigns.html', locals())


@csrf_exempt
@login_required
def Campaigns(request):
    campaigns = Campaign.objects.filter(user=request.user, active=True)
    return render(request, 'ccc/campaigns/campaigns.html', locals())


@login_required
def edit_mms(request, c_id=0):
    if request.method == "GET":
        my_date = time.strftime("%d/%m/%Y")
        data = my_date.split('/')
        day, month, year = data[0], data[1], data[2]

        id = request.POST.get('campaign', None)
        campaign = get_object_or_None(MMSCampaign, id=c_id)
        timezones = TIMEZONE_LIST

        return render(request, 'modals/edit_mms.html', locals())
    elif request.method == "POST":

        campaign = request.POST['campaign']
        send_sample = request.POST.get('send_sample', None)
        auto_r_active = request.POST.get('active', None)
        image = request.FILES.get('image', None)
        image1 = request.FILES.get('image1', None)
        tz = request.POST.get('tz', None)
        if auto_r_active:
            auto_r_active = True
        else:
            auto_r_active = False

        sample_no = request.POST['sample_no']

        text = request.POST['text']

        mms_cp = get_object_or_None(MMSCampaign, id=c_id)

        if campaign and text:

            mms_cp.image = image
            mms_cp.image1 = image1
            mms_cp.text = text
            mms_cp.sample_no = sample_no
            mms_cp.user = request.user

            mms_cp.save()

            try:
                user = UserProfile.objects.get(id=request.user.id)
                if send_sample == 'on' and user.balance.get('sms', 0) > 0:
                    # message = client.messages.create(to=sample_no,from_=number[0].twilio_number,
                    # body="Hello there!",
                    # media_url=['https://demo.twilio.com/owl.png',
                    # 'https://demo.twilio.com/logo.png'])
                    client.sms.messages.create(body=text, to=sample_no, from_=mms_cp.phone)

            except BaseException:
                pass
        return HttpResponseRedirect('/mms-campaigns/')


@login_required
def edit_voice(request, c_id=0):
    if request.method == 'GET':
        # dd/mm/yyyy format
        my_date = time.strftime("%d/%m/%Y")
        data = my_date.split('/')
        day, month, year = data[0], data[1], data[2]
        id = request.POST.get('campaign', None)
        campaign = get_object_or_None(VoiceCampaign, id=c_id)
        timezones = TIMEZONE_LIST
        return render(request, 'modals/edit_voice.html', locals())

    elif request.method == 'POST':
        red_number = request.POST.get('redirect_no', None)
        interval = request.POST.get('interval', None)
        audio = request.FILES.get('audio_once', None)
        text = request.POST.get('text', None)
        campaign = request.POST.get('campaign', None)
        tz = request.POST.get('tz', None)
        from datetime import datetime
        if interval:
            date_object = datetime.strptime(interval, '%d %B %Y - %I:%M %p')
            mytime = pendulum.timezone(tz).convert(date_object)
        else:
            date_object = datetime.now()
            mytime = pendulum.timezone(tz).convert(date_object)
        c = get_object_or_None(VoiceCampaign, id=c_id)

        c.audio = audio
        c.user = request.user
        c.send_at = mytime
        c.voice_to_text = text
        c.save()
        return HttpResponseRedirect('/voice-campaigns/')


@login_required
def edit_sms(request, c_id=0):
    if request.method == 'GET':
        my_date = time.strftime("%d/%m/%Y")
        data = my_date.split('/')
        day, month, year = data[0], data[1], data[2]
        id = request.POST.get('campaign', None)
        campaign = get_object_or_None(SMSCampaign, id=c_id)
        timezones = TIMEZONE_LIST
        return render(request, 'modals/edit_sms.html', locals())

    elif request.method == 'POST':
        send_sample = request.POST.get('send_sample', None)
        team = request.POST.get('team', None)
        auto_schedule = request.POST.get('auto_schedule', None)
        auto_r_active = request.POST.get('active', None)
        interval = request.POST.get('interval', None)
        text = request.POST.get('text', None)
        campaign = request.POST.get('campaign', None)
        tz = request.POST.get('tz', None)
        if auto_r_active:
            auto_r_active = True
        else:
            auto_r_active = False
        if interval:
            date_object = datetime.strptime(interval, '%d %B %Y - %I:%M %p')
            mytime = pendulum.timezone(tz).convert(date_object)
        else:
            date_object = datetime.now()
            mytime = pendulum.timezone(tz).convert(date_object)
        sample_no = request.POST.get('sample_no', None)
        c = get_object_or_None(SMSCampaign, id=c_id)
        c.text = text
        c.user = request.user
        c.send_at = mytime
        c.sample_no = sample_no
        c.save()
        try:
            user = UserProfile.objects.get(id=request.user.id)
            if send_sample == 'on' and user.balance.get('sms', 0) > 0:
                client.sms.messages.create(
                    body=text, to=sample_no, from_=campaign.phone.twilio_number)

        except BaseException:
            pass

        return HttpResponseRedirect('/sms-campaigns/')


@login_required
def edit_email(request, c_id=0):
    if request.method == 'GET':
        my_date = time.strftime("%d/%m/%Y")
        data = my_date.split('/')
        day, month, year = data[0], data[1], data[2]
        id = request.POST.get('campaign', None)
        campaign = get_object_or_None(EmailCampaign, id=c_id)
        templates = CampaignEmailTemplate.objects.all()
        timezones = TIMEZONE_LIST
        return render(request, 'modals/edit_email.html', locals())
    elif request.method == 'POST':
        att1 = request.FILES.get('att1', None)
        att2 = request.FILES.get('att2', None)
        att3 = request.FILES.get('att3', None)
        att4 = request.FILES.get('att4', None)
        att5 = request.FILES.get('att6', None)
        att6 = request.FILES.get('att6', None)
        interval = request.POST.get('interval', None)
        subject = request.POST.get('subject', None)
        sample_email = request.POST.get('sample_email', None)
        body = request.POST.get('body', None)
        cp = request.POST.get('campaign', None)
        tpl = request.POST.get('tpl', None)

        tz = request.POST.get('tz', None)
        if tpl:
            tpl = CampaignEmailTemplate.objects.get(id=int(tpl))
        else:
            template_name = 'default'

        if interval:
            interval = datetime.strptime(interval, '%d %B %Y - %I:%M %p')
            mytime = pendulum.timezone(tz).convert(interval)
        else:
            interval = datetime.now()
            mytime = pendulum.timezone(tz).convert(interval)

        c = get_object_or_None(EmailCampaign, id=c_id)

        c.user = request.user
        c.att1 = att1
        c.att2 = att2
        c.att3 = att3
        c.att4 = att4
        c.att5 = att5
        c.att6 = att6
        c.send_at = mytime
        c.body = body
        c.subject = subject
        c.email_for_sample = sample_email
        c.template = tpl
        c.save()
        user = UserProfile.objects.get(id=request.user.id)
        if sample_email and user.balance.get('email', 0) > 0:
            mytime = pendulum.timezone('UTC').convert(datetime.now())
            OEmail.objects.create(to_email=sample_email, body=body,
                                  subject=subject, template=template_name,
                                  send_at=mytime, campaign=c, from_email=c.campaign.from_email,
                                  company=c.campaign.company, user=c.campaign.user
                                  )
            send_templated_email(
                subject=subject,
                email_body=tpl.email_body,
                sender=c.campaign.from_email,
                recipients=c.email_for_sample,
                email_context={
                    'logo': c.campaign.logo.url if c.campaign.logo else "",
                    'attachment': c.campaign.attachment.url if c.campaign.attachment else "",
                    'body': c.body,
                    'company': c.campaign.company,
                }
            )
        return HttpResponseRedirect('/email-campaigns/')


def ViewCampaign(request, c_id):
    campaign = Campaign.objects.get(id=int(c_id))

    return render(request, 'ccc/campaigns/campaign.html', locals())


@login_required
@csrf_exempt
def FUForm(request):
    campaign = request.POST.get('campaign', None)
    return HttpResponse(json.dumps({'campaign': campaign}))


@login_required
def EndedCampaigns(request):
    campaigns = Campaign.objects.filter(user=request.user, active=False)
    return render(request, 'ccc/campaigns/ended-campaigns.html', locals())


class SupportEmail(SuccessMessageMixin, LoginRequiredMixin, FormView):
    template_name = "ccc/campaigns/support.html"
    form_class = SupportEmailForm
    success_message = "<strong>Email Sent!</strong> " \
                      "Our support will review your query " \
                      "and get back to you ASAP"
    success_url = reverse_lazy('support_email')

    def form_valid(self, form):
        form.send_email(sender=self.request.user)
        return super(SupportEmail, self).form_valid(form)


# Show only one error at a time
def humanize_error_message(errors):
    humanized_field_names = {
        'phone': 'Campaign Number',
        'company': 'Company Name',
        'sample_phone': 'Sample Phone',
        'sms_greeting': 'SMS/MMS Text',
        'sample_phone_for_sms': 'Sample Phone',
        'from_email': 'From Email',
        'e_greeting_subject': 'Email Subject',
        'e_greeting': 'Email Body',
        'sample_email_for_email': 'Sample Email',
        'template': 'Email Template',
        'mms_image1': 'MMS Image 1',
        'mms_image2': 'MMS Image 2',
        'sample_phone_for_mms': 'Sample Phone',
        'mms_greeting_text': 'MMS Text',
        "__all__": "fields",
    }
    for field, field_errors in errors.items():
        for error in field_errors:
            return "%s: %s" % (humanized_field_names.get(field, ""), error)


def add_date_to_filename(file_name):
    """Append a date structure to the filename on gc"""
    current_date = datetime.utcnow().strftime("%Y/%m/%d/")
    return "{}{}".format(current_date, file_name)


def get_random_image_name(suffix):
    """return a unique name - uuid"""
    random_name = "{}{}".format(uuid.uuid4().hex, suffix)
    return add_date_to_filename(random_name)


def store_file_media(file_obj, destination='campaign/', public=True):
    """Upload a media file from source file to MEDIA google storage"""
    filename, file_extension = os.path.splitext(file_obj.name)
    new_image_name = destination + get_random_image_name(file_extension)
    with tempfile.NamedTemporaryFile(mode='w+b', suffix=file_extension) as tmp_file:
        for chunk in file_obj.chunks():
            tmp_file.write(chunk)
        storage_client = storage.Client()
        storage_bucket = storage_client.get_bucket(settings.GS_MEDIA_BUCKET_NAME)
        blob = storage_bucket.blob(new_image_name)
        blob.upload_from_filename(tmp_file.name)
        if public:
            blob.make_public()
    return blob.public_url


def handle_uploaded_file(file_obj):
    """ Handle uploaded file
        create the folder if it doesn't exist.
    """
    return store_file_media(file_obj)


@login_required_ajax
def test_voice_sample(request):
    from ccc.campaigns.utils.evms_test_utility import ChannelTest
    test = ChannelTest()
    is_sent, message = test.voice_test(request)
    return HttpResponse(message)


@login_required_ajax
def test_sms_sample(request):
    from ccc.campaigns.utils.evms_test_utility import ChannelTest
    test = ChannelTest()
    is_sent, message = test.sms_test(request)
    return HttpResponse(message)


@login_required_ajax
def test_email_sample(request):
    # TODO: refactor/reuse with `TemplatePreview`
    from ccc.campaigns.utils.evms_test_utility import ChannelTest
    test = ChannelTest()
    campaign_id = request.POST.get('campaign_id')
    pk = request.POST.get('pk')
    campaign_id = pk or campaign_id
    is_sent, message = test.email_test(request, campaign_id=campaign_id, is_edit=True if pk else False)
    return HttpResponse(message)


@csrf_exempt
def sample_voice_call(request, id):
    resp = VoiceResponse()
    svc = get_object_or_404(SampleVoiceCall, id=id)
    if svc.voice_greeting:
        url = 'http://' + Site.objects.get_current().domain
        url = url + svc.voice_greeting.url

        resp.play(url)
        resp.record(maxLength="120", action="/handle-recording/")

    elif svc.greeting_text:
        resp.say(svc.greeting_text)
        resp.record(maxLength="120", action="/handle-recording/")

    return HttpResponse(resp, content_type='application/xml')


class CampaignCreateView(LoginRequiredMixin, AjaxableResponseMixin, CreateView):
    model = Campaign
    form_class = CampaignCreationForm
    template_name = "ccc/create/campaign_new.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CampaignCreateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Get form kwargs"""
        kwargs = super(CampaignCreateView, self).get_form_kwargs()
        if kwargs.get('data'):
            kwargs['data']._mutable = True
            for key, value in schedular_mapping.items():
                campaign_trigger_date = kwargs.get('data', {}).get(value)
                if kwargs['data'].get(key) == '4':
                    kwargs['data'][value] = datetime.strptime(campaign_trigger_date, '%d %B %Y - %I:%M %p')
            kwargs['data']._mutable = False
        return kwargs

    def get_context_data(self, **kwargs):
        Contact = django_app.get_model('contacts', 'Contact')
        context = super(CampaignCreateView, self).get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.filter(user=self.request.user)
        context['templates'] = CampaignEmailTemplate.objects.filter(
            Q(private_template=True, visible_to=self.request.user) |
            Q(private_template=False))
        context['teams'] = Team.objects.filter(creator=self.request.user)
        context['phones'] = get_phone_number(self.request.user)
        context['mms_formset'] = CampaignMMSImagesFormset()
        context['attachment_formset'] = attachment_formset_factory(self.request.user)()
        context['premium_templates'] = TemplateDesign.objects.filter(user=self.request.user, is_active=True,
                                                                     is_public=False, template_type='email')
        context['recommended_premium_templates'] = TemplateDesign.objects.filter(user=self.request.user,
                                                                                 is_active=True, is_public=True,
                                                                                 template_type='email')
        context['template_values'] = {}
        context['template_values']['Contact'] = [
            (f[1], "%s__%s" % (Contact.TEMPLATE_PREFIX, f[0])) for f in Contact.TEMPLATE_FIELDS]

        # show tutorial for on first time only
        """
        IMPORTANT tutorial app is using a package calles "django-wysiwyg-redactor" that is terminated for 
        "violating license of agreement" and the last version of this package doesn't have support for the 
        last version of DJ and Python. 
        
        See: https://twitter.com/douglascoding/status/854115884897619970
        
        We will fork this project and maintain this privately in our Pypi server but while I'll commented / disable
        the "tutorial" app # FIXME # TODO
        
        # CODE Commented:
        if not self.request.user.tutorial_shown:
            video = Video.objects.filter(in_popup=True).first()
            if video:
                context['tutorial_video'] = video
                self.request.user.tutorial_shown = True
                self.request.user.save()
        """

        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.template:
            formset = attachment_formset_factory(self.request.user)(
                self.request.POST, self.request.FILES, instance=self.object)
            if not formset.is_valid():
                return HttpResponseBadRequest(json.dumps(formset.errors))

        self.object.user = self.request.user
        self.object.active = True

        phone = form.cleaned_data.get("phone")

        self.object.save()
        phone.in_use = True
        phone.save()
        self.object.update_twilio_urls()

        recording_saved = False
        if form.cleaned_data.get('voice_greeting_type', None) == 'voice_greeting_record':
            try:
                audio_data = b64decode(
                    form.cleaned_data.get('voice_greeting_original_recording', None).split(',')[1])
            except (IndexError, TypeError):
                pass  # invalid format?
            else:
                filename = 'rec_' + \
                           ''.join(
                               random.sample(string.ascii_lowercase + string.digits, 10)) + '.wav'
                self.object.voice_greeting_original = ContentFile(
                    audio_data, filename)
                self.object.save()
                recording_saved = True

        voice_greeting = form.cleaned_data["voice_greeting_original"]

        if voice_greeting or recording_saved:
            campaign_convert_audio_format(campaign_id=self.object.id).execute()

        if self.object.template:
            formset.save()
        if form.data.get('premium_email_template'):
            template_design = TemplateDesign.objects.get(
                pk=form.data.get('premium_email_template'),
                user=self.request.user,
                is_active=True,
                template_type='email')
            save_or_update_premium_template(self.object, template_design, 'email')
        return self.render_to_json_response({
            'success': 'true',
            'redirect_to': self.get_success_url(),
        })

    def form_invalid(self, form):
        return super(CampaignCreateView, self).form_invalid(form)

    def get_success_url(self):
        return reverse('assign_contacts_to_campaign', kwargs={'pk': self.object.pk})


# class FollowUpCampaignCreateView(LoginRequiredMixin, AjaxableResponseMixin, CreateView):
#     # TODO: reuse/combine with edit.FollowUpCampaignUpdateView
#
#     model = FUCampaign
#     template_name = "ccc/modals/add_follow_up_campaign.html"
#     form_class = FollowUpCampaignForm
#
#     def dispatch(self, *args, **kwargs):
#         # raise 404 for archived/ended parent campaigns
#         get_object_or_404(
#             Campaign, pk=self.kwargs.get("campaign_id"), active=True)
#         return super(FollowUpCampaignCreateView, self).dispatch(*args, **kwargs)
#
#     def get_success_url(self):
#         return reverse("view_campaign", kwargs={'c_id': self.kwargs['campaign_id']})
#
#     def get_form_kwargs(self):
#         form_kwargs = super(FollowUpCampaignCreateView, self).get_form_kwargs()
#         form_kwargs['parent_campaign'] = Campaign.objects.get(
#             id=self.kwargs['campaign_id'])
#         return form_kwargs
#
#     def get_context_data(self, **kwargs):
#         context = super(
#             FollowUpCampaignCreateView, self).get_context_data(**kwargs)
#         context['templates'] = CampaignEmailTemplate.objects.filter(
#             Q(private_template=True, visible_to=self.request.user) |
#             Q(private_template=False))
#         campaign = Campaign.objects.get(id=self.kwargs.get("campaign_id"))
#         context['campaign'] = campaign
#
#         context['attachment_formset'] = attachment_formset_factory(
#             self.request.user)()
#
#         context['template_values'] = {}
#         Contact = django_app.get_model('contacts', 'Contact')
#         contact_fields = [(f[1], "%s__%s" % (Contact.TEMPLATE_PREFIX, f[0]))
#                           for f in Contact.TEMPLATE_FIELDS]
#
#         # TODO: add extra fields
#         context['template_values']['Contact'] = contact_fields
#
#         return context
#
#     def form_valid(self, form):
#         campaign = Campaign.objects.get(id=self.kwargs['campaign_id'])
#         follow_up_campaign = form.save(commit=False)
#         follow_up_campaign.user = self.request.user
#         follow_up_campaign.campaign = campaign
#
#         formset = attachment_formset_factory(self.request.user, parent_class=FUCampaign)(
#             self.request.POST, self.request.FILES, instance=follow_up_campaign)
#
#         # formset = attachment_formset(self.request.POST, self.request.FILES, user=self.request.user)
#         if follow_up_campaign.template and not formset.is_valid():
#             return HttpResponseBadRequest(json.dumps(formset.errors))
#
#         follow_up_campaign.onleadcapture = False
#         follow_up_campaign.specific = False
#         follow_up_campaign.now4leads = False
#         follow_up_campaign.recur = False
#         follow_up_campaign.custom = False
#
#         schedule = form.cleaned_data.get('schedule')
#         if schedule == '1':
#             follow_up_campaign.onleadcapture = True
#
#         elif schedule == '2':
#             follow_up_campaign.specific = True
#
#         elif schedule == '3':
#             follow_up_campaign.now4leads = True
#
#         elif schedule == '4':
#             follow_up_campaign.send_at = form.cleaned_data.get(
#                 'recur_duration', None)
#             follow_up_campaign.duration = form.cleaned_data.get(
#                 'recur_step', None)
#             follow_up_campaign.recur = True
#
#         elif schedule == '5':
#             follow_up_campaign.custom = True
#
#         voice = form.cleaned_data.get('voice_original', '')
#
#         follow_up_campaign.email_body = form.cleaned_data.get(
#             'e_greeting', None)
#         follow_up_campaign.email_subject = form.cleaned_data.get(
#             'e_greeting_subject', None)
#
#         super(FollowUpCampaignCreateView, self).form_valid(form)  # saved here
#
#         if follow_up_campaign.template:
#             formset.save()
#
#         recording_saved = False
#         if form.cleaned_data.get('voice_greeting_type', None) == 'voice_greeting_record':
#             try:
#                 audio_data = b64decode(
#                     form.cleaned_data.get('voice_greeting_original_recording', None).split(',')[1])
#             except (IndexError, TypeError):
#                 pass  # invalid format?
#             else:
#                 filename = 'rec_' + \
#                            ''.join(
#                                random.sample(string.ascii_lowercase + string.digits, 10)) + '.wav'
#                 follow_up_campaign.voice_original = ContentFile(
#                     audio_data, filename)
#                 follow_up_campaign.save()
#                 recording_saved = True
#
#         if voice or recording_saved:
#             fu_campaign_convert_audio_format(campaign_id=follow_up_campaign.id).execute()
#
#         # send now if "Now for exisitng leads" schedule was selected
#         if follow_up_campaign.now4leads:
#             follow_up_campaign.send_now_for_existing_leads()
#
#         if follow_up_campaign.recur:
#             # TODO #FIXME PENDING PENDING FOR AFTER OF DEMO
#             follow_up_campaign.schedule_for_celery()
#
#         return HttpResponse(json.dumps({"url": self.get_success_url()}))


@login_required_ajax
def test_mms_sample(request):
    from ccc.campaigns.utils.evms_test_utility import ChannelTest
    test = ChannelTest()
    is_sent, message = test.mms_test(request)
    if is_sent:
        return HttpResponse(message)
    return HttpResponseBadRequest()


class TemplatePreview(LoginRequiredAjaxMixin, BaseFormView):
    # TODO: refactor/reuse with `test_email_sample`
    form_class = PreviewEmailForm

    @method_decorator(csrf_exempt)  # TODO: fix
    def dispatch(self, request, *args, **kwargs):
        return super(TemplatePreview, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        pk = self.kwargs.get('pk', None)
        self.object = CampaignEmailTemplate.objects.filter(
            Q(private_template=True, visible_to=self.request.user) |
            Q(private_template=False)).filter(pk=pk).first()
        if not self.object:
            return HttpResponse(status=404)

        parent_campaign = None
        if 'campaign_id' in self.request.POST:  # if this is followup campaign
            parent_campaign = Campaign.objects.get(
                user=self.request.user,
                # campaign (parent) id for FUC
                pk=self.request.POST.get('campaign_id')
            )

        # TODO: refactor/reuse
        formset = formset_factory(form=make_attachment_form(self.request.user),
                                  extra=0)(self.request.POST,
                                           self.request.FILES, prefix='templateimages_set')
        objects = []
        if formset.is_valid():
            for form_ in formset:
                for key in ['digital_image', 'digital_audio', 'digital_video', 'digital_attachment', 'url']:
                    if form_.cleaned_data.get(key, None):
                        objects.append(
                            {key: form_.cleaned_data[key], "description": form_.cleaned_data['description']})
                        continue
        else:
            return HttpResponseBadRequest(json.dumps(formset.errors))

        if len(objects) < self.object.number_of_max_uploads:
            for o in range(len(objects), self.object.number_of_max_uploads):
                objects.append({})

        objects = objects[:self.object.number_of_max_uploads]
        context = {'body': form.cleaned_data.get('e_greeting', ''),
                   'contact_fname': '<<First Name>>',
                   'e_greeting': form.cleaned_data.get('e_greeting', ''),
                   'objects': objects,
                   'hostname': Site.objects.get_current().domain}
        context['protocol'] = 'https://'

        if parent_campaign:
            context['company'] = parent_campaign.company
        else:
            context['company'] = form.cleaned_data['company']

        context['username'] = "<<Contact name>>"

        tpl = loader.get_template(self.object.template.path)

        # local, not yet uploaded/saved file
        logo_file = form.cleaned_data['logo']
        if logo_file:
            data = logo_file.read()
            img_data = "data:image;base64,%s" % data.encode('base64')
            context['logo'] = img_data  # serve as base64 image

        if parent_campaign:
            if parent_campaign.logo:
                context['logo'] = parent_campaign.logo

        else:  # get already saved logo if user has not changed the logo
            if 'logo' not in context and 'pk' in self.request.POST:
                campaign = Campaign.objects.get(user=self.request.user, pk=self.request.POST.get('pk'))
                if campaign.logo:
                    context['logo'] = campaign.logo

        return HttpResponse(transform(tpl.render(context)))

    def form_invalid(self, form):
        return HttpResponse(json.dumps(form.errors))
