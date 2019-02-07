# Google AWS App plugin for cloudtoken.
#
# Author: Mike Fuller (mfuller@atlassian.com)


from .google_auth import Google
from pyquery import PyQuery
import argparse
import logging
import os
import pickle
import pwd
import requests


class Plugin(object):
    def __init__(self, config):
        self._config = config
        self._name = "google_aws"
        self._description = "Authenticate against Google AWS App."
        self._cookiejar = None
        self._session = requests.session()
        self._args = None
        self.logger = logging.getLogger(__name__)

    def __str__(self):
        return __file__

    @staticmethod
    def unset(args):
        pass

    @staticmethod
    def arguments(defaults):
        google_defaults = defaults.get("google-aws", {})
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-I",
            "--idp-id",
            help="Google SSO IDP identifier ($GOOGLE_IDP_ID)",
            default=google_defaults.get("idp_id", None),
        )
        parser.add_argument(
            "-S", "--sp-id", help="Google SSO SP identifier ($GOOGLE_SP_ID)", default=google_defaults.get("sp_id", None)
        )
        parser.add_argument(
            "-D",
            "--disable-u2f",
            action="store_true",
            help="Disable U2F functionality.",
            default=google_defaults.get("disable_u2f", True),
        )
        return parser

    def execute(self, data, args, flags):
        self._args = args
        self._cookiejar = "{}/cookiejar".format(args.cloudtoken_dir)
        self._load_cookies()
        try:
            google_client = Google(args, self._session)
            google_client.do_login()
            html = PyQuery(google_client.session_state.text)
            response = html("input[@name='SAMLResponse']")
            if response:
                saml_response = response[0].value
            else:
                raise Exception("SAML Response not found in response from Google {}".format(response))

            self._session = google_client.session
            if not args.daemon:
                self._write_cookies()

        except AttributeError as e:
            self.logger.exception("Unable to login to Google AWS IdP. Exiting. {}".format(e))
            exit(1)
        else:
            data.append({"plugin": self._name, "data": saml_response})
            return data

    def _load_cookies(self):
        """Read the cookies cache from disk.
        :return: True on success.
        """
        if os.path.isfile(self._cookiejar) and os.stat(self._cookiejar).st_size != 0:
            with open(self._cookiejar, "rb") as filehandle:
                self._session.cookies = pickle.load(filehandle)
                logging.debug("Loaded cached cookies: {}".format(self._session.cookies))
        self._session.cookies.clear_expired_cookies()

        return True

    def _write_cookies(self):
        """Write the cookie cache to disk.
        :return: True on success.
        """
        with open(self._cookiejar, "wb") as filehandle:
            pickle.dump(self._session.cookies, filehandle, protocol=4)
            os.chmod(self._cookiejar, 0o600)

        # Files get written out as root when in daemon mode so this fixes that.
        if self._args.daemon:
            if os.path.isfile(self._cookiejar):
                user = pwd.getpwnam(self._args.system_username)
                os.chown(self._cookiejar, user.pw_uid, user.pw_gid)
        return True
