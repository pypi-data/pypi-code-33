from collections.abc import Iterable
from collections import namedtuple, OrderedDict
from copy import deepcopy
import re
import itertools
import numpy as np
# from alignmentrs import Sequence, Marker
from blockrs import Block
from blockrs.block import remove_sites


class Sequence:
    def __init__(self, name, description, sequence):
        self.id = name
        self.description = description
        self.sequence = sequence

    def __repr__(self):
        return '{}(id={}, description="{}", sequence={})'.format(
            self.__class__.__name__, self.id, self.description, self.sequence
        )

    def __str__(self):
        if self.description:
            return '>{}\n{}'.format(self.id, self.sequence)
        return '>{} {}\n{}'.format(self.id, self.description, self.sequence)


class Marker(Sequence):
    pass


class CatBlock:
    def __init__(self, name, start, stop):
        self.name = name
        self.start = start
        self.stop = stop

    def __repr__(self):
        return 'CatBlock(name={}, start={}, stop={})'.format(
            self.name, self.start, self.stop
        )

    def __str__(self):
        return '{}={}:{}'.format(self.name, self.start, self.stop)

class AlignmentMatrix:
    """AlignmentMatrix depicts an aligned set of sequences as
    a 2d array of uint32 values.
    """
    def __init__(self, array, dtype='<U1'):
        """Creates a new alignment matrix.

        Parameters
        ----------
        array : np.array
        dtype : str or numpy.dtype

        """
        self.matrix = array.astype(dtype)

    @classmethod
    def empty(cls, nsamples, nsites, dtype):
        """Creates an empty alignment matrix with a given number of rows
        (nsamples) and columns (nsites).

        Parameters
        ----------
        nsamples : int
            Number of samples (rows)
        nsites : int
            Number of sites (columns)
        dtype : str or numpy.dtype

        """
        return cls(np.empty(nsamples, nsites), dtype=dtype)

    @property
    def nsamples(self):
        """Returns the number of samples (rows) in the alignment matrix.
        """
        return self.matrix.shape[0]

    @property
    def nsites(self):
        """Returns the number of sites (columns) in the alignment matrix.
        """
        return self.matrix.shape[1]

    @property
    def shape(self):
        """Returns the shape of the alignment matrix.

        Returns
        -------
        tuple
            Tuple of number of rows and columns of the alignment

        """
        return self.matrix.shape

    @classmethod
    def subset(cls, aln_matrix, rows=None, cols=None,
               row_step=1, col_step=1):
        """Returns a subset of the alignment matrix by both samples and sites.

        Parameters
        ----------
        m : AlignmentMatrix
        rows : list
        cols : list
        row_step : int
        col_step : int

        Returns
        -------
        AlignmentMatrix

        """
        if rows is None:
            rows = range(0, aln_matrix.nsamples, row_step)
        else:
            if isinstance(rows, int):
                rows = [rows]
            if row_step != 1:
                raise ValueError('row_step value is considered only if rows ' \
                                 'is None')
        if cols is None:
            cols = range(0, aln_matrix.nsites, col_step)
        else:
            if isinstance(cols, int):
                cols = [cols]
            if col_step != 1:
                raise ValueError('col_step value is considered only if cols ' \
                                 'is None')
        # Create a new alignment matrix
        new_aln_matrix = cls(aln_matrix.matrix[rows][:, cols],
                             dtype=aln_matrix.dtype)
        return new_aln_matrix

    def replace_sample(self, i, sequence):
        """Replaces the sequence for a given row in the alignment matrix.

        Parameters
        ----------
        sequence : str or iterable
        i : int

        """
        # Check if nsites is equal
        if len(sequence) != self.nsites:
            raise ValueError(
                'length of sequence not equal to {}'.format(self.nsites))
        if isinstance(sequence, str):
            self.matrix[i, :] = list(sequence)
        elif isinstance(sequence, Iterable):
            self.matrix[i, :] = sequence
        else:
            raise TypeError('sequence must be a string or an iterable')

    def insert_sample(self, i, sequence):
        """Inserts a new sequence in the alignment matrix at the specified
        row position. This increases the total number of rows.

        Parameters
        ----------
        sequence : str or iterable
        i : int

        """
        # Check if nsites is equal
        if len(sequence) != self.nsites:
            raise ValueError(
                'length of sequence not equal to {}'.format(self.nsites))
        if isinstance(sequence, str):
            new_array = np.array([list(sequence)])
        elif isinstance(sequence, Iterable):
            new_array = np.array([sequence])
        else:
            raise TypeError('sequence must be a string or an iterable')
        self.matrix = np.insert(self.matrix, i, new_array, axis=0)

    def append_sample(self, sequence):
        """Inserts a new sequence after the last row of the alignment matrix.
        This increases the total number of rows by 1.

        Parameters
        ----------
        sequence : str or iterable

        """
        # Check if nsites is equal
        if len(sequence) != self.nsites:
            raise ValueError(
                'length of sequence not equal to {}'.format(self.nsites))
        if isinstance(sequence, str):
            new_array = np.array([list(sequence)])
        elif isinstance(sequence, Iterable):
            new_array = np.array([sequence])
        else:
            raise TypeError('sequence must be a string or an iterable')
        self.matrix = np.append(self.matrix, new_array, axis=0)

    def remove_samples(self, i):
        """Removes sample sequences based on the given index.
        If index is a number, only one sequence is removed.
        If the index is a list of numbers, the sequence found at each row
        number is deleted.

        Parameters
        ----------
        i : int or list of int

        """
        self.matrix = np.delete(self.matrix, i, axis=0)

    def get_samples(self, i):
        """Returns a new alignment matrix containing only the samples specified
        by the index.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        AlignmentMatrix

        """
        if isinstance(i, int):
            i = [i]
        return self.__class__.subset(self, rows=i)

    def get_samples_as_str(self, i=None):
        """Returns a list of sequence strings containing only the samples
        specified by the index.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        list of str

        """
        if i is None:
            i = range(self.nsamples)
        elif isinstance(i, int):
            i = [i]
        return [''.join(row) for row in self.matrix[i, :]]

    def get_sites(self, i):
        """Returns a new alignment matrix containing only the sites specified
        by the index.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        AlignmentMatrix

        """
        if isinstance(i, int):
            i = [i]
        return self.__class__.subset(self, cols=i)

    def get_sites_as_str(self, i=None):
        """Returns a list of sequence strings containing only the sites
        specified by the index.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        list of str

        """
        if i is None:
            i = range(self.nsites)
        elif isinstance(i, int):
            i = [i]
        return [''.join(row) for row in self.matrix[:, i]]

    def replace_site(self, i, sequence):
        """Replaces the sequence for a given column in the alignment matrix.

        Parameters
        ----------
        sequence : str or iterable
        i : int

        """
        # Check if nsamples is equal
        if len(sequence) != self.nsites:
            raise ValueError(
                'length of sequence not equal to {}'.format(self.nsamples))
        if isinstance(sequence, str):
            self.matrix[:, i] = list(sequence)
        elif isinstance(sequence, Iterable):
            self.matrix[:, i] = sequence
        else:
            raise TypeError('sequence must be a string or an iterable')

    def insert_site(self, i, sequence):
        """Inserts a new sequence in the alignment matrix at the specified
        site position. This increases the total number of columns.

        Parameters
        ----------
        sequence : str or iterable
        i : int

        """
        # Check if nsamples is equal
        if len(sequence) != self.nsites:
            raise ValueError(
                'length of sequence not equal to {}'.format(self.nsamples))
        if isinstance(sequence, str):
            new_array = np.array([list(sequence)])
        elif isinstance(sequence, Iterable):
            new_array = np.array([sequence])
        else:
            raise TypeError('sequence must be a string or an iterable')
        self.matrix = np.insert(self.matrix, i, new_array, axis=1)

    def append_site(self, sequence):
        """Inserts a new sequence at after the last column of the
        alignment matrix. This increases the total number of columns by 1.

        Parameters
        ----------
        sequence : str or iterable

        """
        # Check if nsamples is equal
        if len(sequence) != self.nsites:
            raise ValueError(
                'length of sequence not equal to {}'.format(self.nsamples))
        if isinstance(sequence, str):
            new_array = np.array([list(sequence)]).T
        elif isinstance(sequence, Iterable):
            new_array = np.array([sequence]).T
        else:
            raise TypeError('sequence must be a string or an iterable')
        self.matrix = np.append(self.matrix, new_array, axis=1)

    def remove_sites(self, i):
        """Removes sites based on the given index.
        If index is a number, only one site is removed.
        If the index is a list of numbers, the sequence found at each column
        number is deleted.

        Parameters
        ----------
        i : int or list of int

        """
        self.matrix = np.delete(self.matrix, i, axis=1)

    def __len__(self):
        return len(self.matrix)

    def __repr__(self):
        return "{}(nsamples={}, nsites={})\n{}".format(
            self.__class__.__name__,
            self.nsamples,
            self.nsites,
            repr(self.matrix)
        )

    def __str__(self):
        return '\n'.join(self.get_samples_as_str())


