#! /usr/bin/env python
# -*- coding: utf-8 -*-

import cPickle
import ConfigParser
import cStringIO
import datetime
import hashlib
import os
import re
import shutil
import sys
import signal
import subprocess
import threading
import traceback
import warnings
import xml.etree.ElementTree as ET
from optparse import OptionParser

import numpy
from termcolor import colored
from Bio.PDB import PDBExceptions

import ARCIMBOLDO_BORGES
import ARCIMBOLDO_LITE
import arci_output
import alixe_library as al
import BORGES_MATRIX
import Bioinformatics3
import Bioinformatics
import Data
import Grid
import Quaternions
import SELSLIB2
import SystemUtility
import ANOMLIB

warnings.simplefilter("ignore", PDBExceptions.PDBConstructionWarning)

"""ARCIMBOLDO-SHREDDER exploits fragments from distant homologs to phase macromolecular structures. This module
contains the main program"""

#######################################################################################################
#                                              CLASSES                                                #
#######################################################################################################


class inputConfig():
    def __init__(self):
        self.list_all_attr = []

    def get_list_attr(self):
        return self.list_all_attr

    def changeAttr(self, name_keyword, value_keyword):
        """ NS, change one of the tuples of the attribute list"""
        for i,tup in enumerate(self.list_all_attr):
            if tup[0] == name_keyword:
                self.list_all_attr[i] = (name_keyword,type(value_keyword))
                break

    def __setattr__(self, name_keyword, value_keyword):
        # if self.__dict__.has_key(name_keyword):
        #     dict.__setattr__(self,name_keyword, value_keyword)
        # else:
        #     self.__dict__[name_keyword]=value_keyword
        # self.list_all_attr.append((name_keyword,type(value_keyword)))

        # NS: changed on 22 Nov 2018
        if self.__dict__.has_key(name_keyword):
            # Check the list and replace in case the type of value_keyword has changed
            self.changeAttr(name_keyword, value_keyword)

        # Now change / fill the dictionary
        self.__dict__[name_keyword] = value_keyword

    def get_value(self, name_keyword):
        try:
            return self.name_keyword
        except:
            print 'Sorry, ', name_keyword, ' could not be retrieved'

#######################################################################################################
#                                            FUNCTIONS                                                #
#######################################################################################################


def __launchShredExec(SHRED_METHOD, Config, job_type, model_file, trim_to_polyala, maintainCys, current_directory,
                      dirmodels,inpconf):
    """ Generation of the models for the required modality of shredder

    :param SHRED_METHOD: method can be 'spherical', 'sequential','borges_superposition', or 'secondary_structure'
    :type SHRED_METHOD: str
    :param Config: configuration of the run read from the bor and the defaults
    :type Config: Config.Parser object
    :param job_type: keyword for reading the configuration file (ARCIMBOLDO_SHREDDER in this case)
    :type job_type: str
    :param model_file: path to the template model
    :type model_file: str
    :param trim_to_polyala: if True, trim the sidechains of the model and leave only polyalanin
    :type trim_to_polyala: bool
    :param maintainCys: if True, leave the sidechains from cysteines in the model
    :type maintainCys: bool
    :param current_directory: path to working directory
    :type current_directory: str
    :param dirmodels: path where to write the output models
    :type dirmodels: str
    :param inpconf: object with configuration
    :type inpconf: inputConfig object

    Returns:
    For the sequential mode:
        :return howmany:
        :rtype howmany: list
        :return indic: keys are .... and values are e.g. {4: (0, 182), 5: (182, 364), 6: (364, 546), 7: (546, 728), ...}
        :rtype dict:
        :return chunk_range: contains the range plus the step, the mode, and the sidechains treatment
                             e.g. (4, 21, 1, 'omit', True, False)
        :rtype chunk_range: tuple
    For the spherical mode:
        :return dict_oristru: dictionary with the annotation of the template at different levels of structure
        :rtype dict_oristru: dict
        :return model_file: path to the template model file, now modified accordingly
        :rtype model_file: str
    """

    bfacnorm = Config.getboolean(job_type, "BFACNORM")
    if SHRED_METHOD == "sequential":
        chunk_range = (
        int(Config.get(job_type, "SHRED_RANGE").split()[0]), int(Config.get(job_type, "SHRED_RANGE").split()[1]) + 1,
        int(Config.get(job_type, "SHRED_RANGE").split()[2]), Config.get(job_type, "SHRED_RANGE").split()[3],
        trim_to_polyala, maintainCys)
        lim_bott, lim_top, step_size, mode_type, polyBack, mantCys = chunk_range
        fix_ss = None
        remove_coil = None
        if mode_type == "omit" and len(Config.get(job_type, "SHRED_RANGE").split()) >= 6:
            fix_ss = Config.get(job_type, "SHRED_RANGE").split()[4]
            remove_coil = Config.get(job_type, "SHRED_RANGE").split()[5]

        if mode_type not in ["omit", "fragment"]:
            print "Please configure properly the SHRED_RANGE parameter: the mode '" + mode_type + "' does not exists."
            sys.exit(0)
        # NOTE CM modify the full template and not each PDB
        if bfacnorm:
            Bioinformatics3.normalize_bfactors_of_pdb(model_file, 25.0)
        if polyBack:
            print "\nTrimming to polyala is active, sidechains will be removed from the model\n"
            if mantCys:
                print "\nThe cysteine residues will kept their sidechains"
        Bioinformatics3.trim_sidechains_and_cysteines(pdb_model=model_file, poliA=polyBack, cys=mantCys)


        howmany, indic = SELSLIB2.generate_chunks_progressive(pdbf=model_file, from_omit_res=lim_bott,
                                                              to_omit_res=lim_top, step_size=step_size,
                                                              mode_type=mode_type,
                                                              polyBack=polyBack, mantCys=mantCys, fix_ss=fix_ss,
                                                              remove_coil=remove_coil,
                                                              direc=os.path.join(current_directory, dirmodels))
        return howmany, indic, chunk_range
    elif SHRED_METHOD == "spherical":
        community_list=Config.get(job_type,'community_clustering').split()
        if len(community_list) == 3:
            print '\n Community clustering set to: '
            algorithm_community = str(community_list[0])
            if algorithm_community not in ['fastgreedy', 'infomap', 'eigenvectors', 'label_propagation',
                                           'community_multilevel', 'edge_betweenness', 'spinglass', 'walktrap']:
                print 'Sorry, the algorithm for the community clustering is not recognised'
                sys.exit(1)
            print '  algorithm ',algorithm_community
            if community_list[1].lower() == 'true':
                pack_beta_community = True
            else:
                pack_beta_community = False
            if community_list[2].lower() == 'true':
                homogenity_community = True
            else:
                homogenity_community = False
            print '  pack_beta_community ',pack_beta_community
            print '  homogenity_community ', homogenity_community
        else:
            print "\nPlease configure properly the community_clustering parameter"
            sys.exit(1)

        if len(Config.get(job_type, "sphere_definition").split()) < 7:
            print "\nPlease configure properly the sphere_definition parameter. It needs to have at least the following 5 items: size/'default' step 'maintain_coil'/'remove_coil' min_size_alpha min_size_beta"
            print "    size (integer): target size (in residues) of the models to be generated. If left to string 'default', decision will be based on eLLG target"
            print "    step (integer): window to process the sequence and center the model generation"
            print "    maintain_coil or remove_coil or partial_coil_n(string): trim the model removing the coil, leave it as given or add n residues to each secondary structure"
            print "    min_size_alpha (int): minimum size (in residues) for alpha helices"
            print "    min_size_beta (int): minimum size (in residues) for beta strands"
            print "    min_diff_alpha (float): minimum difference in score for annotating alpha helices"
            print "    min_diff_beta (float): minimum difference in score for annotating beta strands"
            sys.exit(1)
        pathito_models=os.path.join(current_directory,dirmodels)
        pathito_borgesarci=os.path.join(current_directory,'ARCIMBOLDO_BORGES')
        if os.path.exists(pathito_models) and os.path.exists(pathito_borgesarci): # Check if the models folder has been already generated correctly, to avoid recomputing them
            print "\nThe models directory was found to be already generated, skipping template annotation and  model generation"
            print "   Template annotation read from annotated_template.pkl"
            back_annotation=open(os.path.join(current_directory,'annotated_template.pkl'),'rb')
            dict_oristru=cPickle.load(back_annotation)
            back_annotation.close()
            pathito_model_file = os.path.join(current_directory,'input_search.pdb')
            model_file=pathito_model_file
            return dict_oristru,model_file
        if Config.get(job_type, "sphere_definition").split()[0] == 'default':  # size will be based on the eLLG target
            def_sphere = None
        else:
            def_sphere = int(Config.get(job_type, "sphere_definition").split()[0])
        step_sphere = int(Config.get(job_type, "sphere_definition").split()[1])
        remove_coil_sp = str(Config.get(job_type, "sphere_definition").split()[2])
        if remove_coil_sp == "remove_coil":
            remove_coil = True
            nres_extend=0
        elif remove_coil_sp == "maintain_coil":
            remove_coil = False
            nres_extend=0
        elif remove_coil_sp.startswith("partial_coil"):
            nres_extend=int(remove_coil_sp.split('_')[-1])
            remove_coil = True
        else:
            print 'Please provide a valid option for the coil treatment'
            sys.exit(1)

        min_alpha = int(Config.get(job_type, "sphere_definition").split()[3])
        min_beta = int(Config.get(job_type, "sphere_definition").split()[4])
        min_diff_alpha = float(Config.get(job_type, "sphere_definition").split()[5])
        min_diff_beta = float(Config.get(job_type, "sphere_definition").split()[6])

        # NOTE: if the gyre_preserve_chains keyword is True, then the annotation used will be the same for all cycles
        # and will be that in the original pdb given by the user as template
        gyre_preserve_chains = Config.getboolean(job_type, "GYRE_PRESERVE_CHAINS")

        # Template annotation
        model_file, \
        dict_oristru, \
        distance_matrix_CA, \
        names_matrix, \
        ss_percentage = Bioinformatics3.shredder_template_annotation(model_file=model_file,
                                                                    current_directory=current_directory,
                                                                    bfacnorm=bfacnorm, poliA=trim_to_polyala,
                                                                    cys=maintainCys, remove_coil=remove_coil,
                                                                    nres_extend=nres_extend, min_alpha=min_alpha,
                                                                    min_beta=min_beta,min_diff_ah=min_diff_alpha,
                                                                    min_diff_bs=min_diff_beta,
                                                                    gyre_preserve_chains=gyre_preserve_chains,
                                                                    algorithm_community=algorithm_community,
                                                                    pack_beta_community=pack_beta_community,
                                                                    homogenity_community=homogenity_community)

        # Get the minimal nres for the target_ellg, using the template as model
        SystemUtility.close_connection(inpconf.DicGridConn, inpconf.DicParameters, inpconf.cm)
        # First compute what will be the minimal rmsd in the run and use that one
        RMSD = Config.getfloat(job_type, "rmsd_shredder")
        RMSD_ARC = Config.getfloat(job_type, "rmsd_arcimboldo")
        RMSD_ARC = RMSD # I will do this later on anyway in the case of the shredder spheres
        inpconf.RMSD_ARC = RMSD_ARC # NOTE CM: I think otherwhise this change will not be passed
        cycle_ref = Config.getint(job_type, "number_cycles_model_refinement")
        rmsd_decrease=Config.getfloat(job_type,'step_rmsd_decrease_gyre')
        USE_RGR = Config.get(job_type, "ROTATION_MODEL_REFINEMENT")
        if USE_RGR != 'NO_GYRE' and USE_RGR != 'no_gyre' and cycle_ref>1:
            last_rmsd= RMSD_ARC-(float(cycle_ref-1)*rmsd_decrease)
        else:
            last_rmsd=RMSD_ARC
        if last_rmsd <=0.0:
            print 'EXITING NOW... With the current parameterization, the last rmsd that will be used in the run is ' \
                  '0 or smaller. Please change parameterization and rerun'
            sys.exit(0)


        mrsumpath = os.path.join(current_directory, "ELLG_COMPUTATION_"+str(last_rmsd)+"/ellg_computation.sum")
        #tablesumpath = os.path.join(current_directory, "ELLG_COMPUTATION_"+str(last_rmsd)+"/table_ellg.sum")

        if not os.path.exists(mrsumpath):
            print "\nComputing minimal nres for an rmsd of ",last_rmsd
            onemodel = os.path.join(current_directory, "onemodel")
            try:
                os.mkdir(onemodel)
            except:
                shutil.rmtree(onemodel)
                os.mkdir(onemodel)
            os.link(model_file,os.path.join(onemodel,os.path.basename(model_file)))
            SystemUtility.open_connection(inpconf.DicGridConn, inpconf.DicParameters, inpconf.cm)
            if hasattr(inpconf.cm, "channel"):
                print cm.copy_directory(onemodel, onemodel)

            list_models_calculate_ellg = [os.path.join(onemodel,os.path.basename(model_file))]
            (nqueuetest, convNamestest) = SELSLIB2.startMR_ELLG(DicParameters=inpconf.DicParameters, cm=inpconf.cm,
                                                                sym=inpconf.sym,
                                                                nameJob="ELLG_COMPUTATION_"+str(last_rmsd), list_solu_set=[],
                                                                list_models_calculate=list_models_calculate_ellg,
                                                                outputDire=os.path.join(current_directory,"./ELLG_COMPUTATION_"+ str(last_rmsd)+"/"),
                                                                mtz=inpconf.mtz, MW=inpconf.MW, NC=inpconf.NC,
                                                                F=inpconf.F, SIGF=inpconf.SIGF,
                                                                Intensities=inpconf.Intensities,Aniso=inpconf.Aniso,
                                                                normfactors=inpconf.normfactors,
                                                                tncsfactors=inpconf.tncsfactors,
                                                                spaceGroup=inpconf.spaceGroup,
                                                                nice=inpconf.nice, RMSD=last_rmsd, lowR=99,
                                                                highR=inpconf.resolution_rotation_shredder,
                                                                ellg_target=inpconf.ellg_target)

            dict_result_ellg = SELSLIB2.evaluateMR_ELLG(inpconf.DicParameters, inpconf.cm, inpconf.DicGridConn,
                                                        nameJob="ELLG_COMPUTATION_"+str(last_rmsd),
                                                        outputDicr=os.path.join(current_directory,"./ELLG_COMPUTATION_"+
                                                                                str(last_rmsd)+"/"),
                                                        nqueue=nqueuetest,ensembles=convNamestest)

        else:
            dict_result_ellg = SELSLIB2.readMR_ELLGsum(mrsumpath)

        themodel = str(dict_result_ellg.keys()[0])
        nres_for_target_ellg=int(dict_result_ellg[themodel]['nres_for_target_ellg'])
        print "\n\nThe number of residues to reach the target eLLG, ", inpconf.ellg_target, " at ",last_rmsd," A is ", \
            nres_for_target_ellg , "\n\n"
        if def_sphere==None:
            def_sphere=nres_for_target_ellg
        if (def_sphere != None) and (def_sphere<nres_for_target_ellg):
            print 'Advisory: The size given for generating the models will not reach the minimum scattering ' \
                  'fraction to get a target eLLG of ', inpconf.ellg_target
            # NOTE: should I actually terminate or leave it to run?
        if def_sphere > len(dict_oristru.keys()):
            print 'Sorry, size set for the models is larger than the size of the template. EXITING NOW'
            sys.exit(0)

        dict_oristru = Bioinformatics3.shredder_spheres(current_directory,dirmodels,model_file,
                                                     dist_matrix=distance_matrix_CA, convNamesMatrix=names_matrix,
        	                                         target_size=def_sphere,dictio_template=dict_oristru,
                                                     step=step_sphere,min_ah=min_alpha, min_bs=min_beta)

        return dict_oristru,model_file # also return the model_file path to the processed model file

    elif SHRED_METHOD == "secondary_structure":
        print "This experimental method it does not support the OMIT LLG evaluation, for now. " \
              "Autoconfiguring SHRED_LLG: False"
        SHRED_LLG = False

        cut_alpha_comb = Config.getint(job_type, "cut_alpha_comb")
        cut_beta_comb = Config.getint(job_type, "cut_beta_comb")
        cut_ss_comb = Config.getint(job_type, "cut_ss_comb")
        mode = ""
        omit_ss = None
        if cut_ss_comb > 0:
            omit_ss = cut_ss_comb
        elif cut_alpha_comb > 0 and cut_beta_comb > 0:
            omit_ss = (cut_alpha_comb, cut_beta_comb)
        elif cut_beta_comb > 0:
            omit_ss = (0, cut_beta_comb)
        elif cut_alpha_comb > 0:
            omit_ss = (cut_alpha_comb, 0)
        else:
            print "You have select to shred using Secondary Structure elements, but cut_ss_comb, cut_alpha_comb, cut_beta_comb are all <= 0. Exit."
            sys.exit(0)
        listapdbs = SELSLIB2.generate_chunks_bySS(model_file, omit_ss, os.path.join(current_directory, dirmodels))
        return
    elif SHRED_METHOD == "borges_superposition":
        return
    else:
        print "The method " + SHRED_METHOD + "is not a valid SHREDDER method. Please check you .bor file and the manual."
        sys.exit(0)


