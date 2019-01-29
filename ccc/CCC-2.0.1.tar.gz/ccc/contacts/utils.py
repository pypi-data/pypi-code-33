import phonenumbers
from rest_framework.pagination import PageNumberPagination

DEFAULT_REGION = 'US'


def clean_phone(phone):
    country = None
    if phone:
        region = None
        if '+' not in phone:
            region = DEFAULT_REGION
        try:
            parsed_phone = phonenumbers.parse(phone, region)
        except phonenumbers.NumberParseException:
            phone = None
            country = DEFAULT_REGION
        else:
            country = phonenumbers.region_code_for_number(parsed_phone) or DEFAULT_REGION
            phone = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.E164)
    return phone, country


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
