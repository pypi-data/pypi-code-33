#! /usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import cStringIO
import copy
import datetime
import getpass
import hashlib
import json
import os
import re
import shutil
import signal
import sys
import threading
import subprocess
import traceback
import warnings
import xml.etree.ElementTree as ET
from optparse import OptionParser
import glob

from termcolor import colored
from Bio.PDB import PDBExceptions

import ADT
import alixe_library as al
import arci_output
import Bioinformatics
import Data
import Grid
import Quaternions
import SELSLIB2
#import LOWLIB
import SystemUtility
import ANOMLIB

warnings.simplefilter("ignore", PDBExceptions.PDBConstructionWarning)


#######################################################################################################
#                                            FUNCTIONS                                                #
#######################################################################################################

def startARCIMBOLDO(BorData, input_bor, DicParameters={}, DicGridConn={}, cm=None, sym=None, doTest=True, mtz_given="",
                    F_given="", SIGF_given="", normfactors="", tncsfactors="", Intensities=False, Aniso=True, nice=0,
                    out_phaser_given="", fneed=False, startCheckQueue=False,modelLowName="None",isShredder=False):

    try:
        Config_1 = ConfigParser.ConfigParser()
        Config_1.read(input_bor)
        coiled_coil = Config_1.getboolean("ARCIMBOLDO", "coiled_coil")
        Config_1 = None
    except:
        coiled_coil = False

    if coiled_coil:
        print '\nChanging defaults for Coiled Coil mode'
        PACK_TRA = True
        Data.defaults_bor = Data.defaults_bor.replace("PACK_TRA: False","PACK_TRA: True")
        USE_TNCS = False
        Data.defaults_bor = Data.defaults_bor.replace("TNCS: True","TNCS: False")
        VRMS = True
        Data.defaults_bor = Data.defaults_bor.replace("VRMS: False","VRMS: True")


    if not isShredder:
        BorData.readfp(cStringIO.StringIO(Data.defaults_bor))
        BorData.read(input_bor)

    model_directory = ""
    toExit = False
    helix_list = []
    helix_inverted = []
    list_length = []
    model_file = ""

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
    distribute_computing = ""

    #NS keeping the sh and sol after evaluateftf
    cleanshsol=True
    ANOMALOUS=False
    llgdic=None   #We need it later in shelxe_cycles

    try:
        distribute_computing = Config.get("CONNECTION", "distribute_computing").strip().lower()
        if distribute_computing in ["multiprocessing", "supercomputer"]:
            SELSLIB2.PATH_NEW_PHASER = Config.get("LOCAL", "path_local_phaser")
            SELSLIB2.PATH_NEW_SHELXE = Config.get("LOCAL", "path_local_shelxe")
            # SELSLIB2.PATH_NEW_ARCIFIRE = Config.get("LOCAL","path_local_arcimboldo_fire")
        NSEARCH = int(Config.getfloat("ARCIMBOLDO", "fragment_to_search"))
        if NSEARCH > 15:
            print colored("WARNING", "red"), "Searching for more than 15 fragments is not supported in ARCIMBOLDO_LITE"
            toExit = True
            raise Exception
        try:
            if NSEARCH == 1:
                helix_length = Config.getint("ARCIMBOLDO", "helix_length")
                list_length.append(helix_length)
            else:
                try:
                    helix_length = Config.getint("ARCIMBOLDO", "helix_length")
                    for t in range(NSEARCH):
                        list_length.append(helix_length)
                except:
                    try:
                        for t in range(NSEARCH):
                            helix_length = Config.getint("ARCIMBOLDO", "helix_length_" + str(t + 1))
                            list_length.append(helix_length)
                    except:
                        print "Please, specify the common helix_length or the particular length for each helix"
                        raise Exception

            list_length = sorted(list_length, reverse=True)
            helix_list = Bioinformatics.getIdealHelicesFromLenghts(list_length, Data.th70pdb)
            helix_inverted = Bioinformatics.getIdealHelicesFromLenghts(list_length,Data.th70pdb_inverted, reversed=True)

        except:
            #print traceback.print_exc(file=sys.stdout)
            if NSEARCH == 1:
                model_file = Config.get("ARCIMBOLDO", "model_file")
                if not os.path.exists(model_file):
                    if model_file.lower() == "fe2s2":
                        helix_list = [[Data.Fe2S2, {}]]
                    elif model_file.lower() == "fe2s4":
                        helix_list = [[Data.Fe2S4, {}]]
                    elif model_file.lower() == "heme":
                        helix_list = [[Data.heme, {}]]
                    else:
                        print colored("FATAL", "red"), "The model pdb file: " + str(os.path.abspath(
                            model_file)) + " does not exist or it is not user readable: ", getpass.getuser()
                        toExit = True
                else:
                    try:
                        stry = Bioinformatics.getStructure("test", model_file)
                        if len(stry.get_list()) <= 0:
                            raise Exception
                    except:
                        print colored("FATAL", "red"), "The input pdb model file " + str(os.path.abspath(
                            model_file)) + " is not a standard pdb file and cannot be correctly interpreted"
                        toExit = True
                    helix_list.append([model_file, {}])
            else:
                try:
                    model_file = Config.get("ARCIMBOLDO", "model_file")
                    if not os.path.exists(model_file):
                        if model_file.lower() == "fe2s2":
                            helix_list = []
                            for t in range(NSEARCH):
                                helix_list.append([Data.Fe2S2, {}])
                        elif model_file.lower() == "fe2s4":
                            helix_list = []
                            for t in range(NSEARCH):
                                helix_list.append([Data.Fe2S4, {}])
                        elif model_file.lower() == "heme":
                            helix_list = []
                            for t in range(NSEARCH):
                                helix_list.append([Data.heme, {}])
                        else:
                            print colored("FATAL", "red"), "The input pdb model file: " + str(os.path.abspath(
                                model_file)) + " does not exist or it is not user readable: ", getpass.getuser()
                            toExit = True
                    else:
                        try:
                            stry = Bioinformatics.getStructure("test", model_file)
                            if len(stry.get_list()) <= 0:
                                raise Exception
                        except:
                            print colored("FATAL", "red"), "The input pdb model file " + str(os.path.abspath(
                                model_file)) + " is not a standard pdb file and cannot be correctly interpreted"
                            toExit = True

                        for t in range(NSEARCH):
                            helix_list.append([model_file, {}])
                except:
                    try:
                        helix_list = []
                        for t in range(NSEARCH):
                            helim = Config.get("ARCIMBOLDO", "model_file_" + str(t + 1))
                            if not os.path.exists(helim):
                                if helim.lower() == "fe2s2":
                                    helix_list.append([Data.Fe2S2, {}])
                                elif helim.lower() == "fe2s4":
                                    helix_list.append([Data.Fe2S4, {}])
                                elif helim.lower() == "heme":
                                    helix_list.append([Data.heme, {}])
                                else:
                                    print colored("FATAL", "red"), "The input pdb model file: " + str(os.path.abspath(
                                        model_file)) + " does not exist or it is not user readable: ", getpass.getuser()
                                    toExit = True
                            else:
                                try:
                                    stry = Bioinformatics.getStructure("test_" + str(t), helim)
                                    if len(stry.get_list()) <= 0:
                                        raise Exception
                                    helix_list.append([helim, {}])
                                except:
                                    print colored("FATAL", "red"), "The input pdb model file " + str(os.path.abspath(
                                        helim)) + " is not a standard pdb file and cannot be correctly interpreted"
                                    toExit = True
                    except:
                        print "Specify a common model or a particular model for each fragment"
                        toExit = True

        mtz = Config.get("GENERAL", "mtz_path")
        hkl = Config.get("GENERAL", "hkl_path")
        ent = Config.get("GENERAL", "ent_path")
        mtz = os.path.abspath(mtz)
        hkl = os.path.abspath(hkl)


        pdbcl = Config.get("GENERAL", "pdb_path")
        if ent != None and ent.endswith(".ent"):
            ent = os.path.abspath(ent)
        else:
            ent = ""

        if pdbcl != None and pdbcl.endswith(".pdb"):
            pdbcl = os.path.abspath(pdbcl)
        else:
            pdbcl = ""

        model_file = os.path.abspath(model_file)

        try:
            sequence = Config.get("ARCIMBOLDO", "sequence")
            for lett in sequence:
                if lett not in Bioinformatics.AALISTOL:
                    print "Sequence is not valid, symbol", lett, "not recognized"
                    toExit = True
                    sys.exit(0)
            MW = float(len(lett) * 100)
        except:
            MW = Config.getfloat("ARCIMBOLDO", "molecular_weight")
        try:
            NC = Config.getint("ARCIMBOLDO", "number_of_component")   
        except:
            NC=-1    #NS: Now NC== -1 means automatic mode, will also be launched if it is equal to zero
        try:
            F = Config.get("ARCIMBOLDO", "f_label")
            SIGF = Config.get("ARCIMBOLDO", "sigf_label")
            Intensities = False
        except:
            F = Config.get("ARCIMBOLDO", "i_label")
            SIGF = Config.get("ARCIMBOLDO", "sigi_label")
            Intensities = True

        nice = Config.getint("ARCIMBOLDO", "nice")
        RMSD = Config.getfloat("ARCIMBOLDO", "rmsd")
    except:
        print "Mandatory tags are missing:"
        print traceback.print_exc(file=sys.stdout)
        toExit = True

    if toExit:
        return


    # Check whether to perform or not the anisotropy and tncs corrections in every step
    Aniso = Config.getboolean("ARCIMBOLDO", "ANISO")


    # NOTE CM: Testing for microED data
    formfactors = Config.get("ARCIMBOLDO", "formfactors")
    # NOTE CM: Testing for microED data

    # SET OUTPUT PARAMETERS
    current_directory = Config.get("GENERAL", "working_directory")

    #NS ANOM: parsing the anomalous parameters
    ANOMDIR=os.path.join(current_directory,"ANOMFILES")         #just a name for the moment, the directory is not created yet
    startExpAnomDic, otherAnomParamDic, fragAnom =ANOMLIB.parseAnomalousParameters(configParserObject=Config, ANOMDIR=ANOMDIR)
    ANOMALOUS= True if fragAnom else False                      # A master switch for Anomalous parameters

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
        nameJob = Config.get("ARCIMBOLDO", "name_job")
        nameJob = "_".join(nameJob.split())
        if len(nameJob.strip()) == 0:
            print '\nKeyword name_job is empty, setting a default name for the job...'
            nameJob = (os.path.basename(mtz))[:-4] + '_arcimboldo_lite'
        DicParameters["nameExecution"] = nameJob
    except:
        print "Mandatory tags are missing:"
        print traceback.print_exc(file=sys.stdout)
        sys.exit(1)

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
            SELSLIB2.GRID_TYPE_R = setupbor.get("GRID", "type_remote")
            if SELSLIB2.GRID_TYPE_R == "Condor":
                SELSLIB2.SHELXE_REQUIREMENTS = setupbor.get("CONDOR", "requirements_shelxe")
                SELSLIB2.PHASER_REQUIREMENTS = setupbor.get("CONDOR", "requirements_phaser")
                SELSLIB2.BORGES_REQUIREMENTS = setupbor.get("CONDOR", "requirements_borges")
            SELSLIB2.LOCAL = False
        except:
            print colored("ATTENTION: Some keywords in the configuration file are missing. Contact your administrator",
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

    # SETTING
    clusteringAlg = Config.get("ARCIMBOLDO", "rotation_clustering_algorithm")
    excludeLLG = Config.getfloat("ARCIMBOLDO", "exclude_llg")
    excludeZscore = Config.getfloat("ARCIMBOLDO", "exclude_zscore")
    excludeZscoreRNP = Config.getfloat("ARCIMBOLDO", "exclude_zscoreRNP")  #NS: to put a cutoff on TFZ== after RNP step
    thresholdCompare = Config.getfloat("ARCIMBOLDO", "threshold_algorithm")
    USE_PACKING = Config.getboolean("ARCIMBOLDO", "use_packing")
    res_rot = Config.getfloat("ARCIMBOLDO", "resolution_rotation")
    sampl_rot = Config.getfloat("ARCIMBOLDO", "sampling_rotation")
    res_tran = Config.getfloat("ARCIMBOLDO", "resolution_translation")
    sampl_tran = Config.getfloat("ARCIMBOLDO", "sampling_translation")
    res_refin = Config.getfloat("ARCIMBOLDO", "resolution_refinement")
    sampl_refin = Config.getfloat("ARCIMBOLDO", "sampling_refinement")
    POST_MORTEM = Config.getboolean("ARCIMBOLDO", "post_mortem")
    if Config.has_option("ARCIMBOLDO", "swap_model_after_translation"):
        swap_model = Config.get("ARCIMBOLDO", "swap_model_after_translation")
    else:
        swap_model = None

    USE_TRANSLA = True

    VRMS = Config.getboolean("ARCIMBOLDO", "VRMS")
    VRMS_GYRE = Config.getboolean("ARCIMBOLDO", "VRMS_GYRE")
    UPDATE_RMSD = Config.getboolean("ARCIMBOLDO", "update_rmsd")
    UPDATE_RMSD_FIXED = Config.getboolean("ARCIMBOLDO", "update_rmsd_fixed")
    BFAC = Config.getboolean("ARCIMBOLDO", "BFAC")
    CLASHES = Config.getint("ARCIMBOLDO", "pack_clashes")
    noDMinitcc = Config.getboolean("ARCIMBOLDO", "noDMinitcc")
    USE_OCC = Config.getboolean("ARCIMBOLDO", "OCC")
    usePDO = Config.getboolean("ARCIMBOLDO", "usePDO")
    BULK_FSOL = Config.getfloat("ARCIMBOLDO", "BULK_FSOL")
    BULK_BSOL = Config.getfloat("ARCIMBOLDO", "BULK_BSOL")
    RNP_GYRE = Config.getboolean("ARCIMBOLDO", "GIMBLE")
    BASE_SUM_FROM_WD = Config.getboolean("ARCIMBOLDO", "BASE_SUM_FROM_WD")
    SELSLIB2.BASE_SUM_FROM_WD = BASE_SUM_FROM_WD
    solution_sorting_scheme = Config.get("ARCIMBOLDO", "solution_sorting_scheme").upper()
    savePHS = Config.getboolean("ARCIMBOLDO", "savePHS")
    ellg_target = Config.getfloat("ARCIMBOLDO", "ellg_target")
    archivingAsBigFile = Config.getboolean("ARCIMBOLDO", "archivingAsBigFile")
    phs_fom_statistics = Config.getboolean("ARCIMBOLDO", "phs_fom_statistics")
    fixed_models_directory = Config.get("ARCIMBOLDO", "fixed_models_directory")
    randomize_trans_per_rot = Config.getint("ARCIMBOLDO", "randomize_trans_per_rot")
    randomize_translations = True if randomize_trans_per_rot > 0 else False
    range_rmsd_tra = Config.getfloat("ARCIMBOLDO", "range_rmsd_tra")
    range_rmsd = True if range_rmsd_tra > 0 else False

    solution_verification = Config.getboolean("ARCIMBOLDO","solution_verification")
    # TODO: decide which parameters we allow to overwrite and which not
    PACK_TRA = Config.getboolean("ARCIMBOLDO", "PACK_TRA")
    USE_TNCS = Config.getboolean("ARCIMBOLDO", "TNCS")
    search_inverted_helix = Config.getboolean("ARCIMBOLDO", "search_inverted_helix")
    search_inverted_helix_from_fragment = Config.getint("ARCIMBOLDO", "search_inverted_helix_from_fragment")
    top_inverted_solution_per_cluster = Config.getint("ARCIMBOLDO", "top_inverted_solution_per_cluster")
    #NS : I need sometimes to use more autotracing cycles in the end
    nAutoTracCyc = Config.getint("ARCIMBOLDO",'nAutoTracCyc')

    #NS: change the number of autotracing cycles per bunch (number of bunches defined by nAutoTracCyc, default:1)
    nBunchAutoTracCyc=Config.getint("ARCIMBOLDO",'nBunchAutoTracCyc')

    #####NS LOW : Options
    ArcimboldoLOW = Config.getboolean("ARCIMBOLDO", "ArcimboldoLOW")
    phased_TF= Config.getint("ARCIMBOLDO", "phased_TF")  #NS ADD : 0 for False, otherwise it indicates the fragment number from which phases from previous fixed fragments are used
    #NOTE: Phased_TF cannot be 1 since there is no fragment from cycle zero, so if the user puts 1: turn it back into 0.
    use_protocols=Config.getint("ARCIMBOLDO","use_protocols")  #NS: for fragment i (integer given) try different protocols before passing to the next fragment, i.e until something works

    transformPDB=Config.get("ARCIMBOLDO","transformPDB")  #NS ADD make your input model poly-alanine, poly-serine, pseudo serine, aromatics only
    solventContent=Config.getfloat("ARCIMBOLDO","solventContent") #Solvent content to use in the shelxe DM calculations --> now taken from unitcell content analysis result following the number of mol/asu
    unitCellcontentAnalysis=Config.getboolean("ARCIMBOLDO","unitCellcontentAnalysis")
    tncsVector=Config.get("ARCIMBOLDO","tncsVector")
    tncsVector=tncsVector.split('_')  #tNCS vector if any, coordinates separated by UNDERSCORE (default 0_0_0 will be provided as an array to SELSLIB2.anisotropyCorrection_and_test)
    tncsVector=[float(x) for x in tncsVector]  #transform the tncs vector in array of coordinates
    TopFilesRNP=0 #NS To output only n solutions after rigid body refinement (if>0 avoid getting too many junk solutions for low res mode)
    cycleNExcludeZscoreRNP=Config.getint("ARCIMBOLDO", "cycleNExcludeZscoreRNP")  #apply the excludeZscoreRNP cutoff from this cycle number
    #####END NS LOW : Options


    skipResLimit = False

    try:
        skipResLimit = Config.getboolean("ARCIMBOLDO", "SKIP_RES_LIMIT")
    except:
        pass

    useFIXED = False
    if os.path.exists(fixed_models_directory) and os.path.isdir(fixed_models_directory):
        saw = 0
        for root, subFolders, files in os.walk(fixed_models_directory):
            for fileu in files:
                pdbf = os.path.join(root, fileu)
                if pdbf.endswith(".pdb"):
                    stry = Bioinformatics.getStructure("test_" + str(saw), pdbf)
                    if len(stry.get_list()) <= 0:
                        print colored("FATAL", "red"), "The model pdb file: " + str(
                            os.path.abspath(pdbf)) + " is not a standard PDB file."
                        sys.exit(1)
                    saw = + 1

        path_rot = os.path.join(current_directory, "./ens1_frag1/1_FRF_LIBRARY/")
        SELSLIB2.generateFakeMRSum(fixed_models_directory, "ROT", False, path_rot, "clusters", arcimboldo=True)
        path_tra = os.path.join(current_directory, "./ens1_frag1/3_FTF_LIBRARY/")
        SELSLIB2.generateFakeMRSum(fixed_models_directory, "TRA", False, path_tra, "clusters", arcimboldo=True)
        path_pack = os.path.join(current_directory, "./ens1_frag1/4_PACK_LIBRARY/")
        SELSLIB2.generateFakeMRSum(fixed_models_directory, "TRA", False, path_pack, "clusters", arcimboldo=True)
        path_rnp = os.path.join(current_directory, "./ens1_frag1/5_RNP_LIBRARY/")
        if not os.path.exists(os.path.join(path_rnp, "0")):
            shutil.copytree(fixed_models_directory, os.path.join(path_rnp, "0"))
        SELSLIB2.generateFakeMRSum(fixed_models_directory, "TRA", False, path_rnp, "clusters", arcimboldo=True)
        useFIXED = True

    topFRF_1 = Config.getint("ARCIMBOLDO", "topFRF_1")
    if topFRF_1 <= 0:
        topFRF_1 = None
    topFTF_1 = Config.getint("ARCIMBOLDO", "topFTF_1")
    if topFTF_1 <= 0:
        topFTF_1 = None
    topPACK_1 = Config.getint("ARCIMBOLDO", "topPACK_1")
    if topPACK_1 <= 0:
        topPACK_1 = None
    topRNP_1 = Config.getint("ARCIMBOLDO", "topRNP_1")
    if topRNP_1 <= 0:
        topRNP_1 = None
    topExp_1 = Config.getint("ARCIMBOLDO", "topExp_1") - 1
    if topExp_1 <= 0:
        topExp_1 = None

    topFRF_n = Config.getint("ARCIMBOLDO", "topFRF_n")
    if topFRF_n <= 0:
        topFRF_n = None
    topFTF_n = Config.getint("ARCIMBOLDO", "topFTF_n")
    if topFTF_n <= 0:
        topFTF_n = None
    topPACK_n = Config.getint("ARCIMBOLDO", "topPACK_n")
    if topPACK_n <= 0:
        topPACK_n = None
    topRNP_n = Config.getint("ARCIMBOLDO", "topRNP_n")
    if topRNP_n <= 0:
        topRNP_n = None
    topExp_n = Config.getint("ARCIMBOLDO", "topExp_n") - 1
    if topExp_n <= 0:
        topExp_n = None
    force_core = Config.getint("ARCIMBOLDO", "force_core")
    if force_core <= 0:
        force_core = None
    force_exp = Config.getboolean("ARCIMBOLDO", "force_exp")

    fixed_frags = 1
    evaLLONG = False  # It just works with helices and distributionCV better not use it for now
    RECOVER = True

    # PREPARING OR ADDING A NCS Matrix
    ncs = json.loads(Config.get("ARCIMBOLDO", "RNCS_MATL"))

    # STARTING THE GRID MANAGER
    GRID_TYPE = ""
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
        linsh = Config.get("ARCIMBOLDO", "shelxe_line")
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
        anismtz, normfactors, tncsfactors, F, SIGF, spaceGroup, cell_dim, resolution, unique_refl, aniout, anierr,\
        fneed, shelxe_new, tNCS_bool = SELSLIB2.anisotropyCorrection_and_test(cm=cm, sym=sym, DicGridConn=DicGridConn,
                                                                              DicParameters=DicParameters,
                                                                              current_dir=current_directory, mtz=mtz,
                                                                              F=F, SIGF=SIGF, Intensities=Intensities,
                                                                              Aniso=Aniso, formfactors=formfactors,
                                                                              nice=nice,pda=Data.th70pdb, hkl=hkl,
                                                                              ent=ent, shelxe_line=shlxLinea0, tncsVector=[0,0,0])
    else:
        mtz = mtz_given
        F = F_given
        SIGF = SIGF_given
        # READING THE SPACEGROUP FROM PHASER OUT
        spaceGroup = SELSLIB2.readSpaceGroupFromOut(out_phaser_given)

        # READING THE CELL DIMENSIONS FROM PHASER OUT
        cell_dim = SELSLIB2.cellDimensionFromOut(out_phaser_given)

        # READING THE RESOLUTION FROM PHASER OUT
        resolution = SELSLIB2.resolutionFromOut(out_phaser_given)

        # READING THE NUMBER OF UNIQUE REFLECTIONS FROM PHASER OUT
        unique_refl = SELSLIB2.uniqueReflectionsFromOut(out_phaser_given)


    if resolution > 2.0 and coiled_coil:
        search_inverted_helix = True
        Config.set("ARCIMBOLDO", "search_inverted_helix", "True")
        solution_verification = True
        Config.set("ARCIMBOLDO", "solution_verification", "True")


    sg = Config.get("ARCIMBOLDO", "spacegroup")
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
        sys.exit(1)
    else:
        print '\n Input space group has been correctly processed'
        # Perform specific actions depending on space group
        if sg_number == 1:
            print '\n Space group is P1 '
            if not tNCS_bool:  # If no tNCS has been found
                print '\n Data does not appear to have tNCS, setting tncs keyword to false'
                USE_TNCS = False
    sg_symbol = dictio_space_groups[sg_number]['symbol']
    spaceGroup = sg_symbol

    # SHELXE LINES
    try:
        linsh = Config.get("ARCIMBOLDO", "shelxe_line")
        try:
            linsh_last = Config.get("ARCIMBOLDO", "shelxe_line_last")
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
        # TODO: change the default line depending on shelxe version
        if resolution <= 1.0:
            linsh = "-m200 -a8 -s0.25 -v0.5 -t10 -q -y" + str('%.2f' % (resolution))
            linsh_last = "-m200 -a1 -s0.2 -v0.5 -t10 -q -y" + str('%.2f' % (resolution))+ " -e1.0"
            if shelxe_new and coiled_coil:
                linsh = "-m200 -a8 -s0.25 -v0.5 -t10 -Q -I200 -y" + str('%.2f' % (resolution)) + " -e1.0"
                linsh_last = "-m200 -a1 -s0.2 -v0.5 -t10 -q -I200 -y" + str('%.2f' % (resolution)) + " -e1.0"
        elif resolution <= 1.3:  # and resolution > 1.0:
            linsh = "-m100 -a8 -s0.35 -v0.25 -t10 -q -y" + str('%.2f' % (resolution))
            linsh_last = "-m100 -a1 -s0.3 -v0.25 -t10 -q -y" + str('%.2f' % (resolution))+ " -e1.0"
            if shelxe_new and coiled_coil:
                linsh = "-m100 -a8 -s0.35 -v0.5 -t10 -Q -I100 -y" + str('%.2f' % (resolution)) + " -e1.0"
                linsh_last = "-m100 -a1 -s0.3 -v0.25 -t10 -q -I100 -y" + str('%.2f' % (resolution)) + " -e1.0"
        elif resolution <= 1.5:  # and resolution > 1.3:
            linsh = "-m50 -a8 -s0.45 -v0.1 -t10 -q -y" + str('%.2f' % (resolution))
            linsh_last = "-m50 -a1 -s0.4 -v0.1 -t10 -q -y" + str('%.2f' % (resolution))+ " -e" + \
                        str('%.2f' % (resolution-0.5))
            if shelxe_new and coiled_coil:
                linsh = "-m50 -a8 -s0.45 -v0.1 -t10 -Q -I50 -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution-0.3))
                linsh_last = "-m50 -a1 -s0.4 -v0.1 -t10 -q -I50 -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution-0.5))
        elif resolution <= 2.0:  # and resolution > 1.5:
            linsh = "-m15 -a8 -s0.5 -v0 -t10 -q -y" + str('%.2f' % (resolution))
            linsh_last = "-m15 -a1 -s0.45 -v0 -t10 -q -y" + str('%.2f' % (resolution))+ " -e" + \
                        str('%.2f' % (resolution-0.5))
            if shelxe_new and coiled_coil:
                linsh = "-m15 -a8 -s0.5 -v0 -t10 -Q -I15 -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution-0.3))
                linsh_last = "-m15 -a1 -s0.45 -v0 -t10 -q -I15 -y" + str('%.2f' % (resolution)) + " -e" + \
                             str('%.2f' % (resolution - 0.5))
        else:  # resolution > 2.0:
            linsh = "-m10 -a8 -s0.6 -v0 -t10 -q -y" + str('%.2f' % (resolution))
            linsh_last = "-m10 -a1 -s0.55 -v0 -t10 -q -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution-0.5))
            if shelxe_new and coiled_coil and resolution <= 2.5:
                linsh = "-m10 -a8 -s0.6 -v0 -t10 -Q -I10 -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution - 0.3))
                linsh_last = "-m10 -a1 -s0.55 -v0 -t10 -q -I10 -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution - 0.5))
            elif shelxe_new and coiled_coil and resolution <= 3.0:
                linsh = "-m5 -a8 -s0.6 -v0 -t10 -Q -I5 -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution - 0.3))
                linsh_last = "-m5 -a1 -s0.55 -v0 -t10 -q -I5 -y" + str('%.2f' % (resolution)) + " -e" + \
                        str('%.2f' % (resolution - 0.5))
        if fneed:
            linsh += " -f"
            linsh_last += " -f"

    # WRITE the correct line to the config so that the html shows it correctly
    Config.set("ARCIMBOLDO", "shelxe_line", linsh)
    Config.set("ARCIMBOLDO", "shelxe_line_last", linsh_last)
    
    listash = linsh.split()
    nautocyc = 0
    listash1 = linsh.split()
    listash2 = []
    dfound = False
    yfound = False
    for toc in range(len(listash)):
        param = listash[toc]
        if param.startswith("-a"):
            nautocyc = int(param[2:]) + 1
            param = "-a0"
            nk = 0
            for prr in listash:
                if prr.startswith("-K"):
                    nk = int(prr[2:])
                    #print 'nk is ',nk
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
        if param.startswith("-d"):
            nd = float(param[2:])
            param = "-d1.0"
            if toc + 1 < len(listash) and not listash[toc + 1].startswith("-"):
                listash[toc + 1] = ""
                listash1[toc + 1] = ""
            listash[toc] = param
            dfound = True
        if param.startswith("-y"):
            ny = float(param[2:])
            param = "-y1.0"
            if toc + 1 < len(listash) and not listash[toc + 1].startswith("-"):
                listash[toc + 1] = ""
            listash[toc] = param
            yfound = True
    if not skipResLimit: #NS: I don't want these options at low resolution
        if not dfound:
            listash.append("-d1.0")
        if not yfound:
            listash.append("-y1.0")

    if noDMinitcc and nautocyc > 1:
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
        lisyash2 = copy.deepcopy(listash)
        listash2.append("-x1")
        listash.append("-x")
        listash1.append("-x")
        linsh_last = linsh_last + ' -x '

    linsh = " ".join(listash)
    shlxLinea0 = linsh
    linsh2 = " ".join(listash2)
    shlxLineaP = linsh2
    shlxLinea1 = " ".join(listash1)
    shlxLineaLast = linsh_last


    inputDir = os.path.join(current_directory, DicParameters["nameExecution"] + "_ensembles/")
    ensemblesDir = os.path.join(current_directory, DicParameters["nameExecution"] + "_ensembles/")

    if not (os.path.exists(inputDir)):
        os.makedirs(inputDir)
    else:
        shutil.rmtree(inputDir)
        os.makedirs(inputDir)


    ###NICO
    if (ArcimboldoLOW and phased_TF and Intensities):
        #amplitudes are added to the mtz file (which is a path to mtz here), which contained only intensities
        mtz=LOWLIB.computeFfromI(current_directory=current_directory,mtzIn=mtz)

    #NS ANOM checks and update the required files for experimental phasing and generates the hkl_fa and ins_fa files with SHELXC file if they don't exist
    if ANOMALOUS:
        startExpAnomDic=ANOMLIB.updateAnomParamDic(hkl=hkl, mtz=mtz, current_directory=current_directory, otherAnomParamDic=otherAnomParamDic, cell_dim=cell_dim, sg_number=sg_number, startExpAnomDic=startExpAnomDic)
        solutions_filtered_out={}    #will contain the names of all the solutions to remove after evaluateExp or evaluateExp_cc functions
        convNamesAnom={}
        savePHS=True
        filterLiteFromFragNumber=otherAnomParamDic['filterLiteFromFragNumber']

        #It seems reasonnable to start filtering solution from the expCC calculation of the last fragment placed
        if filterLiteFromFragNumber == 1:
            filterLiteFromFragNumber=NSEARCH

        if not startExpAnomDic:
            print("Error, something went wrong when trying to update the anomalous parameters, quitting now")
            sys.exit(1)
    ######## end of anomalous files treatment

    if len(helix_list) == 0: # There is only one model file
        shutil.copyfile(model_file, os.path.join(inputDir, os.path.basename("th" + str(1) + "_0_0.pdb")))
        model_file = os.path.join(inputDir, os.path.basename("th" + str(1) + "_0_0.pdb"))

    elif len(list_length) > 0: # There are ideal helices
        model_file = os.path.join(inputDir, os.path.basename("th" + str(list_length[0]) + "_0_0.pdb"))
        mf = open(model_file, "w")
        mf.write(helix_list[0][0])
        mf.close()

    else: # There are model files
        # NOTE: we need to differenciate between heme and model files
        if not os.path.exists(helix_list[0][0]): # then it is an internal group
            model_file = os.path.join(inputDir, os.path.basename("th" + str(1) + "_0_0.pdb"))
            mf = open(model_file, "w")
            mf.write(helix_list[0][0])
            mf.close()
        else:
            model_file = os.path.join(inputDir, os.path.basename("th" + str(1) + "_0_0.pdb"))
            shutil.copyfile(helix_list[0][0], os.path.join(inputDir, os.path.basename("th" + str(1) + "_0_0.pdb")))


    if len(helix_inverted) > 0 and search_inverted_helix:
        model_file_inverted = os.path.join(inputDir, os.path.basename("thinverted" + str(list_length[0]) + "_0_0.pdb"))
        mf = open(model_file_inverted, "w")
        mf.write(helix_inverted[0][0])
        mf.close()

    nameModel = os.path.join(inputDir, os.path.basename(model_file))

    ensembles_mode = False
    with open(nameModel, "r") as cf:
        alli = cf.read()
        ensembles_mode = alli.count("MODEL") > 1

    print("=========MODEL FILE===============")
    print("        "+nameModel+"             ")
    print("    MULTIPLE ENSEMBLES:  "+str(ensembles_mode))
    print("==================================")

    SystemUtility.open_connection(DicGridConn, DicParameters, cm)
    if hasattr(cm, "channel"):
        # Copy the required files in the remove server
        actualdi = cm.get_remote_pwd()
        print cm.change_remote_dir("..")
        print cm.copy_directory(inputDir, inputDir)
        print cm.change_remote_dir(os.path.basename(os.path.normpath(inputDir)))
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

        print cm.change_remote_dir(actualdi)

    Config.remove_section("ARCIMBOLDO-BORGES")
    Config.remove_section("ARCIMBOLDO-SHREDDER")


    allborf = cStringIO.StringIO()
    Config.write(allborf)
    allborf.flush()
    allborf.seek(0)
    allbor = allborf.read()
    allborf.close()

    # RETRIEVING THE LAUE SIMMETRY FROM THE SPACEGROUP
    laue = quate.getLaueSimmetry(spaceGroup)
    if laue == None:
        print 'Some problem happened during retrieval of the laue symmetry for this space group'

    # completeness = (4/3)*pi*2**3 * V /(2**d)3
    completeness = 100
    topNextFragment = 1000

    new_t = None

    # if options.gui:
    #    pass
    # TODO: start the OutputViewer.py
    #    import OutputViewer
    #    new_t = SystemUtility.OutputThreading(OutputViewer.generateAndWhatchGUI,current_directory,nameOutput)
    # else:
    #       new_t = SystemUtility.OutputThreading(SELSLIB2.generateHTML,current_directory,nameOutput)

    xml_out = os.path.join(current_directory, nameOutput + ".xml")
    xml_obj = ET.Element('arcimboldo')
    ET.SubElement(xml_obj, 'data')
    ET.SubElement(xml_obj, 'configuration')
    ET.SubElement(xml_obj.find('configuration'), 'time_start').text = str(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    ET.SubElement(xml_obj.find('configuration'), 'bor_name').text = input_bor
    # ET.SubElement(xml_obj.find('configuration'), 'bor_text').text = allbor
    # NOTE TESTING
    lines_bor = allbor.split('\n')
    allbor = ''
    for i in range(len(lines_bor)):
        if not lines_bor[i].startswith('skip_res_limit') or not lines_bor[i].startswith('stop_if_solved'):
            allbor = allbor + (lines_bor[i] + '\n')
    # NOTE TESTING
    ET.SubElement(xml_obj.find('configuration'), 'bor_text').text = allbor
    ET.SubElement(xml_obj.find('configuration'), 'do_packing').text = str(USE_PACKING)
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

    SELSLIB2.POSTMORTEM = POST_MORTEM
    arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)

    if startCheckQueue:
        SystemUtility.startCheckQueue(sym, delete_check_file=False)
    # new_t.start()

    try:
        stop_if_solved = Config.getboolean("ARCIMBOLDO","STOP_IF_SOLVED")
        if coiled_coil:
            stop_if_solved = False # In coiled coil case we want to perform all cycles

        SELSLIB2.STOP_IF_SOLVED = stop_if_solved
    except:
        pass

    # Check resolution limit
    print '\n Resolution is ',resolution
    print '\n Coiled coil is set to ',coiled_coil
    if resolution > 2.5 and not skipResLimit and not coiled_coil:
        print colored("ATTENTION: Your resolution is lower than 2.5 A ARCIMBOLDO_LITE will stop now.", 'red')
        sys.exit(1)
    elif resolution > 3.0 and not skipResLimit and coiled_coil:
        print colored("ATTENTION: Coiled coil protocol was active but your resolution is lower than 3.0 A ARCIMBOLDO_LITE will stop now.", 'red')
        sys.exit(1)

    #NS CALCULATE PATTERSON PEAKS FROM DATA
    PattersonPeaksData=None
    if ANOMALOUS:
        nBunchAutoTracCyc=ANOMLIB.NBUNCH    #5 cycles if anomalous
        if otherAnomParamDic['patterson']:
            PattersonPeaksData=ANOMLIB.pattersonFromData(pathTo_hkl_file=startExpAnomDic['hkl_fa'], resolution=resolution, spaceGroupNum=sg_number,unitCellParam=cell_dim, cutoffDistance=0.1, filterMethod="sigma", cutoffRelIntensity = 0.1, gridDivide=3, ngridMax=100000, amplitudes=True)

    #NS: CHANGING THE DEFAULT NUMBER OF AUTOTRACING CYCLES PER BUNCH (DEFAULT 1)
    if nBunchAutoTracCyc>1:
        print("\nINFO: Changing the defaut number of autotracing cycle per bunch from 1 to {}".format(nBunchAutoTracCyc))
        shlxLinea1, shlxLineaP, shlxLineaLast = SELSLIB2.changeArgInShelxeLine(shelxeLineList=(shlxLinea1, shlxLineaP, shlxLineaLast), argDic={'-a': nBunchAutoTracCyc})
        print("INFO: shlxLinea1, shlxLineaP, shlxLineaLast changed to {}, {} and {}".format(shlxLinea1, shlxLineaP, shlxLineaLast))
    #NS UNIT CELL CONTENT ANALYSIS (optional) 
    if unitCellcontentAnalysis or NC<=0:
        solventContent, NC= SELSLIB2.unitCellContentAnalysis(current_directory=current_directory, spaceGroup=spaceGroup,cell_dim=cell_dim, MW=MW, resolution=resolution ,moleculeType="protein", numberOfComponents=NC,solventContent=solventContent)

        if solventContent is None or NC is None:
            print("ERROR, your solvent content or number of components is lower or equal to zero, quitting now!")
            sys.exit(1)
    #Finally set up the shelxe line for further steps (adding radius of the sphere of influence and solvent content)
        solvarg_re=re.compile(r"\-s[\d.]+")
        m0=solvarg_re.search(shlxLinea0)
        m1=solvarg_re.search(shlxLinea1)
        mP=solvarg_re.search(shlxLineaP)
        mLast=solvarg_re.search(shlxLineaLast)

        if resolution>2.5:                    #NS: Arbitrary cutoff for the radius of the sphere of influence
            shlxLinea0 += " -S%s"%resolution  
            shlxLinea1 += " -S%s"%resolution
            shlxLineaP += " -S%s"%resolution
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

        if mP:
            shlxLineaP = re.sub(solvarg_re,"-s%.2f"%solventContent, shlxLineaP)
        else:
            shlxLineaP += " -s%.2f"%solventContent

        if mLast:
            shlxLineaLast = re.sub(solvarg_re,"-s%.2f"%solventContent, shlxLineaLast)
        else:
            shlxLineaLast += " -s%.2f"%solventContent

        del(m0,m1,mP,mLast)    #Remove these variable from memory 

        print("INFO: Lines for shelxe jobs:")
        print("shlxLinea0 :%s "%shlxLinea0)
        print("shlxLinea1 :%s "%shlxLinea1)
        print("shlxLineaP :%s "%shlxLineaP)
        print("shlxLineaLast :%s "%shlxLineaLast)

    # Compute eLLG
    outputDireELLG = os.path.join(current_directory, "ELLG_COMPUTATION")
    if not (os.path.exists(outputDireELLG)):
        os.makedirs(outputDireELLG)

    list_model_calculate_ellg = SELSLIB2.prepare_files_for_MR_ELLG_LITE(outputDire=outputDireELLG + "/PREPARED_FILES", helix_list=helix_list, list_length=list_length)

    for i, ele in enumerate(list_model_calculate_ellg):
        mrsumpath = os.path.join(outputDireELLG, "ELLG_COMPUTATION_" + str(i)+"/ellg_computation.sum")
        if not os.path.exists(mrsumpath):
            (nqueuetest, convNamestest) = SELSLIB2.startMR_ELLG(DicParameters=DicParameters, cm=cm, sym=sym,
                                                            nameJob="ELLG_COMPUTATION_" + str(i), list_solu_set=list_model_calculate_ellg[:i],
                                                            list_models_calculate=list_model_calculate_ellg[i],
                                                            outputDire=outputDireELLG + "/ELLG_COMPUTATION_" + str(i),
                                                            mtz=mtz, MW=MW, NC=NC, F=F, SIGF=SIGF,
                                                            Intensities=Intensities, Aniso=Aniso,
                                                            normfactors=normfactors, tncsfactors=tncsfactors,
                                                            spaceGroup=spaceGroup, nice=nice, RMSD=RMSD, lowR=99,
                                                            highR=res_rot, ellg_target=ellg_target)

            dict_result_ellg = SELSLIB2.evaluateMR_ELLG(DicParameters, cm, DicGridConn, nameJob="ELLG_COMPUTATION",
                                                    outputDicr=outputDireELLG + "/ELLG_COMPUTATION_" + str(i),
                                                    nqueue=nqueuetest, ensembles=convNamestest)
        else:
            dict_result_ellg = SELSLIB2.readMR_ELLGsum(mrsumpath)

    ensembles = {}
    CluAll = []
    RotClu = []
    encn = {}
    skipuntil = None
    skipped = False

    if force_core != None:
        sym.PROCESSES = force_core

    if os.path.exists(os.path.join(current_directory, "temp")):
        shutil.rmtree(os.path.join(current_directory, "temp"))

    i = 1   #FIRST FRAGMENT

    
    #NS: Try different protocols when phased_TF is activated (either F/SIGF from SHELXE)
    #transfoTABLE={0:"none",1:"none",2:"none",3:"arom",4:"polya",5:"polys",6:"pseudos"}
    if ArcimboldoLOW:
        triedprotocols=[]  #to store the protocols already tried
        tNCSfound=False     #to remember that tNCS have been found , Nico for LOW
        firstProtocol=True  #Will become false if the search is done again for a given fragment

    while (i<=NSEARCH):

        if skipuntil != None and i != skipuntil:
            print "==>Skipuntil is %s, skipping fragment %s"%(skipuntil,i)
            i+=1
            print "=>i is now %s"%i
            continue

        proto=0 #NS low (keep this for compatibility)
        if ArcimboldoLOW:
            protoGenerator =LOWLIB.generateProtocol(Fcalc_TF=phased_TF, use_protocols=use_protocols, i=i) #iterator
            proto=next(protoGenerator)  #protocol number to pass to the translation function
            print("---------------> Protocol %d"%proto)
            #Add the current protocol to "current protocols"
            triedprotocols.append(proto)

        
        skipuntil = None
        nameDir = os.path.join(current_directory, "ens1_frag" + str(i) + "/")

        if ArcimboldoLOW:  #Removes the directories 3_FTF_LIBRARY and afterwards to redo a search with a different protocol
            if not firstProtocol:
                LOWLIB.removePreviousDirectories(nameDir)

        if os.path.exists(nameDir + "skip"):
            print "Skipping fragment ", i
            flin = os.path.join(current_directory, "./ens1_frag" + str(i + 1) + "/1_FRF_LIBRARY/clusters.sum")

            if i == 1:
                SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput, "ARCIMBOLDO",
                                         "TABLE", ensembles, i, readSum=flin,coiled_coil=coiled_coil)
                SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput, "ARCIMBOLDO",
                                         "JUMPFRAG_" + str(i) + "_" + str(i + 1), ensembles, i,coiled_coil=coiled_coil)
            else:
                SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput, "ARCIMBOLDO",
                                         "TABLE", ensembles, i + 1, readSum=flin,coiled_coil=coiled_coil)
                SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput, "ARCIMBOLDO-SKIP",
                                         "JUMP", ensembles, i,coiled_coil=coiled_coil)
            skipped = True
            i+=1
            continue

        if not (os.path.exists(nameDir)):
            os.makedirs(nameDir)

        SystemUtility.open_connection(DicGridConn, DicParameters, cm)
        if cm != None and hasattr(cm, "channel"):
            print cm.create_remote_dir(DicParameters["nameExecution"] + "_" + str(i))
            print cm.change_remote_dir(DicParameters["nameExecution"] + "_" + str(i))

        SystemUtility.close_connection(DicGridConn, DicParameters, cm)

        peaks = 75

        if i == 1:
            topFRF = topFRF_1
            topFTF = topFTF_1
            topRNP = topRNP_1
            topPACK = topPACK_1
            topExp = topExp_1


        else:
            topFRF = topFRF_n
            topFTF = topFTF_n
            topRNP = topRNP_n
            topPACK = topPACK_n
            topExp = topExp_n

        if i > 1 and len(helix_list) > 0:   #If not first round and pdb models provided in helix_list 
            if len(list_length) > 0:        #If ideal helices are provided
                model_file = os.path.join(ensemblesDir, os.path.basename("th" + str(list_length[i - 1]) + "_0_0.pdb"))
                mf = open(model_file, "w")
                mf.write(helix_list[i - 1][0])
                mf.close()

                if hasattr(cm, "channel"):
                    SystemUtility.open_connection(DicGridConn, DicParameters, cm)
                    actualdi = cm.get_remote_pwd()
                    print cm.change_remote_dir(cm.remote_library_path)
                    print cm.copy_local_file(model_file, os.path.basename(model_file), send_now=True)
                    print cm.change_remote_dir(actualdi)
                    SystemUtility.close_connection(DicGridConn, DicParameters, cm)

                for key in ensembles.keys():
                    if key.startswith("ensembleID") and "INV" not in key:
                        fra = int(key.split("FR")[-1].split("_")[0])
                        if not useFIXED or fra > 1:
                            model_f = os.path.join(ensemblesDir,
                                                   os.path.basename("th" + str(list_length[fra]) + "_0_0.pdb"))
                            ensembles[key] = os.path.join(ensemblesDir, os.path.basename(model_f))
                for tin in range(len(list_length)):
                    heli_len = list_length[tin]
                    model_f = os.path.join(ensemblesDir, os.path.basename("th" + str(heli_len) + "_0_0.pdb"))
                    ensembles["ensemble" + str(tin + 1)] = os.path.join(ensemblesDir, os.path.basename(model_f))
            else:           #If pdb models are provided instead 
                if os.path.exists(helix_list[i - 1][0]):
                    model_file = os.path.join(ensemblesDir, os.path.basename("th" + str(i) + "_0_0.pdb"))
                    shutil.copyfile(helix_list[i - 1][0], model_file)
                else:
                    model_file = os.path.join(ensemblesDir, os.path.basename("th" + str(i) + "_0_0.pdb"))
                    mf = open(model_file, "w")
                    mf.write(helix_list[i-1][0])
                    mf.close()
                if hasattr(cm, "channel"):
                    SystemUtility.open_connection(DicGridConn, DicParameters, cm)
                    actualdi = cm.get_remote_pwd()
                    print cm.change_remote_dir(cm.remote_library_path)
                    print cm.copy_local_file(model_file, os.path.basename(model_file), send_now=True)
                    print cm.change_remote_dir(actualdi)
                    SystemUtility.close_connection(DicGridConn, DicParameters, cm)

                for key in ensembles.keys():
                    if key.startswith("ensembleID") and "INV" not in key:
                        if not usePDO:
                            fra = int(key.split("FR")[-1].split("_")[0])
                            if not useFIXED or fra > 1:
                                model_f = os.path.join(ensemblesDir, os.path.basename("th" + str(fra + 1) + "_0_0.pdb"))
                                ensembles[key] = os.path.join(ensemblesDir, os.path.basename(model_f))

                for tin in range(1, NSEARCH + 1):
                    model_f = os.path.join(ensemblesDir, os.path.basename("th" + str(tin) + "_0_0.pdb"))
                    ensembles["ensemble" + str(tin)] = os.path.join(ensemblesDir, os.path.basename(model_f))

            if len(helix_inverted) > 0 and search_inverted_helix:
                model_file_inverted = os.path.join(ensemblesDir, os.path.basename("thinverted" + str(list_length[i - 1]) + "_0_0.pdb"))
                mf = open(model_file_inverted, "w")
                mf.write(helix_inverted[i - 1][0])
                mf.close()

                if hasattr(cm, "channel"):
                    SystemUtility.open_connection(DicGridConn, DicParameters, cm)
                    actualdi = cm.get_remote_pwd()
                    print cm.change_remote_dir(cm.remote_library_path)
                    print cm.copy_local_file(model_file_inverted, os.path.basename(model_file_inverted), send_now=True)
                    print cm.change_remote_dir(actualdi)
                    SystemUtility.close_connection(DicGridConn, DicParameters, cm)

                for key in ensembles.keys():
                    if "INV" in key:
                        fra = int(key.split("FR")[-1].split("_")[0])
                        if not useFIXED or fra > 1:
                            model_f_inverted = os.path.join(ensemblesDir,
                                                   os.path.basename("thinverted" + str(list_length[fra]) + "_0_0.pdb"))
                            ensembles[key] = os.path.join(ensemblesDir, os.path.basename(model_f_inverted))
                for tin in range(len(list_length)):
                    heli_len = list_length[tin]
                    model_f_inverted = os.path.join(ensemblesDir, os.path.basename("thinverted" + str(heli_len) + "_0_0.pdb"))
                    ensembles["ensemble" + str(tin + 1)+"INV"] = os.path.join(ensemblesDir, os.path.basename(model_f_inverted))

        if ArcimboldoLOW:
            LOWLIB.replaceFragments(ensemblesDir=ensemblesDir, cell_dim=cell_dim,spaceGroup=spaceGroup,transform=transformPDB)
            LOWLIB.printHeader(jobType="FRF",fragNumber=i,protocolNumber=proto)

        if not os.path.exists(os.path.join(nameDir, "1_FRF_LIBRARY/clusters.sum")):  #ROTATION SEARCH (whatever round number) if clusters file not present
            SystemUtility.open_connection(DicGridConn, DicParameters, cm)

            # print("SHERLOCK HEAP")
            # for elem in CluAll:
            #     hep=elem["heapSolutions"]
            #     for sol in hep.asList():
            #         print sol[1]
            #         print "\n\n"
            # sys.exit(0)

            (nqueue, ensembles) = SELSLIB2.startFRF(DicParameters=DicParameters, cm=cm, sym=sym,
                                                    nameJob="1_FRF_LIBRARY_" + str(i), dir_o_liFile=inputDir,
                                                    outputDire=nameDir + "1_FRF_LIBRARY", mtz=mtz, MW=MW, NC=NC, F=F,
                                                    SIGF=SIGF, Intensities=Intensities, Aniso=Aniso,
                                                    normfactors=normfactors, tncsfactors=tncsfactors, nice=nice,
                                                    RMSD=RMSD, lowR=99, highR=res_rot, final_rot=peaks, save_rot=peaks,
                                                    frag_fixed=i, spaceGroup=spaceGroup, sampl=sampl_rot,
                                                    ensembles=ensembles, tops=topNextFragment, VRMS=VRMS, BFAC=BFAC,
                                                    BULK_FSOL=BULK_FSOL, BULK_BSOL=BULK_BSOL,formfactors=formfactors)

            SystemUtility.endCheckQueue()

            if ArcimboldoLOW:
                LOWLIB.printHeader(jobType="startFRF",fragNumber=i,protocolNumber=proto)

            # print "############################" #NS ADD
            # print "# evaluate_FRF_clusterOnce (fragment %s, protocol %s)"%(i,proto)
            # print "############################"
                            #NS TRY

            CluAll, RotClu, ensembles = SELSLIB2.evaluateFRF_clusterOnce(DicParameters, cm, sym, DicGridConn, [],
                                                                         "1_FRF_LIBRARY_" + str(i),
                                                                         nameDir + "1_FRF_LIBRARY/", nqueue, quate,
                                                                         laue, ncs, spaceGroup, ensembles,
                                                                         clusteringAlg, excludeLLG, i, cell_dim,
                                                                         thresholdCompare, evaLLONG,
                                                                         applyNameFilter=False, tops=topFRF,
                                                                         isArcimboldo=True, giveids=True)

            if distribute_computing == "multiprocessing":
                # print "############################" #NS ADD
                # print "# filterClustersAndSolutionByCores (fragment %s, protocol %s)"%(i,proto)
                # print "############################"
                CluAll = SELSLIB2.filterClustersAndSolutionByCores(CluAll, sym)

            saveM = False
            if i > 1:
                saveM = True
            # print "############################" #NS ADD
            # print "# writeSumClusters (fragment %s, protocol %s)"%(i,proto)
            # print "############################"
            SELSLIB2.writeSumClusters(CluAll, nameDir + "1_FRF_LIBRARY/", "clusters", ensembles, RotClu=RotClu,
                                      saveMAP=saveM)
            # while len(SystemUtility.LISTJOBS) > 0:
            #    time.sleep(1)
        else:                         #IF clusters file present, read it directly instead of performing rotation search
            # print "############################" #NS ADD
            # print "# readClustersFromSUMToDB (fragment %s, protocol %s)"%(i,proto)
            # print "############################"
            ensembles, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                               nameDir + "1_FRF_LIBRARY/clusters.sum",
                                                                               "ROTSOL")
            for key in ensembles.keys():
                try:
                    if search_inverted_helix and "INV" in key:
                        os.link(model_file_inverted, os.path.join(ensemblesDir, ensembles[key]))
                    else:
                        os.link(model_file, os.path.join(ensemblesDir, ensembles[key]))
                except:
                    pass

        #         #saving the values of the current solution from rotation if the loop has to start again with a different protocol but same fragment index i
        # CluAll_BAK = CluAll[:]
        # RotClu_BAK = RotClu[:]
        # ensembles_BAK = dict(ensembles)
        # encn_BAK = dict(encn)

        # #reloading them if changing protocol
        # if protoidx !=0:
        #     #remove the current fragment's folder to start again with a different protocol
        #     shutil.rmtree(os.path.join(current_directory, "ens1_frag" + str(i) + "/"))
        #     CluAll = CluAll_BAK
        #     RotClu = RotClu_BAK
        #     ensembles = ensembles_BAK
        #     encn = encn_BAK

        if i == 1:
            SELSLIB2.writeOutputFile(lock=lock, DicParameters=DicParameters, ClusAll=CluAll,
                                     outputDir=current_directory, filename=nameOutput, mode="ARCIMBOLDO-CLUSTERS",
                                     step="FRF", ensembles=ensembles, frag_fixed=i, coiled_coil=coiled_coil)
        if not skipped:
            SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput, "ARCIMBOLDO", "TABLE",
                                     ensembles, i, readSum=nameDir + "1_FRF_LIBRARY/clusters.sum",coiled_coil=coiled_coil)
        arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)
        skipped = False

        # TODO: study how to adapt Picasso analysis for grid
        if POST_MORTEM and i == 1 and os.path.exists(ent):
            #NOTE: make it work also when inverted helices are used. Do we need to modify something?
            dictRMSD, sumPathGyre = SELSLIB2.executePicasso(current_directory, sym, nameOutput, model_file, quate,
                                                            cell_dim, laue, ncs, CluAll, ensembles, ent, Data.th70pdb)
            if sumPathGyre is not None:
                C, en = SELSLIB2.readClustersFromSUM(sumPathGyre)
                SystemUtility.open_connection(DicGridConn, DicParameters, cm)
                nq, conv2 = SELSLIB2.startRGR(DicParameters=DicParameters, cm=cm, sym=sym, nameJob=str(0) + "_A",
                                              ClusAll=C, ensembles=en,
                                              outputDire=os.path.join(current_directory, str(0) + "_A"), mtz=mtz, MW=MW,
                                              NC=NC, F=F, SIGF=SIGF, Intensities=Intensities, Aniso=Aniso,
                                              normfactors=normfactors, tncsfactors=tncsfactors, nice=nice, RMSD=RMSD,
                                              lowR=99, highR=res_rot, frag_fixed=1, spaceGroup=spaceGroup,
                                              save_rot=peaks, sampl=sampl_rot, LIMIT_CLUSTER=0, USE_TNCS=USE_TNCS,
                                              isOMIT=True, VRMS=VRMS_GYRE, BFAC=BFAC, sigr=sigr, sigt=sigt,
                                              preserveChains=preserveChains, BULK_FSOL=BULK_FSOL, BULK_BSOL=BULK_BSOL,
                                              formfactors=formfactors)
                SystemUtility.endCheckQueue()
                cns, Clur = SELSLIB2.evaluateRGR(DicParameters, cm, sym, DicGridConn, str(0) + "_A",
                                                 os.path.join(current_directory, str(0) + "_A"), True, cell_dim, quate,
                                                 conv2, None, conv2, LIMIT_CLUSTER=0, isOMIT=True, ent=ent)
                SELSLIB2.writeSumClusters(Clur, os.path.join(current_directory, "./"), "llg_optimal_rot", cns)
                shutil.rmtree(os.path.join(current_directory, str(0) + "_A"))
                C, en = SELSLIB2.readClustersFromSUM(os.path.join(current_directory, "./llg_optimal_rot.sum"))
                llgs = []
                namerts = []
                for item in C[0]["heapSolutions"]:
                    prio, rt = item
                    llgs.append(rt["llg"])
                    namerts.append(en[rt["name"]])
                examinList = []
                for zas in range(0, 100, 5):
                    examinList.append(ADT.get_percentage_llg_range(llgs, namerts, (zas / 100.0), (zas + 10) / 100.0))
                bf = 110
                dictions = {}
                for item in examinList:
                    basic, safellg = item
                    for filebf in basic:
                        print "modifying", filebf, "with threshold llg", safellg
                        old_bf = bf
                        if llgs[namerts.index(filebf)] < 0:
                            bf = 999.00
                        Bioinformatics.normalizeBFACTORS_ofPDB(filebf, bf)
                        fq = open(filebf, "r")
                        listbf = fq.readlines()
                        fq.close()
                        for linea in listbf:
                            if linea.startswith("ATOM") or linea.startswith("HETATM"):
                                dictions[linea[17:27]] = linea[60:66]

                        bf = old_bf
                    bf -= 5
                pdballent = ""
                fq = open(ent, "r")
                listent = fq.readlines()
                fq.close()
                for key in dictions.keys():
                    for linea in listent:
                        if key in linea:
                            linea = linea[:60] + dictions[key] + linea[66:]
                            pdballent += linea

                fj = open(os.path.join(current_directory, "./llgmodeled.ent"), "w")
                fj.write(pdballent)
                fj.close()

            ensembles, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                               nameDir + "1_FRF_LIBRARY/clusters.sum",
                                                                               "ROTSOL")

        foolsum = ""

        #TRANSLATION SEARCH :
        if i > 1 or ((spaceGroup not in ["P1", "P 1"] or USE_TNCS) and not randomize_translations):
            #Valid block if *Not first round
            #               * or First round but Space group not P1
            #               * or First round and Space group is P1 but the USE_TNCS option is on
            #               * The randomize_translations option is never on
            if not os.path.exists(os.path.join(nameDir, "3_FTF_LIBRARY/clusters.sum")):
                if range_rmsd:                 #If the option RANGE_RMSD used (practically never the case)
                    old_TNCS = USE_TNCS
                    USE_TNCS = False
                    rmsd_ranges = [round(r / 10.0, 2) for r in
                                   xrange(int((RMSD - range_rmsd_tra) * 10), (int((RMSD + range_rmsd_tra) * 10)) + 1) if
                                   r > 0]
                    for ind, rms in enumerate(rmsd_ranges):
                        if not os.path.exists(os.path.join(nameDir, "4_PACK_LIBRARY_" + str(rms) + "/clusters.sum")):
                            ensembles, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                               nameDir + "1_FRF_LIBRARY/clusters.sum",
                                                                                               "ROTSOL")
                            SystemUtility.open_connection(DicGridConn, DicParameters, cm)
                            nqueue3 = SELSLIB2.startFTFOnePerCluster(DicParameters=DicParameters, cm=cm, sym=sym,
                                                                     nameJob="3_FTF_LIBRARY_" + str(i) + "_" + str(rms),
                                                                     ClusAll=CluAll, ensembles=ensembles,
                                                                     outputDire=nameDir + "3_FTF_LIBRARY_" + str(
                                                                         rms) + "/", mtz=mtz, MW=MW, NC=NC, F=F,
                                                                     SIGF=SIGF, Intensities=Intensities, Aniso=Aniso,
                                                                     normfactors=normfactors, tncsfactors=tncsfactors,
                                                                     nice=nice, RMSD=rms, lowR=99, highR=res_tran,
                                                                     final_tra=peaks, save_tra=peaks, frag_fixed=i,
                                                                     spaceGroup=spaceGroup, cutoff_pack=CLASHES,
                                                                     usePDO=usePDO, sampl=sampl_tran, USE_TNCS=USE_TNCS,
                                                                     tops=topNextFragment, VRMS=VRMS, BFAC=BFAC,
                                                                     BULK_FSOL=BULK_FSOL, BULK_BSOL=BULK_BSOL,
                                                                     PACK_TRA=PACK_TRA,formfactors=formfactors)

                            SystemUtility.endCheckQueue()

                            CluAll_a, ensembles_a, nfixfr_a = SELSLIB2.evaluateFTF(DicParameters=DicParameters, cm=cm,
                                                                                   sym=sym, DicGridConn=DicGridConn,
                                                                                   nameJob="3_FTF_LIBRARY_" + str(
                                                                                       i) + "_" + str(rms),
                                                                                   outputDicr=nameDir + "3_FTF_LIBRARY_"
                                                                                              + str(rms) + "/",
                                                                                   nqueue=nqueue3, ensembles=ensembles,
                                                                                   excludeZscore=excludeZscore,
                                                                                   fixed_frags=i, quate=quate,
                                                                                   mode="TRA", laue=laue,
                                                                                   listNCS=ncs,
                                                                                   clusteringMode=clusteringAlg,
                                                                                   cell_dim=cell_dim,
                                                                                   thresholdCompare=thresholdCompare,
                                                                                   evaLLONG=evaLLONG,
                                                                                   tops=topFTF, applyNameFilter=False,
                                                                                   isArcimboldo=True, giveids=True,use_tNCS=USE_TNCS)
                            SystemUtility.open_connection(DicGridConn, DicParameters, cm)


                            nqueue4 = SELSLIB2.startPACKOnePerCluster(DicParameters=DicParameters, cm=cm, sym=sym,
                                                                      nameJob="4_PACK_LIBRARY_" + str(i) + "_" + str(
                                                                          rms), ClusAll=CluAll_a, ensembles=ensembles_a,
                                                                      outputDire=nameDir + "4_PACK_LIBRARY_" + str(
                                                                          rms) + "/", mtz=mtz, MW=MW, NC=NC, F=F,
                                                                      SIGF=SIGF, Intensities=Intensities, Aniso=Aniso,
                                                                      normfactors=normfactors, tncsfactors=tncsfactors,
                                                                      nice=nice, RMSD=rms, lowR=99, highR=res_tran,
                                                                      cutoff=CLASHES,
                                                                      spaceGroup=spaceGroup,
                                                                      frag_fixed=i, tops=topNextFragment, usePDO=usePDO,
                                                                      VRMS=VRMS, BFAC=BFAC,
                                                                      randomize_trans_per_rot=randomize_trans_per_rot,
                                                                      consider_inverted_helix=search_inverted_helix,
                                                                      formfactors=formfactors)
                            SystemUtility.endCheckQueue()
                            CluAll_a, ensembles_a, tolose = SELSLIB2.evaluateFTF(DicParameters=DicParameters, cm=cm,
                                                                                 sym=sym, DicGridConn=DicGridConn,
                                                                                 nameJob="4_PACK_LIBRARY_" + str(
                                                                                     i) + "_" + str(rms),
                                                                                 outputDicr=nameDir + "4_PACK_LIBRARY_" + str(
                                                                                     rms) + "/", nqueue=nqueue4,
                                                                                 ensembles=ensembles_a,
                                                                                 excludeZscore=excludeZscore,
                                                                                 fixed_frags=i, quate=quate,
                                                                                 mode="PACK", laue=laue, listNCS=ncs,
                                                                                 clusteringMode=clusteringAlg,
                                                                                 cell_dim=cell_dim,
                                                                                 thresholdCompare=thresholdCompare,
                                                                                 evaLLONG=evaLLONG, tops=topPACK,
                                                                                 isArcimboldo=True,
                                                                                 applyNameFilter=False,use_tNCS=USE_TNCS)
                            shutil.rmtree(nameDir + "3_FTF_LIBRARY_" + str(rms) + "/")

                            CluAll_a = SELSLIB2.filterAllSolsByTop(CluAll_a, i, peaks)
                            if distribute_computing == "multiprocessing":
                                CluAll_a = SELSLIB2.filterClustersAndSolutionByCores(CluAll_a, sym)
                            SELSLIB2.writeSumClusters(CluAll_a, nameDir + "4_PACK_LIBRARY_" + str(rms) + "/",
                                                      "clusters", ensembles_a)
                    maxzcall = 0
                    maxrms = 0
                    for ind, rms in enumerate(rmsd_ranges):
                        ensembles, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                           nameDir + "4_PACK_LIBRARY_" + str(
                                                                                               rms) + "/clusters.sum",
                                                                                           "ROTSOL")
                        maxzscore = max([item[1]["zscore"] for clu in CluAll for item in clu["heapSolutions"].asList()])
                        if maxzscore > maxzcall:
                            maxzcall = maxzscore
                            maxrms = rms
                    print "MAX ZSCORE for the FTF is:", maxzcall, "and was reached with setting a rmsd of", maxrms
                    RMSD = maxrms
                    USE_TNCS = old_TNCS

                #FROM this point, the option RANGE_RMSD doesn't need to be True
                #Properly starting the translation search from here, starting by reading rotation clusters
                ensembles, CluAll, RotClu, encn = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                   nameDir + "1_FRF_LIBRARY/clusters.sum",
                                                                                   "ROTSOL")
                SystemUtility.open_connection(DicGridConn, DicParameters, cm)
                
                               
                if ArcimboldoLOW:
                    LOWLIB.printHeader(jobType="startFTFOnePerCluster",fragNumber=i,protocolNumber=proto)

                    #Avoid re-generating the F-calc if it was already done
                    if phased_TF and proto in (1,2):
                        if (proto==1 and 2 not in triedprotocols) or (proto==2 and 1 not in triedprotocols):
                            makeFcalc=True
                            LOWLIB.prepareFTF()  #NEED TO DEVELOP THAT IN LOWLIB generate the Fcalc datasets 
                    

                #nqueue3,dicEqRots
                nqueue3 = SELSLIB2.startFTFOnePerCluster(DicParameters=DicParameters, cm=cm, sym=sym,
                                                         nameJob="3_FTF_LIBRARY_" + str(i), ClusAll=CluAll,
                                                         ensembles=ensembles, outputDire=nameDir + "3_FTF_LIBRARY/",
                                                         mtz=mtz, MW=MW, NC=NC, F=F, SIGF=SIGF, Intensities=Intensities,
                                                         Aniso=Aniso, normfactors=normfactors, tncsfactors=tncsfactors,
                                                         nice=nice, RMSD=RMSD, lowR=99, highR=res_tran, final_tra=peaks,
                                                         save_tra=peaks, frag_fixed=i, spaceGroup=spaceGroup,
                                                         cutoff_pack=CLASHES, usePDO=usePDO, sampl=sampl_tran,
                                                         USE_TNCS=USE_TNCS, tops=topNextFragment, VRMS=VRMS, BFAC=BFAC,
                                                         BULK_FSOL=BULK_FSOL, BULK_BSOL=BULK_BSOL, PACK_TRA=PACK_TRA,
                                                         excludeZscore=excludeZscore,formfactors=formfactors,
                                                         phased_TF=phased_TF,cell_dim=cell_dim,hklfile=hkl,resolution=resolution,
                                                         protocol=proto, makeFcalc=False,model_file=model_file,tncsVector=tncsVector) #NSADD:phased_TF=phased_TF,cell_dim=cell_dim,hklfile=hkl

                SystemUtility.endCheckQueue()

                # print "############################" #NS ADD
                # print "# evaluateFTF (fragment %s, protocol %s)"%(i,proto)
                # print "############################"
                CluAll, ensembles, nfixfr = SELSLIB2.evaluateFTF(DicParameters, cm, sym, DicGridConn,
                                                                 "3_FTF_LIBRARY_" + str(i), nameDir + "3_FTF_LIBRARY/",
                                                                 nqueue3, ensembles, excludeZscore, i, quate, "TRA",
                                                                 laue, ncs, clusteringAlg, cell_dim, thresholdCompare,
                                                                 evaLLONG, tops=topFTF, applyNameFilter=False,
                                                                 isArcimboldo=True, giveids=True,cleanshsol=cleanshsol,use_tNCS=USE_TNCS)

                if ArcimboldoLOW:
                    if use_protocols and excludeZscore and not CluAll:
                        print "No solution passed the TFZ cut off criteria after FTF (TFZ=%s)"%excludeZscore
                        print "Redoing a search for this fragment with a different protocol"
                        protoidx+=1
                        continue

              
                if nfixfr > 0 and nfixfr != i and USE_TNCS:
                    #NS add: in case tNCS is found, the TFZ== filter is not applied (i.e zero)
                    if i==1:
                        print "INFO: tNCS has been found, pairs of fragments are searched for instead of individual ones."
                        print "INFO: tNCS has been found, TFZ== filter NOT active (reset from %s to 0)"%excludeZscoreRNP
                        tNCSfound=True
                        excludeZscoreRNP=0

                    nuod = os.path.join(current_directory, "ens1_frag" + str(nfixfr) + "/")
                    print "==>moving %s to %s"%(nameDir, nuod)
                    shutil.move(nameDir, nuod)
                    #NS store the dictionary of rotation names in a json file in case a run has to be restarted from a further step
                    if ArcimboldoLOW:
                       # print "TOTO IS HERE"
                        with open(os.path.join(nuod,"3_FTF_LIBRARY","dicEqRots.json"),'w') as f:
                            json.dump(dicEqRots,f)

                    CluAll = SELSLIB2.filterAllSolsByTop(CluAll, nfixfr, peaks)
                    if distribute_computing == "multiprocessing":
                        CluAll = SELSLIB2.filterClustersAndSolutionByCores(CluAll, sym)

                    SELSLIB2.writeSumClusters(CluAll, nuod + "3_FTF_LIBRARY/", "clusters", ensembles)
                    shutil.copyfile(nuod + "1_FRF_LIBRARY/clusters.sum", nuod + "1_FRF_LIBRARY/clustersROTCLU.sum")
                    shutil.copyfile(nuod + "3_FTF_LIBRARY/clustersRotations.sum",
                                    nuod + "1_FRF_LIBRARY/clustersRotations.sum")
                    os.makedirs(nameDir)
                    f = open(nameDir + "skip", "w")
                    f.close()
                    f = open(nuod + "1_FRF_LIBRARY/clusters.sum", "r")
                    alls = f.read()
                    f.close()
                    newalls = re.sub("FR" + str(i - 1), "FR" + str(nfixfr - 1), alls)

                    def dashrepl(matchobj):
                        # print "Modifico",matchobj.group(0),"in",matchobj.group(0)+"_"+matchobj.group(0)[-1:]
                        return matchobj.group(0) + "_" + (matchobj.group(0).split()[-1]).split("_")[-1]

                    newalls = re.sub("/////////////////////////////////////////////\n.*Original Rot. Cluster: .*",
                                     dashrepl, newalls)
                    f = open(nuod + "1_FRF_LIBRARY/clusters.sum", "w")
                    f.write(newalls)
                    f.close()
                    Clui, cnvi = SELSLIB2.readClustersFromSUM(nuod + "1_FRF_LIBRARY/clusters.sum")
                    for clk in Clui:
                        for itin in clk["heapSolutions"].asList():
                            prin, rotin = itin
                            rotin["n_prev_cluster"] = SELSLIB2.__getIDClusterFromDescription(
                                rotin["original_rotcluster"])
                    SELSLIB2.writeSumClusters(Clui, nuod + "1_FRF_LIBRARY/", "clusters", cnvi)
                    ensembles, CluAll, rt, et = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                                 nuod + "1_FRF_LIBRARY/clusters.sum",
                                                                                 "ROTSOL")
                    SELSLIB2.writeSumClusters(CluAll, nuod + "1_FRF_LIBRARY/", "clusters", ensembles)
                    SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput, "ARCIMBOLDO", "JUMPFRAG_" + str(i) + "_" + str(nfixfr), ensembles, i, coiled_coil=coiled_coil)

                    #NS tag for Arcimboldo_Low so that it can retrieve which model this folder corresponds to
                    if ArcimboldoLOW and not glob.glob(os.path.join(nameDir,"model_file*.txtmod")):
                        outens = open(os.path.join(nameDir,"model_file"+modelLowName+".txtmod"), "w") #NS, to keep track of which model from the ARCIMBOLDO LOW script we are dealing with
                        outens.write("Protocol used: %s\n"%proto)
                        outens.write("model_file: %s\n"%model_file)
                        if tNCSfound:
                            outens.write("tNCS")
                        outens.close()

                    skipuntil = nfixfr
                    if NSEARCH < nfixfr:
                        print "You have looked for ", NSEARCH, "fragment(s) but TNCS was found. Please add another fragment to the search to the fragment_to_search keyword"
                        sys.exit(0)
                    i += 1
                    continue
                else:
                    #SELSLIB2.writeSumClusters(CluAll, nameDir + "3_FTF_LIBRARY/", "clusters_before_filter_top", ensembles)

                    #NS store the dictionary of rotation names in a json file in case a run has to be restarted from a further step
                    if ArcimboldoLOW:
                        with open(os.path.join(nameDir,"3_FTF_LIBRARY","dicEqRots.json"),'w') as f:
                            json.dump(dicEqRots,f)

                    CluAll = SELSLIB2.filterAllSolsByTop(CluAll, i, peaks)
                    if distribute_computing == "multiprocessing":
                        #SELSLIB2.writeSumClusters(CluAll, nameDir + "3_FTF_LIBRARY/", "clusters_before_filter_core", ensembles)
                        CluAll = SELSLIB2.filterClustersAndSolutionByCores(CluAll, sym)
                    SELSLIB2.writeSumClusters(CluAll, nameDir + "3_FTF_LIBRARY/", "clusters", ensembles)
            else:
                ensembles, CluAll, rt, et = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                             nameDir + "3_FTF_LIBRARY/clusters.sum",
                                                                             "ROTSOL")
                for key in ensembles.keys():
                    try:
                        if search_inverted_helix and "INV" in key:
                            os.link(model_file_inverted, os.path.join(ensemblesDir, ensembles[key]))
                        else:
                            os.link(model_file, os.path.join(ensemblesDir, ensembles[key]))
                    except:
                        pass

            SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput, "ARCIMBOLDO", "FTF",
                                     ensembles, i, readSum=nameDir + "3_FTF_LIBRARY/clusters.sum",coiled_coil=coiled_coil)
            arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)
            folsum = nameDir + "3_FTF_LIBRARY/clusters.sum"
        else: #If FIRST ROUND FOR TRANSLATION SEARCH and * space group is P1 and TNCS is OFF (i.e no need for translation search) or * (the randomize translation option is ON)
            SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput, "ARCIMBOLDO", "FTF",
                                     ensembles, i, makeEmpty=True, readSum=nameDir + "1_FRF_LIBRARY/clusters.sum",coiled_coil=coiled_coil)
            folsum = nameDir + "1_FRF_LIBRARY/clusters.sum"
            arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)
            USE_PACKING = True if randomize_translations else USE_PACKING
            USE_PACKING = True if (i > 1 and spaceGroup in ["P1", "P 1"]) else USE_PACKING
            USE_TRANSLA = False

        # CHECK FOR NO SOLUTIONS IN TRANSLATION WHEN USING TRANSLATION PACKING CHECK
        if PACK_TRA and USE_PACKING:
            toExit = True
            for clund in CluAll:
                if len(clund["heapSolutions"].asList()) > 0:
                    toExit = False
                    break
            if toExit:
                if i == 1:
                    print "EXIT"
                    sys.exit(0)
                else:
                    break

        if USE_PACKING:
            toExit = True
            if not os.path.exists(os.path.join(nameDir, "4_PACK_LIBRARY/clusters.sum")):



                SystemUtility.open_connection(DicGridConn, DicParameters, cm)

                # print "############################" #NS ADD
                # print "# startPACKOnePerCluster (fragment %s, protocol %s)"%(i,proto)
                # print "############################"
                nqueue4 = SELSLIB2.startPACKOnePerCluster(DicParameters=DicParameters, cm=cm, sym=sym,
                                                          nameJob="4_PACK_LIBRARY_" + str(i), ClusAll=CluAll,
                                                          ensembles=ensembles, outputDire=nameDir + "4_PACK_LIBRARY/",
                                                          mtz=mtz, MW=MW, NC=NC, F=F, SIGF=SIGF,
                                                          Intensities=Intensities, Aniso=Aniso, normfactors=normfactors,
                                                          tncsfactors=tncsfactors, nice=nice, RMSD=RMSD, lowR=99,
                                                          highR=res_tran, cutoff=CLASHES,
                                                          spaceGroup=spaceGroup, frag_fixed=i,
                                                          tops=topNextFragment, usePDO=usePDO, VRMS=VRMS, BFAC=BFAC,
                                                          randomize_trans_per_rot=randomize_trans_per_rot,
                                                          consider_inverted_helix=search_inverted_helix,
                                                          formfactors=formfactors)

                # print "############################" #NS ADD
                # print "# evaluateFTF  (after packing, fragment %s, protocol %s)"%(i,proto)
                # print "############################"


                SystemUtility.endCheckQueue()
                CluAll, ensembles, tolose = SELSLIB2.evaluateFTF(DicParameters=DicParameters, cm=cm, sym=sym,
                                                                 DicGridConn=DicGridConn,
                                                                 nameJob="4_PACK_LIBRARY_" + str(i),
                                                                 outputDicr=nameDir + "4_PACK_LIBRARY/", nqueue=nqueue4,
                                                                 ensembles=ensembles, excludeZscore=excludeZscore,
                                                                 fixed_frags=i, quate=quate, mode="PACK", laue=laue,
                                                                 listNCS=ncs, clusteringMode=clusteringAlg,
                                                                 cell_dim=cell_dim, thresholdCompare=thresholdCompare,
                                                                 evaLLONG=evaLLONG, tops=topPACK, isArcimboldo=True,
                                                                 applyNameFilter=False,cleanshsol=cleanshsol,use_tNCS=USE_TNCS)


                # Check if something remains in the Solution list, exit otherwise
                for clund in CluAll:
                    if len(clund["heapSolutions"].asList()) > 0:
                        print 'There are solutions that survive the packing '
                        toExit = False
                        break

                if not toExit:
                    CluAll = SELSLIB2.filterOutImprobableSols(CluAll, excludeLLG)
                    toExit = True
                    for clund in CluAll:
                        if len(clund["heapSolutions"].asList()) > 0:
                            print("There are solutions that survive the filtering of improbable solutions")
                            toExit = False
                            break

                if toExit and not ArcimboldoLOW:
                    print "Either packing has excluded everything or the surviving solutions did not pass the filtering of improbable solutions"
                    # TODO: wait for the all children or thread processes to end before to quit, in order for the output to be properly written
                    if i == 1:
                        print "EXIT"
                        sys.exit(0)
                    else:
                        print "SKIPPING"
                        break

                elif toExit and ArcimboldoLOW:
                    print "Packing has excluded everything...NEXT PROTOCOL"
                    print "Redoing a search for this fragment with a different protocol"
                    protoidx+=1
                    continue


                SELSLIB2.writeSumClusters(CluAll, nameDir + "4_PACK_LIBRARY/", "clusters", ensembles)
            else:
                ensembles, CluAll, rt, et = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                             nameDir + "4_PACK_LIBRARY/clusters.sum",
                                                                             "ROTSOL")
                for key in ensembles.keys():
                    try:
                        if search_inverted_helix and "INV" in key:
                            os.link(model_file_inverted, os.path.join(ensemblesDir, ensembles[key]))
                        else:
                            os.link(model_file, os.path.join(ensemblesDir, ensembles[key]))
                    except:
                        pass

            
            for clund in CluAll:
                if len(clund["heapSolutions"].asList()) > 0:
                    toExit = False
                    break

            if toExit:
                print "Packing has excluded everything"
                # TODO: wait for the all processes or threads to finish #NS added conditions
                if i == 1 :
                    print "EXIT"
                    sys.exit(0)
                else:
                    print "SKIPPING"
                    break

            SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput, "ARCIMBOLDO", "PACK",
                                     ensembles, i, readSum=nameDir + "4_PACK_LIBRARY/clusters.sum",coiled_coil=coiled_coil)
            arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)
            sumPACK = nameDir + "4_PACK_LIBRARY/clusters.sum"
        else:
            SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput, "ARCIMBOLDO", "PACK",
                                     ensembles, i, makeEmpty=True, readSum=folsum,coiled_coil=coiled_coil)
            arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)
            USE_TRANSLA = False
            sumPACK = nameDir + "3_FTF_LIBRARY/clusters.sum"

        if (search_inverted_helix and search_inverted_helix_from_fragment <= 0) or (search_inverted_helix and i == search_inverted_helix_from_fragment):
            sumPACK = nameDir + "4.5_INVERTED_LIBRARY/clusters.sum"

        if swap_model != None:
            #NOTE: In principle I think this should never affect the inverted helix options but take in mind to revise it
            print "MODEL_FILE is", model_file
            shutil.copyfile(swap_model, model_file)

            """
            for key in ensembles.keys():
                if key.startswith("ensembleID"):
                        fra = int(key.split("FR")[-1].split("_")[0])
                        if fra+1 == i:
                                ensembles[key] = swap_model
                else:
                                ensembles[key] = swap_model
            """
        if (search_inverted_helix and search_inverted_helix_from_fragment <= 0) or (search_inverted_helix and i == search_inverted_helix_from_fragment):
            ensembles, CluAll = SELSLIB2.generateInvertedHelices(ensembles,CluAll,top_inverted_solution_per_cluster)
            SELSLIB2.writeSumClusters(CluAll, nameDir + "4.5_INVERTED_LIBRARY/", "clusters", ensembles)
            ensembles, CluAll, rt, et = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                         nameDir + "4.5_INVERTED_LIBRARY/clusters.sum",
                                                                         "ROTSOL")
            for key in ensembles.keys():
                try:
                    if search_inverted_helix and "INV" in key:
                        os.link(model_file_inverted, os.path.join(ensemblesDir, ensembles[key]))
                    else:
                        os.link(model_file, os.path.join(ensemblesDir, ensembles[key]))
                except:
                    pass

        # Rigid body refinement

        if not os.path.exists(os.path.join(nameDir, "5_RNP_LIBRARY/clusters.sum")) and not toExit:  #NS: added condition on toExit

            SystemUtility.open_connection(DicGridConn, DicParameters, cm)


            #NS: retrieve the dictionary of rotation names in a json file in case a run has to be restarted from a further step
            if ArcimboldoLOW and spaceGroup not in ["P1", "P 1"]:
                with open(os.path.join(nameDir,"3_FTF_LIBRARY/","dicEqRots.json")) as f:
                    dicEqRots=json.load(f)
            else:
                dicEqRots=None

            ensero = copy.deepcopy(ensembles)

            if ArcimboldoLOW:
                LOWLIB.printHeader(jobType="startRNPOnePerCluster",fragNumber=i,protocolNumber=proto)

            (nqueue5, convino) = SELSLIB2.startRNPOnePerCluster(DicParameters=DicParameters, cm=cm, sym=sym,
                                                                nameJob="5_RNP_LIBRARY_" + str(i), ClusAll=CluAll,
                                                                ensembles=ensembles,
                                                                outputDire=nameDir + "5_RNP_LIBRARY/", mtz=mtz, MW=MW,
                                                                NC=NC, F=F, SIGF=SIGF, Intensities=Intensities,
                                                                Aniso=Aniso, normfactors=normfactors,
                                                                tncsfactors=tncsfactors, nice=nice, RMSD=RMSD, lowR=99,
                                                                highR=res_refin, spaceGroup=spaceGroup, frag_fixed=i,
                                                                tops=topNextFragment, usePDO=usePDO, sampl=sampl_refin,
                                                                VRMS=VRMS, USE_TNCS=USE_TNCS, USE_RGR=False,BFAC=BFAC,
                                                                BULK_FSOL=BULK_FSOL, BULK_BSOL=BULK_BSOL,
                                                                RNP_GYRE=RNP_GYRE,
                                                                consider_inverted_helix=search_inverted_helix,
                                                                phased_TF=phased_TF,protocol=0,
                                                                TopFilesRNP=TopFilesRNP,dicEqRots=dicEqRots)
            SystemUtility.endCheckQueue()

            #These options are changed if LOW is activated
            nDefinitiveSolFound = 1000
            exclZRNP=0.0

            if ArcimboldoLOW:
                LOWLIB.printHeader(jobType="evaluateFTF",fragNumber=i,protocolNumber=proto)
                nDefinitiveSolFound = 1000 #NS KEEP only n solutions with good TFZ== during RNP for Arcimboldo low
                exclZRNP= excludeZscoreRNP if i>=cycleNExcludeZscoreRNP else 0.0  # this way you can set no filter on the first cycle only

            CluAll, ensembles, tolose = SELSLIB2.evaluateFTF(DicParameters=DicParameters, cm=cm, sym=sym,
                                                             DicGridConn=DicGridConn,nameJob="5_RNP_LIBRARY_" + str(i),
                                                             outputDicr=nameDir + "5_RNP_LIBRARY/", nqueue=nqueue5,
                                                             ensembles=ensembles, excludeZscore=excludeZscore,
                                                             fixed_frags=i, quate=quate, mode="RNP", laue=laue,
                                                             listNCS=ncs, clusteringMode=clusteringAlg,
                                                             cell_dim=cell_dim, thresholdCompare=thresholdCompare,
                                                             evaLLONG=evaLLONG,applyNameFilter=False, convNames=convino,
                                                             tops=topRNP,isArcimboldo=True, renamePDBs=True,
                                                             excludeZscoreRNP=excludeZscoreRNP, cleanshsol=cleanshsol,
                                                             make_positive_llg=False, is_verification=False, nDefinitiveSolFound=nDefinitiveSolFound,use_tNCS=USE_TNCS)


            if ArcimboldoLOW and use_protocols and excludeZscoreRNP and (not CluAll):
                print "No solution passed the TFZ cut off criteria after rigid body refinement (TFZ==%s)"%excludeZscoreRNP
                print "Redoing a search for this fragment with a different protocol"
                firstProtocol=False
                continue
                excludeZscore=tmpZscore  #setting the excludeZscore back to what it was

            SystemUtility.endCheckQueue()




            if ensembles_mode:
                SELSLIB2.substitute_single_solution_with_full_ensemble(ensero,ensembles,CluAll,nameDir + "5_RNP_LIBRARY/")

            ensembles["ensemble1"] = os.path.join(ensemblesDir, os.path.basename(model_file))
            if search_inverted_helix:
                ensembles["ensembleI1"] = os.path.join(ensemblesDir, os.path.basename(model_file_inverted))

            if USE_TRANSLA:
                CluAll, ensembles = SELSLIB2.mergeZSCOREinRNP(DicParameters, sumPACK, CluAll, ensembles,
                                                              isARCIMBOLDO_LITE=True)
                SELSLIB2.writeSumClusters(CluAll, nameDir + "5_RNP_LIBRARY/", "clusters", ensembles)
            #NOTE CM I think this will give a problem in P1 for a first fragment, attempting to solve it
            else:
                SELSLIB2.writeSumClusters(CluAll, nameDir + "5_RNP_LIBRARY/", "clusters", ensembles)

        else:
            ensembles, CluAll, rt, et = SELSLIB2.readClustersFromSUMToDB(DicParameters,
                                                                         nameDir + "5_RNP_LIBRARY/clusters.sum",
                                                                         "ROTSOL")
            for key in ensembles.keys():
                try:
                    if search_inverted_helix and "INV" in key:
                        os.link(model_file_inverted, os.path.join(ensemblesDir, ensembles[key]))
                    else:
                        os.link(model_file, os.path.join(ensemblesDir, ensembles[key]))
                except:
                    pass


        #######################################################################
        # Updating the rmsd of any fixed fragment with the vrms optimization  #
        # This is performed every time VRMS = True                            #
        # Moreover if UPDATE_RMSD = True then also the new rmsd for searching #
        # a new fragment is updated to the minimum vrms obtained              #
        #######################################################################

        if VRMS and UPDATE_RMSD_FIXED:
            newCluAll = []
            newRMSD=0     #To write in the txtmod file for ARCILOW
            for clu in CluAll:
                newclu = {"heapSolutions":ADT.Heap()}
                for item in clu["heapSolutions"]:
                    prio,rota = item
                    if "vrms" in rota:  #NS TMP FIX
                        print("Changing RMS for VRMS: %s --> %s"%(rota["rmsd"], rota["vrms"]))
                        rota["rmsd"] = rota["vrms"]
                        newRMSD = rota["vrms"]

                       # if "fixed_frags" in rota:    NS: if my fixed fragment is another protein, I don't want it to be updated with the current RMSD
                       #    for rol in rota["fixed_frags"]:
                       #        rol["rmsd"] = rota["vrms"]
                    else:
                        print("WARNING: KEY 'vrms' not in rota: %s"%rota)
                        newRMSD = rota["rmsd"]

                    newclu["heapSolutions"].push(prio,rota)
                newCluAll.append(newclu)
            CluAll = newCluAll

        if VRMS and UPDATE_RMSD:
            RMSD = min([item[1]["vrms"] for clu in CluAll for item in clu["heapSolutions"].asList()])

        if ArcimboldoLOW and VRMS and UPDATE_RMSD_FIXED:  #For having the VRMS in place of RMSD in LOW
            print("Overwriting RMSD by VRMS in 5_RNP_LIBRARY/clusters.sum for fragment %s"%i)
            SELSLIB2.writeSumClusters(CluAll, nameDir + "5_RNP_LIBRARY/", "clusters", ensembles)

        SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput, "ARCIMBOLDO", "RNP",
                                 ensembles, i, readSum=nameDir + "5_RNP_LIBRARY/clusters.sum",coiled_coil=coiled_coil)
        arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)
        # ensembles = SELSLIB2.readClustersFromSUMToDB(DicParameters, nameDir+"5_RNP_LIBRARY/clusters.sum","ROTSOL")

        SELSLIB2.writeGraphSumClusters(nameDir + "5_RNP_LIBRARY/clusters.sum")


        if USE_OCC and not os.path.exists(os.path.join(nameDir, "5.5_OCC_LIBRARY")):
            SystemUtility.open_connection(DicGridConn, DicParameters, cm)

            #print "############################" #NS ADD
            #print "# startOCC (after RNP, fragment %s)"%i
            #print "############################"
            (nqueue15, c) = SELSLIB2.startOCC(DicParameters=DicParameters, cm=cm, sym=sym, nameJob="5.5_OCC_" + str(i),
                                              dir_o_liFile=nameDir + "5_RNP_LIBRARY/",
                                              outputDire=nameDir + "5.5_OCC_LIBRARY/", mtz=mtz, MW=MW, NC=NC, F=F,
                                              SIGF=SIGF, Intensities=Intensities, Aniso=Aniso, normfactors=normfactors,
                                              tncsfactors=tncsfactors, nice=nice, RMSD=RMSD, lowR=99, highR=res_refin,
                                              final_rot=75, save_rot=75, frag_fixed=1, spaceGroup=spaceGroup,
                                              sampl=sampl_refin, ellg=None, nres=None, rangeocc=None, merge=None,
                                              occfrac=None, occoffset=None, ncycles=None, VRMS=VRMS, BFAC=BFAC,
                                              BULK_FSOL=BULK_FSOL, BULK_BSOL=BULK_BSOL,formfactors=formfactors)

            SystemUtility.endCheckQueue()
            SELSLIB2.evaluateOCC(DicParameters, cm, sym, DicGridConn, "5.5_OCC_" + str(i), nameDir + "5.5_OCC_LIBRARY/",
                                 nqueue15, c)

        if USE_OCC:
            inputDir = nameDir + "5.5_OCC_LIBRARY/"
        else:
            inputDir = nameDir + "5_RNP_LIBRARY/"

        CC_Val1 = None

        if not os.path.exists(os.path.join(nameDir, "./6_EXPVAL_LIBRARY/solCC.sum")):
            SystemUtility.open_connection(DicGridConn, DicParameters, cm)

            if ArcimboldoLOW:
                LOWLIB.printHeader(jobType="startExpansion",fragNumber=i,protocolNumber=proto)

            # NS expansion to evaluate initCC
            # It will look for all .pdb files present in "5_RNP_LIBRARY/" and expand them
            (nqueue6, convNames6) = SELSLIB2.startExpansion(cm, sym, "6_EXPVAL_" + str(i),
                                                            nameDir + "6_EXPVAL_LIBRARY/", hkl, ent, nice, cell_dim,
                                                            spaceGroup, shlxLinea0, inputDir, fragAnom=fragAnom,**startExpAnomDic)  #NS ANOM: could already perform ha search at this point

            # print "############################" #NS ADD
            # print "# evaluateExp_CC (fragment %s, protocol %s)"%(i,proto)
            # print "############################"
            SystemUtility.endCheckQueue()

            #Option to filter by anomalous criterions peak height and PattScore (lst file with no ha are always filtered out) 
            filterPattAndHeight=False
            if ANOMALOUS:
                #New entry of filtered out solutions for cluster i
                if str(i) not in solutions_filtered_out:
                    solutions_filtered_out[str(i)]={}
                    
                solutions_filtered_out[str(i)]["6_EXPVAL_"]=[]

                #IT seems better not to have the Patterson filtering for the first fragment
                filterPattAndHeight=False if i < filterLiteFromFragNumber else True
                    

                #For Lite, convNames6 is a dictionnary with entries of the type '5.pda': '/localdata/nicolas/TRIAL_CROSSF/hell_anomalousRELOADED/RUN/ens1_frag1/5_RNP_LIBRARY/0/ensembleIDxx0FR0_7-32.pdb'                          
                llgdic= ANOMLIB.llgdic(convNames6, CluAll, isLite=True)  #Get the llg and zscore for all solutions
                CC_Val1, eliminatedSol = SELSLIB2.evaluateExp_CC(DicParameters=DicParameters, cm=cm, sym=sym, DicGridConn=DicGridConn, nameJob="6_EXPVAL_" + str(i), 
                                                  outputDicr=nameDir + "6_EXPVAL_LIBRARY/", nqueue=nqueue6, convNames=convNames6, isArcimboldo=True,
                                                  usePDO=usePDO, savePHS=savePHS, archivingAsBigFile=archivingAsBigFile,
                                                  phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim, anomDic=startExpAnomDic, pattersonPeaks=PattersonPeaksData, filterPattAndHeight=filterPattAndHeight,llgdic=llgdic)


                # Filter out the eliminated solutions from the heap list
                if not CC_Val1:
                    print("\nWARNING: the anomalous signal scoring has eliminated all the solutions, you may try again with less restrictive constraints")
                    print("Quitting now")
                    sys.exit(1)
                else:
                    solutions_filtered_out[str(i)]["6_EXPVAL_"] +=  eliminatedSol
                    print("REMARK:, eliminated solutions")
                    print(solutions_filtered_out[str(i)]["6_EXPVAL_"])
                    if len(solutions_filtered_out[str(i)]["6_EXPVAL_"])>0:
                        ANOMLIB.saveFilteredSol(os.path.join(ANOMDIR,'filteredSol.json'),solutions_filtered_out)
                        CluAll = ANOMLIB.filterCluAll(CluAll, solutions_filtered_out[str(i)]["6_EXPVAL_"], LIMIT_CLUSTER=i )

            else:                
                CC_Val1 = SELSLIB2.evaluateExp_CC(DicParameters=DicParameters, cm=cm, sym=sym, DicGridConn=DicGridConn, nameJob="6_EXPVAL_" + str(i), 
                                                  outputDicr=nameDir + "6_EXPVAL_LIBRARY/", nqueue=nqueue6, convNames=convNames6, isArcimboldo=True,
                                                  usePDO=usePDO, savePHS=savePHS, archivingAsBigFile=archivingAsBigFile,
                                                  phs_fom_statistics=phs_fom_statistics, fragNumber=i, spaceGroupNum=sg_number, cell_dim=cell_dim)
        else:
            CC_Val1, con = SELSLIB2.readCCValFromSUM(os.path.join(nameDir, "./6_EXPVAL_LIBRARY/solCC.sum"))
            if ANOMALOUS and os.path.exists(os.path.join(ANOMDIR,'filteredSol.json')):     #If the program has stopped, it can retrieve the filtered solutions from here
                #Retrieve any filtered out solutions if they exist in json
                solutions_filtered_out=ANOMLIB.retrieveFilteredSol(os.path.join(ANOMDIR,'filteredSol.json'))
                print("REMARK: retrieving filtered-out solution list (anomalous scoring) from %s"%os.path.join(ANOMDIR,'filteredSol.json'))

        if usePDO:
            if not useFIXED:
                for key in ensembles:
                    if "INV" in key:
                        try:
                            keydes = key.split("xx")[1]
                            newfile = os.path.join(ensemblesDir, "thinverted" + str(i) + "_0_0xx" + keydes + ".pdb")
                            ensembles[key] = newfile
                            # print key,"....",newfile
                        except:
                            pass
                    else:
                        try:
                            keydes = key.split("xx")[1]
                            newfile = os.path.join(ensemblesDir, "th" + str(i) + "_0_0xx" + keydes + ".pdb")
                            ensembles[key] = newfile
                            # print key,"....",newfile
                        except:
                            pass
            else:
                for key in ensembles:
                    try:
                        newfile = os.path.join(ensemblesDir, os.path.basename(ensembles[key]))
                        ensembles[key] = newfile
                    except:
                        pass

            for dix in CC_Val1:
                fileis = dix["corresp"]
                oldfile = fileis[:-4] + ".pdo"
                newfile = os.path.join(ensemblesDir, os.path.basename(fileis))
                try:
                    os.link(oldfile, os.path.join(ensemblesDir, newfile))
                except:
                    pass

        if os.path.exists(ent) and i == 1 and os.path.exists(os.path.join(current_directory, nameOutput + "_mosed")):
            mosed_dir = os.path.join(current_directory, nameOutput + "_mosed")
            CC_Val1, con = SELSLIB2.readCCValFromSUM(os.path.join(nameDir, "./6_EXPVAL_LIBRARY/solCC.sum"))
            # SELSLIB2.PDA_same_origin_cell_sym(sym, i, DicParameters, CC_Val1, con, hkl, cell_dim, spaceGroup, shlxLineaP, mosed_dir, os.path.join(current_directory,"./pda_"+str(i)+"frag_same_origin/"))
            SELSLIB2.analyze_all_solutions(sym, i, DicParameters, CC_Val1, con, hkl, cell_dim, spaceGroup, shlxLineaP,
                                           mosed_dir,
                                           os.path.join(current_directory, "./pda_" + str(i) + "frag_same_origin/"))

        SELSLIB2.writeOutputFile(lock, DicParameters, CluAll, current_directory, nameOutput, "ARCIMBOLDO", "INITCC",
                                 ensembles, i, path1=nameDir + "6_EXPVAL_LIBRARY/solCC.sum",
                                 readSum=nameDir + "5_RNP_LIBRARY/clusters.sum",coiled_coil=coiled_coil)
        arci_output.generateHTML(lock, current_directory, nameOutput,coiled_coil=coiled_coil)
        
        #NS pass to the next fragment only if a solution has been found (CluAll contains something, for the low res case)
        if CluAll:
            i+=1

            if ArcimboldoLOW :
                firstProtocol=True  #index of the protocol array to use
                triedprotocols=[] #reinitialize the triedprotocols array
                if not glob.glob(os.path.join(nameDir,"model_file*.txtmod")):
                    #Write down the protocol that worked for this fragment, mvrms etc
                    outens = open(os.path.join(nameDir,"model_file"+modelLowName+".txtmod"), "w") #NS, to keep track of which model from the ARCIMBOLDO LOW script we are dealing with
                    outens.write("Protocol used: %s\n"%proto)
                    outens.write("model_file: %s\n"%model_file)
                    outens.write("vrms: %s"%newRMSD)
                    outens.close()


            print "\n*************END OF FRAGMENT %s SEARCH*************\n"%str(i-1)

            inputDir = CluAll
            if os.path.exists(nameDir + "7_PREPARED/"):
                for r, subF, fi in os.walk(nameDir + "7_PREPARED/"):
                    for fileu in fi:
                        pdbf = os.path.join(r, fileu)
                        if pdbf.endswith(".pdb"):
                            os.remove(pdbf)

            convNames14 = SELSLIB2.startPREPARE(cm, sym, "7_PREPARED_" + str(i), CC_Val1, nameDir + "7_PREPARED/", cell_dim,
                                                spaceGroup, topExp, topNext=topNextFragment)
        else:
            if ArcimboldoLOW:
                firstProtocol=False
                continue
            print("\nIt seems that there are no solutions left!\n")
            break



    #END OF THE WHILE LOOP OVER i (fragment)
    CC_Vals = []
    cons = None

    for i in range(1, NSEARCH + 1):
        nameDir = os.path.join(current_directory, "ens1_frag" + str(i) + "/")

        if os.path.exists(nameDir + "skip"):
            print "Skipping fragment ", i
            continue

        # NS NOTE: It would be good to have explicit names about what this is returning
        enst, clur, arp, frap = SELSLIB2.readClustersFromSUMToDB(DicParameters, nameDir + "5_RNP_LIBRARY/clusters.sum",
                                                                 "ROTSOL")

        # NS NOTE: Where the dictionnary of solutions CC_Val1 is created from solCC.sum, con1 (convnames seems to be useless here)
        CC_Val1, con1 = SELSLIB2.readCCValFromSUM(os.path.join(nameDir, "./6_EXPVAL_LIBRARY/solCC.sum"))

        # NS NOTE: Selections of the solutions according to a scheme (by default AUTO for A_LITE and LLG for BORGES and SHREDDER )
        CC_Vals = SELSLIB2.unifyCC2(CC_Vals, CC_Val1, [], enst, clur, suffixA="", suffixB="", suffixC="", llgn=2,
                                    solution_sorting_scheme=solution_sorting_scheme)

    if force_core != None:
        sym.PROCESSES = force_core

    if distribute_computing == "multiprocessing":
        topExp = sym.PROCESSES - 1

    # NOTE: Temporary Activated
    if distribute_computing == "multiprocessing" and sym.PROCESSES - 1 < 8:
        force_exp = True

    if force_exp:
        topExp = 2 * (sym.PROCESSES - 1)

    # NS NOTE: The solutions to be sent for exansions are transmitted via the CC_Vals dictionary of solutions, the selection happens in unifyCC2
    convNames14 = SELSLIB2.startPREPARE(cm, sym, "7_PREPARED_ALL", CC_Vals,
                                        os.path.join(current_directory, "EXP_PREPARE/"), cell_dim, spaceGroup, topExp,
                                        topNext=topNextFragment)



    if nautocyc > 0 and len(CC_Vals) > 0:
        # NS: custom number of autotracing cycles
        if nAutoTracCyc >0:
            nautocyc = nAutoTracCyc +1

        #NS ANOM: write a COOT script to load the trace and heavy atoms maps as well as the corresponding .phs files and load them automatically
        ANOMLIB.writeCOOTscript(current_directory,spaceGroup=spaceGroup, unitCell=cell_dim)

        # Here the pdb files to be extended will be looked for in the directory EXP_PREPARE (from the previous startPREPARE funcions)
        SELSLIB2.shelxe_cycles(lock=lock, DicParameters=DicParameters, cm=cm, sym=sym, DicGridConn=DicGridConn,
                               output_directory=current_directory, nameOutput=nameOutput,
                               dirPathPart=os.path.join(current_directory, "./EXP_PREPARE"),
                               fragdirectory=current_directory, fromNcycles=1, toNcycles=nautocyc, mtz=mtz,MW=MW, NC=NC,
                               F=F, SIGF=SIGF, res_refin=res_refin, Intensities=Intensities, Aniso=Aniso,
                               normfactors=normfactors, tncsfactors=tncsfactors, nice=nice, RMSD=RMSD, quate=quate,
                               laue=laue, ncs=ncs, spaceGroup=spaceGroup, hkl=hkl, ent=ent,cell_dim=cell_dim,
                               shlxLinea0=shlxLinea0, shlxLineaB=shlxLinea1, shlxLineaLast=shlxLineaLast,
                               USE_PACKING=USE_PACKING, USE_TRANSLA=USE_TRANSLA, USE_TNCS=USE_TNCS, 
                               solution_verification=solution_verification,
                               solution_sorting_scheme=solution_sorting_scheme, topExp=topExp,
                               topNextFragment=topNextFragment,startExpAnomDic=startExpAnomDic, pattersonPeaks=PattersonPeaksData, llgdic=llgdic, nBunchAutoTracCyc=nBunchAutoTracCyc)



    SystemUtility.open_connection(DicGridConn, DicParameters, cm)

    if cm != None and hasattr(cm, "channel"):
        print cm.change_remote_dir("..")
        print cm.get_remote_pwd()

    try:
        if hasattr(cm, "channel"):
            # REMOVE THE FULL LIBRARY IN THE REMOTE SERVER
            actualdi = cm.get_remote_pwd()
            print cm.change_remote_dir("..")
            print cm.remove_remote_dir(inputDir, inputDir)
            print cm.remove_remote_dir(DicParameters["nameExecution"])
            print cm.change_remote_dir(actualdi)
    except:
        pass

    SystemUtility.close_connection(DicGridConn, DicParameters, cm)
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
            print traceback.print_exc(file=sys.stdout)

        try:
            signal.signal(signal.SIGKILL,SystemUtility.signal_term_handler)
        except:
            print traceback.print_exc(file=sys.stdout)

        try:
            signal.signal(signal.SIGINT,SystemUtility.signal_term_handler)
        except:
            print traceback.print_exc(file=sys.stdout)


    head1 = """
.-----------------------------------------------------------------------------------------------------------.
|          _____   _____ _____ __  __ ____   ____  _      _____   ____        _      _____ _______ ______   |
|    /\   |  __ \ / ____|_   _|  \/  |  _ \ / __ \| |    |  __ \ / __ \      | |    |_   _|__   __|  ____|  |
|   /  \  | |__) | |      | | | \  / | |_) | |  | | |    | |  | | |  | |_____| |      | |    | |  | |__     |
|  / /\ \ |  _  /| |      | | | |\/| |  _ <| |  | | |    | |  | | |  | |_____| |      | |    | |  |  __|    |
| / ____ \| | \ \| |____ _| |_| |  | | |_) | |__| | |____| |__| | |__| |     | |____ _| |_   | |  | |____   |
|/_/    \_\_|  \_\\\\_____|_____|_|  |_|____/ \____/|______|_____/ \____/      |______|_____|  |_|  |______|  |
#-----------------------------------------------------------------------------------------------------------#
                                    Requires Phaser >= 2.8.x and Shelxe 2018
    """
    print colored(head1, 'cyan')
    print """
    Institut de Biologia Molecular de Barcelona --- Consejo Superior de Investigaciones Científicas
                     I.B.M.B.                                            C.S.I.C.

                    Department of Structural Biology - María de Maeztu Unit of Excellence
                                         Crystallographic Methods Group
                       http://www.sbu.csic.es/research-groups/crystallographic-methods/

    In case this result is helpful, please, cite:

    Phaser crystallographic software
    McCoy, A. J., Grosse-Kunstleve, R. W., Adams, P. D., Winn, M. D., Storoni, L. C. & Read, R. J.
    (2007) J Appl Cryst. 40, 658-674.

    Extending molecular-replacement solutions with SHELXE
    Thorn, A. & Sheldrick, G. M.
    (2013) Acta Cryst. D69, 2251-2256.

    ARCIMBOLDO-LITE: single-workstation implementation and use
    Sammito, M., Millan, C.,Frieske, D., Rodriguez-Freire, E., Borges, R. J., & Uson, I.
    (2015) Acta Cryst. D71, 1921-1939.

    """
    print "Email support: ", colored("bugs-borges@ibmb.csic.es", 'blue')
    print "\nARCIMBOLDO_LITE website: ", colored("http://chango.ibmb.csic.es/arcimboldo", 'blue')
    print "\n"
    usage = """usage: %prog [options] example.bor"""

    parser = OptionParser(usage=usage)
    # parser.add_option("-x", "--XGUI", action="store_true", dest="gui", help="Will automatically launch the GUI Option Viewer to read the output", default=False)
    parser.add_option("-v", "--devhelp", action="store_true", dest="devhelp",
                      help="Print customizable parameters for developers", default=False)
    parser.add_option("-b", "--borconf", action="store_true", dest="borconf",
                      help="Print customizable parameters for users", default=False)
    parser.add_option("-f", "--borfile", dest="borfile", help="Create a template .bor file", metavar="FILE")

    (options, args) = parser.parse_args()

    if options.borfile != None:
        f = open(options.borfile, "w")
        text_file = """
#NOTE: for a full documentation of the parameters, please read the manual at: http://chango.ibmb.csic.es/manual
#NOTE: For optional parameters default values are quoted.
#A tutorial on how to run ARCIMBOLDO_LITE can be found our website at: http://chango.ibmb.csic.es/tutorial_arc

[CONNECTION]:
#NOTE: following is default
distribute_computing: multiprocessing
#NOTE: other modes are:
#distribute_computing: local_grid
#setup_bor_path: /path/to/setup.bor

#NOTE: if the RSA private key is not found or invalid, a password is required
#distribute_computing: remote_grid
#setup_bor_path: /path/to/setup.bor
#remote_frontend_passkey: ~/.ssh/id_rsa

[GENERAL]:
#NOTE: following are mandatory
working_directory= /path/to/workdir
mtz_path: %(working_directory)s/data.mtz
hkl_path: %(working_directory)s/data.hkl

[ARCIMBOLDO]
#NOTE: following are mandatory
name_job: example_name
molecular_weight:
f_label: F
sigf_label: SIGF
#NOTE: or alternatively use intensities
#i_label: I
#sigi_label: SIGI
number_of_component: 1
fragment_to_search: 2
helix_length: 14
#NOTE: to use different helix lengths write instead "helix_length_n"
#specifying the length for EACH search fragment
#helix_length_1: 15
#helix_length_2: 13
#NOTE: to use a specific pdb model as search fragment, comment out "helix_length" and set:
#model_file: /path/to/the/file.pdb
#NOTE: to use a different model for each search fragment, specify "model_file_n"
#    for EACH fragment
#model_file_1: /path/to/file1.pdb
#model_file_2: /path/to/file2.pdb
#NOTE: to use a compound model use in "model_file" the name of the compound
#      supported list is commented in following:
#model_file: Fe2S2
#model_file: Fe2S4
#model_file: heme
#NOTE: following are optional. -1 means PHASER defaults
#pack_clashes: 0
#TNCS: True
#resolution_rotation: 1.0
#sampling_rotation: -1
#resolution_translation: 1.0
#sampling_translation: -1
#resolution_refinement: 1.0
#sampling_refinement: -1
#NOTE: the program automatically configure the shelxe_line but you can decomment it and use your own
#shelxe_line:

[LOCAL]
#    Third party software paths
path_local_phaser:
path_local_shelxe:
"""
        f.write(text_file)
        f.close()
        sys.exit(0)

    if options.borconf:
        print
        print colored("""#""", 'blue') + colored('NOTE', 'yellow') + colored(
            """: for a full documentation of the parameters, please read the manual at: """, 'blue') + colored(
            """ http://chango.ibmb.csic.es/manual""", 'red')
        print

        print colored("""#""", 'blue') + colored('NOTE', 'yellow') + colored(
            """: For optional parameters default values are quoted.""", 'blue')
        print colored("""#Tutorial can be found in the website.""", 'blue')
        print """
[CONNECTION]:
"""
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(': following is default', 'blue'),
        print """
distribute_computing: multiprocessing
"""
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(': other modes are:', 'blue'),
        print colored("""
#distribute_computing: local_grid
#setup_bor_path: /path/to/setup.bor

""", 'blue')
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
            ': if the RSA private key is not found or invalid, a password is required', 'blue'),
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

