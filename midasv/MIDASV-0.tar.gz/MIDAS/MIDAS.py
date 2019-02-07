#!/usr/bin/env python

__author__ = "Vrushali Dipak Fangal"
__copyright__ = "Copyright 2014"
__license__ = "MIT"
__maintainer__ = "Vrushali Dipak Fangal"
__email__ = "vrushali@broadinstitute.org"
__status__ = "Development"
__created__ = "Oct, 2017"

#import dependencies
import xmltodict
import glob
from bioservices import *
import re
import os
import argparse
import sys

#logo : http://patorjk.com/software/taag/#p=display&f=Alpha&t=MIDAS%0A
#sbml : http://sbml.org/Special/specifications/sbml-level-2/version-1/html/
#wikipathways :  https://www.pathvisio.org/gpml/
#kegg : https://bioservices.readthedocs.io/en/master/kegg_tutorial.html
print("""
          _____                    _____                    _____                    _____                    _____          
         /\    \                  /\    \                  /\    \                  /\    \                  /\    \         
        /::\____\                /::\    \                /::\    \                /::\    \                /::\    \        
       /::::|   |                \:::\    \              /::::\    \              /::::\    \              /::::\    \       
      /:::::|   |                 \:::\    \            /::::::\    \            /::::::\    \            /::::::\    \      
     /::::::|   |                  \:::\    \          /:::/\:::\    \          /:::/\:::\    \          /:::/\:::\    \     
    /:::/|::|   |                   \:::\    \        /:::/  \:::\    \        /:::/__\:::\    \        /:::/__\:::\    \    
   /:::/ |::|   |                   /::::\    \      /:::/    \:::\    \      /::::\   \:::\    \       \:::\   \:::\    \   
  /:::/  |::|___|______    ____    /::::::\    \    /:::/    / \:::\    \    /::::::\   \:::\    \    ___\:::\   \:::\    \  
 /:::/   |::::::::\    \  /\   \  /:::/\:::\    \  /:::/    /   \:::\ ___\  /:::/\:::\   \:::\    \  /\   \:::\   \:::\    \ 
/:::/    |:::::::::\____\/::\   \/:::/  \:::\____\/:::/____/     \:::|    |/:::/  \:::\   \:::\____\/::\   \:::\   \:::\____\

\::/    / ~~~~~/:::/    /\:::\  /:::/    \::/    /\:::\    \     /:::|____|\::/    \:::\  /:::/    /\:::\   \:::\   \::/    /
 \/____/      /:::/    /  \:::\/:::/    / \/____/  \:::\    \   /:::/    /  \/____/ \:::\/:::/    /  \:::\   \:::\   \/____/ 
             /:::/    /    \::::::/    /            \:::\    \ /:::/    /            \::::::/    /    \:::\   \:::\    \     
            /:::/    /      \::::/____/              \:::\    /:::/    /              \::::/    /      \:::\   \:::\____\    
           /:::/    /        \:::\    \               \:::\  /:::/    /               /:::/    /        \:::\  /:::/    /    
          /:::/    /          \:::\    \               \:::\/:::/    /               /:::/    /          \:::\/:::/    /     
         /:::/    /            \:::\    \               \::::::/    /               /:::/    /            \::::::/    /      
        /:::/    /              \:::\____\               \::::/    /               /:::/    /              \::::/    /       
        \::/    /                \::/    /                \::/____/                \::/    /                \::/    /        
         \/____/                  \/____/                  --                       \/____/                  \/____/         

""")

#######################################
######## Identify File type ###########
#######################################

def identify_file_type(xml_doc):
      key = list(xml_doc.keys())[0]
      ### BioPax
      if key == 'rdf:RDF': 
            doc = xml_doc[key]
            file_type = 'biopax'
      ### SBML
      elif key == 'sbml':
            doc = xml_doc[key]
            file_type = 'sbml'
      ### KEGG
      elif key == 'pathway':
            doc = xml_doc[key]
            file_type = 'kegg'
      ### WikiPathways
      elif key == 'Pathway':
            doc = xml_doc[key]
            file_type = 'WikiPathways'
      ### Consensus
      return doc, file_type


#######################################
############# Consensus ###############
#######################################

### Extract data from the Consensus format dataframe
def extract_data_consensus(df):
      rules = df.to_dict('records')
      consensus_rules = []
      for rule in rules:
            interaction = {}
            for key in rule.keys():
                  interaction[key] = [rule[key].strip()]
            consensus_rules.append(interaction)
      return consensus_rules


#######################################
############## KEGG ###################
#######################################

### Load data from KEGG
def load_kegg(doc) :
      ### Load a KGML file from kegg
      title = doc['@title']
      entry_elements = doc['entry']
      relation_elements = doc['relation']
      return title, entry_elements, relation_elements

### Extract elements from EKGG
def extract_elements_kegg(entry_elements):
      ### Extract interacting elements from kegg file
      kegg = KEGG(verbose=False)
      entries = {}

      tmp = []
      for entry in entry_elements:
            iden = entry['@id']
            name_format = ''
            if '@name' in entry['graphics'].keys():
                  name = entry['graphics']['@name']
                  name_format = name.split(',')[0]
                  name_format = name_format.replace('...','')
                  if entry['@type'] in ['compound','ortholog']:
                        if not kegg.get(name_format) == 404:
                              comp_name = re.findall(r'\nNAME(.*)\n',kegg.get(name_format))
                              glycan_name = re.findall(r'\nCOMPOSITION(.*)\n',kegg.get(name_format))
                              if comp_name:
                                    compound_name = comp_name[0].strip().replace(';','')
                              if glycan_name:
                                    compound_name = glycan_name[0].strip().replace(';','')
                              entries[iden] = compound_name
                        else:
                              entries[iden] = name_format
                  else:
                        entries[iden] = name_format
            elif entry['@type'] == 'group': #['compound', 'gene', 'ortholog', 'map', 'group']
                  grp = []
                  for component in entry['component']:
                        grp.append(entries[component['@id']])
                  entries[iden] = ':'.join(grp)
            else: ## entry['type'] = 'map'
                  entries[iden] = name_format           
      return entries

