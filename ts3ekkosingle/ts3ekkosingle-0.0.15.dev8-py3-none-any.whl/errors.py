import ts3


class TS3InvalidCommand(ts3.TS3Error):
    def __init__(self, cmd=None):
        self.cmd = cmd

    def __str__(self):
        if self.cmd is not None:
            return 'The command "{}" is not a valid command.'.format(self.cmd)
        else:
            return 'The command could not be parsed from the message (probably no command in message)'


class TS3InsufficientPermissions(ts3.TS3Error):
    def __init__(self, client=None, action=None):
        self.client = client
        self.action = action

    def __str__(self):
        return 'The client "{}" is not allowed to perform the action "{}"'.format(self.client, self.action)


class TS3AuthenticationFailed(ts3.TS3Error):
    def __str__(self):
        return 'Authentication failed - maybe endpoint is not up yet?'


class EkkoUnsuitedCommand(Exception):
    def __str__(self):
        return 'This command did not get processed by the handler because it was found unsuited.'


class EkkoNonexistentAlias(Exception):
    def __init__(self, aliasname, permanent=False):
        self.aliasname = aliasname
        self.permanent = permanent

    def __str__(self):
        return f'The alias \'{self.aliasname}\' (permanent={self.permanent}) does not exist.'


class EkkoNonexistentPermissionDoc(Exception):
    def __init__(self, permission):
        self.permission = permission

    def __str__(self):
        return f'There is no documentation for the permission \'{self.permission}\' available.'


class EkkoNonexistentGrant(Exception):
    def __init__(self, grant_id):
        self.grant_id = grant_id

    def __str__(self):
        return f'There is no permission grant with the id {self.grant_id}.'


class PermissionDenied(Exception):
    def __init__(self, msg: str, is_deny_request: bool):
        self.msg = msg
        self.__is_deny_request = is_deny_request

    @property
    def request_type(self) -> str:
        if self.__is_deny_request:
            return 'deny request'
        else:
            return 'grant request'

    def __repr__(self):
        return f'Permission denied, ({self.request_type}): {self.msg}'


class PermissionDuplicate(Exception):
    def __init__(self, grant):
        self.grant = grant

    def __repr__(self):
        return f'Permission Duplicate found for grant={self.grant}'


class EkkoParsingError(Exception):
    """
    To be raised by a custom argparser, to indicate a problem with the parsed input.
    """

    def __init__(self, message, usage):
        self.message = message
        self.usage = usage

    def __str__(self):
        return f'{self.usage}{self.message}'


class EkkoArgparserMessage(Exception):
    """
    Raised by a custom argparser, to indicate that the user requested either help or usage information 
    (which are included in this exception).
    """
    pass


class EkkoInvalidLocalMedia(Exception):
    """
    To be raised if a local media file is requested but can not be delivered, because it is not in the limiting
    media directory path or because it does not exist.
    """

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return f'Access to file \'{self.filename}\' denied. Does not exist or you are not permitted to access it.'
