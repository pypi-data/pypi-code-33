# Standard Library
import json
import logging

from abc import abstractmethod
from typing import Any, Dict, List, Optional, Union

# Third Party Library
import jsonpath_rw

from lxml.etree import HTML
from lxml.etree import _Element as Element

# Local Folder
from .response import Response
from .utils import Params, sentinel


__all__ = (
    "AttrCSSSelectorExtractor",
    "CSSSelectorExtractor",
    "Extractor",
    "Field",
    "HTMLExtractor",
    "HTMLItem",
    "Item",
    "JSONExtractor",
    "JSONItem",
    "META_KEY_ETREE",
    "META_KEY_JSON",
    "TextCssSelectorExtractor",
    "XpathExtractor",
)
logger = logging.getLogger(__name__)


META_KEY_ETREE = "EXTRACTOR_ETREE"
META_KEY_JSON = "EXTRACTOR_JSON"


class Extractor:
    def parse(self, response: Response) -> Union[Element, Any]:
        raise NotImplementedError()

    @abstractmethod
    def extract(
        self, root: Union[Element, Any]
    ) -> Union[List[str], List[Element], Any]:
        raise NotImplementedError()

    @abstractmethod
    def extract_first(
        self, root: Union[Element, Any], default: Any = sentinel
    ) -> Union[str, Element, Any]:
        rv = self.extract(root)
        if not rv:
            if default is sentinel:
                raise ValueError(f"Invalid {self!r}")

            return default

        return rv[0]

    @abstractmethod
    def extract_from_response(
        self, response: Response
    ) -> Union[List[str], List[Element], Any]:
        root = self.parse(response)
        return self.extract(root)

    def extract_first_from_response(
        self, response: Response, default: Any = sentinel
    ) -> Union[str, Element, Any]:
        root = self.parse(response)
        return self.extract_first(root, default=default)


class HTMLExtractor(Extractor):
    def parse(self, response: Response) -> Element:
        if META_KEY_ETREE not in response.meta:
            response.meta[META_KEY_ETREE] = HTML(response.text)

        return response.meta.get(META_KEY_ETREE)


class XpathExtractor(HTMLExtractor):
    def __init__(self, expr: str):
        self.expr = expr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expr!r})"

    def extract(self, root: Element) -> Union[List[str], List[Element]]:
        return root.xpath(self.expr)


class CSSSelectorExtractor(HTMLExtractor):
    def __init__(self, expr: str):
        self.expr = expr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expr!r})"

    def extract(self, root: Element) -> List[Element]:
        return root.cssselect(self.expr)


class TextCssSelectorExtractor(CSSSelectorExtractor):
    def extract(self, root: Element) -> List[str]:
        return [ele.text for ele in super().extract(root) if ele.text]


class AttrCSSSelectorExtractor(CSSSelectorExtractor):
    def __init__(self, expr: str, attr: str, default: Any = sentinel):
        super().__init__(expr)
        self.attr = attr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expr={self.expr!r}, attr={self.attr!r})"

    def extract(self, root: Element) -> List[str]:
        return [
            ele.get(self.attr)
            for ele in super().extract(root)
            if self.attr in ele.keys()
        ]


class JSONExtractor(Extractor):
    def __init__(self, expr: str):
        self.expr = expr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expr!r})"

    def parse(self, response: Response) -> Any:
        if META_KEY_JSON not in response.meta:
            response.meta[META_KEY_JSON] = json.loads(response.text)

        return response.meta.get(META_KEY_JSON)

    def extract(self, root: Any) -> Any:
        return [m.value for m in jsonpath_rw.parse(self.expr).find(root)]


class Field:
    def __init__(
        self, extractor: Extractor, default: Any = sentinel, is_many: bool = False
    ):
        self.extractor = extractor
        self.default = default
        self.is_many = is_many

    def extract(self, root: Union[Element, Any]) -> Union[str, Element, Any]:
        if self.is_many:
            return self.extractor.extract(root)
        else:
            return self.extractor.extract_first(root, default=self.default)


class Item(Extractor):
    root_extractor: Optional[Extractor] = None
    fields: Dict[str, Extractor] = {}

    def __init__(self, root_extractor: Union[Extractor, None, Params] = sentinel):
        if root_extractor is not sentinel:
            assert root_extractor is None or isinstance(root_extractor, Extractor)
            self.root_extractor = root_extractor

    def extract(self, root: Element) -> Union[List[str], List[Element]]:
        if self.root_extractor is not None:
            roots = self.root_extractor.extract(root)
        else:
            roots = [root]

        rvs = []
        for root in roots:
            rv = {}
            for name, extractor in self.fields.items():
                value = extractor.extract(root)
                rv[name] = value

            rvs.append(rv)

        return rvs


class HTMLItem(Item, HTMLExtractor):
    pass


class JSONItem(Item, JSONExtractor):
    pass
