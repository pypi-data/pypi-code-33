import io
from itertools import chain
from os.path import join as pjoin

from .uniprot import uniprot_url
from .parse.fastas import parse


class Fastas(object):
    def __init__(self, fastas=[]):
        self.fastas = list(fastas)

    def read(self, path):
        """Read the fastas from a file.

        Args:
            path (str): path to the file.
        """
        with open(path, 'r') as f:
            fastas = f.read()
        self.fastas = list(parse(fastas))

    def write(self, path, append=False):
        """Write file under the given path.

        Arguments
        =========
        path : str
            Path where to dump the file.
        """
        fp = 'a' if append else 'w+'
        with open(path, fp) as h:
            for f in self.fastas:
                h.write("{}\n{}\n".format(f.header, str(f)))

    def __iter__(self):
        """Iterate over sequences."""
        for f in self.fastas:
            yield f

    def __len__(self):
        """Return the number of sequences in the fasta file.""" 
        return len(self.fastas)

    def __getitem__(self, key):
        """Return the key-th fasta sequence."""
        return self.fastas[key]

    def __repr__(self):
        return "Fastas({})".format(len(self))

    def reverse(self):
        """Produce new Fastas containing reversed copy of sequences."""
        rev_self = self.copy()
        for f in self:
            rev_self.fastas.append(f.reverse())
        return rev_self

    def copy(self):
        r = Fastas()
        for f in self:
            r.fastas.append(f.copy())
        return r

    def append(self, other):
        """Append copies of fastas."""
        for f in other:
            self.fastas.append(f.copy())

    def __add__(self, other):
        """Add two fastas.

        Args:
            other (Fastas): The other fastas, e.g. contaminants.
        """
        res = self.copy()
        res.append(other)
        return res
