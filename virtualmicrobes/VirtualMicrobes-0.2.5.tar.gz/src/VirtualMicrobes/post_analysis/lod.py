'''
Created on Apr 11, 2015

@author: thocu
'''
import collections
import cython_gsl_interface.integrate as integrate  # @UnresolvedImport
from VirtualMicrobes.environment.Environment import Locality
import random
import VirtualMicrobes.simulation.Simulation as simu
import os
import numpy as np
from VirtualMicrobes.plotting.Graphs import BindingNetwork, MetabolicNetwork, Genome, PhyloTreeGraph
import VirtualMicrobes.my_tools.utility as util
import pandas as pd
import matplotlib.pyplot as plt
import glob
import shutil
import copy


def simple_stats(x):
    return (np.average(x), np.median(x), np.min(x), np.max(x), np.std(x))

def ancestor_networks(ancestors, GRN_grapher, metabolome_grapher, genome_grapher, max_genome_size, suffixes):
    
    for anc in ancestors:
        GRN_grapher.init_network(anc)
        GRN_grapher.layout_network_positions(prog='nwx')
        GRN_grapher.redraw_network()
        GRN_grapher.update_figure()
        for suffix in suffixes:
            GRN_grapher.save_fig(labels=[str(anc.time_birth).zfill(10), 'nwx'], suffix=suffix, bbox_inches='tight')
        #GRN_grapher.clear_graph()
        GRN_grapher.layout_network_positions(prog='dot')
        GRN_grapher.redraw_network()
        GRN_grapher.update_figure()
        for suffix in suffixes:
            GRN_grapher.save_fig(labels=[str(anc.time_birth).zfill(10), 'bound', 'dot'], suffix=suffix, bbox_inches='tight')
        
        GRN_grapher.redraw_network(edge_effect='effect_apo')
        GRN_grapher.update_figure()
        for suffix in suffixes:
            GRN_grapher.save_fig(labels=[str(anc.time_birth).zfill(10), 'apo', 'dot'], suffix=suffix, bbox_inches='tight')
        
        GRN_grapher.clear_graph()
        metabolome_grapher.redraw_network(reactions_dict=anc.reaction_set_dict,
                                          building_blocks=anc.building_blocks)
        metabolome_grapher.update_figure()
        for suffix in suffixes:
            metabolome_grapher.save_fig(labels=[str(anc.time_birth).zfill(10)], suffix=suffix, bbox_inches='tight')
        
        genome_grapher.plot_genome_structure(anc, labels=[str(anc.time_birth).zfill(10)],  
                                             max_size=max_genome_size)
        genome_grapher.update_figure()
        for suffix in suffixes:
            genome_grapher.save_fig(labels=[str(anc.time_birth).zfill(10)], suffix=suffix)

def lod_time_course_plots(ancestors, sim_graphs, save_dir, suffixes):
    fig = plt.figure(figsize=(12,12))
    mol_ax = fig.add_subplot(321)
    mol_ax.set_title('internal molecule conc')
    prot_ax = fig.add_subplot(323)
    prot_ax.set_title('protein concentration')
    size_ax = fig.add_subplot(322)
    size_ax.set_title('cell size')
    tox_ax = fig.add_subplot(324)
    tox_ax.set_title('toxicity')
    prod_ax = fig.add_subplot(326)
    prod_ax.set_title('production')
    
    for anc in ancestors:
        size_dat = anc.get_cell_size_time_course()
        if not len(size_dat[0,:]):
            continue
        
        mol_dat = anc.get_mol_time_course_dict()
        prot_dat = anc.get_gene_type_time_course_dict()
        
        tox_dat = anc.get_toxicity_time_course()
        prod_dat = anc.get_raw_production_time_course()
        
        
        sim_graphs.plot_mol_class_data(mol_ax, mol_dat)
        sim_graphs.plot_prot_data(prot_ax, prot_dat)
        
        title = size_ax.get_title()
        size_ax.clear()
        size_ax.set_title(title)
        size_ax.plot(size_dat[0,:],size_dat[1,:])
        
        title = tox_ax.get_title()
        tox_ax.clear()
        tox_ax.set_title(title)
        tox_ax.plot(tox_dat[0,:], tox_dat[1,:])
                     
        title = prod_ax.get_title()
        prod_ax.clear()
        prod_ax.set_title(title)
        prod_ax.plot(prod_dat[0,:], prod_dat[1,:])
        
        for suffix in suffixes:
            fig.savefig(os.path.join(save_dir,'time_course_'+str(anc.time_birth).zfill(10)+suffix), 
                         bbox_inches='tight')
        

