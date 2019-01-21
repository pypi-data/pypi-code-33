#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module with assorted geometrical functions on
macromolecules.
"""

import sys
from math import sqrt

from Bio.PDB import Entity
from numpy import *

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


def center_of_mass(entity, geometric=False):
    """
    Returns gravitic [default] or geometric center of mass of an Entity.
    Geometric assumes all masses are equal (geometric=True)
    """
    # Structure, Model, Chain, Residue
    if isinstance(entity, Entity.Entity):
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


def calculate_shape_param(structure):
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

    if isinstance(structure, Entity.Entity):
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

    gy_tensor = mat(
        [[tensor_xx, tensor_yx, tensor_xz], [tensor_yx, tensor_yy, tensor_yz], [tensor_xz, tensor_yz, tensor_zz]])
    gy_tensor = (1.0 / n_atoms) * gy_tensor

    D, V = linalg.eig(gy_tensor)
    [a, b, c] = sorted(sqrt(D))  # lengths of the ellipsoid semi-axis
    rg = sqrt(sum(D))

    l = average([D[0], D[1], D[2]])
    A = (((D[0] - l) ** 2 + (D[1] - l) ** 2 + (D[2] - l) ** 2) / l ** 2) * 1 / 6
    S = (((D[0] - l) * (D[1] - l) * (D[2] - l)) / l ** 3)

    return ((a * 2, b * 2, c * 2), rg, A, S)

    # print "%s" % '#Dimensions(a,b,c) #Rg #Anisotropy'
    # print "%.2f" % round(a,2), round(b,2), round(c,2) , round(rg,2) , round(A,2)


def calculate_moment_of_intertia_tensor(structure):
    """
    Calculates the moment of inertia tensor from the molecule.
    Returns a numpy matrix.
    """

    if isinstance(structure, Entity.Entity):
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

    if isinstance(structure, Entity.Entity):
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

    in_tensor = mat([[tensor_xx, tensor_xy, tensor_xz], [tensor_xy, tensor_yy, tensor_yz], [tensor_xz,
                                                                                            tensor_yz, tensor_zz]])
    D, V = linalg.eig(in_tensor)

    a = sqrt((5 / (2 * s_mass)) * (D[0] - D[1] + D[2]))
    b = sqrt((5 / (2 * s_mass)) * (D[2] - D[0] + D[1]))
    c = sqrt((5 / (2 * s_mass)) * (D[1] - D[2] + D[0]))
    return sorted([a, b, c]), D, V


if __name__ == "__main__":
    import Bioinformatics

    structure = Bioinformatics.getStructure("ref", sys.argv[1])
    tuplona = calculate_moment_of_intertia_tensor(structure)
    # for atom in structure.get_atoms():
    #       atom.mass = atom_weights[atom.element.capitalize()]
    com = center_of_mass(structure, False)
    com = com.coord
    print "The centroid of mass is: " + str('%.2f' % (com[0])) + ", " + str('%.2f' % (com[1])) + ", " + str(
        '%.2f' % (com[2]))
    print "The tensor of the moment of inertia is: " + str('%.2f' % (tuplona[0][0])) + ", " + str(
        '%.2f' % (tuplona[0][1])) + ", " + str('%.2f' % (tuplona[0][2]))
    print "Autovalors are: " + str('%.2f' % (tuplona[1][0])) + ", " + str('%.2f' % (tuplona[1][1])) + ", " + str(
        '%.2f' % (tuplona[1][2]))
