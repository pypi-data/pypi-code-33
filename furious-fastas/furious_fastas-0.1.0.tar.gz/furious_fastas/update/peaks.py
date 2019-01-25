from datetime import datetime
from os.path import join
from os import makedirs as mkdir, listdir as ls
from shutil import move as mv

from ..download import download
from ..contaminants import conts


def update_peaks(db_path, species2url, contaminants=conts, verbose=True):
    """Update the fasta data bases for the Peaks software.

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
        fastas = download(url)
        contaminated_fastas = fastas + conts
        reviewed = "SP" if 'reviewed:yes' in url else "TR"
        file = "{}_{}_{}_{}_contaminated.fasta".format(now,
                                                       name,
                                                       reviewed,
                                                       str(len(fastas)))
        fastas.write(join(current,file))
        if verbose:
            print("\t{} x".format(name))
    if verbose:
        print("Succeeeded!")
