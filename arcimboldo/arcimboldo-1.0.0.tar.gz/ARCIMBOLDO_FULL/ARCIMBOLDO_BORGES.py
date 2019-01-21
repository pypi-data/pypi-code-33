#! /usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import cStringIO
import copy
import datetime
import getpass
import hashlib
import os
import re
import operator
import pickle
import shutil
import subprocess
import signal
import sys
import threading
import traceback
import warnings
import xml.etree.ElementTree as ET
from optparse import OptionParser
from optparse import SUPPRESS_HELP
from Bio.PDB import PDBExceptions
from Bio.PDB import *

import numpy
from termcolor import colored

import ADT
import ANOMLIB
import alixe_library as al
import arci_output
import Bioinformatics3
import Bioinformatics
import Data
import Grid
import Quaternions
import SELSLIB2
import SystemUtility
import ALIXE

warnings.simplefilter("ignore", PDBExceptions.PDBConstructionWarning)

"""ARCIMBOLDO-BORGES exploits libraries of folds to phase macromolecular structures. This module
contains the main program"""

#######################################################################################################
#                                            FUNCTIONS                                                #
#######################################################################################################

def startROT_NODE(datafile):
    """ Clustering of rotations in multiprocessing, in the situation where more than 8 cores are available.

    It will compute rotations for 1000 models, and then, use these first 1000 for clustering the rest in parallel
    (-j argument in ARCIMBOLDO_BORGES)

    :param datafile:
    :type datafile:
    :return:
    :rtype:
    """

    f = open(datafile, "r")
    lista_dati = pickle.load(f)
    f.close()
    os.remove(datafile)
    SELSLIB2.PATH_NEW_PHASER = lista_dati[0]
    SELSLIB2.PATH_NEW_SHELXE = lista_dati[1]
    SELSLIB2.PATH_NEW_ARCIFIRE = lista_dati[2]
    DicParameters = lista_dati[3]
    nice = lista_dati[4]
    DicGridConn = lista_dati[5]
    RotClu = lista_dati[6]
    nameJob = lista_dati[7]
    outputDicr = lista_dati[8]
    nqueue = lista_dati[9]
    laue = lista_dati[10]
    ncs = lista_dati[11]
    spaceGroup = lista_dati[12]
    ensembles = lista_dati[13]
    clusteringAlg = lista_dati[14]
    excludeLLG = lista_dati[15]
    fixed_frags = lista_dati[16]
    cell_dim = lista_dati[17]
    thresholdCompare = lista_dati[18]
    evaLLONG = lista_dati[19]
    isArcimboldo = lista_dati[20]
    tops = lista_dati[21]
    LIMIT_CLUSTER = lista_dati[22]
    applyNameFilter = lista_dati[23]
    candelete = lista_dati[24]
    giveids = lista_dati[25]
    Clusts = lista_dati[26]
    sym = lista_dati[27]
    GRID_TYPE = lista_dati[28]
    QNAME = lista_dati[29]
    FRACTION = lista_dati[30]
    PARTITION = lista_dati[31]
    make_positive_llg = lista_dati[32]    

    cm = None
    if cm == None:
        if GRID_TYPE == "Condor":
            cm = Grid.condorManager()
        elif GRID_TYPE == "SGE":
            cm = Grid.SGEManager(qname=QNAME, fraction=FRACTION)
        elif GRID_TYPE == "MOAB":
            cm = Grid.MOABManager(partition=PARTITION)
        elif GRID_TYPE == "SLURM":
            if PARTITION != None and PARTITION != '':
                cm = Grid.SLURMManager(partition=PARTITION)
            else:
                cm = Grid.SLURMManager()
        elif GRID_TYPE == "TORQUE":
            FRACTION = setupbor.getint("TORQUE", "cores_per_node")
            PARALLEL_JOBS = setupbor.getint("TORQUE", "number_of_parallel_jobs")
            MAUI = setupbor.getboolean("TORQUE", "maui")
            cm = Grid.TORQUEManager(qname=QNAME, cores_per_node=FRACTION, parallel_jobs=PARALLEL_JOBS, maui=MAUI)

    if cm is not None:
        cm.setRank("kflops")
        cm.nice_user = "true"

    quate = Quaternions.Quaternions()

    merged, unmerged, convNames = SELSLIB2.evaluateFRF_clusterOnce(DicParameters=DicParameters, cm=cm, sym=sym,
                                                                   DicGridConn=DicGridConn, RotClu=RotClu,
                                                                   nameJob=nameJob,outputDicr=outputDicr, nqueue=nqueue,
                                                                   quate=quate, laue=laue, ncs=ncs,
                                                                   spaceGroup=spaceGroup,ensembles=ensembles,
                                                                   clusteringAlg=clusteringAlg,
                                                                   excludeLLG=excludeLLG, fixed_frags=fixed_frags,
                                                                   cell_dim=cell_dim, thresholdCompare=thresholdCompare,
                                                                   evaLLONG=evaLLONG, isArcimboldo=isArcimboldo,
                                                                   tops=tops, LIMIT_CLUSTER=LIMIT_CLUSTER,
                                                                   applyNameFilter=applyNameFilter, candelete=False,
                                                                   giveids=giveids, merge=Clusts,
                                                                   make_positive_llg=make_positive_llg)

    SELSLIB2.writeSumClusters(merged, outputDicr, "merged", convNames)
    SELSLIB2.writeSumClusters(unmerged, outputDicr, "unmerged", convNames)

    f = open(os.path.join(outputDicr, nameJob + "_end.txt"), "w")
    f.write("EXIT STATUS: SUCCESS")
    f.close()


