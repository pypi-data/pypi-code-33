# -*- coding: utf-8 -*-

########################################################################
# Author: Nicolas Maillet                                              #
# Copyright © 2018 Institut Pasteur, Paris.                            #
# See the COPYRIGHT file for details                                   #
#                                                                      #
# This file is part of Rapid Peptide Generator (RPG) software.         #
#                                                                      #
# RPG is free software: you can redistribute it and/or modify          #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or    #
# any later version.                                                   #
#                                                                      #
# RPG is distributed in the hope that it will be useful,               #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public license    #
# along with RPG (LICENSE file).                                       #
# If not, see <http://www.gnu.org/licenses/>.                          #
########################################################################

"""Contains classes and function related to sequences"""
from rpg import core

class Peptide:
    """Definition of a peptide, containing the header of its original
    sequence, an amino acid sequence, the name of the enzyme used to
    produce it and more informations.

    :param header: header of the peptide
    :param sequence: sequence in amino acids
    :param enzyme_name: name of the enzyme used
    :param aa_pka: pKa values (IPC / Stryer)
    :param nb_peptide: number of this peptide (default: 0)
    :param position: position of cleavage on the original sequence (default: 0)
    :type header: str
    :type sequence: str
    :type enzyme_name: str
    :type aa_pka: str
    :type nb_peptide: int
    :type position: int

    :var size: size of the peptide
    :var mass: mass of the peptide
    :var p_i: pI of the peptide
    :vartype size: int
    :vartype mass: float
    :vartype p_i: float
    """
    def __init__(self, header, sequence, enzyme_name, aa_pka, nb_peptide=0,
                 position=0):
        self.header = header  # header of this peptide
        self.sequence = sequence  # peptide sequence
        self.enzyme_name = enzyme_name  # name of the enzyme used
        self.aa_pka = aa_pka # pKa values for pI calculation
        self.nb_peptide = nb_peptide  # number of this peptide
        self.position = position  # position of cleavage
        self.size = len(sequence)  # size of the peptide
        # Mass of the peptide
        tmp_mass = core.WATER_MASS
        for i in sequence:
            tmp_mass += core.AA_MASS_AVERAGE[i]
        self.mass = round(tmp_mass, 5)  # mass of the peptide
        self.p_i = self.get_isoelectric_point()

    # self representation for print
    def __repr__(self):
        pka = "IPC"
        if self.aa_pka == core.AA_PKA_S:
            pka = "Stryer"
        return "Original header: " + self.header + "\nNo. peptide: " + \
            str(self.nb_peptide) + "\nEnzyme: " + self.enzyme_name + \
            "\nCleav. pos: " + str(self.position) + "\nPep. size: " + \
            str(self.size) + "\nPep. mass: " + str(self.mass) + \
            "\npKa values from: " + pka + "\nPep. pI: " + str(self.p_i) +\
            "\nSequence: " + self.sequence + "\n"

    # Equality between two Peptides
    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    # Create a clean output according to fmt
    def __format__(self, fmt):
        ret = ""
        # Formating the print according to format
        if fmt == "fasta":
            ret += ">"
            separator = "_"
        elif fmt == "csv":
            separator = ","
        else:
            separator = "\t"
        # Main values to print
        ret += self.header + separator + str(self.nb_peptide) + separator + \
            self.enzyme_name + separator + str(self.position) + separator + \
            str(self.size) + separator + str(self.mass) + separator + \
            str(self.p_i)
        # Last separator, \n for fasta format
        if fmt == "fasta":
            ret += "\n"
        else:
            ret += separator
        # End of the print
        ret += self.sequence
        return ret

    def get_isoelectric_point(self):
        """Compute isoelectric point (pI) of the peptide using
        binary search.

        :return: computed pI
        :rtype: float

        :note: This function used :py:const:`~rpg.core.AA_PKA`
        """
        ph_val = 7 # Neutral pH, starting point of binary search
        ph_min = 0.0 # Minimal pH
        ph_max = 14.0 # Maximal pH
        precision = 0.01
        # While we are not precise enough
        while (ph_val-ph_min > precision) or (ph_max-ph_val > precision):
            # Compute the pI
            qn1 = -1.0 / (1.0 + pow(10, (self.aa_pka["Cterm"] - ph_val)))
            qn2 = -self.sequence.count('D') / (1.0 + pow(10, (self.aa_pka["D"]-
                                                              ph_val)))
            qn3 = -self.sequence.count('E') / (1.0 + pow(10, (self.aa_pka["E"]-
                                                              ph_val)))
            qn4 = -self.sequence.count('C') / (1.0 + pow(10, (self.aa_pka["C"]-
                                                              ph_val)))
            qn5 = -self.sequence.count('Y') / (1.0 + pow(10, (self.aa_pka["Y"]-
                                                              ph_val)))
            qp1 = self.sequence.count('H') / (1.0 + pow(10, (ph_val -
                                                             self.aa_pka["H"])))
            qp2 = 1.0 / (1.0 + pow(10, (ph_val - self.aa_pka["Nterm"])))
            qp3 = self.sequence.count('K') / (1.0 + pow(10, (ph_val -
                                                             self.aa_pka["K"])))
            qp4 = self.sequence.count('R') / (1.0 + pow(10, (ph_val -
                                                             self.aa_pka["R"])))
            nq_final = qn1 + qn2 + qn3 + qn4 + qn5 + qp1 + qp2 + qp3 + qp4
            # We are below solution, good pH value must be smaller
            if nq_final < 0.0:
                ph_max = ph_val
                ph_val -= (ph_max - ph_min) / 2
            # We are above solution, good pH value must be bigger
            else:
                ph_min = ph_val
                ph_val += (ph_max - ph_min) / 2
        # We got a good enough pH value
        return round(ph_val, 2)

class Sequence:
    """Definition of an amino acid sequence to digest.

    :param header: header of the sequence
    :param sequence: sequence itself
    :type header: str
    :type sequence: str
    """
    def __init__(self, header, sequence):
        self.header = header  # header of this peptide
        self.sequence = sequence  # peptide sequence

    # self representation for print
    def __repr__(self):
        return "Header: " + self.header + "\nSequence: " + self.sequence + "\n"

    # Equality between two Sequences
    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

def check_sequence(seq):
    """Validate an input sequence. Each amino acid should be in
    :py:const:`~rpg.core.AMINOACIDS`.

    :param seq: the sequence to check
    :type seq: str

    :return: Sequence in UPPERCASE
    :rtype: str
    """
    validate = seq.strip().upper()
    for i in validate:
        if i not in core.AMINOACIDS:
            core.handle_errors("amino acid \"%s\" in %s not recognized." %
                               (i, validate), 0, "Sequence ")
    return validate
