from typing import List, Tuple

from ..edit import str2str, str2lst
from ..edit.label_propagation import (
    propagate_by_replacement_group,
    reduce_by_span_group,
    expand_by_span_group,
)

from .base import Operator, Realigner


class Tokenizer(Operator):
    """
    Base class for Operators which tokenize text.
    """

    def __init__(self, realigner_class):
        super().__init__(input_type=str, output_type=list)
        self._realigner_class = realigner_class

    def __eq__(self, other):
        same_realigner_class = self._realigner_class == other._realigner_class
        return same_realigner_class and super().__eq__(other)

    def transform(  # type: ignore
            self,
            input_sequence: str,
            labels: List[int],
            state: dict = None,
        ) -> Tuple[List[str], List[int], 'Realigner']:

        tokens = self._tokenize(input_sequence)

        # transform sequence
        forward_replacement_group = str2lst.gen_replacement_group(input_sequence, tokens)
        temp_str = str2str.apply(input_sequence, forward_replacement_group)
        inverse_replacement_group = str2str.inverse(input_sequence, forward_replacement_group)

        span_group = str2lst.gen_span_group(temp_str, tokens)

        # labels
        output_labels = propagate_by_replacement_group(labels, forward_replacement_group)
        output_labels = reduce_by_span_group(output_labels, span_group)

        realigner = self._realigner_class(
            input_length=len(tokens),
            output_length=len(input_sequence),
            edit={
                'replacement_group': inverse_replacement_group,
                'span_group': span_group,
            },
        )
        return tokens, output_labels, realigner

    def _tokenize(self, input_str: str) -> List[str]:
        raise NotImplementedError


class TokenizerRealigner(Realigner):

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        raise NotImplementedError

    def _realign_labels(self, labels: List[int]) -> List[int]:
        output_labels = expand_by_span_group(labels=labels, span_group=self._edit['span_group'])
        output_labels = propagate_by_replacement_group(
            labels=output_labels,
            replacement_group=self._edit['replacement_group'],
            transduce_func=self._backward_transduce_func,
        )
        return output_labels
