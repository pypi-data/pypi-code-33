from urllib.parse import urlencode
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
import opisense_client as oc
import requests
import json

""" Parameters """
API_URL = 'https://api.opinum.com:443/'
AUTHORIZATION_URL = 'https://identity.opinum.com/connect/token'
headers = {"Content-Type": "application/json",
           "Authorization": "",
           "X-Opisense-Api-Version": "1.1"}

""" Methods """


def GET(opisense_token: str, api_filter, json_output=False, feedback=False):
    """
    Get every Opisense Objects corresponding to the ApiFilter
    :param opisense_token: token needed to authorize the call. See "Authorize function"
    :param api_filter: ApiFilter object
    :param json_output: if Truem returns the json object from the response
    :param feedback: if True, prints HTTP response code in console
    :return:
    """
    headers['Authorization'] = opisense_token
    result = requests.get(API_URL + api_filter.path + '?' + urlencode(api_filter.filters, True), headers=headers)
    if feedback == True:
        print('Response: ' + str(result.status_code))
    if json_output:
        try:
            return result.json()
        except:
            raise ValueError('No JSON available in the response')
    else:
        return result


def POST(opisense_object, opisense_token: str, parent_id=None, force_path=None, feedback=False):
    """
    Creates a new Opisense Object
    :param opisense_object: Opisense Object to create
    :param opisense_token: token needed to authorize the call. See "Authorize function"
    :param parent_id: parent object ID needed to create some objects type
    :param feedback: if True, prints HTTP response code in console
    :param force_path: if specified, POST to this path instead of the default one
    :return:
    """
    if force_path:
        path = force_path
    else:
        path = opisense_object.api_path

    json_object = opisense_object.json()
    headers['Authorization'] = opisense_token
    if opisense_object.type == 'variable':
        if parent_id:
            result = requests.post(API_URL + "variables/source/" + str(parent_id), headers=headers, data=json_object)
        else:
            raise ValueError('The parent sourceId is mandatory to create a variable')
    else:
        result = requests.post(API_URL + path, headers=headers, data=json_object)
    if feedback == True:
        print('Response: ' + str(result.status_code))
    return result


def PUT(opisense_object, opisense_token: str, parent_id=None, force_path=None, feedback=False):
    """
    Updates existing Opisense Object
    :param opisense_object: Opisense Object to update
    :param opisense_token: token needed to authorize the call. See "Authorize function"
    :param parent_id: parent object ID needed to update some objects type
    :param feedback: if True, prints HTTP response code in console
    :param force_path: if specified, PUT to this path instead of the default one
    :return:
    """
    if force_path:
        path = force_path
    else:
        path = opisense_object.api_path

    json_object = opisense_object.json()
    headers['Authorization'] = opisense_token
    object_id = opisense_object.id
    if opisense_object.type == 'variable':
        if parent_id and object_id:
            result = requests.put(API_URL + "sources/" + str(parent_id) + "/variables/" + str(object_id),
                                  headers=headers,
                                  data=json_object)
        else:
            raise ValueError('The variableId and parent sourceId are mandatory to update a variable')
    else:
        if object_id:
            result = requests.put(API_URL + path + "/" + str(object_id), headers=headers,
                                  data=json_object)
        else:
            raise ValueError('The object id is mandatory to update an object')
    if feedback == True:
        print('Response: ' + str(result.status_code))
    return result


def DELETE(opisense_object, opisense_token: str, force_path=None, feedback=False):
    """
    Deletes existing Opisense Object
    :param opisense_object: Opisense Object to delete
    :param opisense_token: token needed to authorize the call. See "Authorize function"
    :param feedback: if True, prints HTTP response code in console
    :param force_path: if specified, DELETE to this path instead of the default one
    :return:
    """
    if force_path:
        path = force_path
    else:
        path = opisense_object.api_path

    headers['Authorization'] = opisense_token
    if opisense_object.id:
        result = requests.delete(API_URL + path + "/" + str(opisense_object.id), headers=headers)
    else:
        raise ValueError('The object id is mandatory to delete an object')
    if feedback == True:
        print('Response: ' + str(result.status_code))
    return result


def authorize(user_credentials: dict, api_credentials: dict, feedback=False):
    """
    gets Opisense Token
    :param user_credentials: dict containing 'client_id' , 'client_secret' and 'scope' keys
    :param api_credentials: dict containing 'username' and 'password' keys
    :param feedback: if True, prints HTTP response code in console
    :return: str : Opisense Token
    """
    client_id = api_credentials['client_id']
    client_secret = api_credentials['client_secret']
    scope = api_credentials['scope']
    oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
    token = oauth.fetch_token(token_url='https://identity.opinum.com/connect/token',
                              scope=scope,
                              username=user_credentials['username'],
                              password=user_credentials['password'],
                              client_id=client_id,
                              client_secret=client_secret,
                              auth=None)
    access_token = 'Bearer ' + token['access_token']
    if feedback == True:
        api_filter = oc.ApiFilter('account')
        account = GET(access_token, api_filter).json()
        print('Got a valid token for the account ' + str(account['id']) + ' - ' + str(account['name']))
    return access_token
