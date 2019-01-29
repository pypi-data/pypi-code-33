from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from election.models import Candidate


class CandidateAPI(View):
    def get(self, request):
        candidates = Candidate.objects.filter(
            race__office__slug="president", race__cycle__slug="2020"
        ).order_by("person__last_name")

        data = [
            {"label": candidate.person.full_name, "value": candidate.uid}
            for candidate in candidates
        ]

        return JsonResponse(data, safe=False)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
