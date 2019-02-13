import argparse
from collections import Counter
from pynextgen.logging_config import get_logger
import pysam
from multiprocessing import Pool
from functools import partial
from pynextgen.utils import simplify_outpath, exec_command
import os
from pynextgen.bed import Bed
import pandas as pd
import itertools


logger = get_logger(__file__, __name__)

# IN DVPT

# get_read_by_id is HIGHLY SUBOPTIMAL (found some index methods in
# pysam but did not manage to make it work to accelerate the acces to
# read by names)


def count(bam_file, interval):
    """Perform RNA-seq data count over a region.

    .. warning:: So far ONLY WORKING for use for DIVTRANS PROJECT. Also, this is only counting 2nd of the pair.
    """

    reverse = 0
    forward = 0

    alignment = pysam.AlignmentFile(bam_file)

    for read in alignment.fetch(interval.chro, interval.start, interval.end):
        # Assume library in strand specific rf
        if read.is_read2:
            if read.is_reverse:
                reverse += 1
            else:
                forward += 1

    return (
        interval.name,
        interval.chro,
        interval.start,
        interval.end,
        forward,
        reverse,
    )


def count_over_intervals(bam_file, bed_file, threads=1):
    """Perform RNA-seq data counts over all intervals of a bed file.

    .. warning:: So far ONLY WORKING for use for DIVTRANS PROJECT. Also, this is only counting 2nd of the pair.
        """

    bed = Bed(bed_file)
    results = []

    logger.info("Starting count on intervals")

    p = Pool(threads)

    f = partial(count, bam_file)

    results = p.map(f, [x for x in bed.get_intervals()])

    # for counter, interval in enumerate(bed.get_intervals()):

    #     results.append(self.count(interval))

    # if counter % 10000 == 0:
    #     logger.info(f'{counter} intervals done !')

    return pd.DataFrame(
        results, columns=["id", "chro", "start", "end", "forward", "reverse"]
    ).set_index(["id"])


class Bam(object):
    """A object representation of a bam compressed alignment file
    """

    def __init__(self, path):
        self.path = path
        self.alignment = pysam.AlignmentFile(path)

    def __repr__(self):
        return f"BAM Object for file: {self.path}"

    def sort(self):
        """ Sort a bam file 
        """
        sorted_bam_path = f"{os.path.splitext(self.path)[0]}_S.bam"
        exec_command(f"samtools sort {self.path} -o {sorted_bam_path}")

        return Bam(sorted_bam_path)

    def index(self):
        """Generate the sam index
        """
        exec_command(f"samtools index {self.path}")

        return self

    def multi_fetch(self, interval_list, bam_out=""):
        """Extract a list of intervals from a bam and write them to a bam file

        :param interval_list: list of genomic regions to extract ie: [1:912436-960073, 1:14,642,898-14,652,296]
        :param bam_out: path to the bam to write selection to.
        :returns: A Bam object
        :rtype: Bam object
        """

        if not bam_out:
            bam_out = simplify_outpath(self.path, suffix="_fetched.bam", keep_path=True)

        with pysam.AlignmentFile(bam_out, "wb", template=self.alignment) as b:

            for interval in interval_list:
                chro = interval.split(":")[0]
                start, end = [
                    int(x) for x in interval.split(":")[1].replace(",", "").split("-")
                ]
                logger.debug(f"Extracting interval: {chro}:{start}-{end} from {self}")

                for read in self.alignment.fetch(chro, start, end):
                    b.write(read)

        return Bam(bam_out)

    def block_order_check(self):
        """Verify that pysam blocks are ordered by coordinates
        (The documentation of pysam is not yet explicit on this point)
        """

        for segment in self.alignment:
            blocks = segment.get_blocks()
            coords = list(itertools.chain.from_iterable(blocks))
            if coords != sorted(coords):
                raise IOError("Apparently the pysam blocks are not coordinated sorted")


