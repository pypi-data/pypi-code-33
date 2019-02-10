#-*- coding: ISO-8859-15 -*-
#
# Copyright 2016 Jean-Luc PLOIX
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================
# $Id: atoms.py 4238 2016-09-27 11:27:39Z jeanluc $
#  Module  chem_gm.core.atoms
#  Projet GraphMachine
# 
#
#  Author: Jean-Luc PLOIX
#  Janvier 2013
#    Version 0.1
#===============================================================================
"""Module graphmachine.chem_gm.core.atoms

Atom lists, dictionaries and properties definitions
"""
from six.moves.configparser import SafeConfigParser
# from six.moves.configparser import SafeConfigParser
from collections import defaultdict
from ...monal.util.utils import str2tuple
from ..gmconstants import filedict, checkinstall

#-------------------------------------------------------------------------------
class SmiError(Exception):
    pass

#-------------------------------------------------------------------------------
Hydrogenes = ['H', 'D']
Atomes = ['C', 'N', 'O', 'F', 'Cl', 'Br', 'I', 'Si', 'S', 'P', 'Ge'] # od parser
Atomes += Hydrogenes # new parser
AromaticAtomes = ['c', 'n', 'o', 's', 'si']
centraux0 = ['C']
centraux1 = ['C', 'N', 'O']
Atomes1 = [val for val in Atomes if len(val)==1]
Atomes2 = [val for val in Atomes if len(val)==2]

# AtomesOrdonnes = sorted(Atomes, lambda x, y: cmp(len(y), len(x)))
# AromaticOrdonnes = sorted(AromaticAtomes, lambda x, y: cmp(len(y), len(x)))
AtomesOrdonnes = sorted(Atomes, key=len)
AromaticOrdonnes = sorted(AromaticAtomes, key=len)

connectdef = defaultdict(lambda: -1) # connectivité de chaque atome i.e. nb de noeud d'entrée connectables au noeud indicateur atomique
#c onnectdef['C'] = 4
#c onnectdef['N'] = 4
#co nnectdef['O'] = 2

atomName = defaultdict(lambda: "unknown")    # nom atomique
numeroAtom = defaultdict(lambda: -1) # numero atomique
massAtom = defaultdict(lambda: -1)   # masse atomique moyenne
valence = defaultdict(lambda: -1)    # valences observées
preferredVal = defaultdict(lambda: ())
maxvalence = defaultdict(lambda: ())

# lecture des dictionnaires dans le fichier de config
try:
    configfile = filedict["atoms.cfg"]
except KeyError:
    badlist = checkinstall("", ("atoms.cfg",))
    configfile = filedict["atoms.cfg"]
# config = SafeConfigParser()
config = SafeConfigParser()
config.read(configfile)
for opt in config.sections():
    options = config.options(opt)
    atomName[opt] = config.get(opt, 'name')
    numeroAtom[opt] = int(config.get(opt,  'numero'))
    massAtom[opt] = float(config.get(opt, 'mass'))
    st = config.get(opt, 'valence')
    valence[opt] = int(st)
    if "vals" in options:
        st = config.get(opt, "vals")
        lst = str2tuple(st)
        lst2 = [int(value[1:-1]) for value in lst if value.startswith('_') and value.endswith('_')]
        lst3 = []
        for value in lst:
            try:
                lst3.append(int(value))
            except:
                lst3.append(int(value[1:-1]))
        #=======================================================================
        # for value in lst:
        #    if value.startswith('_'):
        #        lst2.append(int(value[1:]))
        #=======================================================================
        preferredVal[opt] = tuple(lst2)
        maxvalence[opt] = max(lst3)
    else:
        preferredVal[opt] = (valence[opt],)
        maxvalence[opt] = valence[opt]
#-------------------------------------------------------------------------------
bonddict = { # degré et isomerie des liaisons
        '-': (1, 0),
        '=': (2, 0),
        '#': (3, 0),
        '/': (1, 1),
        '\\': (1, 2)}

