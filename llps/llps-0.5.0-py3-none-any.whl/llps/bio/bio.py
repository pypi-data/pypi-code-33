
from subprocess import CalledProcessError
from os.path import abspath

from gimmebio.seqs.sample_management import get_sample_name_and_end
from ..utils import run_cmd, md5_sum


class BioValidationError(Exception):
    """Error thrown when validating a filetype.

    Does not necessarily mean the file is malformed,
    rather represents a potential internal issue.
    """

    pass


def get_lines_in_file(filename, logger, gzipped=False):
    """Return the number of lines in the file.

    Write an error to the logger if the file is not properly gzipped.
    Return 0 if there is an error.
    """
    cmd = 'gunzip -c' if gzipped else 'cat'
    try:
        line_count = run_cmd(f'set -o pipefail &&  {cmd} {filename}| wc -l')
        return int(line_count)
    except CalledProcessError:
        if gzipped:
            logger(f'[ERROR] gzip_issue {filename}')
            return 0
        raise


def process_one_fastx(filename, logger):
    """Return the number of lines in the file."""
    expected_lines = 2
    for ext in ['.fq', '.fastq']:
        if ext in filename:
            expected_lines = 4
    line_count = get_lines_in_file(filename, logger, gzipped=filename[-3:] == '.gz')
    if line_count and line_count % expected_lines != 0:
        logger(f'[ERROR] bad_line_count {line_count} {filename}')
        return 0, None
    md5 = None if not line_count else md5_sum(filename)
    return line_count, md5


def process_fastx_filepair(f1_name, f2_name, logger):
    """Check that both files are well formed and match."""
    sample_name1, end1 = get_sample_name_and_end(f1_name)
    sample_name2, end2 = get_sample_name_and_end(f2_name)
    if (end1, end2) != (1, 2):
        raise BioValidationError('Paired files are not proper ends')
    if sample_name1 != sample_name2:
        raise BioValidationError(f'Sample names {sample_name1} and {sample_name2} do not match.')
    l1, md51 = process_one_fastx(f1_name, logger)
    l2, md52 = process_one_fastx(f2_name, logger)
    if l1 != l2:
        logger(f'[ERROR] mismatched_line_count {l1} {l2} {f1_name} {f2_name}')
        return 0, None, None
    return l1, md51, md52


def add_named_fastx_to_schema(schema, filepaths, logger, build_schema):
    grouped = {}
    for filepath in filepaths:
        sample_name, end = get_sample_name_and_end(filepath)
        grouped[sample_name] = grouped.get(sample_name, {})
        grouped[sample_name][end] = filepath

    for sample_name, group in grouped.items():
        unpaired = group.get(0, None)
        if unpaired:
            line_count, md5 = process_one_fastx(unpaired, logger)
            if line_count:
                schema.add_file(
                    build_schema(unpaired, md5, line_count, sample_name=sample_name)
                )
        r1, r2 = group.get(1, None), group.get(2, None)
        if r1 and r2:
            line_count, md51, md52 = process_fastx_filepair(r1, r2, logger)
            if line_count:
                schema.add_file(
                    build_schema(r1, md51, line_count, sample_name=sample_name),
                )
                schema.add_file(
                    build_schema(r2, md52, line_count, sample_name=sample_name),
                )
        elif r1 or r2:
            logger(f'[ERROR] unpaired fastq {sample_name}')
    return schema


def add_unnamed_fastx_to_schema(schema, filepaths, logger, build_schema):
    for unpaired in filepaths:
        line_count, md5 = process_one_fastx(unpaired, logger)
        if line_count:
            schema.add_file(build_schema(unpaired, md5, line_count))
    return schema
