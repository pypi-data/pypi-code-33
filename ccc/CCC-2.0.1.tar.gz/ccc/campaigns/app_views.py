import json
import os

from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic.base import TemplateView

from ccc.campaigns.forms import EmailAttachmentsForm
from ccc.campaigns.models import (Campaign, CampaignEmailTemplate,
                                  TemplateImages)
from ccc.common.mixins import AjaxableResponseMixin, LoginRequiredMixin


def handle_uploaded_file(f):
    filename, extension = os.path.splitext(f.name)
    full_path = "media/campaigns/email/templates/%s" % f.name
    with open(full_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return full_path


class UploadImageView(LoginRequiredMixin, AjaxableResponseMixin, CreateView):

    form_class = EmailAttachmentsForm
    model = TemplateImages
    template_name = "base_attachments.html"

    def form_valid(self, form):
        number = form.cleaned_data['number']
        try:
            instance = TemplateImages.objects.get(
                number=number, campaign_id=self.kwargs['campaign_id'])
            image = form.cleaned_data['image']
            description = form.cleaned_data['description']
            instance.image = image
            url = form.cleaned_data['url']
            attachment = form.cleaned_data['attachment']
            instance.url = url
            instance.description = description
            if attachment:
                attachment = handle_uploaded_file(attachment)
            instance.attachment = attachment
            instance.save()
        except TemplateImages.DoesNotExist:
            campaign = Campaign.objects.get(id=self.kwargs['campaign_id'])
            instance = form.save(commit=False)
            instance.campaign_id = self.kwargs['campaign_id']
            instance.template = campaign.template
            instance.save()
        url = reverse(
            "upload_template_images_url", args=([self.kwargs['campaign_id']]))
        return HttpResponse(json.dumps({"message": "Media Uploaded successfully", 'url': url}))

    def get_media_template(self, path):
        return path.split('/')[-1]

    def get_context_data(self, **kwargs):
        user = self.request.user
        HOSTNAME = Site.objects.get_current().domain
        campaign_id = self.kwargs.get('campaign_id')
        camapign_obj = get_object_or_404(Campaign, pk=campaign_id)
        context = super(UploadImageView, self).get_context_data(**kwargs)
        context['template'] = self.get_media_template(
            camapign_obj.template.template.url)
        context['host'] = HOSTNAME + "/" + "static/"
        context['STATIC_URL'] = '/static/'
        context['template_obj'] = camapign_obj.template
        context['object'] = camapign_obj.template
        context['objects'] = camapign_obj.templateimages_set.all()
        context['digital_videos'] = user.digitalvideo_set.all()
        context['digital_audios'] = user.digitalaudio_set.all()
        context['digital_images'] = user.digitalimage_set.all()
        context['digital_attachment'] = user.digitalattachment_set.all()
        try:
            context['logo'] = camapign_obj.logo.url
        except BaseException:
            context['logo'] = None
        context['company'] = camapign_obj.company
        context['e_greeting'] = camapign_obj.e_greeting
        context['name'] = camapign_obj.name
        context['username'] = camapign_obj.user.first_name
        context['hostname'] = HOSTNAME
        context['protocol'] = "http://"

        return context


class TemplateImagesView(LoginRequiredMixin, AjaxableResponseMixin, CreateView):
    form_class = EmailAttachmentsForm
    model = TemplateImages
    template_name = "base_attachments.html"

    def form_valid(self, form):
        user = self.request.user
        number = form.cleaned_data['number']
        template_id = self.kwargs['template_id']

        try:
            instance = TemplateImages.objects.get(
                number=number, template_id=template_id, user=user)
            image = form.cleaned_data['image']
            description = form.cleaned_data['description']
            instance.image = image
            url = form.cleaned_data['url']
            attachment = form.cleaned_data['attachment']
            instance.url = url
            instance.description = description
            if attachment:
                attachment = handle_uploaded_file(attachment)
            instance.attachment = attachment
            instance.save()

        except TemplateImages.DoesNotExist:
            template = CampaignEmailTemplate.objects.get(id=template_id)
            instance = form.save(commit=False)
            instance.template_id = template_id
            instance.user = user
            instance.save()

        return HttpResponse(json.dumps({"message": "Media Uploaded successfully", "id": instance.id}))

    def get_media_template(self, path):
        return path.split('/')[-1]

    def get_context_data(self, **kwargs):
        user = self.request.user
        HOSTNAME = Site.objects.get_current().domain
        template_id = self.kwargs.get('template_id')
        template = get_object_or_404(CampaignEmailTemplate, pk=template_id)
        context = super(TemplateImagesView, self).get_context_data(**kwargs)
        context['template'] = self.get_media_template(template.template.url)
        context['host'] = HOSTNAME + "/" + "static/"
        objects = TemplateImages.objects.filter(template=template, user=user)
        context['objects'] = objects

        if context['objects']:
            camapign_obj = context['objects'].first().campaign

            try:
                context['logo'] = camapign_obj.logo.url
            except BaseException:
                context['logo'] = None
            context['company'] = camapign_obj.company
            context['e_greeting'] = camapign_obj.e_greeting
            context['name'] = camapign_obj.name
            context['username'] = camapign_obj.user.first_name
            context['hostname'] = HOSTNAME
            context['protocol'] = "http://"
            context['path'] = camapign_obj.logo.path
        # for i in range(1, template.number_of_max_uploads+1):
        #     context['objects'].append({})
        # for obj in objects:
        #     context['objects'][obj.number - 1] =  obj

        return context


class CampaignTemplates(TemplateView):
    template_name = "ccc/campaigns/landing_pages/template1.html"
