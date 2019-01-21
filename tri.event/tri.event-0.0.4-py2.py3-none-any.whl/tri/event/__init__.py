import json
from datetime import (
    datetime,
    timedelta,
)
from logging import getLogger
from typing import (
    Dict,
    List,
    Union,
    Tuple,
    Callable,
)

import requests

__version__ = '0.0.4'

AUTH_CLIENT_ID = 'a2caed62-e28d-11e4-86da-b39459ee2d75'
AUTH_PROFILE_SCOPE = f'{AUTH_CLIENT_ID}:profile'


class EventType:
    def __init__(self, namespace: str, event_name: str):
        self.namespace = namespace
        self.event_name = event_name

    def __eq__(self, other):
        return isinstance(other, EventType) and self.namespace == other.namespace and self.event_name == other.event_name

    def __str__(self):
        return ":".join((self.namespace, self.event_name))

    def __repr__(self):
        return f'<EventType {self.namespace}:{self.event_name}>'

    @staticmethod
    def parse(s: str) -> 'EventType':
        namespace, separator, event_name = s.partition(':')
        assert separator
        return EventType(namespace=namespace, event_name=event_name)


class PublishEvent:
    def __init__(self, event_id: str, event_type: EventType, role_grants: List[Dict[str, str]], payload: object):
        self.event_id = event_id
        self.event_type = event_type
        self.role_grants = role_grants
        self.payload = payload

    def __eq__(self, other):
        return (
            isinstance(other, PublishEvent)
            and self.event_id == other.event_id
            and self.event_type == other.event_type
            and self.role_grants == other.role_grants
            and self.payload == other.payload
        )

    def __repr__(self):
        return f'<PublishEvent event_id={self.event_id} event_type={self.event_type} role_grants={self.role_grants}>'


class Event:
    def __init__(self, event_id: str, event_type: EventType, ack_ref: str, payload: object):
        self.event_id = event_id
        self.event_type = event_type
        self.ack_ref = ack_ref
        self.payload = payload

    def __eq__(self, other):
        return (
            isinstance(other, Event)
            and self.event_id == other.event_id
            and self.event_type == other.event_type
            and self.ack_ref == other.ack_ref
            and self.payload == other.payload
        )

    def __repr__(self):
        return f'<Event event_id={self.event_id} event_type={self.event_type} ack_ref={self.ack_ref}>'


class Subscription:
    def __init__(self, event_types: List[EventType], user_id: str, offset: str):
        self.event_types = event_types
        self.user_id = user_id
        self.offset = offset

    def __eq__(self, other):
        return (
            isinstance(other, Subscription)
            and self.event_types == other.event_types
            and self.user_id == other.user_id
            and self.offset == other.offset
        )

    def __repr__(self):
        return f'<Subscription user_id={self.user_id} event_types={self.event_types} offset={self.offset}>'


class PublishTopic:
    def __init__(self, event_name: str, role_required: str, scopes_required: List[str]):
        self.event_name = event_name
        self.role_required = role_required
        self.scopes_required = scopes_required

    def __eq__(self, other):
        return (
            isinstance(other, PublishTopic)
            and self.event_name == other.event_name
            and self.role_required == other.role_required
            and self.scopes_required == other.scopes_required
        )

    def __repr__(self):
        return f'<PublishTopic event_name={self.event_name} roles_required={self.role_required} scopes_required={self.scopes_required}>'


class Topic:
    def __init__(self, event_type: EventType):
        self.event_type = event_type

    def __eq__(self, other):
        return isinstance(other, Topic) and self.event_type == other.event_type

    def __str__(self):
        return ":".join((self.event_type.namespace, self.event_type.event_name))

    def __repr__(self):
        return f'<Topic {self.event_type.namespace}:{self.event_type.event_name}>'


class TriUnauthorized(Exception):
    pass


class TriAuthSessionException(Exception):
    pass


class TriException(Exception):
    def __init__(self, response):
        self.response = response
        super().__init__()

    def __str__(self):
        return f"<{self.__class__.__name__}: Code: {self.response.status_code} Result: {self.response.text} >"


