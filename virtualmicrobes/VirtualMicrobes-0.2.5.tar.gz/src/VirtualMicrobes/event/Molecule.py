import collections
def _increase_func(x):
    return int(x) + 1
 
class MoleculeClass(object):
    
    def __init__(self, name, molecule_species=None, energy_level=1, 
                 is_energy=False, has_building_block=False):
        self.name = name
        self.energy_level = energy_level
        self.molecules = collections.OrderedDict()
        self.reactant_in = []
        self.product_in = []
        self.is_energy = is_energy
        self.has_building_block = has_building_block
        if molecule_species is not None:
            for m in molecule_species:
                self.add_molecule(m)
                
    def reactant_in_reaction(self, reaction):
        '''
        Add a reaction that has a molecule of this class as one of its
        reactants. 
        :param reaction: the reaction
        '''
        self.reactant_in.append(reaction)
        
    def product_in_reaction(self, reaction):
        self.product_in.append(reaction)  
    
    def add_molecule(self, molecule):
        '''
        Add a molecule to this molecule class. We will put the 'internal'
        variants in the class; Internal variants of molecules reference the
        external molecules.
        :param molecule:
        '''
        if molecule.name not in self.molecules.keys():
            self.molecules[molecule.name] = molecule
            if molecule.mol_class is not None:
                print molecule.mol_class
                raise Exception("The molecule you're trying to add to this mol_class is already in a mol_class")
            molecule.mol_class = self       
            molecule.is_energy = self.is_energy   
            
        else:
            print molecule.name, "already in molecule class"
            
    def __str__(self):
        s = self.name
        if self.is_energy:
            s += '*'
        return s  # + ":" + str(self.molecules.values())
    
    def __len__(self):
        return len(self.molecules)
    
    def __iter__(self):
        for mol in self.molecules.values():
            yield mol
    
    def __copy__(self):
        return self
    
    def __deepcopy__(self, memo):
        '''
        Change copy semantics to ascertain that Molecules can not be deepcopied.
        The Molecules are 'ideal' molecules (types), and no actual tokens are
        created, (only different concentrations in different compartments)
        
        :param memo:
        '''
        return self
    

class Molecule(object):

    """
     Small molecules of the system. Can exist internally or externally.
     Some are metabolites that can take place in (enzymatic) reactions.
     Can diffuse over membranes and may be transported into or out of the cell.

    :version:
    :author:
    """

    index = 0
    class_version = '1.0'
    def __init__(self, name, toxic_level=None, is_internal=True,
                 pair=True,is_building_block=False,
                 is_gene_product=False, mol_class=None, is_energy=False, 
                 environment=None, **kwargs):
        self.version = self.__class__.class_version
        self.index = self.unique_index()   
        self.name = name
        self.paired = None
        if pair:
            self.pair_up()
        
        self.toxic_level = toxic_level
        self.is_building_block = is_building_block    
        self.is_gene_product = is_gene_product
        self.is_internal = is_internal
        self.mol_class = mol_class
        self.is_energy = is_energy
        self.environment = environment
        
    @property
    def energy_level(self):
        return self.mol_class.energy_level
        
    @property
    def is_internal(self):    
        return self._is_internal
    
    @is_internal.setter
    def is_internal(self, val):
        self._is_internal = val
        if self.paired is not None:
            self.paired._is_internal = not val
    
    @property
    def toxic_level(self):
        return self._toxic_level 
    
    @toxic_level.setter
    def toxic_level(self, l):
        self._toxic_level = l
        if self.paired is not None:
            self.paired._toxic_level = l
       
    @property
    def is_building_block(self):
        return self._is_building_block
    
    @is_building_block.setter
    def is_building_block(self, val):
        self._is_building_block = val
        if self.paired is not None:
            self.paired._is_building_block = val
        
    @property
    def is_gene_product(self):
        return self._is_gene_product
    
    @is_gene_product.setter
    def is_gene_product(self, val):
        self._is_gene_product = val
        if self.paired is not None:
            self.paired._is_gene_product = val
        
    @property
    def is_energy(self):
        return self._is_energy
    
    @is_energy.setter
    def is_energy(self, val):
        self._is_energy = val
        if self.paired is not None:
            self.paired._is_energy = val
            
    @property
    def mol_class(self):
        return self._mol_class
    
    @mol_class.setter
    def mol_class(self, c):
        self._mol_class = c
        if self.paired is not None:
            self.paired._mol_class = c
    
    @property
    def environment(self):
        return self._environment 
    
    @environment.setter
    def environment(self, env):
        self._environment = env
        if self.paired is not None:
            self.paired._environment = env
    
    @property
    def is_influxed(self):
        if self.environment is None:
            return False
        return self in self.environment.influxed_mols or (self.paired and self.paired in self.environment.influxed_mols) 
    
    @classmethod
    def unique_index(cls, increase=None):
        if increase is None:
            increase = _increase_func
        cls.index = increase(cls.index)
        return cls.index
        
    def pair_up(self):
        '''
        Create a paired molecule for self on the other side of the Cell
        membrane. When updating a property of self, the property of the paired molecule 
        is automatically updated (if appropriate; e.g. toxic_level or is_energy)  
        '''
        paired = Molecule(name=self.name, pair=False)
        self.paired = paired
        paired.paired = self  # .append(self)
    
    def set_building_block(self, val=True):
        self.is_building_block = val
        self.mol_class.has_building_block = True
    
    def __str__(self):
        s = self.name
        if self.is_energy:
            s += '*'
        if self.is_building_block:
            s = '[' + s + ']'
        if self.is_influxed:
            s = '{' +s + '}'
        return s 
      
    def __repr__(self):
        
        return ('%s(name=%r, toxic_level=%r, is_internal=%r,'
                'is_building_block=%r,'
                'is_gene_product=%r, mol_class=%s, is_energy=%r)' % 
                (self.__class__, self.name, self.toxic_level, self.is_internal,
                 self.is_building_block, self.is_gene_product,
                 self.mol_class, self.is_energy)
        )
    
    def __copy__(self):
        return self
    
    def __deepcopy__(self, memo):
        '''
        Change copy semantics to ascertain that Molecules can not be deepcopied.
        The Molecules are 'ideal' molecules (types), and no actual tokens are
        created, (only different concentrations in different compartments)
        
        :param memo:
        '''
        return self
        
    def upgrade(self):
        '''
        Upgrading from older pickled version of class to latest version. Version
        information is saved as class variable and should be updated when class
        invariants (e.g. fields) are added.
        '''
        version = float(self.version)
        if version < 1.:
            self.environment = None
        
        self.version = self.class_version
        print 'upgraded class', self.__class__.__name__,
        print 'from version', version ,'to version', self.version
            
    def __setstate__(self, state):
        self.__dict__ = state
        if not hasattr(self, 'version'):
            self.version = '0.0'
        if self.version != self.class_version:
            self.upgrade()    
    
class MoleculeIndexer(object):
    
    def __init__(self):
        pass
        