class BaseAlignment(AlignmentMatrix):
    """BaseAlignment represents a mulitple sequence alignment
    by storing the IDs and descriptions in individual lists, and
    representing the aligned sequences as a 2d array of uint32 values.
    """
    def __init__(self, sequence_list, dtype='<U1'):
        """Creates a new alignment from a list of Sequence objects

        Parameters
        ----------
        sequence_list : list of Sequence

        """
        # Create alignment matrix from data
        # Call parent constructor
        super().__init__(np.array([list(s.sequence) for s in sequence_list]),
                         dtype=dtype)
        # Add new attributes
        self.ids = [s.id for s in sequence_list]
        self.descriptions = [s.description for s in sequence_list]
        self._metadata = ('ids', 'descriptions')

    @classmethod
    def subset(cls, aln, rows=None, cols=None, row_step=1, col_step=1):
        """Returns a subset of the alignment matrix by both samples and sites.

        Parameters
        ----------
        m : BaseAlignment
        rows : list
        cols : list
        row_step : int
        col_step : int

        Returns
        -------
        BaseAlignment

        """
        if rows is None:
            rows = range(0, aln.nsamples, row_step)
        else:
            if isinstance(rows, int):
                rows = [rows]
            if row_step != 1:
                raise ValueError('row_step value is considered only if rows' \
                                 'is None')
        if cols is None:
            cols = range(0, aln.nsites, col_step)
        else:
            if isinstance(cols, int):
                cols = [cols]
            if col_step != 1:
                raise ValueError('col_step value is considered only if cols ' \
                                 'is None')
        # Create a new BaseAlignment
        new_aln = cls(aln.matrix[rows][:, cols], dtype=aln.dtype)
        # Overwrite metadata
        new_aln._metadata = aln._metadata  # copy tuple
        for name in new_aln._metadata:
            new_value = [v for i, v in enumerate(aln.__getattribute__(name))
                         if i in rows]
            new_aln.__setattr__(name, new_value)
        return new_aln

    def get_samples(self, i):
        """Returns a new alignment matrix containing only the samples specified
        by the index.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        BaseAlignment

        """
        if isinstance(i, int):
            return self.__class__.subset(self, rows=i)
        # handles single string input
        elif isinstance(i, str):
            # gets id index from id
            return self.__class__.subset(self, rows=self.ids.index(i))
        elif isinstance(i, list):
            if len(i) == sum((isinstance(j, int) for j in i)):
                return self.__class__.subset(self, rows=i)
            elif len(i) == sum((isinstance(j, str) for j in i)):
                # get int position in self.ids and then use subset
                i = [self.ids.index(idx) for idx in i]
            else:
                raise ValueError('i must be a list of int or str')
        else:
            raise ValueError('i must be an int or str, or a list of int or str')
        return self.__class__.subset(self, rows=i)

    def get_samples_as_str(self, i=None):
        """Returns a list of sequences as strings containing only the
        specified samples.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        list of str

        """
        if i is None:
            return [''.join(row) for row in self.matrix]
        return [''.join(row) for row in self.get_samples(i).matrix]

    def get_samples_as_fasta(self, i=None):
        """Returns a list of sequences as strings containing only the
        specified samples.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        list of str

        """
        matrix = self.matrix if i is None else self.get_samples(i).matrix
        zipped = zip(self.ids, self.descriptions, matrix)
        return ['>{} {}\n{}'.format(sid, desc, ''.join(row)) if desc else
                '>{}\n{}'.format(sid, ''.join(row))
                for sid, desc, row in zipped]

    def remove_samples(self, i):
        """Removes sample sequences based on the given index.
        If index is a number, only one sequence is removed.
        If the index is a list of numbers, the sequence found at each row
        number is deleted.

        Parameters
        ----------
        i : int or list of int

        """
        if isinstance(i, int):
            return self.__class__.subset(self, rows=i)
        elif isinstance(i, str):
            # gets id index from id
            return self.__class__.subset(self, rows=self.ids.index(i))  
        elif isinstance(i, list):
            if len(i) == sum((isinstance(j, int) for j in i)):
                return self.__class__.subset(self, rows=i)
            elif len(i) == sum((isinstance(j, str) for j in i)):
                # get int position in self.ids and then use subset
                i = [self.ids.index(idx) for idx in i]
            else:
                raise ValueError('i must be a list of int or str')
        else:
            raise ValueError('i must be an int or str or a list of int or str')
        super().remove_samples(i)

    def get_sites(self, i):
        """Returns a new alignment matrix containing only the sites specified
        by the index.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        AlignmentMatrix

        """
        if isinstance(i, int):
            return self.__class__.subset(self, rows=i)
        # same as above
        elif isinstance(i, str):
            # gets id index from id
            return self.__class__.subset(self, rows=self.ids.index(i))
        elif isinstance(i, list):
            if len(i) == sum((isinstance(j, int) for j in i)):
                return self.__class__.subset(self, rows=i)
            else:
                raise ValueError('i must be a list of int')
        else:
            raise ValueError('i must be an int or str or a list of int or str')
        return self.__class__.subset(self, cols=i)

    def get_sites_as_str(self, i=None):
        """Returns a list of sequences as strings containing only the
        specified sites.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        list of str

        """
        if i is None:
            return [''.join(col) for col in self.matrix.T]
        return [''.join(col) for col in self.get_sites(i).matrix]

    def get_sites_as_fasta(self, i=None):
        """Returns a list of sequences as strings containing only the
        specified sites.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        list of str

        """
        matrix = self.matrix.T if i is None else self.get_sites(i).matrix
        return ['>{}\n{}'.format(i, ''.join(col))
                for i, col in enumerate(matrix)]

    def remove_sites(self, i):
        """Removes sites based on the given index.
        If index is a number, only one site is removed.
        If the index is a list of numbers, the sequence found at each column
        number is deleted.

        Parameters
        ----------
        i : int or list of int

        """
        super().remove_sites(i)

    def __str__(self):
        return '\n'.join(self.get_samples_as_fasta())


