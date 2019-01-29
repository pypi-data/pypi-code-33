import json
from math import ceil

from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from twilio.jwt.client import ClientCapabilityToken
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

from ccc.campaigns.cloud_tasks import send_email
from ccc.campaigns.models import OVoiceCall
from ccc.click_to_call.cloud_tasks import (convert_audio_personalized_message,
                                           save_call_recording,
                                           throttle_send_personalized_messages)
from ccc.click_to_call.models import (AssociateMasterList, AutoDialerList,
                                      PersonalizedMessage, TwimlApplication)
from ccc.click_to_call.serializers import (AutoDialerListSerializer,
                                           AutoDialerMasterListSerializer)
from ccc.common.mixins import LoginRequiredMixin
from ccc.contacts.models import Contact
from ccc.marketing.autodialer.api.serializers import (PersonalizedMessageSerializer,
                                                      SendPersonalizedMessageSerializer)
from ccc.mixin import AuthMixin, StandardResultsSetPagination
from ccc.packages.models import TwilioNumber
from ccc.utils.utils import validate_media_absolute_url


class AutoDialListViewSet(AuthMixin, viewsets.ModelViewSet):
    def get_queryset(self):
        return AutoDialerList.objects.filter(associated_to__user=self.request.user)

    serializer_class = AutoDialerListSerializer
    pagination_class = StandardResultsSetPagination


