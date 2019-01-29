from django import forms

from ccc.digital_assets.models import (DigitalAttachment, DigitalAudio,
                                       DigitalImage, DigitalVideo)


class DigitalAssetsForm(forms.ModelForm):
    image_name = forms.CharField(max_length=100, required=False)
    audio = forms.FileField(required=False)
    audio_name = forms.CharField(max_length=100, required=False)
    video = forms.FileField(required=False)
    video_name = forms.CharField(max_length=100, required=False)
    attachment = forms.FileField(required=False)
    attachment_name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = DigitalImage
        exclude = ['user']

    def clean(self):
        data = self.cleaned_data
        if not any([data.get('audio'), data.get('video'), data.get('image'), data.get('attachment')]):
            raise forms.ValidationError("Attach at least one media file to save")
        if data.get('image') and not data.get('image_name'):
            raise forms.ValidationError("Please type a name for your image asset")

        if data.get('attachment') and not data.get('attachment_name'):
            raise forms.ValidationError("Please type a name for your attachment asset")

        if data.get('video') and not data.get('video_name'):
            raise forms.ValidationError("Please type a name for your video asset")

        if data.get('audio') and not data.get('audio_name'):
            raise forms.ValidationError("Please type a name for your audio asset")

        return self.cleaned_data

    def clean_video(self):
        video = self.cleaned_data['video']
        if video and video._size > (10 * 1024 * 1024):
            raise forms.ValidationError("Video size can't be more than 10 MB")
        return self.cleaned_data['video']

    def clean_audio(self):
        audio = self.cleaned_data['audio']
        if audio and audio._size > (10 * 1024 * 1024):
            raise forms.ValidationError("Audio size can't be more than 10 MB")
        return self.cleaned_data['audio']

    def clean_image(self):
        image = self.cleaned_data['image']
        if image and image._size > (10 * 1024 * 1024):
            raise forms.ValidationError("Image size can't be more than 10 MB")
        return self.cleaned_data['image']

    def clean_attachment(self):
        attachment = self.cleaned_data['attachment']
        if attachment and attachment._size > (10 * 1024 * 1024):
            raise forms.ValidationError("attachment size can't be more than 10 MB")
        return self.cleaned_data['attachment']


class BaseAssetForm(forms.ModelForm):
    class Meta:
        exclude = ['user']


class AudioForm(BaseAssetForm):
    class Meta(BaseAssetForm.Meta):
        model = DigitalAudio


class VideoForm(forms.ModelForm):
    class Meta(BaseAssetForm.Meta):
        model = DigitalVideo


class ImageForm(forms.ModelForm):
    class Meta(BaseAssetForm.Meta):
        model = DigitalImage


class AttachmentForm(forms.ModelForm):
    class Meta(BaseAssetForm.Meta):
        model = DigitalAttachment


class CreateAudioForm(BaseAssetForm):
    class Meta(BaseAssetForm.Meta):
        model = DigitalAudio

    def __init__(self, *args, **kwargs):
        super(CreateAudioForm, self).__init__(*args, **kwargs)
        self.fields['audio'].required = True
        self.fields['audio_name'].required = True


class CreateVideoForm(forms.ModelForm):
    class Meta(BaseAssetForm.Meta):
        model = DigitalVideo

    def __init__(self, *args, **kwargs):
        super(CreateVideoForm, self).__init__(*args, **kwargs)
        self.fields['video'].required = True
        self.fields['video_name'].required = True


class CreateImageForm(forms.ModelForm):
    class Meta(BaseAssetForm.Meta):
        model = DigitalImage

    def __init__(self, *args, **kwargs):
        super(CreateImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = True
        self.fields['image_name'].required = True


class CreateAttachmentForm(forms.ModelForm):
    class Meta(BaseAssetForm.Meta):
        model = DigitalAttachment

    def __init__(self, *args, **kwargs):
        super(CreateAttachmentForm, self).__init__(*args, **kwargs)
        self.fields['attachment'].required = True
        self.fields['attachment_name'].required = True
