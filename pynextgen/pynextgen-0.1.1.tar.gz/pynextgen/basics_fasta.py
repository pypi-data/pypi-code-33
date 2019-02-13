#! /usr/bin/env python

import re
from pathlib import Path
import pysam
import pynextgen.basics_nuc_seq as bns
import matplotlib.pyplot as plt
from collections import Counter
import click
import os
import pandas as pd
from itertools import groupby
from pynextgen.logging_config import get_logger

logger = get_logger(__file__, __name__)

# TODO: check if dedup_fasta can be improved using yield as in
# /home/ekornobis/code/allemand/gphn/7.2_generate_ref_before_rsem.py

# TO IMPROVE:
# Fasta method to_dict


class BioSeq(object):
    """ A representation of a biological sequence
    """

    def __init__(self, name, seq):
        self.name = name
        self.seq = seq

    def __repr__(self):
        return f"Biological sequence: >{self.name} {self.seq[:10]}..."

    def ungap(self):
        """ Remove gaps from a sequence
        """

        self.seq = self.seq.replace("-", "")

        return self


class Fasta(object):
    """A Fasta sequence file object
    """

    def __init__(self, path):

        if os.path.isfile(path):
            self.path = Path(path)
        else:
            raise IOError("No such file: {}".format(path))

    def __repr__(self):
        return "<Fasta Object for: {}".format(self.path)

    def __len__(self):
        """ Number of sequences in the fasta file
        """
        length = sum(1 for _ in self.parse())
        return length

    def parse(self):
        """
        Parse a fasta file. Used for to_dict

        From brentp https://www.biostars.org/p/710/
        """

        # for seq in pysam.FastxFile(self.path):
        #    yield seq.name, seq.sequence

        with self.path.open() as fas:
            # ditch the boolean (x[0]) and just keep the header or sequence since
            # we know they alternate.
            fa_iter = (x[1] for x in groupby(fas, lambda line: line[0] == ">"))
            for header in fa_iter:
                # drop the ">"
                name = next(header)[1:].strip()
                # join all sequence lines to one.
                sequence = "".join(s.strip() for s in next(fa_iter))

                yield BioSeq(name, sequence)

    def to_dict(self, simple_ID=True):
        """
        Get a dictionnary from fasta file with:
        key = seq_id
        value = seq

        If simple_ID is True, then the seq_id in the dictionnary will be
        the original one truncated after the first white space.
        """

        seq_d = {}
        fasta_gen = self.parse()

        # build a dictionnary with key=seq id, value=seq
        for bioseq in fasta_gen:

            if simple_ID:
                # for ex: for trinity output, split()[0] removes the len, path infos
                seq_id = bioseq.name.split(" ")[0]

            else:
                seq_id = bioseq.name

            seq_d[seq_id] = bioseq.seq

        # Check if no empty sequences
        empty_seqs = [k for k in seq_d if len(seq_d[k]) == 0]
        if empty_seqs:
            raise IOError(
                "Something seems wrong with this sequence:\n" + "\n".join(empty_seqs)
            )

        return seq_d

    def dedup(self, fasta_out=None, graph=True, **kwargs):
        """
        Returns a dictionary with the duplicate sequences
        merged under a single entry (the name of the sequence will be the
        concatenation of all the previous sequence names).
        WARNING: Output dictionnary is as:
        keys=sequences
        values=sequence names

        kwargs are passed to the plot.bar function

        Produce a fasta outfile if specified
        """

        dedup_dict = {}
        for seq in pysam.FastxFile(self.path):
            if seq.sequence in dedup_dict:
                dedup_dict[seq.sequence].append(seq.name)
            else:
                dedup_dict[seq.sequence] = [seq.name]

        # reads_per_seq = Counter(map(lambda x: len(x), dedup_dict.values()))

        reads_per_seq = Counter([len(x) for x in dedup_dict.values()])
        logger.info(
            f"Number of identical copies per sequence for {self.path}: {reads_per_seq}"
        )

        if graph:
            labels, values = zip(*reads_per_seq.items())
            plt.bar(labels, values, **kwargs)
            plt.xlabel("Number of copies")
            plt.ylabel("Frequencies")

        # Create a fasta file with only unique sequences
        if fasta_out:
            with open(fasta_out, "w") as f:
                for seq in dedup_dict:
                    f.write(">" + "-".join(dedup_dict[seq]) + "\n")
                    f.write(seq + "\n")

        return dedup_dict

    def filter(self, keep_regexp, suffix="filtered"):
        """
        Filter sequences based on sequence ID based on the specified regex
        """

        fasta_gen = self.parse()
        outfile = self.path.with_name(self.path.stem + "_" + suffix + ".fas")
        pat = re.compile(keep_regexp)

        with outfile.open("w") as fas_out:
            for bioseq in fasta_gen:
                if re.match(pat, bioseq.name):
                    fas_out.write(f">{bioseq.name}\n{bioseq.seq}\n")

        return Fasta(outfile)

    def stats(self):
        """
        Produce statistics on the sequences in the fasta file
        """

        logger.info("Producing stats for: %s" % self.path)

        fasta_df = pd.DataFrame(
            {
                "seq_names": [seq.name for seq in pysam.FastxFile(self.path)],
                "seq_len": [len(seq.sequence) for seq in pysam.FastxFile(self.path)],
                "GC_content": [
                    bns.get_seq_GC(seq.sequence) for seq in pysam.FastxFile(self.path)
                ],
                "Ns": [seq.sequence.count("N") for seq in pysam.FastxFile(self.path)],
            }
        )
        fasta_df = fasta_df.set_index("seq_names")

        return fasta_df

    def summary(self):
        """
        Produce a statistic summary for the Fasta file
        """

        fasta_df = self.stats()
        plt.subplot(1, 2, 1)
        plt.boxplot(fasta_df["seq_len"])
        plt.title("Sequence length boxplot")
        plt.subplot(1, 2, 2)
        plt.hist(fasta_df["seq_len"], bins=100, log=True)
        plt.title("Sequence length Histogram(log)")
        plt.show()

        print(fasta_df.describe())

        return fasta_df


@click.command()
@click.argument("fasta")
def main(fasta):

    f = Fasta(fasta)

    f.summary()


if __name__ == "__main__":

    main()
