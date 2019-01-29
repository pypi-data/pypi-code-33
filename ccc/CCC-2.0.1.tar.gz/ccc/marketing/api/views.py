"""
API / Resources for Survey's API on Fusion APP.
"""
import re

from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from twilio.rest import Client as TwilioRestClient

from ccc.campaigns.models import Campaign, RedirectNumber
from ccc.marketing.api.serializers import (BuyTwilioNumberSerializer,
                                           RedirectNumberSerializer,
                                           TeamMemberSerializer,
                                           TeamSerializer,
                                           TwilioNumberFullSerializer,
                                           TwilioNumberSerializer,
                                           TwilioPhoneSerializer)
from ccc.mixin import AuthParsersMixin, StandardResultsSetPagination
from ccc.packages.models import TwilioNumber
from ccc.survey.models import Survey
from ccc.teams.models import Team, TeamMember
from ccc.users.models import UserProfile
from ccc.utils.utils import (onetime_charge_for_additional_numbers, )

ACCOUNT_SID = settings.TWILIO_SID
AUTH_TOKEN = settings.TWILIO_TOKEN
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


class AvailablePhoneNumbersListAPIView(AuthParsersMixin, generics.ListAPIView):
    """
    List all available Twilio phone numbers to use : /api/marketing/available-phone-numbers/
    in new surveys. add URL param '?fields=all to return all fields comprehensively'
    """
    serializer_class = TwilioNumberSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.GET.get('fields', None) == 'all':
            return TwilioNumberFullSerializer
        return TwilioNumberSerializer

    def get_queryset(self):
        if self.request.GET.get('campaign'):
            current_phone = Campaign.objects.filter(pk=self.request.GET.get('campaign')).first().phone
            # Filter numbers that are available for particular campaign, this needs to include the currently assigned
            return TwilioNumber.objects.filter(user=self.request.user).filter(
                Q(pk=current_phone.id) | Q(in_use=False)
            ).order_by('-last_updated')
        if self.request.GET.get('survey'):
            current_phone = Survey.objects.filter(pk=self.request.GET.get('survey')).first().phone
            # Filter numbers that are available for particular survey, including the currently assigned
            if current_phone:
                return TwilioNumber.objects.filter(user=self.request.user).filter(
                    Q(pk=current_phone.id) | Q(in_use=False)
                )
        return TwilioNumber.objects.filter(user=self.request.user, in_use=False).order_by('-last_updated')


class TeamViewSet(AuthParsersMixin, ModelViewSet):
    """" Team View """
    queryset = Team.objects.all().order_by('-date_created')
    serializer_class = TeamSerializer

    def get_queryset(self):
        # Todo create filters.
        queryset = super(TeamViewSet, self).get_queryset()
        return queryset.filter(creator=self.request.user)


class TeamMemberViewSet(AuthParsersMixin, ModelViewSet):
    """Add Team member to team"""
    queryset = TeamMember.objects.all().order_by('-date_created')
    serializer_class = TeamMemberSerializer


class GetPhoneNumberFromTwilioViewSet(AuthParsersMixin, generics.CreateAPIView):
    serializer_class = TwilioPhoneSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        number = data.get('number', '')
        num_type = data.get('num_type')
        country = data.get('country', "US")  # by default find US numbers
        numbers = []
        if num_type == 'international':
            if number != '':
                number = re.sub(r'\W+', '', number)
                client.api.available_phone_numbers(country).local.list(contains=number,
                                                                       sms_enabled='true',
                                                                       mms_enabled='true',
                                                                       voice_enabled='true')
            else:
                numbers = client.api.available_phone_numbers(country).local.list(sms_enabled='true',
                                                                                 mms_enabled='true',
                                                                                 voice_enabled='true')
        elif num_type == 'local':
            area_code = data.get('area_code')
            country = "US"
            if number != '':
                number = re.sub(r'\W+', '', number)
                numbers = client.api.available_phone_numbers(country).local.list(contains=number,
                                                                                 area_code=area_code,
                                                                                 sms_enabled='true',
                                                                                 mms_enabled='true',
                                                                                 voice_enabled='true'
                                                                                 )
            else:
                numbers = client.api.available_phone_numbers(country).local.list(contains=area_code,
                                                                                 area_code=area_code,
                                                                                 sms_enabled='true',
                                                                                 mms_enabled='true',
                                                                                 voice_enabled='true'
                                                                                 )
        elif num_type == 'toll_free':
            if number != '':
                number = re.sub(r'\W+', '', number)
                numbers = client.api.available_phone_numbers(country).toll_free.list(contains=number,
                                                                                     sms_enabled='true',
                                                                                     voice_enabled='true'
                                                                                     )
            else:
                area_code = data.get('area_code')
                if area_code:
                    numbers = client.api.available_phone_numbers(country).toll_free.list(area_code=area_code,
                                                                                         sms_enabled='true',
                                                                                         voice_enabled='true'
                                                                                         )
                else:
                    numbers = client.api.available_phone_numbers(country).toll_free.list(sms_enabled='true',
                                                                                         voice_enabled='true')
        else:
            numbers = client.api.available_phone_numbers("US").local.list(sms_enabled='true',
                                                                          mms_enabled='true',
                                                                          voice_enabled='true')
        if numbers:
            data = []
            for number in numbers:
                data.append(number.__dict__.get('_properties'))
        return JsonResponse(data=data, safe=False, status=200)


