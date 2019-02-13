import os
import re

from io import StringIO
from multiprocessing.dummy import Pool
import subprocess
import pandas as pd
import matplotlib.pyplot as plt

from functools import partial

from pynextgen.basics_fasta import Fasta
from pynextgen.utils import exec_command, simplify_outpath
from pybedtools import BedTool

from pynextgen.logging_config import get_logger


logger = get_logger("", __name__, "debug")

# WHY NOT pybedtools ?
# Did not find a way to easily keep track of originak bed file names
# Difficulty for threading encountered in 2016

# TOFIX
# DANGEROUS behavior: better indeed to use temporary files (or even back to pybedtools) in following case:
# 2 intersect are made sequentially, one with -wa and the other with -v options
# Only a single *intersect* file will be create with the results from the last operations (completely opposite of the actual file needed)

# Improvements:
# Add function 'Pandas dataframe to Bed object'
# TODO Centralize the exec_command / create outfolder / outfile path (DRY) and add f'' string formatting

# Assumptions:
# For Interval class, bedfile should have 3 or 6 fields


def df_to_bed(df, path):
    """ Create a bed object from a pandas dataframe
    """

    df.to_csv(path, sep="\t", header=None, index=False)
    return Bed(path)


def get_chrom_sizes(fasta, outfile=""):
    """ Get the chromosomes sizes from a reference fasta file.
    Mainly to make use of it in bedtools fisher and shuffle
    """

    chro_sizes = Fasta(fasta).stats()["seq_len"]

    if outfile:
        with open(outfile, "w") as f:
            chro_sizes.to_csv(outfile, sep="\t")

    return chro_sizes


class Interval(object):
    """A class for each intervals contained in a bed file
    Bed file should have 6 fields
    """

    def __init__(self, line):
        "Get interval from a bed file line"
        line = line.split()
        self.chro = line[0]
        self.start = int(line[1])
        self.end = int(line[2])

        if len(line) > 3:
            self.name = line[3]
            self.score = int(line[4])
            self.strand = line[5]

    def __repr__(self):
        return "Interval: {0}:{1}-{2}".format(self.chro, self.start, self.end)

    def __len__(self):
        return self.end - self.start


