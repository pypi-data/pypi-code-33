from bgez.core.inputs import InputType

__all__ = [
    'ButtonType',
]

class ButtonType(InputType[int]):

    RELEASED = 0
    RELEASING = 1
    PRESSING = 2
    PRESSED = 3

    STATES = (RELEASED, RELEASING, PRESSING, PRESSED)

    @classmethod
    def _normalize(cls, values):
        return cls._filter(values)

    @classmethod
    def _union(cls, values):
        '''
        Returns the highest state in `states`.\n
        This represents the case where multiple keys contribute to one action.
        (you can press either one or the other)
        '''
        return max(values)

    @classmethod
    def _intersection(cls, values):
        '''
        Returns the lowest state in `states`.\n
        This represents the case where multiple keys represent one action.
        (you have to press every key)
        '''
        return min(values)

    def released(self) -> bool:
        return self.value() == ButtonType.RELEASED

    def releasing(self) -> bool:
        return self.value() == ButtonType.RELEASING

    def pressing(self) -> bool:
        return self.value() == ButtonType.PRESSING

    def pressed(self) -> bool:
        return self.value() == ButtonType.PRESSED

    def active(self) -> bool:
        value = self.value()
        return value == ButtonType.PRESSED or value == ButtonType.PRESSING

    def inactive(self) -> bool:
        value = self.value()
        return value == ButtonType.RELEASED or value == ButtonType.RELEASING
