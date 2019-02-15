#!/usr/bin/env python
'''Split one or more fastq files based on barcode sequence.'''

from __future__ import print_function
from __future__ import division
import argparse
from collections import defaultdict
import codecs
import gzip
import io
import os
import re
import sys
import subprocess
if sys.version_info < (2, 7):
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict

__version__ = "0.18.4"
__author__ = "Lance Parsons & Robert Leach"
__author_email__ = "lparsons@princeton.edu,rleach@princeton.edu"
__copyright__ = "Copyright 2011, Lance Parsons & Robert leach"
__license__ = ("BSD 2-Clause License "
               "http://www.opensource.org/licenses/BSD-2-Clause")

UNMATCHED = 'unmatched'
MATCHED = 'matched'
MULTIMATCHED = 'multimatched'
# Used in the N-dimensional dictionary to help
# diagnose which barcode set is matching/not matching
ANY = 'any'
OUTPUT_FILENAME_TEMPLATE = '{prefix}{sample_id}-read-{readnum}{suffix}'


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(description=globals()['__doc__'])
    parser.add_argument('--version', action='version',
                        version='%(prog)s version ' + globals()['__version__'])

    required_group = parser.add_argument_group("Barcodes")

    required_group.add_argument('--bcfile', metavar='FILE',
                                help='REQUIRED: Tab delimited file: '
                                '"Sample_ID <tab> Barcode_Sequence"  '
                                'Multiple barcode columns with different '
                                'barcode lengths allowed, but all barcodes in '
                                'each inidividual column must be the same '
                                'length.')
    required_group.add_argument('--idxread', metavar='READNUM', type=int,
                                nargs='+', help="REQUIRED: Indicate in "
                                "which read file(s) to search for the "
                                "corresponding column of barcode sequences, "
                                "e.g. if the first column of barcodes is in "
                                "the second sequence read file and the "
                                "second column's barcodes are in the third "
                                "sequence read file, you'd supply "
                                "`--idxread 2 3`")
    required_group.add_argument('--mismatches', default=0, type=int,
                                help='Number of mismatches allowed in '
                                'barcode matching')
    required_group.add_argument('--barcodes_at_end', action='store_true',
                                default=False, help='Barcodes are at the end '
                                'of the index read (default is at the '
                                'beginning)')

    output_group = parser.add_argument_group("Output Options")

    output_group.add_argument('--prefix', default='',
                              help='Prefix for output files')
    output_group.add_argument('--suffix', default=None,
                              help='Suffix for output files (default based '
                              'on --format)')
    output_group.add_argument('--galaxy', action='store_true', default=False,
                              help='Produce "Galaxy safe" filenames by '
                              'removing underscores (default: %(default)s)')
    output_group.add_argument('--nosanitize', action='store_true',
                              default=False, help='Do not produce "safe" '
                              'filenames by replacing unusual characters in '
                              'the supplied prefix and sample IDs with '
                              'underscores. (default: %(default)s)')
    output_group.add_argument('-v', '--verbose', action='store_true',
                              default=False, help='verbose output')
    output_group.add_argument('--gzipout', action='store_true', default=False,
                              help='Output files in compressed gzip format '
                              '(default is uncompressed)')
    output_group.add_argument('--split_all', action='store_true',
                              default=False, help='Split all input files, '
                              'including index read files (by default, index '
                              'read files are not split unless all read files '
                              'are index files)')

    input_group = parser.add_argument_group("Input format")

    input_group.add_argument('--format', default='fastq',
                             help='Specify format for sequence files (fasta '
                             'or fastq)')
    input_group.add_argument('--gzipin', action='store_true', default=False,
                             help='Assume input files are in gzip format, '
                             'despite file extension (default is auto based '
                             'on input file extension)')

    seqs_group = parser.add_argument_group("Sequence Inputs")

    seqs_group.add_argument('fastq_files', metavar='FILE', type=str, nargs='+',
                            help='A series of 1 or more [optionally zipped] '
                            'fastq files.')

    # Error-check the values provided from the command line
    try:
        options = parser.parse_args()
        if options.fastq_files is None or options.idxread is None:
            parser.error('Sequence files and at least one number indicating '
                         'the indexed file(s) (--idxread) is required')
        if len(options.fastq_files) < 1:
            parser.error('Must specify at least one sequence file')
        if len(options.fastq_files) < len(options.idxread):
            parser.error('Must specify at least one sequence file')
        if not options.bcfile:
            parser.error('Must specify a barcodes file with "--bcfile" option')
        if ((min(options.idxread) < 1) or
                (max(options.idxread) > len(options.fastq_files))):
            parser.error('Invalid index read number ("--idxread"), must be '
                         'between 1 and %s (the number of supplied sequence '
                         'files)' % len(options.fastq_files))
    except SystemExit as e:  # Prevent exit when calling as function
        return(e.code)

    # Split all files if requested, otherwise split all files if all files are
    # index files
    split_all = options.split_all
    if not split_all:
        split_all = (len(options.fastq_files) == len(options.idxread))

    # Read barcodes files into n-dimensional dictionary
    # barcode_dict = None
    # approx_bc_dict = None
    # sample_dict = None
    # barcode_sizes = None
    try:
        (barcode_dict, approx_bc_dict, sample_dict, barcode_sizes) = (
            read_barcodes(options.bcfile, len(options.idxread),
                          options.mismatches, not options.nosanitize,
                          options.galaxy))
    except (BarcodeLengthError, FileOpenError, DupeBarcodeRowsError) as e:
        sys.stderr.write(e.message)
        return(e.code)

    # initialize the read counts for each barcode
    total_read_count = 0
    matched_counts = multi_dimensions(len(options.idxread), int)
    unmatched_counts = multi_dimensions(len(options.idxread), int)
    error_counts = 0
    # TODO() Verbose: print barcode_dict

    # Determine if we should use gzip for input
    basename, extension = os.path.splitext(options.fastq_files[0])
    if extension == '.gz':
        options.gzipin = True

    # Set the suffix (before determination of gzip output mode)
    if options.suffix is not None:
        suffix = options.suffix
    elif options.format is not None:
        suffix = '.%s' % options.format
    elif extension != '.gz':
        suffix = '.%s' % extension
    else:
        suffix = 'fastq'

    # Determine if we should use gzip for output
    if (options.gzipout is True or
            (options.suffix is not None and options.suffix == '.gz')):
        options.gzipout = True
        if options.suffix is None or suffix != '.gz':
            suffix = '%s.gz' % suffix

    # Determine if we need to edit the prefix for galaxy mode
    prefix = options.prefix
    if options.galaxy:
        prefix = prefix.replace("_", "-")

    # Open input filehandles for each read
    # print "Opening the input file handles..."
    inputs = {}
    for i in range(0, len(options.fastq_files)):
        try:
            if options.gzipin:
                inputs[i] = open_gzip_in(options.fastq_files[i])
            else:
                inputs[i] = codecs.open(options.fastq_files[i], 'rU',
                                        encoding='utf-8')
        except (OSError, IOError) as e:
            sys.stderr.write("ERROR: Unable to open %s: %s\n"
                             % (options.fastq_files[i], e))
            return(10)
        except FileDoesNotExistError as e:
            sys.stderr.write(e.message)
            return(e.code)

    readidxs = [i - 1 for i in options.idxread]

    # Open output filehandles for each barcode set and sequence file
    # print "Opening the output barcode file handles..."
    outputs = multi_dimensions((len(options.idxread) + 1), open)
    try:
        openOutfiles(outputs, barcode_dict, prefix, suffix, inputs,
                     options.gzipout, split_all, readidxs)
    except (FileExistsError, FileOpenError) as e:
        sys.stderr.write(e.message)
        return(e.code)

    # Open the file handle for the unmatched file
    # print "Opening the output un/multi-matched file handles..."
    unmatchedOutputs = defaultdict(open)
    multimatchedOutputs = defaultdict(open)
    for i in range(0, len(inputs)):

        if not split_all and i in readidxs:
            continue

        unmf = OUTPUT_FILENAME_TEMPLATE.format(prefix=prefix,
                                               sample_id=UNMATCHED,
                                               readnum=i + 1,
                                               suffix=suffix)

        if os.path.isfile(unmf):
            sys.stderr.write("ERROR: File exists: %s.\n" % unmf)
            return(7)

        try:
            if options.gzipout:
                unmatchedOutputs[i] = open_gzip_out(unmf)
            else:
                unmatchedOutputs[i] = codecs.open(unmf, 'w',
                                                  encoding='utf-8')
        except (OSError, IOError) as e:
            sys.stderr.write("ERROR: Unable to open %s: %s\n" % (unmf, e))
            return(3)

        mmf = OUTPUT_FILENAME_TEMPLATE.format(prefix=prefix,
                                              sample_id=MULTIMATCHED,
                                              readnum=i + 1,
                                              suffix=suffix)

        if os.path.isfile(mmf):
            sys.stderr.write("ERROR: File exists: %s." % mmf)
            return(8)

        try:
            if options.gzipout:
                multimatchedOutputs[i] = open_gzip_out(mmf)
            else:
                multimatchedOutputs[i] = codecs.open(mmf, 'w',
                                                     encoding='utf-8')
        except (OSError, IOError) as e:
            sys.stderr.write(
                "ERROR: Unable to open %s: {msg}\n".format(msg=e)
                % mmf)
            return(4)

    # Debug mode reads the 1st 10000 reads of each file when prefix has "debug"
    debug_mode = False
    if re.match('debug', prefix):
        debug_mode = True

    try:
        (total_read_count, error_counts) = (
            splitSequences(in_handles=inputs,
                           in_filenames=options.fastq_files,
                           idxread_indexes=readidxs,
                           barcode_sizes=barcode_sizes,
                           approx_bc_dict=approx_bc_dict,
                           outputs=outputs,
                           unmatchedOutputs=unmatchedOutputs,
                           multimatchedOutputs=multimatchedOutputs,
                           matched_counts=matched_counts,
                           unmatched_counts=unmatched_counts,
                           barcodes_at_end=options.barcodes_at_end,
                           split_all=split_all,
                           verbose=options.verbose,
                           debug_mode=debug_mode))
    except FileDoesNotExistError as e:
        sys.stderr.write(e.message)
        return(e.code)
    except subprocess.CalledProcessError as e:
        sys.stderr.write("{}\n\t{}".format(str(e), e.output))
        return(e.returncode)

    # Report the final matched/unmatched counts in a table to STDOUT
    try:
        printCounts(barcode_dict, matched_counts, unmatched_counts,
                    error_counts, total_read_count, len(options.idxread),
                    sample_dict=sample_dict, prefix=options.prefix,
                    suffix=suffix)
    except UnicodeEncodeError:
        sys.stderr.write("ERROR: Unrecognized character found in sample table "
                         "output.  Set the PYTHONIOENCODING (e.g. to "
                         "'UTF-8') as an environment variable and run again, "
                         "or edit your barcode file to use only ASCII "
                         "characters.\n")
        return(11)

    return(0)


