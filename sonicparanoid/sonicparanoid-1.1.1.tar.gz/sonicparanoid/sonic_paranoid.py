# -*- coding: utf-8 -*-
'''Execute the SonicParanoid.'''
import os
import sys
from shutil import copy, rmtree, move
import platform
import zipfile
import subprocess
import time
import fnmatch
import numpy as np
#### IMPORT TO GENERATE PyPi package
#'''
from sonicparanoid import seq_tools as seqtools
from sonicparanoid import ortholog_detection as orthodetect
from sonicparanoid import orthogroups
from sonicparanoid import sys_tools as systools
from sonicparanoid import hdr_mapping as idmapper
from sonicparanoid import remap_tables_c as remap
#'''
####

#### IMPORTS TO RUN LOCALLY
'''
import seq_tools as seqtools
import ortholog_detection as orthodetect
import sys_tools as systools
#'''
####


########### FUNCTIONS ############
def get_params():
    """Parse and analyse command line parameters."""
    # create the possible values for sensitivity value
    cnt = 0.9
    sensList = []
    for i in range(1, 9):
        sensList.append(float(i))
        for j in range(1, 10):
            fval = float(i + float(j / 10.))
            if fval <= 8.5:
                sensList.append(fval)
    # define the parameter list
    import argparse
    sonicparanoid_usage = '\nDefine --input-directory and --output-directory to find ortholog relationships for the proteomes in the input directory.\n'
    parser = argparse.ArgumentParser(description='SonicParanoid 1.0',  usage='%(prog)s -i <INPUT_DIRECTORY> -o <OUTPUT_DIRECTORY>[options]', prog='sonicparanoid')
    #start adding the command line options
    parser.add_argument('-i', '--input-directory', type=str, required=True, help='Directory containing the proteomes (in FASTA format) of the species to be analyzed.', default=None)
    parser.add_argument('-o', '--output-directory', type=str, required=True, help='The directory in which the results will be stored.', default=None)
    parser.add_argument('-m', '--mode', required=False, help='SonicParanoid execution mode. The default mode is suitable for most studies. Use sensitive or most-sensitive if the input proteomes are not closely related.', choices=['fast', 'default', 'sensitive', 'most-sensitive'], default='default')
    parser.add_argument('-p', '--project-id', type=str, required=False, help='Name for the project reflecting the run. If not specified it will be automatically generated using the current date and time.', default="")
    parser.add_argument('-sh', '--shared-directory', type=str, required=False, help='The directory in which the alignment files are stored. If not specified it will be created inside the main output directory.', default=None)
    parser.add_argument('-db', '--mmseqs-dbs', type=str, required=False, help='The directory in which the database files for MMseqs2 will be stored. If not specified it will be created inside the main output directory.', default=None)
    parser.add_argument('-t', '--threads', type=int, required=False, help='Number of parallel 1-CPU jobs to be used. Default=4', default=4)
    #parser.add_argument('-c', '--cutoff', type=int, required=False, help='Cutoff value to be used when processing alignments.', default=40)
    parser.add_argument('-se', '--sensitivity', type=float, required=False, help='Sensitivity for MMseqs2. This will overwrite the --mode option.', default=None)
    parser.add_argument('-noidx', '--no-indexing', required=False, help='Avoid the creation of indexes for MMseqs2 databases. IMPORTANT: while this saves starting storage space it makes MMseqs2 slightly slower.\nThe results might also be sligthy different.', default=False, action='store_true')
    parser.add_argument('-ot', '--overwrite-tables', required=False, help='This will force the re-computation of the ortholog tables. Only missing alignment files will be re-computed.', default=False, action='store_true')
    parser.add_argument('-ow', '--overwrite', required=False, help='Overwrite previous runs and execute it again. This can be useful to update a subset of the computed tables.', default=False, action='store_true')
    #parser.add_argument('-u', '--update', type=str, required=False, help='Update the ortholog tables database by adding or removing input proteomes. Performs only required alignments (if any) for new species pairs, and re-compute the ortholog groups.\nNOTE: an ID for the update must be provided.', default=None)
    parser.add_argument('-ml', '--max-len-diff', type=float, required=False, help='Maximum allowed length-difference-ratio between main orthologs and canditate inparalogs.\nExample: 0.5 means one of the two sequences could be two times longer than the other\n 0 means no length difference allowed; 1 means any length difference allowed. Default=0.5', default=0.5)
    parser.add_argument('-mgs', '--max-gene-per-sp', type=int, required=False, help='Limits the maximum number of genes per species in the multi-species output table. This option reduces the verbosity of the multi-species output file when comparing a high number of species (especially eukaryotes). Default=10', default=30)
    parser.add_argument('-sm', '--skip-multi-species', required=False, help='Skip the creation of multi-species ortholog groups.', default=False, action='store_true')
    parser.add_argument('-op', '--output-pairs', required=False, help='Output a text file with all the orthologous relations.', default=False, action='store_true')
    parser.add_argument('-qfo11', '--qfo-2011', required=False, help='Output a text file with all the orthologous relations formatted to be uploaded to the QfO benchmark service.\nNOTE: implies --output-pairs', default=False, action='store_true')
    parser.add_argument('-ka', '--keep-raw-alignments', required=False, help='Do not delete raw MMseqs2 alignment files. NOTE: this will triple the space required for storing the results.', default=False, action='store_true')
    parser.add_argument('-rs', '--remove-old-species', required=False, help='Remove alignments and pairwise ortholog tables related to species used in a previous run. This option should be used when updating a run in which some input proteomes were modified or removed.', default=False, action='store_true')
    parser.add_argument('-un', '--update-input-names', required=False, help='Remove alignments and pairwise ortholog tables for an input proteome used in a previous which file name conflicts with a newly added species. This option should be used when updating a run in which some input proteomes or their file names were modified.', default=False, action='store_true')
    parser.add_argument('-d', '--debug', required=False, help='Output debug information.', default=False, action='store_true')
    args = parser.parse_args()
    return (args, parser)



