from django import forms
import django_filters as filters
from dbcron import models


def get_tags(request=None):
    return models.Job.objects.values_list('tag', 'tag').distinct()


class JobFilterSet(filters.FilterSet):
    id = filters.BaseInFilter(widget=forms.HiddenInput)
    is_active = filters.BooleanFilter()
    tags = filters.MultipleChoiceFilter(choices=get_tags)

    class Meta:
        model = models.Job
        fields = []
