#!/usr/bin/env python

import re
import time
import requests
from getpass import getpass


def authn():
    username = 's103151'
    password = getpass()
    org_url = 'https://bbva-us.okta.com'

    headers = {'content-type': 'application/json'}
    data = {'username': username, 'password': password}

    okta_resp = requests.post('{}/api/v1/authn'.format(org_url), headers=headers, json=data)

    if okta_resp.ok:
        response_data = okta_resp.json()
        status = response_data['status']
        if status == 'SUCCESS':
            sessionToken = response_data['sessionToken']
        elif status == 'MFA_ENROLL':
            sessionToken = handle_enroll(org_url, response_data)
        elif status == 'MFA_REQUIRED':
            sessionToken = handle_mfa(org_url, response_data)
        else:
            raise Exception('Something went wrong!\n{}'.format(response_data))

        print('Session Token: {}'.format(sessionToken))

        session_id = fetchSessionId(org_url, sessionToken)
        print('Session ID: {}'.format(session_id))


def handle_enroll(org_url, response_data):
    qr_code_url = 'https://qrcode-term.herokuapp.com/qr'
    data = response_data['_embedded']
    factors = [factor['factorType'] for factor in data['factors']]
    print('The following factors are available:\n {}'.format('\n'.join(factors)))
    state_token = response_data['stateToken']

    headers = {'content-type': 'application/json'}
    enroll_request_data = {'stateToken': state_token, 'factorType': 'push', 'provider': 'OKTA'}
    enroll_response = requests.post(
        '{}/api/v1/authn/factors'.format(org_url),
        headers=headers,
        json=enroll_request_data
    )
    enroll_data = enroll_response.json()
    status = enroll_data['status']
    factor_id = enroll_data['_embedded']['factor']['id']
    if status != 'MFA_ENROLL_ACTIVATE':
        raise Exception('Unexpected status: {}. \n{}'.format(status, enroll_data))

    qr_url = enroll_data['_embedded']['factor']['_embedded']['activation']['_links']['qrcode']['href']
    print(qr_url)
    requests.get(qr_code_url, json={'qrUrl': qr_code_url}, headers=headers)
    # Add wait for user to scan here

    factor_enroll_url = '{}/api/v1/authn/factors/{}/lifecycle/activate/poll'.format(org_url, factor_id)
    factor_enroll = requests.post(factor_enroll_url, headers=headers, json=enroll_request_data)
    factor_enroll_json = factor_enroll.json()
    factor_enroll_status = factor_enroll_json['status']
    if factor_enroll_status != 'SUCCESS':
        raise Exception('Unexpected status: {}.\n{}'.format(factor_enroll_status, factor_enroll_json))
    return factor_enroll_json['sessionToken']


def handle_mfa(org_url, response_data):
    state_token = response_data['stateToken']
    factors = response_data['_embedded']['factors']
    push_factor_id = [factor['id'] for factor in factors if factor['factorType'] == 'push'][0]

    status = 'MFA_CHALLENGE'
    tries = 0
    headers = {'content-type': 'application/json'}
    verify_data = {'stateToken': state_token}
    verify_url = '{}/api/v1/authn/factors/{}/verify'.format(org_url, push_factor_id)
    while (status == 'MFA_CHALLENGE' and tries < 10):
        verify_response = requests.post(verify_url, headers=headers, json=verify_data)
        verify_response_json = verify_response.json()
        status = verify_response_json['status']
        tries += 1
        print('Waiting for Okta push notification...')
        time.sleep(10)

    if status != 'SUCCESS':
        raise Exception('MFA Failed, try again.')

    return verify_response_json['sessionToken']


def fetchSessionId(org_url, session_token):
    session_id = ''
    session_url = '{}/login/sessionCookieRedirect'.format(org_url)
    session_params = {
        'checkAccountSetupComplete': 'true',
        'token': session_token,
        'redirectUrl': 'https://{}/user/notifications'.format(org_url)
    }
    session_id_response = requests.get(session_url, params=session_params)
    sid_re = re.compile(r'.*sid=([^;]*);.*')
    session_id_match = re.match(sid_re, session_id_response.headers.get('Set-Cookie'))
    if session_id_match:
        if len(session_id_match.groups()) > 0:
            session_id = session_id_match.groups()[0]
    return session_id


if __name__ == '__main__':
    authn()

# import os
# import re
# import sys
# import configparser
# from getpass import getpass
# import stsauth
# from stsauth import STSAuth
# import bs4
# from bs4 import BeautifulSoup

# username = 's103151'
# password = getpass()
# credentialsfile = '~/.aws/credentials'

# sts_auth = STSAuth(username, password, credentialsfile)

# sts_auth.parse_config_file()
# response = sts_auth.session.get(sts_auth.idpentryurl)
# response.soup = BeautifulSoup(response.text, "lxml")
# login_form = response.soup.find(id='loginForm')
# okta_login = response.soup.find(id='okta-login-container')

# form_response = sts_auth.authenticate_to_adfs_portal(response)
# form_response.soup = BeautifulSoup(form_response.text, "lxml")
# login_form = form_response.soup.find(id='loginForm')
# okta_login = form_response.soup.find(id='okta-login-container')
