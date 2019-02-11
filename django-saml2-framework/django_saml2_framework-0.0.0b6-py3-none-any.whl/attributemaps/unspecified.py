from saml2.saml import NAME_FORMAT_UNSPECIFIED

DJ_UNSPECIFIED = ''  # anyone have a good idea?

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
    'identifier': NAME_FORMAT_UNSPECIFIED,
    'fro': {DJ_UNSPECIFIED + field: field for field in FIELDS},
    'to': {field: DJ_UNSPECIFIED + field for field in FIELDS},
}
