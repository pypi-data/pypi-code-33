import logging

import requests
from six.moves.urllib.parse import urlparse

from .. import _collector


logger = logging.getLogger(__name__)


def send_rabbitmq_queue_stats(broker_url, queue_names):
    queue_names = set(queue_names)
    parsed = urlparse(broker_url)

    url = "https://{}/api/queues".format(parsed.hostname)
    username = parsed.username or "guest"
    password = parsed.password or "guest"

    try:
        response = requests.get(url, auth=(username, password), timeout=0.1)
    except requests.exceptions.RequestException:
        # We set a very aggressive timeout on the request so that we do not
        # block our worker for very long. It's expected that this will
        # sometimes fail, but it's unlikely to matter since we should be
        # collecting queue stats frequently. As such, we log but otherwise
        # swallow the exception (so we do not Rollbar or emit generic error
        # metrics)
        logger.info("Error requesting metrics from RabbitMQ, skipping")
        _collector.increment("rabbitmq.stats.timeout", value=1)
        return

    response.raise_for_status()

    payload = response.json()

    for queue in payload:
        if queue["name"] in queue_names:
            _collector.gauge(
                "queue.messages.ready",
                value=queue.get("messages_ready", 0),
                tags={"queue": queue["name"]},
            )

            _collector.gauge(
                "queue.messages.unacked",
                value=queue.get("messages_unacknowledged", 0),
                tags={"queue": queue["name"]},
            )
