import json
import requests

from django.http import HttpResponse, JsonResponse, QueryDict
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from election.models import Candidate
from tracker.models import Quote
from tracker.serializers import QuoteSerializer

CHANNEL = settings.SLACKFORMS_FEEDBACK_CHANNEL


class QuoteAPI(View):
    def get(self, request):
        if request.GET.get("id"):
            quote = Quote.objects.get(id=request.GET.get("id", ""))
            data = QuoteSerializer(quote).data
            data["candidate"] = quote.candidate.uid
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

        quote = Quote.objects.get(id=data_id)

        if request_data.get("candidate"):
            candidate = Candidate.objects.get(uid=request_data["candidate"])
            quote.candidate = candidate

        if request_data.get("text"):
            quote.text = request_data["text"]

        if request_data.get("date"):
            quote.date = request_data["date"].split("T")[0]

        if request_data.get("link"):
            quote.link = request_data["link"]

        if request_data.get("place"):
            quote.place = request_data["place"]

        quote.save()

        # create feedback message
        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": CHANNEL,
            "data_id": quote.id,
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

        kwargs = {}
        # handle the API logic
        if request.POST.get("candidate"):
            candidate = Candidate.objects.get(uid=request.POST["candidate"])
            kwargs["candidate"] = candidate

        if request.POST.get("text"):
            kwargs["text"] = request.POST["text"]

        if request.POST.get("date"):
            kwargs["date"] = request.POST["date"].split("T")[0]

        if request.POST.get("link"):
            kwargs["link"] = request.POST["link"]

        if request.POST.get("place"):
            kwargs["place"] = request.POST["place"]

        quote = Quote.objects.create(**kwargs)

        # create feedback message
        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": CHANNEL,
            "data_id": quote.id,
            "form": form_name,
            "text": "<@{}> created a new `{}` entry: {}.".format(
                username, form_name, quote.id
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

        quote = Quote.objects.get(id=data_id)
        quote.delete()

        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": CHANNEL,
            "data_id": quote.id,
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