def check_gcc():
    '''Check that gcc is installed'''
    from sh import which
    shOut = which('gcc')
    #print('Check gcc (c++) compiler...')
    #print(shOut)
    if not shOut is None:
        from sh import gcc
        version = str(gcc('--version'))
        #print(version)
        return (version, True)
    else:
        print('ERROR: you must install gcc version 5.1 or above before continuing')
        return (None, False)



def check_quick_multiparanoid_installation(gccVer=None, gccOk=False):
    '''Check that the C++ files have been compiled.'''
    quickparaRoot = orthogroups.get_quick_multiparanoid_src_dir()
    # check for the existance of qa1
    qaPath = os.path.join(quickparaRoot, 'qa1')
    qa1ok = True
    if not os.path.isfile(qaPath):
        qa1ok = False
    # check for the existance of qa2
    qaPath = os.path.join(quickparaRoot, 'qa2')
    qa2ok = True
    if not os.path.isfile(qaPath):
        qa2ok = False
    # if one of the binaries is missing then compile
    if not (qa1ok and qa2ok):
        if not gccOk:
            sys.stderr.write('\nERROR: no gcc compiler was found in your system.\n')
            sys.stderr.write('Please, go to https://gcc.gnu.org\n')
            sys.stderr.write('And follow the instructions to install the latest version of GCC in your system.\n')
            sys.exit(-5)
        # continue and compile the binaries
        compile_quick_multiparanoid(quickparaRoot, gccVer)



