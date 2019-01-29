import json
import logging
import uuid

from django.apps import apps as django_app
from django.contrib.sites.models import Site
from django.core.files import File
from django.http import (Http404, HttpResponse, HttpResponseRedirect,
                         JsonResponse)
from django.template import Context, Template
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from pydub import AudioSegment
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from ccc.campaigns.cloud_tasks import send_email, voice_call
from ccc.campaigns.models import (IMMS, ISMS, OMMS, OSMS, Campaign,
                                  EmailCampaign, IEmail, IVoiceCall,
                                  MappedKeywords, MMSCampaign, OEmail,
                                  OVoiceCall, RedirectNumber, RejectedNumber,
                                  SampleVoiceCall, SMSCampaign, VoiceCampaign)
from ccc.campaigns.utils.evms_test_utility import GoogleUploadHandler
from ccc.campaigns.utils.shortcut import shorten_url
from ccc.contacts.models import Contact, ContactGroup
from ccc.marketing.campaigns.api.serializers import (CampaignFilter,
                                                     CampaignKeywordsSerializer,
                                                     CampaignSerializer,
                                                     EmailCampaignFilter,
                                                     EmailCampaignSerializer,
                                                     IncomingEmailSerializer,
                                                     IncomingMMSSerializer,
                                                     IncomingSMSSerializer,
                                                     MappedKeywordSerializer,
                                                     MMSCampaignFilter,
                                                     MMSCampaignSerializer,
                                                     OutgoingCallsSerializer,
                                                     OutgoingEmailSerializer,
                                                     OutgoingMMSSerializer,
                                                     OutgoingSMSSerializer,
                                                     ReceivedCallsSerializer,
                                                     SampleVoiceCallSerializer,
                                                     SMSCampaignFilter,
                                                     SMSCampaignSerializer,
                                                     TestEmailCampaignSerializer,
                                                     TriggerCampaignSerializer,
                                                     VoiceCampaignFilter,
                                                     VoiceCampaignSerializer)
from ccc.mixin import AuthParsersMixin, StandardResultsSetPagination
from ccc.packages.models import TwilioNumber
from ccc.storages.handle import get_thumbnail
from ccc.teams.models import Team, TeamMember
from ccc.users.models import UserProfile
from ccc.utils.utils import validate_media_absolute_url
from django_filters.rest_framework import DjangoFilterBackend

logger = logging.getLogger(__name__)


