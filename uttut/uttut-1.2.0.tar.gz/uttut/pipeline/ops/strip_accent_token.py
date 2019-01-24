from typing import List, Tuple
import unicodedata

from .base import Operator, Realigner
from .label_transducer import get_most_common_except_not_entity
from ..edit.replacement import ReplacementGroup
from ..edit import str2str
from ..edit.label_propagation import propagate_by_replacement_group


class StripAccentToken(Operator):

    """
    Strip accent token

    E.g.
    >>> from uttut.pipeline.ops.strip_accent_token import StripAccentToken
    >>> op = StripAccentToken()
    >>> output_seq, output_labels, realigner = op.transform(
        u"H\u00E9llo", [1, 2, 3, 4, 5])
    >>> output_seq
    "Hello"
    >>> output_labels
    [1, 2, 3, 4, 5]
    >>> realigner(output_labels)
    [1, 2, 3, 4, 5]

    """

    def __init__(self):
        super().__init__(input_type=str, output_type=str)
        self._realigner_class = StripAccentTokenRealigner

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

        output_str = _strip_accents(input_str)
        assert len(input_str) == len(output_str)

        for i, (input_char, output_char) in enumerate(zip(input_str, output_str)):
            if input_char != output_char:
                replacement_group.add(
                    start=i,
                    end=i + 1,
                    new_value=output_char,
                    annotation="strip-accent-token",
                )
        replacement_group.done()
        return replacement_group

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)


class StripAccentTokenRealigner(Realigner):

    def _realign_labels(self, labels: List[int]) -> List[int]:
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=self._edit,
            transduce_func=self._backward_transduce_func,
        )

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)


def _strip_accents(text: str) -> str:

    """Strips accents from a piece of text

    This code is copied from Bert `tokenization.py`.

    """

    text = unicodedata.normalize("NFD", text)
    output = []
    for char in text:
        cat = unicodedata.category(char)
        if cat == "Mn":
            continue
        output.append(char)
    return "".join(output)
