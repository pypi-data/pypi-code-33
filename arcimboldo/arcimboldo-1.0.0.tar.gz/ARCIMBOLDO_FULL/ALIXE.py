#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python imports
from __future__ import division

import ConfigParser
import cPickle
import cProfile
import copy
import datetime
import math
import operator
import os
import shutil
import sys
import time
import traceback
import numpy

import alixe_library as al
import SELSLIB2

# Get a copy of the space group dictionary
dictio_space_groups = al.get_spacegroup_dictionary()

# Functions to help in optimization
def timing(f):
    """

    :param f:
    :type f:
    :return:
    :rtype:
    """

    def wrap(*args, **kwds):
        time1 = time.time()
        ret = f(*args, **kwds)
        time2 = time.time()
        print ('%s function took %0.3f s' % (f.__name__, (time2 - time1)))
        return ret

    return wrap


def profileit(func):
    """

    :param func:
    :type func:
    :return:
    :rtype:
    """

    def wrapper(*args, **kwargs):
        datafn = func.__name__ + ".profile"  # Name the data file sensibly
        prof = cProfile.Profile()
        retval = prof.runcall(func, *args, **kwargs)
        prof.dump_stats(datafn)
        return retval

    return wrapper

def fishing_round_by_prio_list(dict_first_round_by_rotclu, reference_hkl, sg_symbol,phstat_version, path_phstat,
                               ncores, clust_fold, path_ins, path_best, cell, resolution, cycles, tolerance, orisub,
                               weight, ent_path=None):

    """

    :param dict_first_round_by_rotclu:
    :type dict_first_round_by_rotclu:
    :param reference_hkl:
    :type reference_hkl:
    :param sg_symbol:
    :type sg_symbol:
    :param phstat_version:
    :type phstat_version:
    :param path_phstat:
    :type path_phstat:
    :param ncores:
    :type ncores:
    :param clust_fold:
    :type clust_fold:
    :param path_ins:
    :type path_ins:
    :param path_best:
    :type path_best:
    :param cell:
    :type cell:
    :param resolution:
    :type resolution:
    :param cycles:
    :type cycles:
    :param tolerance:
    :type tolerance:
    :param orisub:
    :type orisub:
    :param weight:
    :type weight:
    :return:
    :rtype:
    """

    # NOTE CM: I should possibly deprecate the use of the python version, but meanwhile this will make it work
    f_fom=(True if weight == 'f' else False)

    list_prio = []
    list_to_remove = []
    sg_number = al.get_space_group_number_from_symbol(sg_symbol)
    seed = 0  # We give the input sorted so in the fortran phstat we want it to use the first one as ref
    for rotclu in dict_first_round_by_rotclu.keys():
        topllg = 0
        name_clust_topllg = ''
        topzscore = 0
        name_clust_topzscore = ''
        for cluster in dict_first_round_by_rotclu[rotclu].keys():
            if dict_first_round_by_rotclu[rotclu][cluster]['dict_FOMs']['llg'] > topllg:
                topllg = dict_first_round_by_rotclu[rotclu][cluster]['dict_FOMs']['llg']
                name_clust_topllg = cluster
            if dict_first_round_by_rotclu[rotclu][cluster]['dict_FOMs']['zscore'] > topzscore:
                topzscore = dict_first_round_by_rotclu[rotclu][cluster]['dict_FOMs']['zscore']
                name_clust_topzscore = cluster
        if name_clust_topllg not in list_prio:
            list_prio.append(name_clust_topllg)
        if name_clust_topzscore not in list_prio:
            list_prio.append(name_clust_topzscore)
    list_rest = []
    for rotclu in dict_first_round_by_rotclu.keys():
        for cluster in dict_first_round_by_rotclu[rotclu]:
            if cluster not in list_prio:
                list_rest.append((cluster, dict_first_round_by_rotclu[rotclu][cluster]['dict_FOMs']['llg']))
    sorted_list_rest = sorted(list_rest, key=lambda x: x[1])
    for i in range(len(sorted_list_rest)):
        sorted_list_rest[i] = sorted_list_rest[i][0]
    list_prio.extend(sorted_list_rest)
    number_of_trials = int(ncores)
    max_number_of_trials = len(list_prio)
    dict_result_by_trial = {}
    raw_clust_second_round = open(os.path.join(clust_fold, "info_clust_second_round_raw"), 'w')
    del raw_clust_second_round
    table_clust_second_round = open(os.path.join(clust_fold, "info_clust_second_round_table"), 'w')
    if ent_path != None:
        table_clust_second_round.write('%-40s %-5s %-10s %-10s %-10s %-10s\n' % ('Cluster', 'n_phs', 'wmpd_max', 'wmpd_min','phi_cc','phi_wmpe'))
    else:
        table_clust_second_round.write(
            '%-40s %-5s %-10s %-10s %-10s \n' % ('Cluster', 'n_phs', 'wmpd_max', 'wmpd_min', 'phi_cc'))
    del table_clust_second_round
    for i in range(number_of_trials):
        if i >= max_number_of_trials:
            break  # We can't use more references, we finished the list!
        reference = list_prio[i]
        if (os.path.split(reference))[1] in list_to_remove:
            print "This reference, ", reference, " was already fished with another reference. Skipping this cycle"
            continue  # We go to the next iteration, because this reference has been fished already
        name_ref = os.path.split(reference)[1]
        name_phi = reference[:-4] + "_ref.phi"
        if phstat_version == 'python':
            dict_phs = {}
            dict_phs[reference] = True
            for j in xrange(len(list_prio)):
                name_file = (os.path.split(list_prio[j]))[1]
                if (list_prio[j] not in dict_phs.keys()) and (name_file not in list_to_remove):
                    dict_phs[list_prio[j]] = False
            dict_result_by_trial[list_prio[i]] = startALIXEasPHSTAT(clust_fold, reference_hkl, dict_phs, cell,
                                                                    sg_number, tolerance=tolerance,
                                                                    resolution=resolution, cycles=cycles, f_fom=f_fom)
        elif phstat_version == 'fortran':
            path = os.path.normpath(clust_fold)  # relative path because fortran does not accept such long paths
            list_path = path.split(os.sep)
            relative_path_clust_fold = './' + list_path[-1]
            # 1) Write an ls file with the list of phs, putting first the reference
            path_ls = os.path.join(clust_fold, reference[:-4] + "_ref.ls")
            relative_ref = os.path.join(relative_path_clust_fold, name_ref)
            lsrotfile = open(path_ls, 'w')
            lsrotfile.write(relative_ref + '\n')
            for j in range(len(list_prio)):
                phs_namefile = (os.path.split(list_prio[j]))[1]
                phs_relative_path = os.path.join(relative_path_clust_fold, phs_namefile)
                if phs_relative_path != relative_ref and (phs_namefile not in list_to_remove):
                    lsrotfile.write(phs_relative_path + '\n')
            lsrotfile.close()
            # 2.1) Link the ins file
            os.link(path_ins, os.path.join(clust_fold, path_ls[:-3] + ".ins"))
            # 2.1) Link a pda file
            os.link(path_best, os.path.join(clust_fold, path_ls[:-3] + ".pda"))
            # 3) Launch the function in alixe_library
            complete_output,errors = al.call_phstat_print_for_clustering(path_ls[:-3], relative_path_clust_fold, path_phstat,
                                                                  resolution, seed, tolerance, cycles, orisub, weight)
            print complete_output
            print errors

            ls = open(path_ls, "r")
            lineas_fichero_ls = ls.readlines()
            numero_phs = len(lineas_fichero_ls)
            del ls

            dict_result_by_trial[reference] = {name_phi: None}

            # NOTE CM: Change to make it compatible with our newest phstat
            #dict_result_by_trial[reference][name_phi] = al.read_phstat_print_clusterization_output(ls_content,
            #                                                                                      complete_output,
            #                                                                                       cycles)
            dict_result_by_trial[reference][name_phi] = al.read_phstat_isa_clusterization_output(complete_output=complete_output,
                                                                                                 cycles=cycles, n_files=numero_phs)

        # NOTE: Because of the relative paths, in the fortran case I need to modify the dictionary now to contain the full paths
        raw_clust_second_round = open(os.path.join(clust_fold, "info_clust_second_round_raw"), 'a')
        table_clust_second_round = open(os.path.join(clust_fold, "info_clust_second_round_table"), 'a')
        raw_clust_second_round.write(
            "*********************************************************************************************************************************************\n")
        n_phs = len(dict_result_by_trial[list_prio[i]][name_phi].keys())
        raw_clust_second_round.write("CLUSTER fishing with reference " + name_ref + ' , found in file ' + name_ref[
                                                                                                          :-4] + '_ref.phi, containing ' + str(
            n_phs) + ' phase files' + '\n')
        for key1 in dict_result_by_trial[list_prio[i]].keys():
            wmpe_max = 0.0
            wmpe_min = 90.0
            for key2 in dict_result_by_trial[list_prio[i]][key1].keys():
                if phstat_version == 'fortran':
                    new_key2 = os.path.join(clust_fold, os.path.split(key2)[1])
                    dict_result_by_trial[list_prio[i]][key1][new_key2] = copy.deepcopy(
                        dict_result_by_trial[list_prio[i]][key1][key2])
                    del dict_result_by_trial[list_prio[i]][key1][key2]
                    raw_clust_second_round.write(
                        new_key2 + "\t" + str(dict_result_by_trial[list_prio[i]][key1][new_key2]) + '\n')
                    wmpe = dict_result_by_trial[list_prio[i]][key1][new_key2]['wMPE_first']
                else:
                    raw_clust_second_round.write(
                        key2 + "\t" + str(dict_result_by_trial[list_prio[i]][key1][key2]) + '\n')
                    wmpe = dict_result_by_trial[list_prio[i]][key1][key2]['wMPE']
                list_to_remove.append(os.path.split(key2)[1])
                if wmpe > wmpe_max:
                    wmpe_max = wmpe
                if wmpe < wmpe_min and wmpe != 0.0:  # Because 0.0 is to itself, the reference
                    wmpe_min = wmpe
            name_cluster = (os.path.split(key1))[1]
            if wmpe_max == 0.0 and wmpe_min == 90.0:  # Then we have not clustered them
                wmpe_max = 0.0
                wmpe_min = 0.0
            # TODO: I should also include the generation of some sum file like in the first round

            # TODO: Here, if I do have an ent, perform a postmortem (CAREFUL, THIS IS COPIED FROM ELSEWHERE)

            if ent_path != None:
                table_clust_second_round.write('%-40s %-5s %-10s %-10s %-10s %-10s\n' % (
                'Cluster', 'n_phs', 'wmpd_max', 'wmpd_min', 'phi_cc', 'phi_wmpe'))
            else:
                table_clust_second_round.write(
                    '%-40s %-5s %-10s %-10s %-10s \n' % ('Cluster', 'n_phs', 'wmpd_max', 'wmpd_min', 'phi_cc'))

            #     # 2) Starting from from the phi file
            #     name_shelxe = ((os.path.split(cluster))[1])[:-4]
            #     path_name_shelxe = os.path.join(clust_fold, name_shelxe)
            #     if ent_present:
            #         os.link(ent_filename, path_name_shelxe + ".ent")
            #     os.link(hkl_filename, path_name_shelxe + ".hkl")
            #     os.link(path_ins, path_name_shelxe + ".ins")
            #     output = al.phase_with_shelxe_from_phi(shelxe_line_alixe, name_shelxe, clust_fold, shelxe_path)
            #     lst_file = open(path_name_shelxe + '.lst', 'r')
            #     lst_content = lst_file.read()
            #     list_fom = al.extract_EFOM_and_pseudoCC_shelxe(lst_content)
            #     if ent_present:  # Retrieve final MPE and save them too
            #         list_mpe = al.extract_wMPE_shelxe(clust_fold + name_shelxe + '.lst')
            #         dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['final_MPEs_phi'] = list_mpe
            #     # Soon I will have a version of SHELXE that also computes initCC
            #     # initcc = al.extract_INITCC_shelxe(lst_content)
            #     dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['efom_phi'] = list_fom[0]
            #     dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['pseudocc_phi'] = list_fom[1]
            #     dict_clust_by_rotclu[rotclu][cluster]['dict_FOMs']['CC_phi'] = 0.0

            table_clust_second_round.write('%-40s %-5i %-10f %-10f \n' % (name_cluster, n_phs, wmpe_max, wmpe_min))
        del raw_clust_second_round
        del table_clust_second_round
    return dict_result_by_trial


