from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ccc.packages.models import PackageType
from ccc.pages.forms import ContactUsForm


class SetTimeZoneView(View):
    def get(self, request):
        timezone_name = request.GET.get('timezone')
        request.session['timezone'] = timezone_name
        request.session['django_timezone'] = timezone_name
        return HttpResponse('set-time-zone', timezone_name)


class Home(View):
    def get(self, request):
        plans = PackageType.subscription_objects.all()
        contact_form = ContactUsForm()

        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('srm:users:users.dashboard'))

        return render(request, 'crm/home.html', locals())

    def post(self, request):
        contact_form = ContactUsForm(request.POST)
        if contact_form.is_valid():
            email = EmailMessage(
                "New contact form submission",
                contact_form.cleaned_data.get('content'),
                "Your website" + '',
                [settings.CONTACT_US_EMAIL],
                headers={'Reply-To': contact_form.cleaned_data.get('contact_email')}
            )
            email.send()
            return redirect(reverse('srm:home') + '?mail_sent=true')
        else:
            return render(request, 'crm/home.html', locals())


class TopSearchView(APIView):
    def get(self, request, *args, **kwargs):
        query_param = self.request.query_params.get('search')
        results = {'campaigns': [], 'surveys': []}
        if query_param:
            from ccc.campaigns.models import Campaign
            from ccc.marketing.campaigns.api.serializers import CampaignSerializer
            from ccc.marketing.surveys.api.serializers import SurveySerializer
            from ccc.survey.models import Survey
            from django.db.models import Q
            campaigns = Campaign.objects.filter(
                Q(name__icontains=query_param) |
                Q(keyword__icontains=query_param),
                user=request.user
            ).distinct().order_by('-created_at')[:10]
            surveys = Survey.objects.filter(
                user=request.user,
                title__icontains=query_param
            ).distinct().order_by('-created')[:10]
            results.update({'campaigns': CampaignSerializer(campaigns, many=True, context={'request': request}).data})
            results.update({'surveys': SurveySerializer(surveys, many=True).data})
        return Response(results, status=status.HTTP_200_OK)
