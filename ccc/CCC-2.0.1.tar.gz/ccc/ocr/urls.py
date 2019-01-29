from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from ccc.ocr.views import (OcrFileUploadView, OCRImageViewSet,
                           OCRSurveyImageViewSet, OCRView)

app_name = 'ocr'

router = DefaultRouter()
router.register(r'campaign/contact/images', OCRImageViewSet)
router.register(r'survey/contact/images', OCRSurveyImageViewSet)


urlpatterns = [
    url('^upload/$', OCRView.as_view(), name='ocr_upload'),
    url('^upload/api/$', OcrFileUploadView.as_view(), name='ocr_api_upload'),
]

urlpatterns = urlpatterns + router.urls
