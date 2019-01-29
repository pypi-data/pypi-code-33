from rest_framework import serializers
from tracker.models import CandidateRankingSet, CandidateRanking


class CandidateRankingSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateRankingSet
        fields = ("id", "date")


class CandidateRankingSerializer(serializers.ModelSerializer):
    candidate = serializers.SerializerMethodField()

    def get_candidate(self, obj):
        return obj.candidate.person.full_name

    class Meta:
        model = CandidateRanking
        fields = ("id", "candidate", "value", "explanation", "ranking_set")
