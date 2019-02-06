"""
State to just set the hostname.
"""
__func_alias__ = {
    'is_': 'is',
}


def __virtual__():
    if 'network.get_hostname' in __salt__ and 'network.mod_hostname' in __salt__:
        return True
    else:
        return False, "Network module hostname functions not available"


def is_(name):
    """
    Sets the system's hostname.

    Updates both /etc and the live hostname.

    Does not update the "fqdn", /etc/mailname, or any other variants. See
    hostname(1) for more information on these.
    """
    ret = {
        'name': name,
        'result': False,
        'changes': {},
        'comment': '',
    }

    current_name = __salt__['network.get_hostname']()

    if current_name == name:
        ret['result'] = True
        ret['comment'] = 'Hostname already set to {}'.format(current_name)
        return ret

    changes = {name: {'old': current_name, 'new': name}}

    if __opts__['test']:
        ret['changes'] = changes
        ret['result'] = None
        ret['comment'] = 'Hostname would be changed from {0} to {1}'.format(current_name, name)
        return ret

    ret['result'] = __salt__['network.mod_hostname'](name)

    updated_name = __salt__['network.get_hostname']()

    if ret['result'] is False:
        ret['comment'] = 'Failed to update hostname'
    elif ret['result'] is None:
        ret['result'] = False
        ret['comment'] = 'network.mod_hostname refused to update the hostname'
    elif updated_name != name:
        ret['result'] = False
        ret['comment'] = (
            'Updated hostname, but it did not stick '
            '(Tried to update {} to {} but got {} instead)'
        ).format(current_name, name, updated_name)
    else:
        ret['changes'] = changes
        ret['comment'] = 'Updated hostname'

    return ret

