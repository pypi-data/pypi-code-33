'''
Holds connection information for the project, as well as handles sending messages to Spark
@author Philip Whiting (phwhitin)
'''
import logging
from pymongo import MongoClient
import requests
LOGGER = logging.getLogger(__name__)

API_BASE = '/code/cda/notification/v1/publish'

SS1 = 'SCRAM-SHA-1'

JSON_HEADERS = {'Content-Type': 'application/json;charset=utf-8'}

class Connections(object):
    '''Configurable connections interface for interaction with remote resources'''

    def __init__(self, **kwargs):
        '''Init function'''
        self.environment = kwargs.get('environment')
        self.notification_api_url = kwargs.get('notification_api_url')
        self.mongo_groups = kwargs.get('mongo_groups', {})
        mongo_db_username = kwargs.get('mongo_db_username')
        mongo_db_password = kwargs.get('mongo_db_password')
        mongo_db_prefix = kwargs.get('mongo_db_prefix')
        if mongo_db_username and mongo_db_password and mongo_db_prefix:
            self.mongo_groups['default'] = {
                'mongo_db_username': mongo_db_username,
                'mongo_db_password': mongo_db_password,
                'mongo_db_prefix': mongo_db_prefix
            }

        self.default_spark_room = kwargs.get('default_spark_room')
        self.spark_token = kwargs.get('spark_token')
        self._mongos = {}
        self._auths = {}

    def publish_to_spark(self, msg, room=None):
        '''Publishes a message to the spark room via the notification API'''
        room = room or self.default_spark_room
        payload = _generate_api_payload(msg)
        destination = payload['destination']
        destination['roomId'] = room
        destination['bearerToken'] = self.spark_token
        return self._publish_payload(payload)

    def publish_email_obj(self, email, sender=''):
        '''Sends an email using the email object'''
        return self.publish_email(email.payload, sender, email.subject,
                                  email.tos, email.ccs, email.bccs)

    def publish_email(self, data, sender='', subject='', tos=None, ccs=None, bccs=None):
        '''Sends an email via the notification API'''
        payload = _generate_api_payload(data, message_type='EMAIL')
        payload['subject'] = subject
        payload['sender'] = sender
        destination = payload['destination']
        destination['emailAddresses'] = tos or []
        destination['ccEmailAddresses'] = ccs or []
        destination['bccEmailAddresses'] = bccs or []

        return self._publish_payload(payload)

    def _publish_payload(self, payload):
        '''Publishes the payload to the notification API'''
        return requests.post(self.notification_api_url + API_BASE,
                             headers=JSON_HEADERS, json=payload, verify=self.environment != 'dev')

    def get_mongo(self, num, *auth_dbs, **kwargs):
        '''
        Opens and returns a Mongo Client for dft-mongo-num for the specified auth dbs.
        This client is cached to prevent multiple connections
        '''
        if 'group' in kwargs:
            group = self.mongo_groups.get(kwargs.pop('group'))
        else:
            group = self.mongo_groups.get('default')
        host = self._get_host(num, group)
        client = self._mongos.get(host, MongoClient(host, 18000, **kwargs))
        auths = self._auths.get(host, [])
        for auth_db in auth_dbs:
            if not auth_db in auths:
                client[auth_db].authenticate(group['mongo_db_username'], group['mongo_db_password'],
                                             mechanism=SS1)
                auths.append(auth_db)

        self._auths[host] = auths
        if not host in self._mongos:
            self._mongos[host] = client

        return client

    def _get_host(self, num, group):
        '''Determines host based on config'''
        return {
            'prod': group['mongo_db_prefix'] + ('' if num <= 0 else '-' + str(num))
        }.get(self.environment, group['mongo_db_prefix'] + str(num + 1))

def _generate_api_payload(data, message_type='SPARK'):
    '''Generates the payload for a call to the notification API'''
    return {
        'data': data,
        'destination': {
            'type': message_type
        }
    }

def disable_warnings():
    '''Disables the SSL warnings about indesurec requests'''
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
