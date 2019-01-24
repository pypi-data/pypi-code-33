from typing import List, Tuple

from .base import Operator, Realigner
from .tokens import PAD_TOKEN

from ..edit import lst2lst
from ..edit.replacement import ReplacementGroup
from ..edit.label_propagation import propagate_by_replacement_group


class Pad(Operator):

    """
    Pad sequence to the given length using PAD_TOKEN (<pad>).

    E.g.
    >>> from uttut.pipeline.ops.pad import Pad
    >>> op = Pad(5)
    >>> output_seq, output_labels, realigner = op.transform(['apple'], [1])
    >>> output_seq
    ['apple', '<pad>', '<pad>', '<pad>', '<pad>']
    >>> output_labels
    [1, 0, 0, 0, 0]
    >>> realigner(output_labels)
    [1]

    """

    def __init__(
            self,
            maxlen: int,
            pad_token: str = PAD_TOKEN,
        ):
        super().__init__(input_type=list, output_type=list)
        self.pad_token = pad_token
        self.maxlen = maxlen

    def __eq__(self, other):
        same_pad_token = self.pad_token == other.pad_token
        same_maxlen = self.maxlen == other.maxlen
        return same_pad_token and same_maxlen and super().__eq__(other)

    def transform(  # type: ignore
            self,
            input_sequence: List[str],
            labels: List[int],
            state: dict = None,
        ) -> Tuple[List[str], List[int], 'Realigner']:

        forward_replacement_group = self._gen_forward_replacement_group(input_sequence)
        output_sequence = lst2lst.apply(input_sequence, forward_replacement_group)
        inverse_replacement_group = lst2lst.inverse(input_sequence, forward_replacement_group)

        updated_labels = propagate_by_replacement_group(
            labels, forward_replacement_group, self._forward_reduce_func)

        realigner = PadRealigner(
            edit=inverse_replacement_group,
            input_length=len(output_sequence),
            output_length=len(input_sequence),
        )

        return output_sequence, updated_labels, realigner

    def _gen_forward_replacement_group(
            self,
            input_lst: List[str],
            annotation: str = None,
        ) -> ReplacementGroup:

        seqlen = len(input_lst)
        diff = self.maxlen - seqlen

        if seqlen == self.maxlen:
            replacement_group = ReplacementGroup.add_all([])
        elif seqlen > self.maxlen:
            replacement_group = ReplacementGroup.add_all(
                [(self.maxlen, seqlen, [])],
            )
        else:
            replacement_group = ReplacementGroup.add_all(
                [(seqlen, seqlen, [self.pad_token] * diff)],
            )
        return replacement_group

    def _forward_reduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return [0] * output_size


class PadRealigner(Realigner):

    def _realign_labels(self, labels: List[int]) -> List[int]:
        return propagate_by_replacement_group(labels, self._edit, self._backward_reduce_func)

    def _backward_reduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return [0] * output_size
