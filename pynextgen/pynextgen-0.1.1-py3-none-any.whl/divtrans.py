"""
=================================
Divergent Transcription Detection
=================================

Detection of divergent transcription events from paired and
stranded RNA-seq datasets


"""

import os
import subprocess
import pysam
import fileinput
import pandas as pd

from pynextgen.logging_config import get_logger
import pynextgen.basics_bam as bb
import pynextgen.bed as bl
from pynextgen.utils import simplify_outpath, exec_command

logger = get_logger("", __name__, "info")


class Oread(object):
    """ An oriented read object
    """

    def __init__(self, ali_read):
        """get orientation of unspliced reads from a pysam alignment. Valid
        only for stranded rf librairies

        """

        blocks = ali_read.get_blocks()
        self.chro = ali_read.reference_name
        self.start = blocks[0][0]
        self.end = blocks[0][-1]

        if self.start > self.end:
            raise (IOError(f"Check block definition for read {self}"))

        if (ali_read.is_read1 and ali_read.is_reverse) or (
            ali_read.is_read2 and not ali_read.is_reverse
        ):
            self.strand = "+"

        elif (ali_read.is_read1 and not ali_read.is_reverse) or (
            ali_read.is_read2 and ali_read.is_reverse
        ):
            self.strand = "-"

        else:
            raise (IOError("Check loop !"))

    def __repr__(self):
        return "<Oread object: {chro}:{start}-{end} ({ori})>".format(
            chro=self.chro, start=self.start, end=self.end, ori=self.strand
        )


class Fragment(object):
    """A definition of a sequence fragment for paired reads: the interval
    between the left-most aligned position and right-most aligned
    position on the genome (ie read1 + space between the 2 reads +
    read2)

    """

    def __init__(self, ali_read, lib_type="rf"):
        """ Define fragment and set its strand
        """

        self.chro = ali_read.reference_name

        if ali_read.is_reverse:
            self.end = ali_read.reference_end
            self.start = self.end + ali_read.template_length

        else:
            self.start = ali_read.reference_start
            self.end = self.start + ali_read.template_length

        if lib_type == "rf":
            self.strand = (
                "+"
                if (
                    (ali_read.is_read1 and ali_read.is_reverse)
                    or (ali_read.is_read2 and not ali_read.is_reverse)
                )
                else "-"
            )

    def __repr__(self):
        return f"Fragment: {self.chro}: {self.start}-{self.end} {self.strand}"


def get_oriented_reads(bam, segment_type, max_template_length):
    """To investigate the orientation of the transcription accross an alignment.
    """
    count = 0
    multi_blocks_reads = 0
    large_templates = 0

    with pysam.AlignmentFile(bam) as bam:
        for read in bam:

            count += 1
            if count % 10_000_000 == 0:
                logger.debug(f"{count:,} reads treated")

            if read.is_secondary:
                continue

            if abs(read.template_length) > max_template_length:
                large_templates += 1
                continue

            # Remove the reads with gaps/splicing (ie reads with multiple pysam blocks)
            if len(read.blocks) == 1:
                # In case Fragments are used, only consider the read
                # of the pair which is appearing first in the sorted
                # bam (otherwise this will create fragments for both
                # and disturb the coordinates order needed for
                # divtrans detection)
                if not (segment_type == Fragment and read.is_reverse):
                    yield segment_type(read)

            else:
                multi_blocks_reads += 1

    logger.info(
        f"Bam: {bam}; Total reads: {count:,}; Too large templates removed: {large_templates}; Spliced reads removed: {multi_blocks_reads:,}"
    )


