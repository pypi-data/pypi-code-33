import phonenumbers

__all__ = [
    'humanize_tel',
    'safe_tel'
]


# Functions

def humanize_tel(tel, country='GB'):
    """Return a human friendly (UK format) telephone number"""

    try:
        return phonenumbers.format_number(
            phonenumbers.parse(tel, country),
            phonenumbers.PhoneNumberFormat.NATIONAL
        )
    except phonenumbers.phonenumberutil.NumberParseException:
        return None

def safe_tel(tel, country='GB'):
    """
    Used to provide a version that can safely be used in a `tel:` HTML link.
    """

    try:
        return phonenumbers.format_number(
            phonenumbers.parse(tel, country),
            phonenumbers.PhoneNumberFormat.E164
        )
    except phonenumbers.phonenumberutil.NumberParseException:
        return None
