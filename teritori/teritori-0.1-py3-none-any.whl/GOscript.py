import warnings
import numpy as np
import argparse
import os
import errno
import tempfile
import subprocess
from Bio import SeqIO
import matplotlib.pyplot as plt
from collections import defaultdict
import seaborn as sns
from scipy import stats, signal, integrate
import time


warnings.filterwarnings("ignore")

# --- FUNCTIONS --- #


def sliding_sumdiff(sequence, win_size):
    """
    Iterate over an array of gene orientation values with a double-sided sliding window. For each iteration,
    calculate the difference between the sum of the right side and the sum of the left.

    Keyword arguments:
    sequence --
    win_size --
    :param sequence: the gene orientation array. Each element is either -1 or 1
    :param win_size: the size of each side of the double sliding window (int). Total window size is 2*win_size + 1
    :return: list with the result calculations with same length as input array
    """

    # Extend the data array to facilitate calculation of end positions
    sequence_extended = np.append(sequence, sequence[0:win_size])
    sequence_extended = np.append(sequence[-win_size:], sequence_extended)

    return [sum(sequence_extended[i + win_size: i + (2 * win_size)]) - sum(sequence_extended[i: i + win_size]) for i in
            range(len(sequence))]


def find_genes(in_file, length=False):
    """
    Run Prodigal to find genes in an input FASTA file. Save the result in a temporary file, parse it using Biopython
    SeqIO. Optionally read length of genome using a second temporary file via a FASTA output from Prodigal.

    :param in_file: the name of the input file
    :param length: whether or not to output genome length (boolean). Default is False
    :return: a dict with the genes calculated by Prodigal under 'genes'. Optionally also genome length under 'length'
    """

    print("Running Prodigal...\n")

    tmp1 = tempfile.NamedTemporaryFile(delete=False)
    prod_command = ["prodigal", '-i', in_file, '-f', 'gff', '-d', tmp1.name]
    if length:
        tmp2 = tempfile.NamedTemporaryFile(delete=False)
        prod_command = prod_command + ['-o', tmp2.name]  # add secondary output to Prodigal command to read length
    prodigal_out = None
    try:
        FNULL = open(os.devnull, 'w')
        subprocess.check_call(prod_command, stdout=FNULL, shell=False)
        prodigal_out = SeqIO.to_dict(SeqIO.parse(tmp1.name, 'fasta'))
    except subprocess.CalledProcessError:
        print("Error with Prodigal")
    tmp1.close()
    os.unlink(tmp1.name)
    if length:
        tmp2.close()
        with open(tmp2.name, 'r') as f:
            f.readline()
            gff_data = f.readline().rstrip()  # Read header line of secondary output

    ret = {'genes': prodigal_out}
    if length:
        ret['length'] = int(gff_data.split(';')[1].split('=')[1])  # Parse genome length from header

    os.unlink(tmp2.name)

    return ret


def parse_genes(prod_genes):
    """
    Parse the the Biopython SeqRecord representation of the Prodigal GFF output. Specifically, retrieve the
    start positions, end positions, strand orientation and sequences of each gene
    :param prod_genes: A SeqRecord object with genes found by Prodigal
    :return: A dict with the retrieved data
    """

    starts = []
    ends = []
    strands = []
    seqs = []
    for record in prod_genes:
        data = prod_genes[record].description.split(' # ')
        starts.append(int(data[1]))
        ends.append(int(data[2]))
        strands.append(int(data[3]))
        seqs.append(prod_genes[record].seq)
    samp_id = data[0] # simply use the last entry to retrieve the ID (same for whole data set)

    return {'start': starts, 'end': ends, 'strand': strands, 'sequence': seqs, "id": samp_id}


