import datetime

import pytz
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (CreateView, ListView, UpdateView,
                                  View)
from rest_framework.viewsets import ModelViewSet

from ccc.common.mixins import LoginRequiredMixin
from ccc.digital_assets.forms import *
from ccc.digital_assets.models import (DigitalAttachment, DigitalAudio,
                                       DigitalImage, DigitalVideo)
from ccc.digital_assets.serializers import DigitalImageSerializer
from ccc.packages.decorators import check_user_subscription


class CreateDigitalAssetsView(LoginRequiredMixin, CreateView):
    template_name = "crm/digital_assets/assets_create.html"
    form_class = DigitalAssetsForm

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse("srm:digital-assets:user_assets_url")

    def form_valid(self, form):
        user = self.request.user
        data = form.cleaned_data
        audio, audio_name = data.get('audio'), data.get('audio_name')
        video, video_name = data.get('video'), data.get('video_name')
        image, image_name = data.get('image'), data.get('image_name')
        attachment, attachment_name = data.get('attachment'), data.get('attachment_name')
        if image:
            DigitalImage.objects.create(image=image, image_name=image_name, user=user)
            # save_image.delay(image, user.id, image_name)
        if audio:
            DigitalAudio.objects.create(audio=audio, audio_name=audio_name, user=user)
            # save_audio.delay(audio, user.id, audio_name)

        if video:
            DigitalVideo.objects.create(video=video, video_name=video_name, user=user)
            # save_video.delay(video=video, user_id=user.id)

        if attachment:
            # save_attachment.delay(attachment=attachment, user_id=user.id, attachment_name=attachment_name)
            DigitalAttachment.objects.create(
                attachment=attachment, user_id=user.id, attachment_name=attachment_name)

        return HttpResponseRedirect(self.get_success_url())


class UserDigitalAssetsView(LoginRequiredMixin, ListView):
    model = DigitalImage
    template_name = "crm/digital_assets/digital-assets.html"

    # template_name = "ccc/digital_assets/user-assets_list.html"

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        try:
            date = self.request.GET.get('date')
        except:
            pass

        if date is not None and date != '':
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
            date = pytz.utc.localize(date)
            end_date = date + datetime.timedelta(days=1)
            return DigitalImage.objects.filter(user=self.request.user, uploaded_at__range=[date, end_date])
        else:
            return DigitalImage.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(UserDigitalAssetsView, self).get_context_data(**kwargs)
        try:
            date = self.request.GET.get('date')
        except:
            pass
        if date is not None and date != '':
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
            date = pytz.utc.localize(date)
            end_date = date + datetime.timedelta(days=1)
            context['videos'] = DigitalVideo.objects.filter(user=user, uploaded_at__range=[date, end_date])
            context['audios'] = DigitalAudio.objects.filter(user=user, uploaded_at__range=[date, end_date])
            context['attachments'] = DigitalAttachment.objects.filter(user=user, uploaded_at__range=[date, end_date])
            context['total'] = DigitalVideo.objects.filter(user=user, uploaded_at__range=[date,
                                                                                          end_date]).count() + DigitalAudio.objects.filter(
                user=user, uploaded_at__range=[date, end_date]).count() + DigitalAttachment.objects.filter(user=user,
                                                                                                           uploaded_at__range=[
                                                                                                               date,
                                                                                                               end_date]).count() + self.get_queryset().count()
        else:
            context['videos'] = DigitalVideo.objects.filter(user=user)
            context['audios'] = DigitalAudio.objects.filter(user=user)
            context['attachments'] = DigitalAttachment.objects.filter(user=user)
            context['total'] = DigitalVideo.objects.filter(user=user).count() + DigitalAudio.objects.filter(
                user=user).count() + DigitalAttachment.objects.filter(user=user).count() + self.get_queryset().count()
        return context


class UpdateVideoView(LoginRequiredMixin, UpdateView):
    model = DigitalVideo
    template_name = "crm/digital_assets/update_video.html"
    form_class = VideoForm

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse("srm:digital-assets:user_assets_url")


class UpdateAudioView(LoginRequiredMixin, UpdateView):
    model = DigitalAudio
    template_name = "crm/digital_assets/update_audio.html"
    form_class = AudioForm

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse("srm:digital-assets:user_assets_url")


class UpdateImageView(LoginRequiredMixin, UpdateView):
    model = DigitalImage
    template_name = "crm/digital_assets/update_image.html"
    form_class = ImageForm

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse("srm:digital-assets:user_assets_url")


