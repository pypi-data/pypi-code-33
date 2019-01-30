from abc import ABC, abstractmethod
from enum import Enum, auto
import logging
from functools import partial, reduce
import operator
import re
from typing import Optional, List, Tuple, Any, Type, Set, TYPE_CHECKING, Callable

from .utils import Interval

from .base import QueryBuildException
from .operations import QueryOperableStatement
from .transformation import QueryTransformableStatement

if TYPE_CHECKING:
    from .rows import QueryRowOrderMark, QueryRow  # pylint: disable=unused-import

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.1"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = [
    'QueryBinaryFilterStatement', 'StatementType', 'QueryAndStatement',
    'EmptyQueryStatement', 'QueryTable', 'SamplingType', 'QueryFilterStatement'
]

_log = logging.getLogger(__name__)

SamplingList = Optional[List[Tuple['SamplingType', Any]]]


def _correct_compare(arg1, arg2) -> bool:
    if hasattr(arg1, '__corrupted_eq_check__'):
        return arg1._equals(arg2)
    return arg1 == arg2


def _build_row(row: 'QueryRow', document, access_method):
    return reduce(access_method, row.row_path, document)


def _build_operands(statement: 'QueryBinaryFilterStatement', obj, access_method) -> Tuple[Any, Any]:
    from .rows import QueryRow  # pylint: disable=redefined-outer-name

    return (
        _build_row(statement.left, obj, access_method)
        if isinstance(statement.left, QueryRow) else statement.left,
        _build_row(statement.right, obj, access_method)
        if isinstance(statement.right, QueryRow) else statement.right
    )


def _adapt_function(element):
    from ..register import orm_register

    if isinstance(element, QueryFilterStatement):
        element._adapt_query()
    elif isinstance(element, Interval):
        element.left_bound = orm_register.backend_adapter.serialize_value(
            orm_register.backend_adapter.ensure_compatibility(element.left_bound)
        )
        element.right_bound = orm_register.backend_adapter.serialize_value(
            orm_register.backend_adapter.ensure_compatibility(element.right_bound)
        )
    else:
        element = orm_register.backend_adapter.serialize_value(
            orm_register.backend_adapter.ensure_compatibility(element)
        )
    return element


def sampling_merge(left: 'QueryFilterStatement', right: 'QueryFilterStatement') -> SamplingList:
    if left.sampling is None:
        return right.sampling
    result = left.sampling.copy()
    if right.sampling is not None:
        for sampling_tuple in right.sampling:
            if any(x[0] == sampling_tuple[0] for x in result):
                raise QueryBuildException("Cannot merge sampling with same sampling types!")
            result.append(sampling_tuple)
    return result


class StatementType(Enum):

    eq = '=='  # pylint: disable=invalid-name
    lt = '<'  # pylint: disable=invalid-name
    gt = '>'  # pylint: disable=invalid-name
    ne = '!='  # pylint: disable=invalid-name
    le = '<='  # pylint: disable=invalid-name
    ge = '>='  # pylint: disable=invalid-name
    isin = 'in'  # pylint: disable=invalid-name
    bound = 'bound'  # pylint: disable=invalid-name
    match = 'match'  # pylint: disable=invalid-name

    @property
    def operator(self) -> Optional[Callable]:
        if hasattr(operator, self.name):
            return getattr(operator, self.name)
        return None

    @property
    def has_operator(self) -> bool:
        return self.operator is not None


class SamplingType(Enum):

    limit = auto()
    skip = auto()
    sample = auto()
    order_by = auto()


