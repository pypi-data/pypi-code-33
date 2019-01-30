#!/usr/bin/env python

import logging
import re
import socket
import ssl
import time

class IrcNotifier:

    def __init__(self, params):
        self.server     = params.get("server", "")
        self.port       = params.get("port", "")
        self.use_tls    = params.get("use_tls", True)
        self.channel    = params.get("channel", "")
        self.nick       = params.get("nick", "")

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.use_tls:
            self.client = ssl.wrap_socket(self.client)

    def _wait_for_welcome(self, timeout=5):
        msg = ''
        start = time.time()
        while True:
            msg += self.client.recv(1024).decode("utf-8")
            match = re.search(r"^:\S+ 001 (?P<nick>\S+) :", msg, flags=re.M)
            if match:
                break
            elif time.time() - start > timeout:
                raise Exception('Timeout waiting for IRC server response')
            time.sleep(0.5)

        return True

    def send(self, info):
        '''
            Minimum implementation to send a message to an IRC channel.
        '''

        self.client.connect((self.server, self.port))

        msg = "NICK %s\n" % self.nick
        self.client.send(msg.encode("utf-8"))

        msg = "USER %s 0 * :check_certs bot\n" % (self.nick,)
        self.client.send(msg.encode("utf-8"))

        self._wait_for_welcome()

        msg = "JOIN %s\n" % (self.channel)
        self.client.send(msg.encode("utf-8"))

        msg = "%s expires on %s, and in %d days" % (
            info.get("site", "SITE_NOT_PROVIDED"),
            info.get("not_valid_after", "NOT_VALID_AFTER_NOT_PROVIDED"),
            info.get("expires_in_days", "EXPIRES_IN_DAYS_NOT_PROVIDED"),
        )
        msg = "PRIVMSG %s %s\n" % (self.channel, msg)
        self.client.send(msg.encode("utf-8"))

        # Give the server time to process the message before closing
        # the connection
        time.sleep(1)

        self.client.close()

def setup(app, params):
    app.register_notifier(IrcNotifier(params))
