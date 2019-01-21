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

"""Contains class and function needed to perform a digestion"""
import os
import random
from rpg import core
from rpg import rule
from rpg import sequence

class ResultOneDigestion:
    """Result of the digestion of one sequence by one enzyme.

    :param enzyme_name: name of the enzyme used
    :param peptides: all resulting peptides after digestion
    :param nb_cleavage: number of cleavage that occurs
    :param pos_miscleavage: position of miscleavage that occurs
    :type enzyme_name: str
    :type peptides: list(:py:class:`~rpg.sequence.Peptide`)
    :type nb_cleavage: int
    :type pos_miscleavage: list(int)
    """
    def __init__(self, enzyme_name, peptides=None, nb_cleavage=0,
                 pos_miscleavage=None):
        self.enzyme_name = enzyme_name  # Enzyme name used for this digestion
        self.peptides = peptides
        if self.peptides is None:
            self.peptides = []
        self.nb_cleavage = nb_cleavage  # number of cleavage
        self.pos_miscleavage = pos_miscleavage  # position of m-c
        if self.pos_miscleavage is None:
            self.pos_miscleavage = []

    # self representation for print
    def __repr__(self):
        return "Number of cleavage: " + str(self.nb_cleavage) + \
               "\nNumber of miscleavage: " + \
               str(len(self.pos_miscleavage)) + \
               "\nPositions of miscleavage: " + str(self.pos_miscleavage)\
               + "\nRatio of miscleavage: " + \
               str(self.get_ratio_miscleavage()) + \
               "\nPeptides: " + str(self.peptides) + "\n"

    # Equality between two ResultOneDigestion
    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    # Needed with __eq__ to make it hashable
    def __hash__(self):
        return hash(self.__dict__.values())

    # Create a clean output according to fmt
    def __format__(self, fmt):
        ret = ""
        for peptide in self.peptides:
            ret += format(peptide, fmt) + "\n"
        return ret

    def pop_peptides(self):
        """Empty :attr:`self.peptides` and returns all peptides.

        :return: all the peptides
        :rtype: list(:py:class:`~rpg.sequence.Peptide`)
        """
        ret = self.peptides[:]
        self.peptides = []
        return ret

    def add_peptide(self, pep):
        """Add a peptide to :attr:`self.peptides`.

        :param pep: peptide to add
        :type pep: :py:class:`~rpg.sequence.Peptide`
        """
        self.peptides.append(pep)

    def inc_nb_cleavage(self):
        """Increase :attr:`self.nb_cleavage` by 1."""
        self.nb_cleavage += 1

    def get_nb_miscleavage(self):
        """Get the number of miscleavages that occurs
        on this digestion.

        :return: number of miscleavage
        :rtype: int
        """
        return len(self.pos_miscleavage)

    def add_miscleavage(self, new_pos_miscleavage):
        """Add a miscleavage to :attr:`self.pos_miscleavage`.

        :param new_pos_miscleavage: position of miscleavage
        :type new_pos_miscleavage: int
        """
        self.pos_miscleavage.append(new_pos_miscleavage)

    def get_ratio_miscleavage(self):
        """Get ratio of miscleavage.

        :return: ratio of miscleavage
        :rtype: float
        """
        ret = 0
        if self.nb_cleavage > 0 or self.get_nb_miscleavage() > 0:
            ret = self.get_nb_miscleavage() / (self.nb_cleavage + \
                                                 self.get_nb_miscleavage()) \
                                              * 100
        return ret

    def get_miscleavage_pos(self):
        """Get positions of miscleavage as a string.

        :return: positions of miscleavage
        :rtype: str
        """
        ret = ""
        for i in self.pos_miscleavage:
            ret += str(i) + ", "
        return ret[:-2]

    def get_cleavage_pos(self):
        """Get positions of cleavage as a string.

        :return: positions of cleavage
        :rtype: str
        """
        ret = ""
        # Ignore last position, i.e. end of input sequence
        for i in self.peptides[:-1]:
            ret += str(i.position) + ", "
        return ret[:-2]

    def merge(self, other):
        """Fuse two :py:class:`ResultOneDigestion` by adding to
        :attr:`self` the peptides of :attr:`other` and changing their
        :py:class:`~rpg.enzyme.Enzyme`. It also update :attr:`self.nb_cleavage` and
        :attr:`self.pos_miscleavage`.

        :param other: object to fuse with `self`
        :type other: :py:class:`ResultOneDigestion`
        """
        # Add Peptides from other and change their enzyme_name
        for peptide in other.peptides:
            peptide.enzyme_name = self.enzyme_name
            self.add_peptide(peptide)
        # Add nb_cleavage from other
        self.nb_cleavage += other.nb_cleavage
        # Add pos_miscleavage from other
        self.pos_miscleavage += other.pos_miscleavage

    def get_smallest_peptide(self):
        """Get the (first) smallest peptide of :attr:`self.peptides`.

        :return: the smallest peptide
        :rtype: :py:class:`~rpg.sequence.Peptide`
        """
        small = self.peptides[0]
        for i in self.peptides[1:]:
            if i.size < small.size:
                small = i
        return small

    def get_more_info(self):
        """Return informations and statistics about this digestion,
        *i.e.* number of (mis)-cleavages and positions, miscleavage
        ratio, size of the smallest peptide and first and last peptide.

        :return: informations and statistics ready to be printed
        :rtype: str
        """
        ret = ""
        ret += "\nNumber of cleavage: " + str(self.nb_cleavage) + "\n"
        ret += "Cleavage position: " + self.get_cleavage_pos() + "\n"
        ret += "Number of miscleavage: " + str(self.get_nb_miscleavage())\
               + "\n"
        ret += "miscleavage position: " + self.get_miscleavage_pos() + "\n"
        ret += "miscleavage ratio: %.2f%%\n" % self.get_ratio_miscleavage()
        ret += "Smallest peptide size: " + \
                str(self.get_smallest_peptide().size) + "\n"
        ret += "N terminal peptide: " + self.peptides[0].sequence + "\n"
        ret += "C terminal peptide: " + self.peptides[-1].sequence
        return ret

