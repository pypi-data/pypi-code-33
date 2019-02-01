# encoding=utf8
# author=spenly
# mail=i@spenly.com

from redis import StrictRedis
import re
import random
from urllib.parse import urlparse
from urllib.request import urlopen
import os

NETWORK_META_DATA_URL_ENV_KEY = "NETWORK_META_DATA_URL"


def parse_redis_url(url):
    """
    Parse a redis URL.
    :param url: redis://host:port[,host2:port2,...][/service_name[/db]][?socket_timeout=0.1]
    :return: redis kwargs
    """
    url = urlparse(url)
    if url.scheme != 'redis':
        raise ValueError('Unsupported scheme: {}'.format(url.scheme))

    def parse_host(s):
        if ':' in s:
            host, port = s.split(':', 1)
            port = int(port)
        else:
            host = s
            port = 6379
        return host, port

    if '@' in url.netloc:
        auth, hostspec = url.netloc.split('@', 1)
    else:
        auth = None
        hostspec = url.netloc
    if auth and ':' in auth:
        _, password = auth.split(':', 1)
    else:
        password = None
    host, port = parse_host(hostspec)
    db = int("0" + re.sub("\D", "", url.path))
    kwargs = {"host": host, "port": port, "password": password, "db": db}
    return kwargs


def get_host_ip():
    # get host ip from API
    # default aws mate data API
    aws_meta_data_url = "http://169.254.169.254/latest/meta-data/local-ipv4"
    network_meta_data_url = os.getenv(NETWORK_META_DATA_URL_ENV_KEY) or aws_meta_data_url
    try:
        host_ip = urlopen(network_meta_data_url, timeout=5).read()
        host_ip = host_ip.decode("utf8", errors="ignore").strip()
    except Exception as ex:
        ex_msg = "get aws EC2 instance IP failed:\n" + str(ex)
        raise BaseException(ex_msg)
    return host_ip


class AutoDiscovery(object):

    def __init__(self, redis_prefix="", serving_port=8500, register_mode=False, **kwargs):
        self._redis = StrictRedis(**kwargs)
        self.register_mode = register_mode
        if self.register_mode:
            _host_ip = get_host_ip()
            # e.g. 192_168_42_70
            self._register_ip = _host_ip.replace(".", "_")
            self.hostport = "%s:%d" % (_host_ip, serving_port)
        self._redis_prefix = redis_prefix
        self._max_retry_limit = 3

    def _build_model_name_ver(self, model_name, version=None):
        if version:
            return "%s_%s@%d" % (self._redis_prefix, model_name, version)
        else:
            return "%s_%s" % (self._redis_prefix, model_name)

    def register(self, model_name, version, hostport=None, timeout=10):
        """
        register a TF serving info
        :param model_name: model name
        :param version: model version
        :param hostport: GPU instance hostport value, e.g. "192.168.42.70:8500"
        :param timeout: expire time
        :return:
        """
        if not self.register_mode:
            raise BaseException("Register action is not allowed, cause register_mode is False.")
        version = int(version)
        model_name_ver = self._build_model_name_ver(model_name, version)
        key = "%s:%s" % (model_name_ver, self._register_ip)
        hostport = hostport or self.hostport
        ex_msg = None
        for retry in range(self._max_retry_limit):
            try:
                self._redis.set(key, value=hostport, ex=timeout)
                break
            except Exception as ex:
                # if retries reached to the max
                if retry == (self._max_retry_limit - 1):
                    ex_msg = str(ex)
        if ex_msg:
            ex_msg = "AutoDiscovery register retries reach to limit[%d]:\n %s" % (
                self._max_retry_limit, ex_msg)
            raise BaseException(ex_msg)

    def get_host_port(self, model_name, version=None):
        """
        get a TF serving host info
        :param model_name:
        :param version: int or str
        :return:
        """
        if not version:
            model_name_prefix = self._build_model_name_ver(model_name)
            start_index = len(model_name_prefix) + 1
            latest_ver = -1
            # find the latest version
            for item in self._redis.keys("%s*" % model_name_prefix):
                # model_name@ver:ip, e.g.: language_detection@1:10.112.3.54
                item = isinstance(item, bytes) and item.decode("utf8") or item
                end_index = item.index(":")
                cur_ver = int(item[start_index:end_index])
                latest_ver = (cur_ver > latest_ver) and cur_ver or latest_ver
            # version validation
            if latest_ver < 0:
                raise Exception("No available serving versions for model %s" % model_name)
            else:
                version = latest_ver
        version = int(version)
        model_name_ver = self._build_model_name_ver(model_name, version)
        keys = self._redis.keys("%s*" % model_name_ver)
        # value validation, empty value will raise a exception
        if not keys:
            raise Exception("Serving host for %s@%s not exists" % (model_name, version))
        key = random.choice(keys)
        val = self._redis.get(key)
        if isinstance(val, bytes):
            val = val.decode("utf8")
        return val


if __name__ == "__main__":
    # get redis url from param or ENV
    args = parse_redis_url("redis://192.168.44.130")
    # test register error, any one host without redis
    # args = parse_redis_url("redis://192.168.44.131")
    args["register_mode"] = True
    ad = AutoDiscovery(**args)
    print("\nregister: test@1=hostport_for_test")
    ad.register("test", "1", "hostport_for_test")
    print("\nget hostport for model test@latest")
    print("value => " + ad.get_host_port("test", None))

    print("\nget host port for model test@1")
    print("value => " + ad.get_host_port("test", version=1))

    print("\nregister: abc@2=hostport_for_abc")
    ad.register("abc", 2, "hostport_for_abc@2")

    print("\nget hostport for model abc@latest")
    print("value => " + ad.get_host_port("abc"))

    print("\nget host port for model test@2 will occur a exception:")
    print("value => " + ad.get_host_port("test", version=2))
