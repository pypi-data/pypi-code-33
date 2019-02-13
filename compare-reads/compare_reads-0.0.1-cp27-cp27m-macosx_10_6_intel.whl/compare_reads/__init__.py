"""Compare Alignment sort order using htslib rules."""
__version__ = '0.0.1'

import pysam

from ._compare_reads import (  # noqa
    _compare_read_names,
    _compare_sort,
    _compare_sort_with_queryname,
)


def compare_sort(a, b):
    """Compare sort order for a or b, where a and b can be pysam.AlignedSegment instances or readname strings."""
    if isinstance(a, pysam.AlignedSegment):
        if isinstance(b, pysam.AlignedSegment):
            return _compare_sort(a, b)
        return _compare_sort_with_queryname(a, b)
    elif isinstance(b, pysam.AlignedSegment):
        return -1 * _compare_sort_with_queryname(b, a)
    else:
        return _compare_read_names(a, b)
