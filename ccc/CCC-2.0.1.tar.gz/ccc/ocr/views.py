import json
import re

from django.http.response import HttpResponse
from django.views.generic.edit import FormView
from google.cloud import vision
from rest_framework.parsers import (FileUploadParser, FormParser, JSONParser,
                                    MultiPartParser)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from ccc.campaigns.models import Campaign
from ccc.ocr.forms import DocumentForm
from ccc.ocr.models import ImageContacts
from ccc.ocr.serializers import OCRImageContactsSerializer
from ccc.survey.models import Survey


class OCRView(FormView):
    template_name = 'ccc/ocr/upload_image.html'
    form_class = DocumentForm
    success_url = '/thanks/'

    def form_invalid(self, form):
        return FormView.form_invalid(self, form)

    def form_valid(self, form):
        from google.cloud import vision
        import google.auth
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        credentials, project = google.auth.default()
        client = vision.Client(project=project, credentials=credentials)
        bytes_image = client.image(
            content=self.request.FILES['document'].read())
        text = bytes_image.detect_text()
        text_data = [x.description for x in text]
        return HttpResponse(json.dumps(text_data), content_type="application/json")


class OcrFileUploadView(APIView):
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request, *args, **kwargs):
        if not self.request.FILES.get('document'):
            return Response(data={"error": "document parameter missing or blank"})

        campaign_id = request.POST.get('campaign_id')
        survey_id = request.POST.get('survey_id')
        if campaign_id and not Campaign.objects.filter(id=campaign_id, user=request.user).exists():
            return Response(data={"error": "campaign_id is not registered with user"})
        elif survey_id and not Survey.objects.filter(id=survey_id, user=request.user).exists():
            return Response(data={"error": "survey_id is not registered with user"})
        elif survey_id and campaign_id:
            return Response(data={"error": "campaign_id and survey_id both are present"})
        elif not survey_id and not campaign_id:
            return Response(data={"error": "campaign_id or survey_id missing or blank"})

        file_obj = request.FILES['document']

        unique_upload_id = request.POST.get("uuid_key", '')
        result = {"phones": [],
                  "emails": [],
                  "content": "",
                  "uuid_key": unique_upload_id}

        # do some stuff with uploaded file
        # TODO Arrange import and move regex to constant
        phone_pattern = re.compile(
            r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
        email_pattern = re.compile(r'[a-zA-Z0-9-_.]+@[a-zA-Z0-9-_.]+')
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        client = vision.ImageAnnotatorClient()
        image = vision.types.Image(content=file_obj.read())
        response = client.text_detection(image=image)
        text_data = [u"{}".format(x.description) for x in response.text_annotations]
        text_data = " ".join(text_data)
        result["phones"] = phone_pattern.findall(text_data)
        result["emails"] = email_pattern.findall(text_data)
        result["content"] = text_data

        if unique_upload_id:
            contact_obj = ImageContacts.objects.create(
                unique_upload_id=unique_upload_id)
        else:
            contact_obj = ImageContacts.objects.create()
        if campaign_id:
            contact_obj.campaign_id = campaign_id
        else:
            contact_obj.survey_id = survey_id
        contact_obj.save()
        contact_obj.image = file_obj
        contact_obj.phones = json.dumps(result["phones"])
        contact_obj.emails = json.dumps(result["emails"])
        contact_obj.converted_text = text_data
        contact_obj.save()
        result["uuid_key"] = contact_obj.unique_upload_id
        return Response(data=result)


class OCRImageViewSet(ModelViewSet):
    """
        Class for handling Movie request
    """
    serializer_class = OCRImageContactsSerializer
    model = ImageContacts
    queryset = ImageContacts.objects.all()
    paginate_by = 10

    def list(self, request, *args, **kwargs):
        self.object_list = ImageContacts.objects.filter(
            campaign__user=request.user,)
        if request.GET.get("campaign_id"):
            self.object_list = self.object_list.filter(campaign_id=request.GET["campaign_id"])
        self.object_list = self.object_list.distinct("unique_upload_id")
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)


class OCRSurveyImageViewSet(ModelViewSet):
    """
        Class for handling Movie request
    """
    serializer_class = OCRImageContactsSerializer
    model = ImageContacts
    queryset = ImageContacts.objects.all()
    paginate_by = 10

    def list(self, request, *args, **kwargs):
        self.object_list = ImageContacts.objects.filter(
            survey__user=request.user,)
        if request.GET.get("survey_id"):
            self.object_list = self.object_list.filter(survey_id=request.GET["survey_id"])
        self.object_list = self.object_list.distinct("unique_upload_id")
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)
