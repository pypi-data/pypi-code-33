import json
import logging
import os
import tempfile
import uuid
from datetime import datetime

from django.apps import apps as django_app
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files import File
from django.forms.formsets import formset_factory
from django.shortcuts import get_object_or_404
from django.template import Context, Template
from django.urls import reverse
from google.cloud import storage
from pydub import AudioSegment
from sorl.thumbnail import get_thumbnail

from ccc.campaigns.cloud_tasks import send_email, voice_call
from ccc.campaigns.forms import (TestSampleEmailForm, TestSampleMMSForm,
                                 TestSampleSMSForm, TestSampleVoiceForm,
                                 make_attachment_form)
from ccc.campaigns.models import OMMS, OSMS, Campaign, OEmail
from ccc.campaigns.views.campaign import humanize_error_message
from ccc.packages.models import TwilioNumber
from ccc.users.models import UserProfile

PROTOCOL = 'https://'
logger = logging.getLogger(__name__)


class GoogleUploadHandler(object):

    def add_date_to_filename(self, file_name):
        """Append a date structure to the filename on gc"""
        current_date = datetime.utcnow().strftime("%Y/%m/%d/")
        return "{}{}".format(current_date, file_name)

    def get_random_image_name(self, suffix):
        """return a unique name - uuid"""
        random_name = "{}{}".format(uuid.uuid4().hex, suffix)
        return self.add_date_to_filename(random_name)

    def handle_uploaded_file(self, file_obj, destination='campaign/', public=True):
        """ Handle uploaded file
            create the folder if it doesn't exist.
        """
        filename, file_extension = os.path.splitext(file_obj.name)
        new_image_name = destination + self.get_random_image_name(file_extension)
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


