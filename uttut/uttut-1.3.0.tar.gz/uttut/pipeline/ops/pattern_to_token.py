from typing import List, Tuple, Pattern

from .base import Operator, LabelAligner
from ..edit.replacement import ReplacementGroup
from ..edit import str2str
from ..edit.label_propagation import propagate_by_replacement_group


class PatternRecognizer(Operator):
    """
    Base class for Operators which recognize text patterns using regular expressions
    and replace them with a predefined token.
    """

    REGEX_PATTERN: Pattern
    TOKEN: str

    def __init__(self, label_aligner_class):
        super().__init__(input_type=str, output_type=str)
        self._label_aligner_class = label_aligner_class

    def __eq__(self, other):
        same_label_aligner_class = self._label_aligner_class == other._label_aligner_class
        return same_label_aligner_class and super().__eq__(other)

    def _transform(self, input_sequence: str) -> Tuple[str, 'LabelAligner']:
        forward_replacement_group = self._gen_forward_replacement_group(input_sequence)
        output_sequence = str2str.apply(input_sequence, forward_replacement_group)

        label_aligner = self._label_aligner_class(
            input_sequence=input_sequence,
            edit=forward_replacement_group,
            output_length=len(output_sequence),
        )
        return output_sequence, label_aligner

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
            replacement_group.add(
                start=match.start(),
                end=match.end(),
                new_value=self.TOKEN,
                annotation=annotation,
            )
            shift = match.end()
        replacement_group.done()
        return replacement_group


class PatternRecognizerAligner(LabelAligner):

    def _transform(self, labels: List[int]):
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=self._forward_edit,
            transduce_func=self._forward_transduce_func,
        )

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        raise NotImplementedError

    def _inverse_transform(self, labels):
        inverse_replacement_group = str2str.inverse(self._input_sequence, self._forward_edit)
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=inverse_replacement_group,
            transduce_func=self._backward_transduce_func,
        )

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        raise NotImplementedError
