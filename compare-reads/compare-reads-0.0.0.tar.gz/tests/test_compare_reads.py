"""Test compare_sort function."""
import os

import pysam
import pytest

from compare_reads import (
    _compare_read_names,
    _compare_sort,
    _compare_sort_with_queryname,
    compare_sort,
)

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_files',
)


@pytest.mark.datafiles(os.path.join(FIXTURE_DIR, 'softclip.bam'))
def test_compare_sort(datafiles):  # noqa: D103
    path = os.path.join(str(datafiles), 'softclip.bam')  # why ?
    with pysam.AlignmentFile(path) as af:
        reads = [r for r in af]
    assert _compare_sort(reads[0], reads[1]) == -1
    assert _compare_sort(reads[1], reads[2]) == -1
    assert _compare_sort(reads[2], reads[2]) == 0
    assert _compare_sort(reads[2], reads[1]) == 1
    assert _compare_sort(reads[1], reads[0]) == 1
    assert _compare_sort(reads[0], reads[0]) == 0
    assert _compare_sort_with_queryname(reads[0], 'read_100') < 0
    assert _compare_read_names('read1', 'read2') == -1
    assert _compare_read_names('read2', 'read2') == 0
    assert _compare_read_names('read2', 'read1') == 1
    # Test higher level python wrapper that figures out argument type
    assert compare_sort(reads[0], reads[1]) == -1
    assert compare_sort(reads[0], 'read_100') < 0
    assert compare_sort('read_100', reads[0]) > 0
    assert compare_sort('read2', 'read1') == 1
