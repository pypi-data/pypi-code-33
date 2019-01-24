from typing import List

import re

from .pattern_to_token import PatternRecognizer, PatternRecognizerRealigner
from .label_transducer import get_most_common


class MergeWhiteSpaceCharacters(PatternRecognizer):

    """
    Recognize contiguous whitespace characters in the string
    and replace it with a whitespace character (" ")

    E.g.
    >>> from uttut.pipeline.ops.merge_whitespace_characters import MergeWhiteSpaceCharacters
    >>> op = MergeWhiteSpaceCharacters()
    >>> output_seq, output_labels, realigner = op.transform("\n\n  \t\t", [1, 1, 1, 1, 1, 1])
    >>> output_seq
    " "
    >>> output_labels
    [0]
    >>> realigner(output_labels)
    [0, 0, 0, 0, 0, 0]

    """

    REGEX_PATTERN = re.compile(r"\s+")
    TOKEN = " "

    def __init__(self):
        super().__init__(realigner_class=MergeWhiteSpaceCharactersRealigner)

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common(labels=labels, output_size=output_size)


class MergeWhiteSpaceCharactersRealigner(PatternRecognizerRealigner):

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common(labels=labels, output_size=output_size)
