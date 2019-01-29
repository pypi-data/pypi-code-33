from __future__ import unicode_literals

from datetime import datetime

import pendulum
from django.conf import settings
from django.http import JsonResponse, QueryDict
from django.http.response import HttpResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView, FormView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator

from ccc.campaigns.models import Campaign
from ccc.campaigns.utils.shortcut import save_or_update_premium_template
from ccc.common.mixins import LoginRequiredMixin
from ccc.packages.decorators import check_user_subscription
from ccc.template_design.forms import (EmailTemplateDesignForm,
                                       WebTemplateDesignForm)
from ccc.template_design.gcloud_tasks import (email_and_web_analytics,
                                              save_contact,
                                              save_email_template)
from ccc.template_design.models import (CampaignTemplateDesign,
                                        LandingPageFormData, TemplateDesign)
from slugify import slugify


class TemplateDesignDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'crm/template_design/email_template_form.html'
    model = TemplateDesign
    success_url = reverse_lazy('srm:template-design:design_landing_page')

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class MyPageTemplateView(TemplateView):
    template_name = 'crm/template_design/my_page.html'
    model = TemplateDesign

    @method_decorator(csrf_exempt)
    @method_decorator(check_user_subscription)
    def dispatch(self, request, *args, **kwargs):
        return super(MyPageTemplateView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        campaign_template = CampaignTemplateDesign.objects.get(template__pk=kwargs.get('pk'))
        LandingPageFormData.objects.create(template=campaign_template.template, data=request.POST.dict())

        save_contact(user_id=request.user.id, campaign_id=campaign_template.campaign_id, data=request.POST.dict())

        return self.get(request, *args, **kwargs)

    def get_analytics_data(self, obj):
        qdict = QueryDict('', mutable=True)
        qdict.update({'type': 'web', 'template_id': obj.id, 'template_name': obj.name})
        return qdict.urlencode()

    def get_context_data(self, **kwargs):
        context = super(MyPageTemplateView, self).get_context_data(**kwargs)
        obj = self.model.objects.get(pk=kwargs['pk'])
        context['analytic_data'] = self.get_analytics_data(obj)
        context['object_data'] = obj
        if self.request.method == 'POST':
            confirmation_message = "Thanks your registration recieved"
            context['confirmation_message'] = confirmation_message
        return context


class TemplateDesignFormView(LoginRequiredMixin, FormView):
    """Template Design View """
    template_name = 'crm/template_design/email_template_form.html'
    form_class = EmailTemplateDesignForm
    model = TemplateDesign
    success_url = reverse_lazy('srm:template-design:design_landing_page')

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_instance(self, pk):
        """Get instance"""
        return self.model.objects.get(pk=pk)

    def get_context_data(self, **kwargs):
        context = super(TemplateDesignFormView, self).get_context_data(**kwargs)
        context['client_id'] = settings.BEE_CLIENT_ID
        context['client_secret'] = settings.BEE_SECRET_ID
        return context

    def get_form_kwargs(self):
        kwargs = super(TemplateDesignFormView, self).get_form_kwargs()
        pk = self.kwargs.get('pk')
        if pk:
            if not (self.request.method == 'POST' and self.get_instance(pk).is_public):
                kwargs.update({'instance': self.get_instance(pk)})
        return kwargs

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(TemplateDesignFormView, self).get_initial()
        initial['user'] = self.request.user
        pk = self.kwargs.get('pk')
        if pk and self.get_instance(pk).is_public and not (self.request.method == 'POST'):
            initial['name'] = ''
        return initial

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        form.save(commit=False)
        form.instance.update_thumbnail()
        form.instance.name_slug = slugify(form.instance.name)
        form.save()
        # Async task
        save_email_template(**{'id': form.instance.id}).execute()
        next_url = self.request.GET.get('next')

        if next_url:
            self.success_url = next_url
        return JsonResponse({'next_url': self.get_success_url()})


class WebTemplateDesignFormView(TemplateDesignFormView):
    template_name = 'crm/template_design/web_template_form.html'
    form_class = WebTemplateDesignForm

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(WebTemplateDesignFormView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        pk = self.kwargs.get('pk')
        initial = super(WebTemplateDesignFormView, self).get_initial()
        template_type = 'web'
        initial['template_type'] = 'web'
        if pk and self.request.method == 'GET':
            campaign_tem_design = self.get_instance(
                pk).campaigntemplatedesign_set.filter(template_type=template_type).first()
            if campaign_tem_design:
                initial['campaign'] = campaign_tem_design.campaign_id
        return initial

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        form.save()
        campaign = Campaign.objects.get(pk=form.data['campaign'])
        save_or_update_premium_template(campaign, form.instance, 'web')
        # form.instance.update_thumbnail()

        # Async task
        save_email_template(**{'id': form.instance.id}).execute()

        next_url = self.request.GET.get('next')

        if next_url:
            self.success_url = next_url
        return JsonResponse({'next_url': self.get_success_url()})


class TemplateDesignListView(LoginRequiredMixin, ListView):
    """Template Design View """
    # template_name = 'ccc/template_design/base.html'
    template_name = 'crm/landing-page.html'
    model = TemplateDesign
    queryset = TemplateDesign.objects.all()

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super(TemplateDesignListView, self).get_queryset()
        return queryset.filter(user=self.request.user, is_active=True, is_public=False, template_type="web")

    def get_context_data(self, **kwargs):
        context = super(TemplateDesignListView, self).get_context_data(**kwargs)
        context['public_web_template'] = TemplateDesign.objects.filter(
            is_active=True, is_public=True, template_type="web")
        return context


class EmailAndWebAnalyticsView(ListView):
    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = request.GET.dict()
        data.update({'created_date': datetime.utcnow().replace(tzinfo=pendulum.timezone('UTC')).isoformat(),
                     'ip_address': self.request.META.get('HTTP_X_REAL_IP')})

        # async task
        email_and_web_analytics(**data).execute()
        return HttpResponse("Done")