class Bed(object):
    """Bed object
    """

    def __init__(self, path):

        if not os.path.exists(path):
            raise IOError("The bed file {} does not exist".format(path))

        self.path = path
        self.name = os.path.splitext(os.path.basename(path))[0]

    def __len__(self):
        return sum(1 for _ in open(self.path))

    def __repr__(self):
        return f"<Bed object: {self.name}>\n"

    def head(self, nlines=10):
        return self.to_df().head(nlines)

    def move_to(self, newpath):
        """Move the bed file associated
        """
        os.rename(self.path, newpath)
        self.path = newpath
        self.name = os.path.basename(self.path)

        return self

    def to_df(self):
        """ Bed file to pandas dataframe
        """
        return pd.read_csv(self.path, sep="\t", header=None, low_memory=False)

    def to_saf(self, set_strand=""):
        """Save bed file as a saf (for FeatureCounts)

        """

        out_path = os.path.splitext(self.path)[0] + ".saf"

        with open(out_path, "w") as f:

            f.write("GeneID\tChr\tStart\tEnd\tStrand\n")
            for interval in self.get_intervals():
                f.write(
                    f"{interval.name}\t{interval.chro}\t{interval.start}\t{interval.end}\t{interval.strand}\n"
                )

        return out_path

    def to_BedTool(self):
        """ Return a BedTool object from pybedtools
        """

        bed = BedTool(self.path)
        bed.name = self.name

        return bed

    def as_ensembl(self):
        """ Return a bed without the 'chr'
        """

        ensembl_bed = os.path.splitext(self.path)[0] + "_E.bed"

        with open(ensembl_bed, "w") as bed_out:
            with open(self.path, "r") as bed_in:
                for line in bed_in:
                    bed_out.write(re.sub("^chr", "", line))

        return Bed(ensembl_bed)

    def get_intervals(self):
        with open(self.path) as bed:
            for line in bed:
                # Skip the track definition line
                if line.startswith("track"):
                    continue
                else:
                    yield Interval(line)

    def get_length_distribution(self):

        len_distrib = []
        for interval in self.get_intervals():
            len_distrib.append(len(interval))

        return len_distrib

    def total_bases(self):
        nbases = 0
        with open(self.path) as bed:
            for line in bed:
                line = line.split()
                nbases += int(line[2]) - int(line[1])

        return nbases

    def stats(self, full_report=False):
        """
            Produce all stats for a bed file
        """

        stats = {
            "Nbases": f"{self.total_bases():.2e}",
            "Nintervals": f"{len(self): .2e}",
            "path": self.path,
            "name": self.name,
            "bedobj": self,
        }

        if full_report:
            len_distrib = pd.Series(self.get_length_distribution()).describe()
            len_distrib.index = "len_distrib_" + len_distrib.index

            # Merging stat dictionnaries
            stats = {**stats, **len_distrib.to_dict()}

        return stats

    def plot(self, log=False):
        """
        Summarize stats with plots
        """

        len_distrib = self.get_length_distribution()

        pd.DataFrame(len_distrib).plot(kind="hist", bins=100, log=log)
        plt.title("{}: Histogram of interval lengths".format(self.name))
        plt.xlabel("Interval length")
        plt.ylabel("Frequencies")

    def sort(self, outfolder="bed_outfolder"):
        """ Sort bed file
        """
        os.makedirs(outfolder, exist_ok=True)
        sort_path = os.path.join(outfolder, self.name + "_S.bed")

        cmd = "sort -k1,1 -k2,2n {0} > {1}".format(self.path, sort_path)

        exec_command(cmd)

        return Bed(sort_path)

    def merge(self, outfolder="bed_outfolder", supp_args=""):
        """ Merge bed
        """
        os.makedirs(outfolder, exist_ok=True)
        merged_path = os.path.join(outfolder, self.name + "_M.bed")

        cmd = "bedtools merge -i {0} {1} > {2}".format(
            self.path, supp_args, merged_path
        )
        exec_command(cmd)

        return Bed(merged_path)

    def filter_by_distance(self, bedobj, max_distance, outfolder="bed_outfolder"):
        """Select the intervals which are at distance of any feature in bedobj
        smaller than max_distance
        """

        dist_df = self.closest(bedobj, supp_args="-d").to_df()
        distances = dist_df.iloc[:, 6]

        filtered_path = simplify_outpath(
            self.path,
            suffix=f"_filtered_{max_distance}b_max_from_{bedobj.name}.bed",
            keep_path=True,
            check_exist=False,
        )

        # With the -d option, -1 means no closest inteval found
        # So it has to filter out as well
        filtered_bed = df_to_bed(
            dist_df.loc[(distances < max_distance) & (distances >= 0)], filtered_path
        )
        return filtered_bed

    def filter_by_size(self, max_size):
        """Select only the intervals which have a size inferior or equal to
        max_size
        """

        interval_sizes = self.to_df().iloc[:, 2] - self.to_df().iloc[:, 1]

        filtered_path = simplify_outpath(
            self.path,
            suffix=f"_filtered_{max_size}b_max_length.bed",
            keep_path=True,
            check_exist=False,
        )

        filtered_bed = df_to_bed(
            self.to_df().loc[interval_sizes <= max_size], filtered_path
        )

        return filtered_bed

    def concat(self, bedobj, outfolder="bed_outfolder"):
        """Concatenate 2 bed files
        """

        os.makedirs(outfolder, exist_ok=True)
        concat_path = os.path.join(
            outfolder, self.name + "_concat_" + bedobj.name + ".bed"
        )

        cmd = "cat {0} {1} | sort -k1,1 -k2,2n > {2}".format(
            self.path, bedobj.path, concat_path
        )
        subprocess.check_output(cmd, shell=True)

        exec_command(cmd)

        return Bed(concat_path)

    def closest(self, bed_obj, outfolder="bed_outfolder", supp_args=""):
        """ Make default bedtools closest
        """

        os.makedirs(outfolder, exist_ok=True)
        closest_path = os.path.join(
            outfolder, self.name + "-closest-" + bed_obj.name + ".bed"
        )

        cmd = "bedtools closest -a {0} -b {1} {2} > {3}".format(
            self.path, bed_obj.path, supp_args, closest_path
        )
        exec_command(cmd)

        return Bed(closest_path)

    def intersect(self, bed_obj, outfolder="bed_outfolder", supp_args=""):
        """ Make default bedtools intersect of two beds"""

        os.makedirs(outfolder, exist_ok=True)
        inter_path = os.path.join(
            outfolder, self.name + "-inter-" + bed_obj.name + ".bed"
        )
        cmd = "bedtools intersect -a {0} -b {1} {2} | bedtools sort > {3}".format(
            self.path, bed_obj.path, supp_args, inter_path
        )
        exec_command(cmd)

        return Bed(inter_path)

    def subtract(self, bed_obj, outfolder="bed_outfolder", supp_args=""):
        """ Make default bedtools subtract of bed1 - bed2"""

        os.makedirs(outfolder, exist_ok=True)
        subtract_path = os.path.join(
            outfolder, self.name + "-minus-" + bed_obj.name + ".bed"
        )
        cmd = "bedtools subtract -a {0} -b {1} {2} > {3}".format(
            self.path, bed_obj.path, supp_args, subtract_path
        )
        exec_command(cmd)

        return Bed(subtract_path)

    def complement(self, genome_chro_size, outfolder="bed_outfolder", supp_args=""):
        """ Wrapper for bedtools complement
        """

        os.makedirs(outfolder, exist_ok=True)
        complement_path = os.path.join(outfolder, self.name + "-complemented.bed")
        cmd = "bedtools complement {0} -i {1} -g {2} {3} > {4}".format(
            supp_args, self.path, genome_chro_size, supp_args, complement_path
        )
        exec_command(cmd)

        return Bed(complement_path)

    def fisher(self, bed_obj, genome_chro_size, supp_args=""):
        """ Make bedtools fisher test
        """

        cmd = "bedtools fisher -a {0} -b {1} -g {2} {3}".format(
            self.path, bed_obj.path, genome_chro_size, supp_args
        )

        output = subprocess.check_output(cmd, shell=True).decode("utf-8")

        # Extract test values at the end of fisher output
        header = output.split("\n")[-3].split("\t")
        values = output.split("\n")[-2].split("\t")

        res = {k: float(v) for k, v in zip(header, values)}

        res["bed1"] = self.name
        res["bed2"] = bed_obj.name

        if len(res) != 6:
            raise IOError("Not correct fisher output for comparison:\n{}".format(cmd))

        return res

    def multi_shuffle(
        self, nshuffle, genome_chro_size, supp_args="", outfolder="bed_outfolder"
    ):
        """ Bedtools shuffle multiple times
        """
        shuffle_beds = []

        for i in range(nshuffle):
            shuffle_path = os.path.join(
                outfolder, self.name + "-shuffle-" + str(i) + ".bed"
            )
            cmd = "bedtools shuffle -i {0} -g {1} {2} > {3}".format(
                self.path, genome_chro_size, supp_args, shuffle_path
            )

            logger.debug("Running: {}".format(cmd))

            exec_command(cmd)
            shuffle_beds.append(Bed(shuffle_path))

        return shuffle_beds

    def coverage(self, cov, outfolder="bed_outfolder", supp_args=""):
        """Bedtools coverage
        cov is for now either a bed_obj or a path to a bam file
        """

        if isinstance(cov, Bed):
            cov_path = cov.path
            cov_name = cov.name
        elif os.path.exists(cov) and os.path.splitext(cov)[-1] == ".bam":
            cov_path = cov
            cov_name = os.path.basename(cov)
        else:
            raise IOError(
                'Coverage supported format are so far only Bed objects and path to bam files (ie "-b" file)'
            )

        coverage_out_path = os.path.join(
            outfolder, self.name + "-coveredby-" + cov_name + ".bed"
        )
        cmd = "bedtools coverage -a {0} -b {1} {2} > {3}".format(
            self.path, cov_path, supp_args, coverage_out_path
        )
        exec_command(cmd)

        return Bed(coverage_out_path)

    def cluster(self, outfolder="bed_outfolder", supp_args=""):
        """ Bedtools cluster
        """

        os.makedirs(outfolder, exist_ok=True)
        cluster_path = os.path.join(outfolder, self.name + "_clustered" + ".bed")

        cmd = "bedtools cluster -i {0} {1} > {2}".format(
            self.path, supp_args, cluster_path
        )
        exec_command(cmd)

        return Bed(cluster_path)

    def slop(
        self, left, right, genome_chro_size, outfolder="bed_outfolder", supp_args=""
    ):
        """ Bedtools slop, forcing use with -l and -r"""

        os.makedirs(outfolder, exist_ok=True)
        slop_path = os.path.join(
            outfolder, self.name + "_slop_l" + str(left) + "_r" + str(right) + ".bed"
        )

        cmd = "bedtools slop -i {0} -g {1} -l {2} -r {3} {4} > {5}".format(
            self.path, genome_chro_size, left, right, supp_args, slop_path
        )
        exec_command(cmd)

        return Bed(slop_path)

    def shift(self, n_bases, genome_chro_size, outfolder="bed_outfolder", supp_args=""):
        """ Bedtools shift, forcing use of -s"""

        os.makedirs(outfolder, exist_ok=True)
        shift_path = os.path.join(
            outfolder, self.name + "_shift_" + str(n_bases) + ".bed"
        )

        cmd = "bedtools shift -i {0} -g {1} -s {2} {3} > {4}".format(
            self.path, genome_chro_size, n_bases, supp_args, shift_path
        )
        exec_command(cmd)

        return Bed(shift_path)

    def flank(
        self, left, right, genome_chro_size, outfolder="bed_outfolder", supp_args=""
    ):
        """ Bedtools flank, forcing use with -l and -r"""

        os.makedirs(outfolder, exist_ok=True)
        flank_path = os.path.join(
            outfolder, self.name + "_flank_l" + str(left) + "_r" + str(right) + ".bed"
        )

        cmd = "bedtools flank -i {0} -g {1} -l {2} -r {3} {4} > {5}".format(
            self.path, genome_chro_size, left, right, supp_args, flank_path
        )
        exec_command(cmd)

        return Bed(flank_path)

    def jaccard(self, bed_obj, supp_args=""):
        """ Bedtools jaccard
        """

        cmd = "bedtools jaccard -a {0} -b {1} {2}".format(
            self.path, bed_obj.path, supp_args
        )

        output = subprocess.check_output(cmd, shell=True).decode("utf-8")

        jaccard_index = pd.read_csv(StringIO(output), sep="\t")
        jaccard_index["bed1"] = [self.name]
        jaccard_index["bed2"] = [bed_obj.name]

        return jaccard_index

    def window(self, bed_obj, window_size, outfolder="bed_outfolder", supp_args=""):
        """ Bedtools window
        """
        os.makedirs(outfolder, exist_ok=True)

        window_path = os.path.join(
            outfolder,
            self.name + "_window_" + str(window_size) + "_" + bed_obj.name + ".bed",
        )

        cmd = "bedtools window -a {0} -b {1} -w {2} {3} > {4}".format(
            self.path, bed_obj.path, window_size, supp_args, window_path
        )
        exec_command(cmd)

        return Bed(window_path)


