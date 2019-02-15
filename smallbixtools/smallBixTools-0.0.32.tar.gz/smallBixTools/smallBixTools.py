import tempfile
import subprocess
from itertools import groupby
from operator import itemgetter
import sys
import os
from Bio import SeqIO
import operator
import hashlib
from Bio import pairwise2
from collections import defaultdict
import pandas as pd

__author__ = "David Matten"
__credits__ = ["David Matten", "Colin Anthony", "Carolyn Williamson"]
__license__ = "GPL"
__maintainer__ = "David Matten"
__email__ = "david.matten@uct.ac.za"
__status__ = "Development"


def extract_seqs_not_in_csv_from_fasta(csv_fn, fasta_fn, out_fn):
    """
    Function to extract sequences from a fasta file which do NOT have their sequence id in a .csv file.
    Only exact matches are considered.
    All seqids which are in the .fasta input, and NOT described in the .csv file, are written to the out_fn in .fasta
    format.
    This function was created for use with blast results for fasta file, where not every sequence will have a blast
    result - and we want to find those which don't.

    :param csv_fn: Csv full path and filename. .csv file has no headings. only a single column.
    :param fasta_fn: The input .fasta file which is used in conjunction with the specified csv_fn. Sequence ids
                     must match exactly between this and the .csv
    :param out_fn: Writes sequences to this output .fasta file, which do not have their sequence id included in the
                   input .csv file
    :return:  No return. stdout is written to. out_fn is written to.
    """
    # if os.path.exists(out_fn):
    #     print("The output file already exists and would be destroyed if we continued. Exiting now to save from "
    #           "destructive behaviour.")
    #     raise IOError
    dct = fasta_to_dct(fasta_fn)
    df = pd.read_csv(csv_fn, header=None)
    csv_seqids = df[0].tolist()

    in_fasta_not_in_csv = []
    for seqid in dct.keys():
        if seqid not in csv_seqids:
            in_fasta_not_in_csv.append(seqid)
    not_in_csv_dct = {}
    for seqid in in_fasta_not_in_csv:
        not_in_csv_dct[seqid] = dct[seqid]

    dct_to_fasta(not_in_csv_dct, out_fn)
    print("Found {} sequences in the fasta file which were not in the .csv file. "
          "They have been written to: {}".format(len(not_in_csv_dct), out_fn))


def extract_seqs_in_csv_from_fasta(csv_fn, fasta_fn, out_fn):
    """
    Function to extract sequences from a fasta file based on their sequence id - specified in a .csv file.
    Only exact matches will be collected.
    All seqids in the .csv file which are not found will be printed to stdout with an error message.

    :param csv_fn: Csv full path and filename. .csv file has no headings. only a single column.
    :param fasta_fn:
    :param out_fn: the output fasta file destined to contain the sequences described in the input .csv file.
    :return: No return. Stdout is written to.
    """
    if os.path.exists(out_fn):
        print("The output file already exists and would be destroyed if we continued. Exiting now to save from "
              "destructive behaviour.")
        raise IOError
    dct = fasta_to_dct(fasta_fn)
    df = pd.read_csv(csv_fn, header=None)
    seqids = df[0].tolist()

    sampled_dct = {}

    not_found = []
    for seqid in seqids:
        if seqid in dct.keys():
            sampled_dct[seqid] = dct[seqid]
        else:
            not_found.append(seqid)
    if len(not_found) > 0:
        print("These seqids were not found")
        print(not_found)

    # write out the sampled sequences to the new fasta file
    dct_to_fasta(sampled_dct, out_fn)


def haplo_extract(haplo_fasta, haplo_log, recreated_fasta=None):
    """
    Input is a haplotyped fasta file, and its corresponding haplotype log file created by the sister method:
    "haplotype_compress"

    :param haplo_fasta: A fasta file. Representative sequences of this file are shown in the log as having other exact
    matching sequences.
    :param haplo_log: The log file which keeps track of which sequence ids had the exact same sequence in the original
    fasta file
    :param recreated_fasta: The output path to where the expanded fasta file should go.
    :return: Returns a none if no errors. raises errors if they occur.
    """

    # if we didn't get a name for the outfile, lets make one.
    if not recreated_fasta:
        recreated_fasta = os.path.splitext(haplo_fasta)[0] + "_expanded.fasta"
    # Make sure the filename doesn't already exist. Don't want to over wsrite something.
    if os.path.exists(recreated_fasta):
        print("Output recreated full fasta file already exists: {}".format(recreated_fasta))
        print("Please remove this file or specify a path where it doesn't exist.\nNow exiting.")
        sys.exit()

    # make a dictionary of the fasta file, and a dict to collect the expanded set
    haplo_dct = fasta_to_dct(haplo_fasta)
    expanded_dct = haplo_dct.copy()


    # step over the log csv, adding to the expanded dictioary.
    try:
        df = pd.read_csv(haplo_log)

        for haplo_seqid, haplo_seq in haplo_dct.items():  # these seqids have _0.18 type frequencies appended to seqids
            # get all the seqids from the csv file which have this as their "Representative_seqid"
            haplo_seqid_without_freq = haplo_seqid[:haplo_seqid.rfind("_")]
            selection = df[df["Representative_seqid"] == haplo_seqid_without_freq]
            selection_expand_seqids = selection["seq_with_same_seq"].values
            for seqid_to_include in selection_expand_seqids:
                expanded_dct[seqid_to_include] = haplo_seq
    except Exception as e:
        print(e)
        raise e


    # step over the log csv, adding to the expanded dictionary.
    # try:
    #     df = pd.read_csv(haplo_log)
    #     print(df)
    #     for expand_seqid in df["seq_with_same_seq"].values:
    #         representative_seqid = df[df["seq_with_same_seq"] == expand_seqid]["Representative_seqid"].values[0]
    #         # print(representative_seqid)
    #         # r = input("Continue?")
    #         representative_seq = haplo_dct[representative_seqid]
    #         expanded_dct[expand_seqid] = representative_seq
    #
    #     # for representative_seqid in haplo_dct.keys():
    #     #     print("representative_seqid: ", representative_seqid)
    #     #     grouped_seqids = df[df["Representative_seqid"] == representative_seqid].values
    #     #
    #     #     print(f"There are {len(grouped_seqids)} seqids in this group.")
    #     #     print("they are: ", grouped_seqids)
    #     #     for add_me_seqid in grouped_seqids:
    #     #         print(add_me_seqid)
    #     #         expanded_dct[add_me_seqid] = haplo_dct[representative_seqid]
    #     #     print(f"expanded dict is now {len(expanded_dct)} items long.")
    #     #     r = input("Continue?")
    # except Exception as e:
    #     print(e)
    #     raise e

    # write expanded dictionary to fasta file
    try:
        dct_to_fasta(expanded_dct, recreated_fasta)
    except Exception as e:
        print(e)
        raise e

    return None


