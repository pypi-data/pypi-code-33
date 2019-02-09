from saml2.saml import NAME_FORMAT_BASIC

DJ_BASIC = 'django.user.'  # anyone have a good idea?

FIELDS = [
    'username',
    'first_name',
    'last_name',
    'email',
    'is_staff',
    'is_active',
    'date_joined',
    'last_login',
]

MAP = {
    'identifier': NAME_FORMAT_BASIC,
    'fro': {DJ_BASIC + field: field for field in FIELDS},
    'to': {field: DJ_BASIC + field for field in FIELDS},
}
