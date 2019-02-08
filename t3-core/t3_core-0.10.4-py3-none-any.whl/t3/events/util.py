import os
import logging
from t3.env import load_env

# Env vars
# Get env dictionary. This feeds from env, .env, and then vcap services
# For local dev, move .env.dist to .env and play with settings
# In CI, a service.yaml is likely to be used
BASE_DIR = os.getcwd()
_env = load_env(dot_env_path=BASE_DIR)


# ##########################################################################
# Event system configs & debug
#   DEBUG=true               - to set true or false to turn on/off debug logs
#   T3_EVENTS=false          - to set true or false to turn on/off events
#   T3_EVENTS_AMQP_URL       - rabbit mq amqp url string to connect to
# ##########################################################################

T3_EVENTS = True if str(os.getenv('T3_EVENTS', 'false')).lower() == 'true' else False
DEBUG = True if str(os.getenv('DEBUG', 'false')).lower() == 'true' else False

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


def get_rabbit_mq_conn():
    if T3_EVENTS:
        return os.getenv('T3_EVENTS_AMQP_URL', 'amqp://rabbitmq:rabbitmq@localhost:5672/')
    else:
        raise Exception('T3 Events Disabled')


# Utility functions
def get_task_name(task_name):
    return f'task-{task_name}'


def get_topic_name(topic_name):
    return f'topic-{topic_name}'
