import logging

from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ccc.campaigns.models import CampaignEmailTemplate
from ccc.marketing.emailtemplates.api.serializers import (EmailTemplateSerializer,
                                                          TemplateDesignSerializer)
from ccc.mixin import AuthParsersMixin
from ccc.template_design.models import TemplateDesign

logger = logging.getLogger(__name__)


class EmailTemplateViewSet(AuthParsersMixin, ModelViewSet):
    """ EmailTemplate to get premium template pass parameter as <api>?premium=true
    and to get recommended email template pass parameter as <api>?recommended=true"""
    serializer_class = EmailTemplateSerializer
    queryset = CampaignEmailTemplate.objects.all().order_by('-date_created')
    order_by = 'id'

    def get_serializer_class(self):
        if self.request.query_params.get('premium') or self.request.query_params.get('recommended'):
            return TemplateDesignSerializer
        return self.serializer_class

    def get_queryset(self):
        if self.request.query_params.get('premium'):
            self.query_set = TemplateDesign.objects.filter(user=self.request.user, is_active=True, is_public=False,
                                                           template_type='email').order_by('-created_at')
        elif self.request.query_params.get('recommended'):
            self.query_set = TemplateDesign.objects.filter(is_active=True, is_public=True,
                                                           template_type='email').order_by('-created_at')
        else:
            self.query_set = super(EmailTemplateViewSet, self).get_queryset()
        return self.query_set

    @action(methods=['get'], detail=False)
    def transfer(self, request, *args, **kwargs):
        # This view is to import all the old/existing templates, not really main function of the application
        import csv
        import os
        from ccc.template_design.models import TemplateDesign
        reader = csv.reader(open(os.path.join(settings.BASE_DIR, 'template_design_templatedesign.csv'), 'r'))
        list_data = []
        for row in reader:
            dict_obj = {}
            dict_obj.update({
                'name': row[1],
                'email_body': row[2],
                'preview': row[3],
                'is_active': True if row[4] == 't' else False,
                'is_public': True if row[5] == 't' else False,
                'template_type': row[10],
                'json_data': row[11],
                'user_id': 1
            })
            list_data.append(TemplateDesign(**dict_obj))
        TemplateDesign.objects.bulk_create(list_data)
        return Response({'status': 'success'}, status=200)