def startALIXEasPHSTAT(clust_fold, reference_hkl, dict_phs, cell, sg_number, tolerance=75.0, resolution=2.0, cycles=3,
                       f_fom=True):
    """ Minimal version of the ALIXE program.

    :param clust_fold: directory to perform the clustering
    :type clust_fold: str
    :param reference_hkl: the path for the hkl given for shelxe, to filter by evalues the phs in case there is extrapolated data
    :type reference_hkl: str
    :param dict_phs: phs dictionary with values that are the phs and keys set to True if they have to be tested as references and False otherwhise
    :type dict_phs: dict
    :param cell: the unit cell parameters, in the form of a list of floats
    :type cell: list
    :param sg_number: space group number
    :type sg_number: int
    :param tolerance: tolerance for the MPE value between the phase sets
    :type tolerance: float
    :param resolution: resolution to filter the phase sets for combination
    :type resolution: float
    :param cycles: number of macrocycles of combination
    :type cycles: int
    :param f_fom: If true, mpe are weighted by Fvalues, otherwhise, by E values
    :type f_fom: bool
    :return: dictio_clusters
    :rtype: dict
    """

    print '\n ALIXE started at: ', time.strftime("%c")
    start = datetime.datetime.now()
    dictio_clusters = {}  # Dictionary to return the results

    # Get the symmetry information thanks to the sg_number
    symops = al.get_symops_from_sg_dictionary(sg_number)
    polar, origins = al.get_origins_from_sg_dictionary(sg_number)

    # Compute the coefficients needed for other calculations
    unit = cell[0] * cell[1] * cell[2]  # Sides of the cell (abc)
    #print 'SHERLOCK cell ',cell
    coef1 = []
    coef2 = []
    coef3 = []
    list_cos = []
    list_sin = []
    for n in range(0, 3):
        angle_rad = 1.74533 * math.pow(10, -2) * (cell[n + 3])  # Convert to radian units the angles
        #print 'SHERLOCK n, angle_rad',n,angle_rad
        cos_angle = numpy.cos(angle_rad)
        #print 'SHERLOCK cos_angle',cos_angle
        list_cos.append(cos_angle)
        sin_angle = numpy.sin(angle_rad)
        #print 'SHERLOCK sin_angle',sin_angle
        list_sin.append(sin_angle)
        exp1 = 2.0 * unit * (cos_angle / cell[n])  # 2.0 * abc * (cos_angle/side)
        #print 'SHERLOCK exp1 --> 2.0 * abc * (cos_angle/side)',exp1
        coef1.append(exp1)
    volume = unit * math.sqrt(1 - (list_cos[0]) ** 2 - (list_cos[1]) ** 2 - (list_cos[2]) ** 2 + (
    2 * list_cos[0] * list_cos[1] * list_cos[2]))  # V = abc * (1-cos²α-cos²β-cos²γ+2cosαcosβcosγ)^(-1/2)
    #print 'SHERLOCK volume ',volume
    unit = unit / volume # abc / volume
    #print 'SHERLOCK unit abc / volume ',unit
    for n in range(0, 3):
        exp2 = 0.25 * unit * ((list_sin[n] / cell[n]) ** 2)
        #print 'SHERLOCK, n, exp2',n,exp2
        coef2.append(exp2)
    unit = unit / volume # (abc / V) / V , so abc/V²
    #print 'SHERLOCK unit abc/V²', unit
    coef3.append(unit * cell[0] * (list_cos[1] * list_cos[2] - list_cos[0]))  # (abc/V²) * a *(cosβ*cosγ-cosα)
    coef3.append(unit * cell[1] * (list_cos[0] * list_cos[2] - list_cos[1]))  # (abc/V²) * b *(cosα*cosγ-cosβ)
    coef3.append(unit * cell[2] * (list_cos[0] * list_cos[1] - list_cos[2]))  # (abc/V²) * c *(cosα*cosβ-cosγ)
    #print 'SHERLOCK coef3 list',coef3
    #print 'SHERLOCK coef2 list', coef2


    # TODO: Add a filtering for the extrapolated phases in the phs if they exists

    # Generate a list with the phs from the dictionary that are references
    list_references = [phs for _, phs in enumerate(dict_phs.keys()) if dict_phs[phs]]

    # Use the first phs file to compute the evalues and epsilon factors
    ref_for_evalues = list_references[0]
    # Process the array
    array_ref = al.read_phs_file(ref_for_evalues)
    #print 'Resolution check set to ',resolution
    array_ref, max_resolution = al.check_resolution_limit(array_ref, resolution, coef2,
                                          coef3)  # We will use the coefficients saved in coef2 and coef3
    #if max_resolution!=resolution:
    #     print 'Warning: the resolution cut set for phase clustering is of ',resolution
    #     print 'while your data has a maximum resolution of ',max_resolution
         #print 'Automatically adjusting resolution to ',max_resolution
         #resolution=max_resolution
    array_ref = al.change_to_standard_equivalent_reflections(array_ref, sg_number)
    array_ref = al.sort_reflections_phs(array_ref)
    # Get the number of reflections that we expect in all the phs files
    nreflections = len(array_ref)
    # Find epsilon factor and 1/dsquared
    epsilon, onedsquared, res_max = al.get_epsilon_1overdsquared_and_resmax(array_ref, symops, coef2, coef3)
    # Estimate E-values (whats changes in phs is phases, not structure factors)
    array_evalues, array_aux = al.get_evalues_and_array_aux(epsilon, onedsquared, res_max,
                                                            array_ref)  # e-values only in the array_evalues
    #print 'SHERLOCK check finished processing array_ref'
    #sys.exit(0)

    # Save the information that is common to all phs 
    # # # Before
    # array_miller_indices = []
    # array_f_sigf = []
    # for i, _ in enumerate(array_ref):
    #     array_miller_indices.append([array_ref[i][0], array_ref[i][1], array_ref[i][2]])
    #     array_f_sigf.append([array_ref[i][3], array_ref[i][6]])
    # # # After
    array_miller_indices = [ [array_ref[i][0], array_ref[i][1], array_ref[i][2]] for i, _ in enumerate(array_ref)]
    array_f_sigf = [ [array_ref[i][3], array_ref[i][6]] for i, _ in enumerate(array_ref) ]
    array_ref = None

    n_phs = len(dict_phs.keys())
    print "\n Processing ", str(n_phs), " phase files"
    # Prepare the arrays to save
    list_arrays_va_to_modify = [None for x in xrange(n_phs)]
    list_arrays_vb_to_modify = [None for x in xrange(n_phs)]
    list_arrays_to_modify = [None for x in xrange(n_phs)]
    list_names_phs = [None for x in xrange(n_phs)]

    for iphs, phs in enumerate(dict_phs.keys()):
        try:
            if phs[-4:] == ".phi":  # NOTE: My phi files are the same as phs files NOW
                array_phs = al.read_phs_file(phs)
            elif phs[-4:] == ".phs":
                array_phs = al.read_phs_file(phs)
            else:
                print "ALIXE only supports clustering of SHELXE phi or phs files"
                sys.exit(0)
            # Save the name so that we have the correct order
            list_names_phs[iphs] = phs  # phs is the full path of the phs
            # Check resolution limit
            filter_res_array, max_resolution = al.check_resolution_limit(array_phs, resolution, coef2,coef3)
            # Find equivalent reflections with standard indices and transform phases
            array_merged = al.change_to_standard_equivalent_reflections(filter_res_array, sg_number)
            # Sort reflections in order of higher h,k and l indexes
            sorted_array = al.sort_reflections_phs(array_merged)
            new_sorted_array = []
            for r in range(len(sorted_array)):
                if not ((sorted_array[r][0] == array_miller_indices[r][0]) and
                        (sorted_array[r][1] == array_miller_indices[r][1]) and
                        (sorted_array[r][2] == array_miller_indices[r][2])):
                    #print 'SHERLOCK there are non equivalent indices between the arrays'
                    #print 'sorted_array h,k,l',sorted_array[r][0],sorted_array[r][1],sorted_array[r][2]
                    #print 'array_miller_indices h,k,l',array_miller_indices[r][0],array_miller_indices[r][1],array_miller_indices[r][2]
                    #print 'type(sorted_array[r][0])',type(sorted_array[r][0])
                    #print 'type(array_miller_indices[r][0])',type(array_miller_indices[r][0])
                    # NOTE CM: Temporary to see how many reflections have this problem and whether it affects a lot or not
                    continue
                    #sys.exit(0)
                else:
                    new_sorted_array.append(sorted_array[r])

            if len(sorted_array)!=len(new_sorted_array):
                print 'phs with the problem is ',phs
                print 'SHERLOCK len(sorted_array)',len(sorted_array)
                print 'SHERLOCK len(new_sorted_array)',len(new_sorted_array)
                sys.exit(0)
            # Reduce the array to the phi and FOM values
            reduced_array = al.reduce_array_phs_to_PHI_and_FOM(sorted_array)  # [FOM,PHI]
            list_arrays_to_modify[iphs] = reduced_array
            # For all, including the reference, obtain VA and VB
            arrva, arrvb = al.get_VA_and_VB(reduced_array)
            list_arrays_va_to_modify[iphs] = arrva
            list_arrays_vb_to_modify[iphs] = arrvb
        except:
            print '\n Attention: Some error happened during processing of file ', phs
            sys.exit(0)

    print '\n Finished reading the phs files'

    # Save the arrays as pickle objects
    save_double_array = open(os.path.join(clust_fold, 'double_array.pkl'), 'wb')
    cPickle.dump(list_arrays_to_modify, save_double_array)
    save_double_array.close()
    save_arrva = open(os.path.join(clust_fold, 'arrva.pkl'), 'wb')
    cPickle.dump(list_arrays_va_to_modify, save_arrva)
    save_arrva.close()
    save_arrvb = open(os.path.join(clust_fold, 'arrvb.pkl'), 'wb')
    cPickle.dump(list_arrays_vb_to_modify, save_arrvb)
    save_arrvb.close()

    # Now test all references in the list
    for _, reference in enumerate(list_references):
        print "\n Testing reference", reference
        name_phi = (os.path.split(reference)[1])[:-4] + '_ref.phi'
        path_phi = os.path.join(clust_fold, name_phi)
        position = list_names_phs.index(reference)
        dictio_clusters[path_phi] = {}
        # We load the arrays again for each reference to make sure we have the unmodified original ones
        back_double_array = open(os.path.join(clust_fold, 'double_array.pkl'), 'rb')
        list_arrays_to_modify = cPickle.load(back_double_array)
        back_double_array.close()
        array_ref = copy.deepcopy(list_arrays_to_modify[position])
        back_arrva = open(os.path.join(clust_fold, 'arrva.pkl'), 'rb')
        list_arrays_va_to_modify = cPickle.load(back_arrva)
        back_arrva.close()
        back_arrvb = open(os.path.join(clust_fold, 'arrvb.pkl'), 'rb')
        list_arrays_vb_to_modify = cPickle.load(back_arrvb)
        back_arrvb.close()
        # Phase combination macrocycles
        for c in range(cycles):
            print '\n Cluster analysis cycle ', str(c + 1)
            print '\n N' + '\t' + 'wMPE' + '\t' + 'Dif' + '\t' + 'MapCC' + '\t' + 'Origin shift' + '\t\t' + 'Phase file'
            dictio_clusters[path_phi][c + 1] = {}  # We will save the results cycle by cycle
            # For every phs, find and apply origin shifts relative to reference phases
            dict_wmpes_sel = {}
            list_wmpes_sel = []
            for pos, _ in enumerate(list_arrays_to_modify):
                name_current_phs = list_names_phs[pos]
                dict_wmpes_sel[name_current_phs] = {"wMPE": 0.0, "diff_wMPE": 0.0, "mapcc": 0.0}
                s = 0.0
                t = 0.0
                # Check that the number of reflections is the expected one (all should have the same)
                nreflections_current = len(list_arrays_to_modify[pos])
                if nreflections_current != nreflections:
                    print 'The number of reflections of this phase file is not compatible with the reference file'
                    print 'Please check, some error in the files is expected'
                    print 'SHERLOCK nreflections',nreflections
                    print 'SHERLOCK nreflections_current',nreflections_current
                    sys.exit(0)
                for r, _ in enumerate(list_arrays_to_modify[pos]):
                    list_arrays_to_modify[pos][r][1] = list_arrays_vb_to_modify[pos][r]  # Phases setting
                    # Check the FOM to be set
                    if f_fom == True:
                        list_arrays_to_modify[pos][r][0] = array_f_sigf[r][0] * list_arrays_va_to_modify[pos][
                            r]  # Structure Factor current reflection * FOM current reflection
                    elif f_fom == False:
                        list_arrays_to_modify[pos][r][0] = array_evalues[r] * list_arrays_va_to_modify[pos][
                            r]  # E-value current reflection * FOM current reflection
                    s = s + list_arrays_to_modify[pos][r][0] # Summatory of the FOMs
                    t = t + list_arrays_to_modify[pos][r][0] * abs(
                        ((900.0 + list_arrays_to_modify[pos][r][1] - list_arrays_vb_to_modify[pos][r]) % 360.0) - 180.0)
                # Here is where when we have to apply the origin shifts and calculate the wMPE and the mapCC
                current_weights = list_arrays_va_to_modify[pos]  # array with the FOMs of the current phs
                sorted_list_wmpe, sorted_list_mapcc = al.apply_origin_shift_and_compute_wMPE_and_CC(n_reflections=nreflections,
                                                                                                    symops=symops,
                                                                                                    array_ref=array_ref,
                                                                                                    array_miller_indices=
                                                                                                    array_miller_indices,
                                                                                                    array_f_sigf=array_f_sigf,
                                                                                                    current_array=
                                                                                                    list_arrays_to_modify[pos],
                                                                                                    current_weights=
                                                                                                    current_weights,
                                                                                                    array_evalues=
                                                                                                    array_evalues,
                                                                                                    array_aux=array_aux,
                                                                                                    sg_number=sg_number,
                                                                                                    f_fom=f_fom)
                shift_to_apply = sorted_list_wmpe[0][1]
                wmpe_shift = sorted_list_wmpe[0][0]
                for i in range(len(sorted_list_mapcc)):  # Get the mapCC that corresponds to that shift
                    if sorted_list_mapcc[i][1] == shift_to_apply:
                        map_CC = sorted_list_mapcc[i][0]
                # Get difference top best/second best for the wMPE if we are not in a polar sg
                if polar == False:
                    diff_mpe = sorted_list_wmpe[1][0] - sorted_list_wmpe[0][0]
                elif polar == True:
                    diff_mpe = 0
                dict_wmpes_sel[name_current_phs] = {"wMPE": wmpe_shift, "diff_wMPE": diff_mpe, "mapcc": map_CC,
                                                    'shift': shift_to_apply}
                list_wmpes_sel.append((name_current_phs, wmpe_shift))
                for r, _ in enumerate(list_arrays_vb_to_modify[pos]):  # Modify the phases saved
                    list_arrays_vb_to_modify[pos][r] = ((720.0 + (360.0 * (((
                                                                            shift_to_apply[0] * array_miller_indices[r][
                                                                                0]) + (
                                                                            shift_to_apply[1] * array_miller_indices[r][
                                                                                1]) + (
                                                                            shift_to_apply[2] * array_miller_indices[r][
                                                                                2])) % 1.0)) +
                                                         list_arrays_vb_to_modify[pos][r]) % 360.0)

            # Sort the phase sets according to their mean phase error
            sorted_by_mpe = sorted(list_wmpes_sel, key=lambda x: x[1], reverse=False)
            # Check if anything will cluster under the tolerance we set
            if len(sorted_by_mpe) > 1:
                if sorted_by_mpe[1][1] > tolerance:
                    print 'There are not solutions to cluster under the tolerance set'
                    #print '**********************************'
                    #print 'SHERLOCK sorted_by_mpe'
                    #for ele in sorted_by_mpe:
                    #    print ele
                    #print '**********************************'
                    if c + 1 != 1:
                        print 'HEY, THIS HAPPENED IN A CYCLE DIFFERENT FROM CYCLE 1'
                        print 'Error, please report to bugs-borges@ibmb.csic.es'
                        sys.exit(0)
                    dictio_clusters[path_phi] = {sorted_by_mpe[0][0]: {'wMPE': sorted_by_mpe[0][1],
                                                                       'diff_wMPE': dict_wmpes_sel[sorted_by_mpe[0][0]][
                                                                           'diff_wMPE'],
                                                                       'mapcc': dict_wmpes_sel[sorted_by_mpe[0][0]][
                                                                           'mapcc'], 'shift': [0.0, 0.0, 0.0]}}
                    # Write the phases with the resolution cut to a file
                    file_phi = open(path_phi, 'w')
                    pos = list_names_phs.index(sorted_by_mpe[0][0])  # Position of the reference array in the reading
                    nreflections = len(list_arrays_va_to_modify[pos])
                    for r in xrange(nreflections):
                        # 3I4,F9.2,F8.4,F8.1,F8.2
                        file_phi.write('%4i%4i%4i%9.2f%8.4f%8.1f%8.2f\n' % (
                        array_miller_indices[r][0], array_miller_indices[r][1], array_miller_indices[r][2],
                        array_f_sigf[r][0], list_arrays_va_to_modify[pos][r], list_arrays_vb_to_modify[pos][r],
                        array_f_sigf[r][1]))
                    del file_phi
                    return dictio_clusters

            # Combine phases for cluster
            # 1) Generate clean arrays of contributions VA and VB and for the combination
            va = [0.0 for _ in range(len(array_ref))]  # fom
            vb = [0.0 for _ in range(len(array_ref))]  # phases
            wa_combi = [0.0 for _ in range(len(array_ref))]
            # 2) Iterate over the phs files (consider sorting)
            for ind in range(len(sorted_by_mpe)):
                current_phs = sorted_by_mpe[ind][0]
                current_wmpe = sorted_by_mpe[ind][1]
                current_dif_wmpe = dict_wmpes_sel[current_phs]['diff_wMPE']
                current_mapcc = dict_wmpes_sel[current_phs]['mapcc']
                current_shift = dict_wmpes_sel[current_phs]['shift']
                pos = list_names_phs.index(current_phs)
                if current_wmpe < tolerance:
                    print ' ', ind + 1, '\t', "{0:.1f}".format(current_wmpe), '\t', "{0:.1f}".format(
                        current_dif_wmpe), '\t', "{0:.2f}".format(current_mapcc), '\t', current_shift,'\t' ,current_phs
                    dictio_clusters[path_phi][c + 1][current_phs] = copy.deepcopy(dict_wmpes_sel[current_phs])
                    for r in xrange(nreflections):
                        list_arrays_to_modify[pos][r][1] = list_arrays_vb_to_modify[pos][r]
                        t = 0.0174533 * list_arrays_to_modify[pos][r][1]  # 0.0174533 is 2pi/360
                        s = list_arrays_va_to_modify[pos][r]
                        va[r] = va[r] + (s * (numpy.cos(t)))
                        vb[r] = vb[r] + (s * (numpy.sin(t)))
                    t = numpy.sqrt(1.0 / (ind + 1))
                    for r in xrange(nreflections):
                        wa_combi[r] = min(1.0, numpy.sqrt(math.pow(va[r], 2) + math.pow(vb[r], 2)) * t)
                        # Use either structure factors or normalized structure factors for the combined phases
                        list_arrays_to_modify[pos][r][0] = wa_combi[r] * array_evalues[
                            r]  # e-weighted,as it is in the fortran prototype
                        ##                        if f_fom==True:
                        ##                            list_arrays_to_modify[pos][r][0]=array_f_sigf[r][0]*wa_combi[r] #  StructureFactor * new_weight
                        ##                        elif f_fom==False:
                        ##                            alist_arrays_to_modify[pos][r][0]=array_evalues[r]*wa_combi[r] # E-value * new_weight
                        if wa_combi[r] > 0.0001:
                            list_arrays_to_modify[pos][r][1] = (720.0 + 57.29578 * numpy.arctan2(vb[r], va[r])) % 360
                        # NOTE: experimenting what is happening here
                        #current_weights[r] = list_arrays_to_modify[pos][r][0] # Save the new weight
                        # NOTE: experimenting what is happening here
                    # Compute again the shift, because now we changed the phases
                    sorted_list_wmpe2, sorted_list_mapcc2 = al.apply_origin_shift_and_compute_wMPE_and_CC(n_reflections
                                                                                                          =nreflections,
                                                                                                          symops=symops,
                                                                                                          array_ref=
                                                                                                          array_ref,
                                                                                                          array_miller_indices=array_miller_indices,
                                                                                                          array_f_sigf=array_f_sigf,
                                                                                                          current_array=list_arrays_to_modify[
                                                                                                              pos],
                                                                                                          current_weights=current_weights,
                                                                                                          array_evalues=array_evalues,
                                                                                                          array_aux=array_aux,
                                                                                                          sg_number=sg_number,
                                                                                                          f_fom=f_fom)
                    shift_to_apply2 = sorted_list_wmpe2[0][1]
                    if shift_to_apply2 != [0.0, 0.0, 0.0]:  # Check if there ever is another shift after
                        if not (abs(shift_to_apply2[0]) < 0.01 and abs(shift_to_apply2[1]) < 0.01 and abs(
                                shift_to_apply2[2]) < 0.01):
                            print "There is another shift to apply after phase merging ", shift_to_apply2
                            #sys.exit(0)
                            print "Applying it"
                            for r in xrange(nreflections):
                                list_arrays_to_modify[pos][r][1] = ((720.0 + (360.0 * (((
                                                                            shift_to_apply2[0] * array_miller_indices[r][
                                                                                0]) + (
                                                                            shift_to_apply2[1] * array_miller_indices[r][
                                                                                1]) + (
                                                                            shift_to_apply2[2] * array_miller_indices[r][
                                                                                2])) % 1.0)) +
                                                         list_arrays_vb_to_modify[pos][r]) % 360.0)
                    # Change the phases in the reference array so that they correspond to the combined map                                                 list_arrays_to_modify[pos][r][1]) % 360.0)
                    for r in xrange(nreflections):
                        array_ref[r][1] = list_arrays_to_modify[pos][r][1]
        # Write the cumulative phases to a file
        file_phi = open(path_phi, 'w')
        # print 'path_phi',path_phi
        for r in xrange(len(array_ref)):
            # 3I4,F9.2,F8.4,F8.1,F8.2
            file_phi.write('%4i%4i%4i%9.2f%8.4f%8.1f%8.2f\n' % (
            array_miller_indices[r][0], array_miller_indices[r][1], array_miller_indices[r][2], array_f_sigf[r][0],
            wa_combi[r], array_ref[r][1], array_f_sigf[r][1]))
        del file_phi

    print '\n Cleaning up....'
    for fich in os.listdir(clust_fold):
        if fich.endswith('.pkl'):
            os.remove(os.path.join(clust_fold, fich))
    # Return just the last cycle results
    # dictio_clusters_third = {}
    # for key in dictio_clusters.keys():
    #     dictio_clusters_third[key] = dictio_clusters[key][cycles]
    # end = datetime.datetime.now()
    # print " ALIXE took  ", end - start, "to run"
    # return dictio_clusters_third
    # NOTE CM: do we really only want the last cycle?
    # NOTE CM: first cycle is more representative of what has happened with the original files
    dictio_clusters_first = {}
    for key in dictio_clusters.keys():
        dictio_clusters_first[key] = dictio_clusters[key][1]
    #print 'SHERLOCK dictio_clusters_first',dictio_clusters_first
    #sys.exit(0)
    return dictio_clusters_first




