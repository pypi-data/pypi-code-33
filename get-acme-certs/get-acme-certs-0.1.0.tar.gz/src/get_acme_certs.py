#! /usr/bin/env python

"""
    Script: get_acme_certs.py
    Source: https://gitlab.com/rveach/get-acme-certs
    Purpose: Gather Traefik TLS certificates from the acme.json file for use in other places.
"""

import argparse
import base64
import json
import os
import re

def split_fullchain(dest_dir, filename='fullchain.pem'):
    """
        The fullchain.pem is the certificate and csr.
        Most other apps need this in two separate files.
    """

    # full path to the fullchain file
    fc_file = os.path.join(dest_dir, filename)

    # regex match to pull everything from between the stanzas.
    pattern = re.compile(r"\-{5}BEGIN\sCERTIFICATE\-{5}[\s\S]+?\-{5}END\sCERTIFICATE\-{5}")
    with open(fc_file) as fc_fd:
        cert_matches = re.findall(pattern, fc_fd.read())

    # only proceed if we found 2, and write them to the right files.
    if len(cert_matches) == 2:

        cert_file_path = os.path.join(dest_dir, 'cert.pem')
        with open(cert_file_path, 'w') as cert_file:
            cert_file.write(cert_matches[0])
        os.chmod(cert_file_path, 0o600)

        chain_file_path = os.path.join(dest_dir, 'chain.pem')
        with open(chain_file_path, 'w') as chain_file:
            chain_file.write(cert_matches[1])
        os.chmod(chain_file_path, 0o600)
        

def write_file(cert_path, new_contents):
    """ shortcut to write the file """
    with open(cert_path, "wb") as cert_file:
        cert_file.write(new_contents)
    os.chmod(cert_path, 0o600)

def check_file(dest_dir, filename, new_contents):
    """ check to see if the file was updated. """
    cert_path = os.path.join(dest_dir, filename)
    cert_changed = False

    if os.path.exists(cert_path):
        with open(cert_path) as cert_file:
            old_contents = cert_file.read()

        if old_contents != new_contents:
            write_file(cert_path, new_contents)
            cert_changed = True

    else:
        write_file(cert_path, new_contents)
        cert_changed = True

    return cert_changed


def main(acme_json, domain, dest_dir):
    """ main function - do the work """

    # check requirements
    if not os.path.exists(acme_json):
        raise OSError("the acme.json file does not exit.")
    if not os.path.isdir(dest_dir):
        raise OSError("The destination directory does not exist.")

    # load data
    with open(acme_json, "r") as acme_file:
        acme_data = json.load(acme_file)

    # Read certificates
    for this_cert in acme_data['Certificates']:
        print(this_cert['Domain']['Main'])
        if this_cert['Domain']['Main'] == domain:
            print("match")
            domain_key = base64.b64decode(this_cert['Key'])
            domain_cert = base64.b64decode(this_cert['Certificate'])

    if not domain_cert:
        raise RuntimeError("Domain certificate could not be found.")
    if not domain_key:
        raise RuntimeError("Domain private key could not be found.")

    key_changed = check_file(dest_dir, 'privkey.pem', domain_key)
    cert_changed = check_file(dest_dir, 'fullchain.pem', domain_cert)

    if cert_changed:
        split_fullchain(dest_dir)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Grab a certificate out of Traefik's acme.json file")
    parser.add_argument('acme_json', help='path to the acme.json file')
    parser.add_argument('domain', help='domain to get certificate for')
    parser.add_argument('dest_dir',
                        help='path to the directory to store the certificate')

    args = parser.parse_args()
    main(args.acme_json, args.domain, args.dest_dir)
