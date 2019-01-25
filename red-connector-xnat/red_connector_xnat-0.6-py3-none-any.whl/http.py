import jsonschema
import requests
from requests.auth import HTTPBasicAuth
from copy import deepcopy


_HTTP_METHODS = ['Get', 'Put', 'Post']
_HTTP_METHODS_ENUMS = deepcopy(_HTTP_METHODS) + [m.lower() for m in _HTTP_METHODS] + [m.upper() for m in _HTTP_METHODS]

_AUTH_METHODS = ['Basic', 'Digest']
_AUTH_METHODS_ENUMS = deepcopy(_AUTH_METHODS) + [m.lower() for m in _AUTH_METHODS] + [m.upper() for m in _AUTH_METHODS]


http_send_schema = {
    'type': 'object',
    'properties': {
        'baseUrl': {'type': 'string'},
        'project': {'type': 'string'},
        'subject': {'type': 'string'},
        'session': {'type': 'string'},
        'containerType': {'enum': ['scans', 'reconstructions', 'assessors']},
        'container': {'type': 'string'},
        'resource': {'type': 'string'},
        'xsiType': {'type': 'string'},
        'file': {'type': 'string'},
        'overwriteExistingFile': {'type': 'boolean'},
        'auth': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'}
            },
            'additionalProperties': False,
            'required': ['username', 'password']
        },
        'disableSSLVerification': {'type': 'boolean'},
    },
    'additionalProperties': False,
    'required': ['baseUrl', 'project', 'subject', 'session', 'containerType', 'container', 'file', 'auth']
}

http_receive_schema = {
    'oneOf': [{
        'type': 'object',
        'properties': {
            'baseUrl': {'type': 'string'},
            'project': {'type': 'string'},
            'subject': {'type': 'string'},
            'session': {'type': 'string'},
            'containerType': {'enum': ['scans', 'reconstructions', 'assessors']},
            'container': {'type': 'string'},
            'resource': {'type': 'string'},
            'file': {'type': 'string'},
            'auth': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'additionalProperties': False,
                'required': ['username', 'password']
            },
            'disableSSLVerification': {'type': 'boolean'},
        },
        'additionalProperties': False,
        'required': [
            'baseUrl', 'project', 'subject', 'session', 'containerType', 'container', 'resource', 'file', 'auth'
        ]
    }, {
        'type': 'object',
        'properties': {
            'baseUrl': {'type': 'string'},
            'project': {'type': 'string'},
            'subject': {'type': 'string'},
            'session': {'type': 'string'},
            'resource': {'type': 'string'},
            'file': {'type': 'string'},
            'auth': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'additionalProperties': False,
                'required': ['username', 'password']
            },
            'disableSSLVerification': {'type': 'boolean'},
        },
        'additionalProperties': False,
        'required': ['baseUrl', 'project', 'subject', 'session', 'resource', 'file', 'auth']
    }]
}


def _auth_method_obj(access):
    if not access.get('auth'):
        return None

    auth = access['auth']

    return HTTPBasicAuth(
        auth['username'],
        auth['password']
    )