def Tree():
    return(defaultdict(Tree))


def read_barcodes(filename, num_dims, mismatches, sanitize, galaxy):
    '''Read barcodes file into dictionary'''

    # Declare a variable-dimension dictionary
    # This was previously a static multi-dimensional dictionary, but it would
    # not have worked...
    real_bc_dict = Tree()
    approx_bc_dict = Tree()
    approx_bc_any_dict = Tree()
    barcode_sizes = None
    numdupes = 0
    dupedict = OrderedDict()

    # Keep track of the sample IDs to make sure they're unique
    sample_dict = OrderedDict()
    barcodes = defaultdict(list)

    try:
        f = codecs.open(filename, 'rU', encoding='utf-8')
    except (OSError, IOError) as ex:
        raise FileOpenError(5, 'Unable to open barcode file: %s' % ex)

    linenum = 0
    with f as filehandle:
        for line in filehandle:

            linenum += 1
            line = line.strip()
            cols = []

            # If the line has something on it and isn't commented
            if line and line[0] != '#':

                cols = re.split('\t+', line)

                # If we got the expected number of columns
                if len(cols) == (num_dims + 1):
                    smpl_id = cols.pop(0)
                    if sanitize:
                        # Eliminate weird characters (being strict here)
                        sample_id_clean = re.sub(
                            r'[^A-Za-z0-9\-\+\.<>@#%^=_~]+', '_', smpl_id)
                    if galaxy:
                        sample_id_clean.replace("_", "-")
                    if sample_id_clean in sample_dict:
                        raise Exception(
                            "Sample IDs are not unique.  Note, this could "
                            "be due to either being in --galaxy mode or "
                            "from sample ID sanitization.  If the sample "
                            "IDs in your barcodes file appear unique, "
                            "either replace UTF8 characters with ASCII "
                            "characters or try supplying --nosantize.  "
                            "Note, UTF8 could cause problems with file "
                            "names on some systems.")
                    sample_dict[sample_id_clean] = smpl_id
                    barcode_sequences = cols
                    if not barcode_sizes:
                        barcode_sizes = [len(e) for e in barcode_sequences]
                else:
                    sys.stderr.write(
                        "Unable to parse line in barcode file: [%s]:"
                        "[%s]. Must contain %s columns (the number of "
                        "values supplied to --idxread plus 1 for the "
                        "sample ID), but found [%s].  Skipping.\n" %
                        (filename, line, (num_dims + 1), len(cols)))
                    continue

                # If the sample ID is not none and the number of defined
                # barcodes is equal to the number of expected barcodes
                defined_barcodes = [
                    e for e in barcode_sequences if e is not None]
                for i, e in enumerate(defined_barcodes):
                    barcodes[i].append(e)
                if ((sample_id_clean is not None) and
                        len(defined_barcodes) == num_dims):

                    # Set the sample ID in the N-Dimensional dictionary
                    try:
                        setNDDictVal(real_bc_dict, defined_barcodes,
                                     sample_id_clean)
                    except (DupeBarcodeRowError) as ex:
                        numdupes += 1
                        dupedict[ex.bcidlist[0]] = 0
                        dupedict[ex.bcidlist[1]] = 0

                    # This creates a dictionary containing all possible
                    # barcode combos, with MULTIMATCHED values pre-computed
                    # print ("Calling setNDApproxDictVal with %s & dict: "
                    #        "[%s]") % (defined_barcodes, approx_bc_dict)
                    setNDApproxDictVal(approx_bc_dict,
                                       defined_barcodes,
                                       mismatches)

                    # Make sure we can get all the barcodes for each dict
                    # dimension
                    dim = 0
                    for barcode in defined_barcodes:
                        dim += 1
                        real_bc_dict[ANY][str(dim)][barcode] = ""
                        # Create dictionary with all barcode combos
                        setNDApproxDictVal(
                            approx_bc_any_dict[ANY][str(dim)],
                            [barcode],
                            mismatches)
                elif ((smpl_id is not None) and
                      (len(defined_barcodes) > num_dims)):
                    raise Exception("More barcode indexes were found in "
                                    "the barcodes file on line %s: '%s' "
                                    "than were expected: [%s] (the number "
                                    "of values supplied to --idxread)."
                                    % (linenum, line, num_dims))

                else:
                    raise Exception("Unable to parse barcode(s) from line "
                                    "%s: '%s'. Expected a sample ID "
                                    "followed by [%s] tab-delimited "
                                    "barcodes" % (linenum, line, num_dims))
        f.close()

    if numdupes > 0:
        raise DupeBarcodeRowsError(12,
                                   "The following barcode IDs have identical "
                                   "index sequences in the barcode file: "
                                   "[%s]: [%s]."
                                   % (filename, ','.join(dupedict.keys())))
    if len(real_bc_dict) == 0:
        raise Exception("Unable to parse any barcodes from barcode file [%s]."
                        % (filename))
    for barcode_list in list(barcodes.values()):
        barcode_lens = list(map(len, barcode_list))
        if not all(each_len == barcode_lens[0] for each_len in barcode_lens):
            raise BarcodeLengthError(1)

    reduceNDDictPaths(approx_bc_dict)

    for dim in real_bc_dict[ANY]:
        reduceNDDictPaths(approx_bc_any_dict[ANY][dim])
        approx_bc_dict[ANY][dim] = approx_bc_any_dict[ANY][dim]

    return(real_bc_dict, approx_bc_dict, sample_dict, barcode_sizes)