class QueryFilterStatement(ABC, QueryOperableStatement, QueryTransformableStatement):

    __slots__ = ('_args', 'sampling',)
    _args_order_important = True

    def __init__(self, *args, model_ref=None) -> None:
        super().__init__(model_ref=model_ref)
        self._args: List = list(args)
        self.sampling: SamplingList = None

    def _adapt_query(self) -> None:
        self._args = list(map(_adapt_function, self._args))

    def filter(self, *filters: 'QueryFilterStatement') -> 'QueryFilterStatement':
        return self & reduce(operator.and_, filters)

    def limit(self, limit: int) -> 'QueryFilterStatement':
        if self.sampling is None:
            self.sampling = []
        if any(sample[0] in [SamplingType.sample, SamplingType.limit] for sample in self.sampling):
            raise QueryBuildException(
                "You cannot call limit after sample or limit!"
                " Please, all add order condition in first statement"
            )
        self.sampling.append((SamplingType.limit, limit))
        return self

    def skip(self, skip: int) -> 'QueryFilterStatement':
        if self.sampling is None:
            self.sampling = []
        self.sampling.append((SamplingType.skip, skip))
        return self

    def sample(self, sample: int) -> 'QueryFilterStatement':
        if self.sampling is None:
            self.sampling = []
        self.sampling.append((SamplingType.sample, sample))
        return self

    def order_by(self, *order_marks: 'QueryRowOrderMark') -> 'QueryFilterStatement':
        if self.sampling is None:
            self.sampling = []
        if any(sample[0] == SamplingType.order_by for sample in self.sampling):
            raise QueryBuildException(
                "You cannot call order_by twice!"
                " Please, all add order condition in first order_by statement"
            )
        self.sampling.append((SamplingType.order_by, order_marks))
        return self

    def merge(self, _other: 'QueryFilterStatement') -> 'QueryFilterStatement':
        raise QueryBuildException(f"{self.__class__.__name__} cannot be merged with anything")

    def can_be_merged(self, _other: 'QueryFilterStatement') -> bool:  # pylint: disable=no-self-use
        return False

    def implict_cast(self, target_type: Type['QueryFilterStatement']) -> Optional['QueryFilterStatement']:  # pylint: disable=no-self-use,unused-argument
        return None

    def __eq__(self, other) -> bool:
        if not isinstance(other, QueryFilterStatement):
            return False
        if not isinstance(other, self.__class__):
            return False
        other_query_filter: QueryFilterStatement = other  # type: ignore
        base_check = (
            len(self._args) == len(other_query_filter._args) and
            self.sampling == other_query_filter.sampling
        )
        if not base_check:
            return False
        if self._args_order_important:
            return self._compare_args_ordered(other_query_filter)
        return self._compare_args_unordered(other_query_filter)

    def _compare_args_ordered(self, other: 'QueryFilterStatement') -> bool:
        for index, arg in enumerate(self._args):
            if not _correct_compare(arg, other._args[index]):
                return False
        return True

    def _compare_args_unordered(self, other: 'QueryFilterStatement') -> bool:
        for arg in self._args:
            if not any(map(partial(_correct_compare, arg), other._args)):  # type: ignore
                return False
        return True

    def __repr__(self) -> str:
        return self.__str__()

    @abstractmethod
    def __and__(self, other: 'QueryFilterStatement') -> 'QueryFilterStatement':
        pass

    def to_python(self, obj, access_method) -> bool:  # pylint: disable=unused-argument
        raise QueryBuildException(f"Cannot cast {str(self)} query to python")


class QueryTable(QueryFilterStatement):

    __slots__ = ()

    @property
    def table_name(self):
        return self._args[0]

    def __str__(self) -> str:
        return f"table[{self.table_name}] over {self.model_ref.__module__}.{self.model_ref.__name__}"  # type: ignore

    def __and__(self, other: 'QueryFilterStatement') -> 'QueryFilterStatement':
        other.sampling = sampling_merge(self, other)
        return other