def startALIXEforARCIMBOLDO(clust_fold, cluster_id, reference_hkl, cell, sg_symbol, tolerance_list=[60.0, 88.0],
                            resolution=2.0, cycles=3, f_fom=True, run='SHREDDER', mode='one_step',
                            confibor=None,input_mode=9):
    """ Performs ALIXE phase clustering internally within the ARCIMBOLDO programs.

    Keyword arguments:
    clust_fold -- path to the folder where to perform the clustering
    cluster_id -- integer with the rotation cluster to evaluate or list with the cluster ids if mode=two_steps
    reference_hkl -- path to hkl file
    cell -- list of 6 elements with the unit cell parameters (STR! CONVERT TO FLOAT)
    sg_symbol -- string with the space group symbol
    tolerance -- list of floats with tolerances for mean phase error
    cycles -- integer, number of cycles of phase combination to be performed
    f_fom -- boolean. If true, mpe are weighted by Fvalues, otherwhise, by E values
    run -- string. Can be 'ARCIMBOLDO', 'BORGES', 'SHREDDER'
    mode -- string. Can be 'fish','full','one_step','two_steps'
    confibor -- ConfigParser object from the main program that is calling ALIXE
    input_mode -- can be 9, 9.5 or 9.6. By default 9, and it means from which folder will the phs files be taken
    """

    print '\n ALIXE started: ', time.strftime("%c")
    skip_FOM_reading = False
    ent_present = False
    hard_limit_phs = 0 # NOTE CM: change it to automatic decision depending on hardware
    skip_copyfiles = False


    if mode not in ['one_step', 'two_steps']:
        print "Sorry, you need to provide a valid mode for alixe: either 'one_step' or 'two_steps' "
        sys.exit(0)

    # Check if alixe has been already performed on that folder and act accordingly depending on mode
    basepath_clustfold = clust_fold
    print "\n Root folder for clustering ", basepath_clustfold
    print '\n Mode for clustering is ',mode

    if mode=='one_step':
        clust_fold = os.path.join(basepath_clustfold, str(cluster_id))
        print "\n Currently processing folder ", clust_fold
        path_for_tuple = os.path.join(clust_fold, 'final_alixe_tuple.pkl')
        if os.path.exists(path_for_tuple):  # Then first round was completed
            back_final_tuple = open(path_for_tuple, 'rb')
            (path_ins, final_dict) = cPickle.load(back_final_tuple)
            print "\n Alixe first round has run succesfully already on this folder"
            print "\n Returning the results"
            # Return only the clusters that contain more than one phase set so that they are expanded
            for cluster in final_dict.keys():
                if final_dict[cluster]['n_phs'] == 1:
                    del final_dict[cluster]
            print "\n",len(final_dict),' phase clusters contain more than one phase set and will be expanded'
            return (path_ins, final_dict)
        else: # Either we have an incomplete run or it was not created yet
            print 'Alixe was not finished in this folder ',clust_fold
            if not os.path.exists(clust_fold):
                os.makedirs(clust_fold)  # Generate the directory if it is not already there
            else: # Otherwhise remove it and generate it from the beginning
                shutil.rmtree(clust_fold)
                os.makedirs(clust_fold)

    elif mode == 'two_steps':
        second_round_clufold = os.path.join(basepath_clustfold, 'R2')
        # First check whether we were finished and can proceed directly to expansions
        path_for_tuple = os.path.join(second_round_clufold, 'tuple_second_round_alixe.pkl')
        if os.path.exists(path_for_tuple):  # Then first round was completed
            back_final_tuple = open(path_for_tuple, 'rb')
            (path_ins, final_dict) = cPickle.load(back_final_tuple)
            print "\n Alixe second round has run succesfully already on this folder"
            print "\n Returning the results"
            # Return only the clusters that contain more than one phase set so that they are expanded
            for cluster in final_dict.keys():
                if final_dict[cluster]['n_phs'] == 1:
                    del final_dict[cluster]
            print "\n",len(final_dict),' phase clusters contain more than one phase set and will be expanded'
            return (path_ins, final_dict)
        # In any case we do not need to reperform steps
        skip_FOM_reading = True
        skip_copyfiles = True


    # Generate the symmetry files
    cell = [ float(cell[i]) for i in range(len(cell)) ]
    sg_number = al.get_space_group_number_from_symbol(sg_symbol)
    path_ins = os.path.join(clust_fold, 'name.ins')
    path_sym = os.path.join(clust_fold, 'name.pda')
    al.generate_fake_ins_for_shelxe(path_ins, cell, sg_number)
    al.generate_fake_pda_for_phstat(path_sym, cell, sg_number)

    if run == 'SHREDDER' or run == 'BORGES':
        if not isinstance(confibor, ConfigParser.ConfigParser):
            print "Sorry, you need to provide a valid bor object in order to run ALIXE on ", run  # Check the bor
            sys.exit()
        topexp = confibor.get('ARCIMBOLDO-BORGES', 'topexp')
        basepath = confibor.get('GENERAL', 'working_directory')
        if not skip_copyfiles:
            list_chosen = al.get_files_from_9_EXP_BORGES(basepath, clust_fold, cluster_id=cluster_id, mode=input_mode,
                                                         hard_limit_phs=hard_limit_phs)

        subrun = 'BORGES'  # To know how to read the solutions. Spherical is generating a BORGESARCI job
        if confibor.has_option('GENERAL', 'ent_path'):  # therefore the lst will have post mortem info
            ent_path = confibor.get('GENERAL', 'ent_path')
            if os.path.exists(ent_path):
                ent_present = True
    else:
        print "Sorry, ALIXE can just run on ARCIMBOLDO_SHREDDER spheres, or ARCIMBOLDO_BORGES runs"
        sys.exit(0)

    # Read the FOMs of the phs files in the phaser and shelxe steps
    if not skip_FOM_reading:
        phs_files = al.list_files_by_extension(clust_fold, 'phs')
        dictio_fragments = {}
        for phs in phs_files:
            dictio_fragments[phs[:-4]] = {'rot_cluster': None, 'llg': None, 'zscore': None, 'initcc': None,
                                          'efom': None, 'pseudocc': None, 'list_MPE': None}
        dictio_fragments = al.get_FOMs_from_lst_files_in_folder(dictio_fragments=dictio_fragments,
                                                                ent_present=ent_present)
        dictio_fragments = al.get_FOMs_from_sum_files_in_folder(wd=basepath, clust_fold=clust_fold,
                                                                dictio_fragments=dictio_fragments,
                                                                gimble=True,
                                                                program=subrun, fragment=1)

    # First round

    if mode == 'one_step':
        tolerance = tolerance_list[0]
        dict_first_round = {}  # To save the results per rotation cluster
        #print 'SHERLOCK clust_fold', clust_fold
        #print 'SHERLOCK os.path.join(basepath_clustfold,str(cluster_id))',os.path.join(basepath_clustfold,str(cluster_id))
        #wd=os.path.relpath(wd, start=os.path.join(arciwd,'ARCIMBOLDO_BORGES'))
        #print("SHERLOCK: wd is {}\n\n".format(wd))
        if run == 'SHREDDER':
            clust_fold_rel = os.path.join("./ARCIMBOLDO_BORGES/11.5_CLUSTERING/", os.path.basename(clust_fold))
            print '1SHERLOCK clust_fold_rel',clust_fold_rel
            clust_fold_rel = os.path.relpath(clust_fold, start="./ARCIMBOLDO_BORGES/11.5_CLUSTERING/")
            print '2SHERLOCK clust_fold_rel',clust_fold_rel
            clust_fold_rel =  os.path.relpath(os.path.join(basepath,"11.5_CLUSTERING", os.path.basename(clust_fold)))
        elif run == 'BORGES':
            #clust_fold_rel = os.path.join("./11.5_CLUSTERING/", os.path.basename(clust_fold))
            clust_fold_rel =  os.path.relpath(os.path.join(basepath,"11.5_CLUSTERING", os.path.basename(clust_fold)))
        print 'SHERLOCK len(clust_fold_rel)',len(clust_fold_rel)
        print 'SHERLOCK clust_fold_rel',clust_fold_rel
        #quit() 

        # 1) Write an ls file with the list of phs
        path_ls = os.path.join(clust_fold, "first_round.ls")
        lsrotfile = open(path_ls, 'w')
        # NOTE: I need to use a relative path because fortran does not accept such long paths
        for i in range(len(list_chosen)):
            phs_namefile = (os.path.split(list_chosen[i]))[1]
            phs_relative_path = os.path.join(clust_fold_rel, phs_namefile)
            lsrotfile.write(phs_relative_path + '\n')
        lsrotfile.close()
        # 2.1) Link the ins file
        if not os.path.exists(os.path.join(clust_fold, "first_round.ins")):
            os.link(path_ins, os.path.join(clust_fold, "first_round.ins"))
        # 2.2) Link the pda file
        if not os.path.exists(os.path.join(clust_fold, "first_round.pda")):
            os.link(path_sym, os.path.join(clust_fold, "first_round.pda"))
        # 3) Launch the function in alixe_library
        # use or not fft depending on space group
        if dictio_space_groups[sg_number]['polar'] and sg_number==1: # at the moment I am interested in testing fast!
            orisub='sxosfft'
        else:
            orisub='sxos'
        dict_first_round = al.clustering_phstat_isa_under_a_tolerance(name_phstat='first_round', wd=clust_fold_rel,
                                                             path_phstat=SELSLIB2.PATH_PHSTAT, tolerance=tolerance,
                                                          resolution=resolution, seed=0, n_cycles=cycles,
                                                          orisub=orisub, weight='e')

        for keyphs in dict_first_round.keys():
            new_key = os.path.abspath(keyphs)
            dict_first_round[new_key] = copy.deepcopy(dict_first_round[keyphs])
            del dict_first_round[keyphs]


        # Save the FOM information for priorization in second round if there is
        for cluster in dict_first_round.keys():
            if dict_first_round[cluster]['n_phs'] > 1:
                #print 'SHERLOCK dict_first_round[cluster]',dict_first_round[cluster]
                list_llg = []
                list_zscore = []
                for phs in dict_first_round[cluster]['dictio_result'].keys():  # For each phs in the cluster
                    #print 'SHERLOCK phs',phs
                    fullpath_file = os.path.abspath(phs)
                    list_llg.append(dictio_fragments[fullpath_file[:-4]]['llg'])
                    list_zscore.append(dictio_fragments[fullpath_file[:-4]]['zscore'])
                # We add the top LLG or ZSCORE as representative of the cluster
                dict_first_round[cluster]['dict_FOMs']['llg'] = (sorted(list_llg, reverse=True))[0]
                dict_first_round[cluster]['dict_FOMs']['zscore'] = (sorted(list_zscore, reverse=True))[0]
            elif dict_first_round[cluster]['n_phs'] == 1:
                name_file = ((dict_first_round[cluster]['dictio_result'].keys())[0])[:-4]
                fullpath_file = os.path.abspath(name_file)
                #print 'SHERLOCK name_file',name_file
                #print 'SHERLOCK fullpath_file',fullpath_file
                #print 'SHERLOCK dict_first_round[cluster]',dict_first_round[cluster]
                dict_first_round[cluster]['dict_FOMs']['llg'] = dictio_fragments[fullpath_file]['llg']
                dict_first_round[cluster]['dict_FOMs']['zscore'] = dictio_fragments[fullpath_file]['zscore']
        save_final_tuple = open(os.path.join(clust_fold, 'final_alixe_tuple.pkl'), 'wb')
        cPickle.dump((path_ins, dict_first_round), save_final_tuple)
        save_final_tuple.close()

        # Write a summary output table with useful information from the first round that can be sortable
        global_table=open(os.path.join(clust_fold, 'global_clusters_table.txt'), 'w')
        global_table.write('%-40s %-10s %-10s %-10s\n' % ('Cluster', 'n_phs', 'topLLG', 'topZSCORE'))
        for cluster in dict_first_round.keys():
            # TODO: write also the rest of the information about the cluster in the table
            basenameclu = os.path.basename(cluster)
            n_phs = dict_first_round[cluster]['n_phs']
            topLLG = dict_first_round[cluster]['dict_FOMs']['llg']
            topZscore = dict_first_round[cluster]['dict_FOMs']['zscore']
            global_table.write('%-40s %-10s %-10s %-10s\n' % (basenameclu, n_phs, topLLG, topZscore))
        del global_table

        # Prepare to return only the clusters that contain more than one phase set so that they are expanded
        print " \n There are ", len(dict_first_round)," phase sets after the first round of phase combination"
        for cluster in dict_first_round.keys():
            if dict_first_round[cluster]['n_phs'] == 1:
                del dict_first_round[cluster]
        print " \n There are ",len(dict_first_round)," phase sets that contained more than one solution"

        for cluster in dict_first_round.keys():
            path_clu = os.path.join(clust_fold, os.path.basename(cluster)[:-4] + '.sum')
            #print 'SHERLOCK path_clu',path_clu
            fileforclu = open(path_clu, 'w')
            fileforclu.write(
                '%-40s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s\n' % (
                'Name', 'wMPD_f', 'wMPD_l', 'diffwMPD_f','diffwMPD_l', 'mapcc_f',
                'mapcc_l', 'shift_f_x', 'shift_f_y', 'shift_f_z', 'shift_l_x', 'shift_l_y',
                'shift_l_z'))
            for phaseset in dict_first_round[cluster]['dictio_result'].keys():
                name = os.path.basename(phaseset)
                #print "SHERLOCK dict_first_round[cluster]['dictio_result'][phaseset].keys()",dict_first_round[cluster]['dictio_result'][phaseset].keys()
                wmpe_first = round(dict_first_round[cluster]['dictio_result'][phaseset]['wMPE_first'], 2)
                wmpe_last = round(dict_first_round[cluster]['dictio_result'][phaseset]['wMPE_last'], 2)
                diff_wmpe_first = round(dict_first_round[cluster]['dictio_result'][phaseset]['diff_wMPE_first'],2)
                diff_wmpe_last = round(dict_first_round[cluster]['dictio_result'][phaseset]['diff_wMPE_last'], 2)
                mapcc_first = round(dict_first_round[cluster]['dictio_result'][phaseset]['mapcc_first'],2)
                mapcc_last = round(dict_first_round[cluster]['dictio_result'][phaseset]['mapcc_last'],2)
                shift_first = dict_first_round[cluster]['dictio_result'][phaseset]['shift_first']
                shift_last = dict_first_round[cluster]['dictio_result'][phaseset]['shift_last']
                fileforclu.write(
                    '%-40s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s\n' % (
                    name, wmpe_first, wmpe_last,
                    diff_wmpe_first,
                    diff_wmpe_last,
                    mapcc_first,
                    mapcc_last,
                    shift_first[0],
                    shift_first[1],
                    shift_first[2],
                    shift_last[0],
                    shift_last[1],
                    shift_last[2]))
            del (fileforclu)
        #print 'SHERLOCK quit and check'
        #quit()
        return (path_ins, dict_first_round)

    # Second round
    if mode == 'two_steps':
        tolerance = tolerance_list[1]

        # Generate the folder in which we will perform the combination
        second_round_clufold = os.path.join(basepath_clustfold,'R2')
        try:
            os.makedirs(second_round_clufold)
        except:
            #print sys.exc_info()
            #traceback.print_exc(file=sys.stdout)
            shutil.rmtree(second_round_clufold)
            os.makedirs(second_round_clufold)

        clust_fold = os.path.join(clust_fold, 'R2')
        if run == 'SHREDDER':
            clust_fold_rel = "./ARCIMBOLDO_BORGES/11.5_CLUSTERING/R2"
        elif run == 'BORGES':
            clust_fold_rel = "./11.5_CLUSTERING/R2"

        # Read all dictionaries from all rotation clusters
        list_phis_to_evaluate = []  # List with tuples (rotclu,cc,phi) for sorting the files according to FOM
        for clu in cluster_id:
            path_pkl = os.path.join(basepath_clustfold +str(clu)+'/final_alixe_tuple.pkl')
            pkl_first_round = open(path_pkl, 'rb')
            path_ins, dictio_clust_first_round = cPickle.load(pkl_first_round)
            for phi_file in dictio_clust_first_round.keys():
                list_phis_to_evaluate.append((phi_file,
                                              dictio_clust_first_round[phi_file]['dict_FOMs']['llg']))
        # NOTE CM: at the moment I am using the topLLG of the solutions in every cluster from the first round, I should
        # include other foms and evaluate which ones work better
        sorted_list_phis_to_evaluate = sorted(list_phis_to_evaluate, key=operator.itemgetter(1),reverse=True)
        sorted_list_phis = [ele[0] for ele in sorted_list_phis_to_evaluate]
        # 1) Write an ls file with the list of phs
        path_ls = os.path.join(clust_fold, "second_round.ls")
        lsrotfile = open(path_ls, 'w')
        # NOTE: I need to use a relative path because fortran does not accept such long paths
        for i in range(len(sorted_list_phis)):
            phs_fullpath=sorted_list_phis[i]
            phs_namefile = (os.path.split(sorted_list_phis[i]))[1]
            phs_relative_path = os.path.join(clust_fold_rel, phs_namefile)
            phs_dest_path = os.path.join(clust_fold,phs_namefile)
            # I also need to link the files from their original folders
            os.link(phs_fullpath,phs_dest_path)
            lsrotfile.write(phs_relative_path + '\n')
        lsrotfile.close()
        # 2.1) Link the ins file
        if not os.path.exists(os.path.join(clust_fold, "second_round.ins")):
            #print 'SHERLOCK path_ins ', path_ins
            #print 'SHERLOCK os.path.join(clust_fold, "second_round.ins") ', os.path.join(clust_fold, "second_round.ins")
            os.link(path_ins, os.path.join(clust_fold, "second_round.ins"))
        # 2.2) Link the pda file
        if not os.path.exists(os.path.join(clust_fold, "second_round.pda")):
            #print 'SHERLOCK path_sym ', path_sym
            #print 'SHERLOCK os.path.join(clust_fold, "second_round.pda") ', os.path.join(clust_fold, "second_round.pda")
            os.link(path_sym, os.path.join(clust_fold, "second_round.pda"))
        # 3) Launch the function in alixe_library
        # use or not fft depending on space group
        if dictio_space_groups[sg_number]['polar'] and sg_number == 1:  # at the moment I am interested in testing fast!
            orisub = 'sxosfft'
        else:
            orisub = 'sxos'

        dict_second_round = al.clustering_phstat_isa_under_a_tolerance(name_phstat='second_round', wd=clust_fold_rel,
                                                                       path_phstat=SELSLIB2.PATH_PHSTAT,
                                                                       tolerance=tolerance, resolution=resolution,
                                                                       seed=0, n_cycles=cycles,
                                                                       orisub=orisub, weight='e')

        for keyphs in dict_second_round.keys():
            new_key = os.path.abspath(keyphs)
            dict_second_round[new_key] = copy.deepcopy(dict_second_round[keyphs])
            del dict_second_round[keyphs]


        # Write a summary output table with useful information from the first round that can be sortable
        global_table=open(os.path.join(second_round_clufold, 'global_clusters_table_second_round.txt'), 'w')
        global_table.write('%-40s %-10s\n' % ('Cluster', 'n_phs'))
        for cluster in dict_second_round.keys():
            basenameclu = os.path.basename(cluster)
            n_phs = dict_second_round[cluster]['n_phs']
            global_table.write('%-40s %-10s \n' % (basenameclu, n_phs))
        del global_table

        # Write a pkl file to avoid recomputation if it is not required
        save_second_round_tuple = open(os.path.join(second_round_clufold, 'tuple_second_round_alixe.pkl'), 'wb')
        cPickle.dump((path_ins, dict_second_round), save_second_round_tuple)
        save_second_round_tuple.close()

        # Prepare to return only the clusters that contain more than one phase set so that they are expanded
        print " \n There are ", len(dict_second_round)," phase sets after the first round of phase combination"
        for cluster in dict_second_round.keys():
            if dict_second_round[cluster]['n_phs'] == 1:
                del dict_second_round[cluster]
        print " \n There are ",len(dict_second_round)," phase sets that contained more than one solution"

        # For every cluster to be expanded, write a summary table file with the information of its contents
        # for cluster in dict_second_round.keys():
        #     path_clu=os.path.join(second_round_clufold, os.path.basename(cluster)[:-4]+'.sum')
        #     fileforclu=open(path_clu, 'w')
        #     fileforclu.write('%-40s %-10s %-10s %-10s %-20s\n' % ('Name of the phs file', 'wMPD', 'diff wMPD', 'map CC',
        #                                                           'shift'))
        #     for phaseset in dict_second_round[cluster]['dictio_result'].keys():
        #         name = os.path.basename(phaseset)
        #         wmpe = round(dict_second_round[cluster]['dictio_result'][phaseset]['wMPE'],2)
        #         diffwmpe = round(dict_second_round[cluster]['dictio_result'][phaseset]['diff_wMPE'],2)
        #         mapcc = round(dict_second_round[cluster]['dictio_result'][phaseset]['mapcc'])
        #         shiftval = dict_second_round[cluster]['dictio_result'][phaseset]['shift']
        #         shift='x = '+str(shiftval[0])+' y = '+str(shiftval[1])+' z = '+str(shiftval[2])
        #         fileforclu.write(
        #             '%-40s %-10s %-10s %-10s %-20s\n' % (name, wmpe, diffwmpe, mapcc, shift))
        #     del(fileforclu)

        return (path_ins, dict_second_round)



