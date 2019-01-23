import json
import re
from collections import OrderedDict

from functools import wraps

from longitude.validators import min_value, combine_validations, max_value
from longitude.config import PAGINATION_PAGE_SIZE, PAGINATION_MAX_PAGE_SIZE
from longitude.schemas import Schema
from longitude.utils import create_result_csv_streamer
from longitude.response import json as json_response
from marshmallow import post_load
from marshmallow import fields as sch_fields
from sanic.response import BaseHTTPResponse, stream


class ListEPFilterSchema(Schema):

    meta = sch_fields.Boolean(required=True, missing=True)
    results = sch_fields.Boolean(required=True, missing=True)
    page = sch_fields.Integer(required=True, missing=1, validate=min_value(1))
    page_of = sch_fields.Integer(required=True, missing=None, validate=min_value(1))

    if PAGINATION_MAX_PAGE_SIZE is not None:
        page_size = sch_fields.Integer(
            required=False,
            default=PAGINATION_PAGE_SIZE,
            validate=combine_validations(
                max_value(PAGINATION_MAX_PAGE_SIZE + 1),
                max_value(10000 + 1),
                min_value(1)
            )
        )

    @post_load
    def add_pagination(self, out_data):

        if PAGINATION_MAX_PAGE_SIZE is None:
            out_data['page_size'] = PAGINATION_PAGE_SIZE

        return out_data


def paginated(fn):
    """
    Parses pagination params from the user request and adds them to request.args.

    Also, truncates the response body if the content_type is json, and the user
    provided meta=0 or results=0 to request.args
    """

    @wraps(fn)
    async def paginated_fn(request, *args, **kwargs):

        pagination, pagination_errors = ListEPFilterSchema().load(request.args)

        if pagination_errors:
            return json_response(pagination_errors, 400)

        request.args['pagination'] = [pagination]

        for pagination_param in request.args.get('pagination').keys():
            request.args.pop(pagination_param, None)

        request.args['meta'] = [request.args.get('pagination').pop('meta')]
        request.args['results'] = [request.args.get('pagination').pop('results')]

        res = await fn(request, *args, **kwargs)

        # We expect the user to take into account request.meta and request.results
        # However, if the user does not treat them and the payload includes results
        # /meta when they should, let's try to remove it and at least get rid
        # of the transports costs
        is_json_response = isinstance(res, BaseHTTPResponse) and \
                           res.body \
                           and res.content_type == 'application/json' \
                           and (
                                   (not request.args.get('meta') and b'"meta"' in res.body) or
                                   (not request.args.get('results') and b'"results"' in res.body)
                           )

        if is_json_response:
            body = json.loads(res.body)
        else:
            body = res

        if isinstance(body, dict):
            if not request.args.get('meta'):
                body.pop('meta', None)

            if not request.args.get('results'):
                body.pop('results', None)

        if is_json_response:
            res.body = json.dumps(body).encode()

        return res

    return paginated_fn


def supports_csv_download(CSV_STRUCTURE):
    """
    For an endpoint returning a {"results:[]} json/dict response, allows
    the user to provide content-type='text/csv' to download the filtered
    set as CSV, deactivating pagination rules.
    """
    def configure_csv_download_fn(fn):

        csv_structure = OrderedDict(
            (re.compile(x), y)
            for x, y
            in CSV_STRUCTURE.items()
        )

        @wraps(fn)
        async def supports_csv_download_fn(request, *args, **kwargs):

            if request.headers.get('accept', '').split(';')[0] == 'text/csv':
                request['page_size'] = ['-1']
                request['page'] = ['0']
                request['meta'] = ['0']
                request['results'] = ['1']

            res = await fn(request, *args, **kwargs)

            if request.headers['accept'] == 'text/csv':
                return stream(
                    create_result_csv_streamer(
                        csv_structure,
                        res['results']
                    ),
                    content_type='text/csv'
                )
            else:
                return res

        return supports_csv_download_fn

    return configure_csv_download_fn


def maybe_wrap_result_in_response(response_constructor):
    """
    Decorator to add to a route callback, wraps the route callback response
    by calling the provided function if the returned value is not an HTTPResponse.
    """
    def maybe_wrap_result_in_response_args(fn):

        @wraps(fn)
        async def maybe_wrap_result_in_response_fn(request, *args, **kwargs):
            res = await fn(request, *args, **kwargs)

            if not isinstance(res, BaseHTTPResponse):
                res = response_constructor(res)

            return res

        return maybe_wrap_result_in_response_fn

    return maybe_wrap_result_in_response_args