class SampleAlignment(BaseAlignment):
    """SampleAlignment represents a mulitple sequence alignment of
    biological sequences.
    """
    def __init__(self, sequence_list, dtype='<U1',
                 to_blocks_fn=None, from_blocks_fn=None,
                 custom_block_lists=None):
        super().__init__(sequence_list, dtype=dtype)
        # Set conversion functions
        self.custom_to_blocks_fn = to_blocks_fn
        self.custom_from_blocks_fn = from_blocks_fn
        # Generate sample block lists from sample descriptions
        if custom_block_lists:
            # TODO: Make a deepcopy method in Rust
            self.block_lists = copy_block_lists(custom_block_lists)
        else:
            self.block_lists = [self.to_blocks(desc)
                                for desc in self.descriptions]
        # Include block_lists in _metadata
        self._metadata = ('ids', 'descriptions', 'block_lists')

    def to_blocks(self, string):
        if not string:
            return []
        if self.custom_to_blocks_fn is None:
            return self.string_to_blocks(string)
        return self.custom_to_blocks_fn(string)

    def from_blocks(self, block_list):
        if not block_list:
            return ''
        if self.custom_from_blocks_fn is None:
            return self.blocks_to_string(block_list)
        return self.custom_from_blocks_fn(block_list)

    @staticmethod
    def string_to_blocks(string):
        if not string:
            return []
        tuple_list = (tuple(map(int, paired.split(':')))
                      for paired in string.split('_')[-1].split(';'))
        return [Block(tpl[0], tpl[1]) for tpl in tuple_list]

    @staticmethod
    def blocks_to_string(block_list):
        if not block_list:
            return ''
        return '{}_{}'.format(
            len(block_list), ';'.join([str(b) for b in block_list]),
        )


    @classmethod
    def subset(cls, aln, rows=None, cols=None, row_step=1, col_step=1):
        if rows is None:
            rows = range(0, aln.nsamples, row_step)
        else:
            if isinstance(rows, int):
                rows = [rows]
            if row_step != 1:
                raise ValueError('row_step value is considered only if rows' \
                                 'is None')
        if cols is None:
            cols = range(0, aln.nsites, col_step)
        else:
            if isinstance(cols, int):
                cols = [cols]
            if col_step != 1:
                raise ValueError('col_step value is considered only if cols ' \
                                 'is None')
        def f(seq, blist, drop_pos_lst):
            _, new_blist = remove_sites(seq, blist, drop_pos_lst)
            return new_blist

        # Creates a new SampleAlignment
        new_aln = cls.__new__(cls)
        # Copies custom functions
        new_aln.custom_to_blocks_fn = deepcopy(aln.custom_to_blocks_fn)
        new_aln.custom_from_blocks_fn = deepcopy(aln.custom_from_blocks_fn)
        # Copy the subset of the matrix
        new_aln.matrix = aln.matrix[rows][:, cols]
        # Copies metadata
        new_aln.ids = [v for i, v in enumerate(aln.ids) if i in rows]
        new_aln._metadata = aln._metadata  # copy tuple
        # Update block_lists
        drop_pos_lst = [i for i in range(aln.nsites) if i not in cols]
        seq_list = (row for row in aln.get_samples_as_str())
        new_aln.block_lists = [
            f(seq, blist, drop_pos_lst)
            for seq, blist in zip(seq_list, aln.block_lists)
        ]
        # Update descriptions
        new_aln.descriptions = [new_aln.from_blocks(blist)
                                for blist in new_aln.block_lists]
        return new_aln

    @classmethod
    def from_matrix(cls, matrix, ids, descriptions, block_lists,
                    to_blocks_fn=None, from_blocks_fn=None):
        # Create an empty SampleAlignment
        new_aln = cls.__new__(cls)
        new_aln.custom_to_blocks_fn = to_blocks_fn
        new_aln.custom_from_blocks_fn = from_blocks_fn
        # Assign values
        new_aln.ids = deepcopy(ids)
        new_aln.descriptions = deepcopy(descriptions)
        new_aln.block_lists = copy_block_lists(block_lists)  # deepcopy blocks
        new_aln._metadata = ('ids', 'descriptions', 'block_lists')
        # Copy the matrix
        new_aln.matrix = np.copy(matrix)
        return new_aln

    # TODO: Add a from_fasta method

    # TODO: Add a method that adds markers and makes this into an Alignment object


