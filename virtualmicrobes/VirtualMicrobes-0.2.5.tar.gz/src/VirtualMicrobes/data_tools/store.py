'''
Created on Feb 7, 2015

@author: thocu
'''

import os
from VirtualMicrobes.my_tools import utility, analysis_tools
import numpy as np
try:
    import bottleneck as bt
    np.nanmean = bt.nanmean
    np.nanmedian = bt.nanmedian
    np.nanmin = bt.nanmin
    np.nanmax = bt.nanmax
    np.nanstd = bt.nanstd
except ImportError:
    pass
import collections
import itertools
from abc import abstractmethod
from VirtualMicrobes.virtual_cell.Population import Population
import shutil
import glob
import random
import networkx as nx
import json
from VirtualMicrobes.post_analysis import network_properties, network_funcs
import tempfile
import pandas
import stat

def tf_name(tf):
    return str(tf.ligand_class) + '(' + str(id(tf)) + ')'

def tf_conservation_to_dict(tf_conservation_dict):
    return { tf_name(tf):cons for tf,cons in tf_conservation_dict.items() }

def eco_type_vector_to_dict(vect_dict):
    data_dict = dict() # NOTE: unordered ok
    for dat_type, d in vect_dict.items():
        prefix = dat_type[:1]+'_' # get first letter of string
        for k,v in d.items():
            data_dict[prefix+ str(k)] = int(v)
    return data_dict

def create_tc_df(tc_dict):
    series = []
    for obj, tc in tc_dict.items():
        series.append(pandas.Series(tc[1,:], tc[0,:], name=str(obj)))
    return pandas.concat(series, axis=1, keys = [ s.name for s in series] ) if series else None

def create_gene_type_time_course_dfs(cell):
    dfs = dict()
    for _type , gene_time_course_dict in cell.get_gene_type_time_course_dict().items():
        if _type == 'enzymes' or _type == 'pumps':
            tc_dict = dict([ (str(gene.reaction) + '_' + str(id(gene)), tc) for (gene, tc) in gene_time_course_dict.items() ])
        elif _type == 'tfs':
            tc_dict = dict([ (str(gene.ligand_class.name) + '_' + str(id(gene)), tc) 
                            for (gene, tc) in gene_time_course_dict.items() ])
        DF = create_tc_df(tc_dict)    
        dfs[_type] = DF
    return dfs


class DataCollection(object):
    
    def __init__(self, save_dir='', name='dummy', filename=None):
        self.name = name
        if filename is None:
            self.filename = self.name
        else:
            self.filename = filename
        self.save_dir = save_dir
        self.init_file(name=self.filename)

    def init_file(self, name=None, labels=[], suffix='.csv'):
        if name is None:
            name = self.name
        self.data_file_name = "_".join(name.split()+ map(str,labels)) + suffix 
        data_file = open(os.path.join(self.save_dir,self.data_file_name), 'w')
        data_file.close()
        
    def change_save_location(self, new_save_dir=None, copy_orig=True, current_save_path=None):
        if copy_orig:
            data_file_name = os.path.basename(self.data_file_name)
            if current_save_path is not None:
                old_data_file = os.path.join(current_save_path, data_file_name) 
            else:
                old_data_file = os.path.join(self.save_dir, data_file_name)
            if os.path.exists(old_data_file):
                try:
                    shutil.copy2(old_data_file, new_save_dir)
                except shutil.Error: # silently catch the case where the orig and dest are the same (e.g. local to host path update)
                    print 'skip copying existing file:', old_data_file  
                    pass
            else:
                print 'Failed to copy', old_data_file, 'to', new_save_dir
            self.save_dir, self.data_file_name = new_save_dir, data_file_name
            
        else:
            self.save_dir = new_save_dir
            self.init_file()
    
    def prune_data_file_to_time(self, max_tp):
        ''' prune a data file by dropping lines starting from *max_tp*.
        
        This function assumes that the first line contains column names
        and subsequent lines are time point data, starting with an comma separated 
        (integer) time point.
        
        :param max_tp: time point to start dropping lines
        '''
        
        data_file_name = os.path.join(self.save_dir, self.data_file_name)
        print 'pruning', data_file_name, 'to time point', max_tp
        info = os.stat(data_file_name)
        uid, gid, mod = info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode)
        
        temp_file  = tempfile.NamedTemporaryFile(dir=self.save_dir, delete=False)
        with open(data_file_name,"ru") as in_file:
            for i,line in enumerate(in_file):
                if not i:
                    temp_file.write(line)
                else:
                    splits = line.split(',')
                    if splits and int(splits[0].strip()) < max_tp:
                        temp_file.write(line)
                    else:
                        break
            temp_file.close()
            os.rename(temp_file.name, data_file_name)
            os.chown(data_file_name, uid, gid)
            os.chmod(data_file_name, mod)
        
    def get_data_point(self, index):
        '''
        Get a data point at index. 
        
        Exception catching to handle case where due to code update a loaded form
        of a DataStore does not yet hold a particular DataCollection. In that
        case a dummy dict producing empty numpy arrays is returned.
        
        :param index: key to a dict shaped data point  
        '''
        if not isinstance(index, tuple):
            index = (index,)
        try:
            d = self.data_points[index]
        except AttributeError:
            d = collections.defaultdict(lambda : np.array([])) 
        return d

    @abstractmethod
    def update_data_points(self, index, dat):        
        pass
    
    @abstractmethod
    def write_data(self):
        pass
        
class ListDataCollection(DataCollection):
    
    def __init__(self, **kwargs):
        super(ListDataCollection,self).__init__(**kwargs)
        self.data_points = collections.OrderedDict()
        
    def update_data_points(self, index, data_vector):
        if not isinstance(index, tuple):
            index = (index,)
        self.data_points[index] = data_vector
        
    def write_data(self, sep=','):
        
        data_file = open(os.path.join(self.save_dir,self.data_file_name), 'a')
        for index, vec in sorted(self.data_points.items(), key=lambda x: x[0]):
            if isinstance(vec, (np.ndarray, np.generic)):           # Numpy data stores should be printed without newlines
                vec = np.array_repr(vec).replace('\n', '')    # Cut of first 6 and last 1, as the output is nested in array(<OUTPUT>)
                data_file.write(sep.join([str(i) for i in index ] + [vec]) + '\n')
            else:                                                   # Other types are fine
                data_file.write(sep.join([str(i) for i in index ] + [str(v) for v in vec]) + '\n')
            del self.data_points[index]
        data_file.close()
    
