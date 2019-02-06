'''
Created on Mar 9, 2014

@author: thocu
'''

from VirtualMicrobes.event.Reaction import Degradation, Transport, Diffusion, Influx,\
    ClassConvert, Convert
from VirtualMicrobes.event.Molecule import Molecule, MoleculeClass
import itertools as it
import numpy as np
import random
import string
import warnings
import collections
import VirtualMicrobes.my_tools.utility as util
from collections import OrderedDict
from VirtualMicrobes.my_tools.utility import OrderedDefaultdict
from orderedset import OrderedSet 
import math

class Locality(object):
    
    class_version = '1.0'

    def __init__(self, params, internal_molecules, influx_reactions, degradation_reactions, env_rand,
                 max_time_course_length=0):

        self.version = self.__class__.class_version

        self.params = params
        self.max_time_course_length = max_time_course_length
        self.volume = self.params.per_grid_cell_volume
        self.internal_molecules = internal_molecules
        self.influx_reactions = influx_reactions
        self.degradation_reactions = degradation_reactions
        self.env_rand = env_rand
        self.molecules = dict() # NOTE: unordered ok
        self.molecules["gene_products"] = util.OrderedDefaultdict(util.GeneProduct)
        self.molecules["small_molecules"] = util.OrderedDefaultdict(util.SmallMol)
        self.init_mol_views()
        self.cells = []
        self.nr_time_points_stored = 0
        self.init_external_mols()
        self.init_variables_map()
        #self.init_time_courses()
        self.new_concentrations = False
            
    def init_variables_map(self):
        self.dimension = 0
        self.variables_map = dict() # NOTE: unordered ok
        self.variables_map["small_molecules"] = dict() # NOTE: unordered ok : keys are unique objects
        self.variables_map["gene_products"] = dict() # NOTE: unordered ok
        self.variables_map["cell_growth"] = dict() # NOTE: unordered ok 
        self.variables_map["cell_toxicity"] =dict() # NOTE: unordered ok
        self.variables_map["cell_volume"] =dict() # NOTE: unordered ok
    
    def init_mol_views(self):
        self.small_mols, self.gene_products = (self.molecules['small_molecules'].viewkeys(), 
                                               self.molecules['gene_products'].viewkeys())
    
    def get_mol_influx_dict(self): # NOTE: unordered ok : use for output only 
        return dict([ (mol, self.molecules['small_molecules'][mol].influx) 
                     for mol in self.small_mols] ) 
        
    def get_mol_concentration_dict(self):    # NOTE: unordered ok : use for output only 
        return dict([ (mol, self.get_small_mol_conc(mol)) 
                     for mol in self.small_mols] )
    
    def get_mol_time_course_dict(self, max_tp=None):
        if max_tp is None:
            max_tp = self.nr_time_points_stored 
        return dict([ (mol, np.vstack((self.time_points[:max_tp],
                                       self.molecules['small_molecules'][mol].time_course[:max_tp]))) 
                     for mol in self.small_mols] )
        
    def _get_mol_property_dict(self, prop_name): 
        mol_property_dict = dict() # NOTE: unordered ok : use for output only 
        for mol in self.small_mols:
            mol_property_dict[mol] = self.molecules["small_molecules"][mol][prop_name]
        return mol_property_dict
    
    def get_mol_per_class_influx_dict(self): # NOTE: not used, purge?
        mol_property_dict = util.OrderedDefaultdict(dict) # NOTE: unordered ok 
        for mol in self.small_mols:
            mol_property_dict[str(mol.paired.mol_class)][mol] = self.molecules["small_molecules"][mol].influx
        return mol_property_dict    
        
    def get_mol_per_class_concentration_dict(self): # NOTE: not used, purge?
        mol_property_dict = util.OrderedDefaultdict(dict) # NOTE: unordered ok 
        for mol in self.small_mols:
            mol_property_dict[str(mol.paired.mol_class)][mol] = self.get_small_mol_conc(mol)
        return mol_property_dict    
    
    def get_cells(self):
        return self.cells[:]
    
    def init_external_mols(self):
        for mol_ext in [ mol_int.paired for mol_int in self.internal_molecules]:
            self.add_small_molecule(mol_ext)
    
    def add_small_molecule(self, mol, concentration=0.): 
        self.molecules["small_molecules"][mol].influx = self.influx_reactions[mol], 0.
        self.molecules["small_molecules"][mol].degradation = self.degradation_reactions[mol.paired], 0. 
        self.init_mol_time_course(self.molecules["small_molecules"][mol])
        self.set_small_mol_conc(mol, concentration)
        
    def update_small_mol_concentrations(self, concentration_dict):
        for mol_ext, conc in concentration_dict.items():
            self.set_small_mol_conc(mol_ext, conc)    
        self.new_concentrations = True
    
    def update_small_mol_degradation_rates(self, degradation_dict):
        for mol_ext, degr in degradation_dict.items():
            (degr_reac, _) = self.molecules["small_molecules"][mol_ext].influx
            self.molecules["small_molecules"][mol_ext].degradation = (degr_reac,degr)
                
    def update_small_mol_influxes(self, influx_dict, no_influx=1e-20):
        for mol_ext, influx in influx_dict.items():
            if influx is None:
                influx = no_influx
            (influx_reac,_) = self.molecules["small_molecules"][mol_ext].influx
            self.molecules["small_molecules"][mol_ext].influx = (influx_reac, influx)
            
    def map_variables(self): 
        '''
        Setup of the mapping of variables in the system to indexes used by the C
        encoded integrator part of the simulation:
        
        * small molecules (metabolites, toxins, resources) 
        * gene products 
        
        In practice we start with an empty dictionary and let 'system' map
        molecules and gene products separately, creating the indexes on the go
        and reporting back on the last used index. 
        '''
        self.init_variables_map()
        self.map_external_molecules()
        for cell in self.cells:
            self.map_cell_internal_mols(cell)
            self.map_cell_gene_products(cell)
    
    def map_external_molecules(self):
        '''
        Mapping of the small molecules to indexes for use in the C integrator.
        The map is an initially empty dictionary. The first level of indexing is
        the container , while the second level is the molecules (type)
        . The container can be a cell or it can be the environment. (see
        also map_variables)
        
        :param start_index:
        '''
        for mol in self.internal_molecules:
            external_mol = mol.paired
            if self not in self.variables_map['small_molecules']:
                self.variables_map["small_molecules"][self] = dict() # NOTE: unordered ok: only accessed by unique key
            self.variables_map["small_molecules"][self][external_mol] = self.dimension  
            self.dimension += 1
        
    def map_cell_internal_mols(self, cell):
        for mol in self.internal_molecules:
            if cell not in self.variables_map["small_molecules"]:
                self.variables_map["small_molecules"][cell] = dict() # NOTE: unordered ok: only accessed by unique key
            self.variables_map["small_molecules"][cell][mol] = self.dimension                   
            self.dimension   += 1
    
    def map_cell_gene_products(self, cell):
        '''
        The mapping is a dictionary of dictionaries; in this way, it is
        possible to recognize the same protein in the two different cells as two
        separate variables. (see also map_external_molecules)
        
        :param start_index:
        '''
        if cell not in self.variables_map["gene_products"]:
            self.variables_map["gene_products"][cell] = dict() # NOTE: unordered ok: only accessed by unique key
        for prod in cell.gene_products:
            self.variables_map["gene_products"][cell][prod] = self.dimension  
            self.dimension   += 1
        self.variables_map["cell_growth"][cell] = self.dimension  
        self.dimension   += 1
        self.variables_map["cell_toxicity"][cell] = self.dimension  
        self.dimension   += 1
        self.variables_map["cell_volume"][cell] = self.dimension  
        self.dimension   += 1
    
    def init_mol_time_course(self, mol_struct, length=None):
        mol_struct.time_course = util.time_course_array(length)
    
    def init_time_courses(self, length=None):
        '''initialize an array to hold time course data of molecules
        
        :param new_max_time_points: max number of time points
        '''        
        if length is None:
            length = self.max_time_course_length
        self.time_points = util.time_course_array(length)
        for mol_struct in self.molecules["small_molecules"].values():
            self.init_mol_time_course(mol_struct, length)
        for mol_struct in self.molecules["gene_products"].values():
            self.init_mol_time_course(mol_struct, length)
    
    def resize_time_courses(self, new_max_time_points):
        if new_max_time_points > self.max_time_course_length:
            self.max_time_course_length = new_max_time_points
            self.init_time_courses()
    
    def clear_mol_time_courses(self):
        for mol_struct in self.molecules["small_molecules"].values():
            mol_struct.time_course = None
        for mol_struct in self.molecules["gene_products"].values():
            mol_struct.time_course = None
    
    def get_small_mol_conc(self, mol):
        if self.tp_index is not None:
            return self.molecules['small_molecules'][mol].time_course[self.tp_index]
        else:
            return self.molecules['small_molecules'][mol].concentration
    
    def set_small_mol_conc(self, mol, val):
        if self.tp_index is not None:
            self.molecules['small_molecules'][mol].time_course[self.tp_index] = val
        self.molecules['small_molecules'][mol].concentration = val
    
    def get_gene_prod_conc(self, gene):
        if self.tp_index is not None:
            return self.molecules['gene_products'][gene].time_course[self.tp_index]
        else:
            return self.molecules['gene_products'][gene].concentration
        
    def set_gene_prod_conc(self, gene, conc):
        if self.tp_index is not None:
            self.molecules['gene_products'][gene].time_course[self.tp_index] = conc
        self.molecules['gene_products'][gene].concentration = conc
    
    @property
    def tp_index(self):
        index = self.nr_time_points_stored - 1
        return index if index > -1 else None
              
    def set_mol_concentrations_from_time_point(self):
        for mol in self.small_mols:
            self.set_small_mol_conc(mol, self.get_small_mol_conc(mol))
        for gene_prod in self.gene_products:
            self.set_gene_prod_conc(gene_prod, self.get_gene_prod_conc(gene_prod))
            
    def spill_dead_cell_contents(self, cell, factor=None):
        if factor is None:
            factor = self.params.spill_conc_factor
        util.within_range(factor, (0., 1.))
        for m in cell.small_mols:
            cell_conc = cell.get_small_mol_conc(m)
            ext_conc = self.get_small_mol_conc(m.paired)
            self.set_small_mol_conc(m.paired, ext_conc + (factor * cell_conc * cell.volume)/ self.volume)
        self.new_concentrations = True
            
    def clear_locality(self):
        '''
        Clear the cells in this locality.
        '''
        for cell in self.cells:
            self.remove_cell(cell)
                
    def remove_cell(self, cell):
        self.cells.remove(cell) 
    
    def add_cell(self, cell):
        self.cells.append(cell)
        
    def _clear_dead_cells(self):
        removed = []
        for c in self.get_cells():
            if not c.alive:
                if self.params.spill_conc_factor and not c.wiped:
                    self.spill_dead_cell_contents(c)
                self.remove_cell(c)
                removed.append(c)
        return removed
    
    def __setitem__(self,key,value):
        self.params[key] = value
    
    def __getitem__(self,key):
        return self.params[key] 
    
    def upgrade(self):
        '''
        Upgrading from older pickled version of class to latest version. Version
        information is saved as class variable and should be updated when class
        invariants (e.g. fields) are added.
        '''
        version = float(self.version)
        if version < 1.:
            self.new_concentrations = False
        self.version = self.class_version
        if version > float(self.class_version):
            print 'upgraded class',
        else:
            print 'reset class', 
        print self.__class__.__name__, ' from version', version ,'to version', self.version

    
    def __getstate__(self):
        odict = self.__dict__.copy() # copy the dict since we change it
        del odict['small_mols']              # remove filehandle entry
        del odict['gene_products']
        return odict

    def __setstate__(self, obj_dict):
        self.__dict__.update(obj_dict)   # update attributes
        self.init_mol_views()  
        if not hasattr(self, 'version'):
            self.version = '0.0'
        if self.version != self.class_version:
            self.upgrade()

