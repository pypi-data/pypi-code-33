from datetime import datetime
from os.path import join
from os import makedirs as mkdir, listdir as ls
from shutil import move as mv
import json

from ..download import download
from ..contaminants import conts
# from .misc import create_xml_description


def update_plgs(db_path,
                species2url,
                contaminants=conts,
                indent=4,
                verbose=True):
    """Update the fasta data bases for the PLGS software.

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
    now = str(datetime.now()).replace(" ", "_").split('.')[0]
    folder = join(db_path,now)
    original = join(folder,'original')
    with_conts = join(folder,'with_contaminants')
    with_conts_rev = join(folder,'with_contaminants_and_reversed')
    mkdir(original)
    mkdir(with_conts)
    mkdir(with_conts_rev)

    if verbose:
        print("Downloading files from Uniprot.")

    stats = [("contaminants", len(contaminants))]
    for name, url in species2url:
        fastas = download(url)
        fastas.write(join(original, name+".fasta"))
        contaminated = fastas + contaminants
        contaminated.write(join(with_conts, name+".fasta"))
        contaminated_reversed = contaminated.reverse()
        contaminated_reversed.write(join(with_conts_rev, name+".fasta"))
        stats.append((name, len(fastas)))
        if verbose:
            print("\t{} x".format(name))

    with open(join(folder,"stats.json"), 'w+') as h:
        json.dump(stats, h, indent=indent)
    
    if verbose:
        print("Erfolgt.")
