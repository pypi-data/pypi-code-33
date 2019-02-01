import logging
import sys
import csv
import re
import ssl
import json
import time
import socket

try:
    from urllib.parse import urlencode, urlunsplit
except ImportError:
    from urlparse import urlunsplit
    from urllib import urlencode

import requests
import websocket
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)


class AlarmDealerClient(object):

    DOMAIN = 'alarmdealer.com'
    WEBSOCKET_PORT = 8800

    EVENT_LOG_HEADERS = [
        'Received', 'System', 'Signal', 'SIA Code', 'Partition', 'Extra',
        'Zone/User', 'Relay Status'
    ]

    def __init__(self):
        self.session = requests.Session()
        self.username = None
        self.password = None
        self.ws = None

    @classmethod
    def get_url(cls, mod, action):
        """Generate a URL given the query params

        ex:
        >>> get_url('auth', 'login')
        'https://alarmdealer.com/index.php?action=login&mod=auth'

        """
        query = urlencode({'mod': mod, 'action': action})
        parts = ('https', cls.DOMAIN, 'index.php', query, '')
        url = urlunsplit(parts)
        return url

    def login(self, username=None, password=None):
        if username:
            self.username = username
        if password:
            self.password = password
        url = self.get_url('auth', 'login')
        r = self.session.get(url)
        assert "Customer Login" in r.text
        url = self.get_url('auth', 'authenticate')
        data = {
            'user_name': self.username,
            'user_pass': self.password,
        }
        r = self.session.post(url, data)
        assert "Event Log" in r.text
        self.ws = None  # now we need to reestablish the websocket

    def logout(self):
        if self.ws:
            self.ws.close()

    def get_event_log(self):
        url = self.get_url('eventlog', 'index')
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find('table', attrs={'class': 'listView'})
        headers = [th.text for th in table.find_all('th')]
        assert headers == self.EVENT_LOG_HEADERS, \
            "headers(%s) have changed" % headers
        trs = table.find_all('tr')
        events = []
        for tr in trs[1:]:
            tds = tr.find_all('td')
            values = [td.text.strip() for td in tds]
            assert len(values) == len(headers)
            events.append(values)
        return events

    def _get_websocket_login_info(self):
        """The login info for the websocket is embedded in a script tag
        on the page.  Find that stuff here.

        """
        url = self.get_url('devices', 'keypad')
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        var_text = soup.find(text=re.compile("window.username"))
        var_lines = [l.strip() for l in var_text.strip().splitlines()]
        vars = [re.match('^window\.([^ ]+) = "([^"]*)";$', l).groups()
                for l in var_lines]
        info = dict(vars)
        return info['username'], info['epass'], info['user_type']

    def _get_websocket(self):
        """Return the existing AlarmDealerWebSocket or create one and return
        it.

        """
        if self.ws is None:
            logger.debug("ws is None so setting up")
            username, epass, user_type = self._get_websocket_login_info()
            url = "wss://%s:%d/ws" % (self.DOMAIN, self.WEBSOCKET_PORT)
            self.ws = AlarmDealerWebSocket(url)
            self.ws.connect()
            self.ws.login(username, epass, user_type)
        else:
            logger.debug("returning existing ws")
        return self.ws

    def get_status(self):
        ws = self._get_websocket()
        while True:
            result = ws.send("send_cmd", cmd="status")
            try:
                data = json.loads(result['data'])
            except ValueError:
                time.sleep(0.500)
                continue
            else:
                status = ' '.join([data['LCD_L1'], data['LCD_L2']])
                return status

    def wait_for_status(self, expected_status):
        while True:
            status = self.get_status()
            if status and re.search(expected_status, status, re.IGNORECASE):
                return status
            time.sleep(1)

    def arm_stay(self):
        ws = self._get_websocket()
        ws.send("send_cmd", cmd="s")

    def arm_away(self):
        ws = self._get_websocket()
        ws.send("send_cmd", cmd="a")

    def disarm(self, code):
        ws = self._get_websocket()
        for digit in code:
            logger.debug("disarm sending digit: %r", digit)
            result = ws.send("send_cmd", cmd=digit)
            logger.debug("disarm send digit result: %r", result)
            time.sleep(1)


class AlarmDealerWebSocket(object):
    """Part of http://alarmdealer.com does stuff via websocket

    This is meant to be used as a part of something like AlarmDealerClient.

    """

    def __init__(self, url):
        self.url = url
        logger.debug("url: %r", self.url)
        self.username = None
        self.epass = None
        self.user_type = None

    def connect(self):
        ssl_opt = {"cert_reqs": ssl.CERT_NONE}
        self.ws = websocket.create_connection(self.url, sslopt=ssl_opt)
        logger.debug("ws: %r", self.ws)

    def close(self):
        self.ws.close()

    def login(self, username=None, epass=None, user_type=None):
        if username is not None:
            self.username = username
        if epass is not None:
            self.epass = epass
        if user_type is not None:
            self.user_type = user_type
        result = self.send("login", username=self.username, epass=self.epass,
                           pass_hashed="true", user_type=self.user_type)
        assert result['msg'] == 'Logged in successfully'

    def send(self, action, **input):
        text = json.dumps({"action": action, "input": input})
        logger.debug("send: %r", text)
        try:
            self.ws.send(text)
            result = self.ws.recv()
        except (websocket._exceptions.WebSocketConnectionClosedException, socket.error):
            logger.debug("websocket closed.  reconnecting")
            self.connect()
            self.login()
            self.ws.send(text)
            result = self.ws.recv()
        logger.debug("recv: %r", result)
        data = json.loads(result)
        assert data['status'] == "OK"
        return data
