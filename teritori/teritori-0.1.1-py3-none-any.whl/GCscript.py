#!/usr/bin/python


"""----------------------------------------------PACKAGES------------------------------------------------------------"""
from __future__ import print_function
import timeit
import matplotlib.pyplot as plt
import numpy as np
import sys
import subprocess
import Bio
from random import choice
from scipy import stats
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler, minmax_scale


"""---------------------------------------------------------------------------------------------------------------------
--------------------------------------------------FUNCTIONS----------------------------------------------------------"""


def fill_positions_dict(genes_dictionary):
    """
    Fills a dictionary with the gene positions
    :param genes_dictionary:    Dictionary containing all genes
    :return:
    """
    positions_dictionary = {}

    for key in genes_dictionary:
        split = genes_dictionary[key].description.split(" # ")

        original_start = int(split[1])
        original_end = int(split[2])
        strand = int(split[3])
        length_gene = len(genes_dictionary[key].seq)

        positions_dictionary[key] = [original_start, original_end, length_gene, strand]

    return positions_dictionary


def calculate_overall_gc(genes_dictionary, positions_dictionary, sequence):
    """

    :param genes_dictionary:        Dictionary with all genes
    :param positions_dictionary:    Dictionary with all gene positions
    :param sequence:                FASTA sequence of the chromosome
    :return:                        G, C, T and A content of the chromosome
    """

    # Initiates count
    G_plus = G_minus = C_plus = C_minus = 0

    # Length of chromosome
    sequence_length = len(sequence)

    # Calculates the relative amount of the bases in the sequence
    G_content = round(((sequence.count('G') + sequence.count('g'))/sequence_length)*100)
    C_content = round(((sequence.count('C') + sequence.count('c'))/sequence_length)*100)
    T_content = round(((sequence.count('T') + sequence.count('t'))/sequence_length)*100)
    A_content = 100 - G_content - C_content - T_content

    return G_content, C_content, T_content, A_content


