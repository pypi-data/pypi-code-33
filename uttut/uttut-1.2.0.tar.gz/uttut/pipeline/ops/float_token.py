from typing import List
import re

from .tokens import FLOAT_TOKEN
from .int_token import IntTokenRealigner
from .label_transducer import get_most_common
from .pattern_to_token import PatternRecognizer


class FloatToken(PatternRecognizer):
    """
    Recognize float (ex: 12.3, 1.7) in the input string
    and replace them with FLOAT_TOKEN (_float_)

    E.g.
    >>> from uttut.pipeline.ops.float_token import FloatToken
    >>> op = FloatToken()
    >>> output_seq, output_labels, realigner = op.transform("10.7", [1, 1, 1, 1])
    >>> output_seq
    "_float_"
    >>> output_labels
    [1, 1, 1, 1, 1, 1, 1]
    >>> realigner(output_labels)
    [1, 1, 1, 1]

    """

    REGEX_PATTERN = re.compile(r"(?<![\.\d])\d+\.\d+(?![\.\d])")
    TOKEN = FLOAT_TOKEN

    def __init__(self):
        super().__init__(realigner_class=IntTokenRealigner)

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common(labels=labels, output_size=output_size)

    def _gen_forward_replacement_group(self, input_str: str):  # type: ignore
        return super()._gen_forward_replacement_group(
            input_str=input_str,
            annotation='float-token',
        )
