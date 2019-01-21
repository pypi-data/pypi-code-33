#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a program done by Claudia Millan

# Import libraries
# Python Modules
import ConfigParser
from collections import Counter
import cPickle
import copy
import itertools
import operator
import os
import shutil
import psutil
import sys
import time
import traceback
import subprocess
from termcolor import colored
from multiprocessing import Pool
# Our own modules
import ALIXE
import alixe_library as al
import Bioinformatics3
import Bio.PDB
import SELSLIB2


# Reading input from command line
if len(sys.argv) == 1:
    print "\nUsage for ARCIMBOLDO runs: autoalixe.py name.bor -mode -ver [additional arguments]"
    print "\nUsage for general solutions: autoalixe.py folder_path -mode -ver [additional arguments]"

    print "\n-mode=fish one_step one_step_parallel two_steps combi ens1_fragN cc_analysis"
    print "\n-ver=fortran or python Use the fortran or the python version of phstat to cluster"
    print "\n\nAdditional arguments:"
    print "\n-path_combi=path Use this in combi mode to perform clustering between this run and the one given in name.bor"
    print "\n-path=path to the fortran PHSTAT executable, only if -ver=fortran"
    print "\n-ref=path_reference_solution Use this phase file as reference for mode fish"
    print "\n-tols=integer,integer From 0 to 90 phase difference tolerance in degrees."
    print "                        First is used for one_step, one_step_parallel, ens1_fragn or fish, second, for combi or two_steps"
    print "\n-res=float Resolution to use in the phase comparison and merging"
    print "\n-fom_sorting=CC Figure of merit to sort the references in first steps. Can be CC, LLG or ZSCORE"
    print "\n-lim=integer Hard limit on the number of solutions to be processed by phstat. Default is 1000"
    print "\n-exp=boolean If True, expansions of the clusters will be performed sequentially. Default is False"
    print "\n-orisub=sxos Subroutine to compute shifts for polar space groups. Can be sxos or sxosfft"
    print "\n-weight=e Weight to apply to compare the phases. Can be e (e-value) or f (amplitudes)"
    print "\n-fragment=1 Folder to check for ARCIMBOLDO_LITE runs (e.g. ens1_frag1). Can be any integer in the range of the number of fragments"
    sys.exit()

# Variables initialization
now = time.time()
type_run = ' '  # To know if clustering is to be applied to an ARCIMBOLDO,BORGES or SHREDDER run
cycles = 3  # cycles for phstat clustering
resolution = 2.0  # resolution for phstat clustering
tolerance_first_round = 60  # First clustering attempt
tolerance_second_round = 88  # Second clustering attempt
global_tolerance = 75  # Only if we fish with a single or a set of references against the pool
ent_present = False
seed = 0  # Also only needed if phstat used is fortran
wd = os.getcwd()
reference_hkl = None  # At the moment this is not working, but I want to maintain the variable until I solve it!
fom_sorting = 'CC'  # can be CC, LLG or ZSCORE
folder_mode = False
path_sol= sys.argv[1]
if os.path.isdir(path_sol):
    folder_mode = True
mode = None
phstat_version = None
path_phstat = None
reference_to_fish = None
ent_filename = None
hkl_filename = None
expansions = False
path_combi = None
orisub = 'sxos'
weight = 'e'
hard_limit_phs = 0
shelxe_line_alixe = "-m5 -a0 "
shelxe_path = 'shelxe'
n_cores = (psutil.cpu_count(logical=False)-1) # default is the number of cores -1

if len(sys.argv) > 2:
    # Read the options
    for i in range(2, len(sys.argv)):
        option = sys.argv[i]
        if option.startswith("-mode"):
            mode = option[6:]
            if mode not in ('fish','cc_analysis','one_step','one_step_parallel','two_steps','combi') and not mode.startswith('ens1_frag'):
                print 'Sorry, you need to provide a valid mode'
                sys.exit(1)
        if option.startswith("-ref"):
            reference_to_fish = option[5:]
            if not os.path.exists(reference_to_fish):
                print "Sorry, you need to provide a valid path for the reference"
                sys.exit(1)
            else:
                print "\nFile ", reference_to_fish, "is going to be used for fishing"
        if option.startswith("-path_combi"):
            path_combi = option[12:]
        if option.startswith("-ver"):
            phstat_version = option[5:]
            print "\nPrototype used in clustering is the one in ", phstat_version
        if option.startswith("-path") and not (option.startswith("-path_combi")):
            path_phstat = option[6:]
        if option.startswith("-lim"):
            hard_limit_phs = int(option[5:])
            print "Hard limit set to ", hard_limit_phs
        if option.startswith("-exp"):
            expansions = bool(option[5:])
            print "Expansions set to ", expansions
        if option.startswith("-res"):
            resolution = float(option[5:])
            print "Resolution set to ",resolution
        if option.startswith('-fom'):
            selection=option[13:]
            if selection not in ('CC','LLG','ZSCORE'):
                print 'Sorry, only CC, LLG or ZSCORE can be used for sorting'
                sys.exit(1)
            else:
                fom_sorting=selection
        if option.startswith("-tols"):
            tolerances = option[6:].split(',')
            tolerance_first_round = int(tolerances[0])
            tolerance_second_round = int(tolerances[1])
            global_tolerance = tolerance_first_round
        if option.startswith('-orisub'):
            orisub=option[8:]
        if option.startswith('-weight'):
            weight = option[8:]
            #print 'SHERLOCK weight',weight
        if option.startswith('-ncores'):
            n_cores = int(option[8:])
            print '\n Warning: This run is going to be executed on ',n_cores,' CPUs'
        if option.startswith('-shelxe_line'):
            shelxe_line_alixe=option[13:]
        if option.startswith('-fragment'):
            fragment=int(option[10:])


if phstat_version == 'fortran' and path_phstat == None:
    print colored("\nPlease, to use the fortran phstat, give the path to the fortran PHSTAT in the option -path", 'red')
    sys.exit(1)
if mode == None:
    print colored("\nThe mode keyword is mandatory. Please provide one of the following modes: fish full one_step one_step_parallel two_steps combi cc_analysis",'red')
    sys.exit(1)
if phstat_version == None:
    print colored("\nThe version keyword is mandatory. Please provide fortran or python in the -ver keyword",'red')
    sys.exit(1)
if mode == 'fish' and reference_to_fish == None:  # reference_to_fish=None
    print colored("\nIf you use fish mode, you need to provide an external reference in the -ref keyword",'red')
    sys.exit(1)
if mode == 'combi' and path_combi == None:
    print colored("\nIf you use combi mode, you need to provide another bor path in the -path_combi keyword",'red')
    sys.exit(1)

# Check if the CLUSTERING folder exists and generation otherwhise
clust_fold = os.path.join(wd, 'CLUSTERING/')
try:
    os.mkdir(clust_fold)
except OSError:
    exctype, value = sys.exc_info()[:2]
    if str(value).startswith("[Errno 17] File exists:"):  # Then the folder exists
        print "\n CLUSTERING folder was already present. Files will be removed to start from the scratch"
        # NOTE: This is what makes sense if we already have the phs created and we just need to put them there.
        shutil.rmtree(clust_fold, ignore_errors=True)
        os.mkdir(clust_fold)
log_file = open(os.path.join(clust_fold, 'autoalixe.log'), 'w')

