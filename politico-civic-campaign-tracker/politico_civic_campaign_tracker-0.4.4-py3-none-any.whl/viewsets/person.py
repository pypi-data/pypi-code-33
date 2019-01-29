from election.models import Candidate
from entity.models import Person
from rest_framework import generics
from tracker.serializers import PersonSerializer, PersonListSerializer


class PersonMixin(object):
    def get_queryset(self):
        candidate_ids = Candidate.objects.filter(
            race__cycle__slug="2020", race__office__slug="president"
        ).values_list("id", flat=True)
        return Person.objects.filter(candidacies__id__in=candidate_ids)


class PersonList(PersonMixin, generics.ListAPIView):
    serializer_class = PersonListSerializer


class PersonDetail(PersonMixin, generics.RetrieveAPIView):
    serializer_class = PersonSerializer
