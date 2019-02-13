#! /usr/bin/env python3

import jinja2
import click
import json
import glob
import os
import re
from pynextgen.logging_config import get_logger

logger = get_logger(__file__, __name__)

CMD_TEMPLATE = ["master_snake.tpl"]
DEFAULT_SNAKEFILE = os.path.join(
    os.path.dirname(__file__), "snake_make_recipes/pre_bam.sm"
)
DEFAULT_CLUSTERCONF = os.path.join(
    os.path.dirname(__file__), "snake_make_recipes/cluster.conf"
)

# Usage
# cd /home/ekornobis/Programming/pyNextGen/snake_make_recipes/test
# python ../config_generator.py -s stranded -p single -b ../../demo_data/ALL/bams -f ../../demo_data/ALL/fqs -g ~/data/genomes/ensembl/h_sapiens/hg37/Homo_sapiens.GRCh37.75.gtf

# Other example with paired data
# python ../config_generator.py -s stranded -p paired -f ~/data/demo/mus_musculus/fqs/ -i ~/data/genomes/ensembl/m_musculus/GRCm38/star_index -r ~/data/genomes/ensembl/m_musculus/GRCm38/Mus_musculus.GRCm38.dna_sm.toplevel.fa -g ~/data/genomes/ensembl/m_musculus/GRCm38/Mus_musculus.GRCm38.87.gtf

# snakemake --cores 20 -s ../post_bam.sm --configfile snakemake.json
# Limitations
# Check the CMD_OPTIONS dictionnary for adding other programs

##### WARNING #####

# Apparently, the CMD_FILE option is NOT WORKING (unhashable type list ERROR)

# ASSUMPTIONS:
###################

# POSSIBLE IMPROVEMENTS:
# Ask for the folder on tars where to copy all necessary files (and
# launch the job directly ?)

CMD_OPTIONS = {
    "qorts": {
        "single": "--singleEnded",
        "paired": "",
        "unstranded": "",
        "stranded": "--stranded --stranded_fr_secondstrand",
        "reverse": "--stranded",
    },
    "qualimap": {
        "single": "",
        "paired": "-pe",
        "unstranded": "-p non-strand-specific",
        "stranded": "-p strand-specific-forward",
        "reverse": "-p strand-specific-reverse",
    },
    "featureCount": {
        "single": "",
        "paired": "-p",
        "unstranded": "-s 0",
        "stranded": "-s 1",
        "reverse": "-s 2",
    },
    "kallisto": {
        "single": "--single",
        "paired": "",
        "unstranded": "",
        "stranded": "--fr-stranded",
        "reverse": "--rf-stranded",
    },
}


class Job:
    """Object representing a job submission to be used in a snakemake
    pipeline run. Basically this object gather all parameters passed
    to the command line and generate a json file to be used as a
    --configfile in snakemake
    """

    def __init__(self, **kwargs):
        self.params = kwargs

        # Building argument string
        for prog in CMD_OPTIONS:
            self.params[prog] = " ".join(
                [CMD_OPTIONS[prog][self.params[p]] for p in ["pair", "strand"]]
            )

        self.params["samples"], self.params["fq_ext"] = self.get_sample_names()

        if self.params["fq_ext"].endswith(".gz"):
            self.params["star"] = "--readFilesCommand zcat"

        # Set template dir to location of the current script
        template_dir = os.path.join(os.path.dirname(__file__), "templates")

        # Render the jinja template
        self.jinjaenv = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

    def __repr__(self):
        return "Snakemake Job object: {0}".format(self.params)

    def generate_config(self, json_out):

        with open(json_out, "w") as out:
            out.write(json.dumps(self.params, indent=4))

    def generate_command_file(self):
        """From a template, generate the slurm command file leading the
        workflow
        """

        text = self.jinjaenv.get_template(CMD_TEMPLATE).render(
            snakefile_path=self.params["snakefile"],
            cluster_conf_path=self.params["cluster_conf"],
            snakemake_json=self.params["json_out"],
        )

        with open(self.params["cmd"], "w") as out:
            out.write(text)

    def get_sample_names(self):

        # Extract fastq extension from fqdir files to specify it later in snakemake file
        if self.params["ext"]:
            ext = self.params["ext"]

        # If extensions not specified, tries to guess it
        else:
            extensions = ("*.fq", "*.fq.gz", "*.fastq", "*.fastq.gz")

            ext = [
                ext[1:]
                for ext in extensions
                if len(glob.glob(os.path.join(self.params["fqdir"], ext))) != 0
            ]

            if len(ext) != 1:
                raise IOError(
                    "Either no known fastqs extension in {0} or more than one \
                extension. Extensions found:{1}".format(
                        self.params["fqdir"], ext
                    )
                )

            ext = ext[0]
            logger.debug('Fastq extension found: "{}"'.format(ext))

        # List samples names for later use in snakemake file
        if self.params["pair"] == "paired":

            basenames = [
                os.path.basename(x).replace(ext, "")
                for x in glob.glob(os.path.join(self.params["fqdir"], "*" + ext))
            ]

            # Specify to type of notation for pairs
            pattern = "({0}{2}|{1}{2})".format(*self.params["pair_notation"], ext)

            samples = list(
                set(
                    [
                        os.path.basename(re.sub(pattern, "", x))
                        for x in glob.glob(
                            os.path.join(self.params["fqdir"], "*" + ext)
                        )
                    ]
                )
            )

        else:
            samples = [
                os.path.basename(x).replace(ext, "")
                for x in glob.glob(os.path.join(self.params["fqdir"], "*" + ext))
            ]

        logger.debug("Samples: {}".format(samples))

        return (samples, ext)


