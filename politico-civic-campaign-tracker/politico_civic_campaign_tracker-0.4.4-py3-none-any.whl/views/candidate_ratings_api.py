import json
import requests

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from election.models import Candidate
from tracker.models import CandidateWinRating, CandidateRatingCategory

CHANNEL = settings.SLACKFORMS_FEEDBACK_CHANNEL


class CandidateRatingsAPI(View):
    def get(self, request):
        if request.GET.get("id"):
            candidate = Candidate.objects.get(uid=request.GET.get("id"))
            win_rating = candidate.win_ratings.latest("date")

            data = {"candidate": candidate.uid, "win_rating": win_rating.id}
            return JsonResponse(data)
        else:
            resp = {}
            return JsonResponse(resp)

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
        candidate = Candidate.objects.get(uid=request.POST["candidate"])

        if request.POST.get("win_category"):
            category = CandidateRatingCategory.objects.get(
                id=request.POST.get("win_category")
            )

            rating = CandidateWinRating.objects.create(
                candidate=candidate, category=category
            )

        # create feedback message
        callback_data = {
            "token": settings.SLACKFORMS_VERIFICATION_TOKEN,
            "channel": CHANNEL,
            "data_id": rating.id,
            "form": form_name,
            "text": "<@{}> changed the ratings for {}.".format(
                username, candidate.person.full_name
            ),
            "new": "Edit",
        }
        requests.post(url=response_url, data=callback_data)

        return HttpResponse(status=200)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