def startARCIMBOLDO_BORGES(BorData, isShredder, input_bor, DicParameters={}, DicGridConn={}, cm=None, sym=None,
                           doTest=True, mtz_given="", F_given="", SIGF_given="", tNCS_bool_given="", Intensities=False, Aniso=True,
                           normfactors="", tncsfactors="", nice=0, out_phaser_given="", fneed=False,
                           startCheckQueue=False, skip_mr=False, dictio_shred_annotation=None):
    """

    :param BorData:
    :type BorData:
    :param isShredder: indicates whether the ARCIMBOLDO-BORGES run comes from an spherical SHREDDER call
    :type isShredder: bool
    :param input_bor:
    :type input_bor:
    :param DicParameters:
    :type DicParameters:
    :param DicGridConn:
    :type DicGridConn:
    :param cm:
    :type cm:
    :param sym:
    :type sym:
    :param doTest:
    :type doTest:
    :param mtz_given:
    :type mtz_given:
    :param F_given:
    :type F_given:
    :param SIGF_given:
    :type SIGF_given:
    :param Intensities:
    :type Intensities:
    :param Aniso:
    :type Aniso:
    :param normfactors:
    :type normfactors:
    :param tncsfactors:
    :type tncsfactors:
    :param nice:
    :type nice:
    :param out_phaser_given:
    :type out_phaser_given:
    :param fneed:
    :type fneed:
    :param startCheckQueue:
    :type startCheckQueue:
    :param skip_mr:
    :type skip_mr:
    :param dictio_shred_annotation:
    :type dictio_shred_annotation:
    :return:
    :rtype:
    """
    try:
        Config_1 = ConfigParser.ConfigParser()
        Config_1.read(input_bor)
        coiled_coil = Config_1.getboolean("ARCIMBOLDO-BORGES", "coiled_coil")
        Config_1 = None
    except:
        coiled_coil = False

    if coiled_coil:
        print 'Changing defaults for Coiled Coil mode'
        PACK_TRA = True
        Data.defaults_bor = Data.defaults_bor.replace("PACK_TRA: False", "PACK_TRA: True")
        USE_TNCS = False
        Data.defaults_bor = Data.defaults_bor.replace("TNCS: True", "TNCS: False")
        VRMS = True
        Data.defaults_bor = Data.defaults_bor.replace("VRMS: False", "VRMS: True")
        # TODO: also check that library to be used contains helices!

    if not isShredder:
        BorData.readfp(cStringIO.StringIO(Data.defaults_bor))
        BorData.read(input_bor)

    model_directory = None

    allborf = cStringIO.StringIO()
    BorData.write(allborf)
    allborf.flush()
    allborf.seek(0)
    allbor = allborf.read()
    allborf.close()
    f = open("/tmp/temp.bor", "w")
    f.write(allbor)
    f.close()
    Config = ConfigParser.ConfigParser()
    Config.readfp(open('/tmp/temp.bor'))
    os.remove("/tmp/temp.bor")

    job_type = "ARCIMBOLDO-BORGES"
    llgdic=None         #NS: Needed later in shelxe_cycle

    try:
        model_directory = Config.get(job_type, "library_path")
    except:
        print colored("FATAL", "red"), "[" + job_type + "]\n library_path: \n Is a mandatory keyword."
        sys.exit(1)

    if not os.path.exists(os.path.abspath(model_directory)):
        print colored("FATAL",
                      "red"), "The path given as library_path it does not exist or it is not accessible by the user: ", getpass.getuser()
        sys.exit(1)

    model_directory = os.path.abspath(model_directory)

    if not os.path.isdir(model_directory):
        print colored("FATAL", "red"), "The path given as library_path is not a directory."
        sys.exit(1)

    model_file = ""
    error_lib = False
    files_error = []
    for root, subFolders, files in os.walk(model_directory):
        for fileu in files:
            pdbf = os.path.join(root, fileu)
            if pdbf.endswith(".pdb"):
                model_file = pdbf
                datos = os.path.basename(pdbf).split("_")
                if len(datos) != 3:
                    error_lib = True
                    files_error.append(pdbf)
                try:
                    s = int(datos[1])
                    z = int(datos[2][:-4])
                except:
                    error_lib = True
                    files_error.append(pdbf)

    if error_lib:
        print colored("FATAL", "red"), "The library given in input: ", model_directory
        print "It is not a standard BORGES library. The following files does not respect the BORGES name convention:"
        for files in files_error:
            print files
        sys.exit(1)

    toExit = False
    try:
        distribute_computing = Config.get("CONNECTION", "distribute_computing").strip().lower()
        if distribute_computing in ["multiprocessing", "supercomputer"]:
            SELSLIB2.PATH_NEW_PHASER = Config.get("LOCAL", "path_local_phaser")
            SELSLIB2.PATH_NEW_SHELXE = Config.get("LOCAL", "path_local_shelxe")
            SELSLIB2.PATH_PHSTAT = Config.get("LOCAL", "path_local_phstat")
            path_to_arciborges = os.path.abspath(__file__)
            if path_to_arciborges.endswith('.py'): # Then we need to change the default
                #arcifullpath = os.path.dirname(path_to_arciborges)
                Config.set("LOCAL", "path_local_arcimboldo",path_to_arciborges)
                SELSLIB2.PATH_NEW_ARCIFIRE = Config.get("LOCAL", "path_local_arcimboldo")
            else: # we are in ccp4, we can keep the default
                SELSLIB2.PATH_NEW_ARCIFIRE = Config.get("LOCAL", "path_local_arcimboldo")

        mtz = Config.get("GENERAL", "mtz_path")
        hkl = Config.get("GENERAL", "hkl_path")
        mtz = os.path.abspath(mtz)
        hkl = os.path.abspath(hkl)
        ent = Config.get("GENERAL", "ent_path")
        pdbcl = Config.get("GENERAL", "pdb_path")
        if ent != None and ent.endswith(".ent"):
            ent = os.path.abspath(ent)
        else:
            ent = ""

        if pdbcl != None and pdbcl.endswith(".pdb"):
            pdbcl = os.path.abspath(pdbcl)
        else:
            pdbcl = ""

        try:
            sequence = Config.get(job_type, "sequence")
            for lett in sequence:
                if lett not in Bioinformatics.AALISTOL:
                    print "Sequence is not valid, symbol", lett, "not recognized"
                    toExit = True
                    sys.exit(0)
            MW = float(len(lett) * 100)
        except:
            MW = Config.getfloat(job_type, "molecular_weight")

        try:
            NC = Config.getint("ARCIMBOLDO-BORGES", "number_of_component")   
        except:
            NC=-1    #NS: Now NC == -1 means automatic mode

        try:
            F = Config.get("ARCIMBOLDO-BORGES", "f_label")
            SIGF = Config.get("ARCIMBOLDO-BORGES", "sigf_label")
            Intensities = False
        except:
            F = Config.get("ARCIMBOLDO-BORGES", "i_label")
            SIGF = Config.get("ARCIMBOLDO-BORGES", "sigi_label")
            Intensities = True

        nice = Config.getint("ARCIMBOLDO-BORGES", "nice")
        RMSD = Config.getfloat(job_type, "rmsd")
    except:
        print "Mandatory tags are missing:"
        print traceback.print_exc(file=sys.stdout)
        toExit = True

    if toExit:
        sys.exit(0)

    Aniso = Config.getboolean("ARCIMBOLDO-BORGES", "ANISO")
    # NOTE CM: Testing for microED data
    formfactors = Config.get("ARCIMBOLDO-BORGES", "formfactors")
    # NOTE CM: Testing for microED data

    peaks = 75

    # SET OUTPUT PARAMETERS
    current_directory = Config.get("GENERAL", "working_directory")

    #NS ANOM: parsing the anomalous parameters
    ANOMDIR=os.path.normpath(os.path.abspath(os.path.join(current_directory,"ANOMFILES")))         #just a name for the moment, the directory is not created yet
    startExpAnomDic, otherAnomParamDic, fragAnom=ANOMLIB.parseAnomalousParameters(configParserObject=Config, ANOMDIR=ANOMDIR)
    ANOMALOUS= True if fragAnom else False                      # A master switch for Anomalous parameters
    ANOM_HARD_FILTER=otherAnomParamDic['hardFilter']            # if True: 'union' selection of solutions discarded during evaluateExpCC from 9.5EXP and 9_EXP, if False: intersection

    if os.path.exists(os.path.join(current_directory, 'temp_transfer')):
        shutil.rmtree(os.path.join(current_directory, 'temp_transfer'))
    if os.path.exists(os.path.join(current_directory, 'grid_jobs')):
        shutil.rmtree(os.path.join(current_directory, 'grid_jobs'))
    if os.path.exists(os.path.join(current_directory, 'temp')):
        shutil.rmtree(os.path.join(current_directory, 'temp'))

    # STATIC REFERENCE TO THE QUATERNION CLASS
    quate = Quaternions.Quaternions()

    # STARTING SYSTEM MANAGER
    if sym == None:
        sym = SystemUtility.SystemUtility()

    try:
        DicParameters = {}
        nameJob = Config.get("ARCIMBOLDO-BORGES", "name_job")
        nameJob = "_".join(nameJob.split())
        if len(nameJob.strip()) == 0:
            print '\nKeyword name_job is empty, setting a default name for the job...'
            nameJob = (os.path.basename(mtz))[:-4] + '_arcimboldo_borges'
        DicParameters["nameExecution"] = nameJob
    except:
        print "Mandatory tags are missing:"
        print traceback.print_exc(file=sys.stdout)

    nameOutput = DicParameters["nameExecution"]

    if os.path.exists(os.path.join(current_directory, nameOutput + ".html")):
        os.remove(os.path.join(current_directory, nameOutput + ".html"))
    if os.path.exists(os.path.join(current_directory, nameOutput + ".xml")):
        os.remove(os.path.join(current_directory, nameOutput + ".xml"))

    setupbor = None
    if distribute_computing == "remote_grid":
        path_bor = Config.get("CONNECTION", "setup_bor_path")
        if path_bor is None or path_bor == "" or not os.path.exists(path_bor):
            print colored(
                "ATTENTION: the path given for the setup.bor does not exist.\n Please contact your administrator",
                "red")
            sys.exit(1)
        try:
            setupbor = ConfigParser.ConfigParser()
            setupbor.readfp(open(path_bor))
            DicGridConn["username"] = setupbor.get("GRID", "remote_frontend_username")
            DicGridConn["host"] = setupbor.get("GRID", "remote_frontend_host")
            DicGridConn["port"] = setupbor.getint("GRID", "remote_frontend_port")
            DicGridConn["passkey"] = Config.get("CONNECTION", "remote_frontend_passkey")
            DicGridConn["promptA"] = (setupbor.get("GRID", "remote_frontend_prompt")).strip() + " "
            DicGridConn["isnfs"] = setupbor.getboolean("GRID", "remote_fylesystem_isnfs")
            try:
                DicGridConn["remote_submitter_username"] = setupbor.get("GRID", "remote_submitter_username")
                DicGridConn["remote_submitter_host"] = setupbor.get("GRID", "remote_submitter_host")
                DicGridConn["remote_submitter_port"] = setupbor.getint("GRID", "remote_submitter_port")
                DicGridConn["promptB"] = (setupbor.get("GRID", "remote_submitter_prompt")).strip() + " "
            except:
                pass
            DicGridConn["home_frontend_directory"] = setupbor.get("GRID", "home_frontend_directory")
            SELSLIB2.PATH_NEW_PHASER = setupbor.get("GRID", "path_remote_phaser")
            SELSLIB2.PATH_NEW_SHELXE = setupbor.get("GRID", "path_remote_shelxe")
            SELSLIB2.PATH_NEW_ARCIFIRE = setupbor.get("GRID", "path_remote_arcimboldo")
            SELSLIB2.GRID_TYPE_R = setupbor.get("GRID", "type_remote")
            if SELSLIB2.GRID_TYPE_R == "Condor":
                SELSLIB2.SHELXE_REQUIREMENTS = setupbor.get("CONDOR", "requirements_shelxe")
                SELSLIB2.PHASER_REQUIREMENTS = setupbor.get("CONDOR", "requirements_phaser")
                SELSLIB2.BORGES_REQUIREMENTS = setupbor.get("CONDOR", "requirements_borges")
            SELSLIB2.LOCAL = False
        except:
            print colored("ATTENTION: Some keyword in your configuration files are missing. Contact your administrator",
                          "red")
            print "Path bor given: ", path_bor
            print traceback.print_exc(file=sys.stdout)
            sys.exit(1)
    elif distribute_computing == "local_grid":
        path_bor = Config.get("CONNECTION", "setup_bor_path")
        if path_bor is None or path_bor == "" or not os.path.exists(path_bor):
            print colored(
                "ATTENTION: the path given for the setup.bor does not exist.\n Please contact your administrator",
                "red")
            sys.exit(1)
        try:
            setupbor = ConfigParser.ConfigParser()
            setupbor.readfp(open(path_bor))
            SELSLIB2.PATH_NEW_PHASER = setupbor.get("LOCAL", "path_local_phaser")
            SELSLIB2.PATH_NEW_SHELXE = setupbor.get("LOCAL", "path_local_shelxe")
            SELSLIB2.PATH_NEW_ARCIFIRE = setupbor.get("LOCAL", "path_local_arcimboldo")
            SELSLIB2.PATH_PHSTAT = setupbor.get("LOCAL", "path_local_phstat")
            SELSLIB2.GRID_TYPE_L = setupbor.get("GRID", "type_local")
            if SELSLIB2.GRID_TYPE_L == "Condor":
                SELSLIB2.SHELXE_REQUIREMENTS = setupbor.get("CONDOR", "requirements_shelxe")
                SELSLIB2.PHASER_REQUIREMENTS = setupbor.get("CONDOR", "requirements_phaser")
                SELSLIB2.BORGES_REQUIREMENTS = setupbor.get("CONDOR", "requirements_borges")
        except:
            print colored("ATTENTION: Some keyword in your configuration files are missing. Contact your administrator",
                          "red")
            print "Path bor given: ", path_bor
            print traceback.print_exc(file=sys.stdout)
            sys.exit(1)

    if distribute_computing == "supercomputer":
        # TODO: Read the list of available nodes
        path_nodes = Config.get("CONNECTION", "nodefile_path")
        if path_nodes is None or path_nodes == "" or not os.path.exists(path_nodes):
            print colored(
                "ATTENTION: the path given for the node file does not exist.\n Please contact your administrator",
                "red")
            sys.exit(1)
        f = open(path_nodes, "r")
        nodes_list = f.readlines()
        f.close()
        # SELSLIB2.PATH_NEW_ARCIFIRE = nodes_list[0].strip()
        # nodes_list = nodes_list[1:]

        for i in range(len(nodes_list)):
            nodes_list[i] = nodes_list[i][:-1] + "***" + str(i)
        SystemUtility.NODES = nodes_list

    # LOCKING FOR ACCESS OUTPUT FILE
    lock = threading.RLock()
    lock = threading.Condition(lock)

    if startCheckQueue:
        SystemUtility.startCheckQueue(sym, delete_check_file=False)
    # VARIABLES FOR REFINEMENT IN P1
    mtzP1 = Config.get("GENERAL", "mtz_p1_path")
    # TODO: It is important to expand directly the anis.mtz in P1 and not ask the user to give the mtzP1.
    # Remember anis.mtz should be expanded in P1 and not the original one mtz
    PERFORM_REFINEMENT_P1 = False
    if mtzP1 != None and mtzP1 != "" and mtzP1 != " ":
        PERFORM_REFINEMENT_P1 = True
        mtzP1 = os.path.abspath(mtzP1)

    if PERFORM_REFINEMENT_P1:
        Fp1 = Config.get(job_type, "f_p1_label")
        SIGFp1 = Config.get(job_type, "sigf_p1_label")
        NCp1 = Config.getint(job_type, "number_of_component_p1")
    else:
        Fp1 = None
        SIGFp1 = None
        NCp1 = None

    # SETTING
    clusteringAlg = Config.get(job_type, "rotation_clustering_algorithm")
    excludeLLG = Config.getfloat(job_type, "exclude_llg")
    excludeZscore = Config.getfloat(job_type, "exclude_zscore")
    thresholdCompare = Config.getfloat(job_type, "threshold_algorithm")
    USE_PACKING = Config.getboolean(job_type, "use_packing")
    filtClu = Config.getboolean(job_type, "filter_clusters_after_rot")
    USE_TRANSLA = True
    USE_NMA = Config.getboolean(job_type, "NMA")
    USE_RGR = Config.get(job_type, "ROTATION_MODEL_REFINEMENT")
    if USE_RGR.lower() == "both":
        USE_RGR = 2
    elif USE_RGR.lower() == "gyre":
        USE_RGR = 1
    else:
        USE_RGR = 0
    # Check the rmsd decrease step for gyre 
    cycle_ref = Config.getint(job_type, "number_cycles_model_refinement")
    cycles_gyre = cycle_ref
    rmsd_decrease=Config.getfloat(job_type,'step_rmsd_decrease_gyre')
    if USE_RGR != 0  and cycle_ref>1:
        last_rmsd= RMSD-(float(cycle_ref-1)*rmsd_decrease)
    else:
        last_rmsd=RMSD
    if last_rmsd <=0.0:
        print 'EXITING NOW... With the current parameterization, the last rmsd that will be used in the run is ' \
              '0 or smaller. Please change parameterization and rerun'
        sys.exit(0)
    USE_NMA_P1 = Config.getboolean(job_type, "NMA_P1")
    USE_OCC = Config.getboolean(job_type, "OCC")
    prioritize_occ = Config.getboolean(job_type, "prioritize_occ")
    applyNameFilter = Config.getboolean(job_type, "applyTopNameFilter")
    randomAtoms = Config.getboolean(job_type, "extend_with_random_atoms")
    SecStrElong = Config.getboolean(job_type, "extend_with_secondary_structure")
    res_rot = Config.getfloat(job_type, "resolution_rotation")
    sampl_rot = Config.getfloat(job_type, "sampling_rotation")
    res_tran = Config.getfloat(job_type, "resolution_translation")
    sampl_tran = Config.getfloat(job_type, "sampling_translation")
    res_refin = Config.getfloat(job_type, "resolution_refinement")
    sampl_refin = Config.getfloat(job_type, "sampling_refinement")
    RGR_SAMPL = Config.getfloat(job_type, "sampling_gyre")
    res_gyre = Config.getfloat(job_type, "resolution_gyre")
    noDMinitcc = Config.getboolean(job_type, "noDMinitcc")
    savePHS = Config.getboolean(job_type, "savePHS")
    archivingAsBigFile = Config.getboolean(job_type, "archivingAsBigFile")
    alixe = Config.getboolean(job_type, "alixe")
    alixe_mode = Config.get(job_type, "alixe_mode")
    ellg_target = Config.getfloat(job_type, "ellg_target")
    phs_fom_statistics = Config.getboolean(job_type, "phs_fom_statistics")
    n_clusters = Config.getint(job_type, "n_clusters")
    prioritize_phasers = Config.getboolean(job_type, "prioritize_phasers")
    USE_TNCS = Config.getboolean(job_type, "TNCS")
    make_positive_llg = Config.getboolean(job_type, "make_positive_llg")
    #NS 
    solventContent=Config.getfloat(job_type,"solventContent") #Solvent content to use in the shelxe DM calculations --> now taken from unitcell content analysis result following the number of mol/asu
    unitCellcontentAnalysis=Config.getboolean(job_type,"unitCellcontentAnalysis")
    
    fixed_model = Config.get(job_type, "fixed_model")
    if fixed_model.endswith(".pdb"):
        stry = Bioinformatics.getStructure("test", fixed_model)
        if len(stry.get_list()) <= 0:
            print colored("FATAL", "red"), "The model pdb file: " + str(
            os.path.abspath(fixed_model)) + " is not a standard PDB file."
            sys.exit(1)
        if not USE_PACKING:
            print 'The swap model after translation option is not available without packing'
            sys.exit(1)
    else:
        fixed_model = None

    try:
        swap_model_after_translation = Config.get(job_type, "swap_model_after_translation")
        if swap_model_after_translation.endswith(".pdb"):
            stry = Bioinformatics.getStructure("test", swap_model_after_translation)
            if len(stry.get_list()) <= 0:
                print colored("FATAL", "red"), "The model pdb file: " + str(
                os.path.abspath(swap_model_after_translation)) + " is not a standard PDB file."
                sys.exit(1)
        else:
            swap_model_after_translation = None
    except:
        swap_model_after_translation = None

    VRMS = Config.getboolean(job_type, "VRMS")
    VRMS_GYRE = Config.getboolean(job_type, "VRMS_GYRE")
    BFAC = Config.getboolean(job_type, "BFAC")
    BULK_FSOL = Config.getfloat(job_type, "BULK_FSOL")
    BULK_BSOL = Config.getfloat(job_type, "BULK_BSOL")
    RNP_GYRE = Config.getboolean(job_type, "GIMBLE")
    PACK_TRA = Config.getboolean(job_type, "PACK_TRA")
    BASE_SUM_FROM_WD = Config.getboolean(job_type, "BASE_SUM_FROM_WD")
    SELSLIB2.BASE_SUM_FROM_WD = BASE_SUM_FROM_WD
    solution_sorting_scheme = Config.get(job_type, "solution_sorting_scheme").upper()
    sigr = Config.getfloat(job_type, "SIGR")
    sigt = Config.getfloat(job_type, "SIGT")
    preserveChains = Config.getboolean(job_type, "GYRE_PRESERVE_CHAINS")
    CLASHES = Config.getint(job_type, "pack_clashes")
    #NS : I need sometimes to use more autotracing cycles in the end
    nAutoTracCyc = Config.getint(job_type,'nAutoTracCyc')

    #NS: change the number of autotracing cycles per bunch (number of bunches defined by nAutoTracCyc, default:1)
    nBunchAutoTracCyc=Config.getint(job_type,'nBunchAutoTracCyc')

    topFRF = Config.getint(job_type, "topFRF")
    if topFRF <= 0:
        topFRF = None
    topFTF = Config.getint(job_type, "topFTF")
    if topFTF <= 0:
        topFTF = None
    topPACK = Config.getint(job_type, "topPACK")
    if topPACK <= 0:
        topPACK = None
    topRNP = Config.getint(job_type, "topRNP")
    if topRNP <= 0:
        topRNP = None
    topExp = Config.getint(job_type, "topExp") - 1
    if topExp <= 0:
        topExp = None
    force_core = Config.getint(job_type, "force_core")
    if force_core <= 0:
        force_core = None
    force_nsol = Config.getint(job_type, "force_nsol")
    if force_nsol <= 0:
        force_nsol = None

    force_exp = Config.getboolean(job_type, "force_exp")

    if alixe:
        savePHS = True
        archivingAsBigFile = False
        # In any case, in order to use ALIXE it is better to have all phs files already computed
        #if alixe_mode == "two_steps":
        prioritize_phasers = True

    if isShredder and not preserveChains: # in case we are using the communities for annotation
        if Config.getint(job_type, "number_cycles_model_refinement")>2:
            print '\n Autoconfiguring number of cycles of model refinement to 2'

    fixed_frags = 1 #for this mode is always one it will change for LEGO
    evaLLONG = False #It just works with helices and distributionCV better not use it for now

    # STARTING THE GRID MANAGER
    GRID_TYPE = ""
    QNAME = ""
    FRACTION = 1
    PARTITION = ""

    if distribute_computing == "remote_grid":
        GRID_TYPE = setupbor.get("GRID", "type_remote")
    elif distribute_computing == "local_grid":
        GRID_TYPE = setupbor.get("GRID", "type_local")

    if cm == None:
        if GRID_TYPE == "Condor":
            cm = Grid.condorManager()
        elif GRID_TYPE == "SGE":
            QNAME = setupbor.get("SGE", "qname")
            FRACTION = setupbor.getfloat("SGE", "fraction")
            cm = Grid.SGEManager(qname=QNAME, fraction=FRACTION)
        elif GRID_TYPE == "MOAB":
            PARTITION = setupbor.get("MOAB", "partition")
            # FRACTION = setupbor.getfloat("MOAB","partition")
            cm = Grid.MOABManager(partition=PARTITION)
        elif GRID_TYPE == "SLURM":
            PARTITION = setupbor.get("SLURM", "partition")
            if PARTITION != None and PARTITION != '':
                cm = Grid.SLURMManager(partition=PARTITION)
            else:
                cm = Grid.SLURMManager()
        elif GRID_TYPE == "TORQUE":
            QNAME = setupbor.get("TORQUE", "qname")
            FRACTION = setupbor.getint("TORQUE", "cores_per_node")
            PARALLEL_JOBS = setupbor.getint("TORQUE", "number_of_parallel_jobs")
            MAUI = setupbor.getboolean("TORQUE", "maui")
            cm = Grid.TORQUEManager(qname=QNAME, cores_per_node=FRACTION, parallel_jobs=PARALLEL_JOBS, maui=MAUI)

    if cm is not None:
        cm.setRank("kflops")
        cm.nice_user = "true"
        # TODO: Eliminate the SGE.py
        PATH_REMOTE_SGEPY = setupbor.get("GRID", "path_remote_sgepy")
        PATH_REMOTE_PYTHON_INTERPRETER = setupbor.get("GRID", "python_remote_interpreter")
        PATH_LOCAL_PYTHON_INTERPRETER = setupbor.get("LOCAL", "python_local_interpreter")

        if PATH_REMOTE_PYTHON_INTERPRETER.strip() in ["", None]:
            PATH_REMOTE_PYTHON_INTERPRETER = "/usr/bin/python"

        if PATH_LOCAL_PYTHON_INTERPRETER.strip() in ["", None]:
            PATH_LOCAL_PYTHON_INTERPRETER = "/usr/bin/python"

    # TEST THE SHELXE USER LINE
    try:
        linsh = Config.get(job_type, "shelxe_line")
        if linsh == None or linsh.strip() == "":
            raise Exception

        listash = linsh.split()
        for toc in range(len(listash)):
            param = listash[toc]
            if param.startswith("-a"):
                param = "-a0"
                if toc + 1 < len(listash) and not listash[toc + 1].startswith("-"):
                    listash[toc + 1] = ""
                listash[toc] = param
                break

        if os.path.exists(ent):
            listash.append("-x")

        linsh = " ".join(listash)
        shlxLinea0 = linsh
    except:
        if os.path.exists(ent):
            shlxLinea0 = "-m1 -a0 -x"
        else:
            shlxLinea0 = "-m1 -a0"

    # ANISOTROPY CORRECTION AND TESTS

    if doTest:
        anismtz, normfactors, tncsfactors, F, SIGF, spaceGroup, cell_dim, resolution, unique_refl, aniout, anierr, \
        fneed, shelxe_new, tNCS_bool = SELSLIB2.anisotropyCorrection_and_test(cm=cm, sym=sym, DicGridConn=DicGridConn,
                                                                              DicParameters=DicParameters,
                                                                              current_dir=current_directory, mtz=mtz,
                                                                              F=F, SIGF=SIGF, Intensities=Intensities,
                                                                              Aniso=Aniso, nice=nice, pda=Data.th70pdb,
                                                                              hkl=hkl, ent=ent, formfactors=formfactors,
                                                                              shelxe_line=shlxLinea0)
    else:
        mtz = mtz_given
        F = F_given
        SIGF = SIGF_given
        tNCS_bool = tNCS_bool_given
        # READING THE SPACEGROUP FROM PHASER OUT
        spaceGroup = SELSLIB2.readSpaceGroupFromOut(out_phaser_given)
        # READING THE CELL DIMENSIONS FROM PHASER OUT
        cell_dim = SELSLIB2.cellDimensionFromOut(out_phaser_given)
        # READING THE RESOLUTION FROM PHASER OUT
        resolution = SELSLIB2.resolutionFromOut(out_phaser_given)
        # READING THE NUMBER OF UNIQUE REFLECTIONS FROM PHASER OUT
        unique_refl = SELSLIB2.uniqueReflectionsFromOut(out_phaser_given)


    # Testing the fortran executable for the phase combination
    #print 'SHERLOCK SELSLIB2.PATH_PHSTAT', SELSLIB2.PATH_PHSTAT
    #print 'SHERLOCK os.path.exists(SELSLIB2.PATH_PHSTAT)', os.path.exists(SELSLIB2.PATH_PHSTAT)
    if not os.path.exists(SELSLIB2.PATH_PHSTAT):
        print 'Sorry, the path given to the phstat executable does not exist'
        print 'Please change the keyword path_local_phstat to a valid path or deactivate the alixe option'
        sys.exit(0)
    else:
        # Check anyway that the program works
        try:
            p = subprocess.Popen(SELSLIB2.PATH_PHSTAT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            complete_output, errors = p.communicate()
            if len(complete_output) > 0:
                print 'phstat was run succesfully'
            else:
                print 'Sorry, there is some error with the path given as phstat_executable'
                sys.exit(0)
        except:
            print 'Sorry, there is some error with the path given as phstat_executable'
            sys.exit(0)

    sg = Config.get(job_type, "spacegroup")
    if sg != "" and sg != " " and sg != None:
        spaceGroup = sg

    # Check spaceGroup symmetry
    print '\n Space group set to ', spaceGroup
    dictio_space_groups=al.get_spacegroup_dictionary()
    try:
        sg_number=int(spaceGroup)
    except:
        sg_number = al.get_space_group_number_from_symbol(spaceGroup)
    if sg_number==None:
        print '\n Sorry, the space group given is not supported'
        sys.exit(0)
    else:
        print '\n Input space group has been correctly processed'
        # Perform specific actions depending on space group
        if sg_number == 1:
            print '\n Space group is P1 '
            print "\n Gimble refinement will be equivalent to GYRE in this space group, automatically setting to False"
            RNP_GYRE = False
            if not tNCS_bool:  # If no tNCS has been found
                print '\n Data does not appear to have tNCS, setting tncs keyword to false'
                USE_TNCS = False
    sg_symbol=dictio_space_groups[sg_number]['symbol']
    spaceGroup=sg_symbol

    #NS ANOM checks and update the required files for experimental phasing and generates the hkl_fa and ins_fa files with SHELXC file if they don't exist
    if ANOMALOUS:
#updateAnomParamDic(hkl=None, mtz=None, current_directory=None, cell_dim=None, sg_number=1,otherAnomParamDic=None, st     artExpAnomDic=None)
        startExpAnomDic=ANOMLIB.updateAnomParamDic(hkl=hkl, mtz=mtz, current_directory=current_directory, otherAnomParamDic=otherAnomParamDic, cell_dim=cell_dim, sg_number=sg_number, startExpAnomDic=startExpAnomDic)
        delEvalDir=True             #Flag to delete the EVALUATION directory in ANOMDIR
        solutions_filtered_out={}    #will contain the names of all the solutions to remove after evaluateExp or evaluateExp_cc functions
        convNamesAnom={}
        savePHS=True
        if not startExpAnomDic:
            print("Error, something went wrong when trying to update the anomalous parameters, quitting now")
            sys.exit(1)

    # Configure shelxe lines
    try:
        linsh = Config.get(job_type, "shelxe_line")

        try:
            linsh_last = Config.get(job_type, "shelxe_line_last")

        except:
            # TODO: Decide what to do when is user-given line and it does not set the shelxe_line_last
            # TODO: But we need to reduce it to one cycle
            linsh_last_list = []
            list_args_linsh_last = linsh.split()
            for arg in list_args_linsh_last:
                if not arg.startswith('-a'):
                    linsh_last_list.append(arg)
            linsh_last = (" ".join(linsh_last_list))+' -a1'
        if linsh == None or linsh.strip() == "":
            raise Exception 
    except:
        # NOTE: if shelxe_new is True, it is because we are using a version from Isabel that supports her autotracing
        if resolution <= 1.0:
            linsh = "-m200 -a8 -s0.25 -v0.5 -t10 -q -o -y" + str('%.2f' % (resolution))
            linsh_last = "-m200 -a1 -s0.2 -v0.5 -t10 -q -o -y" + str('%.2f' % (resolution)) + " -e1.0"
            if shelxe_new and coiled_coil:
                linsh = "-m200 -a8 -s0.25 -v0.5 -t10 -Q -I200 -o -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution-0.3))
                linsh_last = "-m200 -a1 -s0.2 -v0.5 -t10 -q -I200 -o -y" + str('%.2f' % (resolution)) + " -e1.0"
        elif resolution <= 1.3:  # and resolution > 1.0:
            linsh = "-m100 -a8 -s0.35 -v0.25 -t10 -q -o -y" + str('%.2f' % (resolution))
            linsh_last = "-m100 -a1 -s0.3 -v0.25 -t10 -q -o -y" + str('%.2f' % (resolution)) + " -e1.0"
            if shelxe_new and coiled_coil:
                linsh = "-m100 -a8 -s0.35 -v0.5 -t10 -Q -I100 -o -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution-0.3))
                linsh_last = "-m100 -a1 -s0.3 -v0.25 -t10 -q -o -I100 -y" + str('%.2f' % (resolution)) + " -e1.0"
        elif resolution <= 1.5:  # and resolution > 1.3:
            linsh = "-m50 -a8 -s0.45 -v0.1 -t10 -q -o -y" + str('%.2f' % (resolution))
            linsh_last = "-m50 -a1 -s0.4 -v0.1 -t10 -q -o -y" + str('%.2f' % (resolution)) + " -e" + \
                         str('%.2f' % (resolution - 0.5))
            if shelxe_new and coiled_coil:
                linsh = "-m50 -a8 -s0.45 -v0.1 -t10 -Q -I50 -o -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution-0.3))
                linsh_last = "-m50 -a1 -s0.4 -v0.1 -t10 -q -o -I50 -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution-0.5))
        elif resolution <= 2.0:  # and resolution > 1.5:
            linsh = "-m15 -a8 -s0.5 -v0 -t10 -q -o -y" + str('%.2f' % (resolution))
            linsh_last = "-m15 -a1 -s0.45 -v0 -t10 -q -o -y" + str('%.2f' % (resolution))+ " -e" + \
                        str('%.2f' % (resolution-0.5))
            if shelxe_new and coiled_coil:
                linsh = "-m15 -a8 -s0.5 -v0 -t10 -Q -I15 -o -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution-0.3))
                linsh_last = "-m15 -a1 -s0.45 -v0 -t10 -q -o -I15 -y" + str('%.2f' % (resolution)) + " -e" + \
                             str('%.2f' % (resolution - 0.5))
        else:  # resolution > 2.0:
            linsh = "-m10 -a8 -s0.6 -v0 -t10 -q -o -y" + str('%.2f' % (resolution))
            linsh_last = "-m10 -a1 -s0.55 -v0 -t10 -q -o -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution-0.5))
            if shelxe_new and coiled_coil and resolution <= 2.5:
                linsh = "-m10 -a8 -s0.6 -v0 -t10 -Q -I10 -o -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution - 0.3))
                linsh_last = "-m10 -a1 -s0.55 -v0 -t10 -q -o -I10 -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution - 0.5))
            elif shelxe_new and coiled_coil and resolution <= 3.0:
                linsh = "-m5 -a8 -s0.6 -v0 -t10 -Q -I5 -o -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution - 0.3))
                linsh_last = "-m5 -a1 -s0.55 -v0 -t10 -q -o -I5 -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution - 0.5))

        if fneed:
            linsh += " -f"
            linsh_last += " -f"

    # Set properly the shelxe_line at the config so that the html shows it
    Config.set(job_type, "shelxe_line", linsh)
    Config.set(job_type, "shelxe_line_last", linsh_last)
    
    listash = linsh.split()
    nautocyc = 0
    listash1 = linsh.split()
    for toc in range(len(listash)):
        param = listash[toc]
        if param.startswith("-a"):
            nautocyc = int(param[2:]) + 1
            param = "-a0"
            nk = 0
            for prr in listash:
                if prr.startswith("-K"):
                    nk = int(prr[2:])
                    break
            if nk == 0:
                param1 = "-a1"
            else:
                param1 = "-a" + str(nk + 1)
                nautocyc = nautocyc - (nk + 1)

            if toc + 1 < len(listash) and not listash[toc + 1].startswith("-"):
                listash[toc + 1] = ""
                listash1[toc + 1] = ""
            listash[toc] = param
            listash1[toc] = param1
            break

    #NS: bypass the number of autotracing cycles
    if nAutoTracCyc >0:
        nautocyc = nAutoTracCyc +1

    if noDMinitcc:
        for toc in range(len(listash)):
            param = listash[toc]
            if param.startswith("-m"):
                ndenscyc = int(param[2:]) + 1
                param = "-m5"
                if toc + 1 < len(listash) and not listash[toc + 1].startswith("-"):
                    listash[toc + 1] = ""
                listash[toc] = param
                break

    if os.path.exists(ent):
        listash.append("-x")
        listash1.append("-x")
        linsh_last = linsh_last + ' -x '

    linsh = " ".join(listash)
    shlxLinea0 = linsh
    shlxLinea1 = " ".join(listash1)
    shlxLineaLast = linsh_last

    #NS write a Coot script for visualizing best.pdb etc
    if ANOMALOUS:
        ANOMLIB.writeCOOTscript(current_directory,spaceGroup=spaceGroup, unitCell=cell_dim)

    #NS CALCULATE PATTERSON PEAKS FROM DATA
    pattersonPeaks=None
    if ANOMALOUS:
        if nBunchAutoTracCyc == 1:
            nBunchAutoTracCyc=ANOMLIB.NBUNCH 
        if otherAnomParamDic['patterson']:
            pattersonPeaks=ANOMLIB.pattersonFromData(pathTo_hkl_file=startExpAnomDic['hkl_fa'], resolution=resolution, spaceGroupNum=sg_number,unitCellParam=cell_dim, amplitudes=True, harker=True)
    
    #NS: CHANGING THE DEFAULT NUMBER OF AUTOTRACING CYCLES PER BUNCH (DEFAULT 1)
    if nBunchAutoTracCyc>1:
        print("\nINFO: Changing the defaut number of autotracing cycle per bunch from 1 to {}".format(nBunchAutoTracCyc))
        shlxLinea1, shlxLineaLast = SELSLIB2.changeArgInShelxeLine(shelxeLineList=(shlxLinea1, shlxLineaLast), argDic={'-a': nBunchAutoTracCyc})
        print("INFO: shlxLinea1, shlxLineaLast changed to {}, {}".format(shlxLinea1, shlxLineaLast))

    #NS UNIT CELL CONTENT ANALYSIS (optional)
    if unitCellcontentAnalysis or NC<=0:
        print("UNIT CELL CONTENT ANALYSIS")
        solventContent, NC= SELSLIB2.unitCellContentAnalysis(current_directory=current_directory, spaceGroup=spaceGroup,cell_dim=cell_dim, MW=MW, resolution=resolution ,moleculeType="protein", numberOfComponents=NC,solventContent=solventContent)
        
        if solventContent is None or NC is None:
            print("ERROR, your solvent content or number of components is lower or equal to zero, quitting now!")
            sys.exit(1)
        #Set up the shelxe line for further steps (adding radius of the sphere of influence and solvent content)
        solvarg_re=re.compile(r"\-s[\d.]+")
        m0=solvarg_re.search(shlxLinea0)
        m1=solvarg_re.search(shlxLinea1)
        #mP=solvarg_re.search(shlxLineaP)
        mLast=solvarg_re.search(shlxLineaLast)

        if resolution>2.5:                    #NS: Arbitrary cutoff, radius of the sphere of inflence
            shlxLinea0 += " -S%s"%resolution  
            shlxLinea1 += " -S%s"%resolution
            #shlxLineaP += " -S%s"%resolution
            shlxLineaLast += " -S%s"%resolution

        #replace the solvent content if already present in the shelxe command line, add it otherwise
        if m0:
            shlxLinea0 = re.sub(solvarg_re,"-s%.2f"%solventContent, shlxLinea0)
        else:
            shlxLinea0 += " -s%.2f"%solventContent

        if m1:
            shlxLinea1 = re.sub(solvarg_re,"-s%.2f"%solventContent, shlxLinea1)
        else:
            shlxLinea1 += " -s%.2f"%solventContent

        # if mP:
        #     shlxLineaP = re.sub(solvarg_re,"-s%.2f"%solventContent, shlxLineaP)
        # else:
        #     shlxLineaP += " -s%.2f"%solventContent

        if mLast:
            shlxLineaLast = re.sub(solvarg_re,"-s%.2f"%solventContent, shlxLineaLast)
        else:
            shlxLineaLast += " -s%.2f"%solventContent

        del(m0,m1,mLast)    #Remove these variable from memory 

    # RETRIEVING THE LAUE SIMMETRY FROM THE SPACEGROUP
    laue = quate.getLaueSimmetry(spaceGroup)
    if laue == None:
        print 'Some problem happened during retrieval of the laue symmetry for this space group'

    ncs = []  # handling of non crystallographic symmetry will be integrated soon

    if os.path.exists(os.path.join(current_directory, "temp")):
        shutil.rmtree(os.path.join(current_directory, "temp"))

    SystemUtility.open_connection(DicGridConn, DicParameters, cm)
    if hasattr(cm, "channel"):
        # COPY THE FULL LIBRARY and MTZ and HKL, IN THE REMOTE SERVER
        actualdi = cm.get_remote_pwd()
        print cm.change_remote_dir("..")
        try:
            new_model_directory = os.path.join(current_directory,
                                               os.path.basename(os.path.normpath(model_directory)) + "_" +
                                               DicParameters["nameExecution"])
            os.symlink(model_directory, new_model_directory)
            model_directory = new_model_directory
        except:
            exctype, value = sys.exc_info()[:2]
            # NOTE: If the link already exists, I still need to rename correctly the model_directory variable
            new_model_directory = os.path.join(current_directory,
                                               os.path.basename(os.path.normpath(model_directory)) + "_" +
                                               DicParameters["nameExecution"])
            model_directory = new_model_directory
            pass
        print cm.copy_directory(model_directory, model_directory)
        print cm.change_remote_dir(os.path.basename(os.path.normpath(model_directory)))
        cm.remote_library_path = cm.get_remote_pwd()
        print cm.copy_local_file(mtz, os.path.basename(mtz), send_now=True)
        cm.remote_mtz_path = os.path.join(cm.remote_library_path, os.path.basename(mtz))
        print cm.copy_local_file(hkl, os.path.basename(hkl), send_now=True)
        cm.remote_hkl_path = os.path.join(cm.remote_library_path, os.path.basename(hkl))
        print cm.copy_local_file(tncsfactors, os.path.basename(tncsfactors), send_now=True)
        cm.remote_tncs_path = os.path.join(cm.remote_library_path, os.path.basename(tncsfactors))
        print cm.copy_local_file(normfactors, os.path.basename(normfactors), send_now=True)
        cm.remote_norm_path = os.path.join(cm.remote_library_path, os.path.basename(normfactors))
        if os.path.exists(ent):
            print cm.copy_local_file(ent, os.path.basename(ent), send_now=True)
            cm.remote_ent_path = os.path.join(cm.remote_library_path, os.path.basename(ent))
        if os.path.exists(pdbcl):
            print cm.copy_local_file(pdbcl, os.path.basename(pdbcl), send_now=True)
            cm.remote_pdbcl_path = os.path.join(cm.remote_library_path, os.path.basename(pdbcl))

        if PERFORM_REFINEMENT_P1:
            print cm.copy_local_file(mtzP1, os.path.basename(mtzP1), send_now=True)
            cm.remote_mtzP1_path = os.path.join(cm.remote_library_path, os.path.basename(mtzP1))
        # print cm.change_remote_dir("..")
        print cm.change_remote_dir(actualdi)

    Config.remove_section("ARCIMBOLDO")
    Config.remove_section("ARCIMBOLDO-SHREDDER")

    allborf = cStringIO.StringIO()
    Config.write(allborf)
    allborf.flush()
    allborf.seek(0)
    allbor = allborf.read()
    allborf.close()

    # TODO: compute completeness and if below a threshold, warn or exit.
    # completeness = (4/3)*pi*2**3 * V /(2**d)3
    completeness = 100


    new_t = None

    # Hidden parameters and hard resolution limits handling
    skipResLimit = False
    try:
        skipResLimit = Config.getboolean("ARCIMBOLDO-BORGES", "SKIP_RES_LIMIT")
    except:
        pass
    if resolution > 2.5 and not skipResLimit and not coiled_coil:
        print colored("ATTENTION: Your resolution is lower than 2.5 A ARCIMBOLDO_BORGES will stop now.", 'red')
        sys.exit(0)
    elif resolution > 3.0 and not skipResLimit and coiled_coil:
        print colored("ATTENTION: Coiled coil protocol was active but your resolution is lower than 3.0 A "
                      "ARCIMBOLDO_BORGES will stop now.", 'red')
        sys.exit(0)

    try:
        stop_if_solved = Config.getboolean("ARCIMBOLDO-BORGES", "STOP_IF_SOLVED")
        if coiled_coil:
            stop_if_solved = False  # In coiled coil case we want to perform all cycles
        if stop_if_solved == False:
            filtClu = False
        SELSLIB2.STOP_IF_SOLVED = stop_if_solved
    except:
        pass

    print '\n Resolution is ',resolution
    print '\n Coiled coil is set to ',coiled_coil
    print '\n Stop if solved is set to ',stop_if_solved

    xml_out = os.path.join(current_directory, nameOutput + ".xml")
    xml_obj = ET.Element('borges-arcimboldo')
    ET.SubElement(xml_obj, 'data')
    ET.SubElement(xml_obj, 'configuration')
    ET.SubElement(xml_obj.find('configuration'), 'time_start').text = str(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    ET.SubElement(xml_obj.find('configuration'), 'bor_name').text = input_bor
    ET.SubElement(xml_obj.find('configuration'), 'bor_text').text = allbor
    # Remove from the html file the hidden parameters
    lines_bor = allbor.split('\n')
    allbor = ''
    for i in range(len(lines_bor)):
        if not lines_bor[i].startswith('skip_res_limit') or not lines_bor[i].startswith('stop_if_solved'):
            allbor = allbor + (lines_bor[i] + '\n')
    ET.SubElement(xml_obj.find('configuration'), 'bor_text').text = allbor
    ET.SubElement(xml_obj.find('configuration'), 'do_packing').text = str(USE_PACKING)
    ET.SubElement(xml_obj.find('configuration'), 'do_ref_p1').text = str(PERFORM_REFINEMENT_P1)
    if spaceGroup not in ["P1", "P 1"]:
        ET.SubElement(xml_obj.find('configuration'), 'do_traslation').text = str(True)
    else:
        ET.SubElement(xml_obj.find('configuration'), 'do_traslation').text = str(False)
    ET.SubElement(xml_obj.find('data'), 'completeness').text = str('%.2f' % completeness)
    ET.SubElement(xml_obj.find('data'), 'spacegroup').text = str(spaceGroup)
    ET.SubElement(xml_obj.find('data'), 'cell_dim')
    ET.SubElement(xml_obj.find('data/cell_dim'), 'A').text = str('%.2f' % float(cell_dim[0]))
    ET.SubElement(xml_obj.find('data/cell_dim'), 'B').text = str('%.2f' % float(cell_dim[1]))
    ET.SubElement(xml_obj.find('data/cell_dim'), 'C').text = str('%.2f' % float(cell_dim[2]))
    ET.SubElement(xml_obj.find('data/cell_dim'), 'alpha').text = str('%.2f' % float(cell_dim[3]))
    ET.SubElement(xml_obj.find('data/cell_dim'), 'beta').text = str('%.2f' % float(cell_dim[4]))
    ET.SubElement(xml_obj.find('data/cell_dim'), 'gamma').text = str('%.2f' % float(cell_dim[5]))
    ET.SubElement(xml_obj.find('data'), 'resolution').text = str('%.2f' % resolution)
    ET.SubElement(xml_obj.find('data'), 'unique_refl').text = str('%.2f' % unique_refl)
    ET.ElementTree(xml_obj).write(xml_out)

    arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)

    # Determine the number of processes and trials that will be performed according to hardware
    if force_core != None:
        sym.PROCESSES = force_core

    if distribute_computing == "multiprocessing":
        topscalc = sym.PROCESSES * 100
    else:
        topscalc = None

    if force_nsol != None:
        topscalc = force_nsol

    # new_t.start()

    if len(os.path.split(SELSLIB2.PATH_NEW_ARCIFIRE)[0]) == 0:
        p = subprocess.Popen(["which", SELSLIB2.PATH_NEW_ARCIFIRE], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        SELSLIB2.PATH_NEW_ARCIFIRE = out.strip()

    SIZE_LIB = 0

    for root, subFolders, files in os.walk(model_directory):
        for fileu in files:
            pdbf = os.path.join(root, fileu)
            if pdbf.endswith(".pdb"):
                SIZE_LIB += 1

    CLUSTSOL = 1000
    if distribute_computing in ["supercomputer"]:
        CLUSTSOL = len(SystemUtility.NODES)

    if SIZE_LIB <= CLUSTSOL or distribute_computing not in ["multiprocessing", "supercomputer"]:
        CLUSTSOL = SIZE_LIB

    if skip_mr: # NOTE CM: This option skips rotation and translation
        applyNameFilter = True
        path_rot = os.path.join(current_directory, "1_FRF_Library/")
        if not (os.path.exists(path_rot)):
            os.makedirs(path_rot)
        else:
            shutil.rmtree(path_rot)
            os.makedirs(path_rot)
        SELSLIB2.generateFakeMRSum(model_directory, "ROT", True, path_rot, "clustersNoRed")
        path_tran = os.path.join(current_directory, "./6_FTF_Library/")
        if not (os.path.exists(path_tran)):
            os.makedirs(path_tran)
        else:
            shutil.rmtree(path_tran)
            os.makedirs(path_tran)
        SELSLIB2.generateFakeMRSum(model_directory, "TRA", True, path_tran, "clustersNoRedPSol")

    SystemUtility.close_connection(DicGridConn,DicParameters,cm)


    #ELLG calculation

    outputDireELLG = os.path.join(current_directory, "ELLG_COMPUTATION")
    if not (os.path.exists(outputDireELLG)):
        os.makedirs(outputDireELLG)

    mrsumpath = os.path.join(current_directory, "ELLG_COMPUTATION/ellg_computation.sum")
    if not os.path.exists(mrsumpath):
        list_model_calculate_ellg = SELSLIB2.prepare_files_for_MR_ELLG_BORGES(outputDire=outputDireELLG + "/PREPARED_FILES", model_directory=model_directory)
        (nqueuetest, convNamestest) = SELSLIB2.startMR_ELLG(DicParameters=DicParameters, cm=cm, sym=sym,
                                                        nameJob="ELLG_COMPUTATION", list_solu_set=[],
                                                        list_models_calculate=list_model_calculate_ellg,
                                                        outputDire=outputDireELLG,
                                                        mtz=mtz, MW=MW, NC=NC, F=F, SIGF=SIGF,
                                                        Intensities=Intensities, Aniso=Aniso,
                                                        normfactors=normfactors, tncsfactors=tncsfactors,
                                                        spaceGroup=spaceGroup,
                                                        nice=nice, RMSD=last_rmsd, lowR=99,
                                                        highR=res_rot, ellg_target=ellg_target)

        dict_result_ellg = SELSLIB2.evaluateMR_ELLG(DicParameters, cm, DicGridConn, nameJob="ELLG_COMPUTATION",
                                                        outputDicr=outputDireELLG,
                                                        nqueue=nqueuetest, ensembles=convNamestest)
    else:
        dict_result_ellg = SELSLIB2.readMR_ELLGsum(mrsumpath)


    if not os.path.exists(os.path.join(current_directory, "1_FRF_Library/clustersNoRed.sum")):
        if not os.path.exists(os.path.join(current_directory, "1_FRF_Library/clustersNoRed_" + str(CLUSTSOL) + ".sum")):

            SystemUtility.open_connection(DicGridConn, DicParameters, cm)
            (nqueue, convNames) = SELSLIB2.startFRF(DicParameters=DicParameters, cm=cm, sym=sym,
                                                    nameJob="1_FRF_LIBRARY", dir_o_liFile=model_directory,
                                                    outputDire=os.path.join(current_directory, "./1_FRF_Library/"),
                                                    mtz=mtz, MW=MW, NC=NC, F=F, SIGF=SIGF, Intensities=Intensities,
                                                    Aniso=Aniso, normfactors=normfactors, tncsfactors=tncsfactors,
                                                    nice=nice, RMSD=RMSD, lowR=99, highR=res_rot, final_rot=peaks,
                                                    save_rot=peaks, frag_fixed=fixed_frags, spaceGroup=spaceGroup,
                                                    sampl=sampl_rot, fromN=0, toN=CLUSTSOL, VRMS=VRMS, BFAC=BFAC,
                                                    BULK_FSOL=BULK_FSOL, BULK_BSOL=BULK_BSOL,formfactors=formfactors)

            SystemUtility.endCheckQueue()
            CluAll, RotClu = SELSLIB2.evaluateFRF_clusterOnce(DicParameters=DicParameters, cm=cm, sym=sym,
                                                              DicGridConn=DicGridConn, RotClu=[],
                                                              nameJob="1_FRF_LIBRARY",
                                                              outputDicr=os.path.join(current_directory,
                                                                                      "./1_FRF_Library/"),
                                                              nqueue=nqueue, quate=quate, laue=laue, ncs=ncs,
                                                              spaceGroup=spaceGroup, ensembles=convNames,
                                                              clusteringAlg=clusteringAlg, excludeLLG=excludeLLG,
                                                              fixed_frags=fixed_frags, cell_dim=cell_dim,
                                                              thresholdCompare=thresholdCompare, evaLLONG=evaLLONG,
                                                              isArcimboldo=False, tops=topFRF, LIMIT_CLUSTER=None,
                                                              applyNameFilter=True, candelete=True, giveids=False,
                                                              merge=[],make_positive_llg=make_positive_llg)

            SELSLIB2.writeSumClusters(Clusters=CluAll, dirout=os.path.join(current_directory, "./1_FRF_Library/"),
                                      filename="clustersNoRed_" + str(CLUSTSOL), convNames=convNames)
        else:
            convNames, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters=DicParameters,
                                                                               sumPath=os.path.join(current_directory,
                                                                               "./1_FRF_Library/clustersNoRed_" + str(
                                                                                CLUSTSOL) + ".sum"),table="ROTSOL")

            nqueue = len(convNames.keys())

        if distribute_computing in ["multiprocessing", "supercomputer"]:
            Clu1 = copy.deepcopy(CluAll)
            merged_list = []
            unmerged_list = []
            for sizel in range(CLUSTSOL + 1, SIZE_LIB + 1, 100):
                if not os.path.exists(os.path.join(current_directory, "1_FRF_LIBRARY/" + str(sizel) + "/merged.sum")) or not os.path.exists(os.path.join(current_directory, "1_FRF_LIBRARY/" + str(sizel) + "/unmerged.sum")):
                    (nq, convN) = SELSLIB2.startFRF(DicParameters=DicParameters, cm=cm, sym=sym,
                                                    nameJob="1_FRF_LIBRARY_" + str(sizel), dir_o_liFile=model_directory,
                                                    outputDire=os.path.join(current_directory,
                                                                            "./1_FRF_Library/" + str(sizel) + "/"),
                                                    mtz=mtz, MW=MW, NC=NC, F=F, SIGF=SIGF, Intensities=Intensities,
                                                    Aniso=Aniso, normfactors=normfactors, tncsfactors=tncsfactors,
                                                    nice=nice, RMSD=RMSD, lowR=99, highR=res_rot, final_rot=peaks,
                                                    save_rot=peaks, frag_fixed=fixed_frags, spaceGroup=spaceGroup,
                                                    sampl=sampl_rot, fromN=sizel, toN=sizel + 100, VRMS=VRMS, BFAC=BFAC,
                                                    BULK_FSOL=BULK_FSOL, BULK_BSOL=BULK_BSOL,formfactors=formfactors)

                    merged_sum, unmerged_sum = SELSLIB2.evaluateFRF_MPR(DicParameters=DicParameters, GRID_TYPE=GRID_TYPE
                                                                        , QNAME=QNAME, FRACTION=FRACTION,
                                                                        PARTITION=PARTITION, cm=cm, sym=sym, nice=nice,
                                                                        DicGridConn=DicGridConn, RotClu=[],
                                                                        nameJob="1_FRF_LIBRARY" + str(sizel),
                                                                        outputDicr=os.path.join(current_directory,
                                                                                                "./1_FRF_Library/" +
                                                                                                str(sizel) + "/"),
                                                                        nqueue=nq, quate=quate, laue=laue,
                                                                        ncs=ncs, spaceGroup=spaceGroup, ensembles=convN,
                                                                        clusteringAlg=clusteringAlg,
                                                                        excludeLLG=excludeLLG, fixed_frags=fixed_frags,
                                                                        cell_dim=cell_dim,
                                                                        thresholdCompare=thresholdCompare,
                                                                        evaLLONG=evaLLONG,applyNameFilter=True,
                                                                        tops=topFRF, merge=Clu1,
                                                                        make_positive_llg=make_positive_llg)
                    SystemUtility.endCheckQueue(blocking=False)

                    merged_list.append(merged_sum)
                    unmerged_list.append(unmerged_sum)
                else:
                    merged_list.append(os.path.join(current_directory, "1_FRF_LIBRARY/" + str(sizel) + "/merged.sum"))
                    unmerged_list.append(
                        os.path.join(current_directory, "1_FRF_LIBRARY/" + str(sizel) + "/unmerged.sum"))

            SystemUtility.endCheckQueue()

            CluAll, convNames = SELSLIB2.fillClusters(DicParameters=DicParameters, CluAll=CluAll,
                                                      merged_list=merged_list, unmerged_list=unmerged_list,
                                                      convNames=convNames,quate=quate, laue=laue, ncs=ncs,
                                                      cell_dim=cell_dim, clusteringAlg=clusteringAlg,
                                                      threshold_alg=thresholdCompare)

        SELSLIB2.writeSumClusters(Clusters=CluAll, dirout=os.path.join(current_directory, "./1_FRF_Library/"),
                                  filename="clustersNoRed",convNames=convNames, RotClu=[], LIMIT_CLUSTER=None,
                                  saveMAP=False, euler_frac_zero=False)

        convNames, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters=DicParameters,
                                                                           sumPath=os.path.join(current_directory,
                                                                           "./1_FRF_Library/clustersNoRed.sum"),
                                                                           table="ROTSOL",LIMIT_CLUSTER=None,
                                                                           skip_reading_variables=False,
                                                                           give_fixed_frags=False, euler_to_zero=False)
    else:
        # SystemUtility.close_connection(DicGridConn,DicParameters,cm)
        convNames, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                           os.path.join(current_directory,
                                                                                        "./1_FRF_Library/clustersNoRed.sum"),
                                                                           "ROTSOL")

        nqueue = len(convNames.keys())

    # NOTE: START POSTMORTEM ANALYSIS OF THE ROTATIONS (TEMPORARY)
    if os.path.exists(pdbcl):
        pdbcl_directory = os.path.join(current_directory, "ensemble_clustering/")
        if not (os.path.exists(pdbcl_directory)):
            os.makedirs(pdbcl_directory)
        else:
            shutil.rmtree(pdbcl_directory)
            os.makedirs(pdbcl_directory)

        shutil.copyfile(pdbcl, os.path.join(pdbcl_directory, os.path.basename(pdbcl)))

        SystemUtility.open_connection(DicGridConn, DicParameters, cm)
        (nqueue, convNames) = SELSLIB2.startFRF(DicParameters=DicParameters, cm=cm, sym=sym, nameJob="ENT_FRF",
                                                dir_o_liFile=pdbcl_directory,
                                                outputDire=os.path.join(current_directory, "./ENT_FRF/"), mtz=mtz,
                                                MW=MW, NC=NC, F=F, SIGF=SIGF, Intensities=Intensities, Aniso=Aniso,
                                                normfactors=normfactors, tncsfactors=tncsfactors, nice=nice, RMSD=RMSD,
                                                lowR=99, highR=res_rot, final_rot=peaks, save_rot=peaks,
                                                frag_fixed=fixed_frags, spaceGroup=spaceGroup, sampl=sampl_rot,
                                                VRMS=VRMS, BFAC=BFAC, BULK_FSOL=BULK_FSOL, BULK_BSOL=BULK_BSOL,
                                                formfactors=formfactors)

        SystemUtility.endCheckQueue()
        CluAll, RotClu = SELSLIB2.evaluateFRF_clusterOnce(DicParameters, cm, sym, DicGridConn, [], "ENT_FRF",
                                                          os.path.join(current_directory, "./ENT_FRF/"), nqueue, quate,
                                                          laue, ncs, spaceGroup, convNames, clusteringAlg, excludeLLG,
                                                          fixed_frags, cell_dim, thresholdCompare, evaLLONG,
                                                          applyNameFilter=True, tops=topFRF,make_positive_llg=make_positive_llg)

        SELSLIB2.writeSumClusters(CluAll, os.path.join(current_directory, "./ENT_FRF/"), "clustersNoRed", convNames)
        allb = []
        for root, subFolders, files in os.walk(model_directory):
            for fileu in files:
                pdbf = os.path.join(root, fileu)
                if pdbf.endswith(".pdb"):
                    nu = int((fileu.split("_")[0])[4:])
                    allb.append(nu)
        fromV = min(allb)
        toV = max(allb)
        SELSLIB2.analyzeROTclusters(DicParameters, os.path.join(current_directory, "1_FRF_Library/clustersNoRed.sum"),
                                    os.path.join(current_directory, "ENT_FRF/clustersNoRed.sum"),
                                    os.path.join(current_directory, "./ENT_FRF/"), thresholdCompare, clusteringAlg,
                                    quate, laue, ncs, convNames, cell_dim, evaLLONG, fromV, toV)
    # TEMPORANEO#######################################################################
    # NOTE: END POSTMORTEM ANALYSIS OF THE ROTATIONS

    convNames, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters, os.path.join(current_directory, "./1_FRF_Library/clustersNoRed.sum"), "ROTSOL")

    # LIST OF CLUSTERS TO EVALUATE

    priorityClusters = SELSLIB2.writeOutputFile(lock=lock, DicParameters=DicParameters, ClusAll=CluAll,
                                                outputDir=current_directory, filename=nameOutput,
                                                mode="ARCIMBOLDO-BORGES", step="FRF", ensembles=convNames,
                                                frag_fixed=fixed_frags,filterClusters=filtClu,coiled_coil=coiled_coil)

    orderedClusters = priorityClusters

    SELSLIB2.writeOutputFile(lock=lock, DicParameters=DicParameters, ClusAll=CluAll, outputDir=current_directory,
                             filename=nameOutput, mode="ARCIMBOLDO-BORGES", step="FRF", ensembles=convNames,
                             frag_fixed=fixed_frags, coiled_coil=coiled_coil)

    arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)

    i = 0

    limitstoclu = Config.get(job_type, "clusters")  # all or list of clusters to evaluate

    saveRMSD = RMSD

    onerun = False
    if limitstoclu != None and limitstoclu not in ["", "all"]:
        n_clusters = None
        limitstoclu = limitstoclu.split(",")
        orderedClusters = []
        onerun = True
        for cru in limitstoclu:
            orderedClusters.append(int(cru))
            print(orderedClusters)

    if prioritize_phasers:
        onerun = False
    else:
        onerun = True
 
    for step_i in range(2):
        if step_i == 0 and onerun:
            continue

        if step_i == 1 and not onerun:
            listRotaClus = []
            completernp = "RBR"
            if RNP_GYRE:
                completernp = "GIMBLE"
            for spi in orderedClusters:
                # sumPath = os.path.join(current_directory, "./7.5_PACK_Library/"+str(spi)+"/clustersRed.sum")
                if os.path.exists(
                        os.path.join(current_directory, "./8_" + completernp + "/" + str(spi) + "/clustersNoRed.sum")):
                    sumPath = os.path.join(current_directory,
                                           "./8_" + completernp + "/" + str(spi) + "/clustersNoRed.sum")
                    Clu, dicname = SELSLIB2.readClustersFromSUM(sumPath)
                    if len(dicname.keys()) > 0:
                        listRotaClus.append(
                            (len(Clu[0]["heapSolutions"].asList()), Clu[0]["heapSolutions"].pop()[1]["llg"], spi))

            listRotaClus = sorted(listRotaClus, reverse=True)
            mean_all_llg = map(lambda x: x[1], listRotaClus)
            mean_all_llg = numpy.mean(numpy.array(mean_all_llg))
            sorting_llg = sorted(listRotaClus,key=operator.itemgetter(1),reverse=True)
            prioclusterexp = [ ele[2] for ele in sorting_llg]
            # for t in range(len(listRotaClus)):
            #     distpdb, llgclu, nclu = listRotaClus[t]
            #     prioclusterexp.append(nclu)
            orderedClusters = prioclusterexp

        for clusi in range(len(orderedClusters)):

            print("\n<====== ANALYZING CLUSTER {} ======>\n".format(clusi))
            RMSD = saveRMSD
            if n_clusters is not None and clusi > 0 and clusi >= n_clusters:
                break

            i = orderedClusters[clusi]
            topExp_run = 0
            if step_i == 0:
                topExp_run = None
            else:
                topExp_run = topExp

            fixed_frags = 1
            nfixfr = 1
            convNames, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                               os.path.join(current_directory,
                                                                               "./1_FRF_Library/clustersNoRed.sum"),
                                                                               "ROTSOL", LIMIT_CLUSTER=i)


            if ANOMALOUS:  # NS: Need to refilter what was filtered out before

                # NS: I need a dictionary to help me filter CluAll subsequently
                # I don't have this problem for Lite since the values in ConvName dics are directly ensembleXXblabla instead of a pdb name (because of the rename pdb option)
                convNamesAnom.update({ensname : os.path.basename(os.path.normpath(pdbname)) for ensname, pdbname in convNames.items()})

                if len(solutions_filtered_out.keys())==0 and os.path.exists(os.path.join(ANOMDIR,'filteredSol.json')):     #If the program has stopped, it can retrieve the filtered solutions from here
                    solutions_filtered_out=ANOMLIB.retrieveFilteredSol(os.path.join(ANOMDIR,'filteredSol.json'))
                    print("REMARK: retrieving filtered-out solution list (anomalous scoring) from %s"%os.path.join(ANOMDIR,'filteredSol.json'))
                    # for dic in CluAll:
                    #     for heap in list(dic['heapSolutions']):
                    #         print(heap)
                    #         print("\n\n")
                    # sys.exit(1)
                elif str(i) not in solutions_filtered_out.keys():
                    solutions_filtered_out[str(i)]={}    #New entry of filtered out solutions for cluster i


            threshPrevious = thresholdCompare

            cycle_ref = Config.getint(job_type, "number_cycles_model_refinement")
            if not PERFORM_REFINEMENT_P1 and not USE_RGR and not USE_NMA_P1:             # NS: seems to be the case in Borges, so the floowing will be skipped
                cycle_ref = 1
            else:
                cycle_ref += 1

            for q in range(cycle_ref):

                if q > 0:  # Any of the cycles that is not the first
                    RMSD -= rmsd_decrease  # Decrease the rmsd to use by the amount set
                    rmsd_step = rmsd_decrease
                    tid = 1  # Only one top
                    appl_tid = True  # Filter solutions by name

                    if not USE_RGR:
                        if not os.path.exists(os.path.join(current_directory, "./4_FRF_LIBRARY/" + str(i) + "/" + str(q) + "/clustersNoRed.sum")):
                            SystemUtility.open_connection(DicGridConn, DicParameters, cm)
                            (nqueue, convNames) = SELSLIB2.startFRF(DicParameters=DicParameters, cm=cm, sym=sym,
                                                                    nameJob="4_FRF_LIBRARY_" + str(i) + "_" + str(q),
                                                                    dir_o_liFile=CluAll,
                                                                    outputDire=os.path.join(current_directory,
                                                                                            "./4_FRF_LIBRARY/" + str(
                                                                                                i) + "/" + str(q)),
                                                                    mtz=mtz, MW=MW, NC=NC, F=F, SIGF=SIGF,
                                                                    Intensities=Intensities, Aniso=Aniso,
                                                                    normfactors=normfactors, tncsfactors=tncsfactors,
                                                                    nice=nice, RMSD=RMSD, lowR=99, highR=res_rot,
                                                                    final_rot=peaks, save_rot=peaks,
                                                                    frag_fixed=fixed_frags, spaceGroup=spaceGroup,
                                                                    tops=topscalc, sampl=sampl_rot, LIMIT_CLUSTER=i,
                                                                    VRMS=VRMS, BFAC=BFAC, BULK_FSOL=BULK_FSOL,
                                                                    BULK_BSOL=BULK_BSOL,formfactors=formfactors)
                            SystemUtility.endCheckQueue()

                            CluAll, RotClu = SELSLIB2.evaluateFRF_clusterOnce(DicParameters, cm, sym, DicGridConn, [],
                                                                              "4_FRF_LIBRARY_" + str(i) + "_" + str(q),
                                                                              os.path.join(current_directory,
                                                                                           "./4_FRF_LIBRARY/" + str(
                                                                                               i) + "/" + str(q) + "/"),
                                                                              nqueue, quate, laue, ncs, spaceGroup,
                                                                              convNames, clusteringAlg, excludeLLG,
                                                                              fixed_frags, cell_dim, thresholdCompare,
                                                                              evaLLONG, LIMIT_CLUSTER=i, tops=tid,
                                                                              applyNameFilter=appl_tid,make_positive_llg=make_positive_llg)
                            SELSLIB2.writeSumClusters(CluAll, os.path.join(current_directory,
                                                                           "./4_FRF_LIBRARY/" + str(i) + "/" + str(
                                                                               q) + "/"), "clustersRed", convNames,
                                                      LIMIT_CLUSTER=i)
                            convNames, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                               os.path.join(
                                                                                                   current_directory,
                                                                                                   "./4_FRF_LIBRARY/" + str(
                                                                                                       i) + "/" + str(
                                                                                                       q) + "/clustersRed.sum"),
                                                                                               "ROTSOL",
                                                                                               LIMIT_CLUSTER=i)
                            CluAll = SELSLIB2.filterAndCountClusters(CluAll, convNames, "llg", quate, laue, ncs,
                                                                     cell_dim, clusteringAlg, thresholdCompare,
                                                                     unify=True)
                            SELSLIB2.writeSumClusters(CluAll, os.path.join(current_directory,
                                                                           "./4_FRF_LIBRARY/" + str(i) + "/" + str(
                                                                               q) + "/"), "clustersNoRed", convNames,
                                                      LIMIT_CLUSTER=i)
                        else:
                            convNames, CluAll, RotClu, enc = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                              os.path.join(
                                                                                                  current_directory,
                                                                                                  "./4_FRF_LIBRARY/" + str(
                                                                                                      i) + "/" + str(
                                                                                                      q) + "/clustersNoRed.sum"),
                                                                                              "ROTSOL", LIMIT_CLUSTER=i)
                    else:  # Then we skip the 4_FRF, we want to use the previous gyred results
                        # (DicParameters,sumPath,table,LIMIT_CLUSTER=None,skip_reading_variables=False,give_fixed_frags=False)
                        convNames, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters=DicParameters,
                                                                                           sumPath=os.path.join(
                                                                                               current_directory,
                                                                                               "./3_RGR/" + str(
                                                                                                   i) + "/" + str(
                                                                                                   q - 1) + "/clustersNoRed.sum"),
                                                                                           table="ROTSOL",
                                                                                           LIMIT_CLUSTER=i,euler_to_zero=True)
                else: #Then we are at the first cycle
                    print 'SHERLOCK we are at the first gyre cycle'
                    rmsd_step = 0


                if q == cycle_ref - 1:  # We added one to cycle_ref, so this one we don't need to do it
                    if USE_RGR:
                        RMSD += rmsd_decrease
                    break

                if PERFORM_REFINEMENT_P1:
                    if not USE_NMA_P1:
                        if not os.path.exists(os.path.join(current_directory,
                                                           "./3_RBR_P1_BRF/" + str(i) + "/" + str(q) + "/models.sum")):
                            SystemUtility.open_connection(DicGridConn, DicParameters, cm)

                            nq, conv2 = SELSLIB2.startRBRP1(DicParameters, cm, sym,
                                                            "3_RBR_P1_BRF_" + str(i) + "_" + str(q), CluAll, convNames,
                                                            os.path.join(current_directory,
                                                                         "./3_RBR_P1_BRF/" + str(i) + "/" + str(
                                                                             q) + "/"), mtzP1, MW, NCp1, Fp1, SIGFp1,
                                                            Intensities, Aniso, nice, RMSD, 99, 1.0, 1, spaceGroup,
                                                            tops=topscalc, sampl=-1, LIMIT_CLUSTER=i, VRMS=VRMS,
                                                            BFAC=BFAC, BULK_FSOL=BULK_FSOL, BULK_BSOL=BULK_BSOL,
                                                            RNP_GYRE=RNP_GYRE, formfactors=formfactors)

                            SystemUtility.endCheckQueue()
                            CluAll, convNames = SELSLIB2.evaluateRefP1(DicParameters, cm, sym, DicGridConn,
                                                                       "3_RBR_P1_BRF_" + str(i) + "_" + str(q),
                                                                       os.path.join(current_directory,
                                                                                    "./3_RBR_P1_BRF/" + str(
                                                                                        i) + "/" + str(q) + "/"), True,
                                                                       quate, conv2, convNames, LIMIT_CLUSTER=i)
                        else:
                            asd, convie = SELSLIB2.readRefFromSUM(os.path.join(current_directory,
                                                                               "./3_RBR_P1_BRF/" + str(i) + "/" + str(
                                                                                   q) + "/models.sum"))
                            nuovoCon = {}
                            for key in convNames.keys():
                                if os.path.basename(convNames[key]) in convie:
                                    nuovoCon[key] = convie[os.path.basename(convNames[key])]
                            convNames = nuovoCon
                            convie = None
                        CluAll = os.path.join(current_directory, "./3_RBR_P1_BRF/" + str(i) + "/" + str(q) + "/")
                    else:
                        if not os.path.exists(
                                os.path.join(current_directory, "./3_NMA_P1/" + str(i) + "/" + str(q) + "/")):
                            SystemUtility.open_connection(DicGridConn, DicParameters, cm)
                            nqueue15, convNames = SELSLIB2.startNMAFromClusters(DicParameters=DicParameters, cm=cm,
                                                                                sym=sym, ClusAll=CluAll,
                                                                                ensembles=convNames,
                                                                                nameJob="3_NMA_P1_" + str(
                                                                                    i) + "_" + str(q),
                                                                                outputDire=os.path.join(
                                                                                    current_directory,
                                                                                    "./3_NMA_P1/" + str(i) + "/" + str(
                                                                                        q) + "/"), mtz=mtz, MW=MW,
                                                                                NC=NC, F=F, SIGF=SIGF,
                                                                                Intensities=Intensities, Aniso=Aniso,
                                                                                normfactors=normfactor,
                                                                                tncsfactors=tncsfactors, nice=nice,
                                                                                RMSD=RMSD, lowR=99, highR=res_clu,
                                                                                final_rot=peaks, save_rot=peaks,
                                                                                frag_fixed=fixed_frags,
                                                                                spaceGroup=spaceGroup, tops=topscalc,
                                                                                sampl=res_sampl, VRMS=VRMS, BFAC=BFAC,
                                                                                BULK_FSOL=BULK_FSOL,
                                                                                BULK_BSOL=BULK_BSOL,
                                                                                formfactors=formfactors)

                            SystemUtility.endCheckQueue()
                            SELSLIB2.evaluateNMA(DicParameters, cm, sym, DicGridConn,
                                                 "3_NMA_P1_" + str(i) + "_" + str(q), os.path.join(current_directory,
                                                                                                   "./3_NMA_P1/" + str(
                                                                                                       i) + "/" + str(
                                                                                                       q) + "/"), i,
                                                 nqueue15, convNames)
                        if not os.path.exists(
                                os.path.join(current_directory, "./3_EXP_P1/" + str(i) + "/" + str(q) + "/solCC.sum")):
                            SystemUtility.open_connection(DicGridConn, DicParameters, cm)

                            (nqueue14, convNames_4) = SELSLIB2.startExpansion(cm=cm, sym=sym, nameJob="3_EXP_P1" + str(i) + "_" + str(q),
                                                                              outputDire=os.path.join(current_directory,"./3_EXP_P1/" + str(i) + "/" + str(q) + "/"),
                                                                              hkl=hkl, ent=ent, nice=nice, cell_dim=cell_dim, spaceGroup=spaceGroup,
                                                                              shlxLine=shlxLinea0, dirBase="./3_NMA_P1/" + str(i) + "/" + str(q) + "/", fragAnom=fragAnom,**startExpAnomDic)

                            SystemUtility.endCheckQueue()
                            if ANOMALOUS:
                                try:
                                    shutil.rmtree(os.path.join(ANOMDIR, "EVALUATION"))
                                except:
                                    pass

                                #Get the llg and zscore for all solutions:
                                convNamesAnom.update(ConvNames)
                                llgdic= ANOMLIB.llgdic(convNamesAnom, CluAll)

                                CC_Val3, eliminatedSol = SELSLIB2.evaluateExp_CC(DicParameters, cm, sym, DicGridConn,
                                                                  "3_EXP_P1" + str(i) + "_" + str(q),
                                                                  os.path.join(current_directory,
                                                                               "./3_EXP/" + str(i) + "/" + str(q) + "/"),
                                                                  nqueue14, convNames_4, savePHS=savePHS,
                                                                  archivingAsBigFile=archivingAsBigFile,
                                                                  phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim, anomDic=startExpAnomDic, pattersonPeaks=pattersonPeaks, isBORGES=True, llgdic=llgdic)
                                # Filter out the eliminated solutions from the heap list
                                if "3_EXP_P1" not in solutions_filtered_out[str(i)] or os.path.exists(os.path.join(ANOMDIR,'filteredSol.json')):
                                    solutions_filtered_out[str(i)]["3_EXP_P1"] = []

                                solutions_filtered_out[str(i)]["3_EXP_P1"] +=  eliminatedSol                                    
                                if len(solutions_filtered_out[str(i)]["3_EXP_P1"])>0:
                                    ANOMLIB.saveFilteredSol(os.path.join(ANOMDIR,'filteredSol.json'),solutions_filtered_out)
                            else:
                                CC_Val3 = SELSLIB2.evaluateExp_CC(DicParameters, cm, sym, DicGridConn,
                                                                  "3_EXP_P1" + str(i) + "_" + str(q),
                                                                  os.path.join(current_directory,
                                                                               "./3_EXP/" + str(i) + "/" + str(q) + "/"),
                                                                  nqueue14, convNames_4, savePHS=savePHS,
                                                                  archivingAsBigFile=archivingAsBigFile,
                                                                  phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim)                                
                            # SystemUtility.close_connection(DicGridConn,DicParameters,cm)
                        else:
                            CC_Val3, con4 = SELSLIB2.readCCValFromSUM(
                                os.path.join(current_directory, "./3_EXP_P1/" + str(i) + "/" + str(q) + "/solCC.sum"))
                        # TODO: Continue... We should do something with CC_Val3 like take the top for each pdb and put it in the convNames
                        CluAll = os.path.join(current_directory, "./3_EXP_P1/" + str(i) + "/" + str(q) + "/")
                elif USE_RGR:
                    if not os.path.exists(os.path.join(current_directory,"./3_RGR/"+str(i)+"/"+str(q)+"/models.sum")):
                        if q > 0:
                            convNames,CluAll,RotClu,encn = SELSLIB2.readClustersFromSUMToDB(DicParameters=DicParameters, sumPath=os.path.join(current_directory,"./3_RGR/"+str(i)+"/"+str(q-1)+"/clustersNoRed.sum"),table="ROTSOL",LIMIT_CLUSTER=i,euler_to_zero=True)
                        else:
                            convNames,CluAll,RotClu,encn = SELSLIB2.readClustersFromSUMToDB(DicParameters, os.path.join(current_directory,"./1_FRF_Library/clustersNoRed.sum"),"ROTSOL",LIMIT_CLUSTER=i)

                        if isShredder and dictio_shred_annotation!={}:
                            ndir = 0
                            count_models = 0
                            path_models_original=os.path.split(convNames[convNames.keys()[0]])[0]
                            list_models = [os.path.join(path_models_original,index) for index in os.listdir(path_models_original)]
                            models_last_directory = len(list_models) % SELSLIB2.NUMBER_OF_FILES_PER_DIRECTORY
                            if models_last_directory!=0:
                                number_directories = (len(list_models) / SELSLIB2.NUMBER_OF_FILES_PER_DIRECTORY) + 1
                            else:
                                number_directories = (len(list_models) / SELSLIB2.NUMBER_OF_FILES_PER_DIRECTORY)
                            for n in range(ndir,number_directories):
                                if n==number_directories-1 and models_last_directory!=0:  # last group, not 1000 files
                                    sub_list_models = list_models[count_models:count_models+models_last_directory]
                                    count_models = count_models + models_last_directory
                                else:
                                    sub_list_models = list_models[count_models:count_models+1000]
                                    count_models = count_models + 1000
                                new_path_models = os.path.join(current_directory, '2_GROUPING/' + str(i) + "/" + str(q)
                                                               +  "/" + str(n) + "/")
                                try:
                                    os.makedirs(new_path_models)
                                except:
                                    shutil.rmtree(new_path_models)
                                    os.makedirs(new_path_models)
                                if q == 0:
                                    print 'Using the first group of annotation levels on ',new_path_models
                                    Bioinformatics3.modify_chains_according_to_shredder_annotation(pdb=sub_list_models,
                                                                                  dictio_annotation=dictio_shred_annotation,
                                                                                  annotation_level='first_ref_cycle_group',
                                                                                  output_path=new_path_models)
                                    for key in convNames.keys():
                                        if convNames[key] not in sub_list_models:
                                            continue
                                        original_path = convNames[key]
                                        convNames[key] = os.path.join(new_path_models, os.path.basename(original_path))
                                elif q==1:
                                    print 'Using the second group of annotation levels on ',new_path_models
                                    Bioinformatics3.modify_chains_according_to_shredder_annotation(pdb=sub_list_models,
                                                                                  dictio_annotation=dictio_shred_annotation,
                                                                                  annotation_level='second_ref_cycle_group',
                                                                                  output_path=new_path_models)
                                    for key in convNames.keys():
                                        if convNames[key] not in sub_list_models:
                                            continue
                                        original_path=convNames[key]
                                        convNames[key]=os.path.join(new_path_models,os.path.basename(original_path))
                                elif q==2:
                                    print 'Using the third group of annotation levels on ', new_path_models
                                    Bioinformatics3.modify_chains_according_to_shredder_annotation(pdb=sub_list_models,
                                                                                  dictio_annotation=dictio_shred_annotation,
                                                                                  annotation_level='third_ref_cycle_group',
                                                                                  output_path=new_path_models)
                                    for key in convNames.keys():
                                        if convNames[key] not in sub_list_models:
                                            continue
                                        original_path=convNames[key]
                                        convNames[key]=os.path.join(new_path_models,os.path.basename(original_path))

                        SystemUtility.open_connection(DicGridConn,DicParameters,cm)

                        print 'SHERLOCK RMSD before gyre is ',RMSD
                        print 'SHERLOCK rmsd_decrease before gyre',rmsd_decrease
                        print 'SHERLOCK rmsd_step before gyre',rmsd_step
                        nq,convNames = SELSLIB2.startRGR(DicParameters=DicParameters,cm=cm,sym=sym,
                                                         nameJob="3_RGR_"+str(i)+"_"+str(q),ClusAll=CluAll,
                                                         ensembles=convNames,
                                                         outputDire=os.path.join(current_directory,"./3_RGR/"+str(i)+
                                                                                 "/"+str(q)+"/"),mtz=mtz,MW=MW,NC=NC,
                                                         F=F,SIGF=SIGF,Intensities=Intensities,Aniso=Aniso,
                                                         normfactors=normfactors,tncsfactors=tncsfactors,nice=nice,
                                                         RMSD=RMSD,lowR=99,highR=res_gyre,frag_fixed=1,
                                                         spaceGroup=spaceGroup,save_rot=peaks,tops=topscalc,
                                                         sampl=RGR_SAMPL,USE_TNCS=USE_TNCS,LIMIT_CLUSTER=i,isOMIT=False,
                                                         VRMS=VRMS_GYRE, BFAC=BFAC, BULK_FSOL=BULK_FSOL,
                                                         BULK_BSOL=BULK_BSOL, sigr=sigr, sigt=sigt,
                                                         preserveChains=preserveChains,formfactors=formfactors)
                        SystemUtility.endCheckQueue()
                        convNames, CluAll = SELSLIB2.evaluateRGR(DicParameters=DicParameters, cm=cm, sym=sym,
                                                                 DicGridConn=DicGridConn,
                                                                 nameJob="3_RGR_" + str(i) + "_" + str(q),
                                                                 outputDicr=os.path.join(current_directory,
                                                                                         "./3_RGR/" + str(
                                                                                             i) + "/" + str(q) + "/"),
                                                                 maintainOrigCoord=False, cell_dim=cell_dim, quate=quate,
                                                                 convNames=convNames, models_directory=model_directory,
                                                                 ensembles=convNames, LIMIT_CLUSTER=i, isOMIT=False,
                                                                 ent=ent)

                        if USE_RGR == 2 and q == cycle_ref - 2:  # SELECT Both gyre and no gyre for FTF
                            convNames_1FRF, CluAll_1FRF, RotClu_1FRF, encn_1FRF = SELSLIB2.readClustersFromSUMToDB(
                                DicParameters, os.path.join(current_directory, "./1_FRF_Library/clustersNoRed.sum"),
                                "ROTSOL", LIMIT_CLUSTER=i)

                            SELSLIB2.getTheTOPNOfEachCluster(DicParameters=DicParameters, frag_fixed=fixed_frags,
                                                             dirout=os.path.join(current_directory,
                                                                                 "./3_RGR/" + str(i) + "/" + str(
                                                                                     q) + "/"), mode="matrix",
                                                             quate=quate, ClusAll=CluAll_1FRF, convNames=convNames_1FRF,
                                                             ntop=None, writePDB=True, performTranslation=True,
                                                             elongatingModel=None, createSimmetry=False,
                                                             cell_dim=cell_dim, laue=laue, ncs=ncs, modeTra="frac",
                                                             LIMIT_CLUSTER=i, renameWithConvNames=True,
                                                             sufixSolPos=False, appendToName="nogyre")

                            convNames_1FRF, CluAll_1FRF, RotClu_1FRF, encn_1FRF = SELSLIB2.readClustersFromSUMToDB(
                                DicParameters, os.path.join(current_directory, "./1_FRF_Library/clustersNoRed.sum"),
                                "ROTSOL", LIMIT_CLUSTER=i)

                            for key in convNames_1FRF.keys():
                                nuovoc = os.path.basename(convNames_1FRF[key])
                                nuovoc = nuovoc.split("_")[0] + "nogyre_" + nuovoc.split("_")[1] + "_" + \
                                         nuovoc.split("_")[2]
                                nuovoc = os.path.join(
                                    os.path.join(current_directory, "./3_RGR/" + str(i) + "/" + str(q) + "/"), nuovoc)
                                convNames[key + "nogyre"] = nuovoc

                            CluAll = SELSLIB2.mergeRotClusterObjects(CluAll_1FRF, CluAll, suffix="nogyre",reset_euler="both")


                        SELSLIB2.writeSumClusters(CluAll, os.path.join(current_directory,
                                                                       "./3_RGR/" + str(i) + "/" + str(q) + "/"),
                                                  "clustersNoRed", convNames, LIMIT_CLUSTER=i)
                    else:
                        # returns list asd, with one dictionary per solution containing FOMs, and a convNames (convie)
                        asd, convie = SELSLIB2.readRefFromSUM(
                            os.path.join(current_directory, "./3_RGR/" + str(i) + "/" + str(q) + "/models.sum"))
                        nuovoCon = {}
                        for key in convNames.keys():
                            if os.path.basename(convNames[key]) in convie:
                                nuovoCon[key] = convie[os.path.basename(convNames[key])]
                        convNames = nuovoCon
                        convie = None
                    CluAll = os.path.join(current_directory, "./3_RGR/" + str(i) + "/" + str(q) + "/")
                    # print "After cycle gyre...."
                    # for key in convNames.keys():
                    #    print key,convNames[key]

            SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput, "ARCIMBOLDO-BORGES",
                                     "TABLE", convNames, fixed_frags, LIMIT_CLUSTER=i,coiled_coil=coiled_coil)
            arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)

            thresholdCompare = threshPrevious

            print 'SHERLOCK this is the part of the code just before all the translation steps'
            print 'SHERLOCK From these step on, we do not want to change anymore the rmsd of the fragments before running phaser'
            rmsd_step=0
            print 'SHERLOCK RMSD  ', RMSD
            print 'SHERLOCK rmsd_step  ', rmsd_step

            if spaceGroup not in ["P1", "P 1"] or USE_TNCS:
                if not os.path.exists(
                        os.path.join(current_directory, "./6_FTF_Library/" + str(i) + "/clustersNoRedPSol.sum")):
                    SystemUtility.open_connection(DicGridConn, DicParameters, cm)

                    print 'SHERLOCK RMSD before startFTF ', RMSD
                    print 'SHERLOCK rmsd_step before startFTF ', rmsd_step
                    nqueue6 = SELSLIB2.startFTF(DicParameters=DicParameters, cm=cm, sym=sym,
                                                nameJob="6_FTF_Library_" + str(i), ClusAll=CluAll, ensembles=convNames,
                                                outputDire=os.path.join(current_directory,
                                                                        "./6_FTF_Library/" + str(i) + "/"), mtz=mtz,
                                                MW=MW, NC=NC, F=F, SIGF=SIGF, Intensities=Intensities, Aniso=Aniso,
                                                normfactors=normfactors, tncsfactors=tncsfactors, nice=nice, RMSD=RMSD,
                                                lowR=99, highR=res_tran, final_tra=peaks, save_tra=peaks,
                                                frag_fixed=fixed_frags, spaceGroup=spaceGroup, cutoff_pack=CLASHES,
                                                sampl=sampl_tran, USE_TNCS=USE_TNCS, LIMIT_CLUSTER=i, tops=topscalc,
                                                VRMS=VRMS, BFAC=BFAC, BULK_FSOL=BULK_FSOL, BULK_BSOL=BULK_BSOL,
                                                PACK_TRA=PACK_TRA,formfactors=formfactors)

                    SystemUtility.endCheckQueue()
                    CluAll, convNames, nfixfr = SELSLIB2.evaluateFTF(DicParameters, cm, sym, DicGridConn,
                                                                     "6_FTF_Library_" + str(i),
                                                                     os.path.join(current_directory,
                                                                     "./6_FTF_Library/" + str(i) + "/"),
                                                                     nqueue6, convNames, excludeZscore, fixed_frags,
                                                                     quate, "TRA", laue, ncs, clusteringAlg, cell_dim,
                                                                     thresholdCompare, evaLLONG, LIMIT_CLUSTER=i,
                                                                     applyNameFilter=applyNameFilter, tops=topFTF,
                                                                     giveids=not applyNameFilter,
                                                                     make_positive_llg=make_positive_llg)

                    if nfixfr == None or nfixfr <= 0:
                        nfixfr = 1

                    SELSLIB2.writeSumClusters(CluAll,
                                              os.path.join(current_directory, "./6_FTF_Library/" + str(i) + "/"),
                                              "clustersRed", convNames, LIMIT_CLUSTER=i)
                    convNames, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                       os.path.join(current_directory,
                                                                                                    "./6_FTF_Library/" + str(
                                                                                                        i) + "/clustersRed.sum"),
                                                                                       "ROTSOL", LIMIT_CLUSTER=i)

                    if applyNameFilter:
                        CluAll = SELSLIB2.filterAndCountClusters(CluAll, convNames, "zscore", quate, laue, ncs,
                                                                 cell_dim, clusteringAlg, thresholdCompare, unify=True)
                        SELSLIB2.writeSumClusters(CluAll,
                                                  os.path.join(current_directory, "./6_FTF_Library/" + str(i) + "/"),
                                                  "clustersNoRed", convNames, LIMIT_CLUSTER=i)

                    SELSLIB2.writeSumClusters(CluAll,
                                              os.path.join(current_directory, "./6_FTF_Library/" + str(i) + "/"),
                                              "clustersNoRedPSol", convNames, LIMIT_CLUSTER=i)
                    convNames, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                       os.path.join(current_directory,
                                                                                                    "./6_FTF_Library/" + str(
                                                                                                        i) + "/clustersNoRedPSol.sum"),
                                                                                       "ROTSOL", LIMIT_CLUSTER=i)
                else:
                    convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                               os.path.join(
                                                                                                   current_directory,
                                                                                                   "./6_FTF_Library/" + str(
                                                                                                       i) + "/clustersNoRedPSol.sum"),
                                                                                               "ROTSOL",
                                                                                               LIMIT_CLUSTER=i,
                                                                                               give_fixed_frags=True)

                SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput,
                                         "ARCIMBOLDO-BORGES", "FTF", convNames, fixed_frags, LIMIT_CLUSTER=i,coiled_coil=coiled_coil)
                arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)
            else:
                SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput,
                                         "ARCIMBOLDO-BORGES", "FTF", convNames, fixed_frags, makeEmpty=True,
                                         LIMIT_CLUSTER=i,coiled_coil=coiled_coil)
                arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)

                USE_PACKING = True
                USE_TRANSLA = False

            if USE_PACKING:
                if not os.path.exists(
                        os.path.join(current_directory, "./7.5_PACK_Library/" + str(i) + "/clustersRed.sum")):
                    SystemUtility.open_connection(DicGridConn, DicParameters, cm)
                    nqueue8 = SELSLIB2.startPACK(DicParameters=DicParameters, cm=cm, sym=sym,
                                                 nameJob="7.5_PACK_Library_" + str(i), ClusAll=CluAll,
                                                 ensembles=convNames, outputDire=os.path.join(current_directory,
                                                                                              "./7.5_PACK_Library/" + str(
                                                                                                  i) + "/"), mtz=mtz,
                                                 MW=MW, NC=NC, F=F, SIGF=SIGF, Intensities=Intensities, Aniso=Aniso,
                                                 normfactors=normfactors, tncsfactors=tncsfactors, nice=nice, RMSD=RMSD,
                                                 lowR=99, highR=1.0, cutoff=CLASHES, formfactors=formfactors,
                                                 spaceGroup=spaceGroup, frag_fixed=nfixfr,
                                                 tops=topPACK, LIMIT_CLUSTER=i, VRMS=VRMS, BFAC=BFAC)

                    SystemUtility.endCheckQueue()
                    CluAll, convNames, nfixfr = SELSLIB2.evaluateFTF(DicParameters, cm, sym, DicGridConn,
                                                                     "7.5_PACK_Library_" + str(i),
                                                                     os.path.join(current_directory,
                                                                                  "./7.5_PACK_Library/" + str(i) + "/"),
                                                                     nqueue8, convNames, -10, nfixfr, quate, "PACK",
                                                                     laue, ncs, clusteringAlg, cell_dim,
                                                                     thresholdCompare, evaLLONG, LIMIT_CLUSTER=i,
                                                                     tops=topPACK,make_positive_llg=make_positive_llg)

                    SELSLIB2.writeSumClusters(CluAll,
                                              os.path.join(current_directory, "./7.5_PACK_Library/" + str(i) + "/"),
                                              "clustersRed", convNames, LIMIT_CLUSTER=i)
                    convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                               os.path.join(
                                                                                                   current_directory,
                                                                                                   "./7.5_PACK_Library/" + str(
                                                                                                       i) + "/clustersRed.sum"),
                                                                                               "ROTSOL",
                                                                                               LIMIT_CLUSTER=i,
                                                                                               give_fixed_frags=True)

                    all_empty = True
                    for clu in CluAll:
                        if len(clu["heapSolutions"].asList()) > 0:
                            all_empty = False
                            break

                    if all_empty:
                        print "Packing has excluded everything...EXIT"
                        # TODO: Close the output row, to do so write <td></td> for the remaning columns and </tr>
                        continue
                else:
                    convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                               os.path.join(
                                                                                                   current_directory,
                                                                                                   "./7.5_PACK_Library/" + str(
                                                                                                       i) + "/clustersRed.sum"),
                                                                                               "ROTSOL",
                                                                                               LIMIT_CLUSTER=i,
                                                                                               give_fixed_frags=True)
                    if len(convNames.keys()) == 0:
                        print "Packing has excluded everything...EXIT"
                        # TODO: Close the output row, to do so write <td></td> for the remaning columns and </tr>
                        continue

                SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput,
                                         "ARCIMBOLDO-BORGES", "PACK", convNames, fixed_frags, LIMIT_CLUSTER=i,coiled_coil=coiled_coil)
                arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)
                sumPACK = os.path.join(current_directory, "./7.5_PACK_Library/" + str(i) + "/clustersRed.sum")
            else:
                SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput,
                                         "ARCIMBOLDO-BORGES", "PACK", convNames, fixed_frags, makeEmpty=True,
                                         LIMIT_CLUSTER=i,coiled_coil=coiled_coil)
                arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)
                sumPACK = os.path.join(current_directory, "./6_FTF_Library/" + str(i) + "/clustersNoRedPSol.sum")


            # NOTE: This is a new feature, developed by Claudia, needs to be carefully tested
            if swap_model_after_translation!=None:
                print '\n\n ******** This is the moment in which we are going to swap the models *********'
                # convNames, CluAll, RotClu, encn, nfixfr
                # Now I need to superimpose the swap_model_after_translation to all solutions that survived the packing
                # Just in case, I am going to write a new folder for the superposed models
                if not os.path.exists(os.path.join(current_directory, "./7_SWAP/" + str(i) + "/")):
                    #os.makedirs(os.path.join(current_directory, "./7_SWAP/" + str(i) + "/"))
                   
                    saveCluAll=copy.deepcopy(CluAll)
 
                    SELSLIB2.getTheTOPNOfEachCluster(DicParameters=DicParameters, frag_fixed=fixed_frags,
                                                 dirout=os.path.join(current_directory, "./7_SWAP/" + str(i) + "/"),
                                                 mode="matrix", quate=quate, ClusAll=CluAll, convNames=convNames,
                                                 ntop=None, writePDB=True, performTranslation=True,
                                                 elongatingModel=None, createSimmetry=False, cell_dim=cell_dim,
                                                 laue=laue, ncs=ncs, modeTra="frac", LIMIT_CLUSTER=i,
                                                 renameWithConvNames=True, sufixSolPos=not applyNameFilter) 

                    #print 'swap_model_after_translation is',swap_model_after_translation
                    
 
                    path_swap_folder=os.path.join(current_directory, "./7_SWAP/" + str(i) + "/")
                    list_path_models_to_swap=[ os.path.join(path_swap_folder,ele) for ele in os.listdir(path_swap_folder) ]
                    #print "list_path_models_to_swap",list_path_models_to_swap
                    list_swapped_models=[]
 
                    # reference pdb
                    #parser = PDBParser()
                    strutemp = Bioinformatics.getStructure('toswap', swap_model_after_translation)
                    new_list_atoms = Selection.unfold_entities(strutemp, 'A')
                    new_list_atoms=sorted(new_list_atoms,key=lambda x:x.get_parent().get_full_id()[3][1:])
                    PDBTEMP = Bioinformatics.getPDBFromListOfAtom(new_list_atoms)[0]
                    #file_a=open('toswap.pdb','w')
                    #file_a.write(PDBTEMP)
                    #file_a.close()
                    #print 'check reference.pdb !!!'
                    #sys.exit(0)
                    for file_to_swap in list_path_models_to_swap:
                        print '\n\nProcessing',file_to_swap
                        struswap = Bioinformatics.getStructure('swapswap', file_to_swap)
                        old_list_atoms = Selection.unfold_entities(struswap, 'A')
                        old_list_atoms = sorted(old_list_atoms, key=lambda x:x.get_parent().get_full_id()[3][1:])
                        PDBTRANS = Bioinformatics.getPDBFromListOfAtom(old_list_atoms)[0]
                        #file_b=open(file_to_swap[:-4]+'trans.pdb','w')
                        #file_b.write(PDBTRANS)
                        #file_b.close()
                        try:
                            (rmsT,nref,ncom,allAtoms,compStru,pda) = Bioinformatics.getSuperimp(PDBTRANS,PDBTEMP,"PDBSTRINGBM_RESIDUES_CONSERVED",algorithm="nigels-core2",backbone=True,superpose_exclude=1,n_iter=None,onlyCA=True)
                        except:
                            print "Error in superposition at the swapping, skipping this model",file_to_swap
                            #print sys.exc_info()
                            #traceback.print_exc(file=sys.stdout)
                            continue
                        print '************************************************'
                        print 'rmsd between model_to_swap and target is',rmsT
                        print 'writing out swapped model'
                        print 'file_to_swap',file_to_swap
                        if rmsT==100:
                            print 'The rmsd for this model could not be computed, skipping it'
                            continue
                        print '************************************************'  
                        file_c=open(file_to_swap,'w')
                        file_c.write(pda[0])
                        file_c.close()
                        #if rmsT > 10:# we should put a hard limit of how high could it be
                        #    print 'CHECK THIS'
                        #    sys.exit(0)
                        list_swapped_models.append(os.path.basename(file_to_swap))

                        for key in convNames.keys():    
                            #print 'convNames[key]',convNames[key]
                            name=os.path.basename(convNames[key])
                            if name in list_swapped_models:
                                #print '     this model is in list_swapped_models'
                                convNames[key]=os.path.join(path_swap_folder,name)
                                # now we can push the changed rota to the NewCluAll

                    SELSLIB2.writeSumClusters(Clusters=saveCluAll, dirout=path_swap_folder, filename='swapped',RotClu=RotClu, convNames=convNames, LIMIT_CLUSTER=i,euler_frac_zero=True)
                    convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters,os.path.join(current_directory, "./7_SWAP/" + str(i) + "/swapped.sum"),'ROTSOL',
                                                                                               LIMIT_CLUSTER=i,
                                                                                               give_fixed_frags=True)
                else:
                    convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters,os.path.join(current_directory, "./7_SWAP/" + str(i) + "/swapped.sum"),'ROTSOL',
                                                                                               LIMIT_CLUSTER=i,
                                                                                               give_fixed_frags=True)
            # NOTE: This is a new feature, developed by Claudia, needs to be carefully tested
            

            #convNames_writepdbs = copy.deepcopy(convNames)
            if not os.path.exists(os.path.join(current_directory, "./8.5_ROTTRA/" + str(i) + "/")):
                SELSLIB2.getTheTOPNOfEachCluster(DicParameters=DicParameters, frag_fixed=fixed_frags,
                                                 dirout=os.path.join(current_directory, "./8.5_ROTTRA/" + str(i) + "/"),
                                                 mode="matrix", quate=quate, ClusAll=CluAll, convNames=convNames,
                                                 ntop=None, writePDB=True, performTranslation=True,
                                                 elongatingModel=None, createSimmetry=False, cell_dim=cell_dim,
                                                 laue=laue, ncs=ncs, modeTra="frac", LIMIT_CLUSTER=i,
                                                 renameWithConvNames=True, sufixSolPos=not applyNameFilter)

            if not os.path.exists(os.path.join(current_directory, "9.5_EXP",str(i),"solCC.sum")):
                currentClusterDir= os.path.normpath(os.path.join(current_directory, "9.5_EXP",str(i)))

                # NS, delete the old cluster expansion folder if it is already present (meaning it had finished incorrectly in a previous run)
                if ANOMALOUS and os.path.exists(currentClusterDir):
                    try :
                        print("REMARK: It seems that the folder {} exists from a previous interrupted run, deleting it\n.".format(currentClusterDir))
                        shutil.rmtree(currentClusterDir)

                        # Deleting subsequent folders
                        ANOMLIB.deleteSubsequentFiles(root=os.path.abspath(current_directory))  # deletes 10*, 11*, best*
                        dir9Exp=os.path.normpath(os.path.join(current_directory, "9_EXP",str(i)))
                        if os.path.exists(dir9Exp):    #delete also this one since it comes after (just in case)
                            shutil.rmtree(dir9Exp)
                            print("REMARK: It seems that the folder {} also exists from a previous interrupted run, deleting it, as well as subsequent directories 10* 11*\n.".format(dir9Exp))
                            

                    except Exception as e:
                        print("WARNING, cannot delete {}".format(currentClusterDir))
                        print(e)


                SystemUtility.open_connection(DicGridConn, DicParameters, cm)
                print("\n******START_EXPANSION 9_5EXP for cluster {} ******\n".format(i))
                (nqueue9, convNames_2) = SELSLIB2.startExpansion(cm, sym, "9.5_EXP_" + str(i), os.path.join(current_directory,"./9.5_EXP/" + str(i) + "/"), hkl, ent, nice, cell_dim, spaceGroup, shlxLinea0, os.path.join(current_directory, "./8.5_ROTTRA/" + str(i) + "/"),
                                                                 fragdomain=True, fragAnom=fragAnom,**startExpAnomDic)

                SystemUtility.endCheckQueue()
                if ANOMALOUS:
                    if "9.5_EXP" not in solutions_filtered_out[str(i)] or os.path.exists(os.path.join(ANOMDIR,'filteredSol.json')):
                        #reinitialize the dictionnary of eliminated solutions for this cluster since it will be recomputed
                        print("REMARK: Erasing previous recorded filtered solutions from filteredSol.json for cluster {} and step {}".format(i,"9.5_EXP"))
                        solutions_filtered_out[str(i)]["9.5_EXP"] = []


                    if delEvalDir:
                        try:
                            shutil.rmtree(os.path.join(ANOMDIR, "EVALUATION"))
                            shutil.rmtree(os.path.join(ANOMDIR, "RESFILES"))
                            print("** REMARK: deleting the EVALUATION and RESFILES directories from ANOMFILES")

                        except:
                            print("WARNING, cannot delete {}".format(os.path.join(ANOMDIR, "EVALUATION")))

                        finally:
                            delEvalDir=False   #These will not be deleted for the next clusters

                    #Get the llg and zscore for all solutions:

                    convNamesAnom.update(convNames)
                    llgdic= ANOMLIB.llgdic(convNamesAnom, CluAll)

                    CC_Val2, eliminatedSol = SELSLIB2.evaluateExp_CC(DicParameters=DicParameters, cm=cm, sym=sym, DicGridConn=DicGridConn, nameJob="9.5_EXP_" + str(i),
                                                      outputDicr=os.path.join(current_directory, "./9.5_EXP/" + str(i) + "/"), nqueue=nqueue9,
                                                      convNames=convNames_2, savePHS=savePHS, archivingAsBigFile=archivingAsBigFile,
                                                      phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim, anomDic=startExpAnomDic, pattersonPeaks=pattersonPeaks, isBORGES=True, llgdic=llgdic)

                    # CC_Val2 is already filtered when coming out of evaluateExp_CC
                    # But we have to filter out CluAll later because it gets re-read from 7.5_PACK at line 2049
                    solutions_filtered_out[str(i)]["9.5_EXP"] +=  eliminatedSol                                    
                    if len(solutions_filtered_out[str(i)]["9.5_EXP"])>0:
                        ANOMLIB.saveFilteredSol(os.path.join(ANOMDIR,'filteredSol.json'),solutions_filtered_out)
                
                else:
                    CC_Val2 = SELSLIB2.evaluateExp_CC(DicParameters=DicParameters, cm=cm, sym=sym, DicGridConn=DicGridConn, nameJob="9.5_EXP_" + str(i),
                                                      outputDicr=os.path.join(current_directory, "./9.5_EXP/" + str(i) + "/"), nqueue=nqueue9,
                                                      convNames=convNames_2, savePHS=savePHS, archivingAsBigFile=archivingAsBigFile,
                                                      phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim)

                # SystemUtility.close_connection(DicGridConn,DicParameters,cm)
            else:
                CC_Val2, con = SELSLIB2.readCCValFromSUM(
                    os.path.join(current_directory, "./9.5_EXP/" + str(i) + "/solCC.sum"))

            # NS: here it reads the solutions backwards, just after packing
            if not os.path.exists(os.path.join(current_directory, "./8_RBR/" + str(i) + "/clustersNoRed.sum")):
                if USE_PACKING:
                    if swap_model_after_translation==None:
                        convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                               os.path.join(
                                                                                                   current_directory,
                                                                                                   "./7.5_PACK_Library/" + str(
                                                                                                       i) + "/clustersRed.sum"),
                                                                                               "ROTSOL",
                                                                                               LIMIT_CLUSTER=i,
                                                                                               give_fixed_frags=True)
                    else:
                        print 'The swap model option is ON, we need to get the files from the proper directory'
                        convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters,os.path.join(current_directory, "./7_SWAP/" + str(i) + "/swapped.sum"),'ROTSOL',
                                                                                               LIMIT_CLUSTER=i,
                                                                                               give_fixed_frags=True)
                elif USE_TRANSLA:
                    convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                               os.path.join(
                                                                                                   current_directory,
                                                                                                   "./6_FTF_Library/" + str(
                                                                                                       i) + "/clustersNoRedPSol.sum"),
                                                                                               "ROTSOL",
                                                                                               LIMIT_CLUSTER=i,
                                                                                               give_fixed_frags=True)

                else:
                    if not USE_TNCS and not USE_RGR:
                        convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters, os.path.join(
                                                                                                   current_directory,
                                                                                                   "./1_FRF_Library/clustersNoRed.sum"),
                                                                                                   "ROTSOL",
                                                                                                    LIMIT_CLUSTER=i,
                                                                                                    give_fixed_frags=True)
                    elif not USE_TNCS and USE_RGR:
                        # If you reach this point, no translation and no packing has been performed, but gyre has
                        # In that case, it should be reading from 3_RGR not from 1_FRF!
                        last_gyre=cycles_gyre-1
                        convNames,CluAll,RotClu,encn,nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters=DicParameters, 
                                                                                        sumPath=os.path.join(current_directory,
                                                                                        "./3_RGR/"+str(i)+"/"+str(last_gyre)+"/clustersNoRed.sum"),
                                                                                        table="ROTSOL",LIMIT_CLUSTER=i,euler_to_zero=True,give_fixed_frags=True)

                SystemUtility.open_connection(DicGridConn, DicParameters, cm)

                print 'SHERLOCK RMSD before startRNP ',RMSD
                print 'SHERLOCK rmsd_step before startRNP ', rmsd_step
                (nqueue10, convino) = SELSLIB2.startRNP(DicParameters=DicParameters, cm=cm, sym=sym,
                                                        nameJob="8_RBR_" + str(i), ClusAll=CluAll, ensembles=convNames,
                                                        outputDire=os.path.join(current_directory,
                                                                                "./8_RBR/" + str(i) + "/"), mtz=mtz,
                                                        MW=MW, NC=NC, F=F, SIGF=SIGF, Intensities=Intensities,
                                                        Aniso=Aniso, normfactors=normfactors, tncsfactors=tncsfactors,
                                                        nice=nice, RMSD=RMSD, lowR=99, highR=res_refin,
                                                        spaceGroup=spaceGroup, frag_fixed=nfixfr, LIMIT_CLUSTER=i,
                                                        sampl=sampl_refin, VRMS=VRMS, USE_TNCS=USE_TNCS,
                                                        USE_RGR=USE_RGR, BFAC=BFAC, BULK_FSOL=BULK_FSOL,
                                                        BULK_BSOL=BULK_BSOL, RNP_GYRE=False, formfactors=formfactors)

                SystemUtility.endCheckQueue()

                CluAll, convNames, tolose = SELSLIB2.evaluateFTF(DicParameters=DicParameters, cm=cm, sym=sym,
                                                                 DicGridConn=DicGridConn, nameJob="8_RBR_" + str(i),
                                                                 outputDicr=os.path.join(current_directory,"./8_RBR/"
                                                                                         + str(i) + "/"),
                                                                 nqueue=nqueue10,ensembles=convNames, excludeZscore=-10,
                                                                 fixed_frags=nfixfr, quate=quate, mode="RNP", laue=laue,
                                                                 listNCS=ncs, clusteringMode=clusteringAlg,
                                                                 cell_dim=cell_dim, thresholdCompare=thresholdCompare,
                                                                 evaLLONG=evaLLONG,LIMIT_CLUSTER=i,convNames=convino,
                                                                 tops=topRNP,make_positive_llg=make_positive_llg)
                if USE_PACKING:
                    CluAll, convNames = SELSLIB2.mergeZSCOREinRNP(DicParameters, sumPACK, CluAll, convNames,
                                                                  isARCIMBOLDO_LITE=False)

                # Before writing the sum file we need to filter out the fixed fragments and reset the euler and frac
                # to zero
                filteredCluAll=[]
                for clu in CluAll:
                    dicclu = {"heapSolutions": ADT.Heap()}
                    for prio, rotaz in clu["heapSolutions"].asList():
                        if rotaz.has_key('euler'):
                            rotaz['euler']=[0.0,0.0,0.0]
                            #print 'SHERLOCK Setting euler angles to ',rotaz['euler']
                        if rotaz.has_key('frac'):
                            rotaz['frac'] = [0.0, 0.0, 0.0]
                            #print 'SHERLOCK Setting frac to ', rotaz['frac']
                        if rotaz.has_key('quaternion'):
                            rotaz['quaternion'] = [0.0, 0.0, 0.0, 0.0]
                            #print 'SHERLOCK Setting quaternion to ', rotaz['quaternion']
                        if rotaz.has_key('fixed_frags'):
                            returnval=rotaz.pop('fixed_frags', None)
                            #print ' SHERLOCK Removing ',returnval
                        dicclu["heapSolutions"].push(prio, rotaz)
                    filteredCluAll.append(dicclu)
                CluAll=filteredCluAll

                #NS Also, we need to filter eliminated solutions from the anomalous scoring process:
                #if ANOMALOUS and ANOM_HARD_FILTER and len(solutions_filtered_out[str(i)])>0:
                #    print("REMARK: filtering out %d solutions after evaluateExp_CC 9_5exp"%len(solutions_filtered_out[str(i)]))
                #    CluAll = ANOMLIB.filterCluAll(CluAll, set(solutions_filtered_out[str(i)]), LIMIT_CLUSTER=i , convNamesDic=convNamesAnom)
                # print '***********************************************'
                # for clu in filteredCluAll:
                #     for prio, rotaz in clu["heapSolutions"].asList():
                #         print 'SHERLOCK prio, rotaz',prio,rotaz
                #
                # sys.exit(0)



                SELSLIB2.writeSumClusters(Clusters=CluAll,
                                          dirout=os.path.join(current_directory, "./8_RBR/" + str(i) + "/"),
                                          filename="clustersNoRed", convNames=convNames, LIMIT_CLUSTER=i, saveMAP=False,
                                          euler_frac_zero=False) # They will be already reset
            else:
                convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters, os.path.join(current_directory, "./8_RBR/" + str(i) + "/clustersNoRed.sum"), "ROTSOL", LIMIT_CLUSTER=i, give_fixed_frags=True)
                

            if RNP_GYRE:
                names_before_gimble, a, b, c, d = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                   os.path.join(current_directory,
                                                                                                "./8_RBR/" + str(i) +
                                                                                                "/clustersNoRed.sum"),
                                                                                   "ROTSOL", LIMIT_CLUSTER=i,
                                                                                           give_fixed_frags=True)

            if RNP_GYRE and not os.path.exists(
                    os.path.join(current_directory, "./8_GIMBLE/" + str(i) + "/clustersNoRed.sum")):
                convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters, os.path.join(
                    current_directory, "./8_RBR/" + str(i) + "/clustersNoRed.sum"), "ROTSOL", LIMIT_CLUSTER=i,
                                                                                           give_fixed_frags=True)

                SystemUtility.open_connection(DicGridConn, DicParameters, cm)

                (nqueue10, convino) = SELSLIB2.startRNP(DicParameters=DicParameters, cm=cm, sym=sym,
                                                        nameJob="8_GIMBLE_" + str(i), ClusAll=CluAll,
                                                        ensembles=names_before_gimble, outputDire=os.path.join(current_directory,
                                                                                                     "./8_GIMBLE/" + str(
                                                                                                         i) + "/"),
                                                        mtz=mtz, MW=MW, NC=NC, F=F, SIGF=SIGF, Intensities=Intensities,
                                                        Aniso=Aniso, normfactors=normfactors, tncsfactors=tncsfactors,
                                                        nice=nice, RMSD=RMSD, lowR=99, highR=res_refin,
                                                        spaceGroup=spaceGroup, frag_fixed=nfixfr, LIMIT_CLUSTER=i,
                                                        sampl=sampl_refin, VRMS=VRMS, USE_TNCS=USE_TNCS,
                                                        USE_RGR=USE_RGR, BFAC=BFAC, BULK_FSOL=BULK_FSOL,
                                                        BULK_BSOL=BULK_BSOL, RNP_GYRE=True, formfactors=formfactors)

                SystemUtility.endCheckQueue()

                CluAll, convNames, tolose = SELSLIB2.evaluateFTF(DicParameters, cm, sym, DicGridConn,
                                                                 "8_GIMBLE_" + str(i), os.path.join(current_directory,
                                                                                                    "./8_GIMBLE/" + str(
                                                                                                        i) + "/"),
                                                                 nqueue10, convNames, -10, nfixfr, quate, "RNP_GIMBLE", laue,
                                                                 ncs, clusteringAlg, cell_dim, thresholdCompare,
                                                                 evaLLONG, LIMIT_CLUSTER=i, convNames=convino,
                                                                 tops=topRNP, ent=ent, models_directory=model_directory,make_positive_llg=make_positive_llg)
                if USE_TRANSLA:
                    CluAll, convNames = SELSLIB2.mergeZSCOREinRNP(DicParameters, sumPACK, CluAll, convNames,
                                                                  isARCIMBOLDO_LITE=False)

                SELSLIB2.writeSumClusters(CluAll, os.path.join(current_directory, "./8_GIMBLE/" + str(i) + "/"),
                                          "clustersNoRed", convNames, LIMIT_CLUSTER=i)
            elif os.path.exists(os.path.join(current_directory, "./8_GIMBLE/" + str(i) + "/clustersNoRed.sum")):
                convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters, os.path.join(
                   current_directory, "./8_GIMBLE/" + str(i) + "/clustersNoRed.sum"), "ROTSOL", LIMIT_CLUSTER=i,
                                                                                          give_fixed_frags=True)
            else:
                convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters, os.path.join(
                   current_directory, "./8_RBR/" + str(i) + "/clustersNoRed.sum"), "ROTSOL", LIMIT_CLUSTER=i, give_fixed_frags=True)

            # Recompute the LLGs after gimble, by using the computeLLGonly option in the startRNP option
            # Includes the writing of a sum file in order to avoid missing this step or having to recompute it
            if RNP_GYRE and not os.path.exists(os.path.join(current_directory, "./8_GIMBLE_LLG/" + str(i)
                    + "/clustersNoRed.sum")):
                convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters=DicParameters,
                                                                                           sumPath=os.path.join(current_directory,"./8_GIMBLE/" + str(i) +"/clustersNoRed.sum"),
                                                                                           table="ROTSOL",
                                                                                           LIMIT_CLUSTER=i,
                                                                                           skip_reading_variables=False,
                                                                                           give_fixed_frags=True,
                                                                                           euler_to_zero=False)

                SystemUtility.open_connection(DicGridConn, DicParameters, cm)

                (nqueue10, convino) = SELSLIB2.startRNP(DicParameters=DicParameters, cm=cm, sym=sym,
                                                        nameJob="8_GIMBLE_LLG_" + str(i), ClusAll=CluAll,
                                                        ensembles=convNames, outputDire=os.path.join(current_directory,
                                                                                                     "./8_GIMBLE_LLG/"
                                                                                                     + str(i) + "/"),
                                                        mtz=mtz, MW=MW, NC=NC, F=F, SIGF=SIGF, Intensities=Intensities,
                                                        Aniso=Aniso, normfactors=normfactors,tncsfactors=tncsfactors,
                                                        nice=nice, RMSD=RMSD, lowR=99, highR=res_refin,
                                                        spaceGroup=spaceGroup, frag_fixed=nfixfr, LIMIT_CLUSTER=i,
                                                        sampl=sampl_refin, VRMS=VRMS, USE_TNCS=USE_TNCS,
                                                        USE_RGR=USE_RGR, BFAC=BFAC, BULK_FSOL=BULK_FSOL,
                                                        BULK_BSOL=BULK_BSOL, RNP_GYRE=True, computeLLGonly=True,
                                                        formfactors=formfactors)

                SystemUtility.endCheckQueue()

                CluAll, convNames, tolose = SELSLIB2.evaluateFTF(DicParameters=DicParameters, cm=cm, sym=sym,
                                                                 DicGridConn=DicGridConn,
                                                                 nameJob="8_GIMBLE_LLG_" + str(i),
                                                                 outputDicr=os.path.join(current_directory,
                                                                                         "./8_GIMBLE_LLG/" + str(i) +
                                                                                         "/"),
                                                                 nqueue=nqueue10, ensembles=convNames,
                                                                 excludeZscore=-10, fixed_frags=nfixfr, quate=quate,
                                                                 mode="RNP", laue=laue, listNCS=ncs,
                                                                 clusteringMode=clusteringAlg, cell_dim=cell_dim,
                                                                 thresholdCompare=thresholdCompare,
                                                                 evaLLONG=evaLLONG, LIMIT_CLUSTER=i,
                                                                 convNames=convino, tops=topRNP, ent=ent,
                                                                 models_directory=model_directory,
                                                                 make_positive_llg=make_positive_llg)

                SELSLIB2.writeSumClusters(CluAll, os.path.join(current_directory, "./8_GIMBLE_LLG/" + str(i) + "/"),
                                          "clustersNoRed", convNames, LIMIT_CLUSTER=i)

            elif RNP_GYRE and os.path.exists(
                os.path.join(current_directory, "./8_GIMBLE_LLG/" + str(i) + "/clustersNoRed.sum")):
                convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters,os.path.join(current_directory,"./8_GIMBLE_LLG/" + str(i) + "/clustersNoRed.sum"),"ROTSOL",LIMIT_CLUSTER=i,give_fixed_frags=True)
                if ANOMALOUS:
                    convNamesAnom.update(convNames)

            # Now write the output, either of RNP or of GIMBLE_LLG if it has been performed
            SELSLIB2.writeOutputFile(lock=lock, DicParameters=DicParameters, ClusAll=CluAll,
                                     outputDir=current_directory, filename=nameOutput, mode="ARCIMBOLDO-BORGES",
                                     step="RNP", ensembles=convNames, frag_fixed=fixed_frags, LIMIT_CLUSTER=i,
                                     path1=None, path2=None, useRefP1=False, useRGR=False, numberCyclesRef=1,
                                     usePacking=True, useTransla=True, makeEmpty=False, readSum=None,
                                     filterClusters=True,fromphis=False, fromdirexp="11.EXP",coiled_coil=coiled_coil)

            arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)

            if os.path.exists(os.path.join(current_directory, "./8_GIMBLE_LLG/" + str(i) + "/clustersNoRed.sum")):
                SELSLIB2.writeGraphSumClusters(os.path.join(current_directory, "./8_GIMBLE_LLG/" + str(i) + "/clustersNoRed.sum"))
            elif os.path.exists(os.path.join(current_directory, "./8_RBR/" + str(i) + "/clustersNoRed.sum")):
                SELSLIB2.writeGraphSumClusters(os.path.join(current_directory, "./8_RBR/" + str(i) + "/clustersNoRed.sum"))

            path_rnps = os.path.join(current_directory, "./8_RBR/" + str(i) + "/")
            if RNP_GYRE:
                path_rnps = os.path.join(current_directory, "./8_GIMBLE_LLG/" + str(i) + "/")

            #9_EXP
            if not os.path.exists(os.path.join(current_directory, "9_EXP", str(i), "solCC.sum")):

                currentClusterDir= os.path.normpath(os.path.join(current_directory, "9_EXP",str(i)))

                # NS, delete the old cluster expansion folder if it is already present (meaning it had finished incorrectly in a previous run)
                if ANOMALOUS and os.path.exists(currentClusterDir):
                    ANOMLIB.deleteSubsequentFiles(root=os.path.abspath(current_directory))  # deletes 10*, 11*, best*
                    try :
                        shutil.rmtree(currentClusterDir)
                        print("REMARK: It seems that the folder {} exists from a previous interrupted run, deleting it.".format(currentClusterDir))
                        
                    except:
                        print("WARNING, cannot delete {}".format(currentClusterDir))



                SystemUtility.open_connection(DicGridConn, DicParameters, cm)
                print("\n****** START_EXPANSION 9_EXP for cluster {} ******\n".format(i))
                (nqueue11, convNames_3) = SELSLIB2.startExpansion(cm, sym, "9_EXP_" + str(i),
                                                                  os.path.join(current_directory,
                                                                               "./9_EXP/" + str(i) + "/"), hkl, ent,
                                                                  nice, cell_dim, spaceGroup, shlxLinea0, path_rnps,
                                                                  fragdomain=True, fragAnom=fragAnom,**startExpAnomDic)

                SystemUtility.endCheckQueue()
                if ANOMALOUS:
                    convNamesAnom.update(convNames)
                    #NS Get the llg and zscore for all solutions:
                    llgdic= ANOMLIB.llgdic(convNamesAnom, CluAll)

                    if "9_EXP" not in solutions_filtered_out[str(i)] or os.path.exists(os.path.join(ANOMDIR,'filteredSol.json')):
                        #reinitialize the dictionnary of eliminated solutions for this cluster since it will be recomputed
                        print("REMARK: Erasing previous recorded filtered solutions from filteredSol.json for cluster {} and step {}".format(i,"9_EXP"))
                        solutions_filtered_out[str(i)]["9_EXP"]=[]

                    CC_Val1, eliminatedSol = SELSLIB2.evaluateExp_CC(DicParameters=DicParameters, cm=cm, sym=sym, DicGridConn=DicGridConn, nameJob="9_EXP_" + str(i), 
                                                      outputDicr=os.path.join(current_directory, "./9_EXP/" + str(i) + "/"), nqueue=nqueue11,
                                                      convNames=convNames_3, savePHS=savePHS, archivingAsBigFile=archivingAsBigFile,
                                                      phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim, anomDic=startExpAnomDic, pattersonPeaks=pattersonPeaks, isBORGES=True, llgdic=llgdic)


                    if ANOM_HARD_FILTER:
                        # Eliminate in the ends solutions which have been either discarded in 9.5EXP or 9.5 (fast since few models remain in the end)               
                        solutions_filtered_out[str(i)]["9_EXP"] += eliminatedSol
                        CC_Val1,CC_Val2 = ANOMLIB.intersectCCVal([CC_Val1,CC_Val2])
                    else:
                        # eliminate in the end only solutions which have been discarded in BOTH 9.5EXP and 9.5 (more models retained)
                        solutions_filtered_out[str(i)]["9_EXP"] = ANOMLIB.intersectionFilteredSol([CC_Val1,CC_Val2], eliminatedSol)

                    if len(solutions_filtered_out[str(i)]["9_EXP"])>0:
                        print("REMARK: filtering out %d solutions after evaluateExp_CC 9_exp"%len(solutions_filtered_out[str(i)]["9_EXP"]))                        
                        ANOMLIB.saveFilteredSol(os.path.join(ANOMDIR,'filteredSol.json'),solutions_filtered_out)

                        # The solutions eliminated here must be removed from the previous CCVal2 list:

                        

                else:
                    CC_Val1 = SELSLIB2.evaluateExp_CC(DicParameters=DicParameters, cm=cm, sym=sym, DicGridConn=DicGridConn, nameJob="9_EXP_" + str(i), 
                                                      outputDicr=os.path.join(current_directory, "./9_EXP/" + str(i) + "/"), nqueue=nqueue11,
                                                      convNames=convNames_3, savePHS=savePHS, archivingAsBigFile=archivingAsBigFile,
                                                      phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim)                    

            else:
                CC_Val1, con1 = SELSLIB2.readCCValFromSUM(os.path.join(current_directory, "./9_EXP/" + str(i) + "/solCC.sum"))
                # The solutions eliminated here must be removed from the previous CCVal2 list:
                if ANOMALOUS:
                    if ANOM_HARD_FILTER:
                        CC_Val1,CC_Val2 = ANOMLIB.intersectCCVal([CC_Val1,CC_Val2])
                    else:
                        # eliminate in the end only solutions which have been discarded in BOTH 9.5EXP and 9.5 (more models retained)
                        # Here this is just a way of keeping only the relevant solution names to filter cluall afterwards
                        print("The number of eliminated solutions is so far: %d"%len(solutions_filtered_out[str(i)]["9_EXP"]))
                        solutions_filtered_out[str(i)]["9_EXP"] = ANOMLIB.intersectionFilteredSol([CC_Val1,CC_Val2], solutions_filtered_out[str(i)])
                        print("The number of eliminated solutions is now %d"%len(solutions_filtered_out[str(i)]["9_EXP"]))                       


            if os.path.exists(os.path.join(current_directory, "./10_PREPARED/" + str(i) + "/")):
                for r, subF, fi in os.walk(os.path.join(current_directory, "./10_PREPARED/" + str(i) + "/")):
                    for fileu in fi:
                        pdbf = os.path.join(r, fileu)
                        if pdbf.endswith(".pdb"):
                            os.remove(pdbf)

            # NS: if CC_Val1 is empty (nothing selected from 9_EXP), this will return an empty convNames14 dic
            convNames14 = SELSLIB2.startPREPARE(cm=cm, sym=sym, nameJob="10_PREPARED_" + str(i), CC_Val=CC_Val1,
                                                outputDirectory=os.path.join(current_directory,
                                                                             "./10_PREPARED/" + str(i) + "/"),
                                                cell_dim=cell_dim, spaceGroup=spaceGroup, nTop=topExp, topNext=None)

            if USE_NMA:
                if not os.path.exists(os.path.join(current_directory, "./8.6_NMA/" + str(i) + "/")):
                    SystemUtility.open_connection(DicGridConn, DicParameters, cm)
                    (nqueue15, c) = SELSLIB2.startNMA(DicParameters=DicParameters, cm=cm, sym=sym,
                                                      nameJob="8.6_NMA_" + str(i),
                                                      dir_o_liFile=os.path.join(current_directory,
                                                                                "./10_PREPARED/" + str(i) + "/"),
                                                      outputDire=os.path.join(current_directory,
                                                                              "./8.6_NMA/" + str(i) + "/"), mtz=mtz,
                                                      MW=MW, NC=NC, F=F, SIGF=SIGF, Intensities=Intensities,
                                                      Aniso=Aniso, normfactors=normfactors, tncsfactors=tncsfactors,
                                                      nice=nice, RMSD=RMSD, lowR=99, highR=res_refin, final_rot=peaks,
                                                      save_rot=peaks, frag_fixed=fixed_frags, spaceGroup=spaceGroup,
                                                      sampl=sampl_refin, VRMS=VRMS, BFAC=BFAC, BULK_FSOL=BULK_FSOL,
                                                      BULK_BSOL=BULK_BSOL, formfactors=formfactors)

                    SystemUtility.endCheckQueue()
                    SELSLIB2.evaluateNMA(DicParameters, cm, sym, DicGridConn, "8.6_NMA_" + str(i),
                                         os.path.join(current_directory, "./8.6_NMA/" + str(i) + "/"), i, nqueue15, c)

                if not os.path.exists(os.path.join(current_directory, "./9.6_EXP/" + str(i) + "/solCC.sum")):
                    currentClusterDir= os.path.normpath(os.path.join(current_directory, "9.6_EXP",str(i)))

                    # NS, delete the old cluster expansion folder if it is already present (meaning it had finished incorrectly in a previous run)
                    if ANOMALOUS and os.path.exists(currentClusterDir):

                        try :
                            shutil.rmtree(currentClusterDir)
                            print("REMARK: It seems that the folder {} exists from a previous interrupted run, deleting it.".format(currentClusterDir))


                        except:
                            print("WARNING, cannot delete {}".format(currentClusterDir))

                    SystemUtility.open_connection(DicGridConn, DicParameters, cm)

                    (nqueue14, convNames_4) = SELSLIB2.startExpansion(cm, sym, "9.6_EXP_" + str(i),
                                                                      os.path.join(current_directory,
                                                                                   "./9.6_EXP/" + str(i) + "/"), hkl,
                                                                      ent, nice, cell_dim, spaceGroup, shlxLinea0,
                                                                      os.path.join(current_directory,
                                                                                   "./8.6_NMA/" + str(i) + "/"),
                                                                      fragdomain=True, fragAnom=fragAnom,**startExpAnomDic)

                    SystemUtility.endCheckQueue()
                    if ANOMALOUS:

                        if "9.6_EXP" not in solutions_filtered_out[str(i)] or os.path.exists(os.path.join(ANOMDIR,'filteredSol.json')):
                            #reinitialize the dictionnary of eliminated solutions for this cluster since it will be recomputed
                            #solutions_filtered_out={}
                            print("REMARK: Erasing previous recorded filtered solutions from filteredSol.json for cluster {} and step {}".format(i,"9_EXP"))
                            solutions_filtered_out[str(i)]["9.6_EXP"]=[]

                        #Get the llg and zscore for all solutions:
                        llgdic= ANOMLIB.llgdic(convNamesAnom, CluAll)
                        CC_Val3, eliminatedSol = SELSLIB2.evaluateExp_CC(DicParameters=DicParameters, cm=cm, sym=sym, DicGridConn=DicGridConn, nameJob="9.6_EXP_" + str(i),
                                                          outputDicr=os.path.join(current_directory, "./9.6_EXP/" + str(i) + "/"),
                                                          nqueue=nqueue14, convNames=convNames_4, savePHS=savePHS,
                                                          archivingAsBigFile=archivingAsBigFile,
                                                          phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim, anomDic=startExpAnomDic, pattersonPeaks=pattersonPeaks, isBORGES=True, llgdic=llgdic)
                       
                        if ANOM_HARD_FILTER:
                            # Eliminate in the ends solutions which have been either discarded in 9.5EXP or 9.5 (fast since few models remain in the end)               
                            solutions_filtered_out[str(i)]["9.6_EXP"] += eliminatedSol
                            CC_Val1, CC_Val2, CC_Val3 = ANOMLIB.intersectCCVal([CC_Val1,CC_Val2,CC_Val3])
                        else:
                            # eliminate in the end only solutions which have been discarded in BOTH 9.5EXP and 9.5 (more models retained)
                            solutions_filtered_out[str(i)]["9.6_EXP"] = ANOMLIB.intersectionFilteredSol([CC_Val1,CC_Val2,CC_Val3], eliminatedSol)

                        if len(solutions_filtered_out[str(i)]["9.6_EXP"])>0:
                            print("REMARK: filtering out %d solutions after evaluateExp_CC 9.6_exp"%len(solutions_filtered_out[str(i)]["9.6_EXP"]))                        
                            ANOMLIB.saveFilteredSol(os.path.join(ANOMDIR,'filteredSol.json'),solutions_filtered_out)
                            
                            

                    else:
                        CC_Val3 = SELSLIB2.evaluateExp_CC(DicParameters=DicParameters, cm=cm, sym=sym, DicGridConn=DicGridConn, nameJob="9.6_EXP_" + str(i),
                                                          outputDicr=os.path.join(current_directory, "./9.6_EXP/" + str(i) + "/"),
                                                          nqueue=nqueue14, convNames=convNames_4, savePHS=savePHS,
                                                          archivingAsBigFile=archivingAsBigFile,
                                                          phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim)                        

                    # SystemUtility.close_connection(DicGridConn,DicParameters,cm)
                else:
                    CC_Val3, con4 = SELSLIB2.readCCValFromSUM(os.path.join(current_directory, "./9.6_EXP/" + str(i) + "/solCC.sum"))
                    if ANOMALOUS and ANOM_HARD_FILTER:
                        # The solutions eliminated here must be removed from the previous CCVal3 list:
                        CC_Val1, CC_Val2, CC_Val3 = ANOMLIB.intersectCCVal([CC_Val1,CC_Val2,CC_Val3])
            elif USE_OCC:
                if not os.path.exists(os.path.join(current_directory, "./8.6_OCC/" + str(i) + "/")):
                    SystemUtility.open_connection(DicGridConn, DicParameters, cm)

                    (nqueue15, c) = SELSLIB2.startOCC(DicParameters=DicParameters, cm=cm, sym=sym,
                                                      nameJob="8.6_OCC_" + str(i), dir_o_liFile=path_rnps,
                                                      outputDire=os.path.join(current_directory,
                                                                              "./8.6_OCC/" + str(i) + "/"), mtz=mtz,
                                                      MW=MW, NC=NC, F=F, SIGF=SIGF, Intensities=Intensities,
                                                      Aniso=Aniso, normfactors=normfactors, tncsfactors=tncsfactors,
                                                      nice=nice, RMSD=RMSD, lowR=99, highR=res_refin, final_rot=peaks,
                                                      save_rot=peaks, frag_fixed=fixed_frags, spaceGroup=spaceGroup,
                                                      sampl=sampl_refin, ellg=None, nres=None, rangeocc=None,
                                                      merge=None, occfrac=None, occoffset=None, ncycles=None, VRMS=VRMS,
                                                      BFAC=BFAC, BULK_FSOL=BULK_FSOL, BULK_BSOL=BULK_BSOL,
                                                      formfactors=formfactors)

                    SystemUtility.endCheckQueue()
                    SELSLIB2.evaluateOCC(DicParameters, cm, sym, DicGridConn, "8.6_OCC_" + str(i),
                                         os.path.join(current_directory, "./8.6_OCC/" + str(i) + "/"), nqueue15, c)

                # 9.6 EXP    
                if not os.path.exists(os.path.join(current_directory, "9.6_EXP", str(i), "solCC.sum")):
                    currentClusterDir= os.path.normpath(os.path.join(current_directory, "9.6_EXP",str(i)))

                    # NS, delete the old cluster expansion folder if it is already present (meaning it had finished incorrectly in a previous run)
                    if ANOMALOUS and os.path.exists(currentClusterDir):
                        
                        try :
                            shutil.rmtree(currentClusterDir)
                            print("REMARK: It seems that the folder {} exists from a previous interrupted run, deleting it.".format(currentClusterDir))

                        except:
                            print("WARNING, cannot delete {}".format(currentClusterDir))
                        SystemUtility.open_connection(DicGridConn, DicParameters, cm)

                    (nqueue14, convNames_4) = SELSLIB2.startExpansion(cm, sym, "9.6_EXP_" + str(i),
                                                                      os.path.join(current_directory,
                                                                                   "./9.6_EXP/" + str(i) + "/"), hkl,
                                                                      ent, nice, cell_dim, spaceGroup, shlxLinea0,
                                                                      os.path.join(current_directory,
                                                                                   "./8.6_OCC/" + str(i) + "/"),
                                                                      fragdomain=True, fragAnom=fragAnom,**startExpAnomDic)

                    SystemUtility.endCheckQueue()
                    if ANOMALOUS:

                        if "9.6_EXP" not in solutions_filtered_out[str(i)] or os.path.exists(os.path.join(ANOMDIR,'filteredSol.json')):
                            #reinitialize the dictionnary of eliminated solutions for this cluster since it will be recomputed
                            #solutions_filtered_out={}
                            print("REMARK: Erasing previous recorded filtered solutions from filteredSol.json for cluster {} and step {}".format(i,"9.6_EXP"))
                            solutions_filtered_out[str(i)]["9.6_EXP"]=[]


                        #Get the llg and zscore for all solutions:
                        llgdic= ANOMLIB.llgdic(convNamesAnom, CluAll)
                        CC_Val3, eliminatedSol = SELSLIB2.evaluateExp_CC(DicParameters=DicParameters, cm=cm, sym=sym, DicGridConn=DicGridConn, nameJob="9.6_EXP_" + str(i),
                                                          outputDicr=os.path.join(current_directory, "./9.6_EXP/" + str(i) + "/"),
                                                          nqueue=nqueue14, convNames=convNames_4, savePHS=savePHS,
                                                          archivingAsBigFile=archivingAsBigFile,
                                                          phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim, anomDic=startExpAnomDic, pattersonPeaks=pattersonPeaks, isBORGES=True, llgdic=llgdic)
                        
                        if ANOM_HARD_FILTER:
                            # Eliminate in the ends solutions which have been either discarded in 9.5EXP or 9.5 (fast since few models remain in the end)               
                            solutions_filtered_out[str(i)]["9.6_EXP"] += eliminatedSol
                            CC_Val1, CC_Val2, CC_Val3 = ANOMLIB.intersectCCVal([CC_Val1,CC_Val2,CC_Val3])
                        else:
                            # eliminate in the end only solutions which have been discarded in BOTH 9.5EXP and 9.5 (more models retained)
                            solutions_filtered_out[str(i)]["9.6_EXP"] = ANOMLIB.intersectionFilteredSol([CC_Val1,CC_Val2,CC_Val3], eliminatedSol)

                        if len(solutions_filtered_out[str(i)]["9.6_EXP"])>0:                       
                            ANOMLIB.saveFilteredSol(os.path.join(ANOMDIR,'filteredSol.json'),solutions_filtered_out)                     
                        
                    else:
                        CC_Val3 = SELSLIB2.evaluateExp_CC(DicParameters=DicParameters, cm=cm, sym=sym, DicGridConn=DicGridConn, nameJob="9.6_EXP_" + str(i),
                                                          outputDicr=os.path.join(current_directory, "./9.6_EXP/" + str(i) + "/"),
                                                          nqueue=nqueue14, convNames=convNames_4, savePHS=savePHS,
                                                          archivingAsBigFile=archivingAsBigFile,
                                                          phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim)                        

                    # SystemUtility.close_connection(DicGridConn,DicParameters,cm)
                else:
                    CC_Val3, con4 = SELSLIB2.readCCValFromSUM(os.path.join(current_directory, "./9.6_EXP/" + str(i) + "/solCC.sum"))
                    if ANOMALOUS:
                        if ANOM_HARD_FILTER:
                            # The solutions eliminated here must be removed from the previous CCVal1 and CCval2 lists:
                            CC_Val1, CCVal2, CC_Val3 = ANOMLIB.intersectCCVal([CC_Val1,CC_Val2,CC_Val3])
                        else:
                            solutions_filtered_out[str(i)]["9.6_EXP"] = ANOMLIB.intersectionFilteredSol([CC_Val1,CC_Val2,CC_Val3], eliminatedSol)

            else:
                CC_Val3 = []

            convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters, os.path.join(path_rnps,"clustersNoRed.sum"), "ROTSOL", LIMIT_CLUSTER=i,give_fixed_frags=True)
            #NS: here we have to refilter CluAll to what it was after 8_RBR and all subsequent steps, CC_Val1, CC_Val2, CC_Val3 are already filtered in their respective evaluateExp function
            if ANOMALOUS:

                # print("length CC_val1 %d"%len(CC_Val1))
                # print("length CC_val2 %d"%len(CC_Val2))
                # print("length CC_val3 %d"%len(CC_Val3))
                # sys.exit(1)

                if len(CC_Val1)==0 and len(CC_Val2)==0 and len(CC_Val3)==0:
                    print("SORRY: it seems that no solution survived the anomalous scoring process!")
                    print("Next Cluster!")
                    arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)
                    continue

                #Now we can filter CluAll    
                CluAll = ANOMLIB.filterCluAll(CluAll, solutions_filtered_out[str(i)], LIMIT_CLUSTER=i , convNamesDic=convNamesAnom)
                print("REMARK: Removing %d eliminated solutions from CluAll (from the anomalous scoring process)"%len(solutions_filtered_out[str(i)]))

            if not USE_OCC:
                CC_Val = SELSLIB2.unifyCC2(CC_Val1, CC_Val2, CC_Val3, convNames, CluAll, suffixA="_rnp",
                                           suffixB="_rottra", suffixC="_nma",
                                           solution_sorting_scheme=solution_sorting_scheme, mode="ARCIMBOLDO_BORGES")

            elif prioritize_occ:
                CC_Val = SELSLIB2.unifyCC2([], [], CC_Val3, convNames, CluAll, suffixA="_rnp", suffixB="_rottra",
                                           suffixC="_occ", solution_sorting_scheme=solution_sorting_scheme, mode="ARCIMBOLDO_BORGES")
            else:
                CC_Val = SELSLIB2.unifyCC2(CC_Val1, CC_Val2, CC_Val3, convNames, CluAll, suffixA="_rnp",
                                           suffixB="_rottra", suffixC="_occ",
                                           solution_sorting_scheme=solution_sorting_scheme, mode="ARCIMBOLDO_BORGES")

            if USE_NMA or USE_OCC:
                SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput,
                                         "ARCIMBOLDO-BORGES", "INITCC", convNames, fixed_frags,
                                         path1=os.path.join(current_directory, "./9.5_EXP/" + str(i) + "/solCC.sum"),
                                         path2=os.path.join(current_directory, "./9.6_EXP/" + str(i) + "/solCC.sum"),
                                         LIMIT_CLUSTER=i,coiled_coil=coiled_coil)
            else:
                SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput,
                                         "ARCIMBOLDO-BORGES", "INITCC", convNames, fixed_frags,
                                         path1=os.path.join(current_directory, "./9.5_EXP/" + str(i) + "/solCC.sum"),
                                         path2=os.path.join(current_directory, "./9_EXP/" + str(i) + "/solCC.sum"),
                                         LIMIT_CLUSTER=i,coiled_coil=coiled_coil)

            # NS: again, an empty dictionary will be returned here if CC_Val is []
            convNames14 = SELSLIB2.startPREPARE(cm, sym, "10_PREPARED_" + str(i), CC_Val,
                                                os.path.join(current_directory, "./10_PREPARED/" + str(i) + "/"),
                                                cell_dim, spaceGroup, topExp)

            arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)

            if topExp_run is not None:
                if os.path.exists(os.path.join(current_directory, "./10_PREPARED/" + str(i) + "/")):
                    for r, subF, fi in os.walk(os.path.join(current_directory, "./10_PREPARED/" + str(i) + "/")):
                        for fileu in fi:
                            pdbf = os.path.join(r, fileu)
                            if pdbf.endswith(".pdb"):
                                os.remove(pdbf)

                if distribute_computing == "multiprocessing":
                    topExp_run = sym.PROCESSES - 1

                # NOTE: Activated for testing
                if distribute_computing == "multiprocessing" and sym.PROCESSES - 1 < 8:
                    force_exp = True

                if force_exp:
                    topExp_run = 2 * (sym.PROCESSES - 1)

                convNames14 = SELSLIB2.startPREPARE(cm, sym, "10_PREPARED_" + str(i), CC_Val,
                                                    os.path.join(current_directory, "./10_PREPARED/" + str(i) + "/"),
                                                    cell_dim, spaceGroup, topExp_run)

                completernp = "RBR"
                if RNP_GYRE:
                    completernp = "GIMBLE"

                # NOTE: New method to extend solutions randomly
                if randomAtoms or SecStrElong:
                    convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                               os.path.join(
                                                                                                   current_directory,
                                                                                                   "./8_" + completernp + "/" + str(
                                                                                                       i) + "/clustersNoRed.sum"),
                                                                                               "ROTSOL",
                                                                                               LIMIT_CLUSTER=i,
                                                                                               give_fixed_frags=True)
                    if not os.path.exists(os.path.join(current_directory, "./2015_EXPLOIT/" + str(i) + "/")):
                        if randomAtoms:
                            lisvalto = (Config.get(job_type, "parameters_elongation")).split()
                            vala = float(lisvalto[0])
                            valb = int(lisvalto[1])
                            valc = int(lisvalto[2])
                            SELSLIB2.startRandomlyExpand(
                                os.path.join(current_directory, "./10_PREPARED/" + str(i) + "/"),
                                os.path.join(current_directory, "./2015_EXPLOIT/" + str(i) + "/"), vala, valb, valc)
                        elif SecStrElong:
                            lisvalto = (Config.get(job_type, "parameters_elongation")).split()
                            vala = int(lisvalto[0])
                            valb = int(lisvalto[1])
                            valc = int(lisvalto[2])
                            SELSLIB2.startPlaneElongation(
                                os.path.join(current_directory, "./10_PREPARED/" + str(i) + "/"),
                                os.path.join(current_directory, "./2015_EXPLOIT/" + str(i) + "/"), vala, valb, valc)


                    if not os.path.exists(os.path.join(current_directory, "9.6_EXP_REXPL", str(i), "solCC.sum")):

                        currentClusterDir= os.path.normpath(os.path.join(current_directory, "9.6_EXP_REXPL",str(i)))

                        # NS, delete the old cluster expansion folder if it is already present (meaning it had finished incorrectly in a previous run)
                        if ANOMALOUS and os.path.exists(currentClusterDir):

                            try :
                                shutil.rmtree(currentClusterDir)
                                print("REMARK: It seems that the folder {} exists from a previous interrupted run, deleting it.".format(currentClusterDir))

                            except:
                                print("WARNING, cannot delete {}".format(currentClusterDir))


                        SystemUtility.open_connection(DicGridConn, DicParameters, cm)

                        (nqueue14, convNames_4) = SELSLIB2.startExpansion(cm, sym, "9.6_EXPREXPL_" + str(i),
                                                                          os.path.join(current_directory,"./9.6_EXP_REXPL/" + str(i) + "/"), hkl, ent, nice,
                                                                          cell_dim, spaceGroup, shlxLinea0 + " -o",
                                                                          os.path.join(current_directory,"./2015_EXPLOIT/" + str(i) + "/"), fragdomain=True, fragAnom=fragAnom,**startExpAnomDic)

                        SystemUtility.endCheckQueue()
                        if ANOMALOUS:

                            if "9.6_EXP_REXPL" not in solutions_filtered_out[str(i)] or os.path.exists(os.path.join(ANOMDIR,'filteredSol.json')):
                                #reinitialize the dictionnary of eliminated solutions for this cluster since it will be recomputed
                                #solutions_filtered_out={}
                                print("REMARK: Erasing previous recorded filtered solutions from filteredSol.json for cluster {} and step {}".format(i,"9.6_EXP_REXPL"))
                                solutions_filtered_out[str(i)]["9.6_EXP_REXPL"]=[]


                            #Get the llg and zscore for all solutions:
                            llgdic= ANOMLIB.llgdic(convNamesAnom, CluAll)
                            CC_Val3, eliminatedSol = SELSLIB2.evaluateExp_CC(DicParameters=DicParameters, cm=cm, sym=sym, DicGridConn=DicGridConn, nameJob="9.6_EXPREXPL_" + str(i),
                                                              outputDicr=os.path.join(current_directory,
                                                                           "./9.6_EXP_REXPL/" + str(i) + "/"), nqueue=nqueue14,
                                                              convNames=convNames_4, initcc_global=True, savePHS=savePHS,
                                                              archivingAsBigFile=archivingAsBigFile,
                                                              phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim, anomDic=startExpAnomDic, pattersonPeaks=pattersonPeaks, isBORGES=True, llgdic=llgdic)
                            
                            #if ANOM_HARD_FILTER:
                                # Here we'll keep the HARD_FILTER mode by default to work only with what previously retained before               
                            solutions_filtered_out[str(i)]["9.6_EXP_REXPL"] += eliminatedSol
                            CC_Val1, CC_Val2, CC_Val3 = ANOMLIB.intersectCCVal([CC_Val1,CC_Val2,CC_Val3])
                            #else:
                            #    solutions_filtered_out[str(i)] = ANOMLIB.intersectionFilteredSol(solutions_filtered_out[str(i)], eliminatedSol)

                            if len(eliminatedSol)>0:
                                ANOMLIB.saveFilteredSol(os.path.join(ANOMDIR,'filteredSol.json'),solutions_filtered_out)
                                CluAll = ANOMLIB.filterCluAll(CluAll, solutions_filtered_out[str(i)], LIMIT_CLUSTER=i , convNamesDic=convNamesAnom)
                                

                        else:
                            CC_Val3 = SELSLIB2.evaluateExp_CC(DicParameters=DicParameters, cm=cm, sym=sym, DicGridConn=DicGridConn, nameJob="9.6_EXPREXPL_" + str(i),
                                                              outputDicr=os.path.join(current_directory,
                                                                           "./9.6_EXP_REXPL/" + str(i) + "/"), nqueue=nqueue14,
                                                              convNames=convNames_4, initcc_global=True, savePHS=savePHS,
                                                              archivingAsBigFile=archivingAsBigFile,
                                                              phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim)                            

                        # SystemUtility.close_connection(DicGridConn,DicParameters,cm)
                    else:
                        CC_Val3, con4 = SELSLIB2.readCCValFromSUM(os.path.join(current_directory, "./9.6_EXP_REXPL/" + str(i) + "/solCC.sum"))
                        if ANOMALOUS:
                            CC_Val1, CC_Val2, CC_Val3 = ANOMLIB.intersectCCVal([CC_Val1,CC_Val2,CC_Val3])

                        # CC_Val = SELSLIB2.selectCC(CC_Val3)
                    CC_Val = CC_Val3
                    shutil.rmtree(os.path.join(current_directory, "./10_PREPARED/" + str(i) + "/"))
                    convNames14 = SELSLIB2.startPREPARE(cm, sym, "10_PREPARED_" + str(i), CC_Val,
                                                        os.path.join(current_directory,
                                                                     "./10_PREPARED/" + str(i) + "/"), cell_dim,
                                                        spaceGroup, topExp)
                ######################################################

                convNames, CluAll, RotClu, encn, nfixfr = SELSLIB2.readClustersFromSUMToDB(DicParameters, os.path.join(
                    current_directory, "./8_" + completernp + "/" + str(i) + "/clustersNoRed.sum"), "ROTSOL",LIMIT_CLUSTER=i,give_fixed_frags=True)
                # NS re-filtering since CluAll has been called from before
                if ANOMALOUS and len(solutions_filtered_out[str(i)])>0:
                    CluAll = ANOMLIB.filterCluAll(CluAll, solutions_filtered_out[str(i)], LIMIT_CLUSTER=i,convNamesDic=convNamesAnom)

                addo = ""
                if randomAtoms or SecStrElong:
                    addo += " -o"

                if alixe:
                    print("we are starting ALIXE")
                    runstring = ""
                    tuple_phi = ()
                    if isShredder:
                        runstring = "SHREDDER"
                    else:
                        runstring = "BORGES"
                    if alixe_mode == 'one_step':
                        #print 'SHERLOCK starting the one step mode on cluster ',i

                        # NS: check that the directory in which alixe will work contains at list one phs file
                        # For this we can check the size of sumCC.sol in 9, 9.5 and 9.6 folders

                        input_mode=0
                        for folder in (9,9.5,9.6):
                            fileToCheck=os.path.join(current_directory, str(folder)+'_EXP', str(i), 'solCC.sum')
                            if os.path.exists(fileToCheck) and os.path.getsize(fileToCheck)>0:
                                input_mode=folder
                                break

                        if input_mode == 0:
                            print("No folder with solCC.sum could be found for Alixe, SKIPPING TO NEXT CLUSTER")
                            continue
                        else:
                            print("\nNOTE: Search folder for Alixe set to {}".format(input_mode))




                        tuple_phi = ALIXE.startALIXEforARCIMBOLDO(os.path.join(current_directory, "./11.5_CLUSTERING/"), i,
                                                                  hkl, cell_dim, spaceGroup, tolerance_list=[60.0, 88.0],
                                                                  resolution=2.0, cycles=3, f_fom=True, run=runstring,
                                                                  mode=alixe_mode, confibor=BorData, input_mode=input_mode)
                        # Format tuple_phi = (name.ins, {"name.phi":{""})
                        if tuple_phi[1] != {}:  # If any phi, call SELSLIB2.shelxe_cycle_BORGES
                            print '\n ALIXE found phase sets combining under the tolerance set, sending them to expansion'
                            # TODO: check how many clusters are we sending for expansion
                            #print 'SHERLOCK topExp', topExp
                            #print 'SHERLOCK topExp_run',topExp_run
                            #print 'SHERLOCK len(tuple_phi[1].keys())',len(tuple_phi[1].keys())
                            SELSLIB2.shelxe_cycle_BORGES(lock=lock, DicParameters=DicParameters, ClusAll=CluAll, cm=cm,
                                                         sym=sym, DicGridConn=DicGridConn, i=i,
                                                         current_directory=current_directory, nameOutput=nameOutput,
                                                         dirPathPart=os.path.join(current_directory,
                                                                                  "./temp_transfer/" + str(i) + "/"),
                                                         fromNcycles=1, toNcycles=nautocyc, spaceGroup=spaceGroup, hkl=hkl,
                                                         ent=ent,cell_dim=cell_dim, nice=nice,
                                                         shlxLineaB=shlxLinea1 + addo, shlxLineaLast=shlxLineaLast,
                                                         traceShelxe=True,fixed_frags=fixed_frags,
                                                         USE_PACKING=USE_PACKING,USE_TRANSLA=USE_TRANSLA,
                                                         USE_REFINEMENT=PERFORM_REFINEMENT_P1,NUMBER_REF_CYCLES=cycle_ref,
                                                         USE_RGR=USE_RGR,isSHREDDER=isShredder, tuple_phi=tuple_phi, startExpAnomDic=startExpAnomDic, pattersonPeaks=pattersonPeaks, llgdic=llgdic, isAlixe=True, nBunchAutoTracCyc=nBunchAutoTracCyc)
                    elif alixe_mode == 'two_steps':
                        evaluated_clusters = orderedClusters[:n_clusters]
                        for clu in evaluated_clusters:
                            if not os.path.exists(os.path.join(current_directory, "./11.5_CLUSTERING/") +
                                                           str(clu)+'/final_alixe_tuple.pkl'):
                                tuple_phi = ALIXE.startALIXEforARCIMBOLDO(clust_fold=os.path.join(current_directory,
                                                                                                  "./11.5_CLUSTERING/"),
                                                                          cluster_id=clu,reference_hkl=hkl, cell=cell_dim,
                                                                          sg_symbol=spaceGroup, tolerance_list=[60.0, 88.0],
                                                                          resolution=2.0, cycles=3, f_fom=True,
                                                                          run=runstring, mode='one_step',
                                                                          confibor=BorData, input_mode=input_mode)
                            else:
                                print ' The first step of phase combination was already completed at cluster ',clu
                        # Now we can go to the second step
                        # Note, if we could, passing a list instead of a single cluster id
                        tuple_phi_second = ALIXE.startALIXEforARCIMBOLDO(clust_fold=os.path.join(current_directory,
                                                                                              "./11.5_CLUSTERING/"),
                                                                      cluster_id=evaluated_clusters, reference_hkl=hkl,
                                                                      cell=cell_dim, sg_symbol=spaceGroup,
                                                                      tolerance_list=[60.0, 88.0], resolution=2.0,
                                                                      cycles=3, f_fom=True, run=runstring,
                                                                      mode='two_steps',
                                                                      confibor=BorData, input_mode=input_mode)

                        # If any phi, call SELSLIB2.shelxe_cycle_BORGES
                        if tuple_phi_second[1] != {} and not os.path.exists(os.path.join(current_directory,'11_EXP_alixe')):
                            print('\n ALIXE found phase sets combining under the tolerance set, sending them to expansion')

                            SELSLIB2.shelxe_cycle_BORGES(lock=lock, DicParameters=DicParameters, ClusAll=CluAll, cm=cm,
                                                         sym=sym, DicGridConn=DicGridConn, i=i,
                                                         current_directory=current_directory, nameOutput=nameOutput,
                                                         dirPathPart=os.path.join(current_directory,
                                                                                  "./temp_transfer/" + str(i) + "/"),
                                                         fromNcycles=1, toNcycles=nautocyc, spaceGroup=spaceGroup, hkl=hkl,
                                                         ent=ent,cell_dim=cell_dim, nice=nice,
                                                         shlxLineaB=shlxLinea1 + addo, shlxLineaLast=shlxLineaLast,
                                                         traceShelxe=True,fixed_frags=fixed_frags,
                                                         USE_PACKING=USE_PACKING,USE_TRANSLA=USE_TRANSLA,
                                                         USE_REFINEMENT=PERFORM_REFINEMENT_P1,NUMBER_REF_CYCLES=cycle_ref,
                                                         USE_RGR=USE_RGR,isSHREDDER=isShredder, tuple_phi=tuple_phi_second, startExpAnomDic=startExpAnomDic, pattersonPeaks=pattersonPeaks, llgdic=llgdic, isAlixe=True, nBunchAutoTracCyc=nBunchAutoTracCyc)


                # TODO:if solved stop otherwise continue with shelxe_cycle_BORGES
                # NOTE: Currently we try both of them, to avoid missing anything

                # NS: Here the pdb files to be extended will be looked for in the directory temp_transfer (from the previous startPREPARE funcions)

                # If no phase cluster has solved keep going with normal expansions

                failure_all = SELSLIB2.shelxe_cycle_BORGES(lock=lock, DicParameters=DicParameters, ClusAll=CluAll, cm=cm, sym=sym,
                                             DicGridConn=DicGridConn, i=i, current_directory=current_directory,
                                             nameOutput=nameOutput, dirPathPart=os.path.join(current_directory,
                                                                                             "./temp_transfer/" + str(
                                                                                                 i) + "/"),
                                             fromNcycles=1, toNcycles=nautocyc, spaceGroup=spaceGroup, hkl=hkl, ent=ent,
                                             cell_dim=cell_dim,shlxLineaB=shlxLinea1 + addo,shlxLineaLast=shlxLineaLast,
                                             traceShelxe=True, fixed_frags=fixed_frags, USE_PACKING=USE_PACKING,
                                             USE_TRANSLA=USE_TRANSLA,USE_REFINEMENT=PERFORM_REFINEMENT_P1, nice=nice,
                                             NUMBER_REF_CYCLES=cycle_ref,USE_RGR=USE_RGR, isSHREDDER=isShredder,
                                             startExpAnomDic=startExpAnomDic, pattersonPeaks=pattersonPeaks,
                                             llgdic=llgdic, nBunchAutoTracCyc=nBunchAutoTracCyc)

                if failure_all:
                    print 'WARNING: In rotation cluster ',i,' all shelxe jobs failed to trace'

    try:
        if hasattr(cm, "channel"):
            # REMOVE THE FULL LIBRARY IN THE REMOTE SERVER
            actualdi = cm.get_remote_pwd()
            print cm.change_remote_dir("..")
            print cm.remove_remote_dir(model_directory, model_directory)
            print cm.change_remote_dir(actualdi)

        SystemUtility.close_connection(DicGridConn, DicParameters, cm)
    except:
        pass
    # new_t.stop()
    sym.couldIClose = True