class CampaignTypesLog(object):
    def _get_incoming_calls_queryset(self):
        queryset = IVoiceCall.objects.filter(to__in=self.request.user.twilionumber_set.all()
                                             .values_list('twilio_number', flat=True))
        return self.filter_campaign_queryset(queryset).order_by('-date_created')

    def _get_outgoing_calls_queryset(self):
        queryset = OVoiceCall.objects.filter(from_no__in=self.request.user.twilionumber_set.all()
                                             .values_list('twilio_number', flat=True))
        return self.filter_campaign_queryset(queryset).order_by('-date_created')

    def _get_incoming_sms_queryset(self):
        queryset = ISMS.objects.filter(to__in=self.request.user.twilionumber_set.all()
                                       .values_list('twilio_number', flat=True))
        return self.filter_campaign_queryset(queryset).order_by('-date_created')

    def _get_outgoing_sms_queryset(self):
        queryset = OSMS.objects.filter(from_no__in=self.request.user.twilionumber_set.all()
                                       .values_list('twilio_number', flat=True))
        return queryset.order_by('-date_created')

    def _get_incoming_mms_queryset(self):
        queryset = IMMS.objects.filter(to__in=self.request.user.twilionumber_set.all()
                                       .values_list('twilio_number', flat=True))
        return self.filter_campaign_queryset(queryset).order_by('-date_created')

    def _get_outgoing_mms_queryset(self):
        queryset = OMMS.objects.filter(from_no__in=self.request.user.twilionumber_set.all()
                                       .values_list('twilio_number', flat=True))
        return self.filter_campaign_queryset(queryset).order_by('-date_created')

    def _get_incoming_emails_queryset(self):
        queryset = IEmail.objects.filter(campaign_id__in=self.request.user.campaign_set.all()
                                         .values_list('pk', flat=True))
        return self.filter_campaign_queryset(queryset).order_by('-created_at')

    def _get_outgoing_emails_queryset(self):
        queryset = OEmail.objects.filter(campaign_id__in=self.request.user.campaign_set.all()
                                         .values_list('pk', flat=True))
        return self.filter_campaign_queryset(queryset).order_by('-time')

    def filter_campaign_queryset(self, queryset):
        filters = dict(self.request.GET)
        cleaned_filters = dict()
        # Clean the filters and remove the ones with empty values
        for key, value in filters.items():
            if value and key != 'page' and key != 'page_size':
                cleaned_filters.update({key: value[0]})
        queryset = queryset.filter(**cleaned_filters)
        return queryset

    log_serializers_mapping = {
        'incoming_voice': ReceivedCallsSerializer,
        'outgoing_voice': OutgoingCallsSerializer,
        'incoming_sms': IncomingSMSSerializer,
        'outgoing_sms': OutgoingSMSSerializer,
        'incoming_mms': IncomingMMSSerializer,
        'outgoing_mms': OutgoingMMSSerializer,
        'incoming_email': IncomingEmailSerializer,
        'outgoing_email': OutgoingEmailSerializer,
    }

    log_models_mapping = {
        'incoming_voice': IVoiceCall,
        'outgoing_voice': OVoiceCall,
        'incoming_sms': ISMS,
        'outcoming_sms': OSMS,
        'outgoing_mms': OMMS,
        'incoming_mms': IMMS,
        'outgoing_email': OEmail,
        'incoming_email': IEmail,
    }

    log_queryset_mapping = {
        'incoming_voice': _get_incoming_calls_queryset,
        'outgoing_voice': _get_outgoing_calls_queryset,
        'incoming_sms': _get_incoming_sms_queryset,
        'outgoing_sms': _get_outgoing_sms_queryset,
        'incoming_mms': _get_incoming_mms_queryset,
        'outgoing_mms': _get_outgoing_mms_queryset,
        'incoming_email': _get_incoming_emails_queryset,
        'outgoing_email': _get_outgoing_emails_queryset,
    }

    """Rest go here"""


