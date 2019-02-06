from VirtualMicrobes.virtual_cell.Cell import Cell
import random
#from profilestats import profile

import numpy as np
try:
    import bottleneck as bt
    np.nanmean = bt.nanmean
except ImportError:
    pass
from VirtualMicrobes.Tree.PhyloTree import PhyloTree
import itertools as it
import VirtualMicrobes.my_tools.utility as util
import collections
from VirtualMicrobes.virtual_cell.PhyloUnit import PhyloUnit
import orderedset

def _production_scaling_func(x):
    return x

class Population(object):
    class_version = '0.0'

    """
     
    """
    
    def __init__(self, params, environment):
        ### take a reference of the global paramaters ###
        self.version = self.__class__.class_version
        self.params = params
        self.init_pop_rand_gen(self.params.pop_rand_seed)
        self.init_evo_rand_gens(self.params.evo_rand_seed)
        self.reconstruct_tree = False
        self.init_phylo_tree()
        self.init_pop(environment, self.params.init_pop_size, self.params)
        self.max_pop_size = self.params.max_cells_per_locality * len(environment.localities) 
        self.historic_production_max = 0.
        self.production_val_history = []
        self.init_range_dicts()
        
    def init_range_dicts(self):
        self.markers_range_dict = dict()  # NOTE: unordered ok
        self.markers_range_dict['metabolic_type'] = (0, self.max_pop_size * 2)
        self.markers_range_dict['lineage'] = (0, self.max_pop_size * 2)
        self.metabolic_type_marker_dict = util.ReusableIndexDict(fixed_length=self.max_pop_size * 2)
        self.value_range_dict = dict()  # NOTE: unordered ok
            
    def init_pop_rand_gen(self, pop_rand_seed=None):
        if pop_rand_seed is None:
            pop_rand_seed = self.params.pop_rand_seed
        self.pop_rand_gen = random.Random(int(pop_rand_seed))
        
    def init_evo_rand_gens(self, evo_rand_seed=None):
        if evo_rand_seed is None:
            evo_rand_seed = self.params.evo_rand_seed
        self.evo_rand_gen = random.Random(int(evo_rand_seed))
        self.evo_rand_gen_np = np.random.RandomState(int(evo_rand_seed))
        
    def init_pop(self, environment, pop_size = None, params_dict=None):
        if params_dict is None:
            params_dict = self.params
        if pop_size is None:
            pop_size = self.params.init_pop_size    
        self.current_pop_size = 0
        self.cell_dict = collections.OrderedDict()
        self.init_cells_view()
        self.died = []
        self.new_offspring = []
        self.pruned_cells = set()
        if self.params.single_clone_init:
            common_ancestor = self.cloned_pop(pop_size, environment, params_dict)
            self.init_current_ancestors()
            self.init_roots([common_ancestor])
            self.cell_death(common_ancestor, time=0)
            self.update_phylogeny()
        else:
            self.unique_pop(pop_size, environment, params_dict)
            self.init_current_ancestors()
            self.init_roots()
            self.update_phylogeny() #self.roots)
        
        
    def unique_pop(self, pop_size, environment, params_dict ):
        for _ in range(pop_size):
            cell = Cell(params=params_dict, environment=environment,
                        rand_gen=self.pop_rand_gen)
            self.add_cell(cell)
    
    def cloned_pop(self, pop_size, environment, params_dict, time=0):
        common_ancestor = Cell(params=params_dict, environment=environment, 
                        rand_gen=self.pop_rand_gen, time_birth=-1)
        self.add_cell(common_ancestor)
        for _ in range(pop_size):
            clone = common_ancestor.clone(time)
            self.add_cell(clone)
        return common_ancestor
        
    def add_cell(self,cell):
        self.cell_dict[cell] = dict()  # NOTE: unordered ok
        self.cell_dict[cell]['child_count'] = 0
        self.current_pop_size += 1

    def init_current_ancestors(self):
        self.current_ancestors = util.LinkThroughSet(self.cells)
    
    def init_roots(self, roots=None):
        if roots is None:
            self.roots = self.current_ancestors.copy()
        else:
            self.roots = util.LinkThroughSet(roots)
        
    def init_phylo_tree(self, supertree=None):
        if supertree is None:
            supertree = not self.params.single_clone_init
        self.phylo_tree = PhyloTree(supertree=False)#supertree)
        
    def update_phylogeny(self, new_roots=None, reconstruct_tree=None):
        if reconstruct_tree is None:
            reconstruct_tree = self.reconstruct_tree
        
        # add new offspring to the set of all ancestors
        self._update_current_ancestors(set(self.new_offspring))
        # prune dead branches of phylogenies
        self._clear_extinct_lineages()
        if reconstruct_tree:
            print 'reconstructing phylo tree'
            self.phylo_tree.clear()
            tree_nodes = [anc for anc in self.current_ancestors if not anc.alive]
            roots = [ r for r in self.roots if not r.alive]
            self.phylo_tree.update(new_phylo_units=set(tree_nodes) - set(roots) , new_roots=roots)
            self.reconstruct_tree = False
        else:
            died = set(self.died)
            new_roots = died & set(list(self.roots))
            not_in_tree = died & self.pruned_cells
            self.phylo_tree.update(new_phylo_units=died - not_in_tree - new_roots, 
                                   removed_phylo_units=self.pruned_cells - not_in_tree,
                                   new_roots=new_roots )
        self._clear_from_phylo_linker()
        n = len(self.current_ancestors)
        print "now %d ancestor%s" % (n, "s"[n==1:]) , 'and',  
        n = len(self.roots)
        print "%d root%s" % (n, "s"[n==1:])  , 
        #n = len(filter(lambda r: not r.alive, self.roots))
        #print "(%d dead root%s)" % (n, "s"[n==1:])  , 
        n = len(self.phylo_tree.roots)
        print "%d phylo-root%s" % (n, "s"[n==1:])  
            
    def _update_current_ancestors(self, new_offspring):
        self.current_ancestors.update(new_offspring)
        
    def update_cell_params(self, cells=None):
        if cells is None:
            cells = self.cells
        for cell in cells:
            cell.init_cell_params()
    
    def _clear_extinct_lineages(self):
        self._prune_dead_branches()
        self._prune_current_ancestors()
        self._prune_roots()
        
    def _clear_from_phylo_linker(self):
        self._remove_pruned_from_phylo_linker()

    def _prune_dead_branches(self, dead_cells=None):
        if dead_cells is None:
            dead_cells = self.died
        self.pruned_cells = set()
        self.pruned_chromosomes = set()
        self.pruned_genes = set()
        for cell in dead_cells:
            cells, chromosomes, genes = cell.prune_dead_phylo_branches()
            self.pruned_cells.update(cells)
            self.pruned_chromosomes.update(chromosomes)
            self.pruned_genes.update(genes)
        print len(self.pruned_cells), 'cells', len(self.pruned_chromosomes), 'chromosomes', 
        print len(self.pruned_genes), 'genes pruned'
        return self.pruned_cells, self.pruned_chromosomes, self.pruned_genes
    
    def _prune_current_ancestors(self):
        self.current_ancestors -= self.pruned_cells 
        
    def _prune_roots(self):
        self.roots &= self.current_ancestors
        
    def _remove_pruned_from_phylo_linker(self):
        phylo_units = self.pruned_cells | self.pruned_chromosomes | self.pruned_genes
        for phylo_unit in phylo_units:
            if isinstance(phylo_unit, PhyloUnit):# and not phylo_unit in self.died:
                phylo_unit._remove_from_linker_dict()
        
    def clear_pop_changes(self):
        self.new_offspring, self.pruned_cells, self.died = [], set(), []
        
    def reset_divided(self):
        for cell in self.cells:
            cell.divided = False
        
    def init_cells_view(self):
        self.cells = self.cell_dict.viewkeys()
        
    def genome_sizes(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array([ cell.genome_size for cell in cells])
            
    def chromosome_counts(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array([ cell.chromosome_count for cell in cells])
    
    def tf_counts(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array([ cell.tf_count for cell in cells])
    
    def enzyme_counts(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array([ cell.enzyme_count for cell in cells])
    
    def exporter_counts(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array([ cell.eff_pump_count for cell in cells])
    
    def importer_counts(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array([ cell.inf_pump_count for cell in cells])
    
    def point_mut_counts(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array([ cell.point_mut_count for cell in cells])
    
    def chromosomal_mut_counts(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array([ cell.chromosomal_mut_count for cell in cells])
    
    def death_rates(self, cells=None):
        death_rate_dict = self.get_cell_death_rate_dict(cells)
        return np.array([ d for d in death_rate_dict.values() if d is not None ])
    
    def production_values(self, cells=None):
        production_value_dict = self.get_cell_production_dict(cells)
        return np.array([ prod for prod in production_value_dict.values() if prod is not None ])

    def pos_production(self, cells=None):
        pos_production_dict = self.get_cell_pos_production_dict(cells)
        return np.array([ prod for prod in pos_production_dict.values() if prod is not None ])
    
    def production_rates(self, cells=None):
        production_rate_dict = self.get_cell_production_rate_dict(cells)
        return np.array([ prod for prod in production_rate_dict.values() if prod is not None ])
    
    def cell_sizes(self, cells=None):
        cell_size_dict = self.get_cell_size_dict(cells)
        return np.array([ size for size in cell_size_dict.values() if size is not None ])
    
    def toxicity_rates(self, cells=None):
        toxicity_change_dict = self.get_cell_toxicity_rate_dict(cells)
        return np.array([ prod for prod in toxicity_change_dict.values() if prod is not None ])
    
    def average_promoter_strengths(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array( [ cell.avrg_promoter_strengths for cell in cells] )
    
    def tf_average_promoter_strengths(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array( [ cell.tf_avrg_promoter_strengths for cell in cells] )
    
    def enz_average_promoter_strengths(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array( [ cell.enz_avrg_promoter_strengths for cell in cells] )
    
    def pump_average_promoter_strengths(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array( [ cell.pump_avrg_promoter_strengths for cell in cells] )
    
    def differential_regulation(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.tf_differential_reg) for cell in cells] )
    
    def pump_average_vmaxs(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.pump_vmaxs) for cell in cells] )
    
    def enzyme_average_vmaxs(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.enz_vmaxs) for cell in cells] )
    
    def tf_k_bind_operators(self, cells = None):
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.tf_k_bind_ops) for cell in cells])
    
    def tf_ligand_ks(self, cells = None):
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.tf_ligand_ks) for cell in cells])
    
    def enzyme_substrate_ks(self, cells = None):
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.enz_subs_ks) for cell in cells])
    
    def pump_substrate_ks(self, cells = None):
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.pump_subs_ks) for cell in cells])
    
    def pump_energy_ks(self, cells = None):
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.pump_ene_ks) for cell in cells])
    
    
    def offspring_counts(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array([ len(c.living_offspring()) for c in cells ])
    
    def iterages(self, cells=None):
        if cells is None:
            cells = self.cells
        return np.array([ cell.iterage for cell in cells])
    
    def pan_metabolome_dict(self, cells=None):
        pan_genome_dict = {'import':set(), 'conversion':set()}
        if cells is None:
            cells = self.cells
        for cell in cells:
            for (reac_type, reac_set) in cell.reaction_set_dict.items():
                pan_genome_dict[reac_type].update(reac_set)
        return pan_genome_dict  
    
    def reaction_counts(self, cells=None):
        if cells is None:
            cells = self.cells
        all_reactions = []
        for cell in cells:
            for reac_set in cell.reaction_set_dict.values():
                all_reactions += list(reac_set)
        return collections.Counter(all_reactions)
    
    def trophic_type_counts(self, env, cells=None):
        if cells is None:
            cells = self.cells
        return collections.Counter([ cell.trophic_type(env) for cell in cells ])
    
    def reaction_counts_split(self, cells=None):
        if cells is None:
            cells = self.cells
        reaction_counts_split = collections.defaultdict(list)
        for cell in cells:
            for reac_type, reac_set in cell.reaction_set_dict2.items():
                reaction_counts_split[reac_type] += list(reac_set)
        return dict( [ (reac_type, collections.Counter(reacs)) for reac_type, reacs in reaction_counts_split.items() ])
    
    def metabolic_type_counts(self, cells=None):  
        ''' Frequencies of cell sets with equal metabolic capabilities
        
        A metabolic type is defined on the bases of the full set of metabolic reactions
        that an individual can perform using its metabolic gene set.
        A frequency spectrum of these types is than produced in the form of a 
        collections.Counter object. From this object we can ask things like:
        most_common(N) N elements etc.
        '''
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( cell.metabolic_type for cell in cells )
        return type_counts
    
    def producer_type_counts(self, cells=None):
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( map(frozenset, ( c.produces for c in cells ) ) )
        return type_counts
    
    def consumer_type_counts(self, cells=None):
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( map(frozenset, ( c.consumes for c in cells ) ) )
        return type_counts
    
    def import_type_counts(self, cells=None):
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( map(frozenset, ( c.import_type  for c in cells ) ) )
        return type_counts
    
    def export_type_counts(self, cells=None):
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( map(frozenset, ( c.export_type for c in cells ) ) )
        return type_counts
    
    def genotype_counts(self, cells=None):  
        ''' 
        Frequencies of cell sets with equal genotypes
        '''
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( cell.genotype for cell in cells )
        return type_counts
    
    def reaction_genotype_counts(self, cells=None):  
        ''' 
        Frequencies of cell sets with equal reaction genotypes
        '''
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( cell.reaction_genotype for cell in cells )
        return type_counts
    
    @classmethod
    def metabolic_complementarity(cls, cells, strict_providing=False, strict_exploiting=False):
        '''
        Determine for the list of cells what the overlap is in metabolites
        provided and exploited. To provide a metabolite a cell should
        simultaneous produce and export the metabolite. To exploit, it should be
        imported and consumed in a reaction.
        '''
        provided = set.union(set(),*[ c.strict_providing if strict_providing else c.providing  for c in cells ])
        exploited = set.union(set(),*[ c.strict_exploiting if strict_exploiting else c.exploiting for c in cells])
        return provided & exploited
    
    def metabolic_complementarity_pop(self, strict=False):
        return self.metabolic_complementarity(self.cells, strict)
    
    def get_cell_death_rate_dict(self, cells=None):
        return self._get_cell_property_dict("death_rate", cells)
    
    def get_cell_production_dict(self, cells=None, life_time_prod=None):
        '''
        Map cells to their last/ life time production value.
        
        Parameters
        ----------
        cells : sequence of Cell objects
            individuals to map, default is the current population
        life_time_prod : bool
            take life time mean production instead of current
        '''
        if cells is None:
            cells = self.cells
        if life_time_prod is None:
            life_time_prod = self.params.life_time_prod
        if life_time_prod:
            return collections.OrderedDict( [ (c, c.mean_life_time_production) for c in cells ] )
        return collections.OrderedDict( [ (c, c.raw_production) for c in cells ] )
    
    def get_cell_pos_production_dict(self, cells=None):
        if cells is None:
            cells = self.cells
        return collections.OrderedDict( [ (c, c.mean_life_time_pos_production) for c in cells ] )
    
    def get_cell_production_rate_dict(self, cells=None):
        if cells is None:
            cells = self.cells
        return collections.OrderedDict( [ (c, c.raw_production_change_rate) for c in cells ] )
    
    def get_cell_size_dict(self, cells=None):
        if cells is None:
            cells = self.cells
        return collections.OrderedDict( [ (c, c.volume) for c in cells ] )
    
    def get_cell_toxicity_rate_dict(self, cells=None):
        if cells is None:
            cells = self.cells
        return collections.OrderedDict( [ (c, c.toxicity_change_rate) for c in cells ] )
    
    def get_cell_reproduction_dict(self, cells=None):
        '''
        Counts of the number of reproduction events for each cell (living and
        dead direct children)
        '''
        return self._get_cell_property_dict("child_count", cells)
    
    def _get_cell_property_dict(self, prop_name, cells=None):
        if cells is None:
            cells = self.cells
        cell_property_dict = collections.OrderedDict()
        for cell in cells:
            if self.cell_dict[cell].has_key(prop_name):
                cell_property_dict[cell] = self.cell_dict[cell][prop_name]
            else:
                cell_property_dict[cell] = None
        return cell_property_dict
    
        
    def get_cell_death_rate(self, cell):
        return self._get_cell_property(cell, "death_rate")
    
    def get_cell_production(self, cell):
        return cell.raw_production
    
    def _get_cell_property(self, cell, prop_name):
        prop_val = None
        if self.cell_dict[cell].has_key(prop_name):
            prop_val = self.cell_dict[cell][prop_name]
        return prop_val
    
    def update_ete_tree(self):
        '''
        Update the ete tree representation of the phylo_tree.
        '''
        return  self.phylo_tree.to_ete_trees()
    
    
    def metabolic_type_color(self, cell):
        mt_low, mt_high = self.markers_range_dict['metabolic_type']
        metabolic_type = cell.marker_dict.get('metabolic_type',0.)
        mt_color = metabolic_type/ float((mt_high - mt_low)) + mt_low
        return mt_color
    
    def annotate_phylo_tree(self, ete_tree_struct, 
                             features=[], func_features=dict(), max_tree_depth=None, 
                             prune_internal=False, cummulative=True, to_rate=False, 
                             ete_root=None):
        '''
        Annotate the phylogenetic tree with cell data for tree plotting.
        
        Assumes that the ete_tree has been constructed/updated. Creates a
        dictionary of feature dictionaries, keyed by the cells in the tree.
        Attaches the feature dictionaries to nodes in the ete_tree
        (annotate_ete_tree). Transforms some data to cummulative data along the
        branches of the tree. Optionally, prunes internal tree nodes (this will
        greatly simplify the tree drawing algorithm). Finally, transforms some
        data to rate of change data, using branch length for rate calculation.
        
        :param prune_internal: if True, nodes with 1 offspring only will be
        removed/collapsed and their branch length added to the preceding node on
        the branch.
        '''
        if ete_root is None:
            ete_root = ete_tree_struct.tree
        if max_tree_depth is not None:
            self.phylo_tree.ete_prune_external(ete_tree_struct, max_tree_depth)
        self.phylo_tree.ete_annotate_tree(ete_tree_struct, features, 
                                          func_features, ete_root)
        if cummulative:
            self.phylo_tree.ete_cummulative_features(ete_tree_struct, features, 
                                                     func_features, ete_root)
        if prune_internal:
            self.phylo_tree.ete_prune_internal(ete_tree_struct)
        if to_rate:
            max_rate_dict = self.phylo_tree.ete_rate_features(ete_tree_struct, features, 
                                                              func_features, ete_root)
            self.value_range_dict.update( (feature, (0, max_rate)) for feature, max_rate in max_rate_dict.items() )
    
    def ancestors_all_phylo_units(self):
        phylo_units = set()
        for anc in self.current_ancestors:
            phylo_units.update( set([ g for g in anc.genome ]) )
            phylo_units.update( set(anc.genome.chromosomes))
            phylo_units.update( anc.genome.operators)
            phylo_units.update( anc.genome.binding_sequences)
            phylo_units.add(anc)
        return phylo_units
    
    def check_sane_concentrations(self, sane_value=(0.,500), cells=None):
        if cells is None:
            cells = self.cells
        for c in cells:
            insane = c.check_sane_values(sane_value)
            if insane:
                print "cell"+str(c.id)
                mol_tc = c.get_mol_time_course_dict()
                for m, tc in mol_tc.items():
                    print m
                    print tc
                gene_tc = c.get_gene_time_course_dict()
                for g, tc in gene_tc.items():
                    print g
                    print tc
    
    def print_state(self):
        for c in self.cells:
            print "cell"+str(c.id)
            for m, conc in c.get_mol_concentration_dict().items():
                print "("+str(m), str(conc)+")",
            for g, conc in c.get_gene_concentration_dict().items():
                print "("+str(g.id)+g['type'], str(conc)+")",
            print '(tox', str(c.toxicity)+")",
            print '(prod', str(c.raw_production)+")" 
    
    def set_mol_concentrations_from_time_point(self, pos=None):
        for c in self.cells:
            c.set_mol_concentrations_from_time_point(pos)
        
    def best_producer(self):
        best_producer, production = None, 1e-200
        for cell, prod in self.get_cell_production_dict().items():
            if prod is None:
                continue
            if prod > production:
                best_producer = cell
                production = prod
        if best_producer is None:
            print "No cell with production found. Production dict is:"
            print self.get_cell_production_dict()
            #for cell in self.cells:
            print list(self.cells)[0].raw_production_time_course
            raise Exception('No production, no simulation')
            best_producer, prod = self.pop_rand_gen.choice(list(self.cells)), 0
        return best_producer, production

    def most_offspring(self):
        most_fecundant, offspring_count = None, 0
        for cell in self.cells:
            oc = len(cell.living_offspring()) 
            if oc >= offspring_count:
                most_fecundant, offspring_count = cell, oc
        return most_fecundant, offspring_count
    
    def oldest_cell(self):
        bt_sorted = sorted(self.cells, key=lambda c: c.time_birth)
        oldest_cell = None
        try:
            oldest_cell = bt_sorted.pop(0) 
        except:
            pass
        return oldest_cell
    
    def cap_death_rates(self, _max):
        for cell in self.cells:
            self.cell_dict[cell]['death_rate'] = min(self.cell_dict[cell]['death_rate'], _max)
    
    def calculate_death_rates(self,base_death_rate=None, max_die_off_fract=None, 
                              toxicity_scaling=None, cells=None):
        if cells is None:
            cells = self.cells
        if max_die_off_fract is None:
            max_die_off_fract = self.params.max_die_off_fraction
        if base_death_rate is None:
            base_death_rate = self.params.base_death_rate
        if toxicity_scaling is None:
            toxicity_scaling = self.params.toxicity_scaling
        for cell in cells:
            raw_death_rate = cell.calculate_raw_death_rate(base_rate=base_death_rate,
                                                           toxicity_scaling=toxicity_scaling)
            self.cell_dict[cell]["death_rate"] = raw_death_rate
        if max_die_off_fract: 
            self.scale_death_rates(max_die_off_fract, cells)
                    
    def scale_death_rates(self, max_die_off_fract, cells=None):
        util.within_range(max_die_off_fract, (0., 1.))
        if cells is None:
            cells = self.cells
        total_death = sum(self.death_rates())
        raw_death_frac = total_death/float(self.current_pop_size)
        if raw_death_frac > max_die_off_fract:
            print "raw death fraction", raw_death_frac
            scaling = raw_death_frac/max_die_off_fract
            for cell in self.cells:
                self.cell_dict[cell]['death_rate'] /=scaling
                
    def wipe_pop(self, fract, time, min_surv=None, cells=None):
        if cells is None:
            cells = list(self.cells)
        self.pop_rand_gen.shuffle(cells)
        kill_num = int(fract*len(cells)) # Number of cells that will die
        if min_surv is not None and self.current_pop_size - kill_num < min_surv:
            kill_num -=  (min_surv - (self.current_pop_size - kill_num))
        for cell in cells[:kill_num]:
            self.cell_death(cell, time, wiped=True)
        
    def cell_death(self, cell, time, wiped=False):
        del self.cell_dict[cell]
        self.current_pop_size -= 1
        cell.die(time, wiped=wiped)
        self.died.append(cell)
            
    def die_off(self,time, max_die_off_frac=None):
        '''
        assumes death rates have been calculated and set
        :param max_die_off_frac:
        '''
        if max_die_off_frac is None:
            max_die_off_frac = self.params.max_die_off_fraction
        max_die = len(self.cells) 
        if max_die_off_frac is not None:
            max_die = int(max_die * max_die_off_frac)
        death_count = 0
        for cell in list(self.cells):
            if death_count>=max_die:
                break
            if self.params.min_cell_volume is not None and cell.volume < self.params.min_cell_volume:
                death_count+=1 
                self.cell_death(cell, time)
            elif self.evo_rand_gen.uniform(0,1.) < self.cell_dict[cell]['death_rate']:
                death_count+=1
                self.cell_death(cell, time)
        
            
    def reproduce_cell(self,cell, time, spent_production=0., report=False):
        if report:
            print str(cell.id)+": reproducing. Production reached:", cell.raw_production 
        offspring = cell.reproduce(spent_production=spent_production, time=time)
        self.cell_dict[cell]['child_count'] += 1
        self.add_cell(offspring)
        return offspring
        
    def find_the_one(self, cells_competition_value, rand_nr, non=0. , competition_scaling_fact=None):
        if competition_scaling_fact is None:
            competition_scaling_fact = self.params.competition_scaling
        competition_scaling = lambda p, n : p ** n
        cells_competition_value = [ (c, competition_scaling(p, competition_scaling_fact)) 
                                   for (c,p) in cells_competition_value ]
        non = competition_scaling(non, competition_scaling_fact)
        return util.roulette_wheel_draw(cells_competition_value, rand_nr, non)
            
    def prune_metabolic_types(self, cells=None):
        if cells is None:
            cells = self.cells
        cell_metabolic_types = self.metabolic_type_counts(cells).keys()
        extinct = set(self.metabolic_type_marker_dict.keys()) - set(cell_metabolic_types)
        for met_type in extinct:
            self.metabolic_type_marker_dict.remove_key(met_type)
    
    def store_pop_characters(self):
        self.mark_cells_metabolic_type()
    
    def calculate_cells_production(self, production_scaling_funct=None):
        if production_scaling_funct is None:
            production_scaling_funct = _production_scaling_func
        for cell in self.cells:
            production = production_scaling_funct(cell.raw_production)
            self.cell_dict[cell]["production"] = production
    
    def reproduce_at_minimum_production(self, time, competitors=None, max_reproduce=None, reproduction_cost=None):
        if competitors is None:
            competitors = self.cells
        if max_reproduce is None:
            max_reproduce = self.max_pop_size - len(self.cells)
        if reproduction_cost is None:
            reproduction_cost = self.params.reproduction_cost
        new_offspring = []
        cells_production = [ (c,p) for (c,p) in self.get_cell_production_dict(competitors).items() 
                                   if p >= reproduction_cost]
        while cells_production:
            if len(new_offspring) >= max_reproduce:
                break
            rand = self.evo_rand_gen.uniform(0,1)
            the_one, production, index = self.find_the_one(cells_production, rand)
            if production < reproduction_cost:
                raise Exception("cost to reproduce %f higher than cell production %f"%(reproduction_cost, production))
            new_offspring.append(self.reproduce_cell(cell=the_one, time=time, 
                                                     spent_production=reproduction_cost))
            if the_one.raw_production >= reproduction_cost:
                cells_production[index] = (the_one, the_one.raw_production )
            else:
                del cells_production[index]
        self.new_offspring += new_offspring
        return new_offspring
    
    def reproduce_production_proportional(self, time, competitors, max_reproduce=None, 
                                          production_spending_fract=None, non=0.):

        if max_reproduce is None:
            max_reproduce = self.max_pop_size - len(self.cells)
        if production_spending_fract is None:
            production_spending_fract = self.params.product_spending_fraction
        
        util.within_range(production_spending_fract, (0., 1.))
        new_offspring = []   
        cells_production = self.get_cell_production_dict(competitors).items() 
        if not cells_production:
            return new_offspring
            raise Exception("No cells available for reproduction")
        for _ in range(max_reproduce):
            rand = self.evo_rand_gen.uniform(0,1.)
            the_one, production, index = self.find_the_one(cells_production, rand_nr=rand, non=non)
            if the_one is None:
                continue
            reproduction_cost = production_spending_fract * production
            new_offspring.append(self.reproduce_cell(cell=the_one, time=time, 
                                                     spent_production=reproduction_cost))
            cells_production[index] = (the_one, the_one.raw_production)
        self.new_offspring += new_offspring
        return new_offspring
    
    def reproduce_size_proportional(self, time, competitors, max_reproduce=None, 
                                   non=0.):

        if max_reproduce is None:
            max_reproduce = self.max_pop_size - len(self.cells)
        new_offspring = []   
        for _ in range(max_reproduce):
            if not competitors:
                break
            cells_volumes = [ (cell, cell.volume) for cell in competitors ]
            rand = self.evo_rand_gen.uniform(0,1.)
            the_one, _prod, _index = self.find_the_one(cells_volumes, rand_nr=rand, non=non)
            if the_one is None:
                continue
            new_offspring.append(self.reproduce_cell(cell=the_one, time=time))
            if the_one.volume < self.params.cell_division_volume:
                competitors.remove(the_one)
        self.new_offspring += new_offspring
        return new_offspring

    def calculate_reference_production(self, pressure=None, historic_production_weight=None):
        '''
        Calculates a reference production value used to scale the reproductive
        potential of cells during competition to reproduce.
         
        :param pressure: type of selection pressure scaling; can be based on
        current or historical production values.
        '''
        if historic_production_weight is None:
            historic_production_weight = self.params.historic_production_weight
        if pressure is None:
            pressure = self.params.selection_pressure
        if pressure == 'current_scaled':
            self.historic_production_max = np.median(self.production_values()) 
        elif pressure == 'historic_scaled':
            self.historic_production_max = max(self.historic_production_max, 
                                           (self.historic_production_max*(historic_production_weight) + 
                                            np.median(self.production_values())) / (historic_production_weight+1))
        elif pressure == 'historic_window_scaled':
            missing =  self.params.historic_production_window - len(self.production_val_history) 
            historic_average = np.mean(self.production_val_history + [self.historic_production_max] * missing )
            self.historic_production_max = max(self.historic_production_max, historic_average) 
        elif pressure in ['historic_fixed', 'constant']:
            pass
        else:
            raise Exception, 'selection pressure {0} not recognized'.format(pressure)
        if (self.params.max_historic_max is not None and 
            self.historic_production_max > self.params.max_historic_max):
            self.historic_production_max = self.params.max_historic_max
    
    def update_prod_val_hist(self, hist_prod_func=np.median, historic_production_window=None,
                             pop_size_scaling=None):
        '''
        Keep a sliding window view on historic production values. 
        
        
        :param hist_prod_func: calculates the population production value
        :param historic_production_window: length of the sliding window
        '''
        if historic_production_window is None:
            historic_production_window = self.params.historic_production_window
        if pop_size_scaling is None:
            pop_size_scaling = self.params.scale_prod_hist_to_pop
        current_prod_val = hist_prod_func(self.production_values())
        if pop_size_scaling:
            current_prod_val *= self.current_pop_size / float(self.max_pop_size)
        self.production_val_history = self.production_val_history[-historic_production_window:]
        self.production_val_history.append(current_prod_val)


    
    def remove_unproduced_gene_products(self, grid, cutoff=None): 
        if cutoff is None:
            cutoff = self.params.gene_product_conc_cutoff
        for gp in grid:
            cells_updated = False
            for cell in gp.content.get_cells():
                cells_updated |= cell.remove_unproduced_gene_products(cutoff)
            if cells_updated:
                gp.updated = True
            
    def reproduce_on_grid(self, grid, max_pop_per_gp, time, neighborhood='competition', 
                          non=None, selection_pressure=None):
        if non is None:
            non = self.params.non
        if selection_pressure is None:
            selection_pressure = self.params.selection_pressure
        self.calculate_reference_production(selection_pressure)
        if selection_pressure != 'constant' and not self.params.reproduce_size_proportional:
            non = non * self.historic_production_max 
        # update the production_val_history
        self.update_prod_val_hist()
        new_offspring_gp_dict = collections.OrderedDict()
        gps = list(grid.gp_iter)
        self.pop_rand_gen.shuffle(gps)
        for gp in gps:
            nr_cells_in_gp = len(gp.content.get_cells())
            if nr_cells_in_gp >= max_pop_per_gp:
                continue
            competitors = []
            #get neighborhood localities
            neighborhood_localities = orderedset.OrderedSet(gp.neighbors(neighborhood))
            '''Ensuring that we do not look at the same locality more than once due to grid wrapping.'''
            for locality in neighborhood_localities:
                competitors += locality.get_cells()
            if self.params.cell_division_volume is not None:
                competitors = [ c for c in competitors if c.volume >= self.params.cell_division_volume ]
            new_gp_offspring = []
            # scale non with size of the neighborhood and the maximum density per gp
            gp_non = non * len(neighborhood_localities) * self.params.max_cells_per_locality
            if self.params.reproduce_size_proportional:
                new_gp_offspring = self.reproduce_size_proportional(time=time, competitors=competitors, 
                                                                 max_reproduce=(max_pop_per_gp - nr_cells_in_gp),
                                                                 non=gp_non)  
            elif self.params.reproduction_cost is None or time < self.params.grace_time:
                new_gp_offspring = self.reproduce_production_proportional(time=time,competitors=competitors, 
                                                                          max_reproduce=(max_pop_per_gp - nr_cells_in_gp),
                                                                          non=gp_non)
            else:
                new_gp_offspring = self.reproduce_at_minimum_production(time=time,competitors=competitors, 
                                                                          max_reproduce=max((max_pop_per_gp - nr_cells_in_gp),0)
                                                                          )
            for cell in new_gp_offspring:
                new_offspring_gp_dict[cell] = gp
        return new_offspring_gp_dict

    def mutate_new_offspring(self, time, environment,
                             rand_gen=None, rand_gen_np=None):
        if rand_gen is None:
            rand_gen = self.evo_rand_gen
        if rand_gen_np is None:
            rand_gen_np = self.evo_rand_gen_np
        for cell in self.new_offspring:
            cell.mutate(time=time, environment=environment,
                        rand_gen=rand_gen, rand_gen_np=rand_gen_np)
   
    def horizontal_transfer(self, time, grid, environment, rand_gen=None, rand_gen_np=None):
        """
        Applies HGT to all cells in the grid
        
        Parameters
        ----------
        grid : needed for internal HGT and setting the update-flags
        environment: contains all possible reactions to draw a random gene for external HGT
        rand_gen: RNG
        
        Returns
        -------
        -
        """
        if rand_gen is None:
            rand_gen = self.evo_rand_gen
        hgt_gp_dict = collections.OrderedDict()
        gps = list(grid.gp_iter)    # Iterator for all GPs
        for gp in gps:        
            for cell in gp.content.get_cells():
                
                applied = cell.apply_hgt(time=time, gp=gp, 
                                         environment=environment, rand_gen=rand_gen, verbose=False)
                if applied:
                    hgt_gp_dict[cell] = gp
        return hgt_gp_dict

            
    def update_offspring_regulatory_network(self, min_bind_score=None): # if min_bind_score is None, it will default to the parameter
        for cell in self.new_offspring:
            cell.update_grn(min_bind_score)
            
    def grow_time_course_arrays(self):        
        for cell in self.cells:
            cell.grow_time_course_arrays()
    
    def clear_mol_time_courses(self, ):
        for cell in self.cells:
            if not cell.alive:
                cell.clear_mol_time_courses()
            
    def resize_time_courses(self, new_max_time_points):
        '''resize the arrays that can hold time course information 
        of cellular concentrations etc.
        
        :param new_max_time_points: new length of time course array
        '''
        for cell in self.cells:
            cell.resize_time_courses(new_max_time_points)
            
    def reset_production_toxicity_volume(self, cells=None):
        if cells is None:
            cells = self.cells
        for cell in cells:
            cell.raw_production = 0.
            cell.toxicity = 0.
            cell.volume = self.params.cell_init_volume
            
    def mark_cells_metabolic_type(self, cells=None):
        if cells is None:
            cells = self.cells
        min_mark, max_mark = self.markers_range_dict['metabolic_type']
        for cell in cells:
            try:
                mark = self.metabolic_type_marker_dict.index_key(cell.metabolic_type)
            except (StopIteration, IndexError):
                self.prune_metabolic_types()
                mark = self.metabolic_type_marker_dict.index_key(cell.metabolic_type)
                
            cell.mark('metabolic_type', mark)
            if mark < min_mark:
                min_mark = mark
            if mark > max_mark:
                max_mark = mark
        self.markers_range_dict['metabolic_type'] = (min_mark, max_mark)
        return min_mark, max_mark
    
    def cell_markers(self,marker,cells=None ):
        if cells is None:
            cells = self.cells
        return orderedset.OrderedSet([cell.marker_dict[marker] for cell in cells])
    
    def update_lineage_markers(self, cells=None, min_nr_marks=1):
        if cells is None:
            cells = self.cells
        if len(self.cell_markers('lineage', cells)) <= min_nr_marks:
            self.mark_cells_lineage(cells)
    
    def mark_cells_lineage(self, cells=None):
        min_mark, max_mark = self.markers_range_dict['lineage']
        marker_iter = it.count()
        if cells is None:
            cells = self.cells
        for cell in cells:
            mark = marker_iter.next()
            if mark < min_mark:
                min_mark = mark
            if mark > max_mark:
                max_mark = mark
            cell.mark('lineage', mark)
        self.markers_range_dict['lineage'] = (min_mark, max_mark)
        return (min_mark, max_mark)
    
    def average_death_rate(self, cells=None):
        return np.average(self.death_rates(cells)) 
    
    def average_production(self, cells=None):
        return np.average(self.production_values(cells))
    
    def marker_counts(self, marker, cells=None):
        return self.pop_marker_counts(marker, cells)
    
    def pop_marker_counts(self, marker_name, cells=None):
        if cells is None:
            cells = self.cells
        return collections.Counter([cell.marker_dict[marker_name] for cell in cells])
        
    def most_abundant_marker(self, marker_name, cells=None):
        if cells is None:
            cells = self.cells
        most_abundant = self.pop_marker_counts(marker_name, cells).most_common(1)
        if most_abundant:
            return most_abundant[0][0]
        else:
            return -1
        
    def upgrade(self):
        '''
        Upgrading from older pickled version of class to latest version. Version
        information is saved as class variable and should be updated when class
        invariants (e.g. fields) are added.
        '''
        version = float(self.version)
        if version < 1.:
            pass
        self.version = self.class_version
        if version > float(self.class_version):
            print 'upgraded class',
        else:
            print 'reset class', 
        print self.__class__.__name__, ' from version', version ,'to version', self.version
        
    def __getstate__(self):
        odict = dict()  # NOTE: unordered ok
        for k, v in self.__dict__.iteritems():
            if k in ['current_ancestors', 'roots']:
                odict[k] = v._pickle_repr()
            elif k in ['cells', 'phylo_tree']:
                pass
            else:
                odict[k] = v
        return odict

    def __setstate__(self, obj_dict):
        for k, v in obj_dict.iteritems():
            if k in ['current_ancestors', 'roots']:
                setattr(self, k, util.LinkThroughSet._unpickle_repr(v))
            else:
                setattr(self, k, v)
        self.init_cells_view()
        self.init_phylo_tree(0) 
        self.reconstruct_tree = True
        if not hasattr(self, 'version'):
            self.version = '0.0'
        if self.version != self.class_version:
            self.upgrade()
        
    def __getitem__(self, key):
        return self.params[key]