def splitSequences(in_handles, in_filenames, idxread_indexes, barcode_sizes,
                   approx_bc_dict, outputs, unmatchedOutputs,
                   multimatchedOutputs, matched_counts, unmatched_counts,
                   barcodes_at_end, split_all, verbose, debug_mode):
    '''Split the sequence files using the supplied indexes'''

    total_read_count = 0
    error_counts = 0
    primary_index = idxread_indexes[0]

    # For each input line in index read, get index sequence
    for primary_read in read_fastq(in_handles[primary_index]):
        try:
            total_read_count += 1

            # print "Processing read number %s\r" % (total_read_count),
            if verbose & (total_read_count % 1000000 == 0):
                print(total_read_count, file=sys.stderr)

            # For debugging any file
            if debug_mode and total_read_count > 10000:
                break

            # Determine the ID format using the first record
            if total_read_count == 1:
                id_format = (
                    determine_id_format(primary_read['seq_id'][1:]))

            # Get 1 from each file & assert that their IDs match
            cur_reads = {}
            for read_index in range(0, len(in_handles)):
                # print ("read_index: {0}".format(read_index))
                if(read_index is not primary_index):
                    try:
                        cur_reads[read_index] = next(
                            read_fastq(in_handles[read_index]))
                    except StopIteration as e:
                        raise FastqNumRecsError(in_filenames[primary_index],
                                                in_filenames[read_index],
                                                total_read_count)
                    try:
                        assert(match_id(primary_read['seq_id'],
                                        cur_reads[read_index]['seq_id'],
                                        id_format))
                    except AssertionError:
                        raise FastqIdMatchError(
                            primary_read['seq_id'],
                            cur_reads[read_index]['seq_id'])
                else:
                    cur_reads[read_index] = primary_read

            # Get the index sequences from the indexed reads
            index_seqs = []
            if barcodes_at_end:
                index_seqs = (
                    [cur_reads[idxread_indexes[i]]['seq'][-barcode_sizes[i]:]
                     for i in range(0, len(idxread_indexes))])
            else:
                index_seqs = (
                    [cur_reads[idxread_indexes[i]]['seq'][0:barcode_sizes[i]]
                     for i in range(0, len(idxread_indexes))])

            barcode_path = getNDDictVal(approx_bc_dict, index_seqs)

            if(barcode_path is None):
                cur_outputs = unmatchedOutputs
                unmatched_path = getBarcodeMatchPath(approx_bc_dict,
                                                     index_seqs)
                incrementNDDictInt(unmatched_counts, unmatched_path)
                if (UNMATCHED not in unmatched_path and
                        MULTIMATCHED not in unmatched_path):
                    sys.stderr.write('WARNING: Sequences match barcodes on '
                                     'different rows: %s for sequence ID: %s\n'
                                     % (index_seqs, primary_read['seq_id']))
            elif(MULTIMATCHED in barcode_path):
                cur_outputs = multimatchedOutputs
                unmatched_path = getBarcodeMatchPath(approx_bc_dict,
                                                     barcode_path)
                incrementNDDictInt(unmatched_counts, unmatched_path)
                sys.stderr.write('WARNING: More than one barcode matches '
                                 '%s, moving to %s category\n'
                                 % (primary_read['seq_id'], MULTIMATCHED))
            else:
                cur_outputs = getNDDictVal(outputs, barcode_path)
                incrementNDDictInt(matched_counts, barcode_path)

            # Write each sequence to the matched or unmatched output handle
            for i in range(0, len(in_handles)):
                if split_all or i not in idxread_indexes:
                    cur_outputs[i].write(fastq_string(cur_reads[i]))
        except (FastqIdMatchError, FastqNumRecsError) as e:
            sys.stderr.write(e.message)
            error_counts += 1
            continue

    return(total_read_count, error_counts)


