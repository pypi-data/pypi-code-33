
# encoding: utf-8

# =========================================
#       IMPORTS
# --------------------------------------

import rootpath

rootpath.append()

import mybad
import inspecta

import re
import yaml

try:
    from urllib.parse import urlencode
except:
    # Python 2
    from urllib import urlencode


# =========================================
#       CCONSTANTS
# --------------------------------------

DEFAULT_URI = None
DEFAULT_URI_PROTOCOL = 'http'
DEFAULT_URI_AUTH = None
DEFAULT_URI_HOST = 'localhost'
DEFAULT_URI_PORT = 80
DEFAULT_URI_ENDPOINT = ':'.join([str(DEFAULT_URI_HOST), str(DEFAULT_URI_PORT)])
DEFAULT_URI_PATH = '/'
DEFAULT_URI_QUERY = {}

URI_TEST_PATTERN = re.compile('^[a-z]+://')

DEFAULT_SERIALIZER_TEST_PATTERN = URI_TEST_PATTERN


# =========================================
#       ERRORS
# --------------------------------------

class URIError(mybad.Error):
    pass


# =========================================
#       CLASSES
# --------------------------------------

class URI(object):

    Error = URIError

    def serialize(self, data):
        try:
            if data is None:
                return None

            if not isinstance(data, dict):
                data = {}

            protocol = data.get('protocol', None) or DEFAULT_URI_PROTOCOL
            auth = data.get('auth', None) or DEFAULT_URI_AUTH
            host = data.get('host', None) or DEFAULT_URI_HOST
            hosts = data.get('hosts', None) or [host]
            port = data.get('port', None) or DEFAULT_URI_PORT
            ports = data.get('ports', None) or [port]
            path = data.get('path', None) or DEFAULT_URI_PATH
            query = data.get('query', None) or DEFAULT_URI_QUERY

            # TODO: add sophisticated support for `auth` (~credentials)

            endpoints = []

            for host_index, host in enumerate(hosts):
                try:
                    port = ports[host_index]
                except:
                    port = port

                endpoint = '{host}:{port}'.format(
                    host = host,
                    port = port,
                )

                endpoints.append(endpoint)

            endpoints = ','.join(endpoints)

            result = '{protocol}://{auth}@{endpoints}{path}?{query}'.format(
                protocol = protocol,
                auth = auth,
                endpoints = endpoints,
                path = path,
                query = urlencode(query),
            )

            result = result.replace('None', '')
            result = result.replace(':@', '@')
            result = result.replace('//@', '//')

            if not query:
                result = result.replace('?', '')

            return result

        except Exception as error:
            raise URIError(error, details = {
                'data': data,
            })

    def deserialize(self, data):
        try:
            if data is None:
                return None

            data = data or DEFAULT_URI

            protocol = None
            auth = None

            endpoint = None
            endpoints = []
            host = None
            hosts = []
            port = None
            ports = []

            path = None
            query = None

            next_segment = str(data)

            try:
                if '://' in next_segment:
                    protocol = next_segment.split('://')[0]
                    next_segment = '://'.join(next_segment.split('://')[1:])
                else:
                    protocol = DEFAULT_URI_PROTOCOL
            except:
                protocol = DEFAULT_URI_PROTOCOL
            finally:
                if protocol is None or protocol == '' or protocol == '0':
                    protocol = DEFAULT_URI_PROTOCOL

            try:
                if '@' in next_segment:
                    auth = next_segment.split('@')[0]
                    next_segment = '@'.join(next_segment.split('@')[1:])
                else:
                    auth = DEFAULT_URI_AUTH
            except:
                auth = DEFAULT_URI_AUTH
            finally:
                if auth is None or auth == '' or auth == '0':
                    auth = DEFAULT_URI_AUTH

            try:
                if next_segment.startswith('/'):
                    endpoint = DEFAULT_URI_ENDPOINT
                else:
                    endpoint = next_segment.split('/')[0]
                    next_segment = '/'.join(next_segment.split('/')[1:])
            except:
                endpoint = DEFAULT_URI_ENDPOINT
            finally:
                if endpoint is None or endpoint == '' or endpoint == '0':
                    endpoint = DEFAULT_URI_ENDPOINT

            try:
                endpoints = endpoint.split(',')

                for index, endpoint in enumerate(endpoints):
                    endpoint_parts = endpoint.split(':')

                    has_port = len(endpoint_parts) > 1 and len(endpoint_parts[1])

                    if not has_port:
                        endpoint = '{0}:{1}'.format(endpoint, DEFAULT_URI_PORT)

                    endpoints[index] = endpoint

                for endpoint in endpoints:
                    if len(endpoint):
                        endpoint_parts = endpoint.split(':')

                        try:
                            host = endpoint_parts[0]
                        except:
                            host = DEFAULT_URI_HOST
                        finally:
                            if host is None or host == '' or host == '0':
                                host = DEFAULT_URI_HOST

                            hosts.append(host)

                        try:
                            port = endpoint_parts[1]
                        except:
                            port = DEFAULT_URI_PORT
                        finally:
                            port = int('{0}'.format(port).replace(':', ''))

                            if port is None or port == '' or port == '0':
                                port = DEFAULT_URI_PORT

                            ports.append(port)
            except:
                pass

            try:
                endpoint = endpoints[0]
            except:
                pass

            try:
                host = hosts[0]
            except:
                pass

            try:
                port = ports[0]
            except:
                pass

            try:
                if '?' in next_segment:
                    path = next_segment.split('?')[0]
                else:
                    path = next_segment

                next_segment = '?'.join(next_segment.split('?')[1:])

                if not path.startswith('/'):
                    path = '/{0}'.format(path)

            except:
                path = DEFAULT_URI_PATH
            finally:
                if path is None or path == '' or path == '0':
                    path = DEFAULT_URI_PATH

            try:
                if '?' in next_segment:
                    query = next_segment.split('?')[1]
                else:
                    query = DEFAULT_URI_QUERY
            except:
                query = DEFAULT_URI_QUERY
            finally:
                if query is None or query == '' or query == '0':
                    query = DEFAULT_URI_QUERY

            auth = auth and auth.strip()
            credentials = {
                'username': None,
                'password': None,
            }

            if auth:
                auth = dict(enumerate(auth.split('://'))).get(1, auth) # handle potential `protocol` clash

                if auth == ':':
                    auth = None

                if auth and len(auth):
                    auth_object = dict(enumerate(auth.split(':')))

                    username = auth_object.get(0, '').strip()
                    password = auth_object.get(1, '').strip()

                    if not len(username):
                        username = None

                    if not len(password):
                        password = None

                    credentials['username'] = username
                    credentials['password'] = password

                else:
                    auth = None

            key = path and path.strip('/').strip()

            if not len(key):
                key = None

            result = {
                'protocol': protocol,
                'auth': auth,

                'endpoint': endpoint,
                'endpoints': endpoints,

                'host': host,
                'hosts': hosts,

                'port': port,
                'ports': ports,

                'path': path,
                'query': query,

                # commonly useful values

                'credentials': credentials,

                'key': key,
                'namespace': key,
            }

            url = self.serialize(result)

            result['url'] = url

            urls = []

            for endpoint_index, endpoint in enumerate(endpoints):
                endpoint_result = {
                    'protocol': protocol,
                    'auth': auth,

                    'endpoint': endpoint,
                    'endpoints': [endpoint],

                    'host': host,
                    'hosts': [hosts[endpoint_index]],

                    'port': port,
                    'ports': [ports[endpoint_index]],

                    'path': path,
                    'query': query,

                    # commonly useful values

                    'credentials': credentials,
                    'key': key,
                }

                endpoint_url = self.serialize(endpoint_result)

                urls.append(endpoint_url)

            result['urls'] = urls

            return result

        except Exception as error:
            raise URIError(error, details = {
                'data': data,
            })

    def pack(self, *args, **kwargs):
        return self.serialize(*args, **kwargs)

    def unpack(self, *args, **kwargs):
        return self.deserialize(*args, **kwargs)

    def stringify(self, *args, **kwargs):
        return self.serialize(*args, **kwargs)

    def parse(self, *args, **kwargs):
        return self.deserialize(*args, **kwargs)

    def get(self, data):
        if isinstance(data, dict):
            data = self.serialize(data)
            data = self.deserialize(data)
        else:
            data = self.deserialize(data)
            data = self.serialize(data)

        return data

    def test(self, data):
        try:
            if data is None:
                return False

            if not isinstance(data, str):
                return False

            result = re.match(DEFAULT_SERIALIZER_TEST_PATTERN, data)

            return bool(result)

        except Exception as error:
            raise URIError(error, details = {
                'data': data,
            })


# =========================================
#       EXPORTS
# --------------------------------------

Error = URIError

uri = URI()

def serialize(*args, **kwargs):
    return uri.serialize(*args, **kwargs)

def deserialize(*args, **kwargs):
    return uri.deserialize(*args, **kwargs)

def pack(*args, **kwargs):
    return uri.pack(*args, **kwargs)

def unpack(*args, **kwargs):
    return uri.unpack(*args, **kwargs)

def stringify(*args, **kwargs):
    return uri.stringify(*args, **kwargs)

def parse(*args, **kwargs):
    return uri.parse(*args, **kwargs)

def get(*args, **kwargs):
    return uri.get(*args, **kwargs)

def test(*args, **kwargs):
    return uri.test(*args, **kwargs)
