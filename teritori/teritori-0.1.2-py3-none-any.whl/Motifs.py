#!/usr/bin/env python

import os
import numpy as np
from os import system
import subprocess
from io import StringIO
from Bio import SeqIO
from BCBio import GFF
from pylab import *


"""---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------FUNCTIONS---------------------------------------------------------"""


def finding_rrnas(in_file):
    """
    Runs RNAmmer-1.2 to find rRNA genes and parses the output

    :param in_file: The input FASTA file to be analyzed
    :return: Returns a list containing the rRNA genes
    """

    '''Get current working directory'''
    cwd = os.path.dirname(os.path.abspath( __file__ )) + '/conserved_motifs/rnammer'

    var_rnammer = subprocess.Popen(['perl', cwd, '-S', 'bac', '-m', 'lsu,ssu', '-gff', '-', in_file],
                                   stdout=subprocess.PIPE)
    out_file = StringIO(var_rnammer.stdout.read().decode('utf-8'))

    '''List for storing rRNA coordinates'''
    rnammer_res = list()

    '''Fetches the start and end position, and the strand location from the output of RNAmmer'''
    for mot in GFF.parse(out_file):
        for gene_feature in mot.features:
            rnammer_res.append([int(gene_feature.location.start), int(gene_feature.location.end),
                                gene_feature.location.strand])

    '''Sorts the result'''
    rnammer_res.sort()

    return rnammer_res


def finding_ori(rrnas_in, in_seq_len):
    """
    Finds the positions for Ori based on rRNAs
    Input:
    :param rrnas_in:    List of rRNA genes from RNAmmer
    :param in_seq_len:  Length of the input FASTA sequence
    :param linear:      Specifies if the chromosome is linear
    :return: Positions for Ori based on rRNAs
    """

    '''List for storing the interval coordinates'''
    shift = list()
    for i in range(len(rrnas_in)):
        if i == len(rrnas_in) - 1:
            if rrnas_in[i][2] != rrnas_in[0][2]:
                shift.append(i)
        else:
            if rrnas_in[i][2] != rrnas_in[i+1][2]:
                shift.append(i)

    if len(shift) != 2:
        return [0, 0]
    elif len(shift) == 2:
        if rrnas_in[shift[0]][2] == -1:
            ori_start = rrnas_in[shift[0]][1]
            ori_end = rrnas_in[shift[0]+1][0]
            return [ori_start, ori_end]
        elif rrnas_in[shift[1]][2] == -1:
            if shift[1] == len(rrnas_in) - 1:
                ori_start = rrnas_in[shift[1]][1]
                ori_end = rrnas_in[0][0]
                return [ori_start, ori_end]
            else:
                ori_start = rrnas_in[shift[1]][1]
                ori_end = rrnas_in[shift[1] + 1][0]
                return [ori_start, ori_end]


def finding_ter(rrnas_in, in_seq_len):
    """
    Finds the positions for Ter based on rRNAs

    :param rrnas_in:    List of rRNA genes from RNAmmer
    :param in_seq_len:  The length of the input FASTA sequence
    :return: Positions for Ter based on rRNAs
    """

    '''List for storing the interval coordinates'''
    shift = list()
    for i in range(len(rrnas_in)):
        if i == len(rrnas_in) - 1:
            if rrnas_in[i][2] != rrnas_in[0][2]:
                shift.append(i)
        else:
            if rrnas_in[i][2] != rrnas_in[i+1][2]:
                shift.append(i)

    if len(shift) != 2:
        return [0, 0]
    elif len(shift) == 2:
        if rrnas_in[shift[1]][2] == 1:
            if shift[1] == len(rrnas_in) - 1:
                ter_start = rrnas_in[shift[1]][1]
                ter_end = rrnas_in[0][0]
                return [ter_start, ter_end]
            else:
                ter_start = rrnas_in[shift[1]][1]
                ter_end = rrnas_in[shift[1]+1][0]
                return [ter_start, ter_end]
        elif rrnas_in[shift[0]][2] == 1:
            ter_start = rrnas_in[shift[0]][1]
            ter_end = rrnas_in[shift[0]+1][1]
            return [ter_start, ter_end]