def predict_ori_ter(data, win_size=None, method="cumulative"):
    """
    Calculate strand orientation trend of a genome (cumulative or sumdiff), and predict ori and ter. If
    cumulative, assume ori as the global minimum and ter as the maximum - opposite for sumdiff
    :param data: an array of strand orientation data. Each element is -1 or 1
    :param win_size: The window for sumdiff calculations. Only required if method is 'sumdiff'
    :param method: Which method to use for trend calculation. Accepts 'cumulative' (default) or 'sumdiff'
    :return: strand_sum: the result of the trend calculation. ori_prediction: the index of predicted ori site.
    ter_prediction: the index of predicted ter site
    """

    if not method == "cumulative" and not method == "sumdiff":
        raise Exception("Invalid input method (cumulative or sumdiff are options, default is cumulative)")
    if method == "sumdiff" and win_size == None:
        raise Exception("param win_size must be set for sumdiff calculation")
    if method == "cumulative":
        strand_sum = np.cumsum(data)
        ori_prediction = np.argmin(strand_sum)
        ter_prediction = np.argmax(strand_sum)
    else:
        strand_sum = sliding_sumdiff(data, win_size)
        ori_prediction = np.argmax(strand_sum)
        ter_prediction = np.argmin(strand_sum)

    return strand_sum, ori_prediction, ter_prediction


def ori_gene_to_bp(ori_pred, ter_pred, gene_intervals):
    """
    Convert predicted ori and ter gene indices to a basepair position interval. Interval is from the end of the gene
    at prediction, to the start of the next gene in the genome.
    :param ori_pred: index of predicted ori site
    :param ter_pred: index of predicted ter site
    :param gene_intervals: a list of position intervals for all genes in the genome
    :return: ori_interval: the interval in which predicted ori lies. ter_interval: the interval in which predicted
    ter lies
    """

    ori_first = gene_intervals[ori_pred]
    ori_next = gene_intervals[0] if ori_pred == len(gene_intervals) - 1 else gene_intervals[ori_pred + 1]
    while ori_next[0] == ori_first[1]:
        ori_pred = ori_pred + 1
        ori_next = gene_intervals[0] if ori_pred == len(gene_intervals) - 1 else gene_intervals[ori_pred + 1]
    ori_interval = (ori_first[1], ori_next[0])

    ter_first = gene_intervals[ter_pred]
    ter_next = gene_intervals[0] if ter_pred == len(gene_intervals) - 1 else gene_intervals[ter_pred + 1]
    while ter_next[0] == ter_first[1]:
        ter_pred = ter_pred + 1
        ter_next = gene_intervals[0] if ter_pred == len(gene_intervals) - 1 else gene_intervals[ter_pred + 1]

    ter_interval = (ter_first[1], ter_next[0])

    return ori_interval, ter_interval


def find_best_prediction(data, gene_intervals, method="cumulative"):
    """
    Find the best prediction of ori and ter by iteratively decreasing window size and calculating position difference.
    When position changes less than 100 basepairs, accept as best solution.
    :param data: Array of strand orientation data. Each element is -1 or 1
    :param gene_intervals: The position intervals of all genes in the genome
    :param method: 'cumulative' (default) or 'sumdiff'
    :return: the trend calculation of best prediction, as well as the predicted gene indices and basepairs of ori and
    ter. Also returns the window size of the best prediction
    """

    min_win = len(data) // 6 if method == "sumdiff" else 2  # sumdiff method needs larger window than cumulative
    current_win = len(data) // 3 if method == "cumulative" else len(data) // 2  # see above comment
    current_sum, current_ori, current_ter = predict_ori_ter(data, win_size=current_win, method=method)
    current_ori_int, current_ter_int = ori_gene_to_bp(current_ori, current_ter, gene_intervals)

    while current_win >= min_win:
        new_win = current_win // 2
        new_sum, new_ori, new_ter = predict_ori_ter(data, new_win, method=method)
        new_ori_int, new_ter_int = ori_gene_to_bp(new_ori, new_ter, gene_intervals)
        if abs(new_ori_int[0] - current_ori_int[0]) < 100 and abs(new_ter_int[0] - current_ter_int[0]) < 100:
            break
        else:
            current_win = new_win
            current_sum = new_sum
            current_ori = new_ori
            current_ter = new_ter
            current_ori_int = new_ori_int
            current_ter_int = new_ter_int
    return current_sum, current_ori, current_ter, current_ori_int, current_ter_int, current_win


def position_distance(a, b, g_length):
    """
    Calculate the shortest distance between two positions on a circular genome.
    :param a: index of first position
    :param b: index of second position
    :param g_length: total genome length in basepairs
    :return: the calculated distance
    """

    diff = abs(a - b)
    return min(diff, g_length - diff)  # because circular, the shortest distance can be either a-b or length - (a-b)


