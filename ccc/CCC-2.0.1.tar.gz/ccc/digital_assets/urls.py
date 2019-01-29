from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from ccc.digital_assets.views import (AttachmentListView, AudioListView,
                                      CreateAttachmentView, CreateAudioView,
                                      CreateDigitalAssetsView, CreateImageView,
                                      CreateVideoView, DeleteAttachmentView,
                                      DeleteAudioView, DeleteImageView,
                                      DeleteVideoView, ImageListApi,
                                      ImageListView, UpdateAttachmentView,
                                      UpdateAudioView, UpdateImageView,
                                      UpdateVideoView, UserDigitalAssetsView,
                                      VideoListView)

app_name = 'digital-assets'

router = DefaultRouter()
router.register(r'imagelist', ImageListApi)

urlpatterns = [
    url(r'^create-assets/$', CreateDigitalAssetsView.as_view(), name='create_assets_url'),
    url(r'^user-assets/$', UserDigitalAssetsView.as_view(), name='user_assets_url'),
    url(r'^update-audio/(?P<pk>[0-9]+)/$', UpdateAudioView.as_view(), name='audio_update_url'),
    url(r'^update-video/(?P<pk>[0-9]+)/$', UpdateVideoView.as_view(), name='video_update_url'),
    url(r'^update-image/(?P<pk>[0-9]+)/$', UpdateImageView.as_view(), name='image_update_url'),
    url(r'^update-attachment/(?P<pk>[0-9]+)/$', UpdateAttachmentView.as_view(), name='attachment_update_url'),
    url(r'^audios/list/$', AudioListView.as_view(), name='audio_list_url'),
    url(r'^videos/list/$', VideoListView.as_view(), name='video_list_url'),
    url(r'^images/list/$', ImageListView.as_view(), name='image_list_url'),
    url(r'^attachments/list/$', AttachmentListView.as_view(), name='attachment_list_url'),
    url(r'^delete-audio/(?P<pk>[0-9]+)/$', DeleteAudioView.as_view(), name='audio_delete_url'),
    url(r'^delete-video/(?P<pk>[0-9]+)/$', DeleteVideoView.as_view(), name='video_delete_url'),
    url(r'^delete-image/(?P<pk>[0-9]+)/$', DeleteImageView.as_view(), name='image_delete_url'),
    url(r'^delete-attachment/(?P<pk>[0-9]+)/$', DeleteAttachmentView.as_view(), name='attachment_delete_url'),
    url(r'^attachments/create/$', CreateAttachmentView.as_view(), name='attachment_create_url'),
    url(r'^audios/create/$', CreateAudioView.as_view(), name='audio_create_url'),
    url(r'^videos/create/$', CreateVideoView.as_view(), name='video_create_url'),
    url(r'^images/create/$', CreateImageView.as_view(), name='image_create_url'),
    url(r'^', include(router.urls))
]