def hmm_runner(in_file, hmm_file, out_path):
    """
    Runs nhmmer to find motifs

    :param in_file:     Input FASTA file to be analyzed
    :param hmm_file:    hmm file of the aligned motifs
    :param out_path:    Path of output file
    :return: Nada
    """
    # The command to be run by nhmmer
    cmd = ('nhmmer --dfamtblout %s -E 1000 --F3 1 %s %s '
           '> ./out_test.hmm' % (out_path, hmm_file, in_file))

    '''Executes the command'''
    system(cmd)


def hmm_parser(txt_file):
    """
    Parser for the result from nhmmer.
    Chooses the most probable motifs and store them in list.

    :param txt_file:    Text file obtained by nhmmer
    :return:            List containing the motifs
    """

    '''List for storing the motifs'''
    hmms = []

    '''Fetches the start and end position, the strand location and the E-value from the output of nhmmer'''
    with open(txt_file, 'r') as file:
        for line in file:
            if not line.startswith('#'):
                splits = line.split()
                hmms.append([int(splits[9]), int(splits[10]), splits[8], float(splits[4])])

    return hmms


def finding_dnaa_boxes(motifs, ori_start=0, ori_end=0):
    """
    Finds the positions of Ori based on dnaA boxes

    :param motifs:      The start position of Ori based on the rRNAs
    :param ori_start:   The end location of Ori based on the rRNAs
    :param ori_end:     A list of parsed motifs from nhmmer
    :return:            Positions for Ori based on dnaA boxes
    """
    # Defines list for storing ORI prediction
    ori_out = [ori_start, ori_end]

    x_motifs = list()

    '''Dictionary for storing the dnaa boxes and their information'''
    motifs_dict = dict()
    for mot in motifs:
        if mot[0] <= mot[1]:
            motifs_dict[mot[0]] = [mot[0], mot[1], mot[2]]
        else:
            motifs_dict[mot[1]] = [mot[1], mot[0], mot[2]]

    '''Generates list of sorted keys'''
    keylist = sorted(motifs_dict)

    '''Dictionary for storing sorted dnaA boxes'''
    motifs_sorted = dict()
    for keypos in keylist:
        motifs_sorted[keypos] = motifs_dict[keypos]

    '''If no rRNAs were found the dnaA box interval is set to the first and the last dnaA box
     Otherwise finds an interval within the rRNA interval'''
    if ori_out == [0, 0]:
        # Saves beginning of first dnaA box and end of last dnaA box
        ori_out = [list(motifs_sorted.items())[0][1][0], list(motifs_sorted.items())[-1][1][1]]
    else:
        '''If the first value in the interval is larger than the last, the predicted interval
        ranges over the end and beginning of the sequence.
        Otherwise the interval is within the sequence.'''
        if ori_out[0] > ori_out[1]:
            # Finds indices of dnaA boxes after first rRNA-interval index
            # and saves the first one as the beginning of the dnaA box ORI interval
            geq = np.where(np.greater_equal(keylist, ori_out[0]))[0]
            if len(geq) != 0:
                ori_out[0] = motifs_sorted[keylist[geq[0]]][0]

            # Finds indices of dnaA boxes before the second rRNA-interval index
            # and saves the last one as the end of the dnaA box ORI interval
            leq = np.where(np.less_equal(keylist, ori_out[1]))[0]
            if len(leq) != 0:
                ori_out[1] = motifs_sorted[keylist[leq[-1]]][1]

            # Finds all indices which did not match the above criteria and
            # removes them from the sorted dictionary
            remove = np.where(np.logical_and(np.less(keylist, ori_out[0]),np.greater(keylist, ori_out[1])))[0]
            for i in remove:
                del motifs_sorted[keylist[i]]

            '''Variables needed'''
            shift = []              # List saving index where dnaA boxes shift from + to minus and vice versa
            start = end = j = 0

            '''For every motifs still in the sorted dictionary, 
            the strand information is added to the shift list.
            Also finds the strand information of the start and end indices.'''
            for sort_key in motifs_sorted:
                shift.append([sort_key, motifs_sorted[sort_key][2]])
                if ori_out[0] == motifs_sorted[sort_key][0]:
                    start = j
                if ori_out[1] == motifs_sorted[sort_key][1]:
                    end = j
                j = j + 1

            '''If the end index strand is + and the previous is -, 
            the end of the dnaA ORI interval is changed to the end of the previous dnaA box.'''
            if shift[end][1] == "+":
                for i in range(end, 1, -1):
                    if shift[i][1] == "+" and shift[i-1][1] == "-":
                        ori_out[1] = motifs_sorted[shift[i-1][0]][1]
                        break

            '''If the start index strand is - and the next is +, 
            the end of the dnaA ORI interval is changed to the beginning of the next dnaA box.'''
            if shift[start][1] == "-":
                for i in range(start, len(shift)-1):
                    if shift[i][1] == "-" and shift[i+1][1] == "+":
                        ori_out[0] = motifs_sorted[shift[i+1][0]][0]
                        break

        elif ori_out[0] <= ori_out[1]:
            # Finds dnaA indices greater than beginning of rRNA interval and less than end of rRNA interval
            # and sets the start of the dnaA ORI interval to the beginning of the first one and
            # the end of the dnaA ORI interval to the end of the last one
            beg_gleq = np.where(np.logical_and(np.greater_equal(keylist, ori_out[0]),
                                               np.less_equal(keylist, ori_out[1])))[0]
            end_gleq = np.where(np.logical_and(np.greater_equal(keylist, ori_out[0]),
                                               np.less_equal(keylist, ori_out[1])))[0]
            if len(beg_gleq) != 0:
                ori_out[0] = motifs_sorted[keylist[beg_gleq[0]]][0]
            if len(end_gleq) != 0:
                ori_out[1] = motifs_sorted[keylist[end_gleq[-1]]][1]

            # Removes all other dnaA boxes not fulfilling the above criteria from the sorted dictionary
            remove1 = np.where(np.less(keylist, ori_out[0]))[0]
            remove2 = np.where(np.greater(keylist, ori_out[1]))[0]
            for i in remove1:
                del motifs_sorted[keylist[i]]
            for i in remove2:
                del motifs_sorted[keylist[i]]

            shift = []                  # List saving index where dnaA boxes shift from + to minus and vice versa

            '''For every motifs still in the sorted dictionary, 
            the strand information is added to the shift list.
            Also finds the strand information of the start and end indices.'''
            for sort_key in motifs_sorted:
                shift.append([sort_key, motifs_sorted[sort_key][2]])
                x_motifs.append(motifs_sorted[sort_key])

            '''If the start index strand is - and the next is +, 
            the start of the dnaA ORI interval is changed to the start of the next dnaA box.'''
            if shift[0][1] == "-":
                for i in range(len(shift)-1):
                    if shift[i][1] == "-" and shift[i+1][1] == "+":
                        ori_out[0] = motifs_sorted[shift[i+1][0]][0]
                        break

            '''If the end index strand is + and the previous is -, 
            the end of the dnaA ORI interval is changed to the end of the previous dnaA box.'''
            if shift[-1][1] == "+":
                for i in range(len(shift)-1, 1, -1):
                    if shift[i][1] == "+" and shift[i-1][1] == "-":
                        ori_out[1] = motifs_sorted[shift[i-1][0]][1]
                        break

    return ori_out, motifs_sorted