#######################################################################################################
#                                               MAIN                                                  #
#######################################################################################################

def main():
    warnings.simplefilter("ignore", DeprecationWarning)
    # Put the signal retrieval for the killing
    if hasattr(sys, '_MEIPASS'):
        try:
            signal.signal(signal.SIGTERM,SystemUtility.signal_term_handler)
        except:
            pass
        try:
            signal.signal(signal.SIGKILL,SystemUtility.signal_term_handler)
        except:
            pass
        try:
            signal.signal(signal.SIGINT,SystemUtility.signal_term_handler)
        except:
            pass

    head1 = """
.-----------------------------------------------------------------------------------------------------------------------.
|          _____   _____ _____ __  __ ____   ____  _      _____   ____        ____   ____  _____   _____ ______  _____  |
|    /\   |  __ \ / ____|_   _|  \/  |  _ \ / __ \| |    |  __ \ / __ \      |  _ \ / __ \|  __ \ / ____|  ____|/ ____| |
|   /  \  | |__) | |      | | | \  / | |_) | |  | | |    | |  | | |  | |_____| |_) | |  | | |__) | |  __| |__  | (___   |
|  / /\ \ |  _  /| |      | | | |\/| |  _ <| |  | | |    | |  | | |  | |_____|  _ <| |  | |  _  /| | |_ |  __|  \___ \  |
| / ____ \| | \ \| |____ _| |_| |  | | |_) | |__| | |____| |__| | |__| |     | |_) | |__| | | \ \| |__| | |____ ____) | |
|/_/    \_\_|  \_\\\\_____|_____|_|  |_|____/ \____/|______|_____/ \____/      |____/ \____/|_|  \_\\\\_____|______|_____/  |
#-----------------------------------------------------------------------------------------------------------------------#
                                        Requires Phaser >= 2.8.x and Shelxe 2018
    """

    print colored(head1, 'cyan')
    print """
    Institut de Biologia Molecular de Barcelona --- Consejo Superior de Investigaciones Científicas
                     I.B.M.B.                                            C.S.I.C.

                    Department of Structural Biology - “María de Maeztu” Unit of Excellence
                                         Crystallographic Methods Group
                       http://www.sbu.csic.es/research-groups/crystallographic-methods/

    In case this result is helpful, please, cite:

    Phaser crystallographic software
    McCoy, A. J., Grosse-Kunstleve, R. W., Adams, P. D., Winn, M. D., Storoni, L. C. & Read, R. J.
    (2007) J Appl Cryst. 40, 658-674.

    Extending molecular-replacement solutions with SHELXE
    Thorn, A. & Sheldrick, G. M.
    (2013) Acta Cryst. D69, 2251-2256.

    Exploiting tertiary structure through local folds for ab initio phasing
    Sammito, M., Millán, C., Rodríguez, D. D., M. de Ilarduya, I., Meindl, K.,
    De Marino, I., Petrillo, G., Buey, R. M., de Pereda, J. M., Zeth, K., Sheldrick, G. M. & Usón, I.
    (2013) Nat Methods. 10, 1099-1101.
    """
    print "Email support: ", colored("bugs-borges@ibmb.csic.es", 'blue')
    print "\nARCIMBOLDO_BORGES website: ", colored("http://chango.ibmb.csic.es", 'blue')
    print "\n"
    usage = """usage: %prog [options] example.bor"""

    parser = OptionParser(usage=usage)
    # parser.add_option("-x", "--XGUI", action="store_true", dest="gui", help="Will automatically launch the GUI Option Viewer to read the output", default=False)
    parser.add_option("-v", "--devhelp", action="store_true", dest="devhelp",
                      help="Print customizable parameters for developers", default=False)
    parser.add_option("-b", "--borconf", action="store_true", dest="borconf",
                      help="Print customizable parameters for users", default=False)
    parser.add_option("-f", "--borfile", dest="borfile", help="Create a template .bor file", metavar="FILE")
    parser.add_option("-r", "--rottest", dest="rottest", help=SUPPRESS_HELP)

    (options, args) = parser.parse_args()

    if options.borfile != None:
        f = open(options.borfile, "w")
        text_file = """
#NOTE: for a full documentation of the parameters, please read the manual at: http://chango.ibmb.csic.es/manual
#NOTE: The values in the optional parameters are the default ARCIMBOLDO-SHREDDER values.
#A tutorial on how to run ARCIMBOLDO_BORGES can be found our website at: http://chango.ibmb.csic.es/tutorial

[CONNECTION]:
#NOTE: following is default
distribute_computing: multiprocessing
#NOTE: other modalities are:
#distribute_computing: local_grid
#setup_bor_path: /path/to/setup.bor
#NOTE: if the passkey is not found or invalid, a password is required
#distribute_computing: remote_grid
#setup_bor_path: /path/to/setup.bor
#remote_frontend_passkey: ~/.ssh/id_rsa

[GENERAL]:
#NOTE: following are mandatory
working_directory= /path/to/workdir
mtz_path: %(working_directory)s/data.mtz
hkl_path: %(working_directory)s/data.hkl
#NOTE: only if you want to use patterson correlation refinement for helical folds
#mtz_p1_path: %(working_directory)s/dataP1.mtz

[ARCIMBOLDO-BORGES]
#NOTE: following are mandatory
name_job: example_name
molecular_weight:
f_label: F
sigf_label: SIGF
#Or alternatively
#i_label: I
#sigi_label: SIGI
number_of_component: 1
library_path: /path/to/the/borges/library/
#NOTE: following are optional. -1 means PHASER defaults
#NOTE: the program automatically configure the shelxe_line but you can decomment it and use your own
#shelxe_line:
#NOTE: clusters can take all, or a list of cluster id eg.: 0,1,2
#clusters: all
#n_clusters: 4
#prioritize_phasers: False
#f_p1_label:
#sigf_p1_label:
#number_of_component_p1:
#rmsd: 0.2
#resolution_rotation: 1.0
#sampling_rotation: -1
#resolution_translation: 1.0
#sampling_translation: -1
#resolution_refinement: 1.0
#sampling_refinement: -1
#TNCS: True
#pack_clashes: 0
#NMA: False
#ROTATION_MODEL_REFINEMENT: BOTH

[LOCAL]
# Third party software paths
path_local_phaser: phenix.phaser
path_local_shelxe: shelxe
path_local_arcimboldo: ARCIMBOLDO_BORGES
path_local_phstat: phstat
"""
        f.write(text_file)
        f.close()
    if options.borconf:
        print
        print colored("""#""", 'blue') + colored('NOTE', 'yellow') + colored(
            """: for a full documentation of the parameters, please read the manual at: """, 'blue') + colored(
            """ http://chango.ibmb.csic.es/manual""", 'red')
        print

        print colored("""#""", 'blue') + colored('NOTE', 'yellow') + colored(
            """: The values in the optional parameters are the default ARCIMBOLDO-SHREDDER values.""", 'blue')
        print colored("""#Tutorial can be found in the website.""", 'blue')
        print """
[CONNECTION]:
"""
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(': following is default', 'blue'),
        print """
distribute_computing: multiprocessing
"""
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(': other modalities are:', 'blue'),
        print colored("""
#distribute_computing: local_grid
#setup_bor_path: /path/to/setup.bor

""", 'blue')
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
            ': if the passkey is not found or invalid, a password is required', 'blue'),
        print colored("""
#distribute_computing: remote_grid
#setup_bor_path: /path/to/setup.bor
#remote_frontend_passkey: ~/.ssh/id_rsa
""", 'blue'),
        print """
[GENERAL]:
"""
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(': following are mandatory', 'blue'),
        print """
working_directory= /path/to/workdir
mtz_path: %(working_directory)s/data.mtz
hkl_path: %(working_directory)s/data.hkl
"""
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
            ': only if you want to use patterson correlation refinement for helical folds', 'blue'),
        print colored("""
#mtz_p1_path: %(working_directory)s/dataP1.mtz
""", 'blue')
        print """
[ARCIMBOLDO-BORGES]
"""
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(': following are mandatory', 'blue'),
        print """
name_job: example_name
molecular_weight:
f_label: F
sigf_label: SIGF
#Or alternatively
#i_label: I
#sigi_label: SIGI
number_of_component: 1
library_path: /path/to/the/borges/library/
"""
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
            ': following are optional. -1 means PHASER defaults', 'blue'),

        print colored("""
#NOTE: the program automatically configure the shelxe_line but you can decomment it and use your own
#shelxe_line: """, 'blue')
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
            ': clusters can take all, or a list of cluster id eg.: 0,1,2', 'blue'),
        print colored("""
#clusters: all
#n_clusters: 4
#f_p1_label:
#sigf_p1_label:
#number_of_component_p1:
#rmsd: 0.2
#resolution_rotation: 1.0
#sampling_rotation: -1
#resolution_translation: 1.0
#sampling_translation: -1
#resolution_refinement: 1.0
#sampling_refinement: -1
#resolution_gyre: 1.0
#TNCS: True
#pack_clashes: 0
#NMA: False
#ROTATION_MODEL_REFINEMENT: BOTH
#OCC: False
""", 'blue'),
        print """
[LOCAL]""",
        print colored("""
# Third party software paths
# Requires PHASER 2.7.x""", 'blue'),
        print """
path_local_phaser: phenix.phaser
path_local_shelxe: shelxe
path_local_arcimboldo: ARCIMBOLDO_BORGES
path_local_phstat: phstat
"""
    if options.devhelp:
        print "The selected option is only available for the developers team. Please insert the password:"
        command = raw_input("<> ")
        if hashlib.sha224(command).hexdigest() == "d286f6ad6324a21cf46c7e3c955d8badfdbb4a14d630e8350ea3149e":
            print """

FULL LIST OF PARAMETERS FOR ARCIMBOLDO-BORGES:

[CONNECTION]:
distribute_computing: multiprocessing
#distribute_computing: local_grid
#distribute_computing: remote_grid
#remote_frontend_passkey: ~/.ssh/id_rsa
#setup_bor_path:

[GENERAL]
working_directory= /path/to/workdir
mtz_path: %(working_directory)s/data.mtz
hkl_path: %(working_directory)s/data.hkl
ent_path: %(working_directory)s/structure.ent
pdb_path: %(working_directory)s/structure.pdb
mtz_p1_path: %(working_directory)s/dataP1.mtz

[ARCIMBOLDO-BORGES]
name_job: example_name
molecular_weight:
f_label: F
sigf_label: SIGF
number_of_component: 1
library_path: /path/to/the/borges/library/
clusters: all
n_clusters: 4
prioritize_phasers: False
f_p1_label:
sigf_p1_label:
"""
            print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(': or alternatively use intensities',
                                                                                   'blue')
            print colored("""
#i_label: I
#sigi_label: SIGI
""", 'blue')
            print """
number_of_component_p1:
rmsd: 0.2
rotation_clustering_algorithm: rot_matrices
threshold_algorithm: 15
resolution_rotation: 1.0
sampling_rotation: -1
resolution_translation: 1.0
sampling_translation: -1
resolution_refinement: 1.0
resolution_gyre: 1.0
sampling_refinement: -1
exclude_llg: 0
exclude_zscore: 0
spacegroup:
use_packing: True
#NOTE: the program automatically configure the shelxe_line but you can decomment it and use your own
shelxe_line:
number_cycles_model_refinement: 3
TNCS: True
VRMS: False
VRMS_GYRE: False
fixed_model:
solution_sorting_scheme: AUTO
#solution_sorting_scheme: LLG
#solution_sorting_scheme: ZSCORE
#solution_sorting_scheme: INITCC
#solution_sorting_scheme: COMBINED
GIMBLE: False
# 0.35 Default Phaser
BULK_FSOL: -1
# 45 Default Phaser
BULK_BSOL: -1
BFAC: False
pack_clashes: 0
# NOTE: if Aniso is set to True, anisotropy and tncs correction will be recomputed in each phaser step
ANISO: False
nice: 0
NMA: False
#ROTATION_MODEL_REFINEMENT: NO_GYRE
#ROTATION_MODEL_REFINEMENT: BOTH
#ROTATION_MODEL_REFINEMENT: GYRE
SIGR: 0.0
SIGT: 0.0
PACK_TRA: False
BASE_SUM_FROM_WD: True
alixe_mode: one_step
GYRE_PRESERVE_CHAINS: False
NMA_P1: False
OCC: False
prioritize_occ: True
OMIT_vs_LLG: False
sampling_gyre: -1
applyTopNameFilter: True
noDMinitcc: True
phs_fom_statistics: False
savePHS: False
archivingAsBigFile: False
filter_clusters_after_rot: True
extend_with_random_atoms: False
extend_with_secondary_structure: False
parameters_elongation: 4.8 60 150
#parameters_elongation: 5 150 1
topFRF: 200
topFTF: 70
topPACK: -1
topRNP: 200
topExp: 40
force_core: -1
force_nsol: -1
force_exp: False
coiled_coil: False

[LOCAL]
# Third party software paths
# Requires PHASER 2.7.x
path_local_phaser: phenix.phaser
path_local_shelxe: shelxe
path_local_arcimboldo: ARCIMBOLDO_BORGES
path_local_phstat: phstat
"""
            sys.exit(0)
        else:
            print "Sorry. You have not the permissions."
            sys.exit(0)

    if options.rottest is not None and options.rottest != "" and os.path.exists(options.rottest):
        startROT_NODE(options.rottest)
    else:
        if len(args) < 1:
            parser.print_help()
            sys.exit(0)

    model_directory = ""
    if len(args) < 1:
        parser.print_help()
        sys.exit(0)

    input_bor = os.path.abspath(args[0])
    print '\n Reading the bor configuration file for ARCIMBOLDO_BORGES at ', input_bor
    if not os.path.exists(input_bor):
        print 'Sorry, the given path for the bor file either does not exist or you do not have the permissions to read it'
        sys.exit(1)
    path_module = os.path.dirname(__file__)

    Config = ConfigParser.ConfigParser()
    #Config.readfp(cStringIO.StringIO(Data.defaults_bor))
    #Config.read(input_bor)

    try:
        startARCIMBOLDO_BORGES(Config, False, input_bor, startCheckQueue=True)
    except SystemExit:
        pass
    except:
        print traceback.print_exc(file=sys.stdout)
        if hasattr(sys, '_MEIPASS'):
            print "Exited with errors, temp file was ", sys._MEIPASS, " and was removed before exiting"

if __name__ == "__main__":
    main()

