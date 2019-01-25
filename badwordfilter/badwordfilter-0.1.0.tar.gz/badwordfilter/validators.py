from .badwordfilter import ProfanityFilter
from django.core.exceptions import ValidationError

pf = ProfanityFilter()


def validate_is_profane(value):
    if pf.is_bad(value) is True:
        raise ValidationError(f'{value} is bad word')