### Extract reactions from KEGG
def extract_reactions_kegg(entries, relation_elements):
      ### Extract interacts from kegg file
      reactions = []
      if isinstance(relation_elements,dict):
            interaction = {}
            entry1 = relation_elements['@entry1']
            entry2 = relation_elements['@entry2']
            type_of_reaction = relation_elements['@type']
            reaction_type = relation_elements['subtype']['@name']
            reaction_value = relation_elements['subtype']['@value']
            if not reaction_type == 'missing interaction':
                  interaction['products'] = entries[entry2]
                  interaction['reactants'] = entries[entry1]
                  interaction['modifiers'] = ''
                  interaction['type'] = reaction_type
            reactions.append(interaction)
            #return reactions

      for relation in relation_elements:
            entry1 = relation['@entry1']
            entry2 = relation['@entry2']
            type_of_reaction = relation['@type']  # PPrel or PCrel

            interaction = {}
            if 'subtype' in relation.keys():#['subtype'])
                  if isinstance(relation['subtype'],dict):
                        reaction_type = relation['subtype']['@name']
                        reaction_value = relation['subtype']['@value']
                  elif isinstance(relation['subtype'],list):
                        for subtype in relation['subtype']:
                              if subtype['@name'].lower() == 'inhibition':
                                    reaction_type = subtype['@name']
                                    reaction_value = subtype['@value']
                                    break
                              else:
                                    reaction_type  = relation['subtype'][-1]['@name']
                                    reaction_value = relation['subtype'][-1]['@value']
            else:
                  reaction_type = type_of_reaction

            #remove missing interactions
            if not reaction_type == 'missing interaction':
                  interaction['products'] = [entries[entry2]]
                  interaction['reactants'] = ['']#[entries[entry1]]
                  interaction['modifiers'] = [entries[entry1]]
                  interaction['type'] = [reaction_type]
            if interaction and interaction not in reactions:  #Avoid repeats
                  reactions.append(interaction)
      return reactions

### Get interactions from kegg file
def execute_kegg(doc, filename):
      print('Processing file: ',filename)
      title, entry_elements, relation_elements = load_kegg(doc)
      kegg_elements = extract_elements_kegg(entry_elements)
      kegg_relations = extract_reactions_kegg(kegg_elements, relation_elements)
      '''
      for rel in kegg_relations:
            print(rel)
      '''
      return kegg_relations

#######################################
############## SBML ###################
#######################################

## Load SBML file
def load_sbml(doc) :
      ### Load an XML file from SBML and check if it is valid else ignore it
      species = doc['model']['listOfSpecies']['species']
      reactions = doc['model']['listOfReactions']['reaction']
      return species, reactions

## Extract SBML element names
def extract_elements_name_sbml(xml_dict): #dict_name = elements
      dict_name = {}
      iden = xml_dict['@id']
      name = xml_dict['@name']
      dict_name[iden] = name
      return dict_name

## Extract SBML elements
def extract_elements_sbml(species):
      elements = {}
      if isinstance(species,dict) :
            element = extract_elements_name_sbml(species)
            elements.update(element)
      else:
            for elem in species:
                  element = extract_elements_name_sbml(elem)
                  elements.update(element)
      return elements

## Extract SBML reaction
def extract_reaction_sbml(reaction,elements): #dict_name = interactions
      interaction = {}
      reac_id = reaction['@id']
      tmp = {}
      tmp['reactants'] = []
      tmp['products'] = []
      tmp['modifiers'] = []
      tmp['type'] = []
      if 'listOfReactants' in reaction.keys():
            reactants = reaction['listOfReactants']['speciesReference']
            if isinstance(reactants,dict):
                  tmp['reactants'].append(elements[reactants['@species']])
            else:
                  for reactant in reactants:
                        tmp['reactants'].append(elements[reactant['@species']])
            if 'listOfProducts' in reaction.keys():
                  products = reaction['listOfProducts']['speciesReference']
                  if isinstance(products,dict):
                        tmp['products'].append(elements[products['@species']])
                  else:
                        for product in products:
                              tmp['products'].append(elements[product['@species']])
            if 'listOfModifiers' in reaction.keys():
                  modifiers = reaction['listOfModifiers']['modifierSpeciesReference']
                  if isinstance(modifiers,dict):
                        interaction_type = modifiers['@id'].strip().split('_')[2]
                        if interaction_type == 'negativeregulator':  
                              tmp['type'].append('inhibition')
                        else:
                              tmp['type'].append('activation')
                        tmp['modifiers'].append(elements[modifiers['@species']])
                        
                  else:
                        for modifier in modifiers:
                              interaction_type = modifier['@id'].strip().split('_')[2]
                              if interaction_type == 'negativeregulator':
                                    tmp['type'].append('inhibition')
                              else:
                                    tmp['type'].append('activation')
                              tmp['modifiers'].append(elements[modifier['@species']])
            interaction[reac_id] = tmp
      return interaction

## Extract all reactions from SBBML
def extract_reactions_all_sbml(reactions,elements):
      interactions = {}
      if isinstance(reactions,dict) :
            interaction = extract_reaction_sbml(reactions,elements)
            interactions.update(interaction)
      else:
            for reaction in reactions:
                  interaction = extract_reaction_sbml(reaction,elements)
                  interactions.update(interaction)
      return interactions.values()

### Get interactions from sbml file
def execute_sbml(doc, filename):
      print('Processing file: ',filename)

      ### Store pathway elements in elements
      species, reactions = load_sbml(doc)
      sbml_elements = extract_elements_sbml(species)
      sbml_relations = extract_reactions_all_sbml(reactions,sbml_elements)
      '''
      for rel in sbml_relations:
            print(rel)
      '''
      return sbml_relations


#######################################
########## WikiPathways ###############
#######################################

