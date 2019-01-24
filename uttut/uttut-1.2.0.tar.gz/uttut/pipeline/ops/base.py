from abc import ABC, abstractmethod
from typing import Tuple, List, Any


class Operator(ABC):

    """Base class for Ops

    Sub-classes should implement `transform`

    Attributes:
        input_type: input type of sequence to transform
        output_type: output type of transformed sequence

    """

    def __init__(self, input_type, output_type):
        self._input_type = input_type
        self._output_type = output_type

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        same_input_type = self._input_type == other._input_type
        same_output_type = self._output_type == other._output_type
        return same_input_type and same_output_type

    @property
    def input_type(self):
        return self._input_type

    @property
    def output_type(self):
        return self._output_type

    @abstractmethod
    def transform(
            self,
            input_sequence,
            labels: List[int],
            state: dict = None,
        ) -> Tuple[Any, List[int], 'Realigner']:

        """Transform input_sequence and label

        Transform input_sequence to certain form which meets the output_type
        and updates labels if necessary.

        Args:
            input_sequence (input_type): utterance or tokens
            labels (ints): has same length of input_sequence
            state (dict): data dependent information (output of fit)

        Returns:
            output (output_type): the transformed result
            labels (ints): has same length as output of transfrom
            realigner (obj): an instance of Realigner

        """
        pass


class Realigner(ABC):

    """Base class for label Realigner

    Sub-classes should implement `_realign_labels`

    Attributes:
        input_length (int): the length of sequence transformed by Operator
        output_length (int): the length of input sequence passed to Operator.transform
        edit: process of transformation documented by `edit` structure.

    """

    def __init__(self, edit, input_length: int, output_length: int):
        self._edit = edit
        self._input_length = input_length
        self._output_length = output_length

    def __call__(self, labels: List[int]) -> List[int]:

        """Realign model labels to original input

        Args:
            labels (ints): has same length as output of Operator.transfrom

        Raise:
            ValueError if length of labels is not matched.

        Return:
            labels (ints): has same length as input of Operator.transform

        """
        self._validate_input(labels)
        output_labels = self._realign_labels(labels)
        self._validate_output(output_labels)
        return output_labels

    def _validate_input(self, labels: List[int]):
        if len(labels) != self._input_length:
            raise ValueError('Invalid input labels')

    def _validate_output(self, labels: List[int]):
        if len(labels) != self._output_length:
            raise ValueError('Invalid output labels')

    @abstractmethod
    def _realign_labels(self, labels: List[int]) -> List[int]:
        pass