def one_digest(pep, enz, aa_pka):
    """Digest a peptide with an enzyme.

    :param pep: peptide to digest
    :param enz: enzyme to digest with
    :param aa_pka: pKa values (IPC / Stryer)
    :type pep: :py:class:`~rpg.sequence.Peptide`
    :type enz: :py:class:`~rpg.enzyme.Enzyme`
    :type aa_pka: str

    :return: result of the digestion
    :rtype: :py:class:`ResultOneDigestion`
    """
    enzyme_name = enz.name
    ret = ResultOneDigestion(enzyme_name)
    # Original pos is index of starting position of this peptide (0)
    # but in the original sequence
    if pep.position > 0:
        original_pos = pep.position - len(pep.sequence)
    else:
        original_pos = 0
    cpt = 0
    previous_pos = 0
    after = False
    a_cut_occurs = False
    # For each letter of the peptide
    for pos, _ in enumerate(pep.sequence):
        # We need to cut here because of previous pos
        if after:
            after = False
            tmp_seq = pep.sequence[previous_pos:pos]
            tmp_peptide = sequence.Peptide(pep.header, tmp_seq, enzyme_name,
                                           aa_pka, cpt, pos + original_pos)
            ret.add_peptide(tmp_peptide)
            cpt += 1
            a_cut_occurs = True
            # A cleavage occur
            ret.inc_nb_cleavage()
            # current position
            previous_pos = pos
        before = True
        # Check each rules
        for rul in enz.rules:
            # Default: do not cut this position
            cut = None
            # Apply the rule: if we need to cut
            cut = rule.handle_rule(pep.sequence, pos, rul, cut)
            if cut is True:
                # Random to handle miscleavage
                tmp_rand = random.random() * 100
                # Rand > ratio_miscleavage, no miscleavage occurs
                if tmp_rand > enz.ratio_miscleavage:
                    # Test, this should NEVER be used
                    if rul.pos == -1:
                        core.handle_errors("not able to understand if I shou"
                                           "ld cut BEFORE or AFTER the restri"
                                           "ction site:("
                                           , 0, "Fatal ")
                    # Cut AFTER
                    elif rul.pos == 1:
                        # We need to cut at the next pos
                        after = True
                    # Cut BEFORE
                    elif rul.pos == 0 and before and pos != 0:
                        # Prevent blank return if we already cut AFTER
                        # the last letter, i.e. (,A,) on AA
                        if previous_pos != pos:
                            tmp_seq = pep.sequence[previous_pos:pos]
                            tmp_peptide = sequence.Peptide(pep.header, tmp_seq,
                                                           enzyme_name, aa_pka,
                                                           cpt,
                                                           pos + original_pos)
                            ret.add_peptide(tmp_peptide)
                            cpt += 1
                            # current position
                            previous_pos = pos
                            # Only cut once, even if severals rules say
                            # to cut here
                            before = False
                            a_cut_occurs = True
                            # A cleavage occur
                            ret.inc_nb_cleavage()
                # A miscleavage occurs
                else:
                    ret.add_miscleavage(pos)
    # End of the peptide
    if a_cut_occurs:
        tmp_pos = len(pep.sequence)  # Last portion of protein
        tmp_seq = pep.sequence[previous_pos:]
        tmp_peptide = sequence.Peptide(pep.header, tmp_seq, enzyme_name,
                                       aa_pka, cpt, tmp_pos + original_pos)
        ret.add_peptide(tmp_peptide)
    # Not cut, don't change the peptide
    else:
        ret.add_peptide(pep)
    return ret

