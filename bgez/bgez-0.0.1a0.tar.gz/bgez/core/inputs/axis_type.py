from typing import Optional, Iterable, Type

from bgez.core.inputs import InputType

__all__ = [
    'AxisType',
]

class AxisType(InputType[float]):

    @classmethod
    def _normalize(cls: Type[InputType[float]], values: Iterable[float]) -> Iterable[float]:
        return (max(min(value, 1), -1) for value in cls._filter(values))

    @classmethod
    def _union(cls, values: Iterable[float]) -> float:
        '''
        Returns the furthest value from zero from `values`.\n
        This represents the case where multiple axis contribute to one action.
        '''
        return max(cls._normalize(values), key=abs)

    @classmethod
    def _intersection(cls, values: Iterable[float]) -> float:
        '''
        Returns the closest value from zero from `values`.\n
        Not sure what this represents yet, but if you were to compare two
        joysticks this way, you would have to push them in the same direction
        to see any effect.
        '''
        return min(cls._normalize(values), key=abs)

    def threshold(self, threshold: float, fallback: Optional[float] = None) -> Optional[float]:
        '''
        Returns `None` if `value` is below `threshold`, returns `value` otherwise.
        '''
        value = self.value()
        if abs(value) >= threshold:
            return value
        return fallback