def lod_time_course_data(ancestors, base_save_dir, viewer_path, chunk_size=100 ):
    
    for part, anc_chunk in enumerate(util.chunks(ancestors, chunk_size)):
        num = str(part).zfill(5)
        save_dir = os.path.join(base_save_dir, 'part{}'.format(num))
        util.ensure_dir(save_dir)
        
        for filename in glob.glob(os.path.join(viewer_path, '*')):
            shutil.copy2(filename, save_dir)
        
        prod_series = []
        cell_size_series = []
        tox_series = []
        mol_dfs = []
        prot_dfs = []
        for anc in anc_chunk:
            
            ts_dat =  anc.get_raw_production_time_course()
            ts = pd.Series(data=ts_dat[1], index=ts_dat[0])
            prod_series.append(ts)
            
            ts_dat =  anc.get_cell_size_time_course()
            ts = pd.Series(data=ts_dat[1], index=ts_dat[0])
            cell_size_series.append(ts)
            
            ts_dat =  anc.get_toxicity_time_course()
            ts = pd.Series(data=ts_dat[1], index=ts_dat[0])
            tox_series.append(ts)
            
            mol_time_courses = anc.get_mol_time_course_dict()
            mol_series = dict()
            for mol, tc in mol_time_courses.items():
                mol_series[mol] = pd.Series(data=tc[1], index=tc[0], name=mol) 
            mol_df = pd.DataFrame(mol_series)
            mol_dfs.append(mol_df)
            
            prot_time_courses = anc.get_total_reaction_type_time_course_dict()
            prot_series = dict()
            for _reac_type, tc_dict in prot_time_courses.items():
                for reac, tc in tc_dict.items():
                    if isinstance(reac, tuple):
                        reac, exp = reac
                        name = str(reac) 
                        name += '-e' if exp else '-i'
                    else:
                        name = str(reac)
                    prot_series[name ] = pd.Series(data=tc[1], 
                                                   index=tc[0], 
                                                   name=name ) 
            prot_df = pd.DataFrame(prot_series)
            prot_dfs.append(prot_df)
            
        prod_series = pd.concat(prod_series)
        prod_series = prod_series[~prod_series.index.duplicated(keep='last')]
        ts_base_name = os.path.join(save_dir,'production_time_course')
        prod_series.to_csv(ts_base_name+'.csv', index_label='time point')
        
        cell_size_series = pd.concat(cell_size_series)
        cell_size_series = cell_size_series[~cell_size_series.index.duplicated(keep='last')]
        ts_base_name = os.path.join(save_dir,'cell_size_time_course')
        cell_size_series.to_csv(ts_base_name+'.csv', index_label='time point')
        
        tox_series = pd.concat(tox_series)
        tox_series = tox_series[~tox_series.index.duplicated(keep='last')]
        ts_base_name = os.path.join(save_dir,'toxicity_time_course')
        tox_series.to_csv(ts_base_name+'.csv', index_label='time point')
        
        mol_df_combine = pd.concat(mol_dfs)
        mol_df_combine = mol_df_combine[~mol_df_combine.index.duplicated(keep='last')]
        df_base_name = os.path.join(save_dir,'mol_time_courses')
        mol_df_combine.to_csv(df_base_name+'.csv', index_label='time point')
        
        prot_df_combine = pd.concat(prot_dfs)
        prot_df_combine = prot_df_combine[~prot_df_combine.index.duplicated(keep='last')]
        df_base_name = os.path.join(save_dir,'prot_time_courses')
        prot_df_combine.to_csv(df_base_name+'.csv', index_label='time point')
        