def digest_one_sequence(seq, enz, mode, aa_pka):
    """Launch a digest procedure on one sequence.

    :param sequence: sequence to digest
    :param enz: enzymes to digest with
    :param mode: digestion mode (concurrent / sequential)
    :param aa_pka: pKa values (IPC / Stryer)
    :type sequence: :py:class:`~rpg.sequence.Sequence`
    :type enz: list(:py:class:`~rpg.enzyme.Enzyme`)
    :type mode: str
    :type aa_pka: str

    :return: result of the digestion
    :rtype: list(:py:class:`ResultOneDigestion`)
    """
    ret = None
    if mode == "sequential":
        ret = sequential_digest(seq, enz, aa_pka)
    elif mode == "concurrent":
        ret = concurrent_digest(seq, enz, aa_pka)
    else:
        core.handle_errors("not able to understand digetion mode. Switching "
                           "to 'sequential'.")
        ret = sequential_digest(seq, enz, aa_pka)
    return ret

def sequential_digest(seq, enz, aa_pka):
    """Sequentially digest a sequence with all Enzymes, **one by one**.

    :param seq: sequence to digest
    :param enz: enzymes to digest with
    :param aa_pka: pKa values (IPC / Stryer)
    :type seq: :py:class:`~rpg.sequence.Sequence`
    :type enz: list(:py:class:`~rpg.enzyme.Enzyme`)
    :type aa_pka: str

    :return: result of the digestion
    :rtype: list(:py:class:`ResultOneDigestion`)
    """
    ret = []  # List of ResultOneDigestion
    # Check each enzymes
    for an_enz in enz:
        # Create a fake peptide from input sequence
        fake_peptide = sequence.Peptide(seq.header, seq.sequence, an_enz.name,
                                        aa_pka)
        # Digest it
        ret.append(one_digest(fake_peptide, an_enz, aa_pka))
    return ret

