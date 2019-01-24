from typing import List
import re

from .tokens import FLOAT_TOKEN_WITH_SPACE
from .int_token_with_space import IntTokenWithSpaceRealigner, _forward_transduce_func
from .pattern_to_token import PatternRecognizer


class FloatTokenWithSpace(PatternRecognizer):
    """
    Recognize integer (ex: 12.3, 100.77) in the input string
    and replace them with FLOAT_TOKEN_WTIH_SPACE ( _float_ )

    Note that extra spaces are added behind and after the FLOAT_TOKEN.

    E.g.
    >>> from uttut.pipeline.ops.float_token_with_space import FloatTokenWithSpace
    >>> op = FloatTokenWithSpace()
    >>> output_seq, output_labels, realigner = op.transform("10.7", [1, 1, 1, 1])
    >>> output_seq
    " _float_ "
    >>> output_labels
    [0, 1, 1, 1, 1, 1, 1, 1, 0]
    >>> realigner(output_labels)
    [1, 1, 1, 1]

    """

    REGEX_PATTERN = re.compile(r"(?<![\.\d])\d+\.\d+(?![\.\d])")
    TOKEN = FLOAT_TOKEN_WITH_SPACE

    def __init__(self):
        super().__init__(realigner_class=IntTokenWithSpaceRealigner)

    def _gen_forward_replacement_group(self, input_str: str):  # type: ignore
        return super()._gen_forward_replacement_group(
            input_str=input_str,
            annotation='float-token-with-space',
        )

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return _forward_transduce_func(labels=labels, output_size=output_size, token=self.TOKEN)
