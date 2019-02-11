from saml2.saml import NAME_FORMAT_URI

DJ_URI = 'django/user/'  # anyone have a good idea?

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
    'identifier': NAME_FORMAT_URI,
    'fro': {DJ_URI + field: field for field in FIELDS},
    'to': {field: DJ_URI + field for field in FIELDS},
}