def generate_pair(
    start,
    strand,
    read_name,
    read_cigars=("100M", "100M"),
    fragment_length=300,
    read_length=100,
):
    """ Generate a read pair consumed by generate_bam

    For now generate stranded, paired reads and fixed N sequences

    :param start: list of fragment alignment starts.
    :param strand: list of fragment alignment strands.
    :param fragment_length: length to use to define the fragments in bases.
    :param read_length: length of the reads in bases.

    For now, reference is set to '1'
    """

    read1 = pysam.AlignedSegment()
    read2 = pysam.AlignedSegment()

    # TO correct the infered start position of the downstream read
    # (depending on template length and splicing event lengths)
    read1.cigarstring, read2.cigarstring = read_cigars

    n_spliced_read1 = sum([nbases for cigar, nbases in read1.cigartuples if cigar == 3])
    n_spliced_read2 = sum([nbases for cigar, nbases in read2.cigartuples if cigar == 3])

    if strand == "+":
        # Set SAM flags
        strand = (99, 147)
        read1_start = start
        read2_start = start + fragment_length - n_spliced_read2 - read_length
        read1_tlen, read2_tlen = fragment_length, -fragment_length

    elif strand == "-":
        strand = (83, 163)
        read2_start = start
        read1_start = start + fragment_length - n_spliced_read1 - read_length
        read1_tlen, read2_tlen = -fragment_length, fragment_length

    read1.query_name = read2.query_name = f"read_{read_name}"
    read1.query_sequence = read2.query_sequence = "N" * read_length
    read1.flag, read2.flag = strand
    read1.reference_id = read2.reference_id = 0
    read1.reference_start, read2.reference_start = (read1_start, read2_start)
    read1.mapping_quality = read2.mapping_quality = 255
    read1.next_reference_id = read2.next_reference_id = 0
    read1.next_reference_start, read2.next_reference_start = (read2_start, read1_start)
    read1.query_qualities = read2.query_qualities = pysam.qualitystring_to_array(
        "<" * 100
    )

    read1.template_length, read2.template_length = read1_tlen, read2_tlen

    return (read1, read2)


def generate_bam(bam_out, bam_template, read_tsv):
    """Generate bam files for testing purposes

    For now generate stranded, paired reads

    :param bam_out: Path to the BAM file to generate.
    :param bam_template: Path to the BAM file to use as template.
    :param read_tsv: Path to a tab separated file with start, end,
    ref, and cigar information to create the reads from.

    """
    reads_df = pd.read_csv(read_tsv, sep="\t")

    with pysam.AlignmentFile(
        bam_out, "wb", template=pysam.AlignmentFile(bam_template, check_sq=False)
    ) as bam:

        for index, row in reads_df.iterrows():

            read1, read2 = generate_pair(
                row["starts"],
                row["strands"],
                index,
                read_cigars=row["cigars"].split(","),
                fragment_length=row["fragment_length"],
            )
            bam.write(read1)
            bam.write(read2)

    bam = Bam(bam_out).sort().index()
    return bam


################################################################################
# LEGACY
################################################################################


def open_bam(bam):
    with pysam.AlignmentFile(bam, "rb") as f:
        for i, read in enumerate(f):
            if i % 1_000_000 == 0:
                logger.info("Reached {} reads.".format(i))
            yield read


def get_polyNs_read(bam, poly_len, poly_char):
    """ Get reads with a polyN tail
    """

    for read in open_bam(bam):
        if read.seq.endswith(poly_char * poly_len):
            yield read


def get_read_by_id(id_list, bam):
    """
    Get the alignement from a bam file given an read id_list
    """

    for read in open_bam(bam):
        if read.query_name in id_list:
            yield read


def count_mapped_bases(bam):
    """
    Describe the proportion of each bases in a single read in primary
    alignments (we are trying here to segregate between polyAs and
    genomes As so need to remove the clipped part of the alignments
    before computing nucleotide proportions in reads)
    """

    for read in open_bam(bam):
        if not read.is_secondary:
            count = Counter(read.query_alignment_sequence)
            yield (count)


def overall_mapped_bases_composition(bam):

    all_counts = {"A": 0, "T": 0, "G": 0, "C": 0}

    for count in count_mapped_bases(bam):
        for k in all_counts:
            all_counts[k] += count[k]

    all_counts = {k: all_counts[k] / sum(all_counts.values()) for k in all_counts}

    for k, v in all_counts.items():
        logger.info("{0}: {1}".format(k, v))


# BROCKEN FOR NOW:
# Last checked, pysamstats was giving an error at import


def write_region_coverage(interval, bam, flank):
    """
    From a bam file, get the coverage for each bases in an interval
    (as in pyBedtools interval ie with interval.chrom, interval.start,
    interval.end)
    """

    sam = pysam.AlignmentFile(bam, "rb")
    logger.debug(
        "Interval: {}:{}-{}".format(interval.chrom, interval.start, interval.end)
    )

    with open("coverage_" + simplify_outpath(bam) + "_" + interval.name, "w") as f:
        for base_cov in pysamstats.stat_coverage(
            sam,
            chrom=interval.chrom,
            start=interval.start - flank,
            end=interval.end + flank,
            truncate=True,
            pad=True,
        ):
            f.write("{chrom}\t{pos}\t{reads_all}\t{reads_pp}\n".format(**base_cov))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("bam", help="The path to a bam file")
    parser.add_argument(
        "-b",
        "--base_comp",
        help="Produce composition of the mapped bases",
        action="store_true",
    )

    args = parser.parse_args()

    if args.base_comp:
        overall_mapped_bases_composition(args.bam)
