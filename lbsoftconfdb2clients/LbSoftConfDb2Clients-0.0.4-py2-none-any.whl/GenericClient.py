
from LbCommon.Script import Script
import sys
import os
import subprocess
import time
import logging

READ_ONLY_MODE = 1
WRITE_ALLOWED_MODE = 2


class LbSoftConfDbBaseClient(Script):

    READ_ONLY_SUFFIX = ':8080'
    WRITE_ALLOWED_SUFFIX = ':8090'

    def __init__(self, server_mode=READ_ONLY_MODE,
                 serverAddress='http://localhost',
                 *args, **kwargs):
        Script.__init__(self, *args, **kwargs)
        parser = self.parser
        parser.add_option("--noxmlrpc",
                          dest="noxmlrpc",
                          default=False,
                          action="store_true",
                          help="Use the direct interface to Neo4j "
                               "instead of XMLRPC")
        parser.add_option("--databaseURL",
                          dest="dbConnectStr",
                          default=None,
                          action="store",
                          help="Custom Neo4j database URL")
        parser.add_option("-d",
                          dest="debug",
                          action="store_true",
                          help="Display debug output")
        self.serverAddress = serverAddress
        self.server_mode = server_mode
        self.mConfDB = None
        self.mConfDBReadOnly = None
        self.log = logging.getLogger()


    def run(self, args=sys.argv[1:]):
        self.parseOpts(args)
        if self.options.debug:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.WARNING)
        if self.options.noxmlrpc:
            from LbSoftConfDb2Server.SoftConfDB import SoftConfDB
            self.mConfDB = SoftConfDB(dbConnectStr=self.options.dbConnectStr)
            self.mConfDBReadOnly = self.mConfDB
        else:
            from LbSoftConfDb2Clients.SoftConfDB import SoftConfDB
            address = None
            cookie = None

            if self.server_mode == READ_ONLY_MODE:
                address = "%s%s" % (self.serverAddress, self.READ_ONLY_SUFFIX)
            if self.server_mode == WRITE_ALLOWED_MODE:
                address = "%s%s" % (self.serverAddress,
                                    self.WRITE_ALLOWED_SUFFIX)
                cookie = self._check_cookie(self.serverAddress)
                addressReadOnly = "%s%s" % (self.serverAddress,
                                            self.READ_ONLY_SUFFIX)
                self.mConfDBReadOnly = SoftConfDB(addressReadOnly)
            self.mConfDB = SoftConfDB(address, cookie=cookie)
        Script.run(self, args=args)

    def _get_cookie_path(self):
        '''
        :return: The path for the server cookie on local disk
        '''
        return os.sep + os.path.join('tmp', os.environ['USER'],
                                     "ssocookie-lbsoftconfdb.txt")

    def _download_cookie(self, url, path):
        '''
        Invoke cern-get-sso-cookie to save the server cookie to path
        '''
        cmd = ["cern-get-sso-cookie", "--krb", "-u", url, "--reprocess", "-o",
               path]
        subprocess.check_call(cmd)

    def _check_cookie(self, url):
        '''
        Check whether we have a valid server cookie.
        If not, download one using the cern-get-sso-cookie command
        :return: The server cookie
        '''
        reload_cookie = False
        cookie_file_path = self._get_cookie_path()
        try:
            mtime = os.path.getmtime(cookie_file_path)
            if time.time() - mtime > 3600:
                reload_cookie = True
        except OSError:
            # In this case the file probably does not exist...
            reload_cookie = True

        if reload_cookie:
            url = 'https://ariadne-lhcb.cern.ch/'
            self._download_cookie(url, cookie_file_path)

        return self._get_cookie(cookie_file_path)

    def _get_cookie(self, cookie_file_path):
        """ A function to fetch the sso cookie for server. """
        result = ""
        if not os.path.exists(cookie_file_path):
            logging.debug(
                "No SSO cookie found for Neo4j at {0}, "
                "trying to connect to Neo4j without it.."
                .format(cookie_file_path))
            return result
        else:
            logging.debug(
                "Found SSO cookie for Neo4j at {0}".format(cookie_file_path))

        with open(cookie_file_path) as f:
            line = f.readline()
            while line:
                if line.startswith('#'):
                    line = f.readline()
                    continue
                splitted_line = line.rstrip('\n').split('\t')

                for s in splitted_line:
                    if s.startswith('_saml_idp') or s.startswith(
                            '_shibsession_'):
                        if result:
                            result += '; '
                        result += s + '=' + splitted_line[
                            splitted_line.index(s) + 1]
                        break
                line = f.readline()
        return result