def compress_align_expand_macse(in_fasta, out_fasta, macse_location=None):
    """
    takes a fasta file.
    haplotypes it.
    calculates an alignment with macse.
    expands back up to the original file number of sequences.

    :return: no return.
    """
    if macse_location is None:
        macse_location = "/home/dave/Software/macse/macse_v2.03.jar"
        if not os.path.exists(macse_location):
            print("Macse can't be found here: {}"
                  "\nAnd you didn't tell us where it is.\nNow exiting".format(macse_location))
            sys.exit()

    defult_tmp_dir = tempfile._get_default_tempdir()

    out_log_fn = os.path.join(defult_tmp_dir, next(tempfile._get_candidate_names()))
    compressed_fasta_to_align = os.path.join(defult_tmp_dir, next(tempfile._get_candidate_names()))

    # haplotype file to reduce size
    haplotype_compress(in_fasta, out_log_fn, compressed_fasta_to_align)

    aligned_compressed = os.path.join(defult_tmp_dir, next(tempfile._get_candidate_names()))

    # perform the alignment
    cmd = "java -jar {} -prog alignSequences -seq {} -out_NT {}".format(macse_location,
                                                                        compressed_fasta_to_align,
                                                                        aligned_compressed)
    subprocess.call(cmd, shell=True)

    # expand the file back up to full size
    haplo_extract(aligned_compressed, out_log_fn, out_fasta)

    # clean up afterwards.
    os.remove(out_log_fn)
    os.remove(compressed_fasta_to_align)
    os.remove(aligned_compressed)


def haplotype_compress(in_fasta, out_log, out_fasta=None):
    """
    Input is a fasta file.
    All the entries with the same sequence are collapsed and have a single representative in the output. The
    representative name is chosen at random from within those members of the cluster.
    A log is written, tracking which sequences went into each output cluster.

    Calculates the frequency of the haplotype within the file, and appends this to the sequence id, trailing an
    underscore. A 12 percent frequency is given as: _0.12, 100 percent is _1.0

    This method has a sister function: haplo_extract, which will take the fasta file and log created by this function,
    and re-create the original input.

    :param in_fasta: input fasta file to be haplotyped.
    :param out_log: The sequences which are chosen to be representatives and which sequences belong to this cluster
    are written to this file.
    :param out_fasta: The output fasta file, which is haplotyped.
    :return: Returns a none if no errors. raises errors if they occur.
    """

    if not out_log:
        out_log = os.path.splitext(in_fasta)[0] + "_haplo_log.csv"
    if not out_fasta:
        out_fasta = os.path.splitext(in_fasta)[0] + "_haplotyped.fasta"
    # Make sure they don't already exist. Don't want to over write something.
    if os.path.exists(out_fasta):
        print("Output path already exists: {}".format(out_fasta))
        print("Please specify a path which does not exist.\nNow exiting.")
        sys.exit()
    if os.path.exists(out_log):
        print("Output haplo log file already exists: {}".format(out_log))
        print("Please remove this file or specify a path where it doesn't exist.\nNow exiting.")
        sys.exit()

    # make a dictionary of the fasta file.
    in_dct = fasta_to_dct(in_fasta)

    # create a reversed dictionary, keeping track of seqids with the same seq.
    haplo_rev_dct = {}  # this will have sequences as keys, and seqids as values. both strings.
    seqIDS_with_same_seq = {}  # this will have seqids as keys, and lists of seqids as values. string:[list, of-strings]

    for seqid, seq in in_dct.items():
        if seq in haplo_rev_dct.keys():  # we already have one copy of this sequence
            # add the seqid to the seqIDS_with_same_seq dictionary
            representative_seqid = haplo_rev_dct[seq]
            seqIDS_with_same_seq[representative_seqid].append(seqid)
        else:  # this is the first time we are seeing this sequence.
            # add the seqid to the seqIDS_with_same_seq dictionary, as a new entry.
            seqIDS_with_same_seq[seqid] = []
            # add an entry to the haplo_rev_dct
            haplo_rev_dct[seq] = seqid

    # re-reverse the dictionary to get it back to seqid: seq
    haplo_dict = reverse_dictionary(haplo_rev_dct)

    dct_with_freqs = {}
    # Add the percentage abundance to the seqids.
    total_seq_count = len(in_dct)
    for haplo_seqid, haplo_seq in haplo_dict.items():
        # how many seqs does this one represent?
        this_seq_reps_n = len(seqIDS_with_same_seq[haplo_seqid])
        this_prcnt_abund = this_seq_reps_n / total_seq_count * 100
        new_seqid = haplo_seqid + f"_{this_prcnt_abund}"
        dct_with_freqs[new_seqid] = haplo_seq

    # write the haplotyped dictionary to file.
    try:
        dct_to_fasta(dct_with_freqs, out_fasta)
    except Exception as e:
        print(e)
        raise e

    # write the "log" to file - which sequences are being represented by which other ones.
    try:
        with open(out_log, "w") as fw:
            fw.write("Representative_seqid,seq_with_same_seq\n")
            for rep_seqid, SeqIDS_list in seqIDS_with_same_seq.items():
                for sub_seqid in SeqIDS_list:
                    fw.write(f"{rep_seqid},{sub_seqid}\n")
    except Exception as e:
        print(e)
        raise e

    print(f"Completed compressing to haplotypes. .fasta file:{out_fasta}, log file: {out_log}")
    return None