def n_largest_smallest(data, n):
    """
    Find the indices of the n largest and smallest (respectively) values in an array.
    :param data: the data array
    :param n: the number of indices to find
    :return: two lists: one with the smallest indices and one with the largest
    """

    first_args = np.argpartition(data, n)[:n]
    last_args = np.argpartition(data, -n)[-n:]
    return [(arg, data[arg]) for arg in first_args], [(arg, data[arg]) for arg in last_args]


def perfect_plot(first, ori, ter, last):
    """
    Compute a "perfect" gene orientation plot given an ori and a ter position from a model data set (calculated trend).
     Consists of linear segments with a sign change around ori and ter.
    :param first: a tuple of the index and value of first position in model data
    :param ori: (index, value) of ori from model data
    :param ter: (index, value) of ter from model data
    :param last: (index, value) of the last position in model data
    :return: array with the "perfect" plot values
    """

    out_plot = np.asarray([])
    if ori[0] > ter[0]:
        if ori[0] != last[0]:
            out_plot = np.append(out_plot, np.linspace(start=ter[1], stop=ori[1], num=ori[0] - ter[0]))
            out_plot = np.append(out_plot, np.linspace(start=ori[1], stop=last[1], num=last[0] - ori[0] + 1))
        else:
            out_plot = np.append(out_plot, np.linspace(start=ter[1], stop=ori[1], num=ori[0] - ter[0] + 1))
        if ter[0] != first[0]:
            out_plot = np.append(np.linspace(start=first[1], stop=ter[1], num=ter[0] - first[0]), out_plot)
    elif ori[0] < ter[0]:
        if ori[0] != first[0]:
            out_plot = np.append(out_plot, np.linspace(start=ori[1], stop=ter[1], num=ter[0] - ori[0]))
            out_plot = np.append(np.linspace(start=first[1], stop=ori[1], num=ori[0] - first[0] + 1), out_plot)
        else:
            out_plot = np.append(out_plot, np.linspace(start=ori[1], stop=ter[1], num=ter[0] - ori[0]))
        if ter[0] != last[0]:
            out_plot = np.append(out_plot, np.linspace(start=ter[1], stop=last[1], num=last[0] - ter[0]))
    else:
        raise Exception("Impossible to predict graph (ori and ter are the same?!)")
    return out_plot


def real_perfect_diff(real_data, perfect_data):
    """
    Calculates the coefficient of variation (standard deviation / mean) of the pointwise absolute difference
    between real strand orientation trend data and its "perfect" representation as calculated with perfect_plot().
    :param real_data: array of the real data
    :param perfect_data: array of the perfect data
    :return: the coefficient of variation (float)
    """

    diff = [abs(perfect_data[i] - real_data[i]) for i in range(len(perfect_data))]
    return np.std(diff) / np.mean(diff)