class LOD_Analyser(object):
    '''
    Analyse the evolutionary history of a population by tracing ancestors in the
    line of descent.
    
    Load a population save from a file, keeping a reference in :attr:`ref_sim`.
    From this, initialize :attr:`pop_hist` as a :class:`PopulationHistory`
    object that can analyze the phylogenetic tree of the population and generateancestor_networks
    statistics on the line of descent (:class:`LOD`) of individuals in the
    population. It is possible to load additional population snapshot that
    preceed the focal :class:`PopulationHistory` and compare individuals to
    their contemporaries present in the preceding populations.
    :attr:`compare_saves` contains a list of file names of populations-saves
    that should be compared.
    '''
    
    def __init__(self, args):
        '''
        Initialize the analyzer from an argument dictionary. 
         
        Load the population save from file :param:`args`.pop_save and initialize
        special fields in its :class:`data_tools.store.DataStore` that can hold
        ancestor tracing data. From :attr:`ref_sim` initialize :attr:`pop_hist`
        as a :class:`PopulationHistory` that can be used to generate and analyze
        the evolutionary history of the population stored in :attr:`ref_sim`.
        
        :param args: arguments attribute dictionary
        '''
        self.args = args
        self.ref_sim = simu.load_simulation(args.pop_save, **vars(args))
        #self.ref_sim.data_store.init_ancestry_stats_names() 
        print 'historic maximum of production medium:', self.ref_sim.system.population.historic_production_max
        self.init_ref_history()
        self.compare_saves = args.compare_saves
        
    def init_ref_history(self, ref_sim=None, nr_lods=None, 
                         prune_depth=0, pop_hist_dir='population_history'):
        '''
        Create a :class:`PopulationHistory` from the :attr:`ref_sim`
        (:class:`simulation:Simulation.Simulation) object.
        
        For the :class:`PopulationHistory` object constructs its phylogenetic tree
        and prune back the tree to a maximum depth of (max_depth - prune_depth)
        counted from the root. Then create :class:`LOD` objects representing
        the *lines of descent* of the nr_lods *most diverged* branches in the tree. 
        
        Parameters
        ----------
        
        ref_sim : `simulation.Simulation.Simulation` object
        
        nr_lods : int nr_lods: nr of separate (most distant) lines of descent to initialize
        
        prune_depth : int 
            prune back phylogenies with this many timesteps 
        
        pop_hist_dir : str 
            name of directory to store lod analysis output
            
        '''
        if ref_sim is None:
            ref_sim = self.ref_sim
        if nr_lods is None:
            nr_lods = self.args.nr_lods
        tp = ref_sim.run_time
        save_dir = os.path.join(ref_sim.save_dir, pop_hist_dir+'_'+str(tp))
        self.pop_hist = PopulationHistory(sim=self.ref_sim, 
                                          params=self.ref_sim.params,
                                          nr_lods=nr_lods,
                                          save_dir=save_dir,
                                          prune_depth=prune_depth)
        self.pop_hist.init_phylo_tree()
        self.pop_hist.init_lods()
        self.pop_hist.init_pop_hist_data_store()
                        
    def compare_to_pops(self):
        '''
        Compare selected lines of descent in the reference simulation to a set
        of previous population snapshots in terms of mutation statistics.
                    
        '''
        # TODO check that compare saves are not older than the reference
        # and raise error when it is the case: 
        if not self.args.skip_store:
            self.ref_sim.data_store.init_ancestry_compare_stores(self.pop_hist)
        for compare_save in sorted(self.compare_saves, key=lambda n: int(n.strip('.sav').split('_')[-1])):
            self.pop_hist.compare_to_pop(compare_save)
            #self.compare_to_pop(compare_save)
            #self.ref_sim.data_store.write_data()
            
    def lod_stats(self):
        '''
        Write time series for line of descent properties.
        '''
        print 'Running LOD stats'
        self.pop_hist.lod_stats()
        
    def lod_network_stats(self):
        '''
        Write time series for line of descent network properties.
        '''
        print 'Running LOD Network stats'
        self.pop_hist.lod_network_stats()
        
    def lod_binding_conservation(self):
        '''
        Write time series for TF binding conservation in the line of descent.
        '''
        print 'Running LOD binding conservation'
        self.pop_hist.lod_binding_conservation()
            
    def draw_ref_trees(self):
        
        self.pop_hist.draw_ref_trees()
        
        
        
    def lod_networks(self, stride=None, time_interval=None, lod_range=None, formats=None): 
        if stride is not None and time_interval is not None:
            raise Exception('defining both lod_generation_interval and lod_time_interval is not allowed')
        if stride is None:
            stride = self.args.lod_generation_interval
        if time_interval is None:
            time_interval = self.args.lod_time_interval
        if lod_range is None:
            lod_range = self.args.lod_range
        if formats is None:
            formats = self.args.image_formats
        self.pop_hist.plot_lod_networks(stride, time_interval, lod_range, formats)

    def lod_time_courses(self, stride=None, time_interval=None, lod_range=None):
        '''
        Write time series for line of descent properties such as network
        connectivity, protein expression etc.
        
        Either use a stride or a time interval to sample individuals from the lod.
        '''
        if stride is not None and time_interval is not None:
            raise Exception('defining both lod_generation_interval and lod_time_interval is not allowed')
        if stride is None:
            stride = self.args.lod_generation_interval
        if time_interval is None:
            time_interval = self.args.lod_time_interval
        if lod_range is None:
            lod_range = self.args.lod_range
        self.pop_hist.lods_time_course_data(stride, time_interval, lod_range)
        
    def lod_time_course_plots(self, stride=None, time_interval=None, lod_range=None, formats=None):
        '''
        Write time series for line of descent properties such as network
        connectivity, protein expression etc.
        
        Either use a stride or a time interval to sample individuals from the lod.
        '''
        if stride is not None and time_interval is not None:
            raise Exception('defining both lod_generation_interval and lod_time_interval is not allowed')
        if stride is None:
            stride = self.args.lod_generation_interval
        if time_interval is None:
            time_interval = self.args.lod_time_interval
        if lod_range is None:
            lod_range = self.args.lod_range
        if formats is None:
            formats = self.args.image_formats
        self.pop_hist.lods_time_course_plots(stride, time_interval, lod_range, formats)
        
    def newick_trees(self):
        self.pop_hist.newick_trees()

    def __enter__(self):
        return self
    
    def __exit__(self, _type, _value, _traceback):     
        self.ref_sim.close_phylo_shelf()
        
    def __str__(self):
        return str(self.pop_hist)

