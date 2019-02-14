import os
import ujson
import redis

redis_tests = None


def setup_redis_tests(**redis_kwargs):
    global redis_tests
    redis_tests = redis.Redis(**redis_kwargs)


def save_test_result(data):
    global redis_tests
    redis_tests.set("test_result",
                    ujson.dumps(data),
                    ex=30)


def get_test_result():
    return redis_tests.get("test_result")


def get_test_data_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "test_data")