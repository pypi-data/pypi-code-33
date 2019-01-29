from pydnameth.infrastucture.path import get_cache_path
from pydnameth.config.annotations.conditions import check_conditions
from pydnameth.config.annotations.types import AnnotationKey
import os.path
import pickle
import numpy as np


def subset_annotations(config):
    aux_data_fn = get_cache_path(config) + '/' + 'aux_data.pkl'

    if os.path.isfile(aux_data_fn):
        f = open(aux_data_fn, 'rb')
        aux_data = pickle.load(f)
        f.close()
        config.cpg_list = aux_data['cpg_list']
        config.cpg_gene_dict = aux_data['cpg_gene_dict']
        config.cpg_bop_dict = aux_data['cpg_bop_dict']
        config.gene_cpg_dict = aux_data['gene_cpg_dict']
        config.gene_bop_dict = aux_data['gene_bop_dict']
        config.bop_cpg_dict = aux_data['bop_cpg_dict']
        config.bop_gene_dict = aux_data['bop_gene_dict']
    else:
        config.cpg_list = []
        config.cpg_gene_dict = {}
        config.cpg_bop_dict = {}
        config.gene_cpg_dict = {}
        config.gene_bop_dict = {}
        config.bop_cpg_dict = {}
        config.bop_gene_dict = {}

        cpgs = config.annotations_dict[AnnotationKey.cpg.value]
        genes = config.annotations_dict[AnnotationKey.gene.value]
        bops = config.annotations_dict[AnnotationKey.bop.value]
        map_infos = config.annotations_dict[AnnotationKey.map_info.value]
        for id in range(0, len(cpgs)):

            if id % 10000 == 0:
                print('id: ' + str(id))

            curr_ann_dict = {}
            for key in config.annotations_dict:
                curr_ann_dict[key] = config.annotations_dict[key][id]

            if check_conditions(config, curr_ann_dict):

                cpg = cpgs[id]
                gene_raw = genes[id]
                curr_genes = list(set(gene_raw.split(';')))
                bop = bops[id]

                config.cpg_list.append(cpg)

                config.cpg_gene_dict[cpg] = curr_genes

                config.cpg_bop_dict[cpg] = bop

                for gene in curr_genes:
                    if gene in config.gene_cpg_dict:
                        config.gene_cpg_dict[gene].append(cpg)
                    else:
                        config.gene_cpg_dict[gene] = [cpg]

                for gene in curr_genes:
                    if gene in config.gene_bop_dict:
                        config.gene_bop_dict[gene].append(bop)
                    else:
                        config.gene_bop_dict[gene] = [bop]

                if len(bop) > 0:
                    if bop in config.bop_cpg_dict:
                        config.bop_cpg_dict[bop].append(cpg)
                    else:
                        config.bop_cpg_dict[bop] = [cpg]

                config.bop_gene_dict[bop] = curr_genes

        # Sorting cpgs by map_info in gene dict
        for curr_gene, curr_cpgs in config.gene_cpg_dict.items():
            curr_map_infos = []
            for curr_cpg in curr_cpgs:
                cpg_index = cpgs.index(curr_cpg)
                curr_map_infos.append(int(map_infos[cpg_index]))
            order = np.argsort(curr_map_infos)
            curr_cpgs_sorted = list(np.array(curr_cpgs)[order])
            config.gene_cpg_dict[curr_gene] = curr_cpgs_sorted

        # Sorting cpgs by map_info in bop dict
        for curr_bop, curr_cpgs in config.bop_cpg_dict.items():
            curr_map_infos = []
            for curr_cpg in curr_cpgs:
                cpg_index = cpgs.index(curr_cpg)
                curr_map_infos.append(int(map_infos[cpg_index]))
            order = np.argsort(curr_map_infos)
            curr_cpgs_sorted = list(np.array(curr_cpgs)[order])
            config.bop_cpg_dict[curr_bop] = curr_cpgs_sorted

        aux_data = {
            'cpg_list': config.cpg_list,
            'cpg_gene_dict': config.cpg_gene_dict,
            'cpg_bop_dict': config.cpg_bop_dict,
            'gene_cpg_dict': config.gene_cpg_dict,
            'gene_bop_dict': config.gene_bop_dict,
            'bop_cpg_dict': config.bop_cpg_dict,
            'bop_gene_dict': config.bop_gene_dict,
        }

        f = open(aux_data_fn, 'wb')
        pickle.dump(aux_data, f, pickle.HIGHEST_PROTOCOL)
        f.close()
