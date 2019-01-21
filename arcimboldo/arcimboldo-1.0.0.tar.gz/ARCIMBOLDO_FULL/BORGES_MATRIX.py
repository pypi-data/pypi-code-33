#! /usr/bin/env python
# -*- coding: utf-8 -*-

#future imports
from __future__ import print_function
from __future__ import division
#from __future__ import unicode_literals

# System imports
import os
import sys
import stat

#####################################################################
# All the functions in this module were written by:                 #
# author: Massimo Sammito                                           #
# email: msacri@ibmb.csic.es / massimo.sammito@gmail.com            #
#####################################################################


info_p = sys.version_info
info_g = (sys.version).splitlines()
PYTHON_V = info_p.major

import argparse
import warnings
import time
import datetime
import copy
import traceback
import shutil
import subprocess
import multiprocessing
import threading
import io
import tempfile
import re

if PYTHON_V == 3:
    import configparser
elif PYTHON_V == 2:
    import ConfigParser

# format imports
import json
import pickle
import tarfile
import gzip
import shelve

# graphics
import matplotlib

matplotlib.use('Agg')
# matplotlib.use('TkAgg')
from termcolor import colored, cprint
import matplotlib.pyplot as plt
import pylab
if PYTHON_V == 3:
    from pyqtgraph.Qt import QtGui, QtCore, USE_PYSIDE, USE_PYQT5

# Scientific and numerical imports
import math
import numpy
import random
import scipy
import scipy.spatial
import scipy.sparse
import scipy.cluster
import scipy.special
import sklearn
import sklearn.preprocessing
import igraph
import igraph.vendor.texttable
import Bio.PDB
from Bio import pairwise2
from Bio.SubsMat import MatrixInfo as matlist
from Bio import SeqIO
import itertools
import sklearn.metrics
import sklearn.cluster

# personal libraries imports
import Bioinformatics3
if PYTHON_V == 3:
    import Graphics
import SystemUtility
import Grid

warnings.simplefilter("ignore", Bio.PDB.PDBExceptions.PDBConstructionWarning)
#warnings.simplefilter("ignore", DeprecationWarning)

#######################################################################################################
#                                           CONSTANT VARIABLES                                         #
#######################################################################################################

color_dict = {}
list_ids = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
kn = list(igraph.drawing.colors.known_colors.keys())
numpy.random.shuffle(kn)
for h, idn in enumerate(list_ids):
    color_dict[idn] = kn[h]

SCALING = "min_max"
# :(0.5,0.1,0.3),"min_max":(0.5,0.1,0.3)}
THRESH_CORR = {"robust_scale":{"isomorphism_ladder":0.7,"compare_signatures":0.1,"remove_redundance_chain":0.0005,"compare_instruction":0.005,"total_ladder":1.5,"filter_bipartite":0.45,"acceptable_sum_score":0.4},
               "min_max":     {"isomorphism_ladder":0.7,"compare_signatures":0.1,"remove_redundance_chain":0.0005,"compare_instruction":0.005,"total_ladder":3.4,"filter_bipartite":1.5,"acceptable_sum_score":0.3}} #"filter_bipartite":0.25,"total_ladder":1.4,"isomorphism_ladder":0.5

BS_UU_EA = {0: 24.6315759411, 1: 24.6315759411, 2: 24.6315759411, 3: 24.6315759411, 4: 24.6315759411, 5: 24.6315759411, 6: 24.6315759411, 7: 24.6315759411, 8: 24.6315759411, 9: 24.6315759411, 10: 25.181356029, 11: 25.181356029, 12: 25.181356029, 13: 25.181356029, 14: 25.181356029, 15: 25.181356029, 16: 25.181356029, 17: 25.181356029, 18: 25.181356029, 19: 25.181356029, 20: 19.4507911121, 21: 19.4507911121, 22: 19.4507911121, 23: 19.4507911121, 24: 19.4507911121, 25: 19.4507911121, 26: 19.4507911121, 27: 19.4507911121, 28: 19.4507911121, 29: 19.4507911121, 30: 11.3597418176, 31: 11.3597418176, 32: 11.3597418176, 33: 11.3597418176, 34: 11.3597418176, 35: 11.3597418176, 36: 11.3597418176, 37: 11.3597418176, 38: 11.3597418176, 39: 11.3597418176, 40: 7.02861712458, 41: 7.02861712458, 42: 7.02861712458, 43: 7.02861712458, 44: 7.02861712458, 45: 7.02861712458, 46: 7.02861712458, 47: 7.02861712458, 48: 7.02861712458, 49: 7.02861712458, 50: 4.80950476952, 51: 4.80950476952, 52: 4.80950476952, 53: 4.80950476952, 54: 4.80950476952, 55: 4.80950476952, 56: 4.80950476952, 57: 4.80950476952, 58: 4.80950476952, 59: 4.80950476952, 60: 2.9131204661, 61: 2.9131204661, 62: 2.9131204661, 63: 2.9131204661, 64: 2.9131204661, 65: 2.9131204661, 66: 2.9131204661, 67: 2.9131204661, 68: 2.9131204661, 69: 2.9131204661, 70: 2.2662363626, 71: 2.2662363626, 72: 2.2662363626, 73: 2.2662363626, 74: 2.2662363626, 75: 2.2662363626, 76: 2.2662363626, 77: 2.2662363626, 78: 2.2662363626, 79: 2.2662363626, 80: 1.00816816131, 81: 1.00816816131, 82: 1.00816816131, 83: 1.00816816131, 84: 1.00816816131, 85: 1.00816816131, 86: 1.00816816131, 87: 1.00816816131, 88: 1.00816816131, 89: 1.00816816131, 90: 0.658308105329, 91: 0.658308105329, 92: 0.658308105329, 93: 0.658308105329, 94: 0.658308105329, 95: 0.658308105329, 96: 0.658308105329, 97: 0.658308105329, 98: 0.658308105329, 99: 0.658308105329, 100: 0.26275204204, 101: 0.26275204204, 102: 0.26275204204, 103: 0.26275204204, 104: 0.26275204204, 105: 0.26275204204, 106: 0.26275204204, 107: 0.26275204204, 108: 0.26275204204, 109: 0.26275204204, 110: 0.145656023305, 111: 0.145656023305, 112: 0.145656023305, 113: 0.145656023305, 114: 0.145656023305, 115: 0.145656023305, 116: 0.145656023305, 117: 0.145656023305, 118: 0.145656023305, 119: 0.145656023305, 120: 0.129948020792, 121: 0.129948020792, 122: 0.129948020792, 123: 0.129948020792, 124: 0.129948020792, 125: 0.129948020792, 126: 0.129948020792, 127: 0.129948020792, 128: 0.129948020792, 129: 0.129948020792, 130: 0.0842520134803, 131: 0.0842520134803, 132: 0.0842520134803, 133: 0.0842520134803, 134: 0.0842520134803, 135: 0.0842520134803, 136: 0.0842520134803, 137: 0.0842520134803, 138: 0.0842520134803, 139: 0.0842520134803, 140: 0.0514080082253, 141: 0.0514080082253, 142: 0.0514080082253, 143: 0.0514080082253, 144: 0.0514080082253, 145: 0.0514080082253, 146: 0.0514080082253, 147: 0.0514080082253, 148: 0.0514080082253, 149: 0.0514080082253, 150: 0.0114240018278, 151: 0.0114240018278, 152: 0.0114240018278, 153: 0.0114240018278, 154: 0.0114240018278, 155: 0.0114240018278, 156: 0.0114240018278, 157: 0.0114240018278, 158: 0.0114240018278, 159: 0.0114240018278, 160: 0.0071400011424, 161: 0.0071400011424, 162: 0.0071400011424, 163: 0.0071400011424, 164: 0.0071400011424, 165: 0.0071400011424, 166: 0.0071400011424, 167: 0.0071400011424, 168: 0.0071400011424, 169: 0.0071400011424, 170: 0.0, 171: 0.0, 172: 0.0, 173: 0.0, 174: 0.0, 175: 0.0, 176: 0.0, 177: 0.0, 178: 0.0, 179: 0.0, 180: 0.0}
BS_UD_EA = {0: 0.00200625952973, 1: 0.00200625952973, 2: 0.00200625952973, 3: 0.00200625952973, 4: 0.00200625952973, 5: 0.00200625952973, 6: 0.00200625952973, 7: 0.00200625952973, 8: 0.00200625952973, 9: 0.00200625952973, 10: 0.0170532060027, 11: 0.0170532060027, 12: 0.0170532060027, 13: 0.0170532060027, 14: 0.0170532060027, 15: 0.0170532060027, 16: 0.0170532060027, 17: 0.0170532060027, 18: 0.0170532060027, 19: 0.0170532060027, 20: 0.00702190835406, 21: 0.00702190835406, 22: 0.00702190835406, 23: 0.00702190835406, 24: 0.00702190835406, 25: 0.00702190835406, 26: 0.00702190835406, 27: 0.00702190835406, 28: 0.00702190835406, 29: 0.00702190835406, 30: 0.0060187785892, 31: 0.0060187785892, 32: 0.0060187785892, 33: 0.0060187785892, 34: 0.0060187785892, 35: 0.0060187785892, 36: 0.0060187785892, 37: 0.0060187785892, 38: 0.0060187785892, 39: 0.0060187785892, 40: 0.00702190835406, 41: 0.00702190835406, 42: 0.00702190835406, 43: 0.00702190835406, 44: 0.00702190835406, 45: 0.00702190835406, 46: 0.00702190835406, 47: 0.00702190835406, 48: 0.00702190835406, 49: 0.00702190835406, 50: 0.0230719845919, 51: 0.0230719845919, 52: 0.0230719845919, 53: 0.0230719845919, 54: 0.0230719845919, 55: 0.0230719845919, 56: 0.0230719845919, 57: 0.0230719845919, 58: 0.0230719845919, 59: 0.0230719845919, 60: 0.0290907631811, 61: 0.0290907631811, 62: 0.0290907631811, 63: 0.0290907631811, 64: 0.0290907631811, 65: 0.0290907631811, 66: 0.0290907631811, 67: 0.0290907631811, 68: 0.0290907631811, 69: 0.0290907631811, 70: 0.0642003049514, 71: 0.0642003049514, 72: 0.0642003049514, 73: 0.0642003049514, 74: 0.0642003049514, 75: 0.0642003049514, 76: 0.0642003049514, 77: 0.0642003049514, 78: 0.0642003049514, 79: 0.0642003049514, 80: 0.155485113554, 81: 0.155485113554, 82: 0.155485113554, 83: 0.155485113554, 84: 0.155485113554, 85: 0.155485113554, 86: 0.155485113554, 87: 0.155485113554, 88: 0.155485113554, 89: 0.155485113554, 90: 0.489527325255, 91: 0.489527325255, 92: 0.489527325255, 93: 0.489527325255, 94: 0.489527325255, 95: 0.489527325255, 96: 0.489527325255, 97: 0.489527325255, 98: 0.489527325255, 99: 0.489527325255, 100: 1.53880105931, 101: 1.53880105931, 102: 1.53880105931, 103: 1.53880105931, 104: 1.53880105931, 105: 1.53880105931, 106: 1.53880105931, 107: 1.53880105931, 108: 1.53880105931, 109: 1.53880105931, 110: 4.22117005056, 111: 4.22117005056, 112: 4.22117005056, 113: 4.22117005056, 114: 4.22117005056, 115: 4.22117005056, 116: 4.22117005056, 117: 4.22117005056, 118: 4.22117005056, 119: 4.22117005056, 120: 10.0764384881, 121: 10.0764384881, 122: 10.0764384881, 123: 10.0764384881, 124: 10.0764384881, 125: 10.0764384881, 126: 10.0764384881, 127: 10.0764384881, 128: 10.0764384881, 129: 10.0764384881, 130: 14.2544739588, 131: 14.2544739588, 132: 14.2544739588, 133: 14.2544739588, 134: 14.2544739588, 135: 14.2544739588, 136: 14.2544739588, 137: 14.2544739588, 138: 14.2544739588, 139: 14.2544739588, 140: 18.0824171415, 141: 18.0824171415, 142: 18.0824171415, 143: 18.0824171415, 144: 18.0824171415, 145: 18.0824171415, 146: 18.0824171415, 147: 18.0824171415, 148: 18.0824171415, 149: 18.0824171415, 150: 17.8075595859, 151: 17.8075595859, 152: 17.8075595859, 153: 17.8075595859, 154: 17.8075595859, 155: 17.8075595859, 156: 17.8075595859, 157: 17.8075595859, 158: 17.8075595859, 159: 17.8075595859, 160: 18.9531337774, 161: 18.9531337774, 162: 18.9531337774, 163: 18.9531337774, 164: 18.9531337774, 165: 18.9531337774, 166: 18.9531337774, 167: 18.9531337774, 168: 18.9531337774, 169: 18.9531337774, 170: 14.2655083862, 171: 14.2655083862, 172: 14.2655083862, 173: 14.2655083862, 174: 14.2655083862, 175: 14.2655083862, 176: 14.2655083862, 177: 14.2655083862, 178: 14.2655083862, 179: 14.2655083862, 180: 14.2655083862}
BS_MAX = {0:max(BS_UD_EA.values()), 1:max(BS_UU_EA.values())}
SIGNATURE_ANGLE_BS = False

atom_weights = {
    'H': 1.00794,
    'He': 4.002602,
    'Li': 6.941,
    'Be': 9.012182,
    'B': 10.811,
    'C': 12.0107,
    'N': 14.0067,
    'O': 15.9994,
    'F': 18.9984032,
    'Ne': 20.1797,
    'Na': 22.989770,
    'Mg': 24.3050,
    'Al': 26.981538,
    'Si': 28.0855,
    'P': 30.973761,
    'S': 32.065,
    'Cl': 35.453,
    'Ar': 39.948,
    'K': 39.0983,
    'Ca': 40.078,
    'Sc': 44.955910,
    'Ti': 47.867,
    'V': 50.9415,
    'Cr': 51.9961,
    'Mn': 54.938049,
    'Fe': 55.845,
    'Co': 58.933200,
    'Ni': 58.6934,
    'Cu': 63.546,
    'Zn': 65.39,
    'Ga': 69.723,
    'Ge': 72.64,
    'As': 74.92160,
    'Se': 78.96,
    'Br': 79.904,
    'Kr': 83.80,
    'Rb': 85.4678,
    'Sr': 87.62,
    'Y': 88.90585,
    'Zr': 91.224,
    'Nb': 92.90638,
    'Mo': 95.94,
    'Tc': 98.0,
    'Ru': 101.07,
    'Rh': 102.90550,
    'Pd': 106.42,
    'Ag': 107.8682,
    'Cd': 112.411,
    'In': 114.818,
    'Sn': 118.710,
    'Sb': 121.760,
    'Te': 127.60,
    'I': 126.90447,
    'Xe': 131.293,
    'Cs': 132.90545,
    'Ba': 137.327,
    'La': 138.9055,
    'Ce': 140.116,
    'Pr': 140.90765,
    'Nd': 144.24,
    'Pm': 145.0,
    'Sm': 150.36,
    'Eu': 151.964,
    'Gd': 157.25,
    'Tb': 158.92534,
    'Dy': 162.50,
    'Ho': 164.93032,
    'Er': 167.259,
    'Tm': 168.93421,
    'Yb': 173.04,
    'Lu': 174.967,
    'Hf': 178.49,
    'Ta': 180.9479,
    'W': 183.84,
    'Re': 186.207,
    'Os': 190.23,
    'Ir': 192.217,
    'Pt': 195.078,
    'Au': 196.96655,
    'Hg': 200.59,
    'Tl': 204.3833,
    'Pb': 207.2,
    'Bi': 208.98038,
    'Po': 208.98,
    'At': 209.99,
    'Rn': 222.02,
    'Fr': 223.02,
    'Ra': 226.03,
    'Ac': 227.03,
    'Th': 232.0381,
    'Pa': 231.03588,
    'U': 238.02891,
    'Np': 237.05,
    'Pu': 244.06,
    'Am': 243.06,
    'Cm': 247.07,
    'Bk': 247.07,
    'Cf': 251.08,
    'Es': 252.08,
    'Fm': 257.10,
    'Md': 258.10,
    'No': 259.10,
    'Lr': 262.11,
    'Rf': 261.11,
    'Db': 262.11,
    'Sg': 266.12,
    'Bh': 264.12,
    'Hs': 269.13,
    'Mt': 268.14,
}

FINISHED = False
PATH_NEW_BORGES = ""
GRID_TYPE = ""
MAX_PDB_TAR = 5.0
NUMBER_OF_PARALLEL_GRID_JOBS = 70000
GLOBAL_MAXIMUM = 1000
number_of_solutions = 0
canCluster = True
doCluster_global = True
listjobs = []
toclientdir = ""
list_ncs_dictio = []

#######################################################################################################
#                                           SUPPORT FUNC                                              #
#######################################################################################################

#######################################################################################################
#                                           GEOMETRICAL FUNC                                          #
#######################################################################################################

def get_dot_between(A, B):
    """
    Return the dot product between two vectors
    :param A: A vector
    :type A: numpy.array
    :param B: B vector
    :type B: numpy.array
    :return dot: dot product
    :rtype: float
    """

    return (A * B).sum(axis=0)


def norm(A):
    return numpy.sqrt((A ** 2).sum(axis=0))


# @SystemUtility.profileit
# @SystemUtility.timing
def angle_between(A, B, N, signed=True):
    """
    ANGLE BETWEEN TWO 3D VECTORS:
    1- dot(norm(A),norm(B)) (ANGLES UNSIGNED, PROBLEMS FOR SMALL ANGLES WITH ROUNDINGS)
    2- arcos(dot(A,B)/(|A|*|B|))  (ANGLE UNSIGNED, PROBLEMS FOR SMALL ANGLES WITH ROUNDINGS)
    3- arctan2(|cross(A,B)|,dot(A,B)) (ANGLE UNSIGNED BUT NOT PROBLEMS OF ROUNDINGS
    Method 2 and 3 are equivalent: TESTED
      define a vector NORM ex.: N = [0,0,1]
      sign = dot(NORM,cross(A,B))
      if sign < 0 then ANGLE measured in 3 should be negative

    :param A: array coordinate first vector
    :type A: numpy.array
    :param B: array coordinate second vector
    :type B: numpy.array
    :param N: array coordinate normal direction
    :type N: numpy.array
    :param signed: True if signed angle should be returned, False otherwise
    :type signed: bool
    :return angle: the angle between A and B 
    :rtype angle: float
    """

    # Cross = numpy.cross(A,B) ### this is 5 times slower according cProfiler,

    CrossX = A[1] * B[2] - A[2] * B[1]
    CrossY = A[2] * B[0] - A[0] * B[2]
    CrossZ = A[0] * B[1] - A[1] * B[0]
    Cross = numpy.asarray([CrossX, CrossY, CrossZ])

    fCross = numpy.sqrt((Cross ** 2).sum(axis=0))
    scaP2 = get_dot_between(A, B)
    Teta_2 = numpy.arctan2(fCross, scaP2)

    if signed:
        sign = get_dot_between(N, Cross)
        if sign < 0:
            Teta_2 = -Teta_2

        return Teta_2
    else:
        return Teta_2


def angle_between_by_acos(A, B):
    return numpy.arccos(get_dot_between(A, B) / (norm(A) * norm(B)))


def get_atoms_distance(in_a, in_b):
    """
    Return the euclidean distance between the two 3d coordinates
    :param in_a: 3d coord a
    :type in_a: numpy.array
    :param in_b: 3d coord b
    :type in_b: numpy.array
    :return d,D: distance and vector distance 
    :rtype d,D: (float,numpy.array) 
    """

    D = in_a - in_b
    d = numpy.sqrt((D ** 2).sum(axis=0))
    return d, D


def cantor_pairing(listall):
    if len(listall) == 0:
        return None
    if len(listall) == 1:
        return listall[0]
    lastElement = listall.pop(0)
    return (0.5 * (cantor_pairing(listall) + lastElement) * (cantor_pairing(listall) + lastElement + 1) + lastElement)

def get_plane_from_3_points(x,y,z):
    a = ((y[1]-y[0])*(z[2]-z[0]))-((z[1]-z[0])*(y[2]-y[0]))
    b = -1 *(((x[1]-x[0])*(z[2]-z[0]))-((z[1]-z[0])*(x[2]-x[0])))
    c = ((x[1]-x[0])*(y[2]-y[0]))-((y[1]-y[0])*(x[2]-x[0]))
    d = -1* ((a*x[0])+(b*x[1])+(c*x[2]))

    return a,b,c,d


def get_plane_from_3_points_2(A,B,C):
    a = ((B[1]-A[1])*(C[2]-A[2]))-((C[1]-A[1])*(B[2]-A[2]))
    b = ((B[2]-A[2])*(C[0]-A[0]))-((C[2]-A[2])*(B[0]-A[0]))
    c = ((B[0]-A[0])*(C[1]-A[1]))-((C[0]-A[0])*(B[1]-A[1]))
    d = -1* ((a*A[0])+(b*A[1])+(c*A[2]))

    return a,b,c,d


def get_point_distance_from_plane(plane, q):
    a,b,c,d = plane
    dis = numpy.abs(((a*q[0])+(b*q[1])+(c*q[2]))+d)/numpy.sqrt((a**2)+(b**2)+(c**2))
    return dis

def center_of_mass(entity, geometric=False):
    """
    Returns gravitic [default] or geometric center of mass of an Entity.
    Geometric assumes all masses are equal (geometric=True)
    """
    global atom_weights

    # Structure, Model, Chain, Residue
    if isinstance(entity, Bio.PDB.Entity.Entity):
        atom_list = entity.get_atoms()
    # List of Atoms
    elif hasattr(entity, '__iter__') and [x for x in entity if x.level == 'A']:
        atom_list = entity
    else:  # Some other weirdo object
        raise ValueError("Center of Mass can only be calculated from the following objects:\n"
                         "Structure, Model, Chain, Residue, list of Atoms.")

    class COM:
        def __init__(self, coord):
            self.coord = coord

    positions = [[], [], []]  # [ [X1, X2, ..] , [Y1, Y2, ...] , [Z1, Z2, ...] ]
    masses = []

    for atom in atom_list:
        try:
            atom.mass = atom_weights[atom.element.capitalize()]
        except:
            atom.mass = 1.0

        masses.append(atom.mass)

        for i, coord in enumerate(atom.coord.tolist()):
            positions[i].append(coord)

    # If there is a single atom with undefined mass complain loudly.
    if 'ukn' in set(masses) and not geometric:
        raise ValueError("Some Atoms don't have an element assigned.\n"
                         "Try adding them manually or calculate the geometrical center of mass instead.")

    if geometric:
        com = COM([sum(coord_list) / len(masses) for coord_list in positions])
        return com
    else:
        w_pos = [[], [], []]
        for atom_index, atom_mass in enumerate(masses):
            w_pos[0].append(positions[0][atom_index] * atom_mass)
            w_pos[1].append(positions[1][atom_index] * atom_mass)
            w_pos[2].append(positions[2][atom_index] * atom_mass)
        com = COM([sum(coord_list) / sum(masses) for coord_list in w_pos])
        return com


def calculate_shape_param(structure,rounding=None):
    """
    Calculates the gyration tensor of a structure.
    Returns a tuple containing shape parameters:

      ((a,b,c), rg, A, S)

      (a,b,c) - dimensions of the semi-axis of the ellipsoid
      rg    - radius of gyration of the structure
      A     - sphericity value
      S     - anisotropy value

      References:
           1.  Rawat N, Biswas P (2011) Shape, flexibility and packing of proteins and nucleic acids in complexes. Phys Chem Chem Phys 13:9632-9643
           2.  Thirumalai D (2004) Asymmetry in the Shapes of Folded and Denatured States of Proteinss - The Journal of Physical Chemistry B
           3.  Vondrasek J (2011) Gyration- and Inertia-Tensor-Based Collective Coordinates for Metadynamics. Application on the Conformational Behavior of Polyalanine Peptides and Trp-Cage Folding - The Journal of Physical Chemistry A
    """

    com = center_of_mass(structure, True)
    cx, cy, cz = com.coord

    n_atoms = 0
    tensor_xx, tensor_xy, tensor_xz = 0, 0, 0
    tensor_yx, tensor_yy, tensor_yz = 0, 0, 0
    tensor_zx, tensor_zy, tensor_zz = 0, 0, 0

    if isinstance(structure, Bio.PDB.Entity.Entity):
        atom_list = structure.get_atoms()
    # List of Atoms
    elif hasattr(structure, '__iter__') and [x for x in structure if x.level == 'A']:
        atom_list = structure
    else:  # Some other weirdo object
        raise ValueError("Center of Mass can only be calculated from the following objects:\n"
                         "Structure, Model, Chain, Residue, list of Atoms.")

    for atom in atom_list:
        ax, ay, az = atom.coord
        tensor_xx += (ax - cx) * (ax - cx)
        tensor_yx += (ax - cx) * (ay - cy)
        tensor_xz += (ax - cx) * (az - cz)
        tensor_yy += (ay - cy) * (ay - cy)
        tensor_yz += (ay - cy) * (az - cz)
        tensor_zz += (az - cz) * (az - cz)
        n_atoms += 1

    gy_tensor = numpy.mat([[tensor_xx, tensor_yx, tensor_xz], [tensor_yx, tensor_yy, tensor_yz], [tensor_xz, tensor_yz, tensor_zz]])
    gy_tensor = (1.0 / n_atoms) * gy_tensor

    D, V = numpy.linalg.eig(gy_tensor)
    [a, b, c] = sorted(numpy.sqrt(D))  # lengths of the ellipsoid semi-axis
    rg = numpy.sqrt(sum(D))

    l = numpy.average([D[0], D[1], D[2]])
    A = (((D[0] - l) ** 2 + (D[1] - l) ** 2 + (D[2] - l) ** 2) / l ** 2) * 1 / 6
    S = (((D[0] - l) * (D[1] - l) * (D[2] - l)) / l ** 3)

    if rounding is None:
        return ((a * 2, b * 2, c * 2), rg, A, S)
    else:
        return ((round(a * 2,rounding), round(b * 2,rounding), round(c * 2,rounding)), round(rg,rounding), round(A,rounding), round(S,rounding))

    # print "%s" % '#Dimensions(a,b,c) #Rg #Anisotropy'
    # print "%.2f" % round(a,2), round(b,2), round(c,2) , round(rg,2) , round(A,2)


def calculate_moment_of_intertia_tensor(structure):
    """
    Calculates the moment of inertia tensor from the molecule.
    Returns a numpy matrix.
    """
    global atom_weights

    if isinstance(structure, Bio.PDB.Entity.Entity):
        atom_list = structure.get_atoms()
        # List of Atoms
    elif hasattr(structure, '__iter__') and [x for x in structure if x.level == 'A']:
        atom_list = structure
    else:  # Some other weirdo object
        raise ValueError("Center of Mass can only be calculated from the following objects:\n"
                         "Structure, Model, Chain, Residue, list of Atoms.")
    s_mass = 0.0
    for atom in atom_list:
        atom.mass = atom_weights[atom.element.capitalize()]
        s_mass += atom.mass

    com = center_of_mass(structure, False)
    cx, cy, cz = com.coord

    n_atoms = 0
    tensor_xx, tensor_xy, tensor_xz = 0, 0, 0
    tensor_yx, tensor_yy, tensor_yz = 0, 0, 0
    tensor_zx, tensor_zy, tensor_zz = 0, 0, 0
    # s_mass = sum([a.mass for a in atom_list])

    if isinstance(structure, Bio.PDB.Entity.Entity):
        atom_list = structure.get_atoms()
    elif hasattr(structure, '__iter__') and [x for x in structure if x.level == 'A']:
        atom_list = structure

    for atom in atom_list:
        ax, ay, az = atom.coord
        tensor_xx += ((ay - cy) ** 2 + (az - cz) ** 2) * atom_weights[atom.element.capitalize()]
        tensor_xy += -1 * (ax - cx) * (ay - cy) * atom_weights[atom.element.capitalize()]
        tensor_xz += -1 * (ax - cx) * (az - cz) * atom_weights[atom.element.capitalize()]
        tensor_yy += ((ax - cx) ** 2 + (az - cz) ** 2) * atom_weights[atom.element.capitalize()]
        tensor_yz += -1 * (ay - cy) * (az - cz) * atom_weights[atom.element.capitalize()]
        tensor_zz += ((ax - cx) ** 2 + (ay - cy) ** 2) * atom_weights[atom.element.capitalize()]

    in_tensor = numpy.mat([[tensor_xx, tensor_xy, tensor_xz], [tensor_xy, tensor_yy, tensor_yz], [tensor_xz,
                                                                                            tensor_yz, tensor_zz]])
    D, V = numpy.linalg.eig(in_tensor)

    a = numpy.sqrt((5 / (2 * s_mass)) * (D[0] - D[1] + D[2]))
    b = numpy.sqrt((5 / (2 * s_mass)) * (D[2] - D[0] + D[1]))
    c = numpy.sqrt((5 / (2 * s_mass)) * (D[1] - D[2] + D[0]))
    return sorted([a, b, c]), D, V

#######################################################################################################
#                                          STARTER FUNCTIONS                                          #
#######################################################################################################

def perform_superposition_starter(args):
    global PYTHON_V

    Bioinformatics3.rename_hetatm_and_icode(args.reference)
    Bioinformatics3.rename_hetatm_and_icode(args.target)

    if args.gui is None or not args.gui:
        perform_superposition(reference=args.reference, target=args.target, sensitivity_ah=args.sensitivity_ah,
                              sensitivity_bs=args.sensitivity_bs, peptide_length=args.peptide_length,
                              write_graphml=args.write_graphml, write_pdb=True, ncycles=args.cycles, deep=args.deep,
                              top=args.topn, gui=None, sampling=args.sampling, core_percentage=args.core_percentage,
                              force_core_expansion_through_secstr=args.force_core_expansion_through_secstr, criterium_selection_core=args.criterium_selection_core, use_signature=args.use_signature, match_edges_sign=args.match_edges_sign, verbose=True)
    elif PYTHON_V == 3:
        gui_gra = Graphics.QTGraph_superposition(title="BORGES_MATRIX for superposition v. 4.0.0",
                                                 reference=args.reference, target=args.target,
                                                 sensitivity_ah=args.sensitivity_ah, sensitivity_bs=args.sensitivity_bs,
                                                 peptide_length=args.peptide_length, write_graphml=args.write_graphml,
                                                 write_pdb=True, ncycles=args.cycles, deep=args.deep, top=args.topn,
                                                 sampling=args.sampling, core_percentage=args.core_percentage,
                                                 force_core_expansion_through_secstr=args.force_core_expansion_through_secstr, criterium_selection_core=args.criterium_selection_core, verbose=True)
        timer = QtCore.QTimer()
        # timer.setInterval(0.001)
        timer.timeout.connect(gui_gra.redraw)
        timer.start(0)
        gui_gra.app.exec_()
    else:
        print("In Python 2.x the GUI option is not supported. Sorry.")
        sys.exit(0)

def annotate_pdb_model_starter(args):
    Bioinformatics3.rename_hetatm_and_icode(args.pdbmodel)
    annotate_pdb_model(reference=args.pdbmodel, sensitivity_ah=args.sensitivity_ah,
                           sensitivity_bs=args.sensitivity_bs, peptide_length=args.peptide_length,
                           width_pic=args.width_pic, height_pic=args.height_pic, write_graphml=args.write_graphml,
                           write_pdb=True, gui=None)

def decompose_by_community_clustering_starter(args):
    Bioinformatics3.rename_hetatm_and_icode(args.pdbmodel)
    decompose_by_community_clustering(reference=args.pdbmodel, sensitivity_ah=args.sensitivity_ah,
                                          sensitivity_bs=args.sensitivity_bs, peptide_length=args.peptide_length,
                                          pack_beta_sheet=args.pack_beta_sheet, max_ah_dist=args.max_ah_dist,
                                          min_ah_dist=args.min_ah_dist, max_bs_dist=args.max_bs_dist,
                                          min_bs_dist=args.min_bs_dist, write_graphml=args.write_graphml,
                                          write_pdb=True, homogeneity=args.homogeneity, gui=None)

def find_local_folds_in_the_graph_starter(args):
    Bioinformatics3.rename_hetatm_and_icode(args.pdbmodel)
    find_local_folds_in_the_graph(reference=args.pdbmodel, sensitivity_ah=args.sensitivity_ah,
                                      sensitivity_bs=args.sensitivity_bs, peptide_length=args.peptide_length,
                                      write_graphml=args.write_graphml, write_pdb=True, gui=None)

def find_central_structural_core_shells_starter(args):
    Bioinformatics3.rename_hetatm_and_icode(args.pdbmodel)
    find_central_structural_core_shells(reference=args.pdbmodel, sensitivity_ah=args.sensitivity_ah,
                                            sensitivity_bs=args.sensitivity_bs, peptide_length=args.peptide_length,
                                            write_graphml=args.write_graphml, write_pdb=True, gui=None)

def compare_structures_starter(args):
    Bioinformatics3.rename_hetatm_and_icode(args.reference)
    Bioinformatics3.rename_hetatm_and_icode(args.target)

    compare_structures(reference=args.reference, target=args.target, sensitivity_ah=args.sensitivity_ah,
                           sensitivity_bs=args.sensitivity_bs, peptide_length=args.peptide_length,
                           write_graphml=args.write_graphml, write_pdb=True, core_percentage=args.core_percentage,
                           force_core_expansion_through_secstr=args.force_core_expansion_through_secstr, criterium_selection_core= args.criterium_selection_core,
                           use_seq_alignments= args.use_seq_alignments, score_alignment=args.score_alignment, size_tree=args.size_tree, gap_open=args.gap_open,
                           rmsd_max=args.rmsd_max, ncycles=args.cycles, deep=args.deep, top=args.topn, extract_only_biggest_subfolds=args.extract_only_biggest_subfolds, gui=None, sampling=args.sampling)

def generate_ensembles_starter(args):
    generate_ensembles(directory=args.directory_database, sensitivity_ah=args.sensitivity_ah,
                           sensitivity_bs=args.sensitivity_bs, peptide_length=args.peptide_length,
                           write_graphml=args.write_graphml, write_pdb=True, core_percentage=args.core_percentage, force_core_expansion_through_secstr=args.force_core_expansion_through_secstr,
                       criterium_selection_core=args.criterium_selection_core, use_seq_alignments= args.use_seq_alignments, score_alignment=args.score_alignment, size_tree=args.size_tree, gap_open=args.gap_open,
                           rmsd_max=args.rmsd_max, ncycles=args.cycles, deep=args.deep, top=args.topn, extract_only_biggest_subfolds=args.extract_only_biggest_subfolds, gui=None, sampling=args.sampling)

def understand_dynamics_starter(args):
    understand_dynamics(directory=args.directory_database, sensitivity_ah=args.sensitivity_ah,
                      sensitivity_bs=args.sensitivity_bs, peptide_length=args.peptide_length,
                      write_graphml=args.write_graphml, write_pdb=True, core_percentage=args.core_percentage,
                      force_core_expansion_through_secstr=args.force_core_expansion_through_secstr,
                      criterium_selection_core=args.criterium_selection_core,
                      use_seq_alignments=args.use_seq_alignments, score_alignment=args.score_alignment,
                      size_tree=args.size_tree, gap_open=args.gap_open,
                      rmsd_max=args.rmsd_max, ncycles=args.cycles, deep=args.deep, top=args.topn,
                      extract_only_biggest_subfolds=args.extract_only_biggest_subfolds, gui=None,
                      sampling=args.sampling)


def compact_library_starter(args):
    compact_library(directory=args.directory_database, reference=args.pdbmodel, sensitivity_ah=args.sensitivity_ah,
                           sensitivity_bs=args.sensitivity_bs, peptide_length=args.peptide_length,
                           write_graphml=args.write_graphml, cycles=args.cycles, deep=args.deep,
                           top=args.topn, sampling=args.sampling,howmany_models=args.size_ensemble, howmany_pdbs=args.number_of_ensembles,
                           rmsd_thresh=args.rmsd_thresh, write_pdb=True, core_percentage=args.core_percentage,
                           force_core_expansion_through_secstr=args.force_core_expansion_through_secstr, criterium_selection_core=args.criterium_selection_core, gui=None)

def map_variations_library_starter(args):
    map_variations_library(directory=args.directory_database, gui=None)

def annotate_ncs_starter(args):
    Bioinformatics3.rename_hetatm_and_icode(args.pdbmodel)

    annotate_ncs(reference=args.pdbmodel, ncs_fold=args.ncs_fold, sensitivity_ah=args.sensitivity_ah,
                                          sensitivity_bs=args.sensitivity_bs, peptide_length=args.peptide_length,
                                          pack_beta_sheet=args.pack_beta_sheet, max_ah_dist=args.max_ah_dist,
                                          min_ah_dist=args.min_ah_dist, max_bs_dist=args.max_bs_dist,
                                          min_bs_dist=args.min_bs_dist, write_graphml=args.write_graphml,
                                          write_pdb=True, homogeneity=args.homogeneity, sampling=args.sampling, core_percentage=args.core_percentage,
                                          force_core_expansion_through_secstr=args.force_core_expansion_through_secstr, criterium_selection_core=args.criterium_selection_core, gui=None)

def generate_library_starter(args):
    Bioinformatics3.rename_hetatm_and_icode(args.pdbmodel)

    generate_library(max_n_models_per_pdb = args.max_n_models_per_pdb, local_grid = args.local_grid, remote_grid = args.remote_grid, supercomputer = args.supercomputer, force_core = args.force_core, directory_database = args.directory_database,
    c_angle = args.c_angle, c_dist = args.c_dist, c_angle_dist = args.c_angle_dist, c_cvl_diff = args.c_cvl_diff, score_intra_fragment = args.score_intra_fragment, j_angle = args.j_angle, j_dist = args.j_dist, j_angle_dist = args.j_angle_dist,
    j_cvl_diff = args.j_cvl_diff, score_inter_fragments = args.score_inter_fragments, rmsd_clustering = args.rmsd_clustering, exclude_residues_superpose = args.exclude_residues_superpose, work_directory = args.work_directory,
    use_lib_to_superpose = args.use_lib_to_superpose, targz = args.targz, pdbmodel = args.pdbmodel, remove_coil = args.remove_coil, weight = "distance_avg",
    sensitivity_ah = args.sensitivity_ah, sensitivity_bs = args.sensitivity_bs, peptide_length = args.peptide_length, enhance_fold = args.enhance_fold, superpose = True, process_join = False,
    nilges = args.nilges, ncycles=args.cycles, deep=args.deep, top=args.topn, sampling=args.sampling, sequence=args.sequence, ncssearch=args.ncssearch, multimer=args.multimer,
    rmsd_min=args.rmsd_min, rmsd_max=args.rmsd_max, step_diag=args.step_diag, ssbridge=args.ssbridge, connectivity=args.connectivity, representative=args.representative, sidechains=args.sidechains, core_percentage=args.core_percentage,
    force_core_expansion_through_secstr=args.force_core_expansion_through_secstr, criterium_selection_core=args.criterium_selection_core, gui = None, classic=True)

def generatelibrary_with_signature_starter(args):
    Bioinformatics3.rename_hetatm_and_icode(args.pdbmodel)
    global SIGNATURE_ANGLE_BS
    SIGNATURE_ANGLE_BS = args.signature_strict_angles_bs

    generate_library(max_n_models_per_pdb=args.max_n_models_per_pdb, local_grid=args.local_grid,
                     remote_grid=args.remote_grid, supercomputer=args.supercomputer, force_core=args.force_core,
                     directory_database=args.directory_database,
                     c_angle=args.c_angle, c_dist=args.c_dist, c_angle_dist=args.c_angle_dist,
                     c_cvl_diff=args.c_cvl_diff, score_intra_fragment=args.score_intra_fragment, j_angle=args.j_angle,
                     j_dist=args.j_dist, j_angle_dist=args.j_angle_dist,
                     j_cvl_diff=args.j_cvl_diff, score_inter_fragments=args.score_inter_fragments,
                     rmsd_clustering=args.rmsd_clustering, exclude_residues_superpose=args.exclude_residues_superpose,
                     work_directory=args.work_directory,
                     use_lib_to_superpose=args.use_lib_to_superpose, targz=args.targz, pdbmodel=args.pdbmodel,
                     remove_coil=args.remove_coil, weight="distance_avg",
                     sensitivity_ah=args.sensitivity_ah, sensitivity_bs=args.sensitivity_bs,
                     peptide_length=args.peptide_length, enhance_fold=args.enhance_fold, superpose=True,
                     process_join=False,
                     nilges=args.nilges, ncycles=args.cycles, deep=args.deep, top=args.topn, sampling=args.sampling,
                     sequence=args.sequence, ncssearch=args.ncssearch, multimer=args.multimer,
                     rmsd_min=args.rmsd_min, rmsd_max=args.rmsd_max, step_diag=args.step_diag, ssbridge=args.ssbridge,
                     connectivity=args.connectivity, representative=args.representative, sidechains=args.sidechains,
                     core_percentage=args.core_percentage,
                     force_core_expansion_through_secstr=args.force_core_expansion_through_secstr,
                     criterium_selection_core=args.criterium_selection_core, gui=None, classic=False, signature_threshold=args.signature_threshold)

def generatelibrary_from_sequence_starter(args):
    generate_library_from_sequence(directory_database=args.directory_database, sequence=args.sequence, secstr=args.secondary_structure,coil_diff=args.allowed_coil_difference,sensitivity_ah=args.sensitivity_ah, sensitivity_bs=args.sensitivity_bs, peptide_length=args.peptide_length)

#######################################################################################################
#                                             FUNCTIONS                                               #
#######################################################################################################



def _score_words(word1,word2,signature_angle_bs=False):
    score = 0

    word1l = word1.split("+")
    word2l = word2.split("+")


    #SEC STRUC
    if word1l[0][0] == word2l[0][0]:
        score += 20
    else:
        score -= 10000

    #SEC STRUC
    if word1l[0][1] == word2l[0][1]:
        score += 20
    else:
        score -= 10000

    #print("SIGNATURE ANGLE:",signature_angle_bs,set([word1[0],word2[0],word1[1],word2[1]]),set([word1[0],word2[0],word1[1],word2[1]]),len(set([word1[0],word2[0],word1[1],word2[1]])))
    terenzio = set([word1l[0][0],word2l[0][0],word1l[0][1],word2l[0][1]])
    diff_angle = abs(int(word1l[1])-int(word2l[1]))
    if not signature_angle_bs or len(terenzio)>1 or "H" in terenzio:
        #ANGLE CV
        if diff_angle <= 30:
            score += 20
        else:
            multi = (diff_angle/30)*(-10)
            score += 20+multi
    else:
        # ANGLE CV
        if diff_angle <= 30:
            score += 20
        elif diff_angle <= 50:
            score += -40
        elif diff_angle <= 70:
            score += -100
        else:
            score += -10000

    #DISTANCE
    diff_dist = abs(int(word1l[2])-int(word2l[2]))
    if word1l[0][0] == word2l[0][0] == "S":
        if diff_dist <= 1:
            score += 20
        elif diff_dist <= 2:
            score += 0
        elif diff_dist <= 3:
            score -= 40
        elif diff_dist <= 4:
            score -= 100
        else:
            score -= 10000
    else:
        if diff_dist <= 2:
            score += 20
        else:
            multi = (diff_dist / 2) * (-10)
            score += 20 + multi

    #ANGLE OF THE DISTANCE
    diff_ang_dist = abs(int(word1l[3])-int(word2l[3]))

    if diff_ang_dist <= 30:
        score += 20
    else:
        multi = (diff_ang_dist/30) * (-10)
        score += 20 + multi

    # DISTANCE X
    diff_dist_x = abs(int(word1l[4])-int(word2l[4]))

    if diff_dist_x <= 2:
        score += 20
    else:
        multi = (diff_dist_x/2) * (-10)
        score += 20 + multi

    # DISTANCE Y
    diff_dist_y = abs(int(word1l[5]) - int(word2l[5]))

    if diff_dist_y <= 2:
        score += 20
    else:
        multi = (diff_dist_y / 2) * (-10)
        score += 20 + multi

    # DISTANCE Z
    diff_dist_z = abs(int(word1l[6]) - int(word2l[6]))

    if diff_dist_z <= 2:
        score += 20
    else:
        multi = (diff_dist_z / 2) * (-10)
        score += 20 + multi

    #BS SHEET ID CHECKER
    if word1l[7] == word2l[7]:
        score += 20
    else:
        score -= 40
    #print("WORD1",word1,"WORD2",word2,"SCORE",score)
    return int(round(score))


def _score_words1(word1,word2,signature_angle_bs=False):
    score = 0

    #SEC STRUC
    if word1[0] == word2[0]:
        score += 20
    else:
        score -= 10000

    #SEC STRUC
    if word1[1] == word2[1]:
        score += 20
    else:
        score -= 10000

    #print("SIGNATURE ANGLE:",signature_angle_bs,set([word1[0],word2[0],word1[1],word2[1]]),set([word1[0],word2[0],word1[1],word2[1]]),len(set([word1[0],word2[0],word1[1],word2[1]])))
    terenzio = set([word1[0],word2[0],word1[1],word2[1]])
    if not signature_angle_bs or len(terenzio)>1 or "H" in terenzio:
        #ANGLE CV
        if word1[2] == word2[2]:
            score += 20
        else:
            multi = abs(ord(word1[2])-ord(word2[2]))*(-10)
            score += 20+multi
    else:
        # ANGLE CV
        if word1[2] == word2[2]:
            score += 20
        elif word1[2] == "F" or word2[2] == "F":
            score -= 100
        else:
            multi = abs(ord(word1[2]) - ord(word2[2]))
            if multi == 1:
                multi *= -20
                score += 20 + multi
            elif multi == 2:
                #NOTE: It might be necessary to have the multi more penalized like multi *= -40
                multi *= -20
                score += 20 + multi
            else:
                score -= 10000

    #DISTANCE
    if word1[3] == "Z" or word2[3] == "Z":
        score -= 100
    elif word1[3] == word2[3]:
        score += 20
    else:
        multi = abs(ord(word1[3]) - ord(word2[3])) * (-10)
        score += 20 + multi

    #ANGLE OF THE DISTANCE
    if word1[4] == word2[4]:
        score += 20
    else:
        multi = abs(ord(word1[4]) - ord(word2[4])) * (-20)
        score += 20 + multi

    # DISTANCE X
    if word1[5] == "Z" or word2[5] == "Z":
        score -= 100
    elif word1[5] == word2[5]:
        score += 20
    else:
        multi = abs(ord(word1[5]) - ord(word2[5])) * (-10)
        score += 20 + multi

    # DISTANCE Y
    if word1[6] == "Z" or word2[6] == "Z":
        score -= 100
    elif word1[6] == word2[6]:
        score += 20
    else:
        multi = abs(ord(word1[6]) - ord(word2[6])) * (-10)
        score += 20 + multi

    # DISTANCE Z
    if word1[7] == "Z" or word2[7] == "Z":
        score -= 100
    elif word1[3] == word2[7]:
        score += 20
    else:
        multi = abs(ord(word1[7]) - ord(word2[7])) * (-10)
        score += 20 + multi

    #BS SHEET ID CHECKER
    if word1[8] == word2[8]:
        score += 20
    else:
        score -= 40
    #print("WORD1",word1,"WORD2",word2,"SCORE",score)
    return score


def _score_words2(word1,word2):
    score = 0

    #SEC STRUC
    if word1[0] == word2[0]:
        score += 20
    else:
        score -= 10000

    #SEC STRUC
    if word1[1] == word2[1]:
        score += 20
    else:
        score -= 10000

    #ANGLE CV
    if word1[2] == word2[2]:
        score += 20
    else:
        multi = abs(ord(word1[2])-ord(word2[2]))*(-40)
        score += 20+multi

    #DISTANCE
    if word1[3] == "Z" or word2[3] == "Z":
        score -= 100
    elif word1[3] == word2[3]:
        score += 20
    else:
        multi = abs(ord(word1[3]) - ord(word2[3])) * (-10)
        score += 20 + multi

    #ANGLE OF THE DISTANCE
    if word1[4] == word2[4]:
        score += 20
    else:
        multi = abs(ord(word1[4]) - ord(word2[4])) * (-40)
        score += 20 + multi

    # DISTANCE X
    if word1[5] == "Z" or word2[5] == "Z":
        score -= 100
    elif word1[5] == word2[5]:
        score += 20
    else:
        multi = abs(ord(word1[5]) - ord(word2[5])) * (-10)
        score += 20 + multi

    # DISTANCE Y
    if word1[6] == "Z" or word2[6] == "Z":
        score -= 100
    elif word1[6] == word2[6]:
        score += 20
    else:
        multi = abs(ord(word1[6]) - ord(word2[6])) * (-10)
        score += 20 + multi

    # DISTANCE Z
    if word1[7] == "Z" or word2[7] == "Z":
        score -= 100
    elif word1[3] == word2[7]:
        score += 20
    else:
        multi = abs(ord(word1[7]) - ord(word2[7])) * (-10)
        score += 20 + multi

    #BS SHEET ID CHECKER
    if word1[8] == word2[8]:
        score += 20
    else:
        score -= 40
    #print("WORD1",word1,"WORD2",word2,"SCORE",score)
    return score


def galign_signature(s1, s2, gap_open, gap_extend, mode="global"):
    l = 0
    if mode == "global":
        q1 = pairwise2.align.globalcs(s1, s2, _score_words, gap_open, gap_extend, gap_char=['-------'])
    else:
        q1 = pairwise2.align.localcs(s1, s2, _score_words, gap_open, gap_extend, gap_char=['-------'])

    return q1


def galign2(s1, s2, s3, s4=None,gap_open=-10):
    if s3 == None:
        return 0
    l = 0
    try:
        matrix = matlist.structure  # matlist.blosum62 #NOTE: matlist.blosum45
        gap_open = gap_open  # NOTE #-10
        gap_extend = -1  # NOTE #-0.5
        s1 = s1.replace("-", "X")
        s2 = s2.replace("-", "X")
        s3 = s3.replace("-", "X")
        s1 = s1.replace("U", "X")
        s2 = s2.replace("U", "X")
        s3 = s3.replace("U", "X")
        s1 = s1.replace("O", "K")
        s2 = s2.replace("O", "K")
        s3 = s3.replace("O", "K")
        s1 = s1.replace("B", "X")
        s2 = s2.replace("B", "X")
        s3 = s3.replace("B", "X")
        s1 = s1.replace("Z", "X")
        s2 = s2.replace("Z", "X")
        s3 = s3.replace("Z", "X")
        s1 = s1.replace("J", "X")
        s2 = s2.replace("J", "X")
        s3 = s3.replace("J", "X")

        if "X" in s1 or "X" in s2 or "X" in s3:
            return 0

        q3 = [[-10000,-10000,-10000]]
        q4 = [[-10000,-10000,-10000]]

        q1 = pairwise2.align.globalds(s1, s3, matrix, gap_open, gap_extend)
        q2 = pairwise2.align.globalds(s2, s3, matrix, gap_open, gap_extend)
        if s4 is not None:
            q3 = pairwise2.align.globalds(s1, s4, matrix, gap_open, gap_extend)
            q4 = pairwise2.align.globalds(s2, s4, matrix, gap_open, gap_extend)
        #l = q1[0] if q1[0][2] > q2[0][2] else q2[0]
        l = max(q1[0][2], q2[0][2], q3[0][2], q4[0][2])
    except:
        print(sys.exc_info())
        traceback.print_exc(file=sys.stdout)

    return l


def lalign2(s1, s2, s3, s4=None,gap_open=-10):
    if s3 == None:
        return 0
    l = 0
    try:
        matrix = matlist.structure  # matlist.blosum62 #NOTE: matlist.blosum45
        gap_open = gap_open  # NOTE #-10
        gap_extend = -1  # NOTE #-0.5
        s1 = s1.replace("-", "X")
        s2 = s2.replace("-", "X")
        s3 = s3.replace("-", "X")
        s1 = s1.replace("U", "X")
        s2 = s2.replace("U", "X")
        s3 = s3.replace("U", "X")
        s1 = s1.replace("O", "K")
        s2 = s2.replace("O", "K")
        s3 = s3.replace("O", "K")
        s1 = s1.replace("B", "X")
        s2 = s2.replace("B", "X")
        s3 = s3.replace("B", "X")
        s1 = s1.replace("Z", "X")
        s2 = s2.replace("Z", "X")
        s3 = s3.replace("Z", "X")
        s1 = s1.replace("J", "X")
        s2 = s2.replace("J", "X")
        s3 = s3.replace("J", "X")

        if "X" in s1 or "X" in s2 or "X" in s3:
            return 0

        q3 = [[-10000,-10000,-10000]]
        q4 = [[-10000,-10000,-10000]]

        q1 = pairwise2.align.localds(s1, s3, matrix, gap_open, gap_extend)
        q2 = pairwise2.align.localds(s2, s3, matrix, gap_open, gap_extend)
        if s4 is not None:
            q3 = pairwise2.align.localds(s1, s4, matrix, gap_open, gap_extend)
            q4 = pairwise2.align.localds(s2, s4, matrix, gap_open, gap_extend)
        #l = q1[0] if q1[0][2] > q2[0][2] else q2[0]
        l = max(q1[0][2], q2[0][2], q3[0][2], q4[0][2])
    except:
        print(sys.exc_info())
        traceback.print_exc(file=sys.stdout)

    return l

def is_node_compatible_from_signature(g1, g2, n1, n2):
    seq1_source_l = [s.split("_") for s in g1.vs[n1]["sequences"].split("-")]
    seq2_source_l = [s.split("_") for s in g2.vs[n2]["sequences"].split("-")]

    uno = False
    if sorted([s[0] for s in seq1_source_l]) == sorted([s[0] for s in seq2_source_l]):
        #print(sorted([s[0] for s in seq1_source_l]), sorted([s[0] for s in seq2_source_l]))
        uno = True
    else:
        return False

    if not g1.vs["use_seq_alignments"][0]:
        return True

    due = False
    score = galign2("".join([s[1] for s in seq1_source_l]), "".join([s[1] for s in seq1_source_l][::-1]),
                    "".join([s[1] for s in seq2_source_l]), "".join([s[1] for s in seq2_source_l][::-1]),gap_open=g1.vs["gap_open"][0])
    #score = lalign2("".join([s[1] for s in seq1_source_l]), "".join([s[1] for s in seq1_source_l][::-1]),
    #                "".join([s[1] for s in seq2_source_l]), "".join([s[1] for s in seq2_source_l][::-1]))

    if score > g1.vs["score_alignment"][0]:
        # print (seq1_source_l,seq1_target_l,score)
        return True
    else:
        return False

#NOTE: Very very very very very important: it looks like here the order is really g2, g1, e2, e1 being g2 the caller, g1 the first argument
#of the caller isomorphism
def is_edge_compatible_from_signature(g2, g1, e2, e1):
    #cosdist = scipy.spatial.distance.correlation(g1.es[e1]["value"], g2.es[e2]["value"])
    #return cosdist <= 0.005

    score = _score_words(g1.es[e1]["value"],g2.es[e2]["value"],signature_angle_bs=g1.es[e1]["signature_angle_bs"])
    #print("CHECKING",g1.es[e1]["value"],g2.es[e2]["value"],score)
    #if score < 40:
    #    print("Score is not good breaking")
    #print("******",set([g1.es[e1].source, g1.es[e1].target]),set([1,3]),set([g2.es[e2].source, g2.es[e2].target]),set([6,22]),set([g1.es[e1].source, g1.es[e1].target]) == set([1,3]),set([g2.es[e2].source, g2.es[e2].target]) == set([6,22]))
    return score >= 40

def _score_shapes(shape1,shape2):
    return abs(sum(abs(numpy.array(shape1)-numpy.array(shape2))))

def shape_parameters_floats(resis,structure):
    atoms = [Bioinformatics3.get_atom(structure,resi[1],resi[2],resi[3],"CA") for resi in resis]
    shape = calculate_shape_param(atoms,rounding=3)
    shape = [shape[0][0],shape[0][1],shape[0][2],shape[1],shape[2],shape[3]]
    #tensor = calculate_moment_of_intertia_tensor(atoms)
    return shape

def is_edge_compatible_from_signature2(g1, g2, e1, e2):
    #cosdist = scipy.spatial.distance.correlation(g1.es[e1]["value"], g2.es[e2]["value"])
    #return cosdist <= 0.005

    score = _score_words(g1.es[e1]["value"],g2.es[e2]["value"])

    #print(g1.es[e1]["value"],g2.es[e2]["value"],score)
    if g2.vcount() > 3:
        return score >= 50
    elif score < 50:
        return False

    # if abs(sum(abs(g1.es[e1]["shape"]-g2.es[e2]["shape"]))) <= 1.0:
    #      print(g1.es[e1]["shape"])
    #      print(g2.es[e2]["shape"])
    #      print(g1.es[e1]["shape"]-g2.es[e2]["shape"])
    #      print(sum(abs(g1.es[e1]["shape"]-g2.es[e2]["shape"])))
    tr = 1.0
    if g2.vcount() == 2:
        tr = 1.0
    else:
        tr = 2.0

    return abs(sum(abs(g1.es[e1]["shape"]-g2.es[e2]["shape"]))) <= tr

def is_edge_compatible_restricted_cvs_graphs(g1, g2, e1, e2):
    """
    Return True if the two edges correlates with a score lower than or equal to 0.5

    :param g1: Graph 1 from which edge 1 is retrieved
    :param g2: Graph 2 from which edge 2 is retrieved
    :param e1: Edge 1 index
    :param e2: Edge 2 index
    :return: True if edges are correlated
    """
    cosdist = scipy.spatial.distance.correlation(g1.es[e1]["metric2"], g2.es[e2]["metric2"])

    return cosdist <= THRESH_CORR[SCALING]["isomorphism_ladder"]


def is_edge_compatible_restricted_secstr_graphs(g1, g2, e1, e2):
    cosdist = scipy.spatial.distance.correlation(g1.es[e1]["scaled_mean"], g2.es[e2]["scaled_mean"])

    return cosdist <= THRESH_CORR[SCALING]["compare_signatures"]


def is_edge_compatible_restricted_secstr_graphs_get_val(g1, g2, e1, e2):
    cosdist = scipy.spatial.distance.correlation(g1.es[e1]["scaled_mean"], g2.es[e2]["scaled_mean"])

    return cosdist


def is_compatible(instruction, step, thresholds=[], verbose=False, test_equality=False):
    """
    Test if the instruction set and step set correlates

    :param instruction: [continuity:int, (cvl1:float,cvl2:float), angle_between:float, distance:float, angle_distance:float, reslist:list, (sstype1:str,sstype2:str)]
    :param step:        [continuity:int, (cvl1:float,cvl2:float), angle_between:float, distance:float, angle_distance:float, reslist:list, (sstype1:str,sstype2:str)]
    :param thresholds:
    :param verbose:
    :param test_equality:
    :return:
    """

    ins_cont = instruction[0]
    step_cont = step[0]
    uno = numpy.array([instruction[1][0], instruction[1][1]] + instruction[2:5])
    due = numpy.array([step[1][0], step[1][1]] + step[2:5])

    if ins_cont == 1 and step_cont != 1:
        if verbose:
            print("Not Sequential when required", ins_cont, step_cont)
        return False

    corr = scipy.spatial.distance.correlation(uno, due)

    if test_equality:
        thresh = THRESH_CORR[SCALING]["remove_redundance_chain"]
    else:
        thresh = THRESH_CORR[SCALING]["compare_instruction"]

    if verbose:
        print("=====================COMPARISON VECTORS=======================")
        print("uno:", uno)
        print("due:", due)
        print("correlation:", corr, "threshold:", thresh)
        print("==============================================================")

    return corr <= thresh


def is_compatible_older_version(instruction, step, thresholds=[], verbose=False, test_equality=False):
    """
    Test if instruction and step are compatible 
    :param instruction: 
    :type instruction: 
    :param step: 
    :type step: 
    :param thresholds: 
    :type thresholds: 
    :param verbose: 
    :type verbose: 
    :param test_equality: 
    :type test_equality: 
    :return: 
    :rtype: 
    """

    cv_cont_thresh = 0.15
    cv_cont_alpha = 15
    cv_cont_dista = 1
    cv_cont_beta = 15

    a = cv_cont_thresh
    b = cv_cont_alpha
    c = cv_cont_dista
    d = cv_cont_beta

    cv_jump_thresh = 0.15
    cv_jump_alpha = 30
    cv_jump_dista = 3  # 1
    cv_jump_beta = 30

    ins_cont = instruction[0]
    ins_cvl = instruction[1]
    ins_alpha = instruction[2]
    ins_dista = instruction[3]
    ins_beta = instruction[4]

    step_cont = step[0]
    step_cvl = step[1]
    step_alpha = step[2]
    step_dista = step[3]
    step_beta = step[4]

    if len(thresholds) > 0 and ins_cont != 1:
        cv_jump_thresh = thresholds[3]
        cv_jump_alpha = thresholds[0]
        cv_jump_dista = thresholds[1]
        cv_jump_beta = thresholds[2]
    elif len(thresholds) > 0 and ins_cont == 1:
        a = thresholds[3]
        b = thresholds[0]
        c = thresholds[1]
        d = thresholds[2]
    """
    #When looking for coils also cv_cont_thresh and cv_jump_thresh should be increased because the distorsion is strong
    cv_cont_thresh = 0.60
    cv_cont_alpha = 6
    cv_cont_dista = 3
    cv_cont_beta = 6
    cv_jump_thresh = 0.60
    cv_jump_alpha = 8
    cv_jump_dista = 4
    cv_jump_beta = 8
    """

    if test_equality:
        a = 0.13
        b = 5
        c = 0.3
        d = 5
        cv_jump_thresh = 0.13
        cv_jump_alpha = 5
        cv_jump_dista = 0.3
        cv_jump_beta = 5

    if verbose:
        print("============Thresholds used=================")
        print("CONTINOUS dcvs:", a)
        print("CONTINOUS theta:", b)
        print("CONTINOUS distance:", c)
        print("CONTINOUS phi:", d)
        print("JUMP dcvs:", cv_jump_thresh)
        print("JUMP theta", cv_jump_alpha)
        print("JUMP distance", cv_jump_dista)
        print("JUMP phi", cv_jump_beta)
        print("============Thresholds used=================")

    if ins_cont == 1 and step_cont != 1:
        if verbose:
            print("Not Sequential when required", ins_cont, step_cont)
        return False
    if ins_cont == 1 and abs(
                    abs(ins_cvl[1] - [ins_cvl[0]]) - abs(step_cvl[1] - step_cvl[0])) > a or ins_cont != 1 and abs(
                abs(ins_cvl[1] - ins_cvl[0]) - abs(step_cvl[1] - step_cvl[0])) > cv_jump_thresh:
        if verbose:
            print("CVL Incompatible", abs(ins_cvl - step_cvl))
        return False
    if ins_cont == 1 and abs(ins_alpha - step_alpha) > b or ins_cont != 1 and (abs(
                ins_alpha - step_alpha) > cv_jump_alpha):  # and abs(ins_alpha-step_alpha/2.0) > cv_jump_alpha and abs(ins_alpha/2.0-step_alpha) > cv_jump_alpha):
        if verbose:
            print("Angle between vectors Incompatible", abs(ins_alpha - step_alpha))
        return False
    if ins_cont == 1 and abs(ins_dista - step_dista) > c or ins_cont != 1 and abs(
                    ins_dista - step_dista) > cv_jump_dista:
        if verbose:
            print("Distance Magnitude Incompatible", abs(ins_dista - step_dista))
        return False
    if ins_cont == 1 and abs(ins_beta - step_beta) > d or ins_cont != 1 and (abs(
                ins_beta - step_beta) > cv_jump_beta):  # and abs(ins_beta-step_beta/2.0) > cv_jump_beta and abs(ins_beta/2.0-step_beta) > cv_jump_beta):
        if verbose:
            print("Distance Angle Incompatible", abs(ins_beta - step_beta), ins_cont)
        return False

    if verbose:
        print("Accepted!")

    return True


#@SystemUtility.timing
# @SystemUtility.profileit
def compute_scores(matrice, cvs, matrix=None, verbose=False, diagonals=None):
    # In this function it is assumed that all (cv-cv) in fragments_bounds indeces are sorted ASC
    matrice["jumps_locations"] = []
    matrice["continous_locations"] = []
    matrice["fragments_scores"] = []
    matrice["jumps_scores"] = []
    matrice["continous_locations_chains"] = []

    for s in range(len(matrice["fragments_bounds"])):
        frag = sorted(matrice["fragments_bounds"][s])
        # Continous locations
        con_loc = []
        a, b = frag

        toreset = False
        # if matrix == None and diagonals != None:
        #       toreset = True
        if "sequence_of_chains" in matrice:
            matrice["continous_locations_chains"].append(matrice["sequence_of_chains"][s])

        if a == b:
            con_loc.append((a, b))
        else:
            for t in range(a, b):
                con_loc.append((t, t + 1))
        matrice["continous_locations"].append(con_loc)

        test = []
        for fragin in range(len(matrice["continous_locations"])):
            fragb = matrice["continous_locations"][fragin]
            if matrix == None and diagonals != None:
                toreset = True
                matrix = diagonals[matrice["continous_locations_chains"][fragin]][0]
            listas = []
            for tupl in fragb:
                if matrix == None:
                    listas.append(tupl[0])
                    listas.append(tupl[1])
                else:
                    # print "===tuploide===",matrix[tupl][-3],matrix[tupl],tupl
                    for ele in matrix[tupl][-2]:
                        listas.append(tuple(ele[2:]))
            check = set(listas)
            test.append(check)
            if toreset:
                matrix = None
        if len(test) > 1:
            result = set.intersection(*test)
            # print test
            # print "Intersection is", result
            if len(result) > 0:
                return None, cvs

        if matrix == None and diagonals != None:
            toreset = True
            matrix = diagonals[matrice["sequence_of_chains"][s]][0]

        # computing fragments scores
        sumConScore_cv = 0
        sumConScore_theta = 0
        sumConScore_distance = 0
        sumConScore_phi = 0
        for pos in con_loc:
            if matrix == None:
                instruction = matrice[pos]
            else:
                instruction = matrix[pos]

            sumConScore_cv += instruction[1][0] + instruction[1][1]
            sumConScore_theta += instruction[2]
            sumConScore_distance += instruction[3]
            sumConScore_phi += instruction[4]
        matrice["fragments_scores"].append((sumConScore_cv, sumConScore_theta, sumConScore_distance, sumConScore_phi))

        if toreset:
            matrix = None

        if "border_of_cvs" in matrice:
            tosum = matrice["border_of_cvs"][matrice["sequence_of_chains"][s]]
            # print "Frag 1 is from chain",matrice["sequence_of_chains"][s],"adding",tosum
            a += tosum
            b += tosum

        # in principle we do not need to add continous locations in matrice because they should be computed already!

        # jumping
        if len(matrice["fragments_bounds"]) == 1:
            start_s = s
        else:
            start_s = s + 1
        for r in range(start_s, len(matrice["fragments_bounds"])):
            fragr = sorted(matrice["fragments_bounds"][r])
            c, d = fragr

            if "border_of_cvs" in matrice:
                tosum = matrice["border_of_cvs"][matrice["sequence_of_chains"][r]]
                # print "Frag 2 is from chain",matrice["sequence_of_chains"][r],"adding",tosum
                c += tosum
                d += tosum

            A = tuple(sorted([a, c]))
            B = tuple(sorted([a, d]))
            C = tuple(sorted([b, c]))
            D = tuple(sorted([b, d]))
            E = tuple(sorted([(b + a) // 2, (d + c) // 2]))  # (((b-a)//2)+a) == (b+a)//2
            matrice["jumps_locations"].append((s, r, A, B, C, D, E))
            if matrix == None:
                if A not in matrice:
                    matrice[A] = compute_instruction(cvs[A[0]], cvs[A[1]])
                if B not in matrice:
                    matrice[B] = compute_instruction(cvs[B[0]], cvs[B[1]])
                if C not in matrice:
                    matrice[C] = compute_instruction(cvs[C[0]], cvs[C[1]])
                if D not in matrice:
                    matrice[D] = compute_instruction(cvs[D[0]], cvs[D[1]])
                if E not in matrice:
                    matrice[E] = compute_instruction(cvs[E[0]], cvs[E[1]])
            else:
                if A not in matrix:
                    matrix[A] = compute_instruction(cvs[A[0]], cvs[A[1]])
                if B not in matrix:
                    matrix[B] = compute_instruction(cvs[B[0]], cvs[B[1]])
                if C not in matrix:
                    matrix[C] = compute_instruction(cvs[C[0]], cvs[C[1]])
                if D not in matrix:
                    matrix[D] = compute_instruction(cvs[D[0]], cvs[D[1]])
                if E not in matrix:
                    matrix[E] = compute_instruction(cvs[E[0]], cvs[E[1]])
            # computing jumping scores
            sumJumScore_cv = 0
            sumJumScore_theta = 0
            sumJumScore_distance = 0
            sumJumScore_phi = 0
            # print "-----------",matrice["jumps_locations"]
            for pos in matrice["jumps_locations"][-1][2:]:
                if matrix == None:
                    instruction = matrice[pos]
                else:
                    instruction = matrix[pos]
                # print "Computing scores using instruction: ",pos,instruction
                sumJumScore_cv += instruction[1][0] + instruction[1][1]
                if verbose:
                    print("Summing to theta", instruction[2])
                sumJumScore_theta += instruction[2]
                sumJumScore_distance += instruction[3]
                if verbose:
                    print("Summing to phi", instruction[4])
                sumJumScore_phi += instruction[4]
            if verbose:
                print("+++++++++++++++", s, r, sumJumScore_cv, sumJumScore_theta, sumJumScore_distance, sumJumScore_phi)
            matrice["jumps_scores"].append(
                (s, r, sumJumScore_cv, sumJumScore_theta, sumJumScore_distance, sumJumScore_phi))

    return matrice, cvs


def compute_instruction(in_a, in_b, angle_type="degree", unique_fragment_cv=False):
    """
    Compute the tertiary relationships between two CVs. Angle, Distance and angle distance
    
    :param in_a: first CV
    :type in_a: list
    :param in_b: second CV
    :type in_b: list
    :param angle_type: return "degree", "dot", "radians"
    :type angle_type: str
    :return: angle, distance and angle distance 
    :rtype: list
    """

    N = numpy.array([[0.0, 0.0, 1.0]])

    _1 = in_a[2] - in_a[3]
    _2 = in_b[2] - in_b[3]

    # Distance Magnitude and distance direction
    D1 = in_b[2] - in_a[2]
    d, D = get_atoms_distance(in_a[2], in_b[2])

    if angle_type.lower() == "degree_by_dot":
        # TETA_1 = angle_between_by_acos(_1, _2)
        TETA_1 = angle_between(_1, _2, N, signed=False)
        TETA_2 = angle_between(_1, D, N, signed=False)
        TETA_2a = angle_between(_2, D, N, signed=False)
        # TETA_2d = angle_between(_1, D1, N, signed=False)
        # TETA_2e = angle_between(_2, D1, N, signed=False)
    elif angle_type.lower() in ["degree", "radians"]:
        TETA_1 = angle_between(_1, _2, N, signed=False)
        if abs(in_a[0] - in_b[0]) == 1:
            TETA_b = angle_between_by_acos(_1, _2)

        TETA_2 = angle_between(_1, D, N, signed=False)
        TETA_2a = angle_between(_2, D, N, signed=False)
        # TETA_2d = angle_between(_1, D1, N, signed=False)
        # TETA_2e = angle_between(_2, D1, N, signed=False)
        # print(TETA_1,TETA_2,TETA_2a,TETA_2d,TETA_2e)
    elif angle_type.lower() == "dot":
        TETA_1 = get_dot_between(_1, _2)
        TETA_2 = TETA_2a = get_dot_between(_1, D)

    TETA_2 = min(TETA_2, TETA_2a)

    if angle_type.lower().startswith("degree"):
        TETA_2 *= 57.2957795
        TETA_1 *= 57.2957795

    if d == 0:
        TETA_2 = 0.0

    valued = []

    if not unique_fragment_cv and in_a[0] == in_b[0]:
        valued = [1.0, (in_a[1], in_b[1]), 0.0, 0.0, 0.0, in_a[4]]
    elif unique_fragment_cv:
        valued = [abs(in_a[0] - in_b[0]), (in_a[1], in_b[1]), TETA_1, d, TETA_2, D, in_a[4] + in_b[4]]
    else:
        valued = [abs(in_a[0] - in_b[0]), (in_a[1], in_b[1]), TETA_1, d, TETA_2, in_a[4] + in_b[4]]

    a = in_a[1]
    b = in_b[1]
    if a >= 2.2 - 0.18 and a <= 2.2 + 0.18:
        a = "ah"
    elif a >= 1.39 - 0.24 and a <= 1.39 + 0.24:
        a = "bs"
    else:
        a = "nn"
    if b >= 2.2 - 0.18 and b <= 2.2 + 0.18:
        b = "ah"
    elif b >= 1.39 - 0.24 and b <= 1.39 + 0.24:
        b = "bs"
    else:
        b = "nn"

    # valued.append(None)
    valued.append((a, b))
    # if len(in_a) == 5:
    #     in_a.append(None)
    #     in_a.append(a)
    # if len(in_b) == 5:
    #     in_b.append(None)
    #     in_b.append(b)

    return valued


@SystemUtility.timing
def write_image_from_graph(graph, outputname, print_labels=False, x=800, y=800, set_label=None):
    global color_dict

    if print_labels:
        igraph.plot(graph, outputname, vertex_label=[
            str(vertex["reslist"][0][2]) + "_" + str(vertex["reslist"][0][3][1]) + "-" + str(
                vertex["reslist"][-1][3][1]) for vertex in graph.vs],
                    vertex_color=[color_dict[vertex["reslist"][0][2]] for vertex in graph.vs], vertex_size=60,
                    bbox=(0, 0, x, y))
    elif set_label is not None:
        igraph.plot(graph, outputname, vertex_label=graph.vs[set_label], vertex_size=160, bbox=(0, 0, x, y))
    else:
        igraph.plot(graph, outputname)


@SystemUtility.timing
def get_pdb_string_from_residues(mapping,structure):
    global list_ids
    #print("FILE INPUT IS",reference)

    #structure = Bioinformatics.get_structure("ref",reference)
    # dics = {}
    # for key,value in mapping.items():
    #     if key[0]-1 not in dics:
    #         dics[key[0]-1] = [key[1]]
    #     else:
    #         dics[key[0]-1].append(key[1])
    #
    #     for ele in value:
    #         if ele[0]-1 not in dics:
    #             dics[ele[0]-1] = [ele[1]]
    #         else:
    #             dics[ele[0]-1].append(ele[1])

    dics = mapping

    pdball = ""
    resi_wow = []
    for key, value in sorted(dics.items(), key=lambda x: x[0]):
        chainid = list_ids[key-1]
        resis = [Bioinformatics3.get_residue(structure, resi[1], resi[2], resi[3]) for resi in value]
        atoms = []
        for p, resi in enumerate(resis):
            if resi.get_full_id() in resi_wow:
                continue
            # print(resi,resi.get_full_id())
            # print([a for a in resi])
            if all([Bioinformatics3.get_residue(structure, v[p][1], v[p][2], v[p][3]).has_id("N") for k,v in sorted(dics.items(), key=lambda x: x[0])]): atoms.append(resi["N"])
            if all([Bioinformatics3.get_residue(structure, v[p][1], v[p][2], v[p][3]).has_id("CA") for k,v in sorted(dics.items(), key=lambda x: x[0])]): atoms.append(resi["CA"])
            if all([Bioinformatics3.get_residue(structure, v[p][1], v[p][2], v[p][3]).has_id("CB") for k,v in sorted(dics.items(), key=lambda x: x[0])]): atoms.append(resi["CB"])
            if all([Bioinformatics3.get_residue(structure, v[p][1], v[p][2], v[p][3]).has_id("C") for k,v in sorted(dics.items(), key=lambda x: x[0])]): atoms.append(resi["C"])
            if all([Bioinformatics3.get_residue(structure, v[p][1], v[p][2], v[p][3]).has_id("O") for k,v in sorted(dics.items(), key=lambda x: x[0])]): atoms.append(resi["O"])
            resi_wow.append(resi.get_full_id())
        pdbmod, cnv = Bioinformatics3.get_pdb_from_list_of_atoms(reference=atoms, renumber=True, uniqueChain=True, chainId=chainid, sort_reference=False)
        pdball += "REMARK 299 NCS GROUP BEGIN\n"
        pdball += pdbmod+"\n"
        pdball += "REMARK 299 NCS GROUP END\n"

    atoms = []
    chainid = list_ids[len(dics.keys())]
    for resi in Bio.PDB.Selection.unfold_entities(structure, 'R'):
        if resi.get_full_id() in resi_wow:
            continue
            # print(resi,resi.get_full_id())
            # print([a for a in resi])
        if resi.has_id("N"): atoms.append(resi["N"])
        if resi.has_id("CA"): atoms.append(resi["CA"])
        if resi.has_id("CB"): atoms.append(resi["CB"])
        if resi.has_id("C"): atoms.append(resi["C"])
        if resi.has_id("O"): atoms.append(resi["O"])
        resi_wow.append(resi.get_full_id())
    pdbmod, cnv = Bioinformatics3.get_pdb_from_list_of_atoms(atoms, renumber=True, uniqueChain=True, chainId=chainid, sort_reference=False)
    pdball += pdbmod + "\n"

    return pdball


#@SystemUtility.timing
def get_pdb_string_from_graph(g, structure, renumber=True, chainid="A", uniqueChain=True, mapping=[], extends=0, polyala=True):
    s = []
    if len(mapping) == 0:
        way = g.vs
    else:
        way = []
        for z, v in enumerate(g.vs):
            if mapping[z] >= 0:
                way.append(g.vs[mapping[z]])

    for v in way:
        s += [tuple(t[:-1]) for t in v["reslist"]]
    s = list(set(s))

    reference = []
    for model in structure.get_list():
        for chain in model.get_list():
            residues = chain.get_list()
            for r,residue in enumerate(residues):
                # print residue.get_full_id()
                if residue.get_full_id() in s or (extends>0 and any([residues[r-t].get_full_id() in s for t in range(1,extends+1) if r-t >= 0]+[residues[r+t].get_full_id() in s for t in range(1,extends+1) if r+t < len(residues)])):
                    reference += residue.get_unpacked_list()

    pdbmod, cnv = Bioinformatics3.get_pdb_from_list_of_atoms(reference, renumber=renumber, uniqueChain=uniqueChain, chainId=chainid, polyala=polyala)
    return pdbmod


@SystemUtility.timing
def get_pdb_string_from_cvs(cvlist, structure, chainid="A"):
    s = []
    for v in cvlist:
        s += [tuple(t[:-1]) for t in v["reslist"]]
    s = list(set(s))

    reference = []
    for model in structure.get_list():
        for chain in model.get_list():
            for residue in chain.get_list():
                # print residue.get_full_id()
                if residue.get_full_id() in s:
                    reference += residue.get_unpacked_list()
    pdbmod, cnv = Bioinformatics3.get_pdb_from_list_of_atoms(reference, renumber=True, uniqueChain=True, chainId=chainid)
    return pdbmod


@SystemUtility.timing
def get_edge_product_graph(g1, g2, graphs_from_same_structure=False, restrictions_edges=None, verbose=False):
    print("START COMPATIBILITY GRAPH ", datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    print("ADDING VERTICES", datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

    g1.es["name"] = [json.dumps([1] + sorted([g1.vs[edge.source]["name"], g1.vs[edge.target]["name"]])) for edge in
                     g1.es]
    g2.es["name"] = [json.dumps([2] + sorted([g2.vs[edge.source]["name"], g2.vs[edge.target]["name"]])) for edge in
                     g2.es]

    if SCALING == "robust_scale":
        X = sklearn.preprocessing.robust_scale(g1.es["metric"]+g2.es["metric"], axis=0, copy=True)
    elif SCALING == "min_max":
        X = sklearn.preprocessing.minmax_scale(g1.es["metric"] + g2.es["metric"], feature_range=(0, 1), axis=0, copy=True)
    g1.es["metric2"] = X[:g1.ecount()]
    g2.es["metric2"] = X[g1.ecount():]

    # CREATE the Full Graph of the sum edge graph between g1 and g2 on edges
    g = igraph.Graph(g1.ecount() + g2.ecount(), directed=False)
    g.vs["name"] = g1.es["name"] + g2.es["name"]
    g.vs["type"] = [0] * g1.ecount() + [1] * g2.ecount()

    print("PREPARING EDGES AND WEIGHTS", datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

    # ADDING EDGES
    # edges_to_add = [(v.index,z.index) for v in g.vs for z in g.vs if (json.loads(v["name"])[0] == json.loads(z["name"])[0]) and (len(set(json.loads(v["name"])[1:]) & set(json.loads(z["name"])[1:])) == 1)]
    edges_to_add = []

    # for edge in edges_to_add:
    #     print g.vs[edge[0]]["name"],g.vs[edge[1]]["name"]

    # weights = [0.001]*len(edges_to_add)
    # weights_corr = [0.001]*len(edges_to_add)
    weights = []
    weights_corr = []
    z = 0

    print("THEORETICAL PRODUCT",g1.ecount()*g2.ecount())
    for edge in itertools.product(*[g1.es, g2.es]):
        if restrictions_edges:
            ad1 = tuple(sorted([g1.vs[edge[0].source]["secstr"],g1.vs[edge[0].target]["secstr"]]))
            ad2 = tuple(sorted([g2.vs[edge[1].source]["secstr"],g2.vs[edge[1].target]["secstr"]]))
            if not (ad1 in restrictions_edges and ad2 == restrictions_edges[ad1]):
                continue

        if graphs_from_same_structure:
            a = set([g1.vs[edge[0].source]["secstr"],g1.vs[edge[0].target]["secstr"],g2.vs[edge[1].source]["secstr"],g2.vs[edge[1].target]["secstr"]])
            if len(a) < 4:
                continue
        cosdist = scipy.spatial.distance.correlation(edge[0]["metric2"], edge[1]["metric2"])

        # print("Num.", z, "distance between g1", json.dumps([1] + sorted([g1.vs[edge[0].source]["name"], g1.vs[edge[0].target]["name"]])), "and g2", json.dumps([2] + sorted([g2.vs[edge[1].source]["name"], g2.vs[edge[1].target]["name"]])), "is",
        #       "correlation:",cosdist,"braycurtis",scipy.spatial.distance.braycurtis(edge[0]["metric2"], edge[1]["metric2"]),"canberra",scipy.spatial.distance.canberra(edge[0]["metric2"], edge[1]["metric2"]),
        #       "chebyshev", scipy.spatial.distance.chebyshev(edge[0]["metric2"], edge[1]["metric2"]),"cityblock", scipy.spatial.distance.cityblock(edge[0]["metric2"], edge[1]["metric2"]),
        #       "cosine", scipy.spatial.distance.cosine(edge[0]["metric2"], edge[1]["metric2"]),"euclidean", scipy.spatial.distance.euclidean(edge[0]["metric2"], edge[1]["metric2"]),
        #       "sqeuclidean", scipy.spatial.distance.sqeuclidean(edge[0]["metric2"], edge[1]["metric2"]))

        #NOTE: activate only when verbose
        if verbose:
            print("Num.", z, "distance between g1",
                 json.dumps([1] + sorted([g1.vs[edge[0].source]["name"], g1.vs[edge[0].target]["name"]])), "and g2",
                 json.dumps([2] + sorted([g2.vs[edge[1].source]["name"], g2.vs[edge[1].target]["name"]])), "is",
                 "correlation:", cosdist)
            print(edge[0]["metric"], end=""), print(edge[0]["metric2"])
            print(edge[1]["metric"], end=""), print(edge[1]["metric2"])
            print()
        edges_to_add.append((g.vs.find(
            name=json.dumps([1] + sorted([g1.vs[edge[0].source]["name"], g1.vs[edge[0].target]["name"]]))).index,
                             g.vs.find(name=json.dumps(
                                 [2] + sorted([g2.vs[edge[1].source]["name"], g2.vs[edge[1].target]["name"]]))).index))
        if cosdist == 0:
            cosdist = 0.0000001
        weights.append(10.0 / cosdist)
        weights_corr.append(cosdist)
        z += 1

    # print("GENERATING NUMPY MATRIX", datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    # matrix = numpy.array(weights_corr)
    # matrix = numpy.reshape(matrix,(g1.ecount(),g2.ecount()))
    # indexlist = numpy.argsort(numpy.linalg.norm(matrix, axis=1))
    # matrix = matrix[indexlist]
    # means_rows = matrix.mean(axis=1)
    # means_columns = matrix.mean(axis=0)
    # means_rows = numpy.reshape(means_rows,(1,len(means_rows)))
    # means_columns = numpy.reshape(means_columns,(1,len(means_columns)))
    # print(means_rows)
    # print(means_columns)
    # #plt.imshow(means_rows, cmap='hot', interpolation='none')
    # #plt.imshow(means_columns, cmap='hot', interpolation='none')
    # plt.imshow(matrix, cmap='hot', interpolation='none')
    # #plt.savefig("heatmap2.pdf")
    # plt.show()
    # quit()
    print("ADDING EDGES", len(edges_to_add), datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    g.add_edges(edges_to_add)

    print("ADDING WEIGHTS", len(edges_to_add),
          datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    g.es["weight"] = weights
    g.es["weight_corr"] = weights_corr

    print("ENDING THE COMPATIBILITY GRAPH", datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

    return g


# @SystemUtility.timing
def find_all_paths_of_given_length(G, u, n, graph_ref, graph_targ, exclude_set=None):
    if exclude_set == None:
        exclude_set = set([u["name"]])
    else:
        exclude_set.add(u["name"])
    if n == 0:
        # print(exclude_set)
        # print("N 0 but",len(exclude_set))
        return [[u["name"]]]
    # print(exclude_set,"----------------",[G.es[G.get_eid(nei,G.vs.find(name=exclude_set[-1]).index)]["weight_corr"] for nei in G.neighbors(u)])
    # print("CURRENT WEIGHT FILTER:",1.0/float(n))
    ###tu = G.vs.find(name=exclude_set[-1]).index
    # print("----------------------",[G.vs[s]["name"] for s in G.neighbors(u)])
    # print(".......................",exclude_set)

    paths = [[u["name"]] + path for neighbor in G.neighbors(u) if G.vs[neighbor]["name"] not in exclude_set for path in
             find_all_paths_of_given_length(G, G.vs[neighbor], n - 1, graph_ref, graph_targ, exclude_set) if
             len(path) % 2 == 0 or check_isomorphism_in_ladder_graph(G.es.select(
                 lambda z: sorted([G.vs[z.source]["name"], G.vs[z.target]["name"]]) in [sorted([m, path[h]]) for h, m in
                                                                                        enumerate([u["name"]] + path) if
                                                                                        h % 2 == 0 and h <= len(
                                                                                            path) - 1]).subgraph(),G,
                                                                     graph_ref, graph_targ, return_boolean=True)]
    exclude_set.remove(u["name"])
    # print(paths)
    return paths


# @SystemUtility.timing
def check_isomorphism_in_ladder_graph(spantree, full_prod, graph_ref, graph_targ, return_boolean=False, pdb_model=""):
    gra_1_f = []
    gra_2_f = []
    associations = []
    corr = None
    if spantree.ecount() < 1 and return_boolean:
        return False
        # if return_boolean:
        #    wer = float(spantree.ecount())/(total_e-20)
        # print("WER is",wer,spantree.ecount())
    # print("================",spantree.vs["name"],"=======================")
    # print("----------------",spantree.ecount(),"-----------------------")
    for edge in sorted(spantree.es, key=lambda x: x["weight_corr"]):
        valori_1 = json.loads(spantree.vs[edge.source]["name"])
        valori_2 = json.loads(spantree.vs[edge.target]["name"])
        if valori_1[0] == valori_2[0]:
            continue

        #print("SHERLOCK .....", valori_1, valori_2, ".....")

        gra_1 = []
        gra_2 = []

        if valori_1[0] == 1:
            gra_1.append((graph_ref.vs.find(name=valori_1[1]).index, graph_ref.vs.find(name=valori_1[2]).index))
        elif valori_1[0] == 2:
            gra_2.append((graph_targ.vs.find(name=valori_1[1]).index, graph_targ.vs.find(name=valori_1[2]).index))

        if valori_2[0] == 1:
            gra_1.append((graph_ref.vs.find(name=valori_2[1]).index, graph_ref.vs.find(name=valori_2[2]).index))
        elif valori_2[0] == 2:
            gra_2.append((graph_targ.vs.find(name=valori_2[1]).index, graph_targ.vs.find(name=valori_2[2]).index))

        #print("SHERLOCK: gra_1",gra_1,"gra_2",gra_2)
        g_a = graph_ref.es.select(
            lambda e: (e.source, e.target) in gra_1_f + gra_1 or (e.target, e.source) in gra_1_f + gra_1).subgraph()
        g_b = graph_targ.es.select(
            lambda e: (e.source, e.target) in gra_2_f + gra_2 or (e.target, e.source) in gra_2_f + gra_2).subgraph()

        isom = g_b.get_subisomorphisms_vf2(g_a, edge_compat_fn=is_edge_compatible_restricted_cvs_graphs)
        # isom = g_b.get_subisomorphisms_vf2(g_a)

        if len(isom) > 0:
            asso = []
            inserted = False
            for s, iso in enumerate(isom):
                # print()
                uno = g_a.vs["name"]
                due = [g_b.vs[ind]["name"] for ind in iso]
                ##### print("----------------------")
                ##### print(uno)
                ##### print("----------------------")
                ##### print(due)
                #tre = [full_prod.get_eid(full_prod.vs.find(name=json.dumps([1] + sorted([uno[i], uno[j]]))).index,
                #                         full_prod.vs.find(name=json.dumps([2] + sorted([due[i], due[j]]))).index,
                #                        error=False) if len(
                #    full_prod.vs.select(name=json.dumps([1] + sorted([uno[i], uno[j]])))) == 1 and len(
                #    full_prod.vs.select(name=json.dumps([2] + sorted([due[i], due[j]])))) == 1 else None for i in
                #       range(len(uno)) for j in range(len(uno)) if i != j]

                #print(tre)
                ######print(".........................")
                # if -1 in tre:
                #     continue
                # else:
                check_uno = {}
                check_uno_cont = {}
                for r, f in enumerate(uno):
                    t = g_a.vs.find(name=f)["secstr"]
                    if t in check_uno:
                        check_uno[t].append(r)
                        check_uno_cont[t].append(int(f.split("_")[0]))
                    else:
                        check_uno[t] = [r]
                        check_uno_cont[t] = [int(f.split("_")[0])]

                check_due = {}
                check_due_cont = {}
                for r, f in enumerate(due):
                    t = g_b.vs.find(name=f)["secstr"]
                    if t in check_due:
                        check_due[t].append(r)
                        check_due_cont[t].append(int(f.split("_")[0]))
                    else:
                        check_due[t] = [r]
                        check_due_cont[t] = [int(f.split("_")[0])]

                for key in check_uno_cont:
                    # check_uno_cont[key] = sorted(check_uno_cont[key])
                    check_uno_cont[key] = [(check_uno_cont[key][t] - check_uno_cont[key][t + 1]) for t in
                                           range(len(check_uno_cont[key]) - 1)]
                for key in check_due_cont:
                    # check_due_cont[key] = sorted(check_due_cont[key])
                    check_due_cont[key] = [(check_due_cont[key][t] - check_due_cont[key][t + 1]) for t in
                                           range(len(check_due_cont[key]) - 1)]

                # print(uno,check_uno,check_uno_cont)
                # print(due,check_due,check_due_cont)

                found = True
                for key in check_uno:
                    found = False
                    for key2 in check_due:
                        if check_uno[key] == check_due[key2] and check_uno_cont[key] == check_due_cont[key2]:
                            found = True
                            break
                    if not found:
                        break
                if not found:
                    continue

                inserted = True
                dico = list(zip(uno, due))
                # print(check_uno,check_due,dico)
                asso.append(dico)
                associations = copy.deepcopy(asso)

            if not inserted:
                #print("SHERLOCK Edge", edge.source, edge.target, "is not compatible because not inserted ")
                if return_boolean:
                    return False
            if corr is None:
                corr = 0
            corr += edge["weight_corr"]
            gra_1_f += gra_1
            gra_2_f += gra_2
            # print("--------")
        else:
            #print("SHERLOCK Edge", edge.source, edge.target, "is not compatible")
            if return_boolean:
                return False

    g_a = graph_ref.es.select(
        lambda e: (e.source, e.target) in gra_1_f or (e.target, e.source) in gra_1_f).subgraph()
    g_b = graph_targ.es.select(
        lambda e: (e.source, e.target) in gra_2_f or (e.target, e.source) in gra_2_f).subgraph()
    if not return_boolean:
        g_a.write_graphml(os.path.join("./", os.path.basename(pdb_model)[:-4] + "_g_a.graphml"))
        g_b.write_graphml(os.path.join("./", os.path.basename(pdb_model)[:-4] + "_g_b.graphml"))

    # if not return_boolean:
    #    print("Final allowed associations")
    #    print(associations)
    #    print("Total corr obtained", corr)
    # for asso in associations:
    # print(type(asso))
    # print("\t", asso)
    # print()
    # print(associations,corr)

    # print([(graph_ref.vs.find(name=r[0])["secstr"],graph_targ.vs.find(name=r[1])["secstr"]) for t in associations for r in t])
    #####print("Total corr obtained", corr)
    # print(spantree.vcount())
    # if spantree.vcount() == 8:
    #    print(sum([edge["weight_corr"] for edge in spantree.es]),corr,spantree.vcount())

    if return_boolean:
        return corr <= THRESH_CORR[SCALING]["total_ladder"], corr, g_a, g_b, associations
    else:
        return corr, g_a, g_b, associations


@SystemUtility.timing
def __fill_ladder_list_with_initial_optimal_seeds(ladder, graph_ref, graph_targ, trials=1000000000):
    global THRESH_CORR
    map_graph = {1: graph_ref, 2: graph_targ}

    ladder_list1 = []
    best_match = None
    best_corr = 1000000
    for z in range(trials):
        #print(".", end="")
        if len(ladder_list1) > 0:
            matched = (ladder_list1[0],[])
            print(matched)
            #print(matched)
            q = [g for f in matched for a in f for g in [ladder.es[a].source, ladder.es[a].target]]
            t = set(q)
        else:
            q = t = []
        if len(q) == 0 or len(q) != len(t):
            ladder_list1 = [[q.index] for q in ladder.es if
                            (ladder.es[q.index]["weight_corr"] < THRESH_CORR[SCALING]["filter_bipartite"]) and
                            (map_graph[json.loads(ladder.vs[ladder.es[q.index].source]["name"])[0]].vs.find(
                                name=json.loads(ladder.vs[ladder.es[q.index].source]["name"])[1])["isSpecial"]) and
                            (map_graph[json.loads(ladder.vs[ladder.es[q.index].source]["name"])[0]].vs.find(
                                name=json.loads(ladder.vs[ladder.es[q.index].source]["name"])[2])["isSpecial"]) and
                            (map_graph[json.loads(ladder.vs[ladder.es[q.index].target]["name"])[0]].vs.find(
                                name=json.loads(ladder.vs[ladder.es[q.index].target]["name"])[1])["isSpecial"]) and
                            (map_graph[json.loads(ladder.vs[ladder.es[q.index].target]["name"])[0]].vs.find(
                                name=json.loads(ladder.vs[ladder.es[q.index].target]["name"])[2])["isSpecial"])]
            n = min(len(set(graph_ref.vs["secstr"])), len(set(graph_targ.vs["secstr"])))
            t = random.sample(ladder_list1, 2)
            ladder_list1 = [[a[0] for a in t]]
            continue

        # print(len(q),len(t))
        matched = sorted([a for f in matched for a in f])
        spantree = ladder.es.select(lambda e: e.index in matched).subgraph(delete_vertices=True)
        results = check_isomorphism_in_ladder_graph(spantree, ladder, graph_ref, graph_targ, return_boolean=True)
        if results:
            res, corr, g_a, g_b, associations = results
            if corr < best_corr:
                print("FOUND NEW BEST:", matched)
                print([(spantree.vs[o.source]["name"], spantree.vs[o.target]["name"]) for o in spantree.es], corr)
                inserted = True
                best_corr = corr
        else:
            ladder_list1 = []
            continue

        w = spantree.es[numpy.argmax([edge["weight_corr"] for edge in spantree.es])]
        name1 = spantree.vs[w.source]["name"]
        name2 = spantree.vs[w.target]["name"]
        print("WORST SCORE FROM:", name1,name2,w["weight_corr"])
        names = [b for a in ladder_list1 for b in a if (ladder.vs[(ladder.es[b]).source]["name"], ladder.vs[(ladder.es[b]).target]["name"]) in [(name1,name2),(name2,name1)]]
        #print("SELECTED NAME", names, ladder.es[names[0]]["weight_corr"])
        ladder_list1[0].remove(names[0])
        #print(ladder_list1)
        sec1 = map_graph[json.loads(ladder.vs[ladder.es[names[0]].source]["name"])[0]].vs.find(name=json.loads(ladder.vs[ladder.es[names[0]].source]["name"])[1])["secstr"]
        sec2 = map_graph[json.loads(ladder.vs[ladder.es[names[0]].source]["name"])[0]].vs.find(name=json.loads(ladder.vs[ladder.es[names[0]].source]["name"])[2])["secstr"]
        sec3 = map_graph[json.loads(ladder.vs[ladder.es[names[0]].target]["name"])[0]].vs.find(name=json.loads(ladder.vs[ladder.es[names[0]].target]["name"])[1])["secstr"]
        sec4 = map_graph[json.loads(ladder.vs[ladder.es[names[0]].target]["name"])[0]].vs.find(name=json.loads(ladder.vs[ladder.es[names[0]].target]["name"])[2])["secstr"]
        ladder_list2 = [q.index for q in ladder.es if
                        (map_graph[json.loads(ladder.vs[ladder.es[q.index].source]["name"])[0]].vs.find(
                            name=json.loads(ladder.vs[ladder.es[q.index].source]["name"])[1])["secstr"] == sec1) and
                        (map_graph[json.loads(ladder.vs[ladder.es[q.index].source]["name"])[0]].vs.find(
                            name=json.loads(ladder.vs[ladder.es[q.index].source]["name"])[2])["secstr"] == sec2) and
                        (map_graph[json.loads(ladder.vs[ladder.es[q.index].target]["name"])[0]].vs.find(
                            name=json.loads(ladder.vs[ladder.es[q.index].target]["name"])[1])["secstr"] == sec3) and
                        (map_graph[json.loads(ladder.vs[ladder.es[q.index].target]["name"])[0]].vs.find(
                            name=json.loads(ladder.vs[ladder.es[q.index].target]["name"])[2])["secstr"] == sec4)]
        #print(ladder_list2)
        t = random.sample(ladder_list2, 1)
        ladder_list1 = [ladder_list1[0]+[a for a in t]]


#@SystemUtility.timing
def check_one_configuration(matched,ladder,graph_ref, graph_targ, reference, target):
    q = [g for a in matched for g in [ladder.es[a].source, ladder.es[a].target]]
    t = set(q)
    if len(q) != len(t):
        #print("SHERLOCK: wrong lens",len(q),len(t))
        return False

    matched = sorted([a for a in matched])
    spantree = ladder.es.select(lambda e: e.index in matched).subgraph(delete_vertices=True)
    results = check_isomorphism_in_ladder_graph(spantree, ladder, graph_ref, graph_targ, return_boolean=True)

    if results:
        res, corr, g_a, g_b, associations = results
        results = select_best_superposition_overall_cycles("", [(len(matched), corr, matched, [], [], g_a, g_b, associations)],
                                                           reference, target, graph_ref, graph_targ,
                                                           write_pdb=False, gui=None, verbose=False)
        #print("RMSDDDD:", results["rmsd"], "ASSOCIATIONS:", associations, "CORR:", corr)
        if results["rmsd"] < 0.8:
            return True
        else:
            return False

    else:
        return False


#@SystemUtility.timing
def improve_one(one, fix,ladder, graph_ref, graph_targ, reference, target, start_time=None, break_sec=100):
    r = 5
    a = [fix[1]] + [str(int(fix[1].split("_")[0]) + i) + "_" + fix[1].split("_")[1] for i in range(1, r)] + [
        str(int(fix[1].split("_")[0]) - i) + "_" + fix[1].split("_")[1] for i in range(1, r)]
    b = [fix[2]] + [str(int(fix[2].split("_")[0]) + i) + "_" + fix[2].split("_")[1] for i in range(1, r)] + [
        str(int(fix[2].split("_")[0]) - i) + "_" + fix[2].split("_")[1] for i in range(1, r)]
    c = [one[1]]+[str(int(one[1].split("_")[0]) + i) + "_" + one[1].split("_")[1] for i in range(1,r)]+[str(int(one[1].split("_")[0]) - i) + "_" + one[1].split("_")[1] for i in range(1,r)]
    d = [one[2]]+[str(int(one[2].split("_")[0]) + i) + "_" + one[2].split("_")[1] for i in range(1,r)]+[str(int(one[2].split("_")[0]) - i) + "_" + one[2].split("_")[1] for i in range(1,r)]

    # print(a)
    # print(b)
    for combi in itertools.product(*[a, b, c, d]):
        if start_time and time.time() >= start_time + break_sec:
            return []
        fix = json.dumps([1, combi[0], combi[1]])
        v = json.dumps([2, combi[2], combi[3]])
        mat = [fix, v]
        #print(mat)
        try:
            mat = [ladder.get_eid(ladder.vs.find(name=mat[0]).index, ladder.vs.find(name=mat[1]).index)]
        except:
            continue

        alpha = check_one_configuration(mat, ladder, graph_ref, graph_targ, reference, target)
        if alpha:
            return mat
    return []

#@SystemUtility.timing
def local_optimization_of_vector_alignment(matched, spantree, res, corr, g_a, g_b, associations, results, ladder, graph_ref, graph_targ, reference, target, start_time=None, break_sec=100):

    map_graph = {1: graph_ref, 2: graph_targ}

    ###print(matched)
    lista = [(spantree.vs[o.source]["name"], spantree.vs[o.target]["name"]) for o in spantree.es]

    explore = [json.loads(z) for t in lista for z in t if json.loads(z)[0] == 2]
    fixed = [json.loads(z) for t in lista for z in t if json.loads(z)[0] == 1]

    improved_first = improve_one(explore[0],fixed[0], ladder, graph_ref, graph_targ, reference, target, start_time=start_time, break_sec=break_sec)
    if len(improved_first) == 0:
        return False, matched, spantree, res, corr, g_a, g_b, associations, results, fixed, explore
    else:
        if len(explore) == 1 and len(fixed) == 1:
            matched = improved_first
            spantree = ladder.es.select(lambda e: e.index in matched).subgraph(delete_vertices=True)
            results2 = check_isomorphism_in_ladder_graph(spantree, ladder, graph_ref, graph_targ, return_boolean=True)
            if results2:
                #print("First", explore[0], fixed[0], "has been improved!!!")
                lista = [(spantree.vs[o.source]["name"], spantree.vs[o.target]["name"]) for o in spantree.es]
                explore = [json.loads(z) for t in lista for z in t if json.loads(z)[0] == 2]
                fixed = [json.loads(z) for t in lista for z in t if json.loads(z)[0] == 1]
                res, corr, g_a, g_b, associations = results2
                results2 = select_best_superposition_overall_cycles("",
                                                                    [(len(matched), corr, matched, fixed, explore, g_a,
                                                                      g_b, associations)],
                                                                    reference, target, graph_ref, graph_targ,
                                                                    write_pdb=False, gui=None, verbose=False)
                # print("RMSDDDDD:", results["rmsd"], "ASSOCIATIONS:", associations, "CORR:", corr)
                return True, matched, spantree, res, corr, g_a, g_b, associations, results2, fixed, explore
            else:
                return False, matched, spantree, res, corr, g_a, g_b, associations, results, fixed, explore

        improved_second = improve_one(explore[1], fixed[1], ladder, graph_ref, graph_targ, reference, target, start_time=start_time, break_sec=break_sec)
        if len(improved_second) == 0:
            return False, matched, spantree, res, corr, g_a, g_b, associations, results, fixed, explore
        else:
            matched = improved_first+improved_second
            spantree = ladder.es.select(lambda e: e.index in matched).subgraph(delete_vertices=True)
            results2 = check_isomorphism_in_ladder_graph(spantree, ladder, graph_ref, graph_targ, return_boolean=True)
            if results2:
                lista = [(spantree.vs[o.source]["name"], spantree.vs[o.target]["name"]) for o in spantree.es]
                explore = [json.loads(z) for t in lista for z in t if json.loads(z)[0] == 2]
                fixed = [json.loads(z) for t in lista for z in t if json.loads(z)[0] == 1]
                res, corr, g_a, g_b, associations = results2
                results2 = select_best_superposition_overall_cycles("",
                                                                   [(len(matched), corr, matched, fixed, explore, g_a, g_b, associations)],
                                                                   reference, target, graph_ref, graph_targ,
                                                                   write_pdb=False, gui=None, verbose=False)
                #print("RMSDDDDD:", results["rmsd"], "ASSOCIATIONS:", associations, "CORR:", corr)
                return True, matched, spantree, res, corr, g_a, g_b, associations, results2, fixed, explore
            else:
                return False, matched, spantree, res, corr, g_a, g_b, associations, results, fixed, explore


@SystemUtility.timing
def compute_correlation_between_graphs(reference, target, structure_ref, structure_targ, graph_ref, graph_targ, pdb_model, initial_filtering_by_special=False, ncycles=15,
                                       deep=False, top=4, max_sec=1, break_sec=300, min_correct=1, graphs_from_same_structure=False, write_graphml=False, gui=None, signal=None,
                                       restrictions_edges=None, force_core_expansion_through_secstr=False, verbose=False):
    if write_graphml:
        graph_ref.write_graphml(os.path.join("./", os.path.basename(pdb_model)[:-4] + "_graphref.graphml"))
        graph_targ.write_graphml(os.path.join("./", os.path.basename(pdb_model)[:-4] + "_graphtarg.graphml"))

    g_prod = get_edge_product_graph(graph_ref, graph_targ, graphs_from_same_structure=graphs_from_same_structure, restrictions_edges=restrictions_edges)

    if gui is not None:
        gui.draw_graph(g_prod, "product", where="top", scale=0.0001, show_labels=False)

    ladder = g_prod.copy()
    best_length = 0
    best_match = None
    best_fixed = None
    best_eliminate = None
    fixed = None
    eliminate = None
    best_corr = 1000000
    best_g_a = None
    best_g_b = None
    best_associations = None
    #ladder_list1 = [[q.index] for q in ladder.es if ladder.es[q.index]["weight_corr"] < THRESH_CORR[SCALING]["filter_bipartite"]]
    ###ladder_list1 = None
    map_graph = {1: graph_ref, 2: graph_targ}

    if initial_filtering_by_special:
        ladder_list1 = [[q.index] for q in ladder.es if
                            (ladder.es[q.index]["weight_corr"] < THRESH_CORR[SCALING]["filter_bipartite"]) and
                            (map_graph[json.loads(ladder.vs[ladder.es[q.index].source]["name"])[0]].vs.find(
                                name=json.loads(ladder.vs[ladder.es[q.index].source]["name"])[1])["isSpecial"]) and
                            (map_graph[json.loads(ladder.vs[ladder.es[q.index].source]["name"])[0]].vs.find(
                                name=json.loads(ladder.vs[ladder.es[q.index].source]["name"])[2])["isSpecial"]) and
                            (map_graph[json.loads(ladder.vs[ladder.es[q.index].target]["name"])[0]].vs.find(
                                name=json.loads(ladder.vs[ladder.es[q.index].target]["name"])[1])["isSpecial"]) and
                            (map_graph[json.loads(ladder.vs[ladder.es[q.index].target]["name"])[0]].vs.find(
                                name=json.loads(ladder.vs[ladder.es[q.index].target]["name"])[2])["isSpecial"])]
    else:
        ladder_list1 = [[q.index] for q in ladder.es if ladder.es[q.index]["weight_corr"] < THRESH_CORR[SCALING]["filter_bipartite"]]
    ladder_list2 = [[q.index] for q in ladder.es if ladder.es[q.index]["weight_corr"] < THRESH_CORR[SCALING]["filter_bipartite"]]
    ladder_list3 = [q.index for q in ladder.es if ladder.es[q.index]["weight_corr"] < THRESH_CORR[SCALING]["filter_bipartite"]]

    ladder_list1 = sorted(ladder_list1, key=lambda x: sum([ladder.es[s]["weight_corr"] for s in x]))

    # a = [[tuple(sorted([map_graph[json.loads(ladder.vs[ladder.es[q[0]].source]["name"])[0]].vs.find(name=json.loads(ladder.vs[ladder.es[q[0]].source]["name"])[1])["secstr"],map_graph[json.loads(ladder.vs[ladder.es[q[0]].source]["name"])[0]].vs.find(name=json.loads(ladder.vs[ladder.es[q[0]].source]["name"])[2])["secstr"]])), tuple(sorted([map_graph[json.loads(ladder.vs[ladder.es[q[0]].target]["name"])[0]].vs.find(name=json.loads(ladder.vs[ladder.es[q[0]].target]["name"])[1])["secstr"],map_graph[json.loads(ladder.vs[ladder.es[q[0]].target]["name"])[0]].vs.find(name=json.loads(ladder.vs[ladder.es[q[0]].target]["name"])[2])["secstr"]]))] for q in ladder_list1]
    # b = set([])
    # l = []
    #print("SHERLOCK INITIAL LEN:",len(ladder_list1))
    # for q, t in enumerate(a):
    #     #print(t,tuple(sorted(t)))
    #     if tuple(sorted(t)) not in b:
    #         b.add(tuple(sorted(t)))
    #         print("ADDING:",tuple(sorted(t)))
    #         l.append(ladder_list1[q])
    # print("FINAL LEN:",len(l))
    # ladder_list1 = l
    ladder_list1b = copy.deepcopy(ladder_list1)
    ladder_list2b = sorted(ladder_list2, key=lambda x: sum([ladder.es[s]["weight_corr"] for s in x]))

    #edge1 = ladder.es.select(lambda e: ladder.vs[e.source]["name"]==json.dumps([1, "65_B", "82_B"]) and ladder.vs[e.target]["name"]==json.dumps([2, "120_D", "150_F"]))[0]
    #edge2 = ladder.es.select(lambda e: ladder.vs[e.source]["name"]==json.dumps([1, "63_B", "82_B"]) and ladder.vs[e.target]["name"]==json.dumps([2, "132_D", "150_F"]))[0]
    # print("EDGE1:",ladder.vs[edge1.source]["name"],ladder.vs[edge1.target]["name"],graph_ref.vs.find(name="65_B")["reslist"],graph_ref.vs.find(name="82_B")["reslist"],graph_targ.vs.find(name="120_D")["reslist"],graph_targ.vs.find(name="150_F")["reslist"])
    # print("EDGE2:",ladder.vs[edge2.source]["name"],ladder.vs[edge2.target]["name"],graph_ref.vs.find(name="63_B")["reslist"],graph_ref.vs.find(name="82_B")["reslist"],graph_targ.vs.find(name="132_D")["reslist"],graph_targ.vs.find(name="150_F")["reslist"])
    # print("CORR edge1:",edge1["weight_corr"],edge1["weight"])
    # print("CORR edge2:",edge2["weight_corr"],edge2["weight"])
    # quit()
    if gui is not None:
        gui.draw_graph(ladder.es.select(lambda e: e.index in ladder_list3).subgraph(), "product", where="top", scale=0.0001, show_labels=False)

    best_for_cycle = []
    secs_seen_1 = set([])
    secs_seen_2 = set([])
    #f = open("cond6-01234567F.txt","w")
    for n in range(ncycles):
        loco = []
        map_processed = {}
        has_been_inserted = False
        now_break = False

        #numpy.random.shuffle(ladder_list1)
        #numpy.random.shuffle(ladder_list2)

        start = time.time()
        looping = True
        if n==0:
            ladder_list2 = [1]
        else:
            # if force_core_expansion_through_secstr:
            #     ladder_list1 = ladder_list1b
            ladder_list2 = ladder_list2b

        while looping:
            looping = False
            for matched in itertools.product(*[ladder_list1, ladder_list2]):
                inserted = False
                if n==0:
                    matched = (matched[0],[])

                if time.time() >= start + max_sec:
                    now_break = True
                if time.time() >= start + break_sec:
                    looping = False
                    break
                if len(ladder_list1) <= 0 or len(ladder_list2) <= 0:
                    looping = False
                    break
                if now_break and (n > 0 or len(loco) >= min_correct):
                    looping = False
                    break
                #if len(ladder_list1)*len(ladder_list2) > 10000:
                #    print("TROPPI",len(ladder_list1)*len(ladder_list2))
                #    matched = ([random.choice(ladder_list1),random.choice(ladder_list2)])

                q = [g for f in matched for a in f for g in [ladder.es[a].source, ladder.es[a].target]]
                t = set(q)

                if len(q) != len(t):
                    continue
                # print(len(q),len(t))
                matched = sorted([a for f in matched for a in f])
                #print(matched)
                #print([l[0] for l in loco])
                if matched in [l[0] for l in loco]:
                    continue

                # match = ladder.maximum_bipartite_matching(types='type', weights="weight")
                # print("Iteration P:",p,"MATCHED EDGES:",len(match.edges()),"LEN EDGES LADDER:",ladder.ecount())
                # print([u.index for u in match.edges()])
                spantree = ladder.es.select(lambda e: e.index in matched).subgraph()

                #if n == 0:
                lista = [(spantree.vs[o.source]["name"], spantree.vs[o.target]["name"]) for o in spantree.es]
                #fixed = [lista[0][0],lista[1][0]]
                #eliminate = [lista[0][1],lista[1][1]]
                fixed = [l[0] for l in lista]
                eliminate = [l[1] for l in lista]

                    #print(fixed,eliminate)
                    #if lista[0][0] in map_processed and map_processed[lista[0][0]] not in matched:
                if all(map(lambda x: x in map_processed and  map_processed[x] not in matched, fixed)):
                    #print("ERRORE",fixed,map_processed.keys(),matched)
                    #print("ERRORE ",lista,"e stato gia incontrato ed equivale a",map_processed[lista],"NON",matched)
                    continue

                if verbose: print("SHERLOCK",[(spantree.vs[t.source]["name"],spantree.vs[t.target]["name"]) for t in spantree.es])

                # spantree.write_graphml(os.path.join("./", os.path.basename(pdb_model)[:-4] + "_matching"+str(p)+".graphml"))
                results = check_isomorphism_in_ladder_graph(spantree, ladder, graph_ref, graph_targ, return_boolean=True)
                if verbose and not results: print("NON ISOMORFO",matched)

                if results:
                    res, corr, g_a, g_b, associations = results
                    # print(matched)
                    # print([(spantree.vs[o.source]["name"], spantree.vs[o.target]["name"]) for o in spantree.es],sum(w))

                    if len(matched) > best_length or (len(matched) == best_length and corr < best_corr+0.5):
                        if gui is not None:
                            bipartite = ladder.es.select(lambda e: e.index in matched).subgraph(delete_vertices=False)
                            bipartite.es["color"] = [(255, 0, 0, 255)] * spantree.ecount()
                            gui.draw_graph(bipartite, "product", where="top", scale=0.0001, show_labels=False)
                            corr, g_a, g_b, associations = check_isomorphism_in_ladder_graph(spantree, ladder, graph_ref,
                                                                                             graph_targ,
                                                                                             return_boolean=False,
                                                                                             pdb_model=pdb_model)
                            gui.draw_graphs_with_same_pos(g_a, g_b, associations, "cage_reference", "cage_target",
                                                          where_a="bottom-right", where_b="bottom-left", scale_a=0.1,
                                                          scale_b=0.1, show_labels_a=True, show_labels_b=True)
                            if corr < best_corr:
                                gui.draw_text("FOUND NEW BEST: " + str(matched) + " number of matched edges: " + str(len(matched)) + " SumErrors: " + str(corr))

                        results = select_best_superposition_overall_cycles("", [(len(matched), corr, matched, fixed, eliminate, g_a, g_b, associations)],
                                                                           reference, target, graph_ref, graph_targ, write_pdb=False, gui=gui, verbose=False)

                        if verbose: print("RMSD before local optimization:", results["rmsd"], "ASSOCIATIONS:", associations, "CORR:", corr)
                        # uno = graph_ref.vs.find(name=json.loads(fixed[0])[1] if isinstance(fixed[0],str) else fixed[0][1])
                        # due = graph_ref.vs.find(name=json.loads(fixed[0])[2] if isinstance(fixed[0],str) else fixed[0][2])
                        # tre = graph_targ.vs.find(name=json.loads(eliminate[0])[1] if isinstance(eliminate[0],str) else eliminate[0][1])
                        # quattro = graph_targ.vs.find(name=json.loads(eliminate[0])[2] if isinstance(eliminate[0],str) else eliminate[0][2])
                        # print("Uno",uno["name"],"is",uno["reslist"],uno["secstr"])
                        # print("Due",due["name"],"is",due["reslist"],due["secstr"])
                        # print("Tre",tre["name"],"is",tre["reslist"],tre["secstr"])
                        # print("Quattro",quattro["name"],"is",quattro["reslist"],quattro["secstr"])
                        # print(graph_ref.es[graph_ref.get_eid(uno.index,due.index)]["metric"])
                        # #######print(list(graph_ref.es[graph_ref.get_eid(uno.index,due.index)]["metric2"]))
                        # print(graph_targ.es[graph_targ.get_eid(tre.index,quattro.index)]["metric"])
                        # #######print(list(graph_targ.es[graph_targ.get_eid(tre.index,quattro.index)]["metric2"]))

                        if results["rmsd"] < 0.8:
                            inserted = True
                            loco.append((matched, corr))
                        elif n == 0 and corr <= 0.6:
                            found_new_match, matched, spantree, res, corr, g_a, g_b, associations,results,fixed,eliminate  = local_optimization_of_vector_alignment(matched, spantree, res, corr, g_a, g_b, associations, results, ladder, graph_ref, graph_targ, reference, target, start_time=start, break_sec=break_sec)
                            if found_new_match:
                                inserted = True
                                loco.append((matched, corr))
                            else:
                                inserted = False
                        else:
                            inserted = False

                        if verbose: print("RMSD after local optimization:", results["rmsd"], "ASSOCIATIONS:", associations, "CORR:", corr)
                        # uno = graph_ref.vs.find(
                        #     name=json.loads(fixed[0])[1] if isinstance(fixed[0], str) else fixed[0][1])
                        # due = graph_ref.vs.find(
                        #     name=json.loads(fixed[0])[2] if isinstance(fixed[0], str) else fixed[0][2])
                        # tre = graph_targ.vs.find(
                        #     name=json.loads(eliminate[0])[1] if isinstance(eliminate[0], str) else eliminate[0][1])
                        # quattro = graph_targ.vs.find(
                        #     name=json.loads(eliminate[0])[2] if isinstance(eliminate[0], str) else eliminate[0][2])
                        # print("Uno", uno["name"], "is", uno["reslist"], uno["secstr"])
                        # print("Due", due["name"], "is", due["reslist"], due["secstr"])
                        # print("Tre", tre["name"], "is", tre["reslist"], tre["secstr"])
                        # print("Quattro", quattro["name"], "is", quattro["reslist"], quattro["secstr"])
                        # print(graph_ref.es[graph_ref.get_eid(uno.index, due.index)]["metric"])
                        # ######print(list(graph_ref.es[graph_ref.get_eid(uno.index, due.index)]["metric2"]))
                        # print(graph_targ.es[graph_targ.get_eid(tre.index, quattro.index)]["metric"])
                        # ######print(list(graph_targ.es[graph_targ.get_eid(tre.index, quattro.index)]["metric2"]))

                        #f.write("RMSD: " + str(results["rmsd"]) + " ASSOCIATIONS: " + str(associations) + " CORR: " + str(corr) + "\n")

                        if inserted and (len(matched) > best_length or corr < best_corr):
                            has_been_inserted = True
                            if verbose: print("FOUND NEW BEST:", matched)
                            if verbose: print([(spantree.vs[o.source]["name"], spantree.vs[o.target]["name"]) for o in spantree.es],corr)
                            # print([(map_graph[json.loads(spantree.vs[o.source]["name"])[0]].vs.find(name=json.loads(spantree.vs[o.source]["name"])[1])["reslist"], map_graph[json.loads(spantree.vs[o.source]["name"])[0]].vs.find(name=json.loads(spantree.vs[o.source]["name"])[2])["reslist"], map_graph[json.loads(spantree.vs[o.target]["name"])[0]].vs.find(name=json.loads(spantree.vs[o.target]["name"])[1])["reslist"], map_graph[json.loads(spantree.vs[o.target]["name"])[0]].vs.find(name=json.loads(spantree.vs[o.target]["name"])[2])["reslist"]) for o in spantree.es])
                            # ellen = [(map_graph[json.loads(spantree.vs[o.source]["name"])[0]].es[map_graph[json.loads(spantree.vs[o.source]["name"])[0]].get_eid(map_graph[json.loads(spantree.vs[o.source]["name"])[0]].vs.find(name=json.loads(spantree.vs[o.source]["name"])[1]).index, map_graph[json.loads(spantree.vs[o.source]["name"])[0]].vs.find(name=json.loads(spantree.vs[o.source]["name"])[2]).index)], map_graph[json.loads(spantree.vs[o.target]["name"])[0]].es[map_graph[json.loads(spantree.vs[o.target]["name"])[0]].get_eid(map_graph[json.loads(spantree.vs[o.target]["name"])[0]].vs.find(name=json.loads(spantree.vs[o.target]["name"])[1]).index, map_graph[json.loads(spantree.vs[o.target]["name"])[0]].vs.find(name=json.loads(spantree.vs[o.target]["name"])[2]).index)]) for o in spantree.es]
                            # print("METRIC1:",ellen[0][0]["metric"],ellen[0][1]["metric"])
                            # print("METRIC-1:",ellen[0][0]["metric2"],ellen[0][1]["metric2"])
                            # print("METRIC2:",ellen[1][0]["metric"],ellen[1][1]["metric"])
                            # print("METRIC-2:",ellen[1][0]["metric2"],ellen[1][1]["metric2"])
                            # print("CORR1:",scipy.spatial.distance.correlation(ellen[0][0]["metric2"], ellen[0][1]["metric2"]))
                            # [('[1, "13_A", "5_A"]', '[2, "5_C", "6_C"]'), ('[1, "14_A", "5_A"]', '[2, "5_C", "7_C"]')]
                            # u1 = [1, "13_A", "5_A"]
                            # u2 = [2, "4_C", "6_C"]
                            # u3 = [1, "14_A", "5_A"]
                            # u4 = [2, "4_C", "7_C"]
                            # print([(map_graph[a[0]].vs.find(name=a[1])["reslist"], map_graph[a[0]].vs.find(name=a[2])["reslist"], map_graph[b[0]].vs.find(name=b[1])["reslist"], map_graph[b[0]].vs.find(name=b[2])["reslist"]) for a,b in [(u1,u2),(u3,u4)]])
                            # ellen = [(map_graph[a[0]].es[
                            #               map_graph[a[0]].get_eid(
                            #                   map_graph[a[0]].vs.find(
                            #                       name=a[1]).index,
                            #                   map_graph[a[0]].vs.find(
                            #                       name=a[2]).index)],
                            #           map_graph[b[0]].es[
                            #               map_graph[b[0]].get_eid(
                            #                   map_graph[b[0]].vs.find(
                            #                       name=b[1]).index,
                            #                   map_graph[b[0]].vs.find(
                            #                       name=b[2]).index)]) for a,b in [(u1,u2),(u3,u4)]]
                            # print("METRIC1:", ellen[0][0]["metric"], ellen[0][1]["metric"])
                            # print("METRIC-1:", ellen[0][0]["metric2"], ellen[0][1]["metric2"])
                            # print("METRIC2:", ellen[1][0]["metric"], ellen[1][1]["metric"])
                            # print("METRIC-2:", ellen[1][0]["metric2"], ellen[1][1]["metric2"])
                            # print("CORR1:", scipy.spatial.distance.correlation(ellen[0][0]["metric2"], ellen[0][1]["metric2"]))
                            # print("CORR2:", scipy.spatial.distance.correlation(ellen[1][0]["metric2"], ellen[1][1]["metric2"]))
                            # #print("PLANE1:",ellen[0][0]["plane_equation"],ellen[0][1]["plane_equation"])
                            # #print("PLANE2:",ellen[1][0]["plane_equation"],ellen[1][1]["plane_equation"])
                            # quit()
                            best_corr = corr
                            best_match = matched
                            best_g_a = g_a
                            best_g_b = g_b
                            best_associations = associations
                            best_fixed = fixed
                            best_eliminate = eliminate
                        best_length = len(matched)

                if n == 0: #or inserted:
                    fixed = [json.dumps(s).strip("'\"").replace("\\", "") for s in fixed]
                    if inserted:
                        for di,ele in enumerate(fixed):
                            map_processed[ele] = matched[di]

                    looping = True
                    #fixed = [json.dumps(t) if isinstance(t,list) else t for t in fixed]
                    #fixed = [json.dumps(json.loads(t)) for t in fixed]

                    if verbose: print("BEFORE TRIMMING",len(ladder_list1),"FIXED",fixed,"MATCHED",matched)

                    ladder_list1 = [[q] for w in ladder_list1 for q in w if (ladder.vs[ladder.es[q].source]["name"] not in fixed or (inserted and q in matched) or (not inserted and q not in matched)) and (ladder.vs[ladder.es[q].target]["name"] not in fixed or (inserted and q in matched) or (not inserted and q not in matched))]

                    if verbose: print("AFTER TRIMMING",len(ladder_list1))
                    ladder_list1 = sorted(ladder_list1, key=lambda x: sum([ladder.es[s]["weight_corr"] for s in x]))
                    #print("VERIFICO [263088]",[263088] in ladder_list1)
                    #print(ladder.vs[ladder.es[263088].source]["name"],ladder.vs[ladder.es[263088].target]["name"],fixed,matched,ladder.vs[ladder.es[263088].target]["name"] not in fixed)
                    # print("BEFORE TRIMMING 2", len(ladder_list2))
                    # ladder_list2 = [[q.index] for q in ladder.es if [q.index] in ladder_list2 and (
                    # ladder.vs[q.source]["name"] not in fixed or q.index in matched) and (
                    #                 ladder.vs[q.target]["name"] not in fixed or q.index in matched)]
                    # print("AFTER TRIMMING 2", len(ladder_list2))
                    # ladder_list2 = sorted(ladder_list2, key=lambda x: sum([ladder.es[s]["weight_corr"] for s in x]))
                    break

                if n > 0 and force_core_expansion_through_secstr and inserted:
                    uno = graph_ref.vs.find(name=json.loads(fixed[0])[1] if isinstance(fixed[0],str) else fixed[0][1])
                    due = graph_ref.vs.find(name=json.loads(fixed[0])[2] if isinstance(fixed[0],str) else fixed[0][2])
                    tre = graph_targ.vs.find(name=json.loads(eliminate[0])[1] if isinstance(eliminate[0],str) else eliminate[0][1])
                    quattro = graph_targ.vs.find(name=json.loads(eliminate[0])[2] if isinstance(eliminate[0],str) else eliminate[0][2])
                    if verbose: print("Uno",uno["name"],"is",uno["reslist"],uno["secstr"])
                    if verbose: print("Due",due["name"],"is",due["reslist"],due["secstr"])
                    if verbose: print("Tre",tre["name"],"is",tre["reslist"],tre["secstr"])
                    if verbose: print("Quattro",quattro["name"],"is",quattro["reslist"],quattro["secstr"])
                    secs_seen_1.add(uno["secstr"])
                    secs_seen_1.add(due["secstr"])
                    secs_seen_2.add(tre["secstr"])
                    secs_seen_2.add(quattro["secstr"])
                    l1 = []
                    for ele in ladder_list1b:
                        name_source = ladder.vs[ladder.es[ele[0]].source]["name"]
                        name_target = ladder.vs[ladder.es[ele[0]].target]["name"]
                        #print("NAME SOURCE",name_source,"NAME TARGET",name_target)
                        graph_id_s,s1,s2 = json.loads(name_source)
                        graph_id_t,t1,t2 = json.loads(name_target)
                        sl = set([map_graph[graph_id_s].vs.find(name=s1)["secstr"], map_graph[graph_id_s].vs.find(name=s2)["secstr"]])
                        tl = set([map_graph[graph_id_t].vs.find(name=t1)["secstr"], map_graph[graph_id_t].vs.find(name=t2)["secstr"]])
                        #print("SECSEEN_1", secs_seen_1, "SECSEEN_2", secs_seen_2, "sl", sl, "tl", tl)

                        if len(sl&secs_seen_1) < 2 and len(tl&secs_seen_2) < 2: #they can share only 0 or 1 secondary structure but not both
                            l1.append(ele)
                            #print("ADDING",ele)
                    ladder_list1b = l1
                    l2 = []
                    for ele in ladder_list2b:
                        name_source = ladder.vs[ladder.es[ele[0]].source]["name"]
                        name_target = ladder.vs[ladder.es[ele[0]].target]["name"]
                        # print("NAME SOURCE",name_source,"NAME TARGET",name_target)
                        graph_id_s, s1, s2 = json.loads(name_source)
                        graph_id_t, t1, t2 = json.loads(name_target)
                        sl = set([map_graph[graph_id_s].vs.find(name=s1)["secstr"],
                                  map_graph[graph_id_s].vs.find(name=s2)["secstr"]])
                        tl = set([map_graph[graph_id_t].vs.find(name=t1)["secstr"],
                                  map_graph[graph_id_t].vs.find(name=t2)["secstr"]])
                        # print("SECSEEN_1", secs_seen_1, "SECSEEN_2", secs_seen_2, "sl", sl, "tl", tl)

                        if len(sl & secs_seen_1) < 2 and len(tl & secs_seen_2) < 2:  # they can share only 0 or 1 secondary structure but not both
                            l2.append(ele)
                            # print("ADDING",ele)
                    ladder_list2b = l2
                    #quit()

        if has_been_inserted:
            best_for_cycle.append((best_length,best_corr,best_match,best_fixed,best_eliminate,best_g_a,best_g_b,best_associations))
            has_been_inserted = False

        multi = top
        if deep:
            if verbose: print(len(loco), (ncycles - n) * multi)
            # print(len(loco), (n+1)*5)
        else:
            if verbose: print(len(loco), top)
        # quit()
        if deep:
            ladder_list1 = [pera[0] for pera in sorted(loco, key=lambda x: x[1])[:(ncycles - n) * multi if len(loco) > (ncycles - n) * multi else len(loco)]]
            # ladder_list1 = [pera[0] for pera in sorted(loco,key=lambda x: x[1])[:(n+1)*10 if len(loco) > (n+1)*10 else len(loco)]]
        else:
            ladder_list1 = [pera[0] for pera in sorted(loco, key=lambda x: x[1])[:top if len(loco) > top else len(loco)]]

        #ladder_list2 = [[q.index] for q in ladder.es if ladder.es[q.index]["weight_corr"] < THRESH_CORR[SCALING]["filter_bipartite"]]

    #####print(";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
    if len(best_for_cycle) == 0 or all([t[2] == None for t in best_for_cycle]):
        #print("STRANO len(best_for_cycle) == 0",len(best_for_cycle) == 0,"all([t[2] == None for t in best_for_cycle]",all([t[2] == None for t in best_for_cycle]))
        return []

    #spantree = ladder.es.select(lambda e: e.index in best_match).subgraph()
    #corr, g_a, g_b, associations = check_isomorphism_in_ladder_graph(spantree, ladder, graph_ref, graph_targ,
    #                                                                 return_boolean=False, pdb_model=pdb_model)
    #print("BEST ASSOCIATIONS:", associations, "WITH CORR:", corr)

    #return corr, g_a, g_b, associations
    #f.close()
    return best_for_cycle

# @SystemUtility.timing
# @SystemUtility.profileit
def format_and_remove_redundance(cvs_global, sep_chains, only_reformat=False):
    """
    Format CVs and remove redundance for chains with identical values of CVs
    
    :param cvs_global: list of CVs
    :type cvs_global: list of lists
    :param sep_chains: list of delimiters ids for different chains
    :type sep_chains: list of tuples
    :param only_reformat: True if only reformat must be done but not removing, False to allow removing
    :type only_reformat: bool
    :return: 
    :rtype: 
    :raise: ValueError if sep_chains is empty
    """

    if len(sep_chains) == 0:
        raise ValueError('sep_chains cannot be empty')

    if len(sep_chains) == 1:
        return [cvs_global]

    done = []
    equals = {}
    for i in range(len(sep_chains)):
        a = sep_chains[i]
        if i not in equals:
            equals[i] = []
            done.append(i)
        for j in range(i + 1, len(sep_chains)):
            if j in done:
                continue

            b = sep_chains[j]
            equal = True
            if only_reformat:
                equal = False
            else:
                if a[1] - a[0] == b[1] - b[0]:
                    for p in range(a[1] - a[0] - 1):
                        in_i_a = cvs_global[a[0] + p]
                        in_j_a = cvs_global[a[0] + p + 1]
                        in_i_b = cvs_global[b[0] + p]
                        in_j_b = cvs_global[b[0] + p + 1]
                        dip_a = compute_instruction(in_i_a, in_j_a)
                        dip_b = compute_instruction(in_i_b, in_j_b)

                        if not is_compatible(dip_a, dip_b, verbose=False, test_equality=True):
                            equal = False
                            break
                else:
                    equal = False

            if equal:
                if i in equals:
                    equals[i].append(j)
                else:
                    equals[i] = [j]
                done.append(j)

    cvs_list = []
    for key in equals:
        cvs_list.append(cvs_global[sep_chains[key][0]:sep_chains[key][1]])

    return cvs_list


def validate_residue(residue, ca_list, o_list, all_atom_ca, number_of_residues, ignore):
    """
    Validates a residue and update the passed lists. It allows only valid residues according Bioinformatics.AAList with atoms with at least an occupancy of 10% 
    
    :param residue: Residue object
    :type residue: Bio.PDB.Residue
    :param ca_list: list of coords and properties for CA atoms
    :type ca_list: list [0] pos_X [1] pos_Y [2] pos_Z [3] residue full id [4] residue name code in 3 letters
    :param o_list: list of coords and properties for O atoms
    :type o_list: list [0] pos_X [1] pos_Y [2] pos_Z [3] residue full id [4] residue name code in 3 letters
    :param all_atom_ca: array of CA atoms
    :type all_atom_ca: list of Bio.PDB.Atom
    :param number_of_residues: number of residues read
    :type number_of_residues: int
    :param ignore: set of residue full ids to be ignored
    :type ignore: set
    :return coord_ca, o_list, all_atom_ca, number_of_residues: 
    :rtype (list, list, list, int): 
    """

    if (residue.get_resname().upper() in Bioinformatics3.AAList) and (residue.has_id("CA")) and (
    residue.has_id("O")) and (residue.has_id("C")) and (residue.has_id("N")):
        if residue.get_full_id() in ignore:
            return ca_list, o_list, all_atom_ca, number_of_residues

        ca = residue["CA"]
        o = residue["O"]
        if any(map(lambda x: x.get_occupancy() < 0.1, [ca, o, residue["C"], residue["N"]])):
            return ca_list, o_list, all_atom_ca, number_of_residues

        number_of_residues += 1

        # for each atom 4 values are saved:
        # [0] pos_X [1] pos_Y [2] pos_Z [3] residue full id [4] residue name code in 3 letters
        co_ca = ca.get_coord()
        co_o = o.get_coord()
        ca_list.append(
            [float(co_ca[0]), float(co_ca[1]), float(co_ca[2]), residue.get_full_id(), residue.get_resname()])
        all_atom_ca.append(ca)
        o_list.append([float(co_o[0]), float(co_o[1]), float(co_o[2]), residue.get_full_id(), residue.get_resname()])

    return ca_list, o_list, all_atom_ca, number_of_residues


def get_cvs(structure, use_list=[], ignore_list=[], length_fragment=3, one_model_per_nmr=False):
    """
    Parse a structure and generate for every consecutive 'length_fragment' residues a CV with a window f 1 overlapping residue.
    
    :param structure: The structure object of the structure
    :type structure: Bio.PDB.Structure
    :param use_list: 
    :type use_list: list
    :param ignore_list: 
    :type ignore_list: list
    :param length_fragment: Define the peptide length for computing a CV
    :type length_fragment: int
    :param one_model_per_nmr: 
    :type one_model_per_nmr: bool
    :return (cvs, separating_chains): List of CVs and the id separation for each chain
    :rtype: (list,list)
    """

    allAtomCA = []
    ca_list = []
    o_list = []
    numberOfResidues = 0
    separating_chains = []
    start_separa = 0
    end_separa = 0
    cvs = []

    if len(use_list) > 0:
        for fra in use_list:
            lir = [residue for residue in Bio.PDB.Selection.unfold_entities(structure[fra["model"]][fra["chain"]], "R")
                   if residue.get_id() in fra["resIdList"]]
            for residue in lir:
                ca_list, o_list, allAtomCA, numberOfResidues = validate_residue(residue, ca_list, o_list, allAtomCA,
                                                                                numberOfResidues, ignore_list)
    elif one_model_per_nmr:
        #print('SHERLOCK structure.get_list()[0]',structure.get_list()[0])
        #print('SHERLOCK type(structure.get_list()[0])', type(structure.get_list()[0]))
        lir = Bio.PDB.Selection.unfold_entities(structure.get_list()[0], "R")
        for residue in lir:
            ca_list, o_list, allAtomCA, numberOfResidues = validate_residue(residue, ca_list, o_list, allAtomCA,
                                                                            numberOfResidues, ignore_list)
    else:
        lir = Bio.PDB.Selection.unfold_entities(structure, "R")
        for residue in lir:
            ca_list, o_list, allAtomCA, numberOfResidues = validate_residue(residue, ca_list, o_list, allAtomCA,
                                                                            numberOfResidues, ignore_list)

    # This is the number of possible cvs n_cvs = n_aa - (n_peptides - 1) = n_aa - n_peptides + 1
    numberOfSegments = numberOfResidues - length_fragment + 1

    coordCA = numpy.array([c[:3] for c in ca_list])
    coordO = numpy.array([c[:3] for c in o_list])

    if numberOfSegments <= 0:
        # print ("\t\t\tNo enough residues available to create a fragment")
        return cvs, separating_chains

    vectorsCA = numpy.empty((numberOfSegments, 3))
    vectorsCA.fill(0.0)
    vectorsO = numpy.empty((numberOfSegments, 3))
    vectorsO.fill(0.0)
    vectorsH = numpy.empty((numberOfSegments, 1))
    vectorsH.fill(0.0)

    # a  b  c  d  e  f
    # |--0--|
    #    |--1--|
    #       |--2--|
    #          |--3--|
    # ==================
    # 4 vectors (from 0 to 3)
    #
    # |--0--| = a/3+b/3+c/3
    # |--1--| = |--0--|+(d-a)/3 = a/3 + b/3 + c/3 + d/3 -a/3 = b/3 + c/3 + d/3
    # |--2--| = |--1--|+(e-b)/3 = b/3 + c/3 + d/3 + e/3 -b/3 = c/3 + d/3 + e/3

    vectorsCA[0] = vectorsCA[0] + (coordCA[:length_fragment, :] / float(length_fragment)).sum(axis=0)
    vectorsO[0] = vectorsO[0] + (coordO[:length_fragment, :] / float(length_fragment)).sum(axis=0)
    for i in range(1, len(vectorsCA)):
        vectorsCA[i] = vectorsCA[i - 1] + (coordCA[i + length_fragment - 1] - coordCA[i - 1]) / float(length_fragment)
        vectorsO[i] = vectorsO[i - 1] + (coordO[i + length_fragment - 1] - coordO[i - 1]) / float(length_fragment)

    H = vectorsCA - vectorsO
    vectorsH = numpy.sqrt((H ** 2).sum(axis=1))

    last_chain = None

    for i in range(len(vectorsCA)):
        # if same occupancy take the lowest bfactor
        prevRes = (" ", None, " ")
        ncontigRes = 0
        resids = []
        prev_model = None
        prev_chain = None

        for yui in range(i, i + length_fragment):  # quindi arrivo a i+lengthFragment-1
            resan = (ca_list[yui])[3]
            resids.append(list(resan) + [ca_list[yui][4]])
            resa = resan[3]

            if prevRes == (" ", None, " "):
                ncontigRes += 1
            elif prev_chain == None or prev_chain == resan[2]:
                resaN = Bioinformatics3.get_residue(structure, resan[1], resan[2], resan[3])
                prevResC = Bioinformatics3.get_residue(structure, prev_model, prev_chain, prevRes)
                if Bioinformatics3.check_continuity(prevResC, resaN):
                    ncontigRes += 1
            prevRes = resa
            prev_model = resan[1]
            prev_chain = resan[2]

        if ncontigRes != length_fragment:
            vectorsH[i] = 100  # this value identify a not reliable measure for cv
        else:
            cvs.append([i, vectorsH[i], vectorsCA[i], vectorsO[i], resids])

        if prev_chain == last_chain:
            end_separa = len(cvs)
        else:
            last_chain = prev_chain
            if start_separa < end_separa:
                separating_chains.append((start_separa, end_separa))
            start_separa = end_separa

    if start_separa < end_separa:
        separating_chains.append((start_separa, end_separa))

    if len(separating_chains) > 0 and separating_chains[0] == (0, 0):
        separating_chains = separating_chains[1:]  # this is done to eliminate the first (0,0) that is unuseful

    return cvs, separating_chains


def get_ss_from_cvl(cvl1):
    """
    Return ah,bs or coil for the cvl in input
    
    :param cvl1: 
    :type cvl1: 
    :return: 
    :rtype: 
    """

    delta_cvla = 0.2  # 0.2
    delta_cvlb = 0.05  # 0.12
    exty1 = "bs" if (float(cvl1) >= 1.4 - delta_cvlb and float(cvl1) <= 1.4 + delta_cvlb) else "coil"
    if exty1 == "coil":
        exty1 = "ah" if (float(cvl1) >= 2.2 - delta_cvla and float(cvl1) <= 2.2 + delta_cvla) else "coil"
    return exty1


def get_unique_cv_among_residues(strucc, resilist):
    """
    
    :param strucc: 
    :type strucc: 
    :param resilist: 
    :type resilist: 
    :return: 
    :rtype: 
    """

    listCA = numpy.empty((len(resilist), 3))
    listO = numpy.empty((len(resilist), 3))
    for i, x in enumerate(resilist):
        resi = Bioinformatics3.get_residue(strucc, x[1], x[2], x[3])
        listCA[i] = resi["CA"].get_coord()
        listO[i] = resi["O"].get_coord()
    if len(listCA) == 0 or len(listO) == 0:
        return None

    CAx = listCA.mean(axis=0)
    Ox = listO.mean(axis=0)
    return [0, 0, CAx, Ox, []]


def get_all_fragments(graph):
    graph.vs["resIdList"] = graph.vs["reslist"]
    graph.vs["pdbid"] = [p[0][0] for p in graph.vs["reslist"]]
    graph.vs["model"] = [p[0][1] for p in graph.vs["reslist"]]
    graph.vs["chain"] = [p[0][2] for p in graph.vs["reslist"]]
    graph.vs["fragLength"] = [len(p) for p in graph.vs["reslist"]]
    l = sorted([v for v in graph.vs], key=lambda x: tuple(x["reslist"][0]))

    return l


def get_connected_fragment_to_edge(fragment, edge):
    ind = fragment.index
    if edge.source == ind:
        return edge.graph.vs[edge.target]
    elif edge.target == ind:
        return edge.graph.vs[edge.source]
    else:
        return None


def get_vseq_neighbours_fragments(graph, fragment, sortmode=None):
    if not sortmode:
        return fragment.neighbors()  # VertexSeq
    else:
        return [get_connected_fragment_to_edge(fragment, edge) for edge in
                sorted(graph.es.select(graph.incident(fragment)), key=lambda x: x[sortmode])]  # VertexSeq


def get_eseq_neighbours_fragments(graph, fragment, sortmode=None):  # sortmode="avg",sortmode="min"
    if not sortmode:
        return [graph.es[graph.get_eid(frag.index, fragment.index)] for frag in fragment.neighbors()]  # EdgeSeq
    else:
        #print(graph.incident(fragment), type(graph.es.select(graph.incident(fragment))))
        return sorted(graph.es.select(graph.incident(fragment)), key=lambda x: x[sortmode])  # EdgeSeq


@SystemUtility.timing
# @SystemUtility.profileit
def get_3d_cvs_matrix(cvs, is_model, maximum_distance=None, maximum_distance_bs=None, just_diagonal_plus_one=False,
                      mixed_chains=False):
    if mixed_chains:
        cvs = [cv for cvst in cvs for cv in cvst]

    n = len(cvs)

    # matrice = ADT.get_matrix(n,n)
    high_d = 0

    ####Sparse matrices we just need a sparse triangular matrix that can grow
    ###matrice = scipy.sparse.lil_matrix((n,n), dtype=list)

    if is_model:
        matrix = {}
        matrix["n"] = n
        matrix["fragments_bounds"] = [[0]]

        for i in range(n):
            for j in range(i, n):
                if just_diagonal_plus_one and j != i + 1:
                    continue

                valued = compute_instruction(cvs[i], cvs[j])
                if maximum_distance != None and valued[3] >= maximum_distance:
                    continue

                if maximum_distance_bs != None and valued[-1] == ("bs", "bs") and valued[3] >= maximum_distance_bs:
                    continue

                matrix[(i, j)] = valued
                if valued[3] > high_d:
                    high_d = valued[3]

                if j == i + 1:
                    if valued[0] != 1:
                        matrix["fragments_bounds"][-1].append(i)
                        matrix["fragments_bounds"].append([j])
    else:
        # NOTE: when is not is_model maximum_distance and maximum_distance_bs are ignored. If we really want that filters then after this creation
        # I should do something to filter them out.
        matrix = {(i, j): compute_instruction(cvs[i], cvs[j]) for i in range(n) for j in range(i, n) if
                  not just_diagonal_plus_one or j != i + 1}
        matrix["n"] = n

    if is_model:
        if matrix[(n - 2, n - 1)][0] == 1:
            matrix["fragments_bounds"][-1].append(n - 1)
        else:
            matrix["fragments_bounds"][-1].append(n - 1)
            # matrice["fragments_bounds"].append([n-1,n-1])
        matrix, cvs = compute_scores(matrix, cvs)
        return matrix, cvs, high_d
    else:
        return matrix, cvs, None

def print_pattern(pattern):
    print("CONTINOUS FRAGMENTS:")
    for f in range(len(pattern["continous_locations"])):
        print("=====================Frag. n.: ", f, "========================")
        for index in pattern["continous_locations"][f]:
            i, j = index
            u = pattern[(i, j)]

            if i != j:
                ssdes = ""
                if u[6][0] == u[6][1] and u[0] == 1:
                    ssdes = u[6][0] + "\t"
                else:
                    ssdes = u[6][0] + " - " + u[6][1] + "\t"

                print(ssdes, i, j, u[0], u[1], u[2], u[3], u[4], u[5][0][1], u[5][0][2], list(map(lambda x: x[3][1], u[5])))

        print("=====================Scores Frag. n.:", f, "==================")
        print( "Score CV:             ", pattern["fragments_scores"][f][0])
        print( "Score angle vectors:  ", pattern["fragments_scores"][f][1])
        print( "Score distance:       ", pattern["fragments_scores"][f][2])
        print( "Score angle distance: ", pattern["fragments_scores"][f][3])
        print( "============================================================")

    print("CHECKING CONTROLS")
    for f in range(len(pattern["jumps_locations"])):
        s, r, A, B, C, D, E = pattern["jumps_locations"][f]
        # s,r,A,B,C,D = pattern["jumps_locations"][f]
        print( "=====================Check: ", s, r, "========================")
        for index in pattern["jumps_locations"][f][2:]:
            i, j = index
            u = pattern[(i, j)]

            if i != j:
                ssdes = ""
                if u[6][0] == u[6][1] and u[0] == 1:
                    ssdes = u[6][0] + "\t"
                else:
                    ssdes = u[6][0] + " - " + u[6][1] + "\t"

                print(ssdes, i, j, u[0], u[1], u[2], u[3], u[4])
        print("=====================Scores Check:", s, r, "==================")
        print( "Score CV:             ", pattern["jumps_scores"][f][2])
        print( "Score angle vectors:  ", pattern["jumps_scores"][f][3])
        print( "Score distance:       ", pattern["jumps_scores"][f][4])
        print( "Score angle distance: ", pattern["jumps_scores"][f][5])
        print( "============================================================")
    print()


@SystemUtility.timing
# @SystemUtility.profileit
def aleph_secstr(strucc, cvs_list, matrix, min_ah=None, min_bs=None, min_diff_ah=0.45, min_diff_bs=0.20):
    """
    Annotates the secondary structure through CVs and return a graph with no edges
    # FORMULA ALPHA ANGLE
    #n = 0.5
    #mean = 20.0
    #v = 0.9
    #p = 0.5
    #topx = 180.0
    #step = 0.01

    # FORMULA BETA ANGLE
    #n=0.5
    # mean = 54.0
    # v = 0.9
    # p = 0.5
    # topx = 180.0
    # step = 0.01

    # FORMULA ALPHA CVL
    #n=0.5 or 1
    # mean = 2.2
    # v = 0.9
    # v = 0.0 this is to have a plateau with 0 after 2.2
    # p = 0.8
    # p = 1.0 this is to have a plateau with 0 after 2.2
    # topx = 2.4
    # step = 0.01

    # FORMULA BETA CVL
    # n=0.5 or 1
    # mean = 1.4
    # v = 0.9
    # p = 0.8
    # topx = 2.4
    # step = 0.01
        
    :param strucc: 
    :type strucc: 
    :param cvs_list: 
    :type cvs_list: 
    :param min_ah: 
    :type min_ah: 
    :param min_bs: 
    :type min_bs: 
    :param min_diff_ah: 
    :type min_diff_ah: 
    :param min_diff_bs: 
    :type min_diff_bs: 
    :return: 
    :rtype: 
    """

    global BS_UD_EA
    global BS_UU_EA
    global BS_MAX

    dist_mean_bs = 5.1
    dist_mean_ah = 0.0
    dist_num_ah = 0
    angle_mean_bs = 54
    angle_mean_ah = 20
    cvl_mean_bs = 1.4
    cvl_mean_ah = 2.2
    thresh_scores = 1.5

    a = [[lis[1], get_ss_from_cvl(lis[1]), lis[4], lis[0]] for lis in cvs_list]
    dimap = {value[0]: i for (i, value) in enumerate(cvs_list)}

    def __scoring_tick_fn(u, mean, topx, v=0.9, p=0.5, n=0.5):
        r = numpy.abs((u - mean) / mean) ** n if u <= mean else (((((u - mean) * ((mean * v))) / (
        mean + ((topx - mean) * p) - mean)) / mean)) ** n if u <= mean + ((topx - mean) * p) else (v + (((((u - (
        mean + (topx - mean) * p)) * (mean - (mean * v))) / (topx - (mean + (topx - mean) * p) + (
        mean * v))) / mean))) ** n
        return r

    def __check_by_unified_score_step2(uno, due, dizio3d, take_first=True, validate=["bs", "coil"], min_num_bs=1.0):
        ###value1 = compute_instruction(cvs_list[dimap[uno[3]]], cvs_list[dimap[due[3]]])
        sup = tuple(sorted([dimap[uno[3]], dimap[due[3]]]))
        value1 = matrix[sup]
        if value1[0] != 1:
            return uno, due, True

        beta_score_uno = 100000
        alpha_score_uno = 100000
        beta_score_due = 100000
        alpha_score_due = 100000
        #if uno[3] == 134:
        #    print("BEFORE UNO",uno[1], uno[0], value1[2], uno[2], "---", uno[3])
        if take_first and (dizio3d is None or uno[1] in validate):
            beta_score_uno = __scoring_tick_fn(uno[0], cvl_mean_bs, 2.4, v=0.9, p=0.8, n=1) + __scoring_tick_fn(
                value1[2], angle_mean_bs, 180.0, v=0.9, p=0.5, n=0.5) #n=0.5
            alpha_score_uno = __scoring_tick_fn(uno[0], cvl_mean_ah, 2.4, v=0.0, p=1.0, n=1) + __scoring_tick_fn(
                value1[2], angle_mean_ah, 180.0, v=0.9, p=0.5, n=0.5)
            CA_CA_d = value1[3]

            if dizio3d is not None:
                #if uno[3] == 134:
                #    print("UNO cvl+int_angles bs:",beta_score_uno,"ah:",alpha_score_uno)
                if uno[3] not in dizio3d or len(dizio3d[uno[3]]) == 0:
                    listuno = []
                    beta_score_uno += 5
                else:
                    listuno = sorted(dizio3d[uno[3]], key=lambda x: x[2])
                    # NOTE: Here we do not take the absolute value of the difference because when the min distance is lower than the mean
                    #      in principle is not a bad condition and we want to add just 0 in that case
                    beta_score_uno += __scoring_tick_fn(listuno[0][2], dist_mean_bs, 10.0, v=0.9, p=0.5, n=0.5) if listuno[0][2] >= dist_mean_bs else 0  #n=0.5

                if len(listuno) < min_num_bs:
                    beta_score_uno += 5
                else:
                    # NOTE: Add the external angles
                    listuno = sorted(listuno, key=lambda x: x[2], reverse=True)
                    listunobleah = sorted([p[2] for p in listuno], reverse=True)
                    f = [((-1.0 * (t + 1)) / (e * len(listuno)))*2*(max(BS_UD_EA[int(round(listuno[t][1]))],BS_UU_EA[int(round(listuno[t][1]))])/BS_MAX[numpy.argmax([BS_UD_EA[int(round(listuno[t][1]))],BS_UU_EA[int(round(listuno[t][1]))]])]) for t, e in enumerate(listunobleah)]
                    #print("f is", f)
                    #print("Ho sottratto sum(f)", 1 + sum(f), f)
                    beta_score_uno += sum(f)

                beta_score_uno /= 4
                alpha_score_uno /= 2
                #if uno[3] == 134:
                #    print("UNO cvl+int_angles+dist+numlinks bs:",beta_score_uno,"ah:",alpha_score_uno,"len(listuno)",len(listuno),"f",sum(f))
                ###print("UNO: NUMLINKS BS",len(listuno))

            if beta_score_uno < alpha_score_uno and beta_score_uno <= thresh_scores and numpy.abs(
                            alpha_score_uno - beta_score_uno) >= min_diff_bs:
                uno[1] = "bs"
            elif dizio3d is None and alpha_score_uno < beta_score_uno and alpha_score_uno <= thresh_scores and numpy.abs(
                            alpha_score_uno - beta_score_uno) >= min_diff_ah:
                uno[1] = "ah"
            elif dizio3d is not None and alpha_score_uno < beta_score_uno and alpha_score_uno <= thresh_scores and numpy.abs(
                            alpha_score_uno - beta_score_uno) >= min_diff_ah:
                uno[1] = "coil"
            else:
                uno[1] = "coil"

            #if uno[3] == 134:
            #    print("ANNOTATION UNO IS:",uno)

        if (dizio3d is None or due[1] in validate):
            ###print("CVL score:",__scoring_tick_fn(due[0],cvl_mean_bs,2.4,v=0.9,p=0.8,n=1),"con cvl=",due[0])
            ###print("Angle score:",__scoring_tick_fn(value1[2],angle_mean_bs,180.0,v=0.9,p=0.5,n=0.5),"con angle=",value1[2])
            beta_score_due = __scoring_tick_fn(due[0], cvl_mean_bs, 2.4, v=0.9, p=0.8, n=1) + __scoring_tick_fn(
                value1[2], angle_mean_bs, 180.0, v=0.9, p=0.5, n=0.5) #n=0.5
            alpha_score_due = __scoring_tick_fn(due[0], cvl_mean_ah, 2.4, v=0.0, p=1.0, n=1) + __scoring_tick_fn(
                value1[2], angle_mean_ah, 180.0, v=0.9, p=0.5, n=0.5)
            CA_CA_d = value1[3]
            ###print("XCa-XCa distance",CA_CA_d)
            #if due[3] == 134:
            #    print("BEFORE DUE", due[1], due[0], value1[2], due[2], "---", due[3])
            #if due[3] == 134:
            #    print("DUE cvl+int_angles bs:", beta_score_due, "ah:", alpha_score_due)
            #    print("CVL_BS",__scoring_tick_fn(due[0], cvl_mean_bs, 2.4, v=0.9, p=0.8, n=1))
            #    print("CVL_AH",__scoring_tick_fn(due[0], cvl_mean_ah, 2.4, v=0.0, p=1.0, n=1))
            #    print("ANG_BS",__scoring_tick_fn(value1[2], angle_mean_bs, 180.0, v=0.9, p=0.5, n=0.5))
            #    print("ANG_AH",__scoring_tick_fn(value1[2], angle_mean_ah, 180.0, v=0.9, p=0.5, n=0.5))

            if dizio3d is not None:
                ###print(due,"VALIDATE is",validate)
                ###print("DUE BEFORE bs:", beta_score_due, "ah:", alpha_score_due)
                if due[3] not in dizio3d or len(dizio3d[due[3]]) == 0:
                    #print("We are HEre where list is 0")
                    listdue = []
                else:
                    listdue = sorted(dizio3d[due[3]], key=lambda x: x[2])
                    ###print("How is it listdue",[(q[0],q[1]) for q in sorted(dizio3d[due[3]], key=lambda x: x[0])])
                    # NOTE: Here we do not take the absolute value of the difference because when the min distance is lower than the mean
                    #      in principle is not a bad condition and we want to add just 0 to the score
                    beta_score_due += __scoring_tick_fn(listdue[0][2], dist_mean_bs, 10.0, v=0.9, p=0.5, n=0.5) if \
                    listdue[0][2] >= dist_mean_bs else 0 #n=0.5

                if len(listdue) < min_num_bs:
                    #print("MIN is",min_num_bs,"LEN is",len(listdue),listdue,"BETASCORE was",beta_score_due)
                    beta_score_due += 5
                else:
                    #TODO: Add the external angles
                    listdue = sorted(listdue, key= lambda x: x[2], reverse=True)
                    #print(listdue)
                    # for t,e in enumerate(listdue):
                    #     y = (-1.0 * (t + 1)) / (e[2] * len(listdue))
                    #     print("Base y=",y)
                    #     m = max(BS_UD_EA[int(round(listdue[t][1]))],BS_UU_EA[int(round(listdue[t][1]))])
                    #     print("The angle is",int(round(listdue[t][1])),"in BS_UD f is",BS_UD_EA[int(round(listdue[t][1]))],"in BS_UU f is",BS_UU_EA[int(round(listdue[t][1]))],"max is",m)
                    #     f = BS_MAX[numpy.argmax([BS_UD_EA[int(round(listdue[t][1]))],BS_UU_EA[int(round(listdue[t][1]))]])]
                    #     print("MAX of the corresponding distribution ",f)
                    #     print("Value",y*(m/f))
                    f = [((-1.0 * (t + 1)) / (e[2] * len(listdue)))*2*(max(BS_UD_EA[int(round(listdue[t][1]))],BS_UU_EA[int(round(listdue[t][1]))])/BS_MAX[numpy.argmax([BS_UD_EA[int(round(listdue[t][1]))],BS_UU_EA[int(round(listdue[t][1]))]])]) for t, e in enumerate(listdue)]
                    #print("BETA SCORE WAS:",beta_score_due)
                    beta_score_due += sum(f)
                    #print("f is", f)
                    #print("Ho sottratto sum(f)", 1 + sum(f), f)
                    #print("Ho sottratto sum(f)",sum(f), f)
                ###cont_dist = [p[0] for p in sorted(listdue, key=lambda x: x[0])]
                ###num_cont_dist = sum([0 if o == 0 or cont_dist[o - 1] + 1 == u else 1 for o, u in enumerate(cont_dist)])
                ###print("Nuovo parametro continuita distanze",cont_dist,num_cont_dist)

                beta_score_due /= 4
                alpha_score_due /= 2

                #if due[3] == 134:
                #    print("DUE cvl+int_angles+dist+numlinks bs:",beta_score_uno,"ah:",alpha_score_uno,"len(listuno)",len(listdue),"f",sum(f))
                ###print("DUE: NUMLINKS BS",len(listdue))

            if beta_score_due < alpha_score_due and beta_score_due <= thresh_scores and numpy.abs(
                            alpha_score_due - beta_score_due) >= min_diff_bs:
                due[1] = "bs"
            elif dizio3d is None and alpha_score_due < beta_score_due and alpha_score_due <= thresh_scores and numpy.abs(
                            alpha_score_due - beta_score_due) >= min_diff_ah:
                due[1] = "ah"
            elif dizio3d is not None and alpha_score_due < beta_score_due and alpha_score_due <= thresh_scores and numpy.abs(
                            alpha_score_due - beta_score_due) >= min_diff_ah:
                due[1] = "coil"
            else:
                due[1] = "coil"

        # print("UNO AFTER bs:", beta_score_uno, "ah:", alpha_score_uno)
        # print(uno)
        # print()
        # #
        # print("DUE AFTER bs:", beta_score_due, "ah:", alpha_score_due)
        # print(due)
        # print()
                #if due[3] == 134:
            #    print("ANNOTATION DUE IS:",due)

        return uno, due, False

    def __get_associations(a, stringent=True):
        associations = {}
        for e in a:
            for resi in e[2]:
                if tuple(resi) not in associations:
                    associations[tuple(resi)] = {"bs": 0, "ah": 0, "coil": 0, "COIL": 0}
                associations[tuple(resi)][e[1]] += 1

        lisorted = sorted(associations.keys(), key=lambda x: x[:3]+(x[3][1:],))
        for t, key in enumerate(lisorted):
            result = ""
            # or (associations[key]["ah"] >= 2 and associations[key]["bs"] == 0) \
            # or (t>0 and t<len(associations.keys())-1 and associations[key]["ah"] == 1 and associations[key]["coil"] == 2 and associations[lisorted[t-1]]["result"] == "coil" and associations[lisorted[t+1]]["ah"] >= 2 and associations[lisorted[t+1]]["bs"] == 0):
            max_for_key = sum([associations[key][z] for z in associations[key].keys()])
            if max_for_key > 3: max_for_key = 3

            if associations[key]["ah"] == max_for_key \
                    or (max_for_key < 3 and  associations[key]["ah"] >=1 and associations[key]["bs"] == 0) or (t > 0 and t < len(associations.keys()) - 1 and associations[key]["ah"] >= 2 and
                                associations[key]["bs"] == 0 and associations[lisorted[t - 1]]["result"] == "coil" and
                                associations[lisorted[t + 1]]["ah"] >= 3):
                result = "ah"
            elif stringent and associations[key]["bs"] == max_for_key:
                result = "bs"
            elif not stringent and (associations[key]["bs"] == max_for_key
                                    or (associations[key]["bs"] == 2 and associations[key]["COIL"] == 0)
                                    or (associations[key]["bs"] == 1 and associations[key]["ah"] < 2 and associations[key]["COIL"] == 0)
                                    or (associations[key]["bs"] >= 1 and associations[key]["COIL"] == 1 and t > 0 and associations[key]["bs"] >= 1 and associations[key]["ah"] <= 1 and associations[lisorted[t - 1]]["result"] in ["coil","COIL"])
                                    or (associations[key]["bs"] >= 1 and associations[key]["COIL"] == 1 and t > 1 and associations[key]["bs"] >= 1 and associations[key]["ah"] <= 1 and associations[lisorted[t - 2]]["result"] in ["coil", "COIL"])
                                    or (associations[key]["bs"] >= 1 and associations[key]["COIL"] == 1 and t < len(associations.keys()) - 1 and associations[key]["bs"] >= 1 and associations[key]["ah"] <= 1 and associations[lisorted[t + 1]]["coil"]+associations[lisorted[t + 1]]["COIL"] > 1)
                                    or (associations[key]["bs"] >= 1 and associations[key]["COIL"] == 1 and t < len(associations.keys()) - 2 and associations[key]["bs"] >= 1 and associations[key]["ah"] <= 1 and associations[lisorted[t + 2]]["coil"]+associations[lisorted[t + 2]]["COIL"] > 1)):

                # or (t>0 and t<len(associations.keys())-1 and associations[key]["bs"] == 1 and associations[key]["coil"] == 2 and associations[lisorted[t-1]]["result"] == "coil" and associations[lisorted[t+1]]["bs"] >= 2 and associations[lisorted[t+1]]["ah"] == 0)):
                result = "bs"
            else:
                result = "coil"

            #print("STRINGENT:", stringent, "T all:", associations[key], "T:", t, "RESULT:",result,"RESI",key)  # ,"T-1 all: "+str(associations[lisorted[t - 1]]) if t>0 else "","T+1 all: "+str(associations[lisorted[t+1]]) if t<len(associations.keys()) - 1 else "")
            associations[key]["result"] = result
            #print(key, associations[key], result)
        return associations

    def __generate_graph2(a, min_ah, min_bs, associations):
        if min_ah is not None and min_ah < 3:
            min_ah = 3
        if min_bs is not None and min_bs < 3:
            min_bs = 3

        listaFrags = []
        used = set([])
        for e in a:
            #print(e)
            if len(listaFrags) == 0:
                #print("A")
                listaFrags.append([])
                #print("Was empty adding []",listaFrags)
            if e[1].lower() != "coil" and len(listaFrags[-1]) == 0:
                #print("B")
                #print("e[1]=",e[1],"that is not coil and ",len(listaFrags[-1]),"is empty")
                listaFrags[-1].append(e)
                for r in e[2]:
                    used.add(tuple(r))
            elif any(map(lambda x: x[1].lower() == e[1].lower() and x[2][0][2] == e[2][0][2] and len(
                    (set([tuple(p) for p in x[2]]) & set([tuple(p) for p in e[2]]))) > 0, listaFrags[-1])):
                #print("C")
                #print("e[1]=",e[1],"but could be automatically attachable to ",listaFrags[-1])
                listaFrags[-1].append(e)
                for r in e[2]:
                    used.add(tuple(r))
            elif any(map(lambda x: e[1].lower() != "coil" and x[1] in ["ah", "bs"] and x[1] != e[1] and x[2][0][2] == e[2][0][
                2] and len((set([tuple(p) for p in x[2]]) & set([tuple(p) for p in e[2]]))) > 0, listaFrags[-1])):
                #print("We need to change", e[1], "into coil because previous was a different sstype and it is continous")
                #print("e[1]=",e[1],"that is not coil and we need to open a new list")
                e[1] = "coil"
                listaFrags.append([e])
                for r in e[2]:
                    used.add(tuple(r))
            elif e[1].lower() != "coil":  # and all(map(lambda x: tuple(x) not in used, e[2])):
                #print("D")
                #print("e[1]=",e[1],"that is not coil and we need to open a new list")
                listaFrags.append([e])
                for r in e[2]:
                    used.add(tuple(r))
            elif e[1].lower() == "coil":
                 #print (e[2],"this is coil")
                 listaFrags.append([e])
                 for r in e[2]:
                     used.add(tuple(r))
            else:
                #print ("E")
                #print ("e[1]=", e[1], "creating an empty list")
                listaFrags.append([e])

        # print("===============================LISTAFRAGS===============================")
        # for fra in listaFrags:
        #     print(fra)
        # print("=========================================================================")

        listaFrags = [
            {"sstype": fragl[0][1].lower(), "reslist": fragl[0][2][:] + list(map(lambda x: x[2][-1], fragl[1:])),
             "cvids": list(map(lambda x: x[3], fragl)), "cvls": list(map(lambda x: x[0], fragl)), "sequence": "".join(
                list(map(lambda x: Bioinformatics3.AADICMAP[x[4]],
                         fragl[0][2][:] + list(map(lambda x: x[2][-1], fragl[1:])))))} for
            fragl in listaFrags if len(fragl) > 0 and fragl[0][1] in ["ah", "bs", "coil","COIL"]]

        #
        # for frag in listaFrags:
        #         print (frag["sstype"])

        seen = set([])
        for o, frag in enumerate(listaFrags):
            newcorrect = []
            newseq = ""
            resforgraph = []
            seqforgraph = ""
            for resi in frag["reslist"]:
                #print (resi, associations[tuple(resi)]["result"], "==", frag["sstype"])
                if associations[tuple(resi)]["result"] == frag["sstype"] and tuple(resi) not in seen:
                    if o > 0 and len(listaFrags[o - 1]["reslist"]) > 0:
                        # print (listaFrags[o-1])
                        resaN = Bioinformatics3.get_residue(strucc, resi[1], resi[2], resi[3])
                        prev = listaFrags[o - 1]["reslist"][-1]
                        prevResC = Bioinformatics3.get_residue(strucc, prev[1], prev[2], prev[3])
                        if Bioinformatics3.check_continuity(resaN, prevResC) and listaFrags[o - 1]["sstype"] in ["ah", "bs"]:
                            resforgraph.append((0, "-", "-", ('', '-', '')))
                            seqforgraph += "-"
                        else:
                            newcorrect.append(resi)
                            newseq += Bioinformatics3.AADICMAP[resi[4]]
                            resforgraph.append(resi)
                            seqforgraph += Bioinformatics3.AADICMAP[resi[4]]
                            if tuple(resi) not in seen:
                                seen.add(tuple(resi))
                    else:
                        newcorrect.append(resi)
                        newseq += Bioinformatics3.AADICMAP[resi[4]]
                        resforgraph.append(resi)
                        seqforgraph += Bioinformatics3.AADICMAP[resi[4]]
                        if tuple(resi) not in seen:
                            seen.add(tuple(resi))
                else:
                    resforgraph.append((0, "-", "-", ('', '-', '')))
                    seqforgraph += "-"
            frag["reslist"] = newcorrect
            frag["sequence"] = newseq
            frag["resforgraph"] = resforgraph
            frag["seqforgraph"] = seqforgraph

            if len(frag["reslist"]) == 0:
                frag["sstype"] = "coil"

        if min_ah is not None and min_bs is not None:
            listaFrags = [fr for i, fr in enumerate(listaFrags) if
                          (fr["sstype"] == "coil" and len(fr["reslist"]) > 0) or
                          (fr["sstype"] == "ah" and len(fr["reslist"]) >= min_ah) or (
                              fr["sstype"] == "bs" and len(fr["reslist"]) >= min_bs)]


            add_coil = []
            listaFrags = sorted(listaFrags,key=lambda x: x["reslist"][-1])
            for o, frag in enumerate(listaFrags):
                if o > 0 and len(listaFrags[o - 1]["reslist"]) > 0 and len(listaFrags[o]["reslist"]) > 0 and \
                                listaFrags[o - 1]["sstype"] in ["ah", "bs"] and listaFrags[o]["sstype"] in ["ah", "bs"]:
                    resaN = Bioinformatics3.get_residue(strucc, frag["reslist"][0][1], frag["reslist"][0][2], frag["reslist"][0][3])
                    prev = listaFrags[o - 1]["reslist"][-1]
                    prevResC = Bioinformatics3.get_residue(strucc, prev[1], prev[2], prev[3])
                    #print(o, prev, frag["reslist"][0], Bioinformatics.check_continuity(resaN, prevResC))
                    #geome = compute_instruction(get_unique_cv_among_residues(strucc, listaFrags[o - 1]["reslist"]), get_unique_cv_among_residues(strucc, listaFrags[o]["reslist"]), unique_fragment_cv=True)

                    if Bioinformatics3.check_continuity(resaN, prevResC):
                        #print([resi[4] for resi in listaFrags[o - 1]["reslist"][-3:]])
                        #print([resi[4] for resi in listaFrags[o]["reslist"][:3]])
                        try:
                            id1_gly = [resi[4] for resi in listaFrags[o - 1]["reslist"][-3:]].index("GLY")
                        except:
                            id1_gly = -1
                        try:
                            id1_pro = [resi[4] for resi in listaFrags[o - 1]["reslist"][-3:]].index("PRO")
                        except:
                            id1_pro = -1
                        try:
                            id2_gly = [resi[4] for resi in listaFrags[o]["reslist"][:3]].index("GLY")
                        except:
                            id2_gly = -1
                        try:
                            id2_pro = [resi[4] for resi in listaFrags[o]["reslist"][:3]].index("PRO")
                        except:
                            id2_pro = -1
                        #print(id1_gly,id1_pro,id2_gly,id2_pro)

                        A = False
                        B = False
                        if id1_gly >= 0:
                            dirco = {"sstype": "coil", "reslist": [listaFrags[o - 1]["reslist"][-3+id1_gly]], "cvids": [listaFrags[o - 1]["cvids"][-1]] ,
                                     "cvls": [listaFrags[o - 1]["cvls"][-1]], "sequence": "".join(list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], [listaFrags[o - 1]["reslist"][-3 + id1_gly]])))}

                            add_coil.append(dirco)

                            if id1_gly < 2:
                                listaFrags[o]["reslist"] = listaFrags[o - 1]["reslist"][-3+id1_gly+1:] + listaFrags[o]["reslist"]
                                listaFrags[o]["sequence"] =  "".join(list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o]["reslist"])))
                                #listaFrags[o]["cvids"] = [listaFrags[o - 1]["cvids"][-1]] + listaFrags[o]["cvids"]
                                #listaFrags[o]["cvls"] = [listaFrags[o - 1]["cvls"][-1]] + listaFrags[o]["cvls"]
                            listaFrags[o - 1]["reslist"] = listaFrags[o - 1]["reslist"][:-3+id1_gly]
                            listaFrags[o - 1]["sequence"] = "".join(list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o - 1]["reslist"])))
                            #listaFrags[o - 1]["cvids"] =  listaFrags[o - 1]["cvids"][:-1]
                            #listaFrags[o - 1]["cvls"] = listaFrags[o - 1]["cvls"][:-1]

                            A = True
                            #print("A",listaFrags[o - 1]["reslist"])
                            #print("A",listaFrags[o]["reslist"])
                        elif id1_pro >= 0:
                            dirco = {"sstype": "coil", "reslist": [listaFrags[o - 1]["reslist"][-3 + id1_pro]],
                                     "cvids": [listaFrags[o - 1]["cvids"][-1]],
                                     "cvls": [listaFrags[o - 1]["cvls"][-1]], "sequence": "".join(list(
                                    map(lambda x: Bioinformatics3.AADICMAP[x[4]],
                                        [listaFrags[o - 1]["reslist"][-3 + id1_pro]])))}

                            add_coil.append(dirco)

                            if id1_pro < 2:
                                listaFrags[o]["reslist"] = listaFrags[o - 1]["reslist"][-3+id1_pro+1:] + listaFrags[o]["reslist"]
                                listaFrags[o]["sequence"] =  "".join(list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o]["reslist"])))
                            listaFrags[o - 1]["reslist"] = listaFrags[o - 1]["reslist"][:-3+id1_pro]
                            listaFrags[o - 1]["sequence"] = "".join(
                                list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o - 1]["reslist"])))

                            A = True
                            #print("B", listaFrags[o - 1]["reslist"])
                            #print("B", listaFrags[o]["reslist"])
                        elif id2_gly >= 0:
                            dirco = {"sstype": "coil", "reslist": [listaFrags[o]["reslist"][id2_gly]],
                                     "cvids": [listaFrags[o]["cvids"][-1]],
                                     "cvls": [listaFrags[o]["cvls"][-1]], "sequence": "".join(list(
                                    map(lambda x: Bioinformatics3.AADICMAP[x[4]],
                                        [listaFrags[o]["reslist"][id2_gly]])))}

                            add_coil.append(dirco)
                            listaFrags[o - 1]["reslist"] = listaFrags[o - 1]["reslist"] + listaFrags[o]["reslist"][:id2_gly]
                            listaFrags[o - 1]["sequence"] = "".join(
                                list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o - 1]["reslist"])))

                            if len(listaFrags[o]["reslist"]) > 3:
                                listaFrags[o]["reslist"] = listaFrags[o]["reslist"][id2_gly+1:]
                                listaFrags[o]["sequence"] =  "".join(list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o]["reslist"])))

                            B = True
                            #print("C", listaFrags[o - 1]["reslist"])
                            #print("C", listaFrags[o]["reslist"])
                        elif id2_pro >= 0:
                            dirco = {"sstype": "coil", "reslist": [listaFrags[o]["reslist"][id2_pro]],
                                     "cvids": [listaFrags[o]["cvids"][-1]],
                                     "cvls": [listaFrags[o]["cvls"][-1]], "sequence": "".join(list(
                                    map(lambda x: Bioinformatics3.AADICMAP[x[4]],
                                        [listaFrags[o]["reslist"][id2_pro]])))}

                            add_coil.append(dirco)
                            listaFrags[o - 1]["reslist"] = listaFrags[o - 1]["reslist"] + listaFrags[o]["reslist"][:id2_pro]
                            listaFrags[o - 1]["sequence"] = "".join(
                                list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o - 1]["reslist"])))

                            if len(listaFrags[o]["reslist"]) > 3:
                                listaFrags[o]["reslist"] = listaFrags[o]["reslist"][id2_pro + 1:]
                                listaFrags[o]["sequence"] =  "".join(list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o]["reslist"])))

                            B = True
                            #print("D", listaFrags[o - 1]["reslist"])
                            #print("D", listaFrags[o]["reslist"])
                        else:
                            dirco = {"sstype": "coil", "reslist": [listaFrags[o - 1]["reslist"][-1]],
                                     "cvids": [listaFrags[o - 1]["cvids"][-1]],
                                     "cvls": [listaFrags[o - 1]["cvls"][-1]], "sequence": "".join(list(
                                    map(lambda x: Bioinformatics3.AADICMAP[x[4]],
                                        [listaFrags[o - 1]["reslist"][-1]])))}

                            add_coil.append(dirco)
                            listaFrags[o - 1]["reslist"] = listaFrags[o - 1]["reslist"][:-1]
                            listaFrags[o - 1]["sequence"] = "".join(
                                list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o - 1]["reslist"])))

                            A = True
                            #print("E", listaFrags[o - 1]["reslist"])
                            #print("E", listaFrags[o]["reslist"])

                        #print(add_coil)
                        #quit()

                        if A and len(listaFrags[o-1]["reslist"]) < 3:
                            listaFrags[o - 1]["sstype"] = "coil"
                        elif B and len(listaFrags[o]["reslist"]) < 3:
                            listaFrags[o]["sstype"] = "coil"

            listaFrags = [fr for fr in listaFrags if len(fr["reslist"])>0]
            listaFrags = sorted(listaFrags,key=lambda x: x["reslist"][-1])

        g = igraph.Graph.Full(len(listaFrags))

        for i, fr in enumerate(listaFrags):
            g.vs[i]["sstype"] = fr["sstype"]
            g.vs[i]["reslist"] = fr["reslist"]
            g.vs[i]["unique_cv"] = get_unique_cv_among_residues(strucc, fr["reslist"])
            try:
                g.vs[i]["vecLength"] = get_atoms_distance(g.vs[i]["unique_cv"][2],g.vs[i]["unique_cv"][3])
            except:
                g.vs[i]["vecLength"] = -1
            g.vs[i]["cvids"] = fr["cvids"]
            g.vs[i]["resforgraph"] = fr["resforgraph"]
            g.vs[i]["seqforgraph"] = fr["seqforgraph"]
            # indfri = int(len(fr["cvids"]) / 2)
            # indfr = fr["cvids"][indfri]
            # cvst = list(filter(lambda x: x[0] == indfr, cvs_list))[0]
            # g.vs[i]["com"] = [(cvst[2][0] + cvst[3][0]) / 2.0, (cvst[2][1] + cvst[3][1]) / 2.0,
            #                   (cvst[2][2] + cvst[3][2]) / 2.0]
            g.vs[i]["cvls"] = fr["cvls"]
            g.vs[i]["sequence"] = fr["sequence"]
        return g, a

    def __generate_graph(a, min_ah, min_bs, associations):
        if min_ah is not None and min_ah < 3:
            min_ah = 3
        if min_bs is not None and min_bs < 3:
            min_bs = 3

        listaFrags = []
        for asso in sorted(associations.keys(), key=lambda x: x[:3]+(x[3][1:],)):
            if len(listaFrags) == 0:
                listaFrags.append([])
            if len(listaFrags[-1]) == 0:
                listaFrags[-1].append(asso)
            elif len(listaFrags[-1]) > 0 and associations[listaFrags[-1][-1]]["result"].lower() == associations[asso]["result"].lower():
                resi = asso
                prev = listaFrags[-1][-1]
                resaN = Bioinformatics3.get_residue(strucc, resi[1], resi[2], resi[3])
                prevResC = Bioinformatics3.get_residue(strucc, prev[1], prev[2], prev[3])
                if Bioinformatics3.check_continuity(resaN, prevResC):
                    listaFrags[-1].append(asso)
                else:
                    listaFrags.append([asso])
            else:
                listaFrags.append([asso])

        listaFrags = [
            {"sstype": associations[fragl[0]]["result"].lower(),
             "reslist": [list(fr) for fr in fragl],
             "cvids": sorted(set([e[3] for fr in fragl for e in a if list(fr) in e[2]])),
             "sequence": "".join(list(map(lambda x: Bioinformatics3.AADICMAP[x[4]],fragl)))}
            for fragl in listaFrags if len(fragl) > 0 and associations[fragl[0]]["result"].lower() in ["ah", "bs", "coil", "COIL"]]

        for o,frag in enumerate(listaFrags):
            if o > 0 and len(listaFrags[o - 1]["reslist"]) > 0 and len(set(listaFrags[o - 1]["cvids"])&set(frag["cvids"])) > 0:
                listaFrags[o - 1]["cvids"] = sorted(list(set(listaFrags[o - 1]["cvids"])-set(frag["cvids"])))
                listaFrags[o - 1]["cvls"] = [e[0] for e in a if e[3] in listaFrags[o - 1]["cvids"]]
            listaFrags[o]["cvls"] = [e[0] for e in a if e[3] in listaFrags[o]["cvids"]]

        if min_ah is not None and min_bs is not None:
            # print('SHERLOOOOOOOOCK I should b entering here')
            # print('min_ah,min_bs',min_ah,min_bs)

            listaFrags = [fr for i, fr in enumerate(listaFrags) if
                          (fr["sstype"] == "coil" and len(fr["reslist"]) > 0) or
                          (fr["sstype"] == "ah" and len(fr["reslist"]) >= min_ah) or (
                                  fr["sstype"] == "bs" and len(fr["reslist"]) >= min_bs)]
            # for frag in listaFrags:
            #     if frag['sstype']!='coil':
            #         print("frag['sstype']",frag['sstype'],"len(frag['reslist']",len(frag['reslist']))
            # sys.exit(0)

        add_coil = []
        listaFrags = sorted(listaFrags, key=lambda x: x["reslist"][-1])
        for o, frag in enumerate(listaFrags):
            if o > 0 and len(listaFrags[o - 1]["reslist"]) > 2 and len(listaFrags[o]["reslist"]) > 2 and \
                    listaFrags[o - 1]["sstype"] in ["ah", "bs"] and listaFrags[o]["sstype"] in ["ah", "bs"]:
                resaN = Bioinformatics3.get_residue(strucc, frag["reslist"][0][1], frag["reslist"][0][2], frag["reslist"][0][3])
                prev = listaFrags[o - 1]["reslist"][-1]
                prevResC = Bioinformatics3.get_residue(strucc, prev[1], prev[2], prev[3])

                if Bioinformatics3.check_continuity(resaN, prevResC):
                    # print([resi[4] for resi in listaFrags[o - 1]["reslist"][-3:]])
                    # print([resi[4] for resi in listaFrags[o]["reslist"][:3]])
                    try:
                        id1_gly = [resi[4] for resi in listaFrags[o - 1]["reslist"][-3:]].index("GLY")
                    except:
                        id1_gly = -1
                    try:
                        id1_pro = [resi[4] for resi in listaFrags[o - 1]["reslist"][-3:]].index("PRO")
                    except:
                        id1_pro = -1
                    try:
                        id2_gly = [resi[4] for resi in listaFrags[o]["reslist"][:3]].index("GLY")
                    except:
                        id2_gly = -1
                    try:
                        id2_pro = [resi[4] for resi in listaFrags[o]["reslist"][:3]].index("PRO")
                    except:
                        id2_pro = -1
                    # print(id1_gly,id1_pro,id2_gly,id2_pro)

                    A = False
                    B = False
                    if id1_gly >= 0:
                        dirco = {"sstype": "coil", "reslist": [listaFrags[o - 1]["reslist"][-3 + id1_gly]],
                                 "cvids": [listaFrags[o - 1]["cvids"][-1]],
                                 "cvls": [listaFrags[o - 1]["cvls"][-1]], "sequence": "".join(list(
                                map(lambda x: Bioinformatics3.AADICMAP[x[4]],
                                    [listaFrags[o - 1]["reslist"][-3 + id1_gly]])))}

                        add_coil.append(dirco)

                        if id1_gly < 2:
                            listaFrags[o]["reslist"] = listaFrags[o - 1]["reslist"][-3 + id1_gly + 1:] + \
                                                       listaFrags[o]["reslist"]
                            listaFrags[o]["sequence"] = "".join(
                                list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o]["reslist"])))
                            # listaFrags[o]["cvids"] = [listaFrags[o - 1]["cvids"][-1]] + listaFrags[o]["cvids"]
                            # listaFrags[o]["cvls"] = [listaFrags[o - 1]["cvls"][-1]] + listaFrags[o]["cvls"]
                        listaFrags[o - 1]["reslist"] = listaFrags[o - 1]["reslist"][:-3 + id1_gly]
                        listaFrags[o - 1]["sequence"] = "".join(
                            list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o - 1]["reslist"])))
                        # listaFrags[o - 1]["cvids"] =  listaFrags[o - 1]["cvids"][:-1]
                        # listaFrags[o - 1]["cvls"] = listaFrags[o - 1]["cvls"][:-1]

                        A = True
                        # print("A",listaFrags[o - 1]["reslist"])
                        # print("A",listaFrags[o]["reslist"])
                    elif id1_pro >= 0:
                        dirco = {"sstype": "coil", "reslist": [listaFrags[o - 1]["reslist"][-3 + id1_pro]],
                                 "cvids": [listaFrags[o - 1]["cvids"][-1]],
                                 "cvls": [listaFrags[o - 1]["cvls"][-1]], "sequence": "".join(list(
                                map(lambda x: Bioinformatics3.AADICMAP[x[4]],
                                    [listaFrags[o - 1]["reslist"][-3 + id1_pro]])))}

                        add_coil.append(dirco)

                        if id1_pro < 2:
                            listaFrags[o]["reslist"] = listaFrags[o - 1]["reslist"][-3 + id1_pro + 1:] + \
                                                       listaFrags[o]["reslist"]
                            listaFrags[o]["sequence"] = "".join(
                                list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o]["reslist"])))
                        listaFrags[o - 1]["reslist"] = listaFrags[o - 1]["reslist"][:-3 + id1_pro]
                        listaFrags[o - 1]["sequence"] = "".join(
                            list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o - 1]["reslist"])))

                        A = True
                        # print("B", listaFrags[o - 1]["reslist"])
                        # print("B", listaFrags[o]["reslist"])
                    elif id2_gly >= 0:
                        dirco = {"sstype": "coil", "reslist": [listaFrags[o]["reslist"][id2_gly]],
                                 "cvids": [listaFrags[o]["cvids"][-1]],
                                 "cvls": [listaFrags[o]["cvls"][-1]], "sequence": "".join(list(
                                map(lambda x: Bioinformatics3.AADICMAP[x[4]],
                                    [listaFrags[o]["reslist"][id2_gly]])))}

                        add_coil.append(dirco)
                        listaFrags[o - 1]["reslist"] = listaFrags[o - 1]["reslist"] + listaFrags[o]["reslist"][
                                                                                      :id2_gly]
                        listaFrags[o - 1]["sequence"] = "".join(
                            list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o - 1]["reslist"])))

                        if len(listaFrags[o]["reslist"]) > 3:
                            listaFrags[o]["reslist"] = listaFrags[o]["reslist"][id2_gly + 1:]
                            listaFrags[o]["sequence"] = "".join(
                                list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o]["reslist"])))

                        B = True
                        # print("C", listaFrags[o - 1]["reslist"])
                        # print("C", listaFrags[o]["reslist"])
                    elif id2_pro >= 0:
                        dirco = {"sstype": "coil", "reslist": [listaFrags[o]["reslist"][id2_pro]],
                                 "cvids": [listaFrags[o]["cvids"][-1]],
                                 "cvls": [listaFrags[o]["cvls"][-1]], "sequence": "".join(list(
                                map(lambda x: Bioinformatics3.AADICMAP[x[4]],
                                    [listaFrags[o]["reslist"][id2_pro]])))}

                        add_coil.append(dirco)
                        listaFrags[o - 1]["reslist"] = listaFrags[o - 1]["reslist"] + listaFrags[o]["reslist"][
                                                                                      :id2_pro]
                        listaFrags[o - 1]["sequence"] = "".join(
                            list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o - 1]["reslist"])))

                        if len(listaFrags[o]["reslist"]) > 3:
                            listaFrags[o]["reslist"] = listaFrags[o]["reslist"][id2_pro + 1:]
                            listaFrags[o]["sequence"] = "".join(
                                list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o]["reslist"])))

                        B = True
                        # print("D", listaFrags[o - 1]["reslist"])
                        # print("D", listaFrags[o]["reslist"])
                    else:
                        dirco = {"sstype": "coil", "reslist": [listaFrags[o - 1]["reslist"][-1]],
                                 "cvids": [listaFrags[o - 1]["cvids"][-1]],
                                 "cvls": [listaFrags[o - 1]["cvls"][-1]], "sequence": "".join(list(
                                map(lambda x: Bioinformatics3.AADICMAP[x[4]],
                                    [listaFrags[o - 1]["reslist"][-1]])))}

                        add_coil.append(dirco)
                        listaFrags[o - 1]["reslist"] = listaFrags[o - 1]["reslist"][:-1]
                        listaFrags[o - 1]["sequence"] = "".join(
                            list(map(lambda x: Bioinformatics3.AADICMAP[x[4]], listaFrags[o - 1]["reslist"])))

                        A = True
                        # print("E", listaFrags[o - 1]["reslist"])
                        # print("E", listaFrags[o]["reslist"])

                    # print(add_coil)
                    # quit()

                    if A and len(listaFrags[o - 1]["reslist"]) < 3:
                        listaFrags[o - 1]["sstype"] = "coil"
                    elif B and len(listaFrags[o]["reslist"]) < 3:
                        listaFrags[o]["sstype"] = "coil"

        listaFrags = [fr for fr in listaFrags if len(fr["reslist"]) > 0]
        listaFrags = sorted(listaFrags, key=lambda x: x["reslist"][-1])

        g = igraph.Graph.Full(len(listaFrags))

        for i, fr in enumerate(listaFrags):
            g.vs[i]["sstype"] = fr["sstype"]
            g.vs[i]["reslist"] = fr["reslist"]
            g.vs[i]["unique_cv"] = get_unique_cv_among_residues(strucc, fr["reslist"])
            try:
                g.vs[i]["vecLength"] = get_atoms_distance(g.vs[i]["unique_cv"][2], g.vs[i]["unique_cv"][3])
            except:
                g.vs[i]["vecLength"] = -1
            g.vs[i]["cvids"] = fr["cvids"]
            #g.vs[i]["resforgraph"] = fr["reslist"]
            #g.vs[i]["seqforgraph"] = fr["sequence"]
            # indfri = int(len(fr["cvids"]) / 2)
            # indfr = fr["cvids"][indfri]
            # cvst = list(filter(lambda x: x[0] == indfr, cvs_list))[0]
            # g.vs[i]["com"] = [(cvst[2][0] + cvst[3][0]) / 2.0, (cvst[2][1] + cvst[3][1]) / 2.0,
            #                   (cvst[2][2] + cvst[3][2]) / 2.0]
            g.vs[i]["cvls"] = fr["cvls"]
            g.vs[i]["sequence"] = fr["sequence"]

        # print("===============================LISTAFRAGS===============================")
        # for fra in listaFrags:
        #      print(fra["sstype"],fra['sequence'])
        # print("=========================================================================")
        return g, a

    def __generate_3d_relations(g, max_distance=10.0, validate=["bs", "coil"]):
        dictio3d = {}
        for i, frag1 in enumerate(g.vs):
            if frag1["sstype"] not in validate:
                continue
            for frag2 in g.vs.select(lambda vertex: vertex.index != frag1.index):
                if frag2["sstype"] not in validate:
                    continue
                for uno in frag1["cvids"]:
                    if uno not in dictio3d:
                        dictio3d[uno] = []
                    for due in frag2["cvids"]:
                        if due == uno:
                            continue
                        # print "||", uno, "--", due,"||",
                        ###value1 = compute_instruction(cvs_list[dimap[uno]], cvs_list[dimap[due]])
                        sup = tuple(sorted([dimap[uno], dimap[due]]))
                        value1 = matrix[sup]
                        if value1[3] <= max_distance:
                            dictio3d[uno].append([due, value1[2], value1[3], value1[4]])
        return dictio3d

    def __check_impossible_angle(z,p,a,enne,zenne,cvs_list,dimap,matrix,angle_mean_bs,angle_mean_ah,strucc):
        # print("========CHECKING=========")
        # if p - 3 >= 0:
        #     print(enne)
        #     print(cvs_list[dimap[z[p - 3][3]]])
        #     print(abs(matrix[tuple(sorted([dimap[enne[3]], dimap[z[p - 3][3]]]))][2] - angle_mean_bs))
        # print()
        # if p - 2 >= 0:
        #     print(zenne)
        #     print(cvs_list[dimap[z[p - 2][3]]])
        #     print(abs(matrix[tuple(sorted([dimap[zenne[3]], dimap[z[p - 2][3]]]))][2] - angle_mean_bs))
        # print("==========================")
        # Checking if the current enne is annotated as ah or bs and if it exists a previous cv at p-3 with the same annotation
        if enne[1] in ["ah", "bs"] and p - 3 >= 0 and z[p - 3][1] == enne[1]:
            # checking if the two CV are representing two tripetides continous but not overlapping
            resaN = Bioinformatics3.get_residue(strucc, enne[2][0][1], enne[2][0][2], enne[2][0][3])
            prevResC = Bioinformatics3.get_residue(strucc, z[p - 3][2][-1][1], z[p - 3][2][-1][2], z[p - 3][2][-1][3])
            if Bioinformatics3.check_continuity(resaN, prevResC):
                # checking if their angle is not too far away from the standard mean of the annotation
                if (enne[1] == "bs" and abs(
                        matrix[tuple(sorted([dimap[enne[3]], dimap[z[p - 3][3]]]))][2] - angle_mean_bs) > 50) \
                        or (enne[1] == "ah" and abs(
                    matrix[tuple(sorted([dimap[enne[3]], dimap[z[p - 3][3]]]))][2] - angle_mean_ah) > 50):
                    # print("We found a case where enne is")
                    # print(enne)
                    # print("And z[p-3] is")
                    # print(z[p-3])
                    # print("the angle between them is",matrix[tuple(sorted([dimap[enne[3]], dimap[z[p-3][3]]]))][2])
                    # enne[1] = "COIL"
                    if z[p - 3][1] not in ["coil", "COIL"]:
                        z[p - 2][1] = "COIL"
                    else:
                        z[p - 3][1] = "COIL"
        # Checking if the current zenne is annotated as ah or bs and if it exists a previous cv at p-2 with the same annotation
        if zenne[1] in ["ah", "bs"] and p - 2 >= 0 and z[p - 2][1] == zenne[1]:
            # checking if the two CV are representing two tripetides continous but not overlapping
            resaN = Bioinformatics3.get_residue(strucc, zenne[2][0][1], zenne[2][0][2], zenne[2][0][3])
            prevResC = Bioinformatics3.get_residue(strucc, z[p - 2][2][-1][1], z[p - 2][2][-1][2], z[p - 2][2][-1][3])
            if Bioinformatics3.check_continuity(resaN, prevResC):
                # checking if their angle is not too far away from the standard mean of the annotation
                if (zenne[1] == "bs" and abs(
                        matrix[tuple(sorted([dimap[zenne[3]], dimap[z[p - 2][3]]]))][2] - angle_mean_bs) > 50) \
                        or (zenne[1] == "ah" and abs(
                    matrix[tuple(sorted([dimap[zenne[3]], dimap[z[p - 2][3]]]))][2] - angle_mean_ah) > 50):
                    # print("We found a case where zenne is")
                    # print(zenne)
                    # print("And z[p-2] is")
                    # print(z[p - 2])
                    # print("the angle between them is", matrix[tuple(sorted([dimap[zenne[3]], dimap[z[p - 2][3]]]))][2])
                    # zenne[1] = "COIL"
                    if z[p - 2][1] not in ["coil", "COIL"]:
                        z[p - 1][1] = "COIL"
                    else:
                        z[p - 2][1] = "COIL"
        z[p] = enne
        z[p + 1] = zenne
        return z

    z = [0 for y in range(len(a))]
    tf = True
    for p in range(len(a) - 1):
        enne, zenne, tf = __check_by_unified_score_step2(a[p], a[p + 1], None, take_first=tf)
        z = __check_impossible_angle(z, p, a, enne, zenne, cvs_list, dimap, matrix, angle_mean_bs, angle_mean_ah, strucc)
    a = z

    # for e in a:
    #     print (e)
    # print()

    text = ""
    for w in range(2):
        associations = __get_associations(a, stringent=True if w == 0 else False)
        # associations = __getAssociations(a)
        g, a = __generate_graph(a, None if w == 0 else min_ah, None if w == 0 else min_bs, associations)

        # for frag in g.vs:
        #      if len(frag["reslist"]) > 0:
        #          print(frag["reslist"][0][3][1], "--", frag["reslist"][-1][3][1], frag["sstype"], "---", frag["unique_cv"])

        dictio_3D = __generate_3d_relations(g, validate=["bs", "coil"] if w == 0 else ["bs"])

        a = [e[:-1] if len(e) == 5 else e for e in a]

        z = [0 for y in range(len(a))]
        tf = True
        for p in range(len(a) - 1):
            enne, zenne, tf = __check_by_unified_score_step2(a[p], a[p + 1], dictio_3D, take_first=tf,
                                                             validate=["bs", "coil"] if w == 0 else ["bs"],
                                                             min_num_bs=1.0 if w == 0 else 1.0)

            z = __check_impossible_angle(z, p, a, enne, zenne, cvs_list, dimap, matrix, angle_mean_bs, angle_mean_ah, strucc)

        a = z

        # for e in a:
        #     print(e)
        # print()
        # print()

        if w == 1:
            associations = __get_associations(a, stringent=True if w == 0 else False)
            # associations = __getAssociations(a)
            g, a = __generate_graph(a, min_ah, min_bs, associations)

        for e in a:
            text += str(e)+"\n"
        text += "\n"
    # for frag in listaFrags:
    #     print([[(w[2],w[3][1]) for w in fr[2]] for fr in frag],len([fr[2] for fr in frag]),[fr[3] for fr in frag],len([fr[3] for fr in frag]))
    #     print([[(w[2],w[3][1]) for w in fr[2]] for fr in frag[:1]]+[[(w[2],w[3][1]) for w in fr[2][-1:]] for fr in frag[1:]],len([[(w[2],w[3][1]) for w in fr[2]] for fr in frag[:1]]+[[(w[2],w[3][1]) for w in fr[2][-2:-1]] for fr in frag[1:]]),[fr[3] for fr in frag],len([fr[3] for fr in frag]))
    #     print(frag)
    #     print()

    with open("fromCVtoAA_12.txt","w") as f:
        f.write(text)

    return g

@SystemUtility.timing
# @SystemUtility.profileit
def aleph_internal_terstr(strucc, g, matrix, cvs):
    """
    
    :param strucc: 
    :type strucc: 
    :param g: 
    :type g: 
    :param cvs: 
    :type cvs: 
    :return: 
    :rtype: 
    """
    dimap = {value[0]: i for (i, value) in enumerate(cvs)}

    for i, frag1 in enumerate(g.vs):
        if len(frag1["cvids"]) > 0:
            alls = numpy.empty((len(frag1["cvids"]) - 1, 3))
            for u in range(len(frag1["cvids"]) - 1):
                a = frag1["cvids"][u]
                b = frag1["cvids"][u + 1]
                ###value1 = compute_instruction(cvs[dimap[a]], cvs[dimap[b]])
                sup = tuple(sorted([dimap[a], dimap[b]]))
                value1 = matrix[sup]
                alls[u] = numpy.array([value1[2], value1[3], value1[4]])
            frag1["alls"] = alls
    return g


@SystemUtility.timing
# @SystemUtility.profileit
def aleph_terstr(strucc, g, matrix, cvs, weight="distance_avg"):
    """
    
    :param strucc: 
    :type strucc: 
    :param g: 
    :type g: 
    :param cvs: 
    :type cvs: 
    :param weight: 
    :type weight: 
    :param full: 
    :type full: 
    :param sheet_factor: 
    :type sheet_factor: 
    :return: 
    :rtype: 
    """

    # print "LEN_CVS:",len(cvs)
    dimap = {value[0]: i for (i, value) in enumerate(cvs)}
    sstype_map = {"ah": 1, "bs": 2, "coil": 3}

    convert = {}
    for i, frag1 in enumerate(g.vs):
        framme1 = []
        for frag2 in g.vs.select(lambda vertex: vertex.index > frag1.index):
            # g.add_edge(frag1.index, frag2.index)
            t = 0.0
            z = [1.0, 1.0, 1.0]
            minimum = 10000000000000.0
            alls = []
            minforcvids = []
            #maximum_number_of_mins = len(frag1["cvids"]) #min(len(frag1["cvids"]),len(frag2["cvids"]))
            fgs = sorted([frag1,frag2],key=lambda x: len(x["cvids"]))
            for a in fgs[0]["cvids"]:
                minoide = [[0.0,100.0,0]]
                for b in fgs[1]["cvids"]:
                    # print "test tertiary frags:",i,"====","a,b,c",a,b,c,"d,e,f",d,e,f
                    ###value1 = compute_instruction(cvs[dimap[a]], cvs[dimap[b]])
                    sup = tuple(sorted([dimap[a], dimap[b]]))
                    value1 = matrix[sup]
                    z = [z[0] + value1[2], z[1] + value1[3], z[2] + value1[4]]
                    minimum = min(minimum, value1[3])
                    alls.append([a, b, value1[2], value1[3], value1[4]])
                    minoide.append([value1[2], value1[3], value1[4]])
                    t += 1
                minforcvids.append(sorted(minoide, key=lambda x: x[1])[0])

            if t==0: t=1
            z = [z[0] / t, z[1] / t, z[2] / t, sstype_map[frag1["sstype"]], sstype_map[frag2["sstype"]]]
            #print(frag1)
            #print(frag2)
            g.es[g.get_eid(frag1.index, frag2.index)]["mean"] = z
            if frag1["sstype"] in ["ah","bs"] and frag2["sstype"] in ["ah","bs"]:
                g.es[g.get_eid(frag1.index, frag2.index)]["mean_cv_uniques"] = compute_instruction(g.vs[frag1.index]["unique_cv"],g.vs[frag2.index]["unique_cv"],unique_fragment_cv=True)[2:6]+z[-2:]
            g.es[g.get_eid(frag1.index, frag2.index)]["avg"] = z[1]
            g.es[g.get_eid(frag1.index, frag2.index)]["min"] = minimum
            g.es[g.get_eid(frag1.index, frag2.index)]["alls"] = alls

            if weight == "distance_avg":
                if frag1["sstype"] == "bs" and frag2["sstype"] == "bs":
                    g.es[g.get_eid(frag1.index, frag2.index)]["weight"] = 100*(100.0/z[1])
                    g.es[g.get_eid(frag1.index, frag2.index)]["spantree_weight"] = z[1]/100.0
                elif frag1["sstype"] == "ah" and frag2["sstype"] == "ah":
                    g.es[g.get_eid(frag1.index, frag2.index)]["weight"] = 80 * (100.0 / z[1])
                    g.es[g.get_eid(frag1.index, frag2.index)]["spantree_weight"] = z[1] / 80.0
                else:
                    g.es[g.get_eid(frag1.index, frag2.index)]["weight"] =  (100.0 / z[1])
                    g.es[g.get_eid(frag1.index, frag2.index)]["spantree_weight"] = z[1]
            elif weight == "distance_min":
                if frag1["sstype"] == "bs" and frag2["sstype"] == "bs":
                    g.es[g.get_eid(frag1.index, frag2.index)]["weight"] = 100 * (100.0 / minimum)
                    g.es[g.get_eid(frag1.index, frag2.index)]["spantree_weight"] = minimum / 100.0
                elif frag1["sstype"] == "ah" and frag2["sstype"] == "ah":
                    g.es[g.get_eid(frag1.index, frag2.index)]["weight"] = 80 * (100.0 / minimum)
                    g.es[g.get_eid(frag1.index, frag2.index)]["spantree_weight"] = minimum / 80.0
                else:
                    g.es[g.get_eid(frag1.index, frag2.index)]["weight"] = (100.0 / minimum)
                    g.es[g.get_eid(frag1.index, frag2.index)]["spantree_weight"] = minimum

            if frag1["sstype"] == "bs" and frag2["sstype"] == "bs" and len(minforcvids) > 0:
                teren = len(minforcvids) if len(minforcvids)<3 else len(minforcvids)-2
                q = (sum([max(BS_UD_EA[int(round(ed[0]))],BS_UU_EA[int(round(ed[0]))])/BS_MAX[numpy.argmax([BS_UD_EA[int(round(ed[0]))],BS_UU_EA[int(round(ed[0]))]])] for ed in minforcvids if ed[1] <= 6])/(teren))*100.0
                framme1.append((q,frag2))

        if frag1["sstype"] == "bs":
            for q,frag2 in sorted(framme1,key=lambda x: x[0], reverse=True)[:2]:
                print("PERCENTAGE OF SHEET", q, frag1["sequence"], frag1["reslist"][0][2], frag2["sequence"], frag2["reslist"][0][2], len(frag1["cvids"]), len(frag2["cvids"]))
                if q >= 35:
                    if frag1["sheet"] is not None:
                        if frag2["sheet"] is not None:
                            convert[frag2["sheet"]] = frag1["sheet"]
                        frag2["sheet"] = frag1["sheet"]
                    elif frag2["sheet"] is not None:
                        if frag1["sheet"] is not None:
                             convert[frag1["sheet"]] = frag2["sheet"]
                        frag1["sheet"] = frag2["sheet"]
                    else:
                        frag1["sheet"] = max([u for u in g.vs["sheet"] if u is not None])+1 if len([u for u in g.vs["sheet"] if u is not None]) > 0 else 0
                        frag2["sheet"] = frag1["sheet"]
                        #print("---",frag1["sequence"],frag2["sequence"],frag1["sheet"],frag2["sheet"])
                # else:
                #     if frag1["sheet"] is not None and frag2["sheet"] is not None and frag1["sheet"] == frag2["sheet"]:
                #         frag2["sheet"] = None

    for key in sorted(convert.keys()):
        g.vs["sheet"] = [n if n is None else n if n != key else convert[key]  for n in  g.vs["sheet"]]

    for frag in g.vs:
       if frag["sstype"] == "bs" and frag["sheet"] is None:
           #print("The fragment",frag["sstype"],frag["sequence"],"is converted to coil because is not packed in a sheet")
           #frag["sstype"] = "coil"
           print("The fragment", frag["sstype"], frag["sequence"],"has None sheet id","chain",frag["reslist"][0][2])
       elif frag["sstype"] == "bs":
           print("The fragment",frag["sstype"],frag["sequence"],"has sheet id:",frag["sheet"],"chain",frag["reslist"][0][2])

    return g

def trim_graph_to_the_nearest_n_edges_for_vertex(graph,size_tree=2):
    span = graph.copy()
    eliminate_edges = []
    for node in span.vs:
        # print("node is",node["name"],"index",node.index)
        eliminate_edges += [(ed.source, ed.target) for ed in
                            sorted(span.es.select(lambda e: (e.source == node.index or e.target == node.index)),
                                   key=lambda d: d["mean"][1])[size_tree + 1:]]
    span.delete_edges(list(set(eliminate_edges)))

    while len(span.components()) > 1:
        for i, conne1 in enumerate(span.components()):
            best_edge = None
            best_dist = 100000000000
            best_attri = None
            for j, conne2 in enumerate(span.components()):
                if j != i:
                    drol = [(graph.es[graph.get_eid(c1,c2)]["mean"][1],(c1,c2),graph.es[graph.get_eid(c1,c2)]) for c1 in conne1 for c2 in conne2]
                    drol_min = sorted(drol, key=lambda x: x[0])[0]
                    if drol_min[0] < best_dist:
                        best_dist = drol_min[0]
                        best_edge = drol_min[1]
                        best_attri = drol_min[2].attributes()
            if best_edge is not None:
                span.add_edge(best_edge[0],best_edge[1],**best_attri)
                break

    if size_tree == 1:
        span = span.spanning_tree()

        eliminate_edges = []
        for node in span.vs:
            if node.degree() > 2:
                eliminate_edges += [(ed.source, ed.target) for ed in
                 sorted(span.es.select(lambda e: (e.source == node.index or e.target == node.index)),
                        key=lambda d: d["mean"][1])[1:]]
        span.delete_edges(list(set(eliminate_edges)))

        while len(span.components()) > 1:
            for i, conne1 in enumerate(span.components()):
                best_edge = None
                best_dist = 100000000000
                best_attri = None
                for j, conne2 in enumerate(span.components()):
                    if j != i:
                        drol = [(graph.es[graph.get_eid(c1,c2)]["mean"][1],(c1,c2),graph.es[graph.get_eid(c1,c2)]) for c1 in conne1 for c2 in conne2 if span.vs[c1].degree() < 2 and span.vs[c2].degree() < 2]
                        drol_min = sorted(drol, key=lambda x: x[0])[0]
                        if drol_min[0] < best_dist:
                            best_dist = drol_min[0]
                            best_edge = drol_min[1]
                            best_attri = drol_min[2].attributes()
                if best_edge is not None:
                    span.add_edge(best_edge[0],best_edge[1],**best_attri)
                    break
    return span

@SystemUtility.timing
def get_signature_of_the_graph(graph, pdb_model, structure, size_tree=2):
    original = graph.copy()
    original = original.vs.select(sstype_in=["bs", "ah"]).subgraph()
    original.vs["name"] = [str(vertex["reslist"][0][3][1]) + "_" + str(vertex["reslist"][0][2]) for vertex in original.vs]
    original.es["edgeid"] = [edge.index for edge in original.es]

    # for node1 in original.vs:
    #     for node2 in original.vs:
    #         if node1.index == node2.index:
    #             continue
    #         print("sstype",node1["sstype"],"sequence",node1["sequence"])
    #         print("sstype",node2["sstype"],"sequence",node2["sequence"])
    #         print("unique",original.es[original.get_eid(node1.index, node2.index)]["mean_cv_uniques"][3], original.es[original.get_eid(node1.index, node2.index)]["mean"][1:])
    # quit()
    if size_tree > 1:
        span2 = trim_graph_to_the_nearest_n_edges_for_vertex(original,size_tree=size_tree*2)
    spantree = trim_graph_to_the_nearest_n_edges_for_vertex(original,size_tree=size_tree)

    #NOTE: The following line is for visualization purpose during debug
    ###spantree.write_graphml(os.path.join("./", os.path.basename(pdb_model)[:-4] + "_opera.graphml"))

    vclust1, dendo1 = get_community_clusters_one_step("fastgreedy", spantree, None, "", "", n=None,
                                                    return_dendo=True, write_pdb=False, weight="weight",
                                                    use_spantree=False)

    vclust2, dendo2 = get_community_clusters_one_step("walktrap", spantree, None, "", "", n=None,
                                                    return_dendo=True, write_pdb=False, weight="weight",
                                                    use_spantree=False)

    vclust3, dendo3 = get_community_clusters_one_step("edge_betweenness", spantree, None, "", "", n=None,
                                                      return_dendo=True, write_pdb=False, weight="weight",
                                                      use_spantree=False)

    def geometry_to_string2(geom,skip_secstr=False):
        if not skip_secstr:
            q = "".join(sorted(["H" if geom[-1] == 1 else "S"]+["H" if geom[-2] == 1 else "S"]))
        else:
            q = ""

        if geom[0] <= 30:
            q += "A"
        elif geom[0] <= 60:
            q += "B"
        elif geom[0] <= 90:
            q += "C"
        elif geom[0] <= 120:
            q += "D"
        elif geom[0] <= 150:
            q += "E"
        else:
            q += "F"

        if geom[1] <= 2:
            q += "J"
        elif geom[1] <= 4:
            q += "K"
        elif geom[1] <= 6:
            q += "L"
        elif geom[1] <= 8:
            q += "M"
        elif geom[1] <= 10:
            q += "N"
        elif geom[1] <= 12:
            q += "O"
        elif geom[1] <= 14:
            q += "P"
        elif geom[1] <= 16:
            q += "Q"
        elif geom[1] <= 18:
            q += "R"
        elif geom[1] <= 20:
            q += "S"
        elif geom[1] <= 22:
            q += "T"
        elif geom[1] <= 24:
            q += "U"
        elif geom[1] <= 26:
            q += "V"
        elif geom[1] <= 28:
            q += "W"
        elif geom[1] <= 30:
            q += "Y"
        else:
            q += "Z"

        if geom[2] <= 30:
            q += "a"
        elif geom[2] <= 60:
            q += "b"
        elif geom[2] <= 90:
            q += "c"
        elif geom[2] <= 120:
            q += "d"
        elif geom[2] <= 150:
            q += "e"
        else:
            q += "f"

        geom[3][0] = abs(geom[3][0])
        geom[3][1] = abs(geom[3][1])
        geom[3][2] = abs(geom[3][2])

        if geom[3][0] <= 2:
            q += "J"
        elif geom[3][0] <= 4:
            q += "K"
        elif geom[3][0] <= 6:
            q += "L"
        elif geom[3][0] <= 8:
            q += "M"
        elif geom[3][0] <= 10:
            q += "N"
        elif geom[3][0] <= 12:
            q += "O"
        elif geom[3][0] <= 14:
            q += "P"
        elif geom[3][0] <= 16:
            q += "Q"
        elif geom[3][0] <= 18:
            q += "R"
        elif geom[3][0] <= 20:
            q += "S"
        elif geom[3][0] <= 22:
            q += "T"
        elif geom[3][0] <= 24:
            q += "U"
        elif geom[3][0] <= 26:
            q += "V"
        elif geom[3][0] <= 28:
            q += "W"
        elif geom[3][0] <= 30:
            q += "Y"
        else:
            q += "Z"

        if geom[3][1] <= 2:
            q += "J"
        elif geom[3][1] <= 4:
            q += "K"
        elif geom[3][1] <= 6:
            q += "L"
        elif geom[3][1] <= 8:
            q += "M"
        elif geom[3][1] <= 10:
            q += "N"
        elif geom[3][1] <= 12:
            q += "O"
        elif geom[3][1] <= 14:
            q += "P"
        elif geom[3][1] <= 16:
            q += "Q"
        elif geom[3][1] <= 18:
            q += "R"
        elif geom[3][1] <= 20:
            q += "S"
        elif geom[3][1] <= 22:
            q += "T"
        elif geom[3][1] <= 24:
            q += "U"
        elif geom[3][1] <= 26:
            q += "V"
        elif geom[3][1] <= 28:
            q += "W"
        elif geom[3][1] <= 30:
            q += "Y"
        else:
            q += "Z"

        if geom[3][2] <= 2:
            q += "J"
        elif geom[3][2] <= 4:
            q += "K"
        elif geom[3][2] <= 6:
            q += "L"
        elif geom[3][2] <= 8:
            q += "M"
        elif geom[3][2] <= 10:
            q += "N"
        elif geom[3][2] <= 12:
            q += "O"
        elif geom[3][2] <= 14:
            q += "P"
        elif geom[3][2] <= 16:
            q += "Q"
        elif geom[3][2] <= 18:
            q += "R"
        elif geom[3][2] <= 20:
            q += "S"
        elif geom[3][2] <= 22:
            q += "T"
        elif geom[3][2] <= 24:
            q += "U"
        elif geom[3][2] <= 26:
            q += "V"
        elif geom[3][2] <= 28:
            q += "W"
        elif geom[3][2] <= 30:
            q += "Y"
        else:
            q += "Z"

        return q


    def geometry_to_string(geom,skip_secstr=False):
        if not skip_secstr:
            q = "".join(sorted(["H" if geom[-1] == 1 else "S"]+["H" if geom[-2] == 1 else "S"]))
        else:
            q = ""

        q += "+"+str(int(round(geom[0])))+"+"+str(int(round(geom[1])))+"+"+str(int(round(geom[2])))


        geom[3][0] = abs(geom[3][0])
        geom[3][1] = abs(geom[3][1])
        geom[3][2] = abs(geom[3][2])

        q += "+"+str(int(round(geom[3][0])))+"+"+str(int(round(geom[3][1])))+"+"+str(int(round(geom[3][2])))+"+"

        return q

    def convert_to_string(structure,graphio,original):
        #print("--",graphio.es["edgeid"])
        sheet_used = [ed for ed in graphio.vs]
        graphn = original.copy()
        graphn = graphn.es.select(lambda ed: ed["edgeid"] in graphio.es["edgeid"] or (graphn.vs[ed.source]["name"] in graphio.vs["name"] and graphn.vs[ed.target]["name"] in graphio.vs["name"] and graphn.vs[ed.source]["sstype"]==graphn.vs[ed.target]["sstype"]=="bs" and graphn.vs[ed.source]["sheet"] == graphn.vs[ed.target]["sheet"])).subgraph()
        #print("++",graphn.es["edgeid"])

        edge_list = sorted(graphn.es, key=lambda d: sorted([d.source, d.target]))
        #print("VCOUNT",graphn.vcount(),"ECOUNT",graphn.ecount())
        signature_max = ""
        for edge in edge_list:
            c, d = sorted([edge.source, edge.target])
            erd = "|" if graphn.vs[edge.source]["sstype"]==graphn.vs[edge.target]["sstype"]=="bs" and graphn.vs[edge.source]["sheet"] == graphn.vs[edge.target]["sheet"] else "."
            #erd = str(graphn.vs[c]["sheet"])+"m" if graphn.vs[c]["sstype"] == "bs" else "-1m"
            #erd += str(graphn.vs[d]["sheet"]) if graphn.vs[d]["sstype"]=="bs" else "-1"
            signature_max += "*"+str(c)+"-"+str(d)+":"+graphn.vs[c]["name"]+"-"+graphn.vs[d]["name"]+":"+geometry_to_string(edge["mean_cv_uniques"])+erd

        signature_max = signature_max[1:]

        return signature_max

    def explore_dendogram(spantree,dendo,clust):
        for cut1 in range(1, spantree.vcount()):
            try:
                vclust = dendo.as_clustering(n=cut1)
                vgraph = vclust.subgraphs()

                for gra in vgraph:
                    #print(gra.vcount(),gra.vs["name"],gra.ecount())
                    if gra.vcount() > 1 and  gra.vcount() > 7:
                        sa_ori = original.copy()
                        tra = sa_ori.vs.select(name_in=gra.vs["name"]).subgraph()
                        tra = trim_graph_to_the_nearest_n_edges_for_vertex(tra,size_tree=size_tree) #TODO: it was tree=size_tree+1
                        sa_ori = original.copy()
                        gra = sa_ori.vs.select(name_in=gra.vs["name"]).subgraph().es.select(edgeid_in=[e["edgeid"] for e in gra.es]+[e["edgeid"] for e in tra.es]).subgraph()
                        #print("FROM AAA",gra.vcount(),gra.ecount())
                    if gra.vcount() > 1: clust.add(convert_to_string(structure,gra,original))
            except:
                print("CANOOT GET A CUT n:",cut1)
                #print(sys.exc_info())
                #traceback.print_exc(file=sys.stdout)
        return clust

    clust = set([])
    clust = explore_dendogram(spantree, dendo1, clust)
    clust = explore_dendogram(spantree, dendo2, clust)
    clust = explore_dendogram(spantree, dendo3, clust)

    if size_tree > 1:
        signature_max_final = ";".join([convert_to_string(structure,span2,original)]+[q for q in clust])
    else:
        signature_max_final = ";".join([q for q in clust])

    return signature_max_final

@SystemUtility.timing
def compact_library(directory, reference, sensitivity_ah, sensitivity_bs, peptide_length, write_graphml, write_pdb, cycles, deep, top, sampling, howmany_models, howmany_pdbs, rmsd_thresh, core_percentage=10, criterium_selection_core="residues", force_core_expansion_through_secstr=False, gui=False, signal=None):
    global THRESH_CORR
    THRESH_CORR["min_max"]["isomorphism_ladder"] = 200.0
    THRESH_CORR["min_max"]["total_ladder"] = 200.0
    THRESH_CORR["min_max"]["filter_bipartite"] = 200.0

    paths = []
    for root, subFolders, files in os.walk(directory):
        for fileu in files:
            pdbf = os.path.join(root, fileu)
            if pdbf.endswith(".pdb"):
                paths.append(pdbf)
                Bioinformatics3.rename_hetatm_and_icode(pdbf)

    numpy.random.shuffle(paths)
    if reference is None:
        single_ref = False
    else:
        single_ref = True

    if single_ref:
        f2 = open(reference, "r")
        allpdb = f2.read()
        f2.close()

    if not os.path.exists(os.path.join("./", "library")):
        os.makedirs(os.path.join("./", "library"))

    for z in range(howmany_pdbs):
        inserted = 1
        used = []

        if not single_ref:
            if len(paths) > 0:
                reference = paths[0]
                f2 = open(reference, "r")
                allpdb = f2.read()
                f2.close()
                del paths[0]
            else:
                break
        elif len(paths) == 0:
            break
        path3, file3 = os.path.split(reference)
        f3 = open(os.path.join("./library","full"+str(z)+"_"+str(howmany_models)+"_0.pdb"), "a")
        f3.write("MODEL 1\n")
        f3.write("REMARK TITLE " + os.path.basename(reference) + "\n")
        f3.write(allpdb + "\n")
        f3.write("ENDMDL\n")
        #f3.close()

        f4 = open(os.path.join("./library","core"+str(z)+"_"+str(howmany_models)+"_0.pdb"), "a")
        f4.write("MODEL 1\n")
        f4.write("REMARK TITLE " + os.path.basename(reference) + "\n")
        f4.write(allpdb + "\n")
        f4.write("ENDMDL\n")
        #f4.close()

        f = open("./results_compact.txt", "a")
        for i, pdb1 in enumerate(paths):
            if inserted > howmany_models:
                break

            #{"rmsd": best_rmsd, "size": best_size, "associations": asso, "transf": best_transf, "graph_ref": g_a, "grapf_targ": g_b, "correlation": corr,"pdb_target":pdbmod}
            dictio = perform_superposition(reference=reference, target=pdb1, sensitivity_ah=sensitivity_ah,
                                  sensitivity_bs=sensitivity_bs, peptide_length=peptide_length,
                                  write_graphml=False, write_pdb=False, ncycles=cycles, deep=deep, top=top,
                                  gui=None, sampling=sampling, core_percentage=core_percentage, criterium_selection_core=criterium_selection_core, force_core_expansion_through_secstr=force_core_expansion_through_secstr, verbose=False)
            if not dictio:
                print("Reference:", os.path.basename(reference), "Target:", os.path.basename(pdb1), "rmsd:",
                      "None", "size_core:", 0, "distance:", 1000)
                continue

            print("Reference:",os.path.basename(reference),"Target:",os.path.basename(pdb1),"rmsd:",dictio["rmsd"],"size_core:",dictio["size"],"distance:",dictio["correlation"])
            if dictio["rmsd"] <= rmsd_thresh:
                used.append(i)
                inserted += 1
                f.write("Reference: "+os.path.basename(reference)+" Target: "+os.path.basename(pdb1)+" rmsd: "+str(dictio["rmsd"])+" size_core: "+str(dictio["size"])+" distance: "+str(dictio["correlation"])+"\n")
                #f3 = open(reference[:-4] + "_ensemble.pdb", "a")
                f3.write("MODEL "+str(inserted)+"\n")
                f3.write("REMARK TITLE " + os.path.basename(pdb1) + "\n")
                f3.write(dictio["pdb_target"] + "\n")
                f3.write("ENDMDL\n")
                #f3.close()

                #f4 = open(reference[:-4] + "_core_ensemble.pdb", "a")
                f4.write("MODEL "+str(inserted)+"\n")
                f4.write("REMARK TITLE " + os.path.basename(pdb1) + "\n")
                f4.write(dictio["pdb_core_target"] + "\n")
                f4.write("ENDMDL\n")
                #f4.close()

        paths = SystemUtility.multi_delete(paths,used)
        f.close()
        f3.close()
        f4.close()

    #map_variations_library("./library", gui=None)

def __compute_percentages_of_compatibility(comp, names1, names2):
    n_correct = 0
    n_new = 0
    n_diff = 0
    for h, name1 in enumerate(names1):
        if name1 in comp and comp[name1] == names2[h]:
            n_correct += 1
        elif name1 not in comp and names2[h] not in comp.values():
            n_new += 1
        else:
            n_diff += 1
    score_correct = round((n_correct / len(names1)) * 100.0)
    score_new = round((n_new / len(names1)) * 100.0)
    score_diff = round((n_diff / len(names1)) * 100.0)
    return score_correct, score_new, score_diff

def __sort_and_extract_most_frequent_pairs(comparison, graph_no_coil_reference, graph_no_coil_target, structure_reference, structure_target, maximum=None, signature_threshold=0.0):
    comp = {}
    comparison = [cron for cron in sorted(comparison, key=lambda p: (sum(p[6]) / len(p[6]), len(p[4])), reverse=True) if sum(cron[6])/len(cron[6]) >= 80]
    uno = []
    due = []
    tro = []
    qua = []
    for t, (pdb1, pdb2, ng1, ng2, names1, names2, scores, values) in enumerate(comparison):
        shape1 = shape_parameters_floats([ren for frag in graph_no_coil_reference.vs for ren in frag["reslist"] if frag["name"] in ng1], structure_reference)
        shape2 = shape_parameters_floats([ren for frag in graph_no_coil_target.vs for ren in frag["reslist"] if frag["name"] in ng2], structure_target)
        score_shape = _score_shapes(shape1, shape2)
        comparison[t] = (pdb1, pdb2, ng1, ng2, names1, names2, scores, score_shape, values)
        nlen = len([res for fra in graph_no_coil_reference.vs for res in fra["reslist"] if fra["name"] in ng1])
        uno.append(sum(scores)/len(scores))
        due.append(score_shape)
        tro.append(nlen)
        qua.append(len(names1))

    uno.append(180)
    uno.append(-100)
    due.append(0)
    tro.append(0)
    qua.append(0)
    if SCALING == "robust_scale":
        uno = sklearn.preprocessing.robust_scale(uno, copy=True)
        due = sklearn.preprocessing.robust_scale(due, copy=True)
        tro = sklearn.preprocessing.robust_scale(tro, copy=True)
        qua = sklearn.preprocessing.robust_scale(qua, copy=True)
    elif SCALING == "min_max":
        uno = sklearn.preprocessing.minmax_scale(uno, feature_range=(0, 1), copy=True)
        due = sklearn.preprocessing.minmax_scale(due, feature_range=(0, 1), copy=True)
        tro = sklearn.preprocessing.minmax_scale(tro, feature_range=(0, 1), copy=True)
        qua = sklearn.preprocessing.minmax_scale(qua, feature_range=(0, 1), copy=True)
    uno = uno[:-2]
    due = due[:-1]
    tro = tro[:-1]
    qua = qua[:-1]

    bren = []
    for t, (pdb1, pdb2, ng1, ng2, names1, names2, scores, score_shape, values) in enumerate(comparison):
        totscore = (uno[t]-due[t]+tro[t]+qua[t])/3
        if totscore >= signature_threshold:
            #print("TOTSCORE", totscore, "THRESHOLD", signature_threshold,uno[t])
            bren.append((pdb1, pdb2, ng1, ng2, names1, names2, scores, score_shape, totscore, values))
    comparison = bren

    for t, (pdb1, pdb2, ng1, ng2, names1, names2, scores, score_shape, totscore, values) in enumerate(comparison):
        #comparison[t] = (pdb1, pdb2, ng1, ng2, names1, names2, scores, score_shape, uno[t]-due[t]+tro[t]+qua[t], values)
        for q, n1 in enumerate(names1):
            tre = tuple([n1, names2[q]])
            if tre in comp:
                comp[tre][0] += 1
                comp[tre][1] = max(len(names1), comp[tre][1])
            else:
                comp[tre] = [1, len(names1)]

    comparison = sorted(comparison, key=lambda p: p[8], reverse=True)

    if not maximum:
        maximum = int(round(len(comp.keys()) / 2))
    cc = 0
    combinations = {}
    for tre in sorted(comp.keys(), key=lambda x: comp[x], reverse=True):
        if maximum is not None and cc >= maximum:
            break
        #print(tre, comp[tre])
        combinations[tre[0]] = tre[1]
        cc += 1
    return comparison, combinations, comp

def generate_ensembles(directory, sensitivity_ah, sensitivity_bs, peptide_length, write_graphml, write_pdb, core_percentage=10, criterium_selection_core="residues",force_core_expansion_through_secstr=False, use_seq_alignments=False, score_alignment=30, size_tree=3, gap_open=-10,
                           rmsd_max=6.0, ncycles=15, deep=False, top=4, extract_only_biggest_subfolds=False, gui=None, sampling="none", signal=None):

    def __get_alllist_bysize(ens, namepdb, grafun, totmodels):
        print("====================================================================================")
        print("=                             " + os.path.basename(namepdb) + "                           =")
        print("====================================================================================")
        bysize = {}
        totresids = sum([len(fra["reslist"]) for fra in grafun.vs])
        totmodels = totmodels if totmodels <= 5 else 5

        for key in sorted(ens.keys(), key=lambda x: len(ens[x]), reverse=True):
            print(key, ":", ens[key])
            new_key = tuple([key[0]] + [k[0] for k in ens[key]])
            new_value = [key[1]] + [k[1] for k in ens[key]]
            if new_key not in bysize:
                bysize[new_key] = [new_value]
            else:
                bysize[new_key].append(new_value)

        for key1 in bysize:
            for key2 in bysize:
                if set(key1) < set(key2):
                    indeces = [key2.index(k) for k in key1]
                    for value in bysize[key2]:
                        values = [value[r] for r in indeces]
                        bysize[key1].append(values)

        # for size in bysize:
        #        print ("....",size, bysize[size])
        # quit()

        all_list = []
        for key in sorted(bysize.keys(), key=lambda x: len(x), reverse=True):
            group = []
            for j in range(1, len(key)):
                zorro = [(t[0],t[j]) for t in bysize[key]]
                zorro = set(zorro)
                group.append([[t[0] for t in zorro], [t[1] for t in zorro], (key[0], key[j])])
            all_list.append(group)


        all_list = sorted(all_list, key=lambda x: (len(x)/totmodels) if len(x)<=totmodels else 1.0 +(sum([len(grafun.vs.find(name=z)["reslist"]) for z in set([t.split("-")[0] for t in x[0][0]]+[t.split("-")[1] for t in x[0][0]])])/totresids), reverse=True)
        #all_list_2 = []
        todel = []
        for i,lista1 in enumerate(all_list):
            subnames1 = set([subs[2][1] for subs in lista1])
            n1 = set([t.split("-")[0] for t in lista1[0][0]]+[t.split("-")[1] for t in lista1[0][0]])
            for j,lista2 in enumerate(all_list):
                if j>i:
                    subnames2 = set([subs[2][1] for subs in lista2])
                    n2 = set([t.split("-")[0] for t in lista2[0][0]] + [t.split("-")[1] for t in lista2[0][0]])
                    if subnames2 <= subnames1 and n2<=n1:
                        todel.append(j)
                    elif subnames2 <= subnames1 and round((len(n2&n1) / len(n2|n1)) * 100.0) >= 80:
                        todel.append(j)

        todel = sorted(list(set(todel)), reverse=True)
        print("TODEL:",todel)

        for d in todel:
            del all_list[d]

        all_list = all_list[:size_tree]
        for lista in all_list:
            print("---")
            for sublist in lista:
                print(sublist[2],len(sublist[0]),len(sublist[1]), "--",len(set(tuple(sublist[0]))),len(set(tuple(sublist[1]))))
            print("---")
        print("\n")
        #quit()
        return all_list

    paths = []
    references = []
    for root, subFolders, files in os.walk(directory):
        for fileu in files:
            pdbf = os.path.join(root, fileu)
            if pdbf.endswith("reference.pdb"):
                references.append(pdbf)
                Bioinformatics3.rename_hetatm_and_icode(pdbf)
            elif pdbf.endswith(".pdb"):
                paths.append(pdbf)
                Bioinformatics3.rename_hetatm_and_icode(pdbf)


    totmodels = len(paths)
    if len(references) == 0 : references = paths

    database = {}
    frequencies = {}
    for i, pdb1 in enumerate(references):
        ensembles = {}
        path_base = os.path.join("./", os.path.basename(pdb1)[:-4])
        if not os.path.exists(path_base):
            os.makedirs(path_base)

        qt = 0
        tot = 1
        nome = ""
        pdball = ""
        codec = {}
        for j, pdb2 in enumerate(paths):
            if pdb1 != pdb2:
                print("Comparing", pdb1, "with", pdb2)
                graph_no_coil_reference, matrix_reference, cvs_reference, struct_ref, graph_no_coil_target, matrix_target, cvs_target, struct_targ, signature_ref, signature_targ, possibilities, collections = compare_structures(
                    pdb1, pdb2, sensitivity_ah, sensitivity_bs, peptide_length,
                    write_graphml, write_pdb, ref_tuple=None if pdb1 not in database else database[pdb1],
                    targ_tuple=None if pdb2 not in database else database[pdb2], core_percentage=core_percentage,
                    criterium_selection_core=criterium_selection_core,
                    force_core_expansion_through_secstr=force_core_expansion_through_secstr, verbose=False, gui=gui,
                    signal=signal,
                    use_seq_alignments=use_seq_alignments, score_alignment=score_alignment, size_tree=size_tree,
                    gap_open=gap_open, rmsd_max=-1.0, ncycles=ncycles, deep=deep, top=top,
                    sampling=sampling, extract_only_biggest_subfolds=extract_only_biggest_subfolds, write_pdbs=False,
                    renumber=False, uniqueChain=False, path_base=path_base, use_frequent_as_seed=True)

                if pdb1 not in database:
                    database[pdb1] = (graph_no_coil_reference, matrix_reference, cvs_reference, signature_ref, struct_ref)
                if pdb2 not in database:
                    database[pdb2] = (graph_no_coil_target, matrix_target, cvs_target, signature_targ, struct_targ)

                frequencies[(pdb1,pdb2)] = possibilities[0][2]
                for key in possibilities[0][0]:
                    if (pdb1,key) not in ensembles:
                        ensembles[(pdb1,key)] = [(pdb2,possibilities[0][0][key])]
                    else:
                        ensembles[(pdb1,key)].append((pdb2,possibilities[0][0][key]))

        all_list = __get_alllist_bysize(ensembles,pdb1,database[pdb1][0],totmodels)

        for h, listkeys in enumerate(all_list):
            selection_dict = {}
            superposed = {}
            for q,(names1,names2,key) in enumerate(listkeys):
                    while 1:
                        pdb1 = key[0]
                        pdb2 = key[1]
                        #print("::::::::::::::::::::::::::::::::::::::::::: ",pdb1,pdb2,"q",q)
                        graph_no_coil_reference, matrix_reference, cvs_reference, signature_ref, structure_reference = database[pdb1]
                        graph_no_coil_target, matrix_target, cvs_target, signature_targ, structure_target = database[pdb2]

                        ng1 = [n.split("-")[0] for n in names1]+[n.split("-")[1] for n in names1]
                        ng2 = [n.split("-")[0] for n in names2]+[n.split("-")[1] for n in names2]

                        restrictions = {tuple(sorted(n1.split("-"))):tuple(sorted(n2.split("-"))) for n1,n2 in sorted(zip(names1,names2), key=lambda x: frequencies[(pdb1,pdb2)][x][0], reverse=True)[:size_tree]} #size_tree
                        #restrictions = {tuple(sorted(n1.split("-"))): tuple(sorted(n2.split("-"))) for (n1, n2) in list(zip(names1, names2))}

                        map_secstr_1 = {tuple(res):frag["name"] for frag in graph_no_coil_reference.vs for res in frag["reslist"] if frag["name"] in ng1}
                        map_secstr_2 = {tuple(res):frag["name"] for frag in graph_no_coil_target.vs for res in frag["reslist"] if frag["name"] in ng2}

                        g1 = graph_no_coil_reference.vs.select(name_in=ng1).subgraph()
                        g2 = graph_no_coil_target.vs.select(name_in=ng2).subgraph()
                        pdb_1 = get_pdb_string_from_graph(graph_no_coil_reference, structure_reference, chainid="A", renumber=False, uniqueChain=False)
                        pdb_2 = get_pdb_string_from_graph(graph_no_coil_target, structure_target, chainid="B", renumber=False, uniqueChain=False)

                        dictio_super = perform_superposition(reference=(io.StringIO(SystemUtility.py2_3_unicode(pdb_1)),structure_reference,graph_no_coil_reference.vs.select(name_in=ng1).subgraph(),matrix_reference,cvs_reference),
                                                              target=(io.StringIO(SystemUtility.py2_3_unicode(pdb_2)),structure_target,graph_no_coil_target.vs.select(name_in=ng2).subgraph(),matrix_target,cvs_target),
                                                              sensitivity_ah=0.000001,
                                                              sensitivity_bs=0.000001,
                                                              peptide_length=peptide_length,
                                                              write_graphml=False, write_pdb=False, ncycles=ncycles,
                                                              deep=deep, top=top, max_sec=1, break_sec=100, min_correct=2,
                                                              gui=None, sampling=sampling,
                                                              core_percentage=core_percentage,
                                                              criterium_selection_core=criterium_selection_core,
                                                              force_core_expansion_through_secstr=force_core_expansion_through_secstr,
                                                              restrictions_edges=restrictions, map_reference=map_secstr_1, map_target=map_secstr_2, verbose=False)

                        if dictio_super and dictio_super["rmsd"] <= rmsd_max*2:
                            pdacc = dictio_super["pdb_target"]
                            dictus = Bioinformatics3.get_CA_distance_dictionary(
                                io.StringIO(SystemUtility.py2_3_unicode(pdb_1)),
                                io.StringIO(SystemUtility.py2_3_unicode(pdacc)), max_rmsd=rmsd_max, last_rmsd=rmsd_max,
                                recompute_rmsd=False, cycles=1, cycle=1, before_apply=None,
                                get_superposed_atoms=False)


                            #atm1 = [atz for ren in Bioinformatics3.get_list_of_residues(structure_reference) for atz in ren if ren.get_full_id()[1:4] in [tr[1:4] for tr in dictus.keys()] and atz.get_name().lower() in ["ca","cb","c","o","n"]]
                            #atm2 = [atz for ren in Bioinformatics3.get_list_of_residues(structure_target) for atz in ren if ren.get_full_id()[1:4] in [tr[1][1:4] for tr in dictus.values()] and atz.get_name().lower() in ["ca","cb","c","o","n"]]
                            #stri1 = Bioinformatics3.get_pdb_from_list_of_atoms(atm1, renumber=False, uniqueChain=False, chainId="A", chainFragment=False, diffchain=None, polyala=False, maintainCys=False, normalize=False, sort_reference=True)[0]
                            #stri2 = Bioinformatics3.get_pdb_from_list_of_atoms(atm2, renumber=False, uniqueChain=False, chainId="A", chainFragment=False, diffchain=None, polyala=False, maintainCys=False, normalize=False, sort_reference=True)[0]
                            nem = set([nhj["name"] for nhj in g1.vs if len(set([tuple(tr[1:4]) for tr in nhj["reslist"]]) & set([tuple(res[1:4]) for res in dictus.keys()])) > 0])
                            names1l = [nel for nel in names1 if nel.split("-")[0] not in nem and nel.split("-")[1] not in nem]
                            names2l = [names2[r] for r,t in enumerate(names1) if t in names1l]

                            selected_names1 = [nel for nel in names1 if nel.split("-")[0] in nem and nel.split("-")[1] in nem]
                            selected_names2 = [names2[r] for r,t in enumerate(names1) if t in selected_names1]
                            print("SELECTED 1",selected_names1)
                            print("SELECTED 2",selected_names2)
                            print("REMAININGS",list(zip(names1l,names2l)))

                            for z, nam1 in enumerate(selected_names1):
                                if (pdb1, nam1) not in selection_dict:
                                    selection_dict[(pdb1, nam1)] = [(pdb2, selected_names2[z])]
                                elif (pdb2, selected_names2[z]) not in selection_dict[(pdb1, nam1)]:
                                    selection_dict[(pdb1, nam1)].append((pdb2, selected_names2[z]))

                            if (pdb1, pdb2) not in superposed:
                                superposed[(pdb1, pdb2)] = [(tuple(selected_names1),tuple(selected_names2),pdb_1,pdacc)]
                            else:
                                superposed[(pdb1, pdb2)].append((tuple(selected_names1),tuple(selected_names2),pdb_1,pdacc))

                            if set(names1l)==set(names1):
                                break
                            else:
                                # with open("r.pdb", "w") as f:
                                #     f.write(pdb_1)
                                #
                                # with open("t.pdb", "w") as f:
                                #     f.write(pdacc)
                                # print(restrictions)

                                names1 = names1l
                                names2 = names2l
                                #print("SHERLOCK NAMES1",names1)
                                #print("SHERLOCK NAMES2",names2)

                                if len(names1) == 0 or len(names2) == 0:
                                    break
                        else:
                            # with open("r.pdb", "w") as f:
                            #     f.write(pdb_1)
                            #
                            # with open("t.pdb", "w") as f:
                            #     f.write(pdb_2)
                            # print(restrictions)
                            # quit()
                            break

            all_list2 = __get_alllist_bysize(selection_dict,pdb1,database[pdb1][0],totmodels)

            for w, listkeys2 in enumerate(all_list2):
                for q2, (names1, names2,  key) in enumerate(listkeys2):
                    pdb1 = key[0]
                    pdb2 = key[1]
                    graph_no_coil_reference, matrix_reference, cvs_reference, signature_ref, structure_reference = database[pdb1]
                    graph_no_coil_target, matrix_target, cvs_target, signature_targ, structure_target = database[pdb2]

                    pdb_1 = None
                    pdbacc = None
                    for chi in superposed[(pdb1,pdb2)]:
                        #print(names1,set(superposed[(pdb1,pdb2)][0]))
                        #print(names2,set(superposed[(pdb1,pdb2)][1]))
                        #print("SHERLOCK",set(names1),set(chi[0]))
                        #print("SHERLOCK",set(names2),set(chi[1]))
                        if len(set(names1)&set(chi[0]))>0 and len(set(names2)&set(chi[1]))>0:
                            pdb_1 = chi[2]
                            pdbacc = chi[3]
                            break
                    #print()
                    # ng1 = [n.split("-")[0] for n in names1] + [n.split("-")[1] for n in names1]
                    # ng2 = [n.split("-")[0] for n in names2] + [n.split("-")[1] for n in names2]
                    # g1 = graph_no_coil_reference.vs.select(name_in=ng1).subgraph()
                    # g2 = graph_no_coil_target.vs.select(name_in=ng2).subgraph()
                    # pdb_1 = get_pdb_string_from_graph(graph_no_coil_reference, structure_reference, chainid="A", renumber=False, uniqueChain=False)
                    # pdb_2 = get_pdb_string_from_graph(graph_no_coil_target, structure_target, chainid="B", renumber=False, uniqueChain=False)
                    # restrictions = {tuple(sorted(n1.split("-"))): tuple(sorted(n2.split("-"))) for n1, n2 in
                    #                 sorted(zip(names1, names2), key=lambda x: frequencies[(pdb1, pdb2)][x][0],
                    #                        reverse=True)[:size_tree]}
                    # map_secstr_1 = {tuple(res): frag["name"] for frag in graph_no_coil_reference.vs for res in
                    #                 frag["reslist"] if frag["name"] in ng1}
                    # map_secstr_2 = {tuple(res): frag["name"] for frag in graph_no_coil_target.vs for res in
                    #                 frag["reslist"] if frag["name"] in ng2}
                    #
                    # dictio_super = perform_superposition(reference=(io.StringIO(SystemUtility.py2_3_unicode(pdb_1)), structure_reference, graph_no_coil_reference.vs.select(name_in=ng1).subgraph(), matrix_reference, cvs_reference),target=(io.StringIO(SystemUtility.py2_3_unicode(pdb_2)), structure_target, graph_no_coil_target.vs.select(name_in=ng2).subgraph(), matrix_target, cvs_target),
                    #                                      sensitivity_ah=0.000001,
                    #                                      sensitivity_bs=0.000001,
                    #                                      peptide_length=peptide_length,
                    #                                      write_graphml=False, write_pdb=False, ncycles=ncycles,
                    #                                      deep=deep, top=top, max_sec=5, break_sec=300, min_correct=2,
                    #                                      gui=None, sampling=sampling,
                    #                                      core_percentage=core_percentage,
                    #                                      criterium_selection_core=criterium_selection_core,
                    #                                      force_core_expansion_through_secstr=force_core_expansion_through_secstr,
                    #                                      restrictions_edges=restrictions, map_reference=map_secstr_1,
                    #                                      map_target=map_secstr_2, verbose=True)
                    # pdbacc = None
                    # print("HERE IT COMES THE TRUE:",dictio_super["rmsd"] if dictio_super else dictio_super,rmsd_max*2)
                    # print("restrictions",restrictions)
                    # print("NOMI",key[0],key[1])
                    # if dictio_super and dictio_super["rmsd"] <= rmsd_max*2:
                    #     pdbacc = dictio_super["pdb_target"]
                    #####structure_target_acc = Bioinformatics3.get_structure("uff",io.StringIO(SystemUtility.py2_3_unicode(pdbacc)))
                    #####dictus = Bioinformatics3.get_CA_distance_dictionary(
                    #####        io.StringIO(SystemUtility.py2_3_unicode(pdb_1)),
                    #####        io.StringIO(SystemUtility.py2_3_unicode(pdbacc)), max_rmsd=rmsd_max, last_rmsd=rmsd_max,
                    #####        recompute_rmsd=False, cycles=1, cycle=1, before_apply=None,
                    #####        get_superposed_atoms=False)

                    #####atm2 = [atz for ren in Bioinformatics3.get_list_of_residues(structure_target_acc) for atz in ren if ren.get_full_id()[1:4] in [tr[1][1:4] for tr in dictus.values()] and atz.get_name().lower() in ["ca","cb","c","o","n"]]
                    #####pdbacc = Bioinformatics3.get_pdb_from_list_of_atoms(atm2, renumber=False, uniqueChain=False, chainId="A", chainFragment=False, diffchain=None, polyala=False, maintainCys=False, normalize=False, sort_reference=True)[0]

                    nres = sum([len(frag["reslist"]) for frag in g1.vs])
                    if q2 == 0 and len(nome) == 0:
                        #nome = os.path.join(path_base, "ensemble_" + str(qt) + "_" + os.path.basename(pdb1)[:-4] + "_" + str(nres) + "aa" + ".pdb")
                        nome = os.path.join(path_base, "ensemble_" + str(qt) + ".pdb")
                        pdball += "MODEL " + str(q2) + "\n"
                        codec[q2] = os.path.basename(pdb1)
                        pdball += "REMARK TITLE " + os.path.basename(pdb1) + "\n"
                        pdball += pdb_1
                        pdball += "ENDMDL" + "\n"

                    if pdbacc is not None:
                        pdball += "MODEL " + str(tot) + "\n"
                        codec[tot] = os.path.basename(pdb2)
                        pdball += "REMARK TITLE " + os.path.basename(pdb2) + "\n"
                        pdball += pdbacc
                        pdball += "ENDMDL"+"\n"
                        tot += 1

        if os.path.exists(nome):
            print("ERROR THIS SHOULD NOT EXISTS",nome)
            quit()

        if len(nome) > 0:
            with open(nome,"w") as flo:
                flo.write(pdball)
                qt += 1

        pdball = Bioinformatics3.trim_ensemble_to_distance(nome,codec,rmsd_max)
        if len(pdball) > 0:
            with open(nome, "w") as flo:
                flo.write(pdball)


def understand_dynamics(directory, sensitivity_ah, sensitivity_bs, peptide_length, write_graphml, write_pdb,
                       core_percentage=10, criterium_selection_core="residues",
                       force_core_expansion_through_secstr=False, use_seq_alignments=False, score_alignment=30,
                       size_tree=3, gap_open=-10,
                       rmsd_max=6.0, ncycles=15, deep=False, top=4, extract_only_biggest_subfolds=False, gui=None,
                       sampling="none", signal=None):
    paths = []
    for root, subFolders, files in os.walk(directory):
        for fileu in files:
            pdbf = os.path.join(root, fileu)
            if pdbf.endswith(".pdb"):
                paths.append(pdbf)
                Bioinformatics3.rename_hetatm_and_icode(pdbf)

    database = {}
    results = []
    for i, pdb1 in enumerate(paths):
        ensembles = {}
        for j, pdb2 in enumerate(paths):
            if i != j:
                path_base = os.path.join("./",os.path.basename(pdb1)[:-4]+"_"+os.path.basename(pdb2)[:-4])
                if not os.path.exists(path_base):
                    os.makedirs(path_base)
                print("Comparing", pdb1, "with", pdb2)
                graph_no_coil_reference, matrix_reference, cvs_reference, struct_ref, graph_no_coil_target, matrix_target, cvs_target, struct_targ, signature_ref, signature_targ, possibilities, collections = compare_structures(
                    pdb1, pdb2, sensitivity_ah, sensitivity_bs, peptide_length,
                    write_graphml, write_pdb, ref_tuple=None if pdb1 not in database else database[pdb1],
                    targ_tuple=None if pdb2 not in database else database[pdb2], core_percentage=core_percentage,
                    criterium_selection_core=criterium_selection_core,
                    force_core_expansion_through_secstr=force_core_expansion_through_secstr, verbose=False, gui=gui,
                    signal=signal,
                    use_seq_alignments=use_seq_alignments, score_alignment=score_alignment, size_tree=size_tree,
                    gap_open=gap_open, rmsd_max=rmsd_max, ncycles=ncycles, deep=deep, top=top,
                    sampling=sampling, extract_only_biggest_subfolds=extract_only_biggest_subfolds, write_pdbs=False,
                    renumber=False, uniqueChain=False,path_base=path_base, use_frequent_as_seed=True)

                if pdb1 not in database:
                    database[pdb1] = (graph_no_coil_reference, matrix_reference, cvs_reference, signature_ref, struct_ref)
                if pdb2 not in database:
                    database[pdb2] = (graph_no_coil_target, matrix_target, cvs_target, signature_targ, struct_targ)


def compare_signatures(sign_r,graph_no_coil_reference,structure_reference,sign_t,graph_no_coil_target,structure_target, write_pdbs=True, search_in_both=True, renumber=True, uniqueChain=True,path_base="./",size_tree=5,biggest_is=None, use_frequent_as_seed=False, verbose=False,signature_threshold=0.0):
    global SIGNATURE_ANGLE_BS
    signa_ang_bs = SIGNATURE_ANGLE_BS

    #shape_r_l = [[h.split(":")[3] for h in z.split("*")] for z in sign_r.split(";")]
    #shape_t_l = [[h.split(":")[3] for h in z.split("*")] for z in sign_t.split(";")]
    sign_r_l = [[h.split(":")[2] for h in z.split("*")] for z in sign_r.split(";")]
    sign_t_l = [[h.split(":")[2] for h in z.split("*")] for z in sign_t.split(";")]
    names_r_l = [[h.split(":")[1] for h in z.split("*")] for z in sign_r.split(";")]
    names_t_l = [[h.split(":")[1] for h in z.split("*")] for z in sign_t.split(";")]
    ids_r_l = [[h.split(":")[0] for h in z.split("*")] for z in sign_r.split(";")]
    ids_t_l = [[h.split(":")[0] for h in z.split("*")] for z in sign_t.split(";")]

    if biggest_is is not None and biggest_is.lower() == "reference":
        biggest_is = graph_no_coil_reference.vcount()
    elif biggest_is is not None and biggest_is.lower() == "target":
        biggest_is = graph_no_coil_target.vcount()
    else:
        biggest_is = None

    set_all = set([])
    def _fill_set_sol(sign1, names1, ids1, sign2, names2, ids2, set_all, biggest_is, viceversa=False):
        visited = set([])
        for j, val_1 in enumerate(sign1):
            #print(j,val_1)
            ####if j == 0:
            ####    continue
            nodes_1 = [int(p) for c in ids1[j] for p in c.split("-")]
            nam_1 = names1[j]
            nlr1 = set([nj.split("-")[0] for nj in nam_1]+[nj.split("-")[1] for nj in nam_1])

            if biggest_is is not None and len(nlr1) < biggest_is:
                continue
            #print("------s-s-------s-s-",nlr1)
            g1 = igraph.Graph(max(nodes_1) + 1, directed=False)

            #betas = {}
            for f, spli in enumerate(ids1[j]):
                # q1 = int(val_1[f][8:].split("m")[0])
                # q2 = int(val_1[f][8:].split("m")[1])
                # o1 = int(spli.split("-")[0])
                # o2 = int(spli.split("-")[1])
                #
                # if q1 not in betas:
                #     betas[q1] = set([o1])
                # else:
                #     betas[q1].add(o1)
                #
                # if q2 not in betas:
                #     betas[q2] = set([o2])
                # else:
                #     betas[q2].add(o2)
                #
                # print("--",val_1[f])
                # val_1[f] = val_1[f][:8]+"|" if q1 == q2 != -1 else val_1[f][:8]+"."
                # print("++",val_1[f])

                g1.add_edge(int(spli.split("-")[0]), int(spli.split("-")[1]), value=val_1[f], names=nam_1[f], signature_angle_bs=signa_ang_bs)


            val_2 = sign2
            nodes_2 = [int(p) for c in ids2 for p in c.split("-")]
            nam_2 = names2
            nlr2 = set([nj.split("-")[0] for nj in nam_2]+[nj.split("-")[1] for nj in nam_2])
            #print("------o-o-------o-o-",nlr2)
            ciao = (tuple(nam_1), tuple(nam_2))
            if ciao in visited:
                continue
            else:
                visited.add(ciao)

            g2 = igraph.Graph(max(nodes_2) + 1, directed=False)
            for f, spli in enumerate(ids2):
                g2.add_edge(int(spli.split("-")[0]), int(spli.split("-")[1]), value=val_2[f], names=nam_2[f], signature_angle_bs=signa_ang_bs)

            #print("COMPATIBLE",g2)
            isom = g2.get_subisomorphisms_vf2(g1, edge_compat_fn=is_edge_compatible_from_signature)

            for iso in isom:
                uno = [s.index for s in g1.vs]
                due = iso
                dic_ana = {uno[y]: due[y] for y in range(len(uno))}
                score_total = [_score_words(g1.es[s.index]["value"], g2.es[g2.get_eid(dic_ana[s.source],dic_ana[s.target])]["value"],signature_angle_bs=signa_ang_bs) for s in g1.es]
                # if tuple(score_total) == (130, 90, 90, 120, 20, 50, 80):
                #     print("REF", uno)
                #     print("TARG", due)
                #
                #     for cd in g2.es:
                #         print("--", cd.source, cd.target, cd["value"], cd["names"])
                #     for cd in g1.es:
                #         print("ANALIZZO",cd.source, cd.target, cd["value"], cd["names"],"CON",g2.es[g2.get_eid(dic_ana[cd.source],dic_ana[cd.target])]["value"],_score_words(cd["value"], g2.es[g2.get_eid(dic_ana[cd.source],dic_ana[cd.target])]["value"],signature_angle_bs=signa_ang_bs))
                values = [(g1.es[s.index]["value"], g2.es[g2.get_eid(dic_ana[s.source],dic_ana[s.target])]["value"]) for s in g1.es]
                ones = g1.vs.select(lambda v: v.index in uno).subgraph()
                twos = [g2.es[g2.get_eid(dic_ana[e.source], dic_ana[e.target])] for e in ones.es]
                #twos = g2.es.select(lambda e: e.source in due and e.target in due and g1.get_eid(dic_ana[e.source], dic_ana[e.target], error=False) >= 0).subgraph()
                one = [o["value"] for o in ones.es]
                one_names = [o["names"] for o in ones.es]
                two = [o["value"] for o in twos]
                two_names = [o["names"] for o in twos]
                # print(one_names)
                # print(two_names)
                # print(score_total,sum(score_total))
                # print()
                #two_names = g2.es.select(lambda e: e.source in due and e.target in due and g1.get_eid(dic_ana[e.source], dic_ana[e.target], error=False) >= 0).subgraph().es["names"]
                e = tuple(sorted(set([s for w in one_names for s in w.split("-")])))
                d = tuple(sorted(set([s for w in two_names for s in w.split("-")])))

                if viceversa:
                    set_all.add((d, e, tuple(two_names), tuple(one_names), tuple(score_total), tuple(values)))
                else:
                    set_all.add((e, d, tuple(one_names), tuple(two_names), tuple(score_total), tuple(values)))
        return set_all

    set_all = _fill_set_sol(sign_r_l, names_r_l, ids_r_l, sign_t_l[0], names_t_l[0], ids_t_l[0],set_all, biggest_is)
    if search_in_both:
        set_all = _fill_set_sol(sign_t_l, names_t_l, ids_t_l, sign_r_l[0], names_r_l[0], ids_r_l[0], set_all, biggest_is, viceversa=True)

    cont_pdb = 0

    stri_all = []
    for se in set_all:
        # print(se)
        # if len(se[0]) > max_size:
        #     max_size = len(se[0])
            #print("CURRENT MAXIMUM SIZE IS", max_size)
            #print("SHRELOCK:",se[0])
        g1 = graph_no_coil_reference.vs.select(name_in=se[0]).subgraph()
        g2 = graph_no_coil_target.vs.select(name_in=se[1]).subgraph()
        # print(g1.vs["name"],g2.vs["name"])
        stri1 = get_pdb_string_from_graph(g1, structure_reference, chainid="A", renumber=renumber, uniqueChain=uniqueChain)
        stri2 = get_pdb_string_from_graph(g2, structure_target, chainid="B", renumber=renumber, uniqueChain=uniqueChain)
        if write_pdbs:
            with open(os.path.join(path_base, "comparison_" + str(cont_pdb) + ".pdb"), "w") as f:
                f.write(stri1)
                f.write(stri2)
        stri_all.append((stri1,stri2,se[0],se[1],se[2],se[3],se[4],se[5]))
        cont_pdb += 1

    comparison = stri_all

    collections = []
    possibilities = []

    if len(comparison) == 0:
        return possibilities, collections

    print("NUMBER OF FOUND FOLDS before trimming", len(comparison))
    comparison, combinations, frequency = __sort_and_extract_most_frequent_pairs(comparison,graph_no_coil_reference, graph_no_coil_target, structure_reference, structure_target, maximum=size_tree, signature_threshold=signature_threshold)
    comparison = comparison[:size_tree*3]
    print("NUMBER OF FOUND FOLDS after trimming", len(comparison))

    comparison = sorted(comparison, key=lambda p: p[8], reverse=True)

    verbose = True
    if verbose:
        for t, (pdb1, pdb2, ng1, ng2, names1, names2, scores, score_shape, totsco, values) in enumerate(comparison):
            if t < (size_tree*3)+1:
                print("=================",t,"=================")#, "cocco_" + str(0) + "_" + str(t) + ".pdb")
                print(ng1)
                print(ng2)
                print(names1)
                print(names2)
                print(values)
                print(scores, sum(scores) / len(scores), "shape", score_shape, "tot", totsco)
                # foe = open("cocco_" + str(0) + "_" + str(t) + ".pdb", "w")
                # foe.write(pdb2)
                # foe.close()
                print("=================","-","=================")

    #print("SHERLOCK",combinations)
    collections.append([])
    first = use_frequent_as_seed
    while len(comparison) > 0:
        if first:
            comp = combinations
            first = False
        else:
            comp = {}
        for k in range(2):
            remainings = []
            #print("BEFORE LEN COMPARISON", len(comparison))
            comparison = sorted(comparison, key=lambda p: p[8], reverse=True)
            for t, (pdb1, pdb2, ng1, ng2, names1, names2, scores, score_shape, totsco, values) in enumerate(comparison):
                score_correct, score_new, score_diff = __compute_percentages_of_compatibility(comp, names1, names2)

                #print(t, "CORRECT", score_correct, "NEW", score_new, "DIFF", score_diff)
                #print(t,"COLLECTION NOW IS",[tuple(sorted(n[2])) for n in collections[-1]])

                if score_new >= 100 and (k == 1 or len(comp.keys()) == 0):
                    for h, name1 in enumerate(names1):
                        comp[name1] = names2[h]
                    collections[-1].append(comparison[t])
                    # print("I AM IN A")
                elif score_new >= 100:
                    remainings.append(comparison[t])
                    # print("I AM IN B")
                elif score_correct >= 100 and k == 0 and tuple(sorted(ng1)) not in [tuple(sorted(n[2])) for n in collections[-1]]:
                    # print("I AM IN C")
                    # print(tuple(sorted(ng1)))
                    # print([tuple(sorted(n[2])) for n in collections[-1]])
                    # print()
                    collections[-1].append(comparison[t])
                elif score_diff <= 0:
                    # print("I AM IN D")
                    for h, name1 in enumerate(names1):
                        if name1 not in comp:
                            comp[name1] = names2[h]
                    if score_new > 0:
                        collections[-1].append(comparison[t])
                else:
                    # print("I AM IN E")
                    remainings.append(comparison[t])
            comparison = remainings
            #print("AFTER LEN COMPARISON", len(comparison))
    possibilities.append([combinations])

    # print("NUMBER OF FOUND FOLDS after trimming", len(possibilities))
    # print("NUMBER OF COLLECTIONS after trimming", len(collections))
    # print("NUMBER OF DISCARDED combinations", len(comparison))
    #
    # print("------------------------------------------------------------------------")
    # comparison = sorted(comparison, key=lambda p: (sum(p[6]) / len(p[6]), len(p[4])), reverse=True)
    # for s, (pdb1, pdb2, ng1, ng2, names1, names2, scores, score_shape, values) in enumerate(comparison):
    #     print(s)
    #     print("NAME1", names1)
    #     print("NAME2", names2)
    #     print(ng1,len(ng1))
    #     print(ng2,len(ng2))
    #     print("SCORES", scores, sum(scores) / len(scores))
    #     print("PAIRS", values)
    #     print()
    # print("------------------------------------------------------------------------")
    max_size = 0

    for t, collect in enumerate(collections):
        g = igraph.Graph()
        g.vs["name"] = []
        d = []
        collect = sorted(collect, key=lambda p: len(p[4]), reverse=True)
        for s, (pdb11, pdb21, ng11, ng21, names11, names21, scores1, score_shape1, totsco1, values1) in enumerate(collect):
            if len(ng11) > max_size:
                max_size = len(ng11)
                print("CURRENT MAX SIZE IS:", max_size,ng11,ng21)
            #elif len(ng11) == max_size:
            #    print("OTHER ACCEPTABLE SIZE IS:", max_size,ng11,ng21)

            firma1 = json.dumps(sorted(names11+names21))
            if firma1 not in g.vs["name"]:
                g.add_vertex(name=firma1)

            l1 = g.vs.find(name=firma1).index

            for p, (pdb12, pdb22, ng12, ng22, names12, names22, scores2, score_shape2, totsco2, values2) in enumerate(collect):
                if p <= s:
                    continue
                firma2 = json.dumps(sorted(names12+names22))
                if firma2 not in g.vs["name"]:
                    g.add_vertex(name=firma2)
                l2 = g.vs.find(name=firma2).index

                if set(ng11) <= set(ng12):
                    d += [(w.source,w.target) for w in g.es.select(lambda e: e.source == l1 or e.target == l1)]
                    g.add_edge(l1,l2,diff=len(set(ng12)-set(ng11)),weight=1/len(set(ng12)-set(ng11)) if len(set(ng12)-set(ng11))>0 else 0,common=[list(set(ng11)&set(ng12)),list(set(ng21)&set(ng22))],is_subset=True)
                elif set(ng12) <= set(ng11):
                    d += [(w.source,w.target) for w in g.es.select(lambda e: e.source == l2 or e.target == l2)]
                    g.add_edge(l1,l2,diff=len(set(ng11)-set(ng12)),weight=1/len(set(ng11)-set(ng12)) if len(set(ng11)-set(ng12))>0 else 0,common=[list(set(ng11)&set(ng12)),list(set(ng21)&set(ng22))],is_subset=True)
                elif len(set(ng11)&set(ng12)) > 0:
                    g.add_edge(l1,l2,diff=len(set(ng11)-set(ng12)),weight=1/len(set(ng11)-set(ng12)) if len(set(ng11)-set(ng12))>0 else 0,common=[list(set(ng11)&set(ng12)),list(set(ng21)&set(ng22))],is_subset=False)
        # print("BEFORE===========")
        # for cro in g.vs:
        #     print(cro["name"])
        # print("=================")
        # g.delete_edges(d)
        # print("AFTER===========")
        # for cro in g.vs:
        #     print(cro["name"])
        # print("=================")
        possibilities[t].append(g)
        possibilities[t].append(frequency)

    return possibilities, collections

#@SystemUtility.timing
def compare_structures(reference, target, sensitivity_ah, sensitivity_bs, peptide_length, write_graphml, write_pdb, core_percentage=10, criterium_selection_core="residues",force_core_expansion_through_secstr=False, ref_tuple=None, targ_tuple=None, verbose=False, use_seq_alignments=False, score_alignment=20, size_tree=5, gap_open=-10, rmsd_max=6.0, ncycles=15, deep=False, top=4, gui=None, sampling="none", extract_only_biggest_subfolds=True, write_pdbs=True, renumber=True, uniqueChain=True, signal=None, path_base="./", search_in_both=True, biggest_is=None, use_frequent_as_seed=False, signature_threshold=0.0):

    if isinstance(reference, io.StringIO):
        reference.seek(0)
    if isinstance(target, io.StringIO):
        target.seek(0)

    sort_mode = "avg"

    if sensitivity_ah < 0:
        sensitivity_ah = 0.45
    if sensitivity_bs < 0:
        sensitivity_bs = 0.20

    weight = "distance_avg"
    pep_len = int(peptide_length)

    pdb_search_in = ""
    if isinstance(reference, io.StringIO):
        all_lines = reference.readlines()
    else:
        f = open(reference, "r")
        all_lines = f.readlines()
        f.close()

    for line in all_lines:
        if line[:6] in ["TITLE ", "CRYST1", "SCALE1", "SCALE2", "SCALE3"]:
            pdb_search_in += line

    if isinstance(reference, io.StringIO):
        reference.seek(0)

    if ref_tuple is None:
        graph_full_reference, structure_reference, matrix_reference, cvs_reference, highd_reference = annotate_pdb_model_with_aleph(
            reference, weight=weight, min_diff_ah=sensitivity_ah, min_diff_bs=sensitivity_bs, peptide_length=pep_len,
            write_pdb=write_pdb,path_base=path_base)
        graph_full_reference.vs["name"] = [str(vertex["reslist"][0][3][1]) + "_" + str(vertex["reslist"][0][2]) for
                                           vertex
                                           in graph_full_reference.vs]
        graph_no_coil_reference = graph_full_reference.vs.select(sstype_in=["ah", "bs"]).subgraph()
        eigen_ref = graph_no_coil_reference.evcent(directed=False, scale=True,
                                                   weights=graph_no_coil_reference.es["weight"],
                                                   return_eigenvalue=True)
        # print("EIGEN Centrality values:", eigen_ref, len(eigen_ref[0]), len(graph_no_coil_reference.vs))
        graph_no_coil_reference.vs["eigen"] = eigen_ref[0]
        graph_no_coil_reference.vs["Label"] = [d["sstype"] + "_" + d["name"] for t, d in
                                               enumerate(graph_no_coil_reference.vs)]
        if not isinstance(reference, io.StringIO) and write_graphml:
            graph_no_coil_reference.write_graphml(os.path.join(path_base, os.path.basename(reference)[:-4] + "_graphref.graphml"))
        sign_r = get_signature_of_the_graph(graph_no_coil_reference, reference, structure_reference, size_tree=1) #TODO: Changed for debugging be careful
    else:
        graph_no_coil_reference, matrix_reference, cvs_reference, sign_r, structure_reference = ref_tuple

    pdb_search_in = ""
    with open(target, "r") as f:
        all_lines = f.readlines()

    for line in all_lines:
        if line[:6] in ["TITLE ", "CRYST1", "SCALE1", "SCALE2", "SCALE3"]:
            pdb_search_in += line

    if targ_tuple is None:
        graph_full_target, structure_target, matrix_target, cvs_target, highd_reference = annotate_pdb_model_with_aleph(
            target, weight=weight, min_diff_ah=sensitivity_ah, min_diff_bs=sensitivity_bs, peptide_length=pep_len,
            write_pdb=write_pdb,path_base=path_base)
        graph_full_target.vs["name"] = [str(vertex["reslist"][0][3][1]) + "_" + str(vertex["reslist"][0][2]) for vertex
                                        in graph_full_target.vs]
        graph_no_coil_target = graph_full_target.vs.select(sstype_in=["ah", "bs"]).subgraph()
        eigen_targ = graph_no_coil_target.evcent(directed=False, scale=True, weights=graph_no_coil_target.es["weight"],
                                                 return_eigenvalue=True)
        # print("EIGEN Centrality values:", eigen_ref, len(eigen_ref[0]), len(graph_no_coil_reference.vs))
        graph_no_coil_target.vs["eigen"] = eigen_targ[0]
        graph_no_coil_target.vs["Label"] = [d["sstype"] + "_" + d["name"] for t, d in
                                            enumerate(graph_no_coil_target.vs)]

        if graph_no_coil_target.vcount() < 2:
            print("WARNING: NOT ENOUGH SECONDARY STRUCTURE CONTENT FOUND IN PDB")
            raise Exception

        if not isinstance(target, io.StringIO) and write_graphml:
            graph_no_coil_target.write_graphml(os.path.join(path_base, os.path.basename(target)[:-4] + "_graphtarg.graphml"))
        sign_t = get_signature_of_the_graph(graph_no_coil_target, target, structure_target, size_tree=size_tree)
    else:
        graph_no_coil_target, matrix_target, cvs_target, sign_t, structure_target = targ_tuple
        if graph_no_coil_target.vcount() < 2:
            print("WARNING: NOT ENOUGH SECONDARY STRUCTURE CONTENT FOUND IN PDB")
            raise Exception

    if rmsd_max < 0:
        possibilities, collections = compare_signatures(sign_r, graph_no_coil_reference, structure_reference, sign_t, graph_no_coil_target, structure_target, write_pdbs=write_pdbs, search_in_both=search_in_both, renumber=renumber, uniqueChain=uniqueChain, size_tree=size_tree, biggest_is=biggest_is, use_frequent_as_seed=use_frequent_as_seed, verbose=verbose, signature_threshold=signature_threshold)
        for t,collect in enumerate(collections):
            if write_graphml:
                possibilities[t][1].write_graphml(os.path.join(path_base, "tree_"+str(t)+".graphml"))
    else:
        possibilities, collections = compare_signatures(sign_r, graph_no_coil_reference, structure_reference, sign_t, graph_no_coil_target, structure_target, write_pdbs=False, search_in_both=True, renumber=False, uniqueChain=False, size_tree=size_tree, biggest_is=biggest_is, use_frequent_as_seed=use_frequent_as_seed, verbose=verbose,signature_threshold=signature_threshold)

        cont_pdb = 0

        for t,collect in enumerate(collections):
            grafus = possibilities[t][1]
            print("NUMBER OF SOLUTIUONS IN COLLECTION",t,"IS",len(collect))
            collect = sorted(collect, key=lambda p: p[8], reverse=True)
            for s, (pdb1, pdb2, ng1, ng2, names1, names2, scores, score_shape, totsco, values) in enumerate(collect):
                #ng1 = tuple(sorted(set([s for w in possibility.keys() for s in w.split("-")])))
                #ng2 = tuple(sorted(set([s for w in possibility.values() for s in w.split("-")])))
                firma = json.dumps(sorted(names1+names2))
                grafus.vs.find(name=firma)["name"] = "c"+str(cont_pdb)

                restrictions = {tuple(sorted(n1.split("-"))):tuple(sorted(n2.split("-"))) for n1,n2 in sorted(zip(names1,names2), key=lambda x: possibilities[t][2][x][0], reverse=True)[:2]}
                map_secstr_1 = {tuple(res):frag["name"] for frag in graph_no_coil_reference.vs for res in frag["reslist"] if frag["name"] in ng1}
                map_secstr_2 = {tuple(res):frag["name"] for frag in graph_no_coil_target.vs for res in frag["reslist"] if frag["name"] in ng2}
                print("NAME1",names1)
                print("NAME2",names2)
                print("SCORES",scores,sum(scores)/len(scores),score_shape,totsco)
                print("PAIRS",values)
                print()

                # g1 = graph_no_coil_reference.vs.select(name_in=ng1).subgraph()
                # g2 = graph_no_coil_target.vs.select(name_in=ng2).subgraph()
                # pdb1 = get_pdb_string_from_graph(g1, structure_reference, chainid="A", renumber=False, uniqueChain=False)
                # pdb2 = get_pdb_string_from_graph(g2, structure_target, chainid="B", renumber=False, uniqueChain=False)

                dictio_super = perform_superposition(reference=(io.StringIO(SystemUtility.py2_3_unicode(pdb1)),structure_reference,graph_no_coil_reference.vs.select(name_in=ng1).subgraph(),matrix_reference,cvs_reference),
                                                      target=(io.StringIO(SystemUtility.py2_3_unicode(pdb2)),structure_target,graph_no_coil_target.vs.select(name_in=ng2).subgraph(),matrix_target,cvs_target),
                                                      sensitivity_ah=0.000001,
                                                      sensitivity_bs=0.000001,
                                                      peptide_length=peptide_length,
                                                      write_graphml=False, write_pdb=False, ncycles=ncycles,
                                                      deep=deep, top=top, max_sec=1, break_sec=100, min_correct=2,
                                                      gui=None, sampling=sampling,
                                                      core_percentage=core_percentage,
                                                      criterium_selection_core=criterium_selection_core,
                                                      force_core_expansion_through_secstr=force_core_expansion_through_secstr,
                                                      restrictions_edges=restrictions, map_reference=map_secstr_1, map_target=map_secstr_2, verbose=False)

                if dictio_super and dictio_super["rmsd"] <= rmsd_max:
                     name = os.path.join(path_base, "comparison_" + str(cont_pdb) + ".pdb")
                     pdacc = dictio_super["pdb_target"]
                     grafus.vs.find(name="c"+str(cont_pdb))["pdb1"] = pdb1
                     grafus.vs.find(name="c"+str(cont_pdb))["pdb2"] = pdacc
                     print("Fold comparison stored in: ",name,"rmsd:",dictio_super["rmsd"], dictio_super["size"])
                     with open(name, "w") as f:
                         f.write(pdb1)
                         f.write(pdacc)
                     cont_pdb += 1
                else:
                    grafus.vs.find(name="c"+str(cont_pdb))["pdb1"] = None
                    grafus.vs.find(name="c"+str(cont_pdb))["pdb2"] = None
                    name = os.path.join(path_base, "wrong_" + str(cont_pdb) + ".pdb")
                    print("Fold comparison stored in: ", name)
                    with open(name, "w") as f:
                        f.write(pdb1)
                        f.write(pdb2)
                    cont_pdb += 1

            for edge in grafus.es:
                pdb1_a = grafus.vs[edge.source]["pdb1"]
                pdb2_a = grafus.vs[edge.source]["pdb2"]
                pdb1_b = grafus.vs[edge.target]["pdb1"]
                pdb2_b = grafus.vs[edge.target]["pdb2"]

                if pdb1_a is None or pdb2_a is None or pdb1_b is None or pdb2_b is None:
                    edge["weight"] = -100
                    continue

                list_CA2a = [residue['CA'] for residue in Bio.PDB.Selection.unfold_entities(Bioinformatics3.get_structure("2a",io.StringIO(SystemUtility.py2_3_unicode(pdb2_a))), 'R') if residue.has_id("CA") and residue.get_id() in [res[3] for frag in graph_no_coil_target.vs.select(name_in=edge["common"][1]) for res in frag["reslist"]]]
                list_CA2b = [residue['CA'] for residue in Bio.PDB.Selection.unfold_entities(Bioinformatics3.get_structure("2b",io.StringIO(SystemUtility.py2_3_unicode(pdb2_b))), 'R') if residue.has_id("CA") and residue.get_id() in [res[3] for frag in graph_no_coil_target.vs.select(name_in=edge["common"][1]) for res in frag["reslist"]]]

                pd1 = Bioinformatics3.get_pdb_from_list_of_atoms(list_CA2a, renumber=False, uniqueChain=True, chainId="A", chainFragment=False, diffchain=None, polyala=False, maintainCys=False, normalize=False, sort_reference=True)[0]
                pd2 = Bioinformatics3.get_pdb_from_list_of_atoms(list_CA2b, renumber=False, uniqueChain=True, chainId="B", chainFragment=False, diffchain=None, polyala=False, maintainCys=False, normalize=False, sort_reference=True)[0]

                with open(os.path.join(path_base, "common_"+str(grafus.vs[edge.source]["name"])+"_"+str(grafus.vs[edge.target]["name"])+".pdb"), "w") as fon:
                    fon.write(pd1+"\n"+pd2)

                dictio = Bioinformatics3.get_CA_distance_dictionary(list_CA2a, list_CA2b, max_rmsd=200, last_rmsd=200,
                                                                recompute_rmsd=False, cycles=1, cycle=1,
                                                                before_apply=None, get_superposed_atoms=False)

                rmsd_b = numpy.sqrt(sum([e[0]**2 for e in dictio.values()])/len(dictio.keys()))

                edge["weight"] = rmsd_b if rmsd_b > 0 else -1

            grafus.vs["pdb1"] = ["" for aa in range(grafus.vcount())]
            grafus.vs["pdb2"] = ["" for aa in range(grafus.vcount())]

            grafus.write_graphml(os.path.join(path_base, "tree_"+str(t)+".graphml"))

    return graph_no_coil_reference, matrix_reference, cvs_reference, structure_reference, graph_no_coil_target, matrix_target, cvs_target, structure_target, sign_r, sign_t, possibilities, collections

def annotate_pdb_model_with_aleph(pdb_model, weight="distance_avg", min_ah=4, min_bs=3, write_pdb=True,
                                  min_diff_ah=0.45, min_diff_bs=0.20, peptide_length=3, is_model=False, only_reformat=True, path_base="./"):
    strucc,cvs_list = parse_pdb_and_generate_cvs(pdb_model, peptide_length=peptide_length, one_model_per_nmr=True, only_reformat=only_reformat)
    return generate_matrix_and_graph(strucc, cvs_list, pdb_model, weight=weight, min_ah=min_ah, min_bs=min_bs, write_pdb=write_pdb,
                              min_diff_ah=min_diff_ah, min_diff_bs=min_diff_bs, is_model=is_model, mixed_chains=True,path_base=path_base)

def parse_pdb_and_generate_cvs(pdbmodel, peptide_length=3, one_model_per_nmr=True, only_reformat=True):
    strucc = Bioinformatics3.get_structure("stru", pdbmodel)
    cvs_global, sep_chains = get_cvs(strucc, length_fragment=peptide_length, one_model_per_nmr=one_model_per_nmr)
    cvs_list = format_and_remove_redundance(cvs_global, sep_chains, only_reformat=only_reformat)

    return strucc,cvs_list

@SystemUtility.timing
def generate_matrix_and_graph(strucc, cvs_list, pdb_model, weight="distance_avg", min_ah=4, min_bs=3, write_pdb=True,
                              min_diff_ah=0.45, min_diff_bs=0.20, is_model=False, mixed_chains=True,
                              maximum_distance=None, maximum_distance_bs=None, just_diagonal_plus_one=False, path_base="./"):
    """
    NOTE CM: this documentation does not correspond with the parameters

    Annotates a protein pdb file with CVs and builds a graph in which each node is a secondary structure element
    or a coil fragment and the edge connecting two nodes is the metric distance between these fragments.
    
    :param pdb_model: The pdb file to annotate
    :type pdb_model: io.TextIOWrapper
    :param weight: The weight scheme for computing edge parameters. ["distance_avg","distance_min","distance_max"]
    :type weight: str
    :param min_ah: Minimum number of residues for an alpha helix to be accepted
    :type min_ah: int
    :param min_bs: Minimum number of residues for a beta strand to be accepted
    :type min_bs: int
    :param write_pdb: Write an annotated pdb file
    :type write_pdb: bool
    :param min_diff_ah: Sensitivity parameter threshold for accepting ah CVs
    :type min_diff_ah: float
    :param min_diff_bs: Sensitivity parameter threshold for accepting bs CVs
    :type min_diff_bs: float
    :param peptide_length: Define the peptide length for computing a CV
    :type peptide_length: int
    :return (g,strucc): The graph and the structure object representing the annotated pdb model
    :rtype (g,strucc): (igraph.Graph,Bio.PDB.Structure)
    """

    matrix, cvs_list, highd = get_3d_cvs_matrix(cvs_list, is_model, mixed_chains=mixed_chains,
                                                maximum_distance=maximum_distance,
                                                maximum_distance_bs=maximum_distance_bs,
                                                just_diagonal_plus_one=just_diagonal_plus_one)

    g = aleph_secstr(strucc, cvs_list, matrix, min_ah=min_ah, min_bs=min_bs, min_diff_ah=min_diff_ah, min_diff_bs=min_diff_bs)
    resil = [tuple(resi[1:4]) for frag in g.vs for resi in frag["reslist"]]
    toadd = []
    for r in Bioinformatics3.get_list_of_residues(strucc):
        if tuple(r.get_full_id()[1:4]) not in resil and r.get_resname() in Bioinformatics3.AADICMAP:
            toadd.append({"reslist":[r.get_full_id()], "sstype":"coil", "resIdList":[r.get_full_id()], "cvids":[], "cvls":[], "sequence":"".join([Bioinformatics3.AADICMAP[r.get_resname()]])})
    s = igraph.Graph.Full(g.vcount()+len(toadd))
    i = 0
    for i, fr in enumerate(g.vs):
        for m in fr.attributes().keys():
            s.vs[i][m] = fr[m]
    i = g.vcount()
    for fr in toadd:
        s.vs[i]["reslist"] = fr["reslist"]
        s.vs[i]["sstype"] = fr["sstype"]
        s.vs[i]["resIdList"] = fr["resIdList"]
        s.vs[i]["cvids"] = fr["cvids"]
        s.vs[i]["cvls"] = fr["cvls"]
        s.vs[i]["sequence"] = fr["sequence"]
        #s.vs[i]["resforgraph"] = fr["resforgraph"]
        i += 1
    g = s

    g.vs["sheet"] = [None for _ in g.vs]

    g = aleph_internal_terstr(strucc, g, matrix, cvs_list)
    g = aleph_terstr(strucc, g, matrix, cvs_list, weight=weight)

    listar = [tuple(res[:-1]) for frag in g.vs for res in frag["reslist"] if frag["sstype"] in ["ah", "bs"]]

    pdbsearchin = ""

    for frag in g.vs:
        if frag["sstype"] == "ah":
            pdbsearchin += Bioinformatics3.get_helix_line(frag.index, "H",
                                                          Bioinformatics3.ATOAAAMAP[frag["sequence"][0]],
                                                          frag["reslist"][0][2], frag["reslist"][0][3][1],
                                                          frag["reslist"][0][3][2],
                                                          Bioinformatics3.ATOAAAMAP[frag["sequence"][-1]],
                                                          frag["reslist"][-1][2], frag["reslist"][-1][3][1],
                                                          frag["reslist"][-1][3][2], 1, "", len(frag["sequence"]))
        elif frag["sstype"] == "bs":
            pdbsearchin += Bioinformatics3.get_sheet_line(frag.index, "B", 1,
                                                          Bioinformatics3.ATOAAAMAP[frag["sequence"][0]],
                                                          frag["reslist"][0][2], frag["reslist"][0][3][1],
                                                          frag["reslist"][0][3][2],
                                                          Bioinformatics3.ATOAAAMAP[frag["sequence"][-1]],
                                                          frag["reslist"][-1][2], frag["reslist"][-1][3][1],
                                                          frag["reslist"][-1][3][2], 0)

    # print pdbsearchin
    for model in strucc.get_list():
        reference = [atm for atm in Bio.PDB.Selection.unfold_entities(strucc[model.get_id()], "A") if
                     (len(listar) == 0 or atm.get_parent().get_full_id() in listar)]
        pdbmod, cnv = Bioinformatics3.get_pdb_from_list_of_atoms(reference, renumber=False, uniqueChain=False)
        pdbsearchin += pdbmod

    if write_pdb:
        fds = open(os.path.join(path_base, os.path.basename(pdb_model)[:-4] + "_input_search.pdb"), "w")
        fds.write(pdbsearchin)
        fds.close()

    #toadd = []

    return g, strucc, matrix, cvs_list, highd

def sampling_filtering(graph, sampling):
    algo_sampling = {'none', 'random', 'first_middle_last', 'first_middle_last_enhanced','1every2', '1every3', '1every4', '1every5'}

    if sampling == 'none':
        return graph
    elif sampling == 'random':
        p = numpy.random.randint(0, graph.ecount() - 1, 100)
        return graph.es.select(lambda e: e.index in p or (graph.vs[e.source]["isSpecial"] and graph.vs[e.target]["isSpecial"])).subgraph()
    elif sampling == 'first_middle_last':
        return graph.vs.select(lambda v: v["isStart"] or v["isMiddle"] or v["isEnd"]).subgraph()
    elif sampling == 'first_middle_last_enhanced':
        return graph.vs.select(lambda v: v["isStart"] or v["isMiddle"] or v["isEnd"] or (v.index+1 < graph.vcount() and graph.vs[v.index+1]["isSpecial"]) or (v.index-1 >= 0 and graph.vs[v.index-1]["isSpecial"])).subgraph()
    elif sampling == '1every2':
        p = range(0, graph.vcount(), 2)
        return graph.vs.select(lambda v: v.index in p or v["isSpecial"]).subgraph()
    elif sampling == '1every3':
        p = range(0, graph.vcount(), 3)
        return graph.vs.select(lambda v: v.index in p or v["isSpecial"]).subgraph()
    elif sampling == '1every4':
        p = range(0, graph.vcount(), 4)
        return graph.vs.select(lambda v: v.index in p or v["isSpecial"]).subgraph()
    elif sampling == '1every5':
        p = range(0, graph.vcount(), 5)
        return graph.vs.select(lambda v: v.index in p or v["isSpecial"]).subgraph()
    else:
        return graph


def get_dictionary_from_community_clusters(graph, vclust, structure, writePDB=False, outputpath=None, header="",
                                           returnPDB=False, adding_t=0):
    global list_ids

    dict_res = {}
    pdbsearchin = ""
    if (writePDB and outputpath is not None) or returnPDB:
        pdbsearchin = header + "\n"

    for t, clust in enumerate(vclust):  # for every group in the community clustered graph
        listar = []
        for vertex in graph.vs:  # for every secondary structure element (vertex) in the clustered graph
            if vertex.index in clust:
                listar += [tuple(res[:-1]) for res in vertex["reslist"]]

        for model in structure.get_list():
            reference = []
            for chain in model.get_list():
                for residue in chain.get_list():
                    if len(listar) == 0 or residue.get_full_id() in listar:
                        reference += residue.get_unpacked_list()
                        dict_res[residue.get_full_id()] = 'group' + str(t + adding_t)
            if (writePDB and outputpath is not None) or returnPDB:
                pdbmod, cnv = Bioinformatics3.get_pdb_from_list_of_atoms(reference, renumber=True, uniqueChain=True,
                                                                         chainId=list_ids[t + adding_t])
                pdbsearchin += pdbmod

        if writePDB and outputpath is not None:
            fds = open(outputpath, "w")
            fds.write(pdbsearchin)
            fds.close()

    if not returnPDB:
        return dict_res
    else:
        return dict_res, pdbsearchin

def get_distance_filtered_graph(graph, bottom_distance=0, top_distance=20, type_distance="avg"):
    if type_distance == "min":
        p = (graph.es.select(min_le=top_distance).subgraph()).es.select(min_ge=bottom_distance).subgraph()
    elif type_distance == "avg":
        p = (graph.es.select(avg_le=top_distance).subgraph()).es.select(avg_ge=bottom_distance).subgraph()
    elif type_distance == "weight":
        p = (graph.es.select(weight_le=top_distance).subgraph()).es.select(weight_ge=bottom_distance).subgraph()
    elif type_distance == "distance":
        p = (graph.es.select(distance_le=top_distance).subgraph()).es.select(distance_ge=bottom_distance).subgraph()
    elif type_distance == "fragdistance":
        p = (graph.es.select(fragdistance_le=top_distance).subgraph()).es.select(
            fragdistance_ge=bottom_distance).subgraph()
    return p


def get_community_clusters(graph, algorithm="fastgreedy", n=None, print_dendo=None, return_dendo=False, weight="weight"):
    vdendo = None
    if algorithm.lower() == "fastgreedy":
        vdendo = graph.community_fastgreedy(weights=weight)
        try:
            vclust = vdendo.as_clustering(n=n)
        except:
            vclust = None

        if print_dendo is not None:
            try:
                igraph.drawing.plot(vdendo, target=print_dendo, bbox=(0, 0, 800, 800))
            except:
                try:
                    igraph.drawing.plot(vdendo, target=print_dendo[:-4] + ".svg", bbox=(0, 0, 800, 800))
                except:
                    pass
    elif algorithm.lower() == "infomap":
        vclust = graph.community_infomap(edge_weights=weight)
    elif algorithm.lower() == "eigenvectors":
        vclust = graph.community_leading_eigenvector(weights=weight)
    elif algorithm.lower() == "label_propagation":
        vclust = graph.community_label_propagation(weights=weight)
    elif algorithm.lower() == "community_multilevel":
        vclust = graph.community_multilevel(weights=weight, return_levels=False)
    elif algorithm.lower() == "edge_betweenness":
        vdendo = graph.community_edge_betweenness(directed=False, weights=weight)
        try:
            vclust = vdendo.as_clustering(n=n)
        except:
            vclust = None

        if print_dendo is not None:
            try:
                igraph.drawing.plot(vdendo, target=print_dendo, bbox=(0, 0, 800, 800))
            except:
                try:
                    igraph.drawing.plot(vdendo, target=print_dendo[:-4] + ".svg", bbox=(0, 0, 800, 800))
                except:
                    pass
    elif algorithm.lower() == "spinglass":
        vclust = graph.community_spinglass(weights=weight)
    elif algorithm.lower() == "walktrap":
        vdendo = graph.community_walktrap(weights=weight)
        if print_dendo is not None:
            try:
                igraph.drawing.plot(vdendo, target=print_dendo, bbox=(0, 0, 800, 800))
            except:
                try:
                    igraph.drawing.plot(vdendo, target=print_dendo[:-4] + ".svg", bbox=(0, 0, 800, 800))
                except:
                    pass
        try:
            vclust = vdendo.as_clustering(n=n)
        except:
            vclust = None
    else:
        vclust = None
    if not return_dendo:
        return vclust
    else:
        return vclust, vdendo


def pack_beta(vclust,graph,pack_beta_sheet):
    if not pack_beta_sheet:
        return vclust

    y = vclust.subgraphs()
    while 1:
        merge = False
        indexes = []
        r = None
        for i, clu1 in enumerate(y):
            for j, clu2 in enumerate(y):
                if j > i:
                    # print([t["sstype"] for t in clu1.vs],[t["sstype"] for t in clu2.vs])
                    # print([t["sstype"]=="bs" for t in clu1.vs],[t["sstype"]=="bs" for t in clu2.vs],[s["mean"] for s in sorted(graph.es.select(lambda x: (graph.vs[x.source]["name"] in clu1.vs["name"] and graph.vs[x.target]["name"] in clu2.vs["name"]) or (graph.vs[x.source]["name"] in clu2.vs["name"] and graph.vs[x.target]["name"] in clu1.vs["name"])), key=lambda e: e["avg"])])
                    # print([(t["sequence"],t["reslist"][0][2]) for t in clu1.vs],[(t["sequence"],t["reslist"][0][2]) for t in clu2.vs])
                    if all([t["sstype"] == "bs" for t in clu1.vs]) and all([t["sstype"] == "bs" for t in clu2.vs]):
                        if len(set(clu1.vs["sheet"])&set(clu2.vs["sheet"]))==1:
                            r = graph.vs.select(name_in=clu1.vs["name"] + clu2.vs["name"]).subgraph()
                            merge = True
                            indexes.append(i)
                            indexes.append(j)
                            break
            if merge:
                break
        if merge:
            # print("merging",indexes)
            z = [q for p, q in enumerate(y) if p not in indexes] + [r]
            y = z
        else:
            break

    # ul = []
    # for o in graph.vs["name"]:
    #     for l, p in enumerate(y):
    #         if o["name"] in p.vs["name"]:
    #             ul.append(l)
    #             break

    ul = [l for o in graph.vs["name"] for l, p in enumerate(y) if o in p.vs["name"]]

    # print(graph.vcount())
    # print(ul)
    vclust = igraph.VertexClustering(graph, membership=ul)
    return vclust


def get_community_clusters_one_step(algo, graph_input_d, structure, pdb_search_in, pathpdb, n=None, print_dendo=None,
                                    return_dendo=False, use_dendo=None, use_spantree=True, write_pdb=True,
                                    weight="weight", pack_beta_sheet=False, homogeneity=False):

    # for u in sorted(graph_input.es["weight"],reverse=True):
    #     print("before",u)
    # print()
    graph_input = graph_input_d.copy()
    graph_input = graph_input.vs.select(sstype_in=["ah", "bs"]).subgraph()
    graph_input.vs["name"] = [str(vertex["reslist"][0][3][1]) + "_" + str(vertex["reslist"][0][2]) for vertex in graph_input.vs]


    if pack_beta_sheet:
        graph_input.es["weight"] = [100*(100.0/e["avg"]) if graph_input.vs[e.source]["sstype"] == graph_input.vs[e.target]["sstype"] else e["weight"] for e in graph_input.es]
        graph_input.es["spantree_weight"] = [e["avg"]/100.0 if graph_input.vs[e.source]["sstype"] == graph_input.vs[e.target]["sstype"] else e["spantree_weight"] for e in graph_input.es]


    if use_spantree:
        graph = graph_input.spanning_tree(weights="spantree_weight")
    else:
        graph = graph_input
    # graph.write_graphml(os.path.join("./", os.path.basename(pathpdb)[:-4] + "_spantree.graphml"))
    # for u in sorted(graph.es["weight"],reverse=True):
    #     print("after",u)
    # print()

    if not homogeneity:
        if not return_dendo and use_dendo is None:
            vclust = get_community_clusters(graph, algorithm=algo, n=n, print_dendo=print_dendo, return_dendo=return_dendo,  weight=weight)
        elif not return_dendo:
            vclust = use_dendo.as_clustering(n=n)
        else:
            vclust, vdendo = get_community_clusters(graph, algorithm=algo, n=n, print_dendo=print_dendo,
                                                    return_dendo=return_dendo, weight=weight)
    else:
        return_dendo = True
        vclust, vdendo = get_community_clusters(graph, algorithm=algo, n=n, print_dendo=print_dendo, return_dendo=return_dendo, weight=weight)
        l = [pack_beta(vdendo.as_clustering(n=i),graph,pack_beta_sheet) for i in range(1,graph.vcount())]
        best_i = None
        best_score = -1.0
        for w,cluster in enumerate(l):
            q=tuple([tuple([t["sstype"] for t in c.vs]) for c in cluster.subgraphs()])
            if not pack_beta_sheet:
                sample = [c.vcount() for c in cluster.subgraphs()]
            else:
                sample = [c.vcount() for c in cluster.subgraphs() if len(set(tuple(c.vs["sstype"])))==1 and c.vs["sstype"][0]=="ah"]

            if len(sample) == 1 or (len(sample) == 0 and pack_beta_sheet):
                uq = 0.0
                CV = 0.0
                normCV = 0.1
            elif len(sample) == 0:
                print("Error!!!!, Clustering has not grouped anything?")
                sys.exit(1)
            else:
                uq = numpy.mean(sample)
                sq = numpy.std(sample)
                CV = sq / uq
                normCV = (((CV - 0) * (1 - 0)) / (numpy.sqrt(len(sample) - 1) - 0)) + 0

            n = graph.vcount()
            # (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin

            corrected_score = cluster.modularity+(uq/n)-(normCV) #cluster.modularity*uq*(len(q)-len(set(q)))
            if  corrected_score > best_score:
                best_i = w
                best_score = corrected_score
            #print(w,cluster.modularity,q,len(q))
            #print(w,cluster.modularity,set(q),len(set(q)))
            #print(w,cluster.modularity,uq/n,normCV,corrected_score)

        if best_i is None:
            return None

        print("Best cut",best_i+1,"modularity",best_score)
        vclust = l[best_i]

    if pack_beta_sheet:
        vclust = pack_beta(vclust,graph,pack_beta_sheet)

    if write_pdb:
        get_dictionary_from_community_clusters(graph, vclust, structure, writePDB=True, outputpath=os.path.join("./",
                                                                                                                os.path.basename(
                                                                                                                    pathpdb)[
                                                                                                                :-4] + "_" + algo + "_distclust.pdb"),
                                               header=pdb_search_in)
    layout = graph.layout("kk")
    try:
        write_image_from_graph(vclust,
                               os.path.join("./", os.path.basename(pathpdb)[:-4] + "_" + algo + "_clustering.png"))
    except:
        # vclust.write_graphml(os.path.join("./", os.path.basename(pathpdb)[:-4] + "_clustering.graphml"))
        pass

    if return_dendo:
        return vclust, vdendo
    else:
        return vclust


def get_community_clusters_two_step(graph, structure, pdb_search_in, pathpdb, sort_mode, min_bs, max_bs,
                                    writePDBandPNG=True, weight="weight"):
    """ Performs two step community clustering in order to group betas in the first place and then the rest of the structure.

    Args:
        graph (igraph object) --
        structure (BioPython structure object) --
        pdb_search_in (str) --
        pathpdb (str) --
        sort_mode (str) -- 'avg','min'
        min_bs (int) --
        max_bs (int) --
        writePDBandPNG (boolean) --


    Returns:
        dict_res1 (dict) --

    """
    graph_no_helices = graph.vs.select(sstype="bs").subgraph()
    #graph_no_helices = get_distance_filtered_graph(graph_no_helices, bottom_distance=min_bs, top_distance=max_bs, type_distance=sort_mode)

    if writePDBandPNG:
        try:
            write_image_from_graph(graph_no_helices,os.path.join("./", os.path.basename(pathpdb)[:-4] + "_clustering.png"))
        except:
            graph_no_helices.write_graphml(os.path.join("./", os.path.basename(pathpdb)[:-4] + "_clustering.graphml"))

    graph_no_strands = graph.vs.select(sstype="ah").subgraph()
    try:
        vclust_bs = get_community_clusters(graph_no_helices, algorithm="fastgreedy", weight=weight)
        dict_res1, pdb1 = get_dictionary_from_community_clusters(graph_no_helices, vclust_bs, structure, writePDB=False,
                                                                 returnPDB=True, adding_t=0, header=pdb_search_in)
        if graph_no_strands.vcount() > 0:
            vclust_ah = get_community_clusters(graph_no_strands, algorithm="fastgreedy", weight=weight)
            dict_res2, pdb2 = get_dictionary_from_community_clusters(graph_no_strands, vclust_ah, structure,
                                                                     writePDB=False, returnPDB=True,
                                                                     adding_t=len(vclust_bs))
            dict_res1.update(dict_res2)
        else:
            pdb2 = ""
        # print pdb1
        # print "======================"
        # print pdb2
        if writePDBandPNG:
            f = open(os.path.join("./", os.path.basename(pathpdb)[:-4] + "_distclust.pdb"), "w")
            f.write(pdb1)
            f.write(pdb2)
            f.close()
    except:
        print("ATTENTION: It was impossible to annotate input structure with the community clustering two steps algorithm")
        print(min_bs, max_bs)
        print(sys.exc_info())
        traceback.print_exc(file=sys.stdout)

    return dict_res1

@SystemUtility.timing
def generate_graph_for_cvs(pdb_model, structure, graph_full, matrix, cvs_list, peptide_length=3):
    # tuplone = Bioinformatics.getFragmentListFromPDBUsingAllAtoms(pdb_model, False)
    # strucc = tuplone[0]

    if isinstance(cvs_list[0][0], list):
        cvs_list = [lis for l in cvs_list for lis in l]

    sstype_map = {"ah": 1, "bs": 2, "coil": 3}

    g = igraph.Graph()
    g.add_vertices(len(cvs_list))

    for z, cvs in enumerate(cvs_list):
        g.vs[z]["secstr"] = None
        for p, frag in enumerate(graph_full.vs):
            a = tuple(tuple(x) for x in cvs[4])
            b = tuple(tuple(x) for x in frag["reslist"])
            if set(a).issubset(b):
                g.vs[z]["secstr"] = p
                ul = get_vseq_neighbours_fragments(graph_full, frag, sortmode="avg")
                if len(ul) > 0:
                    g.vs[z]["nearsecstr"] = ul[0].index
                else:
                    g.vs[z]["nearsecstr"] = None
                #g.vs[z]["com"] = frag["com"]
                g.vs[z]["unique_cv"] = frag["unique_cv"]
                g.vs[z]["cvs"] = z
                g.vs[z]["-1"] = z - 1 if (z - 1 > 0 and g.vs[z - 1]["secstr"] == p) else None
                g.vs[z]["+1"] = None
                if (z - 1 > 0 and g.vs[z - 1]["secstr"] == p):
                    g.vs[z - 1]["+1"] = z

                g.vs[z]["reslist"] = cvs[4]
                g.vs[z]["sstype"] = frag["sstype"]
                g.vs[z]["sequence"] = "".join(map(lambda x: Bioinformatics3.AADICMAP[x[4]], cvs[4]))
                g.vs[z]["sequence_secstr"] = frag["sequence"]
                g.vs[z]["isStart"] = True if g.vs[z]["reslist"] == frag["reslist"][:peptide_length] else False
                g.vs[z]["isMiddle"] = True if g.vs[z]["reslist"] == frag["reslist"][int(len(frag["reslist"]) / 2):int(
                    len(frag["reslist"]) / 2) + peptide_length] else False
                g.vs[z]["isEnd"] = True if g.vs[z]["reslist"] == frag["reslist"][
                                                                 len(frag["reslist"]) - peptide_length:] else False
                g.vs[z]["isSpecial"] = True if g.vs[z]["isStart"] or g.vs[z]["isMiddle"] or g.vs[z]["isEnd"] else False
                g.vs[z]["posandsec"] = ((frag["reslist"].index(g.vs[z]["reslist"][0]) + 1) * 100) + p
                g.vs[z]["pos"] = (frag["reslist"].index(g.vs[z]["reslist"][0]) + 1)
                break

    g = g.vs.select(lambda vertex: vertex["secstr"] is not None).subgraph()

    for frag1 in g.vs:
        for frag2 in g.vs.select(lambda vertex: vertex.index > frag1.index):
            g.add_edge(frag1.index, frag2.index)
            value1 = matrix[(frag1["cvs"], frag2["cvs"])]
            value2 = compute_instruction(frag1["unique_cv"], frag2["unique_cv"], unique_fragment_cv=True)
            z = [value1[2], value1[3], value1[4], sstype_map[frag1["sstype"]], sstype_map[frag2["sstype"]]]
            r = [value2[2], value2[3], value2[4]]
            w = [compute_instruction(cvs_list[frag1["cvs"]],frag2["unique_cv"])[3], compute_instruction(cvs_list[frag2["cvs"]],frag1["unique_cv"])[3]]
            g.es[g.get_eid(frag1.index, frag2.index)]["weight"] = 100.0 / value1[3]
            g.es[g.get_eid(frag1.index, frag2.index)]["metric"] = z+r+w+[len(set([frag1["secstr"], frag2["secstr"]]))]#+[frag1["pos"], frag2["pos"]]
            #g.es[g.get_eid(frag1.index, frag2.index)]["plane_equation"] = numpy.array(list(get_plane_from_3_points_2(cvs_list[frag1["cvs"]][2],cvs_list[frag1["cvs"]][3],cvs_list[frag2["cvs"]][2])[:3]))
            g.es[g.get_eid(frag1.index, frag2.index)]["distance"] = value1[3]

    # for frag1 in g.vs:
    #     for frag2 in g.vs.select(lambda vertex: vertex.index > frag1.index):
    #         g.es[g.get_eid(frag1.index, frag2.index)]["metric"] += [g.es.select(lambda x: x["distance"] >=5.0 <)]
    g.vs["name"] = [str(vertex.index) + "_" + str(vertex["reslist"][0][2]) for vertex in g.vs]

    return g


def generate_cage_graph(reference, structure_reference, graph_no_coil_reference, matrix_reference, cvs_reference,
                        pep_len, sampling, restrictions_edges=None, map_reference=None, gui=None):
    codecs = {}
    if restrictions_edges:
        graph_no_coil_reference = graph_no_coil_reference.vs.select(name_in=set(map_reference.values())).subgraph()
        #bigs = sorted([q.index for q in graph_no_coil_reference.vs], key=lambda x: len(graph_no_coil_reference.vs[x]["reslist"]), reverse=True)[:2]
        #graph_no_coil_reference = graph_no_coil_reference.vs.select(lambda c: c.index in bigs).subgraph()
        for frag in graph_no_coil_reference.vs:
            # for resi in frag["reslist"]:
            #     print(resi,map_reference[tuple(resi)])
            alls = list(set([map_reference[tuple(resi)] for resi in frag["reslist"]]))
            if len(alls) == 1:
                codecs[frag.index] = alls[0]
            else:
                print("NOT EVENLY DISTRIBUTED",alls)
                quit()

    #print("CODECS",codecs)

    graph_ref = generate_graph_for_cvs(reference, structure_reference, graph_no_coil_reference, matrix_reference,
                                       cvs_reference, peptide_length=pep_len)
    #print(reference,graph_ref.vs["secstr"])
    #print("====================")
    cage_ref = graph_ref.es.select(
        lambda e: graph_ref.vs[e.source]["secstr"] != graph_ref.vs[e.target]["secstr"]).subgraph()
    #print(reference,cage_ref.vs["secstr"])

    cage_ref = sampling_filtering(cage_ref, sampling)

    if gui is not None:
        gui.draw_graph(cage_ref, "cage_reference", where="bottom-right", scale=0.1)

    #print(reference,cage_ref.vcount(),cage_ref.ecount(),graph_ref.vcount(),graph_ref.ecount())
    #print(cage_ref.es["weight"])
    try:
        eigen = cage_ref.evcent(directed=False, scale=True, weights=cage_ref.es["weight"], return_eigenvalue=True)
        cage_ref.vs["eigen"] = eigen[0]
    except:
        pass

    cage_ref.vs["Label"] = [d["sstype"] + "_" + d["name"] for t, d in enumerate(cage_ref.vs)]

    #print("SHERLOCK: LEN METRIC",len(cage_ref.es["metric"]),cage_ref.vcount(),cage_ref.ecount())
    if not restrictions_edges or len(restrictions_edges) == 0:
        return cage_ref, {}
    else:
        cage_ref = cage_ref.es.select(lambda e: tuple(sorted([codecs[cage_ref.vs[e.source]["secstr"]], codecs[cage_ref.vs[e.target]["secstr"]]])) in restrictions_edges).subgraph()
        # for e in cage_ref.es:
        #     print(cage_ref.vs[e.source]["reslist"])
        #     print(cage_ref.vs[e.target]["reslist"])
        #     print(map_reference)
        #     print(map_reference[tuple(cage_ref.vs[e.source]["reslist"][0])])
        #     print(map_reference[tuple(cage_ref.vs[e.target]["reslist"][0])])
        #
        # print()
        # for e in cage_ref.es:
        #      s = tuple(sorted([map_reference[tuple(cage_ref.vs[e.source]["reslist"][0])], map_reference[tuple(cage_ref.vs[e.target]["reslist"][0])]]))
        #      print("HERE",s, s in restrictions_edges)

        direl = {tuple(sorted([codecs[cage_ref.vs[e.source]["secstr"]], codecs[cage_ref.vs[e.target]["secstr"]]])):tuple(sorted([cage_ref.vs[e.source]["secstr"],cage_ref.vs[e.target]["secstr"]])) for e in cage_ref.es}
        #print("DIREL",direl)
        #for e in cage_ref.es:
        #    print(tuple(sorted([map_reference[tuple(cage_ref.vs[e.source]["reslist"][0])], map_reference[tuple(cage_ref.vs[e.target]["reslist"][0])]])), tuple(sorted([cage_ref.vs[e.source]["secstr"],cage_ref.vs[e.target]["secstr"]])))
        #print("SHERLOCK: LEN METRIC 222222", len(cage_ref.es["metric"]))

        return cage_ref, direl

def find_nearest_neigh_ncs(resi_one, poslist, recipient, structure):
    #print(list_neigh)
    list_neigh = [(k2, recipient[k2][-1]) for k2 in recipient.keys()]
    for li in list_neigh:
        indi,neigh = li
        #print("model",resi_one[1],neigh[1],"chains",resi_one[2],neigh[2],"resis",resi_one[3][1],neigh[3][1],"index",indi)
        res1 = Bioinformatics3.get_residue(structure, resi_one[1], resi_one[2], resi_one[3])
        res2 = Bioinformatics3.get_residue(structure, neigh[1], neigh[2], neigh[3])
        if Bioinformatics3.check_continuity(res1, res2, swap=True):
            return indi,True

    lideron = []
    list_neigh2 = [(k2, recipient[k2]) for k2 in recipient.keys()]
    for li in list_neigh2:
        indi,neighs = li
        milderon = []
        for neigh in neighs:
            #print("**",resi_one,"**",neigh)
            atom1 = Bioinformatics3.get_residue(structure, resi_one[1], resi_one[2], resi_one[3])["CA"]
            atom2 = Bioinformatics3.get_residue(structure, neigh[1], neigh[2], neigh[3])["CA"]
            d, D = get_atoms_distance(atom1.get_coord(), atom2.get_coord())
            milderon.append(d)
        lideron.append((min(milderon),indi))

    indi = sorted(lideron,key=lambda x: x[0])[0]
    #index = indi[1]-1 #in the list of list_neigh index starts from 0
    # print(indi)
    # print(resi_one)
    # print(list_neigh[index][1][1])
    # print(list_neigh[index][1][2])
    # print(list_neigh[index][1][3])
    # print(lideron)
    #print("model", resi_one[1], list_neigh[index][1][1], "chains", resi_one[2], list_neigh[index][1][2], "resis", resi_one[3][1], list_neigh[index][1][3][1], "distance,index", indi)
    return indi[1],False

@SystemUtility.timing
def elongate_and_uniform_copies(map_ncs,structure,reference):
    for ncs,listr in map_ncs.items():
        listr = sorted(listr)
    return map_ncs


def worker_for_ncs_queue(in_queue):
    global list_ncs_dictio
    can_exit = False

    while 1:
        try:
            dictio = in_queue.get(False)
        except:
            if can_exit and len(multiprocessing.active_children()) == 0:
                print("I AM DONE WITH THE QUEUE EXITING NOW...")
                in_queue.close()
                break
            else:
                time.sleep(1)
                continue

        if dictio == "ENDED":
            can_exit = True
            continue

        list_ncs_dictio.append(dictio)

def execute_ncs_search_between_two_classes(vclust,graph_no_coil_reference,reference,structure_reference, matrix_reference, cvs_reference, force_core_expansion_through_secstr, pep_len, sampling, gui, ty, trials, groupsA, groupsB, in_queue):

    # vclust = [[0, 1, 2], [5, 6, 9, 11, 13, 16, 17, 18, 19, 20, 21]]

    newstru = Bioinformatics3.get_structure("ref", os.path.join("./", os.path.basename(reference)))

    print(vclust)

    g1c = vclust[0]
    cage_g1,l1 = generate_cage_graph(reference, structure_reference, graph_no_coil_reference, matrix_reference,
                                  cvs_reference, pep_len, sampling, gui=gui)
    g1 = cage_g1 = cage_g1.vs.select(lambda v: v["secstr"] in g1c).subgraph()
    g2c = vclust[1]
    cage_g2,l2 = generate_cage_graph(reference, structure_reference, graph_no_coil_reference, matrix_reference,
                                  cvs_reference, pep_len, sampling, gui=gui)

    g2 = cage_g2 = cage_g2.vs.select(lambda v: v["secstr"] in g2c).subgraph()
    print("G1:", g1.vcount(), cage_g1.vcount(), "G2:", g2.vcount(), cage_g2.vcount())
    best_for_cycle = compute_correlation_between_graphs(reference, reference, structure_reference,
                                                        structure_reference, cage_g1,
                                                        cage_g2, reference, ncycles=10,
                                                        deep=True, top=4, max_sec=3, break_sec=200, min_correct=2,
                                                        graphs_from_same_structure=True,
                                                        force_core_expansion_through_secstr=force_core_expansion_through_secstr,
                                                        gui=gui)

    results = select_best_superposition_overall_cycles(reference, best_for_cycle, reference,
                                                       reference, cage_g1, cage_g2,
                                                       enforce_tertiary_structure=False,
                                                       write_pdb=True, gui=gui)

    if results is None or "rmsd" not in results:
        #TODO: Eliminate the ty check and exit with a simple return
        if ty < trials:
            # start = True
            # start = True
            return #continue
        else:
            return #break

    secstrA = set([cage_g1.vs.find(name=json.loads(res.strip("'\"").replace("\\", ""))[1])["secstr"] for res in
                   results["match"]] + [
                      cage_g1.vs.find(name=json.loads(res.strip("'\"").replace("\\", ""))[2])["secstr"] for res in
                      results["match"]])  # +g1c)
    secstrB = set([cage_g2.vs.find(name=json.loads(res.strip("'\"").replace("\\", ""))[1])["secstr"] for res in
                   results["explored"]] + [
                      cage_g2.vs.find(name=json.loads(res.strip("'\"").replace("\\", ""))[2])["secstr"] for res in
                      results["explored"]])
    print("SEC REFERENCE", secstrA)
    print("SEC ALREADY EXPLORED", secstrB)
    dictio = Bioinformatics3.get_CA_distance_dictionary(
        [residue['CA'] for residue in Bio.PDB.Selection.unfold_entities(newstru, 'R') if residue.has_id("CA")],
        results["ca_target"], max_rmsd=0.5, last_rmsd=1.3, recompute_rmsd=True)
    sco = results["correlation"] / len(dictio.keys()) if len(dictio.keys()) > 0 else 100
    print("LEN DICTIO", len(dictio.keys()), "Correlation", results["correlation"], "Weighted score", sco)
    if results["rmsd"] > 0.8: ####or sco > 0.006:  # or len(dictio) < 25: #results["correlation"] > 0.15:
        #TODO: Eliminate the ty check and exit with a simple return
        if ty < trials:
            # restart = True
            # start = True
            return #continue
        else:
            return #break

    # print(results["match"])
    # print([res.strip("'\"").replace("\\","") for res in results["match"]])
    # print([res.strip("'\"").replace("\\","") for res in results["explored"]])
    # secstrA = set([cage_g1.vs.find(name=json.loads(res.strip("'\"").replace("\\",""))[1])["secstr"] for res in results["match"]]+[cage_g1.vs.find(name=json.loads(res.strip("'\"").replace("\\",""))[2])["secstr"] for res in results["match"]])#+g1c)
    # secstrB = set([cage_g2.vs.find(name=json.loads(res.strip("'\"").replace("\\",""))[1])["secstr"] for res in results["explored"]]+[cage_g2.vs.find(name=json.loads(res.strip("'\"").replace("\\",""))[2])["secstr"] for res in results["explored"]])

    # for res in results["explored"]:
    #     print("explored",res)
    # for res in results["match"]:
    #     print("match", res)

    # print("SEC REFERENCE",secstrA)
    # print("SEC ALREADY EXPLORED",secstrB)
    if secstrA not in groupsA:
        groupsA += [h for h in secstrA]
    if secstrB not in groupsB and not secstrB in groupsA:
        groupsB.append(secstrB)

    dictio2 = {}
    for k in dictio:
        k2 = ('a', k[1], k[2], k[3], k[4])
        p = dictio[k][0]
        u = ('a', dictio[k][1][1], dictio[k][1][2], dictio[k][1][3], dictio[k][1][4])
        dictio2[k2] = (p, u)
        #print("-----",k2,p,u)
    dictio = dictio2
    in_queue.put(dictio)
    return

@SystemUtility.timing
def annotate_ncs(reference, ncs_fold, sensitivity_ah, sensitivity_bs, peptide_length, pack_beta_sheet,
                 max_ah_dist, min_ah_dist, max_bs_dist, min_bs_dist, write_graphml, write_pdb,
                 homogeneity, sampling, core_percentage=10, criterium_selection_core="residues", force_core_expansion_through_secstr=False, gui=False, signal=None):
    global SCALING
    global list_ncs_dictio

    # NOTE: PARAMETRIZATION=======
    # write_graphml = bool(write_graphml)
    sort_mode = "avg"

    if sensitivity_ah < 0:
        sensitivity_ah = 0.45
    if sensitivity_bs < 0:
        sensitivity_bs = 0.20
    if min_bs_dist < 0:
        min_bs_dist = 0
    if max_bs_dist < 0:
        max_bs_dist = 15
    if min_ah_dist < 0:
        min_ah_dist = 0
    if max_ah_dist < 0:
        max_ah_dist = 20

    sym = SystemUtility.SystemUtility()

    homogeneity = False
    pack_beta_sheet = False
    weight = "distance_avg"
    pep_len = int(peptide_length)

    pdb_search_in = ""
    f = open(reference, "r")
    all_lines = f.readlines()
    f.close()
    for line in all_lines:
        if line[:6] in ["TITLE ", "CRYST1", "SCALE1", "SCALE2", "SCALE3"]:
            pdb_search_in += line

    graph_full_reference, structure_reference, matrix_reference, cvs_reference, highd_reference = annotate_pdb_model_with_aleph(
        reference, weight=weight, min_diff_ah=sensitivity_ah, min_diff_bs=sensitivity_bs, peptide_length=pep_len,
        write_pdb=write_pdb)
    graph_full_reference.vs["name"] = [str(vertex["reslist"][0][3][1]) + "_" + str(vertex["reslist"][0][2]) for vertex
                                       in graph_full_reference.vs]
    graph_no_coil_reference = graph_full_reference.vs.select(sstype_in=["ah", "bs"]).subgraph()
    eigen_ref = graph_no_coil_reference.evcent(directed=False, scale=True, weights=graph_no_coil_reference.es["weight"],
                                               return_eigenvalue=True)
    # print("EIGEN Centrality values:", eigen_ref, len(eigen_ref[0]), len(graph_no_coil_reference.vs))
    graph_no_coil_reference.vs["eigen"] = eigen_ref[0]
    graph_no_coil_reference.vs["Label"] = [d["sstype"] + "_" + d["name"] for t, d in
                                           enumerate(graph_no_coil_reference.vs)]
    graph_no_coil_reference.write_graphml(
        os.path.join("./", os.path.basename(reference)[:-4] + "_graphref.graphml"))

    #TODO: I think this part is already in get_signature_graph so I need just to call it and return it
    if SCALING == "min_max":
        X = sklearn.preprocessing.minmax_scale(
            numpy.array([numpy.array([z[0], z[1], z[2], z[3], z[4]]) for z in graph_no_coil_reference.es["mean"]]),
            feature_range=(0, 10), axis=0, copy=True)
    elif SCALING == "robust_scale":
        X = sklearn.preprocessing.robust_scale(
            numpy.array([numpy.array([z[0], z[1], z[2], z[3], z[4]]) for z in graph_no_coil_reference.es["mean"]]),
            axis=0, copy=True)

    graph_no_coil_reference.es["scaled_mean"] = X[:graph_no_coil_reference.ecount()]
    # NOTE: Here I create canto_weight which is using not only the distances but also the angles to create a weight for the edges
    # but I am not using it
    t = [cantor_pairing(list(u)) for u in X]
    graph_no_coil_reference.es["cantor_weight"] = t[:graph_no_coil_reference.ecount()]

    #TODO: I should get the signature of the graph including the dendogram
    #vclustp, dendo = get_community_clusters_one_step(algo="walktrap", graph_input=graph_no_coil_reference,
    #                                                 structure=structure_reference, pdb_search_in=pdb_search_in,
    #                                                 pathpdb=os.path.basename(reference),
    #                                                 pack_beta_sheet=pack_beta_sheet, homogeneity=homogeneity,
    #                                                 n=2, weight="weight", write_pdb=True,
    #                                                 return_dendo=True, use_spantree=True)
    #print(dendo)


    merging_results_ncs = {}

    restart = False
    start = False
    edge_used = set([])
    foundB = set([])
    trials = 1
    ty = 0
    groupsB = []
    groupsA = []
    secstrB = set([])
    secstrA = set([])
    wrongs = []
    repart = {}
    for vert in graph_no_coil_reference.vs:
        ch = vert["name"].split("_")[1]
        if ch not in repart:
            repart[ch] = [vert.index]
        else:
            repart[ch].append(vert.index)

    # if all([len(repart[ch]) == 1 for ch in repart.keys()]):
    #     dr = {}
    #     vclust = sorted([clust for clust in vclustp],key=lambda x: len(x), reverse=True)
    #     print(vclust)
    #     for z,clu in enumerate(vclust):
    #         dr[list_ids[z]] = clu
    #     repart = dr

    for key, value in repart.items():
        print(key, value)

    in_queue = multiprocessing.Queue(1000)

    #sym.spawn_function_with_multiprocessing(target=worker_for_ncs_queue,args=(in_queue))
    p = SystemUtility.OutputThreading(worker_for_ncs_queue, in_queue)
    p.start()

    #TODO: Do not allow multiple seeds or starting points
    repartus = sorted(repart.keys())
    for q,key1 in enumerate(repartus):
        if len(repart[key1]) == 1:
            continue
        for w,key2 in enumerate(repartus):
            if len(repart[key2]) == 1:
                continue
            if w>=q:
                vclust = [repart[key1],repart[key2]]

                #print("-----------------------STARING SEEDING", ty + 1, "-----------------------")
                if start:
                    ###edge_starting = sorted([ed for ed in graph_no_coil_reference.es if ed.index not in edge_used and len(graph_no_coil_reference.vs[ed.source]["reslist"]) >= 0 and len(graph_no_coil_reference.vs[ed.target]["reslist"]) >= 0 ], key=lambda x: (graph_no_coil_reference.vs[x.source]["reslist"][2], graph_no_coil_reference.vs[x.target]["reslist"][2], x["mean"][1]))[0]
                    wrong = []
                    edge_starting = \
                    sorted([ed for ed in graph_no_coil_reference.es if ed.index not in edge_used and len(
                        graph_no_coil_reference.vs[ed.source]["reslist"]) >= 0 and len(
                        graph_no_coil_reference.vs[ed.target]["reslist"]) >= 0], key=lambda x: (x["mean"][1]))[0]
                    selected = [edge_starting.source, edge_starting.target]
                    edge_used.add(edge_starting.index)

                    for x in range(1):
                        ###edge_startin2 = sorted([ed for ed in graph_no_coil_reference.es if ed.index not in edge_used and ((ed.source in selected and ed.target not in selected) or (ed.target in selected and ed.source not in selected)) and len(graph_no_coil_reference.vs[ed.source]["reslist"]) >= 0 and len(graph_no_coil_reference.vs[ed.target]["reslist"]) >= 0], key=lambda x: (graph_no_coil_reference.vs[x.source]["reslist"][2], graph_no_coil_reference.vs[x.target]["reslist"][2], x["mean"][1]))[0]
                        edge_startin2 = \
                        sorted([ed for ed in graph_no_coil_reference.es if ed.index not in edge_used and (
                            (ed.source in selected and ed.target not in selected) or (
                                ed.target in selected and ed.source not in selected)) and len(
                            graph_no_coil_reference.vs[ed.source]["reslist"]) >= 0 and len(
                            graph_no_coil_reference.vs[ed.target]["reslist"]) >= 0], key=lambda x: (x["mean"][1]))[0]
                        selected = list(set(selected + [edge_startin2.source, edge_startin2.target]))
                        edge_used.add(edge_startin2.index)

                    vclust = [selected, [v.index for v in graph_no_coil_reference.vs if v.index not in selected]]
                    start = False
                    # print(vclust[0][0],"is",graph_no_coil_reference.vs[vclust[0][0]]["reslist"][0],graph_no_coil_reference.vs[vclust[0][0]]["reslist"][-1])
                    # print(vclust[0][1],"is",graph_no_coil_reference.vs[vclust[0][1]]["reslist"][0],graph_no_coil_reference.vs[vclust[0][1]]["reslist"][-1])
                    ty += 1
                    for u in vclust[0]:
                        print(u, "is", graph_no_coil_reference.vs[u]["reslist"][0],
                              graph_no_coil_reference.vs[u]["reslist"][-1])
                    for u in vclust[1]:
                        print(u, "is", graph_no_coil_reference.vs[u]["reslist"][0],
                              graph_no_coil_reference.vs[u]["reslist"][-1])
                        # vclust[1] = [12,13,14,15]
                        # vclust = sorted([clust for clust in vclustp],key=lambda x: len(x), reverse=True)
                elif restart:
                    # secstrA = groupsB.pop()
                    wrongs += secstrB
                    vclust = [list(secstrA), [t.index for t in graph_no_coil_reference.vs if
                                              t.index not in secstrA and t.index not in foundB | set(groupsA) | set(
                                                  wrongs)]]
                    for u in vclust[0]:
                        print(u, "is", graph_no_coil_reference.vs[u]["reslist"][0],
                              graph_no_coil_reference.vs[u]["reslist"][-1])
                    for u in vclust[1]:
                        print(u, "is", graph_no_coil_reference.vs[u]["reslist"][0],
                              graph_no_coil_reference.vs[u]["reslist"][-1])
                    ty += 1
                    restart = False

                sym.spawn_function_with_multiprocessing(target=execute_ncs_search_between_two_classes, args=(vclust,graph_no_coil_reference,reference,structure_reference, matrix_reference, cvs_reference, force_core_expansion_through_secstr, pep_len, sampling, gui, ty, trials, groupsA, groupsB, in_queue))
                foundB = foundB | secstrB | set(wrongs)

    in_queue.put("ENDED")
    while len(multiprocessing.active_children()) > 0 or len(threading.enumerate()) > 1: pass #print("#PROC:",len(multiprocessing.active_children()),"#THREADS:",len(threading.enumerate()))

    X = numpy.array([len(x.keys()) for x in list_ncs_dictio])
    if len(X) >= 2:
        X = X.reshape(-1, 1)
        best_sil = 0.0
        best_lab = {}
        for n_clusters in (1,2): #(1, 2): #(1, 2, 3, 4, 5):
            ml = []
            if n_clusters > 1:
                model = sklearn.cluster.AgglomerativeClustering(linkage="ward",
                                            connectivity=None,
                                            n_clusters=n_clusters)
                model.fit(X)
                ml = model.labels_
                silhouette_avg = sklearn.metrics.silhouette_score(X, ml)
            else:
                ml = [0 for x in X]
                print("==================",ml)
                silhouette_avg = 0.5

            print("======================================================")
            print("NCLUS: ", n_clusters)
            print("LINKAGE", "ward")
            print("======================================================")
            print(ml, X.T, silhouette_avg)
            print("------------------------------------------------------")
            if silhouette_avg > best_sil:
                best_sil = silhouette_avg
                best_lab = {}
                for c,l in enumerate(ml):
                    if l not in best_lab:
                        best_lab[l] = [list_ncs_dictio[c]]
                    else:
                        best_lab[l].append(list_ncs_dictio[c])
    else:
        best_lab = {0: list_ncs_dictio}

    for clust,group in best_lab.items():
        print("EVALUATING ENSEMBLE CLUSTER n.",clust,"CONTAINING",len(group),"ANNOTATIONS.")
        merging_results_ncs = {}
        for dictio in group:
            for key in dictio:
                #print("*****",key,dictio[key])
                if key not in merging_results_ncs:
                    merging_results_ncs[key] = [dictio[key][1]]
                elif dictio[key][1] not in merging_results_ncs[key]:
                    merging_results_ncs[key].append(dictio[key][1])

                if dictio[key][1] not in merging_results_ncs:
                    merging_results_ncs[dictio[key][1]] = [key]
                elif key not in merging_results_ncs[dictio[key][1]]:
                    merging_results_ncs[dictio[key][1]].append(key)

        while 1:
            remove = None
            for key1 in merging_results_ncs.keys():
                for key2 in merging_results_ncs.keys():
                    if key1 != key2 and len(merging_results_ncs[key1]) == len(merging_results_ncs[key2]) and len(merging_results_ncs[key2]) > 1 and len(set([key1]+merging_results_ncs[key1])&set([key2]+merging_results_ncs[key2])) == len(merging_results_ncs[key2]):
                        # print("1",[key1]+merging_results[key1])
                        # print("2",[key2]+merging_results[key2])
                        # print("3",[key1]+list((set([key2]+merging_results[key2])-set([key1]))|set(merging_results[key1])))
                        # quit()
                        merging_results_ncs[key1] = list((set([key2]+merging_results_ncs[key2])-set([key1]))|set(merging_results_ncs[key1]))
                        remove = key2
                        break
                if remove is not None:
                    break
            if remove is not None:
                del merging_results_ncs[remove]
            else:
                break

        all_ncs = sorted(list(set([len(merging_results_ncs[t]) for t in merging_results_ncs.keys()])), reverse=True)
        structure = Bioinformatics3.get_structure("r", reference)
        for ncs in all_ncs:
            nome = os.path.basename(reference)[:-4] + "_E"+str(clust)+"_NCS" + str(ncs + 1) + ".pdb"
            print("FOUND NCS of size", ncs + 1, "copies...")
            max_keys = [sorted([t] + merging_results_ncs[t]) for t in merging_results_ncs if len(merging_results_ncs[t]) == ncs]
            # sec_keys = [sorted([t]+merging_results[t]) for t in merging_results if len(merging_results[t]) == ncs-1]
            max_keys = sorted(max_keys, key=lambda x: (len(x), x[0]))
            # sec_keys = sorted(sec_keys, key=lambda x: (len(x),x[0]))
            # if ncs > 2:
            #    recipient = {i:[] for i in range(1,ncs+1)}
            # else:

            recipient = {i: [] for i in range(1, ncs + 2)}
            cont_rec  = {i: [] for i in range(1, ncs + 2)}
            #    sec_keys = max_keys
            # print("---------------------------------------------------------------------")
            min_cont = 3
            conti = 0
            allres = set([])
            for keys in max_keys:
                #print(keys, len(keys))
                saved_reci = copy.deepcopy(recipient)
                saved_cont = copy.deepcopy(cont_rec)
                saved_allres = copy.deepcopy(allres)
                resiadd = set([])
                if len(recipient[1]) == 0:
                    for t, k in enumerate(keys):
                        k = ('a', k[1], k[2], k[3], k[4])
                        recipient[t + 1].append(k)
                        recipient[t + 1] = sorted(recipient[t + 1])
                        cont_rec[t + 1].append(True)
                        resiadd.add(k)
                        # print(range(len(keys)))
                else:
                    for t, k in enumerate(keys):
                        k_nearest, contr = find_nearest_neigh_ncs(k, t + 1,
                                                                 recipient,
                                                                 structure)
                        k = ('a', k[1], k[2], k[3], k[4])
                        recipient[k_nearest].append(k)
                        cont_rec[k_nearest].append(contr)
                        resiadd.add(k)
                        #recipient[k_nearest] = sorted(list(set(recipient[k_nearest])))
                        # print(k_nearest,end=" ")
                        # print()
                a = [v[-1] for t, v in sorted(recipient.items(), key=lambda x: x[0])]
                l = [len(v) for t,v in sorted(recipient.items(), key=lambda x: x[0])]
                b = None
                #print(",,,,",a)
                #print(",,,,",l)
                if len(resiadd&allres)>0:
                    recipient = saved_reci
                    cont_rec = saved_cont
                    allres = saved_allres
                    #print("REMOVING because residues are reused", l, c)
                    continue
                else:
                    allres = allres|resiadd

                if len(set(l)) > 1:
                    recipient = saved_reci
                    cont_rec = saved_cont
                    allres = saved_allres
                    #print("REMOVING because wrong lenghts", l, c)
                    continue
                if len(recipient[1]) >= 2:
                    b = [v[-2] for t,v in sorted(recipient.items(),key=lambda x: x[0])]
                    if a == b:
                        recipient = saved_reci
                        cont_rec = saved_cont
                        allres = saved_allres
                        #print("REMOVING because a == b",l)
                        continue

                c = [v[-1] for t,v in sorted(cont_rec.items(),key=lambda x: x[0])]
                if len(set(c)) > 1:
                    recipient = saved_reci
                    cont_rec = saved_cont
                    allres = saved_allres
                    #print("REMOVING because mixed True and False", l, c)
                    continue

                #print(a)
                #print(c)
                #print("CONTI",conti,"MIN_CONT",min_cont,"-1*(conti+1)",-1*(conti+1))
                #print(",,,,",a,c)
                if c[0]: #is True
                    #print("IS TRUE ADDING CONTI",conti)
                    conti += 1
                    #print("+++++",a)
                #elif  check if the disconinutity can be avoided by adding the same number of residues in each copy.
                elif b is not None and [b[u][2] for u in range(len(b))]==[a[u][2] for u in range(len(b))] and len(set([abs(b[u][3][1]-a[u][3][1]) for u in range(len(b))])) == 1 and all([Bioinformatics3.get_residue(structure,v[-2][1],v[-2][2],(' ',v[-2][3][1]+r,' ')) is not None for r in range(1,[o for o in set([abs(b[u][3][1]-a[u][3][1]) for u in range(len(b))])][0])  for t, v in recipient.items()]):
                    u = [r for r in set([abs(b[u][3][1]-a[u][3][1]) for u in range(len(b))])][0]
                    for t, v in recipient.items():
                        for y in [(v[-2][0], v[-2][1], v[-2][2], (' ', v[-2][3][1] + r, ' '), v[-2][4]) for r in
                                  range(1, u)]:
                            allres.add(y)
                            #print("ADDED IN RES:", y, end=" ")
                    #print()
                    recipient = {t: v[:-1]+[(v[-2][0],v[-2][1],v[-2][2],(' ',v[-2][3][1]+r,' '),v[-2][4]) for r in range(1,u)]+[v[-1]] for t, v in recipient.items()}
                    cont_rec = {t: v[:-1]+[True for r in range(1,u)]+[True] for t, v in cont_rec.items()}
                    conti += u
                    #print("......",a)
                    #print("WAS FALSE BUT CAN BE CONTINUED NEW CONTI IS",conti,[len(v) for t,v in sorted(recipient.items(), key=lambda x: x[0])],[len(v) for t,v in sorted(cont_rec.items(), key=lambda x: x[0])])
                elif conti>0 and conti < min_cont:
                    #print("CONTI>0",conti,"MIN_CONT",min_cont)
                    #print("Before recipient", [len(v) for t,v in sorted(recipient.items(),key=lambda x: x[0])])
                    #print("Before cont_rec", [len(v) for t,v in sorted(cont_rec.items(),key=lambda x: x[0])])
                    for t, v in recipient.items(): allres = allres - {v[-1 * (conti + 2)]} if len(v) >= -1 * (-1 * (conti + 2)) else allres
                    recipient = {t: v[:-1*(conti+2)]+[v[-1]] for t, v in recipient.items()}
                    cont_rec  = {t: v[:-1*(conti+2)]+[v[-1]] for t, v in cont_rec.items()}
                    #print("After recipient", [len(v) for t, v in sorted(recipient.items(), key=lambda x: x[0])])
                    #print("len allres",len(allres))
                    #print("After cont_rec", [len(v) for t, v in sorted(cont_rec.items(), key=lambda x: x[0])])
                    conti = 0
                elif conti == 0:
                    #print("CONTI==0", conti, "MIN_CONT", min_cont)
                    #print("Before recipient", [len(v) for t, v in sorted(recipient.items(), key=lambda x: x[0])])
                    #print("Before cont_rec", [len(v) for t, v in sorted(cont_rec.items(), key=lambda x: x[0])])
                    for t, v in recipient.items(): allres = allres - set([v[-2]]) if len(v) >= -1*(-2) else allres
                    recipient = {t: v[:-2]+[v[-1]] for t, v in recipient.items()}
                    cont_rec  = {t: v[:-2]+[v[-1]] for t, v in cont_rec.items()}
                    #print("After recipient", [len(v) for t, v in sorted(recipient.items(), key=lambda x: x[0])])
                    #print("len allres",len(allres))
                    #print("After cont_rec", [len(v) for t, v in sorted(cont_rec.items(), key=lambda x: x[0])])
                else:
                    #print("ACCEPTING because CONTI is",conti)
                    conti = 0
                    #print("++++",a)

            for z in range(len(recipient[1])) :
                for t, v in sorted(recipient.items(), key=lambda x: x[0]):
                    print(v[z],cont_rec[t][z], end=" ")
                print()

            #print([v[z] for z in range(len(recipient[1])) for t,v in sorted(recipient.items(),key=lambda x: x[0])],[v[z] for z in range(len(recipient[1])) for t,v in sorted(cont_rec.items(),key=lambda x: x[0])])

            # if ncs > 2:
            #     recipient[ncs+1] = []
            #     indices = recipient.keys()
            #     for keys in max_keys:
            #         lir = []
            #         lid = []
            #         not_inserted = None
            #         for t, k in enumerate(keys):
            #             k = ('a',k[1],k[2],k[3],k[4])
            #             for tor in indices:
            #                 #print("Checking",k,"is in",recipient[tor])
            #                 if k in recipient[tor]:
            #                     lir.append(tor)
            #                     lid.append(recipient[tor].index(k))
            #                     break
            #             not_inserted = k
            #         print("LIR is",lir,"INDICES",indices,"LID",lid)
            #         if len(lir) == len(indices)-1:
            #             indr = list(set(indices)-set(lir))[0]
            #             print("INDR",indr,"TOBE",ncs+1)
            #             recipient[indr].append(not_inserted)
            #             recipient[indr] = sorted(list(set(recipient[indr])))

            print("---------------------------------------------------------------------")

            # recipient = elongate_and_uniform_copies(recipient,structure,reference)
            pdb1 = get_pdb_string_from_residues(recipient, structure)
            f = open(nome, "w")
            f.write(pdb1)
            f.close()
            print("NCS annotate pdb written at: ", nome)


@SystemUtility.timing
def decompose_by_community_clustering(reference, sensitivity_ah, sensitivity_bs, peptide_length, pack_beta_sheet,
                                      max_ah_dist, min_ah_dist, max_bs_dist, min_bs_dist, write_graphml, write_pdb,
                                      homogeneity, gui=False, signal=None):
    # NOTE: PARAMETRIZATION=======
    # write_graphml = bool(write_graphml)
    sort_mode = "avg"

    if sensitivity_ah < 0:
        sensitivity_ah = 0.45
    if sensitivity_bs < 0:
        sensitivity_bs = 0.20
    if min_bs_dist < 0:
        min_bs_dist = 0
    if max_bs_dist < 0:
        max_bs_dist = 15
    if min_ah_dist < 0:
        min_ah_dist = 0
    if max_ah_dist < 0:
        max_ah_dist = 20

    weight = "distance_avg"
    pep_len = int(peptide_length)

    pdb_search_in = ""
    f = open(reference, "r")
    all_lines = f.readlines()
    f.close()
    for line in all_lines:
        if line[:6] in ["TITLE ", "CRYST1", "SCALE1", "SCALE2", "SCALE3"]:
            pdb_search_in += line

    graph_full_reference, structure_reference, matrix_reference, cvs_reference, highd_reference = annotate_pdb_model_with_aleph(
        reference, weight=weight, min_diff_ah=sensitivity_ah, min_diff_bs=sensitivity_bs, peptide_length=pep_len,
        write_pdb=write_pdb)
    graph_full_reference.vs["name"] = [str(vertex["reslist"][0][3][1]) + "_" + str(vertex["reslist"][0][2]) for vertex
                                       in graph_full_reference.vs]
    graph_no_coil_reference = graph_full_reference.vs.select(sstype_in=["ah", "bs"]).subgraph()
    eigen_ref = graph_no_coil_reference.evcent(directed=False, scale=True, weights=graph_no_coil_reference.es["weight"],
                                               return_eigenvalue=True)
    # print("EIGEN Centrality values:", eigen_ref, len(eigen_ref[0]), len(graph_no_coil_reference.vs))
    graph_no_coil_reference.vs["eigen"] = eigen_ref[0]
    graph_no_coil_reference.vs["Label"] = [d["sstype"] + "_" + d["name"] for t, d in
                                           enumerate(graph_no_coil_reference.vs)]
    graph_no_coil_reference.write_graphml(os.path.join("./", os.path.basename(reference)[:-4] + "_graphref.graphml"))

    for i, frag in enumerate(graph_no_coil_reference.vs):
        print(
            frag.index, "**", frag["sstype"], frag["reslist"][0][2], frag["reslist"][0][3][1], "--",
            frag["reslist"][-1][3][1], frag["sequence"], "CVIDS: ", frag["cvids"][0], frag["cvids"][
                int(len(frag["cvids"]) / 2)], frag["cvids"][-1], "SHEET ID: "+str(frag["sheet"]) if frag["sstype"] == "bs" else "")
        if sort_mode == "avg":
            print("\t\tSORTED LIST OF FRAGMENT BY AVG DISTANCE:")
            print("\t\tPOS:\tN_FRAG:\tAVG_DIST:")
        else:
            print("\t\tSORTED LIST OF FRAGMENT BY MIN DISTANCE:")
            print("\t\tPOS:\tN_FRAG:\tMIN_DIST:")

        for j, edge2 in enumerate(get_eseq_neighbours_fragments(graph_no_coil_reference, frag, sortmode=sort_mode)):
            print("\t\t" + str(j) + "\t" + str(get_connected_fragment_to_edge(frag, edge2).index) + "\t" + str(
                edge2[sort_mode]))

    #graph_no_coil_cc_filter = get_distance_filtered_graph(graph_no_coil_reference, bottom_distance=min_ah_dist, top_distance=max_ah_dist, type_distance=sort_mode)

    # if pack_beta_sheet:
    #     print("EXECUTING TWO STEPS COMMUNITY CLUSTERING....")
    #     dictio_full = get_community_clusters_two_step(graph_no_coil_reference, structure_reference, pdb_search_in,
    #                                                   os.path.basename(reference), sort_mode, min_bs_dist,
    #                                                   max_bs_dist)
    # else:
    print("EXECUTING COMMUNITY CLUSTERING....")
    get_community_clusters_one_step("fastgreedy", graph_no_coil_reference, structure_reference, pdb_search_in, os.path.basename(reference),pack_beta_sheet=pack_beta_sheet,homogeneity=homogeneity)


@SystemUtility.timing
def annotate_pdb_model(reference, sensitivity_ah, sensitivity_bs, peptide_length, width_pic, height_pic, write_graphml,
                       write_pdb, gui=False, signal=None):
    # NOTE: PARAMETRIZATION=======
    # write_graphml = bool(write_graphml)
    sort_mode = "avg"

    if sensitivity_ah < 0:
        sensitivity_ah = 0.45
    if sensitivity_bs < 0:
        sensitivity_bs = 0.20

    weight = "distance_avg"
    pep_len = int(peptide_length)

    pdb_search_in = ""
    f = open(reference, "r")
    all_lines = f.readlines()
    f.close()
    for line in all_lines:
        if line[:6] in ["TITLE ", "CRYST1", "SCALE1", "SCALE2", "SCALE3"]:
            pdb_search_in += line

    graph_full_reference, structure_reference, matrix_reference, cvs_reference, highd_reference = annotate_pdb_model_with_aleph(
        reference, weight=weight, min_diff_ah=sensitivity_ah, min_diff_bs=sensitivity_bs, peptide_length=pep_len,
        write_pdb=write_pdb)
    graph_full_reference.vs["name"] = [str(vertex["reslist"][0][3][1]) + "_" + str(vertex["reslist"][0][2]) for vertex
                                       in graph_full_reference.vs]
    graph_no_coil_reference = graph_full_reference.vs.select(sstype_in=["ah", "bs"]).subgraph()
    try:
        eigen_ref = graph_no_coil_reference.evcent(directed=False, scale=True, weights=graph_no_coil_reference.es["weight"],
                                               return_eigenvalue=True)
        # print("EIGEN Centrality values:", eigen_ref, len(eigen_ref[0]), len(graph_no_coil_reference.vs))
        graph_no_coil_reference.vs["eigen"] = eigen_ref[0]
    except:
        graph_no_coil_reference.vs["eigen"] = [0 for x in graph_no_coil_reference.vs]

    graph_no_coil_reference.vs["Label"] = [d["sstype"] + "_" + d["name"] for t, d in
                                           enumerate(graph_no_coil_reference.vs)]
    graph_no_coil_reference.write_graphml(
        os.path.join("./", os.path.basename(reference)[:-4] + "_graphref.graphml"))

    if graph_no_coil_reference.vcount() > 1:
         name_file_signature = os.path.join("./", os.path.basename(reference)[:-4] + ".sgr")
         signature = get_signature_of_the_graph(graph_no_coil_reference, reference, structure_reference, size_tree=3)
         print("Signature of the graph is stored in the text file: ", name_file_signature)
         with open(name_file_signature, "w") as fpo:
             fpo.write(signature)


    pdbsearchin = ""

    for i, frag in enumerate(graph_no_coil_reference.vs):
        print(
            frag.index, "**", frag["sstype"], frag["reslist"][0][2], frag["reslist"][0][3][1], "--",
            frag["reslist"][-1][3][1], frag["sequence"], "CVIDS: ", frag["cvids"][0], frag["cvids"][
                int(len(frag["cvids"]) / 2)], frag["cvids"][-1])
        if sort_mode == "avg":
            print("\t\tSORTED LIST OF FRAGMENT BY AVG DISTANCE:")
            print("\t\tPOS:\tN_FRAG:\tAVG_DIST:")
        else:
            print("\t\tSORTED LIST OF FRAGMENT BY MIN DISTANCE:")
            print("\t\tPOS:\tN_FRAG:\tMIN_DIST:")

        for j, edge2 in enumerate(get_eseq_neighbours_fragments(graph_no_coil_reference, frag, sortmode=sort_mode)):
            print("\t\t" + str(j) + "\t" + str(get_connected_fragment_to_edge(frag, edge2).index) + "\t" + str(
                edge2[sort_mode]))

    # NOTE: Graphs of the secondary structures
    pylab.figure(figsize=(width_pic, height_pic))
    x = []
    y = []
    z = []
    q = []
    dizioq = {}
    cmap = {"ah": "r", "bs": "y", "coil": "b"}
    for frag in graph_full_reference.vs:
        x += frag["cvids"]
        y += frag["cvls"]
        z += [frag["sstype"]] * len(frag["cvls"])
        q += [str(ty[3][1]) + "_" + str(ty[2]) for ty in frag["reslist"]]
        # print(frag["cvids"],frag["cvls"],[frag["sstype"]]*len(frag["cvls"]),[str(ty[3][1])+"_"+str(ty[2]) for ty in frag["reslist"]])
        # print(len(frag["cvids"]),len(frag["cvls"]),len([frag["sstype"]]*len(frag["cvls"])),len([str(ty[3][1])+"_"+str(ty[2]) for ty in frag["reslist"][:-2]]))

    pylab.scatter(x, y, s=100, color=[cmap[u] for u in z])
    pylab.plot(x, y, linewidth=4)
    for xyq in zip(x, y, q):
        pylab.annotate(xyq[2], xy=xyq[:2], textcoords='data')
        dizioq[xyq[0]] = xyq[2]
    pylab.axhline(y=2.2, color='b')
    pylab.axhline(y=1.4, color='b')
    pylab.title('' + os.path.basename(reference) + ' CVLs', fontsize=20)
    pylab.ylabel('CVL', fontsize=16)
    pylab.xlabel('CV id', fontsize=16)
    # pylab.xlim(numpy.arange(numpy.min(x), numpy.max(x), 1.0))
    pylab.xticks(numpy.arange(numpy.min(x), numpy.max(x), 1.0))
    pylab.savefig(os.path.join("./", os.path.basename(reference)[:-4] + "_CVLs.png"))
    pylab.close()

    f = open(os.path.join("./", os.path.basename(reference)[:-4] + "_CVLs.txt"), "w")
    for opo, l in enumerate(x):
        f.write(str(x[opo]) + "\t" + str(y[opo]) + "\t" + str(q[opo]) + "\t" + str(z[opo]) + "\n")
    # for opo, l in enumerate(x):
    #     f.write(str(x[opo]) + "\t" + str(y[opo]) + "\t" + str(z[opo]) +"\n")
    f.close()

    # NOTE: Graph of the distances of the secondary structures
    pylab.figure(figsize=(width_pic, height_pic))
    x = []
    y = []
    z = []
    q = []
    r = []
    p = []
    s = []
    cmap = {"ah": "r", "bs": "y", "coil": "b"}

    for frag in graph_full_reference.vs:
        if frag["sstype"] == "bs":
            for cvid in frag["cvids"]:
                for frag2 in graph_full_reference.vs:
                    if frag2.index != frag.index:
                        suball = [valo for valo in
                                  graph_full_reference.es[graph_full_reference.get_eid(frag.index, frag2.index)]["alls"]
                                  if cvid in valo[:2] and valo[3] <= 10.0]
                        x += [cvid] * len(suball)
                        y += [ty[3] for ty in suball]
                        s += [ty[2] for ty in suball]
                        q += [ty[0] if ty[0] != cvid else ty[1] for ty in suball]
                        z += [frag2["sstype"]] * len(suball)

    f = open(os.path.join("./", os.path.basename(reference)[:-4] + "_distances.txt"), "w")
    for opo, l in enumerate(x):
        f.write(str(x[opo]) + "\t" + str(q[opo]) + "\t" + str(y[opo]) + "\t" + str(s[opo]) + "\t" + str(
            z[opo]) + "\t" + str(dizioq[x[opo]]) + "\t" + str(dizioq[q[opo]]) + "\n")
        # f.write(str(x[opo])+"\t"+str(q[opo])+"\t"+str(y[opo])+"\t"+str(z[opo])+"\t"+"\n")
    f.close()

    # NOTE: Graph of the angles in secondary structures
    pylab.figure(figsize=(width_pic, height_pic))
    x = []
    y = []
    z = []
    q = []
    o = []
    n = []
    l = []
    k = []
    cmap = {"ah": "r", "bs": "y", "coil": "w"}

    graph_full_reference = graph_full_reference.vs.select(lambda x: len(x["cvids"]) > 0).subgraph()
    for frag in graph_full_reference.vs:
        # print frag["cvids"]
        # print [ty[0] for ty in frag["alls"]]
        # print [frag["sstype"]] * len(frag["cvls"][:-1])
        # print
        # print
        if frag.index < len(graph_full_reference.vs) - 1:
            o += [frag["cvids"][0]]
            n += [graph_full_reference.es[graph_full_reference.get_eid(frag.index, frag.index + 1)]["mean"][0]]
            l += [str(frag["reslist"][0][3][1]) + "-" + str(frag["reslist"][-1][3][1]) + "_" + str(
                frag["reslist"][0][2]) + "--" + str(
                graph_full_reference.vs[frag.index + 1]["reslist"][0][3][1]) + "-" + str(
                graph_full_reference.vs[frag.index + 1]["reslist"][-1][3][1]) + "_" + str(
                graph_full_reference.vs[frag.index + 1]["reslist"][0][2])]
        x += frag["cvids"][:-1]
        y += [ty[0] for ty in frag["alls"]]
        k += [ty[1] for ty in frag["alls"]]
        z += [frag["sstype"]] * len(frag["cvls"][:-1])
        q += [str(frag["reslist"][ty][3][1]) + "_" + str(frag["reslist"][ty][2]) + "-" + str(
            frag["reslist"][ty + 1][3][1]) + "_" + str(frag["reslist"][ty + 1][2]) for ty in
              range(len(frag["reslist"][:-2]) - 1)]

    # print("LEN",len(x),len(y))
    # print(x)
    # print(y)

    pylab.scatter(x, y, s=100, color=[cmap[u] for u in z])
    pylab.plot(x, y, linewidth=4, color="b")
    pylab.scatter(o, n, linewidth=4, color="g")

    f = open(os.path.join("./", os.path.basename(reference)[:-4] + "_Angles.txt"), "w")

    for xyq in zip(x, y, q, z):
        pylab.annotate(xyq[2], xy=xyq[:2], textcoords='data')
        f.write(str(xyq[0]) + "\t" + str(xyq[1]) + "\t" + str(xyq[2]) + "\t" + str(xyq[3]) + "\n")
    # for xy in zip(x, y, z):
    #    f.write(str(xy[0]) + "\t" + str(xy[1]) + "\t" + str(xy[2]) +"\n")

    for onl in zip(o, n, l, z):
        pylab.annotate(onl[2], xy=onl[:2], textcoords='data')
        # f.write(str(onl[0]) + "\t" + str(onl[1]) + "\t" + str(onl[2]) + "\t" + str(onl[3]) +"\n")

    # pylab.axhline(y=2.2, color='b')
    # pylab.axhline(y=1.4, color='b')
    pylab.title('' + os.path.basename(reference) + ' Angles', fontsize=20)
    pylab.ylabel('Angle', fontsize=16)
    pylab.xlabel('CV id', fontsize=16)
    # # pylab.xlim(numpy.arange(numpy.min(x), numpy.max(x), 1.0))
    pylab.xticks(numpy.arange(numpy.min(x), numpy.max(x), 1.0))
    pylab.savefig(os.path.join("./", os.path.basename(reference)[:-4] + "_Angles.png"))
    pylab.close()

    f.close()

    #NOTE: Graph of the Ca-Ca distances
    pylab.figure(figsize=(width_pic, height_pic))
    pylab.scatter(x, k, s=100, color=[cmap[u] for u in z])
    pylab.plot(x, k, linewidth=4, color="b")
    for xk in zip(x, k, q):
        pylab.annotate(xk[2], xy=xk[:2], textcoords='data')
    pylab.title('' + os.path.basename(reference) + ' Ca-Ca distances', fontsize=20)
    pylab.ylabel('Angstrom', fontsize=16)
    pylab.xlabel('CV id', fontsize=16)
    # # pylab.xlim(numpy.arange(numpy.min(x), numpy.max(x), 1.0))
    pylab.xticks(numpy.arange(numpy.min(x), numpy.max(x), 1.0))
    pylab.ylim((0, 4))
    pylab.savefig(os.path.join("./", os.path.basename(reference)[:-4] + "_ca-ca_d.png"))
    pylab.close()

    # r = np.arange(0, 2, 0.01)
    # theta = 2 * np.pi * r

    # ax = pylab.subplot(111, projection='polar')
    v, ax = pylab.subplots(1, sharex=True, figsize=(width_pic, height_pic), subplot_kw=dict(polar=True))

    # ax = axarr.subplot(111, projection='polar')
    # ax.bar(0, numpy.pi, width=0.1)
    # ax.bar(math.pi / 3.0, 3.0, width=math.pi / 3.0)

    # Adjust the axis
    # ax.set_ylim(0, numpy.pi)

    # ax.set_frame_on(False)
    # ax.axes.get_xaxis().set_visible(False)
    # ax.axes.get_yaxis().set_visible(False)

    ax.scatter([(numpy.pi / 180.0) * sole for sole in y], x, color=[cmap[u] for u in z])
    # NOTE: decomment following line to print also external angles
    ####ax.scatter([(numpy.pi/180.0 )*sole for sole in n],o, color="g")
    # NOTE: decomment following line to print also lines connecting dots
    ####ax.plot([(numpy.pi/180.0 )*sole for sole in y],x)
    # for xyq in zip([(numpy.pi/180.0 )*sole for sole in y], x, q):
    #     pylab.annotate(xyq[2], xy=xyq[:2], textcoords='data')
    # ax.set_rmax(len(x))

    # ax.set_rticks([0.5, 1, 1.5, 2])  # less radial ticks
    # ax.set_rlabel_position(-22.5)  # get radial labels away from plotted line
    ax.grid(True)
    pylab.savefig(os.path.join("./", os.path.basename(reference)[:-4] + "_Angles2.png"))
    pylab.close()


#@SystemUtility.timing
def perform_superposition(reference, target, sensitivity_ah=0.000001, sensitivity_bs=0.000001, peptide_length=3, write_graphml=False, write_pdb=False,
                          ncycles=15, deep=False, top=4, max_sec=1, break_sec=300, min_correct=1, gui=None, sampling="none", core_percentage=10, criterium_selection_core="residues", force_core_expansion_through_secstr=False, restrictions_edges=None, map_reference=None, map_target=None, verbose=True, use_signature=False, match_edges_sign=3, signature_threshold=0.0):
    """
      Superpose target pdb onto reference pdb using Characteristic Vectors annotation and graph matching.
    
    :param reference: The pdb reference file
    :type reference: io.TextIOWrapper
    :param target: The pdb target file
    :type target: io.TextIOWrapper 
    :param min_dist_bs: Minimum distance fr CVs annotated as beta strand
    :type min_dist_bs: float
    :param max_dist_bs: Maximum distance fr CVs annotated as beta strand
    :type max_dist_bs: float
    :param sensitivity_ah: Sensitivity parameter threshold for accepting ah CVs
    :type sensitivity_ah: float
    :param sensitivity_bs: Sensitivity parameter threshold for accepting bs CVs
    :type sensitivity_bs: float
    :param peptide_length: Define the peptide length for computing a CV
    :type peptide_length: int
    :param write_graphml: Write graph graphml files
    :type write_graphml: bool
    :return: 
    :rtype: 
    """

    # NOTE: PARAMETRIZATION=======
    # write_graphml = bool(write_graphml)
    sort_mode = "avg"

    if restrictions_edges is None:
        restrictions_edges = {}

    if sensitivity_ah < 0:
        sensitivity_ah = 0.45
    if sensitivity_bs < 0:
        sensitivity_bs = 0.20

    # if force_core_expansion_through_secstr:
    #     max_sec = 5
    #     break_sec = 300
    #     min_correct = 3

    weight = "distance_avg"
    pep_len = int(peptide_length)
    sampling = sampling.lower()

    if use_signature and not (isinstance(reference, tuple) and isinstance(target, tuple)):
        graph_no_coil_reference, matrix_reference, cvs_reference, structure_reference, graph_no_coil_target, matrix_target, cvs_target, structure_target, signature_ref, signature_targ, possibilities, collections = compare_structures(
            reference, target, sensitivity_ah, sensitivity_bs, peptide_length,
            write_graphml, write_pdb, ref_tuple=None,
            targ_tuple=None, core_percentage=core_percentage,
            criterium_selection_core=criterium_selection_core,
            force_core_expansion_through_secstr=force_core_expansion_through_secstr, verbose=False, gui=gui,
            rmsd_max=-1.0, ncycles=ncycles, deep=deep, top=top,
            sampling=sampling, write_pdbs=False,
            renumber=False, uniqueChain=False, use_frequent_as_seed=False, signature_threshold=signature_threshold)

        restrictions_edges = {tuple(sorted(n1.split("-"))): tuple(sorted(n2.split("-"))) for (n1,n2) in sorted(possibilities[0][2].keys(), key=lambda x: possibilities[0][2][x], reverse=True)[:match_edges_sign]}
        ng1 = [n[0] for n in restrictions_edges.keys()]+[n[1] for n in restrictions_edges.keys()]
        ng2 = [n[0] for n in restrictions_edges.values()]+[n[1] for n in restrictions_edges.values()]

        map_reference = {tuple(res): frag["name"] for frag in graph_no_coil_reference.vs for res in frag["reslist"] if
                         frag["name"] in ng1}
        map_target = {tuple(res): frag["name"] for frag in graph_no_coil_target.vs for res in frag["reslist"] if
                         frag["name"] in ng2}
    elif isinstance(reference, tuple) and isinstance(target, tuple):
        reference,structure_reference,graph_no_coil_reference,matrix_reference,cvs_reference = reference
        target,structure_target,graph_no_coil_target,matrix_target,cvs_target = target
    else:
        graph_full_reference, structure_reference, matrix_reference, cvs_reference, highd_reference = annotate_pdb_model_with_aleph(
            reference, weight=weight, min_diff_ah=sensitivity_ah, min_diff_bs=sensitivity_bs, peptide_length=pep_len, write_pdb=write_pdb)
        graph_full_reference.vs["name"] = [str(vertex["reslist"][0][3][1]) + "_" + str(vertex["reslist"][0][2]) for vertex
                                           in graph_full_reference.vs]
        graph_no_coil_reference = graph_full_reference.vs.select(sstype_in=["ah", "bs"]).subgraph()
        eigen_ref = graph_no_coil_reference.evcent(directed=False, scale=True, weights=graph_no_coil_reference.es["weight"],
                                                   return_eigenvalue=True)
        # print("EIGEN Centrality values:", eigen_ref, len(eigen_ref[0]), len(graph_no_coil_reference.vs))
        graph_no_coil_reference.vs["eigen"] = eigen_ref[0]
        graph_no_coil_reference.vs["Label"] = [d["sstype"] + "_" + d["name"] for t, d in
                                               enumerate(graph_no_coil_reference.vs)]

        graph_full_target, structure_target, matrix_target, cvs_target, highd_target = annotate_pdb_model_with_aleph(target,
                                                                                                       weight=weight,
                                                                                                       min_diff_ah=sensitivity_ah,
                                                                                                       min_diff_bs=sensitivity_bs,
                                                                                                       peptide_length=pep_len,
                                                                                                       write_pdb=write_pdb)
        graph_full_target.vs["name"] = [str(vertex["reslist"][0][3][1]) + "_" + str(vertex["reslist"][0][2]) for vertex in
                                        graph_full_target.vs]
        graph_no_coil_target = graph_full_target.vs.select(sstype_in=["ah", "bs"]).subgraph()
        eigen_targ = graph_no_coil_target.evcent(directed=False, scale=True, weights=graph_no_coil_target.es["weight"],
                                                 return_eigenvalue=True)
        graph_no_coil_target.vs["eigen"] = eigen_targ[0]
        graph_no_coil_target.vs["Label"] = [d["sstype"] + "_" + d["name"] for t, d in enumerate(graph_no_coil_target.vs)]

    dizio_resi_ss_reference = {}
    dizio_resi_ss_target = {}
    if criterium_selection_core == "secondary_structures":
        dizio_resi_ss_reference = {tuple(resi[1:-1]): (frag.index,frag["sstype"]) for frag in get_all_fragments(graph_no_coil_reference) for resi in frag["reslist"]}
        dizio_resi_ss_target = {tuple(resi[1:-1]): (frag.index,frag["sstype"]) for frag in get_all_fragments(graph_no_coil_target) for resi in frag["reslist"]}
    dizio_resi_ss_reference["number_of_frags"] = graph_no_coil_reference.vcount()
    dizio_resi_ss_target["number_of_frags"] = graph_no_coil_target.vcount()

    cage_ref, dr = generate_cage_graph(reference, structure_reference, graph_no_coil_reference, matrix_reference,
                                       cvs_reference, pep_len, sampling,
                                       restrictions_edges=[q for q in restrictions_edges.keys()],
                                       map_reference=map_reference, gui=gui)
    cage_targ,dt = generate_cage_graph(target, structure_target, graph_no_coil_target, matrix_target,
                                       cvs_target, pep_len, sampling,
                                       restrictions_edges=[q for q in restrictions_edges.values()],
                                       map_reference=map_target, gui=gui)

    # print("DR",dr)
    # print("DT",dt)
    # print()
    #print("RES BEFORE",restrictions_edges)
    restrictions_edges = {dr[tuple(sorted(k))]:dt[tuple(sorted(v))] for k,v in restrictions_edges.items() if tuple(sorted(k)) in dr and tuple(sorted(v)) in dt}
    #print("RES AFTER",restrictions_edges)
    #print("SHERLOCK",[(graph_no_coil_reference.vs[k[0]]["sequence"],graph_no_coil_reference.vs[k[1]]["sequence"],graph_no_coil_target.vs[v[0]]["sequence"],graph_no_coil_target.vs[v[1]]["sequence"]) for k,v in restrictions_edges.items()])
    try:
        best_for_cycle = compute_correlation_between_graphs(reference, target, structure_reference, structure_target, cage_ref, cage_targ, reference, initial_filtering_by_special=not deep, ncycles=ncycles, deep=deep, top=top, max_sec=max_sec, break_sec=break_sec, min_correct=min_correct, graphs_from_same_structure=False, gui=gui, write_graphml=write_graphml, force_core_expansion_through_secstr=force_core_expansion_through_secstr, restrictions_edges=restrictions_edges, verbose=verbose)
        results = select_best_superposition_overall_cycles(target,best_for_cycle,reference, target, cage_ref, cage_targ, write_pdb=write_pdb, gui=gui, core_percentage=core_percentage, criterium_selection_core=criterium_selection_core, verbose=verbose, dizio_resi_ss_reference=dizio_resi_ss_reference,dizio_resi_ss_target=dizio_resi_ss_target)
        return results
    except:
        print(sys.exc_info())
        traceback.print_exc(file=sys.stdout)
        return {}

def select_best_superposition_overall_cycles(usename,best_for_cycle,pdb_reference, pdb_target, cage_ref, cage_targ, enforce_tertiary_structure=False, write_pdb=True, gui=None, core_percentage=-1, criterium_selection_core="residues", dizio_resi_ss_reference=None, dizio_resi_ss_target=None, verbose=True):
    # associations = [[('0_A', '3_B'), ('1_A', '4_B'), ('2_A', '5_B'), ('3_A', '6_B'), ('5_A', '0_B'), ('6_A', '1_B'), ('7_A', '2_B')]]
    # associations = [[('0_A', '3_B'), ('1_A', '7_B'), ('2_A', '6_B'), ('3_A', '5_B'), ('5_A', '1_B'), ('6_A', '0_B')]]
    #verbose = True

    if isinstance(pdb_reference, io.StringIO):
        pdb_reference.seek(0)
    if isinstance(pdb_target, io.StringIO):
        pdb_target.seek(0)

    best_transf_global = None
    best_all_atoms_b_global = None
    best_atom_list_t_global = None
    if core_percentage <= 0:
        best_overall_score = 100000000
    else:
        best_overall_score = -1
    best_match_global = None
    best_explored_global = None

    for w,best_c in enumerate(best_for_cycle):
        structure_reference = Bioinformatics3.get_structure("re", pdb_reference)
        structure_target = Bioinformatics3.get_structure("cmp", pdb_target)
        size_of_target = len([residue['CA'] for residue in Bio.PDB.Selection.unfold_entities(structure_target, 'R') if residue.has_id("CA")])

        if enforce_tertiary_structure and w==0:
            continue
        best_length, best_corr, best_match, best_fixed, best_explored, best_g_a, best_g_b, associations = best_c

        # print("VERIFICO ASSOCIATIONS",associations)
        # print("VERIFICO EXPLORED",best_explored)
        # print("VERIFICO MATCHED",best_match)
        # print("VERIFICO FIXED",best_fixed)
        # print()
        # print()

        best_asso = None
        best_rmsd = 1000000
        best_size = 0
        best_transf = None
        for asso in associations:
            if verbose: print("ASSOCIATIONS:")
            uno = [u[0] for u in asso]
            due = [u[1] for u in asso]
            if verbose: print(uno)
            if verbose: print(due)
            check_uno = {}
            check_uno_cont = {}
            for r, f in enumerate(uno):
                t = cage_ref.vs.find(name=f)["secstr"]
                if t in check_uno:
                    check_uno[t].append(r)
                    check_uno_cont[t].append(int(f.split("_")[0]))
                else:
                    check_uno[t] = [r]
                    check_uno_cont[t] = [int(f.split("_")[0])]

            check_due = {}
            check_due_cont = {}
            for r, f in enumerate(due):
                t = cage_targ.vs.find(name=f)["secstr"]
                if t in check_due:
                    check_due[t].append(r)
                    check_due_cont[t].append(int(f.split("_")[0]))
                else:
                    check_due[t] = [r]
                    check_due_cont[t] = [int(f.split("_")[0])]

            for key in check_uno_cont:
                check_uno_cont[key] = [(check_uno_cont[key][t] - check_uno_cont[key][t + 1]) for t in
                                       range(len(check_uno_cont[key]) - 1)]
            for key in check_due_cont:
                check_due_cont[key] = [(check_due_cont[key][t] - check_due_cont[key][t + 1]) for t in
                                       range(len(check_due_cont[key]) - 1)]
            select_uno = {}
            for key in check_uno_cont:
                select_uno[key] = 1 if len(check_uno_cont[key]) > 0 and all([q < 0 for q in check_uno_cont[key]]) else -1
            select_due = {}
            for key in check_due_cont:
                select_due[key] = 1 if len(check_due_cont[key]) > 0 and all([q < 0 for q in check_due_cont[key]]) else -1

            if verbose: print(uno, check_uno, check_uno_cont, select_uno)
            if verbose: print(due, check_due, check_due_cont, select_due)

            resilist_a_full = [res for node in asso for res in cage_ref.vs.find(name=node[0])["reslist"][
                                                               ::select_uno[cage_ref.vs.find(name=node[0])["secstr"]]]]
            resilist_b_full = [res for node in asso for res in cage_targ.vs.find(name=node[1])["reslist"][
                                                               ::select_due[cage_targ.vs.find(name=node[1])["secstr"]]]]
            resilist_a = []
            for resi in resilist_a_full:
                if resi not in resilist_a:
                    resilist_a.append(resi)
            resilist_b = []
            for resi in resilist_b_full:
                if resi not in resilist_b:
                    resilist_b.append(resi)
            if verbose: print("=========================================================================================================")
            if verbose: print(resilist_a,len(resilist_a))
            if verbose: print(resilist_b,len(resilist_b))
            if verbose: print("=========================================================================================================")
            atom_list_a = [atom.get_coord() for residue in resilist_a for atom in Bioinformatics3.get_backbone(
                Bioinformatics3.get_residue(structure_reference, residue[1], residue[2], residue[3]), without_CB=True)]
            atom_list_b = [atom.get_coord() for residue in resilist_b for atom in Bioinformatics3.get_backbone(
                Bioinformatics3.get_residue(structure_target, residue[1], residue[2], residue[3]), without_CB=True)]
            atom_list_t = [atom for residue in resilist_b for atom in Bioinformatics3.get_backbone(
                Bioinformatics3.get_residue(structure_target, residue[1], residue[2], residue[3]), without_CB=True)]
            all_atoms_b = [atom for atom in Bio.PDB.Selection.unfold_entities(structure_target, "A")]
            atom_list_a = numpy.asarray(atom_list_a)
            atom_list_b = numpy.asarray(atom_list_b)
            #atom_list_t = numpy.asarray(atom_list_t)
            if verbose: print("Size A:",len(atom_list_a),"Size B:",len(atom_list_b))
            transf, rmsd_list, rmsd = Bioinformatics3.fit_wellordered(atom_list_a, atom_list_b, n_iter=None, full_output=True,
                                                                      n_stdv=2, tol_rmsd=0.005, tol_stdv=0.0005)
            if len(atom_list_a) > best_size or (len(atom_list_a) == best_size and rmsd < best_rmsd):
                best_asso = asso
                best_rmsd = rmsd
                best_size = len(atom_list_a)
                best_transf = transf

        if verbose: print("CYCLE: ",w,"RMSD:", best_rmsd, "SIZE CORE:", best_size,"BEST_SCORE: ",best_rmsd/best_size, "CORR:",best_corr)
        if best_transf is None:
            continue
        if core_percentage <= 0:
            if best_rmsd/best_size <= best_overall_score:
                best_overall_score = best_rmsd/best_size
                best_transf_global = best_transf
                best_match_global = [json.dumps(h) if isinstance(h,list) else h for h in best_fixed]
                best_explored_global = [json.dumps(h) if isinstance(h,list) else h for h in best_explored]
                best_all_atoms_b_global = all_atoms_b
                best_atom_list_t_global = atom_list_t
                best_size_global = best_size
                best_corr_global = best_corr
                best_rmsd_global = best_rmsd
                best_association_global = associations
                best_g_a_global = best_g_a
                best_g_b_global = best_g_b
        else:
            if criterium_selection_core == "residues" or dizio_resi_ss_reference is None or dizio_resi_ss_target is None:
                dictio = Bioinformatics3.get_CA_distance_dictionary(pdb_reference, pdb_target, max_rmsd=1.0,
                                                                    last_rmsd=2.0, cycles=3, recompute_rmsd=False,
                                                                    before_apply=best_transf)

                score = round((len(dictio.keys())/size_of_target)*100.0)
            else:
                dictio = Bioinformatics3.get_CA_distance_dictionary(pdb_reference, pdb_target, max_rmsd=3.0,
                                                                    last_rmsd=4.0, cycles=3, recompute_rmsd=False,
                                                                    before_apply=best_transf)
                score = [dizio_resi_ss_target[tuple(v[1][1:-1])][0] for k,v in dictio.items() if tuple(v[1][1:-1]) in dizio_resi_ss_target and tuple(k[1:-1]) in dizio_resi_ss_reference and dizio_resi_ss_reference[tuple(k[1:-1])][1] == dizio_resi_ss_target[tuple(v[1][1:-1])][1]]
                #print(score)
                # for k,v in dictio.items():
                #    print(v[1][1:-1],"--++--",k,v)

                score = {t:score.count(t) for t in set(score)}
                print("SECS BEFORE FILTERING",score)
                score = {k:v for k,v in score.items() if v>2}
                print("SECS AFTER FILTERING",score)

                # for k,v, in dizio_resi_ss.items():
                #    print(k,v,".....")
                score = round((len(score.keys())/dizio_resi_ss_reference["number_of_frags"])*100.0)
                print("SCORE is",score,"len frags",dizio_resi_ss_reference["number_of_frags"])

            if score >= core_percentage and score > best_overall_score:
                print("Superposition is acceptable")
                best_overall_score = score
                best_transf_global = best_transf
                best_match_global = [json.dumps(h) if isinstance(h, list) else h for h in best_fixed]
                best_explored_global = [json.dumps(h) if isinstance(h, list) else h for h in best_explored]
                best_all_atoms_b_global = all_atoms_b
                best_atom_list_t_global = atom_list_t
                best_size_global = best_size
                best_corr_global = best_corr
                best_rmsd_global = best_rmsd
                best_association_global = associations
                best_g_a_global = best_g_a
                best_g_b_global = best_g_b
            else:
                print("Superposition is not acceptable. Score is:",score,"core percentage request is:",core_percentage, "best overall score is:",best_overall_score)
                #quit()

    if best_transf_global is None:
        return {}

    R, t = best_transf_global
    allAtoms = Bioinformatics3.transform_atoms(best_all_atoms_b_global, R, t)
    pdbmod, cnv = Bioinformatics3.get_pdb_from_list_of_atoms(allAtoms, renumber=False, uniqueChain=False)
    pdbmod2,cnv2 = Bioinformatics3.get_pdb_from_list_of_atoms(best_atom_list_t_global, renumber=False, uniqueChain=False)
    if write_pdb:
        fds = open(os.path.join("./", "sup-" + os.path.basename(usename)), "w")
        fds.write(pdbmod)
        fds.close()
        # fds = open(os.path.join("./", "sup-2" + os.path.basename(usename)), "w")
        # fds.write(pdbmod2)
        # fds.close()

    if verbose: print("Output superposed file was written at:", os.path.join("./", "sup-" + os.path.basename(usename)) if write_pdb else "")

    if gui is not None:
        gui.draw_text(
            "Best core has: " + str(best_size_global) + " residues matched. Total SumErrors is: " + str(
                best_corr_global) + " RMSD: " + str(best_rmsd_global) + " Output superposed file was written at: " + str(
                os.path.join("./", "sup-" + os.path.basename(usename))) if write_pdb else "")

    if verbose: print()
    if verbose: print("Best core has: " + str(best_size_global) + " residues matched. Total SumErrors is: " + str(
                best_corr_global) + " RMSD: " + str(best_rmsd_global) + " Output superposed file was written at: " + str(
                os.path.join("./", "sup-" + os.path.basename(usename))) if write_pdb else "")

    return {"rmsd": best_rmsd_global, "size": best_size_global, "associations": best_association_global, "transf": best_transf_global, "graph_ref": best_g_a_global,
            "grapf_targ": best_g_b_global, "match":best_match_global, "explored":best_explored_global,"correlation": best_corr_global,"pdb_target":pdbmod,"pdb_core_target":pdbmod2,"ca_target":[atom for atom in allAtoms if atom.get_name() == "CA"]}


@SystemUtility.timing
def find_central_structural_core_shells(reference, sensitivity_ah, sensitivity_bs, peptide_length, write_graphml,
                                        write_pdb, gui=False, signal=None):
    # NOTE: PARAMETRIZATION=======
    # write_graphml = bool(write_graphml)
    sort_mode = "avg"

    if sensitivity_ah < 0:
        sensitivity_ah = 0.45
    if sensitivity_bs < 0:
        sensitivity_bs = 0.20

    weight = "distance_avg"
    pep_len = int(peptide_length)

    pdb_search_in = ""
    f = open(reference, "r")
    all_lines = f.readlines()
    f.close()
    for line in all_lines:
        if line[:6] in ["TITLE ", "CRYST1", "SCALE1", "SCALE2", "SCALE3"]:
            pdb_search_in += line

    graph_full_reference, structure_reference, matrix_reference, cvs_reference, highd_reference = annotate_pdb_model_with_aleph(
        reference, weight=weight, min_diff_ah=sensitivity_ah, min_diff_bs=sensitivity_bs, peptide_length=pep_len,
        write_pdb=write_pdb)
    graph_full_reference.vs["name"] = [str(vertex["reslist"][0][3][1]) + "_" + str(vertex["reslist"][0][2]) for vertex
                                       in graph_full_reference.vs]
    graph_no_coil_reference = graph_full_reference.vs.select(sstype_in=["ah", "bs"]).subgraph()
    eigen_ref = graph_no_coil_reference.evcent(directed=False, scale=True, weights=graph_no_coil_reference.es["weight"],
                                               return_eigenvalue=True)
    # print("EIGEN Centrality values:", eigen_ref, len(eigen_ref[0]), len(graph_no_coil_reference.vs))
    graph_no_coil_reference.vs["eigen"] = eigen_ref[0]
    graph_no_coil_reference.vs["Label"] = [d["sstype"] + "_" + d["name"] for t, d in
                                           enumerate(graph_no_coil_reference.vs)]
    graph_no_coil_reference.write_graphml(
        os.path.join("./", os.path.basename(reference)[:-4] + "_graphref.graphml"))

    cage_ref,l1 = generate_cage_graph(reference, structure_reference, graph_no_coil_reference, matrix_reference, cvs_reference, pep_len, "none", gui=gui)
    cage_ref.write_graphml(os.path.join("./", os.path.basename(reference)[:-4] + "_cageref.graphml"))

    for i in numpy.arange(1.4, 0.0, -0.05):
        cage_filt = cage_ref.vs.select(eigen_le=i).select(eigen_ge=i - 0.2).subgraph()
        cage_filt.write_graphml(
            os.path.join("./", os.path.basename(reference)[:-4] + "_core_" + str(i) + ".graphml"))
        pdbg1 = get_pdb_string_from_graph(cage_filt, structure_reference, chainid="A")
        if len(pdbg1) > 0:
            f = open(os.path.join("./", os.path.basename(reference)[:-4] + "_core_" + str(i) + ".pdb"), "w")
            f.write(pdbg1)
            f.close()
            print("CORE with centralities of:", i, "saved on", "./",
                  os.path.basename(reference)[:-4] + "_core_" + str(i) + ".pdb")

@SystemUtility.timing
def find_local_folds_in_the_graph(reference, sensitivity_ah, sensitivity_bs, peptide_length, write_graphml, write_pdb,
                                  gui=False, signal=None):
    # NOTE: PARAMETRIZATION=======
    # write_graphml = bool(write_graphml)
    sort_mode = "avg"

    if sensitivity_ah < 0:
        sensitivity_ah = 0.45
    if sensitivity_bs < 0:
        sensitivity_bs = 0.20

    weight = "distance_avg"
    pep_len = int(peptide_length)

    pdb_search_in = ""
    f = open(reference, "r")
    all_lines = f.readlines()
    f.close()
    for line in all_lines:
        if line[:6] in ["TITLE ", "CRYST1", "SCALE1", "SCALE2", "SCALE3"]:
            pdb_search_in += line

    graph_full_reference, structure_reference, matrix_reference, cvs_reference, highd_reference = annotate_pdb_model_with_aleph(
        reference, weight=weight, min_diff_ah=sensitivity_ah, min_diff_bs=sensitivity_bs, peptide_length=pep_len,
        write_pdb=write_pdb)
    graph_full_reference.vs["name"] = [str(vertex["reslist"][0][3][1]) + "_" + str(vertex["reslist"][0][2]) for vertex
                                       in graph_full_reference.vs]
    graph_no_coil_reference = graph_full_reference.vs.select(sstype_in=["ah", "bs"]).subgraph()
    eigen_ref = graph_no_coil_reference.evcent(directed=False, scale=True, weights=graph_no_coil_reference.es["weight"],
                                               return_eigenvalue=True)
    # print("EIGEN Centrality values:", eigen_ref, len(eigen_ref[0]), len(graph_no_coil_reference.vs))
    graph_no_coil_reference.vs["eigen"] = eigen_ref[0]
    graph_no_coil_reference.vs["Label"] = [d["sstype"] + "_" + d["name"] for t, d in
                                           enumerate(graph_no_coil_reference.vs)]
    graph_no_coil_reference.write_graphml(os.path.join("./", os.path.basename(reference)[:-4] + "_graphref.graphml"))

    # NOTE: This would be the n cut chosen by the algorithm itself, is useful for community clustering decomposition but not for my application here
    ###get_community_clusters_one_step("walktrap", graph_no_coil_reference, structure_reference, pdb_search_in, os.path.basename(reference)[:-4] + "_" + str(0) + ".pdb", n=None)

    dendo = None
    vclust = None
    list_graphs = []
    for cut in range(1, graph_no_coil_reference.vcount() + 1):
        if cut == 1:
            vclust, dendo = get_community_clusters_one_step("walktrap", graph_no_coil_reference, structure_reference,
                                                            pdb_search_in,
                                                            os.path.basename(reference)[:-4] + "_" + str(
                                                                cut) + ".pdb", n=cut,
                                                            print_dendo=os.path.basename(reference)[
                                                                        :-4] + "_dendo.png", return_dendo=True)
            print("Dendogram written at:", os.path.basename(reference)[:-4] + "_dendo.png")

        else:
            vclust = get_community_clusters_one_step("walktrap", graph_no_coil_reference, structure_reference,
                                                     pdb_search_in,
                                                     os.path.basename(reference)[:-4] + "_" + str(cut) + ".pdb",
                                                     n=cut, print_dendo=None, return_dendo=False, use_dendo=dendo)
            print("Fold extracted from dendogram cut level:", cut, "written on:",
                  os.path.basename(reference)[:-4] + "_" + str(cut) + ".pdb")

        list_graphs += vclust.subgraphs()

    for u, g in enumerate(list_graphs):
        g_all = generate_graph_for_cvs(reference, structure_reference, g, matrix_reference, cvs_reference,
                                       peptide_length=pep_len)
        g_all.write_graphml(os.path.join("./", os.path.basename(reference)[:-4] + "_" + str(u) + "_fold.graphml"))
        print("Graph written at:",
              os.path.join("./", os.path.basename(reference)[:-4] + "_" + str(u) + "_fold.graphml"))

def min_distance_atm_list(atom, list_of_atoms, same_type=True):
    coord1 = atom.get_coord()
    r = sorted([(a2,get_atoms_distance(coord1, a2.get_coord())) for a2 in list_of_atoms if not same_type or a2.get_name() == atom.get_name()], key=lambda x: x[1][0])
    if len(r) > 0:
        return atom,r[0]
    else:
        return atom,(None,(10.0,[]))


@SystemUtility.timing
def map_variations_library(directory, gui=None):
    paths = []
    for root, subFolders, files in os.walk(directory):
        for fileu in files:
            pdbf = os.path.join(root, fileu)
            if pdbf.endswith(".pdb"):
                paths.append(pdbf)
                Bioinformatics3.rename_hetatm_and_icode(pdbf)



    for path in paths:
        structure = Bioinformatics3.get_structure(os.path.basename(path), path)
        list_atoms = []
        for model in structure:
            atoms = Bio.PDB.Selection.unfold_entities(model, "A")
            list_atoms.append(atoms)

        zere = [[min_distance_atm_list(atmi,lj,same_type=True) for j,lj in enumerate(list_atoms) if j!=i ] for i,li in enumerate(list_atoms) for atmi in li]
        for li in zere:
            d = sum([z[1][1][0] if z[1][1][0] <= 1.0 else 1.0 for z in li])/len(li)
            docc = 1.0-d
            #(((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
            #nocc = (((docc - 1.0) * (50.0 - 10.0)) / (0.0 - 1.0)) + 10.0
            nocc = (((docc - 1.0) * (5.0 - 1.0)) / (0.0 - 1.0)) + 1.0
            nocc = nocc**2
            print(li[0][0].get_full_id(),docc,"B_Factor:",nocc)

            #for se in li:
            #    print(se[0].get_full_id(),se[1][1][0],se[1][0].get_full_id())
            #print()
            li[0][0].set_occupancy(1.0)
            li[0][0].set_bfactor(nocc)

        if not os.path.exists(os.path.join("./","occ_annotated")):
            os.makedirs(os.path.join("./","occ_annotated"))

        # for m,model in enumerate(structure):
        #     atms = [atm for atm in Bio.PDB.Selection.unfold_entities(model, "A")]
        #     m1 = Bioinformatics.get_pdb_from_list_of_atoms(atms, renumber=True, uniqueChain=False, chainId="A", chainFragment=True, diffchain=None, polyala=True, maintainCys=False)
        #     f = open("./tmp.txt","w")
        #     f.write(m1[0])
        #     f.close()
        #     s1 = Bioinformatics.get_structure(str(m),"./tmp.txt")
        #     structure[m] = s1[0]
        #     os.remove("./tmp.txt")

        Bioinformatics3.write_pdb(structure, os.path.join(os.path.join("./", "occ_annotated"), os.path.basename(path)))


def print_secondary_structure_elements(lisBigSS):
    print("=====================================================================================")
    print("      _________________________________________________________________________      ")
    for l in range(len(lisBigSS)):
        fragment = lisBigSS[l]
        print(str(fragment["pdbid"]) + "  " + str(fragment["model"]) + "  " + str(fragment["chain"]) + "  " + "[" + str(
            (fragment["resIdList"][0])[3][1]) + str((fragment["resIdList"][0])[2]) + ":" + str(
            (fragment["resIdList"][fragment["fragLength"] - 1])[3][1]) + str(
            (fragment["resIdList"][fragment["fragLength"] - 1])[2]) + "]  " + str(fragment["vecLength"]) + "  " + str(
            fragment["sstype"]) + "  " + str(fragment["sequence"]), end="")
        print(" ")
    print("      _________________________________________________________________________      ")
    print("=====================================================================================")



def get_list_of_atoms(structure, solutions, diagonals):  # protein,cvs):
    listAllFrags = []
    for p in range(len(solutions)):
        solu = solutions[p]
        back_atoms_list = []
        atoms_list = []
        resall = []
        cvs_p = []
        cvs_all = []

        for fragment in solu:
            coordfrag = fragment[0]
            chainid = fragment[1]
            protein, cvs = diagonals[chainid]

            for addr in coordfrag:
                i, j = addr
                residr = protein[(i, j)][5]

                if (i, chainid) not in cvs_all:
                    cvs_p.append(cvs[i])
                    cvs_all.append((i, chainid))
                if (j, chainid) not in cvs_all:
                    cvs_p.append(cvs[j])
                    cvs_all.append((j, chainid))

                for res in residr:
                    if res in resall:
                        continue
                    for model in structure.get_list():
                        for chain in model.get_list():
                            for residue in chain.get_list():
                                # print residue.get_full_id(),res
                                if residue.get_full_id() == tuple(res[:-1]):
                                    atoms_list += residue.get_unpacked_list()
                                    back_atoms_list.append(residue["CA"])
                                    back_atoms_list.append(residue["C"])
                                    back_atoms_list.append(residue["O"])
                                    back_atoms_list.append(residue["N"])

                                    if residue.has_id("CB"):
                                        back_atoms_list.append(residue["CB"])
                                    break
                    resall.append(res)
        ida = atoms_list[0].get_full_id()
        # print "-------------------------------------------------------------------------"
        # print resall
        listAllFrags.append((back_atoms_list, atoms_list, cvs_p, ida[0], ida[1]))
    return listAllFrags


def test_binary_combination(combi, pattern, diagonals, identity, structure, dictio_cont, connectivity, index_comb):
    verbose = False
    # if len(combi) == 3 and combi[0]["fragments_bounds"][0] == [106, 109] and combi[1]["fragments_bounds"][0] == [131, 135] and combi[2]["fragments_bounds"][0] == [122,126]:
    # print "Found correspondance combination"
    # verbose=True

    # DONE: check the correspondance between order in combi and the pattern fragment order ex: combi: 0,1,2,3 pattern:5,1,4,2
    listosa = []
    addedin = {}

    fra_consider = []
    for q in range(index_comb + 1):
        fra_consider.append(pattern["fragments_bounds"][pattern["comb_priority"][str(q)]])
    # print "connectivity pattern",fra_consider

    for f in range(len(combi)):
        fra = combi[f]
        protein, cvs = diagonals[fra["chain"]]
        if connectivity and f < len(combi) - 1:
            # print pattern["comb_priority"]
            fra2 = combi[f + 1]
            # print "test combi",fra["fragments_bounds"]+fra2["fragments_bounds"]
            # if bool(fra_consider[f][1]<fra_consider[f+1][0]) == False and bool(fra["fragments_bounds"][0][1]<fra2["fragments_bounds"][0][0]) == False:
            #   print "F1",fra_consider[f][1],"F2",fra_consider[f+1][0],"T1",fra["fragments_bounds"][0][1],"T2",fra2["fragments_bounds"][0][0]
            if fra["chain"] == fra2["chain"]:
                if not (bool(fra_consider[f][1] < fra_consider[f + 1][0]) == bool(
                            fra["fragments_bounds"][0][1] < fra2["fragments_bounds"][0][0])):
                    return False, dictio_cont
            else:
                # Check when fra and fra2 are coming from a different chain
                # print "Chain is different in test_binary",fra["chain"],fra2["chain"],"fra consider is minor",bool(fra_consider[f][1]<fra_consider[f+1][0]),"chain first frag is minor",bool(fra["chain"]<fra2["chain"])
                if not (bool(fra_consider[f][1] < fra_consider[f + 1][0]) == bool(fra["chain"] < fra2["chain"])):
                    return False, dictio_cont

                    # if len(combi) == 4:
                    # if f < len(combi)-1:
                    # print "**********,Test passed for connectivity"
                    # print "Test connectivity among ",f,f+1
                    # print "F1",fra_consider[f][1],"F2",fra_consider[f+1][0],"T1",fra["fragments_bounds"][0][1],"T2",fra2["fragments_bounds"][0][0]
                    # print bool(fra_consider[f][1]<fra_consider[f+1][0]),bool(fra["fragments_bounds"][0][1]<fra2["fragments_bounds"][0][0]),bool(fra_consider[f][1]<fra_consider[f+1][0]) == bool(fra["fragments_bounds"][0][1]<fra2["fragments_bounds"][0][0]),not (bool(fra_consider[f][1]<fra_consider[f+1][0]) == bool(fra["fragments_bounds"][0][1]<fra2["fragments_bounds"][0][0]))
                    # print "fra found",fra["fragments_bounds"][0],fra2["fragments_bounds"][0],"fra template",fra_consider[f],"f+1",fra_consider[f+1]
                    # print "++++++++++++++++++++"
                    # print combi
                    # print "++++++++++++++++++++"
                    # print pattern["fragments_bounds"]
                    # print "::::::::::::::::::::::::::::::::"
        for cvr in fra["continous_locations"]:
            for pair in cvr:
                for resi in protein[pair][5]:
                    resi = tuple(resi)
                    if resi not in listosa:
                        # print "Testo frammento",f,"residuo",resi,"del continuous location",cvr
                        for resi2 in listosa:
                            if addedin[resi2] != f:
                                if (resi, resi2) in dictio_cont:
                                    # if resi[3][1] == 80 and resi2[3][1] == 81:
                                    #   print "****Res1",resi,"Res2",resi2,"Frag1",f,"Frag2",addedin[resi2],"are contigous?",dictio_cont[(resi,resi2)]
                                    if dictio_cont[(resi, resi2)]:
                                        return False, dictio_cont
                                elif (resi2, resi) in dictio_cont:
                                    # if resi[3][1] == 80 and resi2[3][1] == 81:
                                    #   print "****Res1",resi,"Res2",resi2,"Frag1",f,"Frag2",addedin[resi2],"are contigous?",dictio_cont[(resi2,resi)]
                                    if dictio_cont[(resi2, resi)]:
                                        return False, dictio_cont
                                else:
                                    r1 = Bioinformatics3.get_residue(structure, resi[1], resi[2], resi[3])
                                    r2 = Bioinformatics3.get_residue(structure, resi2[1], resi2[2], resi2[3])
                                    # if resi[3][1] == 80 and resi2[3][1] == 81:
                                    #    print "Res1",resi,"Res2",resi2,"Frag1",f,"Frag2",addedin[resi2],Bioinformatics.checkContinuity(r1,r2)
                                    if Bioinformatics3.check_continuity(r1, r2, swap=True):
                                        # print "Res1",resi,"Res2",resi2,"Frag1",f,"Frag2",addedin[resi2],"are contigous"
                                        dictio_cont[(resi, resi2)] = True
                                        return False, dictio_cont
                                    else:
                                        dictio_cont[(resi, resi2)] = False
                                        #       if resi[3][1] == resi2[3][1]+1 or resi[3][1] == resi2[3][1]-1:
                                        #               print "Res1",resi,"Res2",resi2,"Frag1",f,"Frag2",addedin[resi2],"are not contigous"
                        listosa.append(resi)
                        addedin[resi] = f
                    elif addedin[resi] != f:
                        return False, dictio_cont

    # if len(combi)>2:
    #   quit()

    listosa = []  # sorted(listosa)
    addedin = {}
    # print listosa

    l1 = range(len(combi))
    l2 = []
    for l in l1:
        l2.append(pattern["comb_priority"][str(l)])

    if verbose:
        print("-----", l1)
        print(".....", l2)
        print(pattern["comb_priority"])

    # DONE: in pattern jumps_score select only the entries that corresponds to the fragment interested ex: pattern (5,1), (4,2), (1,2) but not
    #      (1,7) or (0,9) or (10,11)
    # DONE: correspondances should match in combi: 0j1,0j2,0j3,1j2,1j3,2j3 corresponds to 5j1,5j4,5j2,1j4,1j2,4j2 now because in pattern are
    #      stored in a symmetric way sorting by the minimum this will corresponds in reality to 1j5,4j5,2j5,1j4,1j2,2j4
    # DONE: now we can call test_solution_fragment and just return the boolen

    compare_scores = []
    start_w = 0
    for a in range(len(l2)):
        s = l2[a]
        if len(l2) == 1:
            start_w = a
        else:
            start_w = a + 1
        for w in range(start_w, len(l2)):
            r = l2[w]
            nval = [s, r]
            nval = sorted(nval)
            found = False
            for score in pattern["jumps_scores"]:
                if score[0] == nval[0] and score[1] == nval[1]:
                    compare_scores.append(score)
                    found = True
                    break
            if not found:
                print("ERROR Unexpected: cannot find jumps scores for", nval, "in pattern")
                sys.exit(1)
    a, b, c = test_solution_fragment(combi, compare_scores, diagonals, identity, verbose=verbose)
    return c, dictio_cont


def compare_sequences(seq1, combination, diagonals, structure, ssbridge):
    seq2 = ""
    seq_vaso = []
    for frag in combination:
        protein, cvs = diagonals[frag["chain"]]
        for conl in range(len(frag["continous_locations"])):
            conli = frag["continous_locations"][conl]
            for co in range(len(conli)):
                con = conli[co]
                valilist = protein[con][5][:3] + [protein[con][5][-1]]
                valore = "".join(map(lambda x: Bioinformatics3.AADICMAP[x], map(lambda x: x[4], valilist)))
                if co == len(conli) - 1:
                    seq2 += valore
                    seq_vaso += valilist
                else:
                    seq2 += valore[0]
                    seq_vaso += [valilist[0]]

    return __compareSeqReal(seq1, seq2, ssbridge, seq_vaso, structure)


def __compareSeqReal(seq1, seq2, ssbridge, seq_vaso, structure):
    resids = []
    for xc in range(len(seq1)):
        if seq1[xc].upper() != "X" and seq1[xc].upper() != seq2[xc].upper():
            return False
        elif ssbridge:
            if seq1[xc].upper() == "C":
                seqv = seq_vaso[xc]
                res = Bioinformatics3.get_residue(structure, seqv[1], seqv[2], seqv[3])
                resids.append(res)

    for r in range(len(resids) - 1):
        S1 = resids[r]["SG"]
        S2 = resids[r + 1]["SG"]
        resaS1X = float(S1.get_coord()[0])
        resaS1Y = float(S1.get_coord()[1])
        resaS1Z = float(S1.get_coord()[2])
        resaS2X = float(S2.get_coord()[0])
        resaS2Y = float(S2.get_coord()[1])
        resaS2Z = float(S2.get_coord()[2])
        checkbond = numpy.sqrt(((resaS1X - resaS2X) ** 2) + ((resaS1Y - resaS2Y) ** 2) + ((resaS1Z - resaS2Z) ** 2))
        if not (checkbond >= 2.0 and checkbond <= 2.10):  # S-S bond is 2.05 A
            return False
    # if isEqual:
    # print "Comparing",seq1,seq2
    # print "IsEqual?",isEqual
    return True


def use_fragments_to_extract_models(listDiscoveredFrags, pattern, diagonals, structure, sequence, identity, stepdiag,
                                    ssbridge, connectivity, lengthFragment=3):
    global GLOBAL_MAXIMUM
    solutions = []
    dictio_cont = {}

    def __check_combinations(listevaluate, pattern, diagonals, identity, structure, dictio_cont, connectivity,
                             index_comb_search):
        returnlist = []
        for com in itertools.product(*listevaluate):
            combi = []
            # print "com",len(com)
            # print "is",com
            if isinstance(com[0], list):
                for c in com[0]:
                    combi.append(c)
            else:
                combi.append(com[0])
            combi.append(com[1])
            result, dictio_cont = test_binary_combination(combi, pattern, diagonals, identity, structure, dictio_cont,
                                                          connectivity, index_comb_search)

            if result:
                returnlist.append(combi)
        return returnlist, dictio_cont

    combinations = []
    # combis = list(product(*listDiscoveredFrags))
    ndsf = 1
    associations = []

    # NOTE: Block to check all fragments extracted
    """"
    print "Descrizione frammenti scoperti"
    for i in range(len(listDiscoveredFrags)):
        print "livello i",i,"are",len(listDiscoveredFrags[i])
        for frag in listDiscoveredFrags[i]:
                #try:
                        bounds = frag["fragments_bounds"][0]
                        protein,cvs = diagonals[frag["chain"]]
                        first_res = protein[(frag["fragments_bounds"][0][0],frag["fragments_bounds"][0][0]+1)][5][0][3][1]
                        last_res =  protein[(frag["fragments_bounds"][0][1]-1,frag["fragments_bounds"][0][1])][5][-1][3][1]
                        #if first_res == 132 and last_res == 138:
                        print bounds,"::",frag["chain"],first_res,"--",last_res,"total",last_res-first_res+1
                #except:
                #        pass
    """
    # END BLOCK

    for qw in range(len(listDiscoveredFrags)):
        lir = listDiscoveredFrags[qw]
        ndsf *= len(lir)
        associations.append([qw, lir])

    if not connectivity:
        associations = sorted(associations, key=lambda x: len(x[1]))

    listDiscoveredFrags = []
    pattern["comb_priority"] = {}
    for rw in range(len(associations)):
        tup = associations[rw]
        listDiscoveredFrags.append(tup[1])
        pattern["frag_priority"][str(tup[0])] = rw
        pattern["comb_priority"][str(rw)] = tup[0]
    associations = None
    print("All theoretical combinations: ", ndsf, "solutions")
    # print "frag_priority: ",pattern["frag_priority"]
    # print "comb_priority: ",pattern["comb_priority"]

    liPassed = listDiscoveredFrags[0]
    for s in range(1, len(listDiscoveredFrags)):
        print("N. to " + str((s + 1)) + "-ary combinations when adding frag. " + str(s) + " to " + str(
            range(0, s)) + ": ", len(liPassed) * len(listDiscoveredFrags[s]))
        # print "====================================="
        # print [liPassed]+[listDiscoveredFrags[s]]
        # print "====================================="
        liPassed, dictio_cont = __check_combinations(copy.deepcopy([liPassed] + [listDiscoveredFrags[s]]), pattern,
                                                     diagonals, identity, structure, dictio_cont, connectivity, s)

    # DONE: Reorder all final solutions in liPassed in their original order according pattern["comb_priority"]

    if len(listDiscoveredFrags) == 1:
        liPassed = map(lambda x: [x], liPassed)

    finli = []
    for combi in liPassed:
        nc = [None for _ in range(len(combi))]
        for ps in range(len(combi)):
            nc[pattern["comb_priority"][str(ps)]] = combi[ps]
        finli.append(nc)
    liPassed = finli

    print("N. to final reduced combinations is: ", len(liPassed))

    print("N. sol:")
    countd = 1
    for combi in liPassed:
        if len(solutions) > GLOBAL_MAXIMUM:
            print("More than", GLOBAL_MAXIMUM, "solutions. Stopping search.")
            break
        if countd % 10000 == 0:
            print("\nTest n." + str(countd) + " of " + str(ndsf) + "\n")
        if (sequence == "" or compare_sequences(sequence, combi, diagonals, structure, ssbridge)):
            fra_comb, cvs, result = test_solution_fragment(combi, pattern["jumps_scores"], diagonals, identity)
            if result:
                combinations.append(fra_comb)
                # TODO: Here I save the solutions but if I just put the continous_locations without a reference to the chainid I cannot use it later
                srd = []
                for r in range(len(fra_comb["continous_locations"])):
                    # print fra_comb["continous_locations"][r], fra_comb["continous_locations_chains"][r]
                    srd.append([fra_comb["continous_locations"][r], fra_comb["continous_locations_chains"][r]])
                solutions.append(srd)
                # solutions.append([[item for sublist in fra_comb["continous_locations"] for item in sublist],[item for sublist in fra_comb["continous_locations_chains"] for item in sublist]])
                print(".", end=' ')
        countd += 1
    print("\n\n")
    return solutions

def test_continous_fragment(frag, compare_scores, protein, identity):
    frag["continous_locations"] = []
    frag["fragments_scores"] = []
    fragb = sorted(frag["fragments_bounds"][0])
    # Continous locations
    con_loc = []
    a, b = fragb

    if a == b:
        con_loc.append((a, b))
    else:
        for t in range(a, b):
            con_loc.append((t, t + 1))
    frag["continous_locations"].append(con_loc)

    # computing fragments scores
    sumConScore_cv = 0
    sumConScore_theta = 0
    sumConScore_distance = 0
    sumConScore_phi = 0
    for pos in con_loc:
        instruction = protein[pos]
        if instruction[0] != 1:
            # print "Fragment",frag["fragments_bounds"],"is not continuos"
            return None, False
        sumConScore_cv += instruction[1][0] + instruction[1][1]
        sumConScore_theta += instruction[2]
        sumConScore_distance += instruction[3]
        sumConScore_phi += instruction[4]
    frag["fragments_scores"].append((sumConScore_cv, sumConScore_theta, sumConScore_distance, sumConScore_phi))

    # TEST CONTINOUS
    A = sorted([frag["fragments_scores"][0][0], compare_scores[0]])
    B = sorted([frag["fragments_scores"][0][1], compare_scores[1]])
    C = sorted([frag["fragments_scores"][0][2], compare_scores[2]])
    D = sorted([frag["fragments_scores"][0][3], compare_scores[3]])
    if A[1] > 0:
        A = A[0] / A[1]
    else:
        A = 1
    if B[1] > 0:
        B = B[0] / B[1]
    else:
        B = 1
    if C[1] > 0:
        C = C[0] / C[1]
    else:
        C = 1
    if D[1] > 0:
        D = D[0] / D[1]
    else:
        D = 1
    Fa = identity[0] / 100.0
    Fb = identity[1] / 100.0
    Fc = identity[2] / 100.0
    Fd = identity[3] / 100.0
    # NOTE: Temporarly deactived. Activate only if verbose
    if False and (A >= Fa and B >= Fb and C >= Fc and D >= Fd):
        # print "Fragment...."
        # for pos in frag["continous_locations"][0]:
        #       print protein[pos][-3],
        print()
        print("=====================Scores Frag.:", len(frag["fragments_bounds"]), "==================")
        print("List:", frag["fragments_bounds"])
        print("Score CV:             ", frag["fragments_scores"][0][0], compare_scores[0], A, Fa, A >= Fa)
        print("Score angle vectors:  ", frag["fragments_scores"][0][1], compare_scores[1], B, Fb, B >= Fb)
        print("Score distance:       ", frag["fragments_scores"][0][2], compare_scores[2], C, Fc, C >= Fc)
        print("Score angle distance: ", frag["fragments_scores"][0][3], compare_scores[3], D, Fd, D >= Fd)
        print("================================================================================")

    if A >= Fa and B >= Fb and C >= Fc and D >= Fd:
        return frag, True
    else:
        return None, False


def test_solution_fragment(frag, compare_scores, diagonals, identity, verbose=False):
    # verbose = True
    solu = {"fragments_bounds": [], "sequence_of_chains": [], "border_of_cvs": {}}
    cvs = []
    for fra in frag:
        solu["fragments_bounds"] += fra["fragments_bounds"]
        solu["sequence_of_chains"] += [fra["chain"]]
        if fra["chain"] not in solu["border_of_cvs"]:
            solu["border_of_cvs"][fra["chain"]] = len(cvs)
            cvs += diagonals[fra["chain"]][1]

    # print "Sequence of chains-------",solu["sequence_of_chains"]
    if all(i == frag[0]["chain"] for i in solu["sequence_of_chains"]):
        protein, cvs = diagonals[frag[0]["chain"]]
        solu, cvs = compute_scores(solu, cvs, matrix=protein, verbose=verbose)
    else:
        solu, cvs = compute_scores(solu, cvs, verbose=verbose, diagonals=diagonals)

    if solu == None:
        # print "Solution not compatible"
        return None, cvs, False

    # TEST JUMPS
    for i in range(len(solu["jumps_scores"])):
        A = sorted([solu["jumps_scores"][i][2], compare_scores[i][2]])
        B = sorted([solu["jumps_scores"][i][3], compare_scores[i][3]])
        # B2 = sorted([solu["jumps_scores"][i][3]-(56*5),compare_scores[i][3]])
        C = sorted([solu["jumps_scores"][i][4], compare_scores[i][4]])
        D = sorted([solu["jumps_scores"][i][5], compare_scores[i][5]])
        A = A[0] / A[1]
        # B2 = B2[0]/B2[1]
        B = B[0] / B[1]
        C = C[0] / C[1]
        D = D[0] / D[1]
        Fa = identity[4] / 100.0
        Fb = identity[5] / 100.0
        Fc = identity[6] / 100.0
        Fd = identity[7] / 100.0

        # verbose = True
        # Temporarly deactived.NOTE: should be activated only if verbose
        if verbose:  # and (A>=Fa and B>=Fb and D>=Fd and C>=Fc):
            print("=====================Scores Jump.:", len(solu["jumps_locations"]), "==================")
            print("List: ", solu["jumps_locations"])
            print("Score CV:             ", solu["jumps_scores"][i][2], compare_scores[i][2], A, Fa, A >= Fa)
            print("Score angle vectors:  ", solu["jumps_scores"][i][3], compare_scores[i][3], B, Fb, B >= Fb)
            # print "Score angle vectors alt:  ",solu["jumps_scores"][i][3]-(56*5),compare_scores[i][3],B2,Fb,B2>=Fb
            print("Score distance:       ", solu["jumps_scores"][i][4], compare_scores[i][4], C, Fc, C >= Fc)
            print("Score angle distance: ", solu["jumps_scores"][i][5], compare_scores[i][5], D, Fd, D >= Fd)
            print("================================================================================")

        if not (A >= Fa and B >= Fb and C >= Fc and D >= Fd):
            return None, cvs, False

    return solu, cvs, True


def extract_models(pattern, protein, structure, cvs, sequence, identity, stepdiag, ssbridge, connectivity,
                   lengthFragment=3):
    listDiscoveredFrags = extract_single_fragments(pattern, protein, structure, cvs, sequence, identity, stepdiag,
                                                 ssbridge, connectivity, lengthFragment=lengthFragment)
    if len(listDiscoveredFrags) == 0:
        return [], {}

    diagonals = {}

    if len(protein.keys()) > 0:
        r = [k for k in protein]
        chainid = protein[r[0]][5][0][2]
        diagonals[chainid] = (protein, cvs)
        for cdf in range(len(listDiscoveredFrags)):
            for cdh in range(len(listDiscoveredFrags[cdf])):
                listDiscoveredFrags[cdf][cdh]["chain"] = chainid

    return use_fragments_to_extract_models(listDiscoveredFrags, pattern, diagonals, structure, sequence, identity, stepdiag,
                                       ssbridge, connectivity, lengthFragment=lengthFragment), diagonals

def extract_single_fragments(pattern, protein, structure, cvs, sequence, identity, stepdiag, ssbridge, connectivity,
                             lengthFragment=3, breakifnofrags=True):
    dictio_cont = {}
    if len(protein) > 1:
        try:
            print ("Number of theoretical matrix elements: ", protein["n"] ** 2, "Number of stored matrix entries: ", len(protein.keys()) - 1, "Chain ID:", protein.values()[0][5][0][2])
        except:
            pass
    else:
        return []

    sys.stdout.flush()
    solutions = []  # it will contain the complete solutions
    listDiscoveredFrags = [[] for _ in range(len(pattern["fragments_bounds"]))]
    # 1: iterate over all kind of fragments
    startNew = 0
    pattern["frag_priority"] = {}
    for i in range(len(pattern["fragments_bounds"])):
        fra_i = pattern["fragments_bounds"][i]
        pattern["frag_priority"][str(i)] = i
        n = fra_i[1] - fra_i[0]
        seq = ""
        # We have just a (cv,cv)
        level_i = []
        firstrun = True
        threshcontdin = 0
        while firstrun or (len(level_i) <= 10 and threshcontdin <= 10):
            firstrun = False
            level_i = []
            iden_copy = list(copy.deepcopy(identity))
            iden_copy[0] -= threshcontdin
            iden_copy[1] -= threshcontdin
            iden_copy[2] -= threshcontdin

            if n == 1 and fra_i[0] == fra_i[1]:
                # Inspecting the diagonal
                for j in range(protein["n"]):
                    bounds = [j, j]
                    fra_j = {"fragments_bounds": [bounds]}
                    # print "Working with",fra_j
                    fra_j, result = test_continous_fragment(fra_j, pattern["fragments_scores"][i], protein, iden_copy)
                    if result:
                        level_i.append(fra_j)
            else:
                if len(sequence) > 0:
                    seq = sequence[startNew:startNew + n + lengthFragment]
                startNew = startNew + n + lengthFragment

                # Inspecting the diagonal+1
                for j in range(0, protein["n"], stepdiag):
                    if j + n >= protein["n"]:
                        continue
                    bounds = [j, j + n]
                    fra_j = {"fragments_bounds": [bounds]}
                    # print "Working with",fra_j
                    fra_j, result = test_continous_fragment(fra_j, pattern["fragments_scores"][i], protein, iden_copy)

                    if result:
                        level_i.append(fra_j)
            if len(level_i) <= 10:
                # print "No solutions available for fragment n.: ",i
                # return solutions
                threshcontdin += 1
            else:
                print("N. of selected fragments for the reference n.:", i, "is", len(
                    level_i), "with percentage identity at", identity[0] - threshcontdin)
                random.shuffle(level_i)
                listDiscoveredFrags[i] += level_i
                break
                # for diret in level_i:
                #   print diret["fragments_bounds"]
        if len(level_i) == 0:
            print("No solutions available for fragment n.: ", i)
            if breakifnofrags:
                return solutions
            else:
                listDiscoveredFrags[i] += level_i
        elif len(level_i) <= 10:
            print("N. of selected fragments for the reference n.:", i, "is", len(level_i), "with percentage identity at", identity[0] - threshcontdin)
            random.shuffle(level_i)
            listDiscoveredFrags[i] += level_i

    return listDiscoveredFrags

def process_structure(pdbf, pattern, sequence, ncssearch, remove_redundance, identity, stepdiag, ssbridge,
                      peptide_length, connectivity, weight, sensitivity_ah, sensitivity_bs, processed_cvlist=[]):
    all_solutions = []
    strucc2 = None
    lisSS = None
    graph_full_reference, strucc, matrix, m_cvs, highd = annotate_pdb_model_with_aleph(pdbf,
                                                                                              weight=weight,
                                                                                              min_diff_ah=sensitivity_ah,
                                                                                              min_diff_bs=sensitivity_bs,
                                                                                              peptide_length=peptide_length,
                                                                                              write_pdb=False,
                                                                                              is_model=False)
    lisSS = get_all_fragments(graph_full_reference)

    if len(processed_cvlist) == 0:
        original = pdbf
        pdbsearch = ""
        tupleResult = None
        stru = None
        if os.path.exists(pdbf):
            stru = Bioinformatics3.get_structure("ref", pdbf)
        else:
            stru = Bioinformatics3.get_structure("ref", io.StringIO(SystemUtility.py2_3_unicode(pdbf)))

        reference = Bioinformatics3.get_list_of_atoms(stru, model=stru.get_list()[0].get_id()) # Analyzing just the first model no multiple NMR
        pdbmod, cnv = Bioinformatics3.get_pdb_from_list_of_atoms(reference, renumber=False, uniqueChain=False)
        pdbmod = "MODEL " + str(stru.get_list()[0].get_id()) + "\n" + pdbmod + "\n\n"
        pdbsearch += pdbmod
        # print pdbsearch
        pdbf = io.StringIO(SystemUtility.py2_3_unicode(pdbsearch))

        if ncssearch:
            strucc2, cvs_list = parse_pdb_and_generate_cvs(pdbf, peptide_length=peptide_length, one_model_per_nmr=True, only_reformat=True)
            listallfrags = [[] for _ in range(len(pattern["fragments_bounds"]))]
            diagonals = {}
            for cvs in cvs_list:
                graph_protein, strucc2, protein, protein_cvs, highd_reference = generate_matrix_and_graph(strucc2, cvs, pdbf,
                weight=weight,
                min_diff_ah=sensitivity_ah,
                min_diff_bs=sensitivity_bs,
                write_pdb=False,
                is_model=False,
                just_diagonal_plus_one = True,
                mixed_chains=False)
                listDiscoveredFrags = extract_single_fragments(pattern, protein, strucc2, protein_cvs, sequence, identity,
                                                               stepdiag, ssbridge, connectivity,
                                                               lengthFragment=peptide_length, breakifnofrags=False)
                if len(listDiscoveredFrags) == 0:
                    continue

                if len(protein.keys()) > 0:
                    chainid = protein.values()[0][5][0][2]
                    diagonals[chainid] = (protein, protein_cvs)
                    for cdf in range(len(listDiscoveredFrags)):
                        for cdh in range(len(listDiscoveredFrags[cdf])):
                            listDiscoveredFrags[cdf][cdh]["chain"] = chainid
                        listallfrags[cdf] += listDiscoveredFrags[cdf]

            solutions = use_fragments_to_extract_models(listallfrags, pattern, diagonals, strucc2, sequence, identity,
                                                        stepdiag, ssbridge, connectivity, lengthFragment=peptide_length)
            solutions = get_list_of_atoms(strucc2, solutions, diagonals)
            all_solutions += solutions
        else:
            strucc2, cvs_list = parse_pdb_and_generate_cvs(pdbf, peptide_length=peptide_length, one_model_per_nmr=True, only_reformat=not remove_redundance)
            for cvs in cvs_list:
                graph_protein, strucc2, protein, protein_cvs, highd_reference = generate_matrix_and_graph(strucc2, cvs,
                                                                                                          pdbf,
                                                                                                          weight=weight,
                                                                                                          min_diff_ah=sensitivity_ah,
                                                                                                          min_diff_bs=sensitivity_bs,
                                                                                                          write_pdb=False,
                                                                                                          is_model=False,
                                                                                                          just_diagonal_plus_one=False,
                                                                                                          mixed_chains=False)
                solutions, diagonals = extract_models(pattern, protein, strucc2, protein_cvs, sequence, identity,
                                                      stepdiag, ssbridge, connectivity, lengthFragment=peptide_length)
                # solutions = removeEqualSolutions(solutions)
                solutions = get_list_of_atoms(strucc2, solutions, diagonals)
                # for frag in solutions[0][2]:
                #       print frag
                #       print "======================================================================="
                all_solutions += solutions
    else:
        # TODO: Check if also when BORGES_MATRIX is started in a Grid (e.g.: Condor) ncsearch is performed.
        # This block is used when matrices are read from shelves in .data file.
        pdbread = io.StringIO(SystemUtility.py2_3_unicode(pdbf))
        if ncssearch:
            listallfrags = [[] for _ in range(len(pattern["fragments_bounds"]))]
            diagonals = {}
            for qw in range(len(processed_cvlist)):
                protein = processed_cvlist[qw][0]
                protein_cvs = processed_cvlist[qw][1]
                listDiscoveredFrags = extract_single_fragments(pattern, protein, strucc2, protein_cvs, sequence, identity,
                                                               stepdiag, ssbridge, connectivity,
                                                               lengthFragment=peptide_length, breakifnofrags=False)
                if len(listDiscoveredFrags) == 0:
                    continue

                if len(protein.keys()) > 0:
                    chainid = protein.values()[0][5][0][2]
                    diagonals[chainid] = (protein, protein_cvs)
                    for cdf in range(len(listDiscoveredFrags)):
                        for cdh in range(len(listDiscoveredFrags[cdf])):
                            listDiscoveredFrags[cdf][cdh]["chain"] = chainid
                        listallfrags[cdf] += listDiscoveredFrags[cdf]

                solutions = use_fragments_to_extract_models(listallfrags, pattern, diagonals, strucc2, sequence, identity,
                                                            stepdiag, ssbridge, connectivity, lengthFragment=peptide_length)
                solutions = get_list_of_atoms(strucc2, solutions, diagonals)
                all_solutions += solutions
        else:
            for qw in range(len(processed_cvlist)):
                protein = processed_cvlist[qw][0]
                protein_cvs = processed_cvlist[qw][1]
                solutions, diagonals = extract_models(pattern, protein, strucc2, protein_cvs, sequence, identity,
                                                      stepdiag, ssbridge, connectivity, lengthFragment=peptide_length)
                solutions = get_list_of_atoms(strucc2, solutions, diagonals)
                all_solutions += solutions

    print("Number of models extracted before clustering: ", len(all_solutions))
    return strucc2, all_solutions, lisSS

def process_structure_with_signature(idname,structure_reference,graph_no_coil_reference,matrix_reference, cvs_reference, structure_target, graph_no_coil_target, matrix_target, cvs_target, saved,justBackbone,DicParameters):
    clusts = []
    solutions = []
    structure = structure_target
    lisBigSS = get_all_fragments(graph_no_coil_target)

    r = 0
    for solu in saved:
        pdbe = None
        if justBackbone:
            pdbe = solu[1]
        else:
            g2 = graph_no_coil_target.vs.select(name_in=solu[3]).subgraph()
            pdbe = get_pdb_string_from_graph(g2, structure_target, chainid="B", renumber=False, uniqueChain=False,
                                             extends=4, polyala=False)

        restrictions_edges = {tuple(sorted(n1.split("-"))): tuple(sorted(n2.split("-"))) for (n1, n2) in zip(solu[4], solu[5])}
        #print("TRYING THIS ASSOCIATIONS:",restrictions_edges)
        ng1 = [n[0] for n in restrictions_edges.keys()] + [n[1] for n in restrictions_edges.keys()]
        ng2 = [n[0] for n in restrictions_edges.values()] + [n[1] for n in restrictions_edges.values()]

        map_reference = {tuple(res): frag["name"] for frag in graph_no_coil_reference.vs for res in frag["reslist"] if
                         frag["name"] in ng1}
        map_target = {tuple(res): frag["name"] for frag in graph_no_coil_target.vs for res in frag["reslist"] if
                      frag["name"] in ng2}

        # print(type(solu[0]))
        # print(type(pdbe))

        dictio_super = perform_superposition(reference=(
            io.StringIO(SystemUtility.py2_3_unicode(solu[0])), structure_reference, graph_no_coil_reference.vs.select(name_in=ng1).subgraph(),
            matrix_reference, cvs_reference), target=(
            io.StringIO(SystemUtility.py2_3_unicode(pdbe)), structure_target, graph_no_coil_target.vs.select(name_in=ng2).subgraph(),
            matrix_target, cvs_target),
            sensitivity_ah=0.000001,
            sensitivity_bs=0.000001,
            peptide_length=DicParameters["peptide_length"],
            write_graphml=False, write_pdb=False, ncycles=DicParameters["ncycles"],
            deep=DicParameters["deep"], top=DicParameters["top"], max_sec=5, break_sec=300, min_correct=2,
            gui=None, sampling=DicParameters["sampling"],
            core_percentage=DicParameters["core_percentage"],
            criterium_selection_core=DicParameters["criterium_selection_core"],
            force_core_expansion_through_secstr=DicParameters["force_core_expansion_through_secstr"],
            restrictions_edges=restrictions_edges, map_reference=map_reference,
            map_target=map_target, signature_threshold=DicParameters["signature_threshold"], verbose=False)
        pdbacc = None
        if dictio_super and dictio_super["rmsd"] <= DicParameters["maxRMSD"]:
            pdbacc = dictio_super["pdb_target"]

        pdball = ""
        if pdbacc is not None:
            structure_target_acc = Bioinformatics3.get_structure("uff",io.StringIO(SystemUtility.py2_3_unicode(pdbacc)))
            aaa = solu[2]
            bbb = solu[3]
            ccc = solu[4]
            ddd = solu[5]

            gg1 = igraph.Graph(n=len(aaa))
            gg1.vs["name"] = aaa
            gg2 = igraph.Graph(n=len(bbb))
            gg2.vs["name"] = bbb
            ccc = [(gg1.vs.find(name=cc.split("-")[0]),gg1.vs.find(name=cc.split("-")[1])) for cc in ccc]
            gg1.add_edges(ccc)
            ddd = [(gg2.vs.find(name=dd.split("-")[0]), gg2.vs.find(name=dd.split("-")[1])) for dd in ddd]
            gg2.add_edges(ddd)

            isom = gg2.get_subisomorphisms_vf2(gg1)
            restri = []
            for iso in isom:
                uno = gg1.vs["name"]
                due = [gg2.vs[ind]["name"] for ind in iso]
                restri.append({k:v for k,v in zip(uno,due)})

            dictus = Bioinformatics3.get_CA_distance_dictionary(
                io.StringIO(SystemUtility.py2_3_unicode(solu[0])),
                io.StringIO(SystemUtility.py2_3_unicode(pdbacc)), max_rmsd=100.0, last_rmsd=100.0,
                recompute_rmsd=False, cycles=1, cycle=1, before_apply=None,
                get_superposed_atoms=False, force_reference_residues=True, data_tuple = (graph_no_coil_reference, graph_no_coil_target, restri, map_reference, map_target))

            structure_target_acc = Bioinformatics3.set_occupancy_to_zero_for_outliers(structure_target_acc,0,dictus)
            pdbacc = Bioinformatics3.get_pdb_from_structure(structure_target_acc,0)

            print("Model:", idname, 0, r, "rmsd:", dictio_super["rmsd"])
            pdball += "REMARK TITLE " + os.path.basename(idname) + "\n"
            pdball += pdbacc
            tuplos = [(idname, 0, r)]
            solutions.append(pdball)
            clusts.append(tuplos)
            r += 1

    return structure, solutions, lisBigSS, clusts


def start_new_process_pdb(pdbsearch, pdbf, DicParameters, doCluster=True, getStructure=False, justBackbone=True, processed_cvlist=[], size_tree=5, classic=False):
    try:
        if not os.path.exists(pdbsearch):
            inpu1 = io.StringIO(SystemUtility.py2_3_unicode(pdbsearch))
        else:
            inpu1 = pdbsearch

        if not os.path.exists(pdbf):
            inpu2 = io.StringIO(SystemUtility.py2_3_unicode(pdbf))
        else:
            inpu2 = pdbf
            nombre = os.path.basename(inpu2)[:-4]

        graph_no_coil_reference, matrix_reference, cvs_reference, structure_reference, graph_no_coil_target, matrix_target, cvs_target, structure_target, signature_ref, signature_targ, possibilities, collections = compare_structures(
            inpu1, inpu2, DicParameters["sensitivity_ah"], DicParameters["sensitivity_bs"], DicParameters["peptide_length"],
            False, False, ref_tuple=None,
            targ_tuple=None, core_percentage=DicParameters["core_percentage"],
            criterium_selection_core=DicParameters["criterium_selection_core"],
            force_core_expansion_through_secstr=DicParameters["force_core_expansion_through_secstr"], size_tree=size_tree, gui=False,
            rmsd_max=-1.0, ncycles=DicParameters["ncycles"], deep=DicParameters["deep"], top=DicParameters["top"],
            sampling=DicParameters["sampling"], write_pdbs=False,
            renumber=False, uniqueChain=False, search_in_both=False, biggest_is="reference", use_frequent_as_seed=False, signature_threshold=DicParameters["signature_threshold"], verbose=True)

        # blo = get_pdb_string_from_graph(graph_no_coil_reference, structure_reference, chainid="A", renumber=False, uniqueChain=False)
        # flo = open("tocco.pdb", "w")
        # flo.write(blo)
        # flo.close()
        #
        # clo = get_pdb_string_from_graph(graph_no_coil_target, structure_target, chainid="A", renumber=False, uniqueChain=False)
        # flo = open("rocco.pdb", "w")
        # flo.write(clo)
        # flo.close()

        saved = []
        for collection in collections:
            for colle in collection:
                #print(len(colle[2]),len(colle[3]),graph_no_coil_reference.vcount())
                if len(colle[2]) == len(colle[3]) == graph_no_coil_reference.vcount():
                    saved.append(colle)

        if len(saved) == 0:
            if getStructure:
                return ("", [], [], None, [])
            else:
                return ("", [], [], [])
        else:
            ng2 = set([s for save in saved for s in save[3]])
            g2 = graph_no_coil_target.vs.select(name_in=ng2).subgraph()
            pdbf = get_pdb_string_from_graph(g2, structure_target, chainid="B", renumber=False, uniqueChain=False,extends=4)
            # flo = open("cocco.pdb","w")
            # flo.write(pdbf)
            # flo.close()
            #pdbf = io.StringIO(SystemUtility.py2_3_unicode(pdbf))

        if os.path.exists(pdbf):
            idname = os.path.basename(pdbf)[:-4].split("_")[0]
        else:
            idname = nombre

        if classic:
            print("================= The size of the fragment for computing a CV is:", DicParameters["peptide_length"], "aa.======================")
            structure, solutions, lisBigSS = process_structure(pdbf, DicParameters["pattern"],
                                                               DicParameters["sequenceLocate"], DicParameters["ncssearch"],
                                                               DicParameters["remove_redundance"],
                                                               DicParameters["identity"], DicParameters["stepdiag"],
                                                               DicParameters["ssbridge"], DicParameters["peptide_length"],
                                                               DicParameters["connectivity"], DicParameters["weight"],
                                                               DicParameters["sensitivity_ah"], DicParameters["sensitivity_bs"],
                                                               processed_cvlist=processed_cvlist)


            #TODO: important change for debugging
            minforcl = 10000000000 #5
            if not doCluster or DicParameters["representative"]:
                minforcl = 99999999999

            start = int(math.floor(numpy.sqrt(len(solutions) / 2.0)))
            #TODO: When finally rewrite clusterization and introduce Kmean through sklearn end should be end=2*start
            end = start #2*start
            # clusts = Bioinformatics.clusterizeByKMeans(DicParameters,"","",solutions,minForClust=minforcl,backbone=False,limitPercluster=None,minKappa=None,maxKappa=None,limitThreshold=-0.1,structure=structure,writeOutput=False)
            clusts = cluster_pdbs_by_kmeans(DicParameters, "", pdbsearch, solutions, DicParameters["sensitivity_ah"], DicParameters["sensitivity_bs"], DicParameters["peptide_length"],
                                        DicParameters["ncycles"], DicParameters["deep"], DicParameters["top"], DicParameters["sampling"], pdbf=pdbf,
                                                       minForClust=minforcl, backbone=False, limitPercluster=None,
                                                       minKappa=start, maxKappa=end, limitThreshold=-0.1,
                                                       structure=structure, writeOutput=False, core_percentage=DicParameters["core_percentage"], criterium_selection_core=DicParameters["criterium_selection_core"], force_core_expansion_through_secstr=DicParameters["force_core_expansion_through_secstr"])
        else:
             structure, solutions, lisBigSS, clusts = process_structure_with_signature(idname,structure_reference,graph_no_coil_reference,matrix_reference, cvs_reference, structure_target, graph_no_coil_target, matrix_target, cvs_target, saved,justBackbone,DicParameters)


        newSolList = []
        newSolRed = []
        for tuplos in clusts:
            if len(tuplos) == 0:
                continue
            cosa = tuplos[0]
            name = cosa[:3]
            pdbid, model, IdSolution = name
            print("choosing: ", pdbid, model, IdSolution)
            q = 0
            if classic:
                if justBackbone:
                    newSolList.append(Bioinformatics3.get_pdb_from_list_of_atoms(solutions[IdSolution][0]))
                else:
                    newSolList.append(Bioinformatics3.get_pdb_from_list_of_atoms(solutions[IdSolution][1]))
                    q = 1
                newSolRed.append(map(lambda x: Bioinformatics3.get_pdb_from_list_of_atoms(solutions[x[:3][2]][q]), tuplos[1:]))
            else:
                newSolList.append(solutions[IdSolution])

        if getStructure:
            return (idname, newSolList, lisBigSS, structure, newSolRed)
        else:
            return (idname, newSolList, lisBigSS, newSolRed)
    except:
        print("An error occured while parsing or decoding PDB ", pdbf, " PID: " + str(os.getpid()))
        print( sys.exc_info())
        traceback.print_exc(file=sys.stdout)
        t = datetime.datetime.now()
        epcSec = time.mktime(t.timetuple())
        now = datetime.datetime.fromtimestamp(epcSec)
        print("" + str(now.ctime()) + "\tError parsing or decoding: " + str(pdbf) + " PID: " + str(os.getpid()) + "\n" + str(sys.exc_info()) + "\n")
        # quit()
        if getStructure:
            return ("", [], [], None, [])
        else:
            return ("", [], [], [])

def create_pdbs(wdir, pdbsearch, pdbfstru, solutions, solred, pdbid, model, DicParameters,
                representative=False, superpose=True, superpose_exclude=1, return_pdbstring=False, nilges=10,
                full_pdb_superpose=None):
    global number_of_solutions

    if not return_pdbstring and not os.path.exists(os.path.join(wdir, "./library/")):
        # shutil.rmtree("./library/")
        os.makedirs(os.path.join(wdir, "./library"))

    allpdbfstru = None
    if isinstance(pdbfstru, str) and os.path.exists(pdbfstru):
        f = open(pdbfstru, "r")
        allpdbfstru = f.readlines()
        f.close()
    else:
        allpdbfstru = pdbfstru.readlines()

    title = ""
    for linea in allpdbfstru:
        lis = linea.split()
        if len(lis) > 1 and lis[0] == "TITLE":
            title += " ".join(lis[1:]) + "  "

    pdbsol = []
    allred = {}
    total = len(solutions)
    dictio_pdb_best = {}
    for p in range(len(solutions)):
        # NOTE: TEMPORANEO
        # Is this "for" block  really needed
        pda = ""
        for lineaA in solutions[p][0].splitlines():
            if lineaA.startswith("ATOM") or lineaA.startswith("HETATM"):
                for lineaB in allpdbfstru:
                    if lineaA[30:54] in lineaB and lineaA[16:20] in lineaB:
                        pda += lineaB
        # print pda
        write = True
        # NOTE: Activate next for debugging
        # superpose = False
        listrmsd = []
        if superpose:
            write = False
            # NOTE: Substituted the old getSuperimp with the new BORGES_MATRIX.perform_superposition
            # {"rmsd": best_rmsd, "size": best_size, "associations": asso, "transf": best_transf, "graph_ref": g_a, "grapf_targ": g_b, "correlation": corr,"pdb_target":pdbmod}
            # TODO: inside the functions that opens reference and target it must be checked if it is a path or not to not open it
            dictio_super = perform_superposition(reference=io.StringIO(SystemUtility.py2_3_unicode(pdbsearch)),
                                                 target=io.StringIO(SystemUtility.py2_3_unicode(pda)),
                                                 sensitivity_ah=DicParameters["sensitivity_ah"],
                                                 sensitivity_bs=DicParameters["sensitivity_bs"],
                                                 peptide_length=DicParameters["peptide_length"],
                                                 write_graphml=False, write_pdb=False, ncycles=DicParameters["ncycles"],
                                                 deep=DicParameters["deep"], top=DicParameters["top"],
                                                 gui=None, sampling=DicParameters["sampling"], core_percentage=DicParameters["core_percentage"], criterium_selection_core=DicParameters["criterium_selection_core"], force_core_expansion_through_secstr=DicParameters["force_core_expansion_through_secstr"], verbose=False)

            name = "" + str(pdbid) + "_" + str(model) + "_" + str(p) + ".pdb"
            if not dictio_super:
                print("Cannot superpose", name)
                rmsT = 100
                name = "" + str(pdbid) + "_" + str(model) + "_" + str(p) + ".pdb"
                pda = solutions[p][0]
                write = False
            else:
                pdacc = dictio_super["pdb_target"]
                rmsT = dictio_super["rmsd"]

            if rmsT >= DicParameters["minRMSD"] and rmsT <= DicParameters["maxRMSD"]:
                if representative and pdbid in dictio_pdb_best and rmsT < dictio_pdb_best[pdbid][1]:
                    os.remove(dictio_pdb_best[pdbid][0])
                    dictio_pdb_best[pdbid] = (os.path.join(wdir, "./library/" + name), rmsT)
                    print(name, rmsT, dictio_super["size"], title)
                    listrmsd.append((rmsT, name))
                    write = True
                elif representative and pdbid not in dictio_pdb_best:
                    dictio_pdb_best[pdbid] = (os.path.join(wdir, "./library/" + name), rmsT)
                    print(name, rmsT, dictio_super["size"], title)
                    listrmsd.append((rmsT, name))
                    write = True
                elif not representative:
                    print(name, rmsT, dictio_super["size"], title)
                    listrmsd.append((rmsT, name))
                    write = True

        if write:
            if not return_pdbstring:
                name = "" + str(pdbid) + "_" + str(model) + "_" + str(p) + ".pdb"
                f = open(os.path.join(wdir, "./library/" + name), "w")
                f.write(pdacc) #pda
                f.close()
                number_of_solutions += 1
                f = open(os.path.join(wdir, "library/" + "list_rmsd.txt"), "a")
                listrmsd = sorted(listrmsd)
                for pair in listrmsd:
                    f.write(pair[1] + "  " + str(pair[0]) + "\n")
                f.close()
            else:
                name = "" + str(pdbid) + "_" + str(model) + "_" + str(p) + ".pdb"
                pdbsol.append((name, pdacc)) #pda
                allred["" + str(pdbid) + "_" + str(model) + "_" + str(p)] = []
                for pda2 in solred[p]:
                    name2 = "" + str(pdbid) + "_" + str(model) + "_" + str(total) + ".pdb"
                    allred["" + str(pdbid) + "_" + str(model) + "_" + str(p)].append((name2, pda2))
                    total += 1

    return pdbsol, allred

def start_new_process(wdir, pdbsearch, pdbstruc, DicParameters, doCluster, backbone, cvs_list_str, superpose, idn,
                      return_pdbstring, thresh, superpose_exclude, extract_superposed_pdbs):
    # NOTE: Activate next line for debugging
    # doCluster = False
    try:
        niceness = os.nice(0)
        os.nice(5 - niceness)
    except:
        pass

    #TODO: For now the superposition against the full_pdb_superpose is not implemented in perform_superposition
    if extract_superposed_pdbs:
        full_pdb_superpose = pdbstruc
    else:
        full_pdb_superpose = None

    (idname, solList, lisBigSS, solred) = start_new_process_pdb(pdbsearch, pdbstruc, DicParameters, doCluster=doCluster,
                                                                justBackbone=backbone, processed_cvlist=cvs_list_str, classic=DicParameters["classic"])

    if len(lisBigSS) == 0:
        lisBigSS = [{"model": 0}]

    if len(solList) > 0:
        if DicParameters["classic"]:
            if len(cvs_list_str) > 0:
                idname = idn
                if return_pdbstring:
                    return create_pdbs(wdir, pdbsearch, io.StringIO(SystemUtility.py2_3_unicode(pdbstruc)), solList, solred, idname,
                                       lisBigSS[0]["model"], DicParameters,
                                       superpose=superpose, return_pdbstring=return_pdbstring,
                                       superpose_exclude=superpose_exclude, nilges=DicParameters["nilges"],
                                       representative=DicParameters["representative"], full_pdb_superpose=full_pdb_superpose)
                else:
                    if doCluster:
                        pdbsols, solred = create_pdbs(wdir, pdbsearch, io.StringIO(SystemUtility.py2_3_unicode(pdbstruc)), solList, solred, idname,
                                                      lisBigSS[0]["model"], DicParameters,
                                                      superpose=superpose, return_pdbstring=True,
                                                      superpose_exclude=superpose_exclude, nilges=DicParameters["nilges"],
                                                      representative=DicParameters["representative"],
                                                      full_pdb_superpose=full_pdb_superpose)
                        cluster_by_rmsd(os.path.join(wdir, "./library"), pdbsols, solred, thresh, superpose_exclude, DicParameters["nilges"], DicParameters["weight"],
                                        DicParameters["sensitivity_ah"], DicParameters["sensitivity_bs"], DicParameters["peptide_length"], DicParameters["ncycles"],
                                        DicParameters["deep"], DicParameters["top"], DicParameters["sampling"], full_pdb_superpose=full_pdb_superpose, core_percentage=DicParameters["core_percentage"], criterium_selection_core=DicParameters["criterium_selection_core"], force_core_expansion_through_secstr=DicParameters["force_core_expansion_through_secstr"])
                    else:
                        create_pdbs(wdir, pdbsearch, io.StringIO(SystemUtility.py2_3_unicode(pdbstruc)), solList, solred, idname,
                                    lisBigSS[0]["model"], DicParameters,
                                    superpose=superpose, return_pdbstring=False, superpose_exclude=superpose_exclude,
                                    nilges=DicParameters["nilges"], representative=DicParameters["representative"],
                                    full_pdb_superpose=full_pdb_superpose)

            else:
                if os.path.exists(pdbstruc):
                    if return_pdbstring:
                        return create_pdbs(wdir, pdbsearch, pdbstruc, solList, solred, idname, lisBigSS[0]["model"],
                                           DicParameters, superpose=superpose,
                                           return_pdbstring=return_pdbstring, superpose_exclude=superpose_exclude,
                                           nilges=DicParameters["nilges"], representative=DicParameters["representative"],
                                           full_pdb_superpose=full_pdb_superpose)
                    else:
                        if doCluster:
                            pdbsols, solred = create_pdbs(wdir, pdbsearch, pdbstruc, solList, solred, idname,
                                                          lisBigSS[0]["model"], DicParameters,
                                                          superpose=superpose, return_pdbstring=True,
                                                          superpose_exclude=superpose_exclude, nilges=DicParameters["nilges"],
                                                          representative=DicParameters["representative"],
                                                          full_pdb_superpose=full_pdb_superpose)
                            cluster_by_rmsd(os.path.join(wdir, "./library"), pdbsols, solred, thresh, superpose_exclude,
                                            DicParameters["nilges"], DicParameters["weight"],
                                            DicParameters["sensitivity_ah"], DicParameters["sensitivity_bs"],
                                            DicParameters["peptide_length"], DicParameters["ncycles"],
                                            DicParameters["deep"], DicParameters["top"], DicParameters["sampling"],
                                            full_pdb_superpose=full_pdb_superpose, core_percentage=DicParameters["core_percentage"], criterium_selection_core=DicParameters["criterium_selection_core"], force_core_expansion_through_secstr=DicParameters["force_core_expansion_through_secstr"])
                        else:
                            create_pdbs(wdir, pdbsearch, pdbstruc, solList, solred, idname, lisBigSS[0]["model"],
                                        DicParameters, superpose=superpose,
                                        return_pdbstring=False, superpose_exclude=superpose_exclude, nilges=DicParameters["nilges"],
                                        representative=DicParameters["representative"],
                                        full_pdb_superpose=full_pdb_superpose)

                else:
                    idname = idn
                    if return_pdbstring:
                        return create_pdbs(wdir, pdbsearch, io.StringIO(SystemUtility.py2_3_unicode(pdbstruc)), solList, solred, idname,
                                           lisBigSS[0]["model"], DicParameters,
                                           superpose=superpose, return_pdbstring=return_pdbstring,
                                           superpose_exclude=superpose_exclude, nilges=DicParameters["nilges"],
                                           representative=DicParameters["representative"],
                                           full_pdb_superpose=full_pdb_superpose)
                    else:
                        if doCluster:
                            pdbsols, solred = create_pdbs(wdir, pdbsearch, io.StringIO(SystemUtility.py2_3_unicode(pdbstruc)), solList, solred,
                                                          idname, lisBigSS[0]["model"],
                                                          DicParameters, superpose=superpose, return_pdbstring=True,
                                                          superpose_exclude=superpose_exclude, nilges=DicParameters["nilges"],
                                                          representative=DicParameters["representative"],
                                                          full_pdb_superpose=full_pdb_superpose)
                            cluster_by_rmsd(os.path.join(wdir, "./library"), pdbsols, solred, thresh, superpose_exclude,
                                            DicParameters["nilges"], DicParameters["weight"],
                                            DicParameters["sensitivity_ah"], DicParameters["sensitivity_bs"],
                                            DicParameters["peptide_length"], DicParameters["ncycles"],
                                            DicParameters["deep"], DicParameters["top"], DicParameters["sampling"],
                                            full_pdb_superpose=full_pdb_superpose, core_percentage=DicParameters["core_percentage"],criterium_selection_core=DicParameters["criterium_selection_core"], force_core_expansion_through_secstr=DicParameters["force_core_expansion_through_secstr"])
                        else:
                            create_pdbs(wdir, pdbsearch, io.StringIO(SystemUtility.py2_3_unicode(pdbstruc)), solList, solred, idname,
                                        lisBigSS[0]["model"], DicParameters,
                                        superpose=superpose, return_pdbstring=False, superpose_exclude=superpose_exclude,
                                        nilges=DicParameters["nilges"], representative=DicParameters["representative"],
                                        full_pdb_superpose=full_pdb_superpose)
        else:
            basename = os.path.join(wdir, "./library")
            if not os.path.exists(basename):
                os.makedirs(basename)

            for q, sol in enumerate(solList):
                nome = os.path.join(basename,idname+"_"+str(lisBigSS[0]["model"])+"_"+str(q)+".pdb")
                with open(nome, "w") as f:
                    f.write(sol)
    else:
        return [], {}

def evaluate_pdb(sym, wdir, pdbf, cvs_list_str, pdbstruc, strucc, lisBig, i, pattern, pattern_cvs, highd,
                 doCluster, superpose, process_join, pdbsearch, pdbn, thresh, superpose_exclude,
                 extract_superposed_pdbs, peptide_length, sequence, ncssearch, multimer, c_angle, c_dist,
                 c_angle_dist, c_cvl_diff, j_angle, j_dist, j_angle_dist, j_cvl_diff, rmsd_min, rmsd_max,
                 step_diag, ssbridge, connectivity, nilges, enhance_fold, representative, pdb_model,
                 sidechains, weight, sensitivity_ah, sensitivity_bs, ncycles, deep, top, sampling, core_percentage, criterium_selection_core, force_core_expansion_through_secstr, classic, signature_threshold, return_pdbstring=False):

    global number_of_solutions

    #lisBig = sorted(lisBig, key=lambda x: x["fragLength"], reverse=True)
    DicParameters = {}
    DicParameters["nameExecution"] = "WOW"
    DicParameters["structure"] = strucc
    DicParameters["cvsModel"] = pattern_cvs
    DicParameters["pattern"] = pattern
    DicParameters["listFragments"] = lisBig
    DicParameters["highest_distance"] = highd
    DicParameters["sequenceLocate"] = sequence
    DicParameters["ncssearch"] = ncssearch
    DicParameters["remove_redundance"] = multimer
    DicParameters["identity"] = (
        float(c_cvl_diff), float(c_angle), float(c_dist), float(c_angle_dist),  float(j_cvl_diff), float(j_angle),
        float(j_dist), float(j_angle_dist))
    DicParameters["minRMSD"] = float(rmsd_min)
    DicParameters["maxRMSD"] = float(rmsd_max)
    DicParameters["stepdiag"] = int(step_diag)
    DicParameters["ssbridge"] = bool(ssbridge)
    DicParameters["connectivity"] = bool(connectivity)
    DicParameters["nilges"] = int(nilges)
    DicParameters["enhance_fold"] = bool(enhance_fold)
    DicParameters["peptide_length"] = int(peptide_length)
    DicParameters["representative"] = bool(representative)
    DicParameters["weight"] = weight
    DicParameters["sensitivity_ah"] = sensitivity_ah
    DicParameters["sensitivity_bs"] = sensitivity_bs
    DicParameters["ncycles"] = ncycles
    DicParameters["deep"] = deep
    DicParameters["top"] = top
    DicParameters["sampling"] = sampling
    DicParameters["core_percentage"] = core_percentage
    DicParameters["criterium_selection_core"] = criterium_selection_core
    DicParameters["signature_threshold"] = signature_threshold
    DicParameters["force_core_expansion_through_secstr"] = force_core_expansion_through_secstr
    DicParameters["classic"] = classic

    # Case shelve .data
    if pdbf.endswith(".data"):
        cv_matrices_shelve = shelve.open(pdbf)
        for key in cv_matrices_shelve:
            if number_of_solutions > 0 and number_of_solutions % 1000 == 0:
                sym.spawn_function_with_multiprocessing(target=intermediate_clustering_library, args=(wdir, pdb_model, DicParameters))
                print("Evaluating structure n.", i + 1, key)
                cvs_list_str = cv_matrices_shelve[key]["cvs_list"]
                pdbstruc = cv_matrices_shelve[key]["structure"]
                if not return_pdbstring:
                    p = sym.spawn_function_with_multiprocessing(target=start_new_process, args=(
                                    wdir, pdbsearch, pdbstruc, DicParameters, doCluster, not sidechains,
                                    cvs_list_str, superpose, key, False, thresh, superpose_exclude,
                                    extract_superposed_pdbs))
                    if process_join:
                        p.join()
            else:
                return start_new_process(wdir, pdbsearch, pdbstruc, DicParameters, doCluster,
                                         not sidechains, cvs_list_str, superpose, key, True,
                                         thresh, superpose_exclude, extract_superposed_pdbs)

    # Case .pdb file
    else:
        if number_of_solutions > 0 and number_of_solutions % 1000 == 0:
            sym.spawn_function_with_multiprocessing(target=intermediate_clustering_library,
                                         args=(wdir, pdb_model, DicParameters))
        if os.path.exists(pdbf):
            print("Evaluating structure n.", i + 1, pdbf)
        else:
            print("Evaluating structure n.", i + 1)
        if not return_pdbstring:
            # Case real .pdb process the matrix
            if cvs_list_str == None and pdbstruc == None:
                if pdbn == "":
                    p = sym.spawn_function_with_multiprocessing(target=start_new_process, args=(
                        wdir, pdbsearch, pdbf, DicParameters, doCluster, not sidechains, [],
                        superpose, "", False, thresh, superpose_exclude, extract_superposed_pdbs))
                else:
                    p = sym.spawn_function_with_multiprocessing(target=start_new_process, args=(
                        wdir, pdbsearch, pdbf, DicParameters, doCluster, not sidechains, [],
                        superpose, pdbn, False, thresh, superpose_exclude, extract_superposed_pdbs))
            # Case .tar.gz use precomputed matrix coming from a .data
            else:
                p = sym.spawn_function_with_multiprocessing(target=start_new_process, args=(
                    wdir, pdbsearch, pdbstruc, DicParameters, doCluster, not sidechains,
                    cvs_list_str, superpose, pdbf, False, thresh, superpose_exclude,
                    extract_superposed_pdbs))
            if process_join:
                p.join()
        else:
            if cvs_list_str == None and pdbstruc == None:
                if pdbn == "":
                    return start_new_process(wdir, pdbsearch, pdbf, DicParameters, doCluster,
                                             not sidechains, [], superpose, "", True, thresh,
                                             superpose_exclude, extract_superposed_pdbs)
                else:
                    return start_new_process(wdir, pdbsearch, pdbf, DicParameters, doCluster,
                                             not sidechains, [], superpose, pdbn, True, thresh,
                                             superpose_exclude, extract_superposed_pdbs)
            # Case .tar.gz use precomputed matrix coming from a .data
            else:
                return start_new_process(wdir, pdbsearch, pdbstruc, DicParameters, doCluster,
                                         not sidechains, cvs_list_str, superpose, pdbf, True,
                                         thresh, superpose_exclude, extract_superposed_pdbs)

def evaluate_model(pdbmodel, enhance_fold, peptide_length, weight, sensitivity_ah, sensitivity_bs):
    graph_full_reference, strucc, pattern, pattern_cvs, highd = annotate_pdb_model_with_aleph(pdbmodel,
                                                                                                 weight=weight,
                                                                                                 min_diff_ah=sensitivity_ah,
                                                                                                 min_diff_bs=sensitivity_bs,
                                                                                                 peptide_length=peptide_length,
                                                                                                 write_pdb=False, is_model=True)

    all_frags = get_all_fragments(graph_full_reference)

    pdbsearch = Bioinformatics3.get_pdb_from_list_of_frags("0", all_frags, strucc, "", externalRes=[], normalize=False)[1]
    full_list = []
    lisBig = sorted(all_frags, key=lambda x: x["fragLength"], reverse=True)

    print_secondary_structure_elements(lisBig)

    if enhance_fold:
        if lisBig[-1]["fragLength"] % 2 == 0:
            peptide_length = lisBig[-1]["fragLength"] - 1
        else:
            peptide_length = lisBig[-1]["fragLength"] - 2

        graph_full_reference, strucc, pattern, pattern_cvs, highd = annotate_pdb_model_with_aleph(pdbmodel,
                                                                                                    weight=weight,
                                                                                                    min_diff_ah=sensitivity_ah,
                                                                                                    min_diff_bs=sensitivity_bs,
                                                                                                    peptide_length=peptide_length,
                                                                                                    write_pdb=False, is_model=True)
        all_frags = get_all_fragments(graph_full_reference)

        pdbsearch = Bioinformatics3.get_pdb_from_list_of_frags("0", all_frags, strucc, "", externalRes=[], normalize=False)[1]
        full_list = []
        lisBig = sorted(all_frags, key=lambda x: x["fragLength"], reverse=True)

        print_secondary_structure_elements(lisBig)

    print_pattern(pattern)

    return pattern, pattern_cvs, highd, pdbsearch, strucc, lisBig, peptide_length

@SystemUtility.timing
@SystemUtility.deprecated('Must be changed soon for a better cluster algorithm not based in references')
def cluster_by_rmsd(directory, pdbsol, solred, thresh, superpose_exclude, nilges, weight, sensitivity_ah, sensitivity_bs, peptide_length, ncycles, deep, top, sampling, full_pdb_superpose=None, core_percentage=-1, criterium_selection_core="residues", force_core_expansion_through_secstr=False):
    howmany = 0
    if not os.path.exists(directory):
        os.makedirs(directory)

    print("Start to clustering...", len(pdbsol))
    print("redundancy: ", len(solred))
    for root, subFolders, files in os.walk(directory):
        for fileu in files:
            if fileu.startswith("rmsd_list"):
                f = open(os.path.join(root, fileu), "r")
                allfiles = f.readlines()
                f.close()
                reference = None
                for line in allfiles:
                    if line.startswith("Reference"):
                        reference = os.path.join(root, line.split()[1])
                        howmany += 1
                        break

                #NOTE: before list of fragments was used to guide superpos,
                # graph_full_reference, stru, matrix_reference, cvs_reference, highd_reference = annotate_pdb_model_with_aleph(reference,
                #                                                                                             weight=weight,
                #                                                                                             min_diff_ah=sensitivity_ah,
                #                                                                                             min_diff_bs=sensitivity_bs,
                #                                                                                             peptide_length=peptide_length,
                #                                                                                             write_pdb=False)
                # all_frags = get_all_fragments(graph_full_reference)
                dds = open(reference, "r")
                modelpdbstring = dds.read()
                dds.close()
                remainings = []
                for it in range(len(pdbsol)):
                    item = pdbsol[it]
                    name, pda = item
                    listona = name.split("_")
                    pdbid = listona[0][:4]
                    model = listona[1]
                    IdSolution = listona[2]
                    if "." in list(IdSolution):
                        IdSolution, ext = IdSolution.split(".")
                    nomefile = os.path.join(root, str(pdbid) + "_" + str(model) + "_" + str(IdSolution) + ".pdb")
                    #NOTE: Substituted the old getSuperimp with the new BORGES_MATRIX.perform_superposition
                    # {"rmsd": best_rmsd, "size": best_size, "associations": asso, "transf": best_transf, "graph_ref": g_a, "grapf_targ": g_b, "correlation": corr,"pdb_target":pdbmod}
                    #TODO: inside the functions that opens reference and target it must be checked if it is a path or not to not open it
                    dictio_super = perform_superposition(reference=io.StringIO(SystemUtility.py2_3_unicode(modelpdbstring)), target=io.StringIO(SystemUtility.py2_3_unicode(pda)),
                                                   sensitivity_ah=sensitivity_ah,
                                                   sensitivity_bs=sensitivity_bs, peptide_length=peptide_length,
                                                   write_graphml=False, write_pdb=False, ncycles=ncycles, deep=deep,
                                                   top=top,
                                                   gui=None, sampling=sampling, core_percentage=core_percentage, criterium_selection_core=criterium_selection_core, force_core_expansion_through_secstr=force_core_expansion_through_secstr, verbose=False)
                    if not dictio_super:
                        print("Cannot superpose", name)
                        rmsdVALFar = 100
                    else:
                        pdacc = dictio_super["pdb_target"]
                        rmsdVALFar = dictio_super["rmsd"]


                    # print "---",pdbid,model,IdSolution,rmsdVALFar
                    if rmsdVALFar <= thresh:
                        flo = open(os.path.join(root, fileu), "a")
                        flo.write(str(pdbid) + " " + str(model) + " " + str(IdSolution) + " " + str(rmsdVALFar) + "\n")
                        flo.close()
                        fla = open(nomefile, "w")
                        fla.write(pdacc)
                        fla.close()
                        # print "Search redundant",""+str(pdbid)+" "+str(model)+" "+str(IdSolution)
                        for item2 in solred["" + str(pdbid) + "_" + str(model) + "_" + str(IdSolution)]:
                            name2, pda2 = item2
                            listona2 = name2.split("_")
                            pdbid2 = listona2[0][:4]
                            model2 = listona2[1]
                            IdSolution2 = listona2[2]
                            if "." in list(IdSolution2):
                                IdSolution2, ext2 = IdSolution2.split(".")
                            nomefile2 = os.path.join(root, str(pdbid2) + "_" + str(model2) + "_" + str(IdSolution2) + ".pdb")        
                            flo2 = open(os.path.join(root, fileu), "a")
                            flo2.write(str(pdbid2) + " " + str(model2) + " " + str(IdSolution2) + " --\n")
                            flo2.close()
                            fla2 = open(nomefile2, "w")
                            fla2.write(pda2[0])
                            fla2.close()
                    else:
                        remainings.append((name, pdacc))

                pdbsol = remainings
    howmany += 1
    if len(pdbsol) > 0:
        while len(pdbsol) > 0:
            remainings = []
            listmodel = []
            modelpdbstring = ""
            for i in range(len(pdbsol)):
                item = pdbsol[i]
                name, pda = item
                listona = name.split("_")
                pdbid = listona[0][:4]
                model = listona[1]
                IdSolution = listona[2]
                if "." in list(IdSolution):
                    IdSolution, ext = IdSolution.split(".")

                if i == 0:
                    writePath = os.path.join(directory, str(howmany))
                    if not os.path.exists(writePath):
                        os.makedirs(writePath)

                    howmany += 1
                    flo = open(os.path.join(writePath, "rmsd_list"), "a")
                    flo.write("Reference: " + os.path.basename(name) + "\n")
                    flo.close()
                    fla = open(os.path.join(writePath, name), "w")
                    fla.write(pda)
                    fla.close()

                    # NOTE: before list of fragments was used to guide superpos,
                    # graph_full_reference, stru, matrix_reference, cvs_reference, highd_reference= annotate_pdb_model_with_aleph(os.path.join(writePath, name),
                    #                                                                                             weight=weight,
                    #                                                                                             min_diff_ah=sensitivity_ah,
                    #                                                                                             min_diff_bs=sensitivity_bs,
                    #                                                                                             peptide_length=peptide_length,
                    #                                                                                             write_pdb=False)
                    # all_frags = get_all_fragments(graph_full_reference)
                    modelpdbstring = pda
                    # print "Reference",os.path.basename(name)
                    # print "Search redundant ",""+str(pdbid)+" "+str(model)+" "+str(IdSolution)
                    for item2 in solred["" + str(pdbid) + "_" + str(model) + "_" + str(IdSolution)]:
                        name2, pda2 = item2
                        listona2 = name2.split("_")
                        pdbid2 = listona2[0][:4]
                        model2 = listona2[1]
                        IdSolution2 = listona2[2]
                        if "." in list(IdSolution2):
                            IdSolution2, ext2 = IdSolution2.split(".")
                        nomefile2 = os.path.join(writePath,
                                                 str(pdbid2) + "_" + str(model2) + "_" + str(IdSolution2) + ".pdb")
                        # if rmsdVALFar2 <= thresh:
                        # print "write: ",str(pdbid2)+" "+str(model2)+" "+str(IdSolution2)
                        flo2 = open(os.path.join(writePath, "rmsd_list"), "a")
                        flo2.write(str(pdbid2) + " " + str(model2) + " " + str(IdSolution2) + " --\n")
                        flo2.close()
                        fla2 = open(nomefile2, "w")
                        fla2.write(pda2[0])
                        fla2.close()
                    continue

                nomefile = os.path.join(writePath, str(pdbid) + "_" + str(model) + "_" + str(IdSolution) + ".pdb")
                # NOTE: Substituted the old getSuperimp with the new BORGES_MATRIX.perform_superposition
                # {"rmsd": best_rmsd, "size": best_size, "associations": asso, "transf": best_transf, "graph_ref": g_a, "grapf_targ": g_b, "correlation": corr,"pdb_target":pdbmod}
                # TODO: inside the functions that opens reference and target it must be checked if it is a path or not to not open it
                dictio_super = perform_superposition(reference=io.StringIO(SystemUtility.py2_3_unicode(modelpdbstring)),
                                                     target=io.StringIO(SystemUtility.py2_3_unicode(pda)),
                                                     sensitivity_ah=sensitivity_ah,
                                                     sensitivity_bs=sensitivity_bs,
                                                     peptide_length=peptide_length,
                                                     write_graphml=False, write_pdb=False, ncycles=ncycles,
                                                     deep=deep,
                                                     top=top,
                                                     gui=None, sampling=sampling, core_percentage=core_percentage, criterium_selection_core=criterium_selection_core, force_core_expansion_through_secstr=force_core_expansion_through_secstr, verbose=False)
                if not dictio_super:
                    print("Cannot superpose", name)
                    rmsdVALFar = 100
                else:
                    pdacc = dictio_super["pdb_target"]
                    rmsdVALFar = dictio_super["rmsd"]

                if rmsdVALFar <= thresh:
                    # print pdbid,model,IdSolution,rmsdVALFar,thresh
                    flo = open(os.path.join(writePath, "rmsd_list"), "a")
                    flo.write(str(pdbid) + " " + str(model) + " " + str(IdSolution) + " " + str(rmsdVALFar) + "\n")
                    flo.close()
                    fla = open(nomefile, "w")
                    fla.write(pdacc)
                    fla.close()
                    # print "Search redundant",""+str(pdbid)+" "+str(model)+" "+str(IdSolution)
                    for item2 in solred["" + str(pdbid) + "_" + str(model) + "_" + str(IdSolution)]:
                        name2, pda2 = item2
                        listona2 = name2.split("_")
                        pdbid2 = listona2[0][:4]
                        model2 = listona2[1]
                        IdSolution2 = listona2[2]
                        if "." in list(IdSolution2):
                            IdSolution2, ext2 = IdSolution2.split(".")
                        nomefile2 = os.path.join(writePath,
                                                 str(pdbid2) + "_" + str(model2) + "_" + str(IdSolution2) + ".pdb")

                        # if rmsdVALFar2 <= thresh:
                        # print "write: ",str(pdbid2)+" "+str(model2)+" "+str(IdSolution2)
                        flo2 = open(os.path.join(writePath, "rmsd_list"), "a")
                        flo2.write(str(pdbid2) + " " + str(model2) + " " + str(IdSolution2) + " --\n")
                        flo2.close()
                        fla2 = open(nomefile2, "w")
                        fla2.write(pda2[0])
                        fla2.close()

                else:
                    remainings.append((name, pda))

            pdbsol = remainings


@SystemUtility.deprecated("Use Silhouette coefficient in sklearn.cluster to choose the value of k")
def cross_validation_to_choose_k_parameter(data, v, treshJump, minKappa=None, maxKappa=None, oneByone=False):
    narr = numpy.array(data)
    whitened = scipy.cluster.vq.whiten(narr)
    # whitened = vq.whiten(narr)
    valori = []
    whishu = copy.deepcopy(whitened)
    numpy.random.shuffle(whishu)

    if len(data) < 4 * v:
        v = 1

    print("V-Parameter chosen for the cross-validation is: " + str(v))
    subs = numpy.array_split(whishu, v)

    kappa = 0
    lastkappa = 0
    start = int(math.floor(numpy.sqrt(len(whitened) / 2) / 2.0))

    if minKappa == None:
        kappa = start
    else:
        kappa = minKappa

    if maxKappa == None:
        lastkappa = start * 2 * 2
    else:
        lastkappa = maxKappa

    if maxKappa != None and minKappa != None and (minKappa == maxKappa):
        return minKappa, whitened

    lastkappa = len(whitened)

    i = int(kappa)
    if i <= 0:
        i = 1

    while True:
        if i > lastkappa:
            break
        print("trying kappa", i)
        sys.stdout.flush()
        avg_crossv = 0.0
        for q in range(len(subs)):
            print("trying test", q)
            test = subs[q]
            avg_sqd = 0.0
            kappa_step = 0
            for z in range(len(subs)):
                if z != q or v == 1:
                    training = subs[z]
                    # print "training",training
                    print("starting clustering with training", z)
                    sys.stdout.flush()
                    groups, labels = scipy.cluster.vq.kmeans2(training, i, iter=20, minit="points")
                    # groups, labels = vq.kmeans2(training,i,iter=20,minit="points")
                    print("done...")

                    """
                    subclu = [[] for _ in range(i)]
                    for p in range(len(labels)):
                        ind = labels[p]
                        subclu[ind].append(training[p])

                    for clut in subclu:
                        k2,pvalue = scipy.stats.mstats.normaltest(clut)
                        print "======"
                        print "K2:",k2,"pvalue",pvalue
                        print "======"

                        for pv in pvalue:
                            if pv < 0.055:
                                kappa_step += 1
                                forceKappa = True
                                break
                    """

                    sum_sqd = 0.0
                    # print "gruppi",groups
                    for ctest in test:
                        sqd_min = numpy.inf
                        for centroid in groups:
                            sqd = 0.0
                            for drep in range(len(centroid)):
                                ep = (centroid[drep] - ctest[drep]) ** 2
                                if not numpy.isnan(ep):
                                    sqd += (centroid[drep] - ctest[drep]) ** 2
                            if sqd < sqd_min:
                                sqd_min = sqd
                                # if sqd_min > 0.1:
                        # sqd_min = numpy.inf
                        sum_sqd += sqd_min
                    avg_sqd += sum_sqd
            if v > 1:
                avg_sqd /= (v - 1)
            avg_crossv += avg_sqd

        avg_crossv /= v
        valori.append([avg_crossv, i])
        print(i, avg_crossv, end=' ')
        kappa = i
        if len(valori) > 1:
            jump = (valori[-2])[0] - (valori[-1])[0]
            print((valori[-2])[0] - (valori[-1])[0])
            if v == 1 and jump > 0:
                i += 1
                print("Next Kappa will be", i, "increased by", 1)
            elif v == 1 and jump <= 0:
                i -= 1
                kappa = i
                break
            elif jump >= 70:
                i += 150
                print("Next Kappa will be", i, "increased by", 150)
            elif jump >= 40:
                i += 80
                print("Next Kappa will be", i, "increased by", 80)
            elif jump >= 30:
                i += 30
                print("Next Kappa will be", i, "increased by", 30)
            elif jump >= 10:
                i += 15
                print("Next Kappa will be", i, "increased by", 15)
            elif jump >= 1.0:
                i += 5
                print("Next Kappa will be", i, "increased by", 5)
            else:
                i += 1

            if jump <= -0.6:
                kappa -= 1
                break

            if abs(jump) <= abs(treshJump):
                break
        else:
            i += 1
            print()

    return kappa, whitened

@SystemUtility.timing
@SystemUtility.deprecated('Must be changed soon for a better cluster algorithm in which k is decided through shilouette and kmeans is performed on normalized dimensional reduced (LSA) data with sklearn')
def cluster_pdbs_by_kmeans(DicParameters, directory, referenceFile, heapSolutions, sensitivity_ah, sensitivity_bs, peptide_length, ncycles, deep, top, sampling, pdbf="", minForClust=10, backbone=False,
                       limitPercluster=None, minKappa=None, maxKappa=None, limitThreshold=-0.1, structure=None,
                       writeOutput=True, core_percentage=-1, criterium_selection_core="residues", force_core_expansion_through_secstr=False):
    import decimal
    decimal.getcontext().prec = 2

    nameExp = DicParameters["nameExecution"]

    print("Reading the models...")

    # if os.path.exists(referenceFile):
    #     graph_full_reference, stru, matrix_reference, cvs_reference, highd_reference = annotate_pdb_model_with_aleph(referenceFile,
    #                                                                                                  weight=weight,
    #                                                                                                  min_diff_ah=sensitivity_ah,
    #                                                                                                  min_diff_bs=sensitivity_bs,
    #                                                                                                  peptide_length=peptide_length,
    #                                                                                                  write_pdb=False)
    #     listamodel = get_all_fragments(graph_full_reference)
    print("Ended...")

    data = []
    ref_labels = []
    if heapSolutions == None:
        n_errors = 0
        nsoluzioni = 1
        for root, subFolders, files in os.walk(directory):
            for fileu in files:
                pdbf = os.path.join(root, fileu)
                if pdbf.endswith(".pdb"):
                    print("Evaluating file ", nsoluzioni, " that is ", pdbf)
                    nodo = os.path.basename(pdbf)[:-4]
                    pdbid = nodo.split("_")[0]
                    model = nodo.split("_")[1]
                    IdSolution = nodo.split("_")[2]
                    error = False
                    rmsd = 0.0
                    # NOTE: Substituted the old getRMSD with the new BORGES_MATRIX.perform_superposition
                    # {"rmsd": best_rmsd, "size": best_size, "associations": asso, "transf": best_transf, "graph_ref": g_a, "grapf_targ": g_b, "correlation": corr,"pdb_target":pdbmod}
                    dictio_super = perform_superposition(reference=referenceFile,
                                                         target=pdbf,
                                                         sensitivity_ah=sensitivity_ah,
                                                         sensitivity_bs=sensitivity_bs,
                                                         peptide_length=peptide_length,
                                                         write_graphml=False, write_pdb=False, ncycles=ncycles,
                                                         deep=deep,
                                                         top=top,
                                                         gui=None, sampling=sampling, core_percentage=core_percentage, criterium_selection_core=criterium_selection_core, force_core_expansion_through_secstr=force_core_expansion_through_secstr, verbose=False)
                    if not dictio_super:
                        n_errors += 1
                        rmsd = -100
                        error = True
                    else:
                        rmsd = dictio_super["rmsd"]
                        if rmsd < 0:
                            n_errors += 1
                            error = True

                    if error:
                        print("Found an rmsd error for: ", pdbf)
                    nsoluzioni += 1
                    structure = Bioinformatics3.get_structure("" + str(pdbid) + "_" + str(model) + "_" + str(IdSolution), pdbf)
                    tensorInertia = (calculate_moment_of_intertia_tensor(structure))[0]
                    com = center_of_mass(structure, False)
                    com = com.coord
                    shape_par = calculate_shape_param(structure)
                    data.append([rmsd, tensorInertia[0], tensorInertia[1], tensorInertia[2], com[0], com[1], com[2],
                                 shape_par[1], shape_par[2], shape_par[3]])
                    ref_labels.append((pdbid, model, IdSolution))
                    print("processed node", pdbid, model, IdSolution, rmsd, "n_sol:", nsoluzioni, "n_err:", n_errors)
    elif heapSolutions != None and structure != None:
        cvs_model = DicParameters["cvsModel"]

        listaSolutions = []
        IdSolution = 0
        back_atm_li = None
        rmsT = None
        pdbid = None
        model = None

        for solu in heapSolutions:
            back_atm_li, atm_li, cvs, pdbid, model = solu
            tensorInertia = (calculate_moment_of_intertia_tensor(back_atm_li))[0]
            com = center_of_mass(back_atm_li, False)
            com = com.coord
            shape_par = calculate_shape_param(back_atm_li)
            data.append([tensorInertia[0], tensorInertia[1], tensorInertia[2], com[0], com[1], com[2], shape_par[1],
                         shape_par[2], shape_par[3]])
            ref_labels.append((pdbid, model, IdSolution))
            # print "Preparing",pdbid,model,IdSolution,rmsT,tensorInertia,com,shape_par
            IdSolution += 1

    subclu = []
    if len(data) > 0:
        if len(data) > minForClust:
            #TODO: Substitute Cross Validation and scipy.vk.kmeans2 for sklearn.cluster.MiniBatchKmeans and shilouette
            kappa, whitened = cross_validation_to_choose_k_parameter(data, 2, limitThreshold, minKappa=minKappa, maxKappa=maxKappa)
            print("Performing a cluster with K-Means with K=" + str(kappa) + " of " + str(len(data)))

            groups, labels = scipy.cluster.vq.kmeans2(whitened, kappa, iter=20, minit="points")
            # groups, labels = vq.kmeans2(whitened,kappa,iter=20,minit="points")

            subclu = [[] for _ in range(kappa)]
            for p in range(len(labels)):
                ind = labels[p]
                name = ref_labels[p]
                rmsdv = data[p]
                # print "p",p
                # print "ind",ind
                # print "name",name
                # print "rmsdv",rmsdv
                # print labels
                # print groups
                subclu[ind].append((name) + tuple(data[p]))
        else:
            subclu = [[] for _ in range(len(data))]
            for p in range(len(data)):
                subclu[p].append((ref_labels[p]) + tuple(data[p]))

        if writeOutput:
            f = open("./clusters.txt", "w")
            f.write("Number of clusters: " + str(len(subclu)) + "\n\n")
            for clus in subclu:
                f.write("===================== " + str(len(clus)) + "\n")
                for pdbin in clus:
                    f.write("\t")
                    f.write("NAME: " + str(pdbin[0]) + " " + str(pdbin[1]) + " " + str(pdbin[2]) + " ")
                    f.write("RMSD: " + str(pdbin[3]) + " ")
                    f.write("Tensor of inertia: " + ("%.2f" % pdbin[4]) + " " + ("%.2f" % pdbin[5]) + " " + (
                        "%.2f" % pdbin[6]) + " ")
                    f.write("Center of mass: " + ("%.2f" % pdbin[7]) + " " + ("%.2f" % pdbin[8]) + " " + (
                        "%.2f" % pdbin[9]) + " ")
                    f.write("Shape Par.: " + ("%.2f" % pdbin[10]) + " " + ("%.2f" % pdbin[11]) + " " + (
                        "%.2f" % pdbin[12]) + " ")
                    f.write("\n")
                f.write("=====================\n")
            f.close()

    nodisalvati = 1
    # print "len(subclu)",len(subclu)
    return subclu

def intermediate_clustering_library(wdir, modelpdb, DicParameters):
    global number_of_solutions
    global canCluster
    # DONE: wait that the lock canCluster is free (True)
    # DONE: block the cluster with canCluster = False
    while 1:
        if canCluster:
            canCluster = False
            break
    # DONE: copy the directory library in temp_cluster
    original_lib = os.path.join(wdir, "./library")
    temp_lib = os.path.join(wdir, "./temp_cluster")
    full_lib = os.path.join(wdir, "./full_lib")
    clustered_lib = os.path.join(wdir, "./clustered_library")
    times = time.strftime("%Y%m%d-%H%M%S")
    tarf = os.path.join(full_lib, "lib_" + times + ".tar")
    clust_txt = os.path.join(full_lib, os.path.basename(tarf)[:-4] + ".txt")
    shutil.copytree(original_lib, temp_lib)
    # DONE: clustering if library has pdb otherwise return
    if len([name for name in os.listdir(temp_lib) if os.path.isfile(os.path.join(temp_lib, name))]) > 0:
        # DONE: clustering with Kmeans and save the clustered file in final_clustered_library
        DicP = {"nameExecution": "clustering"}
        clusts = cluster_pdbs_by_kmeans(DicP, temp_lib, modelpdb, None, DicParameters["sensitivity_ah"], DicParameters["sensitivity_bs"], DicParameters["peptide_length"],
                                        DicParameters["ncycles"], DicParameters["deep"], DicParameters["top"], DicParameters["sampling"], minForClust=10, backbone=False,
                                                   limitPercluster=None, minKappa=None, maxKappa=None,
                                                   limitThreshold=-0.1, writeOutput=True, core_percentage=DicParameters["core_percentage"], criterium_selection_core=DicParameters["criterium_selection_core"], force_core_expansion_through_secstr=DicParameters["force_core_expansion_through_secstr"])

        if not os.path.exists(clustered_lib):
            os.makedirs(clustered_lib)

        newSolList = []
        for tuplos in clusts:
            if len(tuplos) == 0:
                continue
            cosa = tuplos[0]
            name = cosa[0:3]
            pdbid, model, IdSolution = name
            # print "choosing: ",pdbid,model,IdSolution
            # pda = Bioinformatics.getPDBFromListOfAtom(solutions[IdSolution][1])
            shutil.copyfile(os.path.join(temp_lib, str(pdbid) + "_" + str(model) + "_" + str(IdSolution) + ".pdb"),
                            os.path.join(clustered_lib, str(pdbid) + "_" + str(model) + "_" + str(IdSolution) + ".pdb"))
        # DONE: create full_library if does not exist
        if not os.path.exists(full_lib):
            os.makedirs(full_lib)

        # DONE: save the clusters.txt in full_library rename it with an id
        shutil.move(os.path.join(wdir, "clusters.txt"), clust_txt)

        # DONE: tar.gz the library directory and put it in full_library
        tar = tarfile.open(tarf, "a")
        for root, subFolders, files in os.walk(temp_lib):
            for fileu in files:
                pdbf = os.path.join(root, fileu)
                if pdbf.endswith(".pdb"):
                    tar.add(pdbf, arcname=fileu)
                    # DONE: remove each pdb file that it is in full_library from the original library
                    os.remove(os.path.join(original_lib, fileu))
        tar.close()
        compri = gzip.open(tarf + ".gz", 'wb')
        fion = open(tarf, "rb")
        compri.write(fion.read())
        fion.close()
        compri.close()
        os.remove(tarf)

    # DONE: remove temp_cluster
    shutil.rmtree(temp_lib)
    # DONE: put canCluster = True to free the lock
    canCluster = True

#@SystemUtility.timing
def evaluate_grid_job(idname):
    global toclientdir
    global number_of_solutions
    global doCluster_global

    print("Evaluating job ", idname)
    os.remove(os.path.join(toclientdir, idname + ".tar.gz"))
    p = subprocess.Popen('grep "_0_" ' + os.path.join(toclientdir, idname + ".out"), shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outp, errp = p.communicate()
    outp = outp.strip()
    f = open(os.path.join(toclientdir, "rmsd_list.txt"), "a")
    f.write(outp + "\n")
    f.close()
    os.remove(os.path.join(toclientdir, idname + ".out"))

    while 1:
        try:
            # members = tar.getmembers()
            # names = tar.getnames()
            # print "members",members
            # print "names",names
            tar = tarfile.open(os.path.join(toclientdir, idname + "_res.tar.gz"), "r:gz")
            infile = tar.extractfile(idname + "_res_out.data")
            break
        except:
            continue

    # nPDBs = pickle.load(infile)
    thresh = pickle.load(infile)
    superpose_exclude = pickle.load(infile)
    nilges = pickle.load(infile)
    weight = pickle.load(infile)
    sensitivity_ah = pickle.load(infile)
    sensitivity_bs = pickle.load(infile)
    peptide_length =  pickle.load(infile)
    ncycles = pickle.load(infile)
    deep = pickle.load(infile)
    top = pickle.load(infile)
    sampling = pickle.load(infile)
    core_percentage = pickle.load(infile)
    criterium_selection_core = pickle.load(infile)
    force_core_expansion_through_secstr = pickle.load(infile)
    library = os.path.join(toclientdir, "../library/")
    if not os.path.exists(library):
        os.makedirs(library)

    collpdbs = pickle.load(infile)
    solred = pickle.load(infile)
    infile.close()
    tar.close()

    if doCluster_global:
        cluster_by_rmsd(library, collpdbs, solred, thresh, superpose_exclude, nilges, weight, sensitivity_ah, sensitivity_bs, peptide_length, ncycles, deep, top, sampling, core_percentage=core_percentage, criterium_selection_core=criterium_selection_core, force_core_expansion_through_secstr=force_core_expansion_through_secstr)
    else:
        for item in collpdbs:
            pathp = os.path.join(library, item[0])
            f = open(pathp, "w")
            f.write(item[1])
            f.close()

    try:
        os.remove(os.path.join(toclientdir, idname + "_res_out.data"))
    except:
        pass
    try:
        os.remove(os.path.join(toclientdir, idname + "_res.tar.gz"))
    except:
        pass
    try:
        os.remove(os.path.join(toclientdir, idname + ".sh"))
    except:
        pass

    return True


def prepare_and_launch_job(cm, baseline, idname, pdbsfiles, supercomputer, pdb_model):
    global toclientdir
    global PATH_NEW_BORGES
    global NUMBER_OF_PARALLEL_GRID_JOBS

    # print "Number of jobs to evaluate:  "+str(len(listjobs))

    pdbf = os.path.join(toclientdir, idname + ".tar")
    fro = open(os.path.join(toclientdir, idname + "PARAM"), "w")
    pickle.dump(len(pdbsfiles), fro)
    for valo in pdbsfiles:
        pdbf_n, pdbf_c, cvs_list_str, pdbstruc = valo
        pickle.dump(pdbf_n, fro)
        pickle.dump(pdbf_c, fro)
        pickle.dump(cvs_list_str, fro)
        pickle.dump(pdbstruc, fro)
    fro.close()
    tar = tarfile.open(pdbf, "a")
    tar.add(os.path.join(toclientdir, idname + "PARAM"), arcname=idname + "PARAM")
    tar.close()
    os.remove(os.path.join(toclientdir, idname + "PARAM"))
    compri = gzip.open(pdbf + ".gz", 'wb')
    fion = open(pdbf, "rb")
    compri.write(fion.read())
    fion.close()
    compri.close()
    os.remove(pdbf)

    if supercomputer != None and os.path.exists(supercomputer):
        comando = "nice -n5 " + PATH_NEW_BORGES + " -j " + os.path.join(toclientdir,
                                                                        str(idname) + ".tar.gz") + " " + " ".join(
            baseline) + " > " + os.path.join(toclientdir, str(idname) + ".out")
        SystemUtility.launchCommand(comando, os.path.join(toclientdir, str(idname) + ".out"),
                                    """Job ended with success""", 1, single=True)
    else:
        print("# of jobs to evaluate: ", len(SystemUtility.LISTJOBS))
        while len(SystemUtility.LISTJOBS) > NUMBER_OF_PARALLEL_GRID_JOBS:
            time.sleep(3)

        if hasattr(cm, "channel"):
            cm.copy_local_file(pdbf + ".gz", pdbf + ".gz", force_cumulative=False)

        job = Grid.gridJob(str(idname))

        if hasattr(cm, "channel"):
            job.setInitialDir(cm.get_remote_pwd())
        else:
            job.setInitialDir(os.path.abspath(toclientdir))

        script = """#!/bin/bash
if [ -f """ + PATH_NEW_BORGES + """ ]; then
        """ + PATH_NEW_BORGES + """ -j """ + str(idname) + """.tar.gz""" + """ """ + """ """.join(baseline) + """
else
        ./""" + os.path.basename(PATH_NEW_BORGES) + """ -j """ + str(idname) + """.tar.gz""" + """ """ + """ """.join(
            baseline) + """
fi
"""
        f = open(os.path.join(toclientdir, str(idname) + ".sh"), "w")
        f.write(script)
        f.close()

        st = os.stat(os.path.join(toclientdir, str(idname) + ".sh"))
        os.chmod(os.path.join(toclientdir, str(idname) + ".sh"),
                 st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        job.setExecutable(os.path.join(toclientdir, str(idname) + ".sh"))
        job.addInputFile(str(idname) + ".tar.gz", False)
        job.addInputFile(os.path.basename(pdb_model), False)
        job.addInputFile(PATH_NEW_BORGES, False)
        job.addOutputFile(str(idname) + ".out", False)
        # job.addOutputFile(str(idname)+"_res.tar.gz",False)
        (nc, nq) = cm.submitJob(job, isthelast=True)
        SystemUtility.LISTJOBS[idname] = [(os.path.join(toclientdir, str(idname) + ".out"), "success", 1, True, "")]
        print("Search in " + str(nq) + " structure submitted to the cluster " + str(nc))


@SystemUtility.timing
def generate_library_from_sequence(directory_database=None, sequence=None, secstr=None, coil_diff=1, sensitivity_ah=0.5, sensitivity_bs=0.3, peptide_length=3):
    print()
    print("=================")
    print("= READING INPUT =")
    print("=================")
    #TODO 1: read and parse the sequence FASTA file
    record = list(SeqIO.parse(sequence, "fasta"))[0]

    #TODO 2: read and parse the secondary structure prediction file
    #TODO 3; possibly compute the 2 from 1 automatically

    secs = None
    conf = None
    with open(secstr, "r") as f:
        for line in f.readlines():
            linel = line.split()
            if len(linel) > 2:
                if linel[1] == "jnetpred":
                    secs = linel[-1].split("|")
                if linel[1] == "JNETCONF":
                    conf = linel[-1].split("|")

    pairings = None
    if len(record.seq) == len(secs) == len(conf):
        pairings = list(zip(record.seq,secs,conf))
    else:
        print("ERROR: Sequence given is not fully annotated with a secondary structure prediction! Size does not fit")
        sys.exit(0)

    seq = "".join([t[0] for t in pairings])
    secs = "".join([t[1] if t[1] != "" else "C" for t in pairings])
    conf = "".join([t[2] for t in pairings])

    codec = ""
    letter = ""
    mapse = {"C":"cc","H":"ah","E":"bs"}
    numb = 0
    for i in range(len(seq)):
         if secs[i] != letter:
            if letter != "":
                codec += str(numb)+mapse[letter] + "|"
            letter = secs[i]
            numb = 1
         else:
            numb += 1
    if letter != "":
        codec += str(numb) + mapse[letter]

    codecl = codec.split("|")
    if "cc" in codecl[0]:
        codecl = codecl[1:]
    if "cc" in codecl[-1]:
        codecl = codecl[:-1]

    codec = "|".join(codecl)

    print("SEQUENCE",seq)
    print("SECSTRPR",secs)
    print("CONFIDEN",conf)
    print("CODEC   ",codec)
    print()

    allfiles = []
    if os.path.exists(os.path.join(directory_database, "listfiles.txt")):
        print("Reading", os.path.join(directory_database, "listfiles.txt"), "...")
        f = open(os.path.join(directory_database, "listfiles.txt"), "r")
        alllinesaa = f.readlines()
        f.close()
        print("Done...")
        for pdbfl in alllinesaa:
            if len(allfiles) % 1000 == 0:
                print("Parsed", len(allfiles))
            pdbfl = pdbfl.split()
            pdbf = pdbfl[0]
            if pdbf.endswith(".pdb") or pdbf.endswith(".gz") or pdbf.endswith(".ent"):
                allfiles.append(pdbf)
            elif pdbf.endswith(".data"):
                for key in pdbfl[1:]:
                    allfiles.append((pdbf, key))
    else:
        for root, subFolders, files in os.walk(directory_database):
            for fileu in files:
                pdbf = os.path.join(root, fileu)
                if pdbf.endswith(".pdb") or pdbf.endswith(".gz") or pdbf.endswith(".ent"):
                    allfiles.append(pdbf)
                elif pdbf.endswith(".data"):
                    cv_matrices_shelve = shelve.open(pdbf)
                    for key in cv_matrices_shelve:
                        allfiles.append((pdbf, key))
    pdbsfiles = []
    print("Starting shuffle...")
    random.shuffle(allfiles)
    print("List shuffled!")

    for i in range(len(allfiles)):
        pdbf = allfiles[i]
        if isinstance(pdbf, str):
            if pdbf.endswith(".gz"):
                fileObj = gzip.GzipFile(pdbf, 'rb');
                fileContent = fileObj.read()
                fileObj.close()
                os.remove(pdbf)
                pdbf = pdbf[:-3]  # elimino estensione .gz
                fou = open(pdbf, "w")
                fou.write(fileContent.decode("utf-8") if isinstance(fileContent,bytes) else fileContent)
                fou.close()
            if pdbf.endswith(".ent"):
                pdbf2 = pdbf[:-4]  # elimino estensione .ent
                pdbf2 = pdbf2 + ".pdb"
                os.rename(pdbf, pdbf2)
                pdbf = pdbf2
            if os.path.basename(pdbf).startswith("pdb"):
                root, fileu = os.path.split(pdbf)
                pdbf2 = os.path.basename(pdbf)[3:]  # elimino la parola pdb
                pdbf2 = os.path.join(root, pdbf2)
                os.rename(pdbf, pdbf2)
                pdbf = pdbf2
                Bioinformatics3.rename_hetatm_and_icode(pdbf)
            try:
                predict_compare_extract_signature_fold(seq,secs,conf,codec,pdbf,sensitivity_ah, sensitivity_bs, peptide_length, coil_diff)
            except:
                print(sys.exc_info())
                traceback.print_exc(file=sys.stdout)

                
@SystemUtility.timing
def predict_compare_extract_signature_fold(sequence,secs_strc,confidence,codec,pdbf,sensitivity_ah, sensitivity_bs, peptide_length, coil_diff):
    graph_full_reference, stru, matrix_reference, cvs_reference, highd_reference = annotate_pdb_model_with_aleph(
        pdbf,
        weight="distance_avg",
        min_diff_ah=sensitivity_ah,
        min_diff_bs=sensitivity_bs,
        peptide_length=peptide_length,
        write_pdb=False)

    extracted_codec = ""
    dic_resi = Bioinformatics3.get_dictio_resi_to_secstr(graph_full_reference,stru)

    extracted_codec = []
    letter = ""
    chain = ""
    model = None
    numb = 0
    fragindex = None
    for resi in sorted(dic_resi.keys()):
        if dic_resi[resi][0] != letter or resi[0] != model or resi[1] != chain:
            if letter != "":
                extracted_codec[-1] += str(fragindex) + "." + str(numb) + letter + "|" if fragindex is not None else "" + str(numb) + letter + "|"
            letter = dic_resi[resi][0]
            fragindex = dic_resi[resi][1]
            if resi[0] != model or resi[1] != chain:
                model = resi[0]
                chain = resi[1]
                if len(extracted_codec) > 0:
                    extracted_codec[-1] = extracted_codec[-1][:-1]
                extracted_codec.append("")
            numb = 1
        else:
            numb += 1
    if letter != "":
        extracted_codec[-1] += str(fragindex) + "." + str(numb) + letter if fragindex is not None else "" + str(numb) + letter

    print("EXTRACTED CODEC",extracted_codec)
    print("GIVEN CODEC    ",codec)
    simply_extracted_codec = [''.join([i for i in s if not i.isdigit() and i != "."]) for s in extracted_codec]
    print("SIMPLIFIED EXTRACTION",simply_extracted_codec)
    simply_given_codec = ''.join([i for i in codec if not i.isdigit() and i != "."])
    print("SIMPLIFIED GIVEN     ",simply_given_codec)
    results = [[m.start() for m in re.finditer("(?="+simply_given_codec.replace("|","\|")+")", c)] for c in simply_extracted_codec]
    print("FOUND", results)

    codecz = codec.split("|")
    counter = 0
    for ed,seqex in enumerate(extracted_codec):
        for found_s in results[ed]:
            na = simply_given_codec.split("|")
            q = simply_extracted_codec[ed][:found_s]
            if q[-1] == "|":
                q = q[:-1]
            nb = q.split("|")
            #print(nb,"--",na)
            t = extracted_codec[ed].split("|")[:len(nb)]
            z = extracted_codec[ed].split("|")[len(nb):len(nb)+len(na)]
            print("CODEC:",codec)
            print("EXTRA:","|".join(z))
            penalty = 0
            ids = []
            for a in range(len(codecz)):
                if "cc" in codecz[a]:
                    e = abs(int(codecz[a][:-2])-int(z[a][:-2]))
                    if e <= coil_diff:
                        penalty += e
                    else:
                        penalty += 10000+e
                else:
                    id,size = z[a].split(".")
                    penalty += abs(int(codecz[a][:-2])-int(size[:-2]))
                    ids.append(int(id))
            if penalty < 1000:
                print("PENALTY:",penalty)
                print("IDS:",ids)
                namepdb = os.path.basename(pdbf)[:-4]+"_0"+"_"+str(counter)+".pdb"
                print("NAME_PDB:",namepdb)
                print()
                counter += 1
                toro = graph_full_reference.copy()
                toro = toro.vs.select(lambda x: x.index in ids).subgraph()

                stri = get_pdb_string_from_graph(toro, stru, renumber=False, polyala=True)
                if not os.path.exists("./library"):
                    os.makedirs("./library")

                with open(os.path.join("./library",namepdb),"w") as f:
                    f.write(stri)


@SystemUtility.timing
def generate_library(max_n_models_per_pdb=1000,local_grid=None,remote_grid=None,supercomputer=None,force_core=-1, directory_database=None,
                     c_angle=95, c_dist=95, c_angle_dist=95, c_cvl_diff=95, score_intra_fragment=95, j_angle=90, j_dist=90, j_angle_dist=90,
                     j_cvl_diff=95, score_inter_fragments=90, rmsd_clustering=1.5, exclude_residues_superpose=0, work_directory="./",
                     use_lib_to_superpose=False, targz=None, pdbmodel=None, remove_coil=False, weight = "distance_avg",
                     sensitivity_ah=0.45, sensitivity_bs=0.45, peptide_length=3, enhance_fold=False, superpose=True, process_join=False,
                     nilges=3, ncycles=15, deep=True, top=1, sampling="none", sequence="", ncssearch=False, multimer=True,
                     rmsd_min=0.0, rmsd_max=6.0, step_diag=1, ssbridge=False, connectivity=False, representative=False, sidechains=False,
                     gui=None, doCluster=True, sym=None, core_percentage=60, criterium_selection_core="residues", force_core_expansion_through_secstr=False, classic=True, signature_threshold=0.1):
    global PATH_NEW_BORGES
    global GRID_TYPE_R
    global MAX_PDB_TAR
    global toclientdir
    global doCluster_global
    global PYTHON_V

    GLOBAL_MAXIMUM = int(max_n_models_per_pdb)
    if sym is None:
        sym = SystemUtility.SystemUtility()

    if local_grid != None or remote_grid != None or supercomputer != None:
        SystemUtility.startCheckQueue(sym, delete_check_file=False, callback=evaluate_grid_job, forcework=True)

    if int(force_core) > 0:
        sym.PROCESSES = int(force_core)
    if c_angle <= 0 and directory_database != None:
        c_angle = score_intra_fragment
    if c_dist <= 0 and directory_database != None:
        c_dist = score_intra_fragment
    if c_angle_dist <= 0 and directory_database != None:
        c_angle_dist = score_intra_fragment
    if c_cvl_diff <= 0 and directory_database != None:
        c_cvl_diff = score_intra_fragment
    if j_angle <= 0 and directory_database != None:
        j_angle = score_inter_fragments
    if j_dist <= 0 and directory_database != None:
        j_dist = score_inter_fragments
    if j_angle_dist <= 0 and directory_database != None:
        j_angle_dist = score_inter_fragments
    if j_cvl_diff <= 0 and directory_database != None:
        j_cvl_diff = score_inter_fragments

    thresh = float(rmsd_clustering)
    if thresh <= 0.0:
        doCluster = False


    doCluster_global = doCluster

    superpose_exclude = int(exclude_residues_superpose) + 1
    extract_superposed_pdbs = use_lib_to_superpose
    strucc = None
    pattern_cvs = None
    pattern = None
    lisBig = None
    highd = None
    wdir = work_directory
    cm = None
    toclientdir = None
    pdbsearch = None

    if wdir == None or wdir == "":
        wdir = "./"

    if not os.path.exists(wdir):
        os.makedirs(wdir)

    DicGridConn = {}
    baseline = []
    skip = False
    bl = sys.argv[1:]
    for arg in bl:
        if skip:
            skip = False
            continue
        if arg in ["--directory_database", "--supercomputer", "--local_grid", "--remote_grid", "--pdbmodel"]:
            skip = True
            continue
        baseline.append(arg)

    if (local_grid != None and os.path.exists(local_grid)) or (remote_grid != None and os.path.exists(remote_grid)):
        if targz != None:
            print(colored("ATTENTION: --targz option is incompatible with --remote_grid , --local_grid and --supercomputer", "red"))
            print()
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)

        toclientdir = os.path.join(wdir, "./ToProcess")

        if not os.path.exists(toclientdir):
            os.makedirs(toclientdir)

        # read the setup.bor and configure the grid
        setupbor = None
        GRID_TYPE = None
        if remote_grid != None and os.path.exists(remote_grid):
            path_bor = remote_grid
            try:
                if PYTHON_V == 3:
                    setupbor = configparser.ConfigParser()
                    setupbor.read_file(open(path_bor))
                elif PYTHON_V == 2:
                    setupbor = ConfigParser.ConfigParser()
                    setupbor.readfp(open(path_bor))
                DicGridConn["username"] = setupbor.get("GRID", "remote_frontend_username")
                DicGridConn["host"] = setupbor.get("GRID", "remote_frontend_host")
                DicGridConn["port"] = setupbor.getint("GRID", "remote_frontend_port")
                DicGridConn["passkey"] = setupbor.get("CONNECTION", "remote_frontend_passkey")
                DicGridConn["promptA"] = (setupbor.get("GRID", "remote_frontend_prompt")).strip() + " "
                DicGridConn["isnfs"] = setupbor.getboolean("GRID", "remote_fylesystem_isnfs")
                try:
                    DicGridConn["remote_submitter_username"] = setupbor.get("GRID", "remote_submitter_username")
                    DicGridConn["remote_submitter_host"] = setupbor.get("GRID", "remote_submitter_host")
                    DicGridConn["remote_submitter_port"] = setupbor.getint("GRID", "remote_submitter_port")
                    DicGridConn["promptB"] = (setupbor.get("GRID", "remote_submitter_prompt")).strip() + " "
                except:
                    pass
                DicGridConn["home_frontend_directory"] = setupbor.get("GRID", "home_frontend_directory")
                PATH_NEW_BORGES = setupbor.get("GRID", "path_remote_borges")
                GRID_TYPE = setupbor.get("GRID", "type_remote")
            except:
                print(colored("ATTENTION: Some keyword in your configuration files are missing. Contact your administrator", "red"))
                print("Path bor given: ", path_bor)
                print()
                traceback.print_exc(file=sys.stdout)
                sys.exit(1)
        elif local_grid != None and os.path.exists(local_grid):
            path_bor = local_grid
            try:
                if PYTHON_V == 3:
                    setupbor = configparser.ConfigParser()
                    setupbor.read_file(open(path_bor))
                elif PYTHON_V == 2:
                    setupbor = ConfigParser.ConfigParser()
                PATH_NEW_BORGES = setupbor.get("LOCAL", "path_local_borges")
                GRID_TYPE = setupbor.get("GRID", "type_local")
            except:
                print(colored("ATTENTION: Some keyword in your configuration files are missing. Contact your administrator","red"))
                print("Path bor given: ", path_bor)
                print()
                traceback.print_exc(file=sys.stdout)
                sys.exit(1)

        # STARTING THE GRID MANAGER
        if cm == None:
            if GRID_TYPE == "Condor":
                cm = Grid.condorManager()
            elif GRID_TYPE == "SGE":
                QNAME = setupbor.get("SGE", "qname")
                FRACTION = setupbor.getfloat("SGE", "fraction")
                cm = Grid.SGEManager(qname=QNAME, fraction=FRACTION)
            elif GRID_TYPE == "MOAB":
                PARTITION = setupbor.get("MOAB", "partition")
                # FRACTION = setupbor.getfloat("MOAB","partition")
                cm = Grid.MOABManager(partition=PARTITION)
            elif GRID_TYPE == "SLURM":
                PARTITION = setupbor.get("SLURM", "partition")
                if PARTITION != None and PARTITION != '':
                    cm = Grid.SLURMManager(partition=PARTITION)
                else:
                    cm = Grid.SLURMManager()
            elif GRID_TYPE == "TORQUE":
                QNAME = setupbor.get("TORQUE", "qname")
                FRACTION = setupbor.getint("TORQUE", "cores_per_node")
                PARALLEL_JOBS = setupbor.getint("TORQUE", "number_of_parallel_jobs")
                MAUI = setupbor.getboolean("TORQUE", "maui")
                cm = Grid.TORQUEManager(qname=QNAME, cores_per_node=FRACTION, parallel_jobs=PARALLEL_JOBS, maui=MAUI)

        if cm is not None:
            cm.setRank("kflops")
            cm.nice_user = "true"
            PATH_REMOTE_PYTHON_INTERPRETER = setupbor.get("GRID", "python_remote_interpreter")
            PATH_LOCAL_PYTHON_INTERPRETER = setupbor.get("LOCAL", "python_local_interpreter")

            if PATH_REMOTE_PYTHON_INTERPRETER.strip() in ["", None]:
                PATH_REMOTE_PYTHON_INTERPRETER = "/usr/bin/python"

            if PATH_LOCAL_PYTHON_INTERPRETER.strip() in ["", None]:
                PATH_LOCAL_PYTHON_INTERPRETER = "/usr/bin/python"

    elif supercomputer != None and os.path.exists(supercomputer):
        # read the nodes.txt file and process it
        toclientdir = os.path.join(wdir, "./ToProcess")

        if not os.path.exists(toclientdir):
            os.makedirs(toclientdir)

        path_nodes = supercomputer
        f = open(path_nodes, "r")
        nodes_list = f.readlines()
        f.close()
        PATH_NEW_BORGES = nodes_list[0]
        nodes_list = nodes_list[1:]
        for i in range(len(nodes_list)):
            nodes_list[i] = nodes_list[i][:-1] + "***" + str(i)
        SystemUtility.NODES = nodes_list

    if targz == None and directory_database != None:
        pdbsearchin = ""
        listn = []
        graph_full_reference, stru, matrix_reference, cvs_reference, highd_reference = annotate_pdb_model_with_aleph(pdbmodel,
                                                                                                    weight=weight,
                                                                                                    min_diff_ah=sensitivity_ah,
                                                                                                    min_diff_bs=sensitivity_bs,
                                                                                                    peptide_length=peptide_length,
                                                                                                    write_pdb=False)
        all_frags = get_all_fragments(graph_full_reference)
        if remove_coil:
            for fra in all_frags:
                for resi in fra["resIdList"]:
                    listn.append((fra["chain"], resi))

        for model in stru.get_list():
            reference = []
            for chain in model.get_list():
                for residue in chain.get_list():
                    if len(listn) == 0 or (chain.get_id(), residue.get_id()) in listn:
                        reference += residue.get_unpacked_list()
            pdbmod, cnv = Bioinformatics3.get_pdb_from_list_of_atoms(reference, renumber=True, uniqueChain=True)
            # pdbmod = "MODEL "+str(model.get_id())+"\n"+pdbmod+"\n\n"
            pdbsearchin += pdbmod
            # pdbsearchin += "ENDMDL\n\n"

        fds = open(os.path.join(wdir, os.path.basename(pdbmodel)[:-4] + "_input_search.pdb"), "w")
        fds.write(pdbsearchin)
        fds.close()

        #Forcing the garbage collector to empty space
        listn = []
        tupls = []

        pdbmodel = os.path.abspath(os.path.join(wdir, os.path.basename(pdbmodel)[:-4] + "_input_search.pdb"))

    if (local_grid != None and os.path.exists(local_grid)) or (
                    remote_grid != None and os.path.exists(remote_grid)) or (
                    supercomputer != None and os.path.exists(supercomputer)):
        shutil.copyfile(pdbmodel, os.path.join(toclientdir, os.path.basename(pdbmodel)))
        baseline.append("--pdbmodel")
        baseline.append(os.path.basename(pdbmodel))

    pattern = None
    pattern_cvs = None
    highd = None
    if targz != None and os.path.exists(targz):
        fileParaName = targz
        t = datetime.datetime.now()
        epcSec = time.mktime(t.timetuple())
        now = datetime.datetime.fromtimestamp(epcSec)
        print("" + str(now.ctime()))
        sys.stdout.flush()

        tar = tarfile.open(fileParaName, "r:gz")
        print("Read 1 Parameter: the tar.gz archive")
        infile = tar.extractfile((fileParaName[:-7]) + "PARAM")
        print("Read 2 Parameter: the number of pdbs to work with")
        nPDBs = pickle.load(infile)
        pdbsol = []
        solred = {}
        for i in range(nPDBs):
            print("Read 3 Parameter: PDB file to work with")
            pdb_name = pickle.load(infile)
            pdbfile = pickle.load(infile)
            cvs_list_str = pickle.load(infile)
            pdbstruc = pickle.load(infile)
            # print "pdbf",pdb_name
            if i == 0:
                pattern, pattern_cvs, highd, pdbsearch, strucc, lisBig, peptide_length = evaluate_model(pdbmodel, bool(enhance_fold), int(peptide_length),  weight, sensitivity_ah, sensitivity_bs)
            # pdbsearch = pdbsearchin
            pdl, dicl = evaluate_pdb(sym, wdir, pdbfile, cvs_list_str, pdbstruc, strucc, lisBig, i, pattern,
                                     pattern_cvs, highd, doCluster, superpose, process_join, pdbsearch, pdb_name,
                                     thresh, superpose_exclude, extract_superposed_pdbs, peptide_length, sequence,
                                     ncssearch, multimer, c_angle, c_dist, c_angle_dist, c_cvl_diff, j_angle, j_dist,
                                     j_angle_dist, j_cvl_diff, rmsd_min, rmsd_max, step_diag, ssbridge, connectivity,
                                     nilges, enhance_fold, representative, pdbmodel, sidechains, weight, sensitivity_ah,
                                     sensitivity_bs, ncycles, deep, top, sampling, core_percentage, criterium_selection_core, force_core_expansion_through_secstr, classic, signature_threshold, return_pdbstring=True)
            pdbsol += pdl
            solred.update(dicl)
        infile.close()
        tar.close()

        fileout = os.path.basename(fileParaName[:-7]) + "_res"
        pdbf = os.path.join(wdir, fileout + ".tar")
        fro = open(os.path.join(wdir, fileout + "_out.data"), "w")
        # print "Write number of solutions...",len(pdbsol)
        # pickle.dump(len(pdbsol),fro)
        pickle.dump(float(thresh), fro)
        pickle.dump(int(superpose_exclude), fro)
        pickle.dump(int(nilges), fro)
        pickle.dump(weight, fro)
        pickle.dump(sensitivity_ah, fro)
        pickle.dump(sensitivity_bs, fro)
        pickle.dump(peptide_length, fro)
        pickle.dump(ncycles, infile)
        pickle.dump(deep, fro)
        pickle.dump(top, fro)
        pickle.dump(sampling, fro)
        pickle.dump(core_percentage, fro)
        pickle.dump(criterium_selection_core, fro)
        pickle.dump(signature_threshold, fro)
        pickle.dump(force_core_expansion_through_secstr, fro)
        pickle.dump(pdbsol, fro)
        pickle.dump(solred, fro)
        fro.close()
        tar = tarfile.open(pdbf, "a")
        tar.add(os.path.join(wdir, fileout + "_out.data"), arcname=fileout + "_out.data")
        tar.close()
        os.remove(os.path.join(wdir, fileout + "_out.data"))
        compri = gzip.open(pdbf + ".gz", 'wb')
        fion = open(pdbf, "rb")
        compri.write(fion.read())
        fion.close()
        compri.close()
        os.remove(pdbf)
    elif directory_database != None:
        allfiles = []
        if os.path.exists(os.path.join(directory_database, "listfiles.txt")):
            print("Reading", os.path.join(directory_database, "listfiles.txt"), "...")
            f = open(os.path.join(directory_database, "listfiles.txt"), "r")
            alllinesaa = f.readlines()
            f.close()
            print("Done...")
            for pdbfl in alllinesaa:
                if len(allfiles) % 1000 == 0:
                    print("Parsed", len(allfiles))
                pdbfl = pdbfl.split()
                pdbf = pdbfl[0]
                if pdbf.endswith(".pdb") or pdbf.endswith(".gz") or pdbf.endswith(".ent"):
                    allfiles.append(pdbf)
                elif pdbf.endswith(".data"):
                    for key in pdbfl[1:]:
                        allfiles.append((pdbf, key))
        else:
            for root, subFolders, files in os.walk(directory_database):
                for fileu in files:
                    pdbf = os.path.join(root, fileu)
                    if pdbf.endswith(".pdb") or pdbf.endswith(".gz") or pdbf.endswith(".ent"):
                        allfiles.append(pdbf)
                    elif pdbf.endswith(".data"):
                        cv_matrices_shelve = shelve.open(pdbf)
                        for key in cv_matrices_shelve:
                            allfiles.append((pdbf, key))
        pdbsfiles = []
        print("Starting shuffle...")
        random.shuffle(allfiles)
        print("List shuffled!")
        for i in range(len(allfiles)):
            pdbf = allfiles[i]
            if isinstance(pdbf, str):
                if pdbf.endswith(".gz"):
                    fileObj = gzip.GzipFile(pdbf, 'rb');
                    fileContent = fileObj.read()
                    fileObj.close()
                    os.remove(pdbf)
                    pdbf = pdbf[:-3]  # elimino estensione .gz
                    fou = open(pdbf, "w")
                    fou.write(fileContent.decode("utf-8") if isinstance(fileContent,bytes) else fileContent)
                    fou.close()
                if pdbf.endswith(".ent"):
                    pdbf2 = pdbf[:-4]  # elimino estensione .ent
                    pdbf2 = pdbf2 + ".pdb"
                    os.rename(pdbf, pdbf2)
                    pdbf = pdbf2
                if os.path.basename(pdbf).startswith("pdb"):
                    root, fileu = os.path.split(pdbf)
                    pdbf2 = os.path.basename(pdbf)[3:]  # elimino la parola pdb
                    pdbf2 = os.path.join(root, pdbf2)
                    os.rename(pdbf, pdbf2)
                    pdbf = pdbf2
                    Bioinformatics3.rename_hetatm_and_icode(pdbf)

            if i == 0:
                pattern, pattern_cvs, highd, pdbsearch, strucc, lisBig, peptide_length = evaluate_model(pdbmodel, bool(enhance_fold), int(peptide_length),  weight, sensitivity_ah, sensitivity_bs)
                pdbsearch = pdbsearchin
                try:
                    shutil.copyfile(pdbmodel,
                                    os.path.join(toclientdir, os.path.basename(pdbmodel)))
                except:
                    pass

            # Multiprocessing
            if supercomputer == None and local_grid == None and remote_grid == None:
                if isinstance(pdbf, str):
                    evaluate_pdb(sym, wdir, pdbf, None, None, strucc, lisBig, i, pattern, pattern_cvs,
                                 highd, doCluster, superpose, process_join, pdbsearch, "", thresh, superpose_exclude,
                                 extract_superposed_pdbs, peptide_length,  sequence, ncssearch, multimer, c_angle, c_dist, c_angle_dist, c_cvl_diff, j_angle, j_dist,
                                     j_angle_dist, j_cvl_diff, rmsd_min, rmsd_max, step_diag, ssbridge, connectivity,
                                     nilges, enhance_fold, representative, pdbmodel, sidechains, weight, sensitivity_ah,
                                 sensitivity_bs, ncycles, deep, top, sampling, core_percentage, criterium_selection_core, force_core_expansion_through_secstr, classic, signature_threshold)
                elif isinstance(pdbf, tuple):
                    pdbpa = pdbf[0]
                    key = pdbf[1]
                    cv_matrices_shelve = shelve.open(pdbpa)
                    cvs_list_str = cv_matrices_shelve[key]["cvs_list"]
                    pdbstruc = cv_matrices_shelve[key]["structure"]
                    evaluate_pdb(sym, wdir, pdbpa, cvs_list_str, pdbstruc, strucc, lisBig, i, pattern,
                                 pattern_cvs, highd, doCluster, superpose, process_join, pdbsearch, key, thresh,
                                 superpose_exclude, extract_superposed_pdbs, peptide_length, sequence,
                                     ncssearch, multimer, c_angle, c_dist, c_angle_dist, c_cvl_diff, j_angle, j_dist,
                                     j_angle_dist, j_cvl_diff, rmsd_min, rmsd_max, step_diag, ssbridge, connectivity,
                                     nilges, enhance_fold, representative, pdbmodel, sidechains, weight,
                                 sensitivity_ah, sensitivity_bs, ncycles, deep, top, sampling, core_percentage, criterium_selection_core, force_core_expansion_through_secstr, classic, signature_threshold)
            else:
                if isinstance(pdbf, str):
                    f = open(pdbf, "r")
                    pdbread = f.read()
                    f.close()
                    pdbsfiles.append((os.path.basename(pdbf)[:-4], pdbread, None, None))
                elif isinstance(pdbf, tuple):
                    pdbpa = pdbf[0]
                    key = pdbf[1]
                    cv_matrices_shelve = shelve.open(pdbpa)
                    cvs_list_str = cv_matrices_shelve[key]["cvs_list"]
                    pdbstruc = cv_matrices_shelve[key]["structure"]
                    pdbsfiles.append((key, key, cvs_list_str, pdbstruc))

                if (i != 0 and i % MAX_PDB_TAR == 0) or i == len(allfiles) - 1:
                    prepare_and_launch_job(cm, baseline, "job_" + str(i), pdbsfiles, supercomputer, pdbmodel)
                    pdbsfiles = []

    if local_grid != None or remote_grid != None or supercomputer != None:
        SystemUtility.endCheckQueue()
    print("...Writing output files and cleaning...")



#######################################################################################################
#                                               MAIN                                                  #
#######################################################################################################

if __name__ == "__main__":
    start_time = time.time()

    head1 = """
                                      .--------------------------------------------.
                                      |  ____   ____  _____   _____ ______  _____  |
                                      | |  _ \ / __ \|  __ \ / ____|  ____|/ ____| |
                                      | | |_) | |  | | |__) | |  __| |__  | (___   |
                                      | |  _ <| |  | |  _  /| | |_ |  __|  \___ \  |
                                      | | |_) | |__| | | \ \| |__| | |____ ____) | |
                                      | |____/ \____/|_|  \_\\\\_____|______|_____/  |
                                      #--------------------------------------------#
                                                | v. 4.1.0  -- 10/11/2017 |
                    """
    cprint(head1, 'cyan')
    print("""
        Institut de Biologia Molecular de Barcelona --- Consejo Superior de Investigaciones Científicas
                         I.B.M.B.                                            C.S.I.C.

                        Department of Structural Biology - “Maria de Maeztu” Unit of Excellence

        In case this result is helpful, please, cite:

        Exploiting tertiary structure through local folds for ab initio phasing
        Sammito, M., Millán, C., Rodríguez, D. D., M. de Ilarduya, I., Meindl, K.,
        De Marino, I., Petrillo, G., Buey, R. M., de Pereda, J. M., Zeth, K., Sheldrick, G. M. & Usón, I.
        (2013) Nat Methods. 10, 1099-1101.
        """)
    print("Email support: ", colored("bugs-borges@ibmb.csic.es", 'blue'))

    # List of arguments accepted in the command line
    parser = argparse.ArgumentParser(description='Command line options for BORGES_MATRIX')
    general_group = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(title='List of features in BORGES_MATRIX', description='Functions implemented in BORGES_MATRIX', help='Help for each feature')

    general_group.add_argument("--sampling",
                        help="Algorithm to sampling CVs. Default none",
                        type=str, default="none", choices=['none', 'random', 'first_middle_last', 'first_middle_last_enhanced','1every2', '1every3', '1every4', '1every5'])

    general_group.add_argument("--width_pic", help="Width in inches for pictures. Default 100.0", type=float, default=100.0)
    general_group.add_argument("--height_pic", help="Height in inches for pictures. Default 20.0", type=float, default=20.0)
    general_group.add_argument("--pack_beta_sheet",
                        help="Do not break a beta sheet in two community clusters unless is really necessary. Default: False",
                        action='store_true', default=False)
    general_group.add_argument("--homogeneity",
                        help="Favourite homogeneous clusters. Default: False",
                        action='store_true', default=False)
    general_group.add_argument("--max_ah_dist", help="Maximum distance allowed among ah cvs in the graph. Default 20.0",
                        type=float, default=20.0)
    general_group.add_argument("--min_ah_dist", help="Minimum distance allowed among ah cvs in the graph. Default  0.0",
                        type=float, default=0.0)
    general_group.add_argument("--max_bs_dist", help="Maximum distance allowed among bs cvs in the graph. Default 15.0",
                        type=float, default=15.0)
    general_group.add_argument("--min_bs_dist", help="Minimum distance allowed among bs cvs in the graph. Default  0.0",
                        type=float, default=0.0)
    general_group.add_argument("--rmsd_thresh", help="Rmsd threshold to accept a superposition. Default: 1.5",
                        type=float, default=1.5)
    general_group.add_argument("--write_graphml", action="store_true", help="Write graphml files. Default: False",
                        default=False)
    general_group.add_argument("--sensitivity_ah", help="Sensitivity parameter threshold for accepting ah CVs. Default: 0.50",
                        type=float, default=0.50)
    general_group.add_argument("--sensitivity_bs", help="Sensitivity parameter threshold for accepting bs CVs. Default: 0.30",
                        type=float, default=0.30)
    general_group.add_argument("--peptide_length", help="Define the peptide length for computing a CVs. Default: 3", type=int,
                        default=3)
    general_group.add_argument("--cycles", help="Number of iterations performed to extract a maximum match. Default: 15",
                        type=int, default=15)
    general_group.add_argument("--deep", action="store_true", help="Perform a deep search for a maximum match. Default: False",
                        default=False)
    general_group.add_argument("--topn",
                        help="If --deep is active then it is the multiplier for going deep into the solution list, otherwise is the topn of the list. Default: 4",
                        type=int, default=4)

    parser_superpose = subparsers.add_parser("superpose", help='Superpose two pdb models', parents=[general_group])
    parser_superpose.add_argument("--reference", help="Input reference pdb model ", required=True)
    parser_superpose.add_argument("--target", help="Input target pdb model ", required=True)
    parser_superpose.add_argument("--gui", help="Use Graphical User Interface", action='store_true', default=False)
    parser_superpose.add_argument("--core_percentage",
                               help="The minimum percentage that size of the superposed core must cover of the input model to accept the superposition. Default -1 (No use)",
                               type=int, default=-1)
    parser_superpose.add_argument("--force_core_expansion_through_secstr", action="store_true", help=argparse.SUPPRESS)
    parser_superpose.add_argument("--criterium_selection_core", type=str, help="What is the criteria to be used to compute the core_percentage. Default: residues", default="residues", choices=["residues","secondary_structures"])
    parser_superpose.add_argument("--use_signature", action="store_true", help="Use the signature graph to constraits secondary structure matching. Default: False", default=False)
    parser_superpose.add_argument("--match_edges_sign", type=int, help="Number of edges to be matched in the signature. Default: 3", default=3)
    parser_superpose.set_defaults(func=perform_superposition_starter)

    parser_annotate = subparsers.add_parser("annotate", help="Annotate pdbmodel with CVs and produces text and image reports", parents=[general_group])
    parser_annotate.add_argument("--pdbmodel", help="Input a pdb model ", required=True)
    parser_annotate.set_defaults(func=annotate_pdb_model_starter)

    parser_decompose = subparsers.add_parser("decompose", help="Compute community clustering for decomposition in structural units", parents=[general_group])
    parser_decompose.add_argument("--pdbmodel", help="Input a pdb model ", required=True)
    parser_decompose.set_defaults(func=decompose_by_community_clustering_starter)

    parser_findfolds = subparsers.add_parser("find_folds", help="Search and exctracts folds in a protein structure", parents=[general_group])
    parser_findfolds.add_argument("--pdbmodel", help="Input a pdb model ", required=True)
    parser_findfolds.set_defaults(func=find_local_folds_in_the_graph_starter)

    parser_findcentralcores = subparsers.add_parser("find_central_cores", help="Iteratively extracts and writes cores based on centralities", parents=[general_group])
    parser_findcentralcores.add_argument("--pdbmodel", help="Input a pdb model ", required=True)
    parser_findcentralcores.set_defaults(func=find_central_structural_core_shells_starter)

    parser_comparestructures= subparsers.add_parser("compare_structures", help="Compare two structures based on their signatures and graphs", parents=[general_group])
    parser_comparestructures.add_argument("--reference", help="Input reference pdb model ", required=True)
    parser_comparestructures.add_argument("--target", help="Input target pdb model ", required=True)
    parser_comparestructures.add_argument("--core_percentage",
                                  help="The minimum percentage that size of the superposed core must cover of the input model to accept the superposition. Default -1 (No use)",
                                  type=int, default=-1)
    parser_comparestructures.add_argument("--force_core_expansion_through_secstr", action="store_true", help=argparse.SUPPRESS, default=False)
    parser_comparestructures.add_argument("--criterium_selection_core", type=str, help="What is the criteria to be used to compute the core_percentage. Default: residues", default="residues", choices=["residues","secondary_structures"])
    parser_comparestructures.add_argument("--use_seq_alignments", action="store_true", help="When comparing the structures consider also the sequence alignments. Default: False", default=False)
    parser_comparestructures.add_argument("--extract_only_biggest_subfolds", action="store_true", help="When comparing the structures extract only the biggest size of a subfold. Default: False", default=False)
    parser_comparestructures.add_argument("--rmsd_max",  help="Maximum rmsd against any extracted pair. Negative values are interpreted as instruction to do not superpose extracted models. Default: 6.0 (== model difference no grater then 6.0 A)", type=float, default=6.0)
    parser_comparestructures.add_argument("--score_alignment",
                                          help="The minimum score alignment to accept an alignment when comparing two structures. Default 20 (can be negative to accept gaps)",
                                          type=int, default=20)
    parser_comparestructures.add_argument("--size_tree",
                                          help="The number of alternative conformations for the dendogram signature tree. Default 2 (min 1)",
                                          type=int, default=2)
    parser_comparestructures.add_argument("--gap_open",
                                         help="Cost to open a gap when aligning sequences. Default -10 (usually is negative)",
                                         type=int, default=-10)
    parser_comparestructures.set_defaults(func=compare_structures_starter)

    parser_generateensembles= subparsers.add_parser("generate_ensembles", help="Generate ensembles from a set of homologous protein structures", parents=[general_group])
    #parser_generateensembles.add_argument("--pdbmodel", help="Input a pdb model ", required=True)
    parser_generateensembles.add_argument("--directory_database", help="Directory with pdb file models", action='store', required=True)
    parser_generateensembles.add_argument("--size_ensemble", help="Maximum number of models to be included in an ensemble. Default: 20", type=int, default=20)
    parser_generateensembles.add_argument("--core_percentage",
                                          help="The minimum percentage that size of the superposed core must cover of the input model to accept the superposition. Default -1 (No use)",
                                          type=int, default=-1)
    parser_generateensembles.add_argument("--force_core_expansion_through_secstr", action="store_true", help=argparse.SUPPRESS, default=False)
    parser_generateensembles.add_argument("--criterium_selection_core", type=str, help="What is the criteria to be used to compute the core_percentage. Default: residues", default="residues", choices=["residues","secondary_structures"])
    parser_generateensembles.add_argument("--use_seq_alignments", action="store_true",
                                          help="When comparing the structures consider also the sequence alignments. Default: False",
                                          default=False)
    parser_generateensembles.add_argument("--extract_only_biggest_subfolds", action="store_true",
                                          help="When comparing the structures extract only the biggest size of a subfold. Default: False",
                                          default=False)
    parser_generateensembles.add_argument("--rmsd_max",
                                          help="Maximum rmsd against any extracted pair. Negative values are interpreted as instruction to do not superpose extracted models. Default: 6.0 (== model difference no grater then 6.0 A)",
                                          type=float, default=6.0)
    parser_generateensembles.add_argument("--score_alignment",
                                          help="The minimum score alignment to accept an alignment when comparing two structures. Default 20 (can be negative to accept gaps)",
                                          type=int, default=20)
    parser_generateensembles.add_argument("--size_tree",
                                          help="The number of alternative conformations for the dendogram signature tree. Default 2 (min 1)",
                                          type=int, default=2)
    parser_generateensembles.add_argument("--gap_open",
                                          help="Cost to open a gap when aligning sequences. Default -10 (usually is negative)",
                                          type=int, default=-10)
    parser_generateensembles.set_defaults(func=generate_ensembles_starter)

    parser_understanddynamics = subparsers.add_parser("understand_dynamics",
                                                     help="Understand the dynamics of a set of homologous protein structures",
                                                     parents=[general_group])
    parser_understanddynamics.add_argument("--directory_database", help="Directory with pdb file models", action='store',
                                          required=True)
    parser_understanddynamics.add_argument("--size_ensemble",
                                          help="Maximum number of models to be included in an ensemble. Default: 20",
                                          type=int, default=20)
    parser_understanddynamics.add_argument("--core_percentage",
                                          help="The minimum percentage that size of the superposed core must cover of the input model to accept the superposition. Default -1 (No use)",
                                          type=int, default=-1)
    parser_understanddynamics.add_argument("--force_core_expansion_through_secstr", action="store_true", help=argparse.SUPPRESS,
                                          default=False)
    parser_understanddynamics.add_argument("--criterium_selection_core", type=str,
                                          help="What is the criteria to be used to compute the core_percentage. Default: residues",
                                          default="residues", choices=["residues", "secondary_structures"])
    parser_understanddynamics.add_argument("--use_seq_alignments", action="store_true",
                                          help="When comparing the structures consider also the sequence alignments. Default: False",
                                          default=False)
    parser_understanddynamics.add_argument("--extract_only_biggest_subfolds", action="store_true",
                                          help="When comparing the structures extract only the biggest size of a subfold. Default: False",
                                          default=False)
    parser_understanddynamics.add_argument("--rmsd_max",
                                          help="Maximum rmsd against any extracted pair. Negative values are interpreted as instruction to do not superpose extracted models. Default: 6.0 (== model difference no grater then 6.0 A)",
                                          type=float, default=6.0)
    parser_understanddynamics.add_argument("--score_alignment",
                                          help="The minimum score alignment to accept an alignment when comparing two structures. Default 20 (can be negative to accept gaps)",
                                          type=int, default=20)
    parser_understanddynamics.add_argument("--size_tree",
                                          help="The number of alternative conformations for the dendogram signature tree. Default 2 (min 1)",
                                          type=int, default=2)
    parser_understanddynamics.add_argument("--gap_open",
                                          help="Cost to open a gap when aligning sequences. Default -10 (usually is negative)",
                                          type=int, default=-10)
    parser_understanddynamics.set_defaults(func=understand_dynamics_starter)

    parser_compactlibrary= subparsers.add_parser("compact_library", help="Compact BORGES libraries generating superposed ensembled models", parents=[general_group])
    parser_compactlibrary.add_argument("--pdbmodel", help="Input a pdb model ", required=False)
    parser_compactlibrary.add_argument("--directory_database", help="Directory with pdb file models representing the library", action='store', required=True)
    parser_compactlibrary.add_argument("--size_ensemble", help="Maximum number of models to be included in an ensemble. Default: 20", type=int, default=20)
    parser_compactlibrary.add_argument("--number_of_ensembles", help="Number of ensembles to generate from the library. Default: 10", type=int, default=10)
    parser_compactlibrary.add_argument("--core_percentage",
                                          help="The minimum percentage that size of the superposed core must cover of the input model to accept the superposition. Default 60",
                                          type=int, default=60)
    parser_compactlibrary.add_argument("--force_core_expansion_through_secstr", action="store_true", help=argparse.SUPPRESS, default=False)
    parser_compactlibrary.set_defaults(func=compact_library_starter)
    parser_compactlibrary.add_argument("--criterium_selection_core", type=str, help="What is the criteria to be used to compute the core_percentage. Default: residues", default="residues", choices=["residues","secondary_structures"])

    parser_mapvariationslibrary= subparsers.add_parser("map_variations_library", help="Annotate a library by mapping rmsd variations into bfac and occupancies", parents=[general_group])
    parser_mapvariationslibrary.add_argument("--pdbmodel", help="Input a pdb model ",  required=True)
    parser_mapvariationslibrary.add_argument("--directory_database", help="Directory with pdb file models representing the library", action='store', required=True)
    parser_mapvariationslibrary.set_defaults(func=map_variations_library_starter)

    parser_annotatencs= subparsers.add_parser("annotate_ncs", help="Annotate a pdb with NCS in SHELXE format", parents=[general_group])
    parser_annotatencs.add_argument("--pdbmodel", help="Input a pdb model ", required=True)
    parser_annotatencs.add_argument("--ncs_fold", help="Minimum NCS order expected. Default: 2", type=int, default=2)
    parser_annotatencs.add_argument("--core_percentage",
                                       help="The minimum percentage that size of the superposed core must cover of the input model to accept the superposition. Default -1 (No use)",
                                       type=int, default=-1)
    parser_annotatencs.add_argument("--force_core_expansion_through_secstr", action="store_true", help=argparse.SUPPRESS, default=False)
    parser_annotatencs.add_argument("--criterium_selection_core", type=str, help="What is the criteria to be used to compute the core_percentage. Default: residues", default="residues", choices=["residues","secondary_structures"])
    parser_annotatencs.set_defaults(func=annotate_ncs_starter)

    # parser_shiftorigin= subparsers.add_parser("shift_origin", help="Apply to model --pdbmodel the origin shift indicated in --shift", parents=[general_group])
    # parser_shiftorigin.add_argument("--pdbmodel", help="Input a pdb model ",  required=True)
    # parser_shiftorigin.add_argument("--shift", help=" Shift described as x,y,z in fractional coords eg.: 0.0,0.5,0.0 .", type=str, required=True)
    # parser_shiftorigin.set_defaults(func=origin_shift_starter)

    parser_generatelibrary= subparsers.add_parser("generate_library", help="Generate a library of the given fold superposed to the template ready for being used in ARCIMBOLDO_BORGES", parents=[general_group])
    reading = parser_generatelibrary.add_mutually_exclusive_group(required=True)
    reading.add_argument("--pdbmodel", help="Input a pdb model ")
    reading.add_argument("--targz",    help="Read all input from a tar.gz pre-formatted with BORGES_MATRIX for a Grid.")

    parser_generatelibrary.add_argument("--directory_database", help="Directory with pdb file of the deposited structures", action='store', required=True)

    parallelization = parser_generatelibrary.add_mutually_exclusive_group()
    parallelization.add_argument("--supercomputer", help="Nodefile for the supercomputer")
    parallelization.add_argument("--local_grid", help="Path to the setup.bor to start jobs in local grid")
    parallelization.add_argument("--remote_grid", help="Path to the setup.bor to start jobs in remote grid")

    parser_generatelibrary.add_argument("--work_directory", help="Working Directory path. Default is ./", default="./")
    parser_generatelibrary.add_argument("--core_percentage",
                                    help="The minimum percentage that size of the superposed core must cover of the input model to accept the superposition. Default 60",
                                    type=int, default=60)
    parser_generatelibrary.add_argument("--force_core_expansion_through_secstr", action="store_true", help=argparse.SUPPRESS, default=False)
    parser_generatelibrary.add_argument("--criterium_selection_core", type=str, help="What is the criteria to be used to compute the core_percentage. Default: residues", default="residues", choices=["residues","secondary_structures"])
    parser_generatelibrary.add_argument("-C", "--score_intra_fragment", help="Global geometrical match between template and extracted individual fragments expressed as score percentage. Default: 95", type=int, default=95)
    parser_generatelibrary.add_argument("--c_angle", help="Percentage of agreement for internal angles in a fragment. Default: 95", type=int, default=-1)
    parser_generatelibrary.add_argument("--c_dist", help="Percentage of agreement for internal distances in a fragment. Default: 95", type=int, default=-1)
    parser_generatelibrary.add_argument("--c_angle_dist", help="Percentage of agreement for internal distance angles in a fragment. Default: 95", type=int, default=-1)
    parser_generatelibrary.add_argument("--c_cvl_diff", help="Percentage of agreement for internal CVL differences observed in a fragment. Default: 95", type=int, default=-1)
    parser_generatelibrary.add_argument("-J", "--score_inter_fragments", help="Global geometrical match between template and extracted fold expressed as score percentage. Default: 90", type=int, default=90)
    parser_generatelibrary.add_argument("--j_angle", help="Percentage of agreement for external angles between two fragments. Default: 90", type=int, default=-1)
    parser_generatelibrary.add_argument("--j_dist", help="Percentage of agreement for external distances between two fragments. Default: 90", type=int, default=-1)
    parser_generatelibrary.add_argument("--j_angle_dist", help="Percentage of agreement for external distance angles between two fragments. Default: 90", type=int, default=-1)
    parser_generatelibrary.add_argument("--j_cvl_diff", help="Percentage of agreement for external CVL differences observed between two fragments. Default: 90", type=int, default=-1)

    parser_generatelibrary.add_argument("--verbose", action="store_true", help="Verbose output. Default: False", default=False)
    parser_generatelibrary.add_argument("--sidechains", action="store_true", help="Output models with side chains. Default: False", default=False)
    parser_generatelibrary.add_argument("--sequence", help="Require a specific sequence in the output model to match the template. Complete template sequence needs to be given; X marks unspecified residues.", type=str, default="")
    parser_generatelibrary.add_argument("--ncssearch", action="store_true", help="Extract local folds also from NCS relative copies. Default: False", default=False)
    parser_generatelibrary.add_argument("--multimer", action="store_false", help="Remove chain redundancy unless NCS is set. Default: True", default=True)
    parser_generatelibrary.add_argument("--force_core", help="Number of parallel processes. Default: -1 (== #cores machine)", type=int, default=-1)
    parser_generatelibrary.add_argument("--rmsd_min",  help="Minimum rmsd against the template. Default: 0.0 (== extract identical)", type=float, default=0.0)
    parser_generatelibrary.add_argument("--rmsd_max",  help="Maximum rmsd against the template. Default: 6.0 (== model difference no grater then 6.0 A)", type=float, default=6.0)
    parser_generatelibrary.add_argument("--step_diag", help="Step in the descent of the diagonal+1. Default: 1 (== all cvs are visited)", type=int, default=1)
    parser_generatelibrary.add_argument("--rmsd_clustering", help="Rmsd threshold for geometrical clustering of the library. Default: 1.5", type=float, default=1.5)
    parser_generatelibrary.add_argument("--exclude_residues_superpose", help="Number of residues to possibly exclude from the superposition core. Default: 0 (== No exclusion)", type=int, default=0)
    parser_generatelibrary.add_argument("--ssbridge", action="store_true", help="Check for disulphide bridges. Default: False", default=False)
    parser_generatelibrary.add_argument("--nilges", help="Cycles of iteration for the nilges algorithm. Default: 10", type=int, default=10)
    parser_generatelibrary.add_argument("--silencepdbs", action="store_true", dest="silencepdbs", help="Do not write pdb files, but a list of pdbids. Default: False",  default=False)
    parser_generatelibrary.add_argument("--use_lib_to_superpose", action="store_true", help="Use the library extracted as cores to superpose the original PDB to the template. Default: False",  default=False)
    parser_generatelibrary.add_argument("--max_n_models_per_pdb", help="Extract from the same pdb structure no more than the indicated number of models.", type=int, default=1000)
    parser_generatelibrary.add_argument("--enhance_fold", action="store_true",help="Use the minimum fragment length in the template as frgament size for computing CVLs",  default=False)
    parser_generatelibrary.add_argument("--representative", action="store_true", help="For each structure in the PDB database extracts only one model, the one with the lowest rmsd. Default: False",  default=False)
    parser_generatelibrary.add_argument("--remove_coil", action="store_true",  help="Remove coil regions from template before searching. Default: False", default=False)
    parser_generatelibrary.add_argument("--connectivity", action="store_true", help="Fragments extracted must have the same sequence order as template.  Default: False", default=False)

    parser_generatelibrary.set_defaults(func=generate_library_starter)

    parser_generatelibrary_from_sequence = subparsers.add_parser("generate_library_from_sequence",
                                                                  help="Generate a library from a given sequence and secondary structure ready for being used in ARCIMBOLDO_BORGES. This algorithm exploits signatures to predict possible metastructures and folds",
                                                                  parents=[general_group])
    # reading3 = parser_generatelibrary_from_sequence.add_mutually_exclusive_group(required=True)
    # reading3.add_argument("--pdbmodel", help="Input a pdb model ")
    # reading3.add_argument("--targz", help="Read all input from a tar.gz pre-formatted with BORGES_MATRIX for a Grid.")

    parser_generatelibrary_from_sequence.add_argument("--directory_database",
                                                       help="Directory with pdb file of the deposited structures",
                                                       action='store',
                                                       required=True)

    # parallelization3 = parser_generatelibrary_from_sequence.add_mutually_exclusive_group()
    # parallelization3.add_argument("--supercomputer", help="Nodefile for the supercomputer")
    # parallelization3.add_argument("--local_grid", help="Path to the setup.bor to start jobs in local grid")
    # parallelization3.add_argument("--remote_grid", help="Path to the setup.bor to start jobs in remote grid")

    parser_generatelibrary_from_sequence.add_argument("--work_directory", help="Working Directory path. Default is ./", default="./")
    parser_generatelibrary_from_sequence.add_argument("--sequence", help="Path to the template sequence in FASTA format. Complete template sequence needs to be given", type=str, required=True)
    parser_generatelibrary_from_sequence.add_argument("--secondary_structure", help="Path to the template secondary structure prediction in JPRED format (.jalview). Complete prediction needs to be given", type=str, required=True)
    parser_generatelibrary_from_sequence.add_argument("--allowed_coil_difference", help="Number of residues that a coil region can exceed or lack respect the prediction. Default 1", type=int, default=1)
    parser_generatelibrary_from_sequence.set_defaults(func=generatelibrary_from_sequence_starter)

    parser_generatelibrary_with_signature = subparsers.add_parser("generate_library_with_signature",
                                                   help="Generate a library of the given fold superposed to the template ready for being used in ARCIMBOLDO_BORGES. This algorithm exploits signatures for faster and more general library collections",
                                                   parents=[general_group])
    reading2 = parser_generatelibrary_with_signature.add_mutually_exclusive_group(required=True)
    reading2.add_argument("--pdbmodel", help="Input a pdb model ")
    reading2.add_argument("--targz", help="Read all input from a tar.gz pre-formatted with BORGES_MATRIX for a Grid.")

    parser_generatelibrary_with_signature.add_argument("--directory_database",
                                        help="Directory with pdb file of the deposited structures", action='store',
                                        required=True)

    parallelization2 = parser_generatelibrary_with_signature.add_mutually_exclusive_group()
    parallelization2.add_argument("--supercomputer", help="Nodefile for the supercomputer")
    parallelization2.add_argument("--local_grid", help="Path to the setup.bor to start jobs in local grid")
    parallelization2.add_argument("--remote_grid", help="Path to the setup.bor to start jobs in remote grid")

    parser_generatelibrary_with_signature.add_argument("--work_directory", help="Working Directory path. Default is ./", default="./")
    parser_generatelibrary_with_signature.add_argument("--core_percentage",
                                        help="The minimum percentage that size of the superposed core must cover of the input model to accept the superposition. Default 60",
                                        type=int, default=60)
    parser_generatelibrary_with_signature.add_argument("--force_core_expansion_through_secstr", action="store_true",
                                        default=False, help=argparse.SUPPRESS)
    parser_generatelibrary_with_signature.add_argument("--criterium_selection_core", type=str,
                                        help="What is the criteria to be used to compute the core_percentage. Default: residues",
                                        default="residues", choices=["residues", "secondary_structures"])
    parser_generatelibrary_with_signature.add_argument("-C", "--score_intra_fragment",
                                                       help=argparse.SUPPRESS,
                                        type=int, default=95)
    parser_generatelibrary_with_signature.add_argument("--c_angle",
                                                       help=argparse.SUPPRESS,
                                        type=int, default=-1)
    parser_generatelibrary_with_signature.add_argument("--c_dist",
                                                       help=argparse.SUPPRESS,
                                        type=int, default=-1)
    parser_generatelibrary_with_signature.add_argument("--c_angle_dist",
                                                       help=argparse.SUPPRESS,
                                        type=int, default=-1)
    parser_generatelibrary_with_signature.add_argument("--c_cvl_diff",
                                                       help=argparse.SUPPRESS,
                                        type=int, default=-1)
    parser_generatelibrary_with_signature.add_argument("-J", "--score_inter_fragments",
                                                       help=argparse.SUPPRESS,
                                        type=int, default=90)
    parser_generatelibrary_with_signature.add_argument("--j_angle",
                                                       help=argparse.SUPPRESS,
                                        type=int, default=-1)
    parser_generatelibrary_with_signature.add_argument("--j_dist",
                                                       help=argparse.SUPPRESS,
                                        type=int, default=-1)
    parser_generatelibrary_with_signature.add_argument("--j_angle_dist",
                                                       help=argparse.SUPPRESS,
                                        type=int, default=-1)
    parser_generatelibrary_with_signature.add_argument("--j_cvl_diff",
                                                       help=argparse.SUPPRESS,
                                        type=int, default=-1)

    parser_generatelibrary_with_signature.add_argument("--verbose", action="store_true", help="Verbose output. Default: False",
                                        default=False)
    parser_generatelibrary_with_signature.add_argument("--sidechains", action="store_true",
                                        help="Output models with side chains. Default: False", default=False)
    parser_generatelibrary_with_signature.add_argument("--sequence",
                                        help=argparse.SUPPRESS,
                                        type=str, default="")
    parser_generatelibrary_with_signature.add_argument("--ncssearch", action="store_true",
                                        help="Extract local folds also from NCS relative copies. Default: False",
                                        default=False)
    parser_generatelibrary_with_signature.add_argument("--multimer", action="store_false",
                                        help="Remove chain redundancy unless NCS is set. Default: True", default=True)
    parser_generatelibrary_with_signature.add_argument("--force_core",
                                        help="Number of parallel processes. Default: -1 (== #cores machine)", type=int,
                                        default=-1)
    parser_generatelibrary_with_signature.add_argument("--rmsd_min",
                                        help="Minimum rmsd against the template. Default: 0.0 (== extract identical)",
                                        type=float, default=0.0)
    parser_generatelibrary_with_signature.add_argument("--rmsd_max",
                                        help="Maximum rmsd against the template. Default: 6.0 (== model difference no grater then 6.0 A)",
                                        type=float, default=6.0)
    parser_generatelibrary_with_signature.add_argument("--step_diag",
                                        help=argparse.SUPPRESS,
                                        type=int, default=1)
    parser_generatelibrary_with_signature.add_argument("--rmsd_clustering",
                                        help=argparse.SUPPRESS,
                                        type=float, default=1.5)
    parser_generatelibrary_with_signature.add_argument("--exclude_residues_superpose",
                                        help=argparse.SUPPRESS,
                                        type=int, default=0)
    parser_generatelibrary_with_signature.add_argument("--ssbridge", action="store_true",
                                        help=argparse.SUPPRESS, default=False)
    parser_generatelibrary_with_signature.add_argument("--nilges", help="Cycles of iteration for the nilges algorithm. Default: 10",
                                        type=int, default=10)
    parser_generatelibrary_with_signature.add_argument("--silencepdbs", action="store_true", dest="silencepdbs",
                                        help=argparse.SUPPRESS,
                                        default=False)
    parser_generatelibrary_with_signature.add_argument("--use_lib_to_superpose", action="store_true",
                                        help=argparse.SUPPRESS,
                                        default=False)
    parser_generatelibrary_with_signature.add_argument("--max_n_models_per_pdb",
                                        help=argparse.SUPPRESS,
                                        type=int, default=1000)
    parser_generatelibrary_with_signature.add_argument("--enhance_fold", action="store_true",
                                        help=argparse.SUPPRESS,
                                        default=False)
    parser_generatelibrary_with_signature.add_argument("--representative", action="store_true",
                                                       help=argparse.SUPPRESS,
                                                       default=False)
    parser_generatelibrary_with_signature.add_argument("--signature_strict_angles_bs", action="store_true",
                                                       help="Signature cannot allow swap beta strand directions. Default: False",
                                                       default=False)
    parser_generatelibrary_with_signature.add_argument("--signature_threshold",
                                                       help="Minimum threshold to be reached when aligning signatures (0.01, 1.00). Default: 0.1",
                                                       type=float, default=0.1)
    parser_generatelibrary_with_signature.add_argument("--remove_coil", action="store_true",
                                        help="Remove coil regions from template before searching. Default: False",
                                        default=False)
    parser_generatelibrary_with_signature.add_argument("--connectivity", action="store_true",
                                        help=argparse.SUPPRESS,
                                        default=False)

    parser_generatelibrary_with_signature.set_defaults(func=generatelibrary_with_signature_starter)

    print("*******************************************COMMAND LINE**************************************************")
    print(" ".join(sys.argv))
    print("*********************************************************************************************************")

    args = parser.parse_args()
    #try:
    args.func(args)
    #except AttributeError:
    #parser.print_usage()

    print("Time elapsed: {:.2f}s".format(time.time() - start_time))

    t = datetime.datetime.now()
    epcSec = time.mktime(t.timetuple())
    now = datetime.datetime.fromtimestamp(epcSec)
    print("" + str(now.ctime()))

    print("Job ended with success")