def identify_divergent_transcription(segment_gen, distance, no_overlap):
    """Identify sites of divergent transcription from RNA-seq reads generator.

    :param oread_gen: A Oread objects generator, from ``get_oriented_reads``

    :param distance: Specifies the maximum distance between divergent reads to consider \
    a divergent transcription event

    :param no_overlap: Divergent transcription should be considered ONLY if reads are not overlapping.

    :return: Tupple generator which can be easily transformed in a Bed file. \
    Tupple: (chro, start, end, score=0, strand='.')
    """

    upstream_segment = next(segment_gen)
    div_id = 0
    counts = {"-": [], "+": []}

    for downstream_segment in segment_gen:

        if upstream_segment.strand != "-":
            counts["+"] += [upstream_segment]
            # logger.info("bla")
            pass

        elif (downstream_segment.start - upstream_segment.end <= distance) and (
            downstream_segment.strand == "+"
        ):

            # Check if divergent reads are overlapping (ie distance < 0)
            # Not pass but continue (for it to keep the same upstream segment)
            if no_overlap and (downstream_segment.start - upstream_segment.end < 0):
                continue

            elif downstream_segment.chro == upstream_segment.chro:

                logger.debug(
                    f"DIV found for reads {upstream_segment} and {downstream_segment} with distance: {downstream_segment.start - upstream_segment.end}"
                )

                div_id += 1

                yield (
                    upstream_segment.chro,
                    min(upstream_segment.end, downstream_segment.start),
                    max(upstream_segment.end, downstream_segment.start),
                    f"div_event_{div_id}",
                    "0",
                    ".",
                )

        upstream_segment = downstream_segment


def filter_by_counts(
    bed_obj, bam, chro_sizes, flank=100, count_thres=10, count_ratio_thres=5, threads=1
):
    """Filter a bed of divergent transcription events based on the '-'
    Counts upstream and the '+' Counts downstream of each detected event.

    :param bed_obj: Bed object from pynextgen.bed of the divergent transcription events.

    :param bam: path to bam file to count from.

    :param chro_sizes: path to chromosome sizes file for bedtools flank.

    :param flank: The number of bases to look for counts upstream and downstream.

    :param count_thres: The minimum counts which has to be observed upstream and downstream of divergent transcription events.

    :param counts_ratio_thres: The minimum ratio for both transcription ratios: -/+ upstream and +/- downstream.

    :param threads: Number of threads to use

    :return: Bed object from ``pynextgen.bed`` with filtered divergent transcription events.

    .. warning:: Paired reads and strandness -s 2 for counts is assumed ! \

    .. todo:: **IMPROVEMENTS:** Create separate function for feature counting. Also filter_by_coverage is a more advanced function: should use it as model for further improvements of filter_by_counts.

    """

    # Generate upstream - and downstream + bed intervals
    minus_left_divtrans = bed_obj.flank(flank, 0, chro_sizes, outfolder="tmp_beds")
    plus_right_divtrans = bed_obj.flank(0, flank, chro_sizes, outfolder="tmp_beds")

    with fileinput.FileInput(minus_left_divtrans.path, inplace=True) as f:
        for line in f:
            print(line.replace(".", "-"), end="")

    with fileinput.FileInput(plus_right_divtrans.path, inplace=True) as f:
        for line in f:
            print(line.replace(".", "+"), end="")

    # Quantify reads for upstream interval
    counts_upstream = bb.count_over_intervals(
        bam, minus_left_divtrans.path, threads=threads
    )
    counts_upstream.rename(
        columns={"forward": "forward_upstream", "reverse": "reverse_upstream"},
        inplace=True,
    )
    counts_downstream = bb.count_over_intervals(
        bam, plus_right_divtrans.path, threads=threads
    )
    counts_downstream.rename(
        columns={"forward": "forward_downstream", "reverse": "reverse_downstream"},
        inplace=True,
    )

    # Join counts to calculate strand transcription ratio
    # Concatenation is based on the 'id' column set in bb.count_over_intervals

    logger.info("Gathering stranded counts data ...")

    df_counts = pd.concat(
        [
            counts_upstream.loc[:, ["forward_upstream", "reverse_upstream"]],
            counts_downstream.loc[:, ["forward_downstream", "reverse_downstream"]],
        ],
        axis=1,
        names=["test1", "test2"],
    )

    df_counts.loc[:, "counts_ratio_upstream"] = (
        df_counts.reverse_upstream / df_counts.forward_upstream
    )
    df_counts.loc[:, "counts_ratio_downstream"] = (
        df_counts.forward_downstream / df_counts.reverse_downstream
    )

    logger.info("Filtering intervals based on read coverage ...")
    df_counts = df_counts.loc[
        (df_counts.counts_ratio_upstream > count_ratio_thres)
        & (df_counts.counts_ratio_downstream > count_ratio_thres)
        & (df_counts.reverse_upstream > count_thres)
        & (df_counts.forward_downstream > count_thres)
    ]

    div_trans_interval_selection = df_counts.index

    sel_bed = bed_obj.to_df()
    sel_bed = sel_bed.loc[sel_bed.iloc[:, 3].isin(div_trans_interval_selection)]

    bed_out_path = simplify_outpath(
        bed_obj.path, suffix="_counts_filtered.bed", keep_path=True
    )
    sel_bed = bl.df_to_bed(sel_bed, bed_out_path)

    logger.info(f"Filtering for {bed_obj} DONE.")

    return sel_bed