class EventSession:
    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        username: str = None,
        password: str = None,
        refresh_token: str = None,
        scope: str = None,
        session_conf_fn: Callable[[requests.Session], None] = None,
        debug: bool = False,
        auth_url: str = None,
        logger_name: str = "tri.event",
        proxies: Dict[str, str] = None,
        timeout: Union[int, Tuple[int, int]] = (5.0, 5.0),
    ):
        """
        Create a session object that can be used to interact with /events and other API endpoints.

        :param base_url: TriOptima URL, eg. https://secure.trioptima.com.
        :param client_id: Oauth Client ID of the user logging in.
        :param client_secret: Oauth Client Secret of the user logging in.
        :param username: Username of the user logging in. If using username and password to authenticate.
        :param password: Password of the user logging in. If using username and password to authenticate.
        :param refresh_token: Refresh token for the user logging in. If using refresh token to authenticate.
        :param scope: Scopes to request as a space separated list. Only required if using username and password to authenticate.
        :param session_conf_fn: Callable taking a requests session. Can be used to set any additional retry policies, timeouts, etc.
        :param debug: If set to true some additional information will be printed for every request.
        :param auth_url: URL to authenticate against. If not set this will be the same as base_url.
        :param logger_name: Name to use when logging standard error/warning/info/debug messages.
        :param proxies: Requests style dict with any HTTP proxies that may be needed.
        :param timeout: Requests style timeout tuple for connect and read timeout.
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.debug = debug
        self.base_url = base_url
        self.auth_url = auth_url or base_url
        self.log = getLogger(logger_name)
        self.proxies = proxies
        self.timeout = timeout
        self.scope = scope
        self.username = username
        self.password = password
        self.refresh_token = refresh_token
        self.session_conf_fn = session_conf_fn

        self.session = None
        self.token_expiry = None

        # Automatically add this scope if not already present, it is required.
        if self.scope and AUTH_PROFILE_SCOPE not in self.scope:
            self.scope += f' {AUTH_PROFILE_SCOPE}'

        if bool(self.refresh_token) == bool(self.username or password):
            raise TriException('Authentication requires either a refresh token or username and password.')

        self._get_session()

    def _get_session(self):
        if self.session is None or datetime.now() > self.token_expiry:
            params = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }
            if self.refresh_token:
                params['grant_type'] = 'refresh_token'
                params['refresh_token'] = self.refresh_token
            else:
                params['grant_type'] = 'password'
                params['username'] = self.username
                params['password'] = self.password
            if self.scope:
                params['scope'] = self.scope

            kwargs = {'timeout': self.timeout}
            if self.proxies:
                kwargs['proxies'] = self.proxies

            resp = requests.post(f'{self.auth_url}/auth/api/v1/token', data=params, **kwargs)

            if not resp.status_code == 200:
                raise TriAuthSessionException(f'Authentication failed: {resp.text}')
            try:
                data = resp.json()
                access_token = data['access_token']
                expires_in = data['expires_in']
            except(ValueError, KeyError) as e:
                raise TriAuthSessionException(f'Unable to parse token response. Exception: {e} Response: {resp.text}')

            if self.debug and self.log:
                self.log.debug(f'Access token response: {data}')

            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
            self.session = requests.Session()
            self.session.headers.update({'Authorization': 'Bearer ' + access_token})

            if self.session_conf_fn:
                self.session_conf_fn(self.session)

        return self.session

    def close(self):
        self.session.close()

    def get(self, *args, **kw):
        return self._do_request('get', *args, **kw)

    def post(self, *args, **kw):
        return self._do_request('post', *args, **kw)

    def put(self, *args, **kw):
        return self._do_request('put', *args, **kw)

    def patch(self, *args, **kw):
        return self._do_request('patch', *args, **kw)

    def delete(self, *args, **kw):
        return self._do_request('delete', *args, **kw)

    def _do_request(self, verb, *args, expected_status_code=None, **kwargs):
        args = (self.base_url + args[0], *args[1:])

        if self.proxies:
            kwargs.setdefault('proxies', self.proxies)
        kwargs.setdefault('timeout', self.timeout)

        req_fn = getattr(self._get_session(), verb)
        response = req_fn(*args, **kwargs)

        if response.status_code == 401:
            raise TriUnauthorized
        if expected_status_code and response.status_code != expected_status_code:
            raise TriException(response=response)

        if self.debug and self.log:
            data = kwargs.get('json')
            if data:
                self.log.debug("Request: %s", json.dumps(data, indent=2))
            if response.text:
                if 'application/json' in response.headers['Content-Type']:
                    self.log.debug("Response: %s", json.dumps(json.loads(response.text), indent=2))
                else:
                    self.log.debug("Response: %s", response.text)

        return response

    def get_openapi(self) -> str:
        return self.get('/events/openapi.yaml', expected_status_code=200).text

    def publish_intent(self, namespace: str, intents: List[PublishTopic]) -> None:
        topics = [
            {
                'event_name': intent.event_name,
                'role_required': f'{self.client_id}:{intent.role_required}',
                'scope_required': [
                    f'{self.client_id}:{scope}'
                    for scope in intent.scopes_required
                ],
            }
            for intent in intents
        ]

        self.put(
            f'/events/topics/{namespace}',
            json={'topics': topics},
            expected_status_code=201,
        )

    def get_topics(self) -> List[Topic]:
        response = self.get('/events/topics', expected_status_code=200)
        data = response.json()
        return [
            Topic(event_type=EventType.parse(topic['event_type']))
            for topic in data['topics']
        ]

    def subscribe(self, event_types: List[EventType]) -> None:
        self.put(
            '/events/subscriptions',
            json={
                'event_types': [
                    f'{e.namespace}:{e.event_name}'
                    for e in event_types
                ],
            },
            expected_status_code=201,
        )

    def get_subscriptions(self, namespace) -> List[Subscription]:
        response = self.get(f'/events/subscriptions/{namespace}', expected_status_code=200)
        data = response.json()
        return [
            Subscription(
                event_types=[
                    EventType.parse(t)
                    for t in subscription['event_types']
                ],
                user_id=subscription['user_id'],
                offset=subscription['offset'],
            )
            for subscription in data['subscriptions']
        ]

    def publish(self, events: List[PublishEvent]) -> None:
        pevents = [
            {
                "event_id": event.event_id,
                "event_type": str(event.event_type),
                "payload": event.payload,
                "role_grants": event.role_grants,
            }
            for event in events
        ]
        self.post(
            '/events',
            json={"events": pevents},
            expected_status_code=201,
        )

    def poll(self, limit=1) -> List[Event]:
        response = self.get('/events', params=dict(limit=limit), expected_status_code=200)
        data = response.json()
        return [
            Event(
                event_id=event['event_id'],
                event_type=event['event_type'],
                ack_ref=event['ack_ref'],
                payload=event['payload'],
            )
            for event in data['events']
        ]

    def ack(self, ack_ref: str) -> None:
        self.put('/events/ack', json={'ack_ref': ack_ref}, expected_status_code=200)
