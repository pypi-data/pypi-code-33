import argparse
import json
import os
import sys
import requests
import time
import datetime

import config
from crypto_helper import CryptoHelper
from urlparse import urljoin
from version import __version__

## Global variables
user_config = config.Config()
default_start_date = "19700101" # Arbitrary start date: Jan 1 1970
default_end_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y%m%d")  # Default is tomorrow

def set_base_url(args):
    user_config.base_url = args.base_url

def set_api_key(args):
    user_config.api_key = args.api_key
    user_config.headers = ("X-Openfin-Api-Key", user_config.api_key)

def set_private_key_file(args):
    user_config.private_key = args.private_key

def get_app_desktops(args):
    if not args.app_name:
        print "Error: must provide name of app as --app-name"
        return

    urls = [user_config.base_url, 'applications/', args.app_name + '/', 'desktops/']
    url = ""
    for u in urls:
        url = urljoin(url, u)
    res = requests.get(url, headers=user_config.headers)

    suffix_url = 'applications/' + args.app_name + '/desktops'
    url = urljoin(user_config.base_url, suffix_url)
    res = requests.get(url, headers=user_config.headers)
    if res.status_code != requests.codes.ok:
        print "Error: get_app_desktops", res
        return
    print json.dumps(res.json()["response"], indent=4, sort_keys=True)

def get_app_names():
    res = requests.get(urljoin(user_config.base_url, "applications"), headers=user_config.headers)
    try:
        print json.dumps(res.json(), indent=4, sort_keys=True)

    except Exception as e:
        print "Error parsing json={0}".format(e)

def get_desktop_logs(args):
    if not args.app_name:
        print "Error: must provide name of app as --app-name"
        return
    if not args.desktop_id:
        print "Error: must provide desktop id"
        return

    url = os.path.join(user_config.base_url, "applications", args.app_name, "desktops", args.desktop_id)
    res = requests.get(url, headers=user_config.headers)

    start_date, end_date = set_dates(args)
    query_params = {"startDate": start_date, "endDate": end_date}

    url = ''
    urls = [user_config.base_url, 'applications/', args.app_name + '/', 'desktops/', args.desktop_id]
    for u in urls:
        url = urljoin(url, u)

    res = requests.get(url, headers=user_config.headers, params=query_params)
    if res.status_code != requests.codes.ok:
        print "Error: get_desktop_logs", res
        print res.text
        return
    print json.dumps(res.json(), indent=4, sort_keys=True)

def get_logs(args):
    if not args.app_name:
        print "Error: must provide name of app as --app-name"
        return

    start_date, end_date = set_dates(args)
    query_params = {"startDate": start_date, "endDate": end_date}
    if args.username:
        query_params['userName'] = args.username

    suffix_url = 'Applications/' + args.app_name
    url = urljoin(user_config.base_url, suffix_url)

    res = requests.get(url, headers=user_config.headers, params=query_params)
    if res.status_code != requests.codes.ok:
        print "ERROR: --get-logs", res
        return
    print json.dumps(res.json(), indent=4, sort_keys=True)

def download_log(args):
    """
    Given the log uuid, we will receive:
        actual log - AES
        encrypted aes key - RSA
        encrypted aes initialization vector - RSA
    We will download the encrypted files and convert to the log zip file.
    """
    if not args.download_log:
        print "Error: must pass a log id with --download_log"
        return

    log_id = args.download_log
    suffix_url = 'logs/' + log_id
    url = user_config.base_url + suffix_url
    print url

    res = requests.get(url, headers=user_config.headers)
    if res.status_code != requests.codes.ok:
        print "Error: download_log", res
        return

    encrypted_aes_key = res.headers['Encrypted-AES-Key']
    encrypted_aes_iv = res.headers['Encrypted-AES-IV']
    if encrypted_aes_iv and encrypted_aes_key:
        print "Log will be saved with decryption."
        decrypted_aes_key = CryptoHelper.decrypt_rsa(encrypted_aes_key, user_config.private_key)
        if decrypted_aes_key is None:
            print "Error: decryption error"
            return

        decrypted_aes_iv = CryptoHelper.decrypt_rsa(encrypted_aes_iv, user_config.private_key)
        if decrypted_aes_iv is None:
            print "Error: decryption error"
            return

        encrypted_log = res.content
        zip_file_bits = CryptoHelper.decrypt_aes(encrypted_log, decrypted_aes_key, decrypted_aes_iv)
        if zip_file_bits:
            with open(log_id + '.zip', 'wb') as f:
                f.write(zip_file_bits)
        else:
            print "download log error"
    else:
        print "Log will not be saved with decryption."
        with open(log_id + '.zip', 'wb') as f:
            f.write(res.content)

def configure():
    """
    Prompts the user to set configuration, similar to `aws configure`
    """
    base_url = raw_input("base-url [leave blank for default=https://log-manager.openfin.co/api/v1/]: ")
    if base_url != "":
        user_config.base_url = base_url

    api_key = raw_input("api-key: ")
    user_config.api_key = api_key

    private_key_file = raw_input("private-key-file (e.g. C:\Users\me\.ssh\key.pem): ")
    user_config.private_key = private_key_file

    user_config.save()

def print_version():
    print __version__

def set_dates(args):
    start_date = default_start_date
    if args.start_date:
        start_date = args.start_date
    end_date = default_end_date
    if args.end_date:
        end_date = args.end_date

    return start_date, end_date

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--app-name", help="The name of the app")
    parser.add_argument("--get-app-desktops", action="store_true", help="Gets the app's desktops")
    parser.add_argument("--get-app-names", action="store_true", help="Gets application names")
    parser.add_argument("--get-desktop-logs", action="store_true", help="Get desktop logs")
    parser.add_argument("--get-logs", action="store_true", help="Gets logs for the specified application")
    parser.add_argument("--desktop-id", help="Desktop id")
    parser.add_argument("--start-date", help="Start date in ISO 8601 format")
    parser.add_argument("--end-date", help="End date in ISO 8601 format")
    parser.add_argument("--private-key", help="Private key file to decrypt log(s) with")
    parser.add_argument("--base-url", help="update registry with base url")
    parser.add_argument("--api-key", help="log api key to use")
    parser.add_argument("--download-log", help="download log with given uuid")
    parser.add_argument("--version", action="store_true", help="Shows the version")
    parser.add_argument("--configure", action="store_true", help="Configure the CLI")
    parser.add_argument("--username", help="Sets a username used for seeing app logs")

    args = parser.parse_args()

    ## Configuration settings flags
    if args.configure:
        configure()
        return

    if args.base_url:
        set_base_url(args)
    if args.api_key:
        set_api_key(args)
    if args.private_key:
        set_private_key_file(args)

    ## Log Management Api flags
    if args.get_app_desktops:
        get_app_desktops(args)
    elif args.get_app_names:
        get_app_names()
    elif args.get_desktop_logs:
        get_desktop_logs(args)
    elif args.get_logs:
        get_logs(args)
    elif args.download_log:
        download_log(args)

    ## Version / Other
    elif args.version:
        print_version()
    else:
        print "Invalid arguments"
        parser.print_help()

if __name__ == "__main__":
    sys.exit(main())