def __prepareAnewARCIMBOLDO_BORGES(direc, models_direc, namep, Config, inpconf,nAutoTracCyc=0):
    """ Generate the appropiate configuration file for an ARCIMBOLDO_BORGES run that is launched trough SHREDDER.
    Args:
        direc ():
        models_direct():
        namep ():
    Returns:
        bordata (ConfigParser object): contains the configuration to launch a new ARCIMBOLDO_BORGES run from whithin SHREDDER
    """
    bordata = ConfigParser.ConfigParser()
    # Change the defaults that are required for shredder_spheres
    Data.defaults_bor = Data.defaults_bor.replace("ROTATION_MODEL_REFINEMENT: NO_GYRE", "ROTATION_MODEL_REFINEMENT: BOTH")
    Data.defaults_bor = Data.defaults_bor.replace("GIMBLE: False","GIMBLE: True")
    bordata.readfp(cStringIO.StringIO(Data.defaults_bor))
    listpro = ["CONNECTION", "GENERAL", "LOCAL","ANOMALOUS"]
    for elem in listpro:
        if Config.has_section(elem):
            bordata.remove_section(elem)
            bordata.add_section(elem)
            for pair in Config.items(elem):
                bordata.set(elem, pair[0], pair[1])
    bordata.set("GENERAL", "working_directory", direc)
    for pair in bordata.items("ARCIMBOLDO-BORGES"):
        if Config.has_option("ARCIMBOLDO-SHREDDER", pair[0]):
            bordata.set("ARCIMBOLDO-BORGES", pair[0], Config.get("ARCIMBOLDO-SHREDDER", pair[0]))

    bordata.remove_section("ARCIMBOLDO-SHREDDER")
    bordata.remove_section("ARCIMBOLDO")

    bordata.set("ARCIMBOLDO-BORGES", "shelxe_line", Config.get("ARCIMBOLDO-SHREDDER", "shelxe_line"))
    bordata.set("ARCIMBOLDO-BORGES", "shelxe_line_last", Config.get("ARCIMBOLDO-SHREDDER", "shelxe_line_last"))
    bordata.set("ARCIMBOLDO-BORGES", "molecular_weight", inpconf.MW)
    #print 'SHERLOCK setting inpconf.RMSD_ARC',inpconf.RMSD_ARC
    bordata.set("ARCIMBOLDO-BORGES", "rmsd", inpconf.RMSD_ARC)
    bordata.set("ARCIMBOLDO-BORGES", "number_of_component", inpconf.NC)
    bordata.set("ARCIMBOLDO-BORGES", "library_path", models_direc)
    try:
        bordata.set("ARCIMBOLDO-BORGES", "f_label", Config.get("ARCIMBOLDO-SHREDDER", "f_label"))
        bordata.set("ARCIMBOLDO-BORGES", "sigf_label", Config.get("ARCIMBOLDO-SHREDDER", "sigf_label"))
    except:
        bordata.set("ARCIMBOLDO-BORGES", "i_label", Config.get("ARCIMBOLDO-SHREDDER", "i_label"))
        bordata.set("ARCIMBOLDO-BORGES", "sigi_label", Config.get("ARCIMBOLDO-SHREDDER", "sigi_label"))
    bordata.set("ARCIMBOLDO-BORGES", "name_job", namep)
    bordata.set("ARCIMBOLDO-BORGES", "resolution_rotation", inpconf.resolution_rotation_arcimboldo)
    bordata.set("ARCIMBOLDO-BORGES", "sampling_rotation", inpconf.sampling_rotation_arcimboldo)
    bordata.set("ARCIMBOLDO-BORGES", "alixe", inpconf.ALIXE)
    bordata.set("ARCIMBOLDO-BORGES", "ellg_target", inpconf.ellg_target)
    bordata.set("ARCIMBOLDO-BORGES", "filter_clusters_after_rot", False)
    bordata.set("ARCIMBOLDO-BORGES", "prioritize_phasers", inpconf.prioritize_phasers)
    bordata.set("ARCIMBOLDO-BORGES", "gyre_preserve_chains", True)  # If is a SHREDDER, we do take care of the chains before the ARCIMBOLDO_BORGES run

    #NS autotracing cycle number
    bordata.set("ARCIMBOLDO-BORGES", "nAutoTracCyc", nAutoTracCyc)
    #bordata.set("ARCIMBOLDO-BORGES",'unitCellcontentAnalysis',unitCellcontentAnalysis)
    # NS ANOM pass the parameters to Shredder
    anomParameters= ANOMLIB.anomParameters()    #returns a list of the current anomParameters
    for anomP in anomParameters:
        bordata.set("ANOMALOUS", anomP,Config.get("ANOMALOUS", anomP))

    try:
        bordata.set("ARCIMBOLDO-BORGES", "SKIP_RES_LIMIT", Config.get("ARCIMBOLDO-SHREDDER", "SKIP_RES_LIMIT"))
    except:
        pass

    try:
        stop_if_solved = Config.getboolean("ARCIMBOLDO-SHREDDER", "STOP_IF_SOLVED")
        if coiled_coil:
            stop_if_solved = False  # In coiled coil case we want to perform all cycles
        bordata.set("ARCIMBOLDO-BORGES", "STOP_IF_SOLVED", stop_if_solved)
    except:
        pass

    return bordata


def __prepareAnewARCIMBOLDO(pdbf, direc, namep, Config, inpconf):
    bordata = ConfigParser.ConfigParser()
    bordata.readfp(cStringIO.StringIO(Data.defaults_bor))
    listpro = ["CONNECTION", "GENERAL", "LOCAL","ANOMALOUS"]
    for elem in listpro:
        if Config.has_section(elem):
            bordata.remove_section(elem)
            bordata.add_section(elem)
            for pair in Config.items(elem):
                bordata.set(elem, pair[0], pair[1])
        bordata.set("GENERAL", "working_directory", direc)
    for pair in bordata.items("ARCIMBOLDO"):
        if Config.has_option("ARCIMBOLDO-SHREDDER", pair[0]):
            bordata.set("ARCIMBOLDO", pair[0], Config.get("ARCIMBOLDO-SHREDDER", pair[0]))

    bordata.remove_section("ARCIMBOLDO-SHREDDER")
    bordata.remove_section("ARCIMBOLDO-BORGES")
    bordata.set("ARCIMBOLDO", "shelxe_line", Config.get("ARCIMBOLDO-SHREDDER", "shelxe_line"))
    bordata.set("ARCIMBOLDO", "shelxe_line_last", Config.get("ARCIMBOLDO-SHREDDER", "shelxe_line_last"))
    bordata.set("ARCIMBOLDO", "molecular_weight", inpconf.MW)
    bordata.set("ARCIMBOLDO", "number_of_component", inpconf.NC)
    try:
        bordata.set("ARCIMBOLDO", "f_label", Config.get("ARCIMBOLDO-SHREDDER", "f_label"))
        bordata.set("ARCIMBOLDO", "sigf_label", Config.get("ARCIMBOLDO-SHREDDER", "sigf_label"))
    except:
        bordata.set("ARCIMBOLDO", "i_label", Config.get("ARCIMBOLDO-SHREDDER", "i_label"))
        bordata.set("ARCIMBOLDO", "sigi_label", Config.get("ARCIMBOLDO-SHREDDER", "sigi_label"))
    
    bordata.set("ARCIMBOLDO", "rmsd", inpconf.RMSD_ARC)
    bordata.set("ARCIMBOLDO", "model_file", pdbf)
    bordata.set("ARCIMBOLDO", "name_job", namep)
    bordata.set("ARCIMBOLDO", "resolution_rotation", inpconf.resolution_rotation_arcimboldo)
    bordata.set("ARCIMBOLDO", "sampling_rotation", inpconf.sampling_rotation_arcimboldo)

    #NS autotracing cycle number
    bordata.set("ARCIMBOLDO-BORGES", "nAutoTracCyc", nAutoTracCyc)
    #bordata.set("ARCIMBOLDO-BORGES",'unitCellcontentAnalysis',unitCellcontentAnalysis)
    # NS ANOM pass the parameters to Shredder
    anomParameters= ANOMLIB.anomParameters()    #returns a list of the current anomParameters
    for anomP in anomParameters:
        bordata.set("ANOMALOUS", anomP,Config.get("ANOMALOUS", anomP))

    try:
        bordata.set("ARCIMBOLDO", "SKIP_RES_LIMIT", Config.get("ARCIMBOLDO-SHREDDER", "SKIP_RES_LIMIT"))
    except:
        pass

    try:
        stop_if_solved = Config.getboolean("ARCIMBOLDO-SHREDDER", "STOP_IF_SOLVED")
        SELSLIB2.STOP_IF_SOLVED = stop_if_solved
    except:
        pass

    if inpconf.mend_after_translation:
        bordata.set("ARCIMBOLDO", "swap_model_after_translation", model_file)

    # Write an explicit bor file in the ARCIMBOLDO run
    path_explicit_bor = os.path.join(direc, namep)
    file_object_bor = open(path_explicit_bor + '.bor', 'w')
    bordata.write(file_object_bor)
    del file_object_bor
    return bordata


