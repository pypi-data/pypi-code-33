import codecs
import json
import logging
import time
from collections import namedtuple

from minty import Base
from pyramid.httpexceptions import HTTPUnauthorized
from redis import StrictRedis


class SessionRetrieverError(Exception):
    """Base for session retrieval related exceptions."""

    pass


class SessionNotFoundError(SessionRetrieverError, ValueError):
    """Session can't be found in Redis."""

    pass


class SessionDataNotFoundError(SessionRetrieverError, ValueError):
    """Session data can't be found in Redis."""

    pass


class SessionRetriever(Base):
    """HTTP session retriever.

    retrieves a session stored by the Perl application from the Redis store
    """

    __slots__ = ["redis", "decoder"]

    def __init__(self, redis: StrictRedis):
        """Initialize a HTTP session retriever.

        :param redis: Redis connection object to retrieve session data
        :type redis: StrictRedis
        """
        self.redis = redis

    def retrieve(self, session_id: str) -> dict:
        """Retrieve a session from Redis.

        :param session_id: session id to retrieve
        :type session_id: str
        :raises SessionNotFoundError: if the session cannot be found
        :raises SessionDataNotFoundError: if the session is found, but contains
                                          no data
        :return: the session data
        :rtype: dict
        """
        now = time.time()
        with self.statsd.get_timer("retrieve").time("redis.get_expires.time"):
            expiration = self.redis.get(f"expires:{session_id}")

        if expiration is None:
            self.logger.info(f"Session '{session_id}' not found")
            self.statsd.get_counter("retrieve").increment(
                "redis.get_session.not_found.count"
            )
            raise SessionNotFoundError(session_id)

        if float(expiration) < now:
            self.logger.info(f"Session '{session_id}' has expired")
            self.statsd.get_counter("retrieve").increment(
                "redis.get_session.not_found.count"
            )
            raise SessionNotFoundError(session_id)

        with self.statsd.get_timer("retrieve").time("redis.get_session.time"):
            session_data_raw = self.redis.get(f"json:session:{session_id}")

        if session_data_raw is None:
            self.logger.info(f"Session '{session_id}' not found")
            self.statsd.get_counter("retrieve").increment(
                "redis.get_session.not_found.count"
            )
            raise SessionDataNotFoundError(session_id)

        session_data_decoded = codecs.decode(session_data_raw, "base64")
        session_data = json.loads(session_data_decoded)

        self.statsd.get_counter("retrieve").increment(
            "redis.get_session.count"
        )
        self.logger.info(f"Session '{session_id}' retrieved")

        return session_data


def redis_from_config(config: dict) -> StrictRedis:
    """Create a Redis cleint from variables in the config parameter.

    :param config: config variables
    :type config: dict
    :return: configured redis client
    :rtype: StrictRedis
    """
    redis_conf = config["redis"]["session"]

    redis = StrictRedis(**redis_conf)
    return redis


def session_manager_factory(infra_factory):
    """Create a configured SessionRetriever class.

    :param infra_factory: infrastructure factory class
    :type infra_factory: InfrastructureFactory
    :return: configured SessionRetriever class to retrieve session information
        from session store
    :rtype: SessionRetriever
    """
    infra_factory.register_infrastructure(
        name="redis", infrastructure=redis_from_config
    )
    redis = infra_factory.get_infrastructure(
        context=None, infrastructure_name="redis"
    )
    return SessionRetriever(redis)


UserInfo = namedtuple("UserInfo", "user_uuid permissions")


def protected_route(view):
    """Check session and inject `UserInfo` in wrapped view .

    zaaksysteem_session cookie is checked for validity and `UserInfo` is
    injected in the view.

    :param view: view function
    :type view: pyramid view
    :raises HTTPUnauthorized: session not valid or non-existant
    :return: view with `UserInfo` injected
    :rtype: wrapped view
    """

    def view_wrapper(request):
        logger = logging.getLogger(view.__name__)

        try:
            session_id = request.cookies["zaaksysteem_session"]
        except KeyError:
            logger.info(f"Unauthorized: no zaaksysteem_session cookie")
            raise HTTPUnauthorized(
                content_type="application/json",
                json_body={"error": "Unauthorized"},
            )
        try:
            session_info = request.retrieve_session(session_id=session_id)
        except SessionRetrieverError as e:
            logger.info(f"Invalid session: {e}")
            raise HTTPUnauthorized(
                content_type="application/json",
                json_body={"error": "Unauthorized"},
            )
        try:
            user_info_decoded = json.loads(session_info["__user"])
            user_info = UserInfo(
                user_uuid=user_info_decoded["subject_uuid"],
                permissions=user_info_decoded["permissions"],
            )
        except KeyError as e:
            logger.info(f"Unauthorized: error in session data: '{e}'")
            raise HTTPUnauthorized(
                content_type="application/json",
                json_body={"error": "Unauthorized"},
            )
        except TypeError as e:
            logger.info(f"Unauthorized: error in session data: '{e}'")
            raise HTTPUnauthorized(
                content_type="application/json",
                json_body={"error": "Unauthorized"},
            )

        return view(request=request, user_info=user_info)

    return view_wrapper
