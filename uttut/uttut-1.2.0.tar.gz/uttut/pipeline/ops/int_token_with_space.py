from typing import List

import re
from collections import Counter

from .tokens import INT_TOKEN_WITH_SPACE
from .pattern_to_token import PatternRecognizer, PatternRecognizerRealigner
from .label_transducer import get_most_common_except_not_entity
from uttut import ENTITY_LABEL


def _forward_transduce_func(labels: List[int], output_size: int, token: str) -> List[int]:
    counter = Counter(labels)
    common_label = counter.most_common()[0][0]
    token_len = len(token) - 2
    output_label = [ENTITY_LABEL['NOT_ENTITY']] + \
        [common_label] * token_len + [ENTITY_LABEL['NOT_ENTITY']]
    return output_label


class IntTokenWithSpace(PatternRecognizer):
    """
    Recognize integer (ex: 12, 10000) in the input string
    and replace them with INT_TOKEN_WTIH_SPACE ( _int_ )

    E.g.
    >>> from uttut.pipeline.ops.int_token_with_space import IntTokenWithSpace
    >>> op = IntTokenWithSpace()
    >>> output_seq, output_labels, realigner = op.transform("10", [1, 1])
    >>> output_seq
    " _int_ "
    >>> output_labels
    [0, 1, 1, 1, 1, 1, 0]
    >>> realigner(output_labels)
    [1, 1]

    """

    REGEX_PATTERN = re.compile(r"(?<![\.\d])\d+(?![\.\d])")
    TOKEN = INT_TOKEN_WITH_SPACE

    def __init__(self):
        super().__init__(realigner_class=IntTokenWithSpaceRealigner)

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return _forward_transduce_func(labels=labels, output_size=output_size, token=self.TOKEN)

    def _gen_forward_replacement_group(self, input_str: str):  # type: ignore
        return super()._gen_forward_replacement_group(
            input_str=input_str,
            annotation='int-token-with-space',
        )


class IntTokenWithSpaceRealigner(PatternRecognizerRealigner):

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)