def extract_elements_wiki(doc):
      
        ### Initialize
        data_node_elements = ''
        group_elements = ''
        label_elements = ''
        shape_elements = ''

        ### Data Node Elements
        reactants = {}
        data_node_elements = doc['DataNode']
        ### ['@TextLabel', '@GraphId', '@Type', '@GroupRef', 'Comment', 'Attribute', 'Graphics', 'Xref']
        groups = {}
        if isinstance(data_node_elements, dict):
            data_node_elements = [data_node_elements]
        for data_node_element in data_node_elements:
                graph_id = ''
                type_of_element = ''
                group_ref = ''
                name = data_node_element['@TextLabel']
                db = data_node_element['Xref']['@Database']
                db_id = data_node_element['Xref']['@ID']
                if '@Type' in data_node_element.keys():
                    type_of_element = data_node_element['@Type'].strip()
                if '@GraphId' in data_node_element.keys():
                    graph_id = data_node_element['@GraphId'].strip()
                if not graph_id in reactants.keys():
                    reactants[graph_id] = [name]
                else:
                    reactants[graph_id].append(name)
                if '@GroupRef' in data_node_element.keys():
                    group_ref = data_node_element['@GroupRef'].strip()
                    if not group_ref in groups.keys():
                        groups[group_ref] = [name]
                    else:
                        groups[group_ref].append(name)
                if 'Attribute' in data_node_element.keys():
                    attributes = data_node_element['Attribute']
                    value = ''
                    if isinstance(attributes, dict):
                        if attributes['@Key'] == 'cellular_location':
                            value = attributes['@Value'] # location of the element
                    elif isinstance(attributes, list):
                        if attributes[0]['@Key'] == 'cellular_location':
                            value = attributes[0]['@Value']
                                

        ### Find elements from label(phenotypes)
        labels = {}
        if 'Label' in doc.keys():
            label_elements = doc['Label'] # ['@TextLabel', '@GraphId', 'Graphics', 'Attribute', '@GroupRef', 'Comment', 'BiopaxRef']
            if isinstance(label_elements, dict):
                label_elements = [label_elements]
            name = ''
            graph_id = ''
            for label_element in label_elements:
                if '@TextLabel' in label_element.keys():
                    name = label_element['@TextLabel'].strip()
                if '@GraphId' in label_element.keys():
                    #print(label_element.keys())
                    graph_id = label_element['@GraphId']
                labels[graph_id] = [name]
                if '@GroupRef' in label_element.keys():
                    group_ref = label_element['@GroupRef']
                    if not group_ref in groups.keys():
                        groups[group_ref] = [name]
                    else:
                        groups[group_ref].append(name)
                
        ## Shape elements
        shape = {}
        if 'Shape' in doc.keys():
            shape_elements = doc['Shape'] # ['@GraphId', 'Graphics', '@GroupRef', '@TextLabel', 'Comment', 'Attribute', 'BiopaxRef']
            if isinstance(shape_elements, dict):
                shape_elements = [shape_elements]
            for shape_element in shape_elements:
                if '@TextLabel' in shape_element.keys():
                    name = shape_element['@TextLabel'].strip()
                if '@GraphId' in shape_element.keys():
                    graph_id = shape_element['@GraphId']
                    shape[graph_id] = name
                if '@GroupRef' in shape_element.keys():
                    group_ref = shape_element['@GroupRef']
                    if not group_ref in groups.keys():
                        if name:
                            groups[group_ref] = [name]
                        else:
                            groups[group_ref] = [graph_id]
                    else:
                        if name:
                            groups[group_ref].append(name)
                        else:
                            groups[group_ref].append(graph_id)

        #### State
        states = {}
        if 'State' in doc.keys():
            state_elements = doc['State'] # ['@GraphRef', '@TextLabel', '@GraphId', 'Comment', 'Graphics', 'Xref']
            if isinstance(state_elements, dict):
                state_elements = [state_elements]
            for state_element in state_elements:
                graph_ref = state_element['@GraphRef']
                states[graph_ref] = [reactants[graph_ref]]
                if '@GraphId' in state_element.keys():
                    graph_id = state_element['@GraphId']
                    states[graph_id] = reactants[graph_ref]

        #### Group Elements
        if 'Group' in doc.keys():
            group_elements = doc['Group']
            if isinstance(group_elements, dict):
                group_elements = [group_elements]
            for group_element in group_elements:
                group_id = group_element['@GroupId']
                if '@GroupRef' in group_element.keys():
                    group_ref = group_element['@GroupRef']
                    if not group_ref in groups.keys():
                            groups[group_ref] = [group_id]
                if '@GraphId' in group_element.keys():
                    graph_id = group_element['@GraphId']
                    if not graph_id in groups.keys():
                            groups[graph_id] = [group_id]

        for key in groups.keys():
            if groups[key]:
                groups[key] = [':'.join(groups[key])]

        return reactants, labels, shape, states, groups

