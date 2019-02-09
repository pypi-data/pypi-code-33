import redis
import pickle
import time
import inspect
import base64
import hashlib


debug = True


def log(s):
    if debug:
        print(s)


def get_from_cache(url, key):
    r = redis.Redis.from_url(url=url)

    try:
        v = r.get(key)
    except redis.exceptions.ConnectionError:
        log("Unable to connect to Redis.")
        return

    log(key)
    if v:
        return pickle.loads(v)


def write_to_cache(url, fname, obj):
    r = redis.Redis.from_url(url=url)
    try:
        return r.set(fname, pickle.dumps(obj))
    except redis.exceptions.ConnectionError:
        log("Unable to connect to Redis.")
        return


def get_fn_hash(f):
    return base64.b64encode(hashlib.sha1(inspect.getsource(f).encode("utf-8")).digest())


NONE = 0
ARGS = 1
KWARGS = 2


def rcache(url="redis://localhost:6379", timeout=-1, key=ARGS | KWARGS):
    def impl(fn):
        def d(*args, **kwargs):
            log("checking cache on {}".format(fn.__name__))
            if key == ARGS | KWARGS:
                k = pickle.dumps((fn.__name__, args, kwargs))
            if key == ARGS:
                k = pickle.dumps((fn.__name__, args))
            if key == KWARGS:
                k = pickle.dumps((fn.__name__, kwargs))
            if key == NONE:
                k = pickle.dumps((fn.__name__))

            cached = get_from_cache(url, k)
            if cached:
                h, t, to, res = cached
                if get_fn_hash(fn) == h and (to < 0 or (time.time() - t) < to):
                    log("cache hit.")
                    return res

            log("cache miss.")
            res = fn(*args, **kwargs)
            c = (get_fn_hash(fn), time.time(), timeout, res)
            save_t = time.time()
            write_to_cache(url, k, c)
            log("saved cache in {:.2f}s".format(time.time() - save_t))
            return res

        return d

    return impl


if __name__ == "__main__":

    import os
    test_redis_url = os.getenv('TEST_REDIS_URL', 'redis://redis:6379')

    print('Test REDIS url: ', test_redis_url)

    @rcache(url=test_redis_url, timeout=0.2)
    def expensive(k):
        time.sleep(0.2)
        return k

    @rcache(url=test_redis_url, key=KWARGS)
    def expensive2(k, kwarg1=None):
        time.sleep(0.2)
        return k

    def test():
        # Test timeout
        t = time.time()
        v = expensive(1)
        assert v == 1
        assert time.time() - t > 0.1
        t = time.time()
        expensive(1)
        assert time.time() - t < 0.1
        time.sleep(0.3)
        t = time.time()
        expensive(1)
        assert time.time() - t > 0.1
        t = time.time()
        v = expensive(2)
        assert v == 2
        assert time.time() - t > 0.1

        # Test key=_ annotation
        t = time.time()
        v = expensive2(2, kwarg1="test")
        assert v == 2
        assert time.time() - t > 0.1
        t = time.time()
        v = expensive2(1, kwarg1="test")
        assert v == 2
        assert time.time() - t < 0.1
        t = time.time()
        v = expensive2(1, kwarg1="test2")
        assert v == 1
        assert time.time() - t > 0.1
        print("pass")

    test()