import Grid

class Environment(object):
    class_version = '1.1'

    '''
    
    '''

    def __init__(self,params, max_time_course_length=0):
        '''
        :param nr_resource_classes: 
        :param mol_per_res_class:
        :param nr_energy_classes:
        :param mol_per_ene_class:
        :param nr_building_blocks: how many molecules are building blocks
        :param consume_range: range for stoichiometric constants for a resource of a conversion reaction
        :param max_yield: maximum stoichiometric yield of new product in a conversion reaction
        :param transport_cost_range: range of stoichiometric energy cost of an import reaction
        :param per_grid_cell_volume: 
        :param fraction_realized_reactions: fraction of actualized reactions in the simulation of all possible reactions given the set of molecule classes and possible reaction schemes
        :param fraction_mol_transports: fraction of resources that have a import reaction assigned for importing it
        :param reaction_schemes: nr-of-resources to nr-of-product pairs that define the potential reaction space
        :param number_localities: 
        :param toxicity:
        '''
        
        self.version = self.__class__.class_version
        ### take a reference of the global paramaters ###
        self.params = params
        self.max_time_course_length = max_time_course_length
        self.init_rand_gens(self.params.env_rand_seed)
        
        self.resource_classes = collections.OrderedDict()
        self.energy_classes = collections.OrderedDict()
        
        self.init_mol_class_sizes()
        self.init_mol_classes()
        self.init_reactions()
        
        self.init_mol_toxicities(toxicity_avrg=self.params.toxicity, 
                                toxicity_variance_shape=self.params.toxicity_variance_shape)
        
        self.init_influxed_mols(self.params.fraction_influx)
        
        self.init_global_influx_dict()
        self.init_degradation_dict(self.params.small_mol_ext_degr_const, 
                                   self.params.ene_ext_degr_const,
                                   self.params.bb_ext_degr_const,
                                   degradation_variance_shape=self.params.degradation_variance_shape)
        self.init_membrane_diffusion_dict()
        
        self.init_grid()
        self.init_sub_envs()
        self.init_external_mol_vals_on_grid(self.params.init_external_conc)
        
    def init_rand_gens(self, env_rand_seed=None):
        if env_rand_seed is None:
            env_rand_seed = self.params.env_rand_seed
        self.env_rand = random.Random(int(env_rand_seed))
        
    
    def init_mol_class_sizes(self):
        
        nr_resource_classes = self.params.nr_resource_classes
        mol_per_res_class = self.params.mol_per_res_class
        nr_energy_classes = self.params.nr_energy_classes 
        mol_per_ene_class = self.params.mol_per_ene_class
        
        if isinstance(mol_per_res_class, int):
            self.resource_mol_class_sizes = [ mol_per_res_class for _ in range(nr_resource_classes)] 
        else: #assume a range
            self.resource_mol_class_sizes = [ self.env_rand.randint(*mol_per_res_class) for _ in range(nr_resource_classes)]
        if isinstance(mol_per_ene_class, int):
            self.energy_mol_class_sizes = [ mol_per_ene_class for _ in range(nr_energy_classes) ] 
        else:
            self.energy_mol_class_sizes = [ self.env_rand.randint(*mol_per_ene_class) for _ in range(nr_energy_classes) ] 
        
            
    def init_mol_toxicities(self, toxicity_avrg, toxicity_variance_shape=None):
        for mol in self.internal_molecules:
            if toxicity_variance_shape is not None:
                theta = toxicity_avrg / toxicity_variance_shape
                toxicity = self.env_rand.gammavariate(toxicity_variance_shape, theta)
            else:
                toxicity = toxicity_avrg
            mol.toxic_level = toxicity
    
    def print_values(self):
        print 'conversion reactions:'
        for c in self.conversions:
            print c
        print
        print 'transport reactions:'
        for t in self.transports:
            print t    
        print
        print 'toxcities:'
        for mol in self.internal_molecules:
            print mol, '\t', mol.toxic_level
        print
        print 'degradation rates:'
        for mol, degr in self.degradation_dict.items():
            print mol, '\t', degr
        print
        print 'membrane diffusion rates:'
        for mol, diff in self.membrane_diffusion_dict.items():
            print mol, '\t', diff
        print
        print 'influx rates:'
        for i, sub_env in enumerate(self.subenvs):
            print '\tsubenv {}'.format(i)
            for mol,inf_rate in sub_env.influx_dict.items():
                print '\t', mol, '\t', inf_rate
        print
        print 'not influxed:'
        for mol in [ mol for mol in self.external_molecules if mol not in self.influxed_mols ]:
            print mol
    
    @property
    def molecule_classes(self):
        return self.resource_classes.values() + self.energy_classes.values()
    
    @property
    def energy_mols(self):
        return [ m for ec in self.energy_classes.values() for m in ec.molecules ] 
    
    def select_building_blocks(self, nr_bb, mol_classes, substrate_weight_function = lambda m: m.energy_level, weight_scaling=2, rand_gen=None):
        if rand_gen is None:
            rand_gen = self.env_rand
        bb_class_sample = util.OrderedSet()
        mol_classes = util.OrderedSet(mol_classes)
        while len(bb_class_sample) < nr_bb and len(mol_classes):
            weighted_classes =  [ ( m, pow(substrate_weight_function(m), weight_scaling) ) for m in mol_classes ]
            mol_class, _energy , _ = self.pick_mol_class(weighted_classes, rand_gen)
            bb_class_sample.add(mol_class)
            mol_classes.remove(mol_class)
        
        return bb_class_sample
    
    def init_mol_classes(self):
        
        nr_building_blocks = self.params.nr_building_blocks
        res_energy_range = self.params.res_energy_range
        ene_energy_range = self.params.ene_energy_range
        
        mol_class_names = (n+str(i) if i>0 else n for i in xrange(100) for n in string.uppercase)
        self.internal_molecules = []
        for s in self.resource_mol_class_sizes:
            mol_class_name = mol_class_names.next()
            mol_names = [ mol_class_name.lower()+"."+str(i) for i in range(s) ] 
            molecules = [ Molecule(name=n, environment=self) for n in mol_names ] #creates external mol variatns implicitly
            self.internal_molecules += molecules
            mol_class = MoleculeClass(name=mol_class_name,
                                      energy_level=self.env_rand.randint(*res_energy_range),
                                      molecule_species=molecules)
            self.resource_classes[mol_class.name] = mol_class
        
        if self.params.high_energy_bbs:
            bb_class_sample = self.select_building_blocks(nr_building_blocks, self.resource_classes.values())
        else:
            bb_class_sample = self.env_rand.sample(self.resource_classes.values(), min(len(self.resource_classes), nr_building_blocks))
        building_blocks = []
        while len(building_blocks) < nr_building_blocks:
            for rc in bb_class_sample:
                if not util.OrderedSet(rc.molecules) - util.OrderedSet(building_blocks):
                    continue
                while True: #TODO: make this crappy function better
                    bb_temp = self.env_rand.choice(rc.molecules.values())
                    if bb_temp not in building_blocks:
                        building_blocks.append(bb_temp)
                        break
        
        for block in building_blocks:
            block.set_building_block()
        
        for s in self.energy_mol_class_sizes:   
            mol_class_name = mol_class_names.next()
            mol_names = [ mol_class_name.lower()+"."+str(i) for i in range(s) ] 
            molecules = [ Molecule(name=n, environment=self) for n in mol_names ]
            self.internal_molecules += molecules 
            mol_class = MoleculeClass(name=mol_class_name,
                                      energy_level=self.env_rand.randint(*ene_energy_range),
                                      molecule_species=molecules, is_energy=True)
            self.energy_classes[mol_class.name] = mol_class
        
    def init_reactions(self):
        self.init_diffusion()
        self.init_degradation()        
        self.init_reaction_universe()
        self.conversions += self.init_class_conversions(1.)#fraction_realized_reactions)
        self.init_transports()
        self.init_influx()
        self.init_mols_to_reactions()
    
    def pick_mol_class(self, weighted_classes, rand_gen=None):
        '''
        Randomly select a molecule class with probability proportional to a weight.
        
        Parameters
        ----------
        weighted_classes : list of class:`event.Molecule.MoleculeClass`, weight (float) tuples
            molecule classes with their respective weights
        rand_gen : RNG
            RNG
            
        Returns
        -------
        class:`event.Molecule.MoleculeClass`, energy, pos index
            the selected class with its energy level and list index
        '''
        if rand_gen is None:
            rand_gen = self.env_rand
        total_ene = sum( [ w for m,w in weighted_classes] )
        rand = rand_gen.uniform(0, 1.) * total_ene
        cumulative_chance = 0.
        catabolite, energy, index = None, 0., None
        for i,(m, w) in enumerate(weighted_classes):
            cumulative_chance += w
            if rand <= cumulative_chance:
                catabolite, energy, index = m, m.energy_level, i
                break
        return catabolite, energy, index



    def resource_combis_within_energy(self, resource_classes, nr, total_energy):
        '''
        Return combinations of resource classes that have exactly a total sum in energy values. 
        
        Parameters
        ----------
        resource_classes : set of class:`event:Molecules.MoleculeClass`s
            the set to make combinations from
        nr : int
            number of MCs to combine
        total_energy : int
            the sum of energy values that MCs should have
            
        Returns
        -------
        combinations of MCs
        '''
        if nr > 1:
            combis = it.product(*[resource_classes]*nr)
        else:
            combis = [(r,) for r in resource_classes ]
        if isinstance(total_energy, tuple):
            low,high = total_energy
            filtered_low = [ c for c in combis if sum( map(lambda m: m.energy_level, c) ) >= low ]
            filtered = [ c for c in filtered_low if sum( map(lambda m: m.energy_level, c) ) <= high ]
        else:
            filtered = [ c for c in combis if sum( map(lambda m: m.energy_level, c) ) == total_energy ]
        return filtered

    def rand_catabolic_reaction_scheme(self, substrate_classes, product_classes, energy_classes, 
                                       max_products, min_energy,rand_gen=None): # lambda m: 1.): # alternatively 
        '''
        Construct a random catabolic reaction scheme.
        
        Typically a catabolic reaction breaks down a large, energy rich molecule
        into smaller molecules. Energy molecules may be produced in this
        reaction.
        
        Construction is done by randomly selecting a molecule class as the
        substrate of the reaction and than select the molecule classes that will
        be the product of the reaction. The total energy of reactants = products
        (+ energy).
        
        Parameters
        ----------
        substrate_classes : list of class:`event:Molecules.MoleculeClass`
            all resource molecule classes
        product_classes : list of class:`event:Molecules.MoleculeClass`
            molecule classes that can be products of the reaction
        energy_classes : list of class:`event:Molecules.MoleculeClass`
            energy molecule classes
        max_products : int
            maximum number of products in reaction scheme
        min_energy : int
            minimum yield in energy metabolites
                        
        Returns
        -------
        reaction scheme tuple ( list of reactants, list of products, stoichiometries
        '''
        if rand_gen is None:
            rand_gen = self.env_rand
        # weigh potential substrate classes by their energy level
        potential_substrates =  substrate_classes[:]
        while potential_substrates:
            # start by randomly picking a resource class as the substrate of the reaction
            substrate = rand_gen.choice(potential_substrates)
            # remove this substrate from the list, so we don't pick it again.
            energy = substrate.energy_level
            potential_substrates.remove(substrate) 
            products = []
            try:
                product_classes.remove(substrate) # make sure we cannot produce the substrate
            except:
                pass
            # set initial energy_yield equal to energy of substrate
            energy_yield = energy 
            # subtract the energy that should be converted to energy molecules
            nr_products = rand_gen.randint(1,max_products)
                
            if isinstance(min_energy, tuple):
                min_,max_ = min_energy
                if nr_products == 1: # there is a single product, the reaction should yield a minimum of 1 energy
                    min_= max(1, min_)
                    max_ = max(1,max_)
                energy_yield = energy_yield - max_, energy_yield - min_ 
            else:
                min_ = min_energy
                if nr_products == 1:
                    min_ = max(1,min_)
                energy_yield -= min_
            potential_combinations = self.resource_combis_within_energy(product_classes, nr_products, energy_yield)
            
            if not potential_combinations:
                continue # try again, if the substrate list is not empty
            products = list(rand_gen.choice(potential_combinations))
            for p in products:
                energy -= p.energy_level
            break
        if not products:
            return None
        while True:
            potential_energy_classes = [ m for m in energy_classes if m.energy_level <= energy]
            if not potential_energy_classes:
                break 
            energy_class = rand_gen.choice(potential_energy_classes)
            products.append(energy_class)
            energy -= energy_class.energy_level
        products, stois = zip(*sorted(collections.Counter(products).items()))
        reaction_scheme = ((substrate,), tuple(products), tuple([1] + list(stois)))
        return reaction_scheme
    
    def rand_anabolic_reaction_scheme(self, resource_classes, energy_classes, 
                                      product_classes, nr_reactants, max_products,
                                      max_free_energy, max_ene_energy=1, rand=None):
        '''
        Construct a random anabolic reaction scheme.
        
        Construction is done by randomly selecting a molecule classes as the
        substrates of the reaction and than select the molecule classes that
        will be the product of the reaction. The total energy of 
        reactants ( + energy) >= products.
        
        Parameters
        ----------
        resource_classes : list of class:`event:Molecules.MoleculeClass`
            all resource molecule classes
        energy_classes : list of class:`event:Molecules.MoleculeClass`
            energy molecule classes
        max_products : int
            maximum number of products in reaction scheme
        max_ene_energy : int
            maximum energy level that can be provided by energy metabolites as reaction substrate
            
        Returns
        -------
        reaction scheme tuple ( list of reactants, list of products, stoichiometries
        '''
        
        if rand is None:
            rand = self.env_rand
        
        
        if isinstance(nr_reactants, tuple):
            nr_reac = rand.randint(*nr_reactants)
        else:
            nr_reac = nr_reactants
        if nr_reac > 1:
            combis = list(it.product(*[resource_classes]*nr_reac))
        else:
            combis = [(r,) for r in resource_classes ]
        while len(combis):
            potential_products = product_classes[:]
            combi = rand.choice(combis)
            combis.remove(combi)
            reactants = list(combi)
            free_energy = 0
            for r in reactants:
                free_energy += r.energy_level
            
            for reactant in set(reactants):
                try:
                    potential_products.remove(reactant) # ensure that we will not produce one of the reactants  
                except:
                    pass
            nrs = range(1,max_products+1)
            rand.shuffle(nrs)
            for nr_products in nrs:
                min_energy = free_energy - max_free_energy
                max_energy = free_energy + max_ene_energy
                product_combis = self.resource_combis_within_energy(potential_products, nr_products, (min_energy,max_energy))
                if product_combis:
                    break
        if not product_combis:
            return None
        products = list(rand.choice(product_combis))
        for p in products:
            free_energy -= p.energy_level
        
        while True: # add energy to lhs if needed
            if free_energy >= 0:
                break
            rand_ene = rand.choice(energy_classes)
            reactants.append(rand_ene)
            free_energy += rand_ene.energy_level
            
        reactants, reac_stois = zip(*sorted(collections.Counter(reactants).items())) 
        products, prod_stois = zip(*sorted(collections.Counter(products).items())) 
        reaction_scheme = (tuple(reactants), tuple(products), tuple(list(reac_stois) + list(prod_stois)))
        return reaction_scheme
    
    def init_catabolic_reactions(self, nr_catabolic=None, max_products=None, 
                                 min_energy=None, max_path_conversion=None):
        '''
        Initialize the set of catabolic reactions.
        
        Catabolic reactions break down large molecules into smaller molecules.
        If the total free energy of products is lower than that of the
        substrate, energy molecules will also be produced in the reaction until
        reaction is (as) balanced (as possible).
        
        Parameters
        ----------
        nr_catabolic : int
            number of reactions to generate
        max_products : int
            maximum number of species produced in the reaction, excluding energy
        min_energy : int
            minimum amount of energy produced as energy molecules
        max_path_conversion : int
            maximum nr of reactions producing any molecule species
            
        Returns
        -------
        list of class:`event.Reaction.Convert` reactions
        '''
        if nr_catabolic is None:
            nr_catabolic = self.params.nr_cat_reactions
        if max_products is None:
            max_products = self.params.max_nr_cat_products
        if min_energy is None:
            min_energy = self.params.min_cat_energy
        if max_path_conversion is None:
            max_path_conversion = self.params.max_cat_path_conv
        resource_classes, energy_classes = self.resource_classes.values(), self.energy_classes.values() 
        catabolic_reaction_schemes = OrderedSet()
        tries = 0
        max_tries = 1000
        prod_counts = collections.Counter()
        while len(catabolic_reaction_schemes) < nr_catabolic and tries < max_tries:
            if max_path_conversion is not None:
                product_classes = sorted([ p for p in resource_classes if prod_counts[p] < max_path_conversion ])
            else:
                product_classes = resource_classes[:]
            if not len(product_classes):
                break
            reac_scheme = self.rand_catabolic_reaction_scheme(substrate_classes=resource_classes, 
                                                              product_classes=product_classes,
                                                              energy_classes=energy_classes, 
                                                              max_products=max_products,
                                                              min_energy=min_energy)
            if reac_scheme: # check that have a non-empty scheme
                _r, products,_s = reac_scheme
                allowed = True
                if max_path_conversion is not None:
                    # check if the products of this reaction don't violate the maximum pathway conversion constraint.
                    for p in products:
                        count = prod_counts[p]
                        if not p.is_energy and count >= max_path_conversion:
                            allowed = False
                            break
                if allowed:
                    for p in products:
                        prod_counts[p] += 1
                        catabolic_reaction_schemes.add(reac_scheme)
            tries += 1
        if tries == max_tries:
            warnings.warn('Maximum number of tries to create {} catabolic reactions. Created a total of {}.'.format(nr_catabolic, 
                                                                                                                    len(catabolic_reaction_schemes)))
        return [ Convert(*reac_scheme) for reac_scheme in catabolic_reaction_schemes ]
    
    def init_anabolic_reactions(self, nr_anabolic=None, nr_reactants=None, 
                                max_products=None, max_path_conversion=None,
                                max_free_energy=None):
        '''
        Initialize the set of anabolic reactions.
        
        Anabolic reactions combine small molecules into larger molecules. If the
        total free energy of product(s) is larger than that of the substrates,
        energy molecules will also be consumed in the reaction until reaction is
        (as) balanced (as possible).
        
        Parameters
        ----------
        nr_catabolic : int
            number of reactions to generate
        max_products : int
            maximum number of species produced in the reaction
        min_energy : int
            minimum amount of energy produced as energy molecules
        max_path_conversion : int
            maximum nr of reactions producing any molecule species
        max_free_energy : int
            maximum free energy loss from reaction
            
        Returns
        -------
        list of class:`event.Reaction.Convert` reactions
        '''
        if nr_anabolic is None:
            nr_anabolic = self.params.nr_ana_reactions
        if nr_reactants is None:
            nr_reactants = self.params.nr_ana_reactants
        if max_products is None:
            max_products = self.params.max_nr_ana_products
        if max_path_conversion is None:
            max_path_conversion = self.params.max_ana_path_conv
        if max_free_energy is None:
            max_free_energy = self.params.max_ana_free_energy
        resource_classes, energy_classes = self.resource_classes.values(), self.energy_classes.values() 
        anabolic_reaction_schemes = OrderedSet()
        tries = 0
        max_tries = 1000
        prod_counts = collections.Counter()
        while len(anabolic_reaction_schemes) < nr_anabolic and tries < max_tries:
            if max_path_conversion is not None:
                product_classes = sorted([ p for p in resource_classes if prod_counts[p] < max_path_conversion])
            else:
                product_classes = resource_classes[:]
            if not len(product_classes):
                break
            reac_scheme = self.rand_anabolic_reaction_scheme(resource_classes=resource_classes,
                                                             product_classes=product_classes, 
                                                             energy_classes=energy_classes, 
                                                             nr_reactants=nr_reactants, 
                                                             max_products=max_products,
                                                             max_free_energy=max_free_energy)
            if reac_scheme:
                _r, products,_s = reac_scheme
                allowed = True
                if max_path_conversion is not None:
                    # check if the products of this reaction don't violate the maximum pathway conversion constraint.
                    for p in products:
                        count = prod_counts[p]
                        if not p.is_energy and count >= max_path_conversion:
                            allowed = False
                            break
                if allowed:
                    for p in products:
                        prod_counts[p] += 1
                    anabolic_reaction_schemes.add(reac_scheme)
            tries += 1
        if tries == max_tries:
            warnings.warn('Maximum number of tries to create {} anabolic reactions. Created a total of {}.'.format(nr_anabolic, 
                                                                                                                    len(anabolic_reaction_schemes)))
        return [ Convert(*reac_scheme) for reac_scheme in anabolic_reaction_schemes ]
    
    def init_reaction_universe(self):
        cat_reactions = self.init_catabolic_reactions()
        ana_reactions = self.init_anabolic_reactions()
        self.conversions = cat_reactions + ana_reactions
        return self.conversions
                    
    def init_class_conversions(self, fraction_reactions):
        util.within_range(fraction_reactions, (0., 1.))
        class_conversions = []
        metabolite_ene_class_combis = list(it.product(self.resource_classes.values(), self.energy_classes.values()))
        class_convert_combis = []
        for meta_class, ene_class in metabolite_ene_class_combis:
            meta_combis = it.permutations(meta_class.molecules.values(), 2)
            for sub,prod in meta_combis:
                class_convert_combis.append((sub, ene_class, prod))
        nr_reactions = int(len(class_convert_combis) * fraction_reactions)
        for sub, ene_class, prod in self.env_rand.sample(class_convert_combis, nr_reactions):
            cc = ClassConvert(sub, ene_class, prod)
            class_conversions.append(cc)
        return class_conversions
            
    def init_diffusion(self):
        self.diffusion_reactions = collections.OrderedDict()
        for mc in self.molecule_classes:
            for m in mc.molecules.values():
                self.diffusion_reactions[m] = Diffusion(m)
    
    def init_degradation(self):
        self.degradation_reactions = collections.OrderedDict()
        for mc in self.molecule_classes:
            for m in mc.molecules.values():
                self.degradation_reactions[m] = Degradation(m)
                
    def init_influx(self):
        self.influx_reactions = collections.OrderedDict()
        for mc in self.molecule_classes: 
            for m in mc.molecules.values():
                self.influx_reactions[m.paired] = Influx(m.paired)

    def init_transports(self):
        util.within_range(self.params.fraction_mol_transports, (0., 1.))
        self.transports = []
        all_transports = list(it.product(self.resource_classes.values(), self.energy_classes.values()))
        nr_transports = int(len(all_transports) * self.params.fraction_mol_transports)
        for res,ene in self.env_rand.sample( all_transports, nr_transports):
            cost = self.env_rand.randint(*self.params.transport_cost_range) 
            self.transports.append(Transport(res, ene, cost))    
            
    def init_mols_to_reactions(self):
        '''
        Create dictionaries of reactions, keyed on the molecules procuced and
        consumed in the reactions.
        '''
        class_convert_dict = OrderedDefaultdict(list) 
        conversion_dict = {'produced':OrderedDefaultdict(list), 
                           'consumed': OrderedDefaultdict(list)} 
        for c in self.conversions:
            if isinstance(c, ClassConvert):
                class_convert_dict[c.substrate.mol_class].append(c)
            else:
                for reac_class in c.reactants:
                    conversion_dict['consumed'][reac_class].append(c)
                for prod_class in c.products:
                    conversion_dict['produced'][prod_class].append(c)
        transport_dict = OrderedDefaultdict(list)
        for t in self.transports:
            transport_dict[t.substrate_class].append(t)
        self.mols_to_reactions_dict = {'class_convert': class_convert_dict, 
                                       'conversion': conversion_dict,
                                       'transport': transport_dict}
     
    @property
    def external_molecules(self):
        return [ mol.paired for mol in self.internal_molecules ]
    
    @property
    def reactions_dict(self):       
        return dict([('import',self.transports), ('diffusion', self.diffusion_reactions),
                ('conversion', self.conversions), ('degradation', self.degradation_reactions),
                ('influx', self.influx_reactions)])
    
    @property
    def mols_per_class_dict(self):
        d = util.OrderedDefaultdict(list)
        for mol in self.internal_molecules:
            d[mol.mol_class].append(mol)
        return d
        
    def clear_mol_time_courses(self): #TODO translate to grid function (func_on_grid)
        for l in self.localities:
            l.clear_mol_time_courses()
            
    def resize_time_courses(self, new_max_time_points):
        for l in self.localities:
            l.resize_time_courses(new_max_time_points)
                
    def set_mol_concentrations_from_time_point(self): #TODO translate to grid function (func_on_grid)
        for l in self.localities:
            l.set_mol_concentrations_from_time_point()
    
    def influx_change_range(self, param_space):
        new_influx = 0
        if param_space.base is not None:
            new_influx = param_space.base ** self.env_rand.uniform(param_space.lower, 
                                                                   param_space.upper)
        else:
            new_influx = self.env_rand.uniform(param_space.lower, 
                                               param_space.upper)      
        return new_influx  
            
    def influx_change_gamma(self, influx, variance_fact, upper=None, lower=None):
        if influx <= 0 or variance_fact <= 0:
            return influx
        theta = influx / variance_fact
        new_influx = self.env_rand.gammavariate(variance_fact, theta)
        if upper != None:
            new_influx = min(new_influx, upper)
        if lower != None:
            new_influx = max(lower, new_influx)
        return new_influx
    
    def init_sub_envs(self, row_divs=None, col_divs=None, partial_influx=None, influx_combinations=None):
        '''
        Initialize sub-environments by dividing up the grid along rows and columns.
        
        Within each subenvironment, influx can change independently. When partial_influx
        is chosen between 0 and 1, influxed molecules will only appear in a fraction of 
        the subenvironments on the grid.
        
        Parameters
        ----------
        row_divs : int
            nr of divisions on y-axis
        col_divs : int
            nr of divisions on x-axis
        partial_influx : float
            fraction of molecules that will be influxed in each sub-environment
        '''
        if row_divs is None:
            row_divs = self.params.grid_sub_div.row
        if col_divs is None:
            col_divs = self.params.grid_sub_div.col
        if partial_influx is None:
            partial_influx = self.params.sub_env_part_influx 
        if influx_combinations is None:
            influx_combinations = self.params.sub_env_influx_combinations
        self.subenvs = []
        subgrids = list(self.subgrids_gen(row_divs, col_divs))
        for sg in subgrids:
            influx_dict = OrderedDict( (m,inf) for m,inf in self.influx_dict.items() if inf is not None )
            sub_env = util.SubEnv(sub_grid=sg, influx_dict=influx_dict)
            self.subenvs.append(sub_env)
        if partial_influx is not None:
            self.sub_envs_partial_influx(partial_influx)
        elif influx_combinations is not None:
            if influx_combinations == 'richest_first':
                self.sub_envs_influx_combinations(richest_first=True)
            else:
                self.sub_envs_influx_combinations(richest_first=False)
        
    def sub_envs_partial_influx(self, fract):
        '''
        Assign a subset of all influxed molecules per individual sub-environment.
        
        Parameters
        ----------
        fract : float
            fraction of subenvironments where a molecule is fluxed in 
        '''
        influxed_mols = [ mol for (mol,inf) in self.influx_dict.items() if inf is not None ]
        influxed_mols_per_subenv = collections.defaultdict(list)
        for mol in influxed_mols:
            for i in self.env_rand.sample(range(len(self.subenvs)) , max(1, int(fract * len(self.subenvs))) ):
                influxed_mols_per_subenv[i].append(mol)
        
        for i,subenv in enumerate(self.subenvs[:]):
            influx_dict = OrderedDict([ (mol, self.influx_dict[mol]) for mol in influxed_mols_per_subenv[i]  ])
            self.subenvs[i] = subenv._replace(influx_dict=influx_dict)

    def sub_envs_influx_combinations(self, richest_first=True ):
        '''
        Assign a subset of all influxed molecules per individual sub-environment.
        
        Parameters
        ----------
        fract : float
            fraction of subenvironments where a molecule is fluxed in 
        '''
        influxed_mols = [ mol for (mol,inf) in self.influx_dict.items() if inf is not None ]
        combination_lengths = range(len(influxed_mols) + 1)
        if richest_first:
            combination_lengths.reverse()
        combinations = it.chain.from_iterable( it.combinations( influxed_mols, n) for n in combination_lengths )
        
        for i, (subenv, combi) in enumerate(it.izip(self.subenvs[:], combinations)):
            influx_dict = OrderedDict([ (mol, self.influx_dict[mol]) for mol in combi  ])
            self.subenvs[i] = subenv._replace(influx_dict=influx_dict)
        
    def subgrids_gen(self, row_divs=1, col_divs=1):
        '''
        Generate partitions of the grid.
        
        Partitions are constructed from the product of row-chunks and column-
        chunks, such that the grid is divided (approximately) equally according
        to the number of row- and column divisions.
        
        Parameters
        ----------
        row_divs : int
            number of divisions in the row dimension
        col_divs : int
            number of divisions in the column dimension
            
        Yields
        ------
        iterable of '(row_nrs, col_nrs)' partitions of the grid  
        '''
        def chunks(l, n):
            '''Yield successive n-sized chunks from l.'''
            for i in range(0, len(l), n):
                yield l[i:i+n]
        
        chunk_size = int(round(self.grid.rows/float(row_divs))) # round to nearest integer
        row_splits = chunks(range(self.grid.rows), chunk_size)
        chunk_size = int(round(self.grid.cols/float(col_divs))) 
        col_splits = chunks(range(self.grid.cols), chunk_size)
        return it.product(row_splits, col_splits)
    
    def fluctuate(self, time, p_fluct = None, influx_rows=None, influx_cols=None, mols=None, influx_dict=None):
        '''
        Influx fluctuation on the grid.
        
        Sets new influx rates for influxed molecules depending on fluctuation
        frequency. Influx rates may vary between different sub-environments.
        Each sub-environment may define its own set of molecules that can be
        fluxed in.
        
        Parameters
        ----------
        time : int
            simulation time
        p_fluct : float
            fluctuation frequency per influxed molecule
        influx_rows : iterable
            a sequence of row indices on which molecules are exclusively influxed
        influx_cols : iterable
            a sequence of columnt indices on which molecules are exclusively influxed
        mols : list of class:`event.Molecule.Molecule`s
            molecules for which new influx rates should be set
        influx_dict : dict
            mapping from class:`event.Molecule.Molecule` to influx rate (float)
        '''
        if self.params.fluctuate_frequencies is not None: # (simulation) time depencent fluctuation frequency 
            p_fluct = 0.
            for t, p in self.params.fluctuate_frequencies:
                if t < time: # set the fluctation frequency that 
                    p_fluct = p
                else:
                    break
        if influx_rows is None:
            influx_rows = self.params.influx_rows
        if influx_cols is None:
            influx_cols = self.params.influx_cols
        if mols is None:
            mols = self.influxed_mols
        
        for sub_env in self.subenvs:
            rows, cols = sub_env.sub_grid
            if influx_rows is not None:
                rows = [ row for row in rows if row in influx_rows ]
            if influx_cols is not None:
                cols = [ col for col in cols if col in influx_cols ]
            _influx_dict = sub_env.influx_dict if influx_dict is None else influx_dict
            self._fluctuate(time, p_fluct, rows, cols, mols, influx_dict=_influx_dict)
    
    def _fluctuate(self, time, p_fluct, rows, cols, mols, influx_dict):
        '''
        Influx fluctuation in points in the grid. 
        
        See Also
        --------
        func:`fluctuate`
        '''
        for mol_ext in influx_dict:
            if p_fluct is None or self.env_rand.uniform(0, 1.) < p_fluct: 
                if self.params.influx_variance_shape is not None:
                    influx_dict[mol_ext] = self.influx_change_gamma(influx_dict[mol_ext], self.params.influx_variance_shape)
                elif self.params.influx_range is not None:
                    influx = influx_dict[mol_ext]
                    if self.params.fluctuate_extremes:
                        upper = pow(self.params.influx_range.base, self.params.influx_range.upper)
                        lower = pow(self.params.influx_range.base, self.params.influx_range.lower)
                        influx_dict[mol_ext] = upper if influx != upper else lower
                    else:
                        influx_dict[mol_ext] = self.influx_change_range(self.params.influx_range)
        self.func_on_grid(lambda l: l.update_small_mol_influxes(influx_dict), rows, cols)
        
    def func_on_grid(self, gp_func, rows=None, cols=None):
        '''
        Apply a function to a set of grid points. 
        
        The function `gp_func` should take a
        class:`environment.Environment.Locality` as argument. A subset of grid
        points are selected by using rows and cols lists. If both rows and cols
        are given, select gps as a mesh of intersecting rows and cols.
        
        Parameters
        ----------
        gp_func : function
            function on class:`environment.Environment.Locality`
        rows : iterable
            sequence of indices for grid row selection
        cols : iterable 
            sequence of indices for grid column selection
        '''
        gp_iter = None
        if rows is not None and cols is not None:
            gp_iter = self.grid.mesh_iter(rows, cols)
        elif rows is not None:
            gp_iter = self.grid.rows_iter(rows)
        elif cols is not None:
            gp_iter = self.grid.cols_iter(cols)
        else:
            gp_iter = self.grid.gp_iter
        for gp in gp_iter:
            gp_func(gp.content)
            
    def energy_precursors(self):
        '''
        Return set of metabolites that are direct precursors for the energy class
        molecules.
        
        Construct this set by iterating over energy classes and map them to
        reactions that produce the energy classes.
        
        Returns
        -------
        class:OrderedSet
        '''
        energy_precursors = OrderedSet()
        for e in self.energy_classes.values():
            for reac in self.mols_to_reactions_dict['conversion']['produced'][e]:
                for sub_class in reac.reactants:
                    for sub in sub_class.molecules.values():
                        energy_precursors.add(sub)
        return energy_precursors
                
    def init_influxed_mols(self, fraction_influx=None):
        '''
        Select molecules that will be fluxed in in the external environment. 
        '''
        
        fixed = []
        if self.params.influx_energy_precursor:
            fixed = [ mol.paired for mol in self.energy_precursors() ]
        if fraction_influx is None:
            fraction_influx = self.params.fraction_influx
        if isinstance(fraction_influx, float):
            util.within_range(fraction_influx, (0., 1.))
        influxed_mols = [mol for mol in self.external_molecules if mol not in fixed]
        if not self.params.energy_influx:
            influxed_mols = filter(lambda x: not x.is_energy, influxed_mols)
        if not self.params.building_block_influx:
            influxed_mols = filter(lambda x: not x.is_building_block, influxed_mols)
        if not self.params.bb_class_influx:
            influxed_mols = filter(lambda x: not x.mol_class.has_building_block, influxed_mols)
        
        nr = min(len(influxed_mols), fraction_influx) if isinstance(fraction_influx, int) else int(len(influxed_mols)*fraction_influx) 
        if self.params.prioritize_energy_rich_influx:
            influxed_mols = sorted(influxed_mols, key=lambda x: x.energy_level, reverse = True)
            influxed_mols = influxed_mols[:nr]
        elif self.params.prioritize_energy_poor_influx:
            influxed_mols = sorted(influxed_mols, key=lambda x: x.energy_level)
            influxed_mols = influxed_mols[:nr]
        else:
            influxed_mols = self.env_rand.sample(influxed_mols, nr)
        self.influxed_mols = influxed_mols + fixed 
    
    def init_global_influx_dict(self, influx=None):
        '''
        Initialize a global dictionary for influx rates of molecules in the
        external environment.
        '''
        
        def expected_value(base, domain):
            '''
            calculates the expected value of a log-uniformly distributed random
            variable with *base* and *domain* .
            
            This is the mean of the integral of base^x with U(x) a uniform
            distribution on the given domain.
            '''
            m,n = domain
            if m > n:
                m,n = n,m
            elif m == n:
                return base ** m
            return 1./(n - m) * ( base ** n / math.log(base) - base ** m / math.log(base) ) 
        
        if influx is None:
            influx = 1e-20
            if self.params.influx:
                influx = self.params.influx
            elif self.params.influx_range:
                influx = expected_value(self.params.influx_range.base, (self.params.influx_range.lower, self.params.influx_range.upper))
        self.influx_dict = OrderedDict()
        for mol_ext in self.external_molecules:
            if mol_ext in self.influxed_mols:
                self.influx_dict[mol_ext] = influx
            else:
                self.influx_dict[mol_ext] = None
        
    def init_degradation_dict(self, degr_const=None, ene_degr_const=None, 
                              bb_degr_const=None,degradation_variance_shape=None):
        '''
        Initialize a global dictionary for degradation rates of molecules in the
        external environment.
        '''
        
        if degr_const is None:
            degr_const = self.params.small_mol_ext_degr_const
        if ene_degr_const is None:
            ene_degr_const = self.params.ene_ext_degr_const
        if bb_degr_const is None:
            bb_degr_const = self.params.bb_ext_degr_const
        self.degradation_dict = OrderedDict()
        for mol_ext in self.external_molecules:
            if mol_ext.is_energy and ene_degr_const is not None:
                self.degradation_dict[mol_ext] = ene_degr_const
            elif mol_ext.is_building_block and bb_degr_const is not None:
                self.degradation_dict[mol_ext] = bb_degr_const
            else:
                if degradation_variance_shape is not None:
                    theta = degr_const / degradation_variance_shape
                    self.degradation_dict[mol_ext] = self.env_rand.gammavariate(degradation_variance_shape, theta)
                else:
                    self.degradation_dict[mol_ext] = degr_const
                
    def init_membrane_diffusion_dict(self, diff_const=None, energy_proportional=None,
                                 diff_scaling_func=lambda c, e: c / (e**0.7)):
        if diff_const is None:
            diff_const = self.params.small_mol_diff_const
        if energy_proportional is None:
            energy_proportional = self.params.diff_energy_prop
        self.membrane_diffusion_dict = OrderedDict()
        for mol_ext in self.external_molecules:
            if energy_proportional:
                self.membrane_diffusion_dict[mol_ext] = diff_scaling_func(diff_const, mol_ext.energy_level)
            else:
                self.membrane_diffusion_dict[mol_ext] = diff_const
                
    
                
    def start_concentration_dict(self, init_conc=None, init_conc_dict=None, no_influx_conc=1e-20):
        '''
        Make dictionary of start concentrations for external molecules. If the
        init_conc is not given, start with a concentration that is the
        equilibrium value based on influx and degradation rates of the
        metabolite.
        
        :param init_conc:
        '''
        if init_conc_dict is None:
            init_conc_dict = self.params.init_external_conc_vals
        
        concentration_dict = OrderedDict()
        
        def equilibrium_conc(mol):
            influx_points = 1.
            if self.params.influx_rows is not None:
                influx_points *= len(self.params.influx_rows)
            else:
                influx_points *= self.params.grid_rows 
            if self.params.influx_cols is not None:
                influx_points *= len(self.params.influx_cols)
            else:
                influx_points *= self.params.grid_cols
            grid_influx_scale_fact = influx_points / float(len(self.grid))
            return grid_influx_scale_fact * self.influx_dict[mol] / self.degradation_dict[mol] 
        
        for mol_ext in self.external_molecules: #self.influxed_mols:
            if mol_ext in self.influxed_mols:
                if init_conc is not None:
                    concentration_dict[mol_ext]  = init_conc
                else:
                    concentration_dict[mol_ext] = equilibrium_conc(mol_ext)
                if init_conc_dict is not None:
                    try:
                        concentration_dict[mol_ext] = init_conc_dict[mol_ext.name]
                    except KeyError:
                        pass
            else:
                concentration_dict[mol_ext] = no_influx_conc
            print 'resetting', mol_ext, ' concentration to ', concentration_dict[mol_ext]
        
        return concentration_dict
    
    def reset_grid_influx(self):
        '''
        Reinitialize the global infux dict and the per sub environment influx
        rates.
        '''
        print 'resetting grid influx'
        self.init_global_influx_dict()
        self._init_subenv_influx_rates()
    
    def _init_subenv_influx_rates(self):
        '''
        Set influx rates per molecule for each sub-environment.
        '''
        influx_rows, influx_cols = self.params.influx_rows, self.params.influx_cols
        for sub_env in self.subenvs:
            rows, cols = sub_env.sub_grid
            if influx_rows is not None:
                rows = [ row for row in rows if row in influx_rows ]
            if influx_cols is not None:
                cols = [ col for col in cols if col in influx_cols ]
            for mol in sub_env.influx_dict:
                sub_env.influx_dict[mol] = self.influx_dict[mol]
            self.func_on_grid(lambda l: l.update_small_mol_influxes(sub_env.influx_dict), rows, cols)
    
    def reset_grid_concentrations(self, conc=None, init_conc_str=None):
        if conc is None:
            conc = self.params.init_external_conc
        
        print '\nresetting environmental concentrations:'
                  
        concentration_dict = self.start_concentration_dict(conc)
        self.func_on_grid(lambda l: l.update_small_mol_concentrations(concentration_dict))
            
    def init_external_mol_vals_on_grid(self, init_conc=None):
        '''
        Initialize concentrations, degradation and influx rates of molecules on
        the grid.
        '''
        self._init_subenv_influx_rates()
        concentration_dict = self.start_concentration_dict(init_conc)
        self.func_on_grid(lambda l: l.update_small_mol_degradation_rates(self.degradation_dict))
        self.func_on_grid(lambda l: l.update_small_mol_concentrations(concentration_dict))

    def init_grid(self, verbose=False):
        '''
        Initialize the spatial grid. Set wrapping and barriers on particular
        neighborhoods.
        '''
        nr_grid_rows = self.params.grid_rows 
        nr_grid_cols = self.params.grid_cols
        wrap_ew = self.params.wrap_ew
        wrap_ns = self.params.wrap_ns
        frac_horizontal_bar = self.params.frac_horizontal_bar
        max_frac_horizontal = self.params.max_frac_horizontal
        frac_vertical_bar = self.params.frac_vertical_bar
        max_frac_vertical = self.params.max_frac_vertical
        neighborhoods = self.params.barrier_neighborhoods
        rand_gen = self.env_rand
        
        util.within_range(frac_horizontal_bar, (0.,1.))
        util.within_range(frac_vertical_bar, (0.,1.))
        util.within_range(max_frac_horizontal, (0.,1.))
        util.within_range(max_frac_vertical, (0.,1.))
        
        self.grid = Grid.Grid(nr_grid_rows, nr_grid_cols, 
                              nei_wrapped_ew=wrap_ew, nei_wrapped_ns=wrap_ns)
        self.grid.grid_barriers(rand_gen, frac_horizontal_bar, max_frac_horizontal, frac_vertical_bar, 
                                max_frac_vertical, neighborhoods)
        if verbose:
            print self.grid
        
        # initialize the localities that will be coupled to the grid    
        self.init_localities(len(self.grid))
        self.grid.fill_grid(self.localities)
        return self.grid
    
    def init_localities(self, number_localities, max_time_course_length=0, params_dict=None):
        if params_dict is None:
            params_dict = self.params
        self.localities = []
        for _ in range(number_localities):
            l = Locality(params_dict,
                         internal_molecules=self.internal_molecules, 
                         influx_reactions=self.influx_reactions, 
                         degradation_reactions=self.degradation_reactions,
                         env_rand=self.env_rand, 
                         max_time_course_length=max_time_course_length
                         )
            self.localities.append(l)
            
        self.set_tot_volume()
        return self.localities
    
    def update_volume(self,volume=None):
        if volume is None:
            volume = self.params.per_grid_cell_volume
        for l in self.localities:
            l.volume = volume
        self.set_tot_volume()
        
    def set_tot_volume(self):
        self.volume = sum( [ l.volume for l in self.localities ])
    
    def update_cells_on_grid(self, cell_gp_dict):
        for _c, gp in cell_gp_dict.items():
            gp.updated = True
    
    def add_new_cells_to_grid(self, cell_gp_dict):
        for cell, gp in cell_gp_dict.items():
            gp.content.add_cell(cell)
            gp.updated = True
                
    def clear_dead_cells_from_grid(self):
        for gp in self.grid.gp_iter:
            dead_cells = gp.content._clear_dead_cells()
            if len(dead_cells) > 0:
                gp.updated = True
            
    def grid_toggle_update(self, updated=False):
        self.grid.toggle_gps_updated(updated)
            
    def map_variables(self):
        for gp in self.grid.gp_iter:
            if gp.updated:
                gp.content.map_variables()
            
    def grid_data_from_func(self, func):
        grid_array = self.grid.as_numpy_array
        vfunc = np.vectorize(func)
        return vfunc(grid_array)
        
    def populate_localities(self,population): #TODO translate to grid function (func_on_grid)
        print "Populating localities with", len(population.cells), "cells."
        cells = list(population.cells)
        self.env_rand.shuffle(cells)
        while len(cells):
            gps = list(self.grid.gp_iter)
            self.env_rand.shuffle(gps) 
            for gp in gps:
                gp.content.add_cell(cells.pop())
                gp.updated = True
                if not len(cells):
                    break
    
    def repopulate_localities(self,population,generations_ago,density,mixed=False): 
        population.clear_pop_changes()
        if density == 0.0:
            density = len(population.cells)/float(population.max_pop_size)
            
        print 'density ', density

        cells_pop = list(population.cells)
        cell_temp = cells_pop[0].get_ancestor(3)
        #cell_anc = cells_pop[0].get_ancestor(300)
        #cell_anc = cells_pop[0].get_ancestor_from_time(generations_ago)
        cell_anc = cell_temp 
        
        nr_of_clones = int(population.max_pop_size * density / 2)  
        cells = [cell_temp.clone(0) for _ in range(nr_of_clones)]
        
        for cell in cells:
            cell.rejuvenate(cell_temp)
            cell.mark('lineage', int(0.6*2*population.max_pop_size)) # Blue
            
        #anc_temp = cell_temp.get_ancestor(generations_ago)
        

        print 'Time of birth of WT: ', cell_temp.time_birth
        print 'Time of birth of ancestor: ', cell_anc.time_birth

        #Alteratively, put generations_ago on 0, and mutate your ancestors to compete with knockouts: e.g.:        
        #if True:
            #cell_anc.delete_genes(list(cell_anc.genome.tfs), time=0)
        
        ancs = [cell_anc.clone(0) for _ in range(nr_of_clones)]
        
        for anc in ancs:
            anc.rejuvenate(cell_anc)
            anc.mark('lineage', int(0.125*2*population.max_pop_size)) # Yellow
            #anc.mark('lineage', int(0.6*2*population.max_pop_size)) # Yellow
        
        cells = cells + ancs # List of cell-clones, and ancestors of the clone
               
        population.new_offspring += cells
        population.wipe_pop(1.0,0)
        self.clear_dead_cells_from_grid()

        print "Repopulating localities with", len(cells), "cells."
        #cells = list(population.cells)
        
        #self.env_ransd.shuffle(cells)
         
        while len(cells):
            gps = list(self.grid.gp_iter)
            if mixed:
                self.env_rand.shuffle(gps)
            for gp in gps:
                gp.updated = True
                #gp.content.clear_locality()
                if len(cells) > 0:
                    newcell = cells.pop()
                    newcell.alive = True
                    gp.content.add_cell(newcell)
                    population.add_cell(newcell)

        print 'popsize now', population.current_pop_size
        print len(population.cells)

        print sum( map(lambda gp: len(gp.content.cells), self.grid.gp_iter))
        assert len(population.cells) == sum( map(lambda gp: len(gp.content.cells), self.grid.gp_iter))
    
    def metabolite_grid_data_dict(self):
        '''Return dictionary of spatial concentration data per metabolite 
        
        '''
        m_data_dict = dict() # NOTE: unordered ok
        for mol_class in self.molecule_classes:
            for m in mol_class.molecules.values():
                data = self.grid_data_from_func(lambda x: x.content.get_small_mol_conc(m.paired))
                m_data_dict[m] = data
        return m_data_dict
    
    def population_grid_data_dict(self, marker_names, marker_select_func):
        '''Return a dictionary of spatial distribution of values per marker 
        
        :param marker_names: markers to probe on the grid
        :param marker_select_func: how to select a marker value 
        when there are multiple individuals with different values per grid  
        '''
        marker_data_dict = dict() # NOTE: unordered ok
        for marker_name in marker_names:
            data = self.grid_data_from_func(lambda x: marker_select_func(marker_name, x.content.get_cells()) )
            marker_data_dict[marker_name] = data
        return marker_data_dict
    
    def population_grid_neighborhood_data(self, neighborhood_pop_func, neighborhood='competition'):
        return self.grid_data_from_func(lambda x: neighborhood_pop_func(sum([ n.get_cells() for n in  x.neighbors(neighborhood) ] ,[] )))
        
    def population_grid_data(self, data_func):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            data = self.grid_data_from_func(lambda x: data_func(x.content.get_cells())) 
        return data
    
    def perfect_mix(self):
        self.grid.perfect_mix(self.env_rand)
        self.grid_toggle_update(True)
    
    def cells_grid_diffusion(self, diff_rate=None):
        '''
        Cell diffusion on the grid.
        
        diff_rate : float
            Diffusion rate of cells to neighboring grid points. 
        '''
        if diff_rate is None:
            diff_rate = self.params.cells_grid_diffusion
        before = sum ( map(lambda l: len(l.cells), self.grid.content_iter))
        for gp in self.grid.gp_iter:
            for c in gp.content.get_cells():
                if self.env_rand.uniform(0, 1.) < diff_rate:
                    rn = gp.random_neighbor('diffusion', self.env_rand)
                    if rn is None:
                        continue
                    gp.content.remove_cell(c)
                    gp.updated = True
                    rn.content.add_cell(c)
                    rn.updated = True
        assert before == sum (map(lambda l: len(l.cells), self.grid.content_iter))
                    
    def reset_locality_updates(self):
        for l in self.localities:
            l.new_concentrations = False

    def print_state(self):
        for i, l in enumerate(self.localities):
            print 'locality', i
            print 'CONCENTRATION'
            for m, conc in l.get_mol_concentration_dict().items():
                print '\t', m, conc
            print
            print 'INFLUX'
            for m, inf in l.get_mol_influx_dict().items():
                print "\t", m, inf[1]
            print
                
    def __setitem__(self,key,value):
        self.params[key] = value
    
    def __getitem__(self,key):
        return self.params[key]  

    def upgrade(self):
        '''
        Upgrading from older pickled version of class to latest version. Version
        information is saved as class variable and should be updated when class
        invariants (e.g. fields) are added.
        '''
        version = float(self.version)
        if version < 1.:
            self.init_membrane_diffusion_dict()
        if version < 1.1:
            self.init_sub_envs(1,1,1.)
        self.version = self.class_version
        if version > float(self.class_version):
            print 'upgraded class',
        else:
            print 'reset class', 
        print self.__class__.__name__, ' from version', version ,'to version', self.version
        
    def __getstate__(self):
        odict = self.__dict__.copy()
        return odict
        
    def __setstate__(self, d):
        self.__dict__ = d
        if not hasattr(self, 'version'):
            self.version = '0.0'
        if self.version != self.class_version:
            self.upgrade()
        