def extract_interactions_wiki(doc, reactants, labels, shape, states, groups):

        ### Interactions
        i = 0
        all_interactions = {}
        anchor_list = []
        if 'Interaction' in doc.keys():
            interactions = doc['Interaction'] #['@GraphId', 'Graphics', '@GroupRef', 'Xref', 'Comment', 'BiopaxRef', 'Attribute']
            if isinstance(doc['Interaction'], dict):
                interactions = [interactions]
            for interaction in interactions:
                interac = {}
                interac['type'] = ''
                interac['interaction'] = []
                interac['anchor'] = []
                if '@GroupRef' in interaction.keys():
                    group_id = interaction['@GroupRef']
                if '@GraphId' in interaction.keys():
                    interaction_id = interaction['@GraphId']
                else:
                    interaction_id = 'xyz'+str(i)
                type_of_interaction = ''
                graphics = interaction['Graphics'] #['@ZOrder', '@LineStyle', '@LineThickness', 'Point', '@Color', '@ConnectorType', 'Anchor']
                points = graphics['Point']
                type_of_interaction = ''
                for point in points:
                    if '@GraphRef' in point.keys():
                        graph_id = point['@GraphRef']
                        interac['interaction'].append(graph_id)
                    if '@ArrowHead' in point.keys():
                        type_of_interaction = point['@ArrowHead']
                        interac['type'] = type_of_interaction
                    
                    
                ### Anchors
                if 'Anchor' in graphics.keys():
                    anchors = graphics['Anchor']
                    if isinstance(anchors, dict):
                        anchors = [anchors]
                    for anchor in anchors:
                        if '@GraphId' in anchor.keys():
                            anchor_id = anchor['@GraphId']
                            anchor_list.append(anchor_id)
                            interac['anchor'].append(anchor_id)

                if not interac['interaction'] == []:
                    all_interactions[interaction_id] = interac
                i += 1

        
        j = 0
        ### Graphical Line
        if 'GraphicalLine' in doc.keys():
            graphical_line_interacs = doc['GraphicalLine']  ### ['@GraphId', 'Graphics', 'Comment', '@GroupRef', 'Attribute', 'BiopaxRef']
            if isinstance(doc['GraphicalLine'], dict):
                graphical_line_interacs = [graphical_line_interacs]
            for graphical_line_interac in graphical_line_interacs:
                interac = {}
                interac['type'] = ''
                interac['interaction'] = []
                interac['anchor'] = []
                if '@GroupRef' in graphical_line_interac.keys():
                    group_id = graphical_line_interac['@GroupRef']
                if '@GraphId' in graphical_line_interac.keys():
                    interaction_id = graphical_line_interac['@GraphId']
                else:
                    interaction_id = 'xyz'+str(j)
                type_of_interaction = ''
                graphics = graphical_line_interac['Graphics'] #['@ZOrder', '@LineStyle', '@LineThickness', 'Point', '@Color', '@ConnectorType', 'Anchor']
                points = graphics['Point']
                type_of_interaction = ''
                for point in points:
                    if '@GraphRef' in point.keys():
                        graph_id = point['@GraphRef']
                        interac['interaction'].append(graph_id)
                    if '@ArrowHead' in point.keys():
                        type_of_interaction = point['@ArrowHead']
                        interac['type'] = type_of_interaction
                    
                    
                ### Anchors
                if 'Anchor' in graphics.keys():
                    anchors = graphics['Anchor']
                    if isinstance(anchors, dict):
                        anchors = [anchors]
                    for anchor in anchors:
                        if '@GraphId' in anchor.keys():
                            anchor_id = anchor['@GraphId']
                            anchor_list.append(anchor_id)
                            interac['anchor'].append(anchor_id)
                if not interac['interaction'] == []:
                    all_interactions[interaction_id] = interac
                j += 1


        '''
        for key in all_interactions.values():
              print(key['interaction'])
              for anchor in key['anchor']:
                    if anchor == key['interaction'][0]:
                          print('-->',anchor, key['interaction'])
                    else:
                          print('<---', anchor, key['interaction'])
        '''
                    
        ### Find anchors for reactions
        anchor_in_reactions = {}
        anchor_products = {}
        for anchor in anchor_list:
            for interaction_id in all_interactions.keys():
                interaction = all_interactions[interaction_id]['interaction']
                #print(interaction_id, anchor,interaction)
                mut_interaction = interaction
                #print(anchor,'--->',interaction, mut_interaction, all_interactions[interaction_id]['interaction'])
                if anchor in interaction:
                      #print('yyyyy',anchor,interaction)
                      if anchor == interaction[0]:
                            mut_interaction.remove(anchor)
                            #mut_interaction = list(set(interaction) -set([anchor]))
                            if mut_interaction:
                                  if anchor in anchor_products.keys():
                                        anchor_products[anchor].extend(mut_interaction)
                                  else:
                                        anchor_products[anchor] = mut_interaction
                      elif anchor == interaction[1]:
                            mut_interaction.remove(anchor)
                            #mut_interaction = list(set(interaction) -set([anchor]))
                            if mut_interaction:
                                  if anchor in anchor_in_reactions.keys():
                                        anchor_in_reactions[anchor].extend(mut_interaction)
                                  else:
                                        anchor_in_reactions[anchor] = mut_interaction

        ### Add anchorage to the interactions (modifier and products)
        for interaction_id in all_interactions.keys():
            anchorage_list = []
            anchorage_prod_list = []
            for anchor in all_interactions[interaction_id]['anchor']:
                if anchor in anchor_in_reactions.keys() :
                    if anchor_in_reactions[anchor]:
                        for item in anchor_in_reactions[anchor]:
                            if item in groups.keys():
                                name = groups[item]
                            else:
                                name = [item]
                            anchorage_list.extend(name)#extend(anchor_in_reactions[anchor])
                    all_interactions[interaction_id]['modifiers'] = anchorage_list
                if anchor in anchor_products.keys():
                      if anchor_products[anchor]:
                            for item in anchor_products[anchor]:
                                  if item in groups.keys():
                                        name = groups[item]
                                  else:
                                        name = [item]
                            anchorage_prod_list.extend(name)
                      if 'products' in all_interactions[interaction_id].keys():
                            all_interactions[interaction_id]['products'].extend(anchorage_prod_list)
                      else:
                            all_interactions[interaction_id]['products'] = anchorage_prod_list
                
        #print(groups)
        #print(anchor_products)
        #print(anchor_in_reactions)

        final_interactions = {}
        for interaction_id in all_interactions.keys():
            interaction_ref = all_interactions[interaction_id]
            tmp = {}
            tmp['interaction'] = []
            tmp['modifiers'] = []
            tmp['reactants'] = []
            tmp['products'] = []
            #if len(interaction_ref['interaction']) > 1:
            if interaction_ref['interaction']:
                interaction = interaction_ref['interaction']
                if 'products' in interaction_ref:
                      for product in interaction_ref['products']:
                            name = [shape.get(product), labels.get(product), reactants.get(product), groups.get(product), states.get(product)]
                            name = list(filter(None, name))[0]
                            tmp['products'].extend(name)
                type_of_interaction = interaction_ref['type']
                for identifier in interaction:
                    name = [shape.get(identifier), labels.get(identifier), reactants.get(identifier), groups.get(identifier), states.get(identifier)]
                    if '' in name:
                        print(name)
                        continue
                    #print(identifier,name)
                    name = list(filter(None, name))[0]
                    if name[0] in groups.keys():
                        name = groups[name[0]]#[0]
                    if isinstance(name, list):
                        name = name[0]
                    tmp['interaction'].append(name)
                if 'modifiers' in interaction_ref.keys():
                    anchors = interaction_ref['modifiers']
                    for anchor in anchors:
                        identifier = anchor
                        name = [shape.get(identifier), labels.get(identifier), reactants.get(identifier), groups.get(identifier), states.get(identifier)]
                        name = list(filter(None, name))[0]
                        if name[0] in groups.keys():
                            name = groups[name[0]]
                        tmp['modifiers'].append(name[0])

                #print('***',tmp['interaction'][1:], tmp['products'])
                if tmp['interaction']:
                      tmp['reactants'] = [tmp['interaction'][0]]
                      tmp['products'].extend(tmp['interaction'][1:])
                      del tmp['interaction']
                      tmp['modifiers'] = tmp['reactants'] + tmp['modifiers'] # new line
                      tmp['reactants'] = [''] # new line
                      tmp['type'] = [type_of_interaction.replace('mim-','')]
                      #print(tmp)
                      final_interactions[interaction_id] = tmp
                
        return final_interactions.values()
        

### Get interactions from sbml file
def execute_wiki(doc, filename):
      print('Processing file: ',filename)
      reactants, labels, shape, states, groups = extract_elements_wiki(doc)
      wiki_relations = extract_interactions_wiki(doc, reactants, labels, shape, states, groups)
      '''
      for rel in wiki_relations:
            print('--->',rel)
      '''
      return wiki_relations