if not folder_mode:
    # Read the bor file and retrieve the information needed for the run
    Config = ConfigParser.ConfigParser()
    Config.read(path_sol)
    sections = Config.sections()
    multiproc = False
    if not Config.has_section("CONNECTION"):
        multiproc = True
    else:
        computing = Config.get("CONNECTION", "distribute_computing")
        if computing!='multiprocessing':
            # NOTE: The operations related with reading the setup bor and the like are OK only for OUR setup
            # In condor we can read the local one from the setup.bor
            path_setup = Config.get("CONNECTION", "setup_bor_path")
            Config2 = ConfigParser.ConfigParser()
            Config2.read(path_setup)
            try:
                shelxe_path = Config2.get("LOCAL", "path_local_shelxe")
            except:
                print "\nThe bor file did not contain a LOCAL section, assuming shelxe is in the path"
                shelxe_path = 'shelxe'
        else:
            multiproc=True

    if multiproc == True:
        try:
            shelxe_path = Config.get("LOCAL", "path_local_shelxe")
        except:
            print "\nThe bor file did not contain a LOCAL section, assuming shelxe is in the path"
            shelxe_path = 'shelxe'

    # Save information from GENERAL section
    wd = Config.get("GENERAL", "working_directory")
    hkl_filename = Config.get("GENERAL", "hkl_path")
    if Config.has_option("GENERAL", "ent_path"):
        ent_filename = Config.get("GENERAL", "ent_path")
        ent_present = True

    # Put a copy of the hkl file in CLUSTERING and rename it
    shutil.copyfile(hkl_filename, clust_fold + "reflection.hkl")
    print "\nCopying the reflection file " + hkl_filename
    if ent_present:
        shutil.copyfile(ent_filename, clust_fold + "final_solution.ent")
        print "\nYou have an ent file, a post-mortem analysis of MPE will be performed"
        print "\nCopying the ent file " + ent_filename

    # Retrieve shelxe line and perform operations dependant on each type of run
    for section in sections:
        if section == "ARCIMBOLDO":
            name_job = Config.get("ARCIMBOLDO", "name_job")
            shelxe_line = al.get_shelxe_line_from_html_output(name_job, wd)
            if ent_present:
                shelxe_line = shelxe_line + " -x"
            shelxe_line_alixe = al.change_shelxe_line_for_alixe(shelxe_line)
            print "\nYou are executing ALIXE on an ARCIMBOLDO run"
            topexp = al.get_topexp_from_html_output(name_job, wd)
            type_run = 'ARCIMBOLDO'
            break
        elif section == "ARCIMBOLDO-BORGES":
            name_job = Config.get("ARCIMBOLDO-BORGES", "name_job")
            shelxe_line = al.get_shelxe_line_from_html_output(name_job, wd)
            if ent_present:
                shelxe_line = shelxe_line + " -x"
            shelxe_line_alixe = al.change_shelxe_line_for_alixe(shelxe_line)
            print "\nYou are executing ALIXE on an ARCIMBOLDO_BORGES run"
            type_run = 'BORGES'
            topexp = al.get_topexp_from_html_output(name_job, wd)
            break
        elif section == "ARCIMBOLDO-SHREDDER":
            name_job = Config.get("ARCIMBOLDO-SHREDDER", "name_job")
            print "\nYou are executing ALIXE on an ARCIMBOLDO_SHREDDER run"
            shelxe_line = al.get_shelxe_line_from_html_output(name_job, wd)
            # Read the method used to know if it is launching ARCIMBOLDO_BORGES or ARCIMBOLDO_LITEs
            shred_method = Config.get('ARCIMBOLDO-SHREDDER', 'SHRED_METHOD')
            if shred_method == 'spherical' or shred_method == 'secondary_structure':
                # Then inside the working directory an ARCIMBOLDO_BORGES folder should have been written
                print "The run in which you will use ALIXE is a ", shred_method, " SHREDDER "
                type_run = 'BORGES'
                wd = os.path.join(wd, 'ARCIMBOLDO_BORGES')
                topexp = al.get_topexp_from_html_output(name_job + "_BORGESARCI", wd)
            elif shred_method == 'sequential':
                print "Currently this mode is not supported ", shred_method
                type_run = 'ARCIMBOLDO'
                sys.exit(1)
            if ent_present: # Add the -x parameter to the shelxe line for post-mortem
                shelxe_line = shelxe_line + " -x"
            shelxe_line_alixe = al.change_shelxe_line_for_alixe(shelxe_line)
    if type_run == '':
        print "Sorry, you didn't provide any supported bor format. Autoalixe will end now"
        sys.exit(1)
else:
    list_pdbs=[]
    list_input_files = os.listdir(path_sol)
    dict_sorted_input={'0':[]}
    list_phs=[]
    list_pdb_ori=[]
    list_pda=[]
    for inp in list_input_files:
        fullpathinp = os.path.join(path_sol,inp)
        fullpathclu = os.path.join(clust_fold,inp)
        if inp.endswith('.phs'):
            #dict_sorted_input['0'].append(inp)
            shutil.copy(fullpathinp,fullpathclu)
            list_phs.append(fullpathclu)
        elif inp.endswith('.pdb'):
            shutil.copy(fullpathinp, fullpathclu)
            list_pdb_ori.append(fullpathclu)
        elif inp.endswith('.hkl'):
            hkl_filename = os.path.join(path_sol,inp)
        elif inp.endswith('.ent'):
            shelxe_line_alixe = shelxe_line_alixe+' -x'
            ent_present = True
            ent_filename = os.path.join(path_sol,inp)
    if hkl_filename==None:
        print 'Sorry, you need to provide the data in SHELX hkl format. Include it in the input folder '
        sys.exit(0)
    if len(list_phs)==0:
        print '\nYou did not provide phase files, they will be automatically generated using the data '
        info_frag_txt=open(os.path.join(clust_fold,'info_single_frags'),'w')
        info_frag_txt.write('%-25s %-10s %-15s %-15s %-15s %-10s %-10s %-10s\n' % ('Name','Size','InitCCshelx','wMPE_initial','wMPE_final','ShiftXent','ShiftYent','ShiftZent'))
        for ele in list_pdb_ori:
            print 'Linking ',ele
            list_pda.append(ele)
            try:
                os.link(ele,ele[:-4]+'.pda')
            except:
                print "Error"
                print sys.exc_info()
            print '\nNow we will run SHELXE '
            name_shelxe = os.path.basename(ele[:-4])
            try:
                shutil.copy(hkl_filename,os.path.join(clust_fold,name_shelxe+'.hkl'))
            except:
                print "Error"
                print sys.exc_info()
            if ent_present:
                try:
                    shutil.copy(ent_filename, os.path.join(clust_fold,name_shelxe + '.ent'))
                except:
                    print "Error"
                    print sys.exc_info()
            output=al.phase_fragment_with_shelxe(shelxe_line_alixe, name_shelxe, clust_fold, shelxe_path)
            print output
            # TODO: we want to check some things about our fragments so that we can use this info later
            initcc_frag=al.extract_INITCC_shelxe(output)
            shift_shelx = al.extract_shift_from_shelxe(output)
            wmpe_list = al.extract_wMPE_shelxe(os.path.join(clust_fold,name_shelxe + '.lst'))
            wmpe_bef_demod = wmpe_list[0]
            wmpe_after_demod = wmpe_list[2]
            # check also the size of the fragment
            oristru = Bioinformatics3.get_structure(os.path.basename(ele)[:-4], ele[:-4]+'.pda')
            list_atoms = Bio.PDB.Selection.unfold_entities(oristru, 'A')
            list_ca = [atom for atom in list_atoms if atom.id == 'CA']
            size = len(list_ca)
            info_frag_txt.write(
                '%-25s %-10s %-15s %-15s %-15s %-10s %-10s %-10s\n' % (name_shelxe, size, initcc_frag,
                                                                       wmpe_bef_demod, wmpe_after_demod,shift_shelx[0],
                                                                       shift_shelx[1],shift_shelx[2]))

        list_pdbs=list_pda
        del info_frag_txt
    else:
        print '\nYou did provide phase files, those will be used for the phase clustering'
        quit()




if not folder_mode:
    # Now, depending on the type of run in the case of ARCIMBOLDOs, get the files, change their names, and copy them to the cluster folder
    if type_run == 'ARCIMBOLDO' and mode.startswith('ens1_frag'):
        fragment = mode[9:]
        print 'Getting the files from an ARCIMBOLDO run, from the folder of frag ', fragment
        dict_sorted_input = al.get_files_from_ARCIMBOLDO_for_ALIXE(wd=wd, clust_fold=clust_fold, fragment=fragment,
                                                                   hard_limit_phs=hard_limit_phs)
    elif type_run == 'ARCIMBOLDO' and (mode=='two_steps' or mode=='one_step' or mode=='one_step_parallel'): # then I take them from the first fragment only
        print 'Getting the files from the first fragment of an ARCIMBOLDO_LITE run'
        fragment = 1
        dict_sorted_input = al.get_files_from_ARCIMBOLDO_for_ALIXE(wd=wd, clust_fold=clust_fold, fragment=fragment,
                                                                   hard_limit_phs=hard_limit_phs)
    elif type_run == 'ARCIMBOLDO' and mode=='cc_analysis':
        print 'Getting the files from an ARCIMBOLDO_LITE run, fragment number ',fragment
        dict_sorted_input = al.get_files_from_ARCIMBOLDO_for_ALIXE(wd=wd, clust_fold=clust_fold, fragment=fragment,
                                                                   hard_limit_phs=hard_limit_phs)
    elif type_run == "BORGES":
        print 'Getting the files from a BORGES run'
        fragment = 1
        dict_sorted_input = {}
        for id_clu in os.listdir(os.path.join(wd, '9_EXP')):
            print "Getting files from cluster ", id_clu
            dict_sorted_input[id_clu] = al.get_files_from_9_EXP_BORGES(wd, clust_fold, cluster_id=id_clu, mode=9,
                                                                       hard_limit_phs=hard_limit_phs)  # Only the refined solutions
    print "\nCompleted linking of files in CLUSTERING folder"
    list_pdbs = al.list_files_by_extension(clust_fold, 'pda')

if len(list_pdbs)<=1:
    print 'SHERLOCK some problem with len(list_pdbs)',len(list_pdbs)
    sys.exit(1)

if not folder_mode:
    path_sym=os.path.join(wd, 'best.pda')
else:
    path_sym=os.path.join(clust_fold,list_pdbs[0]) # Just the first file
print '\nExtracting symmetry information from ',path_sym
file_pda = open(path_sym, 'r')
cryst_card = al.extract_cryst_card_pdb(file_pda.read())
# Get cell and sg_symbol and number
cell, sg_symbol = al.read_cell_and_sg_from_pdb(path_sym)  # Cell is a list of floats
sg_number = al.get_space_group_number_from_symbol(sg_symbol)
polar, origins = al.get_origins_from_sg_dictionary(sg_number)

# Check FOMs:
dictio_fragments = {}
list_pdbs = al.list_files_by_extension(clust_fold, 'pda')
for pdb in list_pdbs:
    dictio_fragments[pdb[:-4]] = {'rot_cluster': None, 'llg': None, 'zscore': None, 'initcc': None, 'efom': None,
                                  'pseudocc': None, 'list_MPE': None}


