# Copyright (C) Patrick Brady, Brian Moe, Branson Stephens (2015)
#
# This file is part of lvalert
#
# lvalert is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with lvalert.  If not, see <http://www.gnu.org/licenses/>.

#from ligo.lvalert.sleeklvalert import * 

from .version import __version__

import sys
import getpass
import logging
import netrc
import uuid
import ssl

import pkg_resources
from ligo.lvalert.utils import safe_netrc as _netrc

import sleekxmpp

# Experimental error trapping:
import functools

__all__ = ('LVAlertClient',)

log = logging.getLogger(__name__)

DEFAULT_SERVER = 'lvalert.cgca.uwm.edu'

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input

def _get_default_login(netrcfile, server):
    try:
        netrcfile = _netrc(netrcfile)
    except (OSError, netrc.NetrcParseError) as e:
        log.exception('Cannot load netrc file (%s): %s', netrcfile, e)
        return None, None

    auth = netrcfile.authenticators(server)
    if auth is None:
        log.warn('No netrc entry found for server: %s', server)
        return None, None

    default_username, _, default_password = auth
    return default_username, default_password


def _get_login(username, password, netrc, interactive, server):
    default_username, default_password = _get_default_login(netrc, server)
    prompt = 'password for {}@{}: '.format(username, server)

    if username is not None and password is not None:
        return username, password
    elif username is None and default_username is None:
        raise RuntimeError('Username not specified')
    elif username is None or username == default_username:
        return default_username, default_password
    elif interactive:
        return username, getpass.getpass(prompt)
    else:
        raise RuntimeError('Password not specified')

#-- The purpose of this function is to catch exceptions from 
#-- external functions before they get caught in the xml stream
def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print 'Caught an exception in', f.__name__, ":"
	    print(e)
    return func


class LVAlertClient(sleekxmpp.ClientXMPP):
    """An XMPP client configured for LVAlert.

    Parameters
    ----------
    username : str (optional)
        The XMPP username, or :obj:`None` to look up from the netrc_ file.
    password : str (optional)
        The XMPP password, or :obj:`None` to look up from the netrc_ file.
    resource : str (optional)
        The XMPP resource ID, or :obj:`None` to generate a random one.
    netrc : str (optional)
        The netrc_ file. The default is to consult the ``NETRC`` environment
        variable or use the default path of ``~/.netrc``.
    interactive : bool (optional)
        If :obj:`True`, then fall back to asking for the password on the
        command line if necessary.
    server : str (optional)
        The LVAlert server hostname.

    Example
    -------

    Here is an example for performing administrative actions.

    .. code-block:: python

        client = LVAlertClient()
        client.connect()
        client.process(block=False)
        client.subscribe('cbc_gstlal', 'cbc_pycbc')
        client.abort()

    Here is an example for running a listener.

    .. code-block:: python

        def process_alert(node, payload):
            if node == 'cbc_gstlal':
                alert = json.loads(payload)
                ...

        client = LVAlertClient()
        client.listen(process_alert)
        client.connect()
        client.process(block=True)
    """

    def __init__(self, username=None, password=None, resource=None, netrc=None,
                 interactive=False, server=DEFAULT_SERVER):
        username, password = _get_login(
            username, password, netrc, interactive, server)
        if resource is None:
            resource = uuid.uuid4().hex
        jid = '{}@{}/{}'.format(username, server, resource)

        super(LVAlertClient, self).__init__(jid, password)

	# Activate PubSub plugin
        self.register_plugin('xep_0060')

        # Test out xmpp ping to see if it does anything:
        self.register_plugin('xep_0199', {'keepalive': True, 'interval': 5, 'timeout': 5})

        # Add handlers for available events. 
        self.add_event_handler("session_start", self._session_start, threaded=True)

	# Point the clients to the certs. This needs to be addressed.
        self.ca_certs = pkg_resources.resource_filename(__name__, 'certs.pem')

    def _session_start(self, event):
        self.get_roster()
        self.send_presence()

    def listen(self, callback):
        """Set a callback to be executed for each pubsub item received.

        Parameters
        ----------
        callback : callable
            A function of two arguments: the node and the alert payload.
        """
        self._callback = callback
        self.add_event_handler('pubsub_publish', self._pubsub_publish)

    @catch_exception
    def _pubsub_publish(self, msg):
	if msg['type'] in ('chat', 'normal'):
            self._callback(msg['pubsub_event']['items']['node'],
                           msg['pubsub_event']['items']['item']['payload'].text)

    @property
    def _pubsub_server(self):
        return 'pubsub.{}'.format(self.boundjid.server)

    def get_nodes(self):
        """Get a list of all available pubsub nodes."""
        result = self['xep_0060'].get_nodes(self._pubsub_server)
        return [item for _, item, _ in result['disco_items']['items']]

    def get_subscriptions(self):
        """Get a list of your subscriptions."""
        result = self['xep_0060'].get_subscriptions(self._pubsub_server)
        return sorted({stanza['node'] for stanza in
                       result['pubsub']['subscriptions']['substanzas']})

    def subscribe(self, *nodes):
        """Subscribe to one or more pubsub nodes."""
        for node in nodes:
            log.info('Subscribing to %s', node)
            self['xep_0060'].subscribe(self._pubsub_server, node)

    def unsubscribe(self, *nodes):
        """Unsubscribe from one or more pubsub nodes."""
        for node in nodes:

            subscriptions = self['xep_0060'].get_subscriptions(
                self._pubsub_server, node
            )['pubsub']['subscriptions']['substanzas']

            for subscription in subscriptions:
                log.info('Unsubscribing from %s [%s]',
                         node, subscription['subid'])
                self['xep_0060'].unsubscribe(
                    self._pubsub_server, node, subscription['subid'])

    def publish(self, node, msg=None):
        """Publish a message to one or more pubsub nodes."""
        xmlmsg = sleekxmpp.ET.fromstring("<pubsub xmlns='http://jabber.org/protocol/pubsub'>%s</pubsub>"
                                             % msg)
        try:
            result = self['xep_0060'].publish(self._pubsub_server, node,
                                              payload=xmlmsg)
            id = result['pubsub']['publish']['item']['id']
            log.info('Published at item id: %s' % id)
        except Exception as e:
            print(e)
            log.error('Could not publish to: %s' % node)

    def delete(self):
        try:
            self['xep_0060'].delete_node(self.pubsub_server, self.node)
            print('Deleted node: %s' % self.node)
        except:
            logging.error('Could not delete node: %s' % self.node)