def merge_beds(bed_list, prefix, outfolder="bed_outfolder"):
    """ Concatenate, sort and merge a list of beds.

    :param bed_list: A list of Bed objects to merge
    :param prefix: A prefix to use for the output merged file
    :param outfolder: path to the output directory

    """
    merge_path = os.path.join(outfolder, f"{prefix}_merged.bed")

    cmd = f'cat {" ".join(bed_list)} | bedtools sort | bedtools merge > {merge_path}'

    logger.debug(cmd)

    exec_command(cmd)

    return Bed(merge_path)


def merge_bed_list(bed_tuple, outfolder="bed_outfolder"):
    """Concatenate, sort and merge a list of bed files, removing one bed
    at the time.  Name the resulting bed according to the only which
    was not in the concatenation.
    """

    del_bed_name = bed_tuple[0]
    bed_list = bed_tuple[1]

    merge_path = os.path.join(outfolder, "all-merged-except-" + del_bed_name)

    cmd = "cat {0} | bedtools sort | bedtools merge > {1}".format(
        " ".join([bed.path for bed in bed_list]), merge_path
    )

    exec_command(cmd)

    return Bed(merge_path)


def get_all_merged_beds(bed_list, nthreads=1, outfolder="bed_outfolder"):
    """Threaded merge_bed_list
    """

    os.makedirs(outfolder, exist_ok=True)

    pool = Pool(nthreads)

    subsetted_bed_lists = {}

    for i, bed in enumerate(bed_list):

        # Remove one bed at the time and pass the list of beds to concatenate
        # bed_list[:] is to generate a copy to not pop out from actual bed_list
        l = bed_list[:]
        del_bed = l.pop(i)

        subsetted_bed_lists[del_bed.name] = l

    func = partial(merge_bed_list, outfolder=outfolder)

    res = pool.map(func, [(k, i) for k, i in subsetted_bed_lists.items()])

    return res
