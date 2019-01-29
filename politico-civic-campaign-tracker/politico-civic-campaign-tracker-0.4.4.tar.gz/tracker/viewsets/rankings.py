from datetime import datetime
from election.models import Candidate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from tracker.models import CandidateRankingSet, CandidateRanking
from tracker.serializers import (
    CandidateRankingSetSerializer,
    CandidateRankingSerializer,
)


class RankingSetAdminView(APIView):
    def get(self, request, format=None):
        sets = CandidateRankingSet.objects.all()
        data = CandidateRankingSetSerializer(sets, many=True).data
        return Response(data)


class RankingsAdminView(APIView):
    lookup_url_kwarg = "pk"

    def get(self, request, format=None, **kwargs):
        ranking_set = CandidateRankingSet.objects.get(pk=self.kwargs["pk"])
        data = CandidateRankingSerializer(ranking_set.rankings, many=True).data

        response_data = {"rankings": data}
        return Response(response_data)

    def post(self, request, format=None, **kwargs):
        if self.kwargs.get("pk"):
            ranking_set = CandidateRankingSet.objects.get(pk=self.kwargs["pk"])
        else:
            ranking_set = CandidateRankingSet.objects.create(
                date=datetime.now()
            )

        for ranking_data in request.data:
            candidate = Candidate.objects.get(
                person__full_name=ranking_data["candidate"]
            )

            if ranking_data.get("id"):
                ranking = CandidateRanking.objects.get(id=ranking_data["id"])
                ranking.candidate = candidate
                ranking.value = ranking_data["value"]
                ranking.explanation = ranking_data["explanation"]
                ranking.ranking_set = ranking_set
                ranking.save()
            else:
                CandidateRanking.objects.create(
                    candidate=candidate,
                    value=ranking_data["value"],
                    explanation=ranking_data["explanation"],
                    ranking_set=ranking_set,
                )

        return Response(
            "Created/updated rankings", status=status.HTTP_201_CREATED
        )