def openOutfiles(outputs, barcode_dict, prefix, suffix, inputs, gzip_mode,
                 split_all, index_reads):
    '''Opens all the output files for all barcode matches
       (unmatched barcode output files not opened)'''

    if isinstance(barcode_dict, dict):
        for barcode in getRealBarcodes(list(barcode_dict.keys())):
            openOutfiles(outputs[barcode], barcode_dict[barcode], prefix,
                         suffix, inputs, gzip_mode, split_all, index_reads)
    else:
        sample_id = barcode_dict
        for i in range(0, len(inputs)):
            if split_all or i not in index_reads:
                fn = OUTPUT_FILENAME_TEMPLATE.format(prefix=prefix,
                                                     sample_id=sample_id,
                                                     readnum=i + 1,
                                                     suffix=suffix)

                if os.path.isfile(fn):
                    raise FileExistsError(9, fn)

                try:
                    if gzip_mode:
                        outputs[i] = open_gzip_out(fn)
                    else:
                        outputs[i] = codecs.open(fn, 'w', encoding='utf-8')
                except (OSError, IOError) as e:
                    raise FileOpenError(6, 'Unable to open %s: %s' % (fn, e))

            else:
                # So that barcode path has something in it to return, set the
                # values to the standard error stream.  These should not be
                # used.  They are here to make a valid, populated datastructure
                outputs[i] = sys.stderr


def setNDDictVal(in_dict, keys_list, val):
    '''Sets the value of an N-Dimensional dictionary to the supplied value
    using the list of keys'''
    cur_dict = in_dict
    for cur_key in keys_list[0:-1]:
        cur_dict = cur_dict[cur_key]
    if keys_list[-1] in cur_dict:
        raise DupeBarcodeRowError(14, [cur_dict[keys_list[-1]], val])
    cur_dict[keys_list[-1]] = val


def incrementNDDictInt(in_dict, keys_list):
    '''Sets the value of an N-Dimensional dictionary to the supplied value
    using the list of keys'''
    cur_dict = in_dict
    for cur_key in keys_list[0:-1]:
        cur_dict = cur_dict[cur_key]
    cur_dict[keys_list[-1]] += 1