def cluster_by_pattern(fasta_filename):

    def get_freqs(s):
        total_chars = len(s)
        freq_dct = defaultdict(int)
        for char in s:
            freq_dct[char] += 1
        for k in freq_dct.keys():
            freq_dct[k] = freq_dct[k] / total_chars
        return freq_dct

    print("clusters by patterns found in the fasta file.")
    dct = fasta_to_dct(fasta_filename)
    seqs = list(dct.values())
    print(seqs)

    sequencing_platforms_lookups = {"PID_illumina_miseq": {"seq_error_rate": 0.001, },
                                    "PID_pacbio": {},
                                    "pacbio": {},
                                    }

    threshold = 0.1

    # decide which sites are informative here - based on if any character crosses a frequency threshold.
    informative_sites = []
    for i in range(len(seqs[0])):
        pos_chars = [s[i] for s in seqs]
        this_is_an_informative_site = False
        if len(set(pos_chars)) > 1:
            print(pos_chars)
            print(i)
            pos_freqs = get_freqs(pos_chars)
            freqs = list(pos_freqs.values())
            for freq in freqs:
                if freq > threshold:
                    this_is_an_informative_site = True
        if this_is_an_informative_site:
            informative_sites.append(i)

    print("We found the following informative sites: ")
    print(informative_sites)


    # for these informative sites, we want to find the patterns across the sequencs.
    all_patterns = []
    for seq in seqs:
        pattern = ""
        for inf_site in informative_sites:
            pattern += seq[inf_site]
        all_patterns.append(pattern)
    print(all_patterns)
    all_patterns = list(set(all_patterns))
    print("The patterns found are: {}".format(all_patterns))

    # establish cluster numbers for these patterns. "AT" is cluster 1. "TA" is cluster 2. etc.
    ptrn_dct = {}
    for i, ptrn in enumerate(list(set(all_patterns))):
        ptrn_dct[ptrn] = i

    # for each sequence, decide which cluster it belongs to.
    for seq in seqs:
        print("Seq: {}".format(seq))
        this_seq_pattern = ""
        for inf_site in informative_sites:
            this_seq_pattern += seq[inf_site]
        this_cluster = ptrn_dct[this_seq_pattern]
        print("assigned to cluster: {}".format(this_cluster))


def test_cmd_present(cmd):
    '''
    This tests if cmd is executable. This can be used to check if some
    software is available at the given path and executable on a machine.
    For example, if you want to use mafft, and the user says its located at:
    "/opt/not_really_here/mafft", we an test and return False.
    :param cmd: the command to test.
    :return: Bool. True if command is available at path and executable. False if not.
    '''
    from shutil import which
    return which(cmd) is not None


def find_start(s):
    '''
    Given a string, find the position of the first character which is not a gap "-" hyphen.
    :param s: String to search for the first non gap character in
    :return: position of first non-gap character
    '''
    import re
    s = s.upper()
    start = re.search(r'[^-]', s).start()
    return start


def find_end(s):
    '''
    Given a string, s, find the position of the last character which is not a gap "-" hyphen.
    :param s: String to search for the last non gap character in
    :return: position of last non-gap character
    '''
    import re
    # reverse the string.
    s = s[::-1]
    s = s.upper()
    # the last character which is not a gap is the first one in the reversed string.
    # get its position by taking length minus that number.
    end = len(s) - re.search(r'[^-]', s).start()
    return end