# class ChannelTest(GoogleUploadHandler):
#     """ChannelTest"""
#     def email_test(self, request, campaign_id=None, is_edit=False):
#         logger.info("test_email_sample called")
#         user = UserProfile.objects.get(id=request.user.id)
#         if user.balance.get('email', 0) <= 0:
#             return False, "You are out of email credit."
#         parent_campaign = None
#         if campaign_id:  # if this is followup campaign
#             parent_campaign = Campaign.objects.get(user=request.user, pk=campaign_id)
#         Contact = django_app.get_model('contacts', 'Contact')
#         contact_qs = Contact.objects.none()
#         if is_edit or campaign_id:
#             campaign = Campaign.objects.filter(user=request.user, pk=campaign_id).first()
#             if campaign:
#                 contact_qs = campaign.contact_set.all()
#         form = TestSampleEmailForm(
#             request.POST, request.FILES, contacts=contact_qs)
#         if not form.is_valid():
#             return False, humanize_error_message(form.errors)
#         # TODO: refactor/reuse
#         formset = formset_factory(form=make_attachment_form(request.user), extra=0)(request.POST, request.FILES,
#                                                                                     prefix='templateimages_set')
#         objects = []
#         if formset.is_valid():
#             for form_ in formset:
#                 for key in ['digital_image', 'digital_audio', 'digital_video', 'digital_attachment', 'url']:
#                     if form_.cleaned_data.get(key, None):
#                         objects.append(
#                             {key: form_.cleaned_data[key], "description": form_.cleaned_data['description']})
#                         continue
#         else:
#             return False, json.dumps(formset.errors)
#
#         email_subject = form.cleaned_data.get('e_greeting_subject', '')
#
#         if form.cleaned_data.get('email_type') == 'premium':
#             premium_email_template = form.cleaned_data.get('premium_email_template')
#             email_body = premium_email_template.email_body
#         else:
#             cet = form.cleaned_data.get('template', '')
#             email_body = cet.email_body
#             if len(objects) < cet.number_of_max_uploads:
#                 for o in range(len(objects), cet.number_of_max_uploads):
#                     objects.append({})
#             objects = objects[:cet.number_of_max_uploads]
#             if len(objects) < cet.number_of_max_uploads:
#                 for o in range(len(objects), cet.number_of_max_uploads):
#                     objects.append({})
#         sample_email = form.cleaned_data.get('sample_email_for_email', '')
#         from_email = form.cleaned_data.get('from_email', '')
#         context = {}
#         contact = form.cleaned_data.get('sample_email_contact', '')
#         if contact:
#             email_body_contact = form.cleaned_data.get('e_greeting', '')
#             context['body'] = Template(email_body_contact).render(contact.template_context)
#         else:
#             context['body'] = email_body
#         context['e_greeting'] = context['body']
#         context['objects'] = objects
#         context['protocol'] = PROTOCOL
#         context['hostname'] = Site.objects.get_current().domain
#         # temporary save local logo
#         logo_file = request.FILES.get('logo')
#         if logo_file:
#             saved_file = self.handle_uploaded_file(logo_file)
#             context['logo'] = saved_file
#
#         if parent_campaign:  # if this is followup campaign, sho parent's logo
#             if parent_campaign.logo:
#                 context['logo'] = parent_campaign.logo
#
#         else:  # get already saved logo if user has not changed the logo
#             if 'logo' not in context and is_edit:
#                 campaign = Campaign.objects.get(
#                     user=request.user,
#                     pk=campaign_id)
#                 if campaign.logo:
#                     context['logo'] = 'http://' + Site.objects.get_current().domain + campaign.logo.url
#
#         if parent_campaign:
#             context['company'] = parent_campaign.company
#         else:
#             context['company'] = form.cleaned_data['company']
#
#         if contact:
#             context['username'] = contact.first_name
#             context["contact_fname"] = contact.first_name
#         else:
#             context['username'] = "<<Contact name>>"
#             context["contact_fname"] = "<<First Name>>"
#
#         if user.balance.get('email', 0) > 0:
#             logger.info("send email trigger")
#             context['analytic_data'] = {
#                 'test': 'test analytics',
#                 'from_email': from_email,
#                 'to_email': sample_email
#             }
#             logger.info("Send email parameter {}".format(email_subject))
#
#             # Async task
#             send_email(subject=email_subject, email_body=email_body,
#                        from_=from_email, to=sample_email, context=context).execute()
#
#             oemail_attributes = {
#                 'from_email': from_email,
#                 'to_email': sample_email,
#                 'body': email_subject,
#                 'template': '',
#                 'lead_name': "<<SAMPLE USER>>",
#                 'user': request.user
#             }
#             OEmail.objects.create(**oemail_attributes)
#         return True, 'Sample email sent successfully.'
#
#     def sms_test(self, request):
#         user = UserProfile.objects.get(id=request.user.id)
#         if user.balance.get('sms', 0) <= 0:
#             return False, "You are out of SMS credit."
#         modified_post = request.POST.copy()
#
#         if 'campaign_id' in modified_post:  # This is followup campaign
#             campaign = get_object_or_404(
#                 Campaign, pk=request.POST.get('campaign_id'))
#             modified_post.update({
#                 'phone': campaign.phone.id,
#                 'sms_greeting': request.POST.get('sms_text')
#             })
#
#         Contact = django_app.get_model('contacts', 'Contact')
#         contact_qs = Contact.objects.none()
#         if 'pk' in request.POST or 'campaign_id' in request.POST:
#             # prevent from getting Contact info for another account
#             campaign_id = request.POST.get('campaign_id', None)
#             campaign = Campaign.objects.filter(user=request.user, pk=request.POST.get('pk', campaign_id)).first()
#             if campaign:
#                 contact_qs = campaign.contact_set.all()
#
#         form = TestSampleSMSForm(modified_post, request.FILES, contacts=contact_qs)
#         if not form.is_valid():
#             return False, humanize_error_message(form.errors)
#
#         sms_greeting = form.cleaned_data.get('sms_greeting', '')
#
#         contact = form.cleaned_data.get('sample_sms_contact', '')
#         if contact:
#             message = Template(sms_greeting).render(Context(contact.template_context))
#         else:
#             message = sms_greeting
#
#         to = form.cleaned_data.get('sample_phone_for_sms')
#         twilio_number_id = form.cleaned_data.get('phone')
#         try:
#             twilio_number = TwilioNumber.objects.get(pk=twilio_number_id)
#         except TwilioNumber.DoesNotExist:
#             return False, "Invalid Campaign Number"
#         else:
#             from_ = twilio_number.twilio_number
#
#         OSMS.objects.create(from_no=from_, to=to, text=message, is_sample=True)
#         return True, 'Sample Sms sent successfully.'
#
#     def voice_test(self, request):
#         user = UserProfile.objects.get(id=request.user.id)
#         if user.balance.get('talktime', 0) <= 0:
#             return False, "You are out of talk time credit."
#         modified_post = request.POST.copy()
#         modified_files = request.FILES.copy()
#         if 'pk' in modified_post:  # This is followup campaign
#             campaign = get_object_or_404(Campaign, pk=request.POST.get('pk'))
#             modified_post.update({
#                 'phone': campaign.phone.id,
#                 'greeting_text': request.POST.get('greeting_text')
#             })
#             if 'voice_greeting_original' not in modified_files:
#                 voice_greeting_original = request.POST.get('voice_greeting_original')
#                 modified_files['voice_greeting_original'] = campaign.voice_greeting or voice_greeting_original
#
#         form = TestSampleVoiceForm(modified_post, modified_files)
#         if not form.is_valid():
#             return False, humanize_error_message(form.errors)
#         sample_voice = form.save(commit=False)
#         sample_voice.user = request.user
#
#         if form.cleaned_data.get('voice_greeting_original'):
#             sound = AudioSegment.from_file(form.cleaned_data.get('voice_greeting_original'))
#             sample_voice.voice_greeting_converted = File(sound.export("{0}.mp3".format(uuid.uuid4().hex),
#                                                                       format="mp3"))
#         sample_voice.save()
#         relative_url = reverse('sample_voice_call', kwargs={'id': sample_voice.id})
#         url = "https://%s%s" % (Site.objects.first().domain, relative_url)
#         # async task
#
#         voice_call(url=url, to_phone=sample_voice.sample_phone, from_phone=sample_voice.phone.twilio_number).execute()
#         # TODO: Create OVoiceCall object here
#         return True, "Sample voice call generated successfully."
#
#     def mms_test(self, request):
#         user = UserProfile.objects.get(id=request.user.id)
#         if user.balance.get('mms', 0) <= 0:
#             return False, "You are out of MMS credit."
#         modified_post = request.POST.copy()
#         modified_files = request.FILES.copy()
#         if 'campaign_id' in modified_post:  # This is followup campaign
#             campaign = get_object_or_404(
#                 Campaign, pk=request.POST.get('campaign_id'))
#             modified_post.update({
#                 'phone': campaign.phone.id,
#                 'mms_greeting_text': request.POST.get('mms_text')
#             })
#
#         campaign = None
#         if 'pk' in request.POST:
#             campaign = Campaign.objects.get(
#                 user=request.user,
#                 pk=request.POST.get('pk'))
#
#         fucampaign = None
#         if 'fucampaign_pk' in request.POST:
#             fucampaign = FUCampaign.objects.get(
#                 user=request.user,
#                 pk=request.POST.get('fucampaign_pk'))
#
#         form = TestSampleMMSForm(
#             modified_post, modified_files, edit_mode=campaign or fucampaign)
#         if not form.is_valid():
#             return False, humanize_error_message(form.errors)
#         mms_greeting = form.cleaned_data.get('mms_greeting_text', '')
#         to = form.cleaned_data.get('sample_phone_for_mms')
#         twilio_number_id = form.cleaned_data.get('phone')
#         image1 = form.cleaned_data['mms_image1']
#         image2 = form.cleaned_data.get("mms_image2")
#         video = form.cleaned_data.get("mms_video")
#
#         # TODO: Do this in a loop with a large number of attachments possible
#         image1_file, image2_file, video_file_url = None, None, None
#         if image1:
#             image1_file = self.handle_uploaded_file(image1)
#         elif campaign:
#             image1_file = campaign.mms_image1
#         elif fucampaign:
#             image1_file = fucampaign.mms_image1
#
#         if image2:
#             image2_file = self.handle_uploaded_file(image2)
#         elif campaign:
#             image2_file = campaign.mms_image2
#         elif fucampaign:
#             image2_file = fucampaign.mms_image2
#
#         if video:
#             video_file_url = self.handle_uploaded_file(video)
#         elif campaign and campaign.mms_video:
#             video_file_url = campaign.mms_video.url
#         elif fucampaign and fucampaign.mms_video:
#             video_file_url = fucampaign.mms_video.url
#
#         try:
#             twilio_number = TwilioNumber.objects.get(pk=twilio_number_id)
#         except TwilioNumber.DoesNotExist:
#             return False, "Invalid Campaign Number"
#         else:
#             from_ = twilio_number.twilio_number
#
#         media = []
#         if image1_file:
#             thumnail = get_thumbnail(image1_file, '300x200', quality=99)
#             media.append(thumnail.url)
#         if image2_file:
#             thumnail = get_thumbnail(image2_file, '300x200', quality=99)
#             media.append(thumnail.url)
#         if video_file_url:
#             media.append(video_file_url)
#
#         OMMS.objects.create(from_no=from_, campaign=campaign, to=to, text=mms_greeting,
#                             media=media, is_sample=True)
#
#         return True, "Sample MMS sent successfully."
