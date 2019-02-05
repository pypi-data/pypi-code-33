from celery import shared_task

from .task_resources import common
from .task_resources import tunnel_credit
from .task_resources import tunnel_subscription


@shared_task
def tunnel_refresh_subscription():
    tunnel_subscription.monitor_woosub1_renewals()


@shared_task
def tunnel_new_subscription():
    tunnel_subscription.monitor_woosub1_new_subscriptions()


@shared_task
def tunnel_new_credit():
    tunnel_credit.monitor_woo1()


@shared_task
def deactivate_all_expired_limits():
    common.deactivate_all_expired_limits()


@shared_task
def debug_connection_task():
    common.debug_connection_task()
