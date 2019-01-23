###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Created on May 6, 2013

@author: Ben Couturier
'''
import logging
import os
import subprocess
import time
from py2neo.rest import http_headers

ARIADNE_URL="https://ariadne-lhcb.cern.ch/"

def get_ariadne_cookie_path():
    '''
    :return: The path for the ariadne cooki on local disk
    '''
    return os.sep + os.path.join('tmp', os.environ['USER'], "ssocookie-ariadne.txt")


def download_cookie(url, path):
    '''
    Invoke cern-get-sso-cookie to save the ariadne cookie to path
    '''
    cmd = ["cern-get-sso-cookie", "--krb", "-u", url, "--reprocess",  "-o",  path ]
    subprocess.check_call(cmd)

    
def check_cookie(url, cookie_file_path):
    '''
    Check whether we have a valid ariadne cookie.
    If not, download one using the cern-get-sso-cookie command
    :return: The ariadne cookie 
    '''
    reload_cookie = False
    cookie_file_path = get_ariadne_cookie_path()
    try:
        mtime = os.path.getmtime(cookie_file_path)
        if time.time() - mtime > 3600:
            reload_cookie = True
    except OSError:
        # In this case the file probably does not exist...
        reload_cookie = True

    if reload_cookie:
        download_cookie(url, cookie_file_path)

    return get_cookie(cookie_file_path)


def get_cookie(cookie_file_path):
    """ A function to fetch the sso cookie for Ariadne. """
    result=""
    if not os.path.exists(cookie_file_path):
        logging.debug("No SSO cookie found for Ariadne at {0}, trying to connect to Ariadne without it.."
                             .format(cookie_file_path))
        return result
    else:
        logging.debug("Found SSO cookie for Ariadne at {0}".format(cookie_file_path))

    with open(cookie_file_path) as f:
        line = f.readline()
        while line:
            if line.startswith('#'):
                line = f.readline()
                continue
            splitted_line = line.rstrip('\n').split('\t')

            for s in splitted_line:
                if s.startswith('_saml_idp') or s.startswith('_shibsession_'):
                    if result: result += '; '
                    result += s + '=' + splitted_line[splitted_line.index(s) + 1]
                    break
            line = f.readline()
    return result


def with_CERN_SSO(function):
    ''' Decorator to check that the SSO cookie is present and loaded '''
    def check_CERN_SSO_and_run():

        #import ssl
        #ssl._create_default_https_context = ssl._create_unverified_context

        cookie = check_cookie(ARIADNE_URL, get_ariadne_cookie_path())

        # Adding the cookie to the py2neo HTTP headers
        http_headers.add("Cookie", cookie)

        # Now invoking the original function
        function()
        
    return check_CERN_SSO_and_run
