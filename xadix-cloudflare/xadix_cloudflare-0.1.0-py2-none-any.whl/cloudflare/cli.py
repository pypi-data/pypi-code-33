#!/usr/bin/env python2

import logging
import argparse
import sys
import urlparse
import urllib
import copy
import httplib
import requests
import posixpath
import tabulate
import json
import os.path
import dns.resolver
import CloudFlare
#import . as dnspod
from . import *
from . import __version__

def get_public_ip():
    resolver = dns.resolver.Resolver(configure=False)
    nameservers = [ "ns{:d}.google.com".format(index) for index in range(1,5) ]
    logging.debug("using nameservers %s", nameservers)
    nameserver_ips = []
    for record in ["A", "AAAA"]:
        for nameserver in nameservers:
            for answer in dns.resolver.query(nameserver, record):
                nameserver_ips.append(answer.address)
    logging.debug("using nameserver_ips %s", nameserver_ips)
    resolver.nameservers = nameserver_ips
    answer = resolver.query("o-o.myaddr.l.google.com", "TXT")
    logging.debug("got answer = %s", answer)
    public_ip = answer[0].strings[0]
    logging.debug("got public_ip = %s", public_ip)
    return public_ip

def format_dlist(dlist, fmt):
    if fmt=="json":
        return json.dumps(dlist, sort_keys=True, indent=4)
    elif fmt=="table":
        if len(dlist) < 1: return ""
        headers = dlist[0].keys()
        rows = []
        for item in dlist:
            row = []
            for header in headers:
                row.append(item[header] if header in item else None)
            rows.append(row)
        return tabulate.tabulate(rows, headers)

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client

