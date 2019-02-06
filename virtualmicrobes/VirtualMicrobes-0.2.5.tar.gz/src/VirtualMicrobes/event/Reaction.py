from VirtualMicrobes.event.Molecule import MoleculeClass
#from itertools import product
import itertools
from collections import OrderedDict
from VirtualMicrobes.my_tools.utility import ReactionScheme

class BadStoichiometryException(Exception):
    pass




class Reaction (object): 
    #TODO refactor to more easily accept alternatively MoleculeClass and
    #Molecule arguments either as lists or as single arguments

    '''
    A reaction can be associated either with individual molecular 
    species or with a Molecule Classes. 

    '''
    
    def __init__(self, type_, reactants, products, stoichiometry, **kwargs):
        '''
        Reactions are rules to convert Molecules to other Molecules, or Transport
        Molecules from one volume to another volume. A reaction specifies its
        reactants and products as MoleculeClasses or Molecules. Because a
        MoleculeClass can hold multiple Molecules, one Reaction is in fact a
        collection of potential molecular reactions. The actualized reactions
        depend on the properties (binding affinities for specific Molecules) of
        the enzymes and the availability of Molecules.
        
        :param reactants: list of MoleculeClass or Molecule objects, defining the Reactant set
        :param products: list of 
        :param stoichiometry:
        '''
        self.type_ = type_
        self.reactants = reactants
        self.products = products
        if len(stoichiometry) != len(reactants) + len(products):
            raise BadStoichiometryException('Stoichiometry does not match number of reactants and products')
        self.stoichiometry = stoichiometry    
        
        react_stois = zip(self.reactants, self.stoichiometry[:len(self.reactants)])
        prod_stois = zip(self.products, self.stoichiometry[-len(self.products):])
        self.reac_scheme = ReactionScheme(reactants = react_stois, products=prod_stois)
        #print "reaction scheme =", self.reac_scheme
        
    def __str__(self):      
        out = "" 
        out +=  (" + ".join([ str(s)+" "+str(r) + '(' + str(r.energy_level) + ')'   
                             for (s,r) in zip(self.stoichiometry[:len(self.reactants)], self.reactants) ]) )
        out += ' --> ' 
        out += ( " + ".join([ str(s)+" "+str(p) + '(' + str(p.energy_level) + ')'  
                             for (s,p) in zip(self.stoichiometry[-len(self.products):], self.products) ]) ) 
        return out
    
    def __copy__(self):
        return self
    
    def __deepcopy__(self, memo):
        '''
        Deepcopying is overridden such that it will in fact do a shallow copy.
        Because reactions appear as members in Genes. (cf. Molecules)
        
        '''
        return self
        
        
class Influx(Reaction):
    
    def __init__(self, substrate, **kwargs):
        '''
        
        :param substrate: of type Molecule
        '''
        super(Influx,self).__init__('influx', [], [substrate], stoichiometry=[1])
        
    def reaction_scheme(self):
        return {"molecule": self.products[0]}
        
class Diffusion(Reaction):
    
    def __init__(self, substrate, **kwargs):
        '''
        
        :param substrate: of type Molecule
        '''
        super(Diffusion,self).__init__('diffusion', [substrate], [], stoichiometry=[1])
        
    def reaction_scheme(self):
        reaction_dict = dict() # NOTE: unordered ok
        reaction_dict["external"] = self.reactants[0].paired
        reaction_dict["internal"] = self.reactants[0]
        return reaction_dict
        
    def sub_reactions(self):
        internal_resources = self.reactants
        external_resources = [ mol.paired for mol in internal_resources ]
        stoi, = self.stoichiometry
        sub_reactions = [ ([(ext_,stoi)],[(int_,stoi)]) for ext_,int_ in  zip(internal_resources,external_resources)]
        return sub_reactions 
    
class Degradation(Reaction):
    
    def __init__(self, substrate, **kwargs):
        '''

        :param substrate: of type Molecule
        '''
        super(Degradation, self).__init__('degradation', [substrate], [], stoichiometry=[1])
        
    def reaction_scheme(self):
        return {"molecule": self.reactants[0]}
    
    def sub_reactions(self): 
        internal_resources =  self.reactants
        stoi, = self.stoichiometry
        sub_reactions = [ ([(sub, stoi)],) for sub in internal_resources ]
        return sub_reactions
        