def clustering_all_in_ALIXE_under_a_tolerance_python(clust_fold, reference_hkl, list_phs, cell, sg_symbol, tolerance,
                                              resolution, cycles, fom_weigth, ncores):
    '''Sequentially calls startALIXE in order to generate all possible clusters under a certain tolerance.

    :param clust_fold:
    :type clust_fold: str
    :param reference_hkl:
    :type reference_hkl: str
    :param list_phs:
    :type list_phs: list
    :param cell:
    :type cell: list
    :param sg_symbol:
    :type sg_symbol: str
    :param tolerance:
    :type tolerance: float
    :param resolution:
    :type resolution: float
    :param cycles:
    :type cycles: int
    :param fom_weigth: if True, weight applied is by Structure Factors, if False, by E-values
    :type fom_weigth: bool
    :param ncores:
    :type ncores: int
    :return dictio_clusters:  a dictionary with the results of the clustering.
    Keys are phi paths, and value is another dictionary with the following structure:
    :rtype dictio_clusters: dict


    '''
    # Initialize required variables
    dictio_clusters = {}
    sg_number = al.get_space_group_number_from_symbol(sg_symbol)

    # Main loop, until all the phs in the list have been processed or we will not expand them anyway
    while (len(list_phs) > 0) and (len(dictio_clusters.keys()) <= ncores):
        dict_phs = {}
        for i in range(len(list_phs)):
            if i == 0:
                dict_phs[list_phs[i]] = True
            else:
                dict_phs[list_phs[i]] = False
        results = startALIXEasPHSTAT(clust_fold, reference_hkl, dict_phs, cell, sg_number, tolerance, resolution,
                                     cycles, fom_weigth)
        # I can safely assume that if I just give one reference,
        # the results dictionary keys list will have just one phi name
        phi_name = results.keys()[0]
        phs_to_remove = results[phi_name].keys()
        n_phs = len(phs_to_remove)
        #print 'SHERLOCK results', results
        dictio_clusters[phi_name] = {'dictio_result': results[phi_name], 'n_phs': n_phs, 'dict_FOMs': {}}
        #print 'SHERLOCK phi_name',phi_name
        #for key in dictio_clusters[phi_name].keys():
        #    print 'SHERLOCK key ', key
        #    print 'SHERLOCK dictio_clusters[phi_name][key]',dictio_clusters[phi_name][key]
        #sys.exit(0)
        #table_clust_first_round = open(os.path.join(clust_fold, "info_clust_table"), 'a')
        # del table_clust_first_round
        #file_debug_first_round = open(os.path.join(clust_fold, "clusters_dictionary.txt"), 'a')
        #file_debug_first_round.write(
        #    phi_name + '\t' + 'dictio_result ' + str(results[phi_name]) + 'n_phs ' + str(n_phs) + "\n")
        #phs_basenames = [os.path.basename(x) for x in phs_to_remove ]
        #file_debug_first_round.write(os.path.basename(phi_name)+'\t'+str(n_phs)+str(phs_basenames))
        #file_debug_first_round.write("**********************************************")
        #file_debug_first_round.close()
        new_list_phs = []
        for phs in list_phs:
            if phs in phs_to_remove:
                continue
            else:
                new_list_phs.append(phs)
        list_phs = new_list_phs
    return dictio_clusters


