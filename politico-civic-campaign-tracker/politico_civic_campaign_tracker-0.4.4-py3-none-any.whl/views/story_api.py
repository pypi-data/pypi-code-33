import json
import requests

from bs4 import BeautifulSoup
from django.http import HttpResponse, JsonResponse, QueryDict
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from election.models import Candidate
from tracker.models import Story
from tracker.serializers import StorySerializer
from webpreview import OpenGraph

CHANNEL = settings.SLACKFORMS_FEEDBACK_CHANNEL


class StoryAPI(View):
    def get(self, request):
        if request.GET.get("id"):
            story = Story.objects.get(id=request.GET.get("id", ""))
            data = StorySerializer(story).data
            data["candidate"] = story.candidate.uid
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

        story = Story.objects.get(id=data_id)

        if request_data.get("candidate"):
            candidate = Candidate.objects.get(uid=request_data["candidate"])
            story.candidate = candidate

        if request_data.get("url"):
            story.url = request_data["url"]
            data = OpenGraph(
                request_data["url"], ["og:image", "og:title", "og:description"]
            )
            story.headline = data.title
            story.image_url = data.image
            story.description = data.description
            r = requests.get(request_data["url"])
            scraped = BeautifulSoup(r.text, "html.parser")
            author = scraped.find_all("p", "byline")[0]
            time = scraped.find("time")
            story.publish_date = time["datetime"].split(" ")[0]
            story.byline = author.get_text().strip().title().split("By ")[1]

        if request_data.get("description"):
            story.description = request_data["description"]

        story.save()

        # create feedback message
        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": CHANNEL,
            "data_id": story.id,
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

        if request.POST.get("url"):
            kwargs["url"] = request.POST["url"]
            data = OpenGraph(
                request.POST["url"], ["og:image", "og:title", "og:description"]
            )
            kwargs["headline"] = data.title
            kwargs["image_url"] = data.image
            kwargs["description"] = data.description

            r = requests.get(request.POST["url"])
            scraped = BeautifulSoup(r.text, "html.parser")
            author = scraped.find_all("p", "byline")[0]
            time = scraped.find("time")
            kwargs["publish_date"] = time["datetime"].split(" ")[0]
            kwargs["byline"] = (
                author.get_text().strip().title().split("By ")[1]
            )

        if request.POST.get("description"):
            kwargs["description"] = request.POST["description"]

        story = Story.objects.create(**kwargs)

        # create feedback message
        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": CHANNEL,
            "data_id": story.id,
            "form": form_name,
            "text": "<@{}> created a new `{}` entry: {}.".format(
                username, form_name, story.id
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

        story = Story.objects.get(id=data_id)
        story.delete()

        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": CHANNEL,
            "data_id": story.id,
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