# def startARCIMBOLDO_SHREDDER(BorData, input_bor, DicParameters={}, DicGridConn={}, cm=None, sym=None,
#                            doTest=True, mtz_given="", F_given="", SIGF_given="", tNCS_bool_given="", Intensities=False, Aniso=True,
#                            normfactors="", tncsfactors="", nice=0, out_phaser_given="", fneed=False,
#                            startCheckQueue=False, skip_mr=False, dictio_shred_annotation=None):
#     print 'This is the ARCIMBOLDO_SHREDDER function'


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
                        .------------------------------------------------------------.
                        |   _____ _    _ _____  ______ _____  _____  ______ _____    |
                        |  / ____| |  | |  __ \|  ____|  __ \|  __ \|  ____|  __ \   |
                        | | (___ | |__| | |__) | |__  | |  | | |  | | |__  | |__) |  |
                        |  \___ \|  __  |  _  /|  __| | |  | | |  | |  __| |  _  /   |
                        |  ____) | |  | | | \ \| |____| |__| | |__| | |____| | \ \   |
                        | |_____/|_|  |_|_|  \_\______|_____/|_____/|______|_|  \_\  |
                        #------------------------------------------------------------#
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

        Structure solution with ARCIMBOLDO using fragments derived from distant homology models.
        Sammito, M., Meindl, K., M. de Ilarduya, I., Millan, C., Artola-Recolons, C., Hermoso, J. A. & Uson, I.
        (2014) FEBS Journal 281, 4029-4045.

        Exploiting distant homologues for phasing through the generation of compact fragments, local fold refinement
        and partial solution combination
        Millan, C., Sammito, M. D., McCoy, A. J., Nascimento, A. F. Z., Petrillo, G., Oeffner, R. D.,
        Dominguez-Gil, T., Hermoso, J. A., Read, R. J. & Uson, I.
        (2018). Acta Cryst. D74, 290-304.
        """
        print "Email support: ", colored("bugs-borges@ibmb.csic.es", 'blue')
        print "\nARCIMBOLDO_SHREDDER website: ", colored("http://chango.ibmb.csic.es/shredder", 'blue')
        print "\n"
        usage = "usage: %prog [options] model.bor"
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
#A tutorial on how to run ARCIMBOLDO_SHREDDER can be found our website at: http://chango.ibmb.csic.es/tutorial_shredder

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

[ARCIMBOLDO-SHREDDER]
#NOTE: following are mandatory
name_job: example_name
molecular_weight:
# NOTE: It is recommended to use intensities if you have them
i_label: I
sigi_label: SIGI
#Or alternatively
#f_label: F
#sigf_label: SIGF
number_of_component: 1
model_file: /path/to/the/model.pdb

# NOTE: following are optional and have defaults configured
rmsd_shredder: 1.2
rmsd_arcimboldo: 0.8
resolution_rotation_shredder: 1.0
resolution_rotation_arcimboldo: 1.0
sampling_rotation_shredder: -1
sampling_rotation_arcimboldo: -1
resolution_gyre: 1.0
resolution_translation: 1.0
sampling_translation: -1
resolution_refinement: 1.0
sampling_refinement: -1
exclude_llg: 0
exclude_zscore: 0
spacegroup:
use_packing: True
#NOTE: the program automatically configures the shelxe_line  by checking data resolution but you can decomment it and use your own
shelxe_line:
number_cycles_model_refinement: 2
TNCS: True
VRMS: False
VRMS_GYRE: False
BFAC: False
#GIMBLE: False
BULK_FSOL: -1
BULK_BSOL: -1
SIGR: 0.0
SIGT: 0.0
PACK_TRA: False
solution_sorting_scheme: AUTO
#solution_sorting_scheme: LLG
#solution_sorting_scheme: ZSCORE
#solution_sorting_scheme: INITCC
#solution_sorting_scheme: COMBINED
GYRE_PRESERVE_CHAINS: False
#ROTATION_MODEL_REFINEMENT: BOTH
step_rmsd_decrease_gyre: 0.2
SHRED_LLG: False
OCC: False
BFACNORM: True
alixe: False
alixe_mode: one_step
SHRED_METHOD: spherical
# NOTE:  sphere definition parameters are:
#csize/'default' step 'maintain_coil'/'remove_coil'/'partial_coil_n', where n is number of res
# min_size_alpha min_size_beta min_diff_alpha min_diff_beta
sphere_definition: default 1 remove_coil 7 4 0.45 0.2
# Community clustering parameterization: algorithm bool_pack_beta bool_homogenity
community_clustering: fastgreedy False False
#SHRED_METHOD: sequential
#SHRED_RANGE: 4 20 1 omit all
n_clusters: 4

[LOCAL]
# Software paths
# Requires PHASER 2.8.x
path_local_phaser: phenix.phaser
path_local_shelxe: shelxe
path_local_phstat: phstat
path_local_arcimboldo: ARCIMBOLDO_BORGES
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

        [ARCIMBOLDO-SHREDDER]
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
        model_file: /path/to/the/model.pdb
        """
            print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
                ': following are optional. -1 means PHASER defaults', 'blue'),
            print colored("""
        #NOTE: the program automatically configure the shelxe_line but you can decomment it and use your own
        #shelxe_line:
        """, 'blue')
            print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
                ': clusters can take all, or a list of cluster id eg.: 0,1,2', 'blue'),
            print colored("""
        #clusters: all
        #rmsd_shredder: 1.2
        #rmsd_arcimboldo: 0.8
        #resolution_rotation_shredder: 1.0
        #resolution_rotation_arcimboldo: 1.0
        #sampling_rotation_shredder: -1
        #sampling_rotation_arcimboldo: -1
        #resolution_translation: 1.0
        #resolution_gyre: 1.0
        #sampling_translation: -1
        #resolution_refinement: 1.0
        #sampling_refinement: -1""", 'blue')
            print colored("""
        #TNCS: True
        #pack_clashes: 3
        #pack_distance: 3.0
        """, 'blue')
            print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
                ': if True activate LLG evaluation for models and launch ARCIMBOLDOs,\n#\tif False it use the generated models as libraries for ARCIMBOLDO-BORGES',
                'blue'),
            print colored("""
        #SHRED_LLG: True
        """, 'blue')
            print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
                ': the following parameter is used for the ARCIMBOLDOs called from the SHREDDER', 'blue'),
            print colored("""
        #fragment_to_search: 1
        """, 'blue')
            print colored("""#""", 'blue') + colored('\tNOTE', 'yellow') + colored(
                ': to shred the model using a sequential range. In particular\n#\t"SHRED_RANGE: n_min n_max step type" where type could be "omit" to create model without the shredded portion or\n#\tcould be "fragment" to create models just using the shredded portion. If type is "omit" then\n#\talpha helices or beta strands could be fixed and never omitted.\n#\tCoil regions could be trimmed out or could be included in the shredding process.',
                'blue'),
            print colored("""
        #SHRED_METHOD: sequential
        #SHRED_RANGE: 4 20 1 omit all
        #SHRED_RANGE: 4 20 1 omit fix_ah remove_coil
        #SHRED_RANGE: 4 20 1 omit fix_ah maintain_coil
        #SHRED_RANGE: 4 20 1 omit fix_bs remove_coil
        #SHRED_RANGE: 4 20 1 omit fix_bs maintain_coil
        #SHRED_RANGE: 4 20 1 fragment
        """, 'blue')
            print colored("""#""",'blue')+colored('\tNOTE','yellow')+colored(': to shred the model using a 3d sphere','blue'),
            print colored("""
        SHRED_METHOD: spherical
        # NOTE:  sphere definition parameters are:
        #csize/'default' step 'maintain_coil'/'remove_coil'/'partial_coil_n', where n is number of res
        # min_size_alpha min_size_beta min_diff_alpha min_diff_beta
        sphere_definition: default 1 remove_coil 7 4 0.45 0.2
        # NOTE: Depending on whether you do two steps or one, this line will be different
        # One step community clustering
        #community_clustering: one_step fastgreedy 0 30
        # Two steps community clustering
        community_clustering: two_steps 0 25 0 15 2.0

             """,'blue')
            print """
        [LOCAL]""",
            print colored("""
        #   Software paths
        #   Requires PHASER 2.8.x""", 'blue'),
            print """
        path_local_phaser: phenix.phaser
        path_local_shelxe: shelxe
        path_local_phstat: phstat
        path_local_arcimboldo: ARCIMBOLDO_BORGES
        """

        if options.devhelp:
            print "The selected option is only available for the developers team. Please insert the password:"
            command = raw_input("<> ")
            if hashlib.sha224(command).hexdigest() == "d286f6ad6324a21cf46c7e3c955d8badfdbb4a14d630e8350ea3149e":
                print """
        FULL LIST OF PARAMETERS FOR ARCIMBOLDO-SHREDDER:

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

        [ARCIMBOLDO-SHREDDER]
        name_job: example_name
        molecular_weight:
        f_label: F
        sigf_label: SIGF
        #Or alternatively
        #i_label: I
        #sigi_label: SIGI
        number_of_component: 1
        model_file: /path/to/the/model.pdb

        clusters: all
        f_p1_label:
        sigf_p1_label:
        number_of_component_p1:
        rmsd_shredder: 1.2
        rmsd_arcimboldo: 0.8
        rotation_clustering_algorithm: rot_matrices
        threshold_algorithm: 15
        resolution_rotation_shredder: 1.0
        resolution_rotation_arcimboldo: 1.0
        sampling_rotation_shredder: -1
        sampling_rotation_arcimboldo: -1
        resolution_gyre: 1.0
        resolution_translation: 1.0
        sampling_translation: -1
        resolution_refinement: 1.0
        sampling_refinement: -1
        exclude_llg: 0
        exclude_zscore: 0
        spacegroup:
        use_packing: True
        #NOTE: the program automatically configure the shelxe_line but you can decomment it and use your own
        shelxe_line:
        number_cycles_model_refinement: 2
        fragment_to_search: 1
        TNCS: True
        VRMS: False
        VRMS_GYRE: False
        BFAC: False
        GIMBLE: False
        # 0.35 Default Phaser
        BULK_FSOL: -1
        # 45 Default Phaser
        BULK_BSOL: -1
        SIGR: 0.0
        SIGT: 0.0
        PACK_TRA: False
        BASE_SUM_FROM_WD: True
        solution_sorting_scheme: AUTO
        #solution_sorting_scheme: LLG
        #solution_sorting_scheme: ZSCORE
        #solution_sorting_scheme: INITCC
        #solution_sorting_scheme: COMBINED
        GYRE_PRESERVE_CHAINS: False
        # NOTE: if Aniso is set to True, anisotropy and tncs correction will be recomputed in each phaser step
        ANISO: False
        nice: 0
        pack_clashes: 3
        pack_distance: 3.0
        NMA: False
        ROTATION_MODEL_REFINEMENT: BOTH
        step_rmsd_decrease_gyre: 0.2
        NMA_P1: False
        SHRED_LLG: True
        OCC: False
        test_method: BRF
        #test_method: GYRE
        #test_method: RNP
        test_sol:
        test_txt:
        init_location: EULER 0 0 0 FRAC 0 0 0
        prioritize_phasers: False
        prioritize_occ: True
        BFACNORM: True
        alixe: True
        alixe_mode: one_step
        SHRED_METHOD: spherical
        # NOTE:  sphere definition parameters are:
        #csize/'default' step 'maintain_coil'/'remove_coil'/'partial_coil_n', where n is number of res
        # min_size_alpha min_size_beta min_diff_alpha min_diff_beta
        sphere_definition: default 1 remove_coil 7 4 0.45 0.3
        # NOTE: Depending on whether you do two steps or one, this line will be different
        # Community clustering parameterization: algorithm bool_pack_beta bool_homogenity
        community_clustering: fastgreedy True True
        #SHRED_METHOD: secondary_structure
        cut_alpha_comb: 0
        cut_beta_comb: 0
        cut_ss_comb: 3
        SHRED_METHOD: sequential
        SHRED_RANGE: 4 20 1 omit all
        #SHRED_RANGE: 4 20 1 omit fix_ah remove_coil
        #SHRED_RANGE: 4 20 1 omit fix_ah maintain_coil
        #SHRED_RANGE: 4 20 1 omit fix_bs remove_coil
        #SHRED_RANGE: 4 20 1 omit fix_bs maintain_coil
        #SHRED_RANGE: 4 20 1 fragment
        mend_after_translation: False
        parameters_borges_matrix: 50,40,2.5,1
        reference_to_fix_location:
        skip_OMIT: False
        trim_to_polyala: True
        maintainCys: False
        sampling_gyre: -1
        applyTopNameFilter: True
        noDMinitcc: True
        phs_fom_statistics: False
        savePHS: False
        archivingAsBigFile: False
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
        path_local_phaser: phenix.phaser
        path_local_shelxe: shelxe
        # Path to our ancillary programs
        path_local_phstat: phstat
        path_local_arcimboldo: ARCIMBOLDO_BORGES


        """
                sys.exit(0)
            else:
                print "Sorry. You have not the permissions."
                sys.exit(0)


        #parser.add_option("-x", "--XGUI", action="store_true", dest="gui", help="Will automatically launch the GUI Option Viewer to read the output", default=False)
        (options, args) = parser.parse_args()

        model_directory = ""
        if len(args) < 1:
            parser.print_help()
            sys.exit(0)

        # Instantiate the input configuration object
        inpconf = inputConfig()


        input_bor = os.path.abspath(args[0])
        print '\n Reading the bor configuration file for ARCIMBOLDO_SHREDDER at ', input_bor
        if not os.path.exists(input_bor):
            print 'Sorry, the given path for the bor file either does not exist or you do not have the permissions to read it'
            sys.exit(1)
        path_module = os.path.dirname(__file__)

        try:
            Config_1 = ConfigParser.ConfigParser()
            Config_1.read(input_bor)
            coiled_coil = Config_1.getboolean("ARCIMBOLDO-SHREDDER", "coiled_coil")
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
            # TODO: also check that model to be used contains helices!

        # Check what the shred method is to select the defaults for gyre and gimble
        job_type = "ARCIMBOLDO-SHREDDER"
        # I need to read both our bor first, and after the merged one
        Config = ConfigParser.ConfigParser()
        Config.read(input_bor)

        try:
            SHRED_METHOD = Config.get(job_type, "SHRED_METHOD")
        except: # Then use spherical as default mode
            SHRED_METHOD = 'spherical'

        if SHRED_METHOD == 'spherical':
            inpconf.SHRED_LLG = False
        else:
            inpconf.SHRED_LLG=True

        skip_def_gyre = False
        skip_def_gimble = False
        user_set_gyre = False
        user_set_gimble = False
        try:
            RNP_GYRE = Config.get(job_type, "GIMBLE")
            user_set_gimble = True
        except:
            pass
        if SHRED_METHOD=='sequential' and not user_set_gimble:
            skip_def_gimble = True
        try:
            USE_RGR = Config.get(job_type, "ROTATION_MODEL_REFINEMENT")
            user_set_gyre = True
        except:
            pass
        if SHRED_METHOD=='sequential' and not user_set_gyre:
            skip_def_gyre = True

        Config = ConfigParser.ConfigParser()
        Config.readfp(cStringIO.StringIO(Data.defaults_bor))
        Config.read(input_bor)

        model_file = ""

        cm = None
        DicGridConn = {}
        DicParameters = {}
        sym = None

        #SET OUTPUT PARAMETERS
        current_directory = Config.get("GENERAL", "working_directory")
        if os.path.exists(os.path.join(current_directory,'temp_transfer')):
            shutil.rmtree(os.path.join(current_directory,'temp_transfer'))
        if os.path.exists(os.path.join(current_directory,'grid_jobs')):
            shutil.rmtree(os.path.join(current_directory,'grid_jobs'))
        if os.path.exists(os.path.join(current_directory,'temp')):
            shutil.rmtree(os.path.join(current_directory,'temp'))

        try:
            model_file = Config.get(job_type, "model_file")
        except:
            print colored("FATAL","red"),"["+job_type+"]\n model_file: \n \n Is mandatory keyword."
            print traceback.print_exc(file=sys.stdout)
            sys.exit(0)

        try:
            stry = Bioinformatics3.get_structure(name="test",pdbf=model_file)
            if len(stry.get_list()) <= 0:
                raise Exception
        except:
            print colored("FATAL","red"),"The model pdb file "+str(os.path.abspath(model_file))+" given in input is not a standard pdb file and cannot be correctly interpreted"
            print sys.exc_info()
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)

        toExit = False
        try:
            distribute_computing = Config.get("CONNECTION", "distribute_computing").strip().lower()

            if distribute_computing in ["multiprocessing","supercomputer"]:
                SELSLIB2.PATH_NEW_PHASER = Config.get("LOCAL", "path_local_phaser")
                SELSLIB2.PATH_NEW_SHELXE = Config.get("LOCAL", "path_local_shelxe")
                SELSLIB2.PATH_NEW_ARCIFIRE = Config.get("LOCAL","path_local_arcimboldo")
                SELSLIB2.PATH_PHSTAT = Config.get("LOCAL","path_local_phstat")

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
                    if lett not in Bioinformatics3.AALISTOL:
                        print "Sequence is not valid, symbol",lett,"not recognized"
                        toExit = True
                        sys.exit(0)
                MW = float(len(lett)*100)
            except:
                # TODO: check if this value makes sense (if it is either too low or to high)
                MW = Config.getfloat(job_type, "molecular_weight")
                # NOTE: At least, we check that it is not smaller than 0 or negative
                if MW <=0.0:
                    print 'Sorry, the input molecular weight is not correct. ARCIMBOLDO_SHREDDER will exit now, please check the molecular_weight keyword value given'

            #NS: optional number of components (if absent unit cell content analyssis is launched)
            try:
                NC = Config.getint(job_type, "number_of_component")
                if NC == 0:
                    raise Exception
            except:
                NC=-1    #NS: Now NC == -1 means automatic mode
            unitCellcontentAnalysis=Config.getboolean(job_type,"unitCellcontentAnalysis")
            solventContent=Config.getfloat(job_type,"solventContent") #Solvent content to use in the shelxe DM calculations --> now taken from unitcell content analysis result following the number of mol/asu


            #NS : I need sometimes to use more autotracing cycles in the end
            nAutoTracCyc = Config.getint(job_type,'nAutoTracCyc')
            nBunchAutoTracCyc = Config.getint(job_type,'nBunchAutoTracCyc')

            try:
                F = Config.get("ARCIMBOLDO-SHREDDER", "f_label")
                SIGF = Config.get("ARCIMBOLDO-SHREDDER", "sigf_label")
                Intensities = False
            except:
                F = Config.get("ARCIMBOLDO-SHREDDER", "i_label")
                SIGF = Config.get("ARCIMBOLDO-SHREDDER", "sigi_label")
                Intensities = True

            nice = Config.getint("ARCIMBOLDO-SHREDDER","nice")

            RMSD = Config.getfloat(job_type, "rmsd_shredder")
            RMSD_ARC = Config.getfloat(job_type, "rmsd_arcimboldo")
            inpconf.RMSD_ARC = RMSD_ARC
        except:
            print "Mandatory tags are missing:"
            print traceback.print_exc(file=sys.stdout)
            toExit = True

        if toExit:
            sys.exit(0)

        inpconf.F=F
        inpconf.SIGF=SIGF
        inpconf.mtz=mtz
        inpconf.MW=MW
        inpconf.NC=NC
        inpconf.Intensities=Intensities

        Aniso = Config.getboolean("ARCIMBOLDO-SHREDDER", "ANISO")
        inpconf.Aniso = Aniso
        formfactors = Config.get("ARCIMBOLDO-SHREDDER", "formfactors")
        inpconf.formfactors=formfactors

        peaks = 75

        force_core = Config.getint("ARCIMBOLDO-SHREDDER", "force_core")
        if force_core <= 0:
            force_core = None

        setupbor = None
        if distribute_computing == "remote_grid":
            path_bor = Config.get("CONNECTION", "setup_bor_path")
            if path_bor is None or path_bor == "" or not os.path.exists(path_bor):
                print colored("ATTENTION: the path given for the setup.bor does not exist.\n Please contact your administrator","red")
                sys.exit(1)
            try:
                setupbor = ConfigParser.ConfigParser()
                setupbor.readfp(open(path_bor))
                DicGridConn["username"] = setupbor.get("GRID", "remote_frontend_username")
                DicGridConn["host"] = setupbor.get("GRID", "remote_frontend_host")
                DicGridConn["port"] = setupbor.getint("GRID", "remote_frontend_port")
                DicGridConn["passkey"] = Config.get("CONNECTION", "remote_frontend_passkey")
                DicGridConn["promptA"] = (setupbor.get("GRID", "remote_frontend_prompt")).strip()+" "
                DicGridConn["isnfs"] = setupbor.getboolean("GRID", "remote_fylesystem_isnfs")
                try:
                    DicGridConn["remote_submitter_username"] = setupbor.get("GRID", "remote_submitter_username")
                    DicGridConn["remote_submitter_host"] = setupbor.get("GRID", "remote_submitter_host")
                    DicGridConn["remote_submitter_port"] = setupbor.getint("GRID", "remote_submitter_port")
                    DicGridConn["promptB"] = (setupbor.get("GRID", "remote_submitter_prompt")).strip()+" "
                except:
                    pass
                DicGridConn["home_frontend_directory"] = setupbor.get("GRID", "home_frontend_directory")
                SELSLIB2.PATH_NEW_PHASER = setupbor.get("GRID", "path_remote_phaser")
                SELSLIB2.PATH_NEW_SHELXE = setupbor.get("GRID", "path_remote_shelxe")
                SELSLIB2.GRID_TYPE_R = setupbor.get("GRID","type_remote")
                if SELSLIB2.GRID_TYPE_R == "Condor":
                    SELSLIB2.SHELXE_REQUIREMENTS = setupbor.get("CONDOR", "requirements_shelxe")
                    SELSLIB2.PHASER_REQUIREMENTS = setupbor.get("CONDOR", "requirements_phaser")
                    SELSLIB2.BORGES_REQUIREMENTS = setupbor.get("CONDOR", "requirements_borges")
                SELSLIB2.LOCAL = False
            except:
                print colored("ATTENTION: Some keyword in your configuration files are missing. Contact your administrator","red")
                print "Path bor given: ",path_bor
                print traceback.print_exc(file=sys.stdout)
                sys.exit(1)
        elif distribute_computing == "local_grid":
            path_bor = Config.get("CONNECTION", "setup_bor_path")
            if path_bor is None or path_bor == "" or not os.path.exists(path_bor):
                print colored("ATTENTION: the path given for the setup.bor does not exist.\n Please contact your administrator","red")
                sys.exit(1)
            try:
                setupbor = ConfigParser.ConfigParser()
                setupbor.readfp(open(path_bor))
                SELSLIB2.PATH_NEW_PHASER = setupbor.get("LOCAL", "path_local_phaser")
                SELSLIB2.PATH_NEW_SHELXE = setupbor.get("LOCAL", "path_local_shelxe")
                SELSLIB2.PATH_PHSTAT = setupbor.get("LOCAL", "path_local_phstat")
                SELSLIB2.GRID_TYPE_L = setupbor.get("GRID","type_local")
                if SELSLIB2.GRID_TYPE_L == "Condor":
                    SELSLIB2.SHELXE_REQUIREMENTS = setupbor.get("CONDOR", "requirements_shelxe")
                    SELSLIB2.PHASER_REQUIREMENTS = setupbor.get("CONDOR", "requirements_phaser")
                    SELSLIB2.BORGES_REQUIREMENTS = setupbor.get("CONDOR", "requirements_borges")
            except:
                print colored("ATTENTION: Some keyword in your configuration files are missing. Contact your administrator","red")
                print "Path bor given: ",path_bor
                print traceback.print_exc(file=sys.stdout)
                sys.exit(1)


        #STATIC REFERENCE TO THE QUATERNION CLASS
        quate = Quaternions.Quaternions()

        #STARTING SYSTEM MANAGER
        sym = SystemUtility.SystemUtility()

        if force_core != None:
            sym.PROCESSES = force_core

        try:
            DicParameters = {}
            nameJob = Config.get(job_type, "name_job")
            nameJob = "_".join(nameJob.split())
            if len(nameJob.strip()) == 0:
                print '\nKeyword name_job is empty, setting a default name for the job...'
                nameJob = (os.path.basename(mtz))[:-4] + '_arcimboldo_shredder'
            DicParameters["nameExecution"] = nameJob
        except:
            print "Mandatory tags are missing:"
            print traceback.print_exc(file=sys.stdout)

        nameOutput = DicParameters["nameExecution"]

        if os.path.exists(os.path.join(current_directory,nameOutput+".html")):
            os.remove(os.path.join(current_directory,nameOutput+".html"))
        if os.path.exists(os.path.join(current_directory,nameOutput+".xml")):
            os.remove(os.path.join(current_directory,nameOutput+".xml"))

        model_directory = os.path.join(current_directory,DicParameters["nameExecution"]+"_ensembles/")
        if not (os.path.exists(model_directory)):
            os.makedirs(model_directory)
        else:
            shutil.rmtree(model_directory)
            os.makedirs(model_directory)

        if os.path.exists(pdbcl):
            m = os.path.basename(os.path.basename(model_file).split(".")[0][:4]+"001_0_0.pdb")
        else:
            m = os.path.basename(os.path.basename(model_file).split(".")[0]+"_0_0.pdb")

        shutil.copyfile(model_file, os.path.join(model_directory,m))
        model_file = os.path.join(model_directory,m)

        #STARTING THE GRID MANAGER
        GRID_TYPE = ""
        if distribute_computing == "remote_grid":
            GRID_TYPE = setupbor.get("GRID","type_remote")
        elif distribute_computing == "local_grid":
            GRID_TYPE = setupbor.get("GRID","type_local")

        if cm == None:
            if GRID_TYPE == "Condor":
                cm = Grid.condorManager()
            elif GRID_TYPE == "SGE":
                QNAME = setupbor.get("SGE","qname")
                FRACTION = setupbor.getfloat("SGE","fraction")
                cm = Grid.SGEManager(qname=QNAME,fraction=FRACTION)
            elif GRID_TYPE == "MOAB":
                PARTITION = setupbor.get("MOAB","partition")
                cm = Grid.MOABManager(partition=PARTITION)
            elif GRID_TYPE == "SLURM":
                PARTITION = setupbor.get("SLURM","partition")
                if PARTITION != None and PARTITION != '':
                    cm = Grid.SLURMManager(partition=PARTITION)
                else:
                    cm = Grid.SLURMManager()
            elif GRID_TYPE == "TORQUE":
                QNAME = setupbor.get("TORQUE","qname")
                FRACTION = setupbor.getint("TORQUE","cores_per_node")
                PARALLEL_JOBS = setupbor.getint("TORQUE","number_of_parallel_jobs")
                MAUI = setupbor.getboolean("TORQUE","maui")
                cm = Grid.TORQUEManager(qname=QNAME,cores_per_node=FRACTION,parallel_jobs=PARALLEL_JOBS,maui=MAUI)

        if cm is not None:
            cm.setRank("kflops")
            cm.nice_user = "true"
            #TODO: Eliminate the SGE.py
            PATH_REMOTE_SGEPY = setupbor.get("GRID", "path_remote_sgepy")
            PATH_REMOTE_PYTHON_INTERPRETER = setupbor.get("GRID", "python_remote_interpreter")
            PATH_LOCAL_PYTHON_INTERPRETER = setupbor.get("LOCAL", "python_local_interpreter")

            if PATH_REMOTE_PYTHON_INTERPRETER.strip() in ["", None]:
                PATH_REMOTE_PYTHON_INTERPRETER = "/usr/bin/python"

            if PATH_LOCAL_PYTHON_INTERPRETER.strip() in ["", None]:
                PATH_LOCAL_PYTHON_INTERPRETER = "/usr/bin/python"

        if distribute_computing == "supercomputer":
            path_nodes = Config.get("CONNECTION", "nodefile_path")
            if path_nodes is None or path_nodes == "" or not os.path.exists(path_nodes):
                print colored("ATTENTION: the path given for the node file does not exist.\n Please contact your administrator","red")
                sys.exit(1)
            f = open(path_nodes,"r")
            nodes_list = f.readlines()
            f.close()
            for i in range(len(nodes_list)):
                nodes_list[i] = nodes_list[i][:-1]+"***"+str(i)
            SystemUtility.NODES = nodes_list

        if distribute_computing == "supercomputer":
            path_nodes = Config.get("CONNECTION", "nodefile_path")
            if path_nodes is None or path_nodes == "" or not os.path.exists(path_nodes):
                print colored("ATTENTION: the path given for the node file does not exist.\n Please contact your administrator","red")
                sys.exit(1)
            f = open(path_nodes,"r")
            nodes_list = f.readlines()
            f.close()
            #SELSLIB2.PATH_NEW_ARCIFIRE = nodes_list[0].strip()
            #nodes_list = nodes_list[1:]

            for i in range(len(nodes_list)):
                nodes_list[i] = nodes_list[i][:-1]+"***"+str(i)
            SystemUtility.NODES = nodes_list

        inpconf.DicGridConn=DicGridConn
        inpconf.DicParameters=DicParameters
        inpconf.cm=cm
        inpconf.sym=sym

        #LOCKING FOR ACCESS OUTPUT FILE
        lock = threading.RLock()
        lock = threading.Condition(lock)

        #VARIABLES FOR REFINEMENT IN P1
        mtzP1 = Config.get("GENERAL", "mtz_p1_path")
        #TODO: It is important to expand directly the anis.mtz in P1 and not ask the user to give the mtzP1.
        #Remember anis.mtz should be expanded in P1 and not the original one mtz

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


        SHRED_METHOD = Config.get(job_type, "SHRED_METHOD")
        if SHRED_METHOD == 'spherical':
            # NOTE CM: we should do something smarter but at the moment this is consistent also with ccp4i1 approach
            RMSD_ARC = RMSD
            inpconf.RMSD_ARC = RMSD_ARC

        clusteringAlg = Config.get(job_type, "rotation_clustering_algorithm")
        excludeLLG = Config.getfloat(job_type, "exclude_llg")
        excludeZscore = Config.getfloat(job_type, "exclude_zscore")
        thresholdCompare = Config.getfloat(job_type, "threshold_algorithm")
        startLocal = False
        USE_PACKING = Config.getboolean(job_type, "use_packing")
        USE_TRANSLA = True
        USE_NMA = Config.getboolean(job_type, "NMA")
        if not skip_def_gyre:
            USE_RGR = Config.get(job_type, "ROTATION_MODEL_REFINEMENT")
        else:
            if not user_set_gyre:
                USE_RGR = 'no_gyre'  # default for the sequential
                Config.set(job_type,"ROTATION_MODEL_REFINEMENT",USE_RGR) # to change it also in the object and the html
        if USE_RGR.lower() == "both":
            USE_RGR = 2
        elif USE_RGR.lower() == "gyre":
            USE_RGR = 1
        else:
            USE_RGR = 0

        # Check the rmsd decrease step for gyre
        rmsd_decrease=Config.getfloat(job_type,'step_rmsd_decrease_gyre')

        USE_NMA_P1 = Config.getboolean(job_type, "NMA_P1")
        USE_OCC = Config.getboolean(job_type, "OCC")
        prioritize_occ = Config.getboolean(job_type, "prioritize_occ")
        prioritize_phasers = Config.getboolean(job_type, "prioritize_phasers")
        inpconf.prioritize_phasers = prioritize_phasers
        test_method = (Config.get(job_type, "test_method")).upper()
        if test_method not in ["RNP","BRF","GYRE"]:
            print "Test method is not recognized: ",test_method
        if test_method == "GYRE":
            print colored("""ATTENTION: the GYRE method to optimize the rotation of shredded models is
            not yet supported!""",'red')
            sys.exit(1)
        if test_method == "RNP":
            init_location = (Config.get(job_type, "init_location")).upper()
            try:
                initli = init_location.split()
                initl = [[float(initli[1]),float(initli[2]),float(initli[3]),
                          float(initli[5]),float(initli[6]),float(initli[7])]]
            except:
                print colored("""ATTENTION the format input is not correct\n"""+init_location
                              +"""\nwhile it should be:\ninit_location: EULER 0 0 0 FRAC 0 0 0""","red")
        applyNameFilter = Config.getboolean(job_type, "applyTopNameFilter")
        res_rot = Config.getfloat(job_type, "resolution_rotation_shredder")
        inpconf.resolution_rotation_shredder = res_rot
        sampl_rot = Config.getfloat(job_type, "sampling_rotation_shredder")
        resRotArc = Config.getfloat(job_type, "resolution_rotation_arcimboldo")
        inpconf.resolution_rotation_arcimboldo = resRotArc
        samplRotArc = Config.getfloat(job_type, "sampling_rotation_arcimboldo")
        inpconf.sampling_rotation_arcimboldo = samplRotArc
        res_tran = Config.getfloat(job_type, "resolution_translation")
        sampl_tran = Config.getfloat(job_type, "sampling_translation")
        res_refin = Config.getfloat(job_type, "resolution_refinement")
        sampl_refin = Config.getfloat(job_type, "sampling_refinement")
        RGR_SAMPL = Config.getfloat(job_type, "sampling_gyre")
        res_gyre = Config.getfloat(job_type, "resolution_gyre")
        sigr = Config.getfloat(job_type, "SIGR")
        sigt = Config.getfloat(job_type, "SIGT")
        preserveChains = Config.getboolean(job_type,"GYRE_PRESERVE_CHAINS")
        noDMinitcc = Config.getboolean(job_type, "noDMinitcc")
        phs_fom_statistics = Config.getboolean(job_type, "phs_fom_statistics")
        savePHS = Config.getboolean(job_type, "savePHS")
        ellg_target = Config.getfloat(job_type,"ellg_target")
        archivingAsBigFile = Config.getboolean(job_type, "archivingAsBigFile")

        USE_TNCS = Config.getboolean(job_type, "TNCS")
        VRMS = Config.getboolean(job_type, "VRMS")
        VRMS_GYRE = Config.getboolean(job_type, "VRMS_GYRE")
        BFAC = Config.getboolean(job_type, "BFAC")
        BULK_FSOL =  Config.getfloat(job_type, "BULK_FSOL")
        BULK_BSOL =  Config.getfloat(job_type, "BULK_BSOL")
        BFACNORM = Config.getboolean(job_type, "BFACNORM")
        if not skip_def_gimble:
            RNP_GYRE = Config.getboolean(job_type, "GIMBLE")
        else:
            if not user_set_gimble:
                RNP_GYRE = False # default for the sequential
                Config.set(job_type,"GIMBLE",RNP_GYRE) # to change it also in the object and the html

        # Check if remove_coil keyword is set to maintain the coil, and in that case deactivate gyre and gimble
        remove_coil_sp = str(Config.get(job_type, "sphere_definition").split()[2])
        if remove_coil_sp == "remove_coil":
            remove_coil = True
        else:
            remove_coil = False

        if remove_coil == False and SHRED_METHOD == 'spherical' and not preserveChains:
            print colored("""WARNING: gyre and gimble are not supported if the coil is 
                            left at the model without annotation. Automatically configuring...""",'yellow')
            USE_RGR = 0 # set gyre off
            Config.set(job_type,"ROTATION_MODEL_REFINEMENT",'NO_GYRE')
            RNP_GYRE = False # set gimble off
            Config.set(job_type,"GIMBLE",RNP_GYRE) # to change it also in the object and the html


        PACK_TRA = Config.getboolean(job_type, "PACK_TRA")
        BASE_SUM_FROM_WD = Config.getboolean(job_type, "BASE_SUM_FROM_WD")
        SELSLIB2.BASE_SUM_FROM_WD = BASE_SUM_FROM_WD
        solution_sorting_scheme = Config.get(job_type, "solution_sorting_scheme").upper()
        alixe_mode = Config.get(job_type, "alixe_mode")
        ALIXE = Config.getboolean(job_type, "alixe")
        inpconf.ALIXE = ALIXE
        CLASHES = Config.getint(job_type, "pack_clashes")

        SHRED_LLG = Config.getboolean(job_type, "SHRED_LLG")
        trim_to_polyala = Config.getboolean(job_type, "trim_to_polyala")
        maintainCys = Config.getboolean(job_type, "maintainCys")
        coiled_coil = Config.getboolean(job_type,"coiled_coil")


        topFRF = Config.getint(job_type, "topFRF")
        if topFRF <= 0:
            topFRF = None
        topFTF = Config.getint(job_type, "topFTF")
        if topFTF <= 0:
            topFTF = None
        topPACK = Config.getint(job_type,"topPACK")
        if topPACK <= 0:
            topPACK = None
        topRNP = Config.getint(job_type, "topRNP")
        if topRNP <= 0:
            topRNP = None
        topExp = Config.getint(job_type, "topExp")-1
        shlxLinea0 = ""

        if topExp <= 0:
            topExp = None

        #TEST THE SHELXE USER LINE
        try:
            linsh = Config.get(job_type, "shelxe_line")
            if linsh == None or linsh.strip() == "":
                raise Exception
            listash = linsh.split()
            for toc in range(len(listash)):
                param = listash[toc]
                if param.startswith("-a"):
                    param = "-a0"
                    if toc+1 < len(listash) and not listash[toc+1].startswith("-"):
                        listash[toc+1] = ""
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

        # Anisotropy and tNCS correction, retrieval of data info
        anismtz,normfactors,tncsfactors,F,SIGF,spaceGroup,cell_dim,resolution,unique_refl,aniout,anierr,\
        fneed, shelxe_new, tNCS_bool = SELSLIB2.anisotropyCorrection_and_test(cm=cm,sym=sym,DicGridConn=DicGridConn,
                                                                              DicParameters=DicParameters,
                                                                              current_dir=current_directory, mtz=mtz,
                                                                              F=F, SIGF=SIGF, Intensities=Intensities,
                                                                              Aniso=Aniso, formfactors=formfactors,
                                                                              nice=nice, pda=Data.th70pdb, hkl=hkl,
                                                                              ent=ent, shelxe_line=shlxLinea0)


        inpconf.normfactors=normfactors
        inpconf.tncsfactors=tncsfactors
        inpconf.spaceGroup=spaceGroup
        inpconf.nice=nice
        inpconf.ellg_target=ellg_target

        # Testing the fortran executable for the phase combination
        #print 'SHERLOCK SELSLIB2.PATH_PHSTAT',SELSLIB2.PATH_PHSTAT
        #print 'SHERLOCK os.path.exists(SELSLIB2.PATH_PHSTAT)', os.path.exists(SELSLIB2.PATH_PHSTAT)
        if not os.path.exists(SELSLIB2.PATH_PHSTAT):
            print 'Sorry, the path given to the phstat executable does not exist'
            print 'Please change the keyword path_local_phstat to a valid path or deactivate the alixe option'
            sys.exit(0)
        else:
            # Check anyway that the program works
            try:
                p = subprocess.Popen(SELSLIB2.PATH_PHSTAT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                complete_output, errors = p.communicate()
                if len(complete_output)>0:
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
            sys.exit(1)
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
        sg_symbol = dictio_space_groups[sg_number]['symbol']
        spaceGroup = sg_symbol
 
        
        #SHELXE LINE
        default_shelx_line = False
        try:
            linsh = Config.get(job_type, "shelxe_line")
            try:
                linsh_last = Config.get(job_type, "shelxe_line_last")
            except:
                # TODO: Decide what to do when is user-given line. At the moment we use the same one
                # TODO: But we need to reduce it to one cycle
                #traceback.print_exc()
                linsh_last_list = []
                list_args_linsh_last = linsh.split()
                for arg in list_args_linsh_last:
                    if not arg.startswith('-a'):
                        linsh_last_list.append(arg)
                linsh_last = (" ".join(linsh_last_list))+' -a1'
            if linsh == None or linsh.strip() == "":
                raise Exception
        except:
            # NOTE_CM: I write a boolean here to know whether we will be using our default lines or the user ones
            default_shelx_line = True
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


        listash = linsh.split()
        nautocyc = 0
        listash1 = linsh.split()
        for toc in range(len(listash)):
            param = listash[toc]
            if param.startswith("-a"):
                nautocyc = int(param[2:])+1
                param = "-a0"
                nk = 0
                for prr in listash:
                    if prr.startswith("-K"):
                        nk = int(prr[2:])
                        break
                if nk == 0:
                    param1 = "-a1"
                else:
                    param1 = "-a"+str(nk+1)
                    nautocyc = nautocyc-(nk+1)

                if toc+1 < len(listash) and not listash[toc+1].startswith("-"):
                    listash[toc+1] = ""
                    listash1[toc+1] = ""
                listash[toc] = param
                listash1[toc] = param1
                break

        if noDMinitcc:
            for toc in range(len(listash)):
                param = listash[toc]
                if param.startswith("-m"):
                    ndenscyc = int(param[2:])+1
                    param = "-m5"
                    if toc+1 < len(listash) and not listash[toc+1].startswith("-"):
                        listash[toc+1] = ""
                    listash[toc] = param
                    break

        if os.path.exists(ent):
            listash.append("-x")
            listash1.append("-x")

        linshinitcc = " ".join(listash)
        shlxLinea0 = linshinitcc
        shlxLinea1 = " ".join(listash1)
        shlxLineaFull = linsh
        shlxLineaLast = linsh_last

            #NS UNIT CELL CONTENT ANALYSIS (optional)
        if unitCellcontentAnalysis or NC<=0:
            print("UNIT CELL CONTENT ANALYSIS")
            solventContent, NC = SELSLIB2.unitCellContentAnalysis(current_directory=current_directory, spaceGroup=spaceGroup,cell_dim=cell_dim, MW=MW, resolution=resolution ,moleculeType="protein", numberOfComponents=NC, solventContent=solventContent)
            
            if solventContent is None or NC is None:
                print("ERROR, your solvent content or number of components is lower or equal to zero, quitting now!")
                sys.exit(1)
            
            # Re set up the inpconf.NC=NC which will be used in prepareNew ArcimboldoBorges
            inpconf.NC=NC

            #Set up the shelxe line for further steps (adding radius of the sphere of influence and solvent content)
            solvarg_re=re.compile(r"\-s[\d.]+")
            m0=solvarg_re.search(shlxLinea0)
            m1=solvarg_re.search(shlxLinea1)
            mP=solvarg_re.search(shlxLineaFull)
            mLast=solvarg_re.search(shlxLineaLast)

            if resolution>2.5:                    #NS: Arbitrary cutoff, radius of the sphere of inflence
                shlxLinea0 += " -S%s"%resolution  
                shlxLinea1 += " -S%s"%resolution
                shlxLineaFull += " -S%s"%resolution
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
                shlxLineaFull = re.sub(solvarg_re,"-s%.2f"%solventContent, shlxLineaFull)
            else:
                shlxLineaFull += " -s%.2f"%solventContent

            if mLast:
                shlxLineaLast = re.sub(solvarg_re,"-s%.2f"%solventContent, shlxLineaLast)
            else:
                shlxLineaLast += " -s%.2f"%solventContent

            del(m0, m1, mP, mLast)    #Remove these variable from memory 

        # Set properly the shelxe_line at the config so that the html shows it
        Config.set(job_type, "shelxe_line", shlxLineaFull)
        Config.set(job_type, "shelxe_line_last", shlxLineaLast)

        Config.remove_section("ARCIMBOLDO-BORGES")

        if SHRED_METHOD == "sequential":
            howmany, indic, chunk_range = __launchShredExec(SHRED_METHOD,Config,job_type,model_file,trim_to_polyala,
                                                            maintainCys,current_directory,"models",inpconf)
            dictio_annotation_models={} 
        else:
            dictio_annotation_models,model_file = __launchShredExec(SHRED_METHOD,Config,job_type,model_file,
                                                                  trim_to_polyala,maintainCys,current_directory,
                                                                  "models",inpconf)
            # NOTE CM: Changing the shelxe line if user did not give a default and we have beta version of shelxe
            helix_found = False
            beta_found = False
            if default_shelx_line and shelxe_new:
                for key in dictio_annotation_models.keys():
                    if dictio_annotation_models[key]['ss_type_res']=='ah':
                        helix_found = True
                    if dictio_annotation_models[key]['ss_type_res']=='bs':
                        beta_found = True
                linsh = Config.get(job_type, "shelxe_line")
                listaval_line = linsh.split()
                linsh_last = Config.get(job_type, "shelxe_line_last")
                listavalline_last = linsh_last.split()
                if beta_found:
                    linsh = linsh + ' -B3'
                    linsh_last = linsh_last + ' -B3'
                if not helix_found and '-q' in listaval_line:
                    listaval = [ele for ele in listaval_line if ele!='-q']
                    linsh=" ".join(listaval)
                    listaval_last = [ele for ele in listavalline_last if ele!='-q']
                    linsh_last=" ".join(listaval_last)
                shlxLineaFull = linsh
                shlxLineaLast = linsh_last
                # Set properly the shelxe_line at the config so that the html shows it
                Config.set(job_type, "shelxe_line", shlxLineaFull)
                Config.set(job_type, "shelxe_line_last", shlxLineaLast)

        fixed_frags = 1
        evaLLONG = False #It just works with helices and distributionCV better not use it for now

        #RETRIEVING THE LAUE SIMMETRY FROM THE SPACEGROUP
        laue = quate.getLaueSimmetry(spaceGroup)
        if laue == None:
            print 'Some problem happened during retrieval of the laue symmetry for this space group'

        ncs = [] # NOTE CM: Not yet integrated in the clustering of rotations

        if os.path.exists(os.path.join(current_directory,"temp")):
            shutil.rmtree(os.path.join(current_directory,"temp"))

        SystemUtility.open_connection(DicGridConn,DicParameters,cm)
        if hasattr(cm,"channel") and SHRED_LLG:
            #COPY THE FULL LIBRARY and MTZ and HKL, IN THE REMOTE SERVER
            actualdi = cm.get_remote_pwd()
            print cm.change_remote_dir("..")
            print cm.copy_directory(model_directory,model_directory)
            print cm.change_remote_dir(os.path.basename(os.path.normpath(model_directory)))
            cm.remote_library_path = cm.get_remote_pwd()
            print cm.copy_local_file(mtz,os.path.basename(mtz),send_now=True)
            cm.remote_mtz_path = os.path.join(cm.remote_library_path,os.path.basename(mtz))
            print cm.copy_local_file(hkl,os.path.basename(hkl),send_now=True)
            cm.remote_hkl_path = os.path.join(cm.remote_library_path,os.path.basename(hkl))
            print cm.copy_local_file(tncsfactors,os.path.basename(tncsfactors),send_now=True)
            cm.remote_tncs_path = os.path.join(cm.remote_library_path,os.path.basename(tncsfactors))
            print cm.copy_local_file(normfactors,os.path.basename(normfactors),send_now=True)
            cm.remote_norm_path = os.path.join(cm.remote_library_path,os.path.basename(normfactors))
            if os.path.exists(ent):
                print cm.copy_local_file(ent,os.path.basename(ent),send_now=True)
                cm.remote_ent_path = os.path.join(cm.remote_library_path,os.path.basename(ent))
            if os.path.exists(pdbcl):
                print cm.copy_local_file(pdbcl,os.path.basename(pdbcl),send_now=True)
                cm.remote_pdbcl_path = os.path.join(cm.remote_library_path,os.path.basename(pdbcl))

            if PERFORM_REFINEMENT_P1:
                print cm.copy_local_file(mtzP1,os.path.basename(mtzP1),send_now=True)
                cm.remote_mtzP1_path = os.path.join(cm.remote_library_path,os.path.basename(mtzP1))
            print cm.change_remote_dir(actualdi)

        Config.remove_section("ARCIMBOLDO")

        allborf = cStringIO.StringIO()
        Config.write(allborf)
        allborf.flush()
        allborf.seek(0)
        allbor = allborf.read()
        allborf.close()

        #completeness = (4/3)*pi*2**3 * V /(2**d)3
        completeness = 100

        skipResLimit = False
        try:
            skipResLimit = Config.getboolean("ARCIMBOLDO-SHREDDER", "SKIP_RES_LIMIT")
        except:
            pass


        print 'Resolution is ',resolution,'\n'
        print 'Coiled coil is set to ',coiled_coil,'\n'
        if resolution > 2.5 and not skipResLimit and not coiled_coil:
            print colored("ATTENTION: Your resolution is lower than 2.5 A ARCIMBOLDO_SHREDDER will stop now.", 'red')
            sys.exit(1)
        elif resolution > 3.0 and not skipResLimit and coiled_coil:
            print colored("ATTENTION: Coiled coil protocol was active but your resolution is lower than 3.0 A, ARCIMBOLDO_SHREDDER will stop now.", 'red')
            sys.exit(1)

        xml_out = os.path.join(current_directory,nameOutput+".xml")
        xml_obj = ET.Element('arcimboldo')
        ET.SubElement(xml_obj, 'data')
        ET.SubElement(xml_obj, 'configuration')
        ET.SubElement(xml_obj.find('configuration'), 'time_start').text = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        ET.SubElement(xml_obj.find('configuration'), 'bor_name').text = input_bor
        lines_bor=allbor.split('\n')
        allbor=''
        for i in range(len(lines_bor)):
            if not lines_bor[i].startswith('skip_res_limit') or not lines_bor[i].startswith('stop_if_solved'):
                allbor=allbor+(lines_bor[i]+'\n')
        ET.SubElement(xml_obj.find('configuration'), 'bor_text').text = allbor
        ET.SubElement(xml_obj.find('configuration'), 'do_packing').text = str(USE_PACKING)
        if spaceGroup not in ["P1","P 1"]:
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

        arci_output.generateHTML(lock,current_directory,nameOutput,coiled_coil=coiled_coil)

        SystemUtility.startCheckQueue(sym,delete_check_file=False)

        if not inpconf.SHRED_LLG: # Spherical ARCIMBOLDO_SHREDDER case
            Config.set("ARCIMBOLDO-SHREDDER","library_path",os.path.join(current_directory,"./models/"))
            direc = os.path.join(current_directory,"./ARCIMBOLDO_BORGES/")
            if not os.path.exists(direc):
                os.makedirs(direc)
            #print 'SHERLOCK inpconf.RMSD_ARC before ARCIBORGES setting',inpconf.RMSD_ARC
            bord = __prepareAnewARCIMBOLDO_BORGES(direc,os.path.join(current_directory,"./models/"),
                                                  nameOutput+"_BORGESARCI",Config,inpconf, nAutoTracCyc=nAutoTracCyc)
            mend_after_translation = Config.getboolean(job_type, "mend_after_translation")
            if mend_after_translation:
                # then we will use the template model as model to swap in ARCIMBOLDO_BORGES
                print 'inside mend_after_translation condition'
                print 'model_file now',model_file
                # NOTE: Possibly the level of annotation should be input in a keyword
                print 'using second level of annotation for the mend_after_translation'
                Bioinformatics3.modify_chains_according_to_shredder_annotation(pdb=model_file,dictio_annotation=dictio_annotation_models,annotation_level='second_ref_cycle_group',output_path=current_directory)
                #print 'using first level of annotation for the mend_after_translation'
                #Bioinformatics3.modify_chains_according_to_shredder_annotation(pdb=model_file,dictio_annotation=dictio_annotation_models,annotation_level='first_ref_cycle_group',output_path=current_directory)
                # at this stage we have the path to the model file in ensembles folder, but it is not annotated nor trimmed by ss
                bord.set("ARCIMBOLDO-BORGES", "swap_model_after_translation", model_file)
            html_path = os.path.join(bord.get("GENERAL", "working_directory"),bord.get("ARCIMBOLDO-BORGES","name_job")+".html")
            string_infolist=[("Click here to follow the progress with the <b>ARCIMBOLDO_BORGES</b>: ",""+str(html_path))]
            SELSLIB2.writeOutputFile(lock=lock,DicParameters=DicParameters,ClusAll=string_infolist,outputDir=current_directory,filename=nameOutput,mode="ARCIMBOLDO-SHREDDER",step="CREATE_LINK",ensembles={},frag_fixed=0,coiled_coil=coiled_coil)
            arci_output.generateHTML(lock,current_directory,nameOutput,coiled_coil=coiled_coil)
            SystemUtility.close_connection(DicGridConn,DicParameters,cm)
            if preserveChains: # if the chains input should be maintaned in the gyre steps performed later on in BORGES
                dictio_annotation_models={} # we leave it empty, so that it is checked in ARCIMBOLDO_BORGES
                # and no chain modification is performed


            ARCIMBOLDO_BORGES.startARCIMBOLDO_BORGES(BorData=bord,isShredder=True,input_bor="borfile",
                                                 DicParameters=DicParameters,DicGridConn=DicGridConn,cm=None,sym=sym,
                                                 doTest=False,mtz_given=mtz,F_given=F,SIGF_given=SIGF,
                                                     tNCS_bool_given=tNCS_bool,
                                                 normfactors=normfactors,tncsfactors=tncsfactors,Intensities=Intensities,
                                                 Aniso=Aniso,nice=nice,out_phaser_given=aniout,fneed=fneed,
                                                     dictio_shred_annotation=dictio_annotation_models)
            sys.exit(0)
        else:
            mend_after_translation = Config.getboolean(job_type, "mend_after_translation")
            inpconf.mend_after_translation = mend_after_translation
            try:
                reference_to_fix_location = Config.get(job_type, "reference_to_fix_location")
                stry = Bioinformatics3.get_structure("test",reference_to_fix_location)
                if len(stry.get_list()) <= 0:
                    raise Exception
                skip_OMIT = Config.getboolean(job_type, "skip_OMIT")
            except:
                reference_to_fix_location = None
                skip_OMIT = False

        # NOTE CM: From here on, all code corresponds to the sequential mode
        if reference_to_fix_location != None and not os.path.exists(os.path.join(current_directory,"LIB_LOC")):
            workdr = os.path.join(current_directory,"LIB_LOC")
            list_par_bor = Config.get(job_type, "parameters_borges_matrix").split(",")
            Parameters = {}
            Parameters["model"] = reference_to_fix_location
            Parameters["dir"] = model_directory
            Parameters["wdir"] = workdr
            Parameters["continous"] = int(list_par_bor[0])
            Parameters["jumps"] = int(list_par_bor[1])
            Parameters["ncssearch"] = False
            Parameters["multimer"] = True
            Parameters["rmsd_min"] = 0.0
            Parameters["rmsd_max"] = int(list_par_bor[2])
            Parameters["rmsd_clustering"] = 0.0
            Parameters["exclude_residues_superpose"] = int(list_par_bor[3])
            Parameters["nilges"] = 0
            Parameters["enhance_fold"] = True
            pars,opt = BORGES_MATRIX.getArtificialParserOption(Parameters)
            BORGES_MATRIX.startBORGES_MATRIX(pars,opt,doCluster=False,superpose=True,sym=sym,process_join=True)

        if skip_OMIT:
            Config.set("ARCIMBOLDO-SHREDDER","library_path",os.path.join(current_directory,"./LIB_LOC/library/"))
            direc = os.path.join(current_directory,"./ARCIMBOLDO_BORGES/")
            if not os.path.exists(direc):
                os.makedirs(direc)
            bord = __prepareAnewARCIMBOLDO_BORGES(direc,os.path.join(current_directory,"./LIB_LOC/library/"),
                                                  nameOutput+"_BORGESARCI",Config,inpconf,nAutoTracCyc=nAutoTracCyc)
            html_path = os.path.join(bord.get("GENERAL", "working_directory"),bord.get("ARCIMBOLDO-BORGES","name_job")+".html")
            SELSLIB2.writeOutputFile(lock,DicParameters,[("Click here to follow the progress with the <b>ARCIMBOLDO_BORGES</b>: ",""+str(html_path))],current_directory,nameOutput,"ARCIMBOLDO-SHREDDER","CREATE_LINK",{},0,coiled_coil=coiled_coil)
            arci_output.generateHTML(lock,current_directory,nameOutput,coiled_coil=coiled_coil)
            ARCIMBOLDO_BORGES.startARCIMBOLDO_BORGES(bord,True,"borfile",DicParameters=DicParameters,
                                                     DicGridConn=DicGridConn,cm=cm,sym=sym,doTest=False,
                                                     mtz_given=mtz,F_given=F,SIGF_given=SIGF,normfactors=normfactors,
                                                     tNCS_bool_given=tNCS_bool,tncsfactors=tncsfactors,
                                                     Intensities=Intensities,Aniso=Aniso,nice=nice,
                                                     out_phaser_given=aniout,fneed=fneed,skip_mr=True)
            sys.exit(0)
        elif reference_to_fix_location != None:
            # TODO: Create a fake 1_FRF_Library/clustersNoRed.sum with each rotation at 0 0 0 to evaluate the
            # OMIT of all models (or just clusters representatives?)
            direc = os.path.join(current_directory,"./1_FRF_Library/")
            if not os.path.exists(direc):
                os.makedirs(direc)
            SELSLIB2.generateFakeMRSum(os.path.join(current_directory,"./LIB_LOC/library/"),"ROT",False,direc,"clustersNoRed")

        if test_method == "RNP":
            path_rot = os.path.join(current_directory,"1_FRF_Library/")
            SELSLIB2.generateFakeMRSum_sols(model_file,initl,"ROT",False,path_rot,"clustersNoRed",)

        if not os.path.exists(os.path.join(current_directory,"1_FRF_Library/clustersNoRed.sum")):
            (nqueue,convNames) = SELSLIB2.startFRF(DicParameters=DicParameters,cm=cm,sym=sym,nameJob="1_FRF_Library",
                                                   dir_o_liFile=model_directory,
                                                   outputDire=os.path.join(current_directory,"./1_FRF_Library/"),
                                                   mtz=mtz,MW=MW,NC=NC,F=F,SIGF=SIGF,Intensities=Intensities,
                                                   normfactors=normfactors,tncsfactors=tncsfactors,Aniso=Aniso,
                                                   nice=nice,RMSD=RMSD,lowR=99,highR=res_rot,final_rot=peaks,
                                                   save_rot=peaks,frag_fixed=fixed_frags,spaceGroup=spaceGroup,
                                                   sampl=sampl_rot,VRMS=VRMS,BFAC=BFAC,BULK_FSOL=BULK_FSOL,
                                                   BULK_BSOL=BULK_BSOL,formfactors=formfactors)
            SystemUtility.endCheckQueue()
            CluAll,RotClu = SELSLIB2.evaluateFRF_clusterOnce(DicParameters, cm, sym, DicGridConn, [], "1_FRF_Library",os.path.join(current_directory,"./1_FRF_Library/"), nqueue, quate, laue, ncs, spaceGroup, convNames, clusteringAlg, excludeLLG, fixed_frags, cell_dim, thresholdCompare, evaLLONG, applyNameFilter=True, tops=topFRF)
            SELSLIB2.writeSumClusters(CluAll, os.path.join(current_directory,"./1_FRF_Library/"), "clustersNoRed", convNames)
        else:
            SystemUtility.close_connection(DicGridConn,DicParameters,cm)
            convNames,CluAll,RotClu,encn = SELSLIB2.readClustersFromSUMToDB(DicParameters, os.path.join(current_directory,"./1_FRF_Library/clustersNoRed.sum"),"ROTSOL")
            nqueue = len(convNames.keys())

        # Check that we have something to evaluate
        if len(CluAll)==0:
            print 'Sorry, with current parameterisation, no valid rotation clusters were produced. The program will exit now'
            sys.exit(0)

        #NOTE:TEMPORANEO I do not like it!!!##############################################
        if os.path.exists(pdbcl):
            pdbcl_directory = os.path.join(current_directory,"ensemble_clustering/")
            if not (os.path.exists(pdbcl_directory)):
                os.makedirs(pdbcl_directory)
            else:
                shutil.rmtree(pdbcl_directory)
                os.makedirs(pdbcl_directory)

            shutil.copyfile(pdbcl, os.path.join(pdbcl_directory,os.path.basename(pdbcl)))

            SystemUtility.open_connection(DicGridConn,DicParameters,cm)

            (nqueue,convNames) = SELSLIB2.startFRF(DicParameters,cm,sym,"ENT_FRF",pdbcl_directory,
                                                   os.path.join(current_directory,"./ENT_FRF/"),mtz,MW,NC,F,SIGF,
                                                   Intensities,Aniso,nice,RMSD,99,res_rot,peaks,peaks,fixed_frags,
                                                   spaceGroup,sampl=sampl_rot,VRMS=VRMS,BFAC=BFAC,BULK_FSOL=BULK_FSOL,
                                                   BULK_BSOL=BULK_BSOL,formfactors=formfactors)

            SystemUtility.endCheckQueue()
            CluAll,RotClu = SELSLIB2.evaluateFRF_clusterOnce(DicParameters, cm, sym, DicGridConn, [], "ENT_FRF",os.path.join(current_directory,"./ENT_FRF/"), nqueue, quate, laue, ncs, spaceGroup, convNames, clusteringAlg, excludeLLG, fixed_frags, cell_dim, thresholdCompare, evaLLONG, applyNameFilter=True, tops=topFRF)

            SELSLIB2.writeSumClusters(CluAll, os.path.join(current_directory,"./ENT_FRF/"), "clustersNoRed", convNames)
            allb = []
            for root, subFolders, files in os.walk(model_directory):
                for fileu in files:
                    pdbf = os.path.join(root,fileu)
                    if pdbf.endswith(".pdb"):
                        nu = int((fileu.split("_")[0])[4:])
                        allb.append(nu)
            fromV = min(allb)
            toV = max(allb)
            SELSLIB2.analyzeROTclusters(DicParameters,os.path.join(current_directory,"1_FRF_Library/clustersNoRed.sum"),os.path.join(current_directory,"ENT_FRF/clustersNoRed.sum"),os.path.join(current_directory,"./ENT_FRF/"),thresholdCompare,clusteringAlg,quate,laue,ncs,convNames,cell_dim,evaLLONG,fromV,toV)
        #TEMPORANEO#######################################################################

        convNames,CluAll,RotClu,encn = SELSLIB2.readClustersFromSUMToDB(DicParameters, os.path.join(current_directory,"./1_FRF_Library/clustersNoRed.sum"),"ROTSOL")

        #LIST OF CLUSTERS TO EVALUATE
        stats,listRotaClus = SELSLIB2.__statsSteps(DicParameters, CluAll, convNames, fixed_frags)
        listRotaClus = sorted(listRotaClus,reverse=True)
        mean_all_llg = map(lambda x: x[1], listRotaClus)
        mean_all_llg = numpy.mean(numpy.array(mean_all_llg))
        priorityClusters = []
        for t in range(len(listRotaClus)):
            distpdb,llgclu,nclu=listRotaClus[t]
            #print diff, (best*50/100.0), diff < (best*50/100.0)
            if llgclu >= mean_all_llg-10: #(best*50/100.0):
                priorityClusters.append(nclu)

        orderedClusters = priorityClusters

        i = 0

        limitstoclu = Config.get(job_type, "clusters")

        onerun = True
        if limitstoclu != None and limitstoclu  not in ["", "all"]:
            limitstoclu = limitstoclu.split(",")
            orderedClusters = []
            onerun = True
            for cru in limitstoclu:
                orderedClusters.append(int(cru))

        for step_i in range(2):
            if step_i == 0 and onerun:
                continue

            for i in orderedClusters:
                topExp_run = 0
                if step_i == 0:
                    topExp_run = None
                else:
                    topExp_run = topExp

                fixed_frags = 1
                nfixfr = 1
                convNames,CluAll,RotClu,encn = SELSLIB2.readClustersFromSUMToDB(DicParameters, os.path.join(current_directory,"./1_FRF_Library/clustersNoRed.sum"),"ROTSOL")
                threshPrevious = thresholdCompare

                cycle_ref = Config.getint(job_type, "number_cycles_model_refinement")

                if SHRED_METHOD == "borges_superposition":
                    model_file = convNames[CluAll[i]["heapSolutions"].asList()[0][1]["name"]]
                    howmany,indic,chunk_range = __launchShredExec("sequential",Config,job_type,model_file,trim_to_polyala,maintainCys,os.path.join(current_directory,"models"),str(i))

                chunk_sizes = [chunk_range]
                cycle_ref = len(chunk_sizes)

                for q in range(cycle_ref):
                    if not os.path.exists(os.path.join(current_directory,"./2_OMIT_LIBRARY/"+str(i)+"/"+str(q)+"/clustersNoRed.sum")) or not os.path.exists(os.path.join(current_directory,"./library")):
                        sumPath = ""
                        sumPath = os.path.join(current_directory,"./1_FRF_Library/clustersNoRed.sum")
                        #modin = "RGR"
                        modin = test_method
                        convNames = SELSLIB2.startOMITllg(DicParameters=DicParameters,cm=cm,sym=sym,
                                                          DicGridConn=DicGridConn,mode=modin,sizes=chunk_sizes[q],
                                                          nameJob="2_OMIT_LIBRARY_"+str(i)+"_"+str(q),
                                                          outputDire=os.path.join(current_directory,
                                                                                  "./2_OMIT_LIBRARY/"+str(i)+"/"+
                                                                                  str(q)+"/"),
                                                          model_file=model_file,mtz=mtz,MW=MW,NC=NC,F=F,SIGF=SIGF,
                                                          Intensities=Intensities,Aniso=Aniso,normfactors=normfactors,
                                                          tncsfactors=tncsfactors,nice=nice,RMSD=RMSD,lowR=99,
                                                          highR=res_rot,spaceGroup=spaceGroup,frag_fixed=fixed_frags,
                                                          convNames=convNames,quate=quate,laue=laue,ncs=ncs,
                                                          clusteringAlg=clusteringAlg, cell_dim=cell_dim,
                                                          thresholdCompare=thresholdCompare, evaLLONG=evaLLONG,
                                                          sumPath=sumPath, howmany=howmany, indic=indic,
                                                          LIMIT_CLUSTER=i, USE_TNCS=USE_TNCS, sampl=sampl_rot,
                                                          VRMS=VRMS, BFAC=BFAC, trim_to_polyala=trim_to_polyala,
                                                          sigr=sigr, sigt=sigt, preserveChains=preserveChains, ent=ent,
                                                          BULK_FSOL=BULK_FSOL, BULK_BSOL=BULK_BSOL, RNP_GYRE=RNP_GYRE,
                                                          formfactors=formfactors)
                        #CluAll = SELSLIB2.filterAndCountClusters(CluAll, convNames, "llg", quate, laue, ncs, cell_dim,clusteringAlg, thresholdCompare, unify=True)
                        SELSLIB2.writeSumClusters(CluAll,os.path.join(current_directory, "./2_OMIT_LIBRARY/"+str(i)+"/"+str(q)+"/"), "clustersNoRed", convNames, LIMIT_CLUSTER=i)
                    else:
                        convNames,CluAll,RotClu,encn = SELSLIB2.readClustersFromSUMToDB(DicParameters,os.path.join(current_directory, "./2_OMIT_LIBRARY/"+str(i)+"/"+str(q)+"/clustersNoRed.sum"),"ROTSOL",LIMIT_CLUSTER=i)

        try:
            SystemUtility.open_connection(DicGridConn,DicParameters,cm)
            if hasattr(cm,"channel"):
                actualdi = cm.get_remote_pwd()
                print cm.change_remote_dir("..")
                print cm.remove_remote_dir(model_directory,model_directory)
                print cm.change_remote_dir(actualdi)

            SystemUtility.close_connection(DicGridConn,DicParameters,cm)
        except:
            pass


        for i in orderedClusters:
            print '\n Evaluating the ',i,' rotation cluster of the list of sorted clusters\n'
            pdbfa = os.path.join(current_directory,"./library/peaks_"+str(i)+"_0.pdb")
            pdbfb = os.path.join(current_directory,"./library/pklat_"+str(i)+"_0.pdb")
            pdbfc = os.path.join(current_directory,"./library/overt_"+str(i)+"_0.pdb")
            pdbf1 = os.path.join(current_directory,"./library/percentile40_"+str(i)+"_0.pdb")
            pdbf2 = os.path.join(current_directory,"./library/percentile50_"+str(i)+"_0.pdb")
            pdbf3 = os.path.join(current_directory,"./library/percentile55_"+str(i)+"_0.pdb")
            pdbf4 = os.path.join(current_directory,"./library/percentile60_"+str(i)+"_0.pdb")
            pdbf5 = os.path.join(current_directory,"./library/percentile65_"+str(i)+"_0.pdb")
            pdbf6 = os.path.join(current_directory,"./library/percentile70_"+str(i)+"_0.pdb")
            pdbf7 = os.path.join(current_directory,"./library/percentile75_"+str(i)+"_0.pdb")
            pdbf8 = os.path.join(current_directory,"./library/percentile80_"+str(i)+"_0.pdb")
            pdbf9 = os.path.join(current_directory,"./library/percentile85_"+str(i)+"_0.pdb")

            # TODO: Wrap all these common operations of preparing a LITE run in a single function that gets called each time
            # # Also have different modes
            # mode_seq = 'NORMAL'
            # # Three modes: FAST, NORMAL, DEEP
            # # FAST: only peaks, pklat, overt
            # # NORMAL: percentile70,percentile75, peaks, pklat, overt
            # # DEEP: all of them
            # if mode_seq == 'NORMAL':
            #     list_models_to_evaluate = [pdbfa,pdbfb,pdbfc,pdbf6,pdbf7]
            # elif mode_seq == 'FAST':
            #     list_models_to_evaluate = [pdbfa,pdbfb,pdbfc]
            # elif mode_seq == 'DEEP':
            #     list_models_to_evaluate = [pdbfa,pdbfb,pdbfc,pdbf1,pdbf2,pdbf3,pdbf4,pdbf5,pdbf6,pdbf7,pdbf8,pdbf9]
            #
            # def submit_ALITE_from_SHREDDER_SEQ(cwd,cluster,model):
            #     print 'model is ',model
            #     #path_wd = os.path.join(current_directory,"./ARCI_"+str(cluster)+"/percentile40/
            #
            # for model in list_models_to_evaluate:
            #     submit_ALITE_from_SHREDDER_SEQ(cwd=current_directory,cluster=i,model=model)

                

            """
            if not (os.path.exists(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile40/"))):
                    os.makedirs(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile40/"))
            bordata = __prepareAnewARCIMBOLDO(pdbf1,os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile40/"),nameOutput+"_pt40_"+str(i))
            html_path = os.path.join(bordata.get("GENERAL", "working_directory"),bordata.get("ARCIMBOLDO","name_job")+".html")
            SELSLIB2.writeOutputFile(lock,DicParameters,[("Click here to follow the progress with the ARCIMBOLDO and the model <b>"+nameOutput+"_pt40_"+str(i)+"</b>: ",""+str(html_path))],current_directory,nameOutput,"ARCIMBOLDO-SHREDDER","CREATE_LINK",{},0)
            arci_output.generateHTML(lock,current_directory,nameOutput)
            ARCIMBOLDO_LITE.startARCIMBOLDO(bordata,"borfile",DicParameters=DicParameters,DicGridConn=DicGridConn,cm=cm,sym=sym,doTest=False,mtz_given=mtz,F_given=F,SIGF_given=SIGF,normfactors=normfactors,tncsfactors=tncsfactors,Intensities=Intensities,Aniso=Aniso,nice=nice,out_phaser_given=aniout,fneed=fneed)
            SELSLIB2.LAST_AVAILABLE_ROTID = 0
            SELSLIB2.MAP_OF_ROT_COMB = {}

            if not (os.path.exists(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile50/"))):
                    os.makedirs(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile50/"))
            bordata = __prepareAnewARCIMBOLDO(pdbf2,os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile50/"),nameOutput+"_pt50_"+str(i))
            html_path = os.path.join(bordata.get("GENERAL", "working_directory"),bordata.get("ARCIMBOLDO","name_job")+".html")
            SELSLIB2.writeOutputFile(lock,DicParameters,[("Click here to follow the progress with the ARCIMBOLDO and the model <b>"+nameOutput+"_pt50_"+str(i)+"</b>: ",""+str(html_path))],current_directory,nameOutput,"ARCIMBOLDO-SHREDDER","CREATE_LINK",{},0)
            arci_output.generateHTML(lock,current_directory,nameOutput)
            ARCIMBOLDO_LITE.startARCIMBOLDO(bordata,"borfile",DicParameters=DicParameters,DicGridConn=DicGridConn,cm=cm,sym=sym,doTest=False,mtz_given=mtz,F_given=F,SIGF_given=SIGF,normfactors=normfactors,tncsfactors=tncsfactors,Intensities=Intensities,Aniso=Aniso,nice=nice,out_phaser_given=aniout,fneed=fneed)
            SELSLIB2.LAST_AVAILABLE_ROTID = 0
            SELSLIB2.MAP_OF_ROT_COMB = {}

            if not (os.path.exists(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile55/"))):
                    os.makedirs(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile55/"))
            bordata = __prepareAnewARCIMBOLDO(pdbf3,os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile55/"),nameOutput+"_pt55_"+str(i))
            html_path = os.path.join(bordata.get("GENERAL", "working_directory"),bordata.get("ARCIMBOLDO","name_job")+".html")
            SELSLIB2.writeOutputFile(lock,DicParameters,[("Click here to follow the progress with the ARCIMBOLDO and the model <b>"+nameOutput+"_pt55_"+str(i)+"</b>: ",""+str(html_path))],current_directory,nameOutput,"ARCIMBOLDO-SHREDDER","CREATE_LINK",{},0)
            arci_output.generateHTML(lock,current_directory,nameOutput)
            ARCIMBOLDO_LITE.startARCIMBOLDO(bordata,"borfile",DicParameters=DicParameters,DicGridConn=DicGridConn,cm=cm,sym=sym,doTest=False,mtz_given=mtz,F_given=F,SIGF_given=SIGF,normfactors=normfactors,tncsfactors=tncsfactors,Intensities=Intensities,Aniso=Aniso,nice=nice,out_phaser_given=aniout,fneed=fneed)
            SELSLIB2.LAST_AVAILABLE_ROTID = 0
            SELSLIB2.MAP_OF_ROT_COMB = {}

            if not (os.path.exists(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile60/"))):
                    os.makedirs(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile60/"))
            bordata = __prepareAnewARCIMBOLDO(pdbf4,os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile60/"),nameOutput+"_pt60_"+str(i))
            html_path = os.path.join(bordata.get("GENERAL", "working_directory"),bordata.get("ARCIMBOLDO","name_job")+".html")
            SELSLIB2.writeOutputFile(lock,DicParameters,[("Click here to follow the progress with the ARCIMBOLDO and the model <b>"+nameOutput+"_pt60_"+str(i)+"</b>: ",""+str(html_path))],current_directory,nameOutput,"ARCIMBOLDO-SHREDDER","CREATE_LINK",{},0)
            arci_output.generateHTML(lock,current_directory,nameOutput)

            ARCIMBOLDO_LITE.startARCIMBOLDO(bordata,"borfile",DicParameters=DicParameters,DicGridConn=DicGridConn,cm=cm,sym=sym,doTest=False,mtz_given=mtz,F_given=F,SIGF_given=SIGF,normfactors=normfactors,tncsfactors=tncsfactors,Intensities=Intensities,Aniso=Aniso,nice=nice,out_phaser_given=aniout,fneed=fneed)

            SELSLIB2.LAST_AVAILABLE_ROTID = 0
            SELSLIB2.MAP_OF_ROT_COMB = {}

            if not (os.path.exists(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile65/"))):
                    os.makedirs(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile65/"))
            bordata = __prepareAnewARCIMBOLDO(pdbf5,os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile65/"),nameOutput+"_pt65_"+str(i))
            html_path = os.path.join(bordata.get("GENERAL", "working_directory"),bordata.get("ARCIMBOLDO","name_job")+".html")
            SELSLIB2.writeOutputFile(lock,DicParameters,[("Click here to follow the progress with the ARCIMBOLDO and the model <b>"+nameOutput+"_pt65_"+str(i)+"</b>: ",""+str(html_path))],current_directory,nameOutput,"ARCIMBOLDO-SHREDDER","CREATE_LINK",{},0)
            arci_output.generateHTML(lock,current_directory,nameOutput)

            ARCIMBOLDO_LITE.startARCIMBOLDO(bordata,"borfile",DicParameters=DicParameters,DicGridConn=DicGridConn,cm=cm,sym=sym,doTest=False,mtz_given=mtz,F_given=F,SIGF_given=SIGF,normfactors=normfactors,tncsfactors=tncsfactors,Intensities=Intensities,Aniso=Aniso,nice=nice,out_phaser_given=aniout,fneed=fneed)
            SELSLIB2.LAST_AVAILABLE_ROTID = 0
            SELSLIB2.MAP_OF_ROT_COMB = {}
            """

            if not (os.path.exists(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile70/"))):
                os.makedirs(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile70/"))
            bordata = __prepareAnewARCIMBOLDO(pdbf6,os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile70/"),
                                              nameOutput+"_pt70_"+str(i),Config,inpconf)
            html_path = os.path.join(bordata.get("GENERAL", "working_directory"),bordata.get("ARCIMBOLDO","name_job")+".html")
            SELSLIB2.writeOutputFile(lock,DicParameters,[("Click here to follow the progress with the ARCIMBOLDO and the model <b>"+nameOutput+"_pt70_"+str(i)+"</b>: ",""+str(html_path))],current_directory,nameOutput,"ARCIMBOLDO-SHREDDER","CREATE_LINK",{},0,coiled_coil=coiled_coil)
            arci_output.generateHTML(lock,current_directory,nameOutput,coiled_coil=coiled_coil)
            try:
                ARCIMBOLDO_LITE.startARCIMBOLDO(bordata,"borfile",DicParameters=DicParameters,DicGridConn=DicGridConn,cm=cm,sym=sym,doTest=False,mtz_given=mtz,F_given=F,SIGF_given=SIGF,normfactors=normfactors,tncsfactors=tncsfactors,Intensities=Intensities,Aniso=Aniso,nice=nice,out_phaser_given=aniout,fneed=fneed,isShredder=True)
            except:
                print 'The ARCIMBOLDO_LITE run with the percentile70 model has not being completed'
                print 'Continue with the next ARCIMBOLDO_LITE run'
            SELSLIB2.LAST_AVAILABLE_ROTID = 0
            SELSLIB2.MAP_OF_ROT_COMB = {}

            if not (os.path.exists(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile75/"))):
                os.makedirs(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile75/"))
            bordata = __prepareAnewARCIMBOLDO(pdbf7,os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile75/"),
                                              nameOutput+"_pt75_"+str(i),Config,inpconf)
            html_path = os.path.join(bordata.get("GENERAL", "working_directory"),bordata.get("ARCIMBOLDO","name_job")+".html")
            SELSLIB2.writeOutputFile(lock,DicParameters,[("Click here to follow the progress with the ARCIMBOLDO and the model <b>"+nameOutput+"_pt75_"+str(i)+"</b>: ",""+str(html_path))],current_directory,nameOutput,"ARCIMBOLDO-SHREDDER","CREATE_LINK",{},0,coiled_coil=coiled_coil)
            arci_output.generateHTML(lock,current_directory,nameOutput,coiled_coil=coiled_coil)
            try:
                ARCIMBOLDO_LITE.startARCIMBOLDO(bordata,"borfile",DicParameters=DicParameters,DicGridConn=DicGridConn,cm=cm,sym=sym,doTest=False,mtz_given=mtz,F_given=F,SIGF_given=SIGF,normfactors=normfactors,tncsfactors=tncsfactors,Intensities=Intensities,Aniso=Aniso,nice=nice,out_phaser_given=aniout,fneed=fneed,isShredder=True)
            except:
                print 'The ARCIMBOLDO_LITE run with the percentile75 model has not being completed'
                print 'Continue with the next ARCIMBOLDO_LITE run'

            SELSLIB2.LAST_AVAILABLE_ROTID = 0
            SELSLIB2.MAP_OF_ROT_COMB = {}

            # NOTE: if this is to be uncommented, check that the call is like in the active ones
            """
            if not (os.path.exists(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile80/"))):
                    os.makedirs(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile80/"))
            bordata = __prepareAnewARCIMBOLDO(pdbf8,os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile80/"),nameOutput+"_pt80_"+str(i))
            html_path = os.path.join(bordata.get("GENERAL", "working_directory"),bordata.get("ARCIMBOLDO","name_job")+".html")
            SELSLIB2.writeOutputFile(lock,DicParameters,[("Click here to follow the progress with the ARCIMBOLDO and the model <b>"+nameOutput+"_pt80_"+str(i)+"</b>: ",""+str(html_path))],current_directory,nameOutput,"ARCIMBOLDO-SHREDDER","CREATE_LINK",{},0)
            arci_output.generateHTML(lock,current_directory,nameOutput)

            ARCIMBOLDO_LITE.startARCIMBOLDO(bordata,"borfile",DicParameters=DicParameters,DicGridConn=DicGridConn,cm=cm,sym=sym,doTest=False,mtz_given=mtz,F_given=F,SIGF_given=SIGF,normfactors=normfactors,tncsfactors=tncsfactors,Intensities=Intensities,Aniso=Aniso,nice=nice,out_phaser_given=aniout,fneed=fneed)
            SELSLIB2.LAST_AVAILABLE_ROTID = 0
            SELSLIB2.MAP_OF_ROT_COMB = {}

            if not (os.path.exists(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile85/"))):
                    os.makedirs(os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile85/"))
            bordata = __prepareAnewARCIMBOLDO(pdbf9,os.path.join(current_directory,"./ARCI_"+str(i)+"/percentile85/"),nameOutput+"_pt85_"+str(i))
            html_path = os.path.join(bordata.get("GENERAL", "working_directory"),bordata.get("ARCIMBOLDO","name_job")+".html")
            SELSLIB2.writeOutputFile(lock,DicParameters,[("Click here to follow the progress with the ARCIMBOLDO and the model <b>"+nameOutput+"_pt85_"+str(i)+"</b>: ",""+str(html_path))],current_directory,nameOutput,"ARCIMBOLDO-SHREDDER","CREATE_LINK",{},0)
            arci_output.generateHTML(lock,current_directory,nameOutput)

            ARCIMBOLDO_LITE.startARCIMBOLDO(bordata,"borfile",DicParameters=DicParameters,DicGridConn=DicGridConn,cm=cm,sym=sym,doTest=False,mtz_given=mtz,F_given=F,SIGF_given=SIGF,normfactors=normfactors,tncsfactors=tncsfactors,Intensities=Intensities,Aniso=Aniso,nice=nice,out_phaser_given=aniout,fneed=fneed)
            SELSLIB2.LAST_AVAILABLE_ROTID = 0
            SELSLIB2.MAP_OF_ROT_COMB = {}
            """
            if not (os.path.exists(os.path.join(current_directory,"./ARCI_"+str(i)+"/peaks/"))):
                os.makedirs(os.path.join(current_directory,"./ARCI_"+str(i)+"/peaks/"))
            bordata = __prepareAnewARCIMBOLDO(pdbfa,os.path.join(current_directory,"./ARCI_"+str(i)+"/peaks/"),
                                              nameOutput+"_pk_"+str(i),Config,inpconf)
            html_path = os.path.join(bordata.get("GENERAL", "working_directory"),bordata.get("ARCIMBOLDO","name_job")+".html")
            SELSLIB2.writeOutputFile(lock,DicParameters,[("Click here to follow the progress with the ARCIMBOLDO and the model <b>"+nameOutput+"_pk_"+str(i)+"</b>: ",""+str(html_path))],current_directory,nameOutput,"ARCIMBOLDO-SHREDDER","CREATE_LINK",{},0,coiled_coil=coiled_coil)
            arci_output.generateHTML(lock,current_directory,nameOutput,coiled_coil=coiled_coil)
            try:
                ARCIMBOLDO_LITE.startARCIMBOLDO(bordata,"borfile",DicParameters=DicParameters,DicGridConn=DicGridConn,cm=cm,sym=sym,doTest=False,mtz_given=mtz,F_given=F,SIGF_given=SIGF,normfactors=normfactors,tncsfactors=tncsfactors,Intensities=Intensities,Aniso=Aniso,nice=nice,out_phaser_given=aniout,fneed=fneed,isShredder=True)
            except:
                print 'The ARCIMBOLDO_LITE run with the peaks model has not being completed'
                print 'Continue with the next ARCIMBOLDO_LITE run'
            SELSLIB2.LAST_AVAILABLE_ROTID = 0
            SELSLIB2.MAP_OF_ROT_COMB = {}

            if os.path.exists(pdbfc) and not (os.path.exists(os.path.join(current_directory,"./ARCI_"+str(i)+"/overt/"))):
                os.makedirs(os.path.join(current_directory,"./ARCI_"+str(i)+"/overt/"))
            bordata = __prepareAnewARCIMBOLDO(pdbfc,os.path.join(current_directory,"./ARCI_"+str(i)+"/overt/"),
                                              nameOutput+"_po_"+str(i),Config,inpconf)
            html_path = os.path.join(bordata.get("GENERAL", "working_directory"),bordata.get("ARCIMBOLDO","name_job")+".html")
            SELSLIB2.writeOutputFile(lock,DicParameters,[("Click here to follow the progress with the ARCIMBOLDO and the model <b>"+nameOutput+"_po_"+str(i)+"</b>: ",""+str(html_path))],current_directory,nameOutput,"ARCIMBOLDO-SHREDDER","CREATE_LINK",{},0,coiled_coil=coiled_coil)
            arci_output.generateHTML(lock,current_directory,nameOutput,coiled_coil=coiled_coil)
            try:
                ARCIMBOLDO_LITE.startARCIMBOLDO(bordata,"borfile",DicParameters=DicParameters,DicGridConn=DicGridConn,cm=cm,sym=sym,doTest=False,mtz_given=mtz,F_given=F,SIGF_given=SIGF,normfactors=normfactors,tncsfactors=tncsfactors,Intensities=Intensities,Aniso=Aniso,nice=nice,out_phaser_given=aniout,fneed=fneed,isShredder=True)
            except:
                print 'The ARCIMBOLDO_LITE run with the overt model has not being completed'
                print 'Continue with the next ARCIMBOLDO_LITE run'
            SELSLIB2.LAST_AVAILABLE_ROTID = 0
            SELSLIB2.MAP_OF_ROT_COMB = {}

            if not (os.path.exists(os.path.join(current_directory,"./ARCI_"+str(i)+"/pklat/"))):
                os.makedirs(os.path.join(current_directory,"./ARCI_"+str(i)+"/pklat/"))
            bordata = __prepareAnewARCIMBOLDO(pdbfb,os.path.join(current_directory,"./ARCI_"+str(i)+"/pklat/"),
                                              nameOutput+"_pl_"+str(i),Config,inpconf)
            html_path = os.path.join(bordata.get("GENERAL", "working_directory"),bordata.get("ARCIMBOLDO","name_job")+".html")
            SELSLIB2.writeOutputFile(lock,DicParameters,[("Click here to follow the progress with the ARCIMBOLDO and the model <b>"+nameOutput+"_pl_"+str(i)+"</b>: ",""+str(html_path))],current_directory,nameOutput,"ARCIMBOLDO-SHREDDER","CREATE_LINK",{},0,coiled_coil=coiled_coil)
            arci_output.generateHTML(lock,current_directory,nameOutput,coiled_coil=coiled_coil)
            try:
                ARCIMBOLDO_LITE.startARCIMBOLDO(bordata,"borfile",DicParameters=DicParameters,DicGridConn=DicGridConn,cm=cm,sym=sym,doTest=False,mtz_given=mtz,F_given=F,SIGF_given=SIGF,normfactors=normfactors,tncsfactors=tncsfactors,Intensities=Intensities,Aniso=Aniso,nice=nice,out_phaser_given=aniout,fneed=fneed,isShredder=True)
            except:
                print 'The ARCIMBOLDO_LITE run with the pklat model has not being completed'
            SELSLIB2.LAST_AVAILABLE_ROTID = 0
            SELSLIB2.MAP_OF_ROT_COMB = {}

        sym.couldIClose = True
 
    #except SystemExit:
    #    pass
    #except:
    #    print traceback.print_exc(file=sys.stdout)
    #    if hasattr(sys, '_MEIPASS'):
    #        print "Exited with errors, temp file was ", sys._MEIPASS, " and was removed before exiting"

if __name__ == "__main__":
    main()
