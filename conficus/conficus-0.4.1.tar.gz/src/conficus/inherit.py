from .parse import ConfigDict


def inherit(config):  # noqa C901
    '''
    ficus.inherit pushes the configuration values of
    parent section down to its child sections.

    This can be used as a way of simplifying config usage. For example:

    [email]
    server=smtp.location.com
    user=SMTPUSR
    password=CKrit
    from=smtp@location.com

    [email.notifications]
    to=[peter@boondoggle.ca, liz@boondoggle.ca]
    subject=The Subject of Notification
    body=notification_template.txt

    [email.errors]
    to=[errors@boondoggle.ca]
    subject=[Alert] Error
    body=error_template.txt

    '''
    def _inherit(inheritable_options, section):
        # first inherit any options
        # that do not exist
        for key, val in inheritable_options.items():
            if key not in section:
                section[key] = val
        # next collect all current options
        # on the section
        section_options = {}
        for key, val in section.items():
            if not isinstance(val, ConfigDict):
                section_options[key] = val
        # finally, push down the sections options
        # to all its sub-sections
        for key, val in section.items():
            if isinstance(val, ConfigDict):
                _inherit(section_options, val)

    _inherit({}, config)

    return config
