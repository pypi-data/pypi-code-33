from django import template

from ..models import UserAnswer

register = template.Library()


@register.simple_tag(takes_context=True)
def survey_answers_by_contact(context, survey, contact):
    return UserAnswer.objects.filter(
        answer_choice__question__survey=survey, contact=contact).count()
