from django import template
from django.template.defaultfilters import stringfilter
from math import ceil

from ..utils import age, get_utcnow, AgeValueError

register = template.Library()


@register.simple_tag(takes_context=True)
def age_in_years(context, born):
    reference_datetime = context.get("reference_datetime") or get_utcnow()
    try:
        age_in_years = age(born, reference_datetime).years
    except AgeValueError:
        age_in_years = None
    return age_in_years or born


@register.filter
@stringfilter
def human(value):
    return "-".join(
        [value[i * 4 : (i + 1) * 4] for i in range(0, ceil(len(value) / 4))]
    )
