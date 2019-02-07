"""
Provides the Request object.
"""

import json, re
from cgi import parse_qs
from urllib.parse import urlsplit
from cookies import Cookies

ct_appjson = re.compile('^[^;]+/json(;|$)')

class Request:
    """
    Encapsulates the request information in a usable form.

    id
      An internal counter that may be useful for troubleshooting.  It is written to the log to
      help collate log lines.  Note that this value wraps at 2 billion and is not unique over
      time.  It should be plenty for logging.


    headers
      A dictionary containing the request headers.  The dictionary will
      automatically lowercase keys when inserted or used for lookup.

    cookies
      A dictionary (case-sensitive) mapping cookie names to values.

    form
      A dictionary of variables from either the query string if a GET
      or from form or JSON data if it is a POST.  These are preparsed
      so they can be passed to the route in parameters.
    """
    _next_id = 1

    _ohook = None
    # The json.loads object_hook.  Set this using configuration.config(decode_hook).

    def __init__(self, cnxn, method, url, headers, body):
        self.cnxn    = cnxn
        self.method  = method
        self.url     = url
        self.headers = headers
        self.body    = body

        # A counter to help troubleshoot.
        self.id = Request._next_id
        Request._next_id = (Request._next_id + 1) % 2^32-1

        self.form = self.parse_form()

        c = headers.get('cookie', None)
        if c:
            self.cookies = Cookies.from_request(c)
        else:
            self.cookies = Cookies()

    def __repr__(self):
        # Format for debugging, not normal logging.
        return '{}/{} {} body={} bytes'.format(self.id, self.method, self.url, len(self.body))

    def parse_form(self):
        """
        Stores variables into self.form so they can be passed to the URL handlers.

        POSTs will be parsed if the content is JSON or form encoded.  GETs will
        have their variables parsed.
        """
        if self.method == 'GET':
            return { key: val[0] for (key, val) in parse_qs(urlsplit(self.url)[3]).items() }

        if self.method in ('POST', 'PUT'):
            ct = self.headers.get('content-type') or ''
            if ct == 'application/x-www-form-urlencoded':
                return { key: val[0] for (key, val) in parse_qs(self.body.decode('utf8'), True).items() }

            # TODO: Look for charset, etc.
            if ct_appjson.match(ct):
                s = self.body.decode('UTF-8')
                return json.loads(s, object_hook=Request._ohook)

        return None
