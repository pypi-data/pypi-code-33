from typing import List, Tuple

import re

from .base import Operator, Realigner
from ..edit.replacement import ReplacementGroup
from ..edit import str2str


class Lowercase(Operator):
    """
    Recognize uppercase characters and convert them into lowercase characters

    E.g.
    >>> from uttut.pipeline.ops.lowercase import Lowercase
    >>> op = Lowercase()
    >>> output_seq, output_labels, realigner = op.transform("ABc", [1, 2, 3])
    >>> output_seq
    "abc"
    >>> output_labels
    [1, 2, 3]
    >>> realigner(output_labels)
    [1, 2, 3]

    """

    REGEX_PATTERN = re.compile(r"[A-Z]+")

    def __init__(self):
        super().__init__(input_type=str, output_type=str)
        self._realigner_class = LowercaseRealigner

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
        assert len(input_sequence) == len(output_sequence)

        inverse_replacement_group = str2str.inverse(input_sequence, forward_replacement_group)

        realigner = self._realigner_class(
            edit=inverse_replacement_group,
            input_length=len(output_sequence),
            output_length=len(input_sequence),
        )

        return output_sequence, labels, realigner

    def _gen_forward_replacement_group(
            self,
            input_str: str,
            annotation: str = None,
        ) -> ReplacementGroup:

        shift = 0
        replacement_group = ReplacementGroup()

        while shift < len(input_str):
            match = self.REGEX_PATTERN.search(input_str, shift)
            if match is None:
                break
            matched_str = input_str[match.start(): match.end()]
            replacement_group.add(
                start=match.start(),
                end=match.end(),
                new_value=matched_str.lower(),
                annotation=annotation,
            )
            shift = match.end()
        replacement_group.done()
        return replacement_group


class LowercaseRealigner(Realigner):

    def _realign_labels(self, labels: List[int]) -> List[int]:
        return labels
