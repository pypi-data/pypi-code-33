from __future__ import absolute_import, print_function

import functools
import importlib

import bs4
from future.builtins import next, object
from future.utils import python_2_unicode_compatible
from holviapi.connection import Connection as HolviApiConnection
from holviapi.connection import requests
from holviapi.errors import AuthenticationError

# Store multiple pool connections with singleton getter
SINGLETON_MAP = {}


@python_2_unicode_compatible
class ApiConnection(HolviApiConnection):

    @classmethod
    def singleton(self, pool, sessionid, driver_instance):
        """Get a singleton of a connection"""
        global SINGLETON_MAP
        mapkey = (pool, sessionid)
        if not mapkey in SINGLETON_MAP:
            SINGLETON_MAP[mapkey] = ApiConnection(pool, sessionid, driver_instance)
        return SINGLETON_MAP[mapkey]

    def __init__(self, poolname, sessionid, driver):
        self.pool = poolname
        self.sessionid = sessionid
        self.driver = driver

    def _init_session(self, copy_cookies=None):
        """Initializes a requests.Session for us if not already initialized"""
        if not self.session:
            self.session = requests.Session()
            self.session.headers.update({
                'Content-Type': 'application/json',
            })
        if copy_cookies:
            self.session.cookies.update(copy_cookies)
        self.session.remove_expired_responses()

    def sync_cookies_from_driver(self, driver=None):
        """Sync the webdriver cookies to our session"""
        if not self.driver and not driver:
            return
        if not driver:
            driver = self.driver
        self._init_session()
        for cookiedict in driver.get_cookies():
            del cookiedict['expiry'], cookiedict['httpOnly']
            self.session.cookies.set(**cookiedict)

    def sync_cookies_to_driver(self, driver=None):
        """Sync the session cookies to the webdriver"""
        if not self.driver and not driver:
            return
        if not driver:
            driver = self.driver
        self._init_session()
        for cookie in self.session.cookies:
            cookiedict = {
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'expiry': cookie.expires,
            }
            driver.add_cookie(cookiedict)

    def make_get(self, url, params={}):
        """Calls the parent method and then syncs cookies with driver"""
        ret = super(ApiConnection, self).make_get(url, params)
        self.sync_cookies_to_driver()
        return ret

    def _make_ppp(self, method, url, payload):
        """Calls the parent method and then syncs cookies with driver"""
        ret = super(ApiConnection, self)._make_ppp(method, url, payload)
        self.sync_cookies_to_driver()
        return ret


@python_2_unicode_compatible
class Connection(object):

    @classmethod
    def singleton(self, pool, username, password, driverpath='holvirc.chromedriver.driver'):
        """Get a singleton of a connection"""
        global SINGLETON_MAP
        mapkey = (pool, username, password)
        if not mapkey in SINGLETON_MAP:
            SINGLETON_MAP[mapkey] = Connection(pool, username, password, driverpath)
        return SINGLETON_MAP[mapkey]

    def __init__(self, pool, username, password, driverpath='holvirc.chromedriver.driver'):
        self.driverpath = driverpath
        self._driver = None
        self.pool = pool
        self.username = username
        self.password = password
        self.apiconnection = None
        self.login()

    @property
    def driver(self):
        if self._driver:
            return self._driver
        if isinstance(self.driverpath, str):
            parts = self.driverpath.split('.')
            attrname = parts[-1]
            modname = '.'.join(parts[:-1])
            mod = importlib.import_module(modname)
            self._driver = getattr(mod, attrname)
        else:
            self._driver = self.driverpath
        return self._driver

    @property
    def base_url_fmt(self):
        return self.apiconnection.base_url_fmt

    def login(self, username=None, password=None):
        """Log in with username and password, create API connection with the temp credentials"""
        if not username:
            username = self.username
        if not password:
            password = self.password
        tmp_connection = HolviApiConnection(None, None)
        tmp_connection._init_session()
        session = tmp_connection.session
        del session.headers['Authorization'], session.headers['Content-Type']

        login_get_response = session.get('https://holvi.com/login/')
        # Find the form and it's inputs
        soup = bs4.BeautifulSoup(login_get_response.content, features="html.parser")
        loginform = soup.find_all(lambda tag: tag.name == 'form' and tag.has_attr('action') and tag.attrs['action'] == '/login/')[0]
        formdict = {}
        for tag in loginform.find_all('input'):
            formdict[tag.attrs['name']] = tag.attrs.get('value')
        # Get rid of the fingerprint
        del formdict['fingerprint_components'], formdict['fingerprint']
        session.headers['Referer'] = 'https://holvi.com/login/'

        # Set username and password
        formdict['username'] = username
        formdict['pass1'] = password

        login_post_response = session.post('https://holvi.com/login/', data=formdict)
        if login_post_response.status_code in (403, 401):
            AuthenticationError("HTTP Access denied")
        auth_cookie = login_post_response.cookies.get('holvi_jwt_auth')
        if not auth_cookie:
            AuthenticationError("Could not find auth cookie")

        self.apiconnection = ApiConnection(self.pool, login_post_response.cookies.get('sessionid'), None)
        self.apiconnection._init_session(copy_cookies=session.cookies)

    def login_selenium(self, username=None, password=None):
        """Log in with username and password (via selenium), create API connection with the temp credentials"""
        from selenium.webdriver.common.keys import Keys
        import holvirc.helpers as helpers

        if not username:
            username = self.username
        if not password:
            password = self.password
        self.driver.get('https://holvi.com/login/')
        helpers.wait_for(functools.partial(helpers.element_found_by_name, self.driver, "username"))
        un_input = self.driver.find_element_by_name('username')
        un_input.clear()
        un_input.send_keys(username)
        pw_input = self.driver.find_element_by_name('pass1')
        pw_input.clear()
        pw_input.send_keys(password)
        with helpers.wait_for_page_load(self.driver):
            pw_input.send_keys(Keys.RETURN)
        auth_cookie = self.driver.get_cookie('holvi_jwt_auth')
        if not auth_cookie:
            AuthenticationError("Could not find auth cookie")
        self.apiconnection = ApiConnection(self.pool, self.driver.get_cookie('sessionid')['value'], self.driver)
        self.apiconnection.sync_cookies_from_driver()

    def make_get(self, *args, **kwargs):
        """Proxy to the actual API connection handler of the same name see holviapi.Connection"""
        return self.apiconnection.make_get(*args, **kwargs)

    def make_post(self, *args, **kwargs):
        """Proxy to the actual API connection handler of the same name see holviapi.Connection"""
        return self.apiconnection.make_post(*args, **kwargs)

    def make_put(self, *args, **kwargs):
        """Proxy to the actual API connection handler of the same name see holviapi.Connection"""
        return self.apiconnection.make_put(*args, **kwargs)

    def make_patch(self, *args, **kwargs):
        """Proxy to the actual API connection handler of the same name see holviapi.Connection"""
        return self.apiconnection.make_patch(*args, **kwargs)
