from urllib.parse import urlencode, urlsplit, parse_qs, urlunsplit
from tornado.httpclient import HTTPRequest


def make_list(val):
    if isinstance(val, list):
        return val
    else:
        return [val]


def real_ip(request):
    return (request.headers.get('X-Real-Ip', None) or request.headers.get('X-Forwarded-For', None) or
            request.remote_ip or '127.0.0.1')


ITERABLE = (set, frozenset, list, tuple)


def update_url(url, update_args=None, remove_args=None):
    scheme, sep, url_new = url.partition('://')
    if len(scheme) == len(url):
        scheme = ''
    else:
        url = '//' + url_new

    url_split = urlsplit(url)
    query_dict = parse_qs(url_split.query, keep_blank_values=True)

    # add args
    if update_args:
        query_dict.update(update_args)

    # remove args
    if remove_args:
        query_dict = dict([(k, query_dict.get(k)) for k in query_dict if k not in remove_args])

    query = make_qs(query_dict)
    return urlunsplit((scheme, url_split.netloc, url_split.path, query, url_split.fragment))


def make_qs(query_args):
    def _encode(s):
        if isinstance(s, str):
            return s.encode('utf-8')
        else:
            return s

    kv_pairs = []
    for key, val in query_args.items():
        if val is not None:
            encoded_key = _encode(key)
            if isinstance(val, ITERABLE):
                for v in val:
                    kv_pairs.append((encoded_key, _encode(v)))
            else:
                kv_pairs.append((encoded_key, _encode(val)))

    qs = urlencode(kv_pairs, doseq=True)

    return qs


class HTTPTortRequest(object):
    def __init__(self, name: str, retry_count: int = None, is_retry: bool = False, **request_params) -> None:
        self.name = name
        self.request = HTTPRequest(**request_params)
        self.retry_count = retry_count or 0
        self.is_retry = is_retry

        self._initial_params = request_params

    def retry(self) -> 'HTTPTortRequest':
        return HTTPTortRequest(self.name, self.retry_count - 1, True, **self._initial_params)