def combine_align_trim(align_to_me, fasta_file_to_be_added, out_file, mafft_call='mafft'):
    '''
    This method adds the second argument file (fasta_file_to_be_added) onto the first. It uses mafft add by default
    to align the second fasta file onto the first.
    Then finds the starting and ending positions of the sequences from the file specified in the arg "align_to_me",
    and trims ALL sequences to these starting and ending positions.
    :param align_to_me: This is the first source file to be aligned onto. The file which will be trimmed to. Typically
    This is a file with shorter reads.
    :param fasta_file_to_be_added:
    :param out_file: The path to the fasta file where results should be written. This file will be an aligned combined
                        version of the two other input source files.
    :param mafft_call: A non-required argument. How should we call mafft on this machine? Typical mafft installs allow
    for the default mafft call: "mafft"
    :return: No return.
    '''
    if not test_cmd_present(mafft_call):
        print("We require mafft to run this method. Please make sure it is installed, or specify how to run it on this"
              "machine. Get it from: https://mafft.cbrc.jp/alignment/software/")
    if not os.path.isfile(align_to_me):
        print("Specified file is not a file.")
        raise ValueError("Specified file is not a file. {}".format(align_to_me))
    if not os.path.isfile(fasta_file_to_be_added):
        print("Specified file is not a file.")
        raise ValueError("Specified file is not a file. {}".format(fasta_file_to_be_added))
    if os.path.isfile(out_file):
        print("The output file will be overwriten: {}".format(out_file))

    cmd = "{} --thread -1 --add {} {} > {}".format(mafft_call, align_to_me, fasta_file_to_be_added, out_file)
    try:
        subprocess.call(cmd, shell=True)
    except Exception as e:
        print(e)
        print("Error trying to call mafft to add the OGV sequences onto the existing NGS alignment., or removing or "
              "copying files.")
        raise

    align_to_me_dct = fasta_to_dct(align_to_me)
    aligned_dct = fasta_to_dct(out_file)
    if len(align_to_me_dct) == 0:
        print("Something went wrong. The file {} became empty.".format(align_to_me))
        raise ValueError("Something went wrong. The file {} became empty.".format(align_to_me))
    if len(aligned_dct) == 0:
        print("Something went wrong. The file {} became empty.".format(out_file))
        raise ValueError("Something went wrong. The file {} became empty.".format(out_file))

    starting_positions = [find_start(aligned_dct[k]) for k in align_to_me_dct.keys()]  # use the keys from the orig.
    # input, and the sequences from the aligned version - as they are the ones with the gaps we want to find.
    start_pos = int(min(starting_positions))
    ending_positions = [find_end(aligned_dct[k]) for k in align_to_me_dct.keys()]
    end_pos = int(max(ending_positions))
    print("The starting position found is: {}".format(start_pos))
    print("The ending position found is: {}".format(end_pos))
    print("Trimming to this region.")

    out_dct = fasta_to_dct(out_file)
    for k in out_dct.keys():
        out_dct[k] = out_dct[k][start_pos:end_pos]

    dct_to_fasta(out_dct, out_file)


def find_best_global_between_fastas(target_fn, query_fn, csv_out_fn):
    """
    For every sequence in the .fasta formatted query_fn, find the best matching sequence from the target_fn based on
    a global alignment from the BioPython package.
    :param target_fn: The fasta file to check against. Sequences from the query file will be searched against this file.
    :param query_fn: The file to check from. Each one of these sequences will have its best match in the target file
    searched for.
    :param csv_out_fn: Each sequence from the query file will have a single row in this csv file. Column 1 is the query
     seqid. Column 2 is the best found target seqid. Column 3 is an identity count.
    :return: No return. Writes output to csv_out_fn
    """
#    seq_align_call = "/home/dave/Software/seq-align/bin/needleman_wunsch"
    target_dct = fasta_to_dct(target_fn)
    query_dct = fasta_to_dct(query_fn)

    for query_seqid, query_seq in query_dct.items():
        for target_seqid, target_seq in target_dct.items():
            alignments = pairwise2.align.globalxx(query_seq, target_seq)
            print(len(alignments))
            print(alignments[0])

    # TODO complete. Writing out to csv.


def sanitize_fasta_seqids(infile, outfile, valid_chars):
    """
    Read a fasta formatted file. Remove all characters which are not in the valid_chars string.
    :param infile: input file name to check.
    :param outfile: output file name to write to.
    :param valid_chars: string of valid characters.
                        Typically one might use "{}{}".format(string.ascii_letters, string.digits)
    :return: No return. Writes to the outfile specified.
    """
    dct = fasta_to_dct(infile)
    new_dct = {}
    for k, v in dct.items():
        new_k = ""
        for char in k:
            if char in valid_chars:
                new_k += char
        if len(new_k) > 0:
            new_dct[new_k] = v
        else:
            print("If we remove all the illegal characters, there is nothing left to use as a sequence id.")
            raise Exception
    dct_to_fasta(new_dct, outfile)


def compare_seqs_of_fasta_files(fn1, fn2):
    """
    Compares the sequences of two fasta files. Does not compare seqids. Prints a list of the seqids for the sequences
    which are found in one fasta file, but not the other, for both comparison directions. Also returns this a tuple
    of lists.
    :param fn1: fasta file 1
    :param fn2: fasta file 1
    :return: returns a tuple of lists. ([in fn1 and not in fn2], [in fn2 and not in fn1], [in both])
    """
    dct1 = fasta_to_dct(fn1)
    dct2 = fasta_to_dct(fn2)
    all_fn1_seqs = list(dct1.values())
    all_fn2_seqs = list(dct2.values())
    print(all_fn1_seqs)
    in1_not_in2 = []
    in2_not_in1 = []
    in_both = []
    for seqid1, seq1 in dct1.items():
        if seq1 in all_fn2_seqs:
            in_both.append(seqid1)
        else:
            in1_not_in2.append(seqid1)
    for seqid2, seq2 in dct2.items():
        if seq2 not in all_fn1_seqs:
            in2_not_in1.append(seqid2)

    print("All sequences from file 1, which were not found in file 2, their sequence ids are: ")
    print(in1_not_in2)
    print("All sequences from file 2, which were not found in file 1, their sequence ids are: ")
    print(in2_not_in1)

    print("All sequences found in both file 1 and file 2, their sequence ids are: ")
    print(in_both)

    return in1_not_in2, in2_not_in1, in_both