class AssociateMasterListViewSet(AuthMixin, viewsets.ModelViewSet):
    def get_queryset(self):
        return AssociateMasterList.objects.filter(user=self.request.user).order_by('-created_at')

    serializer_class = AutoDialerMasterListSerializer
    pagination_class = StandardResultsSetPagination

    @action(methods=['GET'], detail=True, url_path='auto-dial-list')
    def get_auto_dial_list(self, request, *args, **kwargs):
        queryset = self.get_object().autodialerlist_set.all().order_by('-created_at')
        queryset = self.paginate_queryset(queryset)
        serializer = AutoDialerListSerializer(queryset, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class HandlePhoneCallView(View):
    def get(self, request, *args, **kwargs):
        """This view is entered in voice handler in the twimlApp and it is called by twilio"""
        """Returns TwiML instructions to Twilio's POST requests"""
        # If the browser sent a phoneNumber param, we know this request
        # is a support agent trying to call a customer's phone
        dest_number = ''
        if 'PhoneNumber' in request.GET:
            dest_number = request.GET["PhoneNumber"]
        else:
            # This will raise a error on twilio itself
            pass
        resp = VoiceResponse()
        from_no = request.GET["from_no"] if request.GET.get(
            "from_no") else "+441242305348"
        phone = TwilioNumber.objects.filter(twilio_number=from_no).first()
        user = phone.user if phone else None
        if not user:
            resp.say('This number selected for this call is not assigned to any user or has been released')
            return HttpResponse(str(resp))
        if user.balance.get('talktime', 0) <= 0:
            resp.say('Sorry, You do not have sufficient talktime to make this call')
            return HttpResponse(str(resp))
        max_duration = user.balance.get('talktime', 0) * 60
        o_voice = OVoiceCall.objects.create(campaign=phone.campaign_set.last(), from_no=from_no, to=dest_number,
                                            status='Unconnected')
        callback_url = reverse("srm:api_marketing:autodialer:handle-phone-call-call-back",
                               kwargs={"twilio_number_id": phone.id, 'outgoing_voice_id': o_voice.id})
        with resp.dial(dest_number, caller_id=from_no, action=callback_url,
                       method="GET", time_limit=max_duration, record=True,
                       recording_status_callback=reverse('srm:api_marketing:autodialer:handle-recording-callback',
                                                         kwargs={'outgoing_voice_id': o_voice.id}),
                       recording_status_callback_method='GET') as r:
            pass
        return HttpResponse(str(resp))


@method_decorator(csrf_exempt, name='dispatch')
class HandlePhoneCallCallBackView(View):
    """Class to handle auto dial callback from twilio
    """

    def get(self, request, *args, **kwargs):
        ovoice_id = kwargs.get('outgoing_voice_id')
        status = self.request.GET.get('DialCallStatus')
        call_sid = self.request.GET.get('CallSid')
        call_duration = self.request.GET.get("DialCallDuration", 0)
        call_sent = status == 'completed'
        call_duration_in_mins = ceil(float(call_duration) / 60.0)
        OVoiceCall.objects.filter(pk=ovoice_id).update(status=status, call_sid=call_sid,
                                                       duration=call_duration, sent=call_sent,
                                                       raw_data=str(request.GET))
        twilio_number_id = kwargs["twilio_number_id"]
        queryset = TwilioNumber.objects.filter(pk=twilio_number_id)
        if queryset.exists():
            twilio_obj = queryset[0]
            user = twilio_obj.user
            from ccc.packages.models import Credit
            credits_qs = Credit.objects.filter(package__user=user)
            if credits_qs.exists():
                credit_obj = credits_qs.latest("id")
                credit_obj.talktime = credit_obj.talktime - call_duration_in_mins
                credit_obj.save()
        return HttpResponse(str(VoiceResponse()))


class RetrieveCapabilityToken(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        """Returns a Twilio Client token"""
        # Create a TwilioCapability token with our Twilio API credentials
        ACCOUNT_SID = settings.TWILIO_SID
        AUTH_TOKEN = settings.TWILIO_TOKEN
        capability = ClientCapabilityToken(
            ACCOUNT_SID,
            AUTH_TOKEN)
        # Create a Twiml application for this instance if none exists
        twiml_application = TwimlApplication.objects.all()
        if twiml_application.exists():
            APPLICATION_SID = twiml_application.first().sid
        else:
            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            voice_url = 'https://{}{}'.format(Site.objects.get_current().domain,
                                              reverse('srm:api_marketing:autodialer:handle-phone-call'))
            application = client.applications.create(Site.objects.get_current().domain, voice_method='GET',
                                                     voice_url=voice_url)
            TwimlApplication.objects.create(sid=application.sid)
            APPLICATION_SID = application.sid
        # Allow our users to make outgoing calls with Twilio Client
        capability.allow_client_outgoing(APPLICATION_SID)
        # If the user is on the support dashboard page, we allow them to accept
        # incoming calls to "support_agent"
        # (in a real app we would also require the user to be authenticated)
        if request.GET.get('forPage') == reverse('srm:users:users.dashboard'):
            capability.allow_client_incoming('support_agent')
        else:
            # Otherwise we give them a name of "customer"
            capability.allow_client_incoming('customer')
        # Generate the capability token
        token = capability.to_jwt()
        return HttpResponse(json.dumps({'token': token.decode('utf-8')}), content_type="application/json")


class HandlePhoneCallRecordCallbackView(View):
    def get(self, request, outgoing_voice_id):
        url = request.GET.get('RecordingUrl')
        save_call_recording(url=url, o_voice_id=outgoing_voice_id).execute()
        return HttpResponse(status=200)


class PersonalizedMessagesView(AuthMixin, ModelViewSet):
    serializer_class = PersonalizedMessageSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        search = self.request.query_params.get('search')
        type_ = self.request.query_params.get('type')
        queryset = PersonalizedMessage.objects.filter(user=self.request.user)
        if search:
            queryset = queryset.filter(name__icontains=search)
        if type_:
            queryset = queryset.filter(type__iexact=type_)
        return queryset.order_by('is_default', '-created')

    def perform_create(self, serializer):
        msg = serializer.save(user=self.request.user)
        convert_audio_personalized_message(msg_id=msg.id).execute()

    @action(['GET'], detail=False, url_path='all')
    def get_by_type_non_paginated(self, request, **kwargs):
        type_ = self.request.query_params.get('type')
        queryset = PersonalizedMessage.objects.filter(user=request.user)
        if type_:
            queryset = PersonalizedMessage.objects.filter(user=request.user, type=type_)
        queryset = queryset.order_by('-is_default', '-created')
        data = PersonalizedMessageSerializer(queryset, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(['GET'], detail=True, url_path='set-as-default')
    def set_default(self, request, **kwargs):
        PersonalizedMessage.objects.filter(user=self.request.user, is_default=True,
                                           type=self.get_object().type).update(is_default=False)
        PersonalizedMessage.objects.filter(pk=kwargs.get('pk')).update(is_default=True)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    @action(['POST'], detail=True, url_path='send')
    def send(self, request, *args, **kwargs):
        from_no = self.request.data.get('from_')
        contacts = self.request.data.get('contacts')
        type_ = self.get_object().type
        if SendPersonalizedMessageSerializer(data=request.data).is_valid(raise_exception=True):
            recipient_count = len(contacts) if contacts else 1
            from ccc.users.models import UserProfile
            user = UserProfile.objects.get(pk=self.request.user.id)
            if type_ == 'voice':
                if user.balance.get('talktime', 0) > (recipient_count - 1):
                    throttle_send_personalized_messages(contact_ids=contacts, type_=type_, from_=from_no,
                                                        personal_msg_id=self.get_object().id).execute()
                else:
                    return Response({'error': 'You do not sufficient balance for this action'},
                                    status=status.HTTP_400_BAD_REQUEST)
            elif type_ == 'sms':
                if user.balance.get('sms', 0) > (recipient_count - 1):
                    throttle_send_personalized_messages(contact_ids=contacts, type_=type_, from_=from_no,
                                                        personal_msg_id=self.get_object().id).execute()
                else:
                    return Response({'error': 'You do not sufficient balance for this action'},
                                    status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class TwilioGetPersonalizedMessage(View):
    def get(self, request, pk):
        resp = VoiceResponse()
        pm = PersonalizedMessage.objects.get(pk=pk)
        if pm.audio:
            resp.play(validate_media_absolute_url(pm.audio.url))
        else:
            resp.say(pm.text)
        return HttpResponse(str(resp))


class EmailPhoneConversationView(APIView):
    def post(self, request, *args, **kwargs):
        type_ = request.data.get('type', None)
        email_body = request.data.get('body', None)
        contact = request.data.get('contact', None)
        call_id = kwargs.get('pk')
        o_voice = get_object_or_404(OVoiceCall, pk=call_id)
        user = TwilioNumber.objects.get(twilio_number=o_voice.from_no).user
        if type_ == 'me':
            send_email(subject=f'Phone conversation with {o_voice.to}', email_body=email_body,
                       from_=settings.DEFAULT_FROM_EMAIL, to=user.email, context={}).execute()
        else:
            try:
                contact = Contact.objects.get(phone=contact)
                if not contact.email:
                    return Response({'non_field_errors': ['This contact does not have an associated email address']},
                                    status=status.HTTP_400_BAD_REQUEST)
            except Contact.DoesNotExist:
                return Response({'non_field_errors': ['This number is not in your contact list']},
                                status=status.HTTP_400_BAD_REQUEST)
            email_body = f'<h3>Hi {contact.first_name}</h3><div>Here is a summary of your phone conversation with' \
                         f' our representative</div>' + email_body
            send_email(subject=f'Your phone conversation with {user.first_name}', email_body=email_body,
                       from_=settings.DEFAULT_FROM_EMAIL, to=contact.email, context={}).execute()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