def concurrent_digest(seq, enz, aa_pka):
    """Concurrently digest a sequence with all Enzymes **at the same
    time**.

    :param seq: sequence to digest
    :param enz: enzymes to digest with
    :param aa_pka: pKa values (IPC / Stryer)
    :type seq: :py:class:`~rpg.sequence.Sequence`
    :type enz: list(:py:class:`~rpg.enzyme.Enzyme`)
    :type aa_pka: str

    :return: result of the digestion
    :rtype: list(:py:class:`ResultOneDigestion`)
    """

    # Create the correct name for merged enzymes
    enzymes_name_to_write = ""
    for an_enz in enz:
        enzymes_name_to_write += an_enz.name + "-"
    enzymes_name_to_write = enzymes_name_to_write[:-1]
    # First peptide is the sequence itself
    fake_peptide = sequence.Peptide(seq.header, seq.sequence,
                                    enzymes_name_to_write, aa_pka)
    # Result is currently just the sequence (list of one peptide)
    result = ResultOneDigestion(enzymes_name_to_write, [fake_peptide])
    # Do we digest as much as we can?
    need_more_digest = True
    # As long as we can digest
    while need_more_digest:
        # Save previous stat
        pep_orig = result.peptides
        # Check each enzymes
        for an_enz in enz:
            # Result of the digest
            all_res_digestion_tmp = []
            # For each peptides to digest,
            # remove them from the global result
            for peptide in result.pop_peptides():
                # Digest it, return a list of ResultOneDigestion
                all_res_digestion_tmp.append(one_digest(peptide, an_enz,
                                                        aa_pka))
            # Merge the result of digestion with previous result
            for i in all_res_digestion_tmp:
                result.merge(i)
        # If we didn't digest anything, it is finish
        if result.peptides == pep_orig:
            # Stop digesting
            need_more_digest = False
    # Correct peptide number
    cpt = 0
    for i in result.peptides:
        i.nb_peptide = cpt
        cpt += 1
    # Return peptides as a list.
    # If it is one digestion but in sequential
    # it will be one result by enzyme
    return [result]

def digest_from_input(input_data, enz, mode, aa_pka):
    """Digest all sequences of input data with
    selected enzymes and mode.

    :param input_data: either a sequence or a file of sequence (fasta/fastq)
    :param enz: enzymes to digest with
    :param mode: digestion mode (concurrent / sequential)
    :param aa_pka: pKa values (IPC / Stryer)
    :type input_data: str
    :type enz: list(:py:class:`~rpg.enzyme.Enzyme`)
    :type mode: str
    :type aa_pka: str

    :return: result of digestions
    :rtype: list(list(:py:class:`ResultOneDigestion`))
    """
    # Results of digestion
    results_digestion = []
    # Input is a file?
    if os.path.isfile(input_data):
        with open(input_data) as in_file:
            header_first_car = in_file.read(1)
            in_file.seek(0)
            # Fasta file, can be multi-line
            if header_first_car == ">":
                # First header
                header = in_file.readline().strip()
                # First line
                tmp_line = in_file.readline().strip()
                seq = ""
                while tmp_line:
                    if not tmp_line.startswith(">"):
                        seq += tmp_line
                        tmp_line = in_file.readline().strip()
                    else:
                        # Create a Sequence
                        tmp_seq = sequence.Sequence(header[1:],
                                                    sequence.check_sequence(seq))
                        # Digest sequence
                        results_digestion.append(digest_one_sequence
                                                 (tmp_seq, enz, mode, aa_pka))
                        seq = ""
                        header = tmp_line
                        tmp_line = in_file.readline().strip()
                # Last sequence to digest
                tmp_seq = sequence.Sequence(header[1:],
                                            sequence.check_sequence(seq))
                # Digest it
                results_digestion.append(digest_one_sequence(tmp_seq, enz,
                                                             mode, aa_pka))
            # Fastq file
            elif header_first_car == "@":
                header = in_file.readline().strip()
                while header:
                    seq = in_file.readline().strip()
                    tmp_seq = sequence.Sequence(header[1:],
                                                sequence.check_sequence(seq))
                    # Digest sequence
                    results_digestion.append(digest_one_sequence(tmp_seq, enz,
                                                                 mode, aa_pka))
                    in_file.readline()
                    in_file.readline()
                    header = in_file.readline().strip()
            else:
                core.handle_errors("input file format not recognized (%s)." %
                                   header_first_car, 0, "Input ")
    # input is a single sequence
    else:
        tmp_seq = sequence.Sequence("Input",
                                    sequence.check_sequence(input_data))
        # Digest the sequence
        results_digestion.append(digest_one_sequence(tmp_seq, enz, mode,
                                                     aa_pka))
    # Return all peptides
    return results_digestion
