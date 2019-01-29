from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from tracker.models import CandidateRatingCategory


class RatingsAPI(View):
    def get(self, request):
        categories = CandidateRatingCategory.objects.all().order_by("order")

        data = [
            {"label": category.label, "value": category.id}
            for category in categories
        ]

        return JsonResponse(data, safe=False)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
