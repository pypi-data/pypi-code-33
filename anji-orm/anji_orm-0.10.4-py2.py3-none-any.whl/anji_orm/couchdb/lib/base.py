# pylint: disable=access-member-before-definition
from abc import ABC, abstractmethod
from typing import Dict, Generator, Any, Optional, List, Callable, Tuple, Union, Iterator

from ...core import QueryBuildException
from ..utils import DDOC_FOR_GENERATED_VIEWS_NAME
from .design import DesignDocFilter, DesignDocView, DesignDocUpdate
from .function import CouchDBFilterMapFunction, CouchDBFilterFunction, CouchDBUpdateFunction

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.4"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = [
    'AbstractCouchDBQuery', 'CouchDBMangoQuery',
    'CouchDBDesignDocViewQuery', "CouchDBDesignDocFilterQuery",
    "DummyCouchDBQuery", 'CouchDBDesignDocUpdateQuery'
]

GenResp = Union[Dict, Iterator[Dict]]  # pylint: disable=invalid-name
GenAccept = Union[Dict, List]  # pylint: disable=invalid-name


class AbstractCouchDBQuery(ABC):  # pylint: disable=too-many-instance-attributes

    design_doc_usage = False

    __slots__ = (
        'sort', 'limit', 'skip', 'table_name',
        'params', 'query_identity', 'grab_connection',
        'url', 'method', 'post_processors', 'pre_processors'
    )

    def __init__(self, query_identity: str = '') -> None:
        self.query_identity = query_identity
        self.method = 'post'
        self.table_name: Optional[str] = None
        self.sort: Optional[List] = None
        self.limit: Optional[Tuple] = None
        self.skip: Optional[Tuple] = None
        self.params: Optional[Dict[str, Any]] = None
        self.url: Optional[str] = None
        self.grab_connection: bool = False
        self.post_processors: Optional[List[Callable]] = None
        self.pre_processors: Optional[List[Callable]] = None

    def _prepare_base_dict(self) -> Dict:
        base_dict: Dict[str, Any] = {
            'url': f"{self.table_name}/{self.url}",
            'method': self.method,
            'grab_connection': self.grab_connection
        }
        if self.params is not None:
            base_dict['params'] = self.params
        if self.method != 'get':
            # Note, that json in GET query
            # cause timeouts and stuck problems!
            base_dict['json'] = {}
            for attr in ('sort', 'limit', 'skip'):
                if getattr(self, attr) is not None:
                    base_dict['json'][attr] = getattr(self, attr)
        return base_dict

    @abstractmethod
    def start(self) -> Generator[GenResp, GenAccept, GenAccept]:
        pass

    def __eq__(self, other) -> bool:
        if not isinstance(other, AbstractCouchDBQuery):
            return False
        for attr in AbstractCouchDBQuery.__slots__:
            if attr in ('pre_processors', 'post_processors'):
                first_array = getattr(self, attr, None)
                second_array = getattr(other, attr, None)
                check = (
                    (first_array is None and second_array is None) or
                    (
                        (first_array is not None and second_array is not None) and
                        len(first_array) == len(second_array)
                    )
                )
                if not check:
                    return False
            elif getattr(self, attr, None) != getattr(other, attr, None):
                return False
        return True

    @abstractmethod
    def to_ddoc_view(self) -> 'CouchDBDesignDocViewQuery':
        pass

    @abstractmethod
    def to_ddoc_filter(self) -> 'CouchDBDesignDocFilterQuery':
        pass

    @abstractmethod
    def to_ddoc_update(self) -> 'CouchDBDesignDocUpdateQuery':
        pass

    @abstractmethod
    def to_mango_query(self) -> 'CouchDBMangoQuery':
        pass

    def _load_magic(self, other: 'AbstractCouchDBQuery') -> None:
        for attr in AbstractCouchDBQuery.__slots__:
            attr_value = getattr(other, attr, None)
            if attr_value is not None and getattr(self, attr, None) is None:
                setattr(self, attr, attr_value)

    def __str__(self) -> str:
        args = (f'{key}={getattr(self, key, None)}' for key in AbstractCouchDBQuery.__slots__)
        return f"[{', '.join(args)}]"

    def __repr__(self) -> str:
        return self.__str__()


class DummyCouchDBQuery(AbstractCouchDBQuery):

    def start(self) -> Generator[GenResp, GenAccept, GenAccept]:
        raise NotImplementedError("Dummy Query cannot be runned")

    def to_ddoc_view(self) -> 'CouchDBDesignDocViewQuery':
        return self.to_mango_query().to_ddoc_view()

    def to_ddoc_filter(self) -> 'CouchDBDesignDocFilterQuery':
        return self.to_ddoc_view().to_ddoc_filter()

    def to_ddoc_update(self) -> 'CouchDBDesignDocUpdateQuery':
        return self.to_mango_query().to_ddoc_update()

    def to_mango_query(self) -> 'CouchDBMangoQuery':
        base_query = CouchDBMangoQuery({}, self.query_identity)
        base_query._load_magic(self)
        return base_query