def getNDDictVal(in_dict, keys_list):
    '''Gets the value of an N-Dimensional dictionary using the list of keys'''
    cur_dict = in_dict
    for cur_key in keys_list:
        if cur_key in cur_dict:
            cur_dict = cur_dict[cur_key]
        else:
            return(None)
    return(cur_dict)


def multi_dimensions(n, type):
    """Creates an N-dimensional dictionary containing values at the leaves of
    type 'type'. E.g. A 2-dimensional dictionary of strs would have 2 levels of
    keys that hold string values (mydict['key1']['key2'] = 'my string value')
    """

    '''n <= 0 is correct. E.g. if called with 2 (i.e. a 2D dictionary - like a
    2D array/matrix - where array[2][1] = 5 or dict['key1']['key2'] = 'str' are
    2-dimensional data structures), the the first type returned is a dict (for
    holding 'key1') and the second thing returned is a defaultdict for holding
    'key2' and the last thing returned is the type of the data held at the
    leaves of the dictionary'''
    if n <= 0:
        return(type())

    return(defaultdict(lambda: multi_dimensions(n - 1, type)))


def getRealBarcodes(barcodes):
    '''Return a list of barcodes that exclude generic "matched", "unmatched",
    and "any" pseudo-barcodes'''
    return([bc for bc in barcodes if (bc is not UNMATCHED and
                                      bc is not MATCHED and
                                      bc is not ANY and
                                      bc is not MULTIMATCHED and
                                      bc is not None)])


def matchBarcodes(sequence, barcodes, mismatches):
    '''Find closest match(es) in barcodes to specified sequence with max number
    of mismatches'''
    best_distance = mismatches
    results = []
    for barcode in barcodes:
        if mismatches == 0:
            if (sequence == barcode):
                results.append(barcode)
        else:
            distance = hamming_distance(sequence, barcode)
            if (distance <= best_distance):
                best_distance = distance
                results.append(barcode)
    return(results)


def hamming_distance(s1, s2):
    assert len(s1) == len(s2)
    return(sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2)))


''' Supported types of Fastq IDs '''
ILLUMINA = 'illumina'   # CASVA 1.8+, match up to space
# Illumina CASAVA 1.7 and lower (/1 /2) and NCBI SRA (/f /r),
# match all but last character
STRIPONE = 'stripone'
OTHER = 'other'     # Other, match exactly


def determine_id_format(seq_id):
    '''Determine if the id is new illumina, old illumina (/1 /2 ...), sanger
    (/f /r), or other'''

    id_format = None
    # Illumina CASAVA 1.8+ fastq headers use new format
    read_id_regex = re.compile(r'(?P<instrument>[a-zA-Z0-9_-]+):'
                               '(?P<run_number>[0-9]+):'
                               '(?P<flowcell_id>[a-zA-Z0-9-]+):'
                               '(?P<lane>[0-9]+):(?P<tile>[0-9]+):'
                               '(?P<x_pos>[0-9]+):'
                               '(?P<y_pos>[0-9]+) (?P<read>[0-9]+):'
                               '(?P<is_filtered>[YN]):'
                               '(?P<control_number>[0-9]+):'
                               '(?P<index_sequence>[ACGT]+){0,1}')
    # Old illumina and sanger reads use /1 /2 /3 or /f /r
    strip_one_endings = ['/1', '/2', '/3', '/f', '/r']

    if read_id_regex.match(seq_id):
        id_format = ILLUMINA
    elif (seq_id[-2:] in strip_one_endings):
        id_format = STRIPONE
    else:
        id_format = OTHER
    return(id_format)


def strip_read_from_id(seq_id, id_format=None):
    new_id = seq_id
    if not id_format:
        id_format = determine_id_format(seq_id)
    elif id_format == STRIPONE:
        new_id = seq_id[0:-1]
    elif id_format == ILLUMINA:
        new_id = seq_id.split(' ')[0]
    return(new_id)


def strip_read_from_id_stripone(seq_id):
    return(seq_id[0:-1])


def strip_read_from_id_illumina(seq_id):
    return(seq_id.split(' ')[0])


def match_id(id1, id2, id_format=OTHER):
    ''' Return true if IDs match using rules for specified format '''
    if id_format == STRIPONE:
        if id1[0:-1] == id2[0:-1]:
            return(True)
        else:
            return(False)
    elif id_format == ILLUMINA:
        if (id1.split(' ')[0] == id2.split(' ')[0]):
            return(True)
        else:
            return(False)
    elif id1 == id2:
        return(True)
    else:
        return(False)


def read_fastq(filehandle):
    ''' Return dictionary with "seq_id", "seq", "qual_id", and "qual" '''
    record_line = 0
    read_number = 0
    fastq_record = dict()
    for line in filehandle:
        record_line += 1
        if record_line == 1:
            fastq_record['seq_id'] = line.strip()
        elif record_line == 2:
            fastq_record['seq'] = line.strip()
        elif record_line == 3:
            fastq_record['qual_id'] = line.strip()
        elif record_line == 4:
            record_line = 0
            fastq_record['qual'] = line.strip()
            read_number += 1
            yield fastq_record


def fastq_string(record):
    return("%s\n%s\n%s\n%s\n" % (record['seq_id'], record['seq'],
                                 record['qual_id'], record['qual']))


