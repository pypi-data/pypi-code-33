from oidc_provider.views import userinfo
from django.http import HttpResponse
from djangoldp.views import LDPViewSet
from .models import Project
import requests

class ProjectViewSet(LDPViewSet):
    model = Project
    permission_classes = []
    nested_fields = ["team"]

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        requests.post("https://jabber.happy-dev.fr/happydev_muc_admin/", json={"@context": "https://cdn.happy-dev.fr/owl/hdcontext.jsonld", "@graph": [{"object":self.get_object().get_absolute_url(),"type":"Update"}]})
        return response
