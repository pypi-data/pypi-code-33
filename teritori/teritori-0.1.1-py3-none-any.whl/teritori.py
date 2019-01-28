""""------------------------------------------------PACKAGES---------------------------------------------------------"""
from __future__ import print_function
from Bio import SeqIO
import subprocess
import errno
import tempfile
from teritori import Motifs as mot, GOscript as go, GCscript as gc, final_pred as fp
import argparse
from pylab import *
import csv
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import minmax_scale


"""---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------FUNCTIONS---------------------------------------------------------"""


def run_prodigal(input_file, temp_file):
    """
    Runs prodigal

    :param input_file:  Sequence FASTA file
    :param temp_file:   Name of temporary file
    :return:            Saves output to temporary file
    """
    try:
        prodigal = subprocess.Popen(['prodigal', '-i', input_file, '-d', temp_file, '-f', 'gff'],
                                    stdout=subprocess.PIPE, shell=False)
        prodigal.stdout.read().decode('utf-8')
    except subprocess.CalledProcessError:
        print("Error with Prodigal")


def main():
    """----------------------------------------------PARSER----------------------------------------------------------"""
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="Genome file, FASTA format.")
    parser.add_argument("--genes", help="File containing genes from Prodigal")
    parser.add_argument("-o", "--output", help="Prefix for all files created in script", type=str)
    parser.add_argument("-l", "--linear", help="Specifies that the genome is linear",
                        action="store_true", default=False)
    parser.add_argument("-a", "--all", help="Specifies that all features should be used",
                        action="store_true", default=True)
    parser.add_argument("--gc", help="Use GC-script", action="store_true", default=False)
    parser.add_argument("--go", help="Use Gene orientation script", action="store_true", default=False)
    parser.add_argument("--cm", help="Use script for conserved motifs", action="store_true", default=False)
    parser.add_argument("--graph", help="Should graph be displayed or not?", action="store_true", default=False)
    args = parser.parse_args()

    if args.cm or args.go or args.gc:
        args.all = False

    """----------------------------------------FILE HANDLING---------------------------------------------------------"""
    # Current directory
    cwd = os.getcwd()

    # Path of the directory to be created
    outer_path = cwd + "/terITori"
    results_path = outer_path + "/Results"

    '''Creating directory if it does not already exist'''
    if not os.path.isdir(outer_path):
        try:
            os.mkdir(outer_path)
        except OSError:
            sys.exit("Creation of directory %s failed" % outer_path)
    if not os.path.isdir(results_path):
        try:
            os.mkdir(results_path)
        except OSError:
            sys.exit("Creation of directory %s failed" % results_path)

    # Defines the input file
    in_file = args.input
    gene_file = ""
    if not os.path.exists(os.path.abspath(in_file)):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), in_file)

    # Opens file. The file is properly closed after reading it
    # "rU" --> reading using universal readline mode - independent of OS
    with open(in_file, "rU") as file:
        sequence = SeqIO.read(file, "fasta")     # Reads the sequence, saves sequence in variable.

    """--------------------------------------UNIVERSAL VARIABLES-----------------------------------------------------"""
    # Saves species info
    split_desc = sequence.description.split(",")[0]                         # Full title
    sequence_length = len(sequence.seq)                                     # Full sequence length
    name_species = split_desc.split(None)[1] + " " + split_desc.split(None)[2]      # Name
    strain_split = split_desc.split(None)[3::]                              # Strain information
    strain = ""
    for i in range(0, len(strain_split)):                           # Strain information as string
        strain = strain + strain_split[i] + " "

    # Significance level
    alpha = 0.05

    # Linear or not
    linear = args.linear

    """---------------------------------CREATE RESULTS FOLDER AND FILE-----------------------------------------------"""
    # Create path for results'''
    species = name_species.replace(" ", "_") if not args.output else args.output # uses user-specified prefix as name if it is specified
    inner_path = results_path + "/" + species
    if not os.path.isdir(inner_path):
        try:
            os.mkdir(inner_path)
        except OSError:
            sys.exit("Creation of inner directory %s failed" % inner_path)

    # Create file for handling results'''
    csv_file = inner_path + "/" + species + "_results_teritori.csv"

    with open(csv_file, mode='w') as results:
        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        teritori_writer.writerow([species, "Sequence length:", sequence_length, '', '', ''])
        teritori_writer.writerow(['Prediction measurement', 'ORI', 'p-value \n(ori)', 'TER', 'p-value \n(ter)',
                                  'Comment'])

    log_file = inner_path + "/" + species + "_log.txt"

    with open(log_file, "w") as logs:
        logs.write("{}       Log file -- terITori    Created: {}\n\n".format(
            species, time.asctime(time.localtime(time.time()))))

    """-----------------------------------------------PRODIGAL-------------------------------------------------------"""
    # Dictionary for storing gene information
    genes = list()
    record_dict = dict()

    '''Runs Prodigal if gene orientation, gc-skew or all have been chosen in input, 
    and if a gene file has not been entered'''
    if args.go or args.gc or args.all:
        # Creating temporary file
        temp = tempfile.NamedTemporaryFile(delete=True)

        temp.name = "genes_" + species

        '''If a gene file is entered when running the program, the genes are collected from file.
        Else, Prodigal is run'''
        if args.genes:
            with open(log_file, "a") as logs:
                logs.write("%s      %s      %s" % (time.asctime(time.localtime(time.time())),
                                                   "Genes entered as input -- not running Prodigal.\n", ""))

            gene_file = os.path.abspath(args.genes)
            genes = list(SeqIO.parse(gene_file, "fasta"))

        elif not args.genes:
            ''' Prodigal - returns genes'''
            with open(log_file, "a") as logs:
                logs.write("%s      %s     " % (time.asctime(time.localtime(time.time())),
                                                "No genes previously found - Running Prodigal..."))
                run_prodigal(in_file, temp.name)
                gene_file = os.path.abspath(temp.name)

                logs.write("%s" % "Prodigal successful!\n")

        # Puts all genes from Prodigal or previous gene file into a dictionary'''
        record_dict = dict(SeqIO.index(gene_file, "fasta"))

        '''Saves the dictionary as a file if genes were not specified in input'''
        genes_directory = inner_path + "/" + temp.name
        if not args.genes:
            with open(genes_directory, 'w') as f:
                for key, value in record_dict.items():
                    f.write('%s%s\n' % (">" + value.description, "\n" + value.seq))

        # Closes temporary file'''
        temp.close()

    """-----------------------------------------------------------------------------------------------------------------
    -------------------------------------------CONSERVED MOTIFS---------------------------------------------------------
    -----------------------------------------------------------------------------------------------------------------"""
    # Coordinates from rRNA prediction
    ORI_rrnas = [0, 0]
    TER_rrnas = [0, 0]

    # Coordinates from dnaA and dif motif predictions
    ori_dnaa_boxes = [0, 0]
    ter_dif_motifs = [0, 0]

    # Index where the most number of dnaA boxes are present
    # Used to validate ori_dnaa_boxes interval
    dnaa_max_pos = 0
    dif_max_pos = 0

    # List for storing rRNA results
    rrnas = list()

    # Lists for storing all indices in intervals
    ori_rrna_range = list()
    ter_rrna_range = list()
    ori_dnaa_range = list()
    ter_dif_range = list()

    # Lists for storing sorted dnaA boxes and dif motifs
    dnaa_sorted = list()
    dif_sorted = list()

    '''If -cm is specified: Runs Motifs.py script'''
    if args.cm or args.all:
        with open(log_file, "a") as logs:
            logs.write("%s      %s" % (time.asctime(time.localtime(time.time())), "Starting Conserved Motifs...\n"))

        with open(log_file, "a") as logs:
            logs.write("%s      %s                           " % (time.asctime(time.localtime(time.time())),
                                                                  "...Searching for rRNAs..."))

        ''' ---FINDING rRNAs--- '''
        rrnas = mot.finding_rrnas(in_file)
        '''If rRNAs are found, find ORI and TER and save to file'''
        if len(rrnas) != 0:
            ORI_rrnas = mot.finding_ori(rrnas, sequence_length)
            TER_rrnas = mot.finding_ter(rrnas, sequence_length)
            if ORI_rrnas == [0, 0] == TER_rrnas:
                with open(csv_file, mode='a') as results:
                    teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    teritori_writer.writerow(["rRNAs", "---", "", "---", "", "Predictions not possible"])
            elif ORI_rrnas == [0, 0] != TER_rrnas:
                with open(csv_file, mode='a') as results:
                    teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    teritori_writer.writerow(["rRNAs", "---", "", TER_rrnas, "", "ORI prediction not possible"])
            elif ORI_rrnas != [0, 0] == TER_rrnas:
                with open(csv_file, mode='a') as results:
                    teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    teritori_writer.writerow(["rRNAs", ORI_rrnas, "", "---", "", "TER prediction not possible"])
            else:
                with open(csv_file, mode='a') as results:
                    teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    teritori_writer.writerow(["rRNAs", ORI_rrnas, "", TER_rrnas, "", ""])

            if ORI_rrnas != [0, 0]:
                if ORI_rrnas[1] < ORI_rrnas[0]:
                    ori_rrna_range = list(range(ORI_rrnas[1], sequence_length-1)) + \
                                     list(range(0, ORI_rrnas[0]))
                elif ORI_rrnas[0] <= ORI_rrnas[1]:
                    ori_rrna_range = list(range(ORI_rrnas[0], ORI_rrnas[1]))

            if TER_rrnas != [0, 0]:
                if TER_rrnas[1] < TER_rrnas[0]:
                    ter_rrna_range = list(range(TER_rrnas[1], sequence_length -1)) + \
                                     list(range(0, TER_rrnas[0]))
                elif TER_rrnas[0] <= TER_rrnas[1]:
                    ter_rrna_range = list(range(TER_rrnas[0], TER_rrnas[1]))
        else:
            with open(csv_file, mode='a') as results:
                teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                teritori_writer.writerow(["rRNAs", "---", "", "---", "", "No rRNAs found, prediction not possible"])

        # rRNAs finished
        with open(log_file, "a") as logs:
            logs.write("%s" % "Done!\n")

        ''' ---FINDING dnaA BOXES--- '''
        with open(log_file, "a") as logs:
            logs.write("%s      %s                      " % (time.asctime(time.localtime(time.time())),
                                                             "...Searching for dnaA boxes..."))

        '''Runs nhmmer to find dnaA boxes'''
        mot.hmm_runner(in_file, os.path.dirname(os.path.abspath( __file__ )) + '/conserved_motifs/dnaaboxes.hmm', os.path.dirname(os.path.abspath( __file__ )) + '/prefix_dnaa_boxes.txt')

        '''Parses the output from nhmmer, containing dnaA boxes'''
        dnaa_boxes = mot.hmm_parser(os.path.dirname(os.path.abspath( __file__ )) + '/prefix_dnaa_boxes.txt')

        '''If dnaA boxes are found, determines ORI'''
        if len(dnaa_boxes) != 0:
            '''Finds the positions of Ori based on dnaA boxes'''
            ori_dnaa_boxes, dnaa_sorted = mot.finding_dnaa_boxes(dnaa_boxes, ORI_rrnas[0], ORI_rrnas[1])

            '''If the interval spans the end and beginning of the sequence,
            define all intervals including from beginning of interval to end of sequence
            and from beginning of sequence to end of interval. 
            Otherwise, from beginning of interval to end of interval'''
            if ori_dnaa_boxes != [0, 0]:
                if ori_dnaa_boxes[1] < ori_dnaa_boxes[0]:
                    ori_dnaa_range = list(range(ori_dnaa_boxes[1], sequence_length-1)) + \
                                     list(range(0, ori_dnaa_boxes[0]))
                elif ori_dnaa_boxes[0] <= ori_dnaa_boxes[1]:
                    ori_dnaa_range = list(range(ori_dnaa_boxes[0], ori_dnaa_boxes[1]))

                if len(ori_dnaa_range) > sequence_length//3:
                    ori_dnaa_range = list()

        '''Saving results from dnaA prediction'''
        if ori_dnaa_boxes != [0, 0]:
            with open(csv_file, mode='a') as results:
                teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                teritori_writer.writerow(["dnaA", ori_dnaa_boxes, "", "---", "", "Prediction of ORI"])
        else:
            with open(csv_file, mode='a') as results:
                teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                teritori_writer.writerow(["dnaA", "---", "", "---", "",
                                          "No significant dnaA boxes found, prediction not possible"])
        # dnaA interval finished
        with open(log_file, "a") as logs:
            logs.write("%s" % "Done!\n")

        ''' ---FINDING dnaA MAXIMUM POSITION--- '''
        with open(log_file, "a") as logs:
            logs.writelines("%s      %s                  " % (time.asctime(time.localtime(time.time())),
                                                              "...Calculating dnaA box maximum..."))

        '''If dnaA boxes are found, 1000 bp window with the most number of dnaa boxes'''
        if len(dnaa_boxes) != 0 and ORI_rrnas != [0, 0]:
            dnaa_max_pos = mot.dnaa_max(dnaa_boxes, ORI_rrnas, sequence_length, name_species)

            '''If the index is within the dnaA ORI interval, trust the interval.'''
            if len(ori_dnaa_range) != 0:
                '''Checks if the index is within the interval and saves result.'''
                if dnaa_max_pos in ori_dnaa_range:
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["dnaA max", dnaa_max_pos, "", "---", "",
                                                  "Prediction in dnaA prediction range"])
                else:
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(['dnaA max', dnaa_max_pos, "", "---", "",
                                                  "OBS! Prediction outside dnaA prediction range"])
        # dnaA box maximum finished
        with open(log_file, "a") as logs:
            logs.write("%s" % "Done!\n")

        ''' ---FINDING DIF MOTIFS--- '''
        with open(log_file, "a") as logs:
            logs.write("%s      %s" % (time.asctime(time.localtime(time.time())),
                                       "...Finding dif motifs...\n".format()))

        '''Runs nhmmer to find dif motifs'''
        mot.hmm_runner(in_file, os.path.dirname(os.path.abspath(__file__)) + '/conserved_motifs/difmotifs.hmm', os.path.dirname(os.path.abspath(__file__)) + '/prefix_dif_motifs.txt')

        '''Parses the output from nhmmer, containing dif motifs'''
        dif_motifs = mot.hmm_parser(os.path.dirname(os.path.abspath(__file__)) + '/prefix_dif_motifs.txt')

        '''If dif motifs are found, determine TER interval'''
        if len(dif_motifs) != 0:
            '''Finds the positions of Ter based on dif motifs'''
            ter_dif_motifs, dif_sorted = mot.finding_dif_motifs(dif_motifs, TER_rrnas[0], TER_rrnas[1])

            if ter_dif_motifs != [0, 0]:
                if ter_dif_motifs[1] < ter_dif_motifs[0]:
                    ter_dif_range = list(range(ter_dif_motifs[1], sequence_length - 1)) + \
                                    list(range(0, ter_dif_motifs[0]))
                elif ter_dif_motifs[0] <= ter_dif_motifs[1]:
                    ter_dif_range = list(range(ter_dif_motifs[0], ter_dif_motifs[1]))

                if len(ter_dif_range) > sequence_length//3:
                    ter_dif_range = list()

        '''Saving results from dif prediction'''
        if ter_dif_motifs != [0, 0]:
            with open(csv_file, mode='a') as results:
                teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                teritori_writer.writerow(["dif", "---", "", ter_dif_motifs, "", "Prediction of TER"])
        else:
            with open(csv_file, mode='a') as results:
                teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                teritori_writer.writerow(["dif", "---", "", "---", "",
                                          "No significant dif motifs found, prediction not possible"])

            if ter_dif_motifs != [0, 0]:
                if ter_dif_motifs[1] < ter_dif_motifs[0]:
                    dif_range = list(range(ter_dif_motifs[1], sequence_length)) + \
                                list(range(0, ter_dif_motifs[0]))
                elif ter_dif_motifs[0] <= ter_dif_motifs[1]:
                    dif_range = list(range(ter_dif_motifs[0], ter_dif_motifs[1]))

        # dif motifs finished
        with open(log_file, "a") as logs:
            logs.write("%s" % "Done!\n")

        ''' ---FINDING DIF MOTIF MAXIMUM--- '''
        with open(log_file, "a") as logs:
            logs.writelines("%s     %s                  " % (time.asctime(time.localtime(time.time())),
                                                             "...Calculating dif motif maximum..."))

        '''If dnaA boxes are found, 1000 bp window with the most number of dnaa boxes'''
        if len(dif_motifs) != 0 and TER_rrnas != [0, 0]:
            dif_max_pos = mot.dnaa_max(dif_motifs, TER_rrnas, sequence_length, name_species)

            '''If the index is within the dnaA ORI interval, trust the interval.'''
            if len(ter_dif_range) != 0:
                '''Checks if the index is within the interval and saves result.'''
                if dif_max_pos in ter_dif_range:
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["dif max", "", "", dif_max_pos, "",
                                                  "Prediction in dif prediction range"])
                else:
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(['dif max', "", "", dif_max_pos, "",
                                                  "OBS! Prediction outside dif prediction range"])
        # dif motif maximum finished
        with open(log_file, "a") as logs:
            logs.write("%s" % "Done!\n")

        # Motifs completely finished
        with open(log_file, "a") as logs:
            logs.write("%s      %s                                                   %s"
                       % (time.asctime(time.localtime(time.time())), " ", "Motifs prediction finished! \n"))

    """-----------------------------------------------------------------------------------------------------------------
    -----------------------------------------------GENE ORIENTATION-----------------------------------------------------
    -----------------------------------------------------------------------------------------------------------------"""
    # Coordinates for ORI and TER
    ORI_go = [0, 0]
    TER_go = [0, 0]

    # Gene orientation p-values
    p_ori_go = p_ter_go = 1.0

    # Lists for saving results and overlaps
    ori_go_range = list()
    ori_go_rrna = list()
    ori_go_dnaa = list()
    ter_go_range = list()
    ter_go_rrna = list()
    ter_go_dif = list()

    '''If -go is specified: Runs GOscript.py script'''
    if args.go or args.all:
        with open(log_file, "a") as logs:
            logs.write("%s      %s" % (time.asctime(time.localtime(time.time())), "Starting Gene Orientation...\n"))

        '''Finds the ORI and TER using gene orientation calculations'''
        data_plot, perf_plot, ORI_go, TER_go, starts, ends, best_ori, plus_content, minus_content \
            = go.go_find_ori(in_file, record_dict, sequence_length)

        with open(log_file, "a") as logs:
            logs.write("%s      %s" % (time.asctime(time.localtime(time.time())),
                                       "...Gene orientation data calculated.\n"))

        # Length of produced list
        len_data_plot = len(data_plot)

        '''The list of values is normalized using the value 
        which has the greatest absolute value'''
        if abs(max(data_plot)) > abs(min(data_plot)):
            div = abs(max(data_plot))
        else:
            div = abs(min(data_plot))
        normalized_go = minmax_scale(data_plot, feature_range=(0, 1), axis=0, copy=True)
        normalized_go_perf = minmax_scale(perf_plot, feature_range=(0, 1), axis=0, copy=True)

        '''If the start of the interval is greater than the end of the interval, 
        the intervals are swapped.'''
        if ORI_go[0] > ORI_go[1]:
            ORI_go = list(reversed(ORI_go))
        if TER_go[0] > TER_go[1]:
            TER_go = list(reversed(TER_go))

        ori_go_range = list(range(ORI_go[0], ORI_go[1]))
        ter_go_range = list(range(TER_go[0], TER_go[1]))

        '''If the positions have been previously predicted using the motifs, 
        the gene orientation bootstrap function is run using the previously predicted intervals'''
        if args.cm or args.all:
            '''If dnaA and dif intervals were found, use these for predicting the probabilities of the gene orientation
            interval'''
            if len(ori_dnaa_range) != 0 and len(ter_dif_range) != 0:
                # Saves all positions with intervals
                ori_go_dnaa = list(set(ori_go_range) & set(ori_dnaa_range))
                ter_go_dif = list(set(ter_go_range) & set(ter_dif_range))

                '''Checks if gene orientation intervals overlap with dnaA and dif intervals
                and in that case uses these intervals to predict prediction probability. 
                Otherwise the gene orientation prediction is not probable'''
                if len(ori_go_dnaa) != 0 or len(ter_go_dif) != 0:
                    with open(log_file, "a") as logs:
                        logs.write("%s      %s      " % (time.asctime(time.localtime(time.time())),
                                                         "...Starting Bootstrap function...\n"))

                    p_ori_go, p_ter_go = go.go_bootstrap(normalized_go, normalized_go_perf, starts, ends,
                                                         ORI_go, TER_go, sequence_length, plus_content, minus_content,
                                                         log_file, best_ori,
                                                         ori_dnaa_range, ter_dif_range, ori_go_dnaa, ter_go_dif)
                    with open(log_file, "a") as logs:
                        logs.write("%s" % "   Done! \n")

                else:
                    with open(log_file, "a") as logs:
                        logs.write("%s      %s" % (time.asctime(time.localtime(time.time())),
                                                   "Gene orientation predictions not within probable range. "
                                                   "Bootstrap not performed.\n"))
                    p_ori_go = 1.0
                    p_ter_go = 1.0

            elif len(ori_rrna_range) != 0 and len(ter_rrna_range) != 0:
                # Saves the overlap between gene orientation interval and rRNA intervals
                ori_go_rrna = list(set(ori_go_range) & set(ori_rrna_range))
                ter_go_rrna = list(set(ter_go_range) & set(ter_rrna_range))

                '''Checking if gene orientation interval is within the rrna interval, 
                and uses this to evaluate the uncertainty of the predictions. Otherwise
                the gene orientation prediction is not probably.'''
                if len(ori_go_rrna) != 0 or len(ter_go_rrna) != 0:
                    with open(log_file, "a") as logs:
                        logs.write("%s      %s                   " % (time.asctime(time.localtime(time.time())),
                                                                      "...Starting Bootstrap function...\n"))

                    p_ori_go, p_ter_go = go.go_bootstrap(normalized_go, normalized_go_perf, starts, ends,
                                                         ORI_go, TER_go, sequence_length, plus_content, minus_content,
                                                         log_file, best_ori,
                                                         ori_rrna_range, ter_rrna_range, ori_go_rrna, ter_go_rrna)
                    with open(log_file, "a") as logs:
                        logs.write("%s" % "   Done! \n")
                else:
                    with open(log_file, "a") as logs:
                        logs.write("%s      %s" % (time.asctime(time.localtime(time.time())),
                                                   "Gene orientation predictions not within probable range. "
                                                   "Bootstrap not performed.\n"))
                    p_ori_go = 1.0
                    p_ter_go = 1.0
            else:
                with open(log_file, "a") as logs:
                    logs.write("%s      %s                   " % (time.asctime(time.localtime(time.time())),
                                                                  "...Starting Bootstrap function...\n"))

                p_ori_go, p_ter_go = go.go_bootstrap(normalized_go, normalized_go_perf, starts, ends,
                                                     ORI_go, TER_go, sequence_length, plus_content, minus_content,
                                                     log_file, best_ori)
                with open(log_file, "a") as logs:
                    logs.write("%s" % "   Done! \n")
        else:
            with open(log_file, "a") as logs:
                logs.write("%s      %s                   " % (time.asctime(time.localtime(time.time())),
                                                              "...Starting Bootstrap function...\n"))

            p_ori_go, p_ter_go = go.go_bootstrap(normalized_go, normalized_go_perf, starts, ends,
                                                 ORI_go, TER_go, sequence_length, plus_content, minus_content,
                                                 log_file, best_ori)

            with open(log_file, "a") as logs:
                logs.write("%s" % "   Done! \n")

        comment = ""
        '''Saves Gene orientation predictions to file'''
        if ORI_go != [0, 0] and TER_go != [0, 0]:
            if p_ori_go > alpha:
                comment = "NB! ORI p-value above significance level, \nORI prediction should not be trusted! "
            if p_ter_go > alpha and comment == "":
                comment = "NB! TER p-value above significance level, \nTER prediction should not be trusted! "
            elif p_ter_go > alpha and comment != "":
                comment = "NB! Both p-values above signficance level, \nGene orientation should not be trusted! "

            with open(csv_file, mode='a') as results:
                teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                teritori_writer.writerow(["Gene orientation", ORI_go, p_ori_go, TER_go, p_ter_go, comment])

        elif ORI_go != [0, 0] and TER_go == [0, 0]:
            if p_ori_go > alpha:
                comment = "NB! p-value above significance level, \nORI prediction should not be trusted! "

            with open(csv_file, mode='a') as results:
                teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                teritori_writer.writerow(["Gene orientation", ORI_go, p_ori_go, "---", "",
                                          comment + "TER prediction not possible."])
        elif ORI_go == [0, 0] and TER_go != [0, 0]:
            if p_ter_go > alpha:
                comment = "NB! p-value above significance level, \nTER prediction should not be trusted! "

            with open(csv_file, mode='a') as results:
                teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                teritori_writer.writerow(["Gene orientation", "---", "", TER_go, p_ter_go,
                                          comment + "ORI prediction not possible."])
        else:
            with open(csv_file, mode='a') as results:
                teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                teritori_writer.writerow(["Gene orientation", "---", "", "---", "", "No prediction possible."])

        with open(log_file, "a") as logs:
            logs.write("%s      %s                                                   %s"
                       % (time.asctime(time.localtime(time.time())), " ", "Gene orientation prediction finished! \n"))

    """-----------------------------------------------------------------------------------------------------------------
    ---------------------------------------------------GC-SKEW----------------------------------------------------------
    -----------------------------------------------------------------------------------------------------------------"""
    ORI_gc = ORI_ta = TER_gc = TER_ta = 0
    p_ori_gc = p_ori_ta = p_ter_gc = p_ter_ta = 1.0
    av_diff_gc = av_diff_ta = 0.0
    gc_cum = list()
    ta_cum = list()

    '''If -gc is specified: running GCscript.py'''
    if args.gc or args.all:
        with open(log_file, "a") as logs:
            logs.write("%s      %s" % (time.asctime(time.localtime(time.time())),
                                       "Starting GC-skew...\n"))

        '''If output file name is specified, enter this, otherwise use species name from file'''
        output_name = inner_path + "/" + species

        # Calls on GC and TA calculation
        ORI_gc, TER_gc, gc_cum, gc_normalized, perfect_gc, x_perfect_gc, \
        ORI_ta, TER_ta, ta_cum, ta_normalized, perfect_ta, x_perfect_ta, positions \
            = gc.main(record_dict, sequence, sequence_length, name_species, strain, output_name, args.graph)

        with open(log_file, "a") as logs:
            logs.write("%s      %s" % (time.asctime(time.localtime(time.time())),
                                       "...GC- and TA-skew calculations finished!\n"))

        # Calculates G, C, T and A content of the chromosome
        G_content, C_content, T_content, A_content \
            = gc.calculate_overall_gc(record_dict, positions, sequence.seq)

        # Calculates the average difference between the real and perfect data
        av_diff_gc, av_diff_ta = gc.diff_perf_real(perfect_gc, gc_normalized, perfect_ta, ta_normalized)

        # Finds all indices with value differing less than the average difference,
        # and the break points if found
        aroundori_gc, aroundter_gc, ori_break_gc, ter_break_gc = \
            gc.around_pos(gc_normalized, ORI_gc, TER_gc, av_diff_gc)
        aroundori_ta, aroundter_ta, ori_break_ta, ter_break_ta = \
            gc.around_pos(ta_normalized, ORI_ta, TER_ta, av_diff_ta)

        # Calculates slopes before and after ORI and TER
        av_gc_bf_ori, av_gc_af_ori, av_gc_bf_ter, av_gc_af_ter, av_ta_bf_ori, \
        av_ta_af_ori, av_ta_bf_ter, av_ta_af_ter, average_slope_gc, average_slope_ta, \
        av_ori_ter_gc, av_ori_ter_ta = gc.slopes(gc_normalized, ta_normalized, ORI_gc,
                                                 TER_gc, ORI_ta, TER_ta)

        # Initiates window size
        window_size = int(0.0001*sequence_length)

        ori_ter_gc = abs(gc_normalized[TER_gc] - gc_normalized[ORI_gc])
        ori_ter_ta = abs(ta_normalized[TER_ta] - ta_normalized[ORI_ta])

        '''If signficant dnaA boxes or dif motifs were found - uses this for evaluating other predictions.
        Otherwise, checks if significant rrna intervals - use this for evaluating predictions.'''
        if len(ori_dnaa_range) != 0 or len(ter_dif_range) != 0:
            if (ORI_gc in ori_dnaa_range or TER_gc in ter_dif_range) and \
                    (ORI_ta in ori_dnaa_range or TER_ta in ter_dif_range):
                if av_diff_gc <= av_diff_ta:
                    with open(log_file, "a") as logs:
                        logs.write("%s      %s                   " % (time.asctime(time.localtime(time.time())),
                                                                      "...Starting Bootstrap function...\n"))
                    # Starts bootstrap function
                    p_ori_gc, p_ter_gc \
                        = gc.gc_bootstrap(sequence_length, aroundter_gc,
                                          aroundori_gc, aroundter_ta, aroundori_ta, window_size, G_content, C_content,
                                          T_content, A_content, ori_break_gc, ter_break_gc, ori_break_ta, ter_break_ta,
                                          ORI_gc, TER_gc, log_file, ori_dnaa_range, ter_dif_range)
                    p_ori_ta = 1.0
                    p_ter_ta = 1.0
                    with open(log_file, "a") as logs:
                        logs.write("%s" % "   Done! \n")

                elif av_diff_ta < av_diff_gc:
                    with open(log_file, "a") as logs:
                        logs.write("%s      %s                   " % (time.asctime(time.localtime(time.time())),
                                                                      "...Starting Bootstrap function...\n"))
                    p_ori_ta, p_ter_ta \
                        = gc.gc_bootstrap(sequence_length, aroundter_gc,
                                          aroundori_gc, aroundter_ta, aroundori_ta, window_size, G_content, C_content,
                                          T_content, A_content, ori_break_gc, ter_break_gc, ori_break_ta, ter_break_ta,
                                          ORI_ta, TER_ta, log_file, ori_dnaa_range, ter_dif_range)
                    p_ori_gc = 1.0
                    p_ter_gc = 1.0
                    with open(log_file, "a") as logs:
                        logs.write("%s" % "   Done! \n")

            elif (ORI_gc in ori_rrna_range or TER_gc in ter_rrna_range) and \
                    (ORI_ta in ori_rrna_range or TER_ta in ter_rrna_range):
                if av_diff_gc <= av_diff_ta:
                    with open(log_file, "a") as logs:
                        logs.write("%s      %s                   " % (time.asctime(time.localtime(time.time())),
                                                                      "...Starting Bootstrap function...\n"))
                    # Starts bootstrap function
                    p_ori_gc, p_ter_gc \
                        = gc.gc_bootstrap(sequence_length, aroundter_gc,
                                          aroundori_gc, aroundter_ta, aroundori_ta, window_size, G_content, C_content,
                                          T_content, A_content, ori_break_gc, ter_break_gc, ori_break_ta, ter_break_ta,
                                          ORI_gc, TER_gc, log_file, ori_dnaa_range, ter_dif_range)
                    p_ori_ta = 1.0
                    p_ter_ta = 1.0
                    with open(log_file, "a") as logs:
                        logs.write("%s" % "   Done! \n")

                elif av_diff_ta < av_diff_gc:
                    with open(log_file, "a") as logs:
                        logs.write("%s      %s                   " % (time.asctime(time.localtime(time.time())),
                                                                      "...Starting Bootstrap function...\n"))
                    p_ori_ta, p_ter_ta \
                        = gc.gc_bootstrap(sequence_length, aroundter_gc,
                                          aroundori_gc, aroundter_ta, aroundori_ta, window_size, G_content, C_content,
                                          T_content, A_content, ori_break_gc, ter_break_gc, ori_break_ta, ter_break_ta,
                                          ORI_ta, TER_ta, log_file, ori_dnaa_range, ter_dif_range)
                    p_ori_gc = 1.0
                    p_ter_gc = 1.0
                    with open(log_file, "a") as logs:
                        logs.write("%s" % "   Done! \n")

            else:
                with open(log_file, "a") as logs:
                    logs.write("%s      %s" % (time.asctime(time.localtime(time.time())),
                                               "GC-skew predictions not within probable range. "
                                               "Bootstrap not performed.\n"))
                p_ori_gc = 1.0
                p_ter_gc = 1.0
                p_ori_ta = 1.0
                p_ter_ta = 1.0

        elif len(ori_rrna_range) != 0 or len(ter_rrna_range) != 0:
            if (ORI_gc in ori_rrna_range and TER_gc in ter_rrna_range) or \
                    (ORI_ta in ori_rrna_range and TER_ta in ter_rrna_range):
                if av_diff_gc <= av_diff_ta:
                    with open(log_file, "a") as logs:
                        logs.write("%s      %s                   " % (time.asctime(time.localtime(time.time())),
                                                                      "...Starting Bootstrap function...\n"))
                    # Starts bootstrap function
                    p_ori_gc, p_ter_gc \
                        = gc.gc_bootstrap(sequence_length, aroundter_gc,
                                          aroundori_gc, aroundter_ta, aroundori_ta, window_size, G_content, C_content,
                                          T_content, A_content, ori_break_gc, ter_break_gc, ori_break_ta, ter_break_ta,
                                          ORI_gc, TER_gc, log_file, ori_rrna_range, ter_rrna_range)
                    p_ori_ta = 1.0
                    p_ter_ta = 1.0
                    with open(log_file, "a") as logs:
                        logs.write("%s" % "   Done! \n")
                elif av_diff_ta < av_diff_gc:
                    with open(log_file, "a") as logs:
                        logs.write("%s      %s                   " % (time.asctime(time.localtime(time.time())),
                                                                      "...Starting Bootstrap function...\n"))
                    p_ori_ta, p_ter_ta \
                        = gc.gc_bootstrap(sequence_length, aroundter_gc,
                                          aroundori_gc, aroundter_ta, aroundori_ta, window_size, G_content, C_content,
                                          T_content, A_content, ori_break_gc, ter_break_gc, ori_break_ta, ter_break_ta,
                                          ORI_ta, TER_ta, log_file, ori_rrna_range, ter_rrna_range)
                    p_ori_gc = 1.0
                    p_ter_gc = 1.0
                    with open(log_file, "a") as logs:
                        logs.write("%s" % "   Done! \n")

                else:
                    with open(log_file, "a") as logs:
                        logs.write("%s      %s" % (time.asctime(time.localtime(time.time())),
                                                   "GC-skew predictions not within probable range. "
                                                   "Bootstrap not performed.\n"))
                    p_ori_gc = 1.0
                    p_ter_gc = 1.0
                    p_ori_ta = 1.0
                    p_ter_ta = 1.0

        else:
            if av_diff_gc <= av_diff_ta:
                with open(log_file, "a") as logs:
                    logs.write("%s      %s              " % (time.asctime(time.localtime(time.time())),
                                                                  "...Starting Bootstrap function...\n"))

                p_ori_gc, p_ter_gc = gc.gc_bootstrap(sequence_length, aroundter_gc, aroundori_gc,
                                                     aroundter_ta, aroundori_ta, window_size, G_content, C_content,
                                                     T_content, A_content, ori_break_gc, ter_break_gc, ori_break_ta,
                                                     ter_break_ta, ORI_gc, TER_gc, log_file,
                                                     ori_rrna_range, ter_rrna_range)
                p_ori_ta = 1.0
                p_ter_ta = 1.0

                with open(log_file, "a") as logs:
                    logs.write("%s" % "   Done! \n")
            elif av_diff_ta < av_diff_gc:
                with open(log_file, "a") as logs:
                    logs.write("%s      %s               " % (time.asctime(time.localtime(time.time())),
                                                                  "...Starting Bootstrap function...\n"))

                p_ori_ta, p_ter_ta = gc.gc_bootstrap(sequence_length, aroundter_gc, aroundori_gc,
                                                     aroundter_ta, aroundori_ta, window_size, G_content, C_content,
                                                     T_content, A_content, ori_break_gc, ter_break_gc, ori_break_ta,
                                                     ter_break_ta, ORI_ta, TER_ta, log_file,
                                                     ori_rrna_range, ter_rrna_range)
                p_ori_gc = 1.0
                p_ter_gc = 1.0

                with open(log_file, "a") as logs:
                    logs.write("%s" % "   Done! \n")
            else:
                with open(log_file, "a") as logs:
                    logs.write("%s      %s" % (time.asctime(time.localtime(time.time())),
                                               "GC-skew predictions not within probable range. "
                                               "Bootstrap not performed.\n"))
                p_ori_gc = 1.0
                p_ter_gc = 1.0
                p_ori_ta = 1.0
                p_ter_ta = 1.0

        # Save results in csv file
        comment_gc = ""
        comment_ta = ""
        comment = ""
        if p_ori_gc > alpha:
            comment_gc = "NB! p-value above significance level, \nORI prediction should not be trusted!"
        if p_ter_gc > alpha and comment == "":
            comment_gc = "NB! p-value above significance level, \nTER prediction should not be trusted!"
        elif p_ter_gc > alpha < p_ori_gc:
            comment_gc = "NB! Both p-values above signficance level, \nGC-skew should not be trusted!"

        if p_ori_ta > alpha:
            comment_ta = "NB! p-value above significance level, \nORI prediction should not be trusted!"
        if p_ter_ta > alpha and comment == "":
            comment_ta = "NB! p-value above significance level, \nTER prediction should not be trusted!"
        elif p_ori_ta > alpha < p_ter_ta:
            comment_ta = "NB! Both p-values above signficance level, \nTA-skew should not be trusted!"

        with open(csv_file, mode='a') as results:
            teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            teritori_writer.writerow(["GC-skew", ORI_gc, p_ori_gc, TER_gc, p_ter_gc, comment_gc])
            teritori_writer.writerow(["TA-skew", ORI_ta, p_ori_ta, TER_ta, p_ter_ta, comment_ta])

        # Skew prediction finished
        with open(log_file, "a") as logs:
            logs.write("%s      %s                                                   %s"
                       % (time.asctime(time.localtime(time.time())), " ", "GC-skew prediction finished! \n"))

    """-----------------------------------------------------------------------------------------------------------------
    --------------------------------------------COMBINING THE RESULTS---------------------------------------------------
    -----------------------------------------------------------------------------------------------------------------"""
    with open(log_file, "a") as logs:
        logs.write("%s      %s" % (time.asctime(time.localtime(time.time())),
                                   "Calculating final position..."))

    '''Final prediction variables'''
    ORI_go_range = list()
    TER_go_range = list()

    # Calculates maximum expected difference between ORI and TER
    max_perc_genome = round(sequence_length * 0.65)
    min_perc_genome = int(sequence_length * 0.35)

    # Interval size
    intsize = 250

    # Add final prediction to file. 2 TERs if linear.
    if linear:
        with open(csv_file, mode='a') as results:
            teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            teritori_writer.writerow([""])
            teritori_writer.writerow(["FINAL PREDICTION:"])
            teritori_writer.writerow(["", "ORI", "p-val\n(ori)", "TER 1", "TER 2", "p-val\n(ter)", "Comment"])
    else:
        with open(csv_file, mode='a') as results:
            teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            teritori_writer.writerow([""])
            teritori_writer.writerow(["FINAL PREDICTION:"])
            teritori_writer.writerow(["", "ORI", "p-val\n(ori)", "TER", "p-val\n(ter)", "Comment"])

    fp.combine_all(ori_rrna_range, ori_dnaa_range, ori_go_range, dnaa_max_pos,
                   ORI_gc, ORI_ta, p_ori_gc, p_ori_ta, p_ori_go, ter_rrna_range,
                   ter_dif_range, ter_go_range, dif_max_pos, TER_gc, TER_ta,
                   p_ter_gc, p_ter_ta, p_ter_go, alpha, csv_file, sequence_length,
                   av_diff_gc, av_diff_ta, linear, args.cm, args.gc, args.all, args.go)

    # Final prediction finished
    with open(log_file, "a") as logs:
        logs.write("%s" % "Done! \n")

    """-----------------------------------------------------------------------------------------------------------------
    ----------------------------------------------------PLOT------------------------------------------------------------
    -----------------------------------------------------------------------------------------------------------------"""
    fig_title = name_species
    if args.graph:
        with open(log_file, "a") as logs:
            logs.write("%s      %s" % (time.asctime(time.localtime(time.time())),
                                       "Creating plot..."))
        if args.output:
            title = args.output

        final_result = list()
        with open(csv_file, 'r') as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                final_result.append(row)
        csvFile.close()

        fig = plt.figure()
        sub = fig.add_subplot(111)

        '''If all is chose, motifs are visualized'''
        if args.all or (args.gc and args.cm):
            for i in dnaa_sorted:
                if dnaa_sorted[i][0] > dnaa_sorted[i][1]:
                    x = list(range(dnaa_sorted[i][1], sequence_length)) + \
                        list(range(0, dnaa_sorted[i][0]))
                else:
                    x = list(range(dnaa_sorted[i][0], dnaa_sorted[i][1]))
                y = [0 for x in range(len(x))]
                if dnaa_sorted[i][2] == "+":
                    sub.plot(x, y, 'b>')
                elif dnaa_sorted[i][2] == "-":
                    sub.plot(x, y, 'b<')

            for i in dif_sorted:
                if dif_sorted[i][0] > dif_sorted[i][1]:
                    x = list(range(dif_sorted[i][1], sequence_length)) + \
                        list(range(0, dif_sorted[i][0]))
                else:
                    x = list(range(dif_sorted[i][0], dif_sorted[i][1]))
                y = [1 for x in range(len(x))]
                if dif_sorted[i][2] == "+":
                    sub.plot(x, y, 'r>')
                elif dif_sorted[i][2] == "-":
                    sub.plot(x, y, 'r<')

            for i in rrnas:
                x = list(range(i[0], i[1]))
                y = [0.5 for x in range(len(x))]
                if i[2] == 1:
                    sub.plot(x, y, 'm>')
                elif i[2] == -1:
                    sub.plot(x, y, 'm<')

        '''If go is chosen, go is plotted.'''
        if args.go and not args.all and not args.cm and not args.gc:
            x_go = np.arange(len_data_plot)
            sub.plot(x_go, normalized_go, color='black', linewidth=2)

        '''If gc skew or all is chosen'''
        if args.gc or args.all:
            x = x_perfect_gc
            sub.plot(x, gc_normalized, color='black', linewidth=2)
            sub.plot(x, ta_normalized, color='darkblue', linewidth=2)

        plt.suptitle(fig_title)

        if args.all or args.gc or args.cm:
            plt.xlabel('Sequence position')
        elif args.go and not args.all and not args.gc and not args.cm:
            plt.xlabel('Gene number')

        if args.all or (args.gc and args.cm and args.go) or (args.gc and args.cm):
            black_patch = mpatches.Patch(color='black', label='GC-skew')
            dark_patch = mpatches.Patch(color='darkblue', label='TA-skew')
            blue_patch = mpatches.Patch(color='blue', label='dnA boxes')
            red_patch = mpatches.Patch(color='red', label='dif motifs')
            magenta_patch = mpatches.Patch(color='magenta', label='rRNAs')
            sub.legend(handles=[black_patch, dark_patch, blue_patch, red_patch, magenta_patch], loc='upper center',
                       bbox_to_anchor=(0.5, -0.05), shadow=True, ncol=5)
        elif args.go and not args.gc and not args.all and not args.cm:
            if best_ori == "cum-":
                labletext = "Gene orientation (cumulative)"
            elif best_ori == "sumdiff+":
                labletext = "Gene orientation (sumdiff)"

            black_patch = mpatches.Patch(color='black', label='Gene-orientation')
            sub.legend(handles=[black_patch], loc='upper center',
                       bbox_to_anchor=(0.5, -0.05), shadow=True, ncol=1)
        elif args.gc and not args.go and not args.all and not args.cm:
            black_patch = mpatches.Patch(color='black', label='GC-skew')
            dark_patch = mpatches.Patch(color='darkblue', label='TA-skew')
            sub.legend(handles=[black_patch, dark_patch], loc='upper center',
                       bbox_to_anchor=(0.5, -0.05), shadow=True, ncol=3)
        elif args.gc and args.go:
            black_patch = mpatches.Patch(color='black', label='GC-skew')
            dark_patch = mpatches.Patch(color='darkblue', label='TA-skew')
            sub.legend(handles=[black_patch, dark_patch], loc='upper center',
                       bbox_to_anchor=(0.5, -0.05), shadow=True, ncol=2)
        TER = TER_1 = TER_2 = 0
        p_ori = p_ter = 0.0

        ORI = final_result[-1][1]
        if ORI.isdigit():
            ORI = int(ORI)
            if final_result[-1][2] == "":
                p_ori = '---'
            else:
                p_ori = str(final_result[-1][2])

            sub.axvline(ORI, linestyle='--', color='grey')
        else:
            p_ori = '---'

        if not args.cm:
            if linear:
                len(final_result)
                TER_1 = final_result[-1][3]
                TER_2 = final_result[-1][4]
                print(TER_1, TER_2)
                if TER_1.isdigit() and TER_2.isdigit():
                    TER_1 = int(TER_1)
                    TER_2 = int(TER_2)

                    if final_result[-1][5] == "":
                        p_ter = '---'
                    else:
                        p_ter = str(final_result[-1][5])

                    sub.axvline(TER_1, linestyle='--', color='grey')
                    sub.axvline(TER_2, linestyle='--', color='grey')
                else:
                    p_ter = '---'

                sub.annotate('ORI:' + str(ORI) + ', p-val: ' + p_ori +
                             '          TER:' + str(TER_1) + ' & ' + str(TER_2) + ', p-val: ' + p_ter,
                             xy=(0.07, 1.02), xycoords='axes fraction')
            elif not linear:
                TER = final_result[-1][3]
                if TER.isdigit():
                    TER = int(TER)
                    if final_result[-1][4] == "":
                        p_ter = '---'
                    else:
                        p_ter = str(final_result[-1][4])

                    sub.axvline(TER, linestyle='--', color='grey')
                else:
                    p_ter = '---'

                sub.annotate('ORI:' + str(ORI) + ', p-val: ' + p_ori + '        TER:' + str(TER) + ', p-val: ' + p_ter,
                             xy=(0.1, 1.02), xycoords='axes fraction')

        if args.all or args.gc or args.go or (args.cm and args.go and args.gc) or (args.go and args.gc) \
            or (args.gc and args.cm):
            if args.output:
                plt.savefig(inner_path + "/" + args.output + ".png", format="png")
            else:
                plt.savefig(inner_path + "/" + species + ".png", format="png")

    with open(log_file, "a") as logs:
        logs.write("%s" % "Done! \n\n")

    '''-----------------------------------------terITori finished----------------------------------------------------'''

    with open(log_file, "a") as logs:
        logs.write("%s      %s" % (time.asctime(time.localtime(time.time())),
                                   "terITori successful!"))


if __name__ == "__main__":
    main()