def get_bam_coverage(bam, threads=1):
    """ Get the bamCoverage with deeptools as needed for 'filter_by_coverage'

    :param bam: Path to the bam to compute coverage from
    :param threads: Number of threads to use.
    """

    coverage_beds = {}

    for strand in ("forward", "reverse"):

        out_bed = os.path.splitext(bam)[0] + "_" + strand + ".bed"
        cmd = f"bamCoverage -b {bam} -o {out_bed} --minMappingQuality 255 -p {threads} --filterRNAstrand {strand} -of bedgraph"

        if os.path.isfile(out_bed):
            logger.info(f"Using already available bed file: {out_bed}")
        else:
            exec_command(cmd)

        coverage_beds[strand] = bl.Bed(out_bed)

    return coverage_beds


def get_interval_coverage(bam):
    pass


def filter_by_coverage(
    divtrans_bed_obj,
    bam,
    chro_sizes,
    slop=100,
    cov_thres=10,
    cov_ratio_thres=5,
    threads=1,
):
    """Filter a bed of divergent transcription events based on the '-'
    coverage upstream and the '+' coverage downstream of each detected event.

    :param divtrans_bed_obj: Bed object from pynextgen.bed of the divergent transcription events.
    :param bam: Bam file to get coverage from
    :param chro_sizes: path to chromosome sizes file for bedtools slop
    :param slop: The number of bases to look for covs upstream and downstream using bedtools slop.
    :param cov_thres: The minimum coverage which has to be observed upstream and downstream of divergent transcription events
    :param covs_ratio_thres: The minimum ratio for both coverage ratios: -/+ upstream and +/- downstream
    :param threads: The number of threads to use for deeptools BamCoverage

    :return: tuple of a Bed object from ``pynextgen.bed`` with filtered divergent transcription events and the unfiltered coverage table.

    .. warning:: Strandness rf is assumed by Deeptools !

    .. todo:: Implement BamCoverage (with threads) here in (maybe
    using directly intervals information, the problem with deeptools
    API is I don't know how to properly use CountReadsPerBin for
    stranded coverage counts with paired data: ie. the only selection
    available is on SAM flags...)

    """

    base_path = os.path.splitext(divtrans_bed_obj.path)[0]
    bed_out_path = f"{base_path}_coverage_filtered.bed"
    df_coverage_path = f"{base_path}_coverage.csv"

    upstream_divtrans = divtrans_bed_obj.slop(slop, 0, chro_sizes).to_df()
    upstream_divtrans.iloc[:, 5] = "+"
    upstream_divtrans = bl.df_to_bed(upstream_divtrans, f"{base_path}_upstream.bed")

    downstream_divtrans = divtrans_bed_obj.slop(0, slop, chro_sizes).to_df()
    downstream_divtrans.iloc[:, 5] = "+"
    downstream_divtrans = bl.df_to_bed(
        downstream_divtrans, f"{base_path}_downstream.bed"
    )

    logger.info(f"Calculate coverage for bam: {bam}")
    # get_coverage(upstream_divtrans, bam)

    # downstream_coverage["ratio"] = (
    #     downstream_coverage["base_coverage_forward"]
    #     / downstream_coverage["base_coverage_reverse"]
    # )

    # downstream_coverage = downstream_coverage.add_suffix("_downstream")
    # ################################################################################
    # logger.debug("Concatenating coverage tables")

    # df_coverage = pd.concat([upstream_coverage, downstream_coverage], axis=1, sort=True)

    # # Attempt to extract divergent transcriptio signal from the
    # # background within gene bodies
    # # Calculate ratio + downstream / + upstream and - upstream / - downstream

    # df_coverage["forward_noise_ratio"] = (
    #     df_coverage["counts_forward_downstream"]
    #     / df_coverage["counts_forward_upstream"]
    # )
    # df_coverage["reverse_noise_ratio"] = (
    #     df_coverage["counts_reverse_upstream"]
    #     / df_coverage["counts_reverse_downstream"]
    # )

    # df_coverage.to_csv(df_coverage_path)

    # logger.info("Filtering intervals based on read coverage ...")
    # df_coverage_filtered = df_coverage.loc[
    #     (df_coverage.ratio_upstream > cov_ratio_thres)
    #     & (df_coverage.ratio_downstream > cov_ratio_thres)
    #     & (df_coverage.base_coverage_reverse_upstream > cov_thres)
    #     & (df_coverage.base_coverage_forward_downstream > cov_thres)
    # ]

    # div_trans_interval_selection = df_coverage_filtered.index

    # sel_bed = divtrans_bed_obj.to_df()
    # sel_bed.reset_index(inplace=True)
    # sel_bed = sel_bed.loc[sel_bed.iloc[:, 3].isin(div_trans_interval_selection)]

    # bed_out_path = os.path.splitext(divtrans_bed_obj.path)[0] + "_coverage_filtered.bed"
    # sel_bed = bl.df_to_bed(sel_bed, bed_out_path)

    # logger.info(f"Filtering for {divtrans_bed_obj} DONE.")

    # return (sel_bed, df_coverage)


