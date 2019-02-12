import io
import itertools

import requests
from requests.auth import HTTPBasicAuth

from ._types import Product


class ShopifyClient:

    def __init__(self, *, store_name, api_key, password):
        self.store_name = store_name
        self.api_key = api_key
        self.password = password

    def _make_base_url(self):
        return 'https://{}.myshopify.com/'.format(self.store_name)

    def _make_url(self, path):
        return '{}{}'.format(self._make_base_url(), path)

    def _make_auth(self):
        return HTTPBasicAuth(self.api_key, self.password)

    def request(self, method, path, *args, **kwargs):
        url = self._make_url(path)
        kwargs.setdefault('auth', self._make_auth())
        resp = requests.request(method, url, *args, **kwargs)
        if not resp.ok:
            raise http_error_exception(resp)
        return resp

    def __repr__(self):
        return (
            "ShopifyClient(store_name={}, api_key={})"
            .format(repr(self.store_name), repr(self.api_key)))

    # ================================================================
    # Products API
    # ================================================================

    def get_product_by_id(self, product_id):
        resp = self.request('GET', 'admin/products/{}.json'.format(product_id))
        return resp.json()

    def get_product_by_handle(self, handle):
        products = self.list_all_products({'handle': handle})
        for prod in products:
            return prod
        return None

    def list_all_products(self, filters={}):
        for page in itertools.count(1):
            resp = self.request(
                'GET', 'admin/products.json',
                params={
                    'limit': '250',
                    'page': str(page),
                    **filters,
                })

            products = resp.json()['products']
            if not len(products):
                break  # We reached an end

            for product in products:
                yield Product.from_response(product)

    def create_product(self, product):
        resp = self.request(
            'POST', 'admin/products.json',
            json={'product': product})
        return Product.from_response(resp.json())

    def update_product(self, product_id, updates):

        if 'metafields' in updates:
            # FIXME: need to pass the metafield ID to update
            del updates['metafields']

        resp = self.request(
            'PUT', 'admin/products/{}.json'.format(product_id),
            json={'product': updates})

        return resp.json()

    def delete_product(self, product_id):
        self.request(
            'DELETE', 'admin/products/{}.json'.format(product_id))


class HttpError(Exception):
    pass


def http_error_exception(resp):
    # TODO: exception should be formatted at print time
    # term_width = click.get_terminal_size()[0]
    term_width = 80
    assert not resp.ok
    msg = io.StringIO()

    msg.write(' Request '.center(term_width, '-') + '\n')
    msg.write('{} {}\n'.format(resp.request.method, resp.request.url))
    for key, val in resp.request.headers.items():
        msg.write('{}: {}\n'.format(key, val))
    if resp.request.body:
        msg.write('\n')
        msg.write(format(resp.request.body))
    msg.write('\n\n')

    msg.write(' Response '.center(term_width, '-') + '\n')
    msg.write('{} {}\n'.format(resp.status_code, resp.reason))
    for key, val in resp.request.headers.items():
        msg.write('{}: {}\n'.format(key, val))
    if resp.text:
        msg.write('\n')
        msg.write(resp.text)  # Or resp.content ?
    msg.write('\n')

    msg.write('-' * term_width + '\n')

    return HttpError(msg.getvalue())
