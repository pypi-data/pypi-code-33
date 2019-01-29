import json
import random
import re
import string
from base64 import b64decode
from datetime import datetime

from django.apps import apps as django_app
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DeleteView, DetailView, FormView, UpdateView
from django.views.generic.base import TemplateView, View
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client as TwilioRestClient

from ccc.campaigns.cloud_tasks import (campaign_convert_audio_format,
                                       fu_campaign_convert_audio_format)
from ccc.campaigns.forms import (AssignContactsToCampaignForm,
                                 AssignKwywordsToCampaignForm,
                                 CampaignEmbedUpdateForm,
                                 CampaignSignupExtraFieldFormSet,
                                 CampaignUpdateForm, FollowUpCampaignForm,
                                 NotificationForm, attachment_formset_factory)
from ccc.campaigns.models import (Campaign, CampaignEmailTemplate, FUCampaign,
                                  MappedKeywords, Notify)
from ccc.campaigns.serializers import CampaignKeywordSerializer
from ccc.campaigns.utils.shortcut import (get_task_eta, remove_time_zone,
                                          save_or_update_premium_template)
from ccc.common.mixins import AjaxableResponseMixin, LoginRequiredMixin
from ccc.constants import schedular_mapping
from ccc.contacts.forms import ContactSignupForm
from ccc.contacts.models import Contact, ContactGroup
from ccc.packages.models import TwilioNumber
from ccc.packages.utils import get_phone_number
from ccc.template_design.models import TemplateDesign

ACCOUNT_SID = settings.TWILIO_SID
AUTH_TOKEN = settings.TWILIO_TOKEN

SHA1_RE = re.compile('^[a-f0-9]{40}$')

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


class NotificationView(SuccessMessageMixin, FormView):
    form_class = NotificationForm

    success_url = "/notify/"
    template_name = "ccc/users/notify.html"

    success_message = "Notification settings saved successfully"

    def get_initial(self):
        notify, created = Notify.objects.get_or_create(user=self.request.user)
        initial = dict()
        initial['duration'] = notify.duration
        initial['email'] = notify.email
        initial['sms'] = notify.sms
        initial['phone'] = notify.phone
        initial['mail'] = notify.mail
        initial['call'] = notify.call
        return initial

    def form_valid(self, form):

        n, created = Notify.objects.get_or_create(user=self.request.user)
        notify = form.save(commit=False)
        notify.user = self.request.user
        notify.pk = n.pk
        notify.save()

        return super(NotificationView, self).form_valid(form)


def decode_delay(seconds):
    delay = 0
    duration = 0
    if seconds >= 86400:  # days
        delay = seconds / 86400
        duration = 1
    elif seconds >= 3600:  # hours
        delay = seconds / 3600
        duration = 2
    elif seconds >= 60:  # minutes
        delay = seconds / 60
        duration = 3

    return {
        "delay": delay,
        "duration": duration
    }