class DictDataCollection(DataCollection):
    '''
    Entry point for storing and retrieving structured data 
    '''
    
    def __init__(self, column_names, index_name, to_string=None, **kwargs):
        super(DictDataCollection,self).__init__( **kwargs)
        self.columns = column_names
        self.index_name = index_name
        self.data_points = utility.OrderedDefaultdict(dict)
        self.write_column_names(to_string=to_string)
        
    def update_data_points(self, index, data_dict):
        if not isinstance(index, tuple):
            index = (index,)
        self.data_points[index].update(data_dict)
    
    def write_data(self, sep=','):
        data_file = open(os.path.join(self.save_dir,self.data_file_name), 'a')
        for index,d in sorted(self.data_points.items(), key=lambda x: x[0]):
            data_file.write(sep.join([str(i) for i in index ] + [ str(d.get(col, '')) for col in self.columns ]) + '\n')
            del self.data_points[index]
        data_file.close()
        
    def write_column_names(self, columns=None, index_name=None, to_string=None):
        if columns is None:
            columns = self.columns
        if index_name is None:
            index_name = self.index_name
        if to_string is not None:
            columns = [ to_string(c) for c in columns ]
        column_names = [index_name] + columns
        data_file = open(os.path.join(self.save_dir,self.data_file_name),'w')
        data_file.write(','.join(column_names)+'\n')
        data_file.close()