if not folder_mode:
    # From lst files
    dictio_fragments = al.get_FOMs_from_lst_files_in_folder(dictio_fragments=dictio_fragments, ent_present=ent_present)

    # From SUMs
    # We need to check whether there was gimble or not
    if type_run=='BORGES':
        if os.path.exists(os.path.join(wd,'8_GIMBLE')):
           gimble=True
        else:
           gimble=False
    else:
        gimble=False
    dictio_fragments = al.get_FOMs_from_sum_files_in_folder(wd=wd, clust_fold=clust_fold, dictio_fragments=dictio_fragments,
                                                            gimble=gimble, program=type_run,
                                                            fragment=fragment)

    # Generate the list of rotation clusters that are available for clustering
    list_rot_cluster = al.get_list_rotation_clusters_from_dictio_fragments(dictio_fragments)

    # Save information about FOMs of fragments in a file that is readable as a table
    file_fragments = open(clust_fold + "info_frag", 'w')
    if ent_present:
        file_fragments.write( '%-40s %-10s %-10s %-10s %-10s %-10s %-10s %-10s\n' % ('Name','LLG','Z-score','Rotcluster','InitCC','Efom','PseudoCC','wMPE'))
        for key in dictio_fragments.keys():
            file_fragments.write( '%-40s %-10s %-10s %-10s %-10s %-10s %-10s %-10s\n' % (os.path.basename(key),
                                                                                       dictio_fragments[key]['llg'],
                                                                                       dictio_fragments[key]['zscore'],
                                                                                       dictio_fragments[key]['rot_cluster'],
                                                                                       dictio_fragments[key]['initcc'],
                                                                                       dictio_fragments[key]['efom'],
                                                                                       dictio_fragments[key]['pseudocc'],
                                                                                       dictio_fragments[key]['list_MPE'][2]))
    else:
        file_fragments.write( '%-40s %-10s %-10s %-10s %-10s %-10s %-10s \n' % ('Name','LLG','Z-score','Rotcluster','InitCC','Efom','PseudoCC'))
        for key in dictio_fragments.keys():
            file_fragments.write( '%-40s %-10s %-10s %-10s %-10s %-10s %-10s \n' % (os.path.basename(key),
                                                                                       dictio_fragments[key]['llg'],
                                                                                       dictio_fragments[key]['zscore'],
                                                                                       dictio_fragments[key]['rot_cluster'],
                                                                                       dictio_fragments[key]['initcc'],
                                                                                       dictio_fragments[key]['efom'],
                                                                                       dictio_fragments[key]['pseudocc']))
    file_fragments.close()
else:
    list_rot_cluster = ['0']


# Generate the fake ins file
path_ins = os.path.join(clust_fold, 'symmetry.ins')
al.generate_fake_ins_for_shelxe(path_ins, cell, sg_number)

if mode == 'fish': # NOTE CM: check that this mode will still work with the new versions
    # Check if reference_to_fish is in the list, and add it in case it's not
    phs_files = al.list_files_by_extension(clust_fold, 'phs')
    ref_name = os.path.split(reference_to_fish)[1]
    ref = os.path.join(clust_fold, ref_name)
    ha_picado = False
    if ref not in phs_files:
        phs_files.append(ref)
        os.link(reference_to_fish, ref)
    if phstat_version == 'python':
        if len(phs_files) > 1000:
            print "The python phstat version does not support so many phs files in a single run"
            sys.exit(0)
        dictio_input_alixe = al.generate_input_dictio_for_ALIXE_by_references(phs_files, [ref])
        sg_number=al.get_space_group_number_from_symbol(sg_symbol)
        dictio_result = ALIXE.startALIXEasPHSTAT(clust_fold, reference_hkl, dictio_input_alixe, cell, sg_number,
                                                 tolerance=global_tolerance, resolution=resolution, cycles=cycles,
                                                 f_fom=(True if weight=='f' else False))
        print "Results of the fishing ", dictio_result
        key_phi = dictio_result.keys()[0]
        if len(dictio_result[key_phi].keys()) > 1:
            print "We found something clustering under that tolerance"
            ha_picado = True
    elif phstat_version == 'fortran':
        ls_file = open(clust_fold + 'all_phs.ls', 'w')
        ls_file.write(ref + '\n')  # Write the reference as the 1st value
        seed = 0  # Make sure the reference is used as seed
        for phs in phs_files:
            if phs != ref:
                ls_file.write(phs + "\n")
        del ls_file
        ls_file = open(clust_fold + 'all_phs.ls', 'r')
        ls_file_content = ls_file.read()
        del ls_file
        os.link(path_ins, clust_fold + "all_phs.ins")
        complete_output = al.call_phstat_print_for_clustering('all_phs', "./CLUSTERING/", path_phstat, resolution, seed,
                                                              global_tolerance, cycles)
        print complete_output
        key_phi = os.path.join(clust_fold, "all_phs.phi")
        results_clustering = al.read_phstat_print_clusterization_output(ls_file_content, complete_output, cycles)
        print "Results of the fishing", results_clustering
        if len(results_clustering.keys()) > 1:
            print "We found something clustering under that tolerance"
            ha_picado = True
    if expansions == True and ha_picado == True:
        print "Fishing finished with success, testing expansion"
        print "KEY_PHI", key_phi
        os.link(hkl_filename, key_phi[:-4] + ".hkl")
        if ent_present:
            os.link(ent_filename, key_phi[:-4] + ".ent")
        if phstat_version == 'python':
            os.link(path_ins, key_phi[:-4] + ".ins")
        output = al.phase_with_shelxe_from_phi(shelxe_line, key_phi[:-4], clust_fold, shelxe_path)
        print output
    sys.exit(0)
elif mode == 'one_step' or mode == 'two_steps' or mode == 'combi':  # In either case we need to perform the first step
    # Prepare the input to perform phase clustering inside each rotation cluster
    dict_clust_by_rotclu = {}
    for rotclu in list_rot_cluster:
        dict_clust_by_rotclu[rotclu] = None
        print "\nWe are performing rotation cluster ", rotclu
        list_phs_full = [dict_sorted_input[str(rotclu)][i] for i in range(len(dict_sorted_input[str(rotclu)]))]
        if not folder_mode:
            list_phs_rotclu = al.sort_list_phs_rotclu_by_FOM(list_phs_full,fom_sorting,dictio_fragments)
        else:
            list_phs_rotclu = list_phs_full
        # Now we can do the first clusterization round inside this rotation
        if phstat_version == 'fortran':
            # 1) Write an ls file with the list of phs
            ref_phs = list_phs_rotclu[0]
            path_ls = os.path.join(clust_fold, "first_round.ls")
            lsrotfile = open(path_ls, 'w')
            # NOTE: I need to use a relative path because fortran does not accept such long paths
            for i in range(len(list_phs_rotclu)):
                phs_namefile = (os.path.split(list_phs_rotclu[i]))[1]
                phs_relative_path = os.path.join('./CLUSTERING', phs_namefile)
                lsrotfile.write(phs_relative_path + '\n')
            lsrotfile.close()
            # 2.1) Link the ins file
            if not os.path.exists(os.path.join(clust_fold, "first_round.ins")):
                os.link(path_ins, os.path.join(clust_fold, "first_round.ins"))
            # 2.2) Link the pda file
            if not os.path.exists(os.path.join(clust_fold, "first_round.pda")):
                os.link(path_sym, os.path.join(clust_fold, "first_round.pda"))
            # 3) Launch the function in alixe_library
            # dict_clust_by_rotclu[rotclu] = al.clustering_phstat_print_under_a_tolerance(path_ls[:-3], './CLUSTERING',
            #                                                                             path_phstat,
            #                                                                             tolerance_first_round,
            #                                                                             resolution, seed, cycles)

            # name_phstat, wd, path_phstat, tolerance=75, resolution=1.0, seed=0,
            #                                  n_cycles=3, orisub='sxos', weight='f'
            dict_clust_by_rotclu[rotclu] = al.clustering_phstat_isa_under_a_tolerance(name_phstat=path_ls[:-3],
                                                                                      wd='./CLUSTERING',
                                                                                      path_phstat=path_phstat,
                                                                                      tolerance=tolerance_first_round,
                                                                                      resolution=resolution, seed=seed,
                                                                                      n_cycles=cycles, orisub=orisub,
                                                                                      weight=weight)

            # NOTE: Because of the relative paths, I need to modify the dictionary now to contain the full paths
            for key1 in dict_clust_by_rotclu[rotclu].keys():
                new_key1 = os.path.join(clust_fold, os.path.split(key1)[1])
                dict_clust_by_rotclu[rotclu][new_key1] = copy.deepcopy(dict_clust_by_rotclu[rotclu][key1])
                del dict_clust_by_rotclu[rotclu][key1]
                for key2 in dict_clust_by_rotclu[rotclu][new_key1]['dictio_result'].keys():
                    new_key2 = os.path.join(clust_fold, os.path.split(key2)[1])
                    dict_clust_by_rotclu[rotclu][new_key1]['dictio_result'][new_key2] = copy.deepcopy(
                        dict_clust_by_rotclu[rotclu][new_key1]['dictio_result'][key2])
                    del dict_clust_by_rotclu[rotclu][new_key1]['dictio_result'][key2]
        elif phstat_version == 'python':
            dict_clust_by_rotclu[rotclu] = ALIXE.clustering_all_in_ALIXE_under_a_tolerance(clust_fold=clust_fold,
                                                                                           reference_hkl=None,
                                                                                           list_phs=list_phs_rotclu,
                                                                                           cell=cell,
                                                                                           sg_symbol=sg_symbol,
                                                                                           tolerance=tolerance_first_round,
                                                                                           resolution=resolution,
                                                                                           cycles=cycles,
                                                                                           fom_weigth=True,
                                                                                           ncores=topexp)