class PopulationHistory(object):
    
    def __init__(self, sim, params, save_dir=None , nr_lods=1, prune_depth=None, root=None ):
        self.save_dir = save_dir
        if self.save_dir is not None:
            util.ensure_dir(self.save_dir)
        self.sim = sim
        self.params = params
        self.nr_lods = nr_lods
        self.prune_depth = prune_depth
        self.population = sim.system.population
        for anc in self.population.current_ancestors:
            if self.params.reconstruct_grn:
                anc.update_grn()
        self.environment = sim.system.environment
        self.time_point = sim.run_time
        self.init_rand_gens()
        self.init_test_bed()
        self.tree_lods = list()
    
    def init_phylo_tree(self, prune_depth=None):
        if prune_depth is None:
            prune_depth = self.prune_depth
        self.population.clear_pop_changes()
        self.population.update_phylogeny()
        self.population.phylo_tree.to_ete_trees()
        for root_id, ete_tree_struct in self.population.phylo_tree.ete_trees.items():
            print 'pruning ete tree', root_id
            if prune_depth is not None:
                max_depth = self.population.phylo_tree.max_depth
                print 'tree has depth', max_depth
                self.population.phylo_tree.ete_prune_external(ete_tree_struct, max(0, max_depth - prune_depth))
        
    def init_lods(self, nr_lods=None, save_dir=None,
                  stride=None, time_interval=None, lod_range=None):   
        if nr_lods is None:
            nr_lods = self.nr_lods
        if save_dir is None:
            save_dir = self.save_dir
        if stride is None:
            stride = self.params.lod_generation_interval
        if time_interval is None:
            time_interval = self.params.lod_time_interval
        if lod_range is None:
            lod_range = self.params.lod_range
            
        for root_id, ete_tree_struct in self.population.phylo_tree.ete_trees.items():
            
            tree_save_dir = root_id.split('_')[0]
            
            print 'constructing lines of descent for ete tree', root_id
            leafs = self.population.phylo_tree.ete_n_most_distant_phylo_units(ete_tree_struct, nr_lods)
            if sum( [ not leaf.has_living_offspring() for (leaf, _ete_node) in leafs ]):
                raise Exception('leaf with no living offspring found')
            print 'done'
            lods = collections.OrderedDict()
            for l1, l2, t_dist, top_dist in self.population.phylo_tree.distances(ete_tree_struct.tree,leafs):
                print l1.id, '-->', l2.id, ': time_dist :', t_dist, 'topology_dist :', top_dist
                 
            for leaf, _ete_node in leafs:
                for lod in leaf.lods_up():
                    name = str(leaf.id)
                    lod_save_dir = os.path.join(save_dir, tree_save_dir, name)
                    lods[leaf] = LOD(list(lod), name=name, save_dir = lod_save_dir,
                                          stride=stride, time_interval=time_interval, lod_range=lod_range)
                    break # record 1 lod per leaf
            self.tree_lods.append((ete_tree_struct,lods))
            
    def init_pop_hist_data_store(self):
        self.sim.data_store.init_phylo_hist_stores(phylo_hist=self)
        
    def identify_lod_ancestor(self, ete_tree_struct, lod):
        '''
        Identify the individual in the population that is on the line of descent
        (lod) under consideration.
          
        The nodes in the ete tree corresponding to the *lod* will be annotated
        with a tag.
        
        :param lod: a single line of descent to compare to this population
        '''
        last, last_ete = None, None
            
        phylo2ete_dict = self.population.phylo_tree.ete_get_phylo2ete_dict(ete_tree_struct)
        phylo_id2phylo = dict([ ( (str(phylo_unit.id),phylo_unit.time_birth), phylo_unit) 
                          for phylo_unit in phylo2ete_dict ])
        
        for anc in lod.lod: # going from oldest to youngest
            anc_id = (str(anc.id), anc.time_birth)
            if anc_id not in phylo_id2phylo:  # reached an ancestor that lives later than the leafs in the tree  
                break
            last = phylo_id2phylo[anc_id]
            last_ete = phylo2ete_dict[last][0]
            for ete_node in phylo2ete_dict[last]:
                ete_node.add_feature('lod', True) # annotate the ete nodes as being on the lod
        return last, last_ete
                  
    def init_rand_gens(self, rand_seed=None):
        if rand_seed is None:
            test_rand_seed = self.params.test_rand_seed
        self.test_rand = random.Random(int(test_rand_seed))
        
    def init_test_bed(self):
        self.test_bed = Locality(self.params,
                                 internal_molecules=self.environment.internal_molecules, 
                                 influx_reactions=self.environment.influx_reactions, 
                                 degradation_reactions=self.environment.degradation_reactions,
                                 env_rand=self.test_rand )
    
    def init_integrator(self, diffusion_steps=None, between_diffusion_reports=None,
                        max_retries=3, retry_steps_factor=2.):
        if diffusion_steps is None:
            diffusion_steps = self.params.diffusion_steps
        if between_diffusion_reports is None:
            between_diffusion_reports = self.params.between_diffusion_reports
        max_time_steps_store = max(int(diffusion_steps * between_diffusion_reports 
                                * retry_steps_factor ** (max_retries)), 1)
        integrator = integrate.Integrator(locality = self.test_bed, # @UndefinedVariable
                                          nr_time_points=max_time_steps_store,
                                          nr_neighbors=0,
                                          num_threads=1,
                                          step_function=self.params.step_function,  
                                          hstart=self.params.init_step_size,
                                          epsabs=self.params.absolute_error,
                                          epsrel=self.params.relative_error,
                                          init_time=0.)
        return integrator
    
    def newick_trees(self):
        for ete_tree_struct, lods in self.tree_lods:
            name = ete_tree_struct.tree.name.split('_')[0]
            filename = 'tree' + '_' + name 
            suffix = '.nw'
            ete_tree_struct.tree.write(format=1, 
                                       outfile=os.path.join(self.save_dir, 
                                                            filename + suffix))
    
    def lod_stats(self):
        '''
        Write time series for line of descent properties such as network
        connectivity, protein expression etc.
        
        Either use a stride or a time interval to sample individuals from the lod.
        '''
        cumulative_features = self.sim.data_store.mut_stats_names + self.sim.data_store.fit_stats_names + ['iterage']
        simple_features = self.sim.data_store.functional_stats_names
        for ete_tree_struct, lods in self.tree_lods: 
            self.population.annotate_phylo_tree(ete_tree_struct=ete_tree_struct,
                                                 features=cumulative_features)
            self.population.annotate_phylo_tree(ete_tree_struct=ete_tree_struct,
                                                 features=simple_features, cummulative=False)
            for ref, lod in lods.items():
                print ref.id
                self.sim.data_store.add_lod_data(ete_tree_struct, lod, self.population, self.environment)
        print 'done'
        #self.ref_sim.data_store.write_data()
    
    def lod_network_stats(self):
        '''
        Write time series for line of descent properties such as network
        connectivity, protein expression etc.
        
        Either use a stride or a time interval to sample individuals from the lod.
        '''
        for ete_tree_struct, lods in self.tree_lods:
            print 'ete_tree', ete_tree_struct.tree.name
            for ref, lod in lods.items():
                print 'lod', ref.id
                self.sim.data_store.add_lod_network_data(lod)
        print 'done'
        
    def lod_binding_conservation(self):
        '''
        Write time series for line of descent properties such as network
        connectivity, protein expression etc.
        
        Either use a stride or a time interval to sample individuals from the lod.
        '''
        for ete_tree_struct, lods in self.tree_lods:
            print 'ete_tree', ete_tree_struct.tree.name
            for ref, lod in lods.items():
                print 'lod', ref.id
                self.sim.data_store.add_lod_binding_conservation(lod)
        print 'done'
    
    def plot_lod_networks(self, stride, time_interval, lod_range, formats):
        metabolites = self.environment.mols_per_class_dict
        conversions = self.environment.reactions_dict['conversion']
        imports = self.environment.reactions_dict['import']
        
        suffixes = map(lambda fmt: '.'+fmt, formats)
        for ete_tree_struct, lods in self.tree_lods:
            print 'ete_tree', ete_tree_struct.tree.name
            for ref, lod in lods.items():
                print 'adding network graphs for lod', str(ref.id)
                attr_dict = self.sim.graphs.attribute_mapper
                GRN_grapher = BindingNetwork(lod.save_dir, 'GRN', attribute_dict=attr_dict, show=False)
                metabolome_grapher = MetabolicNetwork(lod.save_dir, 'Metabolome', 
                                                      mol_class_dict=metabolites, 
                                                      conversions=conversions,
                                                      imports=imports, 
                                                      attribute_dict=attr_dict, show=False)
                genome_grapher = Genome(lod.save_dir, 'Genome', attribute_dict=attr_dict, show=False) # Initialise grapher for genome structure (and make directory)
                ancestors = lod.strided_lod(stride, time_interval, lod_range)
                max_genome =  max( [ anc.genome_size for anc in ancestors ] )
                ancestor_networks(ancestors, GRN_grapher, metabolome_grapher, genome_grapher, max_genome, suffixes)
   
    def lods_time_course_plots(self, stride, time_interval, lod_range, formats):
        suffixes = map(lambda fmt: '.'+fmt, formats)
        for ete_tree_struct, lods in self.tree_lods:
            print 'ete_tree', ete_tree_struct.tree.name
            for ref, lod in lods.items():
                print 'lod', ref.id
                save_dir = os.path.join(lod.save_dir, 'time_course_plots')
                util.ensure_dir(save_dir)
                ancestors = lod.strided_lod(stride, time_interval, lod_range)
                lod_time_course_plots(ancestors, self.sim.graphs, 
                                     save_dir = save_dir, suffixes=suffixes)
     
    def lods_time_course_data(self, stride, time_interval, lod_range):
        for ete_tree_struct, lods in self.tree_lods:
            print 'ete_tree', ete_tree_struct.tree.name
            for ref, lod in lods.items():
                print 'lod', ref.id
                save_dir = os.path.join(lod.save_dir, 'time_courses')
                util.ensure_dir(save_dir)
                ancestors = lod.strided_lod(stride, time_interval, lod_range)
                lod_time_course_data(ancestors, base_save_dir = save_dir,
                                     viewer_path=os.path.join(self.sim.utility_path, 'time_course_viewer'))
        
    def draw_ref_trees(self):    
        for ete_tree_struct, lods in self.tree_lods:
            func_features={'metabolic_type':self.population.metabolic_type_color}
            self.population.annotate_phylo_tree(ete_tree_struct,
                                                 func_features=func_features,
                                                  #max_tree_depth=max_depth,
                                                  cummulative=False,
                                                  prune_internal=True, 
                                                  to_rate=False 
                                                  )
            for leaf, lod in lods.items():        
                self.population.phylo_tree.annotate_phylo_units_feature(ete_tree_struct, 
                                                                        lod.lod, 'in_lod')
                self.population.phylo_tree.annotate_leafs(ete_tree_struct, leaf)
            
            attr_dict = self.sim.graphs.attribute_mapper
            range_dic = self.population.value_range_dict
            rescale_factor = 500.0 / self.population.phylo_tree.ete_calc_lca_depth(ete_tree_struct.tree)
            print 'rescale factor is ' + str(rescale_factor)
    
            save_loc = os.path.join(self.save_dir,
                                    ete_tree_struct.tree.name.split('_')[0], 
                                    'ancestry_plots')
            #phylo_grapher = PhyloTreeGraph(save_loc, name='Phylotree', attribute_dict=attr_dict, range_dict=range_dic, show=False)
            phylo_grapher = PhyloTreeGraph(save_loc, name='Phylotree', attribute_dict=attr_dict, show=False)    
            phylo_grapher.update(ete_tree_struct.tree)
            phylo_grapher.save_fig(feature='metabolic_with_lod', name='lodstree', 
                                   rescale=rescale_factor, dpi=10, suffix=".svg")
            print 'Plotted reference tree'
            
    def compare_to_pop(self, compare_save, prune_depth=None, leafs_sample_size=None):
        '''
        Compare the reference :class:`PopulationHistory` to an earlier population-save. 
        
        Parameters
        ----------
        
        compare_save : str
            file location of population-save 
            
        prune_depth : int 
            prune back phylogeny of the :param:compare_save with this many timesteps 
            
        leafs_sample_size : int
            maximum number of phylogenetic tree leafs to use for comparison
        '''
        if prune_depth is None:
            prune_depth = self.params.prune_compare_pop
        if leafs_sample_size is None:
            leafs_sample_size = self.params.leafs_sample_size
        
        params = copy.copy(self.params)
        params['name'] = os.path.join(params['name'], 'temp')
        compare_sim = simu.load_simulation(compare_save, **params)
        comp_pop_hist = PopulationHistory(sim=compare_sim, 
                                     params=self.sim.params,
                                     prune_depth=prune_depth)
        comp_pop_hist.init_phylo_tree()
        comp_phylo_tree = comp_pop_hist.population.phylo_tree
        time_point = int(compare_save.strip('.sav').split('_')[-1])
        cumulative_features = (self.sim.data_store.mut_stats_names + 
                               self.sim.data_store.fit_stats_names + ['iterage'] )
        for ref_ete_tree_struct, ref_lods in self.tree_lods: 
            
            for comp_ete_tree_struct in comp_phylo_tree.ete_trees.values():
                if ref_ete_tree_struct.tree.name != comp_ete_tree_struct.tree.name:
                    # not comparing trees with the same root
                    continue
                
                comp_pop_hist.population.annotate_phylo_tree(ete_tree_struct=comp_ete_tree_struct,
                                                              features=cumulative_features)
                comp_dat = comp_ete_tree_struct, comp_pop_hist
                self.sim.data_store.add_ancestry_data_point(comp_dat, ref_lods, 
                                                            time_point, 
                                                            leafs_sample_size)
        compare_sim.close_phylo_shelf()
        
    def __str__(self):
        return '\n'.join([ str(lod) for tree_lods in self.tree_lods 
                          for lod in tree_lods[1] ])