def make_hash_of_seqids(src_fn, out_fn):
    """
    When calling mafft - sequence ids over 253 in length are truncated. This can result in non-unique ids if the first
    253 characters of the seqid are the same, with a difference following that.
    To get around this - we can has the sequence ids, and write a new .fasta file for mafft to work on, then
    translate the sequence ids back afterwards.

    This function does the hashing and writing to file.

    This is a sibling function to: unmake_hash_of_seqIDS

    Will raise an exception on error

    :param src_fn: the src file to operate on
    :param out_fn: an output file is produced, with the modified sequence ids.
    :return: returns a lookup dictionary for finding the new sequence id name. This dictionary can be used with the
    sibling function: "unmake_hash_of_seqIDS".
    """
    try:
        dct = fasta_to_dct(src_fn)
        new_dct = {}
        translation_dct = {}
        for k, v in dct.items():
            new_k = hashlib.md5(k.encode()).hexdigest()
            new_dct[new_k] = v
            translation_dct[k] = new_k
        dct_to_fasta(new_dct, out_fn)
    except Exception as e:
        print(e)
        raise

    return translation_dct


def unmake_hash_of_seqids(lookup_dict, src_fn, out_fn):
    """
    When calling mafft - sequence ids over 253 in length are truncated. This can result in non-unique ids if the first
    253 characters of the seqid are the same, with a difference following that.
    To get around this - we can has the sequence ids, and write a new .fasta file for mafft to work on, then
    translate the sequence ids back afterwards.

    This function does the translation back afterwards.

    This is a sibling function to: make_hash_of_seqIDS.

    Will raise an exception on error

    :param lookup_dict:
    :param src_fn:
    :param out_fn:
    :return: no return value.
    """
    try:
        dct = fasta_to_dct(src_fn) # the dictionary with hashed seqids.
        back_translated_dct = {} # the 'original' sequence ids are back.
        for old_k, hash_k in lookup_dict.items():
            back_translated_dct[old_k] = dct[hash_k]
        dct_to_fasta(back_translated_dct, out_fn)
    except Exception as e:
        print(e)
        raise


def compare_fasta_files(file1, file2, consider_gaps):
    """
    Compares two fasta files, to see if they contain the same data. The sequences must be named the same. We check if
    sequence A from file 1 is the same as sequence A from file 2.
    The order in the files does not matter.
    Gaps are considered.
    :param file1: first fasta file
    :param file2: second fasta file
    :param consider_gaps: bool value indicating if gaps should be considered or not. True means consider gaps. False
    means don't consider gaps. True: ATC-G  is not equal to ATCG.
    :return: True if the files contain the same data. False if the files contain different data.
    """
    dct1 = fasta_to_dct(file1)
    dct2 = fasta_to_dct(file2)

    if consider_gaps:
        for k in dct1.keys():
            dct1[k] = dct1[k].replace("-", "")
        for k in dct2.keys():
            dct2[k] = dct2[k].replace("-", "")

    for seqid, seq1 in dct1.items():
        if seqid not in dct2.keys():
            return False
        seq2 = dct2[seqid]
        if seq1 != seq2:
            return False
    return True


def countNinPrimer(primer_seq):
    """
    Motifbinner2 requires values to be specified for primer id length and primer length. Its tiresome to have to
    calculate this for many strings. So, I wrote this to help myself.
    An example of a primer sequence might be: NNNNNNNAAGGGCCAAAGGAACCCTTTAGAGACTATG
    And we would like to know how many N's there are, how many other characters there are, and what the combined
    total lenght is.
    :param primer_seq: the primer sequence to have calculations performed on.
    :return: nothing. prints to stdout are done.
    """
    n_count = primer_seq.count("N")
    other_count = primer_seq.count("A") + primer_seq.count("C") + primer_seq.count("G") + primer_seq.count("T")
    print("N: {}".format(n_count))
    print("!N: {}".format(other_count))
    print("total: {}".format(n_count + other_count))
    min_score = 0.85 * (n_count + other_count)
    print("suggested min score: {}".format(min_score))


def convert_count_to_frequency_on_fasta(source_fasta_fn, target_fasta_fn):
    """
    when running vsearch as such:
    vsearch --cluster_fast {} --id 0.97 --sizeout --centroids {}
    We get a centroids.fasta file with seqid header lines like:
    >ATTCCGGTATCT_9;size=1432;
    >CATCATCGTAAG_14;size=1;
    etc.
    This method converts those count values into frequencies.
    Notes: The delimiter between sections in the sequence id must be ";".
    There must be a section in the sequence id which has exactly: "size=x" where x is an integer.
    This must be surrounded by ;
    :param source_fasta_fn: the input fasta file. Full path required.
    :param target_fasta_fn: the output fasta file. Full path required. If this is the same as the input, the input will
                            be over-written.
    :return: No return value.
    """
    dct = fasta_to_dct(source_fasta_fn)
    total_count = 0
    for k in dct.keys():  # step over every sequence id, and tally up the total number of sequences in the orig. file.
        splt = k.split(";")
        for item in splt:
            if "size" in item:
                total_count += int(item.split("=")[1])
    dct2 = {}
    for k in dct.keys():  # step over each seqid, converting its count to a frequency, saving into a new dictionary.
        splt = k.split(";")
        new_k = ""
        for item in splt:
            if item == '':
                continue
            if "size" in item:
                new_k += "freq=" + str(int(item.split("=")[1]) / total_count) + ";"
            else:
                new_k += item + ";"
        new_k.replace(";;", ";")
        dct2[new_k] = dct[k]
    dct_to_fasta(dct2, target_fasta_fn)  # Write the new dictionary to the same filename which was fed into the
    print("Converted absolute counts to frequencies on file: {}".format(target_fasta_fn))


def py3_fasta_iter(fasta_name):
    """
    modified from Brent Pedersen: https://www.biostars.org/p/710/#1412
    given a fasta file. yield tuples of header, sequence
    :param fasta_name: The fasta formatted file to parse.
    """
    fh = open(str(fasta_name), 'r')
    faiter = (x[1] for x in groupby(fh, lambda line: line[0] == ">"))
    for header in faiter:
        # drop the ">"
        header_str = header.__next__()[1:].strip()
        # join all sequence lines to one.
        seq = "".join(s.strip() for s in faiter.__next__())
        yield (header_str, seq)


