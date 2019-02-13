# coding=utf-8
from __future__ import print_function

from requests.auth import HTTPBasicAuth
import json
import subprocess
import requests
import logging
import random

logger = logging.getLogger(__name__)

def executeCommandWithResult(cmd):
    '''
    Run command and capture the output of the command
    '''
    status, result = subprocess.getstatusoutput(cmd)
    if status != 0:
        return None
    return result


def executeCommand(cmd):
    '''
    Run command
    '''
    status, result = subprocess.getstatusoutput(cmd)
    if status != 0:
        logger.error('Exited with {} status while trying to execute {}. Reason: {}'.format(status, cmd, result))
        exit(1)


def jsonFileToDict(filename):
    '''
    reads the json file specfied and returns it as a dictionary
    '''
    result = None
    if (filename is not None and filename.strip()):
        with open(filename.strip()) as f:
            result = json.load(f)
    if result is None:
        logger.error('Unable to read file "{}"'.format(filename))
        exit(1)
    return result

def get_iam_headers(aiosCredentials, env):
    # get a bearer token for storing historical measurementfacts
    iam_token = None
    if env['name'].lower() == 'icp':
        response = requests.get(
            u'{}/v1/preauth/validateAuth'.format(aiosCredentials['url']),
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            },
            auth=HTTPBasicAuth(aiosCredentials['username'], aiosCredentials['password']),
            verify=False
        )
        iam_token = response.json()['accessToken']
    else:
        token_data = {
            'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
            'response_type': 'cloud_iam',
            'apikey': aiosCredentials['apikey']
        }
        response = requests.post(env['iam_url'], data=token_data)
        iam_token = response.json()['access_token']
    iam_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % iam_token
    }
    return iam_headers

def get_error_message(response):
    """
    Gets the error message from a JSON response.
    :return: the error message
    :rtype: string
    """
    error_message = 'Unknown error'
    try:
        error_json = response.json()
        if 'error' in error_json:
            if isinstance(error_json['error'], dict) and 'description' in \
                    error_json['error']:
                error_message = error_json['error']['description']
            else:
                error_message = error_json['error']
        elif 'error_message' in error_json:
            error_message = error_json['error_message']
        elif 'message' in error_json:
            error_message = error_json['message']
        elif 'description' in error_json:
            error_message = error_json['description']
        elif 'errorMessage' in error_json:
            error_message = error_json['errorMessage']
        elif 'msg' in error_json:
            error_message = error_json['msg']
        return error_message
    except:
        return response.text or error_message

# random.choices() not available before Python 3.6
# expects a [] list of the choices and an equal-length [] list of integer weights
def choices(population, weights):
    sum_weights = 0
    for i in weights:
        sum_weights += i
    r = random.randint(0, sum_weights)
    choice = population[0]
    sum_weights = 0
    for i in range(len(weights)):
        sum_weights += weights[i]
        if r <= sum_weights:
            choice = population[i]
            break
    return choice