def printCounts(barcode_dict, matched_counts, unmatched_counts, error_counts,
                total_read_count, numBarcodes, sample_dict, prefix, suffix):
    '''Prints the header of the counts table and calls the 2 recursive
    functions for printing barcode and unmatched barcode count data'''

    # Print the table header
    print('Sample\t', end='')
    for b in range(1, numBarcodes + 1):
        print("Barcode%s\t" % (b), end='')
    print("Count\tPercent\tFiles")

    if total_read_count == 0:
        print("ERROR: Total read count is 0.  No reads were parsed.")
        return()

    # Print the matched counts, sorting the lines
    summary_dict = getMatchedCountsTable(barcode_dict, matched_counts,
                                         total_read_count, [],
                                         sample_dict=sample_dict,
                                         prefix=prefix,
                                         suffix=suffix)
    for orig_sample in sample_dict.values():
        line = summary_dict.get(orig_sample)
        if sys.version_info < (2, 7):
            line = line.encode('utf-8')
        if line is None:
            raise MissingBarcodeIDError(13,
                                        "None encountered while looking up "
                                        "barcode ID: [%s]" % (orig_sample))
        else:
            sys.stdout.write(line)

    # Print the unmatched counts (default sorted by string)
    for line in getUnmatchedCounts(unmatched_counts, total_read_count, [],
                                   prefix, suffix):
        sys.stdout.write(line)
    if error_counts > 0:
        error_line = ('ERRORS\t{barcodes}\t{count}\t{percent:.2f}%\tSTDERR'
                      .format(barcodes='\t'.join(['NA'] * numBarcodes),
                              count=error_counts,
                              percent=(error_counts/total_read_count) * 100))
        print(error_line)


def getMatchedCountsTable(barcode_dict, matched_counts, total_read_count,
                          barcode_path, sample_dict, prefix, suffix):
    '''Recursively builds a "barcode path" and prints a line in the barcode
    counts table for every leaf in the barcode dictionary'''

    summary_dict = dict()
    if isinstance(barcode_dict, dict):
        for barcode in barcode_dict:
            if barcode is not ANY:
                if len(barcode_path) > 0:
                    new_barcode_path = barcode_path[:]
                else:
                    new_barcode_path = []
                new_barcode_path.append(barcode)
                summary_dict.update(
                    getMatchedCountsTable(barcode_dict[barcode],
                                          matched_counts[barcode],
                                          total_read_count,
                                          new_barcode_path,
                                          sample_dict=sample_dict,
                                          prefix=prefix,
                                          suffix=suffix))
    else:
        ret_str = sample_dict[barcode_dict] + "\t"

        for bc in barcode_path:
            ret_str += bc + "\t"
        ret_str += "%s\t%.2f%%\t" % (matched_counts,
                                     (matched_counts / total_read_count) * 100)
        ret_str += OUTPUT_FILENAME_TEMPLATE.format(
            prefix=prefix,
            sample_id=barcode_dict,
            readnum="*",
            suffix=suffix
        ) + "\n"
        summary_dict[sample_dict[barcode_dict]] = ret_str

    return(summary_dict)


def getUnmatchedCounts(unmatched_counts, total_read_count, barcode_path,
                       prefix, suffix):
    '''Recursively builds a "barcode path" (consisting of "MATCHED" and
    "UNMATCHED" values) and prints a line in the barcode counts table for every
    leaf in the unmatched counts dictionary'''
    ret_list = []
    if isinstance(unmatched_counts, dict):
        for barcode in sorted(unmatched_counts.keys()):
            if len(barcode_path) > 0:
                new_barcode_path = barcode_path[:]
            else:
                new_barcode_path = []
            new_barcode_path.append(barcode)
            ret_list.extend(getUnmatchedCounts(
                unmatched_counts[barcode], total_read_count,
                new_barcode_path, prefix, suffix))
    else:
        label = UNMATCHED
        if (UNMATCHED not in barcode_path and MULTIMATCHED in barcode_path):
            label = MULTIMATCHED
        ret_str = "%s\t" % (label)
        for bc in barcode_path:
            ret_str += "%s\t" % (bc)
        ret_str += ("%s\t%.2f%%\t" %
                    (unmatched_counts,
                     (unmatched_counts / total_read_count) * 100))
        ret_str += OUTPUT_FILENAME_TEMPLATE.format(
            prefix=prefix,
            sample_id=label,
            readnum="*",
            suffix=suffix
        ) + "\n"
        ret_list.append(ret_str)
    return(ret_list)


def getBarcodeMatchPath(in_dict, keys_list):
    '''Generates a path of pseudo-barcodes (consisting of "MATCHED",
    "UNMATCHED", and "MULTIMATCHED" values) to use in the summary output.  The
    intent is to give the user useful feedback about which level(s) of barcodes
    are not matrching instead of listing all sequences as simply "UNMATCHED".
    It also reduces complexity of the unmatched output by not including
    specific barcodes, which do not matter in unmatched/multimatched cases.'''
    dim = 0
    path = []
    for cur_key in keys_list:
        dim += 1
        if cur_key is MATCHED or cur_key is MULTIMATCHED:
            path.append(cur_key)
        elif cur_key in in_dict[ANY][str(dim)]:
            path.append(MATCHED)
        else:
            path.append(UNMATCHED)
    return(path)


def setNDApproxDictVal(in_dict, keys_list, mismatches):
    '''Creates (or builds upon) an N-Dimensional ("ND") dictionary (in_dict)
    whose keys are mismatch variants (constructed using the keys_list and the
    number of mismatches provided).  The values at each level (initially:
    changed by reduceNDDictPaths) is a 2 member list containing the number of
    mismatches the key has and the dictionary for the next level.  The values
    at the end of the ND dictionary are (initially: changed by
    reduceNDDictPaths) a 2 member list containing the number of mismatches and
    a list of "original key paths".  (Each path is a list of barcodes.)  The
    keys_list is a series of barcodes representing a row from the barcodes file
    (i.e. 1 barcode from each dimension, in order).
    Note: in_dict must be "l()" where "l" = lambda:defaultdict(l).'''
    setNDApproxDictValHelper(in_dict, keys_list, mismatches, [])


