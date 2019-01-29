from rest_framework import viewsets
from rest_framework.response import Response

from ccc.campaigns.models import ISMS, OSMS, Campaign
from ccc.campaigns.serializers import (CampaignAppSerializer,
                                       CampaignSerializer, ISMSSerializer)
from ccc.packages.models import TwilioNumber


class CampaignViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CampaignSerializer
    model = Campaign

    def get_queryset(self):
        return self.request.user.campaign_set.filter(active=True)


class CampaignAppViewSet(viewsets.ModelViewSet):
    """
        Class for handling Movie request
    """
    serializer_class = CampaignAppSerializer
    model = Campaign
    queryset = Campaign.objects.all()
    paginate_by = 10

    def list(self, request, *args, **kwargs):
        self.object_list = Campaign.objects.filter(user=request.user,
                                                   active=True)
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)


class ISMSViewSet(viewsets.ModelViewSet):
    """
        Class for handling Movie request
    """
    serializer_class = ISMSSerializer
    model = ISMS
    queryset = ISMS.objects.all()
    paginate_by = 10

    def list(self, request, *args, **kwargs):
        numbers_list = TwilioNumber.objects.filter(user=request.user).values_list('twilio_number', flat=True)
        self.object_list = ISMS.objects.filter(to__in=numbers_list).order_by("-date_created")
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        reply_data = self.request.data.get("reply_data")
        isms_id = self.request.data.get("isms_id")
        queryset = ISMS.objects.filter(id=isms_id)
        if not reply_data or not isms_id or not queryset.exists():
            return Response({"error": "SMS data not found"})
        if self.request.user.balance.get('sms', 0) <= 0:
            return Response({"error": "You are out of SMS credit."})
        queryset = queryset[0]
        twilio_number = TwilioNumber.objects.filter(twilio_number=queryset.to)
        if not twilio_number.exists():
            return Response({"error": "Invalid Campaign Number."})
        twilio_number = twilio_number[0]
        from_no = twilio_number.twilio_number
        to = queryset.from_no
        OSMS.objects.create(from_no=from_no, to=to, text=reply_data)
        return Response({"success": "SMS sent successfully."})