def main():
    logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%dT%H:%M:%S", stream=sys.stderr, format="%(asctime)s %(process)d %(thread)d %(levelno)03d:%(levelname)-8s %(name)-12s %(module)s:%(lineno)s:%(funcName)s %(message)s")

    config_dir = os.path.join(os.path.expanduser("~"),".config","xadix-cloudflare")

    root_parser = argparse.ArgumentParser(add_help = False, prog="xadix-cloudflare")
    root_parser.add_argument("--version", action="version", version="xadix-cloudflare {:s}".format(__version__))
    root_parser.add_argument("-v", "--verbose", action="count", dest="verbosity", help="increase verbosity level")
    root_parser.add_argument("-h", "--help", action="help", help="shows this help message and exit")

    root_parser.add_argument("-e", "--email", action="store", dest="email", type=str, required=False, default=None, help="...")
    root_parser.add_argument("-t", "--token", action="store", dest="token", type=str, required=False, default=None, help="...")
    root_parser.add_argument("--cache", action="store", dest="cache", type=str, required=False, default=os.path.join(config_dir,"cache.json"), help="...")
    root_parser.add_argument("--config", action="store", dest="config", type=str, required=False, default=os.path.join(config_dir,"config.json"), help="...")
    root_parser.add_argument("-f", "--format", action="store", dest="format", type=str, required=False, default="table", help="...")

    root_subparsers = root_parser.add_subparsers(dest="subparser0", help="...")

    domain_subparser = root_subparsers.add_parser("domain")
    domain_subparsers = domain_subparser.add_subparsers(dest="subparser1", help="...")

    domain_record_subparser = domain_subparsers.add_parser("record")
    domain_record_subparser.add_argument("-d", "--domain-name", action="store", dest="domain_name", type=str, required=True, help="...")
    domain_record_subparsers = domain_record_subparser.add_subparsers(dest="subparser2", help="...")

    domain_record_list_subparser = domain_record_subparsers.add_parser("list")

    domain_record_upsert_subparser = domain_record_subparsers.add_parser("upsert")
    domain_record_upsert_subparser.add_argument("-n", "--name", action="store", dest="record_name", type=str, required=True, help="...")
    domain_record_upsert_subparser.add_argument("-t", "--type", action="store", dest="record_type", type=str, required=True, help="...")
    #domain_record_upsert_subparser.add_argument("-v", "--value", action="store", dest="record_value", type=str, required=True, help="...")
    domain_record_upsert_subparser.add_argument("-x", "--ttl", action="store", dest="record_ttl", type=int, required=False, help="...")
    domain_record_upsert_subparser_value_group = domain_record_upsert_subparser.add_mutually_exclusive_group(required=True)
    domain_record_upsert_subparser_value_group.add_argument("-v", "--value", action="store", dest="record_value", type=str, default=None, help="...")
    domain_record_upsert_subparser_value_group.add_argument("--value-public", action="store_true", dest="record_value_public", default=False, help="...")
    arguments = root_parser.parse_args( args = sys.argv[1:] )

    if arguments.verbosity is not None:
        root_logger = logging.getLogger("")
        new_level = ( root_logger.getEffectiveLevel() - (min(1,arguments.verbosity))*10 - min(max(0,arguments.verbosity - 1),9)*1 )
        root_logger.setLevel( new_level )
        root_logger.propagate = True
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(new_level)
        requests_log.propagate = True
        http_client.HTTPConnection.debuglevel = 1


    logging.debug("sys.argv = %s, arguments = %s, logging.level = %s", sys.argv, arguments, logging.getLogger("").getEffectiveLevel())

    use_email = None
    if False: None
    elif arguments.email is not None:
        use_email = arguments.email
    elif "XADIX_CLOUDFLARE_EMAIL" in os.environ:
        use_email = os.environ["XADIX_CLOUDFLARE_EMAIL"]

    use_token = None
    if False: None
    elif arguments.token is not None:
        use_token = arguments.token
    elif "XADIX_CLOUDFLARE_TOKEN" in os.environ:
        use_token = os.environ["XADIX_CLOUDFLARE_TOKEN"]

    logging.debug("use_token=%s", use_token)
    logging.debug("use_email=%s", use_email)

    cf = CloudFlare.CloudFlare(email=use_email, token=use_token)
    record_types = ["A", "AAAA", "CNAME", "TXT", "SRV", "LOC", "MX", "NS", "SPF", "CERT", "DNSKEY", "DS", "NAPTR", "SMIMEA", "SSHFP", "TLSA", "URI"]
    if False: None
    elif arguments.subparser0 == "domain":
        if False: None
        elif arguments.subparser1 == "record":
            zones = cf.zones.get(params = {"name": arguments.domain_name})
            zone = zones[0]
            if "record_value" in arguments:
                use_record_value = arguments.record_value
                logging.debug("use_record_value = %s", use_record_value)
            if "record_value_public" in arguments and arguments.record_value_public:
                use_record_value = get_public_ip()
                logging.debug("use_record_value = %s", use_record_value)
            if False: None
            elif arguments.subparser2 == "list":
                for record_type in record_types:
                    records = cf.zones.dns_records.get(zone["id"], params={"type": record_type})
                    sys.stdout.write(format_dlist(records, arguments.format))
                    sys.stdout.write("\n")
            elif arguments.subparser2 == "upsert":
                records = cf.zones.dns_records.get(zone["id"], params={"type": arguments.record_type, "match": "all", "name": arguments.record_name, "per_page": 100})
                if records and len(records) > 0:
                    for record in records:
                        logging.info("updating record=%s", record)
                        result = cf.zones.dns_records.put(zone["id"], record["id"], data={"name": arguments.record_name, "type": arguments.record_type, "content": use_record_value, "ttl": arguments.record_ttl})
                        logging.info("result=%s", result)
                else:
                    result = cf.zones.dns_records.post(zone["id"], data={"name": arguments.record_name, "type": arguments.record_type, "content": use_record_value, "ttl": arguments.record_ttl})
                    logging.info("result=%s", result)

if __name__ == "__main__":
    main()
