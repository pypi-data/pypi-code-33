from typing import List, Callable, Sequence
from collections import Counter

from .replacement import ReplacementGroup
from .span import SpanGroup


def propagate_by_replacement_group(
        labels: List[int],
        replacement_group: ReplacementGroup,
        transduce_func: Callable[[List[int], int], List[int]] = None,
    ) -> List[int]:
    '''Map the labels[fstart_i: fend_i] to output_labels[rstart_i: rend_i]

    Note that the length of replacement_group should be the same as
    that of backward_replacement_group.
    Map the reduced label in [forward_replacement[i].start, forward_replacement[i].end)
    to output list

    Args:
        labels (list of ints)
        replacement_group (ReplacementGroup)
        transduce_func (Callable): a function that return an integer given a list of integers.

    Return:
        labels (list of ints)
    '''
    if transduce_func is None:
        transduce_func = _get_most_common_label

    output_len = _compute_output_length(labels, replacement_group)
    output_labels = [0] * output_len

    i_start = 0
    o_start = 0

    for replacement in replacement_group:
        # before replacement
        fixed_len = replacement.start - i_start
        output_labels[o_start: o_start + fixed_len] = labels[i_start: replacement.start]
        o_start += fixed_len

        # replacement
        expand_size = len(replacement.new_value)
        output_labels[o_start: o_start + expand_size] = transduce_func(
            labels[replacement.start: replacement.end],
            expand_size,
        )

        i_start = replacement.end
        o_start += expand_size

    # final
    output_labels[o_start:] = labels[i_start:]
    return output_labels


def _get_most_common_label(labels: List[int], output_size: int = 1):
    if len(labels) == 0:
        most_common_label = 0
    else:
        counter = Counter(labels)
        most_common_label = counter.most_common(1)[0][0]
    return [most_common_label] * output_size


def _compute_output_length(
        input_seq: Sequence,
        replacement_group: ReplacementGroup,
    ) -> int:
    # use cases: str -> str or list -> list
    len_iters = len(input_seq)
    offset = 0
    for replacement in replacement_group:
        after = len(replacement.new_value)
        before = replacement.end - replacement.start
        offset += after - before

    return len_iters + offset


def reduce_by_span_group(
        labels: List[int],
        span_group: SpanGroup,
        transduce_func: Callable[[List[int], int], List[int]] = None,
    ) -> List[int]:
    # use case: string -> list

    if transduce_func is None:
        transduce_func = _get_most_common_label

    # empty span group and empty labels pair
    if (len(span_group) == 0) and (len(labels) == 0):
        return labels

    if len(labels) != span_group[-1].end:
        raise ValueError('labels and span_group are not compatible.')

    output_len = len(span_group)
    output_labels = [0] * output_len

    for i, span in enumerate(span_group):
        output_labels[i: i + 1] = transduce_func(labels[span.start: span.end], 1)

    return output_labels


def expand_by_span_group(
        labels: List[int],
        span_group: SpanGroup,
    ) -> List[int]:
    # use case: list -> str

    if len(span_group) != len(labels):
        raise ValueError('labels and span_group are not compatible.')

    # empty span group and empty labels pair
    if len(span_group) == 0:
        return labels

    output_len = span_group[-1].end
    output_labels = [0] * output_len

    for span, label in zip(span_group, labels):
        for i in range(span.start, span.end):
            output_labels[i] = label

    return output_labels