class UpdateCampaignView(SuccessMessageMixin, LoginRequiredMixin, AjaxableResponseMixin, UpdateView):

    model = Campaign
    form_class = CampaignUpdateForm
    template_name = "ccc/campaigns/edit_campaign_new.html"
    success_url = "/campaigns/"

    success_message = "%(name)s was updated successfully"

    def get_form_kwargs(self):
        """Get form kwargs"""
        kwargs = super(UpdateCampaignView, self).get_form_kwargs()
        if kwargs.get('data'):

            kwargs['data']._mutable = True
            for key, value in schedular_mapping.items():
                campaign_trigger_date = kwargs.get('data', {}).get(value)
                if kwargs['data'].get(key) == '4':
                    kwargs['data'][value] = datetime.strptime(campaign_trigger_date, '%d %B %Y - %I:%M %p')
                else:
                    kwargs['data'][value] = None
            kwargs['data']._mutable = False

        if kwargs.get('instance'):
            for key, value in schedular_mapping.items():
                data = getattr(kwargs['instance'], value)
                if data:
                    setattr(kwargs['instance'], value, remove_time_zone(data))
        return kwargs

    def get_queryset(self):
        qs = super(UpdateCampaignView, self).get_queryset()
        return qs.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        Contact = django_app.get_model('contacts', 'Contact')
        context = super(UpdateCampaignView, self).get_context_data(**kwargs)
        context['phones'] = get_phone_number(self.request.user, campaign=self.object)
        mapped_keywords = MappedKeywords.objects.filter(
            campaign=self.object,
            is_active=True).values_list('keyword', flat=True)
        mapped_keywords = ", ".join([str(x) for x in mapped_keywords])
        context['mapped_keywords'] = mapped_keywords
        context['templates'] = CampaignEmailTemplate.objects.filter(
            Q(private_template=True, visible_to=self.request.user) |
            Q(private_template=False))
        context['premium_templates'] = TemplateDesign.objects.filter(user=self.request.user, is_active=True,
                                                                     is_public=False, template_type='email')
        context['recommended_premium_templates'] = TemplateDesign.objects.filter(user=self.request.user, is_active=True,
                                                                                 is_public=True, template_type='email')
        context['voice_delay'] = {"duration": 4} if self.object.voice_campaign_trigger_date else decode_delay(self.object.voice_delay)
        context['email_delay'] = {"duration": 4} if self.object.email_campaign_trigger_date else decode_delay(self.object.email_delay)
        context['sms_delay'] = {"duration": 4} if self.object.sms_campaign_trigger_date else decode_delay(self.object.sms_delay)
        context['mms_delay'] = {"duration": 4} if self.object.mms_campaign_trigger_date else decode_delay(self.object.mms_delay)

        context['attachment_formset'] = attachment_formset_factory(self.request.user)(
            instance=context['object'])

        context['template_values'] = {}
        contact_fields = [(f[1], "%s__%s" % (Contact.TEMPLATE_PREFIX, f[0]))
                          for f in Contact.TEMPLATE_FIELDS]

        # TODO: add extra fields
        context['template_values']['Contact'] = contact_fields

        return context

    def form_valid(self, form):
        formset = attachment_formset_factory(self.request.user)(
            self.request.POST, self.request.FILES, instance=self.object)

        if formset.is_valid():
            formset.save()
        else:
            return HttpResponseBadRequest(json.dumps(formset.errors))

        # phone_old can be None, when unachiving a campaign
        phone_old = TwilioNumber.objects.filter(campaign=self.object).first()
        # Save and update premium template
        if form.data.get('premium_email_template'):
            template_design = TemplateDesign.objects.get(
                pk=form.data.get('premium_email_template'),
                user=self.request.user,
                is_active=True,
                template_type='email')
            save_or_update_premium_template(self.object, template_design, 'email')

        super(UpdateCampaignView, self).form_valid(form)
        phone_new = self.object.phone

        if phone_new != phone_old:
            # phone_old can be None, when unarchiving a campaign
            if phone_old:
                phone_old.in_use = False
                phone_old.save()
                phone_old.update_twilio_urls_to_default()
            else:
                self.object.active = True
                self.object.save()

                for recurring_fus in self.object.fucampaign_set.filter(recur=True):
                    recurring_fus.schedule_for_celery()

            phone_new.in_use = True
            phone_new.save()

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

        if form.cleaned_data.get('voice_greeting_original', None) or recording_saved:
            # async task
            campaign_convert_audio_format(campaign_id=self.object.id).execute()

        return HttpResponse(json.dumps({"url": "/campaigns/"}))

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateCampaignView, self).dispatch(request, *args, **kwargs)