class LOD(object):
    '''
    classdocs
    '''

    def __init__(self, lod, name, stride, time_interval, lod_range,  save_dir=None):
        '''
        Store the line of descent to analyse.
        '''
        self.lod = lod
        self.name = name
        self.stride = stride
        self.time_interval = time_interval
        self.lod_range = lod_range
        self.save_dir = save_dir
        if self.save_dir is not None:
            util.ensure_dir(self.save_dir)

    def standardized_production(self, test_params):
        for c in self.lod:
            self.test_bed.clear_locality()
            self.test_bed.add_cell(c)
            integrator = self.init_integrator()
            self.run_system(integrator)
    
    def strided_lod(self, stride=None, time_interval=None, lod_range=None):
        if stride is None:
            stride = self.stride
        if time_interval is None:
            time_interval = self.time_interval
        if lod_range is None:
            lod_range = self.lod_range
            
        if lod_range is None:
            lod_range = (0.,1.)
        if stride is not None and time_interval is not None:
            raise Exception('defining both stride and time_interval is not allowed')
        lod_all = list(self)
        if stride is not None:
            ancestors = lod_all[::stride] 
        elif time_interval is not None:
            ancestors = list(self.t_interval_iter(time_interval))      
        else:
            ancestors = lod_all
        if ancestors[-1] != lod_all[-1]:
            ancestors.append(lod_all[-1])
        
        from_root, from_leaf = int(lod_range[0]*len(ancestors)), int(lod_range[1]*len(ancestors))
        return ancestors[from_root:from_leaf]
    
    def t_interval_iter(self, time_interval):
        '''
        iterate ancestors that are approximately 'time_interval' timesteps apart
        in their time of birth.
        '''
        mod_time = time_interval
        for anc in self:
            prev_mod_time = mod_time
            mod_time = anc.time_birth % time_interval
            if mod_time > prev_mod_time:
                continue
            yield anc
            
    
    def __iter__(self):
        return iter(self.lod)
        
    def __str__(self):
        return '\t'+'\n\t'.join([ str(c) for c in self.lod ])
        
        
    
