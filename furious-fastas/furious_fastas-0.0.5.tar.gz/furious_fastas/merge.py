from itertools import chain
from Bio import SeqIO


def merge_files(paths, out_path, **kwds):
    """Merge files into one, nicely parsable file.

    This is an equivalent of simple unix concatenation of files.

    Arguments
    =========
    paths : list
        A list of paths with files to merge.
    out_path : str
        A path where to save the outcome.
    """
    paths_it = iter(paths)
    path = next(paths_it)
    copyfile(path, out_path)
    with open(out_path, "a") as target:
        for other_path in paths_it:
            with open(other_path, "r") as source:
                target.write(source.read())


def merge_sequence_files(paths,
                         out_path,
                         input_type="fasta"):
    """Merge """
    """Merge sequence files into one, nicely parsable file."""
    all_sequences = chain.from_iterable(SeqIO.parse(p, input_type) for p in paths)
    SeqIO.write(all_sequences, out_path, input_type)