class Http:
    @staticmethod
    def receive(access, internal):
        auth_method_obj = _auth_method_obj(access)

        verify = True
        if access.get('disableSSLVerification'):
            verify = False

        base_url = access['baseUrl'].rstrip('/')
        project = access['project']
        subject = access['subject']
        session = access['session']
        container_type = access.get('containerType')
        container = access.get('container')
        resource = access['resource']
        file = access['file']

        url = '{}/REST/projects/{}/subjects/{}/experiments/{}/resources/{}/files/{}'.format(
            base_url, project, subject, session, resource, file
        )

        if container_type:
            url = '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}'.format(
                base_url, project, subject, session, container_type, container, resource, file
            )

        r = requests.get(
            url,
            auth=auth_method_obj,
            verify=verify,
            stream=True
        )
        r.raise_for_status()

        with open(internal['path'], 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        r.raise_for_status()

        cookies = r.cookies

        r = requests.delete(
            '{}/data/JSESSION'.format(base_url),
            cookies=cookies,
            verify=verify
        )
        r.raise_for_status()

    @staticmethod
    def receive_validate(access):
        jsonschema.validate(access, http_receive_schema)

    @staticmethod
    def send(access, internal):
        auth_method_obj = _auth_method_obj(access)

        verify = True
        if access.get('disableSSLVerification'):
            verify = False

        base_url = access['baseUrl'].rstrip('/')
        project = access['project']
        subject = access['subject']
        session = access['session']
        container_type = access['containerType']
        container = access['container']
        resource = access.get('resource', 'OTHER')
        xsi_type = access.get('xsiType')
        file = access['file']
        overwrite_existing_file = access.get('overwriteExistingFile')

        r = requests.get(
            '{}/REST/projects/{}/subjects/{}/experiments/{}/{}?format=json'.format(
                base_url, project, subject, session, container_type
            ),
            auth=auth_method_obj,
            verify=verify
        )
        r.raise_for_status()
        existing_containers = r.json()['ResultSet']['Result']
        cookies = r.cookies

        try:
            container_exists = False
            existing_xsi_type = None

            for ec in existing_containers:
                if ('ID' in ec and ec['ID'] == container) or ('label' in ec and ec['label'] == container):
                    container_exists = True
                    existing_xsi_type = ec['xsiType']
                    break

            if not container_exists:
                # create container
                container_url = '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}'.format(
                    base_url, project, subject, session, container_type, container
                )

                if xsi_type:
                    container_url = '{}?xsiType={}'.format(container_url, xsi_type)

                r = requests.put(
                    container_url,
                    cookies=cookies,
                    verify=verify
                )
                r.raise_for_status()

                # create file
                with open(internal['path'], 'rb') as f:
                    r = requests.put(
                        '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}?inbody=true'.format(
                            base_url, project, subject, session, container_type, container, resource, file
                        ),
                        data=f,
                        cookies=cookies,
                        verify=verify
                    )
                    r.raise_for_status()

            else:
                if xsi_type and xsi_type != existing_xsi_type:
                    raise Exception(
                        'xsiType "{}" of existing container "{}" does not match provided xsiType "{}"'.format(
                            existing_xsi_type, container, xsi_type))

                r = requests.get(
                    '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources?format=json'.format(
                        base_url, project, subject, session, container_type, container
                    ),
                    cookies=cookies,
                    verify=verify
                )
                r.raise_for_status()
                existing_resources = r.json()['ResultSet']['Result']

                resource_exists = False
                for er in existing_resources:
                    if ('ID' in er and er['ID'] == resource) or ('label' in er and er['label'] == resource):
                        resource_exists = True
                        break

                if not resource_exists:
                    # create file
                    with open(internal['path'], 'rb') as f:
                        r = requests.put(
                            '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}?inbody=true'.format(
                                base_url, project, subject, session, container_type, container, resource, file
                            ),
                            data=f,
                            cookies=cookies,
                            verify=verify
                        )
                        r.raise_for_status()

                else:
                    r = requests.get(
                        '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files?format=json'.format(
                            base_url, project, subject, session, container_type, container, resource
                        ),
                        cookies=cookies,
                        verify=verify
                    )
                    r.raise_for_status()
                    existing_files = r.json()['ResultSet']['Result']

                    file_exists = False
                    for ef in existing_files:
                        if 'Name' in ef and ef['Name'] == file:
                            file_exists = True
                            break

                    if file_exists:
                        if not overwrite_existing_file:
                            raise Exception(
                                'File "{}" already exists and overwriteExistingFile is not set.'.format(file)
                            )
                        # delete file
                        r = requests.delete(
                            '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}'.format(
                                base_url, project, subject, session, container_type, container, resource, file
                            ),
                            cookies=cookies,
                            verify=verify
                        )
                        r.raise_for_status()

                    # create file
                    with open(internal['path'], 'rb') as f:
                        r = requests.put(
                            '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}?inbody=true'.format(
                                base_url, project, subject, session, container_type, container, resource, file
                            ),
                            data=f,
                            cookies=cookies,
                            verify=verify
                        )
                        r.raise_for_status()
        except Exception:
            # delete session
            r = requests.delete('{}/data/JSESSION'.format(base_url), cookies=cookies, verify=verify)
            r.raise_for_status()
            raise

        # delete session
        r = requests.delete('{}/data/JSESSION'.format(base_url), cookies=cookies, verify=verify)
        r.raise_for_status()

    @staticmethod
    def send_validate(access):
        jsonschema.validate(access, http_send_schema)