#######################################
############### BIOPAX ################
#######################################
def extract_elements_biopax(doc):
      elements = {}
      
      '''
      ### Elements
      bp:PhysicalEntity
      bp:SmallMolecule
      bp:Protein
      bp:Complex
      bp:Dna
      bp:Rna
      bp:Control
      '''
      ### Elements
      #### Physical Entities
      if 'bp:PhysicalEntity' in doc.keys():
            physical_entities = doc['bp:PhysicalEntity']
            if isinstance(physical_entities, dict):
                  physical_entities = [physical_entities]
            for phyent in physical_entities:
                  iden = phyent['@rdf:ID']
                  name = (phyent['bp:displayName']['#text']).strip().replace(' ','_').replace('\'','')
                  elements[iden] = name
                  
      #### Small Molecules
      if 'bp:SmallMolecule' in doc.keys():
            small_molecules = doc['bp:SmallMolecule']
            if isinstance(small_molecules, dict):
                  small_molecules = [small_molecules]
            for sm in small_molecules:
                  iden = sm['@rdf:ID']
                  name = (sm['bp:displayName']['#text']).strip().replace(' ','_').replace('\'','')
                  elements[iden] = name

      #### Proteins
      if 'bp:Protein' in doc.keys():
            proteins = doc['bp:Protein']
            if isinstance(proteins, dict):
                  proteins = [proteins]
            for prot in proteins:
                  iden = prot['@rdf:ID']
                  if '#text' in prot['bp:displayName'].keys():
                        name = (prot['bp:displayName']['#text']).strip().replace(' ','_').replace('\'','')
                  else:
                        if isinstance(prot['bp:name'],list):
                              name = prot['bp:name'][0]['#text']
                        else:
                              name = prot['bp:name']['#text']
                  elements[iden] = name
                  
      #### Complex
      if 'bp:Complex' in doc.keys():
            complexes = doc['bp:Complex']
            if isinstance(complexes, dict):
                  complexes = [complexes]
            for complx in complexes:
                  iden = complx['@rdf:ID']
                  if '#text' in complx['bp:displayName'].keys():
                        name = (complx['bp:displayName']['#text']).strip().replace(' ','_').replace('\'','')
                  else:
                        if isinstance(complx['bp:name'],list):
                              name = complx['bp:name'][0]['#text']
                        else:
                              name = complx['bp:name']['#text']
                  elements[iden] = name

      #### DNA
      if 'bp:Dna' in doc.keys():
            dna_elements = doc['bp:Dna']
            if isinstance(dna_elements,dict):
                  dna_elements = [dna_elements]
            for dna in dna_elements:
                  iden = dna['@rdf:ID']
                  if '#text' in dna['bp:displayName'].keys():
                        name = (dna['bp:displayName']['#text']).strip().replace(' ','_').replace('\'','')
                  else:
                        if isinstance(dna['bp:name'], list):
                              name = dna['bp:name'][0]['#text']
                        else:
                              name = dna['bp:name']['#text']
                  elements[iden] = name

      #### RNA                  
      if 'bp:Rna' in doc.keys():
            rna_elements = doc['bp:Rna']
            if isinstance(rna_elements, dict):
                  rna_elements = [rna_elements]
            for rna in rna_elements:
                  iden = rna['@rdf:ID']
                  name = (rna['bp:displayName']['#text']).strip().replace(' ',':').replace('\'','')
                  elements[iden] = name      

      #### Control
      return elements
      

def extract_stoichiometric_coeff(doc, elements):
      stoichiometric_coeffs = {}
      if 'bp:Stoichiometry' in doc.keys():
            stoichiometric_elements = doc['bp:Stoichiometry']
            if isinstance(stoichiometric_elements, dict):
                  stoichiometric_elements = [stoichiometric_elements]
            for stoichiometry in stoichiometric_elements:
                  iden = stoichiometry['@rdf:ID']
                  name = stoichiometry['bp:physicalEntity']['@rdf:resource'].replace('#','')
                  amount = stoichiometry['bp:stoichiometricCoefficient']['#text']
                  stoichiometric_coeffs[elements[name]] = amount
      return stoichiometric_coeffs

def extract_biochemical_interactions_biopax(doc, elements):
      bcr_reaction_elements = doc['bp:BiochemicalReaction']
      if isinstance(bcr_reaction_elements, dict):
            bcr_reaction_elements = [bcr_reaction_elements]
      bcr_relations = {}
      for bcr in bcr_reaction_elements:
            iden = bcr['@rdf:ID']
            name = bcr['bp:displayName']
            direction = bcr['bp:conversionDirection']['#text']
            bcr_relations[iden] = {}
            interaction = {}
            interaction['reactants'] = []
            interaction['products'] = []
            interaction['modifiers'] = ['']
            elem = ''
            if 'bp:left' in bcr.keys():
                  left_elements = bcr['bp:left']
                  if isinstance(left_elements, list):
                        for lelem in left_elements:
                              elem = lelem['@rdf:resource'].replace('#','')
                              interaction['reactants'].append(elements[elem])
                  else:
                        elem = left_elements['@rdf:resource'].replace('#','')
                        interaction['reactants'] = [elements[elem]]
            if 'bp:right' in bcr.keys():
                  right_elements = bcr['bp:right']
                  if isinstance(right_elements, list):
                        for relem in right_elements:
                              elem = relem['@rdf:resource'].replace('#','')
                              interaction['products'].append(elements[elem])
                  else:
                        elem = right_elements['@rdf:resource'].replace('#','')
                        interaction['products'] = [elements[elem]]
            bcr_relations[iden] = interaction
      return bcr_relations

def extract_degradation_interactions_biopax(doc, elements):
      degrad_relations = {}
      if 'bp:Degradation' in doc.keys():
            degradation_elements = doc['bp:Degradation']
            if isinstance(degradation_elements, dict):
                  degradation_elements = [degradation_elements]
            for degrad in degradation_elements:
                  interaction = {}
                  interaction['products'] = []
                  iden = degrad['@rdf:ID']
                  degrad_left = degrad['bp:left']['@rdf:resource'].replace('#','')
                  interaction['reactants'] = elements[degrad_left]
                  degrad_right = ''
                  interaction['products'] = degrad_right
                  name = degrad['bp:displayName']['#text']
                  interaction['modifiers'] = ['']
                  degrad_relations[iden] = interaction
      return degrad_relations

def extract_catalysis_interactions_biopax(doc, elements, bcr_relations, degradation_relations):
      interaction = {}
      if 'bp:Catalysis' in doc.keys():
            catalysis_elements = doc['bp:Catalysis']
            if isinstance(catalysis_elements, dict):
                  catalysis_elements = [catalysis_elements]
            for catalysis in catalysis_elements :
                  catalyst = {}
                  iden = catalysis['@rdf:ID']
                  controller = catalysis['bp:controller']['@rdf:resource'].replace('#','')
                  catalyst['modifiers'] = [elements[controller]]
                  controlled = catalysis['bp:controlled']['@rdf:resource'].replace('#','')
                  control_type = catalysis['bp:controlType']['#text'].replace('#','')
                  catalyst['type'] = [control_type]
                  if controlled in degradation_relations.keys():
                        reaction = degradation_relations[controlled]
                  if controlled in bcr_relations.keys():
                        reaction = bcr_relations[controlled]
                  interaction[iden] = catalyst
      return interaction