def py2_fasta_iter(fasta_name):
    """
    from Brent Pedersen: https://www.biostars.org/p/710/#1412
    given a fasta file. yield tuples of header, sequence
    :param fasta_name: The fasta formatted file to parse.
    """
    fh = open(fasta_name)
    faiter = (x[1] for x in groupby(fh, lambda line: line[0] == ">"))
    for header in faiter:
        # drop the ">"
        header = header.next()[1:].strip()
        # join all sequence lines to one.
        seq = "".join(s.strip() for s in faiter.next())
        yield header, seq


def try_call(cmd, logging=None):
    """
    Try a subprocess call on a string cmd. Raises an error on exceptions. Logging is allowed.
    :param cmd: The string to try calling.
    :param logging: Can optionally take a logging arg. This is the default logging for Python.
    :return: Returns the return code from calling the string command.
    """
    rtrn_code = None
    try:
        captured_stdout = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        if logging != None:
            logging.info(captured_stdout)
    except Exception as e:
        if logging != None:
            logging.warning(e)
        print(e)
        raise
    return rtrn_code


def size_selector(in_fn, out_fn, min, max):
    dct = fasta_to_dct(in_fn)
    dct2 = {}
    for k, v in dct.items():
        if len(v) < min:
            continue
        if len(v) > max:
            dct2[k] = v[:max]
        else:
            dct2[k] = v
    dct_to_fasta(dct2, out_fn)


def split_file_into_timepoints(infile, outpath=None, fields=3, delim="_"):
    """
    Takes a fasta file as input, and splits into multiple fasta files each containing sequences for a single timepoint.

    :param infile: A fasta file, containing sequences for mulitple timepoints. This file will not be modified.
    :param outpath: If outpath is specified, will write outfiles here. If not specified - will write output files
                    to the same place as the input file.
    :param fields: The number of fields to use, delimited by the specified delimiter, to group sequences together.
    eg: fields =3, using underscores. "CAP123_2000_004wpi_blaaa...."
    All sequences starting with "CAP123_2000_004wpi" will be written to the same output file.
    :param delim: The delimiter to use to count fields.
    :return:
    """
    print("Splitting file into multiple time points.")
    dct = fasta_to_dct(infile)
    dct_of_timepoints = {}
    for seqid, seq in dct.items():
        seqid_split = seqid.split(delim)
        file_allocation = delim.join(seqid_split[:fields])  # joins the first X fields of the seqids, to
                                                            # decide which group this sequence belongs to.
        if file_allocation not in dct_of_timepoints.keys():
            dct_of_timepoints[file_allocation] = {seqid: seq}
        else:
            dct_of_timepoints[file_allocation][seqid] = seq
    print(len(dct_of_timepoints))
    if outpath is None:
        outpath = os.path.split(infile)[0]
    for grouping, dct_to_write in dct_of_timepoints.items():
        this_out_fn = os.path.join(outpath, grouping + ".fasta")
        dct_to_fasta(dct_to_write, this_out_fn)
    print("Wrote split files ({} files) to {}.".format(len(dct_of_timepoints), outpath))


def own_cons_maker(infile):
    dct = fasta_to_dct(infile)
    seqs = [v for k, v in dct.items()]
    cons = ""
    for i in range(len(seqs[0])):
        pos = {}
        for k in range(len(seqs)):
            letter = seqs[k][i]
            if letter in pos.keys():
                pos[letter] += 1
            else:
                pos[letter] = 1
        if sys.version_info[0] < 3:
            cons += max(pos.iteritems(), key=operator.itemgetter(1))[0]
        elif sys.version_info[0] >= 3:
            cons += max(pos.items(), key=operator.itemgetter(1))[0]
    return cons


def build_cons_seq(infile):
    # https://www.biostars.org/p/14026/
    from Bio import AlignIO
    from Bio.Align import AlignInfo

    alignment = AlignIO.read(open(infile), "fasta")
    summary_align = AlignInfo.SummaryInfo(alignment)
    consensus = summary_align.dumb_consensus()
    return consensus


def auto_duplicate_removal(in_fn, out_fn):
    """
    FOCUS ON THE SEQIDS LINKED TO THE SEQUENCES.
    Attempts to automatically remove duplicate sequences from the specifed file. Writes results to output file
    specified. Uses BioPython SeqIO to parse the in file specified. Replaces spaces in the sequence id with underscores.
    Itterates over all sequences found - for each one, checking if its key already exists in an accumulating list, if it
    does: check if the sequence which each specifies is the same. If they have the same key, and the same sequence -
    then keep the second instance encountered. Once the file has been parsed - write to the output file specified all
     sequences found which
    Will raise an exception if an error occurs during execution.
    :param in_fn: The file to check. Full path to file is required.
    :param out_fn: Output
    :return: No return value.
    """
    print("Trying to automatically remove duplicate sequences from the in file: %s" %in_fn)
    try:
        dct = {}
        for sequence in SeqIO.parse(open(in_fn), "fasta"):
            new_key = sequence.description.replace(" ", "_")
            new_seq = str(sequence.seq)

            if new_key in dct.keys():
                print("Duplicate sequence ids found. seq_id: %s" %new_key)
                print("Checking if the sequences are the same...")
                if new_seq == dct[new_key]:
                    print("The sequences are the same, the keys are the same. We update the record for this duplicate.")
                elif new_seq != dct[new_key]:
                    print("The sequences are NOT the same, but they have the same sequence id. Cannot auto resolve.")
                    print("Exiting...")
                    sys.exit()
            dct[new_key] = str(sequence.seq)
        dct_to_fasta(dct, out_fn)
        return True
    except Exception as e:
        print(e)
        print("Failed to auto remove duplicates")
        raise