elif mode=='one_step_parallel':
    # Prepare the input to perform phase clustering inside each rotation cluster
    dict_clust_by_rotclu = {}
    dict_rotclu = {}
    for rotclu in list_rot_cluster:
        dict_rotclu[rotclu] = None
        print "\nWe are performing rotation cluster ", rotclu
        list_phs_full = [dict_sorted_input[str(rotclu)][i] for i in range(len(dict_sorted_input[str(rotclu)]))]
        if not folder_mode:
            list_phs_rotclu = al.sort_list_phs_rotclu_by_FOM(list_phs_full,fom_sorting,dictio_fragments)
        else:
            list_phs_rotclu = list_phs_full
        # Now we can do the first clustering round inside this rotation
        if phstat_version == 'fortran': # TODO: no python version for this
            # All this block is what I will need to iterate over and change every time a round is completed
            # list_phs_rotclu should now be smaller and do not have the things that have clustered already
            # while len(list_phs_rotclu) < I need to decide a minimum value
            min_size_list = 2
            dict_global_results = {}
            last_job=False
            single_job=False
            iterations_performed=0
            # print '******************************************************'
            # print 'SHERLOCK starting list_phs_rotclu',list_phs_rotclu
            # print 'SHERLOCK len(list_phs_rotclu)',len(list_phs_rotclu)
            # print '******************************************************'
            while len(list_phs_rotclu) > 1:
                iterations_performed=iterations_performed+1
                total_files = len(list_phs_rotclu)
                list_args = []
                jobs_to_check = []
                #print 'SHERLOCK total_files',total_files
                start_ref_name=os.path.basename(list_phs_rotclu[0])
                start_ref_rel = os.path.join('./CLUSTERING', start_ref_name)
                if (total_files-1) <= min_size_list:
                    last_job=True
                    # single job I can remove it I have the iterations
                    single_job=True
                    break
                # else:
                #     print 'SHERLOCK condition of chunk division'
                #     print 'SHERLOCK total_files',total_files
                #     print 'SHERLOCK min_size_list',min_size_list
                #print 'SHERLOCK n_cores',n_cores
                #print 'SHERLOCK total_files/n_cores',total_files/n_cores
                size_chunk=(total_files-1)/n_cores # we do not count the common reference
                #print 'SHERLOCK size_chunk',size_chunk
                list_fish=list_phs_rotclu[1:]
                #print 'SHERLOCK len(list_fish)',len(list_fish)
                list_to_eval=[list_fish[i:i + size_chunk] for i in xrange(0, len(list_fish), size_chunk)]
                for ind,ele in enumerate(list_to_eval):
                    #print '*****************************'
                    #print 'SHERLOCK ele',ele
                    #print 'SHERLOCK len(ele)',len(ele)
                    size_ls=len(ele)+1 # we need to take into account the reference
                    path_ls=os.path.join(clust_fold,'chunk_'+str(ind)+'.ls')
                    lsrotfile = open(path_ls,'w')
                    lsrotfile.write(start_ref_rel+'\n')
                    for i in range(len(ele)):
                        phs_namefile = (os.path.split(ele[i]))[1]
                        phs_relative_path = os.path.join('./CLUSTERING', phs_namefile)
                        lsrotfile.write(phs_relative_path + '\n')
                    lsrotfile.close()
                    if not os.path.exists(os.path.join(clust_fold, 'chunk_'+str(ind)+".ins")):
                        shutil.copy(path_ins, os.path.join(clust_fold, 'chunk_'+str(ind)+".ins"))
                    if not os.path.exists(os.path.join(clust_fold, 'chunk_'+str(ind)+".pda")):
                        shutil.copy(path_sym, os.path.join(clust_fold, 'chunk_'+str(ind)+".pda"))
                    list_args.append(('chunk_'+str(ind), "./CLUSTERING/", path_phstat, resolution,
                                      seed, tolerance_first_round, cycles, orisub, weight))
                    jobs_to_check.append((os.path.join(clust_fold,'chunk_'+str(ind)+'.out'),size_ls))

                # Now run all the trials
                for argumlist in list_args:
                    #print 'SHERLOCK argumlist',argumlist
                    al.call_phstat_print_for_clustering_parallel(argumlist)
                # I need to know when they have finished
                PHSTAT_OUT_END_CONDITION_LOCAL = """cluster phases written to"""
                PHSTAT_OUT_FAILURE_CONDITION_LOCAL = """Bad command line"""
                PHSTAT_OUT_END_TEST = 1
                return_val = False
                while return_val == False:
                    for job,size_ls in jobs_to_check:
                        #print '\nSHERLOCK job',job
                        return_val = SELSLIB2.checkYOURoutput(myfile=job,conditioEND=PHSTAT_OUT_END_CONDITION_LOCAL,
                                                          testEND=PHSTAT_OUT_END_TEST,sleep_ifnot_ready=True,
                                                          failure_test=PHSTAT_OUT_FAILURE_CONDITION_LOCAL)
                        #print 'SHERLOCK return_val',return_val
                # Now I am sure they have finished, I can evaluate them
                #print 'SHERLOCK Checking the results '
                list_setsol_remove = []
                for output_filename,size_ls in jobs_to_check:
                    print 'Checking ',output_filename
                    name_chunk=os.path.basename(output_filename)[:-4]
                    output_file=open(output_filename,'r')
                    output_content = output_file.read()
                    print output_content
                    # TODO: temporary save the output to check
                    #keepoutpath=os.path.join(clust_fold,name_chunk+'_'+str(iterations_performed)+'.out')
                    #shutil.copyfile(output_filename,keepoutpath)
                    #print 'SHERLOCK check keepoutpath',keepoutpath
                    #quit()
                    # TODO: temporary save the output to check
                    dictio_result = al.read_phstat_isa_clusterization_output(output_content, cycles, size_ls)
                    #print 'SHERLOCK dictio_result',dictio_result
                    #print 'SHERLOCK start_ref_name',start_ref_name
                    #print 'SHERLOCK start_ref_rel',start_ref_rel
                    name_key=start_ref_rel
                    clustered = True if len(dictio_result.keys())>1 else False
                    keys_global=dict_global_results.keys()
                    if name_key in keys_global: # Add this info
                        if not clustered:
                            dict_global_results[name_key].append((name_chunk,set()))
                        else:
                            dict_global_results[name_key].append((name_chunk,set(dictio_result.keys())))
                    else: # Create the key and add the info then
                        if not clustered:
                            dict_global_results[name_key] = []
                            dict_global_results[name_key].append((name_chunk, set()))
                        else:
                            dict_global_results[name_key] = []
                            dict_global_results[name_key].append((name_chunk, set(dictio_result.keys())))
                    list_setsol_remove.extend([os.path.abspath(ele) for ele in dictio_result.keys()])
                #print '\n\nSHERLOCK dict_global_results', dict_global_results
                #print '\nSHERLOCK list_setsol_remove',list_setsol_remove
                #print '\nSHERLOCK set(list_setsol_remove)', set(list_setsol_remove)
                set1 = set(list_phs_rotclu)
                set2 = set(list_setsol_remove)
                new_input = list(set1 - set2)
                #print '\nSHERLOCK new_input',new_input
                #print '\nSHERLOCK total_files before', total_files
                #print '\nSHERLOCK len(new_input)',len(new_input)
                #if iterations_performed==1:
                #    print '\nSHERLOCK CHECK'
                #    quit()
                list_phs_rotclu= [e for e in new_input]

        if last_job: # We need to perform a last one including all the rest of the files
            #print 'SHERLOCK last_job condition '
            list_setsol_remove = []
            while len(list_phs_rotclu)>=1:
                #print 'SHERLOCK list_phs_rotclu',list_phs_rotclu
                path_ls = os.path.join(clust_fold, 'last.ls')
                lsrotfile = open(path_ls, 'w')
                for xi in range(len(list_phs_rotclu)):
                    phs_namefile = (os.path.split(list_phs_rotclu[xi]))[1]
                    phs_relative_path = os.path.join('./CLUSTERING', phs_namefile)
                    lsrotfile.write(phs_relative_path + '\n')
                lsrotfile.close()
                if not os.path.exists(os.path.join(clust_fold, 'last.ins')):
                    shutil.copy(path_ins, os.path.join(clust_fold, 'last.ins'))
                if not os.path.exists(os.path.join(clust_fold, "last.pda")):
                    shutil.copy(path_sym, os.path.join(clust_fold, "last.pda"))
                output,error=al.call_phstat_print_for_clustering('last',"./CLUSTERING/",path_phstat, resolution,
                                          seed, tolerance_first_round, cycles, orisub, weight)
                #print output
                name_chunk='last'
                dictio_result = al.read_phstat_isa_clusterization_output(output, cycles, len(list_phs_rotclu))
                name_key = start_ref_rel
                clustered = True if len(dictio_result) > 1 else False
                keys_global = dict_global_results.keys()
                if name_key in keys_global:  # Add this info
                    if not clustered:
                        dict_global_results[name_key].append((name_chunk, set()))
                    else:
                        dict_global_results[name_key].append((name_chunk, set(dictio_result.keys())))
                else:  # Create the key and add the info then
                    if not clustered:
                        dict_global_results[name_key] = []
                        dict_global_results[name_key].append((name_chunk, set()))
                    else:
                        dict_global_results[name_key] = []
                        dict_global_results[name_key].append((name_chunk, set(dictio_result.keys())))
                list_setsol_remove.extend([os.path.abspath(ele) for ele in dictio_result.keys()])
                set1 = set(list_phs_rotclu)
                set2 = set(list_setsol_remove)
                new_input = list(set1 - set2)
                #print 'SHERLOCK new_input',new_input
                #print 'SHERLOCK len(new_input)',len(new_input)
                #print 'SHERLOCK total_files before', total_files
                list_phs_rotclu=new_input

        # Save the results sorted by rotclu
        #print 'SHERLOCK rotclu',rotclu
        #print 'SHERLOCK dict_global_results',dict_global_results
        #quit()
        dict_rotclu[rotclu] = dict_global_results

    # print 'SHERLOCK dict_rotclu.keys()',dict_rotclu.keys()
    # for keyro in dict_rotclu.keys():
    #     print '\n\nSHERLOCK keyro',keyro
    #     for keyclu in dict_rotclu[keyro].keys():
    #         print '\nSHERLOCK keyclu',keyclu
    #         #print '\nSHERLOCK dict_rotclu[keyro][keyclu]',dict_rotclu[keyro][keyclu]
    #
    # quit()

    for keyro in dict_rotclu.keys():
        #print '***************************'
        #print 'SHERLOCK rotclu ',keyro
        list_to_recalculate = []
        for keyclu in dict_rotclu[keyro].keys():
            #print '\nSHERLOCK keyclu',keyclu
            listsets=dict_rotclu[keyro][keyclu]
            #print '\nSHERLOCK listsets',listsets
            settis=[ele[1] for ele in listsets]
            united=set.union(*settis)
            #print 'SHERLOCK united',united
            if len(united) != 0:
                #print 'SHERLOCK This union is not empty'
                #print 'SHERLOCK len(list(united))',len(list(united))
                list_to_recalculate.append((keyclu,list(united)))
                #quit()

        if len(list_to_recalculate)>0: # NOTE CLAUDIA: I should check whether a single job only
            #print '********************************************************'
            for ref,files in list_to_recalculate:
                filekeep=os.path.basename(ref)[:-4]+'_ref'
                #print 'SHERLOCK filekeep',filekeep
                path_ls = os.path.join(clust_fold, filekeep+'.ls')
                lsrotfile = open(path_ls, 'w')
                lsrotfile.write(ref+ '\n')
                for xi in range(len(files)):
                    #print 'SHERLOCK files[xi]',files[xi]
                    if files[xi]!=ref:
                        lsrotfile.write(files[xi] + '\n')
                lsrotfile.close()
                # TODO: COMPUTE THE JOB
                if not os.path.exists(os.path.join(clust_fold, filekeep+'.ins')):
                    shutil.copy(path_ins, os.path.join(clust_fold, filekeep+'.ins'))
                if not os.path.exists(os.path.join(clust_fold, filekeep+".pda")):
                    shutil.copy(path_sym, os.path.join(clust_fold, filekeep+".pda"))
                output,error=al.call_phstat_print_for_clustering(filekeep,"./CLUSTERING/",path_phstat, resolution,
                                          seed, tolerance_first_round, cycles, orisub, weight)
                #print output
                dictio_result = al.read_phstat_isa_clusterization_output(output, cycles, len(files))
                #print 'SHERLOCK dictio_result',dictio_result
                namecluphi=os.path.abspath(filekeep+".phi")
                #print 'SHERLOCK namecluphi',namecluphi
                #print 'SHERLOCK dict_clust_by_rotclu[keyro]',dict_clust_by_rotclu[keyro]
                #{'dictio_result': dictio_result, 'n_phs': phs_in_cluster,
                #                             'dict_FOMs': {}}
                if keyro in dict_clust_by_rotclu.keys():
                    print 'SHERLOCK the key exists already ',keyro
                    dict_clust_by_rotclu[keyro][namecluphi]={'dictio_result': dictio_result,
                                                             'n_phs': len(dictio_result.keys()),
                                                             'dict_FOMs': {}}
                else:
                    print 'SHERLOCK the key does not exists yet ',keyro
                    dict_clust_by_rotclu[keyro] = {}
                    dict_clust_by_rotclu[keyro][namecluphi]={'dictio_result': dictio_result,
                                                             'n_phs': len(dictio_result.keys()),
                                                             'dict_FOMs': {}}
    # for keyro in dict_clust_by_rotclu.keys():
    #     print '\n\nSHERLOCK keyro',keyro
    #     for keyclu in dict_clust_by_rotclu[keyro].keys():
    #         print 'SHERLOCK keyclu',keyclu
    #
    # quit()

    for keyro in dict_clust_by_rotclu.keys():
        for key1 in dict_clust_by_rotclu[keyro].keys():
            new_key1 = os.path.join(clust_fold, os.path.split(key1)[1])
            dict_clust_by_rotclu[keyro][new_key1] = copy.deepcopy(dict_clust_by_rotclu[keyro][key1])
            del dict_clust_by_rotclu[keyro][key1]
            for key2 in dict_clust_by_rotclu[keyro][new_key1]['dictio_result'].keys():
                new_key2 = os.path.join(clust_fold, os.path.split(key2)[1])
                dict_clust_by_rotclu[keyro][new_key1]['dictio_result'][new_key2] = copy.deepcopy(
                    dict_clust_by_rotclu[keyro][new_key1]['dictio_result'][key2])
                del dict_clust_by_rotclu[keyro][new_key1]['dictio_result'][key2]

    #print 'SHERLOCK implementing the parallel strategy!'
    #print 'SHERLOCK dict_clust_by_rotclu', dict_clust_by_rotclu
    #for key in dict_clust_by_rotclu.keys():
    #    print 'SHERLOCK dict_clust_by_rotclu[key].keys()',dict_clust_by_rotclu[key].keys()
    #sys.exit(0)

