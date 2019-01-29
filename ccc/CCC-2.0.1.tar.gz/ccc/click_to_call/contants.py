# These statuses correspond to the statuses of RealPhoneValidation API
REAL_PHONE_STATUSES = (
    ('connected', 'Always connected'),
    ('connected-75', 'Connected 75% of the time'),

    ('pending', 'Not completed yet'),
    ('disconnected', 'Always disconnected'),

    ('disconnected-85', 'Disconnected 85% of the time'),
    ('disconnected-70', 'Disconnected 70% of the time'),
    ('disconnected-50', 'Disconnected 50% of the time'),

    ('busy', 'Busy'),
    ('unreachable', 'Not reachable'),
    ('invalid phone', 'Phone not valid'),

    ('restricted', 'Cant be dialed'),

    ('ERROR', 'bad phone number'),

    ('invalid-format', 'phone or zip are not in a valid format'),
    ('invalid-phone', 'phone number is not valid'),

    ('bad-zip-code', 'zip code is not valid'),

    ('server-unavailable', 'contact support'),

)

REAL_PHONE_TYPE = (
    ('landline', 'Landline'),
    ('cell-phone', 'Cell Phone'),
    ('voip', 'Voip'),
    ('invalid', 'Invalid'),
    ('unknown', 'Unknown')
)
