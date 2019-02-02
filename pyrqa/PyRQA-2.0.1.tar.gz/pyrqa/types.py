#!/usr/bin/env python

"""
Types.
"""

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


class MatrixRepresentation(object):
    """
    Representation of the matrix data.
    """
    class Uncompressed(object):
        """
        Dense matrix representation.
        """
        pass

    class CSC(object):
        """
        Compressed sparse column matrix representation.
        """
        pass

    class CSR(object):
        """
        Compressed sparse row matrix representation.
        """
        pass


class Tree(object):
    """
    Space partitioning tree.
    """
    class KDTree(object):
        """
        k-d-tree.
        """
        pass

    class BallTree(object):
        """
        Ball tree.
        """
        pass
