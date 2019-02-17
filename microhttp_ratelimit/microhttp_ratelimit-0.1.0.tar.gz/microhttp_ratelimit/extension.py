import functools

from redis import StrictRedis

from nanohttp import settings, context

from microhttp import bus
from microhttp_ratelimit import RedisLeakyBucketRateLimit, HTTPTooManyRequests


delete_multiple_keys_script = '''
local keys = redis.call('keys', ARGV[1])
for i=1,#keys,5000 do
    redis.call('del', unpack(keys, i, math.min(i+4999, #keys)))
end
return keys
'''


def create_redis_connection():
    return StrictRedis(
        **dict(settings.rate_limit.redis),
        decode_responses=True
    )


def configure():
    redis_connection = create_redis_connection()
    delete_script = redis_connection.register_script(
        delete_multiple_keys_script
    )
    bus.ext.rate_limit.redis_connection = redis_connection
    bus.ext.rate_limit.delete_script = delete_script


def get_redis_connection():
    return bus.ext.rate_limit.redis_connection


def _initiate_ip_rate_limiter(rule):
    config = settings.rate_limit
    ip = context.environ['REMOTE_ADDR']
    period = config.ip_rules[rule]['period']
    limit = config.ip_rules[rule]['limit']
    return RedisLeakyBucketRateLimit(
        redis_connection=get_redis_connection(),
        namespace='%s:ip:%s' % (
            config.namespace_prefix,
            ip
        ),
        period=period,
        limit=limit
    )


def reset_ip_throttler(ip=None):
    prefix = settings.rate_limit.namespace_prefix
    key = (
        '%s:ip:%s' % (prefix, ip)
        if ip else
        '%s:ip:*' % prefix
    )
    delete_script = bus.ext.rate_limit.delete_script
    delete_script(args=(key,))


def ip_throttle(*args_, rule: str=None):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            rule_ = rule
            if len(args_) == 1 and isinstance(args_[0], str):
                rule_ = args_[0]
            elif rule_ is None:
                rule_ = 'default'

            rate_limiter = _initiate_ip_rate_limiter(rule_)
            if not rate_limiter.attempt():
                raise HTTPTooManyRequests(
                    wait_time=rate_limiter.get_attempt_expiration_time()
                )

            return func(*args, **kwargs)

        return wrapper

    if args_ and callable(args_[0]):
        f = args_[0]
        return decorator(f)

    return decorator