class QueryBinaryFilterStatement(QueryFilterStatement, ABC):

    _statement_type: StatementType
    _provide_merge_for: Set[StatementType]

    __slots__ = ()

    @property
    def left(self):
        return self._args[0]

    @property
    def right(self):
        return self._args[1]

    @property
    def statement_type(self) -> StatementType:
        return self._statement_type

    def __and__(self, other: QueryFilterStatement) -> QueryFilterStatement:
        if not isinstance(other, QueryBinaryFilterStatement):
            other_candidate = other.implict_cast(QueryBinaryFilterStatement)  # type: ignore
            if other_candidate is None:
                raise TypeError(
                    "Currently, cannot apply and for QueryBinaryFilterStatement"
                    f" with {other.__class__.__name__} query ast class"
                )
            other = other_candidate
        if self.can_be_merged(other):
            result = self.merge(other)
        else:
            result = QueryAndStatement(self, other, model_ref=self.model_ref or other.model_ref)
        result.sampling = sampling_merge(self, other)
        return result

    def and_(self, other: QueryFilterStatement) -> QueryFilterStatement:
        return self.__and__(other)

    def can_be_merged(self, other: QueryFilterStatement) -> bool:
        return (
            isinstance(other, QueryBinaryFilterStatement) and not self.complicated and
            not other.complicated and self.left.row_name == other.left.row_name
        )

    @abstractmethod
    def _merge_provider(self, other: 'QueryBinaryFilterStatement') -> Optional['QueryBinaryFilterStatement']:
        pass

    def to_python(self, obj, access_method) -> bool:
        if self.statement_type.operator is None:
            raise QueryBuildException(
                f"Please, override function to_python for {self.__class__}\n"
                "Base function works only with simple statements"
            )
        left_operand, right_operand = _build_operands(self, obj, access_method)
        return self._statement_type.operator(left_operand, right_operand)  # type: ignore

    def merge(self, other: 'QueryFilterStatement') -> 'QueryFilterStatement':
        if not isinstance(other, QueryBinaryFilterStatement):
            raise TypeError(f"Currently, cannot merge QueryBinaryFilterStatement with {other.__class__.__name__} query ast class")
        merge_provider_founded = False
        if other.statement_type in self._provide_merge_for:
            merge_result = self._merge_provider(other)
            merge_provider_founded = True
        elif self.statement_type in other._provide_merge_for:
            merge_result = other._merge_provider(self)
            merge_provider_founded = True
        if not merge_provider_founded:
            raise QueryBuildException("Cannot find merge provider!")
        if merge_result is None:
            return EmptyQueryStatement()
        return merge_result

    @property
    def complicated(self) -> bool:
        """
        Check if query statement has QueryRow on both leafs
        """
        from .rows import QueryRow  # pylint: disable=redefined-outer-name

        return isinstance(self.right, QueryRow)

    def __str__(self) -> str:
        return f"{self.left} {self.statement_type.value} {self.right}"

    def __repr__(self) -> str:
        return str(self)


class EmptyQueryStatement(QueryFilterStatement):
    """
    Empty query statement, return on incompatable statements merge
    """

    __slots__ = ()

    def __and__(self, other):
        return self

    def and_(self, other):
        return self.__and__(other)

    @property
    def complicated(self) -> bool:
        return False

    def can_be_merged(self, _other: 'QueryFilterStatement') -> bool:
        return True

    def merge(self, _other: 'QueryFilterStatement') -> 'QueryFilterStatement':
        return self

    def __str__(self) -> str:
        return '(empty set)'

    def __repl__(self) -> str:
        return str(self)

    def to_python(self, obj, access_method) -> bool:
        return False


class QueryAndStatement(QueryFilterStatement):

    _args_order_important = False

    __slots__ = ()

    def __and__(self, other: QueryFilterStatement) -> QueryFilterStatement:

        def statement_filter(statement):
            if isinstance(statement, QueryFilterStatement):
                return statement.can_be_merged(other)
            return False

        if not isinstance(other, QueryBinaryFilterStatement):
            other_candidate = other.implict_cast(QueryBinaryFilterStatement)  # type: ignore
            if other_candidate is None:
                raise TypeError(
                    "Currently, cannot apply and to QueryAndStatement with"
                    f" {other.__class__.__name__} query ast class"
                )
            other = other_candidate

        merge_candidate: Optional[QueryBinaryFilterStatement] = next(filter(statement_filter, self._args), None)
        if merge_candidate is not None:
            self._args[self._args.index(merge_candidate)] = merge_candidate.merge(other)
        else:
            self._args.append(other)
        return self

    def and_(self, other: QueryFilterStatement) -> QueryFilterStatement:
        return self.__and__(other)

    @property
    def complicated(self) -> bool:
        return True

    def __str__(self) -> str:
        return ' & '.join(map(str, self._args))

    def __repl__(self) -> str:
        return self.__str__()

    def to_python(self, obj, access_method) -> bool:
        return reduce(
            operator.and_,
            map(lambda x: x.to_python(obj, access_method), self._args[1:]),
            self._args[0].to_python(obj, access_method)
        )