parenthesisdict = { # ouverture et fermeture de parentheses et crochets
        '(': (0, 1),
        ')': (0, -1),
        '[': (1, 1),
        ']': (1, -1)}


#-------------------------------------------------------------------------------
def keyAtoms(atom):
    try:
        return Atomes.index(atom)
    except KeyError:
        return 1000
    
def compareAtoms(atom1, atom2):
    if atom1 == atom2:
        return 0
    if not atom1 in Atomes:
        return -1
    if not atom2 in Atomes:
        return 1
    ind1 = Atomes.index(atom1)
    ind2 = Atomes.index(atom2)
    if ind1 > ind2:
        return 1
    if ind2 > ind1:
        return -1
    return 0
#-------------------------------------------------------------------------------
def addatom(symbol, connectivity, maybearomatic):
    """Add a new atom if it does not exists.
    
     - symbol        -> symbol of the in the perioduc classification nomenclature.
     - numero        -> atomic number
     - connectivity  -> chosen connectivity for this atom
     - maybearomatic -> may be aromatic.
     """
    # ajout d'un nouvel atome s'il n'existe pas
    global Atomes, AtomesOrdonnes, valence, massAtom, numeroAtom, connectdef, AromaticAtomes, AromaticOrdonnes, Connectivite 
    if not symbol in Atomes:
        Atomes.append(symbol)
        connectdef[symbol] = connectivity
        if maybearomatic:
            AromaticAtomes.append(symbol.lower())
#             AromaticOrdonnes = sorted(AromaticAtomes, lambda x, y: cmp(len(y), len(x)))
            AromaticOrdonnes = sorted(AromaticAtomes, key=len)
        AtomesOrdonnes = sorted(Atomes, key=len)       
#        AtomesOrdonnes = sorted(Atomes, lambda x, y: cmp(len(y), len(x)))       

def connectivity(atomlist=Atomes):
    """Read the connectivities of an atom list
    """
    return [connectdef[atom] for atom in atomlist]

def masses(atomlist=Atomes):
    """Read the masses of an atom list
    """
    return [massAtom[atom] for atom in atomlist]

def valences(atomlist=Atomes):
    """Read the valences of an atom list
    """
    return [valence[atom] for atom in atomlist]

def atomnum(atomlist=Atomes):
    """Read the atom numbers of an atom list
    """
    return [numeroAtom[symbol] for symbol in Atomes]

def Z(index):
    try:
        if isinstance(index, int):
            return massAtom[Atomes[index]]
        return massAtom[index.capitalize()]
    except:
        raise IndexError("out of range : %d"%index)

def sortatomlist(source, candidate=Atomes):
    """Sorting the 'source' atom list with respect to the order of a submitted list 'candidate'.
    Erase duplicates if exist.
    Return the sorted list and the remaining
    Initial list remain unmodified. 
    """
    if isinstance(candidate, int):
        candidate = Atomes[:candidate]
    if isinstance(source, str):
        source = source.split(",")
    res = []
    source = source[:]
    for value in candidate:
        if value in source:
            res.append(source.pop(source.index(value)))
    return res, source

def multivalentatomlist(candidates=Atomes):
    """list of multivalent atoms in 'candidates'
    """
    res = []
    for atom in candidates:
        preferred = valence[atom]
        if len(preferredVal[atom]):
            preferred = min([abs(value) for value in preferredVal[atom]])
        if preferred > 1:
            res.append(atom)
    return res

def AtomsLower():
    """Atom list in lower case
    """
    global Atomes
    return [val.lower() for val in Atomes]

#===============================================================================
if __name__ == "__main__":
    pass
#     from string import capitalize
# 
#     for key in massAtom:
# #         st = "%s\t%s\t%s\t%s\t%s"% (key, capitalize(atomName[key]), numeroAtom[key], massAtom[key], valence[key])
#         st = "{0}\t{1}\t{2}\t{3}\t{4}".format(key, capitalize(atomName[key]), numeroAtom[key], massAtom[key], valence[key])
#         print(st)
#     print(atomName['to'])
