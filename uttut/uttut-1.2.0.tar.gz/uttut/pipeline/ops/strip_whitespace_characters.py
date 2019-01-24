from typing import List

import re

from .pattern_to_token import PatternRecognizer, PatternRecognizerRealigner
from .label_transducer import get_not_entity


class StripWhiteSpaceCharacters(PatternRecognizer):

    """
    Recognize leading and trailing whitespace characters in the string
    and replace them with an empty string ("")

    E.g.
    >>> from uttut.pipeline.ops.strip_whitespace_characters import StripWhiteSpaceCharacters
    >>> op = StripWhiteSpaceCharacters()
    >>> output_seq, output_labels, realigner = op.transform(" a\n", [1, 2, 3])
    >>> output_seq
    "a"
    >>> output_labels
    [2]
    >>> realigner(output_labels)
    [0, 2, 0]

    """

    REGEX_PATTERN = re.compile(r"\A\s+|\s+\Z")
    TOKEN = ""

    def __init__(self):
        super().__init__(realigner_class=StripWhiteSpaceCharactersRealigner)

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_not_entity(labels=labels, output_size=output_size)

    def _gen_forward_replacement_group(self, input_str: str):  # type: ignore
        return super()._gen_forward_replacement_group(
            input_str=input_str,
            annotation='strip whitespace',
        )


class StripWhiteSpaceCharactersRealigner(PatternRecognizerRealigner):

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_not_entity(labels=labels, output_size=output_size)