elif mode.startswith('ens1_frag'):
    dict_clust_by_rotclu = {}
    rotclu = 'arci' # In this case we consider all clusters together
    list_phs_full = [ dict_sorted_input[key][i] for key in dict_sorted_input.keys() for i in range(len(dict_sorted_input[key]))]
    list_tuple_sort = []
    for phs in list_phs_full:
        phs_key=phs[:-4]
        list_tuple_sort.append((phs,dictio_fragments[phs_key]['zscore'],dictio_fragments[phs_key]['llg'],dictio_fragments[phs_key]['initcc']))
    if fom_sorting=='CC':
        list_tuple_sort.sort(key=lambda x: x[3],reverse=True)
    elif fom_sorting=='LLG':
        list_tuple_sort.sort(key=lambda x: x[2],reverse=True)
    elif fom_sorting=='ZSCORE':
        list_tuple_sort.sort(key=lambda x: x[1],reverse=True)
    list_phs_full = [ list_tuple_sort[i][0] for i in range(len(list_tuple_sort)) ]
    if phstat_version == 'fortran':
        # 1) Write an ls file with the list of phs
        ref_phs = list_phs_full[0]
        path_ls = os.path.join(clust_fold, "first_round.ls")
        lsrotfile = open(path_ls, 'w')
        # NOTE: I need to use a relative path because fortran does not accept such long paths
        for i in range(len(list_phs_full)):
            phs_namefile = (os.path.split(list_phs_full[i]))[1]
            phs_relative_path = os.path.join('./CLUSTERING', phs_namefile)
            lsrotfile.write(phs_relative_path + '\n')
        lsrotfile.close()
        # 2) Link the ins file
        if not os.path.exists(os.path.join(clust_fold, "first_round.ins")):
            os.link(path_ins, os.path.join(clust_fold, "first_round.ins"))
        # 2) Link the pda file
        if not os.path.exists(os.path.join(clust_fold, "first_round.pda")):
            os.link(path_sym, os.path.join(clust_fold, "first_round.pda"))
        # 3) Launch the function in alixe_library
        # dict_clust_by_rotclu[rotclu] = al.clustering_phstat_print_under_a_tolerance(path_ls[:-3], './CLUSTERING',
        #                                                                             path_phstat,
        #                                                                             tolerance_first_round,
        #                                                                             resolution, seed, cycles)
        dict_clust_by_rotclu[rotclu] = al.clustering_phstat_isa_under_a_tolerance(path_ls[:-3], './CLUSTERING',
                                                                                    path_phstat,
                                                                                    tolerance_first_round,
                                                                                    resolution, seed, cycles,orisub,
                                                                                  weight)
        # NOTE: Because of the relative paths, I need to modify the dictionary now to contain the full paths
        # NOTE: clear thing to move to a function because I do it all the time
        for key1 in dict_clust_by_rotclu[rotclu].keys():
            new_key1 = os.path.join(clust_fold, os.path.split(key1)[1])
            dict_clust_by_rotclu[rotclu][new_key1] = copy.deepcopy(dict_clust_by_rotclu[rotclu][key1])
            del dict_clust_by_rotclu[rotclu][key1]
            for key2 in dict_clust_by_rotclu[rotclu][new_key1]['dictio_result'].keys():
                new_key2 = os.path.join(clust_fold, os.path.split(key2)[1])
                dict_clust_by_rotclu[rotclu][new_key1]['dictio_result'][new_key2] = copy.deepcopy(
                    dict_clust_by_rotclu[rotclu][new_key1]['dictio_result'][key2])
                del dict_clust_by_rotclu[rotclu][new_key1]['dictio_result'][key2]
    elif phstat_version == 'python':
        dict_clust_by_rotclu[rotclu] = ALIXE.clustering_all_in_ALIXE_under_a_tolerance(clust_fold, None,
                                                                                       list_phs_full, cell,
                                                                                       sg_symbol,
                                                                                       tolerance_first_round,
                                                                                       resolution, cycles, True,
                                                                                       ncores=topexp)
