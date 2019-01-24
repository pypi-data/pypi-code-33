from typing import List

from .tokenizer import Tokenizer, TokenizerRealigner
from .label_transducer import get_most_common_except_not_entity


class WhiteSpaceTokenizer(Tokenizer):

    """
    Spilt input string into pieces by whitespace characters

    This is a modification of `whitespace_tokenize` in Bert `tokenization.py`.

    E.g.
    >>> from uttut.pipeline.ops.whitespace_tokenizer import WhiteSpaceTokenizer
    >>> op = WhiteSpaceTokenizer()
    >>> output_seq, output_labels, realigner = op.transform("a b", [1, 2, 3])
    >>> output_seq
    ["a", "b"]
    >>> output_labels
    [1, 3]
    >>> realigner(output_labels)
    [1, 0, 3]

    """

    def __init__(self):
        super().__init__(WhiteSpaceTokenizerRealigner)

    def _tokenize(self, input_str: str) -> List[str]:

        """Split text into list by whitespace characters

        E.g.
        1. "a  \t\t\n\n b" -> ["a", "b"]
        2. "  \n\t\n  " -> []
        3. "  a b \t\n" -> ["a", "b"]

        """
        return input_str.split()


class WhiteSpaceTokenizerRealigner(TokenizerRealigner):

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)
