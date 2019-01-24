"""Test suite for kmer."""

from unittest import TestCase
from os.path import dirname, join

from llps import (
    ProjectSchema,
    InvalidLLPSException,
)
from llps.bio import (
    add_unnamed_fastx_to_schema,
    add_named_fastx_to_schema,
)

CURDIR = dirname(__file__)


def fake_logger(_):
    assert False


def build_schema(path, md5, line_count, sample_name=None):
    out = {
        'path': path,
        'wasabi': {},
        'md5': md5,
        'unzipped_line_count': line_count,
    }
    if sample_name:
        out['sample_name'] = sample_name
    return out


class TestLLPS(TestCase):
    """Test suite for llps."""

    def test_valid_schema(self):
        """Test that we can parse a valid spec without issue."""
        valid_spec_filename = join(CURDIR, 'valid_sample_spec.llps.yaml')
        ProjectSchema.from_file(valid_spec_filename)

    def test_invalid_schema(self):
        """Test that parsing an invalid spec throws an error."""
        invalid_spec_filename = join(CURDIR, 'invalid_sample_spec.llps.yaml')
        with self.assertRaises(InvalidLLPSException):
            ProjectSchema.from_file(invalid_spec_filename)

    def test_add_fasta(self):
        """Test that we can add a single fasta to a schema."""
        valid_spec_filename = join(CURDIR, 'valid_sample_spec.llps.yaml')
        schema = ProjectSchema.from_file(valid_spec_filename)
        add_unnamed_fastx_to_schema(
            schema,
            [join(CURDIR, 'data/ecoli.fa')],
            fake_logger,
            build_schema,
        )

    def test_add_fastq_pair(self):
        """Test that we can add a single fasta to a schema."""
        valid_spec_filename = join(CURDIR, 'valid_sample_spec.llps.yaml')
        schema = ProjectSchema.from_file(valid_spec_filename)
        add_named_fastx_to_schema(
            schema,
            [join(CURDIR, 'data/sample_fq_1.fq.gz'), join(CURDIR, 'data/sample_fq_2.fq.gz')],
            fake_logger,
            build_schema,
        )
