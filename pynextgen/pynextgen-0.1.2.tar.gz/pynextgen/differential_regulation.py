import pandas as pd
from pynextgen.logging_config import get_logger
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from ipywidgets import interactive, Dropdown, fixed
from IPython.display import display, HTML
import os
import math
from matplotlib_venn import venn2

# REQUIREMENTS
# The DR tables should be created with the new version of DR notebook:
# http://localhost:8888/notebooks/Programming/jupyter/good_practices/DEG_DESeq2_1.0.ipynb

# IMPROVEMENTS:
# Object for a list of DR comparisons
# Describe a genes (in which compa is DR, tables for each compa, expression plots, etc...)

logger = get_logger(__file__, __name__)


class CountMatrix(object):
    """A matrix of counts from RNA-seq quantification
    
    The count matrix used for initialization have to be in csv format:
    First column are transcript ids, first line (header) are samples
    
    :param counts_csv: A csv file with RNA-seq counts with header containing sample ids
    :param meta_csv: A csv file with grouping information for each samples. 
    :param index_col: A list with a single entry which specify the name of the column in meta to use for correspondence between meta and counts. By default, the header ['filenames'].
    :param annot_csv: An annotation csv file with a header and a feature_id column used for the correspondace with the feature ids present in the counts_csv file.

    """

    def __init__(
        self,
        counts_csv,
        meta_csv,
        index_col=["filenames"],
        annot_csv="",
        normalize=False,
    ):
        self.path = counts_csv
        self.counts = pd.read_csv(counts_csv, index_col=0).T
        self.meta = pd.read_csv(meta_csv, index_col=index_col)

        self.df = self.to_dataframe()

        if normalize:
            self.normed = self.normalize_counts()

        if annot_csv:
            self.annot = pd.read_csv(annot_csv, index_col=["feature_id"])

    def __repr__(self):
        return f"Count Matrix from csv: {self.path}"

    def head(self, n=5):
        """ Display first n lines of the count matrix

        :param n: Number of lines to display.
        """
        return self.counts.head(n)

    def counts_set_index(self, keys):
        """Re-index the counts using the specified keys (columns names in
        self.meta) as indexes
        """

        df = pd.concat([self.counts, self.meta], axis=1)

        # reindex and drop meta columns
        df = df.set_index(keys).drop(self.meta.columns, axis=1, errors="ignore")

        return df

    def to_dataframe(self):
        """ Get total number of counts for each library and add it to self.df
        """
        # Get sum of all counts
        total_counts = self.counts.sum(axis=1).to_frame()
        total_counts.columns = ["total_counts"]

        # Concatenate metadata, counts and sum of all counts
        df = pd.concat([self.meta, self.counts, total_counts], axis=1, sort=True)
        return df

    def explore_total_counts(self):
        """Allow to interactively plot values from one column of the total
        dataframe self.df by metadata groups.
        """
        meta_group = Dropdown(options=self.meta.columns)

        total_counts_W = interactive(
            self.plot_by_meta_group,
            value_column=fixed("total_counts"),
            meta_column=meta_group,
        )
        display(total_counts_W)

    def plot_by_meta_group(self, value_column, meta_column):
        """Plot counts by groups

        :param value_column: The value_column index to use to select value to plot from the total dataframe.
        :param meta_column: The name of the column to select from metadata.csv for the grouping.

        :returns: Plot distribution over selected groups for the selected value_column.
        """
        figure = sns.barplot(x=meta_column, y=value_column, data=self.df, ci=95)
        figure = sns.swarmplot(x=meta_column, y=value_column, data=self.df)
        plt.xticks(rotation=90)

    def explore_counts(self, degs_dict, annot=pd.DataFrame()):
        """Interactively explore the counts in a jupyter notebook

        :param degs_dict: A dictionnary of gene lists (for example, with comparisons as keys and list of differentially regulated genes as values.
        :param annot: A dictionnary of annotations tables obtained from post_DR.post_DR.

        :returns: None

        """
        logger.info("Displaying only comparisons with number of DEGs > 0")

        degs_dict = {k: degs_dict[k] for k in degs_dict if degs_dict[k]}

        compa = Dropdown(options=degs_dict.keys(), layout={"width": "50%"})
        # Link gene choices to compa selection
        gene = Dropdown(options=degs_dict[compa.value], layout={"width": "50%"})
        meta_group = Dropdown(options=self.meta.columns)

        # Real time updating of the DEGs list
        def update_degs(compa):
            gene.options = degs_dict[compa]

        def plot_counts(value_column, meta_column):
            self.plot_by_meta_group(value_column, meta_column)
            display(HTML(annot.loc[[value_column]].to_html()))

        compa_W = interactive(update_degs, compa=compa)
        gene_meta_W = interactive(
            plot_counts, value_column=gene, meta_column=meta_group, annot=fixed(annot)
        )

        display(compa_W)
        display(gene_meta_W)

    def heatmap(self, drgs=None):
        """ Plot a heatmap from the count matrix

        :param drgs: A list of differentially regulated transcript/gene identifiers
        """
        self.counts.loc[:, drgs]