class Transport(Reaction):
    def __init__(self, substrate_class, energy_source_class, cost, **kwargs):
        '''
        
        :param substrate_class: of type MoleculeClass
        :param energy_source_class: of type MoleculeClass
        :param cost: the cost or stoichiometry of energy to imported substrate
        '''
        '''this implies that 1 substrate molecule will be imported by consuming  "cost" energy_molecules '''
        self.energy_source_class = energy_source_class
        self.substrate_class = substrate_class
        stoichiometry = [1,cost] 
        super(Transport,self).__init__('import', [energy_source_class], [substrate_class], stoichiometry)
        self.init_sub_reaction_dicts()
        
    def init_sub_reaction_dicts(self):
        '''
        Write out dictionaries for the sub_reactions generated by sub_reactions()
        '''
        self.sub_reaction_dicts = []
        for lhs, rhs in self.sub_reactions():
            sub_reaction_dict = dict([("reactants", OrderedDict()),( "products", OrderedDict())])  
            re,stoi = lhs[0]  # NOTE: assuming that first lhs index holds the ONLY substrate
            sub_reaction_dict["reactants"]["substrate"] = {"mol": re, "stoi": stoi} 
            re,stoi = lhs[-1] # NOTE: assuming that the last lhs index holds the energy molecule
            sub_reaction_dict["reactants"]["energy"] = {"mol": re, "stoi": stoi}            
            re,stoi = rhs[0] # NOTE: rhs only holds exactly 1 product
            sub_reaction_dict["products"]["substrate"] = {"mol": re, "stoi": stoi} 
            self.sub_reaction_dicts.append(sub_reaction_dict)        
        return self.sub_reaction_dicts
         
    def sub_reactions(self):
        '''
        Sub-reactions of Transporters link a specific external substrate to its
        internal counterpart. Different energy sources yield combinatorial
        expansion.
        '''
        internal_resources = [ p.molecules.values() for p in self.products ]
        external_resources = [ [ mol.paired for mol in internal ] for internal in internal_resources ]
        ext_int = itertools.chain(*[ zip(external,internal) for external,internal in zip(external_resources, internal_resources) ])
        reactants = itertools.chain(*[ r.molecules.values() if isinstance(r,MoleculeClass) else [r] for r in self.reactants ])       
        sub_stoi, ene_stoi = self.stoichiometry
        sub_reactions = [ ([(ext, sub_stoi), (en, ene_stoi)], [(int_, sub_stoi)])
                         for (en, (ext, int_)) in itertools.product(reactants,  list(ext_int)) ]
        return sub_reactions
    
    def __str__(self):      
        out = "" 
        out +=  (" + ".join([ str(s)+" "+str(r) + '(' + str(r.energy_level) + ')'  
                             for (s,r) in  [ (self.stoichiometry[1], self.reactants[0]) ] ]) )
        out += ' --> ' 
        out += (" + ".join([ str(s)+" "+str(p) + '(' + str(p.energy_level) + ')'  
                            for (s,p) in [ (self.stoichiometry[0], self.products[0])] ]) ) 
        return out
        