class QueryEqualStatement(QueryBinaryFilterStatement):

    _statement_type = StatementType.eq
    _args_order_important = False
    _provide_merge_for = {
        StatementType.ne, StatementType.eq, StatementType.bound, StatementType.ge,
        StatementType.le, StatementType.lt, StatementType.gt, StatementType.isin
    }

    __slots__ = ()

    def _merge_provider(self, other: QueryBinaryFilterStatement) -> Optional[QueryBinaryFilterStatement]:
        compitability_check = (
            (other.statement_type == StatementType.eq and other.right == self.right) or
            (other.statement_type in [StatementType.isin, StatementType.bound] and self.right in other.right) or
            (other.statement_type == StatementType.lt and self.right < other.right) or
            (other.statement_type == StatementType.le and self.right <= other.right) or
            (other.statement_type == StatementType.ge and self.right >= other.right) or
            (other.statement_type == StatementType.gt and self.right > other.right) or
            (other.statement_type == StatementType.ne and self.right != other.right)
        )
        return self if compitability_check else None


class QueryGreaterOrEqualStatement(QueryBinaryFilterStatement):

    __slots__ = ()

    _statement_type = StatementType.ge
    _provide_merge_for = {
        StatementType.ge, StatementType.gt
    }

    def _merge_provider(self, other: QueryBinaryFilterStatement) -> Optional[QueryBinaryFilterStatement]:
        if self.right > other.right:
            return self
        return other


class QueryGreaterStatement(QueryBinaryFilterStatement):

    __slots__ = ()

    _statement_type = StatementType.gt
    _provide_merge_for = {
        StatementType.gt
    }

    def _merge_provider(self, other: QueryBinaryFilterStatement) -> Optional[QueryBinaryFilterStatement]:
        if self.right > other.right:
            return self
        return other


class QueryLowerOrEqualStatement(QueryBinaryFilterStatement):

    __slots__ = ()

    _statement_type = StatementType.le
    _provide_merge_for = {
        StatementType.ge, StatementType.le, StatementType.lt, StatementType.gt
    }

    def _merge_provider(self, other: QueryBinaryFilterStatement) -> Optional[QueryBinaryFilterStatement]:
        if other.statement_type in [StatementType.le, StatementType.lt]:
            if self.right < other.right:
                return self
            return other
        if self.right >= other.right:
            return QueryBoundStatement(
                self.left,
                Interval(
                    other.right, self.right,
                    left_close=other.statement_type == StatementType.ge, right_close=True
                ),
                model_ref=self.model_ref or other.model_ref
            )
        return None


class QueryLowerStatement(QueryBinaryFilterStatement):

    __slots__ = ()

    _statement_type = StatementType.lt
    _provide_merge_for = {
        StatementType.ge, StatementType.lt, StatementType.gt
    }

    def _merge_provider(self, other: QueryBinaryFilterStatement) -> Optional[QueryBinaryFilterStatement]:
        if other.statement_type == StatementType.lt:
            if self.right < other.right:
                return self
            return other
        if self.right >= other.right:
            return QueryBoundStatement(
                self.left,
                Interval(
                    other.right, self.right,
                    left_close=other.statement_type == StatementType.ge, right_close=False
                ),
                model_ref=self.model_ref or other.model_ref
            )
        return None


class QueryNotEqualStatement(QueryBinaryFilterStatement):

    __slots__ = ()

    _statement_type = StatementType.ne
    _args_order_important = False
    _provide_merge_for = {
        StatementType.ne, StatementType.eq, StatementType.bound, StatementType.ge,
        StatementType.le, StatementType.lt, StatementType.gt, StatementType.isin
    }

    def _merge_provider(self, other: QueryBinaryFilterStatement) -> Optional[QueryBinaryFilterStatement]:
        compitability_check = (
            (other.statement_type == StatementType.eq and other.right == self.right) or
            (other.statement_type in [StatementType.isin, StatementType.bound] and self.right in other.right) or
            (other.statement_type == StatementType.lt and self.right < other.right) or
            (other.statement_type == StatementType.le and self.right <= other.right) or
            (other.statement_type == StatementType.ge and self.right >= other.right) or
            (other.statement_type == StatementType.gt and self.right > other.right) or
            (other.statement_type == StatementType.ne and self.right != other.right)
        )
        if not compitability_check:
            return other
        if other.statement_type == StatementType.isin:
            new_elements = tuple(x for x in other.right if x != self.right)
            if new_elements:
                return QueryContainsStatement(self.left, new_elements, model_ref=self.model_ref or other.model_ref)
        if other.statement_type == StatementType.bound:
            if self.right in other.right:
                _log.warning("Currently, bound statement cannot be merged with ne statement, so just ingore ne statement")
            return other
        return None


