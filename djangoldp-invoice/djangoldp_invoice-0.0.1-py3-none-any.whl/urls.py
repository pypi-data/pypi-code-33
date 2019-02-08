from django.conf.urls import url, include
from django.conf import settings
from djangoldp.views import LDPViewSet
from .models import CustomerInvoice
from .models import FreelanceInvoice
from .models import Batch
from .models import Task

urlpatterns = [
    url(r'^freelance-invoices/', LDPViewSet.urls(model=FreelanceInvoice)),
    url(r'^customer-invoices/', LDPViewSet.urls(model=CustomerInvoice,
        nested_fields=["batches", "project", "customer"],
        fields=["@id", "identifier", "title", "state", "htAmount", "tvaRate", "invoicingDate",
        "tvaAmount", "ttcAmount", "batches", "project", "customer"]
    )),
    url(r'^batches/', LDPViewSet.urls(model=Batch,
        nested_fields=["tasks"],
        fields=["@id", "title", "htAmount", "tasks"]
    )),
    url(r'^tasks/', LDPViewSet.urls(model=Task)),
]