def check_mmseqs_installation(root, debug=False):
    """Check if mmseqs has been installed."""
    binDir = os.path.join(root, 'bin/')
    zipDir = os.path.join(root, 'mmseqs2_src/')
    mmseqsPath = os.path.join(binDir, 'mmseqs')
    # copy the zip file if required
    if not os.path.isfile(mmseqsPath):
        ### Install MMseqs2 ###
        # check operative system
        OS = platform.system()
        isDarwin = True
        if OS == 'Linux':
            isDarwin = False
        elif OS == 'Darwin':
            isDarwin = True
        sys.stdout.write('\n\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-')
        print('\nInstalling MMseqs2 binaries for {:s} system...'.format(OS))
        print('Try the AVX2 version...')
        zipPath = ""
        zipName = ""
        if isDarwin:
            zipName = "mmseqs_macos_avx2.zip"
            zipPath = os.path.join(zipDir, zipName)
        else:
            zipName = "mmseqs_linux_avx2.zip"
            zipPath = os.path.join(zipDir, zipName)
        # define the unzipped and final paths
        unzippedPath = os.path.join(binDir, zipName.rsplit(".", 1)[0])
        # unzip the file
        with zipfile.ZipFile(zipPath, "r") as zip_ref:
            zip_ref.extractall(binDir)
        # final mmseqs path
        if os.path.isfile(mmseqsPath):
            os.remove(mmseqsPath)
        # rename the unzipped file and change the permissions
        move(unzippedPath, mmseqsPath)
        # change the permission
        os.chmod(mmseqsPath, 0o751)
        # Check if AVX2 is supported
        mmseqsCmd = mmseqsPath
        process = subprocess.Popen(mmseqsCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_val, stderr_val = process.communicate() #get stdout and stderr
        process.wait()
        # check if an error happened
        mmseqsVersion = "AVX2"
        if len(stderr_val.decode()) > 0:
            print("INFO: Your system does not support the AVX2 instruction set, the SEE4.1 version of MMseqs will be installed...")
            mmseqsVersion = "SSE4.1"
            zipPath = ""
            if isDarwin:
                zipName = "mmseqs_macos_sse41.zip"
                zipPath = os.path.join(zipDir, zipName)
            else:
                zipName = "mmseqs_linux_sse41.zip"
                zipPath = os.path.join(zipDir, zipName)
            # define the unzipped and final paths
            unzippedPath = os.path.join(binDir, zipName.rsplit(".", 1)[0])
            # unzip the file
            with zipfile.ZipFile(zipPath, "r") as zip_ref:
                zip_ref.extractall(binDir)
            # remove binaries if they already exists
            if os.path.isfile(mmseqsPath):
                os.remove(mmseqsPath)
            # rename the unzipped file and change the permissions
            move(unzippedPath, mmseqsPath)
            # change the permission
            os.chmod(mmseqsPath, 0o751)
        # write the final info
        print("The MMseqs2 ({:s}) binaries were installed installed in\n{:s}".format(mmseqsVersion, mmseqsPath))
        sys.stdout.write('-#-#-#-#-#-#- DONE -#-#-#-#-#-#-\n\n')
    else:
        if debug:
            print("MMseqs2 binaries found in\n{:s}".format(mmseqsPath))



def compile_quick_multiparanoid(srcDir, gccVer):
    """Compile the program for multi-species orthology."""
    sys.stderr.write('\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-')
    print('\nCompiling the program for multi-species orthology...')
    print('GCC:\t{:s}'.format(str(gccVer)))
    # compile inpyranoid
    from sh import make
    # move into the src directory
    prevDir = os.getcwd()
    os.chdir(srcDir)
    # first remove any previously compiled file
    shOut = make('clean')
    print('Cleaning any previous installation...')
    print(shOut)
    print('Make...')
    shOut = make('qa')
    print(shOut)
    # return to the previous directory
    os.chdir(prevDir)
    print('-#-#-#-#-#-# DONE #-#-#-#-#-#-')



def cleanup(rootDir=os.getcwd(), debug=False):
    """Remove not required files."""
    if debug:
        print('cleanup :: START')
        print('Root directory:\t%s'%rootDir)
    # list with ending 'wildcard' to detect files to be removed
    wildList = ['.c', '.cpp', '.h', '.o', '.so']
    # traverse the directory
    for dirPath, dirNames, fNames in os.walk(rootDir):
        #if dirPath == rootDir:
        #    continue
        # remove temporary input files
        if os.path.basename(dirPath) == 'mapped_input':
            for f in fNames:
                tmpPath = '%s/%s'%(dirPath, f)
                os.remove(tmpPath)
            continue
        # check if the file name is inclued in the wildcard
        for f in fNames:
            for wcard in wildList:
                if f.endswith(wcard):
                    tmpPath = '%s/%s'%(dirPath, f)
                    os.remove(tmpPath)
            # check if it is mmseqs database file
            if fnmatch.fnmatch(f, '*.mmseqs2db*'):
                tmpPath = '%s/%s'%(dirPath, f)
                os.remove(tmpPath)



def get_mmseqs_supported_version(readmePath):
    """Read a text file and extract the Mmseqs version"""
    if not os.path.isfile(readmePath):
        sys.stderr.write('\nERROR: the file with MMseqs2 version information was not found.\n')
        sys.stderr.write('\nProvided path:\n{:s}\n'.format(readmePath))
        sys.exit(-5)
    # open and read the readme file
    fd = open(readmePath, 'r')
    # skip the first 2 lines...
    fd.readline()
    fd.readline()
    vLine = fd.readline().strip()
    fd.close()
    # return the supported version
    return vLine



def get_input_paths(inDir, debug=False):
    """Check that at least 2 files are provided."""
    # associate a path to each file name
    fname2path = {}
    for f in os.listdir(inDir):
        if f == '.DS_Store':
            continue
        else:
            tmpPath = os.path.join(inDir, f)
            if os.path.isfile(tmpPath):
                fname2path[f] = tmpPath
    # check that at least two input files were provided
    if len(fname2path) < 2:
        sys.stderr.write('ERROR: the directory with the input files only contains {:d} ({:s}) files\nPlease provide at least 2 proteomes.\n'.format(len(fname2path), '\n'.join(list(fname2path.keys()))))
        sys.exit(-5)
    # sort the dictionary by key to avoid different sorting
    # on different systems due to os.listdir()
    sortedDict = dict(sorted(fname2path.items()))
    del fname2path
    return list(sortedDict.values())



def write_run_info_file(infoDir, infoDict, debug=False):
    """Write a file summarizing the run settings."""
    if debug:
        print("write_run_info_file :: START")
        print("Directory with run info: {:s}".format(infoDir))
    infoFile = os.path.join(infoDir, "run_info.txt")
    ofd = open(infoFile, "w")
    for info, val in infoDict.items():
        ofd.write("{:s}\t{:s}\n".format(info, val))
    ofd.close()



def set_project_id(rId: str="", runsDir: str=os.getcwd(), debug=False):
    """Generates a run ID if required."""
    if debug:
        print("set_project_id :: START")
        print("Run name:\t{:s}".format(rId))
        print("Runs directory: {:s}".format(runsDir))
    if not os.path.isdir(runsDir):
        sys.stderr.write('\nERROR: the directory runs does not exist.\n')
        sys.exit(-2)
    # create the runid if required
    if len(rId) == 0:
        ltime = time.localtime(time.time())
        # the id should include:
        # day of the month: tm_mday
        # month of the year: tm_mon
        # 2-digits year: tm_year
        # hours: tm_hour
        # minutes: tm_min
        # seconds: tm_sec
        startTime = "{:d}{:d}{:s}{:d}{:d}{:d}".format(ltime.tm_mday, ltime.tm_mon, str(ltime.tm_year)[2:], ltime.tm_hour, ltime.tm_min, ltime.tm_sec)
        rId = "run_{:s}".format(startTime)
    else: # check that the ID was not previously used
        for f in os.listdir(runsDir):
            if f.startswith('.DS_'):
                continue
            tmpPath = os.path.join(runsDir, f)
            if os.path.isdir(tmpPath):
                if f == rId:
                    sys.stderr.write('\nERROR: the run ID {:s} was used in a previous run.\n'.format(f))
                    sys.stderr.write('Remove the previous run or choose a different run ID.\n')
                    sys.exit(-5)
    return rId



########### MAIN ############
def main():
    # check that everything was installed correctly
    root = os.path.dirname(os.path.abspath(__file__))
    root += '/'
    # settings for the hashing algorithm
    hashAlgo = "sha256"
    hashBits = 256
    # Will contain information to be printed in the info file
    infoDict = {}

    #### FORCE IT TO OK
    # check_quick_multiparanoid_installation('FORCED TO TRUE: Sytem specific GCC version', True)
    ####

    # start measuring the execution time
    ex_start = time.perf_counter()
    #Get the parameters
    args, parser = get_params()
    #start setting the needed variables
    debug = args.debug
    # check MMseqs2 installation
    check_mmseqs_installation(root, debug=debug)
    inDir = None
    if args.input_directory is not None:
        inDir = "{:s}/".format(os.path.realpath(args.input_directory))
    # output dir
    outDir = '{:s}'.format(os.path.realpath(args.output_directory))
    # check that the input directory has been provided
    if (inDir is None):
        sys.stderr.write('\nERROR: no input species.\n')
        parser.print_help()
    # obtain input paths
    inPaths = get_input_paths(inDir, debug=debug)

    # Pair-wise tables directory
    pairwiseDbDir = os.path.join(outDir, "orthologs_db/")
    systools.makedir(pairwiseDbDir)
    # Runs directory
    runsDir = os.path.join(outDir, "runs/")
    systools.makedir(runsDir)
    # set the update variable
    update_run = False
    # check that the snapshot file exists
    snapshotFile = os.path.join(outDir, "snapshot.tsv")
    if update_run:
        # check that it is not the first run
        if not os.path.isfile(snapshotFile):
            sys.stderr.write("\nWARNING: not snapshot file found. The run will considered as the first one.\n")
            update_run = False
    else:
        # force the variable to true if a snapshot exists
        if os.path.isfile(snapshotFile):
            update_run = True

    # Optional directories setup
    alignDir = None
    if args.shared_directory is not None:
        alignDir = "{:s}/".format(os.path.realpath(args.shared_directory))
    else:
        alignDir = os.path.join(outDir, 'alignments/')
        systools.makedir(alignDir)
    dbDirectory = None
    if args.mmseqs_dbs is not None:
        dbDirectory = "{:s}/".format(os.path.realpath(args.mmseqs_dbs))
    else:
        dbDirectory = os.path.join(outDir, "mmseqs2_databases/")
    threads = args.threads
    #coff = args.cutoff
    coff = 40
    owOrthoTbls = args.overwrite_tables
    skipMulti = args.skip_multi_species
    runMode = args.mode
    maxGenePerSp = args.max_gene_per_sp
    # set the sensitivity value for MMseqs2
    sensitivity = 4.0 # default
    if runMode == 'sensitive':
        sensitivity = 6.0
    elif runMode == 'fast':
        sensitivity = 2.5
    elif runMode == 'most-sensitive':
        sensitivity = 7.5
    overwrite = args.overwrite
    if overwrite:
        owOrthoTbls = True
        # remove all the mmseqs2 index files
        if os.path.isdir(dbDirectory):
            for f in os.listdir(dbDirectory):
                fpath = os.path.join(dbDirectory, f)
                try:
                    if os.path.isfile(fpath):
                        os.unlink(fpath)
                    elif os.path.isdir(fpath): rmtree(fpath)
                except Exception as e:
                    print(e)

    # set sensitivity using a user spcified value if needed
    if args.sensitivity:
        if 1. <= args.sensitivity <= 7.5:
            sensitivity = round(args.sensitivity, 1)
            print('WARNING: the run mode \'%s\' will be overwritten by the custom MMseqs sensitivity value of %s.\n'%(runMode, str(args.sensitivity)))
        else:
            sys.stderr.write('\nERROR: the sensitivity parameter must have a value between 1.0 and 7.5\n')

    # set the maximum length difference allowed if difference from default
    if args.max_len_diff != 0.5:
        if not (0. <= args.max_len_diff <= 1.0):
            sys.stderr.write('\nERROR: the length difference ratio must have a value between 0 and 1.\n')
    # set the variable to control the creation of orthologous pairs
    output_relations = args.output_pairs
    if args.qfo_2011:
        output_relations = True
    # set the variable for MMseqs2 database indexing
    idx_dbs = True
    if args.no_indexing:
        idx_dbs = False

    # directory with header and species names mapping
    runID = set_project_id(rId=args.project_id, runsDir=runsDir, debug=debug)
    runDir = os.path.join(runsDir, runID)
    # Pair-wise tables directory
    tblDir = os.path.join(runDir, "pairwise_orthologs/")
    systools.makedir(tblDir)
    # Directory with ortholog groups
    multiOutDir = os.path.join(runDir, 'ortholog_groups/')
    systools.makedir(multiOutDir)
    # variable ued in the update of input files
    updateInputNames = args.update_input_names
    removeOldSpecies = args.remove_old_species
    # name for multispecies groups
    multiSpeciesClstrNameAll = 'ortholog_groups.tsv'

    print('\nSonicParanoid will be executed with the following parameters:')
    print('Run ID:\t{:s}'.format(runID))
    print('Run directory: {:s}'.format(runDir))
    print('Input directory: {:s}'.format(inDir))
    print('Input proteomes: {:d}'.format(len(inPaths)))
    print('Output directory: {:s}'.format(outDir))
    print('Alignments directory: {:s}'.format(alignDir))
    print('Pairwise tables directory: {:s}'.format(tblDir))
    print('Directory with ortholog groups: {:s}'.format(multiOutDir))
    print('Pairwise tables database directory: {:s}'.format(pairwiseDbDir))
    print('Runs directory: {:s}'.format(runsDir))
    print('Update run:\t{:s}'.format(str(update_run)))
    print('Create pre-filter indexes:\t{:s}'.format(str(idx_dbs)))
    print('Complete overwrite:\t{:s}'.format(str(overwrite)))
    print('Re-create ortholog tables:\t{:s}'.format(str(owOrthoTbls)))
    print('CPUs:\t{:d}'.format(threads))
    print('Run mode:\t%s (MMseqs2 s=%s)'%(runMode, str(sensitivity)))

    # populate the info dictionary
    infoDict["Date:"] = time.asctime(time.localtime(time.time()))
    infoDict["Run ID:"] = runID
    infoDict["Run directory:"] = runDir
    infoDict["Input directory:"] = inDir
    infoDict["Output directory:"] = outDir
    infoDict["Input proteomes:"] = str(len(inPaths))
    infoDict["MMseqs DB directory:"] = str(dbDirectory)
    infoDict["Skip MMseqs DB indexing:"] = str(args.no_indexing)
    infoDict["Alignment directory:"] = str(alignDir)
    infoDict["Pairwise tables DB directory:"] = str(pairwiseDbDir)
    infoDict["Directory with pairwise orthologs:"] = str(tblDir)
    infoDict["Directory with ortholog groups:"] = str(multiOutDir)
    infoDict["Cpus:"] = str(threads)
    infoDict["Update run:"] = str(update_run)
    infoDict["MMseqs sensitivity:"] = str(sensitivity)
    infoDict["Max length difference for in-paralogs:"] = str(args.max_len_diff)
    infoDict["Overwrite pair-wise ortholog tables:"] = str(args.overwrite_tables)
    infoDict["Complete overwrite:"] = str(args.overwrite)
    infoDict["Skip creation of ortholog groups:"] = str(args.skip_multi_species)
    if debug:
        infoDict["Directory with SonicParanoid runs:"] = str(runsDir)
        infoDict["Maximum gene per species in groups:"] = str(args.max_gene_per_sp)
        infoDict["QfO 2011 run:"] = str(args.qfo_2011)

    # Check if the run already exists
    spFile = pairsFile = mappedInputDir = None
    spMappingFile = hdrMappingFile = None
    # write the with information on the run
    write_run_info_file(runDir, infoDict, debug=debug)

    # New run
    if not update_run:
        if debug:
            print("First run!")
        # Compute digests
        digestDict, repeatedFiles = idmapper.compute_hash_parallel(inPaths, algo=hashAlgo, bits=hashBits, threads=threads, debug=debug)
        spFile, mappedInputDir, mappedInPaths = idmapper.map_hdrs_parallel(inPaths, outDir=runDir, digestDict=digestDict, idMapDict={}, threads=threads, debug=debug)
        # create the snapshot file
        copy(spFile, snapshotFile)
        # predict pairwise orthology
        spFile, pairsFile, requiredPairsDict = orthodetect.run_sonicparanoid2_multiproc(mappedInPaths, outDir=runDir, tblDir=pairwiseDbDir, threads=threads, alignDir=alignDir, mmseqsDbDir=dbDirectory, create_idx=idx_dbs, sensitivity=sensitivity, cutoff=coff, confCutoff=0.05, lenDiffThr=args.max_len_diff, overwrite_all=overwrite, overwrite_tbls=owOrthoTbls, update_run=update_run, keepAlign=args.keep_raw_alignments, debug=debug)
        # remap the pairwise relations
        remap.remap_pairwise_relations_parallel(pairsFile, runDir=runDir, orthoDbDir=pairwiseDbDir, threads=threads, debug=debug)

        # run multi-species clustering
        if not skipMulti:
            # copy sqltables
            sqlPaths = orthogroups.fetch_sql_files(rootDir=pairwiseDbDir, outDir=multiOutDir, pairsFile=pairsFile, coreOnly=False, debug=debug)
            print('Ortholog tables loaded for multi-species orthology:\t%d'%len(sqlPaths))
            sys.stdout.write('\nCreating ortholog groups...')
            multisp_start = time.perf_counter()
            quickparaRoot = orthogroups.get_quick_multiparanoid_src_dir()
            #create the multi-species clusters
            orthoGrps, grpsStatPaths = orthogroups.run_quickparanoid(sqlTblDir=multiOutDir, outDir=multiOutDir, sharedDir=runDir, srcDir=quickparaRoot, outName=multiSpeciesClstrNameAll, speciesFile=spFile, maxGenePerSp=maxGenePerSp, debug=debug)
            # load the mapping information
            id2SpDict, new2oldHdrDict = idmapper.load_mapping_dictionaries(runDir=runDir, debug=debug)
            # remap the genes in orthogroups
            idmapper.remap_orthogroups(inTbl=orthoGrps, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, debug=debug)
            # remap the flat multi-species table
            flatGrps = os.path.join(multiOutDir, "flat.{:s}".format(os.path.basename(orthoGrps)))
            idmapper.remap_flat_orthogroups(inTbl=flatGrps, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, debug=debug)
            # remap file with not grouped genes
            notGroupedPath = os.path.join(multiOutDir, "not_assigned_genes.{:s}".format(os.path.basename(orthoGrps)))
            idmapper.remap_not_grouped_orthologs(inPath=notGroupedPath, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, debug=debug)
            # remap stats
            idmapper.remap_group_stats(statPaths=grpsStatPaths, id2SpDict=id2SpDict, removeOld=True, debug=debug)
            sys.stdout.write('Ortholog groups creation elapsed time (seconds):\t{:s}\n'.format(str(round(time.perf_counter() - multisp_start, 3))))
    # Run update
    else:
        if debug:
            print("Update run!")
        # update the run info
        spFile, mappedInputDir, mappedInPaths = idmapper.update_run_info(inPaths=inPaths, outDir=runDir, oldSpFile=snapshotFile, algo='sha256', bits=256, threads=threads,  updateNames=updateInputNames, removeOld=removeOldSpecies, overwrite=(overwrite or owOrthoTbls), debug=debug)
        # remove obsolete results
        # sys.exit("DEBUG :: sonic_paranoid :: update_run")
        # run sonicparanoid
        # perform alignments and predict orthologs
        spFile, pairsFile, requiredPairsDict = orthodetect.run_sonicparanoid2_multiproc(mappedInPaths, outDir=runDir, tblDir=pairwiseDbDir, threads=threads, alignDir=alignDir, mmseqsDbDir=dbDirectory, create_idx=idx_dbs, sensitivity=sensitivity, cutoff=coff, confCutoff=0.05, lenDiffThr=args.max_len_diff, overwrite_all=overwrite, overwrite_tbls=owOrthoTbls, update_run=update_run, keepAlign=args.keep_raw_alignments, debug=debug)
        # remap the pairwise relations
        remap.remap_pairwise_relations_parallel(pairsFile, runDir=runDir, orthoDbDir=pairwiseDbDir, threads=threads, debug=debug)

        # run multi-species clustering
        if not skipMulti:
            # copy sqltables
            sqlPaths = orthogroups.fetch_sql_files(rootDir=pairwiseDbDir, outDir=multiOutDir, pairsFile=pairsFile, coreOnly=False, debug=debug)
            print('Ortholog tables loaded for multi-species orthology:\t%d'%len(sqlPaths))
            sys.stdout.write('\nCreating ortholog groups...')
            multisp_start = time.perf_counter()
            quickparaRoot = orthogroups.get_quick_multiparanoid_src_dir()
            #create the multi-species clusters
            orthoGrps, grpsStatPaths = orthogroups.run_quickparanoid(sqlTblDir=multiOutDir, outDir=multiOutDir, sharedDir=runDir, srcDir=quickparaRoot, outName=multiSpeciesClstrNameAll, speciesFile=spFile, maxGenePerSp=maxGenePerSp, debug=debug)
            # load the mapping information
            id2SpDict, new2oldHdrDict = idmapper.load_mapping_dictionaries(runDir=runDir, debug=debug)
            # remap the genes in orthogroups
            idmapper.remap_orthogroups(inTbl=orthoGrps, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, debug=debug)
            # remap the flat multi-species table
            flatGrps = os.path.join(multiOutDir, "flat.{:s}".format(os.path.basename(orthoGrps)))
            idmapper.remap_flat_orthogroups(inTbl=flatGrps, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, debug=debug)
            # remap file with not grouped genes
            notGroupedPath = os.path.join(multiOutDir, "not_assigned_genes.{:s}".format(os.path.basename(orthoGrps)))
            idmapper.remap_not_grouped_orthologs(inPath=notGroupedPath, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, debug=debug)
            # remap stats
            idmapper.remap_group_stats(statPaths=grpsStatPaths, id2SpDict=id2SpDict, removeOld=True, debug=debug)
            sys.stdout.write('Ortholog groups creation elapsed time (seconds):\t{:s}\n'.format(str(round(time.perf_counter() - multisp_start, 3))))

    # remap species pairs file
    # load the mapping info
    id2SpDict, new2oldHdrDict = idmapper.load_mapping_dictionaries(runDir=runDir, debug=debug)
    # create the pairs file with the original species names
    pairsFileRemapped = os.path.join(runDir, "species_pairs_remapped.txt")
    with open(pairsFileRemapped, "w") as ofd:
        with open(pairsFile, "r") as ifd:
            for ln in ifd:
                sp1, sp2 = ln[:-1].split("-", 1)
                ofd.write("{:s}-{:s}\n".format(id2SpDict[sp1], id2SpDict[sp2]))

    # generate file with pairwise relations
    if output_relations:
        # output directory for ortholog realtions
        relDict = os.path.join(runDir, "ortholog_relations")
        systools.makedir(relDict)
        # ALL
        orthoRelName = 'ortholog_pairs.{:s}.tsv'.format(runID)
        if args.qfo_2011:
            orthoRelName = 'ortholog_pairs_benchmark.{:s}.tsv'.format(runID)
        # Extract pairs
        orthodetect.extract_ortholog_pairs(rootDir=os.path.join(runDir, "pairwise_orthologs"), outDir=relDict, outName=orthoRelName, pairsFile=pairsFileRemapped, coreOnly=False, singleDir=True, tblPrefix="", splitMode=args.qfo_2011, debug=debug)

    ex_end = round(time.perf_counter() - ex_start, 3)
    sys.stdout.write('\nTotal elapsed time (seconds):\t{:0.3f}\n'.format(ex_end))

    # sys.exit('DEBUG :: sonic_paranoid.py :: before cleanup')

    # remove not required files
    cleanup(rootDir=runDir, debug=debug)
    # cleanup directory with alignments
    cleanup(rootDir=alignDir, debug=debug)
    # cleanup MMseqs2 DB files
    cleanup(rootDir=dbDirectory, debug=debug)



if __name__ == "__main__":
    main()