def finding_dif_motifs(motifs, ter_start=0, ter_end=0):
    """
    Finds the positions of Ter based on dif motifs

    :param motifs:      Start position of Ter based on the rRNAs
    :param ter_start:   End location of Ter based on the rRNAs
    :param ter_end:     List of parsed motifs from nhmmer
    :return:            Positions for Ter based on dif motifs
    """

    '''Defines list for storing TER prediction'''
    ter_out = [ter_start, ter_end]

    '''List for storing sorted dif motifs'''
    dif_sorted = list()

    '''Dictionary for storing the dif motifs and their information'''
    motifs_dict = dict()
    for mot in motifs:
        if mot[0] <= mot[1]:
            motifs_dict[mot[0]] = [mot[0], mot[1], mot[2]]
        else:
            motifs_dict[mot[1]] = [mot[1], mot[0], mot[2]]

    '''Generates list of sorted keys'''
    keylist = sorted(motifs_dict)

    '''Dictionary for storing sorted dif motifs'''
    motifs_sorted = {}
    for sort_key in keylist:
        motifs_sorted[sort_key] = motifs_dict[sort_key]

    '''If no rRNAs were found the dif motif interval is set to the first and the last dif motif
    Otherwise finds an interval within the rRNA interval'''
    if ter_out == [0, 0]:
        # Saves beginning of first dnaA box and end of last dnaA box
        ter_out = [list(motifs_sorted.items())[0][1][0], list(motifs_sorted.items())[-1][1][1]]
    else:
        '''If the first value in the interval is larger than the last, the predicted interval
        ranges over the end and beginning of the sequence.
        Otherwise the interval is within the sequence.'''
        if ter_out[0] > ter_out[1]:
            # Finds indices of dif motifs after first rRNA-interval index
            # and saves the first one as the beginning of the dif box TER interval
            geq = np.where(np.greater_equal(keylist, ter_out[0]))[0]
            if len(geq) != 0:
                ter_out[0] = motifs_sorted[keylist[geq[0]]][0]

            # Finds indices of dif motifs before the second rRNA-interval index
            # and saves the last one as the end of the dif motif TER interval interval
            leq = np.where(np.less_equal(keylist, ter_out[1]))[0]
            if len(leq) != 0:
                ter_out[1] = motifs_sorted[keylist[leq[-1]]][1]

            # Finds all indices which did not match the above criteria and
            # removes them from the sorted dictionary
            remove = np.where(np.logical_and(np.less(keylist, ter_out[0]),np.greater(keylist, ter_out[1])))[0]
            for i in remove:
                del motifs_sorted[keylist[i]]

            '''Variables needed'''
            shift = []                  # List saving index where dnaA boxes shift from + to minus and vice versa
            start = end = j = 0

            '''For every motifs still in the sorted dictionary, 
            the strand information is added to the shift list.
            Also finds the strand information of the start and end indices.'''
            for key in motifs_sorted:
                shift.append([key, motifs_sorted[key][2]])
                if ter_out[0] == motifs_sorted[key][0]:
                    start = j
                if ter_out[1] == motifs_sorted[key][1]:
                    end = j
                j = j + 1

            '''If the end index strand is + and the previous is -, 
            the end of the dif TER interval is changed to the end of the previous dif motif.'''
            if shift[end][1] == "+":
                for i in range(end, 1, -1):
                    if shift[i][1] == "+" and shift[i-1][1] == "-":
                        ter_out[1] = motifs_sorted[shift[i-1][0]][1]
                        break

            '''If the start index strand is - and the next is +, 
            the end of the dif TER interval is changed to the beginning of the next dif motif.'''
            if shift[start][1] == "-":
                for i in range(start, len(shift)-1):
                    if shift[i][1] == "-" and shift[i+1][1] == "+":
                        ter_out[0] = motifs_sorted[shift[i+1][0]][0]
                        break

        elif ter_out[0] <= ter_out[1]:
            # Finds dif indices greater than beginning of rRNA interval and less than end of rRNA interval
            # and sets the start of the dnaA ORI interval to the beginning of the first one and
            # the end of the dnaA ORI interval to the end of the last one
            beg_gleq = np.where(np.logical_and(np.greater_equal(keylist, ter_out[0]), np.less_equal(keylist, ter_out[1])))[0]
            end_gleq = np.where(np.logical_and(np.greater_equal(keylist, ter_out[0]),
                                                 np.less_equal(keylist, ter_out[1])))[0]

            if len(beg_gleq) != 0:
                ter_out[0] = motifs_sorted[keylist[beg_gleq[0]]][0]
            if len(end_gleq) != 0:
                ter_out[1] = motifs_sorted[keylist[end_gleq[-1]]][1]

            # Removes all other dif motifs not fulfilling the above criteria from the sorted dictionary
            remove1 = np.where(np.less(keylist, ter_out[0]))[0]
            remove2 = np.where(np.greater(keylist, ter_out[1]))[0]

            for i in remove1:
                del motifs_sorted[keylist[i]]
            for i in remove2:
                del motifs_sorted[keylist[i]]

            shift = []                  # List saving index where dnaA boxes shift from + to minus and vice versa

            '''For every motifs still in the sorted dictionary, 
            the strand information is added to the shift list.
            Also finds the strand information of the start and end indices.'''
            for key in motifs_sorted:
                shift.append([key, motifs_sorted[key][2]])
                dif_sorted.append(motifs_sorted[key])

            '''If the start index strand is - and the next is +, 
            the start of the dnaA ORI interval is changed to the start of the next dif motif.'''
            if shift[0][1] == "-":
                for i in range(len(shift)-1):
                    if shift[i][1] == "-" and shift[i+1][1] == "+":
                        ter_out[0] = motifs_sorted[shift[i+1][0]][0]
                        break

            '''If the end index strand is + and the previous is -, 
            the end of the dnaA ORI interval is changed to the end of the previous dif motif.'''
            if shift[-1][1] == "+":
                for i in range(len(shift)-1, 1, -1):
                    if shift[i][1] == "+" and shift[i-1][1] == "-":
                        ter_out[1] = motifs_sorted[shift[i-1][0]][1]
                        break

    return ter_out, motifs_sorted