elif mode == ('cc_analysis'):
    # We need to prepare all the ls files
    phs_files = al.list_files_by_extension(clust_fold, 'phs')
    table_cc_names = open(os.path.join(clust_fold,'corresp_names_ccfiles.txt'),'w')
    dict_cc_names = {}
    list_ls_to_process = []
    for i,phs1 in enumerate(phs_files):
        table_cc_names.write(str(i + 1) + '\t' + os.path.basename(phs1) + '\n')
        dict_cc_names[os.path.basename(phs1)] = str(i + 1)
        if i < len(phs_files)-1:
            path_ls = os.path.join(clust_fold, "ref"+str(i+1)+'.ls')
            #print 'Using reference phs ', phs1
            # We also need to have linked a pda file for each of the ls files
            if not os.path.exists(os.path.join(clust_fold, path_ls[:-3]+".pda")):
                os.link(path_sym, os.path.join(clust_fold, path_ls[:-3]+".pda"))
            lsfile = open(path_ls, 'w')
            for j in range(i,len(phs_files)):
                #print '   And including ',phs_files[j]
                # It needs to be the relative path
                phs_namefile = os.path.basename(phs_files[j])
                phs_relative_path = os.path.join('./CLUSTERING', phs_namefile)
                lsfile.write(phs_relative_path+'\n')
            del lsfile
            list_ls_to_process.append((os.path.basename(path_ls),j-i+1,os.path.basename(phs1)))
    del table_cc_names

    # start your parallel workers at the beginning of your script
    pool = Pool(n_cores)
    print '\n\n Opening the pool with ',n_cores,' workers'

    # prepare the iterable with the arguments
    list_args = []
    for op,tuplels in enumerate(list_ls_to_process):
        namels = tuplels[0]
        phs_in_ls = tuplels[1]
        phs_ref = tuplels[2]
        list_args.append((namels[:-3],"./CLUSTERING/",path_phstat,resolution,0,100,1,orisub,weight))

    # execute a computation(s) in parallel
    pool.map(al.call_phstat_print_for_clustering_parallel, list_args)

    # turn off your parallel workers at the end of your script
    print 'Closing the pool'
    pool.close()

    input_for_ccanalysis = open(os.path.join(clust_fold,'alixecc.dat'),'w')
    info_relations = open(os.path.join(clust_fold,'global_table.dat'),'w')
    info_relations.write('%-25s %-25s %-12s %-12s %-12s %-12s %-12s %-12s \n' % ('File1', 'File2', 'mapCC', 'wMPD','diffwMPD', 'shiftX', 'shiftY', 'shiftZ'))

    for op,tuplels in enumerate(list_ls_to_process):
        namels = tuplels[0]
        phs_in_ls = tuplels[1]
        phs_ref = tuplels[2]
        output_file = open(os.path.join(clust_fold,namels[:-3]+'.out'),'r')
        output_content = output_file.read()
        print output_content
        dictio_result = al.read_phstat_isa_clusterization_output(output_content, 1, phs_in_ls)
        # Note: in this case, there is only one cycle so dictio_result first and last entries are the same
        #print 'SHERLOCK dictio_result'
        #for key in dictio_result.keys():
        #    print key, dictio_result[key]
        #quit()
        ref_id = dict_cc_names[phs_ref]
        for keyphs in dictio_result.keys():
            comp_id = dict_cc_names[os.path.basename(keyphs)]
            comp_name = os.path.basename(keyphs)
            if ref_id == comp_id:
                continue
            mapcc_scaled1 = (dictio_result[keyphs]['mapcc_first'])/100
            wmpd = dictio_result[keyphs]['wMPE_first']
            diffwmpd = dictio_result[keyphs]['diff_wMPE_first']
            shiftx = dictio_result[keyphs]['shift_first'][0]
            shifty = dictio_result[keyphs]['shift_first'][1]
            shiftz = dictio_result[keyphs]['shift_first'][2]
            input_for_ccanalysis.write('\t'+str(ref_id)+'\t'+str(comp_id)+'\t'+str(mapcc_scaled1)+'\n')
            info_relations.write('%-25s %-25s %-12s %-12s %-12s %-12s %-12s %-12s \n' % (phs_ref, comp_name, mapcc_scaled1, wmpd, diffwmpd, shiftx, shifty, shiftz))
    del input_for_ccanalysis
    del info_relations
    # Remove the phi files resulting from this mode
    phi_to_remove=al.list_files_by_extension(clust_fold, 'phi')
    for phi in phi_to_remove: # Remove all the files with ref, not only the phi
        print 'Removing ',phi
        os.remove(phi)
        print 'Removing ',phi[:-4]+'.ls'
        os.remove(phi[:-4]+'.ls')
        print 'Removing ',phi[:-4]+'.pda'
        os.remove(phi[:-4]+'.pda')
        # At the moment I keep them just to be able to check if everything is OK.
        #print 'Removing ',phi[:-4]+'.out'
        #os.remove(phi[:-4]+'.out')

    #TODO with ANTONIA: write some kind of pickle file with
    # the dictio_result or something that allows to rerun just including some files in the folder
    new_now = time.time()
    final_string = '\nTotal time spent in running autoalixe in cc_analysis mode is ' + str((new_now - now)) + ' seconds , or ' + str(
        (new_now - now) / 60) + ' minutes \n Command line used was ' + str(sys.argv)
    log_file.write(final_string)
    print final_string
    del log_file
    sys.exit(0)  # Finishing normally the cc_analysis mode



# Nice table from first round
table_clust_first_round = open(clust_fold + "info_clust_table", 'w')
if ent_present:
    table_clust_first_round.write(
    '%-40s %-5s %-10s %-10s %-10s %-10s %-10s %-10s\n' % ('Cluster', 'n_phs', 'topzscore', 'topllg', 'fused_cc', 'fused_wmpe', 'phi_cc','phi_wmpe'))
    del table_clust_first_round
else:
    table_clust_first_round.write(
    '%-40s %-5s %-10s %-10s %-10s %-10s\n' % ('Cluster', 'n_phs', 'topzscore', 'topllg', 'fused_cc', 'phi_cc'))
    del table_clust_first_round
# Raw output from first run
raw_clust_first_round = open(clust_fold + "info_clust_raw", 'w')
del raw_clust_first_round


# for rotclu in dict_clust_by_rotclu.keys():
#      print 'We are evaluating rotation cluster',rotclu
#      print '*********************************************'
#      print 'SHERLOCK len(dict_clust_by_rotclu[rotclu].keys())',len(dict_clust_by_rotclu[rotclu].keys())
#      #print 'SHERLOCK dict_clust_by_rotclu[rotclu].keys()',dict_clust_by_rotclu[rotclu].keys()
#      for cluster in (dict_clust_by_rotclu[rotclu]).keys():
#          print 'SHERLOCK cluster',cluster
#
# quit()