class CampaignViewSet(AuthParsersMixin, GoogleUploadHandler, ModelViewSet, CampaignTypesLog):
    """ Campaign API
        campaign_id : campaign id
        campaign_type : email/sms/mms/voice/follow_up
    """
    serializer_class = CampaignSerializer
    model = Campaign
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = '__all__'
    filter_class = CampaignFilter
    filter_class_mapping = {
        'email': EmailCampaignFilter,
        'sms': SMSCampaignFilter,
        'mms': MMSCampaignFilter,
        'voice': VoiceCampaignFilter,
    }
    serializer_class_mapping = {
        'email': EmailCampaignSerializer,
        'sms': SMSCampaignSerializer,
        'mms': MMSCampaignSerializer,
        'voice': VoiceCampaignSerializer,
    }
    test_serializer_class_mapping = {
        'email': TestEmailCampaignSerializer,
        'sms': SMSCampaignSerializer,
        'mms': MMSCampaignSerializer,
        'voice': SampleVoiceCallSerializer,
    }
    model_mapping = {
        'email': EmailCampaign,
        'sms': SMSCampaign,
        'mms': MMSCampaign,
        'voice': VoiceCampaign,
    }

    def get_serializer_class(self):
        if self.kwargs.get('campaign_type'):
            return self.serializer_class_mapping.get(self.kwargs['campaign_type'])
        return self.serializer_class

    def get_queryset(self):
        campaign_type = self.kwargs.get('campaign_type')
        if campaign_type:
            self.filter_class = self.filter_class_mapping.get(campaign_type)
            return self.model_mapping.get(campaign_type).objects.filter(
                campaign__id=self.kwargs.get('campaign_id')).order_by('-date_created')
        active = False if self.request.query_params.get('archive') else True
        is_follow_up = True if self.request.query_params.get('is_follow_up') else False
        query_set = self.request.user.campaign_set.filter(active=active, is_follow_up=is_follow_up)
        # If particular campaign or follow up detail is being queried return all
        if self.kwargs.get('pk'):
            query_set = self.request.user.campaign_set.all()
        search = self.request.query_params.get('search')
        campaign_id = self.request.query_params.get('campaign_id')
        if search:
            query_set = self.request.user.campaign_set.filter(name__istartswith=search)
        elif campaign_id:
            query_set = self.request.user.campaign_set.filter(id=campaign_id)
        return query_set

    def perform_create(self, serializer):
        campaign = serializer.save()
        if serializer.__class__.__name__ == 'CampaignSerializer':
            if campaign.phone:
                campaign.update_twilio_urls()
                campaign.phone.in_use = True
                campaign.phone.save()

    def perform_update(self, serializer):
        if serializer.__class__.__name__ == 'CampaignSerializer':
            old_phone_id = self.get_object().phone_id
            if serializer.validated_data.get('phone'):
                new_phone_id = serializer.validated_data.get('phone').id
                # We want to update phone twilio URL if the phone number was changed
                if old_phone_id != new_phone_id:
                    # If a phone number was attached before, update its campaign and its follow-up twilio url to default
                    if old_phone_id:
                        self.get_object().reset_twilio_url_to_default()
                    campaign_obj = serializer.save()
                    campaign_obj.phone.in_use = True
                    campaign_obj.phone.save()
                    # Update the follow up campaign phone numbers, they have to be same
                    campaign_obj.campaign_set.all().update(phone_id=new_phone_id)
                    campaign_obj.update_twilio_urls()
                    return
        serializer.save()

    def perform_destroy(self, instance):
        if instance.__class__.__name__ == 'Campaign' and not instance.is_follow_up:
            self.get_object().reset_twilio_url_to_default()
        instance.delete()

    @action(methods=['get'], detail=False)
    def active_campaign_name_and_phone_number(self, request):
        """Active campaign name and phone number"""
        data = []
        active = False if self.request.query_params.get('archive') else True
        for campaign_id, name, phone in self.request.user.campaign_set.filter(
            active=active).values_list('id', 'name', 'phone__friendly_name'):
            data.append({'id': campaign_id, 'name': name, 'phone': phone})
        return JsonResponse(data, safe=False)

    def _send_email_campaign(self, request, data, campaign_obj):
        context = {}
        subject = data.get('subject')
        from_email = data.get('from_email')
        to_email = data.get('sample_email_for_email')
        body = data.get('body')
        context['analytic_data'] = {
            'test': 'Test email analytics',
            'from_email': from_email,
            'to_email': to_email
        }
        objects = []
        if data.get('email_type') == 'premium':
            template = data.get('premium_email_template')
            email_body = template.email_body
        else:
            template = data.get('template')
            context.update({'body': body, 'e_greeting': body})
            email_body = Template(template.email_body).render(Context(context))
        contact = data.get('sample_email_contact', '')
        if contact:
            email_body = Template(email_body).render(contact.template_context)
        context['body'] = email_body
        context['objects'] = objects
        context['protocol'] = request.META['HTTP_HOST']
        context['hostname'] = request.META['HTTP_HOST']
        context['company'] = campaign_obj.company
        # temporary save local logo
        logo_file = request.FILES.get('logo')
        if logo_file:
            saved_file = self.handle_uploaded_file(logo_file)
            context['logo'] = saved_file
        elif campaign_obj.logo:
            context['logo'] = campaign_obj.logo.url
        send_email(subject=subject,
                   email_body=email_body,
                   from_=from_email,
                   to=to_email, context=context).execute()
        oemail_attributes = {
            'from_email': from_email,
            'to_email': to_email,
            'subject': subject,
            'body': email_body,
            'template': template,
            'lead_name': "<<SAMPLE USER>>",
            'user': request.user,
            'sent': True
        }
        OEmail.objects.create(**oemail_attributes)

    def _send_sms_campaign(self, campaign_obj, data):
        to_number = data.get('sample_no')
        text = data.get('text')
        twilio_number = campaign_obj.phone.twilio_number
        logger.info('SMS campaign started as agrs {} {} {}'.format(text, to_number, twilio_number))
        OSMS.objects.create(from_no=twilio_number, to=to_number, text=text, campaign=campaign_obj, is_sample=True)

    def _send_mms_campaign(self, campaign_obj, data, instance=None):
        mms_greeting = data.get('text')
        to = data.get('sample_no')
        twilio_number = campaign_obj.phone.twilio_number
        image1 = data.get('image1')
        image2 = data.get("image2")
        video = data.get("video")
        logger.info('MMS campaign started as agrs {} {} {}'.format(mms_greeting, to, twilio_number))
        media_file = list()

        def image_video_processing(file, name):
            if file:
                return media_file.append(self.handle_uploaded_file(file))
            elif instance and getattr(instance, name):
                return media_file.append('http:{}'.format(getattr(instance, name).url))

        image_video_processing(image1, 'image1')
        image_video_processing(image2, 'image2')
        image_video_processing(video, 'video')

        media = []
        # todo with thumbnail
        try:
            for image in media_file:
                thumnail = get_thumbnail(image)
                media.append(thumnail.media_link)
        except Exception as ex:
            logger.error(ex)
            media = media_file
        logger.info('MMS campaign hit task as agrs {} {} {}'.format(mms_greeting, to, twilio_number))
        OMMS.objects.create(from_no=twilio_number, to=to, text=mms_greeting, campaign=campaign_obj,
                            media=media, is_sample=True)

    def _send_voice_campaign(self, campaign_obj, serializer):
        data = serializer.validated_data
        voice_greeting_original = data.get('voice_greeting_original')
        audio = data.get('audio')
        if audio:
            voice_greeting_original = audio
            del data['audio']
        voice_campaign = campaign_obj.voicecampaign_set.last()
        if not voice_greeting_original and voice_campaign and voice_campaign.audio:
            voice_greeting_original = voice_campaign.audio
        data.update({'voice_greeting_original': voice_greeting_original})
        instance = SampleVoiceCall(**data)
        instance.save()
        if voice_greeting_original:
            sound = AudioSegment.from_file(instance.voice_greeting_original)
            instance.voice_greeting_converted = File(sound.export("{0}.mp3".format(uuid.uuid4().hex), format="mp3"))
            instance.voice_greeting_original = File(sound.export("{0}.mp3".format(uuid.uuid4().hex), format="mp3"))
            instance.save()
        instance.phone = campaign_obj.phone
        instance.save()
        relative_url = reverse('srm:api_marketing:campaigns:sample_voice_call', kwargs={'pk': instance.id})
        url = "https://%s%s" % (Site.objects.first().domain, relative_url)
        # async task
        voice_call(url=url, to_phone=instance.sample_phone.as_international, from_phone=instance.phone.twilio_number).execute()
        OVoiceCall.objects.create(campaign=campaign_obj, to=instance.sample_phone,
                                  from_no=instance.phone.twilio_number, charged=True)

    @action(methods=['post'], detail=False)
    def test_campaign(self, request, *args, **kwargs):
        """Test all campaign"""
        campaign_type, campaign_id = kwargs['campaign_type'], kwargs['campaign_id']
        campaign_obj = get_object_or_404(Campaign, pk=campaign_id)
        logger.info("Test {} campaign called for campaign_id {}".format(campaign_type, campaign_id))
        if campaign_obj.user.balance.get(campaign_type, 0) <= 0:
            return JsonResponse({'error': "You are out of {} credit.".format(campaign_type)})
        self.serializer_class = self.test_serializer_class_mapping.get(campaign_type)
        serializer_context = self.get_serializer_context()
        # Add is_sample to context so the serializer can verify that a sample_no was entered
        serializer_context.update({'is_sample': True})
        instance = self.model_mapping.get(campaign_type).objects.filter(campaign_id=campaign_id).last()
        serializer = self.serializer_class(data=request.data, instance=instance,
                                           context=serializer_context)
        serializer.is_valid(raise_exception=True)
        if not campaign_obj.phone:
            raise serializers.ValidationError("Campaign should have valid phone number.")
        data = serializer.validated_data
        if campaign_type == 'email':
            self._send_email_campaign(request, data, campaign_obj)
            return JsonResponse({'Success': 'Sample email sent successfully.'})
        elif campaign_type == 'sms':
            self._send_sms_campaign(campaign_obj, data)
            return JsonResponse({'Success': 'Sample sms sent successfully.'})
        elif campaign_type == 'mms':
            self._send_mms_campaign(campaign_obj, data, instance)
            return JsonResponse({'Success': 'Sample mms sent successfully.'})
        elif campaign_type == 'voice':
            self._send_voice_campaign(campaign_obj, serializer)
            return JsonResponse({'Success': 'Sample voice sent successfully.'})
        return JsonResponse({'error': "You are out of {} credit.".format(campaign_type)})

    @action(methods=['GET'], detail=False,
            url_path=r'(?P<campaigntype>(sms|mms|voice|email))')
    def get_all_specific_campaigns(self, request, *args, **kwargs):
        """
            Retrieves all the user's specific campaigns
            To get user's voice campaigns, /api/marketing/campaigns/voice/
            To get user's sms campaigns, /api/marketing/campaigns/sms/
        """
        campaign_type = kwargs.get('campaigntype')

        model = self.model_mapping.get(campaign_type)
        if not model:
            raise Http404('Campaign type does not exist')
        serializer = self.serializer_class_mapping.get(campaign_type)
        queryset = model.objects.filter(user=request.user)
        queryset = self.filter_campaign_queryset(queryset).order_by('-date_created')
        data = serializer(self.paginate_queryset(queryset), many=True, context=self.get_serializer_context()).data
        return self.get_paginated_response(data)

    @action(methods=['GET'], detail=False,
            url_path=r'(?P<campaigntype>(sms|mms|voice|email))/(?P<campaigndirection>(incoming|outgoing))')
    def get_specific_campaigns_incoming_and_outgoing(self, request, *args, **kwargs):
        """
            Retrieves all the user's specific campaigns
            To get user's voice campaigns,
            /api/marketing/campaigns/<voice or sms or mms or email>/<incoming or outgoing>/
        """
        direction = kwargs.get('campaigndirection')
        campaign_type = kwargs.get('campaigntype')

        model = self.model_mapping.get(campaign_type)
        if not model:
            raise Http404('Campaign type does not exist')

        key = f'{direction}_{campaign_type}'

        serializer = self.log_serializers_mapping.get(key)
        queryset = self.log_queryset_mapping.get(key)(self)
        data = serializer(self.paginate_queryset(queryset), many=True, context=self.get_serializer_context()).data
        return self.get_paginated_response(data)

    @action(methods=['POST'], detail=False,
            url_path='sms/incoming/reply')
    def reply_sms(self, request, *args, **kwargs):
        """
            Reply to a received SMS, collects payload {'isms_id': '', 'reply_data': ''}
        """
        reply_data = self.request.data.get("reply_data")
        isms_id = self.request.data.get("isms_id")
        queryset = ISMS.objects.filter(id=isms_id)

        user = UserProfile.get_instance(self.request.user)

        if not reply_data or not isms_id or not queryset.exists():
            return Response({"error": "SMS data not found"}, status=status.HTTP_400_BAD_REQUEST)
        if user.balance.get('sms', 0) <= 0:
            return Response({"error": "You are out of SMS credit."}, status=status.HTTP_400_BAD_REQUEST)
        isms = queryset.first()
        twilio_number = TwilioNumber.objects.filter(twilio_number=isms.to)
        if not twilio_number.exists():
            return Response({"error": "Invalid Campaign Number."}, status=status.HTTP_400_BAD_REQUEST)
        twilio_number = twilio_number[0]
        from_no = twilio_number.twilio_number
        to = isms.from_no
        reply = OSMS.objects.create(from_no=from_no, to=to, text=reply_data, is_reply_to=isms, campaign=isms.campaign)
        return Response(OutgoingSMSSerializer(reply).data, status=status.HTTP_200_OK)