def normalize_counts(self, method="cpm", log=True):
    """Normalize the count matrix

        :param method: The method to use for normalization. 'cpm' ie 'counts per million' is only normalized by library sizes.
        :param log: Apply or not Log-transformation to counts (A pseudocount of 0.5 is added)

        .. todo:: implement a proper normalization method

        .. warning:: NOT FUNCTIONNAL

        """
    counts = self.counts
    counts = (counts + 0.5) / (counts.sum(axis=0) / 10 ** 6)
    counts = np.log2(counts)

    return counts


class Deseq2Results(object):
    """Object to handle DESeq2 results
    """

    def __init__(self, csv_file):
        self.path = csv_file
        self.name = os.path.splitext(os.path.basename(csv_file))[0]
        self.df = self.read_de_res(csv_file)
        self.add_fold_change()
        self.fdr_threshold = None
        self.fc_threshold = None

    def __repr__(self):
        return "Deseq2_results: {}".format(self.name)

    def read_de_res(self, csv_file):

        df = pd.read_csv(csv_file, index_col=0)

        annot_header = [
            "external_gene_name",
            "chromosome_name",
            "start_position",
            "end_position",
            "strand",
            "baseMean",
            "log2FoldChange",
            "lfcSE",
            "stat",
            "pvalue",
            "padj",
        ]

        simple_header = [
            "baseMean",
            "log2FoldChange",
            "lfcSE",
            "stat",
            "pvalue",
            "padj",
        ]

        if list(df.columns) != annot_header and list(df.columns) != simple_header:
            print(list(df.columns))
            raise ValueError("The DR table does not have the correct headers.")

        df.rename_axis("#gene_id", inplace=True)
        return df

    def add_fold_change(self):
        """ Transform logFC in FC and add a column top df
        """

        self.df["fold_change"] = [2 ** x for x in self.df["log2FoldChange"]]

        return self

    def filter_fdr_fc(self, fdr_thres=0.05, fc_thres=0):
        """filter a DESeq2 result with FDR and logFC thresholds
        """

        fc_filt = self.df["fold_change"].abs() >= fc_thres
        fdr_filt = self.df["padj"] < fdr_thres

        self.df = self.df[fc_filt.values & fdr_filt.values]

        self.fdr_threshold = fdr_thres
        self.fc_threshold = fc_thres

        return self

    def get_differential_genes(self):
        """Get list of differentially regulated genes at the current state of
        FDR, FC filtering
        """

        logger.info(
            f"DRGs for thresholds: FDR: {self.fdr_threshold}; FC: {self.fc_threshold};"
        )
        return list(self.df.index)

    def import_annotation(self, csv, index_col, annot_cols, remove_duplications=False):
        """Import gene annotations from a csv file.

        :param csv: A csv file with header and annotations to link to the IDs used as index in self.df
        :param index_col: The name of the column to use as index
        :param annot_cols: The annotation columns to keep
        """

        annot = pd.read_csv(csv, sep="\t")
        annot.set_index(index_col, inplace=True)
        self.annot = annot.loc[self.df.index, annot_cols]

    def extract_gene_names_for_GO(self):
        """ Return a file with one Gene IDs per line for further GO analysis
        """

        outfile = os.path.splitext(self.path)[0] + "_geneIDs_to_GO.txt"
        with open(outfile, "w") as f:
            for gene_ID in self.df.index:
                f.write(gene_ID + "\n")

    def summary(self, annot_file=None, export_file=None):
        """ Describe the DR results

        :param annot_file: 
        :param export_file: 

        """
        return {
            "comparison": self.name,
            "up": (self.df.fold_change > 0).sum(),
            "down": (self.df.fold_change < 0).sum(),
            "total": self.df.shape[0],
        }

    def compare(self, d2res, verbose=False):
        """Compare two Deseq2Results objects.  For now this will plot venn
        diagrams for the comparisons considering UP and DOWN regulated
        genes separately

        If verbose, will return a dictionnary of dataframes with
        subset of genes for each comparisons
        """

        # Compare all:
        deg1 = set(self.df.index)
        deg2 = set(d2res.df.index)

        print("Common to both: {}".format(deg1.intersection(deg2)))

        plt.figure()
        plot_venn(deg1, deg2, self.name, d2res.name, "Differentially regulated")

        # Compare up regulated genes lists
        up1 = set(self.df.loc[self.df.fold_change > 0].index)
        up2 = set(d2res.df.loc[d2res.df.fold_change > 0].index)

        plt.figure()
        plot_venn(up1, up2, self.name, d2res.name, "UP regulated")

        # Compare up regulated genes lists
        down1 = set(self.df.loc[self.df.fold_change < 0].index)
        down2 = set(d2res.df.loc[d2res.df.fold_change < 0].index)

        plt.figure()
        plot_venn(down1, down2, self.name, d2res.name, "DOWN regulated")

        if verbose:
            return {
                self.name + "_specific_up": self.df.loc[up1 - up2],
                d2res.name + "_specific_up": d2res.df.loc[up2 - up1],
                self.name + "_specific_down": self.df.loc[down1 - down2],
                d2res.name + "_specific_down": d2res.df.loc[down2 - down1],
                self.name
                + "_"
                + d2res.name
                + "_common_up": self.df.loc[up1.intersection(up2)],
                self.name
                + "_"
                + d2res.name
                + "_common_down": self.df.loc[down1.intersection(down2)],
            }


def plot_venn(set1, set2, label1, label2, title):
    v = venn2([set1, set2], set_labels=[label1, label2])
    plt.title(title)
