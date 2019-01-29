from rest_framework import generics
from tracker.models import CandidateRatingCategory
from tracker.serializers import CandidateRatingCategorySerializer


class CandidateRatingCategoryMixin(object):
    def get_queryset(self):
        return CandidateRatingCategory.objects.all()


class CandidateRatingCategoryList(
    CandidateRatingCategoryMixin, generics.ListAPIView
):
    serializer_class = CandidateRatingCategorySerializer


class CandidateRatingCategoryDetail(
    CandidateRatingCategoryMixin, generics.RetrieveAPIView
):
    serializer_class = CandidateRatingCategorySerializer