def setNDApproxDictValHelper(in_dict, keys_list, mismatches, real_path):
    '''A recursive helper of setNDApproxDictVal which tracks the "real barcode
    path"  to use in the list of real barcode paths at the end of the
    dictionary.  Note that barcodes may have a 1:many relationship, indicated
    by a barcode being repeated in earlier columns of the barcode file.
    Different paths may also intersect given the number of allowed mismatches.
    '''
    real_path.append(keys_list[0])
    if len(keys_list) == 1:
        # print "Doing last key %s" %(keys_list[0])
        for bcl in getMismatchedBarcodes(keys_list[0], mismatches):
            # print "Processing mismatched barcode record: %s" % (bcl)
            nmm = bcl[0]
            bc = bcl[1]
            if (bc in in_dict and type(in_dict[bc][1]) is list
                    and len(in_dict[bc][1]) > 0
                    and real_path not in in_dict[bc][1]):

                # print ("Adding real path %s to the one existing at barcode "
                #       "%s: %s whose type should be a list: %s"
                #       ) % (real_path, bc, in_dict[bc], type(in_dict[bc]))

                # If the number of mismatches is the same for this barcode
                # variant as it is for the real paths that have already been
                # added to the real paths list, append this real path
                if nmm == in_dict[bc][0]:
                    in_dict[bc][1] += [real_path]
                # Else if the number of mismatches is less for this barcode
                # variant as it is for the real paths that have already been
                # added to the real paths list, overwrite the old list
                elif nmm < in_dict[bc][0]:
                    in_dict[bc] = [nmm, [real_path]]
            elif not (bc in in_dict and type(in_dict[bc][1]) is list
                      and len(in_dict[bc][1]) > 0):
                # print ("Setting new real path %s to real path list for "
                #       "barcode %s: %s whose type should be a list: %s"
                #       ) % (real_path, bc, in_dict[bc], type(in_dict[bc]))
                in_dict[bc] = [nmm, [real_path]]
            # Else: skip poorer match
    else:
        # print "Doing first key %s" %(keys_list[0])
        for bcl in getMismatchedBarcodes(keys_list[0], mismatches):
            nmm = bcl[0]
            bc = bcl[1]
            if bc not in in_dict:
                in_dict[bc] = [nmm, Tree()]
                setNDApproxDictValHelper(in_dict[bc][1],
                                         keys_list[1:],
                                         mismatches,
                                         real_path[:])
            elif (bc in in_dict and nmm == in_dict[bc][0]):
                setNDApproxDictValHelper(in_dict[bc][1],
                                         keys_list[1:],
                                         mismatches,
                                         real_path[:])
            elif (bc in in_dict and nmm < in_dict[bc][0]):
                # print "Type of in_dict[%s] is: %s Resetting list." %
                # (bc, type(in_dict[bc]))
                in_dict[bc] = [nmm, Tree()]
                # in_dict[bc][0] = nmm
                # in_dict[bc][1] = l()
                setNDApproxDictValHelper(in_dict[bc][1],
                                         keys_list[1:],
                                         mismatches,
                                         real_path[:])


def reduceNDDictPaths(in_dict):
    '''After an approximate barcode dictionary has been fully created by
    setNDApproxDictVal, this method reduces the lists of barcode paths to
    individual discrete paths or individual generic MATCHED/MULTIMATCHED paths.
    '''
    if isinstance(in_dict, dict) and len(in_dict) > 0:
        arb_bc = next(iter(in_dict.keys()))
        # print "Checking arbitrary barcode to see what level of the dictionary
        # we're at: %s" % (arb_bc)
        # print "The keys of this level of the dictionary are: %s" %
        # (in_dict.keys())
    if (isinstance(in_dict, dict) and len(in_dict) > 0 and
            isinstance(in_dict[arb_bc][1], dict)):
        for bc in in_dict:
            # Reduction (skipping the list...)
            in_dict[bc] = in_dict[bc][1]
            reduceNDDictPaths(in_dict[bc])
    # Else if the value is a list of lists
    elif (isinstance(in_dict, dict) and len(in_dict) > 0 and
          isinstance(in_dict[list(in_dict.keys())[0]][1], list)):
        # For each last barcode in the dictionary
        for bc in in_dict:
            # Reduction, skipping the outer list
            in_dict[bc] = in_dict[bc][1]
            # If the value at the leaf of the dict is a list of lists
            if (len(in_dict[bc]) > 0 and isinstance(in_dict[bc], list) and
                    len(in_dict[bc][0]) > 0 and
                    isinstance(in_dict[bc][0], list)):
                # If the number of paths is 1
                if len(in_dict[bc]) == 1:
                    in_dict[bc] = in_dict[bc][0]
                else:
                    inner_len = len(in_dict[bc][0])
                    ref_path = in_dict[bc][0]
                    new_path = []
                    for bci in range(0, inner_len):
                        all_matched = True
                        for path in in_dict[bc][1:]:
                            if path[bci] != ref_path[bci]:
                                all_matched = False
                                break
                        if all_matched is True:
                            new_path.append(MATCHED)
                        else:
                            new_path.append(MULTIMATCHED)
                    in_dict[bc] = new_path


def getMismatchedBarcodes(barcode, mismatches):
    '''Given a barcode sequence and a number of allowed mismatches, generate a
    list of barcodes representing all possible matching sequences with the
    allowed number of mismatches.'''
    return(getMismatchedBarcodesHelper(barcode, mismatches, []))