class TriggerCampaignViewSet(AuthParsersMixin, CreateAPIView):
    serializer_class = TriggerCampaignSerializer

    def post(self, *args, **kwargs):
        data = self.request.data
        campaign_id = self.kwargs['campaign_id']
        try:
            campaign = get_object_or_404(Campaign, id=campaign_id, user=self.request.user)
            contact_ids = set()
            for contact_id in data.get("contacts", []):
                contact_ids.add(contact_id)
            for campaign_id in data.get("campaigns", []):
                tmp_obj = Campaign.objects.get(id=campaign_id, user=self.request.user)
                for cont_id in tmp_obj.contact_set.all().values_list("id", flat=True):
                    contact_ids.add(cont_id)
            for group_id in data.get("groups", []):
                tmp_obj = ContactGroup.objects.get(id=group_id, user=self.request.user)
                for cont_id in tmp_obj.contacts.all().values_list("id", flat=True):
                    contact_ids.add(cont_id)
            contact_ids_copy = contact_ids.copy()
            for contact_id in contact_ids:
                contact_obj = Contact.objects.get(id=contact_id)
                if not contact_obj.campaigns.filter(id=campaign.id).exists():
                    # Check if the campaign has been added to the contact already, if not add it and campaign would be
                    # triggered by signal, then remove it from the contacts list, so we can bulk trigger for the rest
                    # of the contacts
                    contact_obj.campaigns.add(campaign.id)
                    # We are using a copy of the set to avoid error 'set size changed during iteration'
                    contact_ids_copy.remove(contact_id)
            from ccc.campaigns.cloud_tasks import campaign_trigger
            campaign_trigger(contact_ids=list(contact_ids_copy), campaign_id=campaign_id).execute()
            result = {"msg": "Campaign trigger completed successfully"}
            response_status = 200
        except Campaign.DoesNotExist:
            result = {"error": "Campaign Not found"}
            response_status = 404
        except Exception as ex:
            logger.error(ex)
            result = {"error": "Unknown error. Please contact support", "msg": str(ex)}
            response_status = 500
        return JsonResponse(data=result, status=response_status)


