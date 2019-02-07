import os

from celery import Celery
from kombu import Queue
from mbq import ranch

from . import launch_darkly


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
celery_app = Celery(
    "ranch_test", task_cls=ranch.killswitch.create_task_class(launch_darkly.variation)
)

celery_app.conf.update(
    broker_url="amqp://rabbitmq",
    task_default_exchange="default",
    task_default_queue="default",
    task_default_routing_key="default",
    task_soft_time_limit=600,  # raises SoftTimeLimitExceeded after 10 min
    timezone="America/New_York",
    worker_hijack_root_logger=False,
    task_queues=(Queue("default"),),
)

celery_app.autodiscover_tasks()