class MarkerAlignment(BaseAlignment):
    """MarkerAlignment represents one or more alignment markers of
    a multiple sequence alignment.
    """
    @property
    def nmarkers(self):
        """Returns the number of markers in the alignment.
        """
        return self.nsamples

    def get_markers(self, i):
        """Returns a new alignment matrix containing only the markers specified
        by the index.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        MarkerAlignment

        """
        return self.get_samples(i)

    def get_markers_as_str(self, i):
        """Returns a list of sequences as strings containing only the
        specified markers.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        list of str

        """
        return self.get_samples_as_str(i)

    def remove_markers(self, i):
        """Removes sites based on the given index.
        If index is a number, only one site is removed.
        If the index is a list of numbers, the sequence found at each column
        number is deleted.

        Parameters
        ----------
        i : int or list of int

        """
        return self.remove_samples(i)

    @classmethod
    def from_matrix(cls, matrix, ids, descriptions):
        # Create an empty SampleAlignment
        new_aln = cls.__new__(cls)
        # Assign values
        new_aln.ids = deepcopy(ids)
        new_aln.descriptions = deepcopy(descriptions)
        new_aln._metadata = ('ids', 'descriptions')
        # Copy the matrix
        new_aln.matrix = np.copy(matrix)
        return new_aln

class BinaryMarkerAlignment(MarkerAlignment):
    """BinaryAlignment represents an set of alignment markers that are
    encoded as 0's and 1's
    """
    def __init__(self, marker_list):
        """Creates a BinaryMarkerAlignment from a list of of Marker

        Parameters
        ----------
        marker_list : list of Marker

        """
        to_uint_fn = int  # assumes x is '0' or '1'
        from_uint_fn = str   # assumes x is int 0 or 1
        super().__init__(marker_list, to_uint_fn=to_uint_fn, 
                         from_uint_fn=from_uint_fn)


