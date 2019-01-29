import json
import requests

from django.http import HttpResponse, JsonResponse, QueryDict
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from election.models import Candidate
from tracker.models import Video
from tracker.serializers import VideoSerializer


CHANNEL = settings.SLACKFORMS_FEEDBACK_CHANNEL


class VideoAPI(View):
    def get(self, request):
        if request.GET.get("id"):
            video = Video.objects.get(id=request.GET.get("id", ""))
            data = VideoSerializer(video).data
            data["candidate"] = video.candidate.uid
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

        video = Video.objects.get(id=data_id)

        if request_data.get("candidate"):
            candidate = Candidate.objects.get(uid=request_data["candidate"])
            video.candidate = candidate

        if request_data.get("video_id"):
            video.video_id = request_data["video_id"]

        if request_data.get("publish_date"):
            video.publish_date = request_data["publish_date"].split("T")[0]

        if request_data.get("title"):
            video.title = request_data["title"]

        if request_data.get("description"):
            video.description = request_data["description"]

        video.save()

        # create feedback message
        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": CHANNEL,
            "data_id": video.id,
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

        if request.POST.get("video_id"):
            kwargs["video_id"] = request.POST["video_id"]

        if request.POST.get("publish_date"):
            kwargs["publish_date"] = request.POST["publish_date"].split("T")[0]

        if request.POST.get("title"):
            kwargs["title"] = request.POST["title"]

        if request.POST.get("description"):
            kwargs["description"] = request.POST["description"]

        video = Video.objects.create(**kwargs)

        # create feedback message
        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": CHANNEL,
            "data_id": video.id,
            "form": form_name,
            "text": "<@{}> created a new `{}` entry: {}.".format(
                username, form_name, video.id
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

        video = Video.objects.get(id=data_id)
        video.delete()

        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": CHANNEL,
            "data_id": video.id,
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