def prod_gc_skew(genes_dictionary, positions, window_size, sequence_length, sequence):
    """
    Produces a list of gc-skew and ta-skew values.

    :param genes_dictionary:    Dictionary with all genes from Prodigal
    :param positions:           Dictionary for positions in whole genome, in all_genes and in third_pos
    :param window_size:         Size of window for calculation
    :param sequence_length:     Length of chromosome
    :param sequence:            FASTA sequence of chromosome
    :return:                    Lists with gc- and ta-skews
    """

    # List for storing every third nt in all genes
    ev_third = ['u'] * sequence_length

    # Reverse of the sequence
    rev = list(sequence.seq)

    # Lists for saving gc- and ta-skews
    gc_skew_list = [0.0] * sequence_length
    ta_skew_list = [0.0] * sequence_length

    for key in genes_dictionary:
        '''If plus strand gene -- save every third nt to list'''
        if positions[key][3] == 1:
            for i in range(positions[key][0]+2, positions[key][1], 3):
                ev_third[i] = sequence.seq[i-1]

        '''If minus strand gene -- reverse list and save every third nt'''
        if positions[key][3] == -1:
            rev[positions[key][0]:positions[key][1]+1] = list(genes_dictionary[key].seq)
            for i in range(positions[key][0]+2, positions[key][1], 3):
                ev_third[i] = rev[i]

        '''Calculate the number of each nt per window for every 10th nt in the list'''
        for i in range(positions[key][0], positions[key][1]+1, 10):
            if i-(window_size//2) < 0:
                rest = abs(i - (window_size//2))
                a = ev_third[sequence_length - 1 - rest:i + (window_size // 2)].count('A') + \
                    ev_third[sequence_length - 1 - rest:i + (window_size // 2)].count('a') + \
                    ev_third[0:i + (window_size // 2)].count('A') + \
                    ev_third[0:i + (window_size // 2)].count('a')
                c = ev_third[sequence_length - 1 - rest:i + (window_size // 2)].count('C') + \
                    ev_third[sequence_length - 1 - rest:i + (window_size // 2)].count('c') + \
                    ev_third[0:i + (window_size // 2)].count('C') + \
                    ev_third[0:i + (window_size // 2)].count('c')
                g = ev_third[sequence_length - 1 - rest:i + (window_size // 2)].count('G') + \
                    ev_third[sequence_length - 1 - rest:i + (window_size // 2)].count('g') + \
                    ev_third[0:i + (window_size // 2)].count('G') + \
                    ev_third[0:i + (window_size // 2)].count('g')
                t = ev_third[sequence_length - 1 - rest:i + (window_size // 2)].count('T') + \
                    ev_third[sequence_length - 1 - rest:i + (window_size // 2)].count('t') + \
                    ev_third[0:i + (window_size // 2)].count('T') + \
                    ev_third[0:i + (window_size // 2)].count('t')
            elif i+(window_size//2) > sequence_length-1:
                rest = abs(sequence_length - (window_size // 2))
                a = ev_third[i-(window_size//2):sequence_length-1].count('A') + \
                    ev_third[i-(window_size//2):sequence_length-1].count('a') + \
                    ev_third[0:rest].count('A') + \
                    ev_third[0:rest].count('a')
                c = ev_third[i - (window_size // 2):sequence_length - 1].count('C') + \
                    ev_third[i - (window_size // 2):sequence_length - 1].count('c') + \
                    ev_third[0:rest].count('C') + \
                    ev_third[0:rest].count('c')
                g = ev_third[i - (window_size // 2):sequence_length - 1].count('G') + \
                    ev_third[i - (window_size // 2):sequence_length - 1].count('g') + \
                    ev_third[0:rest].count('G') + \
                    ev_third[0:rest].count('g')
                t = ev_third[i - (window_size // 2):sequence_length - 1].count('T') + \
                    ev_third[i - (window_size // 2):sequence_length - 1].count('t') + \
                    ev_third[0:rest].count('T') + \
                    ev_third[0:rest].count('t')
            else:
                a = ev_third[i-(window_size//2):i + (window_size//2)].count('A') + ev_third[i-(window_size//2):i + (window_size//2)].count('a')
                c = ev_third[i-(window_size//2):i + (window_size//2)].count('C') + ev_third[i-(window_size//2):i + (window_size//2)].count('c')
                g = ev_third[i-(window_size//2):i + (window_size//2)].count('G') + ev_third[i-(window_size//2):i + (window_size//2)].count('g')
                t = ev_third[i-(window_size//2):i + (window_size//2)].count('T') + ev_third[i-(window_size//2):i + (window_size//2)].count('t')

            '''If not division with zero -- calculate gc- and ta-skew and save to lists'''
            if (g + c) != 0.0:
                gc_skew_list[i] = positions[key][3] * ((g - c) / (g + c))

            if (t + a) != 0.0:
                ta_skew_list[i] = positions[key][3] * ((t - a) / (t + a))

    return gc_skew_list, ta_skew_list


def find_ter_ori(gc_skew_list, ta_skew_list):
    """
    Find positions of ORI and TER

    :param gc_skew_list:    List of gc-skews
    :param ta_skew_list:    List of ta-skews
    :return:                Positions of ORI and TER
    """

    # Producing cumulative gc skew
    gc_cum = list(np.cumsum(gc_skew_list))
    ta_cum = list(np.cumsum(ta_skew_list))

    # Finds minimum value in gc-skew
    ORI_gc = gc_cum.index(min(gc_cum))

    # Finds minimum value in ta-skew
    ORI_ta = ta_cum.index(min(ta_cum))

    # Find maximum value in gc-skew
    TER_gc = gc_cum.index(max(gc_cum))

    # Find maximum value in ta-skew
    TER_ta = ta_cum.index(max(ta_cum))

    return ORI_gc, ORI_ta, TER_gc, TER_ta, gc_cum, ta_cum


def find_actual_position(ORI_gc, ORI_ta, TER_gc, TER_ta, gc_cum, ta_cum, positions):
    """
    Find position of ORI and TER - assumed to be before gene where predicted position is in
    and after the gene where the predicted position is in, respectively

    :param ORI_gc:      Predicted position of ORI using GC-skew
    :param ORI_ta:      Predicted position of ORI using TA-skew
    :param TER_gc:      Predicted position of TER using GC-skew
    :param TER_ta:      Predicted position of TER using TA-skew
    :param gc_cum:      List of cumulative GC-skews
    :param ta_cum:      List of cumulative TA-skews
    :param positions:   List of gene positions
    :return:            Actual position for ORI and TER using both GC and TA-skew,
                        and the indices values in the list (used later for plotting)
    """

    # Initiating that none of the actual positions have been found
    ori_gc_found = ter_gc_found = ori_ta_found = ter_ta_found = False

    '''Loop through all genes, find the gene which contains the predicted position
    and set the new predicted position as the position before that gene (ORI) or after
    that gene (TER). Once all positions have been found, loop breaks.'''
    for gene in positions:
        if not ori_gc_found:
            if positions[gene][0] <= ORI_gc <= positions[gene][1]:
                ORI_gc = positions[gene][0]
                ori_gc_found = True
        if not ter_gc_found:
            if positions[gene][0] <= TER_gc <= positions[gene][1]:
                TER_gc = positions[gene][1]
                ter_gc_found = True
        if not ori_ta_found:
            if positions[gene][0] <= ORI_ta <= positions[gene][1]:
                ORI_ta = positions[gene][0]
                ori_ta_found = True
        if not ter_ta_found:
            if positions[gene][0] <= TER_ta <= positions[gene][1]:
                TER_ta = positions[gene][1]
                ter_ta_found = True
        if ori_gc_found and ter_gc_found and ori_ta_found and ter_ta_found:
            break

    ORI_gc = ORI_gc - 1
    ORI_ta = ORI_ta - 1
    TER_gc = TER_gc - 1
    TER_ta = TER_ta - 1
    # Finds the values for each index
    ORI_gc_val = gc_cum[ORI_gc]
    ORI_ta_val = ta_cum[ORI_ta]
    TER_gc_val = gc_cum[TER_gc]
    TER_ta_val = ta_cum[TER_ta]

    return ORI_gc, ORI_gc_val, TER_gc, TER_gc_val, ORI_ta, ORI_ta_val, TER_ta, TER_ta_val


def av_slope(normalized, first, second):
    """

    :param normalized:  List of normalized data (not necessary to be normalized)
    :param first:       First position - ORI or TER
    :param second:      Second position - ORI or TER
    :return:            Returns the slope
    """
    dy = normalized[second-1] - normalized[first]
    dx = second - first
    return dy / dx


def slopes(gc_normalized, ta_normalized, ORI_gc, TER_gc, ORI_ta, TER_ta, size=100000):
    """
    Calculates slopes before and after ORI and TER

    :param gc_normalized:   Normalized list of gc-skew values
    :param ta_normalized:   Normalized list of ta-skew values
    :param ORI_gc:          Predicted ORI position by gc-skew
    :param TER_gc:          Predicted TER position by gc-skew
    :param ORI_ta:          Predicted ORI position by ta-skew
    :param TER_ta:          Predicted TER position by ta-skew
    :param size:            Size of window to look at
    :return:                Slopes before and after ORI and TER for
                            GC and TA skew lists.
    """
    len_gc_normalized = len(gc_normalized)
    len_ta_normalized = len(ta_normalized)

    # Average overall slope
    average_slope_gc = av_slope(gc_normalized, 0, len_gc_normalized)
    average_slope_ta = av_slope(ta_normalized, 0, len_ta_normalized)

    # Average slope between ori and ter
    if ORI_gc <= TER_gc:
        av_ori_ter_gc = (gc_normalized[ORI_gc] - gc_normalized[TER_gc]) / (ORI_gc - TER_gc)
    elif ORI_gc > TER_gc:
        av_ori_ter_gc = (gc_normalized[TER_gc] - gc_normalized[ORI_gc]) / (TER_gc - ORI_gc)

    if ORI_ta <= TER_ta:
        av_ori_ter_ta = av_slope(ta_normalized, ORI_ta, TER_ta)
    elif ORI_ta > TER_ta:
        av_ori_ter_ta = av_slope(ta_normalized, TER_ta, ORI_ta)

    # Average slope before and after ori and ter for gc and ta skew
    if size < ORI_gc:
        av_gc_bf_ori = av_slope(gc_normalized, ORI_gc - size, ORI_gc)
    else:
        av_gc_bf_ori = av_slope(gc_normalized, 0, ORI_gc)

    # --------
    if ORI_gc < len_gc_normalized-(size+1):
        av_gc_af_ori = av_slope(gc_normalized, ORI_gc, ORI_gc + size)
    else:
        av_gc_af_ori = av_slope(gc_normalized, ORI_gc, len_gc_normalized)

    # --------
    if size < TER_gc:
        av_gc_bf_ter = av_slope(gc_normalized, TER_gc - size, TER_gc)
    else:
        av_gc_bf_ter = av_slope(gc_normalized, 0, TER_gc)

    # --------
    if TER_gc < len_gc_normalized - (size+1):
        av_gc_af_ter = av_slope(gc_normalized, TER_gc, TER_gc + size)
    else:
        av_gc_af_ter = av_slope(gc_normalized, TER_gc, len_gc_normalized)

    # --------
    if size < ORI_ta:
        av_ta_bf_ori = av_slope(ta_normalized, ORI_ta - size, ORI_ta)
    else:
        av_ta_bf_ori = av_slope(ta_normalized, 0, ORI_ta)

    # --------
    if ORI_ta < len_ta_normalized-(size+1):
        av_ta_af_ori = av_slope(ta_normalized, ORI_ta, ORI_ta + size)
    else:
        av_ta_af_ori = av_slope(ta_normalized, ORI_ta, len_ta_normalized)

    # --------
    if size < TER_ta:
        av_ta_bf_ter = av_slope(ta_normalized, TER_ta - size, TER_ta)
    else:
        av_ta_bf_ter = av_slope(ta_normalized, 0, TER_ta)

    # --------
    if TER_ta < len_ta_normalized - (size+1):
        av_ta_af_ter = av_slope(ta_normalized, TER_ta, TER_ta + size)
    else:
        av_ta_af_ter = av_slope(ta_normalized, TER_ta, len_ta_normalized)

    return av_gc_bf_ori, av_gc_af_ori, av_gc_bf_ter, av_gc_af_ter, av_ta_bf_ori, \
        av_ta_af_ori, av_ta_bf_ter, av_ta_af_ter, average_slope_gc, average_slope_ta, \
        av_ori_ter_gc, av_ori_ter_ta


def perfect_plot_norm(first, second, real_normalized):
    """
    Produces datasets with perfect, normalized data - Linear between start and the
    predicted positions, between the predicted positions, and the end of the chromosome

    :param first:           Position with lowest index
    :param second:          Position with highest index
    :param real_normalized: Normalized data
    :return:                Linear data set and the x-values
    """

    # Length of the normalized data set
    rn_length = len(real_normalized)

    # Defines a set of linear data points between start of sequence and first position
    start_first = real_normalized[0:first]
    x_start_first = list(np.arange(0, first, 1))
    slope, intercept = np.polyfit(x_start_first, start_first, 1)
    start_first_vals = [slope * i + intercept for i in x_start_first]

    # Defines a set of linear data points between first and second position
    first_second = real_normalized[first:second]
    x_first_second = list(np.arange(first, second, 1))
    slope, intercept = np.polyfit(x_first_second, first_second, 1)
    first_second_vals = [slope * i + intercept for i in x_first_second]

    # Defines a set of linear data points between second position and end of sequence
    second_end = real_normalized[second:rn_length]
    x_second_end = list(np.arange(second, rn_length, 1))
    slope, intercept = np.polyfit(x_second_end, second_end, 1)
    second_end_vals = [slope * i + intercept for i in x_second_end]

    # Puts the above datasets into two continuous ones
    perfect = start_first_vals + first_second_vals + second_end_vals
    x_perfect = np.arange(0, rn_length, 1)

    return perfect, x_perfect


def diff_perf_real(perfect_gc, real_gc_norm, perfect_ta, real_ta_norm):
    len_perfect_gc = len(perfect_gc)
    len_perfect_ta = len(perfect_ta)
    av_diff_gc = av_diff_ta = 0

    if len(real_gc_norm) == len_perfect_gc and len(real_ta_norm) == len_perfect_ta:
        sum_diff_gc = 0
        sum_diff_ta = 0
        for i in range(len_perfect_gc):
            sum_diff_gc = sum_diff_gc + abs(perfect_gc[i]-real_gc_norm[i])
        for i in range(len_perfect_ta):
            sum_diff_ta = sum_diff_ta + abs(perfect_ta[i]-real_ta_norm[i])
        av_diff_gc = sum_diff_gc/len_perfect_gc
        av_diff_ta = sum_diff_ta/len_perfect_ta
    return av_diff_gc, av_diff_ta


def gc_bootstrap(sequence_length, aroundter_gc, aroundori_gc,
                 aroundter_ta, aroundori_ta, window_size, G_content, C_content,
                 T_content, A_content, ori_break_gc, ter_break_gc, ori_break_ta, ter_break_ta,
                 ORI_gc, TER_gc, log_file, ori_rrna_range = list(), ter_rrna_range = list()):
    """
    Bootstrap function, produces randomly generated sequences with same relative amount of
    the different bases.

    :param sequence_length: Length of chromosome
    :param aroundter_gc:    List containing indexes around TER predicted by GC-skew
    :param aroundori_gc:    List containing indexes around ORI predicted by GC-skew
    :param aroundter_ta:    List containing indexes around TER predicted by TA-skew
    :param aroundori_ta:    List containing indexes around ORI predicted by TA-skew
    :param window_size:     Window size
    :param G_content:       Relative amount of G in sequence
    :param C_content:       Relative amount of C in sequence
    :param T_content:       Relative amount of T in sequence
    :param A_content:       Relative amount of A in sequence
    :param ori_break_gc:    Position of break in indices in aroundori_gc
    :param ter_break_gc:    Position of break in indices in aroundter_gc
    :param ori_break_ta:    Position of break in indices in aroundori_ta
    :param ter_break_ta:    Position of break in indices in aroundter_ta
    :param ORI_rrnas:       Predicted interval of ORI from rRNAs
    :param TER_rrnas:       Predicted interval of TER from rRNAs
    :param ORI_gc:          Predicted ORI by GC-skew
    :param TER_gc:          Predicted TER by GC-skew
    :param ORI_ta:          Predicted ORI by TA-skew
    :param TER_ta:          Predicted TER by TA-skew
    :return:                p-values for ORI and TER from GC- and TA- skew
    """

    # Number of iterations
    N = 1000

    # List for storing indices in rRNA range
    rrnas_ori = list()
    rrnas_ter = list()

    # Initiates p-values
    p_ter_gc = p_ori_gc = p_ter_ta = p_ori_ta = 0.0

    # All predictions and p-values are set to be used
    use_gc_ter = True
    use_gc_ori = True
    use_ta_ter = True
    use_ta_ori = True

    # Calculates maximum expected difference between ORI and TER
    max_perc_genome = round(sequence_length * 0.70)
    min_perc_genome = int(sequence_length * 0.30)

    '''If distance between the predicted positions is greater than the expected, 
    the p-values are set to 1.0'''
    if not min_perc_genome <= abs(ORI_gc - TER_gc) <= max_perc_genome:
        p_ter_gc = p_ori_gc = 1.0
        use_gc_ter = use_gc_ori = False
    # if not min_perc_genome <= abs(ORI_ta - TER_ta) <= max_perc_genome:
    #     p_ter_ta = p_ori_ta = 1.0
    #     use_ta_ter = use_ta_ori = False

    '''If the predicted positions are not in the rRNA prediction range, 
    the p-values are set to 1.0'''
    if len(ori_rrna_range) != 0:
        if ORI_gc not in ori_rrna_range:
            p_ori_gc = 1.0
            use_gc_ori = False
        # if ORI_ta not in ori_rrna_range:
        #     p_ori_ta = 1.0
        #     use_ta_ori = False
    if len(ter_rrna_range) != 0:
        if TER_gc not in ter_rrna_range:
            p_ter_gc = 1.0
            use_gc_ter = False
        # if TER_ta not in ter_rrna_range:
        #     p_ter_ta = 1.0
        #     use_ta_ter = False

    '''If none of the predictions are ok, returns the p-values, otherwise
    runs bootstrap'''
    if not use_gc_ter and not use_gc_ori:
        return p_ter_gc, p_ori_gc
    else:
        # Specifies which bases can be chosen
        bases = ['A', 'T', 'C', 'G']

        # Produces the weights depending on the original sequence composition
        weights = [A_content/100, T_content/100, C_content/100, G_content/100]

        with open(log_file, "a") as logs:
            logs.write("%s           %s" % ("", ".."))

        for i in range(0, N):
            if i % 100 == 0:
                with open(log_file, "a") as logs:
                    logs.write("{}..".format(i))

            # Initiates list for saving every third nt
            new_third = ['u'] * sequence_length

            # Randomly generates a new sequence
            newsample = np.random.choice(bases, sequence_length, p=weights, replace=True)

            # Saves every third nt
            for k in range(2, sequence_length, 3):
                new_third[k] = newsample[k]

            # Initiates list for storing skew values
            newsample_gc = [0.0] * sequence_length
            newsample_ta = [0.0] * sequence_length

            '''Counts the number of the different nt in the windows'''
            for j in range(0, sequence_length, window_size):
                if j-(window_size//2) < 0:
                    rest = abs(j - (window_size//2))
                    a = new_third[sequence_length - 1 - rest:j + (window_size // 2)].count('A') + \
                        new_third[sequence_length - 1 - rest:j + (window_size // 2)].count('a') + \
                        new_third[0:j + (window_size // 2)].count('A') + \
                        new_third[0:j + (window_size // 2)].count('a')
                    c = new_third[sequence_length - 1 - rest:j + (window_size // 2)].count('C') + \
                        new_third[sequence_length - 1 - rest:j + (window_size // 2)].count('c') + \
                        new_third[0:j + (window_size // 2)].count('C') + \
                        new_third[0:j + (window_size // 2)].count('c')
                    g = new_third[sequence_length - 1 - rest:j + (window_size // 2)].count('G') + \
                        new_third[sequence_length - 1 - rest:j + (window_size // 2)].count('g') + \
                        new_third[0:j + (window_size // 2)].count('G') + \
                        new_third[0:j + (window_size // 2)].count('g')
                    t = new_third[sequence_length - 1 - rest:j + (window_size // 2)].count('T') + \
                        new_third[sequence_length - 1 - rest:j + (window_size // 2)].count('t') + \
                        new_third[0:j + (window_size // 2)].count('T') + \
                        new_third[0:j + (window_size // 2)].count('t')
                elif j+(window_size//2) > sequence_length-1:
                    rest = abs(sequence_length - (window_size // 2))
                    a = new_third[j-(window_size//2):sequence_length-1].count('A') + \
                        new_third[j-(window_size//2):sequence_length-1].count('a') + \
                        new_third[0:rest].count('A') + \
                        new_third[0:rest].count('a')
                    c = new_third[j - (window_size // 2):sequence_length - 1].count('C') + \
                        new_third[j - (window_size // 2):sequence_length - 1].count('c') + \
                        new_third[0:rest].count('C') + \
                        new_third[0:rest].count('c')
                    g = new_third[j - (window_size // 2):sequence_length - 1].count('G') + \
                        new_third[j - (window_size // 2):sequence_length - 1].count('g') + \
                        new_third[0:rest].count('G') + \
                        new_third[0:rest].count('g')
                    t = new_third[j - (window_size // 2):sequence_length - 1].count('T') + \
                        new_third[j - (window_size // 2):sequence_length - 1].count('t') + \
                        new_third[0:rest].count('T') + \
                        new_third[0:rest].count('t')
                else:
                    a = new_third[j-(window_size//2):j + (window_size//2)].count('A') + \
                        new_third[j-(window_size//2):j + (window_size//2)].count('a')
                    c = new_third[j-(window_size//2):j + (window_size//2)].count('C') + \
                        new_third[j-(window_size//2):j + (window_size//2)].count('c')
                    g = new_third[j-(window_size//2):j + (window_size//2)].count('G') + \
                        new_third[j-(window_size//2):j + (window_size//2)].count('g')
                    t = new_third[j-(window_size//2):j + (window_size//2)].count('T') + \
                        new_third[j-(window_size//2):j + (window_size//2)].count('t')

                # Generates random gene position - plus or minus strand
                strand = np.random.choice([-1, 1])

                '''If not zero division, calculate and save the gc- and ta-skew'''
                if g + c != 0.0:
                    newsample_gc[j] = strand * (g-c)/(g+c)
                if t + a != 0.0:
                    newsample_ta[j] = strand * (t-a)/(t+a)

            # Find max (ter) and min (ori) positions in bootstrap sample
            ter_btstrap_gc = np.argmax(newsample_gc)
            ori_btstrap_gc = np.argmin(newsample_gc)

            ter_btstrap_ta = np.argmax(newsample_ta)
            ori_btstrap_ta = np.argmin(newsample_ta)

            '''Checks if the predicted positions are within the ranges'''
            if use_gc_ori and aroundori_gc[0] != 0 and aroundori_gc[-1] != len(newsample_gc) - 1:
                if aroundori_gc[0] <= ori_btstrap_gc <= aroundori_gc[-1]:
                    p_ori_gc = p_ori_gc + 1
            elif use_gc_ori and aroundori_gc[0] == 0 and aroundori_gc[-1] == len(newsample_gc) - 1:
                if ori_break_gc <= ori_btstrap_gc <= aroundori_gc[-1] or \
                        0 <= ori_btstrap_gc <= aroundori_gc[aroundori_gc.index(ori_break_gc) - 1]:
                    p_ori_gc = p_ori_gc + 1

            if use_gc_ter and aroundter_gc[0] != 0 and aroundter_gc[-1] != len(newsample_gc) - 1:
                if aroundter_gc[0] <= ter_btstrap_gc <= aroundter_gc[-1]:
                    p_ter_gc = p_ter_gc + 1
            elif use_gc_ter and aroundter_gc[0] == 0 and aroundter_gc[-1] == len(newsample_gc) - 1:
                if ter_break_gc <= ter_btstrap_gc <= aroundter_gc[-1] or \
                        0 <= ter_btstrap_gc <= aroundter_gc[aroundter_gc.index(ter_break_gc) - 1]:
                    p_ter_gc = p_ter_gc + 1

            if use_ta_ori and aroundori_ta[0] != 0 and aroundori_ta[-1] != len(newsample_ta) - 1:
                if aroundori_ta[0] <= ori_btstrap_ta <= aroundori_ta[-1]:
                    p_ori_ta = p_ori_ta + 1
            elif use_ta_ori and aroundori_ta[0] == 0 and aroundori_ta[-1] == len(newsample_ta) - 1:
                if ori_break_ta <= ori_btstrap_ta <= aroundori_ta[-1] or \
                        0 <= ori_btstrap_ta <= aroundori_ta[aroundori_ta.index(ori_break_ta) - 1]:
                    p_ori_ta = p_ori_ta + 1

            if use_ta_ter and aroundter_ta[0] != 0 and aroundter_ta[-1] != len(newsample_ta) - 1:
                if aroundter_ta[0] <= ter_btstrap_ta <= aroundter_ta[-1]:
                    p_ter_ta = p_ter_ta + 1
            elif use_ta_ter and aroundter_ta[0] == 0 and aroundter_ta[-1] == len(newsample_ta) - 1:
                if ter_break_ta <= ter_btstrap_ta <= aroundter_ta[-1] or \
                        0 <= ter_btstrap_ta <= aroundter_ta[aroundter_ta.index(ter_break_ta) - 1]:
                    p_ter_ta = p_ter_ta + 1

    '''If the p-values were not previously changed to 1.0, calculate 
    the final p-values'''
    if use_gc_ter:
        p_ter = p_ter_gc / N
    if use_gc_ori:
        p_ori = p_ori_gc / N
    if use_ta_ter:
        p_ter = p_ter_ta / N
    if use_ta_ori:
        p_ori = p_ori_ta / N

    return p_ori, p_ter


def main(record_dict, sequence, sequence_length, name, strain, output, graph=False):
    """
    Predicts the positions of ORI and TER based on GC skew and TA skew calculations.

    :param record_dict:     Dictionary storing all genes
    :param sequence:        FASTA sequence of the chromosome
    :param sequence_length: Length of the chromosome
    :param name:            Name of the species
    :param strain:          Strains of the species
    :param graph:           If graph should be produced
    :param output:          Specified output name and directory
    :return:                Predicted ORI and TER positions, list containing cumulative sums for
                            GC- and TA-skew, normalized lists of the values, perfect linear data
                            for both measurements given the predicted ORI and TER.
    """

    # Creating positions dictionary - stores all positions in all lists for all genes throughout the code
    positions = fill_positions_dict(record_dict)

    # Specifies which window size to start with
    window_size = int(0.00005*sequence_length)

    '''Produces the GC and TA skew lists'''
    gc_skew_list, ta_skew_list = prod_gc_skew(record_dict, positions, window_size, sequence_length, sequence)

    '''Find ter and ori'''
    ORI_gc, ORI_ta, TER_gc, TER_ta, gc_cum, ta_cum = find_ter_ori(gc_skew_list, ta_skew_list)

    '''Find actual positions -- assuming actual position for ORI is before the gene where the position is 
    indicated and that the actual position for TER is after the gene where the position is indicated.'''
    ORI_gc, ORI_gc_val, TER_gc, TER_gc_val, ORI_ta, ORI_ta_val, TER_ta, TER_ta_val = \
        find_actual_position(ORI_gc, ORI_ta, TER_gc, TER_ta, gc_cum, ta_cum, positions)

    '''Normalization --> All values between 0-1'''
    gc_normalized = minmax_scale(gc_cum, feature_range=(0, 1), axis=0, copy=True)
    ta_normalized = minmax_scale(ta_cum, feature_range=(0, 1), axis=0, copy=True)

    # Initate list for storing perfect, normalized data
    perfect_gc = []
    perfect_ta = []

    # X-axis for the perfect data
    x_perfect_gc = []
    x_perfect_ta = []

    '''Produce perfect plot from predicted ORI and TER'''
    if ORI_gc > TER_gc:
        perfect_gc, x_perfect_gc = perfect_plot_norm(TER_gc, ORI_gc, gc_normalized)
    elif TER_gc > ORI_gc:
        perfect_gc, x_perfect_gc = perfect_plot_norm(ORI_gc, TER_gc, gc_normalized)

    if ORI_ta > TER_ta:
        perfect_ta, x_perfect_ta = perfect_plot_norm(TER_ta, ORI_ta, ta_normalized)
    elif TER_ta > ORI_ta:
        perfect_ta, x_perfect_ta = perfect_plot_norm(ORI_ta, TER_ta, ta_normalized)

    return ORI_gc, TER_gc, gc_cum, gc_normalized, perfect_gc, x_perfect_gc, \
        ORI_ta, TER_ta, ta_cum, ta_normalized, perfect_ta, x_perfect_ta, positions


def around_pos(normalized, ORI, TER, av_diff):
    """
    Check which indices have a cum value differing less than the average difference

    :param normalized:  Normalized list of skew values
    :param ORI:         Predicted position of ORI
    :param TER:         Predicted position of TER
    :param av_diff:     Average difference between perfect and real data
    :return:            Lists of indices around predicted positions with value
                        differing less than the average difference,and the break points if found
    """

    # Initiating lists
    aroundter = list()
    aroundori = list()

    # Initiating break points
    ori_break = -1
    ter_break = -1

    # Length of normalized list
    len_normalized = len(normalized)

    # List of all indices
    indices = list(range(0, len_normalized))

    '''Saves all indices with values differing less than the average difference, 
    and saves the index as a break point when the indices jump more than one step'''
    for val in indices:
        if abs(normalized[val] - normalized[ORI-1]) < abs(av_diff):
            if len(aroundori) != 0:
                if val > aroundori[len(aroundori)-1] + 1:
                    ori_break = val
            aroundori.append(val)

        if abs(normalized[val] - normalized[TER-1]) < abs(av_diff):
            if len(aroundter) != 0:
                if val > aroundter[len(aroundter) - 1] + 1:
                    ter_break = val
            aroundter.append(val)

    '''Deletes all indices from list which are less than the break point if 
    the predicted position is above the break point, and deletes all indices
    from list which are greater than the break point, if the predicted position is 
    less than the break point - IF the first index is not the beginning of the sequence 
    and the last is not the end of the sequence.'''
    if ori_break != -1 and ORI >= ori_break and aroundori[0] != 0 \
            and aroundori[1] != len_normalized - 1:
        del aroundori[0:aroundori.index(ori_break)]
    elif ori_break != -1 and ORI < ori_break and aroundori[0] != 0 \
            and aroundori[1] != len_normalized - 1:
        del aroundori[aroundori.index(ori_break)::]

    if ter_break != -1 and TER >= ter_break and aroundter[0] != 0 \
            and aroundter[1] != len_normalized - 1:
        del aroundter[0:aroundter.index(ter_break)]
    elif ter_break != -1 and TER < ter_break and aroundter[0] != 0 \
            and aroundter[1] != len_normalized - 1:
        del aroundter[aroundter.index(ter_break)::]

    return list(aroundori), list(aroundter), ori_break, ter_break


def find_final_pred(ORI_gc, TER_gc, p_ori_gc, p_ter_gc, ORI_ta, TER_ta, p_ori_ta, p_ter_ta,
                    av_diff_gc, av_diff_ta, alpha):
    """
    Decides on final prediction between GC- and TA-skew.

    :param ORI_gc:      Predicted position of ORI by GC-skew
    :param TER_gc:      Predicted position of TER by GC-skew
    :param p_ori_gc:    p-value for ORI_gc
    :param p_ter_gc:    p-value for TER_gc
    :param ORI_ta:      Predicted position of ORI by TA-skew
    :param TER_ta:      Predicted position of TER by TA-skew
    :param p_ori_ta:    p-value for ORI_ta
    :param p_ter_ta:    p-value for TER_ta
    :param av_diff_gc:  Average difference between perfect and real gc-skew values
    :param av_diff_ta:  Average difference between perfect and real ta-skew values
    :param alpha:       Significance level
    :return:            Final predictions for ORI and TER and the final p-values
    """
    final_ORI = -1
    final_TER = -1
    final_p_ori = -1.0
    final_p_ter = -1.0

    '''If the p-values for the gc and ta positions are all below the significance level,
    checks which of the measurements have the least average difference. If the average difference 
    is the same, combines the two probabilities and the positions.'''
    if p_ori_gc <= alpha >= p_ter_gc and p_ori_ta <= alpha >= p_ter_ta:
        if av_diff_gc < av_diff_ta:
            final_ORI = ORI_gc
            final_TER = TER_gc
            final_p_ori = p_ori_gc
            final_p_ter = p_ter_gc
        elif av_diff_ta < av_diff_gc:
            final_ORI = ORI_ta
            final_TER = TER_ta
            final_p_ori = p_ori_ta
            final_p_ter = p_ter_ta
        elif av_diff_gc == av_diff_ta:
            final_ORI = (ORI_gc + ORI_ta)//2
            final_TER = (TER_gc + TER_ta)//2
            stat, final_p_ori = stats.combine_pvalues([p_ori_gc, p_ori_ta], method='fisher', weights=None)
            stat, final_p_ter = stats.combine_pvalues([p_ter_gc, p_ter_ta], method='fisher', weights=None)

    elif p_ori_gc <= alpha >= p_ter_gc and not (p_ori_ta <= alpha >= p_ter_ta):
        final_ORI = ORI_gc
        final_TER = TER_gc
        final_p_ori = p_ori_gc
        final_p_ter = p_ter_gc
    elif p_ori_ta <= alpha >= p_ter_ta and not (p_ori_gc <= alpha >= p_ter_gc):
        final_ORI = ORI_ta
        final_TER = TER_ta
        final_p_ori = p_ori_ta
        final_p_ter = p_ter_ta

    return final_ORI, final_TER, final_p_ori, final_p_ter
