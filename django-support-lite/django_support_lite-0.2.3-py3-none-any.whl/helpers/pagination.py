import math
from functools import partial
from urllib.parse import urlencode

from django.urls import reverse


class InvalidPageError(Exception):
    pass

class Pagination:
    def __init__(self, count, page, per_page, name, path_params={}, query_params={}, fragment=None):
        if page < 1:
            raise InvalidPageError()

        pages_count = math.ceil(count / per_page)

        if pages_count == 0:
            pages_count = 1

        if page > pages_count:
            raise InvalidPageError()

        url = partial(_url, name, path_params, query_params, fragment)

        self.links = []

        if 3 < page:
            # 1
            self.links.append(
                (1, url(1), 1 == page)
            )

            # ...
            if 4 < page:
                self.links.append(
                    (False, '', False)
                )

        for i in range(1, pages_count + 1):
            if page - 3 < i < page + 3:
                self.links.append(
                    (i, url(i), i == page)
                )

        if page < pages_count - 2:
            # ...
            if page < pages_count - 3:
                self.links.append(
                    (False, '', False)
                )

            # count
            self.links.append(
                (pages_count, url(pages_count), pages_count == page)
            )

        self.iter = None
        self.slice = slice(
            (page - 1) * per_page,
            page * per_page
        )

    def __iter__(self):
        self.iter = iter(self.links)
        return self

    def __next__(self):
        return next(self.iter)

# private

def _url(name, path_params, query_params, fragment, page):
    path_params['page'] = page
    return '{}{}{}'.format(
        reverse(name, kwargs=path_params),
        '?{}'.format(urlencode(query_params)) if query_params else '',
        '#{}'.format(fragment) if fragment else ''
    )
