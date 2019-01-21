#! /usr/bin/env python
# -*- coding: utf-8 -*-

import cStringIO
import cPickle
import copy
import datetime
import itertools
import math
import os
import operator
import pickle
import shutil
import subprocess
import sys
import traceback
from copy import deepcopy
from decimal import *
from itertools import product
from collections import defaultdict
from operator import itemgetter
from itertools import groupby

import numpy
from termcolor import colored
from Bio.PDB import *

import ADT
import BORGES_MATRIX
import SystemUtility
import geometry
import vq

import Bioinformatics3

# from Bio.PDB.DSSP import *
# from Bio.PDB.Vector import *

SUFRAGLENGTH = 3
AAList = ['ALA', 'ASX', 'CYS', 'ASP', 'GLU', 'PHE', 'GLY', 'HIS', 'ILE', 'LYS', 'LEU', 'MET', 'ASN', 'PRO', 'GLN',
          'ARG', 'SER', 'THR', 'SEC', 'VAL', 'TRP', 'XAA', 'TYR', 'GLX', 'PYL', 'UNK', 'XLE', 'MSE', 'ME0']
AADICMAP = {'ALA': 'A', 'CYS': 'C', 'ASP': 'D', 'GLU': 'E', 'PHE': 'F', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LYS': 'K',
            'LEU': 'L', 'MET': 'M', 'MSE': 'M', 'ASN': 'N', 'PRO': 'P', 'GLN': 'Q', 'ARG': 'R', 'SER': 'S', 'THR': 'T',
            'VAL': 'V', 'TRP': 'W', 'TYR': 'Y', 'UNK': '-', 'SEC': 'U', 'PYL': 'O', 'ASX': 'B', 'GLX': 'Z', 'XLE': 'J',
            'XAA': 'X', 'ME0': 'M'}
ATOAAAMAP =  dict((v,k) for k,v in AADICMAP.iteritems())
AALISTOL = AADICMAP.values()

list_id = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'  # All possible chain ids for a PDB



#######################################################################################################
#                                           SUPPORT FUNC                                              #
#######################################################################################################


string_types = (type(b''), type(u''))
import functools
import inspect
import warnings

