# This Python file uses the following encoding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
from events import Events
from creaapi.websocket import CreaWebsocket
from crea.instance import shared_crea_instance
from crea.blockchain import Blockchain
from crea.price import Order, FilledOrder
log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)


class Notify(Events):
    """ Notifications on Blockchain events.

        This modules allows yout to be notified of events taking place on the
        blockchain.

        :param fnt on_block: Callback that will be called for each block received
        :param Crea crea_instance: Crea instance

        **Example**

        .. code-block:: python

            from pprint import pprint
            from crea.notify import Notify

            notify = Notify(
                on_block=print,
            )
            notify.listen()

    """

    __events__ = [
        'on_block',
    ]

    def __init__(
        self,
        # accounts=[],
        on_block=None,
        only_block_id=False,
        crea_instance=None,
        keep_alive=25
    ):
        # Events
        Events.__init__(self)
        self.events = Events()

        # Crea instance
        self.crea = crea_instance or shared_crea_instance()

        # Callbacks
        if on_block:
            self.on_block += on_block

        # Open the websocket
        self.websocket = CreaWebsocket(
            urls=self.crea.rpc.nodes,
            user=self.crea.rpc.user,
            password=self.crea.rpc.password,
            only_block_id=only_block_id,
            on_block=self.process_block,
            keep_alive=keep_alive
        )

    def reset_subscriptions(self, accounts=[]):
        """Change the subscriptions of a running Notify instance
        """
        self.websocket.reset_subscriptions(accounts)

    def close(self):
        """Cleanly close the Notify instance
        """
        self.websocket.close()

    def process_block(self, message):
        self.on_block(message)

    def listen(self):
        """ This call initiates the listening/notification process. It
            behaves similar to ``run_forever()``.
        """
        self.websocket.run_forever()