def getMismatchedBarcodesHelper(barcode, mismatches, skips):
    offbys = [[0, barcode]]
    if mismatches <= 0:
        return(offbys)
    for p in range(0, len(barcode)):
        if p in skips:
            continue
        # Keep track of bases that have already been mutated
        newskips = skips + [p]
        if barcode[p] != 'N':
            offbys.append([len(newskips),
                           barcode[:p] + 'N' + barcode[p + 1:]])
        if barcode[p] != 'A':
            offbys.append([len(newskips),
                           barcode[:p] + 'A' + barcode[p + 1:]])
        if barcode[p] != 'T':
            offbys.append([len(newskips),
                           barcode[:p] + 'T' + barcode[p + 1:]])
        if barcode[p] != 'G':
            offbys.append([len(newskips),
                           barcode[:p] + 'G' + barcode[p + 1:]])
        if barcode[p] != 'C':
            offbys.append([len(newskips),
                           barcode[:p] + 'C' + barcode[p + 1:]])
        # Recurse to add next allowed mismatch
        if mismatches > 1:
            if barcode[p] != 'N':
                offbys += getMismatchedBarcodesHelper(barcode[:p] + 'N' +
                                                      barcode[p + 1:],
                                                      mismatches - 1,
                                                      newskips)
            if barcode[p] != 'A':
                offbys += getMismatchedBarcodesHelper(barcode[:p] + 'A' +
                                                      barcode[p + 1:],
                                                      mismatches - 1,
                                                      newskips)
            if barcode[p] != 'T':
                offbys += getMismatchedBarcodesHelper(barcode[:p] + 'T' +
                                                      barcode[p + 1:],
                                                      mismatches - 1,
                                                      newskips)
            if barcode[p] != 'G':
                offbys += getMismatchedBarcodesHelper(barcode[:p] + 'G' +
                                                      barcode[p + 1:],
                                                      mismatches - 1,
                                                      newskips)
            if barcode[p] != 'C':
                offbys += getMismatchedBarcodesHelper(barcode[:p] + 'C' +
                                                      barcode[p + 1:],
                                                      mismatches - 1,
                                                      newskips)
    return(offbys)


def open_gzip_in(infile):
    '''Opens a gzip file for reading, using external gzip if available'''

    # Determine whether to use the gzip command line tool or not
    if exeExists('gzip'):
        cmd = ['gzip', '-dc', infile]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, bufsize=-1,
                             universal_newlines=True)
        if sys.version.startswith("2"):
            with p.stdout:
                for line in iter(p.stdout.readline, b''):
                    yield line
        else:
            with p:
                for line in p.stdout:
                    yield line
        exit_code = p.wait()
        if exit_code != 0:
            raise subprocess.CalledProcessError(
                p.returncode, subprocess.list2cmdline(cmd), p.stderr.read())
    else:
        with io.TextIOWrapper(io.BufferedReader(gzip.open(infile))) as f:
            for line in f:
                yield(line)


def open_gzip_out(outfile):
    '''Opens a gzip file for writing, using external gzip if available'''

    # Determine whether to use the gzip command line tool or not
    if exeExists('gzip'):
        p = subprocess.Popen(["gzip"], stdin=subprocess.PIPE,
                             stdout=open(outfile, 'wb'), bufsize=-1,
                             universal_newlines=True)
        return(p.stdin)
    else:
        return(io.TextIOWrapper(gzip.open(outfile, 'wb'), encoding='utf-8'))


def exeExists(program):
    '''Determines whether an executable exists (i.e. is in the user\'s path)'''
    import os

    def is_exe(fpath):
        return(os.path.isfile(fpath) and os.access(fpath, os.X_OK))

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return(True)
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return(True)

    return(False)


class BarcodeLengthError(Exception):
    '''Error parsing barcodes file'''
    def __init__(self, code):
        self.code = code
        self.message = "ERROR: Barcode sequences must all be the same length\n"


class FastqIdMatchError(Exception):
    '''Unable to match IDs between two fastq records'''
    def __init__(self, id1, id2):
        self.message = ("ERROR: Index ID mismatch: %s does not match %s\n" %
                        (id1, id2))


class FastqNumRecsError(Exception):
    '''Number of records in fastq files must be the same'''
    def __init__(self, file1, file2, rec_num):
        self.message = ("ERROR: Num reads mismatch: [%s, %s] skipping "
                        "records %s+\n" % (file1, file2, rec_num))


class FileExistsError(Exception):
    '''Output file exists - do not overwrite'''
    def __init__(self, code, filename):
        self.code = code
        self.message = "ERROR: File Exists: %s\n" % filename


class FileDoesNotExistError(Exception):
    '''Input file does not exist - cannot open'''
    def __init__(self, code, filename):
        self.code = code
        self.message = "ERROR: File does not exist: %s\n" % filename


class FileOpenError(Exception):
    '''Error opening file'''
    def __init__(self, code, message):
        self.code = code
        self.message = "ERROR: %s\n" % message


class DupeBarcodeRowsError(Exception):
    '''Duplicate barcode rows'''
    def __init__(self, code, message):
        self.code = code
        self.message = "ERROR: %s\n" % message


class DupeBarcodeRowError(Exception):
    '''Duplicate barcode row'''
    def __init__(self, code, bcidlist):
        self.code = code
        self.bcidlist = bcidlist


class MissingBarcodeIDError(Exception):
    '''Barcode ID lookup evaluated to None during STDOUT print'''
    def __init__(self, code, message):
        self.code = code
        self.message = "ERROR: %s\n" % message


if __name__ == '__main__':
    sys.exit(main())