def deprecated(reason):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    if isinstance(reason, string_types):

        # The @deprecated is used with a 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated("please, use another function")
        #    def old_function(x, y):
        #      pass

        def decorator(func1):

            if inspect.isclass(func1):
                fmt1 = "Call to deprecated class {name} ({reason})."
            else:
                fmt1 = "Call to deprecated function {name} ({reason})."

            @functools.wraps(func1)
            def new_func1(*args, **kwargs):
                warnings.simplefilter('always', DeprecationWarning)
                warnings.warn(
                    fmt1.format(name=func1.__name__, reason=reason),
                    category=DeprecationWarning,
                    stacklevel=2
                )
                warnings.simplefilter('default', DeprecationWarning)
                return func1(*args, **kwargs)

            return new_func1

        return decorator

    elif inspect.isclass(reason) or inspect.isfunction(reason):

        # The @deprecated is used without any 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated
        #    def old_function(x, y):
        #      pass

        func2 = reason

        if inspect.isclass(func2):
            fmt2 = "Call to deprecated class {name}."
        else:
            fmt2 = "Call to deprecated function {name}."

        @functools.wraps(func2)
        def new_func2(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn(
                fmt2.format(name=func2.__name__),
                category=DeprecationWarning,
                stacklevel=2
            )
            warnings.simplefilter('default', DeprecationWarning)
            return func2(*args, **kwargs)

        return new_func2

    else:
        raise TypeError(repr(type(reason)))

#######################################################################################################
#                                                                                                     #
#######################################################################################################

class PdbSubsetError(Exception):
    """
    General error class for this module.
    """

    pass


def pdbSubset(pdb, chain, residues, atom_list=["ATOM  ", "ANISOU", "HETATM", "TER   "], only_atoms=False):
    """
    Grabs a subset of a pdb file, splitting out the pdb, the chain, and the
    actual min and max in the pdb file.
    """

    out = []
    for line in pdb:

        # only look at records indicated by atom_list
        if line[0:6] not in atom_list:
            if not only_atoms:
                if line.split()[0] != "END":
                    out.append(line)
            continue

        # Grab only residues belonging to chain
        if chain == "all" or line[21:22] == chain:

            # Grab only residues above minimum and below maximum
            if residues[0] == 0 and residues[1] == 0:
                out.append(line)
            elif int(line[22:26]) >= residues[0] and \
                            int(line[22:26]) <= residues[1]:
                out.append(line)
            else:
                continue
        else:
            continue

    if len([l for l in out if l[0:6] in atom_list]) == 0:
        err = "No residues in pdb meet subset criteria!"
        raise PdbSubsetError(err)

    # Determine the actual min and max in the pdb file
    residues = [0, 0]
    all_residues = [int(l[22:26]) for l in out if l[0:6] in atom_list]
    residues[0] = min(all_residues)
    residues[1] = max(all_residues)

    return out, chain, residues


class FilterRes(Select): # Inherits from BioPython's Select Class
    """
    Selects the residues given in list_sel_res for writing out a PDB with Biopython's PDBIO.

    Keyword input:
    list_sel_res --> list with the residue objects to select
    """
    selection = []

    def __init__(self, list_sel_res):
        self.selection = map(lambda x: x.get_full_id(), list_sel_res)

    def accept_residue(self, residue):
        if residue.get_full_id() in self.selection:
            return True
        else:
            return False


class FilterResOmit(Select):
    """
    Selects all residues except the ones in list_sel_res for writing out a PDB with Biopython's PDBIO.

    Keyword input:
    list_sel_res --> list with the residue objects to omit
    """
    selection = []

    def __init__(self, list_sel_res):
        self.selection = map(lambda x: x.get_full_id(), list_sel_res)

    def accept_residue(self, residue):
        if residue.get_full_id() in self.selection:
            return False
        else:
            return True


def elongate_extremities(pdb_model, dictio_template, list_distances_full, res_to_complete, min_ah=7, min_bs=4):
    ''' Extends the models generated by shredder_spheres by looking at the extremities of the fragments.

    :param pdb_model:
    :type pdb_model: str
    :param dictio_template:
    :type dictio_template:
    :param list_distances_full:
    :type list_distances_full:
    :param res_to_complete:
    :type res_to_complete:
    :param min_ah:
    :type min_ah:
    :param min_bs:
    :type min_bs:
    :return:
    :rtype:
    '''
    
    # NOTE only to test
    #shutil.copyfile(pdb_model,pdb_model[:-4]+'bef_elongation.pdb')
    #print '\nSHERLOCK','min_ah inside elongation',min_ah
    #print 'SHERLOCK  min_bs inside elongation', min_bs, '\n'
    # NOTE only to test

    trials_limit=0
    list_already_elongated = []
    structure = getStructure(pdb_model[:-4],pdb_model)
    list_residues = sorted(Selection.unfold_entities(structure, 'R'),key=lambda x:x.get_full_id()[3][1:]) # list of residues objects sorted by id
    list_initial_nres= [ resi.get_full_id()[3][1] for resi in list_residues]
    list_initial_idss= list(set([dictio_template[nres]['ss_id_res'] for nres in list_initial_nres]))

    while trials_limit<201: # number of times you will perform the iterative process as a maximum

        trials_limit=trials_limit+1

        # Reread the PDB
        structure = getStructure(pdb_model[:-4], pdb_model)
        list_resi_sorted = sorted(Selection.unfold_entities(structure, 'R'),key=lambda x:x.get_full_id()[3][1:])
        list_distances = []
        list_nres_elongations=[]
        list_removal = []

        # Get the extremities of the continues stretches on the model
        list_extremities=[]
        continuous=[]
        continuous_fraglist=[]
        for i, resi in enumerate(list_resi_sorted):
            if i < len(list_resi_sorted) - 1 :
                check = checkContinuity(resi, list_resi_sorted[i + 1])
                if check==False:
                    list_extremities.append(('end',resi))
                    list_extremities.append(('start',list_resi_sorted[i+1]))
                    if resi.get_full_id()[3][1] not in continuous:
                        continuous.append(resi.get_full_id()[3][1])
                    continuous_fraglist.append(continuous)
                    continuous=[]
                    if i == len(list_resi_sorted) - 2:
                        continuous_fraglist.append([list_resi_sorted[i + 1].get_full_id()[3][1]])
                else:
                    if resi.get_full_id()[3][1] not in continuous:
                        continuous.append(resi.get_full_id()[3][1])
                    if list_resi_sorted[i + 1].get_full_id()[3][1] not in continuous:
                        continuous.append(list_resi_sorted[i + 1].get_full_id()[3][1])
            else:
                break
        if continuous != [] and (continuous not in continuous_fraglist):
            continuous_fraglist.append(continuous)  

        # you need to add the two extremes that are so by definition, that is, the first and the last residue
        list_extremities.append(('end', list_resi_sorted[-1]))
        list_extremities.append(('start', list_resi_sorted[0]))

        continuous_fraglist.sort(key= lambda x: len(x))
        
        list_idsizetuple=[]
        for stretch in continuous_fraglist:
            list_residues_ss = []
            for residue in stretch:
                ss_ident = dictio_template[residue]['ss_id_res']
                list_residues_ss.append((residue,ss_ident))

            list_groups= [list(group) for key,group in itertools.groupby(list_residues_ss,operator.itemgetter(1))]

            for current in list_groups:
                current_group_ss=current[0][1] # the first one gives us the key
                list_resi=[ele[0] for ele in current]
                list_idsizetuple.append((current_group_ss,list_resi))

        list_idsizetuple.sort(key= lambda x: len(x[1]))

        if res_to_complete==0:
            if len(list_idsizetuple[0][1])>= min_ah: # then there is nothing we need to check, the smallest strecht for a given ss is already over the largest limit
                break
            elif len(list_idsizetuple[0][1])>= min_bs and list_idsizetuple[0][0].startswith('bs'): # in case is a beta strand
                break
            elif len(list_idsizetuple[0][1])>= 1 and list_idsizetuple[0][0].startswith('coil'):
                break
            for i in range(len(list_idsizetuple)):
                cont_section_ss=list_idsizetuple[i]
                ss_ident_section = dictio_template[cont_section_ss[1][0]]['ss_id_res']
                list_res = map(lambda x: x[-1][1],dictio_template[cont_section_ss[1][0]]['ss_reslist'])
                if ss_ident_section.startswith('ah') and len(cont_section_ss[1]) < min_ah:
                    remain=min_ah - len(cont_section_ss[1])
                elif ss_ident_section.startswith('bs') and len(cont_section_ss[1]) < min_bs:
                    remain=min_bs - len(cont_section_ss[1])
                
                # rest is in common
                not_yet=[val for val in list_res if val not in cont_section_ss[1]]
                for l in range(1,len(list_idsizetuple)):
                    longest_ss_id=list_idsizetuple[-l][0]
                    longest_ss_res=list_idsizetuple[-l][1]
                    if longest_ss_id==ss_ident_section:
                        continue
                    else:
                        break
                # check that longest_ss does not contain already residues we want to add
                if len(set(not_yet).intersection(set(longest_ss_res)))!=0: # THIS SHOULD NOT HAPPEN!
                    print 'There was a problem, please report to bugs-borges@ibmb.csic.es'
                    sys.exit(0)
                else:
                    list_removal.extend(longest_ss_res[-remain:])
                for index,_ in enumerate(not_yet):
                    if index==len(list_removal):
                        break
                    list_nres_elongations.append(not_yet[index])
                break
        elif res_to_complete<0:
            print 'Something very wrong happened, please report to bugs-borges@ibmb.csic.es'
            sys.exit(1)
        else:
            if trials_limit==201:
                if res_to_complete > 10:
                    # Then I want to exclude this model
                    return dictio_template,False
                else:
                    # Then I am fine, just return OK
                    return dictio_template,True
        # Retrieve the distance from the CA defined in center to all the extremities
        for _,residue_tuple in enumerate(list_extremities):
            residue = residue_tuple[1]
            tag_ext = residue_tuple[0]
            nres = residue.get_full_id()[3][1]
            for i,_ in enumerate(list_distances_full):
                if list_distances_full[i][0]==nres:
                    list_distances.append((list_distances_full[i][1],residue.get_full_id(),tag_ext))
        list_distances.sort(key = lambda x : x[0])

        # Check that the extremes can be elongated
        for i,_ in enumerate(list_distances):
            tag_ext=list_distances[i][2]
            resi_full_id=list_distances[i][1]
            nres = (resi_full_id[3][1])
            # modify reslist to check the numerical id only
            filter_reslist = map(lambda x: x[-1], dictio_template[nres]['ss_reslist'])
            preext_ind=(filter_reslist).index(resi_full_id[-1])
            # two possibilities for extension, depending on n or cterminal
            if preext_ind==0 and tag_ext=='start': # we can't extend below
                continue
            elif preext_ind==len(filter_reslist)-1 and tag_ext=='end': # we can't extend after
                continue
            else:
                if tag_ext=='end':
                    sup_add=filter_reslist[preext_ind + 1][1]
                    if (sup_add not in list_already_elongated) and (sup_add not in list_initial_nres):
                        list_nres_elongations.append(sup_add)
                elif tag_ext=='start':
                    inf_add=filter_reslist[preext_ind - 1][1]
                    if (inf_add not in list_already_elongated) and (inf_add not in list_initial_nres):
                        list_nres_elongations.append(inf_add)

        # If there are no points for elongation we need to go to another secondary structure element
        if len(list_nres_elongations) == 0:
            for i,_ in enumerate(list_distances_full):
                if (list_distances_full[i][0] not in list_already_elongated) and \
                        (list_distances_full[i][0] not in list_initial_nres) and \
                        (dictio_template[list_distances_full[i][0]]['ss_id_res'] not in list_initial_idss):
                    next_res=list_distances_full[i][0]
                    list_nres_elongations.extend([next_res])
                    break
                else:
                    continue

        # Remove what needs to be removed
        if len(list_removal)>0:
            for model in structure.get_list():
                for chain in model.get_list():
                    for residue in chain.get_list():
                        nres_res = residue.get_full_id()[3][1]
                        if nres_res in list_removal:
                            try:
                                index_res=list_already_elongated.index(nres_res)
                                del(list_already_elongated[index_res])
                            except:
                                pass
                            try:
                                index_res2=list_initial_nres.index(nres_res)
                                del(list_initial_nres[index_res2])
                            except:
                                pass
                            mini_id = residue.id
                            chain.detach_child(mini_id)
                            res_to_complete = res_to_complete + 1
            # flush list_removal
            list_removal = []


        # Perform the actual elongation of the model
        for nres in list_nres_elongations:
            addresobj = dictio_template[nres]['residue_object']
            id_chain_where_to_add=dictio_template[nres]['ori_chain']
            if (res_to_complete > 0): # to be sure we don't add more than we need
                try:
                    structure[0][id_chain_where_to_add].add(addresobj)
                    res_to_complete=res_to_complete-1
                    list_already_elongated.append(nres)
                except:
                    exctype, value = sys.exc_info()[:2]
                    if str(value).endswith('defined twice'): # Then the residue is already in the structure
                        pass
                    else:
                        print 'Something wrong happened: ',value
                        sys.exit(0)

        # Save the model before the next iteration
        list_atoms_sorted = sorted(Selection.unfold_entities(structure, 'A'), key=lambda x:x.get_parent().get_full_id()[3][1:]) # sort by residue number
        writePDBFromListOfAtom(list_atoms_sorted, pdb_model, dictio_chains={}, renumber=False,uniqueChain=False)
        # Flush the list of the elongations
        list_nres_elongations=[]

    return dictio_template,True


def get_CA_distance_matrix(pdb_model):
    """

    :param pdb_model:
    :type pdb_model:
    :return:
    :rtype:
    """
    pdb_obj = open(pdb_model, 'r')
    parser = PDBParser()
    structure = parser.get_structure(pdb_model[:-4], pdb_obj)
    list_for_matrix=[]
    names_matrix_dict={}
    list_residues = Selection.unfold_entities(structure,'R')
    list_CA_atoms = [ residue['CA'] for _,residue in enumerate(list_residues) if 'CA' in residue]
    for i in range(len(list_CA_atoms)):
        list_for_matrix.append([])
        for j in range(len(list_CA_atoms)):
            #print 'i,list_CA_atoms[i].get_full_id()[3][1],j,list_CA_atoms[j].get_full_id()[3][1]',i,list_CA_atoms[i].get_full_id()[3][1],j,list_CA_atoms[j].get_full_id()[3][1]
            id_first=list_CA_atoms[i].get_full_id()[3][1]
            id_second=list_CA_atoms[j].get_full_id()[3][1]
            list_for_matrix[i].append(list_CA_atoms[i]-list_CA_atoms[j])
            if names_matrix_dict.has_key(id_first):
                names_matrix_dict[id_first][id_second]=[i,j]
            else:
                names_matrix_dict[id_first]={id_second: [i,j]}
    distance_CA_matrix=numpy.array(list_for_matrix)
    numpy.set_printoptions(precision=3)
    #print '\n',distance_CA_matrix
    #print '\n', names_matrix_dict
    return distance_CA_matrix,names_matrix_dict


def get_sorted_distance_list_to_CA(dist_matrix,convNamesMatrix,center_name):
    """

    :param dist_matrix:
    :type dist_matrix:
    :param convNamesMatrix:
    :type convNamesMatrix:
    :param center_name:
    :type center_name:
    :return:
    :rtype:
    """
    #print ' I need to get all distances to residue ',center_name
    #print 'check where to search in the matrix, convNamesMatrix[int(center_name)]',convNamesMatrix[int(center_name)]
    list_distances=[]
    key_center=int(center_name)
    list_possible_keys=convNamesMatrix.keys()
    for _,key in enumerate(list_possible_keys):
        index_i=convNamesMatrix[key_center][key][0]
        index_j=convNamesMatrix[key_center][key][1]
        # Get the values with the correct index
        value_distance=dist_matrix[index_i][index_j]
        list_distances.append((key,value_distance))
    list_distances.sort(key = lambda x: x[1])
    #return list_distances[1:]
    return list_distances


def fillSecondaryStructureGaps(pdb_model, dictio_template):
    pdb_obj = open(pdb_model, 'r')
    parser = PDBParser()
    structure = parser.get_structure(pdb_model[:-4], pdb_obj)
    list_resi = Selection.unfold_entities(structure, 'R')
    for i, resi in enumerate(list_resi):
        if i + 1 < len(list_resi):
            nres = (resi.get_full_id()[3][1])
            ss_ident = dictio_template[nres]['ss_id_res']
            # print "Current examined residue is ",nres," and belongs to ",ss_ident
            nres2 = (list_resi[i + 1]).get_full_id()[3][1]
            ss_ident2 = dictio_template[nres2]['ss_id_res']
            # print "The following residue is",nres2,' and belongs to',ss_ident2
            if ss_ident == None or ss_ident2 == None:
                continue  # we skip the possibility that they are equal because this is None because the coil has been left
            if ss_ident == ss_ident2:
                # print "These two residues belong to the same secondary structure element"
                check = checkContinuity(resi, list_resi[i + 1])
                if check == False:
                    # print "These two residues have a gap in between even if belonging to the same SS element. Need to solve it!"
                    add = False
                    for j in range(len(dictio_template[nres]['ss_reslist'])):
                        checkres = dictio_template[nres]['ss_reslist'][j][-1]
                        if checkres == resi.get_full_id()[-1]:
                            # print "Starting to add"
                            add = True
                        if checkres == list_resi[i + 1].get_full_id()[-1]:
                            # print "Finishing to add"
                            break
                        if add == True and checkres != resi.get_full_id()[-1]:
                            ncheckres = checkres[1]
                            # print "Adding ncheckres",ncheckres
                            # print "dictio_template[ncheckres]['residue_object']",dictio_template[ncheckres]['residue_object']
                            checkresobj = dictio_template[ncheckres]['residue_object']
                            chain_where_to_add = resi.get_parent()
                            chain_to_add_id = chain_where_to_add.id
                            structure[0][chain_to_add_id].add(checkresobj)
    io = PDBIO()
    io.set_structure(structure)
    io.save(pdb_model)


def modifyChainsShredderAnnotation(pdb, dictio_annotation, annotation_level, output_path):
    """Given a pdb or a list of pdbs, using the annotation dictionary, uses one of the annotation levels and produce and rewrites the pdbs with that chain definition
    pdb can be a string or a list of strings, containing the paths to the pdbs to modify
    dictio_annotation has the following format:
    -  one key per each residue inside
    419: {'residue_object': <Residue ARG het=  resseq=419 icode= >, 'ss_type_res': 'bs', 'ori_nameres': 'ARG', 'ori_nres': 419, 'ss_reslist': [('1hdh_0_0', 0, 'A', (' ', 419, ' ')), ('1hdh_0_0', 0, 'A', (' ', 420, ' ')), ('1hdh_0_0', 0, 'A', (' ', 421, ' ')), ('1hdh_0_0', 0, 'A', (' ', 420, ' ')), ('1hdh_0_0', 0, 'A', (' ', 421, ' '))], 'first_ref_cycle_group': 'group0', 'third_ref_cycle_group': 'group21', 'second_ref_cycle_group': 'group0', 'ss_id_res': 'bs36', 'ori_chain': 'A', 'ori_full_id': ('1hdh_0_0', 0, 'A', (' ', 419, ' '))}
    annotation level can be: 'third_ref_cycle_group','second_ref_cycle_group','first_ref_cycle_group'. As the keys for the residue dictionary
    output_path is the path where the pdb(s) with the changes in the annotation must be written
    """
    dictio_chainid = {}
    if not isinstance(pdb, list):
        pdb = [pdb]
    for i, pdb_file in enumerate(pdb):
        structure = getStructure(os.path.basename(pdb_file[:-4]),pdb_file)
        for model in structure:
            for chain in model:
                for residue in chain:
                    key_chain = residue.get_full_id()  # that is the key for the dictio_chains dictionary
                    key_annotation = key_chain[3][1]
                    #print '\n\nEvaluating residue ',key_chain
                    #print 'dictio_annotation[key_annotation]',dictio_annotation[key_annotation]
                    group = int(dictio_annotation[key_annotation][annotation_level][5:])
                    indx_group=group
                    try:
                        #print 'Trying to use list_id[indx_group]',list_id[indx_group]
                        dictio_chainid[key_chain] = list_id[indx_group]  # the chain id must be different per each different group!
                    except:
                        print 'There are too many groups defined, there are not any more possible ids'
                        sys.exit(0)
        outputpdb_path = os.path.join(output_path, os.path.basename(pdb_file))
        # print 'Saving annotated pdb to ',outputpdb_path
        pdb_file_atoms = Selection.unfold_entities(structure, 'A')
        pdb_file_atoms=sorted(pdb_file_atoms,key=lambda x:x.get_parent().get_full_id()[3][1]) # sort by residue number
        writePDBFromListOfAtom(reference=pdb_file_atoms, outputFilename=outputpdb_path,
                               dictio_chains=dictio_chainid, renumber=False, uniqueChain=False)


def shredder_template_annotation(model_file, current_directory, bfacnorm=True, poliA=True, cys=False, remove_coil=True,
                                 nres_extend=0,min_alpha=7,min_beta=4,min_diff_ah=0.45, min_diff_bs=0.2,
                                 gyre_preserve_chains=False,community_strategy='two_steps',
                                 algorithm_community='fastgreedy',filtergraph_A=0,filtergraph_B=20,filtergraph_C=0,
                                 filtergraph_D=15,beta_weight=2.0):
    """Annotates at different levels of secondary and tertiary structure the template for shredder.

    Args:
       model_file -- str, the path to the pdb file to process
       current_directory -- str, the path of the current working directory
       bfacnorm -- boolean, indicates whether to perform or not a bfactor normalization (default True)
       poliA -- boolean, indicates whether to convert the model to only mainchain atoms (default True)
       cys -- boolean, indicates whether to leave or not cysteine residues untouched even if poliA is True (default False)
       remove_coil -- boolean, indicates whether to leave the coil in the template or not (default True)
       nres_extend -- int, number of residues to add to secondary structure elements in the partial_coil case
       min_alpha -- int, minimum size in residues for any given helix in the template to be considered (default 7)
       min_beta -- int, minimum size in residues for any given beta strand in the template to be considered (default 4)
       min_diff_ah -- float,
       min_diff_bs -- float,
       gyre_preserve_chains -- boolean, ,(default False)
       community_strategy -- str, can be 'one_step' or 'two_steps'
       algorithm_community -- str, ,(default 'fastgreedy)
       top_distance -- int, maximal distance to use in the graph filtering (default 20)
       bottom_distance -- int, minimal distance to use in the graph filtering (default 0)
       beta_weight -- float, weight for the distances between beta strands in the community clustering

    Returns:
       dict_oristru (dict): dictionary with keys being each residue number, and the following structure dict_template[nres] = {'residue_object': BioPython residue object,
                              'ori_full_id': tuple, 'ori_chain': str, 'ori_nres': int,'ori_nameres': str, 'ss_type_res': str (can be ah,bs,coil), 'ss_reslist': list, 'ss_id_res': str,
                              'first_ref_cycle_group': str, 'second_ref_cycle_group': str,'third_ref_cycle_group': str}
       model_file (str): path to the modified template file
       distance_matrix_CA (list of lists):
       names_matrix (list):

    """

    print "\nARCIMBOLDO_SHREDDER template treatment and annotation has started:"

    # 1) Check if model should be trimmed to mainchain, leaving or not the cysteines
    print "\n Processing ", model_file
    if bfacnorm:
        print '\nBfactors are being set to a common value of 25 for all atoms'
        normalizeBFACTORS_ofPDB(model_file, 25.0)
    if poliA:
        print "\nTrimming to polyala is active, sidechains will be removed from the model\n"
        if cys:
            print "\nThe cysteine residues will kept their sidechains"
        trimSidechainsAndCysteines(pdb_model=model_file, poliA=poliA, cys=cys)

    # 2) Read the input model  and save the information about original chains
    # Renumber the pdb (but leave the chains untouched)
    parser = PDBParser()
    oristru_name=os.path.basename(model_file)[:-4]
    oristru = parser.get_structure(os.path.basename(model_file)[:-4], model_file)
    list_atoms = Selection.unfold_entities(oristru, 'A')
    writePDBFromListOfAtom(list_atoms, model_file, dictio_chains={}, renumber=True, uniqueChain=False)

    # 3) Get the secondary and tertiary structure description with BORGES_MATRIX
    graph_template, oristru = BORGES_MATRIX.getProteinGraph(pdbmodel=model_file, weight="distance_avg",
                                                                  full=True,min_ah=3,min_bs=3,
                                                                  min_diff_ah=min_diff_ah, min_diff_bs=min_diff_bs,
                                                                  sheet_factor=beta_weight)
    iterator_frag = BORGES_MATRIX.getAllFragments(graph_template)  # get all secondary structure fragments
    #for frag in iterator_frag:
    #    print frag['sequence'],frag['sstype']
    #sys.exit(0)

    # 4) Open the pdb and populate the dictionary with the residues as keys and saving some information
    if len(Selection.unfold_entities(oristru, 'M')) > 1:
        print "\n Sorry, currently the use of NMR models is not supported in ARCIMBOLDO_SHREDDER"
        sys.exit(1)
    listres_oristru = Selection.unfold_entities(oristru, 'R')
    dict_oristru = {}
    for i, res in enumerate(listres_oristru):
        tuple_id = res.get_full_id()
        chain = tuple_id[2]
        nres = tuple_id[3][1]
        nameres = res.get_resname()

        dict_oristru[nres] = {'residue_object': res, 'ori_full_id': tuple_id, 'ori_chain': chain, 'ori_nres': nres,
                              'ori_nameres': nameres, 'ss_type_res': None, 'ss_reslist': None, 'ss_id_res': None,
                              'first_ref_cycle_group': None, 'second_ref_cycle_group': None,
                              'third_ref_cycle_group': None}
    # NOTE: At the moment, cycles correspond to:
    # first cycle: community clustering groups
    # second cycle: helices independent and beta strands as they were left by the community clustering
    # third cycle: every secondary structure element independently

    # Get the total number of residues now, to compare later one how many are within secondary structure elements
    total_res=len(listres_oristru)
    print '\n Total number of residues in the input template is',total_res


    # 5) Now we need to do the community clustering and populate the dict_oristru with the information
    if remove_coil and not gyre_preserve_chains: # only then we want to annotate in groups
        print '\n Community strategy is ', community_strategy
        if community_strategy == 'two_steps':  # Two steps community
            graph_filtered = BORGES_MATRIX.get_distance_filtered_graph(graph_template, bottom_distance=filtergraph_A,
                                                                       top_distance=filtergraph_B, type_distance="avg")
            # getCommunityClusters_two_step(graph, structure, pdb_search_in, pathpdb, sort_mode, min_bs, max_bs,
            #                        writePDBandPNG=True, weight="weight")
            results_community = BORGES_MATRIX.getCommunityClusters_two_step(graph=graph_filtered, structure=oristru,
                                                                            sort_mode='avg',pdb_search_in='',
                                                                            pathpdb=None,
                                                                            min_bs=filtergraph_C, max_bs=filtergraph_D,
                                                                            writePDBandPNG=False)

        elif community_strategy == 'one_step':  # One step community
            # NOTE: currently commented the part using the distance filters and trying with new algo
            ####graph_filtered = BORGES_MATRIX.get_distance_filtered_graph(graph_template, bottom_distance=filtergraph_A,
            ###                                                           top_distance=filtergraph_B, type_distance="avg")
            ####vclust_filtered = BORGES_MATRIX.getCommunityClusters(graph_filtered,algorithm_community)
            ####results_community = BORGES_MATRIX.getDictioFromCommunityClusters(graph_filtered, vclust_filtered,
            ####                                                                 stru_template, writePDB=False)
            # (algo, graph_input, structure, pdb_search_in, pathpdb, n = None,
            # print_dendo = None, return_dendo = False, use_dendo = None, write_pdb = True,
            # weight = "weight", pack_beta_sheet = False, return_dict = False)

            vclust, results_community = BORGES_MATRIX.get_community_clusters_one_step_new_algo(algo=algorithm_community,
                                                                                               graph_input=graph_template,
                                                                                               structure=oristru,
                                                                                               pdb_search_in="",
                                                                                               pathpdb=None,
                                                                                               write_pdb=True,
                                                                                               pack_beta_sheet=True,
                                                                                               return_dict=True)





    print "\n Found ", len(iterator_frag), " secondary structure elements"
    listres_to_keep = []
    count_extra=0
    for i, dictio in enumerate(iterator_frag):
        # each element in the list is a dictionary with four keys: 'reslist', 'sstype', 'cvls', 'sequence'
        # dictio ["sstype"] --> ah
        # dictio["sequence"] --> MTVKACS
        # dictio["reslist"] --> [[['stru', 0, 'A', (' ', 336, ' '), 'GLY'], ['stru', 0, 'A', (' ', 337, ' '), 'PHE'],...]
        # dictio["cvls"] --> [2.2833399101918643, 2.2618227454832791, 2.1763591424964237,...]
        identifier_ss = dictio["sstype"] + str(i)
        print " \n Secondary structure element found: ", identifier_ss
        if dictio["sstype"] == 'ah' or dictio["sstype"] == 'bs':
            filterlist = map(lambda x: tuple(x[:-1]), dictio["reslist"])
            #print 'SHERLOCK filterlist',filterlist
            #sys.exit(0)
            print "\n     This is a ", dictio["sstype"], " of ", len(filterlist), " residues --> ",dictio['sequence']
            if (len(filterlist) < min_alpha and dictio["sstype"] == 'ah') or (len(filterlist) < min_beta and dictio["sstype"] == 'bs'):
                continue
            dictio["reslist"]=filterlist # we do not need sequence at this point, we can reduce it to its ids
            filterlist.sort()
            # Check if we need to elongate and how many residues
            if nres_extend!=0: # only in the partial_coil case
                # upwards
                first_res_id=filterlist[0][-1][1]
                elong_list_id=[]
                if dict_oristru.has_key(first_res_id-nres_extend):
                    #print '\nwe can extend upwards'
                    for indx in range(first_res_id-nres_extend,first_res_id):
                        # First check if we are entering in another secondary structure
                        if dict_oristru[indx]['ss_type_res']!=None:
                            #print 'We are not free to go, we are accessing another secondary structure'
                            break
                        dict_oristru[indx]['ss_type_res'] = dictio["sstype"]
                        dict_oristru[indx]['ss_id_res'] = identifier_ss
                        dict_oristru[indx]['first_ref_cycle_group']= dict_oristru[first_res_id]['first_ref_cycle_group']
                        dict_oristru[indx]["ori_full_id"]=('stru', dict_oristru[indx]["ori_full_id"][1],
                                                           dict_oristru[indx]["ori_full_id"][2],
                                                           dict_oristru[indx]["ori_full_id"][3])
                        filterlist.append(dict_oristru[indx]["ori_full_id"])
                        filterlist.sort()
                        elong_list_id.append(indx)
                    for indx in elong_list_id: # we want to iterate directly on the ids
                        dict_oristru[indx]['ss_reslist'] = filterlist
                        count_extra = count_extra + 1
                        #print 'Assigning new ss_reslist to ',indx
                        #print "dict_oristru[indx]['ss_reslist']",dict_oristru[indx]['ss_reslist']
                else:
                    continue
                    #print 'sorry, we can not extend upwards'

                # downwards
                #print 'filterlist[-1]',filterlist[-1]
                last_res_id=filterlist[-1][-1][1]
                #print 'last_res_id',last_res_id
                if dict_oristru.has_key(last_res_id+nres_extend):
                    #print 'we can extend downwards'
                    #print 'filterlist before',filterlist
                    elong_list_id=[]
                    for indx in range(last_res_id+1,last_res_id+nres_extend+1):
                        #print 'indx',indx
                        #print 'dict_oristru[indx] before',dict_oristru[indx]
                        if dict_oristru[indx]['ss_type_res']!=None:
                            #print 'We are not free to go, we are accessing another secondary structure'
                            break
                        dict_oristru[indx]['ss_type_res'] = dictio["sstype"]
                        dict_oristru[indx]['ss_id_res'] = identifier_ss
                        dict_oristru[indx]['first_ref_cycle_group']= dict_oristru[last_res_id]['first_ref_cycle_group']       
                        #print 'dict_oristru[indx] after',dict_oristru[indx]
                        #print 'dict_oristru[indx]["ori_full_id"] before',dict_oristru[indx]["ori_full_id"]
                        dict_oristru[indx]["ori_full_id"]=('stru', dict_oristru[indx]["ori_full_id"][1], dict_oristru[indx]["ori_full_id"][2], dict_oristru[indx]["ori_full_id"][3])
                        #print 'dict_oristru[indx]["ori_full_id"] after ',dict_oristru[indx]["ori_full_id"]
                        filterlist.append(dict_oristru[indx]["ori_full_id"])
                        filterlist.sort()
                        elong_list_id.append(indx)
                    #print 'filterlist after',filterlist
                    for indx in elong_list_id: # we want to iterate directly on the ids
                        dict_oristru[indx]['ss_reslist'] = filterlist
                        count_extra = count_extra + 1
                        #print 'Assigning new ss_reslist to ',indx
                        #print "dict_oristru[indx]['ss_reslist']",dict_oristru[indx]['ss_reslist']
                else:
                    continue
                    #print 'sorry, we can not extend downwards'

            listres_to_keep.extend(filterlist)

            if dictio["sstype"] == 'ah' or dictio["sstype"] == 'bs':
                for j in range(len(filterlist)):
                    key = filterlist[j][3][1]
                    dict_oristru[key]['ss_type_res'] = dictio["sstype"]
                    dict_oristru[key]['ss_id_res'] = identifier_ss
                    dict_oristru[key]['ss_reslist'] = filterlist
        # NOTE CM: I am commenting this because annotation of the coil in BM is leaving residues out
        #if dictio["sstype"] == 'coil':
        #    filterlist = map(lambda x: tuple(x[:-1]), dictio["reslist"])
        #    print "\n     This is a ", dictio["sstype"], " of ", len(filterlist), " residues --> ",dictio['sequence']
        #    dictio["reslist"]=filterlist # we do not need sequence at this point, we can reduce it to its ids
        #    filterlist.sort()
            #print 'filterlist',filterlist
        #    identifier_ss = dictio["sstype"] + str(i)
        #   for j in range(len(filterlist)):
        #       key = filterlist[j][3][1]
        #        dict_oristru[key]['ss_type_res'] = dictio["sstype"]
        #        dict_oristru[key]['ss_id_res'] = identifier_ss
        #        dict_oristru[key]['ss_reslist'] = filterlist


    # Annotate the dictonary by groups if community was performed
    if remove_coil and not gyre_preserve_chains:  # only then we want to annotate in groups

        # Check community results
        if len(results_community.keys()) <= 0:
            print '\nWith current community clustering strategy there are no clusters returned, please check'
            sys.exit(1)

        # Get the correct ids to use and annotate groups for gyre and gimble
        list_used_ids=[]
        for key in sorted(results_community.keys()):
            tuple_id = key
            nres = tuple_id[3][1]
            dict_oristru[nres]['first_ref_cycle_group'] = results_community[key]
            ide=int(results_community[key].split("group")[1])
            if ide not in list_used_ids:
                list_used_ids.append(ide)
        list_used_ids.sort()
        last_used_id=list_used_ids[-1]
        #print 'list_used_ids',list_used_ids
        #print 'last_used_id',last_used_id
        #sys.exit(0)

        # Perform the annotation
        number_id = last_used_id  # this corresponds to the last one used in the community clustering
        for i, dictio in enumerate(iterator_frag):
            print '\n Processing element ',i,' that corresponds to ',dictio
            if dictio["sstype"] == 'ah':
                print 'This is an alpha helix formed by ',dictio["reslist"]
                for j in range(len(dictio["reslist"])):
                    key = dictio["reslist"][j][3][1]
                    dict_oristru[key]['third_ref_cycle_group'] = 'group' + str(number_id)  # helices are treated independently in both second and third cycle grouping
                    dict_oristru[key]['second_ref_cycle_group'] = 'group' + str(number_id)
                number_id=number_id+1 # next group
            elif dictio["sstype"] == 'bs':
                print 'This is a beta strand formed by ',dictio["reslist"]
                for j in range(len(dictio["reslist"])):
                    key = dictio["reslist"][j][3][1]
                    dict_oristru[key]['third_ref_cycle_group'] = 'group' + str(number_id)  # one per beta strand
                    dict_oristru[key]['second_ref_cycle_group'] = dict_oristru[key]['first_ref_cycle_group'] # this will keep the same beta community as in the first grouping
                number_id=number_id+1 # next group
            else:
                # coil case
                continue
    # 6) If remove_coil has been set, remove that residues from the model and the dictionary
    if remove_coil:
        for model in oristru.get_list():
            for chain in model.get_list():
                for residue in chain.get_list():
                    id_res = residue.get_full_id()
                    mini_id = residue.id
                    nres = mini_id[1]
                    if id_res not in listres_to_keep:
                        chain.detach_child(mini_id)
                        dict_oristru.pop(nres, None)
                    if dict_oristru.has_key(nres) and dict_oristru[nres]['first_ref_cycle_group']==None:
                        chain.detach_child(mini_id)
                        dict_oristru.pop(nres, None)
    else: # NOTE CM: Annotation of the coil in BM is leaving residues out so everything not ss, is coil
        count_coil=0
        for model in oristru.get_list():
            for chain in model.get_list():
                for residue in chain.get_list():
                    id_res = residue.get_full_id()
                    mini_id = residue.id
                    #chain.detach_child(mini_id)
                    nres = mini_id[1]
                    #print 'SHERLOCK id_res',id_res
                    #print 'SHERLOCK mini_id',mini_id
                    #print 'SHERLOCK nres',nres
                    if dict_oristru[nres]['ss_type_res']==None:
                        #print 'SHERLOCK nres',nres
                        #print "SHERLOCK dict_oristru[nres]", dict_oristru[nres]
                        dict_oristru[nres]['ss_type_res']='coil'
                        dict_oristru[nres]['ss_id_res'] = 'coil'+str(count_coil)

                        #filterlist[('stru', 0, 'A', (' ', 10, ' ')), ('stru', 0, 'A', (' ', 11, ' ')), (
                        #'stru', 0, 'A', (' ', 12, ' ')), ('stru', 0, 'A', (' ', 13, ' ')), (
                        #           'stru', 0, 'A', (' ', 14, ' ')), ('stru', 0, 'A', (' ', 15, ' ')), (
                        #           'stru', 0, 'A', (' ', 16, ' '))]
                        dict_oristru[nres]['ss_reslist']=[id_res]
                        count_coil=count_coil+1
                        #sys.exit(0)

    # for key in sorted(dict_oristru.keys()):
    #    print '\n ',key,dict_oristru[key]
    # sys.exit(0)


    if remove_coil and not gyre_preserve_chains:
        # Check if community clustering has assigned all residues in case we did it
        # Two possibilities: there is a problem with the distances or we extended the secondary structure elements

        #print 'Check before '
        #print 'len(results_community)', len(results_community)
        #print 'len(dict_oristru.keys())', len(dict_oristru.keys())
        #print 'count_extra',count_extra
        if len(results_community) < len(dict_oristru.keys()) and nres_extend != 0:
            # it is normal that we don't have the same, check if the difference correspond to the number of added residues
            if len(results_community) + count_extra == len(dict_oristru.keys()):
                print '\n Todo OK porque hay ',count_extra,' residues ', ' podemos continuar '
            else:
                print colored("FATAL:", "red"), colored(
                "Community clustering did not asign a group to all residues, please consider modifying distances values for the community_clustering",
                'yellow')
                sys.exit(1)
        elif len(results_community) < len(dict_oristru.keys()) and nres_extend == 0:
            if not gyre_preserve_chains: # in that case we are not going to consider community clustering groups
                print colored("FATAL:", "red"), colored("Community clustering did not asign a group to all residues, please consider modifying distances values for the community_clustering",'yellow')
                sys.exit(1)
        else:
            print '\nTodo OK, Super!'
        #sys.exit(0)


    # Check % of secondary structure
    ss_percentage=float(len(listres_to_keep))/total_res*100
    print '\n The percentage of secondary structure for this template is ',ss_percentage
    if ss_percentage < 50:
        print colored("""\nWARNING: With less than 50 per cent of secondary structure present in the template, it would be better to run ARCIMBOLDO_SHREDDER with the full template without removing the coil """,'yellow')
    else:
        print colored("\nMore than 50 per cent of the structure has secondary structure, continuing with the run", "magenta")

    # 5) Write the processed template to generate the models
    if not gyre_preserve_chains and remove_coil:
        print colored("\nRemove coil has been set to on, and gyre and gimble will be performed according to automatic annotation", "magenta")
        list_atoms = Selection.unfold_entities(oristru, 'A')
        list_atoms=sorted(list_atoms,key=lambda x:x.get_parent().get_full_id()[3][1]) # sort by residue number
        outpdbpath = os.path.join(current_directory, "shred_template.pdb")
        writePDBFromListOfAtom(list_atoms, outputFilename=outpdbpath, dictio_chains={}, renumber=False,
                               uniqueChain=False)
        model_file = os.path.abspath(os.path.join(current_directory, "shred_template.pdb"))
    if not gyre_preserve_chains and not remove_coil:
        print colored("\nCoil has been left in the template model and no gyre or gimble refinement will be performed"
        , "magenta")
        list_atoms = Selection.unfold_entities(oristru, 'A')
        list_atoms=sorted(list_atoms,key=lambda x:x.get_parent().get_full_id()[3][1]) # sort by residue number
        outpdbpath = os.path.join(current_directory, "shred_template.pdb")
        writePDBFromListOfAtom(list_atoms, outputFilename=outpdbpath, dictio_chains={}, renumber=False,
                               uniqueChain=False)
        model_file = os.path.abspath(os.path.join(current_directory, "shred_template.pdb"))
    if gyre_preserve_chains and remove_coil:
        print colored("\nRemove coil has been set to on, and gyre and gimble will be performed according to user-given annotation", "magenta")
        # save the model without the coil but with the chain it had at the beginning
        list_atoms = Selection.unfold_entities(oristru, 'A')
        outpdbpath = os.path.join(current_directory, "shred_template.pdb")
        list_atoms=sorted(list_atoms,key=lambda x:x.get_parent().get_full_id()[3][1]) # sort by residue number 
        writePDBFromListOfAtom(list_atoms, outputFilename=outpdbpath, dictio_chains={}, renumber=False,
                               uniqueChain=False)
        model_file = os.path.abspath(os.path.join(current_directory, "shred_template.pdb"))
    if gyre_preserve_chains and not remove_coil:
        print colored("\nThe coil has been left, and gyre and gimble will be performed according to user-given annotation", "magenta")
        # save model with the coil but making sure non-annotated residues are not considered. Keep chains user-given
        list_atoms = Selection.unfold_entities(oristru, 'A')
        outpdbpath = os.path.join(current_directory, "shred_template.pdb")
        list_atoms = sorted(list_atoms, key=lambda x: x.get_parent().get_full_id()[3][1])  # sort by residue number
        writePDBFromListOfAtom(list_atoms, outputFilename=outpdbpath, dictio_chains={}, renumber=False,
                               uniqueChain=False)
        model_file = os.path.abspath(os.path.join(current_directory, "shred_template.pdb"))

    #print 'check model_file',model_file
    #sys.exit(0)

    # Write the pdbs with their grouping levels to check
    if remove_coil and not gyre_preserve_chains:
        path_pdbfirst=os.path.join(current_directory,oristru_name+'_first_grouping_level.pdb')
        shutil.copy(model_file,path_pdbfirst)
        modifyChainsShredderAnnotation(pdb=path_pdbfirst, dictio_annotation=dict_oristru,
                                       annotation_level='first_ref_cycle_group', output_path=current_directory)
        path_pdbsecond=os.path.join(current_directory,oristru_name+'_second_grouping_level.pdb')
        shutil.copy(model_file,path_pdbsecond)
        modifyChainsShredderAnnotation(pdb=path_pdbsecond, dictio_annotation=dict_oristru,
                                       annotation_level='second_ref_cycle_group', output_path=current_directory)
        #shutil.copy(model_file,oristru_name+'_third_grouping_level.pdb')
        #modifyChainsShredderAnnotation(pdb=oristru_name+'_third_grouping_level.pdb', dictio_annotation=dict_oristru,
        #  annotation_level='third_ref_cycle_group', output_path=current_directory)

    # 6) Get the distance matrix between the CA
    distance_matrix_CA, names_matrix = get_CA_distance_matrix(model_file)

    # 7) Save annotation in a pkl file
    save_annotation=open(os.path.join(current_directory,'annotated_template.pkl'),'wb')
    cPickle.dump(dict_oristru,save_annotation)
    save_annotation.close()

    return model_file, dict_oristru, distance_matrix_CA, names_matrix


def shredder_spheres(working_directory, namedir, pdb_model, dictio_template, target_size,dist_matrix, convNamesMatrix, min_ah=7, min_bs=4,step=1, list_centers=[]):

    """ Generates a set of compact models.

    :param working_directory: current working directory in the SHREDDER run
    :type working_directory: str
    :param namedir: output folder
    :type namedir: str
    :param pdb_model: template to extract the models from
    :type pdb_model: str
    :param dictio_template: annotation of the pdb given in pdb_model in terms of secondary and tertiary structure
    :type dictio_template: dict
    :param target_size: size that the models should have
    :type target_size: int
    :param dist_matrix:
    :type dist_matrix:
    :param convNamesMatrix:
    :type convNamesMatrix:
    :param min_ah:
    :type min_ah:
    :param min_bs:
    :type min_bs:
    :param step: step to traverse the sequence
    :type step: int
    :param list_centers: [(name_frag(str),center(list of floats with x,y,z coord of atom)),...]
                        if not empty, only the CA in the list will be used for model generation
    :type list_centers: list of tuples
    :return:
    :rtype:
    """

    # Recognize the path and create the library folder
    current_wd = working_directory
    wd_library = os.path.join(current_wd, namedir)
    if not os.path.exists(wd_library):
        os.mkdir(wd_library)
    elif os.path.exists(wd_library):
        shutil.rmtree(wd_library)
        os.mkdir(wd_library)

    # Generate input for the search
    print '######################################################################################'
    print 'GENERATING MODELS FROM STARTING TEMPLATE AT ',pdb_model
    print '######################################################################################'

    # NOTE CM: hard block to the minimal size for the fragments.
    if min_ah > 7:
        min_ah = 7
    if min_bs > 4:
        min_bs = 4

    # Get the list with all CAs in the template
    structure = getStructure(pdb_model[:-4],pdb_model)
    list_all_CA_atoms = [ residue['CA'] for residue in Selection.unfold_entities(structure, 'R') if residue.has_id('CA')]

    # Check the list_centers option and act accordingly
    if not list_centers:  # Then we want to use ALL the centers defined by the number of residues and step
        for i in range(0, len(list_all_CA_atoms), step):
            nfragtag=str((list_all_CA_atoms[i].get_full_id())[3][1])
            center=list_all_CA_atoms[i].get_coord()
            list_centers.append((nfragtag,center))

    for i, _ in enumerate(list_centers):

        # Identify which is the residue from we will be generating the model
        name_frag = list_centers[i][0]
        print '\n \n \n \n **=====******======******======****======********===********===***********===************=====*********=====******====******=====*****'
        print '\n Processing model centered in ', name_frag

        # Obtain the list of pairwise distances between this residue and all the rest
        sorted_dist_list = get_sorted_distance_list_to_CA(dist_matrix,convNamesMatrix,name_frag)

        # Prepare the lists in which we will perform the model generation
        residues_on_list = [ [sorted_dist_list[x][0], 'off'] for x, _ in enumerate(sorted_dist_list) ]
        new_list_sort = [ [sorted_dist_list[x][0],
                           sorted_dist_list[x][1],
                           dictio_template[sorted_dist_list[x][0]]['ss_id_res']]
                          for x, _ in enumerate(sorted_dist_list)]
        only_nres = [new_list_sort[ni][0] for ni,_ in enumerate(new_list_sort)]
        only_nres_sorted = sorted(only_nres)

        # Start the model generation
        residues_on = 0

        for ires, resi in enumerate(new_list_sort):

            if residues_on > target_size:
                print '\n We passed the target size, reducing the model'
                added.sort(key=operator.itemgetter(1))
                resremove = abs(target_size-residues_on)
                count = 0
                for ind,element in enumerate(added):
                    if count == resremove:
                        break
                    indx = only_nres.index(element[1])
                    residues_on_list[indx][1] = 'off'
                    residues_on -= 1
                    count += 1

            if residues_on == target_size:
                print '\n We reached exactly the target size'
                break

            if target_size-7 < residues_on <= target_size:
                print '\n We almost reached the target size, we will complete by elongation'
                break

            if residues_on_list[ires][1] == 'on': # we skip it, it was already selected
                continue
            else:
                #resi_id=resi[0]
                resi_ss=resi[2]
                prev_resi_id=resi[0]
                if resi_ss.startswith('bs'):  # limit to minimal size of beta strands
                    limit_ss=min_bs
                elif resi_ss.startswith('ah'):  # limit to minimal size of alpha helices
                    limit_ss=min_ah
                elif resi_ss.startswith('coil'): # limit to minimal size of coil
                    limit_ss=1
                # Check what other things we can add
                added=[]
                for inext in range(ires,len(new_list_sort)):
                    if len(added) >= limit_ss:
                        break
                    current_resi_id = new_list_sort[inext][0]
                    current_resi_ss = new_list_sort[inext][2]
                    if current_resi_ss == resi_ss:
                        # If the closest residue of the same ss is not on, set it
                        if residues_on_list[inext][1] == 'off':
                            added.append((inext,current_resi_id))
                            residues_on_list[inext][1]='on'
                            residues_on = residues_on+1
                            # Add the remaining residues in between these two
                            current_ind = only_nres_sorted.index(current_resi_id)
                            prev_ind = only_nres_sorted.index(prev_resi_id)
                            if abs(current_ind-prev_ind)>1:
                                mini = min(current_ind,prev_ind)
                                maxi = max(current_ind,prev_ind)
                                list_cutind = only_nres_sorted[mini+1:maxi]
                                for ele in list_cutind:
                                    iord = only_nres.index(ele)
                                    if residues_on_list[iord][1]=='off':
                                        residues_on_list[iord][1]='on'
                                        residues_on = residues_on + 1
                                        added.append((iord, ele))
                                
                        prev_resi_id = current_resi_id

                # Check that even if we did not reach our limit by ss, there might be forming part of larger continuous
                # sections
                if len(added) < limit_ss:
                    currently_active = [ele[0] for ele in residues_on_list if ele[1] == 'on'] # current residues
                    ss_cont_list = [new_list_sort[only_nres.index(tt)] for tt in currently_active] # continuous frags
                    same_ss = [ele for ele in ss_cont_list if ele[2] == resi_ss] # residues in our current secondary str
                    same_ss.sort(key=operator.itemgetter(2, 0)) # sorted by name of ss and then by nres
                    same_ss_nres = [ele[0] for _,ele in enumerate(same_ss)]
                    to_include = set([ele[1] for _,ele in enumerate(added)])
                    already_there_cont = []
                    for k, g in groupby(enumerate(same_ss_nres), lambda (i, x): i-x): # to find the consecutive groups
                        group = map(itemgetter(1), g)
                        already_there_cont.append(group)
                    for groupi in already_there_cont:
                        check=set(groupi)
                        union_set=check.union(to_include)
                        if len(union_set)<limit_ss:
                            print 'We should not have reached this point. Please report to bugs-borges@ibmb.csic.es' 
                            sys.exit(0)

        # Write the pdb with the residues that are set to on
        to_save_nres = [ele[0] for ele in residues_on_list if ele[1] == 'on']
        pdb_obj = open(pdb_model, 'r')
        parser = PDBParser()
        structure = parser.get_structure(pdb_model[:-4], pdb_obj)
        io = PDBIO()
        io.set_structure(structure)
        for model in structure.get_list():
            for chain in model.get_list():
                for residue in chain.get_list():
                    residue_nres=residue.get_full_id()[3][1]
                    if not (residue_nres in to_save_nres):
                        chain.detach_child(residue.id)
        pdbmodel_path=wd_library + "/" + 'frag' + name_frag + '_0_0.pdb'
        new_list_atoms = Selection.unfold_entities(structure, 'A')
        new_list_atoms=sorted(new_list_atoms,key=lambda x:x.get_parent().get_full_id()[3][1]) # sort by residue number
        writePDBFromListOfAtom(new_list_atoms, pdbmodel_path, dictio_chains={}, renumber=False,uniqueChain=False)

        # Check the new current model size
        list_ca = getListCA(name=name_frag, pdbf=pdbmodel_path, mode='PDB')
        size = len(list_ca[0][0])
        print '\n     Size before elongation', size
        diff_res = target_size - size
        if diff_res>0:
            print '\n     We need to extend the secondary structure elements of the model to reach the target size by ',\
                diff_res,' residues'
            dictio_template, elong_bool = elongate_extremities(pdb_model=pdbmodel_path, dictio_template=dictio_template,
                                                            list_distances_full=sorted_dist_list,
                                                            res_to_complete=diff_res, min_ah=min_ah, min_bs=min_bs)
            if elong_bool == True: # elongation went OK, we want to keep this model
                print '\n This model was correctly elongated, we will keep it'
            else:
                print '============================================================================'
                print '\n Something went wrong with the elongation of this model, we will skip it'
                print '============================================================================' 
                os.remove(pdbmodel_path)
        else:
            print '\n     This model has already the size required'


    # Filter the redundancy that might remain anyway
    # TODO: Filter using a different method
    print "\n********************************************************************************"
    print 'Before filtering there are ',len(os.listdir(wd_library)),' models'
    filterModelsByCoordinates(wd_library)
    print 'After filtering there are ',len(os.listdir(wd_library)),' models'
    print "********************************************************************************\n"

    return dictio_template


def get_list_ss_elements(pdbinicial, onlyhelix=True, writepdb=True):
    """This function gets fragments of secondary structure from a given pdb path. Based on OLD extraction algorithm
    Input:
    pdbinicial: string, path to the pdb file,
    onlyhelix: boolean for extracting only helices (default True)
    writepdb: boolean to write in the current working directory the fragments extracted (default False)
    Output:
    list with the fragment dictionaries
    if writepdb, pdb files, one per fragment"""
    current_wd = os.getcwd()
    if not (os.path.exists(os.path.join(current_wd, pdbinicial))):
        sys.exit("\nAn error has occurred. Please make sure that you have provide a pdb file with extension .pda")
    list_dict_elements = []  # List with a dictionary per fragment
    tuplaresultado = getFragmentListFromPDB(pdbinicial, False,
                                            False)  # def getFragmentListFromPDB(pdbf,isModel,drawDistri)
    structure, list_dic_frag = tuplaresultado[0], tuplaresultado[1]
    if onlyhelix:
        for frag in list_dic_frag:
            if (frag['sstype'] == 'ch' or frag['sstype'] == 'ah'):
                list_dict_elements.append(frag)
            else:
                continue
    else:
        for frag in list_dic_frag:
            list_dict_elements.append(frag)
    if writepdb:
        for i in range(len(list_dict_elements)):
            if (list_dict_elements[i])["fragLength"] >= 4:
                tuplaresultado2 = getPDBFormattedAsString(str(0), [list_dict_elements[i]], structure,
                                                          "./")  # def getPDBFormattedAsString(nModel,lista,strucActualPDB, pathBase, dizioConv = {}, externalRes=[], useDizioConv=True, normalize=False, bfactorNor=25.0)
                filename, filecont = tuplaresultado2[0], tuplaresultado2[1]
                residue_first = filename.split("_")[1]
                filename = pdbinicial[:-4] + "_" + residue_first.strip() + "_" + list_dict_elements[i][
                    'sstype'] + "_s" + str((list_dict_elements[i])[
                                               "fragLength"]) + ".pda"  # Overwrite the one that Bioinformatics returns with a more informative one
                fichero = open(filename, "w")
                fichero.write(filecont)
                fichero.close()
    return list_dict_elements


def getIdealHelicesFromLenghts(list_length, pdb, reversed=False):
    helix_list = []
    helipdb = cStringIO.StringIO(pdb)
    stru = getStructure("helix", helipdb)
    for helix_length in list_length:
        if isinstance(helix_length, list) or isinstance(helix_length, tuple):
            helix_list.append(getIdealHelicesFromLenghts(helix_length, pdb, reversed=reversed))
        else:
            cont = 0
            lips = []
            allcont = 0
            for model in stru:
                for chain in model:
                    for res in chain:
                        if reversed and allcont < 70-helix_length:
                            allcont += 1
                            continue

                        allcont += 1
                        if cont < helix_length:
                            lips += res.get_list()
                            cont += 1
                        else:
                            break
            helipdb = getPDBFromListOfAtom(lips)
            helix_list.append(helipdb)
    return helix_list


def generatePDB(pdbf, resi_list, filepath, trim_to_polyala=True):
    root, basename = os.path.split(filepath)
    if not os.path.exists(root):
        os.makedirs(root)
    structure = getStructure("ref", pdbf)
    atoms_list = []
    for model in structure:
        for chain in model:
            for resi in chain:
                if resi.get_id()[1] in resi_list:
                    if trim_to_polyala:
                        atoms_list += [resi["CA"], resi["C"], resi["O"], resi["N"]]
                        if resi.has_id("CB"):
                            atoms_list.append(resi["CB"])
                    else:
                        for atom in resi:
                            atoms_list.append(atom)

    pdball = getPDBFromListOfAtom(atoms_list, chainFragment=True)[0]
    f = open(filepath, "w")
    f.write(pdball)
    f.close()


def writePDBWithNameSequence(basePath, listresi1, listresi2):
    name = []
    atoms1 = []
    atoms2 = []
    for t in listresi1:
        name.append(AADICMAP[t.get_resname()])
        for a in t:
            atoms1.append(a)
    for t in listresi2:
        name.append(AADICMAP[t.get_resname()])
        for a in t:
            atoms2.append(a)

    name = "".join(name)
    pathname = os.path.join(basePath, name + ".pdb")
    pdball1 = getPDBFromListOfAtom(atoms1, uniqueChain=True, chainId="A")[0]
    pdball2 = getPDBFromListOfAtom(atoms2, uniqueChain=True, chainId="B")[0]
    f = open(pathname, "w")
    f.write(pdball1)
    f.write(pdball2)
    f.close()


def generatePDBomitting(pdbf, resi_list, filepath, trim_to_polyala=True):
    """

    :param pdbf:
    :type pdbf:
    :param resi_list:
    :type resi_list:
    :param filepath:
    :type filepath:
    :param trim_to_polyala:
    :type trim_to_polyala:
    :return:
    :rtype:
    """
    root, basename = os.path.split(filepath)
    if not os.path.exists(root):
        os.makedirs(root)
    structure = getStructure("ref", pdbf)
    atoms_list = []
    for model in structure:
        for chain in model:
            for resi in chain:
                if resi.get_id()[1] not in resi_list:
                    if trim_to_polyala:
                        atoms_list += [resi["CA"], resi["C"], resi["O"], resi["N"]]
                        if resi.has_id("CB"):
                            atoms_list.append(resi["CB"])
                    else:
                        for atom in resi:
                            atoms_list.append(atom)
    try:
        pdball = getPDBFromListOfAtom(atoms_list, chainFragment=True)[0]
        f = open(filepath, "w")
        f.write(pdball)
        f.close()
    except:
        print "Cannot generate", filepath, "from"
        print "resi_list", resi_list


def sequentialRenumberListOfPdbs(pdblist):
    out = []
    chain = "A"
    for pdb in pdblist:
        for line in pdb.splitlines():
            # For and ATOM record, update residue number
            if line[0:6] == "ATOM  " or line[0:6] == "TER   ":
                num = 0 + int(line[22:26])
                epse = "%s%4i%s" % (line[0:21] + chain, num, line[26:])
                out.append(epse)
            else:
                out.append(line)
        chain = "" + str(chr((ord(chain) + 1)))
    return "\n".join(out)


def pdbOffset(pdb, offset):
    """
    Adds an offset to the residue column of a pdb file without touching anything
    else.
    """

    ## Read in the pdb file
    # f = open(pdb_file,'r')
    # pdb = f.readlines()
    # f.close()

    out = []
    for line in pdb:
        # For and ATOM record, update residue number
        if line[0:6] == "ATOM  " or line[0:6] == "TER   ":
            num = offset + int(line[22:26])
            out.append("%s%4i%s" % (line[0:22], num, line[26:]))
        else:
            out.append(line)

    return "\n".join(out)


def splitPDB(pdbf, strucc, listaFra):
    listAllSplit = []
    inde = 1
    A = 0
    cA = ""
    B = 0
    cB = ""
    C = 0
    cC = ""
    listinde = 0
    indeces = []
    stop = False
    for model in strucc.get_list():
        for chain in model.get_list():
            for residue in chain.get_list():
                if not stop:
                    if listinde == len(listaFra):
                        stop = True
                        break

                    if inde == 1:
                        cA = chain.get_id()
                        A = residue.get_id()[1]
                        indeces.append([cA, A])
                    nume = 0
                    for s in range(listinde + 1):
                        nume += listaFra[s]

                    if inde == nume:
                        cB = chain.get_id()
                        B = residue.get_id()[1]
                        indeces.append([cB, B])
                    if inde == nume + 1 and listinde < len(listaFra):
                        cC = chain.get_id()
                        C = residue.get_id()[1]
                        indeces.append([cC, C])
                        listinde += 1
                inde += 1

    for e in range(0, len(indeces), 2):
        couple = indeces[e:e + 2:1]
        # print couple
        if couple[0][0] != couple[1][0]:  # if cA != cB
            print "ERROR not residues available", indeces
            sys.exit(0)

    f = open(pdbf, "r")
    allpdb = f.readlines()
    f.close()
    for e in range(0, len(indeces), 2):
        notWriteHead = False
        if e > 0:
            notWriteHead = True
        couple = indeces[e:e + 2:1]
        p1, a, b = pdbSubset(allpdb, couple[0][0], [couple[0][1], couple[1][1]],
                             only_atoms=notWriteHead)  # (allpdb,cA,[A,B])
        listAllSplit.append("".join(p1))

    return listAllSplit


def normalizePDB(model_directory):
    # CONVERTING THE MODEL IN THE CORRECT PDB FORMAT TO MAKE THE REF IN P1
    for root, subFolders, files in os.walk(model_directory):
        for fileu in files:
            pdbf = os.path.join(root, fileu)
            if pdbf.endswith(".pdb"):
                print "PDB Structure", pdbf
                strucc = getStructure("ref", pdbf)
                f = open(pdbf, "r")
                alll = f.readlines()
                f.close()
                listaFragLength = []
                for line in alll:
                    lispli = line.split()
                    if lispli[0] == "REMARK" and lispli[1] == "TITLE":
                        work = lispli[2]
                        work = work.split("_")
                        for uuu in range(1, len(work) - 2):
                            uud = work[uuu]
                            uud = uud.split("*")
                            listaFragLength.append(int(uud[1]))
                        break

                vals = splitPDB(pdbf, strucc, listaFragLength)
                for ipa in range(1, len(vals)):
                    vals[ipa] = pdbOffset(vals[ipa].splitlines(), 5)

                f = open(pdbf, "w")
                for pa in vals:
                    f.write(pa)
                    f.write("\n")
                f.write("END   \n")
                f.close()


def normalizeBFACTORS_ofPDB(pdbf, bf):
    f = open(pdbf, "r")
    linee = f.readlines()
    f.close()

    f2 = open(pdbf, "w")
    bf = ("%.2f" % bf)
    if len(bf) <= 5:
        bf = ' ' + bf
    for linea in linee:
        if not linea.startswith("ATOM") and not linea.startswith("HETATM"):
            f2.write(linea)
        else:
            li = linea.split()
            lou = list(linea)
            lou[60] = bf[0]
            lou[61] = bf[1]
            lou[62] = bf[2]
            lou[63] = bf[3]
            lou[64] = bf[4]
            lou[65] = bf[5]
            mio = ''.join(lou)
            mio = mio.strip()
            f2.write(mio + "\n")
    f2.close()


def normalizeBFACTORS(rootdir):
    soluzioni = 1
    for root, subFolders, files in os.walk(rootdir):
        for fileu in files:
            if fileu.endswith(".pdb"):
                pdbf = os.path.join(root, fileu)
                f = open(pdbf, "r")
                linee = f.readlines()
                f.close()

                f2 = open(pdbf, "w")
                print soluzioni, pdbf
                soluzioni += 1
                for linea in linee:
                    if not linea.startswith("ATOM") and not linea.startswith("HETATM"):
                        f2.write(linea + "\n")
                    else:
                        li = linea.split()
                        lou = list(linea)
                        lou[60] = " "
                        lou[61] = "2"
                        lou[62] = "5"
                        lou[63] = "."
                        lou[64] = "0"
                        lou[65] = "0"
                        mio = ''.join(lou)
                        mio = mio.strip()
                        f2.write(mio + "\n")
                f2.close()

@deprecated("Use BORGES_MATRIX.cluster_pdbs_by_kmeans")
def clusterizeByKMeans(DicParameters, directory, referenceFile, heapSolutions, pdbf="", minForClust=10, backbone=False,
                       limitPercluster=None, minKappa=None, maxKappa=None, limitThreshold=-0.1, structure=None,
                       writeOutput=True):
    getcontext().prec = 2
    nameExp = DicParameters["nameExecution"]

    print "Reading the models..."

    if os.path.exists(referenceFile):
        tuplone = getFragmentListFromPDBUsingAllAtoms(referenceFile, False)
        listamodel = tuplone[1]

    print "Ended..."

    data = []
    ref_labels = []
    if heapSolutions == None:
        n_errors = 0
        nsoluzioni = 1
        for root, subFolders, files in os.walk(directory):
            for fileu in files:
                pdbf = os.path.join(root, fileu)
                if pdbf.endswith(".pdb"):
                    print "Evaluating file ", nsoluzioni, " that is ", pdbf
                    nodo = os.path.basename(pdbf)[:-4]
                    pdbid = nodo.split("_")[0]
                    model = nodo.split("_")[1]
                    IdSolution = nodo.split("_")[2]
                    error = False
                    rmsd = 0.0
                    try:
                        rmsd, mj, de = getRMSD(referenceFile, pdbf, "PDB", listmodel=listamodel)
                        if rmsd < 0:
                            n_errors += 1
                            error = True
                    except:
                        n_errors += 1
                        rmsd = -100
                        error = True

                    if error:
                        print "Found an rmsd error for: ", pdbf
                    nsoluzioni += 1
                    structure = getStructure("" + str(pdbid) + "_" + str(model) + "_" + str(IdSolution), pdbf)
                    tensorInertia = (geometry.calculate_moment_of_intertia_tensor(structure))[0]
                    com = geometry.center_of_mass(structure, False)
                    com = com.coord
                    shape_par = geometry.calculate_shape_param(structure)
                    data.append([rmsd, tensorInertia[0], tensorInertia[1], tensorInertia[2], com[0], com[1], com[2],
                                 shape_par[1], shape_par[2], shape_par[3]])
                    ref_labels.append((pdbid, model, IdSolution))
                    print "processed node", pdbid, model, IdSolution, rmsd, "n_sol:", nsoluzioni, "n_err:", n_errors
    elif heapSolutions != None and structure != None:
        cvs_model = DicParameters["cvsModel"]

        listaSolutions = []
        IdSolution = 0
        back_atm_li = None
        rmsT = None
        pdbid = None
        model = None
        """
        refen = referenceFile
        if os.path.exists(referenceFile):
                f = open(referenceFile,"r")
                refen = f.read()
                f.close()
        comparen = pdbf
        if os.path.exists(pdbf):
                f = open(pdbf,"r")
                comparen = f.read()
                f.close()
        """
        for solu in heapSolutions:
            back_atm_li, atm_li, cvs, pdbid, model = solu
            # rmsT = 1.0 #TODO: Compute the RMSD and the superposition using CVS
            """
            rmsd = 0.0
            try:
                 rmsd,mj,de = getRMSD(refen,comparen,"PDBSTRING",backbone=True,listmodel=listamodel)
                 if rmsd < 0:
                    print "errore",rmsd
                    continue
            except:
                 traceback.print_exc(file=sys.stdout)
                 continue
            """
            tensorInertia = (geometry.calculate_moment_of_intertia_tensor(back_atm_li))[0]
            com = geometry.center_of_mass(back_atm_li, False)
            com = com.coord
            shape_par = geometry.calculate_shape_param(back_atm_li)
            data.append([tensorInertia[0], tensorInertia[1], tensorInertia[2], com[0], com[1], com[2], shape_par[1],
                         shape_par[2], shape_par[3]])
            ref_labels.append((pdbid, model, IdSolution))
            # print "Preparing",pdbid,model,IdSolution,rmsT,tensorInertia,com,shape_par
            IdSolution += 1

    subclu = []
    if len(data) > 0:
        if len(data) > minForClust:
            kappa, whitened = __CrossValidationKParameter(data, 2, limitThreshold, minKappa=minKappa, maxKappa=maxKappa)
            print "Performing a cluster with K-Means with K=" + str(kappa) + " of " + str(len(data))

            groups, labels = vq.kmeans2(whitened, kappa, iter=20, minit="points")
            # groups, labels = vq.kmeans2(whitened,kappa,iter=20,minit="points")

            subclu = [[] for _ in range(kappa)]
            for p in range(len(labels)):
                ind = labels[p]
                name = ref_labels[p]
                rmsdv = data[p]
                # print "p",p
                # print "ind",ind
                # print "name",name
                # print "rmsdv",rmsdv
                # print labels
                # print groups
                subclu[ind].append((name) + tuple(data[p]))
        else:
            subclu = [[] for _ in range(len(data))]
            for p in range(len(data)):
                subclu[p].append((ref_labels[p]) + tuple(data[p]))

        if writeOutput:
            f = open("./clusters.txt", "w")
            f.write("Number of clusters: " + str(len(subclu)) + "\n\n")
            for clus in subclu:
                f.write("===================== " + str(len(clus)) + "\n")
                for pdbin in clus:
                    f.write("\t")
                    f.write("NAME: " + str(pdbin[0]) + " " + str(pdbin[1]) + " " + str(pdbin[2]) + " ")
                    f.write("RMSD: " + str(pdbin[3]) + " ")
                    f.write("Tensor of inertia: " + ("%.2f" % pdbin[4]) + " " + ("%.2f" % pdbin[5]) + " " + (
                        "%.2f" % pdbin[6]) + " ")
                    f.write("Center of mass: " + ("%.2f" % pdbin[7]) + " " + ("%.2f" % pdbin[8]) + " " + (
                        "%.2f" % pdbin[9]) + " ")
                    f.write("Shape Par.: " + ("%.2f" % pdbin[10]) + " " + ("%.2f" % pdbin[11]) + " " + (
                        "%.2f" % pdbin[12]) + " ")
                    f.write("\n")
                f.write("=====================\n")
            f.close()

    nodisalvati = 1
    # print "len(subclu)",len(subclu)
    return subclu


def __STDCentroidKParameter(data, v_cycles, treshJump, criteria="mean", minKappa=None, maxKappa=None, oneByone=False):
    narr = numpy.array(data)
    whitened = vq.whiten(narr)
    # whitened = vq.whiten(narr)
    valori = []

    kappa = 0
    lastkappa = 0
    start = (numpy.sqrt(len(whitened) / 2) / 2)

    if minKappa == None:
        kappa = start
    else:
        kappa = minKappa

    if maxKappa == None:
        lastkappa = start * 2 * 2
    else:
        lastkappa = maxKappa

    lastkappa = len(whitened)

    i = int(kappa)
    if i <= 0:
        i = 1

    centroids = []
    while True:
        if i > lastkappa:
            break
        print "trying kappa", i
        sys.stdout.flush()
        avg_crossv = 0.0
        avg_sqd = 0.0
        kappa_step = 0
        allcent = []
        alldist = []
        for v in range(v_cycles):
            centroids, distorsion = vq.kmeans(whitened, i, iter=20)
            allcent.append(centroids)
            alldist.append(distorsion)

        alldist = numpy.array(alldist)
        minInd = numpy.argmin(alldist)
        distorsion = None
        if criteria == "max":
            distorsion = numpy.max(alldist)
        elif criteria == "min":
            distorsion = numpy.min(alldist)
        elif criteria == "mean":
            distorsion = numpy.mean(alldist)
        else:
            print "Error!!!, criteria, ", criteria, " not recognized!"
            raise Exception("Criteria function argument not recognized!")

        centroids = allcent[minInd]
        # print "----",centroids
        # print distorsion
        # groups, labels = vq.kmeans2(training,i,iter=20,minit="points")
        print "done..."
        # D_k = [scipy.spatial.distance.cdist(whitened, [cent], 'euclidean') for cent in groups]
        # cIdx = [numpy.argmin(D,axis=1) for D in D_k]
        # dist = [numpy.min(D,axis=1) for D in D_k]
        # print "D_k",D_k
        # print ";;;",dist
        # avgWithinSS = [sum(d)/whitened.shape[0] for d in dist]
        # print ",,,,,",avgWithinSS

        """
        sum_sqd = 0
        for centroid in groups:
            print "......",centroid
            print labels
            print "-----",numpy.std(centroid)
            sum_sqd += numpy.std(centroid)
        avg_sqd = sum_sqd / len(groups)
        """
        valori.append([distorsion, i])
        print i, distorsion
        kappa = i
        if len(valori) > 1:
            jump = (valori[-2])[0] - (valori[-1])[0]
            print "difference", (valori[-2])[0] - (valori[-1])[0]
            if not oneByone and distorsion >= 3:
                i += 150
                print "Next Kappa will be", i, "increased by", 150
            elif not oneByone and not oneByone and distorsion >= 2:
                i += 100
                print "Next Kappa will be", i, "increased by", 100
            elif not oneByone and distorsion >= 1:
                i += 80
                print "Next Kappa will be", i, "increased by", 80
            elif not oneByone and distorsion >= 0.7:
                i += 70
                print "Next Kappa will be", i, "increased by", 70
            elif not oneByone and distorsion >= 0.6:
                i += 60
                print "Next Kappa will be", i, "increased by", 60
            elif not oneByone and distorsion >= 0.5:
                i += 50
                print "Next Kappa will be", i, "increased by", 50
            elif not oneByone and distorsion >= 0.4:
                i += 40
                print "Next Kappa will be", i, "increased by", 40
            elif not oneByone and distorsion >= 0.3:
                i += 30
                print "Next Kappa will be", i, "increased by", 30
            elif not oneByone and distorsion >= 0.2:
                i += 20
                print "Next Kappa will be", i, "increased by", 20
            elif not oneByone and distorsion >= 0.1:
                i += 10
                print "Next Kappa will be", i, "increased by", 10
            else:
                i += 1
                print "Next Kappa will be", i, "increased by", 1

            if jump <= -0.6:
                # kappa -= 1
                break

            if len(valori) > 2 and abs(jump) <= abs(treshJump):
                # kappa -= 1
                break
        else:
            i += 1
            print

    code, distance = vq.vq(whitened, centroids)
    # print "***",code
    return kappa, code

@deprecated("Use Silhouette coefficient in sklearn.cluster to choose the value of k")
def __CrossValidationKParameter(data, v, treshJump, minKappa=None, maxKappa=None, oneByone=False):
    narr = numpy.array(data)
    whitened = vq.whiten(narr)
    # whitened = vq.whiten(narr)
    valori = []
    whishu = deepcopy(whitened)
    numpy.random.shuffle(whishu)

    if len(data) < 4 * v:
        v = 1

    print "V-Parameter chosen for the cross-validation is: " + str(v)
    subs = numpy.array_split(whishu, v)

    kappa = 0
    lastkappa = 0
    start = int(math.floor(numpy.sqrt(len(whitened) / 2) / 2.0))

    if minKappa == None:
        kappa = start
    else:
        kappa = minKappa

    if maxKappa == None:
        lastkappa = start * 2 * 2
    else:
        lastkappa = maxKappa

    if maxKappa != None and minKappa != None and (minKappa == maxKappa):
        return minKappa, whitened

    lastkappa = len(whitened)

    i = int(kappa)
    if i <= 0:
        i = 1

    while True:
        if i > lastkappa:
            break
        print "trying kappa", i
        sys.stdout.flush()
        avg_crossv = 0.0
        for q in range(len(subs)):
            print "trying test", q
            test = subs[q]
            avg_sqd = 0.0
            kappa_step = 0
            for z in range(len(subs)):
                if z != q or v == 1:
                    training = subs[z]
                    # print "training",training
                    print "starting clustering with training", z
                    sys.stdout.flush()
                    groups, labels = vq.kmeans2(training, i, iter=20, minit="points")
                    # groups, labels = vq.kmeans2(training,i,iter=20,minit="points")
                    print "done..."

                    """
                    subclu = [[] for _ in range(i)]
                    for p in range(len(labels)):
                        ind = labels[p]
                        subclu[ind].append(training[p])

                    for clut in subclu:
                        k2,pvalue = scipy.stats.mstats.normaltest(clut)
                        print "======"
                        print "K2:",k2,"pvalue",pvalue
                        print "======"

                        for pv in pvalue:
                            if pv < 0.055:
                                kappa_step += 1
                                forceKappa = True
                                break
                    """

                    sum_sqd = 0.0
                    # print "gruppi",groups
                    for ctest in test:
                        sqd_min = numpy.inf
                        for centroid in groups:
                            sqd = 0.0
                            for drep in range(len(centroid)):
                                ep = (centroid[drep] - ctest[drep]) ** 2
                                if not numpy.isnan(ep):
                                    sqd += (centroid[drep] - ctest[drep]) ** 2
                            if sqd < sqd_min:
                                sqd_min = sqd
                                # if sqd_min > 0.1:
                        # sqd_min = numpy.inf
                        sum_sqd += sqd_min
                    avg_sqd += sum_sqd
            if v > 1:
                avg_sqd /= (v - 1)
            avg_crossv += avg_sqd

        avg_crossv /= v
        valori.append([avg_crossv, i])
        print i, avg_crossv,
        kappa = i
        if len(valori) > 1:
            jump = (valori[-2])[0] - (valori[-1])[0]
            print (valori[-2])[0] - (valori[-1])[0]
            if v == 1 and jump > 0:
                i += 1
                print "Next Kappa will be", i, "increased by", 1
            elif v == 1 and jump <= 0:
                i -= 1
                kappa = i
                break
            elif jump >= 70:
                i += 150
                print "Next Kappa will be", i, "increased by", 150
            elif jump >= 40:
                i += 80
                print "Next Kappa will be", i, "increased by", 80
            elif jump >= 30:
                i += 30
                print "Next Kappa will be", i, "increased by", 30
            elif jump >= 10:
                i += 15
                print "Next Kappa will be", i, "increased by", 15
            elif jump >= 1.0:
                i += 5
                print "Next Kappa will be", i, "increased by", 5
            else:
                i += 1

            if jump <= -0.6:
                kappa -= 1
                break

            if abs(jump) <= abs(treshJump):
                break
        else:
            i += 1
            print

    return kappa, whitened


def configureToUseDSSP(inputFile):
    # opening a tar file only if it is not yet opened
    # tar is   defined outside this def so it is conserved
    actualPDB += 1
    print "Pdb file : " + inputFile.name + " file size in bytes: " + str(inputFile.size) + " Job n. " + str(actualPDB)
    infile = tar.extractfile(inputFile)
    filename = "./temp/" + inputFile.name
    infile2 = open(filename, "w")
    shutil.copyfileobj(infile, infile2)
    infile.close()
    infile2.close()
    return filename


def configureToNotUseDSSP(inputFile):
    actualPDB += 1
    print "Pdb file : " + inputFile.name + " file size in bytes: " + str(inputFile.size) + " Job n. " + str(actualPDB)
    infile = tar.extractfile(inputFile)
    return infile


def getListCA(name, pdbf, mode, algorithm="biopython", DicParameters=None, backbone=False, listmodel=None,
              allInList=False, minResInChain=None, superpose_exclude=1, pos=[], clusterCYS=False):
    """

    :param name:
    :type name:
    :param pdbf:
    :type pdbf:
    :param mode: Can be 'DB','PDB','PRECOMPUTED','PDBSTRINGBM', 'PDBSTRING', 'PDBSTRINGBM_RESIDUES_CONSERVED'
    :type mode:
    :param algorithm:
    :type algorithm:
    :param DicParameters:
    :type DicParameters:
    :param backbone:
    :type backbone:
    :param listmodel:
    :type listmodel:
    :param allInList:
    :type allInList:
    :param minResInChain:
    :type minResInChain:
    :param superpose_exclude:
    :type superpose_exclude:
    :param pos:
    :type pos:
    :param clusterCYS:
    :type clusterCYS:
    :return:
    :rtype:
    """
    if mode == "DB" and DicParameters != None:
        corresponding = (pdbf.split("/"))[-1]
        pdbid, model, idSolution = corresponding.split("_")
        idSolution, ext = idSolution.split(".")
        nameExp = DicParameters["nameExperiment"]
        (DicParameters, db) = SystemUtility.requestConnectionDatabase(DicParameters)
        cur = db.cursor()
        cur.execute(
            "SELECT backbone,pda FROM " + nameExp + "_SOLUTIONS WHERE pdbid = '" + pdbid + "' AND model = " + model + " AND IdSolution = " + idSolution)
        nodo = cur.fetchone()
        back, pda = nodo
        reference = pickle.loads(back)
        cur.close()
        db.close()
        return reference
    elif mode == "PDB" and listmodel == None:
        structure = getStructure(name, pdbf)
        reference = []
        lineallCA = []
        lineallwCB = []
        for model in structure.get_list():
            for chain in model.get_list():
                if minResInChain != None and len(chain.get_list()) < minResInChain:
                    continue
                for residue in chain.get_list():
                    if residue.has_id("CA"):
                        atom = residue["CA"]
                        reference.append(atom)
                        if allInList:
                            if residue.has_id("CB"):
                                lineallCA.append([residue["CA"], residue["C"], residue["O"], residue["N"], residue["CB"]])
                                lineallwCB.append([residue["CA"], residue["C"], residue["O"], residue["N"]])
                            else:
                                lineallwCB.append([residue["CA"], residue["C"], residue["O"], residue["N"]])
                                lineallCA.append([residue["CA"], residue["C"], residue["O"], residue["N"]])

                    if backbone:
                        # print pdbf,residue.get_full_id()
                        if residue.has_id("CB"):
                            reference.append(residue["CB"])
                        if residue.has_id("C"):
                            reference.append(residue["C"])
                        if residue.has_id("O"):
                            reference.append(residue["O"])
                        if residue.has_id("N"):
                            reference.append(residue["N"])
        withoutcb = []
        for at in reference:
            if at.get_id() != "CB":
                withoutcb.append(at)
        if allInList:
            return [[lineallCA, lineallwCB]]
        else:
            return [[reference, withoutcb]]
    else:
        allfrags = []
        if mode == "PDB":
            allfrags = getFragmentsListWithoutCVS(pdbf)
        elif mode == "PRECOMPUTED":
            allfrags = pdbf
        elif mode.startswith("PDBSTRINGBM"):
            try:
                stru_template = getStructure("stru",cStringIO.StringIO(pdbf))
                list_resi = Selection.unfold_entities(stru_template, 'R')
                list_resi_sorted=sorted(list_resi,key=lambda x:x.get_full_id()[3][1:])
                allfrags = [list_resi_sorted]
            except:
                print sys.exc_info()
                traceback.print_exc(file=sys.stdout)
        elif mode == "PDBSTRING":
            # allfrags = getFragmentsListWithoutCVS(pdbf,notafile=True)
            # tuplone = getFragmentListFromPDBUsingAllAtoms(cStringIO.StringIO(pdbf),False)
            strucd = getStructure("ddds", cStringIO.StringIO(pdbf))
            # asde = range(len(listmodel))
            apt = []
            for model in strucd.get_list():
                for chain in model.get_list():
                    trtrtr = sorted(chain.get_unpacked_list(), __resBioOrder2)

                    # DONE: Change to Continuity by C-N distance
                    for r in range(0, len(trtrtr) - 1):
                        resi1 = trtrtr[r]
                        resi2 = trtrtr[r + 1]
                        # print resi1.get_id()
                        # print resi2.get_id()
                        if checkContinuity(resi1, resi2):
                            # if resi2.get_id()[1] != resi1.get_id()[1]+1:
                            #   print "Really contigous??",resi2.get_id()[1],resi1.get_id()[1]
                            apt.append(resi1)
                            # print "r",r,"r+1",r+1,"len(trtrtr)-2",len(trtrtr)-2,len(trtrtr)
                            if r == len(trtrtr) - 2:
                                apt.append(resi2)
                        else:
                            apt.append(resi1)
                            # allfrags.append(deepcopy(apt))
                            allfrags.append(apt)
                            apt = []
                            if r == len(trtrtr) - 2:
                                apt.append(resi2)

                    if len(apt) > 0:
                        # allfrags.append(deepcopy(apt))
                        allfrags.append(apt)
                        apt = []
                    """
                    for residue in sorted(chain.get_unpacked_list(),__resBioOrder2):
                            #print residue
                            apt.append(residue)
                            if len(apt) == listmodel[asde[0]]["fragLength"]:
                                    allfrags.append(deepcopy(apt))
                                    apt = []
                                    del asde[0]
                    """

        #print "??????????????????????????????????????",len(allfrags)
        if mode == "PDBSTRINGBM":
            listCombi = itertools.permutations(allfrags)
        elif mode == "PDBSTRINGBM_RESIDUES_CONSERVED":
            listCombi = [allfrags]
        else:
            listCombi = [allfrags]

        listValid = []
        if listmodel != None:
            """
            for fra in listmodel:
                 print "frag",fra["fragLength"]
            print "============================="
            for combi in listCombi:
                for crazy in combi:
                        print "crazy",len(crazy)
                print "-----------------"

            listCombi = itertools.permutations(allfrags)
            """
            lio = []
            for combi in listCombi:
                lio.append(combi)
            listCombi = lio

            for combi in listCombi:
                valid = False
                for ui in range(len(listmodel)):
                    frag1 = listmodel[ui]
                    frag2 = combi[ui]
                    # print "Comparing",len(frag2), frag1["fragLength"]
                    if len(frag2) != frag1["fragLength"]:
                        valid = False
                        break
                    else:
                        valid = True
                # print "is valid",valid

                if valid:
                    torange = 1
                    if algorithm in ["biopython-core", "nigels-core2"]:
                        torange = superpose_exclude
                    fragli = [[] for _ in range(len(combi))]
                    for qw in range(torange):
                        for pids in range(len(combi)):
                            it = combi[pids]
                            itans = __sublisttrim(it, qw)
                            listof = []
                            for ita in itans:
                                reference = []
                                for rt in range(len(ita)):
                                    residue = ita[rt]
                                    # if residue.has_id("CA"):
                                    # if (not clusterCYS or (clusterCYS and residue.get_resname() in ["CYS","cys","Cys"] and rt in pos)) and residue.has_id("CA"):
                                    if not clusterCYS and residue.has_id("CA"):
                                        atom = residue["CA"]
                                        reference.append(atom)
                                    # if backbone:
                                    # if (not clusterCYS or (clusterCYS and residue.get_resname() in ["CYS","cys","Cys"] and rt in pos)) and backbone:
                                    if not clusterCYS and backbone:
                                        # print pdbf,residue.get_full_id()
                                        if residue.has_id("CB"):
                                            reference.append(residue["CB"])
                                        if residue.has_id("C"):
                                            reference.append(residue["C"])
                                        if residue.has_id("O"):
                                            reference.append(residue["O"])
                                        if residue.has_id("N"):
                                            reference.append(residue["N"])
                                    if clusterCYS and residue.get_resname() in ["CYS", "cys", "Cys"] and rt in pos:
                                        if residue.has_id("CB"):
                                            reference.append(residue["CB"])
                                        if residue.has_id("SG"):
                                            reference.append(residue["SG"])

                                listof.append((reference, len(ita)))
                            fragli[pids] += listof

                    for com in product(*fragli):
                        reference = []
                        lenfrags = []
                        for fragitem in com:
                            frag, lenfra = fragitem
                            reference += frag
                            lenfrags.append(lenfra)

                        withoutcb = []
                        for at in reference:
                            if at.get_id() != "CB":
                                withoutcb.append(at)
                        listValid.append([reference, withoutcb, lenfrags])
        else:
            for combi in listCombi:
                torange = 1
                if algorithm in ["biopython-core", "nigels-core2"]:
                    torange = superpose_exclude
                fragli = [[] for _ in range(len(combi))]
                for qw in range(torange):
                    for pids in range(len(combi)):
                        it = combi[pids]
                        itans = __sublisttrim(it, qw)
                        listof = []
                        for ita in itans:
                            reference = []
                            for rt in range(len(ita)):
                                residue = ita[rt]
                                # if residue.has_id("CA"):
                                # if (not clusterCYS or (clusterCYS and residue.get_resname() in ["CYS","cys","Cys"] and rt in pos)) and residue.has_id("CA"):
                                if not clusterCYS and residue.has_id("CA"):
                                    atom = residue["CA"]
                                    reference.append(atom)
                                # if backbone:
                                # if (not clusterCYS or (clusterCYS and residue.get_resname() in ["CYS","cys","Cys"] and rt in pos)) and backbone:
                                if not clusterCYS and backbone:
                                    if residue.has_id("CB"):
                                        reference.append(residue["CB"])
                                    if residue.has_id("C"):
                                        reference.append(residue["C"])
                                    if residue.has_id("O"):
                                        reference.append(residue["O"])
                                    if residue.has_id("N"):
                                        reference.append(residue["N"])
                                if clusterCYS and residue.get_resname() in ["CYS", "cys", "Cys"] and rt in pos:
                                    if residue.has_id("CB"):
                                        reference.append(residue["CB"])
                                    if residue.has_id("SG"):
                                        reference.append(residue["SG"])
                            listof.append((reference, len(ita)))
                        fragli[pids] += listof

                #print 'len product fragli',len(list(product(*fragli)))
                #print "analysis",[map(lambda x: x[1], a) for a in fragli]

                for com in product(*fragli):
                    reference = []
                    lenfrags = []
                    for fragitem in com:
                        frag, lenfra = fragitem
                        reference += frag
                        lenfrags.append(lenfra)
                    withoutcb = []
                    for at in reference:
                        if at.get_id() != "CB":
                            withoutcb.append(at)
                    listValid.append([reference, withoutcb, lenfrags])

                    # print "Validi are",len(listValid)
                    # if len(listValid) == 0:
                    #               for fra in listmodel:
                    #                 print "frag_refe",fra["fragLength"]
                    #               for fra in allfrags:
                    #                print "frag_solu",len(fra)
        return listValid
        # print "You need to use PDB and DB mode with or without listmodel, but if it is PRECOMPUTED  mode you need listmodel set"


def __submask(mask, nr):
    new_mask = []
    mask = list(mask)
    for nres in range(nr + 1):
        n1 = [0.0] * nres
        n1 += mask[nres:]
        n2 = mask[:-1 * (nres)]
        n2 += [0.0] * nres
        if len(n1) > 0:
            new_mask.append(numpy.array(n1))
        if len(n2) > 0:
            new_mask.append(numpy.array(n2))

        for i in range(1, nres):
            resto = -1 * (nres - i)
            n3 = [0.0] * i
            n3 += mask[i:resto]
            n3 += [0.0] * (-1 * resto)
            # print "listafrag_i: ",len(listfra3)
            if len(n3) > 0:
                new_mask.append(numpy.array(n3))
    return new_mask


def __sublisttrim(fragment, delres):
    allist = []
    listfra1 = fragment[delres:]
    listfra2 = fragment[:-1 * (delres)]
    # print "Sublist trim function:",len(fragment),"delres is",delres
    # print listfra1
    # print "===============**************=================="
    # print listfra2
    # print "listafrag1: ",len(listfra1)
    # print "listafrag2: ",len(listfra2)

    if len(listfra1) > 0:
        allist.append(listfra1)
    if len(listfra2) > 0:
        allist.append(listfra2)

    for i in range(1, delres):
        resto = -1 * (delres - i)
        listfra3 = fragment[i:resto]
        # print "listafrag_i: ",len(listfra3)
        if len(listfra3) > 0:
            allist.append(listfra3)
    return allist


def getListAllAtoms(name, pdbf):
    structure = None
    try:
        structure = getStructure(name, pdbf)
    except:
        structure = getStructure(name, cStringIO.StringIO(pdbf))

    reference = []
    for model in structure.get_list():
        for chain in model.get_list():
            for residue in chain.get_list():
                for atom in residue:
                    reference.append(atom)
    return structure, reference


def trimSidechainsAndCysteines(pdb_model, poliA, cys):
    # Prepare input pdb depending on choices and write it
    pdb_file = open(pdb_model, 'r')
    pdb_lines = pdb_file.readlines()
    pdb_file.close()
    pdb_medio = open(pdb_model, 'w')  # Overwrite the contents of the previous one
    for line in pdb_lines:
        if not line.startswith("ANISO") and not line.startswith("ATOM") and not line.startswith("HETATM"):
            pdb_medio.write(line)
        elif line.startswith("ATOM") or line.startswith("HETATM"):
            if line.startswith("HETATM"): # check that it is not a water 
                #print 'line',line
                parts = line.split()
                #print 'parts',parts
                type_res = parts[3]
                #print 'type_res',type_res
                if type_res not in ['MSE','SEP','TPO','MIR']: # NOTE: should I include more non-standard residues?
                    #print 'this is a hetatm molecule we want to skip it!'
                    continue # go to next line 
            if poliA == False and cys == False:
                pdb_medio.write(line)  # We do not need to do any selection, just write
            elif poliA == True and cys == True:  # Then we have to save only poliA but mantain the cysteines
                parts = line.split()
                list_items = list(line)
                atom = ''.join(list_items[13:16])
                type_at = atom.strip()
                if type_at in ["CA", "CB", "N", "C", "O", "SG"]:
                    pdb_medio.write(line)
            elif poliA == True and cys == False:  # Plain poliala
                parts = line.split()
                list_items = list(line)
                atom = ''.join(list_items[13:16])
                type_at = atom.strip()
                if type_at in ["CA", "CB", "N", "C", "O"]:
                    pdb_medio.write(line)
            elif poliA == False and cys == True:  # This is redundant, if it has sidechains it will have its cysteins, Same as first option
                pdb_medio.write(line)
    pdb_medio.close()


def trimByChainLimit(pdb_file, min_size):
    '''trim a pdb by removing the chains that do not reach a minimum size
    input:
    pdb_file: string, path to the pdb file to trim
    min_size: integer, minimum number of residues per chain'''
    parser = PDBParser()
    # temporary to test
    # shutil.copy(pdb_file,pdb_file[:-4]+'bef.pdb')
    # temporary to test
    structure = parser.get_structure(pdb_file[:-4], pdb_file)
    chains = Selection.unfold_entities(structure, 'C')
    chains_to_remove = set()
    for chain in chains:
        size_chain = len(chain.get_unpacked_list())
        if size_chain < min_size:
            # print "chain ",chain," is smaller than ",min_size, " so it will be removed"
            chains_to_remove.update(chain.id)

    # Remove the residues and write the pdb
    for model in list(structure):
        for chain in list(model):
            id_chain = chain.id
            if id_chain in chains_to_remove:
                model.detach_child(id_chain)
    atoms = Selection.unfold_entities(structure, 'A')
    if len(atoms) == 0:
        # print "The trimming of this pdb eliminates the whole model, returning False"
        return False
    else:
        writePDBFromListOfAtom(atoms, pdb_file, dictio_chains={}, renumber=False, uniqueChain=False)
        # print "The pdb has been trimmed, returning True"
        return True


def trimBySSLimit(pdb_file,dictio_template,min_size_beta=4,min_size_alpha=7):
    """ Trim a pdb by eliminating the secondary structure elements that do not reach a particular size.
    pdb_file (str) : path to the pdb file to modify (will be overwritten)
    dictio_template (dictionary) : contains the annotation of the original template from which the pdb was extracted
    min_size_alpha (int): size limit to be applied to the alpha helices
    min_size_beta (int): size limit to be applied to the beta strands"""
    parser = PDBParser()
    # temporary to test
    #shutil.copy(pdb_file,pdb_file[:-4]+'bef.pdb')
    # temporary to test
    structure = parser.get_structure(pdb_file[:-4], pdb_file)
    list_resi = Selection.unfold_entities(structure, 'R')
    dictio_count={} # keys will be secondary structure ids and values the set of residues
    list_letters="ABCDEFGHIJKLMNOPQRSTUWXYZabcdefghijklmnopqrst"
    index=0
    elements_to_remove=[]
    for i in range(len(list_resi)-1):
        res1 = list_resi[i]
        res2 = list_resi[i + 1]
        check = checkContinuity(res1, res2)
        if check:
            #print 'These two residues are contiguous'
            nres1 = (res1.get_full_id()[3][1])
            ss_ident1 = dictio_template[nres1]['ss_id_res']
            nres2 = (res2.get_full_id()[3][1])
            ss_ident2 = dictio_template[nres2]['ss_id_res']
            #print 'ss_ident1',ss_ident1
            #print 'ss_ident2', ss_ident2
            if not dictio_count.has_key(ss_ident1):
                dictio_count[ss_ident1] = set()
            dictio_count[ss_ident1].add(nres1)
            if not dictio_count.has_key(ss_ident2):
                dictio_count[ss_ident2] = set()
            dictio_count[ss_ident2].add(nres2)
        else:
            #print 'These two residues are not contiguous'
            nres1 = (res1.get_full_id()[3][1])
            ss_ident1 = dictio_template[nres1]['ss_id_res']
            nres2 = (res2.get_full_id()[3][1])
            ss_ident2 = dictio_template[nres2]['ss_id_res']
            #print 'ss_ident1', ss_ident1
            #print 'ss_ident2', ss_ident2
            if ss_ident1==ss_ident2:
                #print 'discontinous residues belonging to same ss element. Modify dictio count'
                if not dictio_count.has_key(ss_ident1):
                    dictio_count[ss_ident1] = set()
                if not dictio_count.has_key(ss_ident2):
                    dictio_count[ss_ident2] = set()
                dictio_count[ss_ident1].add(nres1)
                #print 'current dictio_count[ss_ident1]',dictio_count[ss_ident1]
                #print 'ss_ident1+list_letters[index]',ss_ident1+list_letters[index]
                if ss_ident1+list_letters[index] not in dictio_count.keys():
                    dictio_count[ss_ident1+list_letters[index]]=dictio_count[ss_ident1]
                    #print 'saving current value of the dictionary in entry'
                    #print 'resetting dictio_count'
                    dictio_count[ss_ident1]=set()
                    index=index+1
            else:
                #print 'discontinous residues belonging to different ss_elements. is OK, but need to save them even if i do not reset'
                if not dictio_count.has_key(ss_ident1):
                    dictio_count[ss_ident1] = set()
                dictio_count[ss_ident1].add(nres1)
                if not dictio_count.has_key(ss_ident2):
                    dictio_count[ss_ident2] = set()
                dictio_count[ss_ident2].add(nres2)
            if i == len(list_resi) - 2 :  # If we reach this point, then the last residue is not continuous so it is single
                dictio_count[ss_ident2].add(nres2)

    print '\n Checking size of secondary structure elements on the model ',dictio_count

    for key in dictio_count.keys():
        if key.startswith('ah'):
            if len(dictio_count[key])<min_size_alpha:
                print 'Adding ',key,' to elements to remove'
                print 'dictio_count[key]',dictio_count[key]
                elements_to_remove.extend(dictio_count[key])
        elif key.startswith('bs'):
            if len(dictio_count[key]) < min_size_beta:
                print 'Adding ', key, ' to elements to remove'
                print 'dictio_count[key]', dictio_count[key]
                elements_to_remove.extend(dictio_count[key])

    #print 'elements_to_remove',elements_to_remove

    # Remove the elements from the object and write the PDB
    parser = PDBParser()
    structure = parser.get_structure(pdb_file[:-4], pdb_file)
    for model in list(structure):
        for chain in list(model):
            for residue in list(chain):
                nres = (residue.get_full_id()[3][1])
                residue_id=residue.id
                if nres in elements_to_remove:
                    #print 'Removing ',nres
                    chain.detach_child(residue_id)
    atoms = Selection.unfold_entities(structure, 'A')
    if len(atoms) == 0:
        #print "The trimming of this pdb eliminates the whole model, returning False"
        return False
    else:
        writePDBFromListOfAtom(atoms, pdb_file, dictio_chains={}, renumber=False, uniqueChain=False)
        #print "The pdb has been trimmed based on secondary structure limits"
        #print "Betas smaller than ",min_size_beta," have been removed"
        #print "Alphas smaller than ", min_size_alpha, " have been removed"
        return True


def trimByContinuityLimit(pdb_file, min_size, preserve_chains=False):
    '''trim a pdb by removing the discontinuous fragments smaller than a minimum size
    input:
    pdb_file: string, path to the pdb file to trim (will be overwritten)
    min_size: integer, minimum number of residues per fragment
    preserve_chains: boolean, maintain the chain id of the residues or change it to a different one per fragment'''
    parser = PDBParser()
    # temporary to test
    # shutil.copy(pdb_file,pdb_file[:-4]+'bef.pdb')
    # temporary to test
    structure = parser.get_structure(pdb_file[:-4], pdb_file)
    residues = Selection.unfold_entities(structure, 'R')
    list_id = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    max_ids = len(list_id)
    dictio_chainid = {}
    residues_to_remove = []
    current_listres = []
    index = 0
    for i in range(len(residues) - 1):
        res1 = residues[i]
        res2 = residues[i + 1]
        id1 = res1.get_full_id()
        chain_idres1 = (res1.get_parent()).id
        id2 = res2.get_full_id()
        chain_idres2 = (res2.get_parent()).id
        check = checkContinuity(res1, res2)
        if check == True:
            if id1 not in current_listres:
                current_listres.append(id1)
            if preserve_chains == True:
                dictio_chainid[id1] = chain_idres1
            else:
                dictio_chainid[id1] = list_id[index]
            if id2 not in current_listres:
                current_listres.append(id2)
            if preserve_chains == True:
                dictio_chainid[id2] = chain_idres2
            else:
                dictio_chainid[id2] = list_id[index]
            if i == len(residues) - 2:
                if len(current_listres) < min_size:  # Last two residues consecutive but smaller than min_size
                    residues_to_remove.extend(deepcopy(current_listres))
        elif check == False:
            if id1 not in current_listres:
                current_listres.append(id1)
            if preserve_chains:
                dictio_chainid[id1] = chain_idres1
            elif not preserve_chains:
                dictio_chainid[id1] = list_id[index]
            if len(current_listres) < min_size:
                residues_to_remove.extend(deepcopy(current_listres))
            if i == len(
                    residues) - 2 and min_size > 1:  # If we reach this point, then the last residue is not continuous so it is single
                residues_to_remove.append(id2)
            else:
                current_listres = []
                current_listres.append(id2)
                index = index + 1
                if index > max_ids:
                    print "There are no more ids to assign to a discontinuous chain. This should not happen, maybe your model contains HETATMs?"
                    sys.exit(1)
                if preserve_chains == True:
                    dictio_chainid[id2] = chain_idres2
                else:
                    dictio_chainid[id2] = list_id[index]

    # Remove the residues and write the pdb
    for model in list(structure):
        for chain in list(model):
            for residue in list(chain):
                id_fullres = residue.get_full_id()
                id_res = residue.id
                if id_fullres in residues_to_remove:
                    chain.detach_child(id_res)
    atoms = Selection.unfold_entities(structure, 'A')
    writePDBFromListOfAtom(atoms, pdb_file, dictio_chains=dictio_chainid, renumber=False, uniqueChain=False)


def writePDBFromListOfAtom(reference, outputFilename, dictio_chains={}, renumber=False, uniqueChain=False):
    '''Write a pdb from a list of atoms.
    Input:
    - reference: string with input path
    - outputFilename: string with output path
    - dictio_chains: dictionary, keys are residues full id, and values are the new chain id
    - renumber: boolean
    - uniqueChain: boolean '''
    pdbString = ""
    numero = 0
    previous = None
    numea = 1
    for item in reference:
        orig_atom_num = item.get_serial_number()
        hetfield, resseq, icode = item.get_parent().get_id()
        segid = item.get_parent().get_segid()
        if renumber:
            hetfield = " "
            orig_atom_num = numea
            numea += 1
            if previous == None or resseq != previous:
                numero += 1
                previous = resseq
                resseq = numero
            elif previous != None:
                resseq = numero
            icode = " "
        if uniqueChain:
            chain_id = "A"
        if item.get_parent().get_full_id() in dictio_chains:
            chain_id = dictio_chains[item.get_parent().get_full_id()]
        else:
            chain_id = item.get_parent().get_parent().get_id()
        resname = item.get_parent().get_resname()
        element = item.get_name()
        pdbString += getAtomLine(item, element, hetfield, segid, orig_atom_num, resname, resseq, icode, chain_id)
    flu = open(outputFilename, "w")
    flu.write(pdbString)
    flu.close()


# NOTE: res1 preceed res2
def checkContinuity(res1, res2):
    resaN = None
    prevResC = None
    try:
        resaN = res2["N"]
        prevResC = res1["C"]
    except:
        return False

    # print resaC.get_coord()
    # print prevResN.get_coord()
    resaNX = float(resaN.get_coord()[0])
    resaNY = float(resaN.get_coord()[1])
    resaNZ = float(resaN.get_coord()[2])
    prevResCX = float(prevResC.get_coord()[0])
    prevResCY = float(prevResC.get_coord()[1])
    prevResCZ = float(prevResC.get_coord()[2])
    checkCont = numpy.sqrt(((resaNX - prevResCX) ** 2) + ((resaNY - prevResCY) ** 2) + ((resaNZ - prevResCZ) ** 2))
    # print resan
    # print prev_model,prev_chain,prevRes
    # print checkCont
    if checkCont <= 1.5:
        return True
    else:
        return False

#@deprecated('Use Bioinformatics3.get_pdb_from_list_of_atoms')
def getPDBFromListOfAtom(reference, renumber=False, uniqueChain=False, chainId="A", chainFragment=False, diffchain=None,
                         polyala=True, maintainCys=False):
    pdbString = ""
    numero = 1
    resn = {}
    nur = 1
    lastRes = None
    prevChain = 0
    lich = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "Z",
            "J", "K", "X", "Y", "W", "a", "b", "c", "d", "e", "f", "g", "h", "i", "l", "m", "n", "o", "p", "q", "r",
            "s", "t", "u", "v", "z", "j", "k", "x", "y", "w", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    # if chainFragment or uniqueChain:
    #   renumber = True
    erel = []
    if not polyala:
        for item in reference:
            res = item.get_parent()
            for atk in res:
                erel.append(atk)
        reference = erel
    elif maintainCys:
        for item in reference:
            res = item.get_parent()
            if res.get_resname() in ["CYS", "cys", "Cys"]:
                for atk in res:
                    erel.append(atk)
            else:
                erel.append(item)
        reference = erel

    for item in reference:
        orig_atom_num = item.get_serial_number()
        hetfield, resseq, icode = item.get_parent().get_id()
        segid = item.get_parent().get_segid()
        chain_id = item.get_parent().get_parent().get_id()
        hetfield = " "
        if (resseq, chain_id) not in resn.keys():
            if lastRes != None:
                # print "Checking Continuity",lastRes.get_parent().get_full_id(),item.get_parent().get_full_id(),checkContinuity(lastRes.get_parent(),item.get_parent())
                # print "Checking Continuity",item.get_parent().get_full_id(),lastRes.get_parent().get_full_id(),checkContinuity(item.get_parent(),lastRes.get_parent())
                # print lich[prevChain]
                # print
                if not checkContinuity(lastRes.get_parent(), item.get_parent()) and not checkContinuity(
                        item.get_parent(), lastRes.get_parent()):
                    if renumber:
                        nur += 10
                    if chainFragment:
                        prevChain += 1
            new_chain_id = chain_id
            if uniqueChain:
                new_chain_id = chainId
            elif chainFragment:
                new_chain_id = lich[prevChain]
            if renumber:
                resn[(resseq, chain_id)] = (nur, new_chain_id)
            else:
                resn[(resseq, chain_id)] = (resseq, new_chain_id)
            lastRes = item
            nur += 1
        tuplr = resn[(resseq, chain_id)]
        resseq = tuplr[0]
        chain_id = tuplr[1]
        icode = " "
        orig_atom_num = numero
        numero += 1

        resname = item.get_parent().get_resname()
        element = item.get_name()
        pdbString += getAtomLine(item, element, hetfield, segid, orig_atom_num, resname, resseq, icode, chain_id)

    if diffchain != None and len(diffchain) > 0:
        prevChain += 1
        lastRes = None
        for item in diffchain:
            orig_atom_num = item.get_serial_number()
            hetfield, resseq, icode = item.get_parent().get_id()
            segid = item.get_parent().get_segid()
            chain_id = item.get_parent().get_parent().get_id()
            hetfield = " "
            if (resseq, chain_id) not in resn.keys():
                if lastRes != None:
                    if not checkContinuity(lastRes.get_parent(), item.get_parent()) and not checkContinuity(
                            item.get_parent(), lastRes.get_parent()):
                        if renumber:
                            nur += 10
                        if chainFragment:
                            prevChain += 1
                new_chain_id = chain_id
                if uniqueChain:
                    new_chain_id = chainId
                elif chainFragment:
                    new_chain_id = lich[prevChain]

                if renumber:
                    resn[(resseq, chain_id)] = (nur, new_chain_id)
                else:
                    resn[(resseq, chain_id)] = (resseq, new_chain_id)
                lastRes = item
                nur += 1
            tuplr = resn[(resseq, chain_id)]
            resseq = tuplr[0]
            chain_id = tuplr[1]
            icode = " "
            orig_atom_num = numero
            numero += 1

            resname = item.get_parent().get_resname()
            element = item.get_name()
            pdbString += getAtomLine(item, element, hetfield, segid, orig_atom_num, resname, resseq, icode, chain_id)

    return pdbString, resn


def distance_sq(X, Y):
    """
    Squared distance between C{X} and C{Y} along the last axis. For details, see L{distance}.

    @return: scalar or array of length m
    @rtype: (m,) numpy.array
    """
    return ((numpy.asarray(X) - Y) ** 2).sum(-1)


def wfit(X, Y, w):
    """
    Return the translation vector and the rotation matrix
    minimizing the weighted RMSD between two sets of d-dimensional
    vectors, i.e. if

        >>> R,t = fit(X,Y)

    then

        >>> Y = dot(Y, transpose(R)) + t

    will be the fitted configuration.

    @param X: (n, d) input vector
    @type X: numpy array

    @param Y: (n, d) input vector
    @type Y: numpy array

    @param w: input weights
    @type w: numpy array

    @return: (d, d) rotation matrix and (d,) translation vector
    @rtype: tuple
    """

    from numpy.linalg import svd, det
    from numpy import dot, sum

    ## center configurations

    norm = sum(w)
    x = dot(w, X) / norm
    y = dot(w, Y) / norm

    ## SVD of correlation matrix

    V, _L, U = svd(dot((X - x).T * w, Y - y))

    ## calculate rotation and translation

    R = dot(V, U)

    if det(R) < 0.:
        U[2] *= -1
        R = dot(V, U)

    t = x - dot(R, y)

    return R, t


def xfit(X, Y, n_iter=10, seed=False, full_output=False):
    """
    Maximum likelihood superposition of two coordinate arrays. Works similar
    to U{Theseus<http://theseus3d.org>} and to L{bfit}.

    @param X: (n, 3) input vector
    @type X: numpy.array
    @param Y: (n, 3) input vector
    @type Y: numpy.array
    @param n_iter: number of EM iterations
    @type n_iter: int
    @type seed: bool
    @param full_output: if true, return ((R, t), scales)
    @type full_output: bool
    @rtype: tuple
    """
    if seed:
        R, t = numpy.identity(3), numpy.zeros(3)
    else:
        R, t = fit(X, Y)

    for _ in range(n_iter):
        data = distance_sq(X, transform(Y, R, t))
        scales = 1.0 / data.clip(1e-9)
        R, t = wfit(X, Y, scales)

    if full_output:
        return (R, t), scales
    else:
        return (R, t)


def fit(X, Y):
    """
    Return the translation vector and the rotation matrix
    minimizing the RMSD between two sets of d-dimensional
    vectors, i.e. if

        >>> R,t = fit(X,Y)

    then

        >>> Y = dot(Y, transpose(R)) + t

    will be the fitted configuration.

    @param X: (n, d) input vector
    @type X: numpy array

    @param Y: (n, d) input vector
    @type Y: numpy array

    @return: (d, d) rotation matrix and (d,) translation vector
    @rtype: tuple
    """

    from numpy.linalg import svd, det
    from numpy import dot

    ## center configurations

    x = X.mean(0)
    y = Y.mean(0)

    ## SVD of correlation matrix

    V, _L, U = svd(dot((X - x).T, Y - y))

    ## calculate rotation and translation

    R = dot(V, U)

    if det(R) < 0.:
        U[-1] *= -1
        R = dot(V, U)

    t = x - dot(R, y)

    return R, t


def transform_atoms(atoms, R, t, s=None, invert=False):
    Y = []

    for atom in atoms:
        Y.append(atom.get_coord())

    Y = transform(Y, R, t, s=s, invert=invert)

    for i in range(len(Y)):
        y = Y[i]
        atoms[i].set_coord(y)

    return atoms


def transform(Y, R, t, s=None, invert=False):
    """
    Transform C{Y} by rotation C{R} and translation C{t}. Optionally scale by C{s}.

        >>> R, t = fit(X, Y)
        >>> Y_fitted = transform(Y, R, t)

    @param Y: (n, d) input vector
    @type Y: numpy.array
    @param R: (d, d) rotation matrix
    @type R: numpy.array
    @param t: (d,) translation vector
    @type t: numpy.array
    @param s: scaling factor
    @type s: float
    @param invert: if True, apply the inverse transformation
    @type invert: bool
    @return: transformed input vector
    @rtype: numpy.array
    """
    if invert:
        x = numpy.dot(Y - t, R)
        if s is not None:
            s = 1. / s
    else:
        x = numpy.dot(Y, R.T) + t
    if s is not None:
        x *= s
    return x


def fit_wellordered(X, Y, n_iter=None, n_stdv=2, tol_rmsd=.5, tol_stdv=0.05, full_output=False):
    """
    Match two arrays onto each other by iteratively throwing out
    highly deviating entries.

    (Reference: Nilges et al.: Delineating well-ordered regions in
    protein structure ensembles).

    @param X: (n, d) input vector
    @type X: numpy array

    @param Y: (n, d) input vector
    @type Y: numpy array

    @param n_stdv: number of standard deviations above which points are considered to be outliers
    @param tol_rmsd: tolerance in rmsd
    @param tol_stdv: tolerance in standard deviations
    @param full_output: also return full history of values calculated by the algorithm

    @rtype: tuple
    """

    from numpy import ones, compress, dot, sqrt, sum, nonzero, std, average

    rmsd_list = []

    rmsd_old = 0.
    stdv_old = 0.

    n = 0
    converged = False

    mask = ones(X.shape[0])
    while not converged:
        ## find transformation for best match
        if n_iter == None or n_iter <= 0:
            R, t = fit(compress(mask, X, 0), compress(mask, Y, 0))
        else:
            R, t = xfit(compress(mask, X, 0), compress(mask, Y, 0), n_iter=n_iter)

        ## calculate RMSD profile

        d = sqrt(sum((X - dot(Y, R.T) - t) ** 2, 1))

        ## calculate rmsd and stdv

        rmsd = sqrt(average(compress(mask, d) ** 2, 0))
        stdv = std(compress(mask, d))
        # print "Best rmsd",best_rmsd

        ## check conditions for convergence

        if stdv < 1e-10: break

        d_rmsd = abs(rmsd - rmsd_old)
        d_stdv = abs(1 - stdv_old / stdv)

        if d_rmsd < tol_rmsd:
            if d_stdv < tol_stdv:
                converged = 1
            else:
                stdv_old = stdv
        else:
            rmsd_old = rmsd
            stdv_old = stdv

        ## store result

        perc = average(1. * mask)

        # print "N is",n,"n_iter is",n_iter,"rmsd_list",rmsd_list,"mask",mask
        # if perc < 0.96: break
        ###if n_iter == 0: break

        ## throw out non-matching rows
        new_mask = mask * (d < rmsd + n_stdv * stdv)
        outliers = nonzero(mask - new_mask)
        rmsd_list.append([perc, rmsd, outliers])
        mask = new_mask

        perc = average(1. * mask)
        if n_iter and n >= n_iter: break

        n += 1

    if full_output:
        return (R, t), rmsd_list, rmsd
    else:
        return (R, t)


def getRMSDfromCommonCore(dicc_1, dicc_2):
    stru1_refe = dicc_1["reference"]
    stru1_cmp = dicc_1["compare"]
    stru2_refe = dicc_2["reference"]
    stru2_cmp = dicc_2["compare"]

    core = {}
    list1_CA = []
    list2_CA = []
    listc_CA = []

    for key in dicc_1:
        if key not in ["reference", "compare"]:
            if key in dicc_2:
                core[key] = (dicc_1[key][0], dicc_2[key][0], dicc_1[key][1], dicc_1[key][2] - dicc_2[key][2])
                # print "---",dicc_1[key][0]
                list1_CA.append(dicc_1[key][0]["CA"].get_coord())
                list2_CA.append(dicc_2[key][0]["CA"].get_coord())
                listc_CA.append(dicc_1[key][1]["CA"].get_coord())

    if len(core.keys()) > 0:
        ref1 = numpy.array(list1_CA)
        ref2 = numpy.array(list2_CA)
        comp = numpy.array(listc_CA)

        transf, rmsd_list, rmsd_1 = fit_wellordered(ref1, comp, n_iter=None, full_output=True)
        transf, rmsd_list, rmsd_2 = fit_wellordered(ref2, comp, n_iter=None, full_output=True)
    else:
        # for key in dicc_1:
        #       print "+++",key
        # for key in dicc_2:
        #       print "---",key
        # quit()
        rmsd_1 = -1
        rmsd_2 = -1

    return (rmsd_1, rmsd_2, core)


def getRMSDAtoms(atoms1, atoms2, superpose=True):
    list1_CA = []
    list2_CA = []

    for atom in atoms1:
        if atom.get_name() in ["CA", "C", "O", "N"]:
            list1_CA.append(atom.get_coord())
    for atom in atoms2:
        if atom.get_name() in ["CA", "C", "O", "N"]:
            list2_CA.append(atom.get_coord())

    if len(list1_CA) == len(list2_CA):
        ref1 = numpy.array(list1_CA)
        ref2 = numpy.array(list2_CA)
        if superpose:
            transf, rmsd_list, rmsd_1 = fit_wellordered(ref1, ref2, n_iter=None, full_output=True)
        else:
            transf = None
            diff = ref1 - ref2
            l = ref1.shape[0]
            rmsd_1 = numpy.sqrt(sum(sum(diff * diff)) / l)
    else:
        print "Not same length", len(list1_CA), len(list2_CA)
        print "LIST C1:===================="
        print list1_CA
        print "LIST C2:===================="
        print list2_CA
        print "============================"
        rmsd_1 = -1
        rmsd_2 = -1
        transf = None

    return (rmsd_1, transf)

@deprecated('Will be removed soon. Use BORGES_MATRIX.perform_superposition')
def getSuperimp(referenceFile, compareFile, mode, DicParameters=None, algorithm="biopython", backbone=False,
                getDictioCorresp=False, superpose_exclude=1, listmodel=None, allAtomsList=None, allAtomsModel=None,
                n_iter=None, pos=[], clusterCYS=False, minmaxrms=None, onlyCA=False):
    '''

    Function to get the best superimposition between two files

    Keyword input:
    referenceFile --
    compareFile --
    mode -- 'PRECOMPUTED', 'PDBSTRING', 'PDBSTRINGBM', 'PDBSTRINGBM_RESIDUES_CONSERVED'
    DicParameters --
    algorithm -- 'nigels-core2',
    backbone --
    getDictioCorresp --
    superpose_exclude --
    listmodel --
    allAtomsList --
    allAtomsModel --
    n_iter --
    pos --
    clusterCYS --
    minmaxrms --
    onlyCA --

    Returns:
    rmsd -- rmsd between referenceFile and compareFile
    nref -- 
    ncom -- 
    allAtoms -- 
    compStru --
    pda -- 
    dictiocorres -- (only if set)

    '''

    # in mode 'PDBSTRINGBM_RESIDUES_CONSERVED', check if one of the models is larger than the other and act accordingly
    if mode=='PDBSTRINGBM_RESIDUES_CONSERVED':
        if algorithm != "nigels-core2":
            print 'The algorithm ',algorithm, ' is not supported with the mode ',mode
            sys.exit(1)
        struref=getStructure('ref',cStringIO.StringIO(referenceFile))
        strucmp=getStructure('cmp',cStringIO.StringIO(compareFile))
        #file_pepe=open('ref_file.pdb','w')
        #file_pepe.write(referenceFile)
        #del file_pepe
        #file_pepa=open('comp_file.pdb','w')
        #file_pepa.write(compareFile)
        #del file_pepa
        list_atoms_ref=Selection.unfold_entities(struref, 'A')
        list_atoms_cmp=Selection.unfold_entities(strucmp, 'A')
        different_size=False
        if len(list_atoms_ref)!=len(list_atoms_cmp):
            different_size=True
            #print ' \n \n ********** We entered the condition in which the two files to compare are DIFFERENT in size \n\n ***********'
            list_atoms_ref= sorted(list_atoms_ref, key=lambda x:x.get_parent().get_full_id()[3][1:])
            list_atoms_cmp= sorted(list_atoms_cmp, key=lambda x:x.get_parent().get_full_id()[3][1:])    
            set_ref = set([ide.get_full_id()[3] for ide in list_atoms_ref]) 
            set_cmp = set([ide.get_full_id()[3] for ide in list_atoms_cmp])
            common_set = set_ref.intersection(set_cmp)
            #print 'common_set',common_set
            common_list_id = sorted(list(common_set),key=lambda x:x[1:])
            #print 'common_list_id',common_list_id
            if set_ref.issuperset(set_cmp):
                #print 'larger set corresponds to the reference. We need to modify referenceFile to the common set of atoms'
                common_list = [ele for ele in list_atoms_ref if ele.get_full_id()[3] in common_list_id ]
                #print 'len(common_list)',len(common_list)
                originalreferenceFile=copy.deepcopy(referenceFile)
                referenceFile=getPDBFromListOfAtom(common_list)[0]
            else:
                #print 'larger set corresponds to the compared. We need to modify compareFile to the common set of atoms'
                common_list = [ele for ele in list_atoms_cmp if ele.get_full_id()[3] in common_list_id ]
                #print 'len(common_list)',len(common_list)
                originalcompareFile=copy.deepcopy(compareFile)
                compareFile=getPDBFromListOfAtom(common_list)[0]
 
    if isinstance(referenceFile, str) or mode == "PRECOMPUTED":
        listValiRef = getListCA("referencia", referenceFile, mode, DicParameters=DicParameters, backbone=backbone,
                                listmodel=listmodel, algorithm=algorithm, superpose_exclude=superpose_exclude, pos=pos,
                                clusterCYS=clusterCYS)
    elif isinstance(referenceFile, list):
        listValiRef = referenceFile

    if isinstance(compareFile, str) or mode == "PRECOMPUTED":
        listValiCmp = getListCA("compare", compareFile, mode, DicParameters=DicParameters, backbone=backbone,
                                listmodel=listmodel, algorithm=algorithm, superpose_exclude=superpose_exclude, pos=pos,
                                clusterCYS=clusterCYS)
    elif isinstance(compareFile, list):
        listValiCmp = compareFile

    #print listValiRef
    #print "======================================"
    #print listValiCmp

    #  print "-----",listValiCmp
    reference = (listValiRef[0])[1]

    nref = len(reference)
    # print "algorithm",algorithm
    pdball = ""
    allAtoms = []
    compStru = None
    dictiocorresp = {}

    # print "len(listValiRef)",len(listValiRef),"len(listValiCmp)",len(listValiCmp)

    if algorithm.startswith("pymol") or algorithm.startswith("minrms") or algorithm.startswith("superpose"):
        nameficheref = "./ref_" + str(datetime.datetime.now()) + ".pdb"
        writePDBFromListOfAtom(reference, nameficheref)

        namefichecmp = "./cmp_" + str(datetime.datetime.now()) + ".pdb"
        compare = (listValiCmp[0])[1]
        writePDBFromListOfAtom(compare, namefichecmp)

        ncom = len(compare)
        # print "nref",nref,"ncom",ncom

    try:
        if algorithm == "nigels-core2":
            if isinstance(compareFile, str):
                compStru, allAtoms = getListAllAtoms("compa", compareFile)
            elif allAtomsList != None:
                allAtoms = allAtomsList
            elif allAtomsModel != None and isinstance(allAtomsModel, str):
                compStru, allAtoms = getListAllAtoms("compa", allAtomsModel)
            else:
                print "You should give a compareFile as PDB file or if compareFile is a a list of combinations of fragments as atoms, then allAtomsList should be configured"
                return (100, 0, 0, [], None, "")

            best_rmsd = 1000000000000
            best_super = None
            best_ncom = None
            best_super_ref = None
            best_nref = None
            best_R = None
            best_t = None
            howm = 1
            ifbreak = False
            tcnt = 1

            liran = range(len(listValiRef))
            numpy.random.shuffle(liran)
            for cren in liran:
                nref, reference, lenfraref = listValiRef[cren]
                #print "===",[f.get_full_id() for f in nref],lenfraref
                refi = []
                k = []
                if clusterCYS:
                    reference = nref

                for atom in reference:
                    if atom.get_name() == "CA":
                        k.append(atom.get_full_id()[3][1])
                    if onlyCA and atom.get_name() != "CA":
                        continue
                    refi.append(atom.get_coord())
                refi = numpy.array(refi)


                for tren in range(len(listValiCmp)):
                    no_cmp, compare, lenfracmp = listValiCmp[tren]
                    #print "===", [f.get_full_id() for f in no_cmp], lenfracmp

                    tocontinue = False
                    if clusterCYS:
                        compare = no_cmp
                    es = zip(lenfraref,lenfracmp)
                    for z in range(len(es)):
                        #print "len lenfraref",len(lenfraref),"len lenfracmp",len(lenfracmp),z
                        if es[z][0] != es[z][1]:
                            tocontinue = True
                            break
                            # else:
                            #       print "--ref--",lenfraref[z],"--cmp--",lenfracmp[z]
                    #print "==================================================="
                    if tocontinue:
                        continue

                    howm += 1
                    compi = []
                    z = []
                    for atom in compare:
                        if atom.get_name() == "CA":
                            z.append(atom.get_full_id()[3][1])
                        if onlyCA and atom.get_name() != "CA":
                            continue
                        compi.append(atom.get_coord())
                    compi = numpy.array(compi)

                    transf, rmsd_list, rmsd = fit_wellordered(refi, compi, n_iter=n_iter, full_output=True, n_stdv=2, tol_rmsd=0.005, tol_stdv=0.0005)
                    R, t = transf
                    # print "---1---============================================================"
                    # print k
                    # print "---2---==========================================================="
                    # print z
                    #print "len(refi)",len(refi),"len(compi)",len(compi),rmsd
                    ncom = len(compi)

                    if rmsd <= best_rmsd:
                        # print "rmsd",rmsd,"best_rmsd",best_rmsd
                        # print "rmsd",rmsd,"list",rmsd_list
                        outliers = 0
                        for tup in rmsd_list:
                            outliers += len(tup[2])
                            # print "==**==**==",ncom-outliers
                        tcnt = 0
                        best_rmsd = rmsd
                        best_super = tren
                        best_super_ref = cren
                        best_ncom = ncom - outliers
                        best_R = R
                        best_t = t
                    else:
                        tcnt += 1

                    if best_rmsd <= 1.0 or tcnt > 400:
                        ifbreak = True
                        break
                if ifbreak:
                    break

            # print "Comparisons done:",howm
            no_cmp, compare, lencmp = listValiCmp[best_super]
            nref, reference, lenref = listValiRef[best_super_ref]
            dictiocorresp = {}
            rmsd = best_rmsd
            ncom = best_ncom
            nref = best_ncom
            for l in range(len(reference)):
                atomr = reference[l]
                atomc = compare[l]
                rline = getAtomLineEasy(atomr)
                cline = getAtomLineEasy(atomc)
                dictiocorresp[cline[17:27]] = rline[17:27]
            if mode=='PDBSTRINGBM_RESIDUES_CONSERVED':
                if different_size:
                    compareFile=copy.deepcopy(originalcompareFile)
                cmpStru, allAtoms = getListAllAtoms("cmpStru", compareFile)
                allAtoms = transform_atoms(allAtoms, best_R, best_t)
                pdball = getPDBFromListOfAtom(allAtoms)
                #print 'pdball',pdball
            else:
                allAtoms = transform_atoms(allAtoms, best_R, best_t)
                pdball = getPDBFromListOfAtom(allAtoms)
        elif algorithm == "nigels-core":
            if isinstance(compareFile, str):
                compStru, allAtoms = getListAllAtoms("compa", compareFile)
            elif allAtomsList != None:
                allAtoms = allAtomsList
            elif allAtomsModel != None and isinstance(allAtomsModel, str):
                compStru, allAtoms = getListAllAtoms("compa", allAtomsModel)
            else:
                print "You should give a compareFile as PDB file or if compareFile is a alist of combinations of fragments as atoms, then allAtomsList should be configured"
                return (100, 0, 0, [], None, "")

            best_rmsd = 1000000000000
            best_R = None
            best_t = None
            best_super = None
            best_ncom = None
            refi = []
            for atom in reference:
                refi.append(atom.get_coord())
            refi = numpy.array(refi)

            for tren in range(len(listValiCmp)):
                no_cmp, compare = listValiCmp[tren]
                ncom = len(compare)
                compi = []
                for atom in compare:
                    compi.append(atom.get_coord())
                compi = numpy.array(compi)

                transf, rmsd_list, rmsd = fit_wellordered(refi, compi, n_iter=n_iter, full_output=True)
                R, t = transf
                # print rmsd_list
                # print "================================",rmsd
                if rmsd <= best_rmsd:
                    outliers = 0
                    for tup in rmsd_list:
                        outliers += len(tup[2])
                    best_rmsd = rmsd
                    best_R = R
                    best_t = t
                    best_super = tren
                    best_ncom = ncom - outliers

            no_cmp, compare = listValiCmp[best_super]
            ncom = best_ncom
            nref = ncom
            dictiocorresp = {}
            for l in range(len(reference)):
                atomr = reference[l]
                atomc = compare[l]
                rline = getAtomLineEasy(atomr)
                cline = getAtomLineEasy(atomc)
                dictiocorresp[cline[17:27]] = rline[17:27]

            # super_imposer = Superimposer()
            # super_imposer.rotran = (best_R,best_t)
            # super_imposer.apply(allAtoms)
            allAtoms = transform_atoms(allAtoms, best_R, best_t)
            pdball = getPDBFromListOfAtom(allAtoms)
        elif algorithm == "biopython":
            if isinstance(compareFile, str):
                compStru, allAtoms = getListAllAtoms("compa", compareFile)
            elif allAtomsList != None:
                allAtoms = allAtomsList
            elif allAtomsModel != None and isinstance(allAtomsModel, str):
                compStru, allAtoms = getListAllAtoms("compa", allAtomsModel)
            else:
                print "You should give a compareFile as PDB file or if compareFile is a alist of combinations of fragments as atoms, then allAtomsList should be configured"
                return (100, 0, 0, [], None, "")

            best_rmsd = 1000000000000
            best_super = -1
            best_ncom = -1
            for tren in range(len(listValiCmp)):
                no_cmp, compare, size = listValiRef[
                    tren]  # NOTE: I am modifying this line eliminating no_cmp it might affect other functions?
                ncom = len(compare)
                # print "nref",len(reference),"ncom",len(compare)
                super_imposer = Superimposer()
                super_imposer.set_atoms(reference, compare)
                rmsd = super_imposer.rms
                # print "rmsd",rmsd,"best_rmsd",best_rmsd
                if rmsd <= best_rmsd:
                    best_rmsd = rmsd
                    best_super = tren
                    best_ncom = ncom

            no_comp, compare, size = listValiCmp[best_super]
            ncom = len(compare)
            super_imposer = Superimposer()
            super_imposer.set_atoms(reference, compare)
            dictiocorresp = {}
            for l in range(len(reference)):
                atomr = reference[l]
                atomc = compare[l]
                rline = getAtomLineEasy(atomr)
                cline = getAtomLineEasy(atomc)
                dictiocorresp[cline[17:27]] = rline[17:27]

            rmsd = super_imposer.rms
            # print "nref",len(reference),"ncom",len(compare),"rmsd",rmsd
            ncom = best_ncom
            super_imposer.apply(allAtoms)
            pdball = getPDBFromListOfAtom(allAtoms)
        elif algorithm == "biopython-core":
            if isinstance(compareFile, str):
                compStru, allAtoms = getListAllAtoms("compa", compareFile)
            elif allAtomsList != None:
                allAtoms = allAtomsList
            elif allAtomsModel != None and isinstance(allAtomsModel, str):
                compStru, allAtoms = getListAllAtoms("compa", allAtomsModel)
            else:
                print "You should give a compareFile as PDB file or if compareFile is a alist of combinations of fragments as atoms, then allAtomsList should be configured"
                return (100, 0, 0, [], None, "")

            best_rmsd = 1000000000000
            best_super = None
            best_ncom = None
            best_super_ref = None
            best_nref = None
            for cren in range(len(listValiRef)):
                nref, reference, lenfraref = listValiCmp[cren]
                for tren in range(len(listValiCmp)):
                    no_cmp, compare, lenfracmp = listValiCmp[tren]
                    tocontinue = False
                    for z in range(len(lenfraref)):
                        if lenfraref[z] != lenfracmp[z]:
                            tocontinue = True
                            break
                            # else:
                            # if lenfraref[z] not in [32,27]:
                            #       tocontinue = True
                            #       break
                            # print "--ref--",lenfraref[z],"--cmp--",lenfracmp[z]
                    # print "==================================================="
                    if tocontinue:
                        continue

                    ncom = len(compare)
                    # print "nref",len(reference),"ncom",len(compare)
                    super_imposer = Superimposer()
                    super_imposer.set_atoms(reference, compare)
                    rmsd = super_imposer.rms
                    # print "rmsd",rmsd,"best_rmsd",best_rmsd
                    if rmsd <= best_rmsd:
                        best_rmsd = rmsd
                        best_super = tren
                        best_super_ref = cren
                        best_ncom = ncom
                        best_nref = nref

            no_cmp, compare = listValiCmp[best_super]
            ncom = len(compare)
            nref, reference = listValiRef[best_super_ref]
            super_imposer = Superimposer()
            super_imposer.set_atoms(reference, compare)
            dictiocorresp = {}
            for l in range(len(reference)):
                atomr = reference[l]
                atomc = compare[l]
                rline = getAtomLineEasy(atomr)
                cline = getAtomLineEasy(atomc)
                dictiocorresp[cline[17:27]] = rline[17:27]

            rmsd = super_imposer.rms
            # print "nref",len(reference),"ncom",len(compare),"rmsd",rmsd
            ncom = best_ncom
            super_imposer.apply(allAtoms)
            pdball = getPDBFromListOfAtom(allAtoms)
        elif algorithm == "pymol_align":
            namefichepml = "./pml_" + str(datetime.datetime.now()) + ".pml"
            nameficheout = "./out_" + str(datetime.datetime.now()) + ".pdb"
            flu = open(namefichepml, "w")
            flu.write("load " + nameficheref + ", \"ref\"\n")
            flu.write("load " + namefichecmp + ", \"cmp\"\n")
            flu.write("align cmp and name ca, ref and name ca\n")
            flu.write("save " + nameficheout + ", \"cmp\"\n")
            flu.close()
            p = subprocess.Popen(['pymol', "-c", namefichepml], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            listout = out.split("\n")
            rmsd = 100
            for line in listout:
                listline = line.split()
                if line.startswith(" Executive: RMS ="):
                    rmsd = float(listline[3])
            os.remove(namefichepml)
            compStru, allAtoms = getListAllAtoms("compa", nameficheout)
            t = open(nameficheout, "r")
            pdball = t.read()
            t.close()
            os.remove(nameficheout)
        elif algorithm == "superpose":
            p = subprocess.Popen(['superpose', nameficheref, namefichecmp], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            out, err = p.communicate()
            # p2 = subprocess.Popen('superpose '+nameficheref+" "+namefichecmp+ ' | grep  "| . .\."',  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # out2, err2 = p2.communicate()
            rmsd = 100
            ncom = 100
            lines = out.splitlines()
            for line in lines:
                if line.startswith("     r.m.s.d:"):
                    linel = line.split()
                    rmsd = float(linel[1])
                if line.startswith("      Nalign:"):
                    linel = line.split()
                    ncom = int(linel[1])
                    break

            stru_refe = getStructure("refe", nameficheref)
            stru_cmp = getStructure("cmp", namefichecmp)
            os.remove(nameficheref)
            os.remove(namefichecmp)

            dictpairing = {}
            dictpairing["reference"] = stru_refe
            dictpairing["compare"] = stru_cmp
            for line in lines:
                if len(line.split("|")) == 5 and line.split("|")[2][4] == ".":
                    chain_query = line.split("|")[1].split(":")[0][-1]
                    resid_query = int(line.split("|")[1].split(":")[1][3:].strip())
                    res_query = getResidue(stru_refe, None, chain_query, resid_query)
                    chain_target = line.split("|")[3].split(":")[0][-1]
                    resid_target = int(line.split("|")[3].split(":")[1][3:].strip())
                    res_target = getResidue(stru_cmp, None, chain_target, resid_target)
                    distance = float(line.split("|")[2][3:7])
                    dictpairing[(resid_query, chain_target, resid_target)] = (res_query, res_target, distance)
            pdball = dictpairing
        elif algorithm == "minrms":
            if minmaxrms != None:
                p = subprocess.Popen(
                    ['minrms', '-HS', '-minN', str(minmaxrms[0]), '-maxN', str(minmaxrms[1]), nameficheref,
                     namefichecmp], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                p = subprocess.Popen(['minrms', '-HS', nameficheref, namefichecmp], stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)

            out, err = p.communicate()
            rmsd = 100
            ncom = 100
            f = open("./align_chimera.plot", "r")
            lines = f.readlines()[1:]
            f.close()
            rmsd_prev = 10000000000000
            rmsd_current = 10000000
            skiptest = False
            for line in lines:
                linel = line.split()
                os.remove("./align" + str(linel[0].strip()) + ".msf")
                if not skiptest:
                    rmsd_current = float(linel[1])
                    if rmsd_prev - rmsd_current > 0.1:
                        rmsd_prev = rmsd_current
                        ncom = int(linel[0].strip())
                    else:
                        rmsd = rmsd_prev
                        skiptest = True

            os.remove("./align_chimera.info")
            os.remove("./align_chimera.plot")
            os.remove(nameficheref)
            os.remove(namefichecmp)
            pdball = ""
        elif algorithm == "pymol_cealign":
            namefichepml = "./pml_" + str(datetime.datetime.now()) + ".pml"
            nameficheout = "./out_" + str(datetime.datetime.now()) + ".pdb"
            flu = open(namefichepml, "w")
            flu.write("load " + nameficheref + ", \"ref\"\n")
            flu.write("load " + namefichecmp + ", \"cmp\"\n")
            flu.write("cealign ref and name ca, cmp and name ca\n")
            flu.write("save " + nameficheout + ", \"cmp\"\n")
            flu.close()
            p = subprocess.Popen(['pymol', "-c", namefichepml], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            listout = out.split("\n")
            rmsd = 100
            ncom = 100
            for line in listout:
                listline = line.split()
                if line.startswith("RMSD"):
                    rmsd = float(listline[1])
                    ncom = int(listline[3])
            os.remove(namefichepml)
            compStru, allAtoms = getListAllAtoms("compa", nameficheout)
            t = open(nameficheout, "r")
            pdball = t.read()
            t.close()
            os.remove(nameficheout)
        elif algorithm == "pymol_super":
            namefichepml = "./pml_" + str(datetime.datetime.now()) + ".pml"
            nameficheout = "./out_" + str(datetime.datetime.now()) + ".pdb"
            flu = open(namefichepml, "w")
            flu.write("load " + nameficheref + ", \"ref\"\n")
            flu.write("load " + namefichecmp + ", \"cmp\"\n")
            flu.write("super cmp and name ca, ref and name ca\n")
            flu.write("save " + nameficheout + ", \"cmp\"\n")
            flu.close()
            p = subprocess.Popen(['pymol', "-c", namefichepml], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            # print "---------------------------OUT--------------------"
            # print out
            # print "---------------------------ERR--------------------"
            # print err
            # print "--------------------------------------------------"
            listout = out.split("\n")
            quit()
            rmsd = 100
            ncom = 100
            for line in listout:
                listline = line.split()
                if line.startswith(" Executive: RMS ="):
                    rmsd = float(listline[3])
                if line.startswith(" ExecutiveAlign"):
                    ncom = int(listline[1])
            os.remove(namefichepml)
            compStru, allAtoms = getListAllAtoms("compa", nameficheout)
            t = open(nameficheout, "r")
            pdball = t.read()
            t.close()
            os.remove(nameficheout)
        if algorithm.startswith("pymol"):
            os.remove(nameficheref)
            os.remove(namefichecmp)
    except:
        rmsd = 100
        print sys.exc_info()
        traceback.print_exc(file=sys.stdout)
        # print "Incorrect File: ",compareFile
        ncom = 0
    if not getDictioCorresp:
        return (rmsd, nref, ncom, allAtoms, compStru, pdball)
    else:
        return (rmsd, nref, ncom, allAtoms, compStru, pdball, dictiocorresp)


def computeRMSD(structureA, structureB, limitAtom="CA"):
    reference = []
    for model in structureA.get_list():
        for chain in model.get_list():
            for residue in chain.get_list():
                for atom in residue:
                    if limitAtom != "all" and atom.get_name() != limitAtom:
                        continue
                    reference.append(atom.get_coord())

    compare = []
    for model in structureB.get_list():
        for chain in model.get_list():
            for residue in chain.get_list():
                for atom in residue:
                    if limitAtom != "all" and atom.get_name() != limitAtom:
                        continue
                    compare.append(atom.get_coord())
    if len(reference) > len(compare):
        how = -1 * (len(reference) - len(compare))
        reference = reference[:how]
    elif len(compare) > len(reference):
        how = -1 * (len(compare) - len(reference))
        compare = compare[:how]

    refe = numpy.array(reference)
    compa = numpy.array(compare)
    # print len(reference),len(compare)
    diff = refe - compa
    l = refe.shape[0]
    return numpy.sqrt(sum(sum(diff * diff)) / l)


def getListValidFromTwoList(refe, compare, areFragments=False):
    listCombi = itertools.permutations(compare)
    listValid = []

    # print "reference",len(refe),"compare",len(compare)
    # printSecondaryStructureElements(refe)
    lio = []
    # print "--",len(compare)
    for combi in listCombi:
        lio.append(combi)
    listCombi = lio

    for combi in listCombi:
        valid = False
        # print combi
        for ui in range(len(refe)):
            # print refe
            frag1 = refe[ui]
            frag2 = combi[ui]
            valuta = None
            if areFragments:
                valuta = frag2["fragLength"] != frag1["fragLength"] and (
                    (frag2["sstype"] in ["bs", "cbs"] and frag1["sstype"] not in ["bs", "cbs"]) or (
                        frag2["sstype"] in ["ah", "ch"] and frag1["sstype"] not in ["ah", "ch"]))
            else:
                valuta = len(frag2) != len(frag1)

            if valuta:
                valid = False
                break
            else:
                valid = True
        if valid:
            listValid.append(combi)
    return listValid


def getRMSD2(referencePDB, comparePDB, justSS=False, pos=[]):
    reference = []
    compare = []
    strucd = getStructure("refe", cStringIO.StringIO(referencePDB))
    for model in strucd.get_list():
        for chain in model.get_list():
            trtrtr = sorted(chain.get_unpacked_list(), __resBioOrder2)
            for r in range(len(trtrtr)):
                resi = trtrtr[r]
                for atom in resi:
                    if justSS and atom.get_name() == "SG":
                        if len(pos) > 0 and r in pos:
                            reference.append(atom)
                        else:
                            reference.append(atom)
                    elif not justSS and atom.get_name() in ["CA", "C", "O", "N"]:
                        reference.append(atom)
    strucc = getStructure("cmp", cStringIO.StringIO(comparePDB))
    for model in strucc.get_list():
        for chain in model.get_list():
            trtrtr = sorted(chain.get_unpacked_list(), __resBioOrder2)
            for r in range(len(trtrtr)):
                resi = trtrtr[r]
                for atom in resi:
                    if justSS and atom.get_name() == "SG":
                        if len(pos) > 0 and r in pos:
                            compare.append(atom)
                        else:
                            compare.append(atom)
                    elif not justSS and atom.get_name() in ["CA", "C", "O", "N"]:
                        compare.append(atom)

    r = []
    c = []
    # print "reference==="
    # print reference
    # print "compare===="
    # print compare
    for atm in reference:
        r.append(atm.get_coord())
    for atm in compare:
        c.append(atm.get_coord())
    refe = numpy.array(r)
    compa = numpy.array(c)
    if len(reference) != len(compare):
        return 100
    diff = refe - compa
    l = refe.shape[0]
    rmsd = numpy.sqrt(sum(sum(diff * diff)) / l)

    return rmsd

@deprecated("Use the new algorithm in BORGES_MATRIX.perform_superposition()")
def getRMSD(referenceFile, compareFile, mode, DicParameters=None, algorithm="biopython", backbone=False, listmodel=None,
            doNotMove=False):
    if isinstance(referenceFile, str):
        listValiRef = getListCA("referencia", referenceFile, mode, DicParameters=DicParameters, backbone=backbone,
                                listmodel=listmodel)
        reference = (listValiRef[0])[1]
    elif isinstance(referenceFile, list):
        reference = referenceFile
        listValiRef = [[reference, reference]]

    if isinstance(compareFile, str):
        listValiCmp = getListCA("compare", compareFile, mode, DicParameters=DicParameters, backbone=backbone,
                                listmodel=listmodel)
        compare = (listValiCmp[0])[1]
    elif isinstance(compareFile, list):
        compare = compareFile
        listValiCmp = [[compare, compare]]

    nref = len(reference)
    ncom = len(compare)
    # print "nref",nref,"ncom",ncom
    # print "algorithm",algorithm
    pdball = ""

    if algorithm != "biopython":
        nameficheref = "./ref_" + str(datetime.datetime.now()) + ".pdb"
        writePDBFromListOfAtom(reference, nameficheref)

        namefichecmp = "./cmp_" + str(datetime.datetime.now()) + ".pdb"
        writePDBFromListOfAtom(compare, namefichecmp)

    # for atom in reference:
    #       print atom.get_full_id()
    # print "===="
    # for atom in compare:
    #       print atom.get_full_id()

    try:
        if algorithm == "biopython":
            # print mode, compareFile
            if not isinstance(compareFile, str) and mode != "PDBSTRING" and isinstance(compareFile[0], list):
                listValiCmp = getListValidFromTwoList(reference, compare)

            best_rmsd = 1000000000000
            best_ncom = -1
            for tren in range(len(listValiCmp)):
                no_cmp, compare, lfr = listValiCmp[tren]
                ncom = len(compare)
                # print "nref",nref,"ncom",ncom
                rmsd = None
                if doNotMove:
                    r = []
                    c = []
                    for atm in reference:
                        r.append(atm.get_coord())
                    for atm in compare:
                        c.append(atm.get_coord())
                    refe = numpy.array(r)
                    compa = numpy.array(c)
                    print len(reference), len(compare)
                    diff = refe - compa
                    l = refe.shape[0]
                    rmsd = numpy.sqrt(sum(sum(diff * diff)) / l)
                else:
                    super_imposer = Superimposer()
                    super_imposer.set_atoms(reference, compare)
                    rmsd = super_imposer.rms

                if rmsd <= best_rmsd:
                    best_rmsd = rmsd
                    best_ncom = ncom

            rmsd = best_rmsd
            ncom = best_ncom
            # print "--",rmsd,ncom
        elif algorithm == "pymol_align":
            namefichepml = "./pml_" + str(datetime.datetime.now()) + ".pml"
            flu = open(namefichepml, "w")
            flu.write("load " + nameficheref + ", \"ref\"\n")
            flu.write("load " + namefichecmp + ", \"cmp\"\n")
            flu.write("align cmp and name ca, ref and name ca\n")
            flu.close()
            p = subprocess.Popen(['pymol', "-c", namefichepml], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            listout = out.split("\n")
            rmsd = -100
            for line in listout:
                listline = line.split()
                if line.startswith(" Executive: RMS ="):
                    rmsd = float(listline[3])
            os.remove(namefichepml)
        elif algorithm == "pymol_cealign":
            namefichepml = "./pml_" + str(datetime.datetime.now()) + ".pml"
            flu = open(namefichepml, "w")
            flu.write("load " + nameficheref + ", \"ref\"\n")
            flu.write("load " + namefichecmp + ", \"cmp\"\n")
            flu.write("cealign ref and name ca, cmp and name ca\n")
            flu.close()
            p = subprocess.Popen(['pymol', "-c", namefichepml], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            listout = out.split("\n")
            rmsd = -100
            for line in listout:
                listline = line.split()
                if line.startswith("RMSD"):
                    rmsd = float(listline[1])
            os.remove(namefichepml)
        elif algorithm == "pymol_super":
            namefichepml = "./pml_" + str(datetime.datetime.now()) + ".pml"
            flu = open(namefichepml, "w")
            flu.write("load " + nameficheref + ", \"ref\"\n")
            flu.write("load " + namefichecmp + ", \"cmp\"\n")
            flu.write("super cmp and name ca, ref and name ca\n")
            flu.close()
            p = subprocess.Popen(['pymol', "-c", namefichepml], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            listout = out.split("\n")
            rmsd = -100
            for line in listout:
                listline = line.split()
                if line.startswith(" Executive: RMS ="):
                    rmsd = float(listline[3])
            os.remove(namefichepml)
        if algorithm != "biopython":
            os.remove(nameficheref)
            os.remove(namefichecmp)
    except:
        rmsd = -100
        print sys.exc_info()
        traceback.print_exc(file=sys.stdout)

    return (rmsd, nref, ncom)


def getNumberOfResidues(pdbf):
    stru = getStructure("ref", pdbf)
    how = 0
    for model in stru.get_list():
        for chain in model.get_list():
            for residue in chain.get_list():
                if residue.has_id("CA") and residue.has_id("C") and residue.has_id("O") and residue.has_id("N"):
                    how += 1

    return how


def getStructure(name, pdbf):
    parser = PDBParser()
    structure = parser.get_structure(name, pdbf)
    return structure


def getFragmentsListWithoutCVS(modelpdb, notafile=False):
    tempDirectory = "./temp"
    if not (os.path.exists(tempDirectory)):
        os.makedirs(tempDirectory)

    allist = []

    alls = []
    globalstru = None
    if notafile:
        alls = modelpdb.splitlines()
        globalstru = getStructure("global", cStringIO.StringIO(modelpdb))
    else:
        lop = open(modelpdb, "r")
        alls = lop.readlines()
        lop.close()
        globalstru = getStructure("global", modelpdb)

    countt = 0
    scrivi = True
    lai = None
    previous = -1
    previous_chain = ""
    lineaDascri = None
    for linea in alls:
        if linea.startswith("ATOM") or linea.startswith("HETATM"):
            if scrivi:
                if lai != None:
                    lai.close()
                    parser = PDBParser()
                    structure = parser.get_structure("referencia", tempDirectory + "/" + str(countt - 1) + ".pdb")
                    reference = []
                    for model in structure.get_list():
                        for chain in model.get_list():
                            for residue in chain.get_list():
                            # atom = residue["CA"]
                                reference.append(residue)
                    allist.append(reference)
                    os.remove(tempDirectory + "/" + str(countt - 1) + ".pdb")
                lai = open(tempDirectory + "/" + str(countt) + ".pdb", "w")
                if lineaDascri != None:
                    lai.write(lineaDascri)
                    lineaDascri = None
                countt += 1
                scrivi = False
            residuo = int((linea[22:26]).strip())
            chain_res = str(linea[21])

            if previous > 0:
                resaN = getResidue(globalstru, globalstru.get_list()[0].get_id(), chain_res, (' ', residuo, ' '))
                prevResC = getResidue(globalstru, globalstru.get_list()[0].get_id(), previous_chain,
                                      (' ', previous, ' '))
                if checkContinuity(prevResC, resaN) or (residuo == previous):
                    lai.write(linea)
                    previous = residuo
                    previous_chain = chain_res
                else:
                    scrivi = True
                    lineaDascri = linea
                    previous = residuo
                    previous_chain = chain_res
            else:
                lai.write(linea)
                previous = residuo
                previous_chain = chain_res
    if lai != None:
        lai.close()
        parser = PDBParser()
        structure = parser.get_structure("referencia", tempDirectory + "/" + str(countt - 1) + ".pdb")
        reference = []
        for model in structure.get_list():
            for chain in model.get_list():
                for residue in chain.get_list():
                    # atom = residue["CA"]
                    reference.append(residue)
        allist.append(reference)
        os.remove(tempDirectory + "/" + str(countt - 1) + ".pdb")

    return allist

@deprecated('Use BORGES_MATRIX.annotate_pdb_model_with_aleph and BORGES_MATRIX.get_all_fragments')
def getFragmentListFromListUsingSomeAtoms(struc, listaFra, caUsed, caNoUsed):
    unaOpera = True
    # print "--"
    # printSecondaryStructureElements(listaFra)
    # print "--"
    while unaOpera:
        almenoUno = True
        unaOpera = False
        while almenoUno:
            almenoUno = False
            for doing in range(len(listaFra)):
                fra1 = listaFra[doing]
                a1 = fra1["resIdList"][0]
                a1N = getResidue(struc, fra1["model"], fra1["chain"], a1)
                # a1C = getAtom(struc,fra1["model"],fra1["chain"],a1,"C")
                a2 = fra1["resIdList"][-1]
                # a2N = getAtom(struc,fra1["model"],fra1["chain"],a2,"N")
                a2C = getResidue(struc, fra1["model"], fra1["chain"], a2)
                modela2 = fra1["model"]
                chaina2 = fra1["chain"]
                pdbida2 = fra1["pdbid"]
                sst = None
                trovato = False
                for boing in range(doing + 1, len(listaFra)):
                    fra2 = listaFra[boing]
                    a3 = fra2["resIdList"][0]
                    a3N = getResidue(struc, fra2["model"], fra2["chain"], a3)
                    # a3C = getAtom(struc,fra2["model"],fra2["chain"],a3,"C")
                    a4 = fra2["resIdList"][-1]
                    # a4N = getAtom(struc,fra2["model"],fra2["chain"],a4,"N")
                    a4C = getResidue(struc, fra2["model"], fra2["chain"], a4)
                    modela3 = fra2["model"]
                    chaina3 = fra2["chain"]
                    pdbida3 = fra2["pdbid"]

                    condizio1 = modela2 == modela3 and chaina2 == chaina3 and checkContinuity(a2C, a3N)
                    condizio2 = modela2 == modela3 and chaina2 == chaina3 and checkContinuity(a4C, a1N)
                    """
                    print "paragono"
                    print fra1["resIdList"]
                    print "con"
                    print fra2["resIdList"]
                    print "condizio1",condizio1
                    print "condizio2",condizio2
                    print modela2,modela3,chaina2,chaina3,a2[1],a3[1]+1,a2[2],a3[2]
                    """
                    if condizio1:
                        sst = createCustomFragment(struc, pdbida2, modela2, chaina2,
                                                   fra1["resIdList"] + fra2["resIdList"], fra1["sstype"],
                                                   fra1["fragLength"] + fra2["fragLength"])
                        trovato = True
                    elif condizio2:
                        sst = createCustomFragment(struc, pdbida2, modela2, chaina2,
                                                   fra2["resIdList"] + fra1["resIdList"], fra2["sstype"],
                                                   fra1["fragLength"] + fra2["fragLength"])
                        trovato = True

                    if trovato:
                        break
                # print "Trovato is in frags",trovato
                if trovato:
                    almenoUno = True
                    unaOpera = True
                    nuova = []
                    # print "doing",doing,"boing",boing
                    # print "lenlistafra",len(listaFra)
                    for q in range(len(listaFra)):
                        if q not in [doing, boing]:
                            nuova.append(listaFra[q])
                            # else:
                            #       print "salto",q
                    nuova.append(sst)
                    listaFra = deepcopy(nuova)
                    break

        almenoUno = True
        while almenoUno:
            almenoUno = False
            done = []
            for pos in range(len(caNoUsed)):
                elem = caNoUsed[pos]
                a1C = elem.get_parent()
                a1N = elem.get_parent()
                a1 = elem.get_parent().get_id()
                chaina1 = elem.get_parent().get_parent().get_id()
                modela1 = elem.get_parent().get_parent().get_parent().get_id()
                trovato = False
                sst = None
                for doing in range(len(listaFra)):
                    fra = listaFra[doing]
                    a2 = fra["resIdList"][0]
                    a2N = getResidue(struc, fra["model"], fra["chain"], a2)
                    # a2C = getAtom(struc,fra1["model"],fra1["chain"],a2,"C")
                    a3 = fra["resIdList"][-1]
                    # a3N = getAtom(struc,fra2["model"],fra2["chain"],a3,"N")
                    a3C = getResidue(struc, fra["model"], fra["chain"], a3)
                    modela2 = fra["model"]
                    chaina2 = fra["chain"]
                    pdbida2 = fra["pdbid"]

                    condizio1 = modela1 == modela2 and chaina1 == chaina2 and checkContinuity(a1C, a2N)
                    condizio2 = modela1 == modela2 and chaina1 == chaina2 and checkContinuity(a3C, a1N)
                    if condizio1:
                        sst = createCustomFragment(struc, pdbida2, modela2, chaina2, fra["resIdList"] + [a1],
                                                   fra["sstype"], fra["fragLength"] + 1)
                        trovato = True
                    elif condizio2:
                        sst = createCustomFragment(struc, pdbida2, modela2, chaina2, fra["resIdList"] + [a1],
                                                   fra["sstype"], fra["fragLength"] + 1)
                        trovato = True

                    if trovato:
                        done.append(pos)
                        break
                # print "Trovato is in atoms",trovato
                if trovato:
                    almenoUno = True
                    unaOpera = True
                    nuova = []
                    # print "lenlistafra",len(listaFra)
                    for q in range(len(listaFra)):
                        if q not in [doing]:
                            nuova.append(listaFra[q])
                            # else:
                            #       print "salto",q
                    nuova.append(sst)
                    listaFra = deepcopy(nuova)

            news_canouse = []
            for ind in range(len(caNoUsed)):
                if ind in done:
                    caUsed.append(caNoUsed[ind])
                else:
                    news_canouse.append(caNoUsed[ind])
            caNoUsed = news_canouse

    listFragso, dicDescriptor = orderFragmentAccordingtopologicalOrder(listaFra, struc, True, True)

    if len(caNoUsed) > 0:
        print caNoUsed
        print "Some residues could not be added automatically to the discovered fragments."

    # printSecondaryStructureElements(listaFra)
    # for cds in caNoUsed:
    #   print cds.get_full_id()
    # print len(caNoUsed)
    return (struc, listFragso, dicDescriptor, caUsed, caNoUsed)

@deprecated('Use BORGES_MATRIX.annotate_pdb_model_with_aleph and BORGES_MATRIX.get_all_fragments')
def getFragmentListFromPDBUsingAllAtoms(inputPdbFile, drawDistri):
    tupleResult = getFragmentListFromPDB(inputPdbFile, True, drawDistri)
    struc = tupleResult[0]
    listaFra = tupleResult[1]
    caUsed = tupleResult[3]
    caNoUsed = tupleResult[4]
    # print "EEEEEEEEE",inputPdbFile
    # print "1",printSecondaryStructureElements(listaFra)
    # print "2",caNoUsed
    # print "3",len(caNoUsed)
    return getFragmentListFromListUsingSomeAtoms(struc, listaFra, caUsed, caNoUsed)

@deprecated('Use BORGES_MATRIX.annotate_pdb_model_with_aleph and BORGES_MATRIX.get_all_fragments')
def getFragmentListFromPDB(pdbf, isModel, drawDistri):
    structure = None
    idname = None
    parser = PDBParser()

    if isinstance(pdbf, str) and os.path.exists(pdbf):
        idname = os.path.basename(pdbf)[:-4]
        structure = parser.get_structure(idname, pdbf)
    else:
        idname = "stru1"
        try:
            idname = os.path.basename(pdbf.name)[:-4]
        except:
            pass
        structure = parser.get_structure(idname, pdbf)

    return getFragmentListFromStructure(structure, isModel, drawDistri, idname)

@deprecated('Use BORGES_MATRIX.annotate_pdb_model_with_aleph and BORGES_MATRIX.get_all_fragments')
def getFragmentListFromStructure(structure, isModel, drawDistri, idname):
    lengthFragment = SUFRAGLENGTH
    atomUsed = []
    allAtomCA = []

    h = []

    for model in structure.get_list():
        for chain in model.get_list():
            coordCA = []
            coordO = []
            numerOfResidues = 0

            for residue in chain.get_list():
                # solo se e un amminoacido ed ha almeno un carbonio alfa e un ossigeno
                if (residue.get_resname().upper() in AAList) and (residue.has_id("CA")) and (residue.has_id("O")) and (
                        residue.has_id("C")) and (residue.has_id("N")):
                    ca = residue["CA"]

                    if ca.get_occupancy() < 0.5:
                        continue
                    if (residue["O"]).get_occupancy() < 0.5:
                        continue
                    if (residue["C"]).get_occupancy() < 0.5:
                        continue
                    if (residue["N"]).get_occupancy() < 0.5:
                        continue

                    numerOfResidues += 1

                    # per ogni atomo di Carbonio alfa, viene salvato in coordCA quattro valori:
                    # [0] pos_X
                    # [1] pos_Y
                    # [2] pos_Z
                    # [3] id del residuo di cui fa parte
                    # [4] residue name code in 3 letters
                    coordCA.append(
                        [float(ca.get_coord()[0]), float(ca.get_coord()[1]), float(ca.get_coord()[2]), residue.get_id(),
                         residue.get_resname()])
                    allAtomCA.append(ca)
                    ca = residue["O"]
                    coordO.append(
                        [float(ca.get_coord()[0]), float(ca.get_coord()[1]), float(ca.get_coord()[2]), residue.get_id(),
                         residue.get_resname()])

            numberOfSegments = numerOfResidues - lengthFragment + 1
            # print numerOfResidues,lengthFragment,numberOfSegments,len(coordCA),len(coordO)
            # sys.exit(0)
            if numberOfSegments <= 0:
                # print "\t\t\tNo enough residues available to create a fragment"
                continue
            vectorsCA = ADT.get_matrix(numberOfSegments, 3)
            vectorsO = ADT.get_matrix(numberOfSegments, 3)

            for i in range(lengthFragment):
                vectorsCA[0] = [vectorsCA[0][0] + coordCA[i][0] / float(lengthFragment),
                                vectorsCA[0][1] + coordCA[i][1] / float(lengthFragment),
                                vectorsCA[0][2] + coordCA[i][2] / float(lengthFragment)]
                vectorsO[0] = [vectorsO[0][0] + coordO[i][0] / float(lengthFragment),
                               vectorsO[0][1] + coordO[i][1] / float(lengthFragment),
                               vectorsO[0][2] + coordO[i][2] / float(lengthFragment)]

            # sto cambiando che invece di -coordCA[i][0] metto coordCA[i-1][0] perche voglio togliere il precedente
            for i in range(1, len(vectorsCA)):
                vectorsCA[i] = [vectorsCA[i - 1][0] + (coordCA[i + lengthFragment - 1][0] - coordCA[i - 1][0]) / float(
                    lengthFragment),
                                vectorsCA[i - 1][1] + (coordCA[i + lengthFragment - 1][1] - coordCA[i - 1][1]) / float(
                                    lengthFragment),
                                vectorsCA[i - 1][2] + (coordCA[i + lengthFragment - 1][2] - coordCA[i - 1][2]) / float(
                                    lengthFragment)]
                vectorsO[i] = [
                    vectorsO[i - 1][0] + (coordO[i + lengthFragment - 1][0] - coordO[i - 1][0]) / float(lengthFragment),
                    vectorsO[i - 1][1] + (coordO[i + lengthFragment - 1][1] - coordO[i - 1][1]) / float(lengthFragment),
                    vectorsO[i - 1][2] + (coordO[i + lengthFragment - 1][2] - coordO[i - 1][2]) / float(lengthFragment)]

            vectorsH = [0.0 for _ in range(numberOfSegments)]

            descPosition = "" + str(idname) + "\t" + str(model.get_id()) + "\t" + str(chain.get_id()) + "\t"

            distriCV = []
            distriDf = []
            for i in range(len(vectorsCA)):
                XH = vectorsCA[i][0] - vectorsO[i][0]
                YH = vectorsCA[i][1] - vectorsO[i][1]
                ZH = vectorsCA[i][2] - vectorsO[i][2]

                prevRes = (" ", None, " ")
                ncontigRes = 0
                resids = []
                prev_model = None
                prev_chain = None

                for yui in range(i, i + lengthFragment):  # quindi arrivo a i+lengthFragment-1
                    resan = (coordCA[yui])[3]
                    resa = resan
                    resids.append(list(resan) + [(coordCA[yui])[4]])
                    if prevRes == (" ", None, " "):
                        ncontigRes += 1
                    else:
                        resaN = getResidue(structure, model.get_id(), chain.get_id(), resan)
                        prevResC = getResidue(structure, prev_model, prev_chain, prevRes)
                        # print "WHY?",resaN,prevResC,checkContinuity(prevResC,resaN)
                        if checkContinuity(prevResC, resaN):
                            ncontigRes += 1
                    prevRes = resa
                    prev_model = model.get_id()
                    prev_chain = chain.get_id()

                if ncontigRes != lengthFragment:
                    vectorsH[i] = 100  # this value identify a not reliable measure for cv
                else:
                    vectorsH[i] = numpy.sqrt(XH * XH + YH * YH + ZH * ZH)

                # print ncontigRes,lengthFragment,i
                # blocco per il calcolo delle distribuzioni
                distriCV.append((i, vectorsH[i]))
                # if vectorsH[i] == -100:
                #       print "non sono continui a",i,coordCA[i][3]
                # print "sono",i,vectorsH[i]
                if i != 0:
                    if vectorsH[i] == 100 and vectorsH[i - 1] == 100:
                        distriDf.append(((i - 1, i), 200))
                    else:
                        distriDf.append(((i - 1, i), numpy.abs(vectorsH[i] - vectorsH[i - 1])))

            resIDs = []
            amn = []
            for q in range(len(coordCA)):
                res = coordCA[q][3]
                resIDs.append(res)
                amn.append(coordCA[q][4])  # take the aa name directly from the array of coordinates
            sstp = discoverFragments(descPosition, coordCA, coordO, resIDs, structure, amn, distriCV, distriDf,
                                     lengthFragment)
            # print resIDs
            # print distriCV
            # print distriDf
            # print coordCA
            # print coordO

            for sst in sstp:
                # print sst
                # print "-----------------------------------"
                if sst["sstype"] != "nothing":
                    if sst["fragLength"] >= 3 and sst["sstype"] != "something":
                        # sst["resIdList"] = sorted(sst["resIdList"])
                        # print sst["resIdList"]
                        h.append(sst)
                        # print sst["fragLength"],"lllllllll"
                        # print sst["distCV"]
                        if drawDistri:
                            drawDistribution(sst, lengthFragment)
                        for up in sst["resIdList"]:
                            # atomUsed.append(allAtomCA[startFrag+up])
                            atomUsed.append(structure[sst["model"]][sst["chain"]][up]["CA"])
                    elif drawDistri:
                        drawDistribution(sst, lengthFragment)
                        # print sst
    # print "////////-",h
    if isModel:
        h, dicDescriptor = orderFragmentAccordingtopologicalOrder(h, structure, False, True)

        atomAvailable = []
        for u in allAtomCA:
            if u not in atomUsed:
                atomAvailable.append(u)

        return (structure, h, dicDescriptor, atomUsed, atomAvailable)
    else:
        # printSecondaryStructureElements(h)
        # sys.exit(0)
        # h = removeEqualStructures(h) #attivare l'eliminazione di strutture uguali dopo la revisione della procedura
        return (structure, h, {}, [], [])

# Ana's function to read HELIX and SHEET records
def read_pdb_ss_information_return_list_dics (input_pdb_file):
    """Reads the pdb and colects the information about each ss element in a list
    :param input_file_pdb: pdb file with the ss annotation
    :type input_pdb_file: str
    :return list_file_all: list containing a dictionary for each aa presented in a ss
    :rtype list_file_all: list
    :return False: In case no remark was found
    :rtype: bool
    """

    file=open(input_pdb_file)
    file_lines=file.readlines()
    file.close()
    list_file_all=[] #List with dictionaries. Each dictionary correspond to each ss element of the pdb file

    def catch_substring(a, b, line):
        try:
            return line[a:b].strip()
        except:
            return ""

    for line in file_lines:
        dic_var= {}
        dic_var['ss']= line[0:6].strip()
        if dic_var['ss'] == 'HELIX':
            dic_var['ser_num'] = int(catch_substring(7, 10, line)) #Serial number of the helix. This starts at 1 abd increases incrementally
            dic_var['helix_id'] = catch_substring(11, 14, line) #Helix identifier. In additio to a serial number, each helix is given and alphanumeric character helix identifier
            dic_var['init_res_name'] = catch_substring(15, 18, line) #Name of the initial residue
            dic_var['init_chain_id'] = catch_substring(19, 20, line) #Chain identifier for the chain containing this helix
            dic_var['init_seq_num'] = int(catch_substring(21, 25, line)) #Sequence number of the initial residue
            dic_var['init_i_code'] = catch_substring(25, 26, line) #Insertion code of the initial residue
            dic_var['end_res_name'] = catch_substring(27, 30, line) #Name of the terminal residue of the helix
            dic_var['end_chain_id'] = catch_substring(31, 32, line) #Chain identifier fot the chain containing this helix
            dic_var['end_seq_num'] = int(catch_substring(33, 37, line)) #Sequence number of the terminal residue
            dic_var['end_i_code'] = catch_substring(37, 38, line) #Insertion code of the terminal residue
            dic_var['helix_class'] = int(catch_substring(38, 40, line)) #Helix class (see ftp://ftp.wwpdb.org/pub/pdb/doc/format_descriptions/Format_v33_A4.pdf)
            dic_var['comment'] = catch_substring(40, 70, line) #Comment about this helix
            dic_var['length'] = int(catch_substring(71, 76, line)) #Length of this helix
            list_file_all.append(dic_var)
        elif dic_var['ss'] == 'SHEET':
            dic_var['strand'] = int(catch_substring(7, 10, line)) #Strand number which starsts aty 1 fot each strand within a sheet and increases by one
            dic_var['sheet_id'] = catch_substring(11, 14, line) #Sheet identifier
            dic_var['num_strands'] = int(catch_substring(14, 16, line)) #Number of strands in sheet
            dic_var['init_res_name'] = catch_substring(17, 20, line) #Residue name of initial residue
            dic_var['init_chain_id'] = catch_substring(21, 22, line) #Chain identifier of initial residue in strand
            dic_var['init_seq_num'] = int(catch_substring(22, 26, line)) #Sequence number of initial residue in strand
            dic_var['init_i_code'] = catch_substring(26, 27, line) #Insertion code of initial residue in strand
            dic_var['end_res_name'] = catch_substring(28, 31, line) #Residue name of terminal residue
            dic_var['end_chain_id'] = catch_substring(32, 33, line) #Chain identifier of terminal residue
            dic_var['end_seq_num'] = int(catch_substring(33, 37, line)) #Sequence number of terminal residue
            dic_var['end_i_code'] = catch_substring(37, 38, line) #Insertion code of terminal residue
            dic_var['sense'] = int(catch_substring(38, 40, line)) #Sense of strand with respect to previous strand in the sheet. 0 if first strand, 1 if parallel, and -1 if anti-parallel
            dic_var['cur_atom'] = catch_substring(41, 45, line) #Registration. Atom name in current strand
            dic_var['cur_res_name'] = catch_substring(45, 48, line) #Registration. Residue name in current strand
            dic_var['cur_chain_id'] = catch_substring(49, 50, line) #Registration. Chain identifier in current strand
            dic_var['cur_res_seq'] = catch_substring(50, 54, line) #Residue sequence number in current strand
            dic_var['cur_i_code'] = catch_substring(54, 55, line) #Registration. Insertion code in current strand
            dic_var['prev_atom'] = catch_substring(56, 60, line) #Registration. Atom name in previous strand
            dic_var['prev_res_name'] = catch_substring(60, 63, line) #Registration. Residue name in previous strand
            dic_var['prev_chain_id'] = catch_substring(64, 65, line) #Registration. Cahin identififer in previous strand
            dic_var['prev_res_seq'] = catch_substring(65, 69, line) #Registration. Residue sequence number in previous strand
            dic_var['prev_i_code'] = catch_substring(69, 70, line) #Registration. Insertion code in previous strand
            list_file_all.append(dic_var)
        if len (list_file_all) == 0:
            return False
        else:
            return list_file_all



# TEMPORANEO NOT USED TO BE CHANGED
def removeEqualStructures(FragmentList):
    """
    TEMPORARY METHOD. NOT USED NOW. TO BE CHANGED. DOESN'T WORK PROPERLY
    """
    frammenti = []

    modelsList = {}
    for uyu in FragmentList:
        mod = uyu["model"]
        if mod not in modelsList.keys():
            modelsList[mod] = []
            modelsList[mod].append(uyu)
        else:
            modelsList[mod].append(uyu)

    for inds0 in modelsList.keys():
        lisBigSSMod = modelsList[inds0]
        chainsList = {}
        for uyuc in lisBigSSMod:
            cha = uyuc["chain"]
            if cha not in chainsList.keys():
                chainsList[cha] = []
                chainsList[cha].append(uyuc)
            else:
                chainsList[cha].append(uyuc)

        for iu1 in range(len(chainsList.keys())):
            inds1 = chainsList.keys()[iu1]
            lisBigSSCha1 = chainsList[inds1]

            save1 = True
            for iu2 in range(iu1 + 1, len(chainsList.keys())):
                inds2 = chainsList.keys()[iu2]
                if inds1 == inds2:
                    continue

                lisBigSSCha2 = chainsList[inds2]
                VisitedList = []
                nEqual = 0
                preva1 = 0
                preva2 = 0
                unoContainsDos = False
                dosContainsUno = True
                for indl1 in range(len(lisBigSSCha1)):
                    fragment1 = lisBigSSCha1[indl1]
                    foundIt = False
                    for indl2 in range(len(lisBigSSCha2)):
                        fragment2 = lisBigSSCha1[indl2]
                        if fragment1["sstype"] != fragment2["sstype"] or indl2 in VisitedList:
                            continue
                        if fragment1["sequence"] == fragment2["sequence"] and fragment1["fragLength"] == fragment2[
                            "fragLength"]:
                            nEqual += 1
                            foundIt = True
                            VisitedList.append(indl2)
                            break
                        regex = re.compile("^[a-zA-Z|-]{0,4}" + fragment1["sequence"] + "[a-zA-Z|-]{0,4}$")
                        if regex.match(fragment2["sequence"]):
                            if fragment1["fragLength"] > fragment2["fragLength"]:
                                preva1 += 1
                                foundIt = True
                                VisitedList.append(indl2)
                                break
                            else:
                                preva2 += 1
                                foundIt = True
                                VisitedList.append(indl2)
                                break
                    if not foundIt:
                        dosContainsUno = False
                if len(VisitedList) == len(lisBigSSCha2):
                    unoContainsDos = True
                if unoContainsDos and dosContainsUno:
                    # sono uguali
                    if preva1 > preva2:
                        # scegli 1
                        save1 = True
                    else:
                        # scegli 2
                        save1 = False
                        break  # passa al prossimo 1
                elif not unoContainsDos and not dosContainsUno:
                    # non sono confrontabili
                    save1 = True
                elif unoContainsDos:
                    # scegli 1
                    save1 = True
                elif dosContainsUno:
                    # scegli 2
                    save1 = False
                    break  # passa al prossimo 1
            if save1:
                # salva1
                for fraggy in lisBigSSCha1:
                    frammenti.append(fraggy)

    return frammenti


def getSSFromResiduesWithRamachandran(listres):
    # listres = listres[1:-1]
    names = [resi.get_resname() for resi in listres]
    tuc = getPhiPsiList(listres)
    listresult = []
    for p in range(len(tuc)):
        pair = tuc[p]
        phi = pair[0]
        psi = pair[1]
        result = getResidueRamachandranStructure(phi, psi, names[p])
        listresult.append(result)

    helices = ["bs1", "bs2", "1gly1", "3gly1"]
    strands = ["rah1", "rah2", "lah1", "lah2", "2gly1", "5gly1", "4pro1"]
    # helices = ["bs1","bs2","out","1gly1","1gly2","2gly1","2gly2","3gly1","4gly1","5gly1","6gly1","1pro2","2pro2","1pro1","2pro1","3pro1","4pro1","1oth1","2oth2","3oth2","4oth2","5oth2"]
    # strands = ["rah1","rah2","lah1","lah2","out","1gly1","1gly2","2gly1","2gly2","3gly1","4gly1","5gly1","6gly1","1pro2","2pro2","1pro1","2pro1","3pro1","4pro1","1oth1","2oth2","3oth2","4oth2","5oth2"]
    try:
        #print "----",list(set(helices)),listresult,set(listresult[1:-1])
        cde = "ah" if len(list(set(helices) & set(listresult[1:-1]))) == 0 else "coil"
        if cde == "coil":
            cde = "bs" if len(list(set(strands) & set(listresult[1:-1]))) == 0 else "coil"
        if cde == "coil":
            cde = "gly" if all(map(lambda x: "gly" in x, listresult[1:-1])) else "coil"
        if cde == "coil":
            cde = "pro" if all(map(lambda x: "pro" in x, listresult[1:-1])) else "coil"
    except:
        print "ERROR:============================="
        print sys.exc_info()
        traceback.print_exc(file=sys.stdout)
        print "==================================="
        cde = "coil"

    # print "SS-Ramachandran",listresult[1:-1],"SS_PREDICTED",cde
    return cde


def computeRamachandran(structure, model, chain, resIDs, nres):
    luc = []
    tuc = []
    resi = structure[model][chain][resIDs[nres]]

    menC = False
    for residue in (structure[model][chain]):
        resaN = resi
        prevResC = residue
        if checkContinuity(prevResC, resaN):
            luc.append(structure[model][chain][residue.get_id()])
            menC = True
            break

    luc.append(resi)

    piuC = False
    for residue in (structure[model][chain]):
        resaN = residue
        prevResC = resi
        if checkContinuity(prevResC, resaN):
            luc.append(structure[model][chain][residue.get_id()])
            piuC = True
            break

    result = None
    if menC and piuC:
        # print "luc",luc
        tuc = getPhiPsiList(luc)
        # print "tuc",tuc

        phi = (tuc[1])[0]
        psi = (tuc[1])[1]
        # print "phi",phi,"psi",psi
        result = getResidueRamachandranStructure(phi, psi, luc[1].get_resname())

    # print "ededede",luc
    # print "e",luc[1]
    # print "eew",result

    return result, menC, piuC

@deprecated('Use Bioinformatics3.get_residue')
def getResidue(structure, model, chain, residue):
    for m in structure:
        if m.get_id() == model or model == None:
            for c in m:
                if c.get_id() == chain:
                    for r in c:
                        if r.get_id() == residue or isinstance(residue, int) and r.get_id()[1] == residue:
                            return r

@deprecated('Use Bioinformatics3.get_atom')
def getAtom(structure, model, chain, residue, atom):
    for m in structure:
        if m.get_id() == model or model == None:
            for c in m:
                if c.get_id() == chain:
                    for r in c:
                        if r.get_id() == residue or isinstance(residue, int) and r.get_id()[1] == residue:
                            for a in r:
                                if a.get_id() == atom:
                                    return a


def discoverFragments(descPosition, CAatomCoord, OatomCoord, resIDs, structure, amn, distCV, distDF, window):
    li = descPosition.split("\t")
    pdb = li[0]
    model = int(li[1])
    chain = li[2]

    meanTAH = 2.2
    meanTBS = 1.4
    st1AH = 0.10
    st2AH = 0.15
    st1BS = 0.10
    st2BS = 0.15
    outsideAlpha = 0.35
    outsideBeta = 0.30
    distSS = []

    isAlphaHelix = False
    isBetaSheet = False
    isCurvedHelix = False
    forceValidation = False
    startFrag = -1
    endFrag = -1
    listReturn = []

    aggio = ""
    cont = 0
    step = window - 1
    jumpindex = -1
    for ind in range(len(distCV)):
        # print "Turno:",distCV[ind]
        if jumpindex != -1 and ind < jumpindex:
            # print "salto il residuo",cont
            distSS.append((-1, ""))
            cont += 1
            continue

        jumpindex = -1
        (indice, cvv) = distCV[ind]

        if startFrag == -1:
            startFrag = ind
            # print startFrag,endFrag

            # print model,chain,cont,step

        result, menC, piuC = computeRamachandran(structure, model, chain, resIDs, cont)

        # print "per capire00",startFrag,ind
        if numpy.abs(meanTAH - cvv) <= st1AH and result not in ["bs1", "bs2", "out"]:
            distSS.append((indice, "ah"))
            isAlphaHelix = True
            if isBetaSheet:
                endFrag = ind + step
                """
                print "creo frammento ",cont,"modo a"
                print "==============================0",startFrag,ind,ind-1
                print len(distCV[startFrag:ind]),len(distSS[startFrag:ind])
                print distCV[startFrag:ind]
                print distSS[startFrag:ind]
                print resIDs[startFrag:endFrag]
                print amn[startFrag:endFrag]
                """
                diston = distSS[startFrag:ind]
                st = recognizeFragment(pdb, model, chain, CAatomCoord[startFrag:endFrag], OatomCoord[startFrag:endFrag],
                                       resIDs[startFrag:endFrag], amn[startFrag:endFrag], distCV[startFrag:ind],
                                       distDF[startFrag:ind], sstype="bs", distS=diston)
                listReturn.append(st)
                if st["fragLength"] >= 3:
                    startFrag = ind + step
                    endFrag = -1
                    jumpindex = ind + step
                else:
                    startFrag = -1
                    endFrag = -1
                    jumpindex = -1

                isAlphaHelix = False
                isBetaSheet = False
                isCurvedHelix = False
        elif numpy.abs(meanTBS - cvv) <= st1BS and result not in ["rah1", "rah2", "lah1", "lah2", "out"]:
            distSS.append((indice, "bs"))
            # distCV[ind] = (indice,cvv,"bs")
            isBetaSheet = True
            if isAlphaHelix or isCurvedHelix:
                # print resIDs[startFrag:endFrag]
                # print isAlphaHelix,isCurvedHelix,isBetaSheet
                # sys.exit(0)
                ti = ""
                if isCurvedHelix:
                    ti = "ch"
                elif isAlphaHelix:
                    ti = "ah"

                endFrag = ind + step
                """print "creo frammento ",cont,"modo b"
                print "==============================0"
                print len(distCV[startFrag:ind]),len(distSS[startFrag:ind])
                print distCV[startFrag:ind]
                print distSS[startFrag:ind]
                print resIDs[startFrag:endFrag]
                print amn[startFrag:endFrag]"""

                diston = distSS[startFrag:ind]

                st = recognizeFragment(pdb, model, chain, CAatomCoord[startFrag:endFrag], OatomCoord[startFrag:endFrag],
                                       resIDs[startFrag:endFrag], amn[startFrag:endFrag], distCV[startFrag:ind],
                                       distDF[startFrag:ind], sstype=ti, distS=diston)
                listReturn.append(st)
                if st["fragLength"] >= 3:
                    startFrag = ind + step
                    endFrag = -1
                    jumpindex = ind + step
                else:
                    startFrag = -1
                    endFrag = -1
                    jumpindex = -1

                isAlphaHelix = False
                isBetaSheet = False
                isCurvedHelix = False
        elif numpy.abs(meanTAH - cvv) <= st2AH and result not in ["bs1", "bs2", "out"]:
            distSS.append((indice, "ahd"))
            # distCV[ind] = (indice,cvv,"ahd")
            isAlphaHelix = True
            if isBetaSheet:
                endFrag = ind + step
                """
                print "creo frammento ",cont,"modo c"
                print "==============================0"
                print len(distCV[startFrag:ind]),len(distSS[startFrag:ind])
                print distCV[startFrag:ind]
                print distSS[startFrag:ind]
                print resIDs[startFrag:endFrag]
                print amn[startFrag:endFrag]
                """
                diston = distSS[startFrag:ind]

                st = recognizeFragment(pdb, model, chain, CAatomCoord[startFrag:endFrag], OatomCoord[startFrag:endFrag],
                                       resIDs[startFrag:endFrag], amn[startFrag:endFrag], distCV[startFrag:ind],
                                       distDF[startFrag:ind], sstype="bs", distS=diston)
                listReturn.append(st)
                if st["fragLength"] >= 3:
                    startFrag = ind + step
                    endFrag = -1
                    jumpindex = ind + step
                else:
                    startFrag = -1
                    endFrag = -1
                    jumpindex = -1

                isAlphaHelix = False
                isBetaSheet = False
                isCurvedHelix = False
        elif numpy.abs(meanTBS - cvv) <= st2BS and result not in ["rah1", "rah2", "lah1", "lah2", "out"]:
            distSS.append((indice, "bsd"))
            # distCV[ind] = (indice,cvv,"bsd")
            isBetaSheet = True
            if isAlphaHelix or isCurvedHelix:
                endFrag = ind + step
                ti = ""
                if isCurvedHelix:
                    ti = "ch"
                elif isAlphaHelix:
                    ti = "ah"
                """print "creo frammento ",cont,"modo d"
                print "==============================0"
                print len(distCV[startFrag:ind]),len(distSS[startFrag:ind])
                print distCV[startFrag:ind]
                print distSS[startFrag:ind]
                print resIDs[startFrag:endFrag]"""

                diston = distSS[startFrag:ind]

                st = recognizeFragment(pdb, model, chain, CAatomCoord[startFrag:endFrag], OatomCoord[startFrag:endFrag],
                                       resIDs[startFrag:endFrag], amn[startFrag:endFrag], distCV[startFrag:ind],
                                       distDF[startFrag:ind], sstype=ti, distS=diston)
                listReturn.append(st)
                if st["fragLength"] >= 3:
                    startFrag = ind + step
                    endFrag = -1
                    jumpindex = ind + step
                else:
                    startFrag = -1
                    endFrag = -1
                    jumpindex = -1

                isAlphaHelix = False
                isBetaSheet = False
                isCurvedHelix = False
        else:
            # print "/////////"
            # print indice
            # print cvv
            # print "////////"
            distSS.append((indice, "d"))
            # print "distorsioneeeeeee"
            # print numpy.abs(meanTAH-cvv),st2AH,meanTAH,cvv
            if cvv == 100 or ((ind + step) - startFrag) + step >= 3:
                endFrag = ind + step
                # print "tagliato",cvv,startFrag,endFrag
                if endFrag != startFrag:
                    forceValidation = True
                    if isCurvedHelix:
                        aggio = "ch"
                    elif isAlphaHelix:
                        aggio = "ah"
                    else:
                        aggio = "bs"
                # print ind,aggio
                """
                elif (((isAlphaHelix or isCurvedHelix) and numpy.abs(meanTAH-cvv) >= outsideAlpha) or (isBetaSheet and numpy.abs(meanTBS-cvv) >= outsideBeta)):
                endFrag = ind+step
                forceValidation = True
                if isCurvedHelix:
                        aggio = "ch"
                elif isAlphaHelix:
                        aggio = "ah"
                else:
                        aggio = "bs"
            elif (((isAlphaHelix or isCurvedHelix) and numpy.abs(meanTAH-cvv) < outsideAlpha and ind == len(distCV)-1) or (isBetaSheet and numpy.abs(meanTBS-cvv) >= outsideBeta and ind == len(distCV)-1)):
                endFrag = ind+step
                forceValidation = True
                if isCurvedHelix:
                        aggio = "ch"
                elif isAlphaHelix:
                        aggio = "ah"
                else:
                        aggio = "bs"
            elif not isAlphaHelix and not isCurvedHelix and not isBetaSheet:
                endFrag = ind+step
                forceValidation = True
                aggio = "nothing"
                """

            toContinue = True
            resultL = []
            result = None
            menC = False
            piuC = False
            for wer in range(window):
                result, menC, piuC = computeRamachandran(structure, model, chain, resIDs, cont + wer)
                resultL.append(result)
                if result in [None, "out"]:
                    # print "=??????",result,resIDs,cont+wer,menC,piuC
                    toContinue = False
                    break

            # print "helix",isAlphaHelix,"curved",isCurvedHelix,"beta",isBetaSheet,"FV",forceValidation,"CONTINUE",toContinue
            if toContinue:
                # print "cococococococococococcccccccccccccccccccccccccccccccccccccccccccccccc"
                # print "result",result,menC,piuC
                # print "prima",startFrag,endFrag
                if forceValidation:
                    if result == None and not piuC and ind == len(distCV) - 1:
                        endFrag = ind + step + 1
                        ind += 1
                    else:
                        endFrag = ind + step
                    # print "dopo",startFrag,endFrag
                    distSS[-1] = (indice, "ch")

                    """
                    print "creo frammento ",cont,"modo l"
                    print "==============================0"
                    print len(distCV[startFrag:ind]),len(distSS[startFrag:ind])
                    print distCV[startFrag:ind]
                    print distSS[startFrag:ind]
                    print resIDs[startFrag:endFrag]
                    """
                    diston = distSS[startFrag:ind]

                    st = recognizeFragment(pdb, model, chain, CAatomCoord[startFrag:endFrag],
                                           OatomCoord[startFrag:endFrag], resIDs[startFrag:endFrag],
                                           amn[startFrag:endFrag], distCV[startFrag:ind], distDF[startFrag:ind],
                                           sstype=aggio, distS=diston)
                    listReturn.append(st)
                    # print st
                    # print "//////////"
                    # sys.exit(0)
                    aggio = ""
                    if st["fragLength"] >= 3:
                        startFrag = ind + step
                        endFrag = -1
                        jumpindex = ind + step
                        # print "=0=",startFrag
                    else:
                        startFrag = -1
                        endFrag = -1
                        jumpindex = -1

                isAlphaHelix = False
                isBetaSheet = False
                isCurvedHelix = False
                if not forceValidation:
                    startFrag = -1
                    endFrag = -1
                    jumpindex = -1
                forceValidation = False
                cont += 1
                # print "subframmento fuori ramachandran"
                # print "ind post",ind
                # print "=1=",startFrag,endFrag
                continue

            result = resultL[0]

            if (isAlphaHelix or isCurvedHelix) and result not in ["bs1", "bs2"]:  # and ramachandran dice che e ah
                isCurvedHelix = True
                distSS[-1] = (indice, "ch")
                """
                if isBetaSheet:
                    endFrag = ind+step

                    print "creo frammento ",cont,"modo e"
                    print "==============================0"
                    print len(distCV[startFrag:ind]),len(distSS[startFrag:ind])
                    print distCV[startFrag:ind]
                    print distSS[startFrag:ind]
                    print resIDs[startFrag:endFrag]

                    diston = distSS[startFrag:ind]
                    st = recognizeFragment(pdb, model, chain, CAatomCoord[startFrag:endFrag], OatomCoord[startFrag:endFrag], resIDs[startFrag:endFrag], amn[startFrag:endFrag], distCV[startFrag:ind], distDF[startFrag:ind], sstype="bs", distS=diston)
                    listReturn.append(st)
                    startFrag = ind+step
                    endFrag = -1
                    jumpindex = ind+step
                    isAlphaHelix = False
                    isBetaSheet = False
                    isCurvedHelix = False
                    #print "trovata elica durante una beta sheet"
                """
            elif (isAlphaHelix or isCurvedHelix) and result in ["bs1", "bs2"]:
                ti = ""
                if isCurvedHelix:
                    ti = "ch"
                elif isAlphaHelix:
                    ti = "ah"

                # distSS[-1] = (indice,ti)
                endFrag = ind + step

                """print "creo frammento ",cont,"modo f"
                print "==============================0"
                print len(distCV[startFrag:ind]),len(distSS[startFrag:ind])
                print distCV[startFrag:ind]
                print distSS[startFrag:ind]
                print resIDs[startFrag:endFrag]"""

                diston = distSS[startFrag:ind]

                st = recognizeFragment(pdb, model, chain, CAatomCoord[startFrag:endFrag], OatomCoord[startFrag:endFrag],
                                       resIDs[startFrag:endFrag], amn[startFrag:endFrag], distCV[startFrag:ind],
                                       distDF[startFrag:ind], sstype=ti, distS=diston)
                listReturn.append(st)
                if st["fragLength"] >= 3:
                    startFrag = ind + step
                    endFrag = -1
                    jumpindex = ind + step
                else:
                    startFrag = -1
                    endFrag = -1
                    jumpindex = -1

                isAlphaHelix = False
                isBetaSheet = False
                isCurvedHelix = False
                # print "trovata una beta o un out dentro un elica"
            elif isBetaSheet and result in ["rah1", "rah2", "lah1", "lah2"]:
                endFrag = ind + step
                # print "prima",startFrag,endFrag
                # distSS[-1] = (indice,"ch")
                """print "creo frammento ",cont,"modo g"
                print "==============================0"
                print len(distCV[startFrag:ind]),len(distSS[startFrag:ind])
                print distCV[startFrag:ind]
                print distSS[startFrag:ind]
                print resIDs[startFrag:endFrag]"""
                diston = distSS[startFrag:ind]

                st = recognizeFragment(pdb, model, chain, CAatomCoord[startFrag:endFrag], OatomCoord[startFrag:endFrag],
                                       resIDs[startFrag:endFrag], amn[startFrag:endFrag], distCV[startFrag:ind],
                                       distDF[startFrag:ind], sstype="bs", distS=diston)
                listReturn.append(st)
                if st["fragLength"] >= 3:
                    startFrag = ind + step
                    endFrag = -1
                    jumpindex = ind + step
                else:
                    startFrag = -1
                    endFrag = -1
                    jumpindex = -1

                isAlphaHelix = False
                isBetaSheet = False
                isCurvedHelix = False
                # print "trovata un elica en una beta strand",result,cont,step,window
                # print "dopo",startFrag,endFrag
            elif isBetaSheet and result not in ["rah1", "rah2", "lah1", "lah2"]:
                distSS[-1] = (indice, "bsr")
            elif result in ["bs1", "bs2"]:
                isBetaSheet = True
                distSS[-1] = (indice, "bsr")
            elif result in ["rah1", "rah2", "lah1", "lah2"]:
                isCurvedHelix = True
                distSS[-1] = (indice, "ch")

            if result in ["1gly2", "2gly2", "1gly1", "2gly1", "3gly1", "4gly1", "5gly1", "6gly1", "1pro2", "2pro2",
                          "1pro1", "2pro1", "3pro1", "4pro1"]:
                distSS[-1] = (indice, result)
                # distSS[-1] = (indice,(distSS[-1])[1]+"_"+result)

            if forceValidation:
                endFrag = ind + step
                # print "prima",startFrag,endFrag
                distSS[-1] = (indice, "ch")
                """print "creo frammento ",cont,"modo z"
                print "=====================lklklk=========0"
                print len(distCV[startFrag:ind]),len(distSS[startFrag:ind])
                print distCV[startFrag:ind]
                print distSS[startFrag:ind]
                print resIDs[startFrag:endFrag]"""
                diston = distSS[startFrag:ind]

                st = recognizeFragment(pdb, model, chain, CAatomCoord[startFrag:endFrag], OatomCoord[startFrag:endFrag],
                                       resIDs[startFrag:endFrag], amn[startFrag:endFrag], distCV[startFrag:ind],
                                       distDF[startFrag:ind], sstype=aggio, distS=diston)
                listReturn.append(st)
                aggio = ""
                forceValidation = False
                isAlphaHelix = False
                isBetaSheet = False
                isCurvedHelix = False

                if st["fragLength"] >= 3:
                    startFrag = ind + step
                    endFrag = -1
                    jumpindex = ind + step
                else:
                    startFrag = -1
                    endFrag = -1
                    jumpindex = -1

                    # print "subframmento fuori ramachandran"
                    # print "ind post",ind
        cont += 1

    # print "fuoriiiiii",ind,cont
    if startFrag != -1 and len(distCV[startFrag:]) > 0 and (isCurvedHelix or isAlphaHelix or isBetaSheet):
        tip = ""
        if isCurvedHelix:
            tip = "ch"
        elif isAlphaHelix:
            tip = "ah"
        else:
            tip = "bs"

        """print "creo frammento ",cont,"modo h"
        print "==============================0"
        print len(distCV[startFrag:]),len(distSS[startFrag:])
        print distCV[startFrag:]
        print distSS[startFrag:]
        print resIDs[startFrag:]"""
        diston = distSS[startFrag:]

        st = recognizeFragment(pdb, model, chain, CAatomCoord[startFrag:], OatomCoord[startFrag:], resIDs[startFrag:],
                               amn[startFrag:], distCV[startFrag:], distDF[startFrag:], sstype=tip, distS=diston)
        listReturn.append(st)

    # printSecondaryStructureElements(listReturn)

    h = listReturn
    # refino and joining de las estructuras,
    More = True
    while More:
        More = False
        for a1 in range(len(h)):
            if len((h[a1])["resIdList"]) == 0:
                continue
            for a2 in range(len(h)):
                if a1 == a2 or len((h[a2])["resIdList"]) == 0:
                    continue
                a1S = ((h[a1])["resIdList"])[0]
                a1E = ((h[a1])["resIdList"])[(h[a1])["fragLength"] - 1]
                a2S = ((h[a2])["resIdList"])[0]
                a2E = ((h[a2])["resIdList"])[(h[a2])["fragLength"] - 1]

                a1SN = getResidue(structure, (h[a1])["model"], (h[a1])["chain"], a1S)
                a1EC = getResidue(structure, (h[a1])["model"], (h[a1])["chain"], a1E)
                a2SN = getResidue(structure, (h[a2])["model"], (h[a2])["chain"], a2S)
                a2EC = getResidue(structure, (h[a2])["model"], (h[a2])["chain"], a2E)

                condizio0 = ((h[a1])["model"] == (h[a2])["model"]) and ((h[a1])["chain"] == (h[a2])["chain"])
                condizio1 = checkContinuity(a1EC, a2SN)
                condizio2 = checkContinuity(a2EC, a1SN)

                condizio4 = (h[a1])["fragLength"] >= 3 and (h[a2])["fragLength"] >= 3

                if not (condizio0 and condizio4 and (condizio1 or condizio2)):
                    continue

                condizio3 = ((h[a1])["sstype"] == (h[a2])["sstype"] == "bs") or (
                    (h[a1])["sstype"] == "cbs" and (h[a2])["sstype"] == "bs") or (
                                (h[a1])["sstype"] == "bs" and (h[a2])["sstype"] == "cbs") or (
                                (h[a1])["sstype"] == (h[a2])["sstype"] == "cbs")

                condizio8 = ((h[a1])["sstype"] == (h[a2])["sstype"] == "ah") or (
                    (h[a1])["sstype"] == "ch" and (h[a2])["sstype"] == "ah") or (
                                (h[a1])["sstype"] == "ah" and (h[a2])["sstype"] == "ch") or (
                                (h[a1])["sstype"] == (h[a2])["sstype"] == "ch")

                treshold = 0
                if condizio3:
                    treshold = 30
                elif condizio8:
                    treshold = 35

                mod1cCA = (h[a1])["centroidCA"]
                mod1cO = (h[a1])["centroidO"]
                mod2cCA = (h[a2])["centroidCA"]
                mod2cO = (h[a2])["centroidO"]
                X1 = mod1cCA[0] - mod1cO[0]
                Y1 = mod1cCA[1] - mod1cO[1]
                Z1 = mod1cCA[2] - mod1cO[2]
                X2 = mod2cCA[0] - mod2cO[0]
                Y2 = mod2cCA[1] - mod2cO[1]
                Z2 = mod2cCA[2] - mod2cO[2]

                TetaReal = angle_between([X1, Y1, Z1], [X2, Y2, Z2], [1.0, 1.0, 1.0], signed=False)
                TetaDeg = TetaReal * 57.2957795
                condizio5 = TetaDeg <= treshold

                # print "Possibilita di unire eliche",condizio8,condizio5,h[a1]["resIdList"][0],h[a2]["resIdList"][0]
                if condizio3 and condizio5:
                    tipo = "cbs"  # this is useful for bs
                    # descript = "beta sheet"

                    sstoc = None
                    if condizio1:  # a1--a2
                        sstoc = recognizeFragment((h[a1])["pdbid"], (h[a1])["model"], (h[a1])["chain"],
                                                  (h[a1])["CAatomCoord"] + (h[a2])["CAatomCoord"],
                                                  (h[a1])["OatomCoord"] + (h[a2])["OatomCoord"],
                                                  (h[a1])["resIdList"] + (h[a2])["resIdList"],
                                                  (h[a1])["amnList"] + (h[a2])["amnList"], None, None, sstype=tipo,
                                                  distS=(h[a1])["distSS"] + (h[a2])["distSS"])
                    elif condizio2:  # a2--a1
                        sstoc = recognizeFragment((h[a2])["pdbid"], (h[a2])["model"], (h[a2])["chain"],
                                                  (h[a2])["CAatomCoord"] + (h[a1])["CAatomCoord"],
                                                  (h[a2])["OatomCoord"] + (h[a1])["OatomCoord"],
                                                  (h[a2])["resIdList"] + (h[a1])["resIdList"],
                                                  (h[a2])["amnList"] + (h[a1])["amnList"], None, None, sstype=tipo,
                                                  distS=(h[a2])["distSS"] + (h[a1])["distSS"])

                    h = SystemUtility.multi_delete(h, [a1, a2])
                    h.append(sstoc)
                    More = True
                    break
                elif condizio8 and condizio5:
                    tipo = "ch"
                    sstoc = None
                    if condizio1:  # a1--a2
                        sstoc = recognizeFragment((h[a1])["pdbid"], (h[a1])["model"], (h[a1])["chain"],
                                                  (h[a1])["CAatomCoord"] + (h[a2])["CAatomCoord"],
                                                  (h[a1])["OatomCoord"] + (h[a2])["OatomCoord"],
                                                  (h[a1])["resIdList"] + (h[a2])["resIdList"],
                                                  (h[a1])["amnList"] + (h[a2])["amnList"], None, None, sstype=tipo,
                                                  distS=(h[a1])["distSS"] + (h[a2])["distSS"])
                    elif condizio2:  # a2--a1
                        sstoc = recognizeFragment((h[a2])["pdbid"], (h[a2])["model"], (h[a2])["chain"],
                                                  (h[a2])["CAatomCoord"] + (h[a1])["CAatomCoord"],
                                                  (h[a2])["OatomCoord"] + (h[a1])["OatomCoord"],
                                                  (h[a2])["resIdList"] + (h[a1])["resIdList"],
                                                  (h[a2])["amnList"] + (h[a1])["amnList"], None, None, sstype=tipo,
                                                  distS=(h[a2])["distSS"] + (h[a1])["distSS"])

                    h = SystemUtility.multi_delete(h, [a1, a2])
                    h.append(sstoc)
                    More = True
                    break

            if More:
                break
    return h

@deprecated('Use BORGES_MATRIX.angle_between')
def angle_between(A, B, N, signed=True):
    # ANGLE BETWEEN TWO 3D VECTORS:
    # 1- dot(norm(A),norm(B)) (ANGLES UNSIGNED, PROBLEMS FOR SMALL ANGLES WITH ROUNDINGS)
    # 2- arcos(dot(A,B)/(|A|*|B|))  (ANGLE UNSIGNED, PROBLEMS FOR SMALL ANGLES WITH ROUNDINGS)
    # 3- arctan2(|cross(A,B)|,dot(A,B)) (ANGLE UNSIGNED BUT NOT PROBLEMS OF ROUNDINGS
    #   define a vector NORM ex.: N = [0,0,1]
    #   sign = dot(NORM,cross(A,B))
    #   if sign < 0 then ANGLE measured in 3 should be negative

    CrossX = A[1] * B[2] - A[2] * B[1]
    CrossY = A[2] * B[0] - A[0] * B[2]
    CrossZ = A[0] * B[1] - A[1] * B[0]

    fCross = numpy.sqrt(CrossX * CrossX + CrossY * CrossY + CrossZ * CrossZ)
    scaP2 = (A[0] * B[0]) + (A[1] * B[1]) + (A[2] * B[2])
    Teta_2 = numpy.arctan2(fCross, scaP2)

    if signed:
        sign = (N[0] * CrossX) + (N[1] * CrossY) + (N[2] * CrossZ)
        if sign < 0:
            Teta_2 = -Teta_2

        return Teta_2
    else:
        return Teta_2


def getAtomLineEasy(atom):
    item = atom
    orig_atom_num = item.get_serial_number()
    hetfield, resseq, icode = item.get_parent().get_id()
    segid = item.get_parent().get_segid()
    resname = item.get_parent().get_resname()
    chain_id = item.get_parent().get_parent().get_id()
    element = item.get_name()
    return getAtomLine(item, element, hetfield, segid, orig_atom_num, resname, resseq, icode, chain_id)

#@deprecated('Use Bioinformatics3.get_atom_line')
def getAtomLine(atom, element, hetfield, segid, atom_number, resname, resseq, icode, chain_id, normalize=False,
                bfactorNor=25.00, charge=" "):
    ATOM_FORMAT_STRING = "%s%6i %-4s%c%3s %c%4i%c   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n"

    if hetfield != " ":
        record_type = "HETATM"
    else:
        record_type = "ATOM "

    element = element.strip().upper()
    # print "ELEMENT value was: ",type(element),element
    element = element[0]
    # print "ELEMENT value is: ",type(element),element

    name = atom.get_fullname()
    altloc = atom.get_altloc()
    x, y, z = atom.get_coord()
    occupancy = atom.get_occupancy()
    if not normalize:
        bfactor = atom.get_bfactor()
    else:
        bfactor = bfactorNor
    args = (
        record_type, atom_number, name, altloc, resname, chain_id, resseq, icode, x, y, z, occupancy, bfactor, segid,
        element, charge)
    ala = ATOM_FORMAT_STRING % args
    if record_type == "HETATM":
        clu = ala.split()
        spaziBianchi = 5 - len(clu[1])
        stri = "HETATM"
        for ulu in range(spaziBianchi):
            stri += " "
        stri += clu[1]
        ala = stri + ala[12:]
    return ala

@deprecated('Use Bioinformatics3.get_helix_line')
def getHelixLine(idnumber,idname,restartname,chainstart,restartnumber,resicodestart,resendname,chainend,resendnumber,resicodeend,typehelix,comment,lenhelix):
    HELIX_FORMAT_STRING = "{:<6s} {:>3d} {:>3s} {:>3s} {:1s} {:>4d}{:1s} {:>3s} {:1s} {:>4d}{:1s}{:>2d}{:>30s} {:>5d}"
    return HELIX_FORMAT_STRING.format("HELIX",idnumber,idname,restartname,chainstart,restartnumber,resicodestart,resendname,chainend,resendnumber,resicodeend,typehelix,comment,lenhelix)+"\n"

@deprecated('Use Bioinformatics3.get_sheet_line')
def getSheetLine(idnumber,idnamesheet,nofstrandsinsheet,restartname,chainstart,restartnumber,resicodestart,resendname,chainend,resendnumber,resicodeend,sense):
    SHEET_FORMAT_STRING = "{:<6s} {:>3d} {:>3s}{:>2d} {:>3s} {:1s}{:>4d}{:1s} {:>3s} {:1s}{:>4d}{:1s}{:>2d} {:>4s}{:>3s} {:1s}{:>4s}{:1s} {:>4s}{:>3s} {:1s}{:>4s}{:1s}"
    return SHEET_FORMAT_STRING.format("SHEET",idnumber,idnamesheet,nofstrandsinsheet,restartname,chainstart,restartnumber,resicodestart,resendname,chainend,resendnumber,resicodeend,sense,"","","","","","","","","","")+"\n"


def getMaxNumberOfBetaPacked(listaBeta):
    h = listaBeta

    maxLength = 0
    for i in range(len(h)):
        a = i
        visited = []
        # print "processo il frammento",i
        for q in range(len(h)):
            minDf = numpy.inf
            minIf = -1
            visited.append(a)
            # print "calcolo la ",q,"distanza minima"
            for j in range(len(h)):
                if j not in visited:
                    mod1cCALi = (h[a])["CAatomCoord"]
                    mod2cCALi = (h[j])["CAatomCoord"]
                    dil = numpy.inf
                    for t in mod1cCALi:
                        for z in mod2cCALi:
                            X = t[0] - z[0]
                            Y = t[1] - z[1]
                            Z = t[2] - z[2]
                            di = numpy.sqrt(X * X + Y * Y + Z * Z)
                            if di < dil:
                                dil = di
                    # print "distanza fra",a,"e",j,"is",dil
                    if dil < minDf:  # and i < j:
                        minDf = dil
                        minIf = j
            # print "distanza minima numero",q,"fra",a,"e",minIf,"is",minDf
            if minDf <= 5.5:
                a = minIf
            else:
                break

        # print "per il frammento",i,"il numero massimo di bs packed is",len(visited)
        if len(visited) > maxLength:
            maxLength = len(visited)

    return maxLength


def computeDistancesForFragments(listfrag):
    dicDescriptor = {}
    maxDist = numpy.NINF
    minDist = numpy.inf
    h = listfrag

    for i in range(len(h)):
        if "distances" in (h[i]).keys():
            (h[i])["distances"] = []

    for i in range(len(h)):
        maxDf = numpy.NINF
        minDf = numpy.inf
        minIf = -1
        maxIf = -1
        maxCf = (-1, -1, -1)
        minCf = (-1, -1, -1)
        for j in range(len(h)):
            if j == i:
                continue
            mod1cCA = (h[i])["centroidCA"]
            mod2cCA = (h[j])["centroidCA"]
            X = mod1cCA[0] - mod2cCA[0]
            Y = mod1cCA[1] - mod2cCA[1]
            Z = mod1cCA[2] - mod2cCA[2]
            di = numpy.sqrt(X * X + Y * Y + Z * Z)
            if di > maxDist:
                maxDist = di

            if di < minDist:
                minDist = di

            if di > maxDf:  # and i < j:
                # if j < i and "distances" in h[j] and i == (((h[j])["distances"])[0])[0]:
                #       continue

                maxDf = di
                maxIf = j
                maxCf = (X, Y, Z)

            if di < minDf:  # and i < j:
                # if j < i and "distances" in h[j] and i == (((h[j])["distances"])[1])[0]:
                #       continue

                minDf = di
                minIf = j
                minCf = (X, Y, Z)

        if "distances" not in (h[i]).keys():
            (h[i])["distances"] = []
            # if i != len(h)-1:
            (h[i])["distances"].append([maxIf, maxCf, maxCf])  # (nmFrag,distance,direction)
            (h[i])["distances"].append([minIf, minCf, minCf])  # (nmFrag,distance,direction)
            # else:
            #       (h[i])["distances"] = []
        else:
            # if i != len(h)-1:
            (h[i])["distances"].append([maxIf, maxCf, maxCf])  # (nmFrag,distance,direction)
            (h[i])["distances"].append([minIf, minCf, minCf])  # (nmFrag,distance,direction)
            # else:
            #       (h[i])["distances"] = []

    dicDescriptor["rangeDistances"] = (minDist, maxDist)

    return h, dicDescriptor


def __subsort(listF, structure):
    while len(listF) > 1:
        fra = listF[0]
        ca1x = fra["CAatomCoord"][0][0]
        ca1y = fra["CAatomCoord"][0][1]
        ca1z = fra["CAatomCoord"][0][2]
        ca2x = fra["CAatomCoord"][1][0]
        ca2y = fra["CAatomCoord"][1][1]
        ca2z = fra["CAatomCoord"][1][2]
        ca3x = fra["CAatomCoord"][2][0]
        ca3y = fra["CAatomCoord"][2][1]
        ca3z = fra["CAatomCoord"][2][2]

        ca1 = [(ca1x + ca2x + ca3x) / 3.0, (ca1y + ca2y + ca3y) / 3.0, (ca1z + ca2z + ca3z) / 3.0]

        can1x = fra["CAatomCoord"][-1][0]
        can1y = fra["CAatomCoord"][-1][1]
        can1z = fra["CAatomCoord"][-1][2]
        can2x = fra["CAatomCoord"][-2][0]
        can2y = fra["CAatomCoord"][-2][1]
        can2z = fra["CAatomCoord"][-2][2]
        can3x = fra["CAatomCoord"][-3][0]
        can3y = fra["CAatomCoord"][-3][1]
        can3z = fra["CAatomCoord"][-3][2]

        can = [(can1x + can2x + can3x) / 3.0, (can1y + can2y + can3y) / 3.0, (can1z + can2z + can3z) / 3.0]
        mini = 100000000
        mindi = -100
        nearj = None
        for j in range(1, len(listF)):
            fra2 = listF[j]
            bca1x = fra2["CAatomCoord"][0][0]
            bca1y = fra2["CAatomCoord"][0][1]
            bca1z = fra2["CAatomCoord"][0][2]
            bca2x = fra2["CAatomCoord"][1][0]
            bca2y = fra2["CAatomCoord"][1][1]
            bca2z = fra2["CAatomCoord"][1][2]
            bca3x = fra2["CAatomCoord"][2][0]
            bca3y = fra2["CAatomCoord"][2][1]
            bca3z = fra2["CAatomCoord"][2][2]

            bca1 = [(bca1x + bca2x + bca3x) / 3.0, (bca1y + bca2y + bca3y) / 3.0, (bca1z + bca2z + bca3z) / 3.0]

            bcan1x = fra2["CAatomCoord"][-1][0]
            bcan1y = fra2["CAatomCoord"][-1][1]
            bcan1z = fra2["CAatomCoord"][-1][2]
            bcan2x = fra2["CAatomCoord"][-2][0]
            bcan2y = fra2["CAatomCoord"][-2][1]
            bcan2z = fra2["CAatomCoord"][-2][2]
            bcan3x = fra2["CAatomCoord"][-3][0]
            bcan3y = fra2["CAatomCoord"][-3][1]
            bcan3z = fra2["CAatomCoord"][-3][2]

            bcan = [(bcan1x + bcan2x + bcan3x) / 3.0, (bcan1y + bcan2y + bcan3y) / 3.0,
                    (bcan1z + bcan2z + bcan3z) / 3.0]

            # 1 a---b c---d : a/c
            DX = ca1[0] - bca1[0]
            DY = ca1[1] - bca1[1]
            DZ = ca1[2] - bca1[2]
            d1 = numpy.sqrt(DX * DX + DY * DY + DZ * DZ)
            # 2 a---b c---d : a/d
            DX = ca1[0] - bcan[0]
            DY = ca1[1] - bcan[1]
            DZ = ca1[2] - bcan[2]
            d2 = numpy.sqrt(DX * DX + DY * DY + DZ * DZ)
            # 3 a---b c---d : b/c
            DX = can[0] - bca1[0]
            DY = can[1] - bca1[1]
            DZ = can[2] - bca1[2]
            d3 = numpy.sqrt(DX * DX + DY * DY + DZ * DZ)
            # 4 a---b c---d : b/d
            DX = can[0] - bcan[0]
            DY = can[1] - bcan[1]
            DZ = can[2] - bcan[2]
            d4 = numpy.sqrt(DX * DX + DY * DY + DZ * DZ)

            dis = [d1, d2, d3, d4]
            mind = min(dis)
            type_d = dis.index(mind)

            if mind < mini:
                mini = mind
                mindi = type_d
                nearj = j
        listF[0] = __sublink(listF[0], listF[nearj], structure, typed=mindi)
        del listF[nearj]

    return listF[0]


def __sublink(lisA, lisB, structure, typed=None):
    fra = {}
    if typed == None:
        ca1x = lisA["CAatomCoord"][0][0]
        ca1y = lisA["CAatomCoord"][0][1]
        ca1z = lisA["CAatomCoord"][0][2]
        ca2x = lisA["CAatomCoord"][1][0]
        ca2y = lisA["CAatomCoord"][1][1]
        ca2z = lisA["CAatomCoord"][1][2]
        ca3x = lisA["CAatomCoord"][2][0]
        ca3y = lisA["CAatomCoord"][2][1]
        ca3z = lisA["CAatomCoord"][2][2]

        ca1 = [(ca1x + ca2x + ca3x) / 3.0, (ca1y + ca2y + ca3y) / 3.0, (ca1z + ca2z + ca3z) / 3.0]

        can1x = lisA["CAatomCoord"][-1][0]
        can1y = lisA["CAatomCoord"][-1][1]
        can1z = lisA["CAatomCoord"][-1][2]
        can2x = lisA["CAatomCoord"][-2][0]
        can2y = lisA["CAatomCoord"][-2][1]
        can2z = lisA["CAatomCoord"][-2][2]
        can3x = lisA["CAatomCoord"][-3][0]
        can3y = lisA["CAatomCoord"][-3][1]
        can3z = lisA["CAatomCoord"][-3][2]

        can = [(can1x + can2x + can3x) / 3.0, (can1y + can2y + can3y) / 3.0, (can1z + can2z + can3z) / 3.0]

        bca1x = lisB["CAatomCoord"][0][0]
        bca1y = lisB["CAatomCoord"][0][1]
        bca1z = lisB["CAatomCoord"][0][2]
        bca2x = lisB["CAatomCoord"][1][0]
        bca2y = lisB["CAatomCoord"][1][1]
        bca2z = lisB["CAatomCoord"][1][2]
        bca3x = lisB["CAatomCoord"][2][0]
        bca3y = lisB["CAatomCoord"][2][1]
        bca3z = lisB["CAatomCoord"][2][2]

        bca1 = [(bca1x + bca2x + bca3x) / 3.0, (bca1y + bca2y + bca3y) / 3.0, (bca1z + bca2z + bca3z) / 3.0]

        bcan1x = lisB["CAatomCoord"][-1][0]
        bcan1y = lisB["CAatomCoord"][-1][1]
        bcan1z = lisB["CAatomCoord"][-1][2]
        bcan2x = lisB["CAatomCoord"][-2][0]
        bcan2y = lisB["CAatomCoord"][-2][1]
        bcan2z = lisB["CAatomCoord"][-2][2]
        bcan3x = lisB["CAatomCoord"][-3][0]
        bcan3y = lisB["CAatomCoord"][-3][1]
        bcan3z = lisB["CAatomCoord"][-3][2]

        bcan = [(bcan1x + bcan2x + bcan3x) / 3.0, (bcan1y + bcan2y + bcan3y) / 3.0, (bcan1z + bcan2z + bcan3z) / 3.0]

        # 1 a---b c---d : a/c
        DX = ca1[0] - bca1[0]
        DY = ca1[1] - bca1[1]
        DZ = ca1[2] - bca1[2]
        d1 = numpy.sqrt(DX * DX + DY * DY + DZ * DZ)
        # 2 a---b c---d : a/d
        DX = ca1[0] - bcan[0]
        DY = ca1[1] - bcan[1]
        DZ = ca1[2] - bcan[2]
        d2 = numpy.sqrt(DX * DX + DY * DY + DZ * DZ)
        # 3 a---b c---d : b/c
        DX = can[0] - bca1[0]
        DY = can[1] - bca1[1]
        DZ = can[2] - bca1[2]
        d3 = numpy.sqrt(DX * DX + DY * DY + DZ * DZ)
        # 4 a---b c---d : b/d
        DX = can[0] - bcan[0]
        DY = can[1] - bcan[1]
        DZ = can[2] - bcan[2]
        d4 = numpy.sqrt(DX * DX + DY * DY + DZ * DZ)

        dis = [d1, d2, d3, d4]
        mind = min(dis)
        typed = dis.index(mind)

    if typed == 0:  # a/c
        fra["resIdList"] = lisA["resIdList"][::-1] + lisB["resIdList"]
        fra["CAatomCoord"] = lisA["CAatomCoord"][::-1] + lisB["CAatomCoord"]
    elif typed == 1:  # a/d
        fra["resIdList"] = lisA["resIdList"][::-1] + lisB["resIdList"][::-1]
        fra["CAatomCoord"] = lisA["CAatomCoord"][::-1] + lisB["CAatomCoord"][::-1]
    elif typed == 2:  # b/c
        fra["resIdList"] = lisA["resIdList"] + lisB["resIdList"]
        fra["CAatomCoord"] = lisA["CAatomCoord"] + lisB["CAatomCoord"]
    elif typed == 3:  # b/d
        fra["resIdList"] = lisA["resIdList"] + lisB["resIdList"][::-1]
        fra["CAatomCoord"] = lisA["CAatomCoord"] + lisB["CAatomCoord"][::-1]

    return fra


def getAtomsList(name, pdb):
    f = open(pdb, "r")
    lines = f.readlines()
    f.close()
    list_atoms = []

    for line in lines:
        lispli = line.split()
        if len(lispli) > 0 and lispli[0] in ["ATOM", "HETATM"]:
            list_atoms.append(lispli)

    return list_atoms


def __getAtoms(lisA, structure, onlyCA=False):
    allatoms = []
    for res in lisA["resIdList"]:
        for model in structure.get_list():
            if model.get_id() == res[1]:
                for chain in model.get_list():
                    if chain.get_id() == res[2]:
                        for residue in chain.get_list():
                            if residue.get_id() == res[3]:
                                if not onlyCA and residue.has_id("N"):
                                    allatoms.append(residue["N"])
                                if residue.has_id("CA"):
                                    allatoms.append(residue["CA"])
                                if not onlyCA and residue.has_id("CB"):
                                    allatoms.append(residue["CB"])
                                if not onlyCA and residue.has_id("C"):
                                    allatoms.append(residue["C"])
                                if not onlyCA and residue.has_id("O"):
                                    allatoms.append(residue["O"])
    return allatoms


def sortFragmentListByMinDistances(lisBigSS, structure):
    lips = {}
    for fra in lisBigSS:
        fra["resIdList"] = map(lambda x: (fra["pdbid"], fra["model"], fra["chain"], x), fra["resIdList"])
        if fra["fragLength"] in lips:
            lips[fra["fragLength"]].append(fra)
        else:
            lips[fra["fragLength"]] = []
            lips[fra["fragLength"]].append(fra)

    for key in sorted(lips.keys(), reverse=True):
        listan = lips[key]
        lips[key] = __subsort(listan, structure)

    while len(lips.keys()) > 1:
        listus = sorted(lips.keys(), reverse=True)
        lida = lips[listus[0]]
        lidb = lips[listus[1]]
        lidc = __sublink(lida, lidb, structure)
        lips[listus[0]] = lidc
        del lips[listus[1]]

    allatoms = __getAtoms(lips[lips.keys()[0]], structure)
    newpdb, resn = getPDBFromListOfAtom(allatoms, renumber=True)
    tuplone = getFragmentListFromPDBUsingAllAtoms(cStringIO.StringIO(newpdb), False)
    strucc = tuplone[0]
    lisBig = tuplone[1]
    return lisBig, strucc, resn


def orderFragmentAccordingtopologicalOrder(FragmentList, structure, removeEqualStructure, isModel):
    h = FragmentList
    h, dicDescriptor = computeDistancesForFragments(h)

    # printSecondaryStructureElements(h)
    for i in range(len(h)):
        tg = h[i]
    # print "frag ",i,"-----"
    #       for kk in tg["distances"]:
    #               print kk

    dizzz = {}

    for j in range(len(h)):
        liu = []
        for i in range(len(h)):
            tg = h[i]
            for lup in range(len(tg["distances"])):
                # if lup == 0: #for the ordering i consider only the minimum distance
                #       continue
                kk = (tg["distances"])[lup]
                if kk[0] == j:
                    liu.append(i)
        dizzz[j] = liu

    nuovoOrd = ADT.robust_topological_sort(dizzz)
    # print nuovoOrd

    """h2 = []
    h3 = deepcopy(h)
    cont = 0
    for u in nuovoOrd:
            for k in u:
                    #(h[k])["distances"] = []
                    for s in range(len(h)):
                            for q in range(len((h[s])["distances"])):
                                    elem = ((h[s])["distances"])[q]
                                    if elem[0] == k:
                                            (((h3[s])["distances"])[q])[0] = cont
                    h2.append(h3[k])
                    cont += 1"""

    h2 = []
    for u in nuovoOrd:
        for k in u:
            h2.append(h[k])

    h2, dicDescriptor = computeDistancesForFragments(h2)

    dizzz = {}

    for j in range(len(h2)):
        liu = []
        for i in range(len(h2)):
            tg = h2[i]
            for lup in range(len(tg["distances"])):
                # if lup == 0: #for the ordering i consider only the minimum distance
                #       continue
                kk = (tg["distances"])[lup]
                if kk[0] == j:
                    liu.append(i)
        dizzz[j] = liu

    nuovoOrd = ADT.robust_topological_sort(dizzz)
    # print nuovoOrd

    for i in range(len(h2)):
        tg = h2[i]
    # print "frag ",i,"-----"
    #       for kk in tg["distances"]:
    #               print kk
    return h2, dicDescriptor

@deprecated("Use Bioinformatics3.get_pdb_from_list_of_frags")
def getPDBFormattedAsString(nModel, lista, strucActualPDB, pathBase, dizioConv={}, externalRes=[], useDizioConv=True,
                            normalize=False, bfactorNor=25.0):
    pdbid = str(strucActualPDB.get_id())
    nomeFilefine = pathBase + "/" + pdbid + "_"
    myHea = ADT.Heap()
    consumedResidue = []

    def actionImplemented(ModelT, ChainT, rex, consumedResidue, myHea):
        for model in strucActualPDB.get_list():
            if model.get_id() != ModelT:
                continue
            for chain in model.get_list():
                if chain.get_id() != ChainT:
                    continue
                for residue in chain.get_list():
                    if residue.get_id() != rex:
                        continue

                    """if residue.get_id() == (' ', 186, ' ') and dizioConv == {}:
                            print "residue",residue.get_id()
                            print "residue full id",residue.get_full_id()
                            print "model",model.get_id()
                            print "chain",chain.get_id()
                            print "is not in consumedResidue",residue.get_full_id() not in consumedResidue"""

                    if residue.get_full_id() not in consumedResidue:
                        if residue.has_id("N"):
                            pos = 0
                            myHea.push((model.get_id(), chain.get_id(),
                                        (residue.get_id()[0], residue.get_id()[1], residue.get_id()[2]), pos),
                                       (residue["N"], "N"))
                        if residue.has_id("CA"):
                            pos = 1
                            myHea.push((model.get_id(), chain.get_id(),
                                        (residue.get_id()[0], residue.get_id()[1], residue.get_id()[2]), pos),
                                       (residue["CA"], "CA"))
                        if residue.has_id("CB"):
                            pos = 2
                            myHea.push((model.get_id(), chain.get_id(),
                                        (residue.get_id()[0], residue.get_id()[1], residue.get_id()[2]), pos),
                                       (residue["CB"], "CB"))
                        if residue.has_id("C"):
                            pos = 3
                            myHea.push((model.get_id(), chain.get_id(),
                                        (residue.get_id()[0], residue.get_id()[1], residue.get_id()[2]), pos),
                                       (residue["C"], "C"))
                        if residue.has_id("O"):
                            pos = 4
                            myHea.push((model.get_id(), chain.get_id(),
                                        (residue.get_id()[0], residue.get_id()[1], residue.get_id()[2]), pos),
                                       (residue["O"], "O"))

                        consumedResidue.append(residue.get_full_id())
        return (consumedResidue, myHea)


        # in this way for each residue i will append only the CA atom that is undersored because
        # Biopython gives me as default the atom with major occupancy when i call residue["CA"],
        # moreover i don't worry about the  < 0.5 occupancy exlusion criteria because if the residue
        # it is included in the solution is because his CA atom has an occupancy > 0.5.

    for resi in externalRes:
        (consumedResidue, myHea) = actionImplemented(resi[0], resi[1], resi[2], consumedResidue, myHea)

    for y in range(len(lista)):
        fragment = lista[y]
        for i in range(len(fragment["resIdList"])):
            re = (fragment["resIdList"])[i]
            if i == 0:
                # nomeFilefine += fragment["chain"]+str(re)
                if len(dizioConv.keys()) > 0:
                    nomeFilefine += str((dizioConv[(fragment["chain"], re, "CA")])[1]) + "*" + str(
                        fragment["fragLength"])
                else:
                    nomeFilefine += str(re[1]) + str(re[2])
            if y != (len(lista) - 1) and i == 0:
                nomeFilefine += "_"
            elif y == (len(lista) - 1) and i == 0:
                if nModel != "":
                    nomeFilefine += "_" + nModel

            (consumedResidue, myHea) = actionImplemented(fragment["model"], fragment["chain"], re, consumedResidue,
                                                         myHea)
            # print "uuuuuuuuuuu",fragment["model"],fragment["chain"],re

    # print "fine processo residui delle strutture"

    # for uio in consumedResidue:
    #       print uio.get_id(), uio.get_resname()

    atom_number = 1
    previousChain = ""
    previousResName = ""
    previousResSeq = None
    lastRes = None
    previousIcode = ""
    pdbString = ""
    pdbString += "REMARK TITLE " + nomeFilefine + "\n"
    resiNumbering = 1
    dizioConvRes = {}
    for values, ite in myHea:
        item = ite[0]
        element = ite[1]
        orig_atom_num = item.get_serial_number()
        hetfield, resseq, icode = item.get_parent().get_id()
        segid = item.get_parent().get_segid()
        resname = item.get_parent().get_resname()
        chain_id = item.get_parent().get_parent().get_id()
        if previousResSeq != None:
            resaN = item.get_parent()
            prevResC = lastRes.get_parent()
            if not checkContinuity(prevResC, resaN) and resseq != previousResSeq:
                format_string = "%s%6i %-4s%c%3s %c%4i \n"
                if useDizioConv:
                    arg = ("TER  ", atom_number, ' ', ' ', previousResName, previousChain, resiNumbering)
                    pdbString += (format_string % arg)
                if len(dizioConv.keys()) == 0:
                    resiNumbering += 20  # to break the continuity of the residues
                    atom_number += 20
                    dizioConvRes[(chain_id, (hetfield, resseq, icode), element)] = (atom_number, resiNumbering)

        if previousResSeq != None and resseq != previousResSeq or (resseq == previousResSeq and icode != previousIcode):
            resiNumbering += 1

        if len(dizioConv.keys()) > 0:
            resiNumbering = (dizioConv[(chain_id, (hetfield, resseq, icode), element)])[1]
            atom_number = (dizioConv[(chain_id, (hetfield, resseq, icode), element)])[0]

        if not useDizioConv:
            pdbString += getAtomLine(item, element, hetfield, segid, orig_atom_num, resname, resseq, icode, chain_id)
        else:
            pdbString += getAtomLine(item, element, chr(ord(' ')), segid, atom_number, resname, resiNumbering,
                                     chr(ord(' ')), chain_id, normalize=normalize, bfactorNor=bfactorNor)
        if len(dizioConv.keys()) == 0:
            dizioConvRes[(chain_id, (hetfield, resseq, icode), element)] = (atom_number, resiNumbering)

        atom_number += 1
        previousChain = chain_id
        previousResName = resname
        previousResSeq = resseq
        previousIcode = icode
        lastRes = item
    if previousResSeq != None:
        format_string = "%s%6i %-4s%c%3s %c%4i \n"
        if useDizioConv:
            arg = ("TER  ", atom_number, ' ', ' ', previousResName, previousChain, resiNumbering)
            pdbString += (format_string % arg)
            atom_number += 1
    pdbString += "END\n"

    if len(dizioConv.keys()) == 0:
        return (nomeFilefine, pdbString, dizioConvRes)
    else:
        return (nomeFilefine, pdbString)


def recognizeFragment(pdb, model, chain, CAatomCoord, OatomCoord, resIDs, amn, distCV, distDF, sstype=None, distS=[]):
    if len(distS) > 0:
        if (distS[0])[1] in ["d", "bsr", "ch", "dd"]:
            distS = distS[1:]
            distCV = distCV[1:]
            distDF = distDF[1:]
            CAatomCoord = CAatomCoord[1:]
            OatomCoord = OatomCoord[1:]
            resIDs = resIDs[1:]
            amn = amn[1:]

    if len(distS) > 0:
        if (distS[-1])[1] in ["d", "bsr", "ch", "dd"]:
            distS = distS[:-1]
            distCV = distCV[:-1]
            distDF = distDF[:-1]
            CAatomCoord = CAatomCoord[:-1]
            OatomCoord = OatomCoord[:-1]
            resIDs = resIDs[:-1]
            amn = amn[:-1]

    dizio = {}
    dizio["fragLength"] = len(resIDs)
    dizio["pdbid"] = pdb
    if not isinstance(model, int):
        dizio["model"] = model.get_id()
    else:
        dizio["model"] = model

    if not isinstance(chain, str):
        dizio["chain"] = chain.get_id()
    else:
        dizio["chain"] = chain

    dizio["resIdList"] = resIDs
    dizio["amnList"] = amn
    dizio["CAatomCoord"] = CAatomCoord
    dizio["OatomCoord"] = OatomCoord

    if len(distS) == 0 and distCV != None and len(distCV) == 0:
        dizio["sstype"] = "nothing"
        dizio["ssDescription"] = "nothing"
        return dizio

    if distCV == None or distDF == None:
        # print "distribuzioni CVs non calcolate per il frammento"
        distCV = []
        distDF = []
        nS = dizio["fragLength"] - SUFRAGLENGTH + 1
        for plo in range(nS):
            # print "plo is",plo
            xca = 0.0
            yca = 0.0
            zca = 0.0
            xo = 0.0
            yo = 0.0
            zo = 0.0
            for qlo in range(SUFRAGLENGTH):
                # print "\tqlo is",qlo
                xca += CAatomCoord[plo + qlo][0]
                yca += CAatomCoord[plo + qlo][1]
                zca += CAatomCoord[plo + qlo][2]
                xo += OatomCoord[plo + qlo][0]
                yo += OatomCoord[plo + qlo][1]
                zo += OatomCoord[plo + qlo][2]
            xca /= SUFRAGLENGTH
            yca /= SUFRAGLENGTH
            zca /= SUFRAGLENGTH
            xo /= SUFRAGLENGTH
            yo /= SUFRAGLENGTH
            zo /= SUFRAGLENGTH

            XH = xca - xo
            YH = yca - yo
            ZH = zca - zo
            cv = numpy.sqrt(XH * XH + YH * YH + ZH * ZH)

            distCV.append((plo, cv))

            if plo != 0:
                distDF.append(((plo - 1, plo), numpy.abs((distCV[-1])[1] - (distCV[-2])[1])))

    dizio["distCV"] = distCV
    dizio["distDF"] = distDF

    seq = []
    for t in dizio["amnList"]:
        seq.append(AADICMAP[t])
    dizio["sequence"] = "".join(seq)

    # compute centroid CA for the fragment
    Xca = 0.0
    Yca = 0.0
    Zca = 0.0
    for i in range(len(CAatomCoord)):
        Xca += CAatomCoord[i][0]
        Yca += CAatomCoord[i][1]
        Zca += CAatomCoord[i][2]

    if len(CAatomCoord) > 0:
        Xca /= len(CAatomCoord)
        Yca /= len(CAatomCoord)
        Zca /= len(CAatomCoord)

    dizio["centroidCA"] = (Xca, Yca, Zca)

    # compute centroid O for the fragment
    Xo = 0.0
    Yo = 0.0
    Zo = 0.0
    for i in range(len(OatomCoord)):
        Xo += OatomCoord[i][0]
        Yo += OatomCoord[i][1]
        Zo += OatomCoord[i][2]

    if len(OatomCoord) > 0:
        Xo /= len(OatomCoord)
        Yo /= len(OatomCoord)
        Zo /= len(OatomCoord)

    dizio["centroidO"] = (Xo, Yo, Zo)

    # compute CV for the fragment
    XH = Xca - Xo
    YH = Yca - Yo
    ZH = Zca - Zo

    dizio["vecLength"] = numpy.sqrt(XH * XH + YH * YH + ZH * ZH)

    if sstype != None and len(distS) == len(distCV):
        if dizio["fragLength"] > 2 and sstype == "ch":
            if (distS[0])[1] == "ch":
                distS[0] = ((distS[0])[0], "dd")

            # if (distS[1])[1] == "ch":
            #        distS[1] = ((distS[1])[0],"dd")

            if (distS[-1])[1] == "ch":
                distS[-1] = ((distS[-1])[0], "dd")

            # if (distS[-2])[1] == "ch":
            #        distS[-2] = ((distS[-2])[0],"dd")

            sstype = "ah"
            for ele in distS:
                ind = ele[0]
                tip = ele[1]
                if tip == "ch":
                    sstype = "ch"
                    break

        dizio["sstype"] = sstype
        dizio["distSS"] = distS
        # print "le due lunghezze sono uguali"
        # print distS
    elif len(distCV) > 0:
        # print "ricalcolo le distSS",len(distS),len(distCV)
        meanTAH = 2.2
        meanTBS = 1.4
        st1AH = 0.10
        st2AH = 0.15
        st1BS = 0.10
        st2BS = 0.15
        outsideAlpha = 0.35
        outsideBeta = 0.30

        distSS = []

        isAlphaHelix = False
        isBetaSheet = False
        isCurvedHelix = False
        isCurvedBeta = False
        isNothing = False

        for ind in range(len(distCV)):
            (indice, cvv) = distCV[ind]

            if ind < len(distS):
                distSS.append((indice, (distS[ind])[1]))
                continue

            if numpy.abs(meanTAH - cvv) <= st1AH:
                distSS.append((indice, "ah"))
                isAlphaHelix = True
                if isBetaSheet or isCurvedBeta:
                    isNothing = True
            elif numpy.abs(meanTBS - cvv) <= st1BS:
                distSS.append((indice, "bs"))
                isBetaSheet = True
                if isAlphaHelix or isCurvedHelix:
                    isNothing = True
            elif numpy.abs(meanTAH - cvv) <= st2AH:
                distSS.append((indice, "ahd"))
                isAlphaHelix = True
                if isBetaSheet or isCurvedBeta:
                    isNothing = True
            elif numpy.abs(meanTBS - cvv) <= st2BS:
                distSS.append((indice, "bsd"))
                isBetaSheet = True
                if isAlphaHelix or isCurvedHelix:
                    isNothing = True
            else:
                distSS.append((indice, "d"))
                if isAlphaHelix:
                    isCurvedHelix = True
                    if isBetaSheet or isCurvedBeta:
                        isNothing = True
                elif isBetaSheet:
                    isCurvedBeta = True
                    if isAlphaHelix or isCurvedHelix:
                        isNothing = True

        dizio["distSS"] = distSS

        if isNothing:
            dizio["sstype"] = "nothing"
        elif isCurvedHelix:
            dizio["sstype"] = "ch"
        elif isAlphaHelix:
            dizio["sstype"] = "ah"
        elif isCurvedBeta:
            dizio["sstype"] = "cbs"
        elif isBetaSheet:
            dizio["sstype"] = "bs"
        else:
            dizio["sstype"] = "nothing"

        if sstype != None:
            dizio["sstype"] = sstype

    if dizio["sstype"] == "nothing":
        dizio["ssDescription"] = "nothing"
    elif dizio["sstype"] == "ch":
        dizio["ssDescription"] = "curved helix"
    elif dizio["sstype"] == "ah":
        dizio["ssDescription"] = "alpha helix"
    elif dizio["sstype"] == "cbs":
        dizio["ssDescription"] = "curved beta strand"
    elif dizio["sstype"] == "bs":
        dizio["ssDescription"] = "beta strand"

    return dizio


def changeChain(pdb, chain, atom_list=["ATOM  ", "ANISOU", "HETATM", "TER   "]):
    allpdb = pdb.splitlines()
    out = ""
    for line in allpdb:
        # only look at records indicated by atom_list
        if line[0:6] not in atom_list:
            if not line.startswith("END"):
                out += line + "\n"
            continue

        # Grab only residues belonging to chain
        out += line[:21] + chain + line[22:] + "\n"
    return out


def filterModelsByCoordinates(path_folder):
    """ Check a folder of pdbs, if they are identical in coordinates, remove the copies and leave one representative.

    :param path_folder:
    :type path_folder:
    :return:
    :rtype:
    """
    # NOTE CM: this could be improved a lot by using something faster and safer
    redundant = []
    complete_list = os.listdir(path_folder)
    dict_coord = {}
    # print "len(complete_list)",len(complete_list)
    # print "len(set(complete_list))",len(set(complete_list))
    for __index, name in enumerate(complete_list):
        parser = PDBParser()
        structure = parser.get_structure(name[:-4], os.path.join(path_folder, name))
        dict_coord[name] = sorted([list(a.get_coord()) for a in Selection.unfold_entities(structure, 'A')],
                                  key=lambda x: (x[0], x[1], x[2]))
    # Now we can start to compare
    for i, name1 in enumerate(complete_list):
        coord1 = dict_coord[name1]
        for j, name2 in enumerate(complete_list):
            if j <= i:
                continue
            coord2 = dict_coord[name2]
            if len(coord1) != len(coord2):
                continue
            if all([coord1[k] == coord2[k] for k in range(len(coord1))]):
                redundant.append(name2)
    # print "len(redundant)",len(set(redundant))
    for __index, redundant_model in enumerate(set(redundant)):
        os.remove(os.path.join(path_folder, redundant_model))


def findSecondaryStructuresContainingFragment(fragment, lisBigSS, DicParameters):
    dizS = {}
    nExceedResidues = DicParameters["exceedResidues"]

    for u in range(len(lisBigSS)):
        item = lisBigSS[u]
        visit = False
        if fragment["sstype"] == "ah" and (item["sstype"] == "ah" or item["sstype"] == "ch"):
            visit = True
        elif fragment["sstype"] == "bs" and (item["sstype"] == "bs" or item["sstype"] == "cbs"):
            visit = True
        elif fragment["sstype"] == item["sstype"]:
            visit = True
        else:
            visit = False

        # NOTE: Contiguity is now checked by C-N distances, but this method find subfragments checking the residue numbers bundaries
        # There is no way to directly change this method (that is not used anymore by the way). Just take note of this consideration.
        if visit and fragment["pdbid"] == item["pdbid"] and fragment["model"] == item["model"] and fragment["chain"] == \
                item["chain"] and (((fragment["resIdList"])[0])[1] > ((item["resIdList"])[0])[1] or (
                        ((fragment["resIdList"])[0])[1] == ((item["resIdList"])[0])[1] and ord(
                    ((fragment["resIdList"])[0])[2]) >= ord(((item["resIdList"])[0])[2]))) and (
                        ((fragment["resIdList"])[fragment["fragLength"] - 1])[1] <
                        ((item["resIdList"])[item["fragLength"] - 1])[1] or (
                                ((fragment["resIdList"])[fragment["fragLength"] - 1])[1] ==
                                ((item["resIdList"])[item["fragLength"] - 1])[1] and ord(
                            ((fragment["resIdList"])[fragment["fragLength"] - 1])[2]) <= ord(
                            ((item["resIdList"])[item["fragLength"] - 1])[2]))):
            # print "frammento contenuto in una superstruttura"

            return {u: [1]}

        if visit and fragment["pdbid"] == item["pdbid"] and fragment["model"] == item["model"] and fragment["chain"] == \
                item["chain"]:
            for i in range(len(fragment["resIdList"])):
                residue = (fragment["resIdList"])[i]
                # print "couldBeEverywhere",couldBeEverywhere
                # if (' ',72,' ') in fragment["resIdList"]:
                #       print couldBeEverywhere,i,u, lastIndexSS, dizS
                if residue in item["resIdList"]:
                    if u in dizS.keys():
                        (dizS[u])[0] += 1
                        (dizS[u]).append(residue)
                    else:
                        dizS[u] = [1, residue]

    for ki in range(len(fragment["resIdList"])):
        residue = (fragment["resIdList"])[ki]
        # print "residuo analizzato",residue
        trovato = False
        for pl in dizS.keys():
            if pl == "outs":
                continue
            listaRes = (dizS[pl])[1:]
            # print "lista",pl
            # print listaRes
            if residue in listaRes:
                trovato = True
                break
        if not trovato:
            # print "non trovato",residue
            # print "aggiungo ad outs"
            if "outs" not in dizS.keys():
                dizS["outs"] = [1, residue]
            else:
                (dizS["outs"])[0] += 1
                (dizS["outs"]).append(residue)

    couldBeEverywhere = False

    if dizS.has_key("outs") and dizS["outs"][0] in range(nExceedResidues):
        couldBeEverywhere = True
    # elif ki in range(fragment["fragLength"]-nExceedResidues,fragment["fragLength"]):
    #     couldBeEverywhere = True
    elif not dizS.has_key("outs"):
        couldBeEverywhere = True
    else:
        couldBeEverywhere = False

    # print dizS, couldBeEverywhere
    if not couldBeEverywhere and (len(dizS.keys()) > 1 or dizS.has_key("outs")):
        return {}
    else:
        # print "frammento contenuto in una superstruttura"
        return dizS


def getPhiPsiList(listResidues):
    """Return the list of phi/psi dihedral angles."""
    ppl = []
    lng = len(listResidues)
    for i in range(0, lng):
        res = listResidues[i]
        try:
            n = res['N'].get_vector()
            ca = res['CA'].get_vector()
            c = res['C'].get_vector()
        except:
            # print "Some atoms are missing"
            # print " Phi/Psi cannot be calculated for this residue"
            ppl.append((None, None))
            res.xtra["PHI"] = None
            res.xtra["PSI"] = None
            continue
        # Phi
        if i > 0:
            rp = listResidues[i - 1]
            try:
                cp = rp['C'].get_vector()
                phi = calc_dihedral(cp, n, ca, c)
                phi = phi * (180 / numpy.pi)
            except:
                phi = None
        else:
            # No phi for residue 0!
            phi = None
        # Psi
        if i < (lng - 1):
            rn = listResidues[i + 1]
            try:
                nn = rn['N'].get_vector()
                psi = calc_dihedral(n, ca, c, nn)
                psi = psi * (180 / numpy.pi)
            except:
                psi = None
        else:
            # No psi for last residue!
            psi = None
        ppl.append((phi, psi))
        # Add Phi/Psi to xtra dict of residue
        res.xtra["PHI"] = phi
        res.xtra["PSI"] = psi
    return ppl


def getResidueRamachandranStructure(phi, psi, residue):
    bs1Area = [(-180, 180), (-62.5, 180), (-62.5, 172.5), (-57.5, 172.5), (-57.5, 167.5), (-52.5, 167.5),
               (-52.5, 157.5), (-47.5, 157.5), (-47.5, 147.5), (-42.5, 147.5), (-42.5, 137.5), (-37.5, 137.5),
               (-37.5, 122.5), (-42.5, 122.5), (-42.5, 117.5), (-47.5, 117.5), (-47.5, 112.5), (-57.5, 112.5),
               (-57.5, 107.5), (-62.5, 107.5), (-62.5, 102.5), (-67.5, 102.5), (-67.5, 97.5), (-72.5, 97.5),
               (-72.5, 62.5), (-77.5, 62.5), (-77.5, 52.5), (-87.5, 52.5), (-87.5, 47.5), (-92.5, 47.5), (-92.5, 52.5),
               (-97.5, 52.5), (-97.5, 67.5), (-102.5, 67.5), (-102.5, 77.5), (-107.5, 77.5), (-107.5, 82.5),
               (-112.5, 82.5), (-112.5, 72.5), (-117.5, 72.5), (-117.5, 62.5), (-122.5, 62.5), (-122.5, 52.5),
               (-127.5, 52.5), (-127.5, 47.5), (-137.5, 47.5), (-137.5, 52.5), (-142.5, 52.5), (-142.5, 57.5),
               (-147.5, 57.5), (-147.5, 67.5), (-152.5, 67.5), (-152.5, 77.5), (-147.5, 77.5), (-147.5, 87.5),
               (-152.5, 87.5), (-152.5, 97.5), (-157.5, 97.5), (-157.5, 112.5), (-162.5, 112.5), (-162.5, 122.5),
               (-167.5, 122.5), (-167.5, 132.5), (-172.5, 132.5), (-172.5, 142.5), (-180, 142.5), (-180, 180)]
    bs2Area = [(-180, 180), (-42.5, 180), (-42.5, 172.5), (-42.5, 172.5), (-37.5, 172.5), (-37.5, 167.5),
               (-32.5, 167.5), (-32.5, 157.5), (-27.5, 157.5), (-27.5, 147.5), (-22.5, 147.5), (-22.5, 127.5),
               (-17.5, 127.5), (-17.5, 112.5), (-22.5, 112.5), (-22.5, 107.5), (-27.5, 107.5), (-27.5, 102.5),
               (-32.5, 102.5), (-32.5, 97.5), (-47.5, 97.5), (-47.5, 92.5), (-52.5, 92.5), (-52.5, 72.5), (-57.5, 72.5),
               (-57.5, 52.5), (-172.5, 52.5), (-177.5, 52.5), (-177.5, 77.5), (-180, 77.5), (-180, 180)]
    rah2Area = [(-57.5, 52.5), (-57.5, 42.5), (-62.5, 42.5), (-62.5, 27.5), (-57.5, 27.5), (-57.5, 22.5), (-52.5, 22.5),
                (-52.5, 12.5), (-47.5, 12.5), (-47.5, 7.5), (-42.5, 7.5), (-42.5, 2.5), (-37.5, 2.5), (-37.5, -7.5),
                (-32.5, -7.5), (-32.5, -12.5), (-27.5, -12.5), (-27.5, -27.5), (-22.5, -27.5), (-22.5, -47.5),
                (-17.5, -47.5), (-17.5, -67.5), (-22.5, -67.5), (-22.5, -77.5), (-27.5, -77.5), (-27.5, -82.5),
                (-47.5, -82.5), (-47.5, -87.5), (-77.5, -87.5), (-77.5, -92.5), (-87.5, -92.5), (-87.5, -112.5),
                (-92.5, -112.5), (-92.5, -122.5), (-97.5, -122.5), (-97.5, -137.5), (-147.5, -137.5), (-147.5, -132.5),
                (-142.5, -132.5), (-142.5, -127.5), (-147.5, -127.5), (-147.5, -97.5), (-152.5, -97.5), (-152.5, -92.5),
                (-157.5, -92.5), (-157.5, -82.5), (-162.5, -82.5), (-162.5, -52.5), (-157.5, -52.5), (-157.5, -37.5),
                (-162.5, -37.5), (-162.5, -7.5), (-167.5, -7.5), (-167.5, 32.5), (-172.5, 32.5), (-172.5, 52.5),
                (-57.5, 52.5)]
    rah1Area = [(-127.5, 47.5), (-112.5, 47.5), (-112.5, 42.5), (-102.5, 42.5), (-102.5, 37.5), (-92.5, 37.5),
                (-92.5, 32.5), (-87.5, 32.5), (-87.5, 22.5), (-82.5, 22.5), (-82.5, 17.5), (-77.5, 17.5), (-77.5, 12.5),
                (-67.5, 12.5), (-67.5, 7.5), (-62.5, 7.5), (-62.5, 2.5), (-57.5, 2.5), (-57.5, -7.5), (-52.5, -7.5),
                (-52.5, -12.5), (-47.5, -12.5), (-47.5, -22.5), (-42.5, -22.5), (-42.5, -32.5), (-37.5, -32.5),
                (-37.5, -62.5), (-42.5, -62.5), (-42.5, -67.5), (-77.5, -67.5), (-77.5, -62.5), (-117.5, -62.5),
                (-117.5, -57.5), (-122.5, -57.5), (-122.5, -47.5), (-127.5, -47.5), (-127.5, -37.5), (-132.5, -37.5),
                (-132.5, -17.5), (-137.5, -17.5), (-137.5, 2.5), (-142.5, 2.5), (-142.5, 32.5), (-137.5, 32.5),
                (-137.5, 47.5), (-127.5, 47.5)]
    # in basso a sinistra
    other1PossibleArea1 = [(-177.5, -180), (-177.5, -177.5), (-172.5, -177.5), (-172.5, -172.5), (-167.5, -172.5),
                           (-167.5, -167.5), (-127.5, -167.5), (-127.5, -172.5), (-97.5, -172.5), (-97.5, -167.5),
                           (-77.5, -167.5), (-77.5, -172.5), (-72.5, -172.5), (-72.5, -177.5), (-67.5, -177.5),
                           (-67.5, -180), (-177.5, -180)]
    # in basso a sinistra
    other1PossibleArea2 = [(-97.5, -137.5), (-92.5, -137.5), (-92.5, -142.5), (-82.5, -142.5), (-82.5, -147.5),
                           (-72.5, -147.5), (-72.5, -152.5), (-67.5, -152.5), (-67.5, -157.5), (-62.5, -157.5),
                           (-62.5, -162.5), (-57.5, -162.5), (-57.5, -167.5), (-52.5, -167.5), (-52.5, -172.5),
                           (-47.5, -172.5), (-47.5, -177.5), (-42.5, -177.5), (-42.5, -180), (-180, -180),
                           (-180, -147.5), (-97.5, -137.5), (-92.5, -137.5), (-92.5, -142.5), (-82.5, -142.5),
                           (-82.5, -147.5), (-72.5, -147.5), (-72.5, -152.5), (-67.5, -152.5), (-67.5, -157.5),
                           (-62.5, -157.5), (-62.5, -162.5), (-57.5, -162.5), (-57.5, -167.5), (-52.5, -167.5),
                           (-52.5, -172.5), (-47.5, -172.5), (-47.5, -177.5), (-42.5, -177.5), (-42.5, -180),
                           (-180, -147.5), (-177.5, -147.5), (-167.5, -147.5), (-167.5, -142.5), (-157.5, -142.5),
                           (-157.5, -137.5), (-147.5, -137.5), (-97.5, -137.5)]
    # in basso al centro
    other2PossibleArea2 = [(72.5, -102.5), (72.5, -112.5), (77.5, -112.5), (77.5, -157.5), (72.5, -157.5), (72.5, -180),
                           (57.5, -180), (57.5, -167.5), (52.5, -167.5), (52.5, -162.5), (47.5, -162.5), (47.5, -157.5),
                           (42.5, -157.5), (42.5, -152.5), (37.5, -152.5), (37.5, -142.5), (32.5, -142.5),
                           (32.5, -107.5), (37.5, -107.5), (37.5, -102.5), (42.5, -102.5), (42.5, -97.5), (52.5, -97.5),
                           (52.5, -92.5), (62.5, -92.5), (62.5, -97.5), (67.5, -97.5), (67.5, -102.5), (72.5, -102.5)]
    # in alto al centro
    other3PossibleArea2 = [(77.5, 180), (77.5, 162.5), (82.5, 162.5), (82.5, 147.5), (72.5, 147.5), (72.5, 157.5),
                           (67.5, 157.5), (67.5, 167.5), (62.5, 167.5), (62.5, 180), (77.5, 180)]
    # in alto a destra
    other4PossibleArea2 = [(162.5, 180), (162.5, 147.5), (167.5, 147.5), (167.5, 132.5), (172.5, 132.5), (172.5, 117.5),
                           (177.5, 117.5), (177.5, 77.5), (180, 77.5), (180, 180), (162.5, 180)]
    # in basso a destra
    other5PossibleArea2 = [(162.5, -180), (162.5, -177.5), (167.5, -177.5), (167.5, -167.5), (172.5, -167.5),
                           (172.5, -157.5), (177.5, -157.5), (177.5, -147.5), (180, -147.5), (180, -180), (162.5, -180)]
    lah1Area = [(57.5, 67.5), (57.5, 62.5), (62.5, 62.5), (62.5, 57.5), (67.5, 57.5), (67.5, 47.5), (72.5, 47.5),
                (72.5, 32.5), (77.5, 32.5), (77.5, 2.5), (62.5, 2.5), (62.5, 7.5), (57.5, 7.5), (57.5, 12.5),
                (52.5, 12.5), (52.5, 22.5), (47.5, 22.5), (47.5, 27.5), (42.5, 27.5), (42.5, 37.5), (37.5, 37.5),
                (37.5, 62.5), (42.5, 62.5), (42.5, 67.5), (57.5, 67.5)]
    lah2Area = [(82.5, 57.5), (87.5, 57.5), (87.5, 42.5), (92.5, 42.5), (92.5, 22.5), (97.5, 22.5), (97.5, -17.5),
                (92.5, -17.5), (92.5, -22.5), (87.5, -22.5), (87.5, -27.5), (82.5, -27.5), (82.5, -37.5), (87.5, -37.5),
                (87.5, -47.5), (92.5, -47.5), (92.5, -57.5), (87.5, -57.5), (87.5, -67.5), (82.5, -67.5), (82.5, -72.5),
                (77.5, -72.5), (77.5, -77.5), (62.5, -77.5), (62.5, -72.5), (57.5, -72.5), (57.5, -67.5), (52.5, -67.5),
                (52.5, -37.5), (57.5, -37.5), (57.5, -27.5), (62.5, -27.5), (62.5, -22.5), (57.5, -22.5), (57.5, -12.5),
                (52.5, -12.5), (52.5, -7.5), (47.5, -7.5), (47.5, -2.5), (42.5, -2.5), (42.5, 2.5), (37.5, 2.5),
                (37.5, 12.5), (32.5, 12.5), (32.5, 22.5), (27.5, 22.5), (27.5, 32.5), (22.5, 32.5), (22.5, 47.5),
                (17.5, 47.5), (17.5, 67.5), (22.5, 67.5), (22.5, 77.5), (27.5, 77.5), (27.5, 82.5), (32.5, 82.5),
                (32.5, 87.5), (47.5, 87.5), (47.5, 92.5), (67.5, 92.5), (67.5, 87.5), (72.5, 87.5), (72.5, 82.5),
                (77.5, 82.5), (77.5, 77.5), (82.5, 77.5), (82.5, 57.5)]

    # glycina in alto a sinistra
    gly1Area1 = [(-180.0, 180.0), (-180.0, 147.5), (-172.5, 147.5), (-172.5, 142.5), (-162.5, 142.5), (-162.5, 137.5),
                 (-157.5, 137.5), (-157.5, 132.5), (-137.5, 132.5), (-137.5, 127.5), (-107.5, 127.5), (-107.5, 122.5),
                 (-82.5, 122.5),
                 (-82.5, 117.5), (-77.5, 117.5), (-77.5, 112.5), (-52.5, 112.5), (-52.5, 117.5), (-47.5, 117.5),
                 (-47.5, 122.5), (-42.5, 122.5), (-42.5, 142.5), (-47.5, 142.5), (-47.5, 152.5), (-52.5, 152.5),
                 (-52.5, 162.5), (-57.5, 162.5), (-57.5, 180.0),
                 (-180.0, 180.0)]
    # glycina centro sinistra
    gly2Area1 = [(-117.5, 37.5), (-117.5, 32.5), (-122.5, 32.5), (-122.5, 27.5), (-127.5, 27.5), (-127.5, 22.5),
                 (-132.5, 22.5), (-132.5, 17.5), (-137.5, 17.5), (-137.5, 7.5), (-132.5, 7.5), (-132.5, 2.5),
                 (-127.5, 2.5), (-127.5, -7.5), (-122.5, -7.5), (-122.5, -17.5), (-117.5, -17.5), (-117.5, -22.5),
                 (-112.5, -22.5), (-112.5, -27.5), (-102.5, -27.5), (-102.5, -32.5), (-97.5, -32.5), (-97.5, -37.5),
                 (-92.5, -37.5), (-92.5, -42.5), (-87.5, -42.5), (-87.5, -47.5), (-82.5, -47.5),
                 (-82.5, -52.5), (-77.5, -52.5), (-77.5, -57.5), (-72.5, -57.5), (-72.5, -62.5), (-42.5, -62.5),
                 (-42.5, -57.5), (-37.5, -57.5), (-37.5, -42.5), (-42.5, -42.5), (-42.5, -27.5), (-47.5, -27.5),
                 (-47.5, -17.5), (-52.5, -17.5), (-52.5, -7.5), (-57.5, -7.5), (-57.5, 2.5), (-62.5, 2.5), (-62.5, 7.5),
                 (-67.5, 7.5), (-67.5, 12.5), (-72.5, 12.5), (-72.5, 17.5), (-77.5, 17.5), (-77.5, 27.5), (-82.5, 27.5),
                 (-82.5, 32.5), (-87.5, 32.5), (-87.5, 37.5), (-117.5, 37.5)]
    # glycina basso sinistra
    gly3Area1 = [(-180.0, -180.0), (-180.0, -147.5), (-162.5, -147.5), (-162.5, -152.5), (-152.5, -152.5),
                 (-152.5, -147.5), (-147.5, -147.5), (-147.5, -152.5), (-132.5, -152.5), (-132.5, -147.5),
                 (-127.5, -147.5), (-127.5, -142.5), (-122.5, -142.5), (-122.5, -137.5), (-117.5, -137.5),
                 (-117.5, -132.5), (-112.5, -132.5), (-112.5, -127.5), (-107.5, -127.5), (-107.5, -122.5),
                 (-92.5, -122.5), (-92.5, -132.5), (-87.5, -132.5), (-87.5, -137.5), (-82.5, -137.5), (-82.5, -142.5),
                 (-77.5, -142.5), (-77.5, -152.5), (-72.5, -152.5), (-72.5, -162.5), (-67.5, -162.5), (-67.5, -172.5),
                 (-62.5, -172.5), (-62.5, -177.5), (-57.5, -177.5), (-57.5, -180.0), (-180.0, -180.0)]
    # glycina alto destra
    gly4Area1 = [(180.0, 180.0), (62.5, 180.0), (62.5, 172.5), (67.5, 172.5), (67.5, 162.5), (72.5, 162.5),
                 (72.5, 152.5), (77.5, 152.5), (77.5, 142.5), (82.5, 142.5), (82.5, 137.5), (87.5, 137.5),
                 (87.5, 132.5), (92.5, 132.5), (92.5, 122.5), (107.5, 122.5), (107.5, 127.5), (112.5, 127.5),
                 (112.5, 132.5), (117.5, 132.5), (117.5, 137.5), (122.5, 137.5), (122.5, 142.5), (127.5, 142.5),
                 (127.5, 147.5), (132.5, 147.5), (132.5, 152.5), (147.5, 152.5), (147.5, 147.5), (152.5, 147.5),
                 (152.5, 152.5), (162.5, 152.5), (162.5, 147.5), (180.0, 147.5), (180.0, 180.0)]
    # glycina centro destra
    gly5Area1 = [(42.5, 62.5), (42.5, 57.5), (37.5, 57.5), (37.5, 42.5), (42.5, 42.5), (42.5, 27.5), (47.5, 27.5),
                 (47.5, 17.5), (52.5, 17.5), (52.5, 7.5), (57.5, 7.5), (57.5, -2.5), (62.5, -2.5), (62.5, -7.5),
                 (67.5, -7.5), (67.5, -12.5), (72.5, -12.5), (72.5, -17.5), (77.5, -17.5), (77.5, -27.5), (82.5, -27.5),
                 (82.5, -32.5), (87.5, -32.5), (87.5, -37.5), (117.5, -37.5), (117.5, -32.5), (122.5, -32.5),
                 (122.5, -27.5), (127.5, -27.5), (127.5, -22.5), (132.5, -22.5),
                 (132.5, -17.5), (37.5, -17.5), (137.5, -7.5), (132.5, -7.5), (132.5, -2.5), (127.5, -2.5),
                 (127.5, 7.5), (122.5, 7.5), (122.5, 17.5), (117.5, 17.5), (117.5, 22.5), (112.5, 22.5), (112.5, 27.5),
                 (102.5, 27.5), (102.5, 32.5), (97.5, 32.5),
                 (97.5, 37.5), (92.5, 37.5), (92.5, 42.5), (87.5, 42.5), (87.5, 47.5), (82.5, 47.5), (82.5, 52.5),
                 (77.5, 52.5), (77.5, 57.5), (72.5, 57.5), (72.5, 62.5), (42.5, 62.5)]
    # glycina basso centro
    gly6Area1 = [(180.0, -180.0), (57.5, -180.0), (57.5, -162.5), (52.5, -162.5), (52.5, -152.5), (47.5, -152.5),
                 (47.5, -142.5), (42.5, -142.5), (42.5, -122.5), (47.5, -122.5), (47.5, -117.5), (52.5, -117.5),
                 (52.5, -112.5), (77.5, -112.5), (77.5, -117.5), (82.5, -117.5), (82.5, -122.5), (107.5, -122.5),
                 (107.5, -127.5), (137.5, -127.5), (137.5, -132.5), (157.5, -132.5), (157.5, -137.5), (162.5, -137.5),
                 (162.5, -142.5), (172.5, -142.5), (172.5, -147.5), (180.0, -147.5), (180.0, -180.0)]
    # glycina sinistra
    gly1Area2 = [(-180.0, 180.0), (-180.0, 112.5), (-172.5, 112.5), (-172.5, 117.5), (-152.5, 117.5), (-152.5, 112.5),
                 (-137.5, 112.5), (-137.5, 107.5), (-127.5, 107.5), (-127.5, 102.5), (-117.5, 102.5), (-117.5, 97.5),
                 (-107.5, 97.5), (-107.5, 92.5), (-102.5, 92.5), (-102.5, 87.5), (-97.5, 87.5), (-97.5, 72.5),
                 (-102.5, 72.5), (-102.5, 62.5), (-107.5, 62.5), (-107.5, 57.5), (-112.5, 57.5), (-112.5, 52.5),
                 (-122.5, 52.5), (-122.5, 47.5), (-137.5, 47.5),
                 (-137.5, 52.5), (-152.5, 52.5), (-152.5, 42.5), (-157.5, 42.5), (-157.5, 7.5), (-152.5, 7.5),
                 (-152.5, -2.5), (-147.5, -2.5), (-147.5, -12.5), (-142.5, -12.5), (-142.5, -22.5), (-137.5, -22.5),
                 (-137.5, -32.5), (-132.5, -32.5),
                 (-132.5, -47.5), (-127.5, -47.5), (-127.5, -52.5), (-122.5, -52.5), (-122.5, -62.5), (-117.5, -62.5),
                 (-117.5, -72.5), (-122.5, -72.5), (-122.5, -82.5), (-127.5, -82.5), (-127.5, -87.5), (-132.5, -87.5),
                 (-132.5, -97.5), (-137.5, -97.5), (-137.5, -112.5), (-142.5, -112.5), (-142.5, -117.5),
                 (-147.5, -117.5), (-147.5, -122.5), (-152.5, -122.5), (-152.5, -127.5), (-162.5, -127.5),
                 (-162.5, -122.5), (-167.5, -122.5), (-167.5, -117.5), (-172.5, -117.5), (-172.5, -112.5),
                 (-180.0, -112.5), (-180.0, -180.0), (-47.5, -180.0), (-47.5, -167.5), (-52.5, -167.5), (-52.5, -162.5),
                 (-57.5, -162.5), (-57.5, -152.5), (-62.5, -152.5), (-62.5, -142.5), (-67.5, -142.5), (-67.5, -132.5),
                 (-72.5, -132.5), (-72.5, -127.5), (-77.5, -127.5), (-77.5, -77.5), (-42.5, -77.5), (-42.5, -72.5),
                 (-32.5, -72.5), (-32.5, -67.5), (-27.5, -67.5), (-27.5, -32.5), (-32.5, -32.5), (-32.5, -17.5),
                 (-37.5, -17.5), (-37.5, -7.5), (-42.5, -7.5), (-42.5, 2.5), (-47.5, 2.5), (-47.5, 7.5), (-52.5, 7.5),
                 (-52.5, 17.5), (-57.5, 17.5), (-57.5, 22.5), (-62.5, 22.5), (-62.5, 32.5), (-67.5, 32.5),
                 (-67.5, 72.5), (-72.5, 72.5), (-72.5, 92.5), (-67.5, 92.5), (-67.5, 97.5), (-52.5, 97.5),
                 (-52.5, 102.5), (-42.5, 102.5), (-42.5, 107.5), (-37.5, 107.5), (-37.5, 112.5), (-32.5, 112.5),
                 (-32.5, 117.5), (-27.5, 117.5), (-27.5, 142.5), (-32.5, 142.5), (-32.5, 152.5), (-37.5, 152.5),
                 (-37.5, 162.5), (-42.5, 162.5), (-42.5, 180.0), (-180.0, 180.0)]
    # glycina destra
    gly2Area2 = [(180.0, 180.0), (47.5, 180.0), (47.5, 167.5), (52.5, 167.5), (52.5, 162.5), (57.5, 162.5),
                 (57.5, 147.5), (62.5, 147.5), (62.5, 142.5), (67.5, 142.5), (67.5, 132.5), (72.5, 132.5),
                 (72.5, 127.5), (77.5, 127.5), (77.5, 77.5), (42.5, 77.5), (42.5, 72.5), (32.5, 72.5), (32.5, 67.5),
                 (27.5, 67.5), (27.5, 32.5), (32.5, 32.5), (32.5, 17.5), (37.5, 17.5), (37.5, 7.5), (42.5, 7.5),
                 (42.5, -2.5), (47.5, -2.5), (47.5, -7.5), (52.5, -7.5), (52.5, -17.5), (57.5, -17.5), (57.5, -22.5),
                 (62.5, -22.5), (62.5, -32.5), (67.5, -32.5), (67.5, -77.5), (72.5, -77.5), (72.5, -92.5),
                 (67.5, -92.5), (67.5, -97.5), (52.5, -97.5), (52.5, -102.5), (42.5, -102.5), (42.5, -107.5),
                 (37.5, -107.5), (37.5, -112.5), (37.5, -112.5), (32.5, -112.5), (32.5, -117.5), (27.5, -117.5),
                 (27.5, -142.5), (32.5, -142.5), (32.5, -152.5), (37.5, -152.5), (37.5, -162.5), (42.5, -162.5),
                 (42.5, -177.5), (47.5, -177.5), (47.5, -180.0), (180.0, -180.0),
                 (180.0, -112.5), (172.5, -112.5), (172.5, -117.5), (152.5, -117.5), (152.5, -112.5), (137.5, -112.5),
                 (137.5, -107.5), (127.5, -107.5), (127.5, -102.5), (117.5, -102.5), (117.5, -97.5), (107.5, -97.5),
                 (107.5, -92.5), (102.5, -92.5), (102.5, -87.5), (97.5, -87.5), (97.5, -67.5), (102.5, -67.5),
                 (102.5, -62.5), (107.5, -62.5), (107.5, -57.5), (112.5, -57.5), (112.5, -52.5), (122.5, -52.5),
                 (122.5, -47.5), (137.5, -47.5), (137.5, -52.5), (152.5, -52.5), (152.5, -42.5), (157.5, -42.5),
                 (157.5, -7.5), (152.5, -7.5), (152.5, 2.5), (147.5, 2.5), (147.5, 12.5), (142.5, 12.5), (142.5, 22.5),
                 (137.5, 22.5), (137.5, 32.5), (132.5, 32.5), (132.5, 47.5), (127.5, 47.5), (127.5, 52.5),
                 (122.5, 52.5), (122.5, 77.5), (127.5, 77.5), (127.5, 87.5), (132.5, 87.5), (132.5, 97.5), (37.5, 97.5),
                 (137.5, 112.5), (142.5, 112.5), (142.5, 117.5), (147.5, 117.5), (147.5, 122.5), (152.5, 122.5),
                 (152.5, 127.5), (162.5, 127.5), (162.5, 122.5), (167.5, 122.5), (167.5, 117.5), (172.5, 117.5),
                 (172.5, 112.5), (180.0, 112.5), (180.0, 180.0)]
    # prolina alto sinistra
    pro1Area1 = [(-92.500, 180.000), (-92.500, 177.500), (-97.500, 177.500), (-97.500, 142.500), (-92.500, 142.500),
                 (-92.500, 122.500), (-87.500, 122.500), (-87.500, 117.500), (-82.500, 117.500), (-82.500, 112.500),
                 (-72.500, 112.500), (-72.500, 107.500), (-67.500, 107.500), (-67.500, 112.500), (-42.500, 112.500),
                 (-42.500, 117.500), (-37.500, 117.500), (-37.500, 147.500), (-42.500, 147.500), (-42.500, 157.500),
                 (-47.500, 157.500), (-47.500, 167.500),
                 (-52.500, 167.500), (-52.500, 172.500), (-57.500, 172.500), (-57.500, 177.500), (-62.500, 177.500),
                 (-62.500, 180.000), (-92.500, 180.000)]
    # prolina basso sinistra
    pro2Area1 = [(-62.500, -180.000), (-62.500, -177.500), (-72.500, -177.500), (-72.500, -172.500),
                 (-87.500, -172.500), (-87.500, -177.500), (-92.500, -177.500), (-92.500, -180.000),
                 (-62.500, -180.000)]
    # prolina centro sinistra
    pro3Area1 = [(-72.500, 82.500), (-82.500, 82.500), (-82.500, 77.500), (-87.500, 77.500), (-87.500, 72.500),
                 (-92.500, 72.500), (-92.500, 62.500), (-87.500, 62.500), (-87.500, 52.500), (-82.500, 52.500),
                 (-82.500, 47.500), (-77.500, 47.500), (-77.500, 52.500), (-72.500, 52.500), (-72.500, 57.500),
                 (-67.500, 57.500), (-67.500, 67.500), (-72.500, 67.500), (-72.500, 82.500)]
    # prolina basso centro sinistra
    pro4Area1 = [(-92.500, 27.500), (-97.500, 27.500), (-97.500, 7.500), (-102.500, 7.500), (-102.500, -2.500),
                 (-97.500, -2.500), (-97.500, -12.500), (-92.500, -12.500), (-92.500, -22.500), (-87.500, -22.500),
                 (-87.500, -27.500), (-82.500, -27.500), (-82.500, -32.500), (-77.500, -32.500), (-77.500, -42.500),
                 (-72.500, -42.500), (-72.500, -52.500), (-67.500, -52.500), (-67.500, -57.500), (-57.500, -57.500),
                 (-57.500, -62.500), (-42.500, -62.500), (-42.500, -57.500), (-37.500, -57.500), (-37.500, -27.500),
                 (-42.500, -27.500), (-42.500, -17.500), (-47.500, -17.500), (-47.500, -12.500), (-52.500, -12.500),
                 (-52.500, -2.500), (-62.500, -2.500), (-62.500, 2.500), (-67.500, 2.500), (-67.500, 7.500),
                 (-77.500, 7.500), (-77.500, 12.500), (-82.500, 12.500), (-82.500, 17.500), (-87.500, 17.500),
                 (-87.500, 22.500), (-92.500, 22.500), (-92.500, 27.500)]
    # prolina alto sinistra
    pro1Area2 = [(-112.500, 180.000), (-112.500, 177.500), (-112.500, 142.500), (-107.500, 142.500),
                 (-107.500, 122.500), (-102.500, 122.500), (-102.500, 112.500), (-97.500, 112.500), (-97.500, 82.500),
                 (-102.500, 82.500), (-102.500, 42.500), (-107.500, 42.500), (-107.500, 37.500), (-112.500, 37.500),
                 (-112.500, -12.500), (-107.500, -12.500), (-107.500, -22.500), (-102.500, -22.500),
                 (-102.500, -32.500), (-97.500, -32.500), (-97.500, -37.500), (-92.500, -37.500), (-92.500, -42.500),
                 (-87.500, -42.500), (-87.500, -52.500), (-82.500, -52.500), (-82.500, -57.500), (-77.500, -57.500),
                 (-77.500, -62.500), (-72.500, -62.500), (-72.500, -67.500), (-62.500, -67.500), (-62.500, -72.500),
                 (-32.500, -72.500), (-32.500, -67.500), (-27.500, -67.500), (-27.500, -62.500), (-22.500, -62.500),
                 (-22.500, -32.500), (-27.500, -32.500), (-27.500, -17.500), (-32.500, -17.500), (-32.500, -7.500),
                 (-37.500, -7.500), (-37.500, -2.500), (-42.500, -2.500), (-42.500, 2.500), (-47.500, 2.500),
                 (-47.500, 7.500), (-52.500, 7.500), (-52.500, 12.500), (-57.500, 12.500), (-57.500, 17.500),
                 (-62.500, 17.500), (-62.500, 22.500), (-67.500, 22.500), (-67.500, 37.500), (-62.500, 37.500),
                 (-62.500, 47.500), (-57.500, 47.500), (-57.500, 97.500), (-47.500, 97.500), (-47.500, 102.500),
                 (-37.500, 102.500), (-37.500, 107.500), (-32.500, 107.500), (-32.500, 112.500), (-27.500, 112.500),
                 (-27.500, 152.500), (-32.500, 152.500), (-32.500, 167.500), (-37.500, 167.500), (-37.500, 172.500),
                 (-42.500, 172.500), (-42.500, 177.500), (-42.500, 180.000), (-112.500, 180.000)]
    # prolina basso sinistra
    pro2Area2 = [(-42.500, -180.000), (-42.500, -177.500), (-47.500, -177.500), (-47.500, -172.500),
                 (-52.500, -172.500), (-52.500, -167.500), (-62.500, -167.500), (-62.500, -162.500),
                 (-67.500, -162.500), (-67.500, -157.500), (-92.500, -157.500), (-92.500, -162.500),
                 (-102.500, -162.500), (-102.500, -167.500), (-107.500, -167.500), (-107.500, -177.500),
                 (-112.500, -177.500), (-112.500, -180.000), (-42.500, -180.000)]

    ritorno = "out"
    if residue.upper() == "GLY":
        if phi == None or psi == None:
            return None
        if pointInsidePolygon(phi, psi, gly1Area2):
            ritorno = "1gly2"
        if pointInsidePolygon(phi, psi, gly2Area2):
            ritorno = "2gly2"
        if pointInsidePolygon(phi, psi, gly1Area1):
            ritorno = "1gly1"
        if pointInsidePolygon(phi, psi, gly2Area1):
            ritorno = "2gly1"
        if pointInsidePolygon(phi, psi, gly3Area1):
            ritorno = "3gly1"
        if pointInsidePolygon(phi, psi, gly4Area1):
            ritorno = "4gly1"
        if pointInsidePolygon(phi, psi, gly5Area1):
            ritorno = "5gly1"
        if pointInsidePolygon(phi, psi, gly6Area1):
            ritorno = "6gly1"

        return ritorno

    if residue.upper() == "PRO":
        if phi == None or psi == None:
            return None
        if pointInsidePolygon(phi, psi, pro1Area2):
            ritorno = "1pro2"
        if pointInsidePolygon(phi, psi, pro2Area2):
            ritorno = "2pro2"
        if pointInsidePolygon(phi, psi, pro1Area1):
            ritorno = "1pro1"
        if pointInsidePolygon(phi, psi, pro2Area1):
            ritorno = "2pro1"
        if pointInsidePolygon(phi, psi, pro3Area1):
            ritorno = "3pro1"
        if pointInsidePolygon(phi, psi, pro4Area1):
            ritorno = "4pro1"

        return ritorno

    if phi == None or psi == None:
        return None
    if pointInsidePolygon(phi, psi, bs2Area):
        ritorno = "bs2"
    if pointInsidePolygon(phi, psi, rah2Area):
        ritorno = "rah2"
    if pointInsidePolygon(phi, psi, lah2Area):
        ritorno = "lah2"
    if pointInsidePolygon(phi, psi, other1PossibleArea2):
        ritorno = "1oth2"
    if pointInsidePolygon(phi, psi, bs1Area):
        ritorno = "bs1"
    if pointInsidePolygon(phi, psi, rah1Area):
        ritorno = "rah1"
    if pointInsidePolygon(phi, psi, lah1Area):
        ritorno = "lah1"
    if pointInsidePolygon(phi, psi, other1PossibleArea1):
        ritorno = "1oth1"
    if pointInsidePolygon(phi, psi, other2PossibleArea2):
        ritorno = "2oth2"
    if pointInsidePolygon(phi, psi, other3PossibleArea2):
        ritorno = "3oth2"
    if pointInsidePolygon(phi, psi, other4PossibleArea2):
        ritorno = "4oth2"
    if pointInsidePolygon(phi, psi, other5PossibleArea2):
        ritorno = "5oth2"

    return ritorno


def pointInsidePolygon(x, y, poly):
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

@deprecated("Use BORGES_MATRIX.print_secondary_structure_elements")
def printSecondaryStructureElements(lisBigSS):
    for l in range(len(lisBigSS)):
        fragment = lisBigSS[l]
        print str(fragment["pdbid"]) + "  " + str(fragment["model"]) + "  " + str(fragment["chain"]) + "  " + "[" + str(
            (fragment["resIdList"][0])[1]) + str((fragment["resIdList"][0])[2]) + ":" + str(
            (fragment["resIdList"][fragment["fragLength"] - 1])[1]) + str(
            (fragment["resIdList"][fragment["fragLength"] - 1])[2]) + "]  " + str(fragment["vecLength"]) + "  " + str(
            fragment["sstype"]) + "  " + str(fragment["sequence"]),
        if "description" in fragment.keys():
            print " -----> ", fragment["description"]
        else:
            print " "


def __resBioOrder(a, b):
    return cmp(a[1], b[1])


def __resBioOrder2(a, b):
    return cmp(a.get_id()[1], b.get_id()[1])


def createCustomFragment(structure, idname, modelV, chainV, residueList, typeOfFrag, lengthFragment):
    sst = {}
    sst["sstype"] = "nothing"
    sst["ssDescription"] = "nothing"
    residueList = sorted(residueList, __resBioOrder)
    for model in structure.get_list():
        if model.get_id() != modelV:
            continue
        for chain in model.get_list():
            coordCA = []
            coordO = []
            numerOfResidues = 0
            if chain.get_id() != chainV:
                continue
            for residue in chain.get_list():
                if residue.get_id() not in residueList:
                    continue

                ca = residue["CA"]
                numerOfResidues += 1
                # per ogni atomo di Carbonio alfa, viene salvato in coordCA quattro valori:
                # [0] pos_X
                # [1] pos_Y
                # [2] pos_Z
                # [3] id del residuo di cui fa parte
                # [4] residue name code in 3 letters
                coordCA.append(
                    [float(ca.get_coord()[0]), float(ca.get_coord()[1]), float(ca.get_coord()[2]), residue.get_id(),
                     residue.get_resname()])
                ca = residue["O"]
                coordO.append(
                    [float(ca.get_coord()[0]), float(ca.get_coord()[1]), float(ca.get_coord()[2]), residue.get_id(),
                     residue.get_resname()])

            numberOfSegments = numerOfResidues - lengthFragment + 1
            # print "number of segments is",numberOfSegments
            if numberOfSegments <= 0:
                continue
            """vectorsCA = ADT.get_matrix(numberOfSegments,3)
            vectorsO = ADT.get_matrix(numberOfSegments,3)

            for i in range(lengthFragment):
                    vectorsCA[0] = [vectorsCA[0][0]+coordCA[i][0]/float(lengthFragment), vectorsCA[0][1]+coordCA[i][1]/float(lengthFragment), vectorsCA[0][2]+coordCA[i][2]/float(lengthFragment)]
                    vectorsO[0] = [vectorsO[0][0]+coordO[i][0]/float(lengthFragment), vectorsO[0][1]+coordO[i][1]/float(lengthFragment), vectorsO[0][2]+coordO[i][2]/float(lengthFragment)]

            for i in range(1,len(vectorsCA)):
                    vectorsCA[i] = [vectorsCA[i-1][0]+(coordCA[i+lengthFragment-1][0]-coordCA[i-1][0])/float(lengthFragment), vectorsCA[i-1][1]+(coordCA[i+lengthFragment-1][1]-coordCA[i-1][1])/float(lengthFragment), vectorsCA[i-1][2]+(coordCA[i+lengthFragment-1][2]-coordCA[i-1][2])/float(lengthFragment)]
                    vectorsO[i] = [vectorsO[i-1][0]+(coordO[i+lengthFragment-1][0]-coordO[i-1][0])/float(lengthFragment), vectorsO[i-1][1]+(coordO[i+lengthFragment-1][1]-coordO[i-1][1])/float(lengthFragment), vectorsO[i-1][2]+(coordO[i+lengthFragment-1][2]-coordO[i-1][2])/float(lengthFragment)]

            vectorsH = [0.0 for _ in range(numberOfSegments)]"""

            for i in range(numberOfSegments):
                # XH = vectorsCA[i][0]-vectorsO[i][0]
                # YH = vectorsCA[i][1]-vectorsO[i][1]
                # ZH = vectorsCA[i][2]-vectorsO[i][2]

                prevRes = (" ", None, " ")
                ncontigRes = 0
                resids = []
                prev_model = None
                prev_chain = None

                for yui in range(i, i + lengthFragment):  # quindi arrivo a i+lengthFragment-1
                    resan = (coordCA[yui])[3]
                    resids.append(list(resan) + [(coordCA[yui])[4]])
                    resa = resan
                    if prevRes == (" ", None, " "):
                        ncontigRes += 1
                    else:
                        resaN = getResidue(structure, model.get_id(), chain.get_id(), resan)
                        prevResC = getResidue(structure, prev_model, prev_chain, prevRes)
                        if checkContinuity(prevResC, resaN):
                            ncontigRes += 1
                    prevRes = resa
                    prev_model = model.get_id()
                    prev_chain = chain.get_id()

                if ncontigRes != lengthFragment:
                    print "The fragment to create does not contain contigous residues!"
                    return sst

                resIDs = []
                amn = []
                for q in range(lengthFragment):
                    res = coordCA[i + q][3]
                    resIDs.append(res)
                    amn.append(coordCA[i + q][4])  # take the aa name directly from the array of coordinates

                sst = recognizeFragment(idname, model, chain, coordCA[i:i + lengthFragment],
                                        coordO[i:i + lengthFragment], resIDs, amn, None, None, sstype=typeOfFrag,
                                        distS=[])

                return sst
    return sst


def drawDistribution3(cvs_list, filename, colors_diff=False):
    qe = open(filename + ".scri", "w")
    qe.write("set terminal png size 800,800\nset output \"" + filename + ".png\"\n")
    towr = "plot "
    cvs_all = {}
    statistics = {}
    for cvs_r in range(len(cvs_list)):
        cvs = cvs_list[cvs_r]
        cvst = []
        tempc = []
        for cv in cvs:
            if len(tempc) == 0 or cv[0] == tempc[-1][0] + 1:
                tempc.append(cv)
            else:
                cvst.append(deepcopy(tempc))
                tempc = []
                tempc.append(cv)
        if len(tempc) > 0:
            cvst.append(deepcopy(tempc))
            tempc = []
        for l in range(len(cvst)):
            cvl = cvst[l]
            qo = open(filename + "_" + str(cvs_r) + "_" + str(l) + ".data", "w")
            color = ""
            for c in range(len(cvl)):
                cv = cvl[c]
                if c == len(cvl) - 1:
                    qo.write(" \t" + str(cv[0]) + "\t" + str(cv[1]) + " #    " + str(
                        cvl[c][1] - cvl[c - 1][1]) + "    " + str(cv[4]) + "\n")
                    if cv[1] - cvl[c - 1][1] <= 0:
                        color = "5"
                    else:
                        color = "1"
                else:
                    qo.write(" \t" + str(cv[0]) + "\t" + str(cv[1]) + " # " + str(cv[4]) + "\n")
                if str(cv[0]) not in cvs_all:
                    cvs_all[str(cv[0])] = [cv[1]]
                else:
                    cvs_all[str(cv[0])].append(cv[1])
            qo.close()
            # towr += "\""+filename+"_"+str(cvs_r)+"_"+str(l)+".data\" using 1:2 notitle with points, \""+filename+"_"+str(l)+".data\" using 1:2 notitle with lines"
            if not colors_diff:
                towr += "\"" + filename + "_" + str(cvs_r) + "_" + str(l) + ".data\" using 1:2 notitle with lines lc 3"
            else:
                towr += "\"" + filename + "_" + str(cvs_r) + "_" + str(
                    l) + ".data\" using 1:2 notitle with lines lc " + color

            if l != len(cvst) - 1:
                towr += ","

        if cvs_r == len(cvs_list) - 1:
            qo = open(filename + "_mean.data", "w")
            qd = open(filename + "_std.data", "w")
            for cvs_key in sorted(map(lambda x: int(x), cvs_all.keys())):
                mean = numpy.mean(cvs_all[str(cvs_key)])
                std = numpy.std(cvs_all[str(cvs_key)])
                statistics[str(cvs_key)] = (mean, std)
                qo.write(" \t" + str(cvs_key) + "\t" + str(mean) + "\n")
                qd.write(" \t" + str(cvs_key) + "\t" + str(mean + std) + "\n")
                qd.write(" \t" + str(cvs_key) + "\t" + str(mean - std) + "\n")
            qo.close()
            qd.close()
            towr += ", \"" + filename + "_mean.data\" using 1:2 notitle with lines lc 2, \"" + filename + "_std.data\" using 1:2 notitle with points lc 1"
            towr += ", 1.4 notitle with lines, 2.2 notitle with lines \n"
        else:
            towr += ", "
    qe.write(towr)
    qe.close()
    # memoria = str((os.popen("~/usr/bin/gnuplot "+filename+".scri")).read())
    try:
        p = subprocess.Popen(['gnuplot', filename + ".scri"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        # os.remove(filename+".scri")
        # os.remove(filename+".data")
    except:
        print ""
    return statistics


def drawDistribution2(cvs, filename):
    qe = open(filename + ".scri", "w")
    qe.write("set terminal png size 800,800\nset output \"" + filename + ".png\"\n")

    cvst = []
    tempc = []
    for cv in cvs:
        if len(tempc) == 0 or cv[0] == tempc[-1][0] + 1:
            tempc.append(cv)
        else:
            cvst.append(deepcopy(tempc))
            tempc = []
            tempc.append(cv)
    if len(tempc) > 0:
        cvst.append(deepcopy(tempc))
        tempc = []
    towr = "plot "
    for l in range(len(cvst)):
        cvl = cvst[l]
        qo = open(filename + "_" + str(l) + ".data", "w")
        for c in range(len(cvl)):
            cv = cvl[c]
            if c == len(cvl) - 1:
                qo.write(
                    " \t" + str(cv[0]) + "\t" + str(cv[1]) + " #    " + str(cvl[c][1] - cvl[c - 1][1]) + "    " + str(
                        cv[4]) + "\n")
            else:
                qo.write(" \t" + str(cv[0]) + "\t" + str(cv[1]) + " # " + str(cv[4]) + "\n")

        qo.close()
        towr += "\"" + filename + "_" + str(l) + ".data\" using 1:2 notitle with points, \"" + filename + "_" + str(
            l) + ".data\" using 1:2 notitle with lines"
        if l == len(cvst) - 1:
            towr += ", 1.4 notitle with lines, 2.2 notitle with lines \n"
        else:
            towr += ", "
    qe.write(towr)
    qe.close()
    # memoria = str((os.popen("~/usr/bin/gnuplot "+filename+".scri")).read())
    try:
        p = subprocess.Popen(['gnuplot', filename + ".scri"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        # os.remove(filename+".scri")
        # os.remove(filename+".data")
    except:
        print ""

    return False


def drawDistribution(fragment, windowLength):
    if not os.path.exists("./temp/drawDistri"):
        os.makedirs("./temp/drawDistri")

    ad = ""
    ae = ""
    if str(((fragment["resIdList"])[0])[2]) != " ":
        ad = str(((fragment["resIdList"])[0])[2])
    if str(((fragment["resIdList"])[-1])[2]) != " ":
        ae = str(((fragment["resIdList"])[-1])[2])

    filename = "./temp/drawDistri/" + str(fragment["pdbid"]) + "_" + str(fragment["model"]) + "_" + str(
        fragment["chain"]) + "_" + str(((fragment["resIdList"])[0])[1]) + ad + str("-") + str(
        ((fragment["resIdList"])[-1])[1]) + ae + "_" + str(fragment["sstype"]) + "_" + str(windowLength)

    qe = open(filename + ".scri", "w")
    qe.write("set terminal png size 800,800\nset output \"" + filename + ".png\"\n")
    # qe.write("set terminal canvas size 800,800\nset output \""+filename+".html\"\nplot \""+filename+".data\" using 1:2 title \"points\" with points, \""+filename+".data\" using 1:2 title \"lines\" with lines, \""+filename+".data\" using 1:2 smooth bezier title \"bezier\" with lines, \""+filename+".data\" using 1:2 smooth csplines title \"csplines\" with lines\n")

    qo = open(filename + ".data", "w")

    cont = ((fragment["resIdList"])[0])[1]
    step = 0  # windowLength-1#windowLength/2
    # print fragment["distCV"]
    # print fragment["distSS"]
    for u in range(len(fragment["distCV"])):
        if u == 0:
            qo.write("#\tX\tY\n")
        (index, jh) = (fragment["distCV"])[u]
        qo.write(" \t" + str(cont + step) + "\t" + str(jh) + "\n")
        qe.write("set label \"" + ((fragment["distSS"])[u])[1] + "\" at " + str(cont + step) + "," + str(jh) + "\n")
        cont += 1
    # qo.write(str(fragment["distCV"])+"\n")
    # qo.write(str(fragment["distSS"])+"\n")
    # qo.write(str(fragment["resIdList"])+"\n")

    qo.close()
    qe.write(
        "plot \"" + filename + ".data\" using 1:2 title \"points\" with points, \"" + filename + ".data\" using 1:2 title \"lines\" with lines, 1.4 notitle with lines, 2.2 notitle with lines\n")
    qe.close()
    # memoria = str((os.popen("~/usr/bin/gnuplot "+filename+".scri")).read())
    try:
        p = subprocess.Popen(['gnuplot', filename + ".scri"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        # os.remove(filename+".scri")
        # os.remove(filename+".data")
    except:
        print ""

    return False


def score(s1, s2, sub):
    """#compute the score between two characters using sub if it is not null
    #INPUT: s1 (the first character)
    #       s2 (the second character)
    #       sub  (matrix of substitution as tuple of two elements: the matrix as list of lists and the symbols as dictionary)
    #OUTPUT: a float containing the score of the comparison of the two characters"""

    x = 0

    if sub:
        x += (sub[0])[(sub[1])[s1]][(sub[1])[s2]]
    else:
        if s1 == s2:
            x += 1
    return x


def compareDistributionAccordingOrientation(AlistFrags, BlistFrags, threshold, shift, where, returnCVS=False):
    returnList = []
    nTota = []
    returnAnyway = []
    retcvs = []
    BlistFragsVali = getListValidFromTwoList(AlistFrags, BlistFrags, areFragments=True)
    bestDegree = 10000
    bestTuple = None

    for BlistFrags in BlistFragsVali:
        for i in range(len(AlistFrags)):
            refrag = []
            reAny = []
            recvs = []
            frag1 = AlistFrags[i]
            frag2 = BlistFrags[i]
            cvv1 = generateVectorsCVS(frag1, full=True)
            cvv2 = generateVectorsCVS(frag2, full=True)

            # print "---cvv1",len(cvv1)
            # print "---cvv2",len(cvv2)
            if len(cvv1) != len(cvv2):
                cvv1 = [cvv1[0], cvv1[int(len(cvv1) / 2)], cvv1[-1]]
                cvv2 = [cvv2[0], cvv2[int(len(cvv2) / 2)], cvv2[-1]]
                # continue

            nThis = len(cvv1)
            ind1, cv1, ind2, cv2, cav1, ov1, cav2, ov2 = 0, 0, 0, 0, 0, 0, 0, 0

            for t in range(len(cvv1) - shift):
                if shift != 0 and where == "A":
                    ind1, cv1, cav1, ov1 = cvv1[t + shift]
                    ind2, cv2, cav2, ov2 = cvv2[t]
                elif shift != 0 and where == "B":
                    ind1, cv1, cav1, ov1 = cvv1[t]
                    ind2, cv2, cav2, ov2 = cvv2[t + shift]
                elif shift == 0:
                    ind1, cv1, cav1, ov1 = cvv1[t]
                    ind2, cv2, cav2, ov2 = cvv2[t]

                X1 = cv1[0]
                Y1 = cv1[1]
                Z1 = cv1[2]
                X2 = cv2[0]
                Y2 = cv2[1]
                Z2 = cv2[2]
                TetaReal = angle_between([X1, Y1, Z1], [X2, Y2, Z2], [1.0, 1.0, 1.0], signed=False)
                tetadeg = TetaReal * 57.2957795

                if tetadeg <= threshold:
                    refrag.append((ind1, ind2, tetadeg))
                reAny.append((ind1, ind2, tetadeg))
                recvs.append((cav1, ov1, cav2, ov2))

            returnList.append(refrag)
            returnAnyway.append(reAny)
            nTota.append(nThis)
            retcvs.append(recvs)

        media = []
        for i in range(len(nTota)):
            summa = 0
            for t in range(len(returnAnyway[i])):
                summa += float(((returnAnyway[i])[t])[2])
            media.append(summa / len(returnAnyway[i]))
        vas = max(media)
        if vas < bestDegree:
            bestDegree = vas
            if not returnCVS:
                bestTuple = nTota, returnList, returnAnyway
            else:
                bestTuple = nTota, returnList, returnAnyway, retcvs

    return bestTuple


def Moses(pathIn, dirOut, sstype):
    rootdir = pathIn
    outDir = dirOut

    if not os.path.exists(outDir):
        os.makedirs(outDir)

    if os.path.isdir(rootdir):
        for root, subFolders, files in os.walk(rootdir):
            for fileu in files:
                pdbf = os.path.join(root, fileu)
                if not pdbf.endswith(".pdb"):
                    continue
                __mose(pdbf, outDir, sstype)
    elif rootdir.endswith(".pdb"):
        __mose(rootdir, outDir, sstype)


def __mose(pdbf, outDir, sstype):
    idname = (os.path.basename(pdbf))[:-4]
    tuplaresultado = getFragmentListFromPDB(pdbf, False, False)
    structure, list_dict_frag = tuplaresultado[0], tuplaresultado[1]

    print "======================" + idname + "======================"
    printSecondaryStructureElements(list_dict_frag)
    print "======================================================"

    for i in range(len(list_dict_frag)):
        if sstype == "all" or (list_dict_frag[i])["sstype"] == sstype:
            tuplaresultado2 = getPDBFormattedAsString(str(0), [list_dict_frag[i]], structure, "")
            filename, filecont = tuplaresultado2[0], tuplaresultado2[1]
            sedI = str((((list_dict_frag[i])["resIdList"])[0])[2])
            sedF = str((((list_dict_frag[i])["resIdList"])[-1])[2])
            if sedI.isspace():
                sedI = ""
            if sedF.isspace():
                sedF = ""
            resI = str((((list_dict_frag[i])["resIdList"])[0])[1]) + sedI
            resF = str((((list_dict_frag[i])["resIdList"])[-1])[1]) + sedF

            filename = outDir + "/" + idname + "_f" + str(i + 1) + "_" + str((list_dict_frag[i])["sstype"]) + "_" + str(
                (list_dict_frag[i])["fragLength"]) + "_" + str((list_dict_frag[i])["chain"]) + "_" + str(
                resI) + "_" + str(resF) + ".pdb"
            fichero = open(filename, "w")
            fichero.write(filecont)
            fichero.close()


def generateVectorsCVS(fragment, full=False):
    distcvs = []
    nS = fragment["fragLength"] - SUFRAGLENGTH + 1
    CAatomCoord = fragment["CAatomCoord"]
    OatomCoord = fragment["OatomCoord"]

    for plo in range(nS):
        # print "plo is",plo
        xca = 0.0
        yca = 0.0
        zca = 0.0
        xo = 0.0
        yo = 0.0
        zo = 0.0
        for qlo in range(SUFRAGLENGTH):
            # print "\tqlo is",qlo
            xca += CAatomCoord[plo + qlo][0]
            yca += CAatomCoord[plo + qlo][1]
            zca += CAatomCoord[plo + qlo][2]
            xo += OatomCoord[plo + qlo][0]
            yo += OatomCoord[plo + qlo][1]
            zo += OatomCoord[plo + qlo][2]
        xca /= SUFRAGLENGTH
        yca /= SUFRAGLENGTH
        zca /= SUFRAGLENGTH
        xo /= SUFRAGLENGTH
        yo /= SUFRAGLENGTH
        zo /= SUFRAGLENGTH

        XH = xca - xo
        YH = yca - yo
        ZH = zca - zo
        if not full:
            distcvs.append((plo, [XH, YH, ZH]))
        else:
            distcvs.append((plo, [XH, YH, ZH], [xca, yca, zca], [xo, yo, zo]))

    return distcvs


def NeedlemanWMatrix(seq1, seq2, k, sub):
    """#compute the score matrix and the path matrix of Needleman Wunsch algorithm
    #INPUT: seq1 (first sequence to align)
    #       seq2 (second sequence to align)
    #       k    (gap penalty)
    #       sub  (matrix of substitution as tuple of two elements: the matrix as list of lists and the symbols as dictionary)
    #OUTPUT: a matrix where each element is a tuple that contains: (score, path) where score is a float and path
    #        is a character 'D' for diagonal, 'U' for Up and 'L' for Left"""

    n = len(seq1) + 1
    m = len(seq2) + 1
    M = ADT.get_matrix(n, m)  # crea righe per colonne

    M[0][0] = (0, 'D')

    for i in range(1, n):
        M[i][0] = (-k * i, 'U')

    for i in range(1, m):
        M[0][i] = (-k * i, 'L')

    for i in range(1, n):
        for j in range(1, m):
            a = (M[i - 1][j - 1])[0] + score(seq1[i - 1], seq2[j - 1], sub)  # seq2 is vertical, seq1 is orizontal
            b = (M[i - 1][j])[0] - k
            c = (M[i][j - 1])[0] - k

            # by using >= comparisons I tend to choose the Diagonal path when i have more possibilities
            if a >= b:
                if a >= c:
                    M[i][j] = (a, 'D')
                else:
                    M[i][j] = (c, 'L')
            elif b > c:
                M[i][j] = (b, 'U')
            else:
                M[i][j] = (c, 'L')

    return M

def eVRMS(nres=100, seqID=30):
    """Computes the expected variance-refined RMSD (eVRMS) of a structure according to the seq identity and number of residues (Robert et al., Acta D. 2013)
    #INPUT: nres: number of residues, seqID sequence identity as a percentage
    #OUTPUT: eVRMS in Angstroms"""

    #Parameters fitted in the paper:
    A=0.0569
    B=173
    C=1.52

    #Model-dependent parameters
    #--> H: Fraction of mutated residues
    H=float(100 - seqID)/100
    eVRMS=A*math.pow((B+nres), 1.0/3) * math.exp(C*H)
    return eVRMS