def consecutive(data):
    """
    Find sections of data with consecutive indices in a list of tuples with (index, value) representing candidates for
    ori and ter
    :param data: list of tuples
    :return: a list of the middle tuples of each found section of consecutives
    """

    if len(data) == 1:
        return [data[0]]
    data.sort(key=lambda x: x[0])
    ret = []
    current_seq = [data[0]]
    for i in range(1, len(data)):
        if data[i][0] == data[i-1][0] + 1:
            current_seq.append(data[i])
        else:
            if len(current_seq) != 0:
                current_seq.append(data[i])
                ret.append(current_seq[(len(current_seq) - 1) // 2])
                current_seq = []
            else:
                current_seq.append(data[i])
    if len(current_seq) != 0:
        ret.append(current_seq[(len(current_seq) - 1) // 2])
    return ret


def outliers(data, cutoff_factor, side):
    """
    Find the upper or lower (determined by 'side') outliers in a list of (index, value) tuples representing
    ori or ter candidates.
    :param data: the input list of candidate tuples
    :param cutoff_factor: how many standard deviations to use as the outlier cutoff
    :param side: 'upper' or 'lower'
    :return: a list of the outlier tuples
    """

    values = [val[1] for val in data]
    data_mean, data_std = np.mean(values), np.std(values)
    cutoff = cutoff_factor * data_std
    if side == "lower":
        return [x for x in data if x[1] < data_mean - cutoff]
    elif side == "upper":
        return [x for x in data if x[1] > data_mean + cutoff]
    else:
        raise Exception("Invalid 'side' argument (lower or upper allowed)")


def find_unique_values(outliers):
    """
    Find unique values in a list of (index, value) tuples out ori and ter prediction outliers.
    :param outliers: An (index, value) tuple list of ori or ter prediction outliers
    :return: a list of (index, value) tuples of the middle index for each group of tuples sharing the same value
    """

    unique_dict = defaultdict(list)
    for val in outliers:
        if val[1] not in unique_dict.keys():
            unique_dict[val[1]] = []
        unique_dict[val[1]].append(val[0])

    return [(value[(len(value) - 1) // 2], key) for key, value in unique_dict.items()]


def select_ori_ter_candidates(data, n, initial_cutoff):
    """
    Find non-consecutive, unique, statistically outlying candidates of ori and ter. Start with a set number of the
    smallest and largest values of a trend calculation data sets, and reduce that candidate set through a series of
    methods.
    :param data: a data array of strand orientation trend calculation
    :param n: how many smallest and largest values to start with as candidates
    :param initial_cutoff: the initial standard deviation cutoff to determine statistical outliers
    :return: two lists of (index, value) tuples with ori and ter candidates
    """

    min_candidates, max_candidates = n_largest_smallest(data, n)
    min_outliers = []
    max_outliers = []

    # iteratively decrease stdev cutoff until at least one outlier (upper and lower) is found
    for i in range(initial_cutoff, 0, -1):
        min_outliers = min_outliers + outliers(min_candidates, i, "lower")
        max_outliers = max_outliers + outliers(max_candidates, i, "upper")
        if len(min_outliers) != 0 and len(max_outliers) != 0:
            break

    # if no outliers are found, move on with all initial candidates. Else, use the found outliers
    if len(min_outliers) == 0:
        min_ret = min_candidates
    else:
        min_ret = min_outliers
    if len(max_outliers) == 0:
        max_ret = max_candidates
    else:
        max_ret = max_outliers

    # only keep the candidates with unique values
    min_uniques = find_unique_values(min_ret)
    max_uniques = find_unique_values(max_ret)

    # only keep candidates with non-consecutive indices
    return consecutive(min_uniques), consecutive(max_uniques)


def combo_diffs(data, min_candidates, max_candidates):
    """
    For two lists of minimum and maximum candidates (respectively, ori and ter or vice versa), calculate the perfect
    plot for each possible combination and compute the coefficient of variation for the difference of that to the real
    data.
    :param data: The calculated trend data set
    :param min_candidates: the list of candidates for minimum position
    :param max_candidates: the list of candidates for maximum position
    :return: a list of tuples with (minimum index, maximum index, calculated coefficient of variation)
    """

    combos_diffs = []
    for min_val in min_candidates:
        for max_val in max_candidates:
            if min_val[0] != max_val[0]:  # if there are combinations with same index for both, ignore those
                perf_plot = perfect_plot((0, data[0]), min_val, max_val, (len(data) - 1, data[-1]))
                diff = real_perfect_diff(data, perf_plot)
                combos_diffs.append((min_val[0], max_val[0], diff))
    return combos_diffs


def go_find_ori(in_file, genes_dictionary, sequence_length):
    """
    Combine all previously defined functions to read a FASTA file and find the bestguess of ori and ter positions
    :param in_file:             File name of the input FASTA genome file
    :param genes_dictionary:    Dictionary containing all genes
    :return:                    The calculated trend data set, the perfect plot,
                                the ori interval and the ter interval of the best prediction,
                                list of gene start positions, list of gene end positions,
                                the method resulting in the best prediction, and the number of
                                plus and minus strands.
    """

    if not genes_dictionary:
        gene_out = find_genes(in_file, length=True)  # include calculation of genome length
        genes = gene_out['genes']
        gene_parse = parse_genes(genes)
    else:
        gene_parse = parse_genes(genes_dictionary)

    strands = gene_parse['strand']
    starts = gene_parse['start']
    ends = gene_parse['end']
    intervals = list(zip(starts, ends))

    strands = np.asarray(strands)

    strand_sum = np.cumsum(strands)
    strand_sumdiff = sliding_sumdiff(strands, len(strands) // 3)

    if sequence_length < 500000:
        no_max = 150
    else:
        no_max = 250

    cum_ori_cands, cum_ter_cands = \
        select_ori_ter_candidates(strand_sum, no_max, 5)        # start with 250 min and max candidates
    sd_ter_cands, sd_ori_cands = \
        select_ori_ter_candidates(strand_sumdiff, no_max, 5)    # and a stdev cutoff of 5

    cum_diffs = combo_diffs(strand_sum, cum_ori_cands, cum_ter_cands)
    cum_mean = np.mean([val[1] for val in cum_diffs])
    sd_diffs = combo_diffs(strand_sumdiff, sd_ori_cands, sd_ter_cands)
    sd_mean = np.mean([val[1] for val in sd_diffs])

    cum_best = [item for item in cum_diffs if item[2] == min([item[2] for item in cum_diffs])][0]
    sd_best = [item for item in sd_diffs if item[2] == min(item[2] for item in sd_diffs)][0]

    cum_best_dev = (cum_best[1] - cum_mean) / cum_mean
    sd_best_dev = (sd_best[1] - sd_mean) / sd_mean

    if cum_best_dev < sd_best_dev:
        final_prediction = cum_best
        best_ori = "cum-"
    elif cum_best_dev > sd_best_dev:
        final_prediction = sd_best
        best_ori = "sumdiff+"
    else:
        # if both predictions are equally good, decide with a coin flip
        if np.random.random(1) < 0.5:
            final_prediction = cum_best
            best_ori = "cum-"
        else:
            final_prediction = sd_best
            best_ori = "sumdiff+"

    if final_prediction == cum_best:
        data_plot = strand_sum
    else:
        data_plot = strand_sumdiff

    perf_plot = perfect_plot((0, data_plot[0]), (final_prediction[0], data_plot[final_prediction[0]]),
                             (final_prediction[1], data_plot[final_prediction[1]]), (len(strands) - 1, data_plot[-1]))

    ori_int, ter_int = ori_gene_to_bp(final_prediction[0], final_prediction[1], intervals)

    plus_content = round((len(np.where(np.equal(strands, 1))[0])/len(strands))*100)
    minus_content = 100 - plus_content

    return list(data_plot), list(perf_plot), list(ori_int), list(ter_int), starts, ends, best_ori,\
        plus_content, minus_content


def go_bootstrap(data_plot, perf_plot, starts, ends, ORI, TER, sequence_length, plus_content, minus_content,
                 log_file, best_ori = "cum-",
                 ori_rrna_range = list(), ter_rrna_range = list(), ori_go_rrna = list(), ter_go_rrna = list()):
    """
    Generates random lists with same number of genes as original sequence.
    The random lists are generated by randomly choosing -1 or 1 (weighted
    depending on the amount of -1 and 1 genes on original chromosome).
    :param data_plot:       List of data points generated by gene orientation function (cum or sumdiff)
    :param perf_plot:       Perfect (linear) plot of the data points given the ORI and TER positions
    :param starts:          List of gene start positions
    :param ends:            List of gene end positions
    :param ORI:             Predicted ORI interval
    :param TER:             Predicted TER interval
    :param sequence_length: Length of chromosome
    :param plus_content:    Number of plus strand genes on original sequence
    :param minus_content:   Number of minus strand genes on original sequence
    :param best_ori:        Method generating the best prediction
    :param ori_rrna_range:  Predicted ORI interval from rRNA
    :param ter_rrna_range:  Predicted TER interval from rRNA
    :return:                p-values for ORI and TER
    """

    # Lists containing indexes ranging from start to finish of the predicted rRNA intervals
    rrnas_ori = list()
    rrnas_ter = list()

    # Strand options - either plus or minus strand
    strand_opt = [-1, 1]

    # Weights - probability of either strand being randomly chosen
    weights = [minus_content / 100, plus_content / 100]

    # Predicted maximum distance from ORI and TER
    max_perc_genome = round(sequence_length * 0.70)
    min_perc_genome = int(sequence_length * 0.30)

    # Initiates p-values for ORI and TER
    p_ter_go = p_ori_go = float(0)

    '''If distance between ORI and TER interval starts or 
    ends is greater than the expected maximum distance, the prediction is likely to
    not be correct and bootstrap function is not performed.'''
    if not min_perc_genome <= abs(ORI[0] - TER[0]) <= max_perc_genome:
        p_ter_go = p_ori_go = 1.0
    else:
        # All indices are save to a list
        indices = list(range(0, len(data_plot)))

        # The indices of ORI and TER are saved as the end of the previous gene
        # and the beginning of the next gene
        if ORI[0] in ends:
            ind_ori = [ends.index(ORI[0]), starts.index(ORI[1])]
        elif ORI[1] in ends:
            ind_ori = [ends.index(ORI[1]), starts.index(ORI[0])]

        if TER[0] in ends:
            ind_ter = [ends.index(TER[0]), starts.index(TER[1])]
        elif TER[1] in ends:
            ind_ter = [ends.index(TER[1]), starts.index(TER[0])]

        # Initiates average difference between actual and perfect data
        av_diff_go = 0

        # Length of actual and perfect data lists
        len_perf_plot = len(perf_plot)
        len_data_plot = len(data_plot)

        '''Calculates average difference between actual and perfect data'''
        if len_data_plot == len_perf_plot:
            sum_diff_go = 0
            for i in range(len_perf_plot):
                sum_diff_go = sum_diff_go + abs(perf_plot[i] - data_plot[i])
            av_diff_go = abs(sum_diff_go / len_perf_plot)

        # Initiates list for storing indexes around ORI and TER with values
        # differing less than the average difference
        aroundter_go = list()
        aroundori_go = list()

        # Initiates index were there may be a jump in the plot. Eg when position
        # is predicted at end or beginning of plot, or otherwise noisy
        ori_break = -1
        ter_break = -1

        '''Saves all indices with value similar to the predicted origin and ter, 
        if there is a jump in indices, the jump positions are saved'''
        for val in indices:
            if abs(data_plot[val] - data_plot[ind_ori[0]]) < abs(av_diff_go) or \
                    abs(data_plot[val] - data_plot[ind_ori[1]]) < abs(av_diff_go):
                if len(aroundori_go) != 0:
                    if val > aroundori_go[len(aroundori_go)-1] + 1:
                        ori_break = val
                aroundori_go.append(val)
            if abs(data_plot[val] - data_plot[ind_ter[0]]) < abs(av_diff_go) or \
                    abs(data_plot[val] - data_plot[ind_ter[1]]) < abs(av_diff_go):
                if len(aroundter_go) != 0:
                    if val > aroundter_go[-1] + 1:
                        ter_break = val
                aroundter_go.append(val)

        '''If a break is found and the predicted origin is greater than the break position, 
        and the range does not span the end and beginning of the sequence, 
        the positions below the break point are deleted. 
        If a break is found and the predicted origin is less than the break position, 
        and the range does not span the end and beginning of the sequence, 
        the positions above the break point are deleted. '''
        if ori_break != -1 and ind_ori[0] >= ori_break and aroundori_go[0] != 0 and aroundori_go[-1] != len_data_plot - 1:
            del aroundori_go[0:aroundori_go.index(ori_break)]
        elif ori_break != -1 and ind_ori[1] <= ori_break and aroundori_go[0] != 0 and aroundori_go[-1] != len_data_plot - 1:
            del aroundori_go[aroundori_go.index(ori_break)::]

        if ter_break != -1 and ind_ter[0] >= ter_break and aroundter_go[0] != 0 and aroundter_go[-1] != len_data_plot - 1:
            del aroundter_go[0:aroundter_go.index(ter_break)]
        elif ter_break != -1 and ind_ter[1] <= ter_break and aroundter_go[0] != 0 and aroundter_go[-1] != len_data_plot - 1:
            del aroundter_go[aroundter_go.index(ter_break)::]

        # Initiates positions of bootstrap predictions
        ter_btstrap_go = 0
        ori_btstrap_go = 0

        #
        ori_start = ori_end = ter_start = ter_end = 0
        p_diff = 0.0

        # Sets number of iterations to 100 000
        N = 1000
        if best_ori == "sumdiff+":
            N = 1000

        with open(log_file, "a") as logs:
            logs.write("%s      %s" % ("    ", ".."))

        btstrap_go = list()
        for i in range(N):

            if i % 100 == 0:
                with open(log_file, "a") as logs:
                    logs.write("{}..".format(i))

            # Generates random sequence of genes
            new_sample_go = np.random.choice(strand_opt, len_data_plot, p=weights, replace=True)

            '''Checking which method generated the best prediction, 
            and decides whether ori and ter is in the maximum or minimum.'''
            if best_ori == "cum-":
                new_sample_go = np.cumsum(new_sample_go)
                ter_btstrap_go = np.argmax(new_sample_go)
                ori_btstrap_go = np.argmin(new_sample_go)
            elif best_ori == "sumdiff+":
                new_sample_go = sliding_sumdiff(new_sample_go, len(new_sample_go) // 3)
                ter_btstrap_go = np.argmin(new_sample_go)
                ori_btstrap_go = np.argmax(new_sample_go)

            if ter_btstrap_go == 0:
                ter_start = ter_start + 1
            elif ter_btstrap_go == len(new_sample_go) - 1:
                ter_end = ter_end + 1
            if ori_btstrap_go == 0:
                ori_start = ori_start + 1
            elif ori_btstrap_go == len(new_sample_go) - 1:
                ori_end = ori_end + 1

            btstrap_go.append([ori_btstrap_go, ter_btstrap_go])

            # if abs(ends[ori_btstrap_go]-starts[ter_btstrap_go]) <= sfperc_genome:
            #     p_diff = p_diff + 1

        '''Checks if the bootstrap predicted ORIs and TERs are within the ranges defined above.
        If yes --> p is increased'''
        for pos in btstrap_go:
            if ori_break != -1 and aroundori_go[0] == 0 and aroundori_go[-1] == len_data_plot - 1:
                if aroundori_go[0] <= pos[0] <= aroundori_go[aroundori_go.index(ori_break) - 1] or \
                        ori_break <= pos[0] <= aroundori_go[-1]:
                    p_ori_go = p_ori_go + 1
            elif ori_break == -1 and aroundori_go[0] != 0 and aroundori_go[-1] != len_data_plot - 1:
                if aroundori_go[0] <= pos[0] <= aroundori_go[-1]:
                    p_ori_go = p_ori_go + 1
            elif ori_break == -1 and aroundori_go[0] == 0 and aroundori_go[-1] == len_data_plot - 1:
                p_ori_go = p_ori_go + 1
            else:
                if aroundori_go[0] <= pos[0] <= aroundori_go[-1]:
                    p_ori_go = p_ori_go + 1

            if ter_break != -1 and aroundter_go[0] == 0 and aroundter_go[-1] == len_data_plot - 1:
                if aroundter_go[0] <= pos[1] <= aroundter_go[aroundter_go.index(ter_break) - 1] or \
                        ter_break <= pos[1] <= aroundter_go[-1]:
                    p_ter_go = p_ter_go + 1
            elif ter_break == -1 and aroundter_go[0] != 0 and aroundter_go[-1] != len_data_plot - 1:
                if aroundter_go[0] <= pos[1] <= aroundter_go[-1]:
                    p_ter_go = p_ter_go + 1
            elif ter_break == -1 and aroundter_go[0] == 0 and aroundter_go[-1] == len_data_plot - 1:
                p_ter_go = p_ter_go + 1
            else:
                if aroundter_go[0] <= pos[1] <= aroundter_go[-1]:
                    p_ter_go = p_ter_go + 1

        p_ter_go = p_ter_go / N
        p_ori_go = p_ori_go / N

        '''If the predicted ORI and TER are not within the rRNA range, 
        this is not a likely prediction --> p = 1.0'''
        if len(ori_rrna_range) != 0:
            if len(ori_go_rrna) == 0:
                p_ori_go = 1.0
        if len(ter_rrna_range) != 0:
            if len(ter_go_rrna) == 0:
                p_ter_go = 1.0

    return p_ori_go, p_ter_go
