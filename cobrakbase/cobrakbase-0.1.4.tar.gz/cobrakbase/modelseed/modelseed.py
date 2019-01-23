def get_stoichiometry(seed_reaction):
    result = {}
    stoichiometry = seed_reaction['stoichiometry']
    for reagent_str in stoichiometry.split(';'):
        reagent_data = reagent_str.split(':')
        if not reagent_data[1] in result:
            result[reagent_data[1]] = 0
        else:
            print('duplicate', reagent_data, stoichiometry)
        result[reagent_data[1]] = float(reagent_data[0])
    return result

class ModelSEED:
    
    def __init__(self, compounds, reactions):
        self.compounds = compounds
        self.reactions = reactions
        print("cpds:", len(self.compounds), "rxns:", len(self.compounds))
        
    def get_formula(self, seed_id):
        return self.get_attribute('formula', seed_id)
    
    def get_name(self, seed_id):
        return self.get_attribute('name', seed_id)

    def get_attribute(self, attr, seed_id):
        seed = self.get_seed_compound(seed_id)
        if seed == None:
            return None
        if attr in seed:
            value = seed[attr]
            if not value == 'null':
                return seed[attr]
        return None
    
    def get_non_obsolete(self, seed_reaction):
        if not seed_reaction['is_obsolete'] == 0 and 'linked_reaction' in seed_reaction:
            for id in seed_reaction['linked_reaction'].split(';'):
                other = self.get_seed_reaction(id)
                if not other == None:
                    if other['is_obsolete'] == 0:
                        return other['id']

        return seed_reaction['id']

    def is_obsolete(self, seed_id):
        seed = self.get_seed_compound(seed_id)
        if seed == None:
            return None
        
        if 'is_obsolete' in seed:
            is_obsolete = seed['is_obsolete']
            if is_obsolete == 0:
                return False
            else:
                return True
        return None

    def get_seed_compound(self, seed_id):
        if seed_id in self.compounds:
            return self.compounds[seed_id]
        return None
    
    def get_seed_reaction(self, seed_id):
        if seed_id in self.reactions:
            return self.reactions[seed_id]
        return None

    def is_abstract(self, seed_id):
        return None