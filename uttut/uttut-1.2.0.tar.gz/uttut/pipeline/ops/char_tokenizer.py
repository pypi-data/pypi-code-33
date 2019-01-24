from typing import List

from .base import Realigner
from .tokenizer import Tokenizer


class CharTokenizer(Tokenizer):

    def __init__(self):
        super().__init__(realigner_class=CharTokenizerRealigner)

    def _tokenize(self, input_str: str) -> List[str]:
        return list(input_str)


class CharTokenizerRealigner(Realigner):

    def _realign_labels(self, labels: List[int]):
        return labels