class DataStore(object):
    '''Storage object for simulation data
    
    Keep a store of simulation data that can be written to disk and retrieved
    for online plotting. Typically, the store will only hold the most recent data
    points before appending the data to relevant on disk storage files. 
    '''
    
    class_version = '1.3'
    
    simple_stats_columns = ['avrg', 'min', 'max', 'median', 'std']
    simple_value_column = ['value']
    metabolic_categories = ['producer', 'consumer', 'import', 'export']
    gain_loss_columns = ['gain', 'loss']
    
    pop_simple_stats_dict = {
                             'toxicity rates' : lambda p: p.toxicity_rates(), 
                             'death rates' : lambda p: p.death_rates(), 
                             'production rates' : lambda p: p.production_rates(), 
                             'production values' : lambda p: p.production_values(),
                             'pos production' : lambda p: p.pos_production(),
                             'offspring counts' : lambda p: p.offspring_counts(), 
                             'iterages' : lambda p: p.iterages(),
                             'tf promoter strengths' : lambda p: p.tf_average_promoter_strengths(),
                             'enzyme promoter strengths' : lambda p: p.enz_average_promoter_strengths(),
                             'pump promoter strengths' : lambda p: p.pump_average_promoter_strengths(),
                             'cell sizes' : lambda p: p.cell_sizes(),
                             'differential regulation': lambda p: p.differential_regulation(),
                             'pump vmaxs' : lambda p: p.pump_average_vmaxs(),
                             'enzyme vmaxs' : lambda p : p.enzyme_average_vmaxs(),
                             'tf counts' : lambda p : p.tf_counts(),
                             'enzyme counts' : lambda p: p.enzyme_counts(),
                             'exporter counts' : lambda p: p.exporter_counts(),
                             'importer counts' : lambda p: p.importer_counts(),
                             'tf_k_bind_ops'  : lambda p: p.tf_k_bind_operators(),
                             'tf_ligand_ks'  : lambda p: p.tf_ligand_ks(),
                             'enz_subs_ks'  : lambda p: p.enzyme_substrate_ks(),
                             'pump_ene_ks' : lambda p: p.pump_substrate_ks(),
                             'pump_subs_ks' : lambda p: p.pump_energy_ks()
                             }
    eco_diversity_stats_dict = {
                                'genotype' : lambda p: p.genotype_counts(),
                                'reaction genotype' : lambda p: p.reaction_genotype_counts(),
                                'metabolic type' : lambda p: p.metabolic_type_counts(),
                                'producer type' : lambda p: p.producer_type_counts(),
                                'consumer type' : lambda p: p.consumer_type_counts(),
                                'import type' : lambda p: p.import_type_counts(),
                                'export type' : lambda p: p.export_type_counts()
                                }
    pop_genomic_stats_dict = {
                              'genome sizes' : lambda p: p.genome_sizes(),
                              'chromosome counts' : lambda p: p.chromosome_counts()
                              }
    snapshot_stats_names = ['historic_production_max']
    mut_stats_names = ['point_mut_count',
                       'chromosomal_mut_count',
                       'stretch_mut_count',
                       'chromosome_dup_count',
                       'chromosome_del_count',
                       'chromosome_fuse_count',
                       'chromosome_fiss_count',
                       'sequence_mut_count',
                       'tandem_dup_count',
                       'stretch_del_count',
                       'stretch_invert_count',
                       'translocate_count',
                       'internal_hgt_count',
                       'external_hgt_count'
                       ]
    fit_stats_names = ['toxicity', 
                       'toxicity_change_rate', 
                       'raw_production', 
                       'raw_production_change_rate'
                       ]
    meta_stats_names = ['providing_count', 
                        'strict_providing_count', 
                        'exploiting_count', 
                        'strict_exploiting_count', 
                        'producing_count', 
                        'consuming_count', 
                        'importing_count', 
                        'exporting_count'
                        ]
    grid_stats = [
                  'neighbor crossfeeding',
                  'strict neighbor crossfeeding', 
                  'exploitive neighbor crossfeeding',
                  'grid production values',
                  'grid production rates', 
                  'grid death rates', 
                  'grid cell sizes'
                  ]
    crossfeed_stats = [
                       'crossfeeding', 
                        'strict crossfeeding', 
                        'exploitive crossfeeding'
                        ] 
    genome_simple_val_stats_names = ['genome_size', 
                       'chromosome_count', 
                       'tf_count', 
                       'enzyme_count', 
                       'eff_pump_count', 
                       'inf_pump_count',
                       'tf_avrg_promoter_strengths', 
                       'enz_avrg_promoter_strengths', 
                       'pump_avrg_promoter_strengths',
                       'tf_sum_promoter_strengths', 
                       'enz_sum_promoter_strengths', 
                       'pump_sum_promoter_strengths'
                       ]
    genome_simple_stats_names = [
                       'tf_promoter_strengths', 
                       'enz_promoter_strengths', 
                       'pump_promoter_strengths',
                       'tf_ligand_differential_ks',
                       'enz_subs_differential_ks', 
                       'pump_subs_differential_ks',
                       'pump_ene_differential_ks', 
                       'tf_differential_reg',
                       'tf_k_bind_ops',
                       'enz_vmaxs',
                       'pump_vmaxs',
                       'tf_ligand_ks',
                       'enz_subs_ks', 
                       'pump_ene_ks',
                       'pump_subs_ks'
                       ]
    genome_dist_stats = [
                         'copy_numbers',
                         'copy_numbers_tfs',
                         'copy_numbers_enzymes',
                         'copy_numbers_inf_pumps',
                         'copy_numbers_eff_pumps'
                         ]
    network_stats_funcs = {'all_node_connectivities':
                           lambda g: np.array([ K for d in nx.all_pairs_node_connectivity(g).values() for K in d.values() ] ),
                           'degree': lambda g: np.array(g.degree().values()),
                           'in_degree': lambda g: np.array(g.in_degree().values()),
                           'out_degree': lambda g: np.array(g.out_degree().values())}
    
    grn_edits = { '': lambda G: G,  
                 '_pruned_1._cT_iT': lambda G: network_funcs.prune_GRN(G, 
                                                            log_dif_effect=1., 
                                                            rescue_regulated=True,
                                                            iterative=True
                                                            )
                 }
    eco_type_stats = ['metabolic_type_vector', 
                               'genotype_vector']
    functional_stats_names = ['conversions_type', 
                              'genotype' ,
                              'reaction_genotype' ,
                              'metabolic_type',
                              'import_type',
                              'export_type',
                              'tf_sensed',
                              'consumes',
                              'produces']
    
    pop_stats_dir = 'population_dat'
    eco_stats_dir = 'ecology_dat'
    ancestry_stats_dir = 'ancestry_compare_dat'
    lod_stats_dir = 'lod_dat'
    best_stats_dir = 'best_dat'
    trophic_type_columns = ['fac-mixotroph', 'autotroph','heterotroph', 'obl-mixotroph']
    
    def __init__(self, base_save_dir, name, utility_path, n_most_frequent_metabolic_types , 
                 n_most_frequent_genomic_counts, species_markers, reactions_dict, small_mols,
                 clean=True, create=True):
        self.version = self.__class__.class_version
        self.base_save_dir = base_save_dir
        self.name = name
        self.init_save_dirs(clean=clean, create=create)
        self.data_collections = dict() # NOTE: unordered ok
        
        # Copying the webapplication to the mutant:
        self.utility_path = utility_path
        self.copy_utility_files()
        
        self.n_most_frequent_metabolic_types = n_most_frequent_metabolic_types
        self.init_stats_column_names(n_most_frequent_metabolic_types,
                                     n_most_frequent_genomic_counts,
                                     species_markers, reactions_dict, small_mols)
        self.init_pop_data_stores()
        self.init_eco_data_stores()
        
    @property
    def save_dir(self):
        return os.path.join(self.base_save_dir, self.name)
    
    def init_save_dirs(self, clean=False, create=True):
        '''create the paths to store various data types
        
        :param clean: (bool) remove existing files in path 
        :param create: create the path within the file system
        '''
        if clean:
            remove_globs = ['*.csv', '*.json', '*.mp4']
        else:
            remove_globs = []
        
        if create:
            utility.ensure_dir(self.save_dir, 
                               remove_globs=remove_globs)
            utility.ensure_dir(os.path.join(self.save_dir,self.pop_stats_dir), 
                               remove_globs=remove_globs)
            utility.ensure_dir(os.path.join(self.save_dir,self.eco_stats_dir), 
                               remove_globs=remove_globs)
            #utility.ensure_dir(os.path.join(self.save_dir,self.ancestry_stats_dir), 
            #                   remove_globs=remove_globs)
            utility.ensure_dir(os.path.join(self.save_dir,self.lod_stats_dir), 
                               remove_globs=remove_globs)
            utility.ensure_dir(os.path.join(self.save_dir,self.best_stats_dir), 
                               remove_globs=remove_globs)

            
    def copy_utility_files(self):
        # Ensure webapp link on top with 00 prefix
        for filename in glob.glob(os.path.join(self.utility_path, '*.html')):           # Copy all but redirection page
            if not filename == os.path.join(self.utility_path, '00_webapplication.html'):
                shutil.copy2(filename, self.save_dir)
        shutil.copy2(os.path.join(self.utility_path, '00_webapplication.html'), os.path.join(self.save_dir, "../")) # Copy redirection page
        for filename in glob.glob(os.path.join(self.utility_path, '*.js')):
            shutil.copy2(filename, self.save_dir)
        for filename in glob.glob(os.path.join(self.utility_path, '*.css')):
            shutil.copy2(filename, self.save_dir)
        shutil.copy2(os.path.join(self.save_dir, '../', 'params.txt'),  os.path.join(self.save_dir))
            
            
    def change_save_location(self, base_save_dir=None, name=None, clean=False, 
                             copy_orig=True, create=True, current_save_path=None):
        if base_save_dir is not None:
            self.base_save_dir = base_save_dir
        if name is not None:
            self.name = name
        self.init_save_dirs(clean=clean, create=create)
        for d in self.data_collections.values():
            save_dir_name = os.path.basename(os.path.normpath(d.save_dir))
            if save_dir_name == self.name:
                save_dir_name = ''
            d.change_save_location(os.path.join(self.save_dir, save_dir_name), 
                                   copy_orig=copy_orig,
                                   current_save_path=os.path.join(current_save_path, self.name, save_dir_name))
        self.copy_utility_files()
        
    def prune_data_files_to_time(self, max_tp):
        for d in self.data_collections.values():
            d.prune_data_file_to_time(max_tp)
        
        
            
    def init_stats_column_names(self, n_most_freq_met_types, n_most_freq_genomic_counts, species_markers,
                                reactions_dict, small_mols):
        '''
        Initialize column names for various data collections
        :param n_most_freq_met_types:
        :param n_most_genomic_counts:
        '''
        
        self.genomic_freq_count_columns = [ 'most_freq'+str(i) for i in range(n_most_freq_genomic_counts) ]
        self.species_columns = species_markers
        
        self.conversion_columns = list(reactions_dict['conversion'])
        self.transport_columns = list( reactions_dict['import'])
        self.small_mol_columns = map(str, small_mols)
        
        conversions = zip(self.conversion_columns, itertools.repeat(False)) 
        imports = zip( self.transport_columns, itertools.repeat(False))
        exports = zip( self.transport_columns, itertools.repeat(True))
        self.reactions_columns = conversions + imports + exports
        self.met_capacity_columns_dict = collections.OrderedDict( ( (cat, cat+'_sum') for cat in self.metabolic_categories) )
        stats = ['avrg_diff', 'max_diff', 'min_diff']
        self.met_difference_columns_dict = collections.OrderedDict( ( (cat,[ cat+'_'+stat 
                                                                            for stat in stats ])
                                                                     for cat in self.metabolic_categories ))
        
    def add_collection(self, dc):
        self.data_collections[dc.name] = dc
        
    def simple_stats(self, dat):
        column_names = self.simple_stats_columns
        if len(dat):
            stats = [ np.nanmean(dat), np.nanmin(dat), np.nanmax(dat), np.nanmedian(dat), np.nanstd(dat) ]
        else:
            # the data can be an empty array 
            stats = [ np.nan, np.nan, np.nan, np.nan, np.nan ]
        return dict(zip(column_names, stats))
    
    def gain_loss(self, cur_dat, prev_dat):
        column_names = self.gain_loss_columns
        gain = len(cur_dat - prev_dat)
        loss = len(prev_dat - cur_dat)
        return dict(zip(column_names, [gain, loss]))
    
    def simple_value(self, dat):
        column_name = self.simple_value_column
        return dict(zip(column_name, [dat]))
        
    def frequency_stats(self, dat, column_names):
        most_frequent = utility.padded_most_frequent(dat, len(column_names))
        return dict( zip(column_names, most_frequent))
    
    def type_differences_stats(self, types, column_names):
        difference_dat = analysis_tools.set_differences(types)
        stats = [ np.average(difference_dat), np.max(difference_dat), np.min(difference_dat)]
        return dict( zip(column_names, stats))
    
    def type_totals_stats(self, types, column_name):
        total_dat = len(frozenset.union(*types)) if types else 0
        return {column_name: total_dat}
        
    def init_ancestry_compare_stores(self, pop_hist):
        save_dir = os.path.join(pop_hist.save_dir,self.ancestry_stats_dir)
        utility.ensure_dir(save_dir)
        for stats_name in self.snapshot_stats_names:
            self.init_simple_value_store(save_dir, stats_name)
            
        for ete_tree_struct, lods in pop_hist.tree_lods:
            ete_name = ete_tree_struct.tree.name.split('_')[0]
            tree_save_dir = os.path.join(save_dir, ete_name )
            utility.ensure_dir(tree_save_dir)
        
            for lod_leaf in lods:
                for stats_name in (self.mut_stats_names + self.fit_stats_names + 
                                   self.meta_stats_names + self.genome_simple_val_stats_names ):
                    dc_name = 'lod'+str(lod_leaf.id)+'_'+stats_name
                    self.init_simple_stats_plus_store(tree_save_dir, dc_name)
                    dc = ListDataCollection(save_dir=tree_save_dir, name=dc_name+'_vector')
                    self.add_collection(dc)
                                
            for stats_name in ( self.fit_stats_names + 
                                   self.meta_stats_names + self.genome_simple_val_stats_names ):
                dc_name = stats_name
                self.init_simple_value_store(tree_save_dir, dc_name+'_lods', 'sample,lod,time_point')
    
    def init_lod_stores(self, lod, met_classes, conversions, transports,
                        first_anc, last_anc):
        lod_id = lod.name
        self.met_type_vector_columns = ( [ 'p_' + str(met_c) for met_c in met_classes ] +
                                         [ 'c_' + str(met_c) for met_c in met_classes ] +
                                         [ 'i_' + str(met_c) for met_c in met_classes ] +
                                         [ 'e_' + str(met_c) for met_c in met_classes ] )
        self.genotype_vector_columns = ( [ 'c_' + str(conv) for conv in conversions] +
                                         [ 't_' + str(trans) for trans in transports] + 
                                         [ 's_' + str(sensed) for sensed in met_classes] ) 
        save_dir = lod.save_dir
        #        else:
        #            save_dir = os.path.join(self.save_dir,self.lod_stats_dir, lod_id)
        lod_save_dir = os.path.join(save_dir, 'stats') 
        utility.ensure_dir(lod_save_dir)
        shutil.copy2(os.path.join(self.utility_path,'00_lod.html'),  lod_save_dir) 
            
        for stats_name in (self.mut_stats_names + self.fit_stats_names + 
                           self.meta_stats_names + self.genome_simple_val_stats_names):
            dc_name = str(lod_id)+'_'+stats_name
            self.init_simple_value_store(lod_save_dir, dc_name, filename=stats_name)
        
        for stats_name in self.genome_dist_stats + self.network_stats_funcs.keys() + self.genome_simple_stats_names:
            dc_name = str(lod_id) + '_' + stats_name
            self.init_simple_stats_store(lod_save_dir, dc_name, filename=stats_name)
        
        for stats_name in self.network_stats_funcs:
            for variant in self.grn_edits:
                dc_name = str(lod_id) + '_' + stats_name + variant
                self.init_simple_stats_store(lod_save_dir, dc_name, filename=stats_name + variant)
        
        for stats_name in self.functional_stats_names:
            dc_name = str(lod_id) + '_' + stats_name
            self.init_gain_loss_store(lod_save_dir, dc_name , filename=stats_name)
            
        stats_name = 'metabolic_type_vector'
        self.init_dict_stats_store(save_dir=lod_save_dir, stats_name=str(lod_id)+'_'+stats_name, index_name='time_point',
                                column_names = self.met_type_vector_columns, filename=stats_name)
        stats_name = 'genotype_vector'
        self.init_dict_stats_store(save_dir=lod_save_dir, stats_name=str(lod_id)+'_'+stats_name, index_name='time_point',
                                column_names = self.genotype_vector_columns, filename=stats_name)
        
        stats_name = 'first_anc_bind_cons'
        self.init_dict_stats_store(save_dir=lod_save_dir, stats_name=str(lod_id)+'_'+stats_name, index_name='time_point',
                                column_names = [ tf_name(tf) for tf in set(first_anc.genome.tfs) ], 
                                filename=stats_name)
        stats_name = 'first_anc_bind_new'
        self.init_dict_stats_store(save_dir=lod_save_dir, stats_name=str(lod_id)+'_'+stats_name, index_name='time_point',
                                column_names = [ tf_name(tf) for tf in set(first_anc.genome.tfs) ], 
                                filename=stats_name)
        
        stats_name = 'last_anc_bind_cons'
        self.init_dict_stats_store(save_dir=lod_save_dir, stats_name=str(lod_id)+'_'+stats_name, index_name='time_point',
                                column_names = [ tf_name(tf) for tf in set(last_anc.genome.tfs) ],
                                filename=stats_name)
        stats_name = 'last_anc_bind_new'
        self.init_dict_stats_store(save_dir=lod_save_dir, stats_name=str(lod_id)+'_'+stats_name, index_name='time_point',
                                column_names = [ tf_name(tf) for tf in set(last_anc.genome.tfs) ],
                                filename=stats_name)
    
    def init_pop_data_stores(self, save_dir=None):
        if save_dir is None:
            save_dir = os.path.join(self.save_dir,self.pop_stats_dir)
        for stats_name in self.pop_simple_stats_dict:
            self.init_simple_stats_store(save_dir, stats_name)
            self.init_list_stats_store(save_dir, stats_name+'_vector')
            
        self.init_simple_value_store(save_dir, 'population size')
        self.init_simple_value_store(save_dir, 'coalescent time')
        self.init_simple_value_store(save_dir, 'production scaling')
        self.init_dict_stats_store(save_dir=save_dir, stats_name='metabolic types', index_name='time_point',
                                   column_names= self.met_capacity_columns_dict.values() 
                                   + sum(self.met_difference_columns_dict.values(), [])  )
        self.init_dict_stats_store(save_dir=save_dir, stats_name='genome sizes', index_name='time_point',
                                   column_names=self.simple_stats_columns + self.genomic_freq_count_columns)
        self.init_dict_stats_store(save_dir=save_dir, stats_name='chromosome counts', index_name='time_point',
                            column_names=self.simple_stats_columns + self.genomic_freq_count_columns)
        self.init_dict_stats_store(save_dir=save_dir, stats_name='species counts', index_name='time_point',
                            column_names=self.species_columns, to_string=lambda x:str(x))
        self.init_dict_stats_store(save_dir=save_dir, stats_name='reaction counts', index_name='time_point',
                            column_names=self.reactions_columns, to_string=lambda x: str(x[0])+' '+str(x[1]))
        self.init_dict_stats_store(save_dir=save_dir, stats_name='trophic type counts', index_name='time_point',
                            column_names=self.trophic_type_columns)
        self.init_dict_stats_store(save_dir=save_dir, stats_name='conversion counts', index_name='time_point',
                            column_names=self.conversion_columns, to_string=str)
        self.init_dict_stats_store(save_dir=save_dir, stats_name='import counts', index_name='time_point',
                            column_names=self.transport_columns, to_string=str)
        self.init_dict_stats_store(save_dir=save_dir, stats_name='export counts', index_name='time_point',
                            column_names=self.transport_columns, to_string=str)

    def init_eco_data_stores(self, save_dir=None):
        if save_dir is None:
            save_dir = os.path.join(self.save_dir,self.eco_stats_dir)
        for stats_name in self.crossfeed_stats:
            self.init_simple_stats_store(save_dir, stats_name)
        for stats_name in self.grid_stats:
            dc = ListDataCollection(save_dir=save_dir, name=stats_name)
            self.add_collection(dc)
        stat_name = 'concentration'
        for mol_name in self.small_mol_columns:
            base_name = stat_name+' '+mol_name
            dc = ListDataCollection(save_dir=save_dir, name='grid '+base_name)
            self.add_collection(dc)
            self.init_simple_stats_store(save_dir, base_name)
            
        for stats_name in self.eco_diversity_stats_dict:
            self.init_simple_value_store(save_dir, stats_name)
    
    def init_dict_stats_store(self, save_dir, stats_name, column_names, index_name='time_point', **kwargs):
        dc = DictDataCollection(save_dir=save_dir, name=stats_name, index_name=index_name,
                            column_names=column_names, **kwargs)
        self.add_collection(dc)
        
    def init_simple_value_store(self, save_dir, stats_name, index_name='time_point', filename=None):    
        self.init_dict_stats_store(save_dir=save_dir, stats_name=stats_name, index_name=index_name, 
                                column_names=self.simple_value_column, filename=filename)
    
    def init_gain_loss_store(self, save_dir, stats_name, index_name='time_point', filename=None):    
        self.init_dict_stats_store(save_dir=save_dir, stats_name=stats_name, index_name=index_name, 
                                column_names=self.gain_loss_columns, filename=filename)
    
    def init_simple_stats_store(self, save_dir, stats_name, index_name='time_point' ,filename=None):
        self.init_dict_stats_store(save_dir=save_dir, stats_name=stats_name, index_name=index_name,
                             column_names=self.simple_stats_columns, filename=filename)
        
    def init_simple_stats_plus_store(self, save_dir, stats_name, index_name='time_point' ):
        self.init_dict_stats_store(save_dir=save_dir, stats_name=stats_name, index_name=index_name,
                             column_names=self.simple_stats_columns + self.simple_value_column)
        
    def init_list_stats_store(self, save_dir, stats_name):
        dc = ListDataCollection(save_dir=save_dir, name=stats_name)
        self.add_collection(dc)
        
    def add_ancestry_data_point(self, comp_dat, ref_lods, time_point, leaf_samples=100):
        '''
        Compare lines of descent in a reference tree to a population snapshot at
        a previous time point.
        
        The *comp_dat* is a po
        
        '''
        ete_tree_struct, comp_pop_hist = comp_dat
        ete_tree = ete_tree_struct.tree
        phylo_tree = comp_pop_hist.population.phylo_tree
        ete_lca = phylo_tree.ete_get_lca(ete_tree)
        lca = phylo_tree.ete_node_to_phylo_unit(ete_tree_struct, ete_lca)
        ete_leaf_nodes = ete_tree.get_leaves()
        phylo_leafs = phylo_tree.ete_nodes_to_phylo_units(ete_tree_struct, ete_leaf_nodes)
        lca_age = float(lca.iterage)
        for stat in self.snapshot_stats_names:
            dat = comp_pop_hist.population.historic_production_max
            dc_name = stat
            self.add_raw_values_dp(dc_name, dat, time_point)
        #comp_pop_hist.population.annotate_phylo_tree2(features=self.mut_stats_names + 
        #                                         self.fit_stats_names + ['iterage'],
        #                                         ete_root=ete_lca)
        for lod_leaf, lod in ref_lods.items():
            ref_ancestor, ref_ancestor_ete = comp_pop_hist.identify_lod_ancestor(ete_tree_struct, lod)
            for stat in self.mut_stats_names + self.fit_stats_names : # here wel look at rates along branches
                lca_stat = getattr(ete_lca, stat)
                ref_val = ((getattr(ref_ancestor_ete, stat) - lca_stat ) / 
                           (getattr(ref_ancestor_ete,'iterage') - lca_age))
                leafs_dat = np.array([ (getattr(node, stat) - lca_stat )/ 
                                      (getattr(node,'iterage') - lca_age) 
                                      for node in ete_leaf_nodes]
                                     )
                dc_name = 'lod'+str(lod_leaf.id)+'_'+stat
                self.add_simple_stats_dp(dc_name, np.nan_to_num(leafs_dat), time_point)
                self.add_raw_values_dp(dc_name, ref_val, time_point)
                dc_name += '_vector'
                self.add_list_dp(dc_name, leafs_dat, time_point)
            
            for stat in  self.meta_stats_names + self.genome_simple_val_stats_names:
                leafs_dat =np.array([ getattr(l,stat) for l in phylo_leafs])
                ref_val = getattr(ref_ancestor, stat)
                dc_name = 'lod'+str(lod_leaf.id)+'_'+stat
                self.add_simple_stats_dp(dc_name,  np.nan_to_num( leafs_dat), time_point)
                self.add_raw_values_dp(dc_name, ref_val, time_point)
                self.add_list_dp(dc_name+'_vector', leafs_dat, time_point)    
            self.write_data()
                
        if len(phylo_leafs) > leaf_samples:
            phylo_leafs = random.sample(phylo_leafs,leaf_samples) 
        for i,leaf in enumerate(phylo_leafs):
            for lod in leaf.lods_up():
                for a in reversed(list(lod)):
                    if str(a.id) == str(lca.id):
                        break
                    for stat in  self.meta_stats_names + self.genome_simple_val_stats_names + self.fit_stats_names:
                        dc_name = stat
                        self.add_raw_values_dp(dc_name+'_lods', getattr(a, stat), 
                                               (time_point, i, a.time_birth) )
                self.write_data()
                break # write for 1 lod only

    def init_phylo_hist_stores(self, phylo_hist):
        met_classes = phylo_hist.environment.molecule_classes
        conversions = phylo_hist.environment.conversions
        transports = phylo_hist.environment.transports
        for tree_lods in phylo_hist.tree_lods:
            for lod in tree_lods[1].values():
                ancestors = lod.strided_lod()
                first = ancestors[0]
                last = ancestors[-1]
                self.init_lod_stores(lod, met_classes, conversions, transports, 
                                     first_anc=first, last_anc=last)
                
    def add_lod_network_data(self, lod, save_dir=None):
        lod_id = lod.name
        ancestors = lod.strided_lod()
        for anc in ancestors:
            print '.',
            tp = anc.time_birth
            G = anc.GRN(with_gene_refs=True) # get the gene regulatory network of ancestor
            for variant, netw_func in self.grn_edits.items():
                grn = netw_func(G)
                for stat, func in self.network_stats_funcs.items():
                    dc_name = str(lod_id)+'_' + stat + variant
                    dat = func(grn)
                    self.add_simple_stats_dp(dc_name, dat, tp)
            self.write_data()
        print
        
    def add_lod_binding_conservation(self, lod):
        
        lod_id = lod.name
        ancestors = lod.strided_lod()
        first = ancestors[0]
        last = ancestors[-1]
        for anc in ancestors:
            print '.',
            tp = anc.time_birth
            tf_cons_dict, tf_new_dict = network_properties.tf_binding_overlap(first, anc, 
                                                                 closest_homolog=True,
                                                                 no_phylogeny=True,
                                                                 verbose=False)
            dat = tf_conservation_to_dict(tf_cons_dict)
            self.add_dp(str(lod_id)+'_'+'first_anc_bind_cons', dat, tp)
            dat = tf_conservation_to_dict(tf_new_dict)
            self.add_dp(str(lod_id)+'_'+'first_anc_bind_new', dat, tp)
             
            tf_cons_dict, tf_new_dict = network_properties.tf_binding_overlap(last, anc, 
                                                                 closest_homolog=True,
                                                                 no_phylogeny=True,
                                                                 verbose=False)
            dat = tf_conservation_to_dict(tf_cons_dict)
            self.add_dp(str(lod_id)+'_'+'last_anc_bind_cons', dat, tp)
            dat = tf_conservation_to_dict(tf_new_dict)
            self.add_dp(str(lod_id)+'_'+'last_anc_bind_new', dat, tp)
            self.write_data()
        print
        
    def add_lod_data(self, ete_tree_struct, lod, pop, env):
        
        lod_id = lod.name
        ancestors = lod.strided_lod()
        prev_anc = None
        for anc in ancestors:
            print '.',
            # For loop below needs to be cleaned up. It prints all pointmutations along the LOD
            
            for k,mut in anc.mutations.items():
                if k == 'sg' and mut:
                    print '\n\Anc at time ', anc.time_birth
                    print '\n Relative mut-chances: ', 'P:', str(float(anc.pump_count)/float(anc.genome_size)), 'TF:', str(float(anc.tf_count)/float(anc.genome_size)), 'E:', str(float(anc.enzyme_count)/float(anc.genome_size))
                    
                    for m in mut:                            
                        if m.par == 'operator':
                            continue
                        print '\tMutating', str(m.par) , 'of', m.genomic_target.params["type"]
                        print '\tReaction: ',
                        try:
                            print m.genomic_target.reaction
                        except:
                            print '...'
                        print '\told value:',
                        if m.par == 'promoter':
                            print m.genomic_target.promoter.strength
                        elif m.par == 'operator':
                            print m.genomic_target.operator
                        elif m.par == 'bind':
                            print m.genomic_target.binding_sequence
                        elif m.par == 'ligand_class':
                            print m.genomic_target.ligand_class
                        elif m.par == 'ene_ks':
                            print m.genomic_target.params["ene_ks"].values()
                        elif m.par == 'ligand_ks':
                            print m.genomic_target.params["ligand_ks"].values()
                        elif m.par == 'subs_ks':
                            print m.genomic_target.params["subs_ks"].values()
                        else:
                            print m.genomic_target[m.par]
                        
                        print '\tnew value:',
                        if m.par in ['ene_ks', 'subs_ks']:
                            print m.new_val.values()
                        else:
                            print m.new_val
                        
            tp = anc.time_birth
            for stat in self.genome_dist_stats + self.genome_simple_stats_names:
                dc_name = str(lod_id)+'_'+stat
                self.add_simple_stats_dp(dc_name, getattr(anc, stat), tp)
            
            for stat in self.meta_stats_names + self.genome_simple_val_stats_names + self.fit_stats_names:
                dc_name = str(lod_id)+'_'+stat
                self.add_raw_values_dp(dc_name, getattr(anc, stat), tp)
                
            for stat in self.eco_type_stats:
                dc_name = str(lod_id) + '_' + stat
                func = getattr(anc, stat)
                vect_dict = func(env)
                dat = eco_type_vector_to_dict(vect_dict)
                self.add_dp(dc_name, dat, tp)
                
            if prev_anc is not None: # We need the previous ancestor in the lod for these stats 
                for stat in self.mut_stats_names:
                    dc_name = str(lod_id)+'_'+stat
                    try:
                        # the birth node of the cell in the tree is a part of the branch of its parent
                        # and therefore the data that we obtain from this node is a property
                        # of the parent. Consequently, the time point of the data is the 'time of birth'
                        # of the parent (prev_anc) of this individual. 
                        node = pop.phylo_tree.ete_phylo_to_ete_birth_nodes(ete_tree_struct, anc)[0]
                        self.add_raw_values_dp(dc_name, getattr(node, stat), prev_anc.time_birth)
                    except IndexError: # no (more) ancestors in the ete_tree representation (pruning)
                        pass 
                for stat in self.functional_stats_names:
                    try:
                        # get differences (gains/losses) between current and previous individual in 
                        # the lod.
                        this_node = pop.phylo_tree.ete_phylo_to_ete_birth_nodes(ete_tree_struct,anc)[0]
                        prev_node = pop.phylo_tree.ete_phylo_to_ete_birth_nodes(ete_tree_struct,prev_anc)[0]
                        dat = len(getattr(this_node, stat) - getattr(prev_node, stat))
                        dc_name = str(lod_id)+'_'+stat 
                        dat = len(getattr(prev_node, stat) - getattr(this_node, stat))
                        self.add_gain_loss_dp(dc_name, getattr(this_node, stat), getattr(prev_node, stat),  prev_anc.time_birth)
                    except IndexError: # no (more) ancestors in the ete_tree representation (pruning)
                        pass 
                    
            self.write_data()
            prev_anc = anc
        print
                
    def add_pop_data_point(self, system, time_point):
        pop = system.population
        env = system.environment
        for dc_name, pop_func in self.pop_simple_stats_dict.items():
            dat = pop_func(pop)
            self.add_simple_stats_dp(dc_name, dat, time_point)
            self.add_list_dp(dc_name+'_vector', list(dat), time_point)
            
        for dc_name, pop_func in self.pop_genomic_stats_dict.items():
            dat = pop_func(pop)
            self.add_simple_stats_dp(dc_name, dat, time_point)
            self.add_frequency_stats_dp(dc_name, dat, self.genomic_freq_count_columns, time_point)

        dat = pop.metabolic_type_counts()
        self.add_metabolic_stats_dp('metabolic types', dat, time_point)
        
        pop_size = pop.current_pop_size
        dat = pop.reaction_counts() 
        for k in dat:
            dat[k] /= float(pop_size)
        self.add_count_stats_dp('reaction counts', dat, time_point)
        
        dat = dict( [(name,0.) for name in self.trophic_type_columns ])
        dat.update(pop.trophic_type_counts(env)) 
        for k in dat:
            dat[k] /= float(pop_size)
        self.add_count_stats_dp('trophic type counts', dat, time_point)
        
        dat = pop.reaction_counts_split()
        enzymes = dat['conversion']
        for k in enzymes:
            enzymes[k] /= float(pop_size)
        self.add_count_stats_dp('conversion counts', enzymes, time_point)
        importers = dat['importer']
        for k in importers:
            importers[k] /= float(pop_size)
        self.add_count_stats_dp('import counts', importers, time_point)
        exporters = dat['exporter']
        for k in exporters:
            exporters[k] /= float(pop_size)
        self.add_count_stats_dp('export counts', exporters, time_point)
        dat = pop.marker_counts('lineage')
        for k in dat:
            dat[k] /= float(pop_size)
        self.add_count_stats_dp('species counts', dat, time_point)
        dat = pop_size
        self.add_raw_values_dp('population size', dat, time_point)
        dat = pop.phylo_tree.coalescent()[1] 
        self.add_raw_values_dp('coalescent time', dat, time_point)
        dat = pop.historic_production_max
        self.add_raw_values_dp('production scaling', dat, time_point)
        
    def add_eco_data_point(self, system, time_point):
        env = system.environment
        pop = system.population
        dat = env.population_grid_neighborhood_data(lambda x: np.average(len(Population.metabolic_complementarity(x)) ) )
        self.add_dp('neighbor crossfeeding', dat, time_point)
        self.add_simple_stats_dp('crossfeeding', dat, time_point)
        dat = env.population_grid_neighborhood_data(lambda x: np.average(len(Population.metabolic_complementarity(x, strict_providing=True, 
                                                                                                                  strict_exploiting=True)) ) )
        self.add_dp('strict neighbor crossfeeding', dat, time_point)
        self.add_simple_stats_dp('strict crossfeeding', dat, time_point)
        dat = env.population_grid_neighborhood_data(lambda x: np.average(len(Population.metabolic_complementarity(x, strict_providing=False,
                                                                                                                  strict_exploiting=True)) ) )
        self.add_dp('exploitive neighbor crossfeeding', dat, time_point)
        self.add_simple_stats_dp('exploitive crossfeeding', dat, time_point)
        
        'resource concentrations', 'markers', 'production rates', 'death rates', 'cell sizes'
        
        stat_name = 'concentration'
        for res, dat in env.metabolite_grid_data_dict().items(): 
            base_name = stat_name+' '+str(res)
            self.add_dp('grid '+base_name, dat, time_point)
            self.add_simple_stats_dp(base_name, dat, time_point)
        
        dat = env.population_grid_data(lambda x: np.average(pop.death_rates(x)))
        self.add_dp('grid death rates', dat, time_point)

        dat = env.population_grid_data(lambda x: np.average(pop.production_values(x)))
        self.add_dp('grid production values', dat, time_point)
               
        dat = env.population_grid_data(lambda x: np.average(pop.pos_production(x)))
        self.add_dp('grid production rates', dat, time_point)
        
        dat = env.population_grid_data(lambda x: np.average(pop.cell_sizes(x)))
        self.add_dp('grid cell sizes', dat, time_point)
        
        for stats_name, func in self.eco_diversity_stats_dict.items():
            dat = func(pop)
            shannon_h = utility.sdi(dat)
            
            self.add_raw_values_dp(stats_name, shannon_h, time_point )
        
    def add_best_data_point(self, best, attribute_mapper, time_point, affix=''):
        best_save_dir = os.path.join(self.save_dir,self.best_stats_dir)
        dat = best.genome # Where best == best producer (production value)
        self.write_genome_json(best_save_dir, 
                               str('best_'+affix), dat, attribute_mapper, [time_point])
        
        gene_type_dfs = create_gene_type_time_course_dfs(best)
        for _type, gene_df in gene_type_dfs.items():
            fname = os.path.join(best_save_dir, str(_type)+'_'+affix+'.csv')
            if gene_df is not None:
                gene_df.to_csv(fname)
            else:
                with open(fname, 'w') as _file:
                    _file.write('') # make an empty csv
        
        df = create_tc_df(best.get_mol_time_course_dict())
        df.to_csv(os.path.join(best_save_dir, str('metabolites_'+affix+'.csv')))
        
        tc = best.get_toxicity_time_course()
        ts = pandas.Series(tc[1,:], tc[0,:], name='toxicity')
        ts.to_csv(os.path.join(best_save_dir, str('toxicity_'+affix+'.csv')))
        
        tc = best.get_raw_production_time_course()
        ts = pandas.Series(tc[1,:], tc[0,:], name='production')
        ts.to_csv(os.path.join(best_save_dir, str('production_'+affix+'.csv')))
        
        tc = best.get_pos_prod_time_course()
        ts = pandas.Series(tc[1,:], tc[0,:], name='pos_prod')
        ts.to_csv(os.path.join(best_save_dir, str('pos_prod_'+affix+'.csv')))
        
        tc = best.get_cell_size_time_course()
        ts = pandas.Series(tc[1,:], tc[0,:], name='cell_size')
        ts.to_csv(os.path.join(best_save_dir, str('cell_size_'+affix+'.csv')))
        
    def write_genome_json(self, save_dir, name, genome, attribute_mapper, labels, suffix='.json'):
        save_file_label = os.path.join(save_dir, name+suffix)
        fh = open(save_file_label, 'w')
        json.dump(genome, fh, default=lambda obj: utility.json_dumper(obj, attribute_mapper),  
                  sort_keys=True, indent=4)
        fh.close()
        name = "_".join(name.split()+ map(str,labels)) + suffix
        save_file = os.path.join(save_dir, name)
        fh = open(save_file, 'w')
        json.dump(genome, fh, default=lambda obj: utility.json_dumper(obj, attribute_mapper),  
                  sort_keys=True, indent=4)
        fh.close()
        
    def add_list_dp(self, dc_name, dat, time_point):    
        try:
            self[dc_name]
        except KeyError:
            self.init_list_stats_store(self.save_dir, dc_name)
        self.add_dp(dc_name, dat, time_point)
    
    def add_dp(self, dc_name, dat, time_point):
        dc = self[dc_name]
        dc.update_data_points(time_point, dat)
    
    def add_raw_values_dp(self, dc_name, dat, time_point):
        try:
            dc = self[dc_name]
        except KeyError:
            self.init_simple_value_store(self.save_dir, dc_name)
            dc = self[dc_name]
        simple_value_dict = self.simple_value(dat)
        dc.update_data_points(time_point, simple_value_dict)
    
    def add_gain_loss_dp(self, dc_name, cur_dat, prev_dat, time_point):
        try:
            dc = self[dc_name]
        except KeyError:  # Provide a fallback for when DataStore was not initialized, saving the data in the root save_dir
            self.init_gain_loss_store(self.save_dir, dc_name)
            dc = self[dc_name]
        gain_loss_dict = self.gain_loss(cur_dat,prev_dat)
        dc.update_data_points(time_point, gain_loss_dict)
    
    def add_simple_stats_dp(self, dc_name, dat, time_point):
        try:
            dc = self[dc_name]
        except KeyError:  # Provide a fallback for when DataStore was not initialized, saving the data in the root save_dir
            self.init_simple_stats_store(self.save_dir, dc_name)
            dc = self[dc_name]
        simple_stats_dict = self.simple_stats(dat)
        dc.update_data_points(time_point, simple_stats_dict)
            
    def add_frequency_stats_dp(self, dc_name, dat, column_names, time_point):
        dc = self[dc_name]
        freq_stats_dict = self.frequency_stats(dat, column_names)
        dc.update_data_points(time_point, freq_stats_dict)
        
    def add_count_stats_dp(self, dc_name, dat, time_point):
        dc = self[dc_name]
        dc.update_data_points(time_point, dat)

    def add_metabolic_stats_dp(self, dc_name, dat, time_point, cutoff=0.05):
        dc = self[dc_name]
        total = float(sum( dat.values()))
        most_common_metablic_types = dat.most_common(self.n_most_frequent_metabolic_types)
        most_common_metablic_types = filter(lambda x: x[1]/ total >= cutoff, most_common_metablic_types)
        most_common_types_dict = map(lambda x: dict(x[0]), most_common_metablic_types)
        most_common_types_per_category = dict([ (cat,[ d[cat] for d in most_common_types_dict ]) 
                                          for cat in self.metabolic_categories ])
        differences_dict = dict() # NOTE: unordered ok
        for cat, most_common_types in most_common_types_per_category.items():
            differences_dict.update(self.type_differences_stats(most_common_types,
                                                                self.met_difference_columns_dict[cat])) 
        dc.update_data_points(time_point, differences_dict)                                                      
        totals_dict = dict() # NOTE: unordered ok
        for cat, most_common_types in most_common_types_per_category.items():
            totals_dict.update(self.type_totals_stats(most_common_types,
                                                      self.met_capacity_columns_dict[cat]))
        dc.update_data_points(time_point, totals_dict)
        
    def write_data(self):
        for dc in self.data_collections.values():
            dc.write_data()
            
            
    def upgrade(self, odict):
        '''
        Upgrading from older pickled version of class to latest version. Version
        information is saved as class variable and should be updated when class
        invariants (e.g. fields) are added. (see also __setstate__) 
        
        Adapted from recipe at http://code.activestate.com/recipes/521901-upgradable-pickles/
        '''
        version = float(self.version)
        if version < 1.:
            self.base_save_dir = os.path.split(odict['save_dir'])[0]
            
            del self.__dict__['save_dir']
            del self.__dict__['pop_stats_dir']
            del self.__dict__['eco_stats_dir']
            del self.__dict__['ancestry_stats_dir']
            del self.__dict__['lod_stats_dir']
            del self.__dict__['best_stats_dir']
        if version < 1.1:
            self.init_dict_stats_store(save_dir=self.save_dir, stats_name='trophic type counts', index_name='time_point',
                                       column_names=self.trophic_type_columns)
        if version < 1.2:
            self.init_list_stats_store(save_dir=self.save_dir, stats_name='grid production values')
        if version < 1.3:
            save_dir = os.path.join(self.save_dir,self.eco_stats_dir)
            for stats_name in self.eco_diversity_stats_dict:
                self.init_simple_value_store(save_dir, stats_name)
        self.version = self.class_version
        if version > float(self.class_version):
            print 'upgraded class',
        else:
            print 'reset class', 
        print self.__class__.__name__, ' from version', version ,'to version', self.version
        
    def __setstate__(self, d):
        self.__dict__ = d
        # upgrade class if it has an older version
        if not hasattr(self, 'version'):
            self.version = '0.0'
        if self.version != self.class_version:
            self.upgrade(d)
        
            
    def __getitem__(self,key):
        '''
        Get a data collection in the DataStore under the key.
        
        The exception handling is in place to allow adding code to store new
        data types, while keeping compatibility with simulation load files that
        do not yet have an entry for this data type.
        
        '''
        dc = self.data_collections[key]
        return dc