def duplicate_sequence_removal(in_fn, out_fn):
    '''
    FOCUS ON THE SEQUENCES ONLY. We don't consider links to the seqids in this method.
    Attempts to automatically remove duplicate sequences from the specifed file. Writes results to specified output
    file. Replaces spaces in the sequence id with underscores.
    Itterates over all sequences found - for each one, checking if it already exists in an accumulating dictionary.
    If it does: Update the key to the new key.
    Once the file has been parsed - write to the output file specified all sequences found.
    Will raise an exception if an error occurs during execution.
    :param in_fn: The file to check. Full path to file is required.
    :param out_fn: Output file path. Full path is required.
    :return: No return value.
    :param in_fn:
    :param out_fn:
    :return: No return
    '''
    dct = fasta_to_dct(in_fn)
    reversed_dct = {}
    squashed_dct = {}
    if duplicate_sequence_in_fn(in_fn):
        # True means: "Yes - we found duplicates"... Lets squash them down. effectively haplotype them.
        reversed_dct = reverse_dictionary(dct)
        squashed_dct = reverse_dictionary(reversed_dct)
        dct_to_fasta(squashed_dct, out_fn)
    else:
        # otherwise, just write out the infile to the outfile path.
        dct_to_fasta(dct, out_fn)


def duplicate_sequence_in_fn(in_fn):
    '''
    Takes a fasta formatted filename, reads it in, checks if there are duplicate sequences found in the file.
    Will raise errors.
    Checks if the length of the set of the sequences is equal to the length of a list of all the sequence values.
    If they are different lengths, then there are duplicates, and True is returned.- "True, there are duplicates"
    If they are not different lengths, then there are NO duplicates, and False is returned.: "False, there are NO duplicates"
    :param in_fn: The filename of the fasta file to check
    :return: True if duplicate sequences are found. False if no duplicate sequences are found.
    '''
    try:
        dct = fasta_to_dct(in_fn)
    except Exception as e:
        print(e)
        raise e
    if len(set(dct.values())) != len(dct.values()):
        return True
    else:
        return False


def hyphen_to_underscore_fasta(fn, out_fn):
    print("Cleaning a fasta file to have underscores in the sequence names, not hyphens.")
    dct = fasta_to_dct(fn)
    cleaned_dct = {}
    for key, value in dct.items():
        cleaned_key = key.replace("-", "_")
        cleaned_dct[cleaned_key] = value
    dct_to_fasta(cleaned_dct, out_fn)
    print("Finished cleaning. Wrote to file: %s" %out_fn)


def customdist(s1, s2):
    """
    A distance measure between two iterables. Typically meant for DNA sequence strings. eg: ATCG and A-CG would be a
    distance of 1. ATTCG to A--CG distance 1 also.
    Gap scores: gap opening: -1. gap extension: penalty of zero. This means any length gap counts the same as a 1 length gap.
    A second disconnected gap counts as an additional -1.
    :param s1: first iterable to compare.
    :param s2: second iterable to compare.
    :return: returns the distance. int.
    """
    assert len(s1) == len(s2)
    dist = 0
    for c1, c2 in zip(s1, s2):
        if c1 != c2:
            dist += 1
    diff = 0
    for i in range(len(s1)-1):
        if s1[i] != s2[i]:
            if (s1[i] == "-" and s1[i+1] == "-" and s2[i+1] != "-") or (s2[i] == "-" and s2[i+1] == "-" and s1[i+1] != "-"):
                diff += 1
    return (dist-diff)


def find_duplicate_ids(fn):
    # and squash if safe
    dct = {}
    for seq in SeqIO.parse(open(fn), "fasta"):
        seq_id = str(seq.description)
        if seq_id in dct.keys():
            dct[seq_id] += 1
        else:
            dct[seq_id] = 1
    for k, v in dct.items():
        if v != 1:
            print("%s was found %s times." %(k, v))
#    dct2 = {}
#    safe = []
#    for k, v in dct.items():
#        if v != 1:
#            seqs = []
#            for seq in SeqIO.parse(open(fn), "fasta"):
#                if str(seq.description) == k:
#                    seqs.append(str(seq.seq).replace("-", ""))
#            if len(list(set(seqs))) == 1:
#                print k
#                print "safe to squash..."
#                safe.append(k)
#    final_dct = {}
#    for seq in SeqIO.parse(open(fn), "fasta"):
#        seq_id = str(seq.description)
#        if seq_id in final_dct.keys():
#            if seq_id in safe:
#                final_dct[seq_id] = str(seq.seq)
#            else:
#                print(seq_id)
#                raw_input("rawr")
#        else:
#            final_dct[seq_id] = str(seq.seq)
#    return final_dct


def reverse_dictionary(d):
    '''
    Creates a reversed dictionary. Keys become values, and values become keys.
    eg: d = {"A": 'a', "B": 'b'}
    becomes:
    {"a": 'A', "b": 'B'}
    If two keys have the same value, only one key is kept in the reversed dictionary.
    :param d: The dictionary to be reversed.
    :return: A reversed dictionary.
    '''
    d2 = {}
    for k, v in d.items():
        d2[v] = k
    return d2


def dct_to_fasta(d, fn):
    """
    :param d: dictionary in the form: {sequence_id: sequence_string, id_2: sequence_2, etc.}
    :param fn: The file name to write the fasta formatted file to.
    :return: Returns True if successfully wrote to file.
    """
    fileName, fileExtension = os.path.splitext(fn)
