import logging
import yaml

try:
    from ts3ekkosingle.errors import EkkoNonexistentPermissionDoc, EkkoNonexistentGrant, PermissionDenied, \
        PermissionDuplicate
except ImportError:
    from .errors import EkkoNonexistentPermissionDoc, EkkoNonexistentGrant, PermissionDenied, PermissionDuplicate

logger = logging.getLogger('ekkobot-permission')


class InvokerCtx:
    """
    Data collection about a specific user. Used to compare against other InvokerCtxs (e.g. permission restrictions)
     to determine if permission rules are matching or not.
    """

    def __init__(self, server_groups, channel_group, unique_id, username=None):
        """
        Create a new InvokerCtx object.

        :param server_groups: list of server group ids
        :param channel_group: channel group id
        :param unique_id: unique id
        :param username: (optional) username, will not be used for matching/comparing
        """
        self.server_groups = server_groups
        self.channel_group = channel_group
        self.unique_id = unique_id
        self.username = username

        if self.server_groups is not None:
            self.server_groups = [int(sgid) for sgid in self.server_groups]
        else:
            self.server_groups = []

        if self.channel_group is not None:
            self.channel_group = int(self.channel_group)

    def match(self, po):
        """
        Determine if a PermissionGrant or InvokerCtx matches with this InvokerCtx. Raises PermissionDenied if any attribute differs.
        
        :param po: PermissionGrant/InvokerCtx
        :raises PermissionDenied: on mismatch
        """
        if self.channel_group != po.channel_group and po.channel_group is not None:
            raise PermissionDenied('client_group does not match', False)
        if self.unique_id != po.unique_id and po.unique_id is not None:
            raise PermissionDenied('unique_id does not match', False)
        for server_group_id in po.server_groups or []:
            if server_group_id not in self.server_groups:
                raise PermissionDenied('server_groups do not match', False)

    def not_match(self, po):
        """
        Determine if a PermissionGrant or InvokerCtx does not match with this InvokerCtx. Raises PermissionDenied if no attribute differs.
        
        :param po: PermissionGrant/InvokerCtx
        :raises PermissionDenied: on full match.
        """
        if self.channel_group == po.channel_group or po.channel_group is None:
            if self.unique_id == po.unique_id or po.unique_id is None:
                for server_group_id in po.server_groups or []:
                    if server_group_id not in self.server_groups:
                        return
                raise PermissionDenied('client_group, unique_id and server_groups match', True)

    def __repr__(self):
        repr = f'<ts3ekkosingle.permission.InvokerCtx server_groups:"{self.server_groups}", ' \
               f'channel_group:"{self.channel_group}", unique_id: "{self.unique_id}"'
        if self.username is not None:
            repr += f', username: "{self.username}"'
        repr += '>'
        return repr


class PermissionManager:
    """

        Sort of thinking about permissions in yaml style.
        A set of servergroups, channelgroups and identities is constructed with AND clauses.
        All sets together are compared with OR.

        The master permission (which allows access to all commands) is called "master".

        ---
        - master:
            - name: xyoz
              identity:
                32dk3okljwe/32xsr3&23ex==

        - media.queue.append:
            -   name: generals
                servergroups:
                    1
                    2
                    24
                channelgroups:
                    2
                    3
                    4
                identity:
                    vm3405789j34kew23/r23x==
            -   name: friendos
                servergroups:
                    3
        - media.queue.skip:
            -   name: idiots
                servergroups:
                    2

            [etc...]
    """
    def __init__(self, path):
        self.permissions = {}
        with open(path, 'r') as f:
            yaml_permissions = yaml.safe_load(f)

        for action, sets in yaml_permissions.items():
            for perm_set in sets:
                try:
                    self.permissions[action].append(
                        InvokerCtx(perm_set.get('servergroups'), perm_set.get('channelgroup'), perm_set.get('identity'))
                    )
                except KeyError:
                    self.permissions[action] = [
                        InvokerCtx(perm_set.get('servergroups'), perm_set.get('channelgroup'), perm_set.get('identity'))
                    ]

    def _query_grants(self, action: str, ictx: InvokerCtx):
        """
        Query database to find a matching grant to the given action/permission and InvokerCtx which would allow 
        the invoker to perform the requested action.
        
        If this function executes without PermissionDenied being raised, then a matching grant was found.
        
        This is the counterpart to `_query_denies`. Only if both functions are called with the same parameters 
        and do not raise the PermissionDenied error, the invoker is actually allowed for the given permission.
        
        :param action: requested permission name
        :param ictx: InvokerCtx about the invoker that requested the permission
        :raises PermissionDenied: if no matching grant could be found
        """
        for result in self.permissions.get(action, []):
            try:
                ictx.match(result)
                logger.info(f'permission finally granted - ictx: {ictx} for action: {action}')
                return
            except PermissionDenied as e:
                logger.debug(e)
                # denied (for this rule, need to check all other rules as well)
                pass
        logger.info(f'permission finally denied - ictx: {ictx} for action: {action}')
        raise PermissionDenied('', False)


    def can(self, action: str, context: InvokerCtx) -> bool:
        """
        Checks if an action/permission is allowed in the given invoker context.
        
        :param action: requested permission name
        :param context: invoker identifications
        :return: bool depending if the action is allowed (True) or denied (False)
        """

        try:
            self._query_grants('master', context)
        except PermissionDenied:
            pass
        else:
            return True

        try:
            self._query_grants(action, context)
        except PermissionDenied:
            return False
        else:
            return True
