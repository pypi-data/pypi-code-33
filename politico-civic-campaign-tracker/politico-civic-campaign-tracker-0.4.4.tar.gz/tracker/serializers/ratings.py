from rest_framework import serializers
from tracker.models import CandidateRatingCategory


class CandidateRatingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateRatingCategory
        fields = ("id", "label", "order")