[ARCIMBOLDO]
"""
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(': following are mandatory', 'blue'),
        print """
name_job: example_name
molecular_weight:
f_label: F
sigf_label: SIGF
"""
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(': or alternatively use intensities',
                                                                               'blue')
        print colored("""
#i_label: I
#sigi_label: SIGI
""", 'blue')
        print """
number_of_component: 1
fragment_to_search: 2
helix_length: 14
"""
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
            ': to use different helix lengths write instead "helix_length_n"\n#\tspecifying the length for EACH search fragment',
            'blue'),

        print colored("""
#helix_length_1: 15
#helix_length_2: 13
""", 'blue')
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
            ': to use a specific pdb model as search fragment, comment out "helix_length" and set:', 'blue'),
        print colored("""
#model_file: /path/to/the/file.pdb
""", 'blue')
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
            ': to use a different model for each search fragment, specify "model_file_n"', 'blue'),
        print colored("""
#    for EACH fragment
#model_file_1: /path/to/file1.pdb
#model_file_2: /path/to/file2.pdb
""", 'blue')
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
            ': to use a compound model use in "model_file" the name of the compound, supported list is commented in following:',
            'blue')
        print colored("""
#model_file: Fe2S2
#model_file: Fe2S4
#model_file: heme
""", 'blue')
        print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
            ': following are optional. -1 means PHASER defaults', 'blue'),
        print colored("""
