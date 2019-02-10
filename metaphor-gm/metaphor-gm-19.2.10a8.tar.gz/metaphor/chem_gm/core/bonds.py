# $Id: bonds.py 4238 2016-09-27 11:27:39Z jeanluc $
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
'''
Created on 2 oct. 2015

@author: jeanluc
'''

# try:
from .atoms import SmiError, valence, numeroAtom, massAtom, Z
# except:
#     from nnmodel.chem_gm.atoms import SmiError, valence, numeroAtom, massAtom, Z
from ...monal.Property import Property, Properties

(NO_BOND,
SINGLE_BOND,
DOUBLE_BOND,
TRIPLE_BOND,
QUADRUPLE_BOND,
AROMATIC_BOND) = range(6)

bondSymbol = {
    NO_BOND: "",
    SINGLE_BOND: "-",
    DOUBLE_BOND: "=",
    TRIPLE_BOND: "#",
    QUADRUPLE_BOND: "$",
    AROMATIC_BOND: r"~",}

bondTypeFromSymbol = {
    "": NO_BOND,
    "-": SINGLE_BOND,
    "=": DOUBLE_BOND,
    "#": TRIPLE_BOND,
    "$": QUADRUPLE_BOND,
    r"~": AROMATIC_BOND,
    "imp": SINGLE_BOND,
    "/": SINGLE_BOND,
    "\\": SINGLE_BOND}

class BondError(SmiError):
    pass
    
@Properties(("broken", "modelbroken", "originClosure", "smilesClosure", "iso", 
             "bondType"), False)
class Bond(object):
    '''
    classdocs
    '''
    _link1 = None
    _link2 = None
    _bondType = NO_BOND
    _originClosure = 0
    _iso = 0
    _smilesClosure = 0
    _broken = 0
    _modelbroken = 0

    def __init__(self, atom1, atom2=None, closure=0, iso=0, bondType=NO_BOND):
        '''
        Constructor
        '''
        self.linkTo(atom1, closure)
        self.linkTo(atom2, closure)
        self._bondType = bondType
        self._iso = iso
        # iso ici est 0, -1 ou 1
        
    def __repr__(self):
        try:
            return "<Bond : %s %s %s>"%(self._link1.numero, self.symbol(True, True), self._link2.numero)
        except:
            return "<Bond %s>"% self.id()
        
    def __str__(self):
        return "%s %s %s" % (self._link1.numero, self.symbol(True, True), self._link2.numero)#, val.symbol) 
    
    def symbol(self, explicit=False, aromatic=False):
        st = bondSymbol[self._bondType]
        if not aromatic and (st == "~"):
            st = "-"
        if not explicit and (st in ["-", ""]):
            st = ""
        if self.iso and st in ["", "-"]:
            st = "/" if self.iso == 1 else "\\" if self.iso == -1 else st
        return st
    
    def brokensymbol(self, model=True):
        if model:
            test = self._modelbroken
        else:
            test = self._broken
        if not test:
            return ""
        return " broken(%s)"% test
    
    def linking(self, atomA, atomB): 
        if not isinstance(atomA, int):
            atomA = atomA.numero
        if not isinstance(atomB, int):
            atomB = atomA.numero
        if atomA == atomB:
            raise BondError("Bond cannot link an atom to itself")
        tg = [self._link1.numero, self._link2.numero]
        return (atomA in tg) and (atomB in tg)                   
    
    def atoms(self):
        return self._link1, self._link2
    
    @Property
    def written(self):
        try:
            return self._link1.written and self._link2.written
        except:
            return False
    
    @Property
    def bondOrder(self):
        res = self.bondType
        if res == AROMATIC_BOND:
            #res = 1.3
            res = 1
        return float(res)
    
    @Property
    def bondNumber(self):
        res = self.bondType
        if res == AROMATIC_BOND:
            res = 1
        return res
    
    @Property
    def linked(self, index):
        if not index:
            return self._link1
        if index == 1:
            return self._link2
        raise IndexError("link index out of range : %s"% index)
    
    @linked.lengetter
    def llinked(self):
        return 2
    
    def linkedto(self, value):
        if value == self.linked[0]:
            return self.linked[1]
        if value == self.linked[1]:
            return self.linked[0]
        raise BondError("not linked to %s"% value)
    
    def isLinked(self, atom):
        return (atom == self.link1) or (atom == self.link2)
    
    def linkTo(self, atom, closure=0):
        #assert atom, "atom must exist to be linked"
        if self._link1 is None:
            self._link1 = atom
            if closure:
                self._link2 = closure
                self._originClosure = closure
                self._broken = closure
        elif atom and ((not closure and (self._link2 is None)) or 
            (closure and (self._link2 == closure))):
            self._link2 = atom
        #else:
        #    raise BondError("Error in linkTo: no available slot")
        
    def danglingBond(self):
        if isinstance(self._link2, int):
            return self._link2
        return False

    def keyForClosure(self):
        k0 = self.bondOrder
        k1 = sum(atom.atomicMass for atom in self.atoms())
        k2 = max(atom.distanceMax for atom in self.atoms())
        return k0, k1, k2
    
    def keyForRing(self, origin, Cfirst=False, Clast=False, limited=False):
        token = self.linkedto(origin)
        if (token.symbol != "C") or not (Cfirst or Clast):
            k0 = token.atomicNumber
        elif Cfirst:
            k0 = 0
        else: # Clast:
            k0 = 1000
#         else:
#             k0 = token.atomicNumber
        k1 = abs(token.charge)
        k2 = self.bondOrder
        if limited:
            return (k0, k1, k2, 0, 0, 0)
        follow = list(bond for bond in token.cbonds if bond != origin)
        if not len(follow) :
            return (k0, k1, k2, 0, 0, 0)
        lst = [bond.keyForRing(token, Cfirst, Clast, True) for bond in follow]
        k3 = sum([val[0] for val in lst])
        k4 = sum([val[1] for val in lst])
        k5 = sum([val[2] for val in lst])
        return (k0, k1, k2, k3, k4, k5)

def keyForClosure(bond):
    return bond.keyForClosure()            
                
        