# Main module
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "\nUsage: ALIXE.py name.ls [options]"
        print "\nOptions:"
        print "\n-s=name_reference Use the name_reference phase file in the ls file as reference for clustering. It also accepts a list separated by commas."
        print "\n-t= Use a tolerance of N degrees for the mean phase difference between the phase sets compared"
        print "\n-r=N Use data to a resolution of N angstroms. Default is 2.0"
        print "\n-c=N Do N macrocycles of phase clustering between the sets"
        # print "-h=hkl_filename Reference hkl to calculate evalues"
        # TODO: it is better that symmetry is given either as a number of the sg or a line in the ls (if maps are given)
        print "\n-p=pdb_filename Read symmetry information from a pdb file"
        print "\n-w=f or -w=e Use f-weights or e-weights for the calculation of mean phase errors. Default is f"
        print "\n-d=working_directory Indicate the folder were to put the results. Default is the current working directory"
        sys.exit(0)
    print "\n Starting date & time " + time.strftime("%c")  # Print initial time
    # Read ls file and save the files in a list
    name_ls = sys.argv[1]
    fich_ls = open(name_ls, 'r')
    list_phs = fich_ls.read().splitlines()
    list_phs = [ phs.strip() for phs in list_phs]
    dictio_phs = {}
    for phs in list_phs:
        dictio_phs[phs] = False
    n_phs = len(list_phs)
    print "\n ", str(n_phs), " phase files found in ", name_ls
    # Read the arguments or set the defaults
    list_options = sys.argv[2:]
    # Defaults
    reference_set = list_phs[0]  # The first one in the ls
    position_ref = 1
    tolerance = 60
    resolution = 2.0
    dictio_phs[reference_set] = True  # Default is to use the first phs in the list
    cycles = 3
    f_fom = True
    reference_hkl = None  # TEMPORARY, NEED TO CHECK WITH ISABEL
    clust_fold = os.getcwd()
    cell = None

    for option in list_options:
        if option.startswith("-s"):
            # Check if they have given a single reference or a list separated by comma
            # if len(option[3:].split(','))>1:
            #    list_references=option[3:].split(',')
            #    for reference in list_references:
            #        dictio_phs[reference]=True
            # elif len(option[3:].split(','))==1: # Then we have a single reference
            # print 'option[3:]',option[3:]
            ref = option[3:]
            dictio_phs[ref] = True
            # If it is not the same one, remove te True from the default
            if ref != reference_set:
                dictio_phs[reference_set] = False
        elif option.startswith("-t"):
            tolerance = float(option[3:])
        elif option.startswith("-r"):
            resolution = float(option[3:])
        elif option.startswith("-h"):
            reference_hkl = option[3:]
        elif option.startswith("-c"):
            cycles = int(option[3:])
        elif option.startswith("-w"):
            weight_fom = option[3:]
            if weight_fom == 'e':
                f_fom = False
        elif option.startswith("-p"):  # Read the symmetry from a pdb file
            pdb_path = str(option[3:])
            cell, sg = al.read_cell_and_sg_from_pdb(pdb_path)  # Cell is a list of floats
            sg_number = al.get_space_group_number_from_symbol(sg)
        elif option.startswith("-d"):
            clust_fold = str(option[3:])

    # Check we have the symmetry info
    if cell == None:
        print "Sorry, you need to provide some pdb file to extract the symmetry information"
        sys.exit(0)

    # Generate a fake ins that SHELXE can read for expansions
    path_ins = os.path.join(clust_fold, 'name.ins')
    al.generate_fake_ins_for_shelxe(path_ins, cell, sg_number)

    # print 'dictio_phs before start alixe',dictio_phs
    # Call the startALIXE function with the appropiate input
    startALIXEasPHSTAT(clust_fold, reference_hkl, dictio_phs, cell, sg_number, tolerance, resolution, cycles, f_fom)
    print "\n Ending date & time " + time.strftime("%c")  # Print initial time