# Read clusters from first round and process them
list_to_expand_first_round = []
count_cluster = 0
for rotclu in dict_clust_by_rotclu.keys():
    print 'We are evaluating rotation cluster',rotclu
    for cluster in (dict_clust_by_rotclu[rotclu]).keys():
        print "\n\tEvaluating cluster ", cluster
        n_phs = dict_clust_by_rotclu[rotclu][cluster]['n_phs']
        count_cluster = count_cluster+1
        if dict_clust_by_rotclu[rotclu][cluster]['n_phs'] > 1:
            print "\t This cluster contains more than one phs"
            list_llg = []
            list_zscore = []
            list_of_filepaths = []  # list of files to join
            dict_clust_by_rotclu[rotclu][cluster][
                'rot_clust_list'] = []  # Generate new key to save original rotation_cluster
            for phs in dict_clust_by_rotclu[rotclu][cluster]['dictio_result'].keys():  # For each phs in the cluster
                print "\t Processing file ", phs
                #print 'SHERLOCK dictio_fragments.keys()',dictio_fragments.keys()
                list_llg.append(dictio_fragments[phs[:-4]]['llg'])
                list_zscore.append(dictio_fragments[phs[:-4]]['zscore'])
                if dictio_fragments[phs[:-4]]['rot_cluster'] not in dict_clust_by_rotclu[rotclu][cluster][
                    'rot_clust_list']:
                    # If more than 1 rot cluster elongated together you will have a list with len >1
                    dict_clust_by_rotclu[rotclu][cluster]['rot_clust_list'].append(
                        dictio_fragments[phs[:-4]]['rot_cluster'])
                shift = dict_clust_by_rotclu[rotclu][cluster]['dictio_result'][phs]['shift_first']
                if shift == [-1,-1,-1]: # Then this phs entered in the third cycle and I need to catch that
                    shift = dict_clust_by_rotclu[rotclu][cluster]['dictio_result'][phs]['shift_last']
                if polar:  # Check if the shift is too small to be considered
                    for i in range(len(shift)):
                        if abs(shift[i]) < 0.0001 and shift[i] != 0.0:  # NOTE: What will be a sensible number?
                            shift[i] = 0.0
                if not (shift == [0.0, 0.0, 0.0]):  # Make sure it is not the reference
                    al.shifting_coordinates(dict_clust_by_rotclu[rotclu][cluster]['dictio_result'][phs]['shift_first'],
                                            phs[:-4] + '.pda')
                    list_of_filepaths.append(phs[:-4] + '_shifted.pda')  # Write pda with its shift
                else:
                    list_of_filepaths.append(phs[:-4] + '.pda')

            # Fuse the files in a single pdb
            al.fuse_pdbs(list_of_filepaths, cluster[:-4] + "_fused.pda")
            al.add_cryst_card(cryst_card, cluster[:-4] + "_fused.pda")

            # Now we are going to check FOMs for the clusters:
            # 1) Starting from from the fused pda
            name_shelxe = ((os.path.split(cluster))[1])[:-4] + "_fused"
            path_name_shelxe = os.path.join(clust_fold, name_shelxe)
            if ent_present:
                try:
                    os.link(ent_filename, path_name_shelxe + ".ent")
                except:
                    print "Error linking the ent file"
                    print sys.exc_info()
            try:
                os.link(hkl_filename, path_name_shelxe + ".hkl")
            except:
                print "Error linking the hkl file"
                print sys.exc_info()
            output = al.phase_fragment_with_shelxe(shelxe_line_alixe, name_shelxe, clust_fold, shelxe_path)
            lst_file = open(path_name_shelxe + '.lst', 'r')
            lst_content = lst_file.read()
            list_fom = al.extract_EFOM_and_pseudoCC_shelxe(lst_content)
            initcc = al.extract_INITCC_shelxe(lst_content)
            dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['efom_fused'] = list_fom[0]
            dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['pseudocc_fused'] = list_fom[1]
            dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['CC_fused'] = initcc
            if ent_present:  # Retrieve final MPE and save them too
                list_mpe = al.extract_wMPE_shelxe(clust_fold + name_shelxe + '.lst')
                dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['final_MPEs_fused'] = list_mpe
                # Get the shift to final and apply it to better see in Coot to what solutions they correspond
                lst_file = open(clust_fold + name_shelxe + '.lst')
                lst_content = lst_file.read()
                shift_to_apply = al.extract_shift_from_shelxe(lst_content)
                if not shift_to_apply == [0.0, 0.0, 0.0]:
                    print "Moving pda ", name_shelxe, ".pda with this shift respect to the ent ", shift_to_apply
                    al.shifting_coordinates_inverse(shift_to_apply, clust_fold + name_shelxe + '.pda')
                    al.add_cryst_card(cryst_card,
                                      clust_fold + name_shelxe + "_shifted.pda")  # Add cryst card to this pdb
                    os.rename(clust_fold + name_shelxe + "_shifted.pda",
                              clust_fold + name_shelxe + "_shifted_to_final.pda")
            # 2) Starting from from the phi file
            name_shelxe = ((os.path.split(cluster))[1])[:-4]
            path_name_shelxe = os.path.join(clust_fold, name_shelxe)
            if ent_present:
                shutil.copy(ent_filename, path_name_shelxe + ".ent")
            shutil.copy(hkl_filename, path_name_shelxe + ".hkl")
            shutil.copy(path_ins, path_name_shelxe + ".ins")
            output = al.phase_with_shelxe_from_phi(shelxe_line_alixe, name_shelxe, clust_fold, shelxe_path)
            #print output
            lst_file = open(path_name_shelxe + '.lst', 'r')
            lst_content = lst_file.read()
            list_fom = al.extract_EFOM_and_pseudoCC_shelxe(lst_content)
            if ent_present:  # Retrieve final MPE and save them too
                list_mpe = al.extract_wMPE_shelxe(clust_fold + name_shelxe + '.lst')
                dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['final_MPEs_phi'] = list_mpe
            # Soon I will have a version of SHELXE that also computes initCC
            #initcc = al.extract_INITCC_shelxe(lst_content)
            dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['efom_phi'] = list_fom[0]
            dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['pseudocc_phi'] = list_fom[1]
            dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['CC_phi'] = 0.0

            # We add the top LLG or ZSCORE as representative of the cluster
            dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['llg'] = (sorted(list_llg, reverse=True))[0]
            dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['zscore'] = (sorted(list_zscore, reverse=True))[0]

            # Prepare to save info from clusters in this file
            name_cluster = os.path.split(cluster)[1]
            if not folder_mode:
                topzscore = dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['zscore']
                topllg = dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['llg']
            else:
                topzscore = -1.0
                topllg = -1.0
            fusedcc = dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['CC_fused']
            phicc = dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['CC_phi']
            # TODO: change this for the CC of the phi when it is available in SHELXE
            list_to_expand_first_round.append((name_cluster, n_phs, topzscore, topllg, fusedcc))
            if ent_present:
                #print 'SHERLOCK WRITING when ent present, count_cluster',count_cluster
                wmpefinal_fused = dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['final_MPEs_fused'][2]
                wmpefinal_phi = dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['final_MPEs_phi'][2]
                table_clust_first_round = open(clust_fold + "info_clust_table", 'a')
                table_clust_first_round.write('%-40s %-5i %-10.2f %-10.2f %-10.2f %-10.2f %-10.2f %-10.2f\n' % (
                name_cluster, n_phs, topzscore, topllg, fusedcc, wmpefinal_fused, phicc, wmpefinal_phi))
                del table_clust_first_round
            else:
                #print 'SHERLOCK WRITING when ent not present, count_cluster',count_cluster
                table_clust_first_round = open(clust_fold + "info_clust_table", 'a')
                table_clust_first_round.write(
                    '%-40s %-5i %-10.2f %-10.2f %-10.2f %-10.2f \n' % (name_cluster, n_phs, topzscore, topllg, fusedcc, phicc))
                del table_clust_first_round
        else: #dict_clust_by_rotclu[rotclu][cluster]['n_phs'] == 1:  # Then we have the FOMs already
            # {'n_phs': 1, 'dictio_result': {'th14_0_0xx0FR0_27-7.phs': {'shift': [0.0, 0.0, 0.0], 'MPE': 0.0}}, 'dict_FOMs': {}}
            name_file = ((dict_clust_by_rotclu[rotclu][cluster]['dictio_result'].keys())[0])[:-4]
            name_file = os.path.join(clust_fold, os.path.split(name_file)[1])
            new_cluster = os.path.join(clust_fold, name_file + '.phs')
            dict_clust_by_rotclu[rotclu][new_cluster] = copy.deepcopy(dict_clust_by_rotclu[rotclu][cluster])
            del dict_clust_by_rotclu[rotclu][cluster]
            os.remove(cluster)  # Remove phi file
            cluster = new_cluster  # Careful! New key
            dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['CC'] = dictio_fragments[name_file]['initcc']
            dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['pseudocc'] = dictio_fragments[name_file]['pseudocc']
            dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['efom'] = dictio_fragments[name_file]['efom']
            # Save also the phaser FOMs
            dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['llg'] = dictio_fragments[name_file]['llg']
            dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['zscore'] = dictio_fragments[name_file]['zscore']
            list_rot = []
            list_rot.append(dictio_fragments[name_file]['rot_cluster'])
            dict_clust_by_rotclu[rotclu][cluster]['rot_clust_list'] = list_rot
            if ent_present and not folder_mode: # NOTE CM: unless the lsts are there because we generated the phs in the folder
                dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['final_MPEs'] = dictio_fragments[name_file][
                    'list_MPE']
                # Get the shift and apply it to better see in Coot to what solutions they correspond
                lst_file = open(name_file + '.lst')
                lst_content = lst_file.read()
                shift_to_apply = al.extract_shift_from_shelxe(lst_content)
                if not shift_to_apply == [0.0, 0.0, 0.0]:
                    print "Moving pda ", name_file + ".pda", ".pda with this shift respect to the ent ", shift_to_apply
                    al.shifting_coordinates_inverse(shift_to_apply, name_file + '.pda')
                    al.add_cryst_card(cryst_card, name_file + "_shifted.pda")  # Add cryst card to this pdb
                    os.rename(name_file + "_shifted.pda", name_file + "_shifted_to_final.pda")
            # Write the information about the cluster in the files
            raw_clust_first_round = open(clust_fold + "info_clust_raw",
                                         'a')  # Prepare to save info from clusters in this file
            raw_clust_first_round.write(
                "**********************************************************************************\n")
            raw_clust_first_round.write(str(cluster) + str(dict_clust_by_rotclu[rotclu][cluster]) + "\n")
            del raw_clust_first_round
            name_cluster = os.path.split(cluster)[1]
            if not folder_mode:
                topzscore = dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['zscore']
                topllg = dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['llg']
                fusedcc = dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['CC']
            else: # TODO: This is quick and dirty to get the mode to work
                topzscore = -1.0
                topllg = -1.0
                fusedcc = -1.0
            if ent_present:
                #print 'SHERLOCK WRITING when ent present, count_cluster', count_cluster
                if not folder_mode:
                    wmpefinal = dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['final_MPEs'][2]
                else:
                    wmpefinal = -1.0 # again, this we would have if we have or produce the lst ourselves
                table_clust_first_round = open(clust_fold + "info_clust_table",
                                               'a')  # Prepare to save info from clusters in this file
                table_clust_first_round.write('%-40s %-5i %-10.2f %-10.2f %-10.2f %-10.2f\n' % (
                name_cluster, n_phs, topzscore, topllg, fusedcc, wmpefinal))
                del table_clust_first_round
            else:
                #print 'SHERLOCK WRITING when ent NOT present, count_cluster', count_cluster
                table_clust_first_round = open(clust_fold + "info_clust_table",
                                               'a')
                table_clust_first_round.write(
                    '%-40s %-5i %-10.2f %-10.2f %-10.2f\n' % (name_cluster, n_phs, topzscore, topllg, fusedcc))
                del table_clust_first_round

    # For each cluster write a summary table file with the information of its contents
    for cluster in dict_clust_by_rotclu[rotclu].keys():
        path_clu = os.path.join(clust_fold, os.path.basename(cluster)[:-4] + '.sum')
        fileforclu = open(path_clu, 'w')
        fileforclu.write(
            '%-40s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s\n' % ('Name','wMPD_first','wMPD_last', 'diff_wMPD','mapcc_first',
                                                 'mapcc_last','shift_first_x','shift_first_y','shift_first_z','shift_last_x','shift_last_y','shift_last_z'))
        for phaseset in dict_clust_by_rotclu[rotclu][cluster]['dictio_result'].keys():
            name = os.path.basename(phaseset)
            wmpe_first = round(dict_clust_by_rotclu[rotclu][cluster]['dictio_result'][phaseset]['wMPE_first'], 2)
            wmpe_last = round(dict_clust_by_rotclu[rotclu][cluster]['dictio_result'][phaseset]['wMPE_last'], 2)
            if phstat_version != 'fortran':
                if dict_clust_by_rotclu[rotclu][cluster]['n_phs']>1 and \
                        isinstance(dict_clust_by_rotclu[rotclu][cluster]['dictio_result'][phaseset]['diff_wMPE'],float):
                    diffwmpe = round(dict_clust_by_rotclu[rotclu][cluster]['dictio_result'][phaseset]['diff_wMPE'], 2)
                else:
                    diffwmpe = -1
            else:
                diffwmpe = -1
            if dict_clust_by_rotclu[rotclu][cluster]['dictio_result'][phaseset]['mapcc_first'] != None:
                mapcc_first = round(dict_clust_by_rotclu[rotclu][cluster]['dictio_result'][phaseset]['mapcc_first'], 2)
            else:
                mapcc_first = -1
            if dict_clust_by_rotclu[rotclu][cluster]['dictio_result'][phaseset]['mapcc_last'] != None:
                mapcc_last = round(dict_clust_by_rotclu[rotclu][cluster]['dictio_result'][phaseset]['mapcc_last'], 2)
            else:
                mapcc_last = -1
            shift_first = dict_clust_by_rotclu[rotclu][cluster]['dictio_result'][phaseset]['shift_first']
            shift_last = dict_clust_by_rotclu[rotclu][cluster]['dictio_result'][phaseset]['shift_last']
            fileforclu.write(
                '%-40s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s\n' % (name, wmpe_first,wmpe_last,
                                                                                           diffwmpe,mapcc_first,
                                                                                           mapcc_last,
                                                                                           shift_first[0],
                                                                                           shift_first[1],
                                                                                           shift_first[2],
                                                                                           shift_last[0],
                                                                                           shift_last[1],
                                                                                           shift_last[2]))
        del (fileforclu)