class Convert(Reaction):
    
    def __init__(self, reactants, products, stoichiometry):
        '''
        
        :param reactants: MoleculeClasses
        :param products: MoleculeClasses
        :param stoichiometry:
        '''
        super(Convert,self).__init__('conversion', reactants, products, stoichiometry)
        self.init_sub_reaction_dicts()       
    
    @property
    def reac_species(self):
        return [ re['mol'] for sub_reac_dict  in self.sub_reaction_dicts for re in sub_reac_dict['reactants'] ]
    
    @property
    def prod_species(self):
        return [ re['mol'] for sub_reac_dict in self.sub_reaction_dicts for re in sub_reac_dict['products'] ]
    
    def init_sub_reaction_dicts(self):
        '''
        Write out dictionaries for the sub_reactions generated by sub_reactions()
        '''
        self.sub_reaction_dicts = []
        for lhs, rhs in self.sub_reactions():
            sub_reaction_dict = {"reactants": [], "products": []}  
            for re,stoi in lhs: 
                sub_reaction_dict["reactants"].append({"mol": re, "stoi": stoi}) 
            
            for re,stoi in rhs: 
                sub_reaction_dict["products"].append({"mol": re, "stoi": stoi}) 
            
            self.sub_reaction_dicts.append(sub_reaction_dict)        
        return self.sub_reaction_dicts
        
    def sub_reactions(self):
        '''
        Returns a list of all potential reaction schemes in the following form:
        ([ (reactant, stoichiometry), .. ], [ (product, stoichiometry) ..] ).
        The general scheme for reactions from and to Molecule Classes maps molecules within 
        a MolClass on lhs to molecules in another class on the rhs as follows:
        
        Reaction scheme as MoleculeClass scheme: 
        A + B -> C , where A :{a0, a1, a2}, B:{b0, b1}, C:{c0, c1, c2*}
        will be translated into:
        
        a0 + b0 -> c0
        a1 + b0 -> c1
        a2 + b0 -> c2*
        
        a0 + b1 -> c0
        a1 + b1 -> c1
        a2 + b1 -> c2*
       
        * If certain molecule species do not exist (e.g. the c2 in the previous example does not
        exist, the reaction is omitted from possible sub-reactions, and will therefor not take place.  
        Note that products on the rhs will always be converted in to the species corresponding
        to the index of the substrate on the lhs. If there is more product than substrates, e.g.
        A -> C + D where D:{d0, d1}, then there will be subreactions for every possible species of D:
        
        a0 -> c0 + d0
        a0 -> c0 + d1
        
        a1 -> c1 + d0
        a1 -> c1 + d1
        
        a2 -> c2 + d0
        a2 -> c2 + d1
                
        Example 2:
        F + G -> H + I    , where F :{f0, f1, f2}, G:{g0}, H:{h0, h1} , I:{i0, i2}
        becomes:
        
        f0 + g0 -> h0 + i0
        f1 + g0 -> h1 + i0
        
        .
        '''
        reac_stois = self.reac_scheme.reactants
        prod_stois = self.reac_scheme.products
        reac_class_prod_class_pairs = []
        # pad the reaction classes or product classes with (None,None) values
        for (reac_class, r_stoi), (prod_class, p_stoi) in itertools.izip_longest(reac_stois, prod_stois, 
                                                                                 fillvalue=(None, None)) : 
            reac_mol_prod_mol_pairs = []
            # expand to molecule species for each Molecule Class, expanding to [] when it was padded
            reac_mols = reac_class.molecules.values() if reac_class != None else []
            prod_mols = prod_class.molecules.values() if prod_class != None else []
            if reac_class is None or prod_class is None:
                # pad combinations with None, to maintain general form of the mapping
                # e.g. : Molecule Class reaction A + B -> C, with A:{a0,a1} , B:{b0,b1}, C:{c0, c1}
                # will be expanded to:
                # reac_class_prod_class_pairs = 
                # [ 
                #   [ ((a0,a0_s), (c0,c0_s)), 
                #     ((a1,a1_s), (c1,c1_s)) ], 
                #   [ ((b0,b0_s), (None,None)), 
                #     ((b1,b1_s), (None,None)) ] 
                # ] 
                for reac_mol, prod_mol in itertools.izip_longest(reac_mols,prod_mols): 
                    reac_mol_prod_mol_pairs.append(( (reac_mol, r_stoi), (prod_mol, p_stoi) ))
            else:
                # do not pad, but zip to shortest sequence. In this way, if a reaction 
                # between Molecule Classes of unequal size (nr species) is modeled, 
                # molecules with no counter part will not have a reaction asigned.
                # e.g. a reaction A + B -> C + D with with A:{a0,a1} , B:{b0,b1}, C:{c0, c1},
                # D: {d0} will be expanded to:
                # reac_class_prod_class_pairs =
                # [ 
                #   [ ((a0,a0_s), (c0,c0_s)), 
                #     ((a1,a1_s), (c1,c1_s)) ],
                #   [ ((b0,b0_s), (d0,d0_s)) ]
                # ] 
                for reac_mol, prod_mol in itertools.izip(reac_mols,prod_mols): 
                    reac_mol_prod_mol_pairs.append(( (reac_mol, r_stoi), (prod_mol, p_stoi) ))
            reac_class_prod_class_pairs.append(reac_mol_prod_mol_pairs)
        
        sub_reactions = []
        # Now, make the product of all (reactant,product) pairs to make up the 
        # full reactions. 
        for rp_class_pairs in itertools.product(*reac_class_prod_class_pairs):
            #itertools.product(*reac_class_prod_class_pairs)
            # [ ( [ [ ( (r_mol, r_stoi), (p_mol, p_stoi) ), ... ] <-- r_mol-p_mol pairs , .. ] 
            #                                                     <-- r_class-p_class pairs, .. )  ... ]
            #                                                     <-- cartesian prod of all r_class-p_class pairs
            lhs, rhs = [], []
            sub_reaction = (lhs, rhs)
            for (r_mol, r_stoi), (p_mol, p_stoi) in rp_class_pairs:
                if r_mol:
                    lhs.append((r_mol, r_stoi))
                if p_mol:
                    rhs.append((p_mol, p_stoi))
            sub_reactions.append(sub_reaction)
        return sub_reactions
    