def get_coverages(slop_divtrans_bed_obj, forward_cov_bed_obj, reverse_cov_bed_obj):
    """Calculate the average per base coverage for a slop region of
    divergent transcription intervals from deeptools coverage beds
    """

    coverages = []

    for suffix, cov_bed in zip(
        ("forward", "reverse"), (forward_cov_bed_obj, reverse_cov_bed_obj)
    ):

        df = (
            slop_divtrans_bed_obj.intersect(cov_bed, supp_args="-wb")
            .to_df()
            .drop(range(4, 9), axis=1)
        )

        df.rename(
            columns={
                0: "chro_divtrans",
                1: "start_divtrans",
                2: "end_divtrans",
                3: "divtrans_event",
                9: f"counts_{suffix}",
            },
            inplace=True,
        )

        df[f"base_coverage_{suffix}"] = df[f"counts_{suffix}"] / (
            df.end_divtrans - df.start_divtrans
        )

        df.drop(
            ["chro_divtrans", "start_divtrans", "end_divtrans"], axis=1, inplace=True
        )

        print(df)
        df = df.groupby("divtrans_event").mean()

        coverages.append(df)
        logger.debug(f"Coverage calculated for {suffix}  ")

        print(df)
    return pd.concat(coverages, axis=1)


def get_divergent_transcription_beds(
    bam,
    distance=100,
    max_template_length=500,
    no_overlap=True,
    remove_GL_contigs=True,
    reuse=True,
    segment="fragment",
):
    """Create orientated read objects, detect divergent transcription
    events with them and create a bed file of these divergent
    transcription events

    :param bam: Bam file to detect divergent transcription from.
    :param distance: The maximum distance between two divergent reads to take into account a divergent transcription event
    :param no_overlap: Divergent transcription should be considered ONLY if read are not overlapping.
    :param remove_GL_contigs: Boolean. Include or not the 'GL_contigs' found sometimes in assemblies.
    :param reuse: if reusing or not a divtrans bed file if already existing.
    """

    segment_gen = get_oriented_reads(
        bam,
        Fragment if segment == "fragment" else Oread,
        max_template_length=max_template_length,
    )

    bed_out = simplify_outpath(
        bam, suffix="_divtrans.bed", keep_path=True, check_exist=False
    )

    if os.path.isfile(bed_out) and reuse:
        logger.info(f"Using already available bed file: {bed_out}")

    else:
        with open(bed_out, "w") as f:
            for interval in identify_divergent_transcription(
                segment_gen, distance=distance, no_overlap=no_overlap
            ):
                # Remove unlocated GL contigs:
                if remove_GL_contigs:
                    if not interval[0].startswith("GL"):
                        f.write("\t".join([str(x) for x in interval]) + "\n")
                else:
                    f.write("\t".join([str(x) for x in interval]) + "\n")

    return bl.Bed(bed_out)