class ArchiveCampaignViewSet(AuthParsersMixin, APIView):
    def get(self, request, pk=None, *args, **kwargs):
        """Archive campaign and release phone number"""
        campaign = get_object_or_404(Campaign, pk=pk, user=request.user)
        active = True if self.request.query_params.get('archive') else False
        if campaign.phone:
            campaign.phone.in_use = False
            campaign.phone.save()
            campaign.phone.update_twilio_urls_to_default()

        campaign.active = active
        campaign.phone = None
        campaign.save()

        # for recurring_fu in campaign.fucampaign_set.filter(recur=True):
        #     recurring_fu.unschedule_from_celery()
        return HttpResponseRedirect(reverse('srm:marketing:campaigns:list_campaigns'))


class VoiceCallContentView(APIView):
    """This path is called by twilio to get the content of the voice campaign (what should be said on the call)"""
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(VoiceCallContentView, self).dispatch(request, *args, **kwargs)

    def get_response(self, pk):
        resp = VoiceResponse()
        voice_campaign = get_object_or_404(VoiceCampaign, id=pk)
        if voice_campaign.audio:
            from ccc.utils.utils import validate_media_absolute_url
            url = validate_media_absolute_url(voice_campaign.audio.url)
            resp.play(url)
            resp.record(maxLength="120", action=reverse('srm:api_marketing:campaigns:handle_recording'))
        elif voice_campaign.voice_to_text:
            resp.say(voice_campaign.voice_to_text)
            resp.record(maxLength="120", action=reverse('srm:api_marketing:campaigns:handle_recording'))
        else:
            resp.say(" Thank you for calling Cloud Custom Connections."
                     "You will receive more information as soon as is available. Goodbye.")
        return HttpResponse(resp, content_type='application/xml')

    def post(self, request, pk):
        return self.get_response(pk)

    def get(self, request, pk):
        return self.get_response(pk)


