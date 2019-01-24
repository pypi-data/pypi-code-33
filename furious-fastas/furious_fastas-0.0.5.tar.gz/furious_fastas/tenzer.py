from datetime import datetime
from itertools import chain
from os.path import join, exists
from os import makedirs as mkdir
from shutil import move as mv
from glob import glob

from furious_fastas.fastas import human, ecoli, wheat, mouse, yeast, leishmania, NamedFastas
from furious_fastas.misc import create_xml_description





# db_path = "/Users/matteo/Projects/furious_fastas/py_data/DB"
def update_fastas(db_path, verbose=True):
    """Update the fasta files used in prof. Stefan Tenzer's group.

    Arguments
    =========
    db_path : str
        Path to the folder where we will store the files.
    """
    if verbose:
        print("Downloading files from Uniprot.")
    for f in (human, ecoli, wheat, mouse, yeast, leishmania):
        f.download_from_uniprot()
        print("\t{} x".format(f.name))

    recent = join(db_path, "recent")
    now    = "fastas_" + str(datetime.now()).replace(" ", "_")
    newest = join(recent, now)
    old    = join(db_path, "old")

    if not exists(old):
        mkdir(old)
    if exists(recent):
        # need to move the recent files into the older database
        # assume that the name will start with 2...
        old_project = glob(join(recent,"fastas_*"))[0]
        mv(src=old_project, dst=old)
    mkdir(newest)

    orig, cont, cont_rev = [join(newest, f) for f in ("original", "contaminated", "contaminated_reversed")]
    for p in (orig, cont, cont_rev):
        mkdir(p)
    if verbose:
        print("Created necessary folders.")

    # combine human, yeast, ecoli into HYE
    HYE = NamedFastas("HYE")
    HYE.fastas.extend(chain(human, yeast, ecoli))
    HYE.original_file = "\n".join((human.original_file, yeast.original_file, ecoli.original_file))
    if verbose:
        print("Created Human-Yeast-Ecoli.")

    for f in (human, ecoli, wheat, mouse, yeast, leishmania, HYE):
        f.write_original_file(join(orig, f.name + ".fasta"))
        create_xml_description(orig)
        if verbose:
            print("Created original files for {}.".format(f.name))

        f.add_contaminants()
        f.write(join(cont, f.name + ".fasta"))
        create_xml_description(cont)
        if verbose:
            print("Appended contaminants to {}.".format(f.name))

        # f.reverse()
        # f.write(join(cont_rev, f.name + ".fasta"))
        create_xml_description(cont_rev)
        if verbose:
            print("Reversed contaminated {}.".format(f.name))

    print("Succeeeded!")