#NOTE: the program automatically configure the shelxe_line but you can decomment it and use your own
#shelxe_line:
#pack_clashes: 0
#TNCS: True
#resolution_rotation: 1.0
#sampling_rotation: -1
#resolution_translation: 1.0
#sampling_translation: -1
#resolution_refinement: 1.0
#sampling_refinement: -1
""", 'blue'),
        print """
[LOCAL]""",
        print colored("""
#    Third party software paths
#    Requires PHASER 2.7.x""", 'blue'),
        print """
path_local_phaser:
path_local_shelxe:
"""
    if options.devhelp:
        print "The selected option is only available for the developers team. Please insert the password:"
        command = raw_input("<> ")
        if hashlib.sha224(command).hexdigest() == "d286f6ad6324a21cf46c7e3c955d8badfdbb4a14d630e8350ea3149e":
            print """

FULL LIST OF PARAMETERS FOR ARCIMBOLDO:

[CONNECTION]:
distribute_computing: multiprocessing
#distribute_computing: local_grid
#distribute_computing: remote_grid
#remote_frontend_passkey: ~/.ssh/id_rsa
#setup_bor_path:

[GENERAL]:
#NOTE: following are mandatory
working_directory= /path/to/workdir
mtz_path: %(working_directory)s/data.mtz
hkl_path: %(working_directory)s/data.hkl
ent_path: %(working_directory)s/structure.ent

[ARCIMBOLDO]
name_job: example_name
molecular_weight:
number_of_component:
i_label: I
sigi_label: SIGI
#Or alternatively
#f_label: F
#sigf_label: SIGF
fragment_to_search: 2
helix_length: 14
"""
            print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
                ': to use a different helix length for each fragment, use instead "helix_length_n"\n\tspecifying the length for EACH fragment to search',
                'blue'),

            print colored("""
#helix_length_1: 15
#helix_length_2: 13
""", 'blue')
            print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
                ': to use a specific pdb model as search fragment, comment out "helix_length" and set:', 'blue'),
            print colored("""
#model_file: /path/to/the/file.pdb
""", 'blue')
            print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
                ': to use a different model for each search fragment, specify "model_file_n"', 'blue'),
            print colored("""
#    for EACH fragment
#model_file_1: /path/to/file1.pdb
#model_file_2: /path/to/file2.pdb
""", 'blue')
            print """
rmsd: 0.2
spacegroup:
rotation_clustering_algorithm: rot_matrices
threshold_algorithm: 15
resolution_rotation: 1.0
sampling_rotation: -1
number_of_component: 1
resolution_translation: 1.0
sampling_translation: -1
resolution_refinement: 1.0
sampling_refinement: -1
exclude_llg: 0
exclude_zscore: 0
use_packing: True
pack_clashes: 0
randomize_trans_per_rot: 0
TNCS: True
VRMS: False
VRMS_GYRE: False
BFAC: False
SIGR: 0.0
SIGT: 0.0
solution_sorting_scheme: AUTO
#solution_sorting_scheme: LLG
#solution_sorting_scheme: ZSCORE
#solution_sorting_scheme: INITCC
#solution_sorting_scheme: COMBINED
GIMBLE: False
PACK_TRA: False
BASE_SUM_FROM_WD: True
# 0.35 Default Phaser
BULK_FSOL: -1
# 45 Default Phaser
BULK_BSOL: -1
GYRE_PRESERVE_CHAINS: False
# NOTE: if Aniso is set to True, anisotropy and tncs correction will be recomputed in each phaser step
ANISO: False
nice: 0

#NOTE: the program automatically configure the shelxe_line but you can decomment it and use your own
#NOTE: shelxe_line_last corresponds to the line that will be applied in the last cycle of autotracing
#shelxe_line:
#shelxe_line_last:

noDMinitcc: True
savePHS: False
phs_fom_statistics: False
OCC: False
usePDO: False
archivingAsBigFile: False
fixed_models_directory:
search_inverted_helix: False
search_inverted_helix_from_fragment: -1
top_inverted_solution_per_cluster: 1000
solution_verification: False
range_rmsd_tra: 0.0
topFRF_1: 1000
topFTF_1: 150
topPACK_1: 10000
topRNP_1: 1000
topExp_1: 60
topFRF_n: 200
topFTF_n: 150
topPACK_n: 10000
topRNP_n: 150
topExp_n: 60
RNCS_MATL = []
force_core = -1
force_exp = False
update_rmsd = False
coiled_coil: False

[LOCAL]""",
            print colored("""
#    Third party software paths
#    Requires PHASER 2.7.x""", 'blue'),
            print """
path_local_phaser:
path_local_shelxe:
"""
            sys.exit(0)
        else:
            print "Sorry. You have no permission."
            sys.exit(0)

    if len(args) < 1:
        parser.print_help()
        sys.exit(0)

    input_bor = os.path.abspath(args[0])
    print '\n Reading the bor configuration file for ARCIMBOLDO_LITE at ',input_bor
    if not os.path.exists(input_bor):
        print 'Sorry, the given path for the bor file either does not exist or you do not have the permissions to read it'
        sys.exit(1)
    path_module = os.path.dirname(__file__)

    Config = ConfigParser.ConfigParser()

    try:
        startARCIMBOLDO(Config, input_bor, startCheckQueue=True)
    except SystemExit:
        pass
    except:
        print traceback.print_exc(file=sys.stdout)
        if hasattr(sys, '_MEIPASS'):
            print "Exited with errors, temp file was ", sys._MEIPASS, " and was removed before exiting"

if __name__ == "__main__":
    main()