class MappedKeywordViewSet(ModelViewSet):
    """
        request data = {
            'campaign': <campaign_pk>,
            'keywords': [<keyword1>, <keyword2>, ... ]
        }

        response data = {
            'campaign': {...}
            'keywords': [
                {...}
            ]
        }
    """

    def get_queryset(self):
        if self.request.method == 'GET':
            return Campaign.objects.filter(user=self.request.user, active=True, mappedkeywords__isnull=False).distinct()
        return MappedKeywords.objects.filter(campaign__user=self.request.user).order_by('-created_at')

    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CampaignKeywordsSerializer
        return MappedKeywordSerializer


class RemoveFileFromCampaignViewSet(AuthParsersMixin, APIView):
    """Class to remove detach file from objects"""
    model_mapping = {'voice': VoiceCampaign,
                     'mms': MMSCampaign}

    def get(self, request, *args, **kwargs):
        result = status_code = ''
        try:
            channel_type = kwargs['channel_type']
            obj = self.model_mapping[channel_type].objects.get(id=kwargs['pk'])
            fields = ['image1', 'image2', 'video']
            if channel_type == 'voice':
                fields = ['audio', 'voice_greeting_original', 'voice_greeting_converted']
            if channel_type == 'mms':
                fields = [request.query_params.get('field')]
            for field in fields:
                setattr(obj, field, None)
            obj.save()
            result = {"status": "success", "message": "File Removed successfully"}
            status_code = 200
        except Exception as ex:
            status_code = 500
            result = {"status": "failure", "message": "Error occurred while removing file {}".format(str(ex))}
        finally:
            return JsonResponse(data=result, status=status_code)