class CouchDBMangoQuery(AbstractCouchDBQuery):

    __slots__ = ('selector', )

    def __init__(self, selector: Dict, query_identity: str = '') -> None:
        super().__init__(query_identity)
        self.selector = selector
        self.url = '_find'

    def start(self) -> Generator[GenResp, GenAccept, GenAccept]:
        base_dict = self._prepare_base_dict()
        base_dict['json']['selector'] = self.selector
        final_response = yield base_dict
        return final_response

    def to_ddoc_view(self) -> 'CouchDBDesignDocViewQuery':
        design_doc = DesignDocView(
            self.query_identity,
            CouchDBFilterMapFunction(self.selector)
        )
        base_query = CouchDBDesignDocViewQuery(design_doc, self.query_identity)
        base_query._load_magic(self)
        return base_query

    def to_ddoc_filter(self) -> 'CouchDBDesignDocFilterQuery':
        return self.to_ddoc_view().to_ddoc_filter()

    def to_mango_query(self) -> 'CouchDBMangoQuery':
        return self

    def to_ddoc_update(self) -> 'CouchDBDesignDocUpdateQuery':
        return self.to_ddoc_view().to_ddoc_update()

    def __eq__(self, other) -> bool:
        if not isinstance(other, CouchDBMangoQuery):
            return False
        if not super().__eq__(other):
            return False
        return self.selector == other.selector

    def __str__(self) -> str:
        return f'MangoQuery[selector={self.selector}, {super().__str__()}'


class CouchDBDesignDocViewQuery(AbstractCouchDBQuery):

    design_doc_usage = True

    __slots__ = ('ddoc_view', )

    def __init__(self, ddoc_view: DesignDocView, query_identity: str = '') -> None:
        super().__init__(query_identity)
        self.ddoc_view = ddoc_view
        self.method = 'get'
        self.url = f'_design/{DDOC_FOR_GENERATED_VIEWS_NAME}/_view/{self.ddoc_view.name}'

    def start(self) -> Generator[GenResp, GenAccept, GenAccept]:
        design_doc_load_query = {
            "method": "get",
            "url": f"{self.table_name}/_design/{DDOC_FOR_GENERATED_VIEWS_NAME}"
        }
        design_doc = yield design_doc_load_query
        if self.ddoc_view.name not in design_doc['views']:  # type: ignore
            design_doc['views'].update(self.ddoc_view.to_dict())  # type: ignore
            design_doc_put_query = {
                "method": "put",
                "url": f"/{self.table_name}/_design/{DDOC_FOR_GENERATED_VIEWS_NAME}",
                "json": design_doc,
            }
            yield design_doc_put_query
        query = self._prepare_base_dict()
        final_response = yield query
        return final_response

    def to_ddoc_view(self) -> 'CouchDBDesignDocViewQuery':
        return self

    def to_ddoc_update(self) -> 'CouchDBDesignDocUpdateQuery':
        design_doc = DesignDocUpdate(
            self.query_identity,
            CouchDBUpdateFunction({}, self.ddoc_view.map_function)
        )
        base_query = CouchDBDesignDocUpdateQuery(design_doc, self)
        base_query._load_magic(self)
        return base_query

    def to_mango_query(self) -> 'CouchDBMangoQuery':
        raise QueryBuildException("Cannot convert design doc query to mango query!")

    def to_ddoc_filter(self) -> 'CouchDBDesignDocFilterQuery':
        if self.ddoc_view.reduce_function:
            raise QueryBuildException("You cannot use changes with reduce in CouchDB :(")
        ddoc_filter = DesignDocFilter(
            self.query_identity,
            CouchDBFilterFunction(self.ddoc_view.map_function)
        )
        base_query = CouchDBDesignDocFilterQuery(ddoc_filter, self.query_identity)
        base_query._load_magic(self)
        return base_query

    def __eq__(self, other) -> bool:
        if not isinstance(other, CouchDBDesignDocViewQuery):
            return False
        if not super().__eq__(other):
            return False
        return self.ddoc_view == other.ddoc_view


