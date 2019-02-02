import time
import json
import logging
import secrets
import hashlib
import argparse
from typing import Iterator, Any, Dict, Tuple, List

import requests
from sseclient import SSEClient

logger = logging.getLogger(__name__)

SERVER = 'http://dicetrust.com'


class Error(Exception):

    def __init__(self, id: str):
        self.id = id


class Client:

    def __init__(self, server=SERVER):
        self.server = server
        self.session = requests.Session()

    def _request(self, method, path, **kwargs):
        url = self.server + path
        response = self.session.request(method, url, **kwargs)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 400:
                error_id = None
                try:
                    error_id = e.response.json()['error']
                except Exception:
                    pass

                if error_id:
                    raise Error(error_id)

            raise

        return response

    def create_session(self, mod: int) -> Dict[str, Any]:
        r = self._request('POST', '/api/session', data={'mod': mod})
        return r.json()

    def get_session(self, session_id: str) -> Dict[str, Any]:
        r = self._request('GET', '/api/session/' + session_id)
        return r.json()

    def generate_integer(self, session_id: str) -> Tuple[int, int]:
        session = self.get_session(session_id)
        mod = session['mod']
        logger.debug("getting a random number below %d", mod)

        my_secret = secrets.token_bytes(32)
        my_digest = hashlib.sha256(my_secret).digest()

        digests = self._add_digest(session_id, my_digest)
        assert my_digest in digests

        all_secrets = self._add_secret(session_id, my_secret)
        assert my_secret in all_secrets

        # Check each secret matches a digest
        n = int.from_bytes(bytes.fromhex('ffffffff'), 'big')
        digests = list(digests)
        for secret in all_secrets:
            assert len(secret) == 32
            digests.remove(hashlib.sha256(secret).digest())

            secret_int = int.from_bytes(secret[:4], 'big')
            n ^= secret_int

        assert len(digests) == 0

        number = n % mod
        logger.debug("generated number is: %d", number)
        return number, mod

    def _add_digest(self, session_id: str, digest: bytes) -> List[bytes]:
        path = '/api/session/' + session_id + '/digests'
        r = self._request('POST', path, data={'digest': digest.hex()})
        digests = r.json()['digests']
        return [bytes.fromhex(s) for s in digests]

    def _add_secret(self, session_id: str, secret: bytes) -> List[bytes]:
        path = '/api/session/' + session_id + '/secrets'
        r = self._request('POST', path, data={'secret': secret.hex()})
        secrets = r.json()['secrets']
        return [bytes.fromhex(s) for s in secrets]

    def subscribe_events(self, session_id: str, last_id: str = None) -> Iterator[Dict[str, Any]]:
        url = self.server + '/api/session/' + session_id + '/events'
        events = SSEClient(url, last_id)
        for event in events:
            yield {
                    'id': event.id,
                    'event': event.event,
                    'data': json.loads(event.data),
            }

    def get_rounds(self, session_id: str) -> List[Dict[str, Any]]:
        r = self._request('GET', '/api/session/' + session_id + '/rounds')
        return r.json()['rounds']


def _cmd_create_session(client: Client, args) -> str:
    return client.create_session(args.mod)['id']


def _cmd_get_session(client: Client, args) -> str:
    return json.dumps(client.get_session(args.session_id))


def _cmd_get_rounds(client: Client, args) -> str:
    return json.dumps(client.get_rounds(args.session_id))


def _cmd_generate_integer(client: Client, args) -> str:
    return '%d %% %d' % client.generate_integer(args.session_id)


def _cmd_subscribe_events(client: Client, args) -> str:
    events = client.subscribe_events(args.session_id, args.last_id)
    for event in events:
        print('%s: %s' % (event['event'], event['data']))

    return ''


def _entry_point():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', default=SERVER)
    parser.add_argument('-l', '--logging-level', default='warning', choices=['debug', 'info', 'warning', 'error'])

    subparsers = parser.add_subparsers(dest='subparser_name', help='sub-command name', required=True)

    parser_create_session = subparsers.add_parser('create-session')
    parser_create_session.set_defaults(func=_cmd_create_session)
    parser_create_session.add_argument('mod', type=int)

    parser_create_session = subparsers.add_parser('get-session')
    parser_create_session.set_defaults(func=_cmd_get_session)
    parser_create_session.add_argument('session_id')

    parser_create_session = subparsers.add_parser('get-rounds')
    parser_create_session.set_defaults(func=_cmd_get_rounds)
    parser_create_session.add_argument('session_id')

    parser_generate_random_int = subparsers.add_parser('generate-integer')
    parser_generate_random_int.set_defaults(func=_cmd_generate_integer)
    parser_generate_random_int.add_argument('session_id')

    parser_subscribe_events = subparsers.add_parser('subscribe-events')
    parser_subscribe_events.set_defaults(func=_cmd_subscribe_events)
    parser_subscribe_events.add_argument('session_id')
    parser_subscribe_events.add_argument('--last_id')

    args = parser.parse_args()

    if args.logging_level:
        logging_level = getattr(logging, args.logging_level.upper())
        logging.basicConfig(level=logging_level)

    client = Client(server=args.server)

    start = time.time()
    output = args.func(client, args)
    end = time.time()

    delta = end - start
    delta = int(delta * 1000)
    logger.info("got result in %d milliseconds", delta)

    print(output)


if __name__ == '__main__':
    _entry_point()