class FollowUpCampaignUpdateView(SuccessMessageMixin, LoginRequiredMixin, AjaxableResponseMixin, UpdateView):
    # TODO: reuse/combine with edit.FollowUpCampaignCreateView

    model = FUCampaign
    template_name = "ccc/modals/edit_fu.html"
    form_class = FollowUpCampaignForm
    success_message = "%(name)s was updated successfully"

    def get_queryset(self):
        qs = super(FollowUpCampaignUpdateView, self).get_queryset()
        return qs.filter(user=self.request.user)

    def get_success_url(self):
        campaign = get_object_or_404(
            Campaign, fucampaign__id=self.kwargs.get('pk'))
        return reverse("view_campaign", kwargs={'c_id': campaign.id})

    def get_context_data(self, **kwargs):
        # I have no idea why we need all this in cotext but we will continue
        # using them
        context = super(
            FollowUpCampaignUpdateView, self).get_context_data(**kwargs)
        context['templates'] = CampaignEmailTemplate.objects.filter(
            Q(private_template=True, visible_to=self.request.user) |
            Q(private_template=False))
        # that's a FUCampaign, not a regular Campaign!
        context['campaign'] = self.get_object()
        campaign = self.get_object().campaign

        context['attachment_formset'] = attachment_formset_factory(self.request.user, parent_class=FUCampaign)(
            instance=self.get_object())

        context['template_values'] = {}
        Contact = django_app.get_model('contacts', 'Contact')
        contact_fields = [(f[1], "%s__%s" % (Contact.TEMPLATE_PREFIX, f[0]))
                          for f in Contact.TEMPLATE_FIELDS]

        # TODO: add extra fields
        context['template_values']['Contact'] = contact_fields

        return context

    def form_valid(self, form):
        formset = attachment_formset_factory(self.request.user, parent_class=FUCampaign)(
            self.request.POST, self.request.FILES, instance=self.object)

        if formset.is_valid():
            formset.save()
        else:
            return HttpResponseBadRequest(json.dumps(formset.errors))

        campaign = get_object_or_404(
            Campaign, fucampaign__id=self.kwargs.get('pk'))
        follow_up_campaign = form.save(commit=False)
        follow_up_campaign.campaign = campaign

        follow_up_campaign.onleadcapture = False
        follow_up_campaign.specific = False
        follow_up_campaign.now4leads = False
        follow_up_campaign.recur = False
        follow_up_campaign.custom = False
        follow_up_campaign.sent = False
        schedule = form.cleaned_data.get('schedule')
        if schedule == '1':
            follow_up_campaign.onleadcapture = True

        elif schedule == '2':
            follow_up_campaign.specific = True

        elif schedule == '3':
            follow_up_campaign.now4leads = True

        elif schedule == '4':
            follow_up_campaign.send_at = form.cleaned_data.get(
                'recur_duration', None)
            follow_up_campaign.duration = form.cleaned_data.get(
                'recur_step', None)
            follow_up_campaign.recur = True

        elif schedule == '5':
            follow_up_campaign.custom = True

        voice = form.cleaned_data.get('voice_original', '')

        follow_up_campaign.email_body = form.cleaned_data.get(
            'e_greeting', None)
        follow_up_campaign.email_subject = form.cleaned_data.get(
            'e_greeting_subject', None)

        super(FollowUpCampaignUpdateView, self).form_valid(form)

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
                follow_up_campaign.voice_original = ContentFile(
                    audio_data, filename)
                recording_saved = True

        if voice or recording_saved:
            # async task
            fu_campaign_convert_audio_format(campaign_id=follow_up_campaign.id).execute()

        # send now if "Now for exisitng leads" schedule was selected
        if follow_up_campaign.now4leads:
            follow_up_campaign.send_now_for_existing_leads()

        if follow_up_campaign.recur:
            follow_up_campaign.schedule_for_celery()
        else:
            follow_up_campaign.unschedule_from_celery()
        follow_up_campaign.save()
        return HttpResponse(json.dumps({"url": self.get_success_url()}))


