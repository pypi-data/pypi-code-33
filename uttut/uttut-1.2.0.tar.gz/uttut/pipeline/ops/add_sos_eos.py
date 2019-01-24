from typing import List, Tuple

from .base import Operator, Realigner
from .tokens import START_TOKEN, END_TOKEN
from ..edit import lst2lst
from ..edit.replacement import ReplacementGroup
from ..edit.label_propagation import propagate_by_replacement_group
from uttut import ENTITY_LABEL


class AddSosEos(Operator):

    """
    Add start token (<sos>) and end token (<eos>) to a sequence.

    E.g.
    >>> from uttut.pipeline.ops.add_sos_eos import AddSosEos
    >>> op = AddSosEos()
    >>> output_seq, output_labels, realigner = op.transform(
        ['I', 'have', '10.7', 'dollars', '.'], [1, 2, 3, 4, 5])
    >>> output_seq
    ['<sos>', 'I', 'have', '10.7', 'dollars', '.', '<eos>']
    >>> output_labels
    [0, 1, 2, 3, 4, 5, 0]
    >>> realigner(output_labels)
    [1, 2, 3, 4, 5]

    """

    def __init__(
            self,
            start_token: str = START_TOKEN,
            end_token: str = END_TOKEN,
        ):
        super().__init__(input_type=list, output_type=list)
        self.start_token = start_token
        self.end_token = end_token

    def __eq__(self, other):
        same_start_token = self.start_token == other.start_token
        same_end_token = self.end_token == other.end_token
        return same_start_token and same_end_token and super().__eq__(other)

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

        realigner = AddSosEosRealigner(
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
        replacement_group = ReplacementGroup.add_all(
            [
                (0, 0, [self.start_token]),  # insert start token
                (seqlen, seqlen, [self.end_token]),  # insert end token
            ],
        )
        return replacement_group

    def _forward_reduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return [ENTITY_LABEL['NOT_ENTITY']] * output_size


class AddSosEosRealigner(Realigner):

    def _backward_reduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return [ENTITY_LABEL['NOT_ENTITY']] * output_size

    def _realign_labels(self, labels: List[int]) -> List[int]:
        return propagate_by_replacement_group(labels, self._edit, self._backward_reduce_func)