def dnaa_max(dnaa_boxes, ORI_rrnas, sequence_length, name):
    """
    Finds the 1000 bp interval containing the greatest amount of bp in dnaA boxes

    :param dnaa_boxes:      dnaA boxes
    :param ORI_rrnas:       Predicted interval for ORI from rRNAs
    :param sequence_length: The length of the entire sequence
    :param name:            Species
    :return:                Index with maximum number of dnaA box bases
    """
    # Initiates start and end indexes for the rRNA ORI interval
    start = ORI_rrnas[0]
    end = ORI_rrnas[1]

    '''Dictionary for storing the dnaa boxes and their information'''
    dnaa_dict = dict()
    for rec in dnaa_boxes:
        if rec[0] <= rec[1]:
            dnaa_dict[rec[0]] = [rec[0], rec[1], rec[2]]
        else:
            dnaa_dict[rec[1]] = [rec[1], rec[0], rec[2]]

    # Generates list of sorted keys
    keylist = sorted(dnaa_dict)
    motifs_sorted = {}

    '''Dictionary for storing sorted dnaA boxes'''
    for key in keylist:
        motifs_sorted[key] = dnaa_dict[key]

    # Defines the window size
    window_size = 1000

    # Creates lists for saving all positions where the bp is in a dnaA box,
    # and for saving the calculated number of bp per window.
    dnaa_list = [0] * sequence_length
    dnaa_count = [0] * sequence_length

    '''If the interval does not span over the end and beginning of the sequence, 
    loop over the interval and save the bp that are within dnaA boxes, 
    and count the number of bp within a 1000 bp window. 
    If the interval does span the end and beginning, loop between the start of the interval 
    and end of sequence, and beginning of sequence to the end of the interval. Save and count.'''
    if start <= end:
        for dnaa in motifs_sorted:
            if start <= motifs_sorted[dnaa][0] <= end and start <= motifs_sorted[dnaa][1] <= end:
                for y in range(motifs_sorted[dnaa][0], motifs_sorted[dnaa][1]):
                    dnaa_list[y] = dnaa_list[y] + 1

        for i in range(start, end, 500):
            if i < end - window_size - 1:
                dnaa_count[i] = sum(dnaa_list[i:i + window_size])
            else:
                for x in range(window_size):
                    dnaa_count[i] = sum(dnaa_list[(i - x):(i - x) + window_size])

    elif start > end:
        for dnaa in motifs_sorted:
            if (0 <= motifs_sorted[dnaa][0] <= end and 0 <= motifs_sorted[dnaa][1] <= end) or \
                    (start <= motifs_sorted[dnaa][0] <= sequence_length and
                     start <= motifs_sorted[dnaa][1] <= sequence_length):
                for y in range(motifs_sorted[dnaa][0], motifs_sorted[dnaa][1]):
                    dnaa_list[y] = dnaa_list[y] + 1
            elif (start <= motifs_sorted[dnaa][0] <= sequence_length and 0
                  <= motifs_sorted[dnaa][1] <= end):
                for y in range(motifs_sorted[dnaa][0], sequence_length):
                    dnaa_list[y] = dnaa_list[y] + 1
                for y in range(0, motifs_sorted[dnaa][1]):
                    dnaa_list[y] = dnaa_list[y] + 1

        for i in range(start, sequence_length, 500):
            if i < end - window_size - 1:
                dnaa_count[i] = sum(dnaa_list[i:i + window_size])
            else:
                for x in range(window_size):
                    dnaa_count[i] = sum(dnaa_list[(i - x):(i - x) + window_size])

        for i in range(0, end, 500):
            if i < end - window_size - 1:
                dnaa_count[i] = sum(dnaa_list[i:i + window_size])
            else:
                for x in range(window_size):
                    dnaa_count[i] = sum(dnaa_list[(i - x):(i - x) + window_size])

    '''Find the maximum number and the index where this occurs'''
    dif_max = dnaa_count.index(max(dnaa_count))

    return dif_max