def extract_template_reaction_biopax(doc, elements):
      template_reactions = {}
      if 'bp:TemplateReaction' in doc.keys():
            template_reaction_elements = doc['bp:TemplateReaction']
            if isinstance(template_reaction_elements, dict):
                  template_reaction_elements = [template_reaction_elements]
            for template_reaction in template_reaction_elements:
                  interaction = {}
                  iden = template_reaction['@rdf:ID']
                  product = template_reaction['bp:product']['@rdf:resource'].replace('#','')
                  name = template_reaction['bp:displayName']['#text']
                  interaction['reaction'] = name
                  interaction['products'] = elements[product]
                  interaction['modifiers'] = ['']
                  interaction['reactants'] = ['']
                  template_reactions[iden] = interaction #+'|' + name
      return template_reactions

def extract_template_reaction_regulation(doc, elements, template_reactions):
      template_regulation = {}
      if 'bp:TemplateReactionRegulation' in doc.keys():
            regulations = doc['bp:TemplateReactionRegulation']
            if isinstance(regulations, dict):
                  regulations = [regulations]
            for regulation in regulations:
                  interaction = {}
                  iden = regulation['@rdf:ID']
                  name = regulation['bp:displayName']['#text']
                  control_type = regulation['bp:controlType']['#text']
                  controller = regulation['bp:controller']['@rdf:resource'].replace('#','')
                  controlled = regulation['bp:controlled']['@rdf:resource'].replace('#','')
                  interaction['reactants'] = elements[controller]
                  interaction['products'] = template_reactions[controlled]['products']
                  interaction['reaction'] = template_reactions[controlled]['reaction']
                  interaction['type'] = [control_type]
                  interaction['modifiers'] = ['']
                  template_regulation[iden] = interaction
      return template_regulation

def extract_control_reactions(doc, elements, bcr_interactions):
      control_reaction = {}
      if 'bp:Control' in doc.keys():
            control_reaction_elements = doc['bp:Control']
            if isinstance(control_reaction_elements, dict):
                  control_reaction_elements = [control_reaction_elements]           
            for reaction in control_reaction_elements:
                  interaction = {}
                  iden = reaction['@rdf:ID']
                  if 'bp:displayName' in reaction.keys():
                        name = reaction['bp:displayName']['#text']
                  control_type = reaction['bp:controlType']['#text']
                  controller = reaction['bp:controller']['@rdf:resource'].replace('#','') #Element
                  controlled = reaction['bp:controlled']['@rdf:resource'].replace('#','') #Reaction
                  interaction['modifiers'] = [elements[controller]]
                  interaction['type'] = [control_type]
                  control_reaction[iden] = interaction
      return control_reaction

def extract_pathways(doc, elements):
      pathways = {}
      all_reactions = []
      if 'bp:Pathway' in doc.keys():
            pathway_elements =  doc['bp:Pathway']
            if isinstance(pathway_elements, dict):
                  pathway_elements = [pathway_elements]       
            for pathway in pathway_elements:
                  p = {}
                  pathway_order = []
                  iden = pathway['@rdf:ID']
                  organism = pathway['bp:organism']['@rdf:resource']
                  title = pathway['bp:displayName']['#text']
                  components =  pathway['bp:pathwayComponent']
                  orders = pathway['bp:pathwayOrder']
                  if isinstance(components, dict):
                        component = components['@rdf:resource'].replace('#','')
                        all_reactions.append(component)
                  elif isinstance(components, list):
                        for component in components:
                              comp = component['@rdf:resource'].replace('#','')
                              all_reactions.append(comp)
                  
                  if isinstance(orders, dict):
                        order = orders['@rdf:resource'].replace('#','')
                        pathway_order.append(order)
                  elif isinstance(orders, list):
                        for order in orders:
                              order = order['@rdf:resource'].replace('#','')
                              pathway_order.append(order)
                  p['Components'] = all_reactions
                  p['Order'] = pathway_order
                  pathways[iden] = pathway_order
      return pathways

def extract_pathway_steps(doc):#, elements, catalysis_reactions, bcr, pathways, control_reactions, template_reaction, degrad_relations):
      path = {}
      path_next = {}
      if 'bp:PathwayStep' in doc.keys():
            pathway_step_elements = doc['bp:PathwayStep']
            if isinstance(pathway_step_elements, dict):
                  pathway_step_elements = [pathway_step_elements]
            for pathway_step in pathway_step_elements:
                  path_step = {}
                  next_steps = {}            
                  pathway_steps = []
                  successive_steps = []
                  iden = pathway_step['@rdf:ID']
                  steps = pathway_step['bp:stepProcess']
                  if 'bp:nextStep' in pathway_step.keys():
                        next_step = pathway_step['bp:nextStep']
                        if isinstance(next_step, dict):
                              n_step = next_step['@rdf:resource'].replace('#','')
                              successive_steps.append(n_step)
                              next_steps[iden] = successive_steps
                        elif isinstance(next_step, list):
                              for new_step in next_step:
                                    n_step = new_step['@rdf:resource'].replace('#','')
                                    successive_steps.append(n_step)
                              next_steps[iden] = successive_steps
                  if isinstance(steps, dict) :
                        step_element = steps['@rdf:resource'].replace('#','')
                        pathway_steps.append(step_element)
                        path_step[iden] = pathway_steps
                  elif isinstance(steps, list):
                        for step in steps:
                              step_element = step['@rdf:resource'].replace('#','')
                              pathway_steps.append(step_element)
                        path_step[iden] = pathway_steps
                  path.update(path_step)
                  path_next.update(next_steps)
            
      return path, path_next


def reactions_in_pathways(path,pathways, bcr_interactions, template_reactions, degrad_interaction, control_reactions, catalysis, temp_reg):
      pathway_reactions = {}
      for pathway in pathways.keys():
            for step in pathways[pathway]:
                  pathway_reactions[step] = path[step]

      only_reactions = []  ###Removed pathways
      for reactions in pathway_reactions.values():
            for reaction in reactions:
                  if not reaction in pathways.keys():
                        if reactions not in only_reactions:
                              only_reactions.append(reactions)
      all_reactions = []
      for identifiers in only_reactions:
            if len(identifiers) == 1:
                  identifier = identifiers[0]
                  controlled_reaction = [bcr_interactions.get(identifier), degrad_interaction.get(identifier), template_reactions.get(identifier)]
                  controlled_reaction = list(filter(None, controlled_reaction))[0]
                  if not controlled_reaction in all_reactions:
                        all_reactions.append(controlled_reaction)
            else:
                 identifier = identifiers[0]
                 controlled_reaction = [bcr_interactions.get(identifier), degrad_interaction.get(identifier), template_reactions.get(identifier)]
                 controlled_reaction = list(filter(None, controlled_reaction))[0]
                 for modifiers in identifiers[1:]:
                       modifier = [control_reactions.get(modifiers), catalysis.get(modifiers), temp_reg.get(modifiers)]
                       modifier = list(filter(None, modifier))[0]
                       controlled_reaction.update(modifier)
                       if not controlled_reaction in all_reactions:
                             all_reactions.append(controlled_reaction)

      return all_reactions
                       