# TODO: Generate the pkl file so that we can read it and perform a combi mode
pkl_round_one = open(os.path.join(clust_fold, 'first_round.pkl'), 'w')
cPickle.dump(dict_clust_by_rotclu, pkl_round_one)
pkl_round_one.close()


if mode == 'one_step' or mode.startswith('ens1_frag') or mode == 'one_step_parallel':
    print "\nOne step clustering performed, results can be found at the files info_clust_raw and info_clust_table, found in the CLUSTERING folder"
    if expansions == True:
        print "Starting the expansions of the clusters from the first round using the phi files"
        # EXPANSIONS FROM COMBINED PHASES
        expansions_folder_phi = os.path.join(clust_fold, 'EXPANSIONS_FROM_PHI')
        os.mkdir(expansions_folder_phi)
        #print '\n SHERLOCK list_to_expand_first_round', list_to_expand_first_round
        list_to_expand_first_round_phi = sorted(list_to_expand_first_round, key=operator.itemgetter(1, 2, 3, 4),
                                                reverse=True)
        list_to_expand_first_round_phi = [os.path.join(clust_fold, ele[0][:-4]) for ele in list_to_expand_first_round]
        #print '\n SHERLOCK list_to_expand_first_round_phi', list_to_expand_first_round_phi
        al.phase_round_with_shelxe(linea_arg=shelxe_line, lista_clusters=list_to_expand_first_round_phi,
                                   wd=expansions_folder_phi, path_shelxe=shelxe_path, hkl_path=hkl_filename,
                                   ins_path=path_ins, ent_path=ent_filename, fragment_type='phi')

elif mode == 'two_steps':
    # TODO: write different functions to test possible ways of combining at the second round
    final_dict = ALIXE.fishing_round_by_prio_list(dict_first_round_by_rotclu=dict_clust_by_rotclu,
                                                  reference_hkl=reference_hkl, sg_symbol=sg_symbol,
                                                  phstat_version=phstat_version, path_phstat=path_phstat, ncores=topexp,
                                                  clust_fold=clust_fold, path_ins=path_ins, path_best=path_sym,
                                                  cell=cell,resolution=resolution, cycles=cycles,
                                                  tolerance=tolerance_second_round, orisub=orisub, weight=weight,
                                                  ent_path=ent_filename)

    print "\nTwo steps clustering performed, results can be found at the files info_clust_second_round_raw and info_clust_second_round_table, found in the CLUSTERING folder"
    if expansions == True:
        list_to_expand_second_round = []
        print '\nStarting the expansions of the clusters from the second round'
        expansions_folder = os.path.join(clust_fold, 'EXPANSIONS')
        os.mkdir(expansions_folder)
        for ref in final_dict.keys():
            for key in final_dict[ref].keys():
                if len(final_dict[ref][key].keys()) > 1:
                    print "This cluster ", key, "contains more then one file, we will expand it"
                    list_to_expand_second_round.append(key[:-4])
        al.phase_round_with_shelxe(linea_arg=shelxe_line, lista_clusters=list_to_expand_second_round,
                                   wd=expansions_folder, path_shelxe=shelxe_path, hkl_path=hkl_filename,
                                   ins_path=path_ins, ent_path=ent_filename, fragment_type='phi')
elif mode == "combi":
    print "We are going to combine the results of this first round with the one of ", path_combi
    for fich in os.listdir(path_combi):
        if fich == "CLUSTERING":
            for fich2 in os.listdir(os.path.join(path_combi, fich)):
                if fich2.endswith(".pkl"):
                    print "Found the pkl file of the first round of ", path_combi
                    path_combi_clustering = os.path.join(path_combi, "CLUSTERING")
                    back_first_round = open(os.path.join(path_combi_clustering, 'first_round.pkl'), 'rb')
                    dict_round_combi = cPickle.load(back_first_round)
                    back_first_round.close()
    # print "dict_round_combi",dict_round_combi # COMBI
    # print "dict_clust_by_rotclu",dict_clust_by_rotclu # CURRENT
    # Can we generate a dictionary with a unique rotation cluster and fool the ALIXE.fishing_round_by_prio_list function?
    new_clust_fold = os.path.join(wd, 'COMBI_CLUSTERING')
    try:
        os.mkdir(new_clust_fold)
    except OSError:
        exctype, value = sys.exc_info()[:2]
        if str(value).startswith("[Errno 17] File exists:"):  # Then the folder exists
            print "\n COMBI CLUSTERING folder is already present. Files will be removed to start from the scracht"
            shutil.rmtree(new_clust_fold, ignore_errors=True)
            os.mkdir(new_clust_fold)
    dict_global = {}
    dict_global['0'] = {}
    for rotclu in dict_round_combi.keys():
        for key in dict_round_combi[rotclu].keys():
            name_file = os.path.split(key)[1]
            new_key = os.path.join(new_clust_fold, name_file)
            os.link(key, new_key)
            dict_global['0'][new_key] = copy.deepcopy(dict_round_combi[rotclu][key])
    for rotclu in dict_clust_by_rotclu.keys():
        for key in dict_clust_by_rotclu[rotclu].keys():
            name_file = os.path.split(key)[1]
            new_key = os.path.join(new_clust_fold, name_file)
            os.link(key, new_key)
            dict_global['0'][new_key] = copy.deepcopy(dict_clust_by_rotclu[rotclu][key])
    # dict_first_round_by_rotclu, reference_hkl, sg_symbol
    final_dict = ALIXE.fishing_round_by_prio_list(dict_first_round_by_rotclu=dict_global, reference_hkl=reference_hkl,
                                                  sg_symbol=sg_symbol, weight=weight,
                                                  phstat_version=phstat_version, path_phstat=path_phstat, ncores=topexp,
                                                  clust_fold=new_clust_fold, path_ins=path_ins, path_best=path_best,
                                                  cell=cell,resolution=resolution, cycles=cycles,
                                                  tolerance=tolerance_second_round, orisub=orisub)
    if expansions == True:
        list_to_expand_combi_round = []
        print '\nStarting the expansions of the clusters from the combination round'
        expansions_folder = os.path.join(new_clust_fold, 'EXPANSIONS')
        os.mkdir(expansions_folder)
        for ref in final_dict.keys():
            for key in final_dict[ref].keys():
                if len(final_dict[ref][key].keys()) > 1:
                    print "This cluster ", key, "contains more then one file, we will expand it"
                    list_to_expand_combi_round.append(key[:-4])
        al.phase_round_with_shelxe(linea_arg=shelxe_line, lista_clusters=list_to_expand_combi_round,
                                   wd=expansions_folder, path_shelxe=shelxe_path, hkl_path=hkl_filename,
                                   ins_path=path_ins, ent_path=ent_filename, fragment_type='phi')

# Print final time
#new_now = time.strftime("%c")
#print "Current date & time " + time.strftime("%c")
new_now=time.time()
final_string = '\nTotal time spent in running autoalixe is '+str((new_now-now))+' seconds , or '+str((new_now-now)/60)+' minutes \n Command line used was '+str(sys.argv)
log_file.write(final_string)
print final_string
del log_file