class UpdateAttachmentView(LoginRequiredMixin, UpdateView):
    model = DigitalAttachment
    template_name = "crm/digital_assets/update_attachment.html"
    form_class = AttachmentForm

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse("srm:digital-assets:user_assets_url")


class AudioListView(LoginRequiredMixin, ListView):
    model = DigitalAudio
    template_name = "ccc/digital_assets/audio_list.html"

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return DigitalAudio.objects.filter(user=self.request.user)


class VideoListView(LoginRequiredMixin, ListView):
    model = DigitalVideo
    template_name = "ccc/digital_assets/video_list.html"

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return DigitalVideo.objects.filter(user=self.request.user)


class ImageListView(LoginRequiredMixin, ListView):
    model = DigitalImage
    template_name = "ccc/digital_assets/image_list.html"

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return DigitalImage.objects.filter(user=self.request.user)


class AttachmentListView(LoginRequiredMixin, ListView):
    model = DigitalAttachment
    template_name = "ccc/digital_assets/attachment_list.html"

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return DigitalAttachment.objects.filter(user=self.request.user)


class DeleteVideoView(LoginRequiredMixin, View):
    model = DigitalVideo

    def post(self, request, *args, **kwargs):
        id_ = self.kwargs['pk']
        instance = DigitalVideo.objects.get(id=id_)
        instance.delete()
        messages.success(request, "Video Deleted Successfully")
        return HttpResponseRedirect(reverse("srm:digital-assets:user_assets_url"))

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(DeleteVideoView, self).dispatch(*args, **kwargs)


class DeleteAudioView(LoginRequiredMixin, View):
    model = DigitalAudio

    def post(self, request, *args, **kwargs):
        id_ = self.kwargs['pk']
        instance = DigitalAudio.objects.get(id=id_)
        instance.delete()
        messages.success(request, "Audio Deleted Successfully")
        return HttpResponseRedirect(reverse("srm:digital-assets:user_assets_url"))

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(DeleteAudioView, self).dispatch(*args, **kwargs)


class DeleteImageView(LoginRequiredMixin, View):
    model = DigitalImage

    def post(self, request, *args, **kwargs):
        id_ = self.kwargs['pk']
        instance = DigitalImage.objects.get(id=id_)
        instance.delete()
        messages.success(request, "Image Deleted Successfully")
        return HttpResponseRedirect(reverse("srm:digital-assets:user_assets_url"))

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(DeleteImageView, self).dispatch(*args, **kwargs)


class DeleteAttachmentView(LoginRequiredMixin, View):
    model = DigitalAttachment

    def post(self, request, *args, **kwargs):
        id_ = self.kwargs['pk']
        instance = DigitalAttachment.objects.get(id=id_)
        instance.delete()
        messages.success(request, "Attachment Deleted Successfully")
        return HttpResponseRedirect(reverse("srm:digital-assets:user_assets_url"))

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(DeleteAttachmentView, self).dispatch(*args, **kwargs)


class CreateAudioView(LoginRequiredMixin, CreateView):
    model = DigitalAudio
    form_class = CreateAudioForm
    template_name = "ccc/digital_assets/create_audio.html"

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        return HttpResponseRedirect(reverse('srm:digital-assets:audio_list_url'))


class CreateVideoView(LoginRequiredMixin, CreateView):
    model = DigitalVideo
    form_class = CreateVideoForm
    template_name = "ccc/digital_assets/create_video.html"

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        return HttpResponseRedirect(reverse('srm:digital-assets:video_list_url'))


class CreateImageView(LoginRequiredMixin, CreateView):
    model = DigitalImage
    form_class = CreateImageForm
    template_name = "ccc/digital_assets/create_image.html"

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        return HttpResponseRedirect(reverse('srm:digital-assets:image_list_url'))


class CreateAttachmentView(LoginRequiredMixin, CreateView):
    model = DigitalAttachment
    form_class = CreateAttachmentForm
    template_name = "ccc/digital_assets/create_attachment.html"

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        return HttpResponseRedirect(reverse('srm:digital-assets:attachment_list_url'))


class ImageListApi(ModelViewSet):
    """Image list api"""
    queryset = DigitalImage.objects.all()
    serializer_class = DigitalImageSerializer

    def get_queryset(self):
        queryset = super(ImageListApi, self).get_queryset()
        return queryset.filter(user=self.request.user)
