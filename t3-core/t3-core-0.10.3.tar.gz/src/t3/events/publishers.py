import signal
from t3.events.base_publisher import BasePublisher
from t3.events.util import get_task_name, get_topic_name, get_rabbit_mq_conn


class TaskPublisher(BasePublisher):
    """
    TaskPublisher is used for tasks, first consumer subscribed to the same queue_name.

    Messages are distributed in round robin fashion
    Any system can send a task to be consumed by the first available worker
    """

    def __init__(self):
        amqp_url = get_rabbit_mq_conn()
        BasePublisher.__init__(self, amqp_url)
        self.set_exchange('task_exchange')
        signal.signal(signal.SIGINT, lambda signum, frame: self.stop())
        signal.signal(signal.SIGTERM, lambda signum, frame: self.stop())

    def set_task_name(self, task_name):
        name = get_task_name(task_name)
        self.set_routing_key(name)


class TopicPublisher(BasePublisher):
    """
    TopicPublisher is used for topics, all consumers subscribed to the routing_key gets the message.

    Messages are delivered at the same time.
    Any system can send a topic to be consumed by the subscribed workers
    """

    def __init__(self):
        amqp_url = get_rabbit_mq_conn()
        BasePublisher.__init__(self, amqp_url)
        self.set_exchange('topic_exchange')
        signal.signal(signal.SIGINT, lambda signum, frame: self.stop())
        signal.signal(signal.SIGTERM, lambda signum, frame: self.stop())

    def set_topic_name(self, topic_name):
        name = get_topic_name(topic_name)
        self.set_routing_key(name)