class CouchDBDesignDocFilterQuery(AbstractCouchDBQuery):

    design_doc_usage = True

    __slots__ = ('ddoc_filter', )

    def __init__(self, ddoc_filter: DesignDocFilter, query_identity: str = '') -> None:
        super().__init__(query_identity)
        self.ddoc_filter = ddoc_filter
        self.url = f'_changes'
        self.method = 'get'
        self.grab_connection = True
        if self.params is None:
            self.params = {}
        self.params['filter'] = f"{DDOC_FOR_GENERATED_VIEWS_NAME}/{self.ddoc_filter.name}"

    def start(self) -> Generator[GenResp, GenAccept, GenAccept]:
        design_doc_load_query = {
            "method": "get",
            "url": f"/{self.table_name}/_design/{DDOC_FOR_GENERATED_VIEWS_NAME}"
        }
        design_doc = yield design_doc_load_query
        if self.ddoc_filter.name not in design_doc['filters']:  # type: ignore
            design_doc['filters'].update(self.ddoc_filter.to_dict())  # type: ignore
            design_doc_put_query = {
                "method": "put",
                "url": f"/{self.table_name}/_design/{DDOC_FOR_GENERATED_VIEWS_NAME}",
                "json": design_doc,
            }
            yield design_doc_put_query
        query = self._prepare_base_dict()
        final_response = yield query
        return final_response

    def to_ddoc_view(self) -> 'CouchDBDesignDocViewQuery':
        design_doc = DesignDocView(
            self.query_identity,
            self.ddoc_filter.filter_function.filter_map
        )
        base_query = CouchDBDesignDocViewQuery(design_doc, self.query_identity)
        base_query._load_magic(self)
        return base_query

    def to_ddoc_update(self) -> 'CouchDBDesignDocUpdateQuery':
        design_doc = DesignDocUpdate(
            self.query_identity,
            CouchDBUpdateFunction({}, self.ddoc_filter.filter_function.filter_map)
        )
        base_query = CouchDBDesignDocUpdateQuery(design_doc, self.to_ddoc_view())
        base_query._load_magic(self)
        return base_query

    def to_ddoc_filter(self) -> 'CouchDBDesignDocFilterQuery':
        return self

    def to_mango_query(self) -> 'CouchDBMangoQuery':
        raise QueryBuildException("Cannot convert design doc query to mango query!")

    def __eq__(self, other) -> bool:
        if not isinstance(other, CouchDBDesignDocFilterQuery):
            return False
        if not super().__eq__(other):
            return False
        return self.ddoc_filter == other.ddoc_filter


class CouchDBDesignDocUpdateQuery(AbstractCouchDBQuery):

    design_doc_usage = True

    __slots__ = ('ddoc_update', 'search_query')

    def __init__(
            self, ddoc_update: DesignDocUpdate,
            search_query: AbstractCouchDBQuery, query_identity: str = '') -> None:
        super().__init__(query_identity)
        self.ddoc_update = ddoc_update
        self.search_query: Union[CouchDBDesignDocViewQuery, CouchDBMangoQuery]
        if search_query.design_doc_usage:
            self.search_query = search_query.to_ddoc_view()
        else:
            self.search_query = search_query.to_mango_query()
        self.url = f'_design/{DDOC_FOR_GENERATED_VIEWS_NAME}/_update/{self.ddoc_update.name}'
        self.method = 'put'

    def _dict_for_doc_id(self, doc_id: str) -> Dict:
        base_dict = self._prepare_base_dict()
        base_dict['url'] = f"{base_dict['url']}/{doc_id}"
        return base_dict

    def start(self) -> Generator[GenResp, GenAccept, GenAccept]:
        search_response = yield from self.search_query.start()
        doc_list = search_response.get('docs', search_response.get('rows', []))  # type: ignore
        doc_ids = map(lambda x: x['value']['_id'], doc_list)
        design_doc_load_query = {
            "method": "get",
            "url": f"/{self.table_name}/_design/{DDOC_FOR_GENERATED_VIEWS_NAME}"
        }
        design_doc = yield design_doc_load_query
        if self.ddoc_update.name not in design_doc['updates']:  # type: ignore
            design_doc['updates'].update(self.ddoc_update.to_dict())  # type: ignore
            design_doc_put_query = {
                "method": "put",
                "url": f"/{self.table_name}/_design/{DDOC_FOR_GENERATED_VIEWS_NAME}",
                "json": design_doc,
            }
            yield design_doc_put_query
        final_response = yield (self._dict_for_doc_id(doc_id) for doc_id in doc_ids)
        return final_response

    def to_ddoc_view(self) -> 'CouchDBDesignDocViewQuery':
        return self.search_query.to_ddoc_view()

    def to_ddoc_update(self) -> 'CouchDBDesignDocUpdateQuery':
        return self

    def to_ddoc_filter(self) -> 'CouchDBDesignDocFilterQuery':
        return self.search_query.to_ddoc_filter()

    def to_mango_query(self) -> 'CouchDBMangoQuery':
        return self.search_query.to_mango_query()

    def __eq__(self, other) -> bool:
        if not isinstance(other, CouchDBDesignDocUpdateQuery):
            return False
        if not super().__eq__(other):
            return False
        return self.ddoc_update == other.ddoc_update
