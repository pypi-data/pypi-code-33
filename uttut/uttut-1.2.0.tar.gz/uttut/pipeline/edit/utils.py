from typing import List, Sequence, MutableSequence, Union

from .replacement import ReplacementGroup


def _transform_sequence(
        input_seq: Union[str, List[str]],
        replacement_group: ReplacementGroup,
        output: MutableSequence,
    ) -> Sequence:
    '''
    input_seq: list of str or pure str
    '''

    start = 0
    i = 0
    for replacement in replacement_group:
        output[i] = input_seq[start: replacement.start]
        output[i + 1] = replacement.new_value
        start = replacement.end
        i += 2

    # tail
    output[-1] = input_seq[start:]

    return output


def _gen_inverse_replacement_group(
        input_seq: Union[str, List[str]],
        replacement_group: ReplacementGroup,
    ) -> ReplacementGroup:
    '''
    input_seq: list of str or pure str
    '''
    if replacement_group.is_empty():
        return ReplacementGroup.add_all([])

    inverse_replacement_group = ReplacementGroup()
    n_replacement = len(replacement_group)

    dists = get_dist_bt_replacement_group(replacement_group)
    dists.append(0)

    start = replacement_group[0].start

    for i in range(n_replacement):
        replacement = replacement_group[i]
        dist = dists[i]
        inverse_replacement_group.add(
            start=start,
            end=start + len(replacement.new_value),
            new_value=input_seq[replacement.start: replacement.end],
        )
        start += len(replacement.new_value) + dist
    inverse_replacement_group.done()
    return inverse_replacement_group


def get_dist_bt_replacement_group(replacement_group: ReplacementGroup) -> List[int]:
    '''Compute the distance between replacement_group

    The distance is the length of sequence.

    Eg.
        Given [Replacement(0, 1, ''), Replacement(4, 7, '')]: [3]  # 4 - 1
        Given [Replacement(0, 3, ''), Replacement(3, 4, ''), Replacement(8, 11, '')]: [0, 4]
    Note that the length of output would be 1 less than that of input replacement_group.

    Arg:
        replacement_group (ReplacementGroup)

    Return:
        dist (ints)
    '''
    n_replacement = len(replacement_group)
    dists = [0] * (n_replacement - 1)

    for i in range(n_replacement - 1):
        dist = replacement_group[i + 1].start - replacement_group[i].end
        dists[i] = dist

    return dists