class Alignment:
    """Alignment is a complete representation of a multiple sequence alignment
    of biological sequences an their annotations such as alignment markers and
    alignment block data.
    """
    def __init__(self, sequence_list, marker_list, name=None,
                 sample_dtype='<U1', marker_dtype='<U1',
                 sample_to_blocks_fn=None, sample_from_blocks_fn=None,
                 marker_to_blocks_fn=None, marker_from_blocks_fn=None):
        """Creates a new Alignment object from a list of Sequence and Marker objects.

        Parameters
        ----------
        sequence_list : list of Sequence
        marker_list : list of Marker

        """
        self.name = name
        self._sample_aln = SampleAlignment(sequence_list, dtype=sample_dtype,
                                           to_blocks_fn=sample_to_blocks_fn, from_blocks_fn=sample_from_blocks_fn)
        self._marker_aln = MarkerAlignment(marker_list, dtype=marker_dtype)
        assert self._sample_aln.nsites == self._marker_aln.nsites

    @property
    def nsites(self):
        """Returns the number of sites in the alignment.
        """
        return self._sample_aln.nsites

    @property
    def nsamples(self):
        """Returns the number of samples in the alignment.
        """        
        return self._sample_aln.nsamples

    @property
    def nmarkers(self):
        """Returns the number of markers in the alignment
        """
        return self._marker_aln.nmarkers

    @property
    def samples(self):
        """Returns the sample alignment
        """
        return self._sample_aln

    @property
    def sample_matrix(self):
        """Returns the sample alignent matrix
        """
        return self._sample_aln.matrix

    @property
    def markers(self):
        """Returns the marker alignment
        """
        return self._marker_aln

    @property
    def marker_matrix(self):
        """Returns the marker alignment matrix
        """
        return self._marker_aln.matrix

    @classmethod
    def subset(cls, aln, sample_ids=None, marker_ids=None, sites=None,
               sample_id_step=1, marker_id_step=1, site_step=1):
        """Returns a subset of the alignment by samples, markers and sites.

        Parameters
        ----------
        aln : Alignment
        sample_ids : list
        marker_ids : list
        sites : list
        sample_id_step : int
        marker_id_step : int
        site_step : int

        Returns
        -------
        Alignment

        """
        if sample_ids is None:
            sample_ids = range(0, aln.nsamples, sample_id_step)
        else:
            if sample_id_step != 1:
                raise ValueError('sample_id_step value is considered only ' \
                                 'if sample_ids is None')
        if marker_ids is None:
            marker_ids = range(0, aln.nmarkers, marker_id_step)
        else:
            if marker_id_step != 1:
                raise ValueError('marker_id_step value is considered only ' \
                                 'if marker_ids is None')
        if sites is None:
            sites = range(0, aln.nsites, site_step)
        else:
            if site_step != 1:
                raise ValueError('site_step value is considered only ' \
                                 'if sites is None')
        new_aln = cls.__new__(cls)
        new_aln.name = aln.name
        new_aln._sample_aln = aln._sample_aln.__class__.subset(
            aln._sample_aln,
            rows=sample_ids, cols=sites,
            row_step=sample_id_step, col_step=site_step
        )
        new_aln._marker_aln = aln._marker_aln.__class__.subset(
            aln._marker_aln,
            rows=marker_ids, cols=sites,
            row_step=marker_id_step, col_step=site_step
        )
        return new_aln

    def replace_sample(self, sequence_str, i):
        """Replaces the sequence for a given row in the alignment matrix.

        Parameters
        ----------
        sequence_str : str
        i : int

        """
        self._sample_aln.replace_sample(sequence_str, i)

    def insert_samples(self, sequence_str, i):
        """Inserts a new sequence in the alignment matrix at the specified
        row position. This increases the total number of rows.

        Parameters
        ----------
        sequence_str : str or list of str
        i : int or list of int

        """
        self._sample_aln.insert_samples(sequence_str, i)

    def append_sample(self, sequence_str):
        """Inserts a new sequence after the last row of the alignment matrix.
        This increases the total number of rows by 1.

        Parameters
        ----------
        sequence_str : str

        """
        self._sample_aln.append_sample(sequence_str)

    def remove_samples(self, i):
        """Removes sample sequences based on the given index.
        If index is a number, only one sequence is removed.
        If the index is a list of numbers, the sequence found at each row
        number is deleted.

        Parameters
        ----------
        i : int or list of int

        """
        self._sample_aln.remove_samples(i)

    def insert_sites(self, sequence_str, i, marker_str=None):
        """Inserts a new sequence in the alignment matrix at the specified
        site position. This increases the total number of columns.

        Parameters
        ----------
        sequence_str : str or list of str
        i : int or list of int

        """
        if marker_str is None and self._marker_aln:
            assert ValueError('marker_str cannot be None if the alignment ' \
                              'has marker sequences')
        if (marker_str is not None) and (not self._marker_aln):
            assert ValueError('The alignment does not use marker sequences')
        self._sample_aln.insert_sites(sequence_str, i)
        if self._marker_aln:
            self._marker_aln.insert_sites(marker_str, i)

    def append_site(self, sequence_str, marker_str=None):
        """Inserts a new sequence at after the last column of the
        alignment matrix. This increases the total number of columns by 1.

        Parameters
        ----------
        sequence_str : str

        """
        if marker_str is None and self._marker_aln:
            assert ValueError('marker_str cannot be None if the alignment ' \
                              'has marker sequences')
        if (marker_str is not None) and (not self._marker_aln):
            assert ValueError('The alignment does not use marker sequences')
        self._sample_aln.append_site(sequence_str)
        if self._marker_aln:
            self._marker_aln.append_site(marker_str)

    def remove_sites(self, i):
        """Removes sites based on the given index.
        If index is a number, only one site is removed.
        If the index is a list of numbers, the sequence found at each column
        number is deleted.

        Parameters
        ----------
        i : int or list of int

        """
        self._sample_aln.remove_sites(i)
        if self._marker_aln:
            self._marker_aln.remove_sites(i)

    def get_samples(self, i):
        """Returns a list of sequence strings containing only the samples
        specified by the index.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        list of str

        """
        return self._sample_aln.get_samples(i)

    def get_markers(self, i):
        """Returns a list of sequence strings containing only the markers
        specified by the index.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        list of str

        """
        return self._marker_aln.get_samples(i)

    def get_sites(self, i):
        """Returns a new alignment containing only the sites specified
        by the index.

        Parameters
        ----------
        i : int or list of int

        Returns
        -------
        AlignmentMatrix

        """
        return self.__class__.subset(self, sites=i)

    @classmethod
    def from_fasta(cls, path, name=None, marker_kw=None,
                   sample_dtype='<U1', marker_dtype='<U1',
                   to_blocks_fn=None, from_blocks_fn=None):
        """Create an Alignment from a FASTA-formatted file.

        Parameters
        ----------
        path : str
            Path to FASTA file
        marker_kw : str, optional
            A sample is considered a marker if this keyword is present
            within the sequence ID
        sample_to_uint_fn : function, optional
        uint_to_sample_fn : function, optional
        marker_to_uint_fn : function, optional
        uint_to_marker_fn : function, optional

        Raises
        ------
        TypeError

        Returns
        -------
        Alignment

        """
        return fasta_file_to_alignment(
            path, name=name, marker_kw=marker_kw,
            sample_dtype=sample_dtype, marker_dtype=marker_dtype,
            to_blocks_fn=to_blocks_fn, from_blocks_fn=from_blocks_fn)

    def to_fasta(self, path):
        """Saves the alignment as a FASTA-formatted text file.

        Parameters
        ----------
        path : str

        """
        with open(path, 'w') as writer:
            print(self, file=writer)

    @classmethod
    def from_matrices(cls, sample_matrix, sample_ids, sample_descriptions,
                      sample_blocks_list, marker_matrix, marker_ids,
                      marker_descriptions, name=None,
                      to_blocks_fn=None,
                      from_blocks_fn=None):
        new_aln = cls.__new__(cls)
        new_aln.name = name
        new_aln._sample_aln = SampleAlignment.from_matrix(
            sample_matrix, sample_ids, sample_descriptions, sample_blocks_list,
            to_blocks_fn=to_blocks_fn, from_blocks_fn=from_blocks_fn)
        new_aln._marker_aln = MarkerAlignment.from_matrix(
            marker_matrix, marker_ids, marker_descriptions)
        return new_aln

    def __repr__(self):
        return '{}(nsamples={}, nsites={}, nmarkers={})'.format(
            self.__class__.__name__,
            self.nsamples,
            self.nsites,
            self.nmarkers
        )

    def __str__(self):
        return '\n'.join([str(self._sample_aln), str(self._marker_aln)])