@click.command()
@click.option(
    "--bamdir",
    "-b",
    default=None,
    type=click.Path(exists=True, resolve_path=True),
    help="Path to the bam directory.",
)
@click.option(
    "--fqdir",
    "-f",
    default=None,
    type=click.Path(exists=True, resolve_path=True),
    required=True,
    help="Path to the fastqs directory.",
)
@click.option(
    "--strand",
    "-s",
    type=click.Choice(["unstranded", "stranded", "reverse"]),
    required=True,
    help='Strandedness: "unstranded", "stranded" or  "reverse stranded".',
)
@click.option(
    "--pair",
    "-p",
    default=False,
    type=click.Choice(["single", "paired"]),
    required=True,
    help='Paired end: either "single" or "paired".',
)
@click.option(
    "--json_out",
    "-o",
    default="snakemake.json",
    type=click.Path(exists=False, resolve_path=True),
    help="Path to the json output file.",
)
@click.option(
    "--gtf",
    "-g",
    default=None,
    type=click.Path(exists=True, resolve_path=True),
    required=True,
    help="Path to the gtf annotation file.",
)
@click.option(
    "--star_index",
    "-i",
    default=None,
    type=click.Path(resolve_path=True),
    required=True,
    help="Path to the star index directory.",
)
@click.option(
    "--ref_fasta",
    "-r",
    default=None,
    type=click.Path(exists=True, resolve_path=True),
    help="Path to the reference genome fasta file.",
)
@click.option(
    "--kallisto_index",
    "-k",
    default=None,
    type=click.Path(exists=True, resolve_path=True),
    help="Path to the kallisto transcriptome index.",
)
@click.option(
    "--ref_bed",
    default=None,
    type=click.Path(exists=True, resolve_path=True),
    help="Path to the refseq genes bed file for RseqQC.",
)
@click.option(
    "--pair_notation",
    nargs=2,
    type=str,
    default=["_1", "_2"],
    help="A list of strings used in fastq files to distinguish between reads1 and reads2 in a pair",
)
@click.option(
    "--ext",
    type=str,
    default=None,
    help="The string used as extensions for the fastq files. \
If not specified, the program will guess the extension from (*.fq, *.fq.gz, *.fastq, *.fastq.gz)",
)
@click.option(
    "--cmd",
    default=None,
    type=click.Path(exists=False, resolve_path=True),
    help="Path to the command file to be created (not created by default)",
)
@click.option(
    "--snakefile",
    default=DEFAULT_SNAKEFILE,
    help="The path to the snakefile workflow to execute (will be added to the cmd file if generated)",
)
@click.option(
    "--cluster_conf",
    default=DEFAULT_CLUSTERCONF,
    help="The path to the cluster configuration file (will be added to the cmd file if generated)",
)
def main(**kwargs):
    """A configuration tool to automatically generate input files for
    snakemake workflows
    """

    job = Job(**kwargs)
    logger.info(f"Initializing: {job}")
    job.generate_config(kwargs["json_out"])

    if job.params["cmd"]:
        job.generate_command_file()


if __name__ == "__main__":
    main()
