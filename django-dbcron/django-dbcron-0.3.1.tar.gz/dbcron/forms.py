from django import forms
from django.utils.translation import ugettext_lazy as _
from dbcron import models


class AbstractJobForm:
    sec = forms.CharField(
        initial='0',
        label=_("Second(s)")
    )
    min = forms.CharField(
        initial='*',
        label=_("Minute(s)")
    )
    hou = forms.CharField(
        initial='*',
        label=_("Hour(s)")
    )
    dom = forms.CharField(
        initial='*',
        label=_("Day(s) of month")
    )
    mon = forms.CharField(
        initial='*',
        label=_("Month")
    )
    dow = forms.CharField(
        initial='*',
        label=_("Day(s) of week")
    )
    yea = forms.CharField(
        initial='*',
        label=_("Year(s)")
    )


class JobForm(AbstractJobForm, forms.ModelForm):
    class Meta:
        model = models.Job
        fields = '__all__'
