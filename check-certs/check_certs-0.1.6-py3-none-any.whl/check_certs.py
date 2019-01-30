#!/usr/bin/env python

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime
from pluginbase import PluginBase
from . import utils

import copy
import logging
import os
import socket
import ssl
import sys
import yaml

class Site:
    def __init__(self, site, config):

        # self.port is set to the port in fqdn string first, then
        # config["port"], then defaults to 443.
        self.fqdn, *port = site.split(":")
        self.port = port[0] if port else config.get("port", None)
        self.port = self.port if self.port else 443

        self.notifiers = []
        self.notify_when_expiring_in = config.get(
            "notify_when_expiring_in", 35
        )

        # The set is used to keep a reference to the plugin, otherwise
        # it is removed and imports in the plugin modules fail.
        self.plugin_source = set()

        notifiers = config.get("notifiers", {})
        for name, params in notifiers.items():
            self._load_notifier(name, params)

        # Do this to support sites that use SNI feature becasue
        # ssl.get_server_certificate(...) doesn't support SNI.
        try:
            sock = ssl.SSLContext().wrap_socket(
                ssl.create_connection((self.fqdn, self.port), 10),
                server_hostname=self.fqdn
            )
        except socket.timeout as e:
            self.cert = None
            logging.warn(e)
            return self.cert
        except socket.gaierror as e:
            self.cert = None
            logging.warn(e)
            return self.cert

        pem_data = ssl.DER_cert_to_PEM_cert(sock.getpeercert(binary_form=True))
        sock.close()

        self.cert = x509.load_pem_x509_certificate(
            pem_data.encode("utf-8"),
            default_backend()
        )

    def _load_notifier(self, name, params={}):

        plugin_base = PluginBase(package="check_certs.plugins")
        plugin_source = plugin_base.make_plugin_source(
            searchpath=[
                os.path.join(os.path.dirname(__file__), "./plugins")
            ]
        )
        # keep a reference to the plugin
        self.plugin_source.add(plugin_source)
        plugin = plugin_source.load_plugin(name + "_notifier")

        plugin.setup(self, params)

    def register_notifier(self, notifier):
        self.notifiers.append(notifier)

    @property
    def expires_in_days(self):
        return (self.cert.not_valid_after - datetime.utcnow()).days

    def send_reminder(self):
        for i in self.notifiers:
            i.send({
                "site": self.fqdn,
                "not_valid_after": self.cert.not_valid_after,
                "expires_in_days": self.expires_in_days
            })

def main():

    if utils.env_is_debug():
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    args = utils.get_args(sys.argv[1:])

    logging.debug(args)

    with open(utils.config_file(), "r") as stream:
        config = yaml.load(stream)

    defaults = config["defaults"]

    # If sites is provided on the command line, then ignore the sites
    # listed in the config file.
    sites = args.sites if args.sites else config["sites"]

    sites_to_expire = []
    for s in sites:
        if isinstance(sites, dict):
            # this is the case when sites is read from a config file
            s_config = sites.get(s) or {}
        else:
            # this is the case when sites is read from command line
            s_config = {
                "port": args.port,
                "notify_when_expiring_in": args.notify_when_expiring_in,
            }

        site = Site(s, utils.deep_merge(copy.deepcopy(defaults), s_config))

        # site.cert should not be None

        if not site.cert:
            logging.warn("%s: unable to obtain its cert" % (s))
            continue

        # start to process the site

        if hasattr(args, "show") and args.show:
            logging.info("%s expires on %s, and in %d days" %
                (s, site.cert.not_valid_after, site.expires_in_days)
            )
            continue

        if site.expires_in_days <= site.notify_when_expiring_in:
            sites_to_expire.append(site)
        else:
            logging.info("%s: OK" % (s))

    for s in sites_to_expire:
        s.send_reminder()

if __name__ == "__main__":
    main()