def execute_biopax(doc, filename):
      print('Processing file: ',filename)
      elements = extract_elements_biopax(doc)
      stoic = extract_stoichiometric_coeff(doc, elements)
      bcr_interactions = extract_biochemical_interactions_biopax(doc, elements)
      degrad_interaction = extract_degradation_interactions_biopax(doc, elements)
      catalysis = extract_catalysis_interactions_biopax(doc, elements, bcr_interactions,degrad_interaction)
      template_reactions = extract_template_reaction_biopax(doc, elements)
      temp_reg = extract_template_reaction_regulation(doc, elements, template_reactions)
      control_reactions = extract_control_reactions(doc, elements, bcr_interactions)
      pathways = extract_pathways(doc, elements)
      path, path_next = extract_pathway_steps(doc)
      pathway_reactions = reactions_in_pathways(path, pathways, bcr_interactions, template_reactions, degrad_interaction, control_reactions, catalysis, temp_reg )
      '''
      for reaction in pathway_reactions:
            print(reaction)
      '''
      return pathway_reactions

########################################################
######## Classify Up-reg and Down-reg relations ########
########################################################
def classify_relations(relations):
      up_regulation_relations = []
      down_regulation_relations = []
      #identifiers for inhibition rules
      inhib_words = ["inhibition","dephosphorylation","ubiquitination","inhib","tbar"]
      for relation in relations:
            #print('-->',relation)
            if 'type' in relation.keys():
                  #print(relation)
                  if relation['type'] == []:
                        up_regulation_relations.append(relation)
                  elif len(relation['type']) > 1:
                        if set(relation['type']) == {'inhibition'} or set(relation['type'])== {'activation','inhibition'}:
                              down_regulation_relations.append(relation)
                  elif any(word in relation['type'][0].lower() for word in inhib_words):
                        if not relation in down_regulation_relations:
                              down_regulation_relations.append(relation)
                  else:
                        if not relation in up_regulation_relations:
                              up_regulation_relations.append(relation)

      return up_regulation_relations, down_regulation_relations


########################################################
################# Translate relations ##################
########################################################
def translate_rules(up_regulation_relations, down_regulation_relations):

      ### Three cases

      ## Single Product
      ### Only up-regulation : up_regulation_relations
      ### Only inhibitors
      ### One inhibition and one up-regulation
      
      ## Multiple products

      ####### Steps:
      ###find pos regulators
      ### find neg regulators
      ### find

      complete_reactions = {}
      final_rules = {}
      all_elements = [] ## Checks if the element should be set to TRUE
      
      for reg in up_regulation_relations:
            #print('>>>',reg)
            products = reg['products']
            reactants = reg['reactants']
            modifiers = reg['modifiers']
            reg_type = reg['type']

            if 'reaction' in reg.keys():
                  print(reg['reaction'])

            if products == reactants:
                  reactants = ['']

            for modifier in modifiers:
                  #print('xxx',modifier)
                  if modifier in reactants:
                        #print(modifier,'wwwwwwwwww')
                        modifiers.remove(modifier)


            ## Frame reaction
            if modifiers == []: ## no modifier
                  if not reactants == ['']:
                        framed_reaction = ' * '.join(reactants)
            else: ## modifier exists
                  if len(reg_type) > 1 and set(reg_type) == {'activation'}:
                        #print('vvvvvvvvvv',reg)
                        framed_reaction = []
                        for modifier in modifiers:
                              framed_reaction.extend([''.join([' * '.join(reactants)]+[' * ' + modifier])])
                        #print('****', framed_reaction)
                        framed_reaction = ' + '.join(framed_reaction)
                        #print('=>',reg_type)
                        #print('*************', framed_reaction)
                  else:
                        modifiers = [' * '.join(modifiers)]
                        if not reactants == ['']:
                              reactants = [' * '.join(reactants)]
                              framed_reaction = ''.join(reactants +[' * ']+ modifiers)
                        else:
                              framed_reaction = ''.join(modifiers)

            #print('===yyyyyyy', framed_reaction)
            ## Single/ Multiple Products
            for product in products:
                  if not product in complete_reactions.keys():
                        complete_reactions[product] = {}
                        complete_reactions[product]['activators'] = []
                  complete_reactions[product]['activators'].append(framed_reaction)
      
      ## Single product and combination reaction
      for reg in down_regulation_relations:
            
            products = reg['products']
            reactants = reg['reactants']
            modifiers = reg['modifiers']
            reg_type = reg['type']

            if products == reactants:
                  reactants = ['']

            for modifier in modifiers:
                  if modifier in reactants:
                        #print(modifier,'wwwwwwwwww')
                        modifiers.remove(modifier)

            #print('>>>>>>', reg)

            ## Frame reaction
            if modifiers == []: ## no modifier
                  if not reactants == ['']:
                        framed_reaction = ' * '.join(reactants)
            else: ## modifier exists
                  if len(reg_type) > 1 : #and set(reg_type) == {'inhibition'}: ## SBML - single product multiple modifiers - all inhibitors or a combination of inhibitors and activators
                        #print('=====>',reg)
                        #print('xxx>',products)
                        #print(reactants)
                        #print(modifiers)
                        #print(reg['type'])
                        #if set(reg_type) == {'inhibition'}:
                        framed_reaction = []
                        #flag = 'sbml'
                        for i in range(len(reg_type)):
                              if reg_type[i] =='inhibition':
                                    framed_reaction.extend([' * '.join(reactants)+ ' * !'+modifiers[i]])
                              else:
                                    framed_reaction.extend([' * '.join(reactants)+ ' * '+modifiers[i]])
                        framed_reaction = ' + '.join(framed_reaction)
                        #print('<-----',framed_reaction)
                        
                  else:
                        modifiers = [' * !'.join(modifiers)]
                        if not reactants == ['']:
                              reactants = [' * '.join(reactants)]
                              framed_reaction = ''.join(reactants +[' * !']+ modifiers)
                        else:
                              framed_reaction = '!'+' *! '.join(modifiers)

            #print('===>', framed_reaction)

            ## Single/ Multiple products
            for product in products:
                  if not product in complete_reactions.keys():
                        complete_reactions[product] = {}
                        complete_reactions[product]['inhibitors'] = []
                  else:
                        if not 'inhibitors' in complete_reactions[product].keys():
                              complete_reactions[product]['inhibitors'] = []
                  complete_reactions[product]['inhibitors'].append(framed_reaction)
                  #print('xxxxxxxxx', framed_reaction)
                  #complete_reactions[product]['activators'].append(framed_pos_reaction)
      
      final_reactions = []
      for key in complete_reactions.keys():
            final_reaction = ''
            if 'activators' in complete_reactions[key].keys():
                  final_react = []
                  final_reaction = ' + '.join(complete_reactions[key]['activators'])
                  for reaction in complete_reactions[key]['activators']:
                        #print('aaaaaaaaa',reaction)
                        for element in reaction.split(' * '):
                              #print('bbbbbbbbbbb', element)
                              react = element
                              if element in  complete_reactions.keys():
                                    #print('ccccccccc', element)
                                    if 'inhibitors' in complete_reactions[element]:
                                          #print('kkkkkkkkkk', complete_reactions[element])
                                          if complete_reactions[element]['inhibitors'][0].startswith('!'):
                                                #print('kkkkkkkkkkkkk',element,complete_reactions[element]['inhibitors'])
                                                react = element+' * '+' * '.join(complete_reactions[element]['inhibitors'])
                                                final_reaction = final_reaction.replace(element,react)
                                                #print('ddddddddd',final_reaction)
            
            if 'inhibitors' in complete_reactions[key].keys():
                  #print('<<<<<<<<<<', key, complete_reactions[key])
                  inhibitors = ' * '.join(complete_reactions[key]['inhibitors'])
                  #inhibitors = '!'+inhibitors
            else:
                  inhibitors = ''

            
            if final_reaction:
                  if inhibitors:
                        final_reaction = key+' <-- '+' [' +final_reaction+'] * '+inhibitors 
                  else:
                        final_reaction = key+' <-- '+ final_reaction
            else:
                  final_reaction = key+' <-- '+inhibitors

            ## Store all the interacting elements
            final_rules[key] = final_reaction
            all_elements.extend(final_reaction.replace('!','').replace(' *','').replace(' +','').replace(' <--','').replace(']','').replace('[','').split(' '))

            ### Write final rules to a file
            final_reactions.append(final_reaction)
            
            #print('*********')
            #print(final_reaction)
            #print(final_reaction.replace('!','').replace('*','').replace('+','').replace('<--','').split('  '))

            ### Starting elements to be set to TRUE
            if key =='':
                  print('Starting Elements', complete_reactions[key])

      
      ## Total number of elements
      print('Total Number of elements :', len(set(all_elements)))

      ## Number of reactions
      #print('Total Number of Reactions :', len(up_regulation_relations)+len(down_regulation_relations))
      print('Total Number of Reactions after combining :', len(final_rules))

      ## Set TRUE/FALSE
      starting_elements = set(all_elements) - set(final_rules.keys())
      for st_el in starting_elements:
            if st_el:
                  final_reactions.append(st_el+ ' <-- 1')

      return final_reactions
            