class FollowUpCampaignDeleteView(LoginRequiredMixin, AjaxableResponseMixin, DeleteView):
    model = FUCampaign

    def get_queryset(self):
        qs = super(FollowUpCampaignDeleteView, self).get_queryset()
        return qs.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('view_campaign', args=[self.object.campaigns.pk])


class UpdateCampaignSignupView(LoginRequiredMixin, UpdateView):

    model = Campaign
    form_class = CampaignEmbedUpdateForm
    template_name = "ccc/campaigns/edit_campaign_embed_form.html"

    success_message = "%(name)s was updated successfully"

    def get_success_url(self):
        return reverse('show_campaign_embed', kwargs={
            'pk': self.get_object().pk})

    def get_queryset(self):
        qs = super(UpdateCampaignSignupView, self).get_queryset()
        return qs.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super(UpdateCampaignSignupView, self).get_context_data(**kwargs)
        if self.request.POST:
            ctx['formset'] = CampaignSignupExtraFieldFormSet(
                self.request.POST, instance=self.object)
        else:
            ctx['formset'] = CampaignSignupExtraFieldFormSet(
                instance=self.object)

        return ctx

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        self.object = form.save()
        if formset.is_valid():
            formset.instance = self.object
            formset.save()

        return super(UpdateCampaignSignupView, self).form_valid(form)


class ShowCampaignEmbedForm(LoginRequiredMixin, DetailView):

    model = Campaign
    template_name = "ccc/campaigns/show_campaign_embed_form.html"

    def get_queryset(self):
        qs = super(ShowCampaignEmbedForm, self).get_queryset()
        return qs.filter(user=self.request.user)

    def get_embed_context_data(self, **kwargs):
        ctx = {}
        ctx['style_absolute_uri'] = self.request.build_absolute_uri(
            static('assets/css/ccc_embed_form_style.css'))
        ctx['script_absolute_uri'] = self.request.build_absolute_uri(
            static('assets/scripts/ccc_embed_form_scripts.js'))
        ctx['action_absolute_uri'] = self.request.build_absolute_uri(
            reverse('contact_signup', args=[self.get_object().pk]))
        ctx['campaign'] = self.get_object()
        ctx['form'] = ContactSignupForm(campaign=self.get_object())
        return ctx

    def get_context_data(self, **kwargs):
        ctx = super(ShowCampaignEmbedForm, self).get_context_data(**kwargs)

        ctx['embed_code'] = get_template('ccc/contacts/ccc_embed_form.html').render(self.get_embed_context_data())
        return ctx


class RemoveFileFromCampaign(LoginRequiredMixin, View):
    """Class to remove detach file from objects
    """
    model = Campaign

    def post(self, request, *args, **kwargs):
        try:
            object_id = request.POST.get('id')
            fields = str(request.POST.get('field', '')).split(',')
            obj = self.model.objects.get(id=object_id)
            for field in fields:
                setattr(obj, field, None)
            obj.save()
            result = {"status": "success",
                      "message": "File Removed successfully"}

        except Exception as ex:
            print("Exception in removing file ", ex)
            result = {"status": "failure",
                      "message": "Error occurred while removing file"}
        finally:
            return HttpResponse(json.dumps(result
                                           ))


class AssignContactsToCampaignView(LoginRequiredMixin, UpdateView):
    model = Campaign
    form_class = AssignContactsToCampaignForm
    template_name = 'ccc/campaigns/campaign_assign.html'
    success_url = reverse_lazy('campaigns')

    def get_form_kwargs(self):
        kwargs = super(AssignContactsToCampaignView, self).get_form_kwargs()
        kwargs.pop('instance', None)
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        qs = super(AssignContactsToCampaignView, self).get_queryset()
        return qs.filter(user=self.request.user)

    def form_valid(self, form):
        campaigns = self.request.POST.getlist('campaigns')
        groups = self.request.POST.getlist('groups')
        contacts = Contact.objects.filter(Q(campaigns__id__in=campaigns) | Q(groups__id__in=groups)).distinct()
        for contact in contacts:
            contact.campaigns.add(self.object)

        return HttpResponseRedirect(self.get_success_url())


