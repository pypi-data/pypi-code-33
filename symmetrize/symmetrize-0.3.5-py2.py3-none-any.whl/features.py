#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: R. Patrick Xian
"""

from . import sym, tps, pointops as po
import numpy as np


class FeatureGenerator(object):
    """ Class for generating 2D features based on given symmetry operations.
    """

    def __init__(self, features):

        self.features = features # features grouped in a nested dictionary

    def addRotationCenter(self, pos, fold):
        """ Add a 2D rotation center to the feature set.
        """

        self.rotcenter = pos
        self.rotfold = fold

    def addInversionCenter(self, pos):
        """ Add a 2D inversion center to the feature set.
        """

        self.addRotationCenter(pos, fold=2)

    def addMirrorPlane(self, axvec=None, pos=None):
        """ Add a 2D mirror plane to the feature set.
        """

        if axvec is not None:
            self.mirrorAxisVector = axvec
            self.pos = []
        elif pos is not None:
            self.pos = pos
            self.mirrorAxisVector = pos[1, :] - pos[0, :]
        else:
            raise ValueError('Need to specify at least a mirror plane vector or '+
            'two point positions in order to add a mirror plane symmetry element!')

    def addSymmetryOperations(self):

        pass

    def genRotationElements(self, points, center, fold):

        pass

    def genInversionElements(self, points, center):

        pass

    def genMirrorElements(self, points, axvec):

        pass

    def generate(self):
        """ Generate point correspondences using symmetry operations.
        """

        for feat_key, feat_val in self.features.items():
            if 'rot' in feat_key:
                pass
            elif 'inv' in feat_key:
                pass
            elif 'mirror' in feat_key:
                pass


class Symmetrizer(FeatureGenerator):

    def __init__(self, features):

        super().__init__(features=features)

    def reference(self):
        """ Reference point set.
        """

        pass

    def target(self):
        """ Target point set.
        """

        pass

    def symmetrize(self, method, **kwds):
        """ Perform symmetrization using specified method.
        """

        if method == 'proj':
            pass
        elif method == 'iter_proj':
            pass
        elif method == 'tps':
            pass
        elif method == 'iter_tps':
            pass