class SendSampleCallView(APIView):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(SendSampleCallView, self).dispatch(request, *args, **kwargs)

    def send_call(self, pk):
        resp = VoiceResponse()
        svc = get_object_or_404(SampleVoiceCall, id=pk)
        if svc.voice_greeting:
            from ccc.utils.utils import validate_media_absolute_url
            url = validate_media_absolute_url(svc.voice_greeting.url)
            resp.play(url)
            resp.record(maxLength="120", action=reverse('srm:api_marketing:campaigns:handle_recording'))

        elif svc.greeting_text:
            resp.say(svc.greeting_text)
            resp.record(maxLength="120", action=reverse('srm:api_marketing:campaigns:handle_recording'))

        return HttpResponse(resp, content_type='application/xml')

    def get(self, request, pk):
        return self.send_call(pk)

    def post(self, request, pk):
        return self.send_call(pk)


@method_decorator(csrf_exempt, name='dispatch')
class HandleRecordingView(View):
    def post(self, request, *args, **kwargs):
        recording_url = request.POST.get("RecordingUrl", None)
        record_sid = request.POST.get("RecordingSid", None)
        call_sid = request.POST.get("CallSid", None)
        duration = request.POST.get("RecordingDuration", None)
        calls = IVoiceCall.objects.filter(call_sid=call_sid)
        if calls:
            call = calls[0]
            call.recording_url = recording_url
            call.recording_duration = duration
            call.recording_sid = record_sid
            call.completed = True
            call.save()
        resp = VoiceResponse()
        resp.say("Goodbye")
        return HttpResponse(resp, content_type='application/xml')


@method_decorator(csrf_exempt, name='dispatch')
class HandleIncomingSMSView(View):
    def dispatch(self, request, *args, **kwargs):
        return super(HandleIncomingSMSView, self).dispatch(request, *args, **kwargs)

    def get_response(self):
        """ This function is the handler of incoming SMS-es for campagins.
                    This is called by twilio. """
        request = self.request
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

    def get(self, request):
        return self.get_response()

    def post(self, request):
        return self.get_response()


@method_decorator(csrf_exempt, name='dispatch')
class HandleIncomingCallView(View):
    def get_response(self):
        """ This function is the handler of incoming calls for campagins.
                    This is called by twilio. """
        request = self.request
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
                    red_no = phone.redirectnumber_set.first()
                    resp.dial(red_no.to_no)
                    resp.say('Goodbye')
                    return HttpResponse(resp, content_type='application/xml')
                cp = Campaign.objects.filter(phone=num[0], active=True).first()
                voice = cp.voicecampaign_set.last() if cp else None
                if voice:
                    if voice.audio:
                        url = validate_media_absolute_url(voice.audio.url)
                        resp.play(url)
                        resp.record(maxLength="120", action=reverse('srm:api_marketing:campaigns:handle_recording'))
                        # resp.gather(numDigits=1, action="/handle-key/", method="POST")
                    elif voice.voice_to_text:
                        resp.say(voice.voice_to_text)
                        # resp.gather(numDigits=1, action="/handle-key/", method="POST")
                        resp.record(maxLength="120", action=reverse('srm:api_marketing:campaigns:handle_recording'))
                    else:
                        resp.say("Thank you. Leave a message after the tone")
                        resp.record(maxLength="120", action=reverse('srm:api_marketing:campaigns:handle_recording'))
                else:
                    resp.say("Thank you. Leave a message after the tone. ")
                    resp.record(maxLength="120", action=reverse('srm:api_marketing:campaigns:handle_recording'))
            else:
                resp.say("Thank you. Leave a message after the tone. ")
                resp.record(maxLength="120", action=reverse('srm:api_marketing:campaigns:handle_recording'))
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

    def get(self, request):
        return self.get_response()

    def post(self, request):
        return self.get_response()


@method_decorator(csrf_exempt, name='dispatch')
class HandleKeyView(View):
    def get_response(self):
        request = self.request
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
            resp.record(maxLength="60", action=reverse('srm:api_marketing:campaigns:handle_recording'))
        return HttpResponse(resp, content_type='application/xml')

    def get(self, request):
        return self.get_response()

    def post(self, request):
        return self.get_response()