class ClassConvert(Convert):
    
    def __init__(self, substrate, energy, product):
        stoichiometry = [1,1,1]
        super(ClassConvert, self).__init__([substrate, energy], [product], stoichiometry)
        self.substrate = substrate
        self.energy_class = energy
        self.product = product
    
    def init_sub_reaction_dicts(self):
        '''
        Write out dictionaries for the sub_reactions generated by sub_reactions()
        '''
        self.sub_reaction_dicts = []
        
        (sub, sub_stoi), (ene_class, ene_stoi) = self.reac_scheme.reactants
        (prod,prod_stoi), = self.reac_scheme.products
        for ene in ene_class.molecules.values():
            sub_reaction_dict = {"reactants": [], "products": []}     
            sub_reaction_dict["reactants"].append({"mol": sub, "stoi": sub_stoi}) 
            sub_reaction_dict["reactants"].append({"mol": ene, "stoi": ene_stoi})
            sub_reaction_dict["products"].append({"mol": prod, "stoi": prod_stoi}) 
            self.sub_reaction_dicts.append(sub_reaction_dict)        

        return self.sub_reaction_dicts

def create_conversions(reaction_stoi_combinations):
    reactions = []
    for reac_stoi, prod_stoi in reaction_stoi_combinations:
        reac, r_stoi = zip(*reac_stoi) # unzipping
        prod, p_stoi = zip(*prod_stoi)
        reactions.append(Convert(reac, prod, r_stoi + p_stoi)) 
    return reactions

def produces(reactions):
    '''
    Set of produced metabolic species.
    
    Parameters
    ----------
    reactions : iterable of class:`Convert` or dict
        set of reactions 
        
    Returns
    -------
    set of `event.Molecule.Molecule`s produced in the reaction set.
    '''
    products = set()
    for r in reactions:
        if isinstance(r, Convert):
            products |= set(r.prod_species)
        elif isinstance(r, dict):
            products |= set(re['mol'] for  re in r['products'])
    return products

def consumes(reactions):
    '''
    Set of consumed metabolic species.
    
    Parameters
    ----------
    reactions : iterable of class:`Convert` or dict
        set of reactions 
        
    Returns
    -------
    set of class:`event.Molecule.Molecule`s consumed in the reaction set.
    '''
    substrates = set()
    for r in reactions:
        if isinstance(r, Convert):
            substrates |= set(r.reac_species)
        elif isinstance(r,dict):
            substrates |= set(re['mol'] for re in r['reactants'])
    return substrates

def find_metabolic_closure(input_set, conversions):
    '''
    Find the autocatalytic closure of metabolites given a set of inputs and
    reactions.
    
    Iteratively overlap the produced + influxed and consumed metabolites of the
    set of conversion reactions, yielding a set of 'potentially autocatalytic
    metabolites'. Iterate over the set of 'potentially autocatalytic reactions'
    and require that all substrates of the reaction are in the set of
    'potentially autocatalytic' metabolites. If not, remove the reaction 
    from the 'potentially autocatalytic' reaction set.
    
    Parameters
    ----------
    input_set : iterable of :class:`event.Molecule.Molecule`
        initial set to start expansion of metabolic set
    
    conversions : iterable of :class:`Conversion`s
        enzymatic reactions that convert metabolites into other metabolites
    
    Returns
    -------
    tuple :( set of class:`event.Molecule.Molecule`s , set of :class:`Conversion`s)
        molecules and reactions in the core autocatalytic cycle.
    '''
    potential_conversions = [ sub_reac for c in conversions for sub_reac in c.sub_reaction_dicts ]
    reduced = True
    while reduced: # keep removing reactions and metabolites until a stable set is found
        reduced = False
        produced = produces(potential_conversions)
        consumed = consumes(potential_conversions)
        potentially_autocatalytic = ( (produced | input_set ) & consumed)  
        for c in list(potential_conversions):
            if set(re['mol'] for re in c['reactants']) - potentially_autocatalytic: # consumes reactant autside auto-cat set
                potential_conversions.remove(c)
                reduced = True 
    
    if not consumed & input_set: # no input mols are being consumed, so it cannot be sustainable
        return set(), set()
    return potentially_autocatalytic, potential_conversions
    
    

def find_product_set(input_mols, conversions):
    '''
    Find metabolites that can be produced from a set of input metabolites, given a set of reactions.
    
    Parameters
    ----------
    input_mols : iterable of :class:`event.Molecule.Molecule`
        initial set to start expansion of metabolic set
    
    conversions : iterable of :class:`Conversion`s
        enzymatic reactions that convert metabolites into other metabolites
        
    Returns
    -------
    set of produced class:`event.Molecule.Molecule`s
    '''
    input_mols = set(input_mols)
    if not input_mols:
        return set()
    _auto_cat_mols, auto_cat_conversions = find_metabolic_closure(input_mols, conversions)
    return produces(auto_cat_conversions)
    
    
    
