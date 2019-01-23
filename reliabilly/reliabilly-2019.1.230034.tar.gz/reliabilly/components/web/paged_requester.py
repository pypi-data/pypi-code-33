from reliabilly.settings import get_service_url
from reliabilly.components.web.http_requestor import HttpRequestor


class PagedRequester(HttpRequestor):
    def __init__(self, service_name, **kwargs):
        super().__init__(**kwargs)
        self.service_name = service_name
        self.current_offset = 0
        self.total = None

    def has_next(self):
        if self.total is not None:
            return self.current_offset < self.total
        return None

    def get_next_page(self):
        results = list()
        headers = self.get_request_headers()
        result = self._call_endpoint(get_service_url(self.service_name), self.current_offset, headers=headers)
        self.current_offset += result['limit']
        if self.total is None:
            self.total = result['total']
        return results

    def get_all(self):
        results = list()
        results += self.get_next_page()
        while self.has_next():
            results += self.get_next_page()
        return results