class BuyNumbersViewSet(AuthParsersMixin, generics.CreateAPIView):
    serializer_class = BuyTwilioNumberSerializer

    def post(self, request, *args, **kwargs):
        numbers = request.POST.getlist('numbers', [])
        if not numbers:
            return JsonResponse({'error': 'Choose at least one number'}, status=400)
        else:
            numbers_remaining = request.user_profile.balance['phones']
            if numbers_remaining < 0:
                numbers_remaining = 0
            purchased_numbers = request.user_profile.purchase_twilio_numbers(numbers=numbers)
            numbers_to_charge = len(purchased_numbers) - numbers_remaining
            onetime_charge_for_additional_numbers(request.user_profile, numbers_to_charge)
            return JsonResponse(data={'message': 'Number purchase'}, status=200)


class CommunicationReportsViewSet(AuthParsersMixin, generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        campaign_id = request.query_params.get('campaign_id')
        static_data = {
            'account_balance': {
                'voice': None,
                'sms': None,
                'mms': None,
                'email': None
            },
            'sent': {
                'voice': None,
                'sms': None,
                'mms': None,
                'email': None
            },
            'receive': {
                'voice': None,
                'sms': None,
                'mms': None,
                'email': None
            },
            'email_analytics': []
        }
        campaign = None
        user = UserProfile.objects.get(pk=request.user.id)
        data = user.usage_stats(campaign)
        static_data['account_balance'].update({'email': data.get('email'),
                                               'sms': data.get('sms'),
                                               'mms': data.get('mms'),
                                               'voice': data.get('phones')})
        static_data['sent'].update({'email': data.get('email_usage')[0],
                                    'sms': data.get('sms_usage')[0],
                                    'mms': data.get('mms_usage')[0],
                                    'voice': data.get('voice_usage')[0]})
        static_data['receive'].update({'email': data.get('email_usage')[1],
                                       'sms': data.get('sms_usage')[1],
                                       'mms': data.get('mms_usage')[1],
                                       'voice': data.get('voice_usage')[1]})
        if campaign_id:
            campaign = Campaign.objects.get(id=campaign_id)
        static_data['email_analytics'] = user.get_email_data(campaign=campaign, is_email_statics=True)
        return JsonResponse(data=static_data)


class UnRedirectedNumbers(generics.ListAPIView):
    def get_queryset(self):
        return TwilioNumber.objects.filter(user=self.request.user, redirectnumber__isnull=True)

    serializer_class = TwilioNumberFullSerializer


class RedirectNumberViewSet(ModelViewSet):
    queryset = RedirectNumber.objects.all().order_by('-date_created')
    serializer_class = RedirectNumberSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return RedirectNumber.objects.filter(user=self.request.user).order_by('-date_created')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EngagedPhoneNumberListView(AuthParsersMixin, generics.ListAPIView):
    """Add params 'engaged_by=campaign or engaged_by=survey to filter by what they are engaged with'"""
    queryset = TwilioNumber.objects.all()

    def get_queryset(self):
        engaged_by = self.request.query_params.get('engaged_by')
        queryset = super(EngagedPhoneNumberListView, self).get_queryset()
        if engaged_by == 'campaign':
            return queryset.filter(user=self.request.user, campaign__isnull=False).order_by('-last_updated').distinct()
        if engaged_by == 'survey':
            return queryset.filter(user=self.request.user, surveys__isnull=False).order_by('-last_updated').distinct()
        return queryset.filter(in_use=True).order_by('-last_updated').distinct()

    serializer_class = TwilioNumberFullSerializer


class PurchasedPhoneNumberListView(AuthParsersMixin, generics.ListAPIView):
    def get_queryset(self):
        return TwilioNumber.objects.filter(user=self.request.user).order_by('-last_updated').distinct()

    serializer_class = TwilioNumberFullSerializer
    pagination_class = StandardResultsSetPagination


class ReleaseNumberView(AuthParsersMixin, APIView):
    def get(self, request, *args, **kwargs):
        phone_number = get_object_or_404(TwilioNumber, pk=kwargs.get('pk'))
        if phone_number.campaign_set.exists() or phone_number.surveys.exists():
            return JsonResponse({'message': 'Number could not be released because it is still in use by a '
                                            'survey or a campaign'}, status=400)
        phone_number.task_release_twilio_number()
        return JsonResponse({'message': 'Number has been released'}, status=200)