class AssignKwywordsToCampaignView(LoginRequiredMixin, FormView):
    """
    Update UnverifiedPhone of user
    """
    form_class = AssignKwywordsToCampaignForm
    template_name = 'ccc/campaigns/edit_campaign_keywords.html'
    success_url = reverse_lazy('list_keywords_to_campaign')
    success_message = "Keyword(s) was updated successfully"

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(AssignKwywordsToCampaignView, self).get_initial()
        campaign_id = self.kwargs['campaign_id']
        mapped_keywords = MappedKeywords.objects.filter(
            campaign=campaign_id,
            is_active=True).values_list('keyword', flat=True)
        mapped_keywords = ", ".join([str(x) for x in mapped_keywords])
        initial['keywords'] = mapped_keywords

        return initial

    def dispatch(self, *args, **kwargs):
        dispatch = super(AssignKwywordsToCampaignView, self).dispatch(*args, **kwargs)
        campaign_id = self.kwargs['campaign_id']
        user = self.request.user
        if not user.campaign_set.filter(id=campaign_id, active=True).exists():
            from rest_framework import exceptions
            raise exceptions.PermissionDenied()
        return dispatch

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        user = self.request.user
        campaign_id = self.kwargs['campaign_id']
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'user': user,
            'campaign_id': campaign_id
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        form.save()
        messages.add_message(self.request, messages.SUCCESS, self.success_message)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(form=form))


class CampaignKeywordListView(LoginRequiredMixin, TemplateView):
    template_name = "ccc/campaigns/campaigns_keywrods.html"


class CampaignKeywordAPIListView(generics.ListAPIView):
    """
    Keyword search for corporate.
    """
    queryset = MappedKeywords.objects.all()
    serializer_class = CampaignKeywordSerializer
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CampaignKeywordAPIListView, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        campigns = self.request.user.campaign_set.filter(active=True)
        queryset = campigns
        return queryset


class TriggerCampaignContact(APIView):
    """
    Trigger Campaign
    """
    queryset = MappedKeywords.objects.all()
    serializer_class = CampaignKeywordSerializer
    paginate_by = 10

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TriggerCampaignContact, self).dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        data = self.request.data
        campaign_id = self.kwargs['campaign_id']
        try:
            campaign = Campaign.objects.get(id=campaign_id, user=self.request.user)
            contact_ids = set()
            for record in data.get("selected_contacts", []):
                if record.get("id"):
                    contact_ids.add(record["id"])

            for record in data.get("selected_campaigns", []):
                if record.get("id"):
                    tmp_obj = Campaign.objects.get(id=record["id"], user=self.request.user)
                    for cont_id in tmp_obj.contact_set.all().values_list("id", flat=True):
                        contact_ids.add(cont_id)

            for record in data.get("selected_groups", []):
                if record.get("id"):
                    tmp_obj = ContactGroup.objects.get(id=record["id"], user=self.request.user)
                    for cont_id in tmp_obj.contacts.all().values_list("id", flat=True):
                        contact_ids.add(cont_id)
            for contact_id in contact_ids:
                contact_obj = Contact.objects.get(id=contact_id)
                if not contact_obj.campaigns.filter(id=campaign.id).exists():
                    contact_obj.campaigns.add(campaign.id)
                else:
                    from ccc.contacts.models import contact_for_campaign_created
                    contact_for_campaign_created(sender=Campaign, instance=contact_obj, action="post_add",
                                                 reverse=True, model=Campaign, pk_set=set([campaign.id]), using=True,
                                                 manual_trigger=True)

            result = {"msg": "Campaign trigger completed successfully"}
        except Campaign.DoesNotExist:
            result = {"error": "Campaign Not found"}
        except Exception as ex:
            result = {"error": "Unknown error. Please contact support", "msg": ex.message}
        return Response(data=result)
