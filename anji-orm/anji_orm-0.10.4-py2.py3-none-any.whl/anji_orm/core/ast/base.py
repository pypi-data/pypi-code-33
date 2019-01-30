import logging
from typing import Any, Optional, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from ..model import Model  # pylint: disable=unused-import

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.4"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = [
    'QueryAst', "QueryBuildException"
]

_log = logging.getLogger(__name__)


class QueryBuildException(Exception):

    pass


class QueryAst:

    __slots__ = ('model_ref', )

    def __init__(self, model_ref: Optional[Type['Model']] = None) -> None:
        self.model_ref: Optional[Type['Model']] = model_ref

    def _adapt_query(self) -> None:
        pass

    def build_query(self) -> Any:
        from ..register import orm_register

        if self.model_ref is None:
            raise QueryBuildException("Cannot build query without model link!")
        self._adapt_query()
        return orm_register.shared.query_parser.parse_query(self)

    def run(self, without_fetch: bool = False):
        from ..register import orm_register

        if self.model_ref is None:
            raise QueryBuildException("Cannot build query without model link!")
        return orm_register.shared.executor.execute_query(self.build_query(), without_fetch=without_fetch)

    def first(self):
        execution_result = self.run()
        return next(execution_result, None)

    async def async_run(self, without_fetch: bool = False, ensure_related: bool = False):
        from ..register import orm_register
        from ..model import Model  # pylint: disable=redefined-outer-name

        if self.model_ref is None:
            raise QueryBuildException("Cannot build query without model link!")
        result = await orm_register.shared.executor.execute_query(self.build_query(), without_fetch=without_fetch)
        if ensure_related:
            if isinstance(result, Model):
                await result.ensure()
        return result

    async def async_first(self, ensure_related: bool = False):
        from ..model import Model  # pylint: disable=redefined-outer-name

        execution_result = await self.async_run()
        result = next(execution_result, None)
        if ensure_related:
            if isinstance(result, Model):
                await result.ensure()
        return result
