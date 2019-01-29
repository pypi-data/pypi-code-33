import json
import requests

from django.http import HttpResponse, JsonResponse, QueryDict
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from campaign.models import Endorsement
from election.models import Candidate

CHANNEL = settings.SLACKFORMS_FEEDBACK_CHANNEL


class EndorsementAPI(View):
    def get(self, request):
        if request.GET.get("id"):
            endorsement = Endorsement.objects.get(id=request.GET.get("id", ""))
            data = {
                "candidate": endorsement.endorsee.candidate.uid,
                "link": endorsement.link,
                "endorser": endorsement.endorser,
                "statement": endorsement.statement,
                "endorsement_date": endorsement.endorsement_date,
            }
            return JsonResponse(data)
        else:
            resp = {}
            return JsonResponse(resp)

    def put(self, request):
        # process the request data
        request_data = QueryDict(request.body)
        meta = json.loads(request_data.get("slackform_meta_data"))
        response_url = meta["response_url"]
        data_id = meta["data_id"]
        username = meta["user"]["id"]
        form_name = meta["form"]
        token = meta["token"]

        if token != settings.SLACKFORMS_VERIFICATION_TOKEN:
            return HttpResponse("Invalid auth token.", status=403)

        # handle the API logic
        endorsement = Endorsement.objects.get(id=data_id)

        if request_data.get("candidate"):
            candidate = Candidate.objects.get(uid=request_data["candidate"])
            endorsement.endorsee = candidate.campaign

        if request_data.get("link"):
            endorsement.link = request_data["link"]

        if request_data.get("endorser"):
            endorsement.endorser = request_data["endorser"]

        if request_data.get("statement"):
            endorsement.statement = request_data["statement"]

        if request_data.get("endorsement_date"):
            endorsement.endorsement_date = request_data[
                "endorsement_date"
            ].split("T")[0]

        endorsement.save()

        # create feedback message
        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": CHANNEL,
            "data_id": endorsement.id,
            "form": form_name,
            "text": "<@{}> edited `{}` entry: {}.".format(
                username, form_name, data_id
            ),
            "edit": "Edit",
            "delete": "Delete",
        }
        requests.post(url=response_url, data=callback_data)

        return HttpResponse(status=200)

    def post(self, request):
        # process the request data
        meta = json.loads(request.POST.get("slackform_meta_data"))
        response_url = meta["response_url"]
        username = meta["user"]["id"]
        form_name = meta["form"]
        token = meta["token"]

        if token != settings.SLACKFORMS_VERIFICATION_TOKEN:
            return HttpResponse("Invalid auth token.", status=403)

        # handle the API logic
        kwargs = {}
        if request.POST.get("candidate"):
            candidate = Candidate.objects.get(uid=request.POST["candidate"])
            kwargs["endorsee"] = candidate.campaign

        if request.POST.get("link"):
            kwargs["link"] = request.POST["link"]

        if request.POST.get("endorser"):
            kwargs["endorser"] = request.POST["endorser"]

        if request.POST.get("statement"):
            kwargs["statement"] = request.POST["statement"]

        if request.POST.get("endorsement_date"):
            kwargs["endorsement_date"] = request.POST[
                "endorsement_date"
            ].split("T")[0]

        endorsement = Endorsement.objects.create(**kwargs)

        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": CHANNEL,
            "data_id": endorsement.id,
            "form": form_name,
            "text": "<@{}> created a new `{}` entry: {}.".format(
                username, form_name, endorsement.id
            ),
            "edit": "Edit",
            "delete": "Delete",
        }
        requests.post(url=response_url, data=callback_data)

        return HttpResponse(status=200)

    def delete(self, request):
        request_data = QueryDict(request.body)
        meta_data = request_data.get("slackform_meta_data")
        meta = json.loads(meta_data)
        response_url = meta["response_url"]
        username = meta["user"]["id"]
        token = meta["token"]
        data_id = meta["data_id"]
        form_name = meta["form"]

        if token != settings.SLACKFORMS_VERIFICATION_TOKEN:
            return HttpResponse("Invalid auth token.", status=403)

        endorsement = Endorsement.objects.get(id=data_id)
        endorsement.delete()

        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": CHANNEL,
            "data_id": endorsement.id,
            "form": form_name,
            "text": "<@{}> deleted a `{}` entry: {}.".format(
                username, form_name, data_id
            ),
            "new": "New",
        }
        requests.post(url=response_url, data=callback_data)

        return HttpResponse(status=200)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