class MIDAS:
    
    def run(self):
        
         ### Add options to inputs
         parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
         parser.add_argument('--DirName', required = True, help="Directory containing input files (KEGG, WikiPathways, BioPax, SBML, Consensus (MIDAS))")
         parser.add_argument('--consensus', required = False, help="Reactions in Consensus file format")
         args = parser.parse_args()

         ### Create output directory
         path = os.getcwd()
         dir_name = os.path.join(path,"Results")
         if not os.path.exists(dir_name):
             os.makedirs(dir_name)

         ### Read input argument values
         dirname = args.DirName
         consensus_file = args.consensus

         ### Store all the rules in the list all_rules 
         all_rules = []

         ### Validate consensus file if given as an argument
         if consensus_file:
               with open(consensus_file,'r',encoding='utf-8') as fd:
                     consensus = pd.read_csv(consensus_file, sep='\t')
                     if list(consensus) == ['modifiers', 'products', 'reactants', 'type']:
                           print('Valid Consensus file :', consensus_file)
                     else:
                           sys.exit("Error: Consensus file not in the prescribed format")
                                       
                     ### Process consensus files
                     consensus_rules = extract_data_consensus(consensus)
                     file_interactions = (consensus_rules)
                     for rule in consensus_rules:
                           print(rule)

         else:
               file_interactions = []

         ### Validate file
         if os.path.isdir(dirname): ## Check if input directory exists
             #file_interactions = []
             for filename in glob.iglob(os.path.join(dirname,'*')):
                   with open(filename,'r',encoding='utf-8') as fd:
                         print('********')
                         try:
                               xml_doc = xmltodict.parse(fd.read())
                               print('Valid XML :', filename)
                         except Exception:
                               print("Corrupted File Ignored :",filename)
                               continue
              
                         ### Identofy File type : Biopax, KEGG, WikiPathways, SBML
                         doc, filetype = identify_file_type(xml_doc)
                         print(filename, '---->',filetype)

                         doc_interactions = ''
                         if filetype == 'kegg':
                               doc_interactions = execute_kegg(doc, filename)
                               print('Number of reactions in',filename,':', len(doc_interactions))
                         elif filetype == 'sbml':
                               doc_interactions = execute_sbml(doc, filename)
                               print('Number of reactions in',filename,':', len(doc_interactions))
                         if filetype == 'WikiPathways':
                               doc_interactions = execute_wiki(doc, filename)
                               print('Number of reactions in',filename,':', len(doc_interactions))
                         elif filetype == 'biopax':
                               doc_interactions = execute_biopax(doc, filename)
                               print('Number of reactions in',filename,':', len(doc_interactions))

                         file_interactions.extend(doc_interactions)
             ### Classify rules
             up_reg, down_reg = classify_relations(file_interactions)

             ##delete this
             tmp = []
             for reg in up_reg:
                   if reg.keys() not in tmp:
                         tmp.append(reg.keys())
             #print('####################',tmp)

             ### Translante rules
             final_rules = translate_rules(up_reg, down_reg)

             with open('final_rules','w') as fopen:
                   for rule in final_rules:
                         fopen.write(rule+'\n')
             fopen.close()
                               

         ### Remove .pyc files
         #os.chdir(path)
         for pyc_file in glob.glob("*.pyc"):
             os.remove(pyc_file)


if __name__ == "__main__":
    
    ### Needed to run, calls the script
    MIDAS().run()

