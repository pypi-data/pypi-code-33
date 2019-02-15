'''Methods to connect N-Tier to aiohttp'''
from http import (HTTPStatus)
from typing import (Any, Callable, Mapping, Optional, Sequence, TypeVar, Union)
from aiohttp.web import (Request, Response, json_response)
from multidict import (MultiDict)
import ntier as N
import ujson
from webdi import (Container)
from .base_classes import (APITransactionBase)

PAGE_DEFAULT = 1
PER_PAGE_DEFAULT = 25
PAGE_KEY = 'page'
PER_PAGE_KEY = 'per_page'
TOTAL_RECORDS_KEY = 'total_records'
TOTAL_PAGES_KEY = 'total_pages'
PAGING_KEY = 'paging'
DATA_KEY = 'data'
ERRORS_KEY = 'errors'
TRANSACTION_CODE_MAP = {
    N.TransactionCode.success: HTTPStatus.OK,
    N.TransactionCode.found: HTTPStatus.OK,
    N.TransactionCode.created: HTTPStatus.CREATED,
    N.TransactionCode.updated: HTTPStatus.OK,
    N.TransactionCode.not_changed: HTTPStatus.OK,
    N.TransactionCode.deleted: HTTPStatus.OK,
    N.TransactionCode.failed: HTTPStatus.BAD_REQUEST,
    N.TransactionCode.not_found: HTTPStatus.NOT_FOUND,
    N.TransactionCode.not_authenticated: HTTPStatus.UNAUTHORIZED,
    N.TransactionCode.not_authorized: HTTPStatus.FORBIDDEN,
    N.TransactionCode.not_valid: HTTPStatus.UNPROCESSABLE_ENTITY,
}
Data = Mapping[str, Any]
T = TypeVar('T')

def set_paging(transaction: N.TransactionBase, data: Data) -> None:
  '''Sets paging on a transaction class based on query string args.'''
  page_str: Optional[str] = data.get(PAGE_KEY)
  per_page_str: Optional[str] = data.get(PER_PAGE_KEY)
  page: Optional[int] = None
  per_page: Optional[int] = None

  if page_str:
    try:
      page = int(page_str)
    except ValueError:
      page = PAGE_DEFAULT
  if per_page_str:
    try:
      per_page = int(per_page_str)
    except ValueError:
      per_page = PER_PAGE_DEFAULT

  if not (page or per_page):
    return

  if not page or page < 0:
    page = PAGE_DEFAULT
  if not per_page or per_page < 0:
    per_page = PER_PAGE_DEFAULT

  transaction.set_paging(page, per_page)

def map_transaction_code(code: N.TransactionCode) -> HTTPStatus:
  '''Map a TransactionCode to an HTTPStatus code.'''
  status_code = TRANSACTION_CODE_MAP.get(code)
  if status_code is None:
    raise Exception(f'Unrecognized transaction code: {code}')
  return status_code

async def build_transaction_data(request: Request) -> MultiDict:
  '''Build a dict from a Request object.'''
  data = MultiDict(request.query)
  data.extend(request.match_info)
  if request.can_read_body:
    body = await request.json()
    data.extend(body)
  return data

async def execute_transaction(
    transaction_name: str,
    serializer: Callable[[Any], Any],
    container: Container,
    request: Request,
) -> Response:
  '''Call a transaction with data from a request and build a JSON response.'''
  data = await build_transaction_data(request)
  transaction: APITransactionBase = container.get(transaction_name)
  set_paging(transaction, data)
  result = await transaction(data)
  http_status = map_transaction_code(result.status_code)

  if http_status < HTTPStatus.BAD_REQUEST:
    result_data = {DATA_KEY: serializer(result.payload)}
    if result.has_paging:
      result_data[PAGING_KEY] = {
          PAGE_KEY: result.paging.page,
          PER_PAGE_KEY: result.paging.per_page,
          TOTAL_RECORDS_KEY: result.paging.total_records,
          TOTAL_PAGES_KEY: result.paging.total_pages,
      }
    return json_response(result_data, status=http_status, dumps=ujson.dumps)

  result_data = {ERRORS_KEY: result.payload}
  return json_response(result_data, status=http_status, dumps=ujson.dumps)