class CatAlignment(Alignment):
    """CatAlignment represents a superalignment of 2 or more
    alignments concatenated together laterally.
    """
    def __init__(self, sequence_list, marker_list, catblocks, 
                 block_lists_map=None, name=None,
                 sample_to_uint_fn=None, uint_to_sample_fn=None,
                 marker_to_uint_fn=None, uint_to_marker_fn=None):
        """Creates a new CatAlignment.

        Parameters
        ----------
        sequence_list : list of Sequence
        marker_list : list of Marker
        concat_list : list of CatBlock

        """
        super().__init__(sequence_list, marker_list, name=name,
                         sample_to_uint_fn=sample_to_uint_fn,
                         uint_to_sample_fn=uint_to_sample_fn,
                         marker_to_uint_fn=marker_to_uint_fn,
                         uint_to_marker_fn=uint_to_marker_fn)
        self.catblocks = OrderedDict([(cb.id, self.catblocks[i])
                                      for i, cb in enumerate(catblocks)])
        self.block_lists_map = OrderedDict() if not block_lists_map else \
                               block_lists_map

    @classmethod
    def concatenate(cls, aln_list, aln_ids=None, use_aln_names=True):
        """Concatenates a list of Alignments into a single superalignment.

        Parameters
        ----------
        aln_list : list of Alignment
            [description]
        aln_ids : list, optional
            If specified, this list will be used as keys
            to access individual alignments.
        use_aln_names : bool, optional
            When aln_ids is None, determines what values to use
            as keys to access individual sequence alignments.
            If True, alignment names are used . If False,
            numbers from 0 corresponding to the position of the
            alignment in the alignment list will be used.

        Returns
        -------
        CatAlignment

        """
        start = 0
        def coords(sid, val):
            nonlocal start
            start += val
            return CatBlock(sid, start-val, start)
        # Create a new concat alignment
        new_aln = cls.__new__(cls)
        new_aln.name = 'concat_' + '_'.join([str(aln.name) for aln in aln_list])
        # Save alignment order
        # Put block lists in a mapping
        if aln_ids is not None:
            new_aln.catblocks = OrderedDict([
                (i, coords(i, v.nsites)) for i, v in zip(aln_ids, aln_list)])
            new_aln.block_lists_map = OrderedDict([
                (i, copy_block_lists(v.samples.block_lists))
                for i, v in zip(aln_ids, aln_list)])
        elif use_aln_names:
            new_aln.catblocks = OrderedDict([
                (v.name, coords(v.name, v.nsites)) for v in aln_list])
            new_aln.block_lists_map = OrderedDict([
                (v.name, copy_block_lists(v.samples.block_lists))
                for v in aln_list])
        else:
            new_aln.catblocks = OrderedDict([
                (i, coords(i, v.nsites)) for i, v in enumerate(aln_list)])
            new_aln.block_lists_map = OrderedDict([
                (i, copy_block_lists(v.samples.block_lists))
                for i, v in enumerate(aln_list)])
        # Create new concatenated block lists
        total_sites = sum((aln.nsites for aln in aln_list))
        concat_block_lists = [[Block(0, total_sites)]
                              for i in range(aln_list[0].nsamples)]
        # Create new sample alignment from matrix
        new_aln._sample_aln = SampleAlignment.from_uint_matrix(
            np.concatenate([aln.sample_matrix for aln in aln_list], axis=1),
            aln_list[0].samples.ids,
            [','.join([str(aln.name) for aln in aln_list])] * \
                len(aln_list[0].samples.descriptions),  # replaces desc
            concat_block_lists,  # empties block list
            to_uint_fn=aln_list[0].samples.custom_to_uint_fn,
            from_uint_fn=aln_list[0].samples.custom_from_uint_fn,
            to_block_fn=aln_list[0].samples.custom_to_block_fn,
            from_block_fn=aln_list[0].samples.custom_from_block_fn,
        )
        # Create new marker alignment from matrix
        new_aln._marker_aln = MarkerAlignment.from_uint_matrix(
            np.concatenate([aln.marker_matrix for aln in aln_list], axis=1),
            aln_list[0].markers.ids,
            aln_list[1].markers.descriptions,
            to_uint_fn=aln_list[0].samples.custom_to_uint_fn,
            from_uint_fn=aln_list[0].samples.custom_from_uint_fn,
        )
        return new_aln

    @classmethod
    def from_fasta(cls, path, name=None, marker_kw=None,
                   block_lists_map=None,
                   sample_to_uint_fn=None, uint_to_sample_fn=None,
                   marker_to_uint_fn=None, uint_to_marker_fn=None):
        """Create a CatAlignment from a FASTA-formatted file.

        Parameters
        ----------
        path : str
            Path to FASTA file
        marker_kw : str, optional
            A sample is considered a marker if this keyword is present
            within the sequence ID
        sample_to_uint_fn : function, optional
        uint_to_sample_fn : function, optional
        marker_to_uint_fn : function, optional
        uint_to_marker_fn : function, optional

        Raises
        ------
        TypeError

        Returns
        -------
        Alignment

        """
        sequence_list = []
        marker_list = []
        for item in fasta_file_to_list(path, marker_kw=marker_kw):
            if isinstance(item, Sequence):
                sequence_list.append(item)
            elif isinstance(item, Marker):
                marker_list.append(item)
            else:
                raise TypeError('expected Sequence or Marker object')
        catblocks = string_to_catblocks(sequence_list[0].description.rstrip())
        return cls(sequence_list, marker_list, catblocks, name=name,
                   block_lists_map=block_lists_map,
                   sample_to_uint_fn=sample_to_uint_fn,
                   uint_to_sample_fn=uint_to_sample_fn,
                   marker_to_uint_fn=marker_to_uint_fn,
                   uint_to_marker_fn=uint_to_marker_fn)

    def to_fasta(self, path, catblocks_path=None, block_lists_path=None):
        """Saves the concatenated alignment as a FASTA-formatted text file.
        Catblocks and block lists can also be simultaneously saves as
        tab-delimitted files.

        Parameters
        ----------
        path : str
        catblocks_path : str, optional
        block_lists_path : str, optional

        """
        # Overwrite descriptions with catblocks
        self.samples.descriptions = [catblocks_to_string(self.catblocks)
                                     for i in self.nsamples]
        if catblocks_path:
            with open(catblocks_path, 'w') as cb_writer:
                print('{}\t{}\t{}'.format('name', 'start', 'stop'), 
                      file=cb_writer)
                for cb in self.catblocks.values():
                    print('{}\t{}\t{}'.format(cb.name, cb.start, cb.stop), 
                          file=cb_writer)
        if block_lists_path:
            with open(block_lists_path, 'w') as b_writer:
                print('{}\t{}\t{}'.format('name', 'start', 'stop'), 
                      file=b_writer)
                for name, blist in self.block_lists_map.items():
                    for b in blist:
                        print('{}\t{}\t{}'.format(name, b.start, b.stop),
                              file=b_writer)
        with open(path, 'w') as writer:
            print(self, file=writer)

    def get_alignment(self, name):
        """Return the subalignment by name or key.

        Parameters
        ----------
        name : int or str
            Name assigned to the alignment during concatenation.

        Raises
        ------
        IndexError
            Returns an IndexError when the given name does not
            match any alignment key.

        Returns
        -------
        Alignment

        """

        if name not in self.catblocks:
            raise IndexError("name not found")
        _, start, stop = self.catblocks[name]
        aln = Alignment.subset(self, sites=range(start, stop))
        aln.name = 'subaln_{}'.format(name)
        aln.samples.block_lists = copy_block_lists(self.block_lists_map[name])
        return aln

    def splitg(self):
        """Splits the concatenated superalignment into individual subalignments
        and returns a generator.

        Yields
        ------
        Alignment

        """

        return (Alignment.subset(self, sites=range(cb.start, cb.stop))
                for cb in self.catblocks)

    def split(self):
        """Splits the concatenated superalignment as a list of its
        individual subalignments.

        Returns
        -------
        list of Alignment

        """
        return list(self.splitg())