#    try:
#        assert fileExtension.lower() in [".fasta", ".fa", ".fas", ".fna", ".ffn", ".faa", ".frn"]
#    except AssertionError:
#        _, _, tb = sys.exc_info()
#        traceback.print_tb(tb) # Fixed format
#        tb_info = traceback.extract_tb(tb)
#        filename, line, func, text = tb_info[-1]
#        print(('An error occurred on line {} in statement {}'.format(line, text)))
#        exit(1)
    try:
        with open(fn, "w") as fw:
            for k, v in list(d.items()):
                fw.write(">"+k+"\n"+v+"\n")
        return True
    except Exception as e:
        print(e)
        return False


def fasta_to_dct(fn):
    """
    Checks which version of Python is being used, calls the appropriate iterator.
    Spaces in the sequence ids are replaced with underscores.
    Duplicate sequence ids are not allowed. An error will be raised.
    :param fn: The fasta formatted file to read from.
    :return: A dictionary of the contents of the fasta file specified. The dictionary in the format:
             {sequence_id: sequence_string, sequence_id2: sequence_2, etc.}
    """
    dct = {}
    if sys.version_info[0] < 3:
        my_gen = py2_fasta_iter(fn)
    elif sys.version_info[0] >= 3:
        my_gen = py3_fasta_iter(fn)
    for k, v in my_gen:
        new_key = k.replace(" ", "_")
        if new_key in dct.keys():
            print("Duplicate sequence ids found. Exiting")
            raise KeyError("Duplicate sequence ids found")
        dct[new_key] = str(v).replace("~", "_")
    return dct


def hamdist(str1, str2):
    """
    Use this after aligning sequences.
    This counts the number of differences between equal length str1 and str2
    The order of the input sequences does not matter.
    :param str1: The first sequence.
    :param str2: The second sequence.
    :return: Returns an int count of the number of differences between the two input strings, considered per position.
    """
    return sum(el1 != el2 for el1, el2 in zip(str1, str2))


def normalized_hamdist(str1, str2):
    """
    Use this after aligning sequences.
    This counts the number of differences between equal length str1 and str2
    The order of the input sequences does not matter.
    :param str1: The first sequence.
    :param str2: The second sequence.
    :return: Returns a float value of the number of differences divided by the length of the first input argument.
    """
    return sum(el1 != el2 for el1, el2 in zip(str1, str2))/float(len(str1))


def find_ranges(data):
    """
    Find contiguous ranges in a list of numerical values.
    eg: data = [1,2,3,4,8,9,10]
        find_ranges(data) will return:
        [[1, 2, 3, 4], [8, 9, 10]]
    :param data: a list of numerical values. (eg: int, float, long, complex)
    :return: a list of lists, each is a contiguous list of values.
    """
    ranges = []
    for k, g in groupby(enumerate(data), lambda i_x:i_x[0]-i_x[1]):
        ranges.append(list(map(itemgetter(1), g)))
    for rng in ranges:
        if len(rng) == 1:
            ranges.remove(rng)
    return ranges


def get_regions_from_panel(in_fn, regions, wd, outfn):
    """
    Slices regions out of a fasta formatted file, joins them together, and writes the resulting fasta file to the given location.
    an example call might be: get_regions_from_panel("test.fasta", [[0, 10], [20, 30]], "/tmp", "outfile.fasta")
    which would, for each sequence in the input file: "test.fasta", take the region from 0 to 10 joined with the
    region from 20 to 30, and write the result to the file: "/tmp/outfile.fasta".
    :param in_fn: the source / input fasta formatted file.
    :param regions: a list of lists. each sub-list has a start and a stop value. these demote the "regions" to
    use / slice. eg: [[0, 10], [20, 30]].
    :param wd: the directory where the output file will be written to.
    :param outfn: the output file name.
    :return: no return.
    """
    p_dct = fasta_to_dct(in_fn)
    fw = open(os.path.join(wd, outfn), "w")
    for k, v in list(p_dct.items()):
        p_seq = v
        p_joined = ""
        for rgn in regions:
            p_joined += p_seq[rgn[0]:rgn[1]]
        fw.write(">"+k+"\n"+p_joined+"\n")
    fw.close()


def get_parent(tree, child_clade):
    """
    Not used. removing in next commit.
    :param tree:
    :param child_clade:
    :return:
    """
    node_path = tree.get_path(child_clade)
    return node_path[-2]


def trim_two_seqs_to_same_data(seq1, seq2):
    """
    takes two ALIGNED sequences as strings, and trims them to where they both have characters, ie: no gaps.
    ---------GATCGATGCTAGC-----
    CATTAGCGCGATCGATGCTAGC-----
    Should be trimmed to:
    GATCGATGCTAGC
    GATCGATGCTAGC
    All gaps within the sequences are kept.
    :param seq1: first string to trim.
    :param seq2: second string to trim.
    :return: (s1, s2) tuple of strings. s1 is seq1 trimmed, and s2 is seq2 trimmed - both to where both have data.
    """
    start = 0
    for c1, c2 in zip(seq1, seq2):
        if (c1 != '-') and (c2 != '-'):
            break
        else:
            start += 1

    rev_1, rev_2 = seq1[::-1], seq2[::-1]
    end = 0
    for c1, c2 in zip(rev_1, rev_2):
        if (c1 != '-') and (c2 != '-'):
            break
        else:
            end += 1
    end = len(seq1) - end

    trimmed1 = seq1[start:end]
    trimmed2 = seq2[start:end]

    return trimmed1, trimmed2


def main():
    print("Call to main in smallBixTools.py. Nothing to do in the main.")


if __name__ == "__main__":
    main()