class DivTransFromBed(object):
    """Object to store methods for divergent transcription detection
    dealing with paired reads with bedtools fragments """

    def __init__(self, bam, name_sorted=False):
        """
        :param bam: A name sorted bam file
        :param name_sorted: If the bam files are already name sorted.
        """
        self.bam = bam
        self.name_sorted = name_sorted

    def __repr__(self):
        return (
            f"Divergent transcription analysis object for: {simplify_outpath(self.bam)}"
        )

    def sort_by_name(self):
        """ Sort the bam file by read name 
        """

        logger.debug("START: Sorting by names")
        sorted_bam = simplify_outpath(self.bam, suffix="_nameSort.bam", keep_path=True)
        cmd = f"samtools sort -n -o {sorted_bam} {self.bam}"

        exec_command(cmd)

        self.bam = sorted_bam

    def filter(self):
        """ Filters bam file based on mapping, mapping of mate, splicing
        """

        logger.debug("START: Filtering bams")
        self.filt_bam = os.path.splitext(self.bam)[0] + "_filt.bam"

        # Filtering bam, removing unmapped, mate unmapped, spliced, secondary mapping
        cmd = "samtools view -h -F 0x4 -F 0x8 -F 0x100 {0} | awk '{{if ($1 ~ /^@/) {{print}} else if ($6 !~ /N/) {{print}}}}' | samtools view -bh > {1}".format(
            self.bam, self.filt_bam
        )

        subprocess.check_output(cmd, shell=True)
        logger.debug("DONE: {}".format(cmd))

        return self

    def to_bedpe(self):
        """From mapped reads in a bam, get bed intervals of the pairs joined
        into fragments
        """

        logger.debug("START: Generate bedpe")
        self.bedpe = os.path.splitext(self.bam)[0] + "_frag.bed"
        # Converting to fragments and bed format
        cmd = "bedtools bamtobed -bedpe -mate1 -i {0} > {1} 2> bedpe.log" "".format(
            self.filt_bam, self.bedpe
        )

        subprocess.check_output(cmd, shell=True)
        logger.debug("DONE: {}".format(cmd))

        return self

    def to_fragments(self, max_insert_size=500):

        logger.debug("START: Generate fragments bed")

        diff_chroms_count = 0
        frag_lengths = []

        bed_out = os.path.splitext(self.bedpe)[0] + "_clean.bed"

        frag_filt_n = 0

        with open(bed_out, "w") as f:
            with open(self.bedpe, "r") as bedin:
                for l in bedin:
                    # Check if different chromosomes
                    if l.split()[0] != l.split()[3]:
                        diff_chroms_count += 1
                        continue

                    coords = [int(l.split()[i]) for i in [1, 2, 4, 5]]
                    start = min(coords)
                    stop = max(coords)

                    frag_l = stop - start
                    frag_lengths.append(frag_l)

                    # This is setting the correct strand (strand of the second of pair)
                    if frag_l <= max_insert_size:
                        f.write(
                            "{0}\t{1}\t{2}\t{3}\t.\t{4}\n".format(
                                l.split()[0], start, stop, l.split()[6], l.split()[9]
                            )
                        )
                    else:
                        frag_filt_n += 1

        logger.info(
            "Number of pairs mapping on different chromosomes: {}".format(
                diff_chroms_count
            )
        )
        logger.info(
            "Min frag_length: {0}; Max frag_length: {1};".format(
                min(frag_lengths), max(frag_lengths)
            )
        )
        logger.info(
            "Number of fragments filtered out because insert size > {0}b: {1}".format(
                max_insert_size, frag_filt_n
            )
        )

        self.fragbed = bl.Bed(bed_out)
        return self

    def merge(self):
        """ Merge bed fragments keeping the strand info
        """

        logger.debug("START: Merging bed")

        # -c 6 -o distinct is to keep the strand info
        self.mergedbed = self.fragbed.sort().merge(
            supp_args="-s -c 4,5,6 -o min,distinct,distinct"
        )

        return self

    def get_div_reads(self):
        """ Get couples of closest reads on opposite strands"""

        df = self.mergedbed.to_df()

        # Separate + and - strands
        pos_strand_df = df[df[5] == "+"]
        neg_strand_df = df[df[5] == "-"]

        pos_bed = bl.df_to_bed(pos_strand_df, self.mergedbed.path + "_plus.bed")
        neg_bed = bl.df_to_bed(neg_strand_df, self.mergedbed.path + "_minus.bed")

        # The divergent read should always be looked upstream considering
        # the orientation of bedA (see bedtools closest manual)
        bed1 = pos_bed.closest(neg_bed, supp_args="-D a -id")
        bed2 = neg_bed.closest(pos_bed, supp_args="-D a -id")
        closest_bed = bed1.concat(bed2).move_to(
            self.mergedbed.path + "_closest_concat.bed"
        )

        # Ignore overlaping reads to look for reads further away
        # Treat special cases where overlapping hide divergent transcription (test with test/frag.bed)
        # This will overwrite the previous beds so need to be concat sequentially
        bed3 = pos_bed.closest(neg_bed, supp_args="-D a -id -io")
        closest_bed = closest_bed.concat(bed3).move_to(
            self.mergedbed.path + "_closest_concat.bed"
        )

        bed4 = neg_bed.closest(pos_bed, supp_args="-D a -id -io")
        closest_bed = closest_bed.concat(bed4).move_to(
            self.mergedbed.path + "_closest_concat.bed"
        )

        self.closest_bed = closest_bed

        return self

    def get_div_read_intervals(self, row, internal=True):
        """ Defines the bed intervals of divergent transcription event
        Either defined as the interval separating divergetn reads (internal=True)
        Or as the min and max of divergent reads coordinates (internal=False)"""

        chro = row.iloc[0]
        coords = sorted(row.iloc[[1, 2, 7, 8]])
        if internal:
            return [chro, coords[1], coords[2], ".", ".", "."]
        else:
            return [chro, min(coords), max(coords), ".", ".", "."]

    def cleanup_intervals(self):
        """ Process fragments beds to extract divergent transcription intervals"""

        logger.debug("START: Divergent intervals detection and cleaning")

        def filter_convergence(row):
            """ Keep only divergent transcription (no convergent)
            """
            # 2 cases for divergent transcription (hence removing convergente transcription)
            if row.iloc[1] <= row.iloc[7] and row.iloc[5] == "-":
                return True
            elif row.iloc[1] >= row.iloc[7] and row.iloc[5] == "+":
                return True
            else:
                return False

        df = self.closest_bed.to_df()

        # Filtering convergence (still detected when reads are overlapping)
        df = df.loc[df.apply(filter_convergence, axis=1)]

        # Filter by event size
        df = df[(abs(df[12]) <= 500)]

        # remove GL contigs
        df = df[[not str(x).startswith("GL") for x in df.iloc[:, 0]]]

        # For cases where no close reads can be found, bedtools add -1 as coordinates
        # This filters this case out
        sel = (
            (df.iloc[:, 1] != -1)
            & (df.iloc[:, 2] != -1)
            & (df.iloc[:, 7] != -1)
            & (df.iloc[:, 8] != -1)
        )
        df = df.loc[sel, :]

        out_prefix = os.path.splitext(self.mergedbed.path)[0]

        df = pd.DataFrame(list(df.apply(self.get_div_read_intervals, axis=1)))

        div_read_intervals = bl.df_to_bed(df, out_prefix + "_div_read.bed")

        # Clustering instead of merging was necessary to get the interval between divergent reads
        # cluster_div_reads = div_read_intervals.sort().cluster()
        # get_div_trans_intervals(cluster_div_reads.path, out_prefix + 'div_trans_final.bed')

        self.divtrans_bed = div_read_intervals.sort().merge()

        return self

    def run(self):
        """ Filter the bam and produce a bed of fragments"""
        if not self.name_sorted:
            self.sort_by_name()
        # Remove read unmapped, mate unmapped, only primary, no spliced
        self.filter()
        # Generate fragments from read pairs and orient them properly
        self.to_bedpe()
        self.to_fragments()
        self.merge()
        self.get_div_reads()
        self.cleanup_intervals()

        return self