def fasta_file_to_list(path, marker_kw=None):
    """Reads a FASTA formatted text file to a list.

    Parameters
    ----------
    path : str

    Returns
    -------
    list of tuple

    """
    name = ''
    description = ''
    _seq = ''
    seq_list = []
    with open(path, 'r') as f:  # pylint: disable=invalid-name
        for line in f.readlines():
            line = line.rstrip()
            if line.startswith('>'):
                # Store sequence if _seq has contents
                if _seq:
                    if marker_kw:
                        if marker_kw in name:
                            seq = Marker(name, description, _seq)
                        else:
                            seq = Sequence(name, description, _seq)
                    else:
                        seq = Sequence(name, description, _seq)
                    seq_list.append(seq)
                    _seq = ''
                # Split id and description
                try:
                    name, description = line[1:].split(' ', 1)
                except ValueError:
                    name = line[1:]
                    description = ''
            else:
                _seq += line
        if _seq:
            if marker_kw:
                if marker_kw in name:
                    seq = Marker(name, description, _seq)
                else:
                    seq = Sequence(name, description, _seq)
            else:
                seq = Sequence(name, description, _seq)
            seq_list.append(seq)
    return seq_list


def fasta_file_to_lists(path, marker_kw=None, char_length=1):
    """Reads a FASTA formatted text file to a list.

    Parameters
    ----------
    path : str

    Returns
    -------
    list of tuple

    """
    name = ''
    description = ''
    _seq = ''
    seq_ids = []
    seq_descriptions = []
    seq_list = []
    marker_ids = []
    marker_descriptions = []
    marker_list = []
    with open(path, 'r') as f:  # pylint: disable=invalid-name
        for line in f.readlines():
            line = line.rstrip()
            if line.startswith('>'):
                # Store sequence if _seq has contents
                if _seq:
                    if marker_kw:
                        if marker_kw in name:
                            marker_ids.append(name)
                            marker_descriptions.append(description)
                            # TODO: Implement char_length
                            marker_list.append(list(_seq))
                        else:
                            seq_ids.append(name)
                            seq_descriptions.append(description)
                            seq_list.append(list(_seq))
                    else:
                        seq_ids.append(name)
                        seq_descriptions.append(description)
                        seq_list.append(list(_seq))
                    _seq = ''
                # Split id and description
                try:
                    name, description = line[1:].split(' ', 1)
                except ValueError:
                    name = line[1:]
                    description = ''
            else:
                _seq += line
        if _seq:
            if marker_kw:
                if marker_kw in name:
                    marker_ids.append(name)
                    marker_descriptions.append(description)
                    marker_list.append(list(_seq))
                else:
                    seq_ids.append(name)
                    seq_descriptions.append(description)
                    seq_list.append(list(_seq))
            else:
                seq_ids.append(name)
                seq_descriptions.append(description)
                seq_list.append(list(_seq))
    return {'sample_ids': seq_ids,
            'sample_descriptions': seq_descriptions,
            'sample_sequences': seq_list,
            'marker_ids': marker_ids,
            'marker_descriptions': marker_descriptions,
            'marker_sequences': marker_list}


