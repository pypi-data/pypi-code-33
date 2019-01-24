from typing import List, Tuple

from .base import Operator, Realigner
from .label_transducer import get_most_common_except_not_entity
from ..edit.replacement import ReplacementGroup
from ..edit import str2str
from ..edit.label_propagation import propagate_by_replacement_group
from uttut import ENTITY_LABEL


class AddWhitespaceAroundCharacter(Operator):

    """
    Base class for Operators which recognize the characters using function `_is_valid_char`
    and add whitespace around the matched one
    """

    def __init__(self):
        super().__init__(input_type=str, output_type=str)
        self._realigner_class = AddWhitespaceAroundCharRealigner

    def __eq__(self, other):
        same_realigner_class = self._realigner_class == other._realigner_class
        return same_realigner_class and super().__eq__(other)

    def transform(  # type: ignore
            self,
            input_sequence: str,
            labels: List[int],
            state: dict = None,
        ) -> Tuple[str, List[int], 'Realigner']:

        forward_replacement_group = self._gen_forward_replacement_group(input_sequence)
        output_sequence = str2str.apply(input_sequence, forward_replacement_group)
        inverse_replacement_group = str2str.inverse(input_sequence, forward_replacement_group)

        updated_labels = propagate_by_replacement_group(
            labels=labels,
            replacement_group=forward_replacement_group,
            transduce_func=self._forward_transduce_func,
        )

        realigner = self._realigner_class(
            edit=inverse_replacement_group,
            input_length=len(output_sequence),
            output_length=len(input_sequence),
        )

        return output_sequence, updated_labels, realigner

    def _gen_forward_replacement_group(self, input_str: str) -> ReplacementGroup:
        replacement_group = ReplacementGroup()

        for i, char in enumerate(input_str):
            if self._is_valid_char(char):
                replacement_group.add(
                    start=i,
                    end=i + 1,
                    new_value=f" {char} ",
                    annotation="add-whitespace-around-any-CJK-char",
                )

        replacement_group.done()
        return replacement_group

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        assert len(labels) == 1
        return [ENTITY_LABEL['NOT_ENTITY'], labels[0], ENTITY_LABEL['NOT_ENTITY']]

    def _is_valid_char(self, char: str) -> bool:
        raise NotImplementedError


class AddWhitespaceAroundCharRealigner(Realigner):

    def _realign_labels(self, labels: List[int]) -> List[int]:
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=self._edit,
            transduce_func=self._backward_transduce_func,
        )

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)
