from datetime import datetime
from itertools import chain
from os.path import join, exists
from os import makedirs as mkdir
from os import listdir as ls
from shutil import move as mv
from glob import glob

from furious_fastas.fastas import NamedFastas, default_contaminants
from furious_fastas.misc import create_xml_description

# db_path = "/Users/matteo/Projects/furious_fastas/py_data/DB"
def update_fastas(db_path, species2url, contaminants=default_contaminants, verbose=True):
    """Update the fasta files used in prof. Stefan Tenzer's group.

    Arguments
    =========
    db_path : str
        Path to the folder where we will store the files.
    species2url : iterable of tuples
        Each tuple consists of the species name and its Uniprot url.
    contaminants :
        Fastas with contaminants.
    verbose : boolean
        Be more verbose?
    """
    if verbose:
        print("Creating necessary folders.")

    current = join(db_path, "current")
    old = join(db_path, "old")
    mkdir(old, exist_ok=True)
    mkdir(current, exist_ok=True)

    for f in ls(current):
        mv(src=join(current, f), dst=old)

    now = str(datetime.now()).replace(" ", "_").split('.')[0]

    if verbose:
        print("Downloading files from Uniprot.")
    for name, url in species2url:
        s = NamedFastas(name)
        s.download_from_uniprot(url)
        s.add_contaminants(contaminants)
        reviewed = "SP" if 'reviewed:yes' in url else "TR"
        s_file = "{}_{}_{}_{}_contaminated.fasta".format(now, name, reviewed, str(len(s)))
        s_path = join(current, s_file)
        s.write(s_path)
        print("\t{} x".format(s.name))
    
    if verbose:
        print("Succeeeded!")