class QueryContainsStatement(QueryBinaryFilterStatement):

    __slots__ = ()

    _statement_type = StatementType.isin
    _provide_merge_for = {
        StatementType.ge, StatementType.le, StatementType.lt, StatementType.gt, StatementType.isin
    }

    def _merge_provider(self, other: QueryBinaryFilterStatement) -> Optional[QueryBinaryFilterStatement]:
        if other.statement_type == StatementType.isin:
            intersection = tuple(x for x in self.right if x in other.right)
            if intersection:
                return QueryContainsStatement(self.left, intersection, model_ref=self.model_ref or other.model_ref)
            return None
        method_name = f"__{other.statement_type.name}__"
        for element in self.right:
            if not getattr(element, method_name)(other.right):
                return None
        return self

    def to_python(self, obj, access_method):
        left_operand, right_operand = _build_operands(self, obj, access_method)
        return left_operand in right_operand


class QueryBoundStatement(QueryBinaryFilterStatement):

    __slots__ = ()

    _statement_type = StatementType.bound
    _provide_merge_for = {
        StatementType.bound, StatementType.ge,
        StatementType.le, StatementType.lt, StatementType.gt, StatementType.isin
    }

    def _merge_provider(self, other: QueryBinaryFilterStatement) -> Optional[QueryBinaryFilterStatement]:
        if other.statement_type == StatementType.isin:
            for element in other.right:
                if element not in self.right:
                    return None
            return other
        interval = self.right.clone()
        # Convert to QueryBoundStatement to make same codebase for many statement type
        # If you want to change it, make sure that all types covered
        if other.statement_type in [StatementType.le, StatementType.lt]:
            interval.right_close = other.statement_type == StatementType.le
            interval.right_bound = other.right
            other = QueryBoundStatement(self.left, interval, model_ref=self.model_ref or other.model_ref)
        if other.statement_type in [StatementType.ge, StatementType.gt]:
            interval.left_close = other.statement_type == StatementType.ge
            interval.left_bound = other.right
            other = QueryBoundStatement(self.left, interval, model_ref=self.model_ref or other.model_ref)
        if other.statement_type == StatementType.bound:
            interval = other.right
        if interval.valid:
            if self.right.contains_interval(interval):
                return other
            if interval.contains_interval(self.right):
                return self
        return None

    def to_python(self, obj, access_method):
        from .rows import QueryRow  # pylint: disable=redefined-outer-name

        value = _build_row(self.left, obj, access_method) if isinstance(self.left, QueryRow) else self.left
        left_operation = operator.ge if self.right.left_close else operator.gt
        right_operation = operator.le if self.right.right_close else operator.lt
        return left_operation(value, self.right.left_bound) and right_operation(value, self.right.right_bound)


class QueryMatchStatement(QueryBinaryFilterStatement):

    __slots__ = ()

    _statement_type: StatementType = StatementType.match
    _provide_merge_for: Set[StatementType] = set()

    def can_be_merged(self, other: QueryFilterStatement) -> bool:
        return False

    def _merge_provider(self, other: 'QueryBinaryFilterStatement') -> Optional['QueryBinaryFilterStatement']:
        raise QueryBuildException("Merge cannot be provided for complicated match statement")

    def to_python(self, obj, access_method) -> bool:
        from .rows import QueryRow  # pylint: disable=redefined-outer-name

        value = _build_row(self.left, obj, access_method) if isinstance(self.left, QueryRow) else self.left
        return bool(re.match(self.right, value))
