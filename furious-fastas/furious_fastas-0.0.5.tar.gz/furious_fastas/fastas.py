from Bio import SeqIO
import io
from itertools import chain
from os.path import join as pjoin
from os import path
import requests

from furious_fastas.uniprot import uniprot_url



class SimpleFastas(object):
    def __init__(self):
        self.fastas = []
        self._reversed = "not reversed"

    def read(self, path):
        """Read the fastas."""
        self.fastas = list(SeqIO.parse(path, "fasta"))

    def write(self, path, original = False):
        """Write file under the given path.

        Arguments
        =========
        path : str
            Path where to dump the file.
        """
        SeqIO.write(self.fastas, path, "fasta")

    def __iter__(self):
        """Iterate over sequences."""
        return iter(self.fastas)

    def __len__(self):
        """Return the number of sequences in the fasta file.""" 
        return len(self.fastas)

    def __getitem__(self, key):
        """Return the key-th fasta sequence."""
        return self.fastas[key]

    def _seq_repr(self):
        fasta_cnt = len(self.fastas)
        if fasta_cnt == 0:
            return "There are no sequences yet."
        elif fasta_cnt == 1:
            return "There is one fasta sequence.\n" + repr(self.fastas[0])
        else:
            out = "There are {} fasta sequences.\n".format(len(self.fastas))
            out += "\n".join(repr(f) for f in self.fastas[:3])
            out += "\n...\n"
            return out

    def __repr__(self):
        return "SimpleFastas, {}.\n{}".format(self._reversed, self._seq_repr())

    def reverse(self):
        """Add reversed sequences to the ones already present."""
        raise NotImplementedError
        if self._reversed == "not reversed":
            #TODO: reverse ...
            # ...
            # ...
            self._reversed = "reversed"



class Contaminants(SimpleFastas):
    """A class representing the contaminants.

    This class cannot be downloaded from Uniprot.
    But we give you some common contaminants for free.
    """
    def __init__(self):
        here = path.abspath(path.dirname(__file__))
        self.read(pjoin(here, "data/contaminants.fasta")) 
        self.name = "contaminants"
        self._reversed = "not reversed"

    def __repr__(self):
        return "Contaminants, {}.\n{}".format(self._reversed, super().__repr__())

default_contaminants = Contaminants()


class Fastas(SimpleFastas):
    def __init__(self):
        super().__init__()
        self._contaminated = False 

    def download_from_uniprot(self, uniprot_query=""):
        """Download the query/species sequences from Uniprot.

        Arguments
        =========
        uniprot_query : str
            The url to use to download the data from Uniprot, e.g. 
            http://www.uniprot.org/uniprot/?query=reviewed:yes+AND+organism:9606&format=fasta
            would be used to retrieved all human proteins that were reviewed.
            Some common choices in Tenzer's group include those in the uniprot 
            dictionary in the furious_fastas.uniprot.
        """
        self.original_file = requests.get(uniprot_query).text
        self.fastas = list(SeqIO.parse(io.StringIO(self.original_file), "fasta"))

    def write_original_file(self, path):
        """Write the file orginally downloaded from the Uniprot."""
        with open(path, "w") as f:
            f.write(self.original_file)

    def add_contaminants(self, contaminants=default_contaminants):
        """Add contaminants to the fastas.

        Arguments
        =========
        contaminants : Fastas
            The input contaminants. By default, we use Tenzer's contaminants.
            I mean, the ones used in his groups, not biblically his.
        """
        if not self._contaminated:
            self.fastas.extend(contaminants)
            self._contaminated = True

    def __repr__(self):
        c = 'w/ contaminants' if self.contaminated else 'w/o contaminants'
        return "Fastas, {}, {}.\n{}".format(c, self._reversed, self._seq_repr())



class NamedFastas(Fastas):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def download_from_uniprot(self, uniprot_query=""):
        """Download the query/species sequences from Uniprot.

        Arguments
        =========
        uniprot_query : str
            The url to use to download the data from Uniprot.
            If not supplied, defaults to all reviewed human proteins found at
            http://www.uniprot.org/uniprot/?query=reviewed:yes+AND+organism:9606&format=fasta
        """
        self.uniprot_query = uniprot_query if uniprot_query else uniprot_url[self.name]
        self.original_file = requests.get(self.uniprot_query).text
        self.fastas = list(SeqIO.parse(io.StringIO(self.original_file), "fasta"))

    def __repr__(self):
        c = 'w/ contaminants' if self.contaminated else 'w/o contaminants'
        return "{} fastas, {}, {}.\n{}".format(self.name,
                                               c,
                                               self._reversed,
                                               self._seq_repr())


human = NamedFastas("human")
ecoli = NamedFastas("ecoli")
wheat = NamedFastas("wheat")
mouse = NamedFastas("mouse")
yeast = NamedFastas("yeast")
leishmania = NamedFastas("leishmania")



def save(fastas, out_path):
    """Save fasta sequences into one, nicely parsable fasta file.

    Arguments
    =========
    fastas : list of furious_fastas.fastas.Fastas
        A list of fastas to merge.
    out_path : str
        A path where the merged fastas should be saved as one bigger fasta file.
    """
    all_sequences = chain.from_iterable(f for f in fastas)
    SeqIO.write(all_sequences, out_path, "fasta")