def fasta_file_to_alignment(path, marker_kw=None, name=None,
                            sample_dtype='<U1', marker_dtype='<U1',
                            to_blocks_fn=None, from_blocks_fn=None):
    """Reads a FASTA formatted text file into an Alignment object.

    Parameters
    ----------
    path : str

    Returns
    -------
    list of tuple

    """
    d = fasta_file_to_lists(path, marker_kw=marker_kw)
    sample_matrix = np.array(d['sample_sequences'], dtype=sample_dtype)
    marker_matrix = np.array(d['marker_sequences'], dtype=marker_dtype)
    if to_blocks_fn is None:
        blocks_list = [SampleAlignment.string_to_blocks(s)
                       for s in d['sample_descriptions']]
    else:
        blocks_list = [to_blocks_fn(s) for s in d['sample_descriptions']]
    return Alignment.from_matrices(
        sample_matrix, d['sample_ids'], d['sample_descriptions'], blocks_list,
        marker_matrix, d['marker_ids'], d['marker_descriptions'], name=name,
        to_blocks_fn=to_blocks_fn, from_blocks_fn=from_blocks_fn)


def copy_block_lists(block_lists):
    return [[Block(b.start, b.stop) for b in blist] for blist in block_lists]

def catblocks_to_string(catblock_list):
    return ';'.join([str(cb) for cb in catblock_list])

def string_to_catblocks(string, int_names=False):
    catblocks_raw = re.findall(r'(\S+?)\=(\d+?)\:(\d+?)', string)
    if int_names:
        return [CatBlock(int(i[0]), int(i[1]), int(i[2]))
                for i in catblocks_raw]
    return [CatBlock(i[0], int(i[1]), int(i[2])) for i in catblocks_raw]
