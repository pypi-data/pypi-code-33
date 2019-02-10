#-*- coding: ISO-8859-15 -*-
# $Id: smitokens.py 4238 2016-09-27 11:27:39Z jeanluc $
#===============================================================================
#  Module core.token
#  Projet GraphMachine
# 
#
#  Author: Jean-Luc PLOIX
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
"""Module graphmachine.core.smitoken

Definition of SmiToken class.

Token from SMILES analysis representing atoms.
"""

#-------------------------------------------------------------------------------
import numpy as np
from collections import defaultdict

from ...monal.Property import Property, Properties, setter, lengetter
try:
    from .atoms import SmiError, valence, numeroAtom, massAtom, Z, preferredVal, \
        maxvalence
    from .bonds import Bond, NO_BOND, SINGLE_BOND, DOUBLE_BOND, AROMATIC_BOND
except:
    from ...chem_gm.core.atoms import SmiError, valence, numeroAtom, massAtom, Z, preferredVal, \
        maxvalence
    from ...chem_gm.core.bonds import Bond, NO_BOND, SINGLE_BOND, DOUBLE_BOND, AROMATIC_BOND

verbose = 0
#-------------------------------------------------------------------------------
class SmiTokenError(SmiError):
    pass

#-------------------------------------------------------------------------------
def tokenKeyValue(tok, withdistance=True):
    alphabond = list(tok.alphagen(True))
    if withdistance:
        return (tok.distanceIndex, tok.atomicNumber, tok.freeelectrons, 
            len(alphabond), max([val.atomicNumber for val in alphabond]), 
            max([val.freeelectrons for val in alphabond]))
        
    else:
        return (tok.atomicNumber, tok.freeelectrons, 
            len(alphabond), max([val.atomicNumber for val in alphabond]), 
            max([val.freeelectrons for val in alphabond]))


@Properties(('numero', 'symbol', 'iso', 'chiral', 'absolutechiral', 
             'charge', 'smilesindex', 'isolatediso', 'rawiso','special',))  #'brokenbonds',
@Properties(('aromatic', ), False)  
class SmiToken(object):
    """class SmiToken(object)
    
    Class of SMILES analysis token.
    A token represent an atom of the SMILES.
    It is created during the compiling of the SMILES. 
    It holds all the attributes read in the SMILES:
    
     - symbol
     - aromaticity
     - bonds
     - broken bonds
     - grade
     - charge
     - chirality
     - isomerism
     - atomic number
        
    It is used in list in the MetaMolecule class.
    During the compiling, a vector attribute 'distances' will be added.
    
    
    Properties:
    
     - numero (read only) -> identifier of the token in the list
     - symbol (read only) -> symbol of the atom
     - aromatic (read only) -> aromaticity
     - iso (read only) -> isomerism
     - chiral (read only) -> chirality 
     - charge (read only) -> charge
     - smilesindex (read only) -> index in the original SMILES
     - richsymbol (read only) -> anriched atom symbol
     - hcount (read only) -> number of hydrogen atoms bonded to the atom
     - valence (read only) -> minimum valence of the atom
     - atomicnumber (read only) -> atomic number of the atom
     - atomicmass (read only) -> atomic mass of the atom
     - grade (read only) -> grade of the     atom
     - freeelectrons (read only) ->number of free electrons
     - distanceIndex (read only)  -> dsitance index
     - group -> 
     - bonds -> list of bonds
     - distances -> list of distances
     - applidata -> data given smiles in [Atom:data] in smiles
     
     
    Creation parameters:  
       
      - parent -> owner of the new object (mandatory)
      - numero -> identifier (mandatory)
      - symbol -> atomic symbol (mandatory)
      - index -> index in the list (default -1)
      - aromatic -> atom aromaticity (default 0)
      - iso -> atom isomerism (default 0)
      - chiral -> atom chirality (default 0)
      - charge -> atomic charge (default 0)
      - mass -> atomic mass (default )
      - hcount -> hydrogen count (default 0)
      - applidata ->  (default None)
    """
    
    def __init__(self, parent, numero, symbol, index=-1, aromatic=0, iso=0, chiral=0, charge=0, mass=0, hcount=0, applidata=None): # SmiToken
        
        assert len(symbol), "symbol cannot be empty"        
        super(SmiToken, self).__init__()
        self._aromatic = aromatic or symbol[0].islower()
        if self._aromatic:
            symbol = symbol.capitalize()
        self.parent = parent # liste parente à laquelle appartient le jeton
        self._group = None  # liste du groupe de voisinage du jeton
        self._numero = numero
        self._symbol = symbol
        self._smilesindex = index  # index dans le smiles d'origine
        self._chiral = chiral
        self._absolutechiral = 0
        self._iso = iso
        self._rawiso = 0
        self._hcount = hcount
        self._charge = charge
        self._atomicMass = mass
        self._cbonds = [] # liste des objets "Bond" liés
        #self._b onds = []  # liste des jetons cibles des liaisons
        #self._b rokenbonds = []  # liste des liaisons brisées 
        #self._b rokenbondindex = [] # indice des anciennes liaisons brisées dans la lise des liaisons 'self._b onds'
        self._distances = None  # vecteur np.array des distances aux autres jetons de la liste
        self._distanceIndex = -1
        if applidata is not None:
            self._applidata = int(applidata)
        self.strdist = False
        self.temppath = None
        self._isolatediso = 0
        self._writtenforced = 0
        self._forceH = 0
        self._priority = None
        self.brokencount = 0
        self._special = 0
        
    def __repr__(self): # SmiToken
        
        if self.numero >= 0:
            return '<SmiToken %d "%s">'% (self.numero, self.symbol)
        return '<SmiToken "%s" %s>'% (self.symbol, self.strtype)
    
    def __hash__(self):
        return hash((self.numero, self.symbol))
    
    def __str__(self): # SmiToken
        lst = ['SmiToken : %s "%s"' % (self.numero, self.symbol)]
        if self.smilesindex >= 0:
            lst.append("smilesindex = %d"% self.smilesindex)
        if self.distanceIndex >= 0:
            lst.append("distanceIndex = %d"% self.distanceIndex)
        if self._aromatic:
            lst.append("aromatic = %d"% self.aromatic)
        if self.grade:
            lst.append('grade = %d'% self.grade)
        if self.charge:
            lst.append("charge = %d"% self.charge)
        if self._atomicMass:
            lst.append("atomic mass = %s"% self.atomicMass)
        if self.absolutechiral:
            lst.append("abs chirality = %d"% self.absolutechiral)
        if self.rawiso:
            lst.append("rawiso = %d"% self.rawiso)
        if self.iso:
            lst.append("iso = %d"% self.iso)
        if self.hcount:
            lst.append("hcount = %d"% self.hcount)
        if self.special:
            lst.append("special = %d"% self.special)
        if self.applidata:
            lst.append("applidata = %s"% self.applidata)
        if len(self.cbonds):
            for i, bond in enumerate(self.cbonds):
                val = bond.linkedto(self)
                if bond.broken:
                    lst.append('cbonds[%d] %s> %s "%s" %s'% (i, bond.symbol(True, True), val.numero, val.symbol, bond.brokensymbol(False)))
                else:
                    lst.append('cbonds[%d] %s> %s "%s"'% (i, bond.symbol(True, True), val.numero, val.symbol))
        if self.strdist:
            if self.distances is not None:
                lst.append('distances :')
                for i, val in enumerate(self.distances):
                    lst.append('\ttoken(%d)\t%d'% (i, val))
        lst.append("")
        st = "\n\t".join(lst)
        return st
    
    def islinked(self, target):
        """boolean True if token is bonded to target
        """
        for bond in self.cbonds:
            if target in bond.atoms():
                return True
        return False           
    
    def smilessymbol(self, isomeric=False, fullH=False):
        """representation of the token in the SMILES.
        """
        res = self.symbol
        if self._atomicMass:
            res = "%s%s"%(self.atomicMass, res)
        self._writtenforced = self._writtenforced or res=="H"
        if self._aromatic:
            res = res.lower()
        if self._special:
            res = "[{0}:{1}]".format(res, self._special)
        activechiral = self.chiral if isomeric else 0
        self._writtenforced = self._writtenforced or bool(activechiral)
        #if isomeric:
        val = '@' if activechiral == 1 else '@@' if activechiral == 2 else ""
        res = "%s%s"%(res, val)
        # mettre ici les attributs H si necessaire
        if not fullH and (self._forceH or activechiral):
            #res = "%s"
            n = self.truehcount
            self._writtenforced = self._writtenforced or bool(n)
            if n == 1:
                res = "%sH"%res
            elif n > 1:
                res = "%s%dH"%(res, n)
        self._writtenforced = self._writtenforced or bool(self.charge)
        if self.charge == 1:
            res = "%s+"% res
        elif self.charge == -1:
            res = "%s-"% res
        elif self.charge > 0:
            res = "%s+%d"%(res, self.charge)
        elif self.charge < 0:
            res = "%s-%d"%(res, -self.charge)
            
        if self.applidata:
            self._writtenforced = True
            res = "%s:%s" %(res, self.applidata)
        if self._writtenforced:
            res = "[%s]" % res
        return res
    
    @Property
    def bonds(self, index):
        """list of the atoms bonded to the token
        """
        cumul = -1
        for bond in self._cbonds: 
            cumul += bond.bondNumber
            if cumul >= index:
                return bond.linkedto(self)
        raise IndexError
    @bonds.lengetter
    def bonds(self):
        cumul = sum(bond.bondNumber for bond in self.cbonds)
        return cumul
    
    def normalizeChiral(self):
        """Order the bonds of the atom when it is chiral.
        Bond with the preceeding token and broken bonds are not modified.
        Depending on the order parity, the chirality may be reversed.
        """
        if not self.chiral:
            return 0
        for bond in list(self.cbonds):
            if bond.bondNumber > 1:
                self._chiral = 0
                self._absolutechiral = 0
                return 0 
        parity = self.getBondsOrderParity(keysort=keyForChiral)  
        self._absolutechiral = _12absolute(self._chiral, parity)
#         if not parity:
#             self.reverseChiral()
#         #self._cbonds[preserved:] = test
        return parity + 1  
        
    @Property
    def modelbrokencount(self):
        """Number of broken bonds.
        """
        lst = [bond for bond in self.cbonds if bond.modelbroken]
        return len(lst)
    
    def clearbrokens(self):
        for bond in self.cbonds:
            bond._broken = 0
    
    def populatebrokenbonds(self, molecule, origin=None):
        """Create closures for Smiles
        """
        if self.written:
            return
        self.written = True
        if origin is None:
            nextbonds = list(self.cbonds)
        else:
            nextbonds = [bond for bond in self.cbonds if bond.linkedto(self) != origin]
        ringbonds = [bond for bond in nextbonds if bond.written]
        self.brokencount += len(ringbonds)
        for bond in ringbonds:
            molecule._ringsmiles += 1
            bond._broken = molecule._ringsmiles
            
            #tok = bond.linkedto(self)
            #self._b rokenbondindex.append(molecule._ringsmiles)
            #self._b rokenbonds.append(tok)
            #tok._b rokenbonds.append(self)
            #tok._b rokenbondindex.append(molecule._ringsmiles)
        #revbonds = list(tok for tok in list(self.bonds) if not tok.written and (tok != origin))
        
        revbonds = list(bond for bond in nextbonds if not bond.linkedto(self).written)
#         revbonds = list(revbonds)
#         revbonds.reverse()
        #revbonds = sorted(revbonds, key=lambda x: keyForRing(self, x))#, reverse=True)
        #revbonds = sorted(revbonds, key=lambda x: x.originClosure)
        
        revbonds = sorted(revbonds, key=lambda x: x.linkedto(self).getPriority(True, self), reverse=True)
        revtok = [bond.linkedto(self) for bond in revbonds]
        for tok in revtok:  
            tok.populatebrokenbonds(molecule, self)
    
    def getBondTo(self, target):
        """get the the existing bonds to ward the target, or None
        """
        for bond in self.cbonds:
            if bond.linkedto(self) == target:
                return bond
        return None
    
    def linkedto(self, target):
        """True if token is linked to target
        """
        for bond in self.cbonds:
            if bond.linkedto(self) == target:
                return True
        return False
    
#     def parseBonds(self):        
#         allusefulbonds = [tok for tok in list(self.bonds) if not tok.written]
#         singlebonds = []
#         doublebonds = []
#         triplebonds = []
#         quadruplebonds = []
#         for tok in allusefulbonds:
#             n = allusefulbonds.count(tok)
#             if n == 1:
#                 singlebonds.append(tok)
#             elif n == 2:
#                 if not tok in doublebonds:
#                     doublebonds.append(tok)
#             elif n == 3:
#                 if not tok in triplebonds:
#                     triplebonds.append(tok)
#             elif n == 4:
#                 if not tok in quadruplebonds:
#                     quadruplebonds.append(tok)       
#         return singlebonds, doublebonds, triplebonds, quadruplebonds
        
#     def getBondTo(self, target):
#         for bond in self.cbonds:
#             if bond.linkedto(target)
    
#     def getBondStr(self, tok, doublebonds, triplebonds=[], quadruplebonds=[]):
#         if tok in quadruplebonds:
#             return "$"
#         if tok in triplebonds:
#             return "#"
#         if tok in doublebonds:
#             return "="
#         if self.iso and (self.iso == tok.iso):# 
#             return "/" if self.iso == 1 else "\\"
#         return ""
    
    def getBondsOrderParity(self, keysort=None, excludeH=False, includePrev=True, includeBroken=True, endlist=[]):
        """Compute the parity of the substutuents with respect of a keysort 
        applied to each substituent.
        includePrev if true, the previous atom is included in the analysis.
        includeBroken if true, the broken links and the previous atom are included in the analysis.
        """
        if not includeBroken:
            lst = [bond.linkedto(self) for (ind, bond) in enumerate(self.cbonds) if ind and not bond.broken]
        elif not includePrev:
            lst = [bond.linkedto(self) for (ind, bond) in enumerate(self.cbonds) if ind]
        else:
            lst = [bond.linkedto(self) for bond in self.cbonds]
        reverse = False
        if excludeH:
            lst = [atom for atom in lst if atom.symbol not in ['H', 'D']]
#             reverse = False
#         else:
#             hs = [atom for atom in lst if atom.symbol in ['H', 'D']]
#             reverse = bool(len(hs)%2)
        if len(endlist):
            delta = len(lst) - len(endlist)
            if delta < 0:
                #raise SmiTokenError
                lst = endlist[-delta:]
            else:
                lst[delta:] = endlist
        if keysort is None:
            slst = sorted(lst, reverse=reverse)
        else:
            slst = sorted(lst, key=keysort, reverse=reverse)
        res = equalParity(lst, slst)
        return res
    
    def getSmiles(self, molecule, origin=None, originbondstr="", isomeric=False, fullH=False, level=0):
        """Return the SMILES representation of the token
        """
        if self.written:
            return "", 0 ,[]
        self.written = True
        res = originbondstr
        nlinked0 = self.cbonds[:]
        if not self.chiral and not fullH:
            nlinked0 = [bond for bond in nlinked0 if bond.linkedto(self).symbol != "H"]
        nlinked  = [bond for bond in nlinked0  if bond.broken or not bond.linkedto(self).written] 
        if self.chiral:
            beginnlinked = [bond for bond in nlinked0  if not bond.broken and bond.linkedto(self).written] 
            #preservedindexes = [nlinked0.index(bond) for bond in beginnlinked]
            #if nlinked0 != beginnlinked + nlinked:
            if len(beginnlinked) != 1:
                pass
                print(molecule.name)
                raise SmiTokenError()
#                 assert nlinked0 == beginnlinked + nlinked
            
        lst = []
        blist = []
        #
        for ind, bond in enumerate(nlinked):
            tok = bond.linkedto(self)
            if bond.broken:
                if bond.broken >= 10:
                    val = "%s%%%s"%(bond.symbol(), bond.broken)
                else:
                    val = "%s%s"%(bond.symbol(), bond.broken)
                crit = (0, 0, 0, bond.bondNumber)
                blist.append((val, crit, tok, [], True))
            else:
                val, ll, indlst = tok.getSmiles(molecule, origin=self, 
                    originbondstr=bond.symbol(), isomeric=isomeric, fullH=fullH, 
                    level=level+1)
                if val:
                    if tok.symbol == "C":
                        crit = ll, 1000, 0, bond.bondNumber # on privilegie les non "C" dans le critere de tri
                    else:
                        crit = ll, tok.atomicNumber, abs(tok.charge), bond.bondNumber
                lst.append((val, crit, tok, indlst, False))
            
        lst = blist + sorted(lst, key=lambda x:x[1]) # ascending sub-smiles criterion
        llst = len(lst)
        
        if self.chiral:
            endlist0 = [val[2] for val in lst]
            endlist = [bond.linkedto(self) for bond in beginnlinked] + endlist0
            parity = self.getBondsOrderParity(keysort=keyForChiral, endlist=endlist)  
            self._chiral = _12absolute(self.absolutechiral, parity)               
        
        res = "%s%s" % (res, self.smilessymbol(isomeric, fullH))
        local = 1
        indexlist = [self.numero]
        toadd = 0
        for ind, (cur, crit, _, indlst, broken) in enumerate(lst):
            indexlist.extend(indlst)
            toadd = max(toadd, crit[0])
            if (ind < llst-1) and not broken: 
                res += '(' + cur + ')'
            else:
                res += cur
        local += toadd

        return res, local, indexlist
    
    def __eq__(self, target):
        res = True
        if id(self) == id(target): return True
        if not isinstance(target, SmiToken): return False
        if not self._smilesindex == target._smilesindex: return False
        if not (self._numero == target._numero): return False
        if not (self._symbol == target._symbol): return False
        if not (self._aromatic == target._aromatic): return False
        if not (self._chiral == target._chiral): return False
        if not (self._iso == target._iso): return False
        if not (self._hcount == target._hcount): return False
        if not (self.applidata == target.applidata): return False
        if not (self._charge == target._charge): return False
        if not (self._atomicMass == target._atomicMass): return False
        #res = res and (len(self._b onds) == len(target._b onds))
#         for b1, b2 in zip(self._bo nds, target._b onds):
#             res = res and (b1._smilesindex == b2._smilesindex)
        if not (len(self._cbonds) == len(target._cbonds)): return False
#         for b1, b2 in zip(self._cbonds, target._cbonds):
#             res = res and (b1.linkedto(self)._smilesindex == b2.linkedto(self)._smilesindex)
        #if not (len(self._b rokenbonds) == len(target._b rokenbonds)): return False
        #for b1, b2 in zip(self._b rokenbonds, target._b rokenbonds):
        #    res = res and (b1._smilesindex == b2._smilesindex)
        return res
    
    def getdiff(self, target):
        """get the differences with target
        """
        if self == target:
            return ""
        lst = []
        if self._numero != target._numero:
            lst.append("numero %s / %s"%(self._numero, target._numero))
        if self._symbol != target._symbol:
            lst.append("symbol %s / %s"%(self._symbol, target._symbol))
        if self._aromatic != target._aromatic:
            lst.append("aromatic %s / %s"%(self._aromatic, target._aromatic))
        if self._chiral != target._chiral:
            lst.append("chiral %s / %s"%(self._chiral, target._chiral))
        if self._iso != target._iso:
            lst.append("iso %s / %s"%(self._iso, target._iso))
        if self._hcount != target._hcount:
            lst.append("hcount %s / %s"%(self._hcount, target._hcount))
        if self.applidata != target.applidata:
            lst.append("class %s / %s"%(self.applidata, target.applidata))
        if self._charge != target._charge:
            lst.append("charge %s / %s"%(self._charge, target._charge))
        if self._atomicMass != target._atomicMass:
            lst.append("atomicMass %s / %s"%(self._atomicMass, target._atomicMass))
#         if len(self._bonds) != len(target._b onds):
#             lst.append("b onds %s / %s"%(self._b onds, target._b onds))
        if len(self._cbonds) != len(target._cbonds):
            lst.append("bonds %s / %s"%(self._cbonds, target._cbonds))
#         if len(self._b rokenbonds) != len(target._br okenbonds):
#             lst.append("b rokenbonds len %s / %s"%(self._br okenbonds, target._b rokenbonds))
        return "\n".join(lst)
    
    @Property
    def writtenforced(self):
        return self._writtenforced
    
    @Property
    def richsymbol(self): # SmiToken
        """eznrighed atom symbol of the atom
        """
        st = self.symbol
        if self.aromatic:
            st = st.lower()
        if self._atomicMass:
            st = str(self._atomicMass) + st
        if self.charge:
            if self.charge > 0:
                st += '+'
            elif self.charge < 0:
                st += '-'
            if abs(self.charge > 1):
                st += str(abs(self.charge))
            st = '[%s]'% st                
        if self.grade:
            st += "g%d"% self.grade
        if self.chiral == 1:
            st += '@'
        elif self.chiral == 2:
            st += '@@'
        if self._hcount:
            if self._hcount == 1:
                st += 'H'
            else:
                st += '%dH'% self._hcount
        if self._iso == 1:
            st += 's'
        elif self._iso == 2:
            st += 'bs'               
        return st
    
#     @property
#     def b onds(self):
#         return self._bonds
    
    @property
    def cbonds(self):
        """list of the bonds.
        """
        return self._cbonds
    
    @Property
    def group(self): # SmiToken
        """list of the neighbourhood tokens.
        """
        return self._group
    
    @setter(group)
    def setgroup(self, value): # SmiToken
        if value is None:
            self._group = None
            return
        if not isinstance(value, list):
            raise SmiTokenError("A group must be a list")
        if not self in value:
            value.append(self)
        self._group = value
    
    @Property
    def hcount(self): # SmiToken
        """number of hydrogen atoms bonded the the token
        """
        return self._hcount
    
    @property
    def truehcount(self):  # SmiToken
        lgr = int(round(sum((bond.bondOrder for bond in self.cbonds if bond.linkedto(self).symbol != "H"))))
        #val = max(self._hcount, self.valence - len(self._b onds))  # a verifier
        val = max(self._hcount, self.valence - lgr)  # a verifier
        if self.charge:
            val += self.charge
        return val
    
    @Property
    def atomicNumber(self): # SmiToke
        """atomic number
        """
        return numeroAtom[self.symbol]
    
    @Property
    def atomicMass(self): # SmiToken
        """atomic mass
        """
        if self._atomicMass:
            return self._atomicMass
        if self.symbol == 'H':
            return 1
        return massAtom[self.symbol]
    
    @Property
    def distanceIndex(self): # SmiToken
        if self._distances is None:
            return -1
        if self._distanceIndex < 0:
            # le calcul de distanceIndex est fait lors de l'appel de la valeur
            self._distanceIndex = max(self.distances) + self.valence -self.grade
        return self._distanceIndex
    
    @property
    def distanceMax(self):
        """lerger distance.
        """
        if self._distances is None:
            return -1
        return max(self._distances)
    
    @Property
    def valence(self): # SmiToken
        """atomic valence
        """
        try:
            nn = preferredVal[self.symbol]
            if not nn:
                nn = valence[self.symbol]
        except:
            nn = valence[self.symbol]
        if isinstance(nn, int):
            return nn
        return min(nn)
        
    @Property
    def valenceMax(self):
        return maxvalence[self.symbol]
    
    def lbonds(self, multi=False):
        if not multi:
            return [bond.linkedto(self) for bond in self._cbonds]
        res = []
        for bond in self._cbonds:
            rg = bond.bondType
            if rg == AROMATIC_BOND:
                rg = 1
            for _ in range(rg):
                res.append(bond.linkedto(self))
    
    @Property
    def grade(self):  # SmiToken
        """atomic grade
        """
        try:
            base = abs(self.charge)
        except:    
            base = 0
        if self.aromatic:
            base += 1
        blst = list(bond.bondOrder for bond in self.cbonds if bond.linkedto(self).symbol != "H")
        gr = base + int(round(sum(blst)))
        #if self.aromatic:
        gr = min(gr, abs(self.valenceMax))
        #noHlist = [tok for tok in self._b onds if tok.symbol != "H"]
#        gr = base + len(noHlist)
#         if self._aromatic:
#             gr += 1
        return gr
    
    @property
    def applidata(self):
        try:
            return self._applidata
        except:
            return 0
    @applidata.setter
    def applidata(self, value):
        self._applidata = value
    
    @Property
    def freeelectrons(self): # SmiToken
        """number of free electrons
        """
        # nombre d'electrons libres.
        return abs(self.charge) #self.valence - self.grade  # todo: a vérifier 
    
    @property
    def has_double_bond(self):
        for ind, bond in enumerate(self._bonds):
            if bond.bondType == DOUBLE_BOND:
#            if val in self._b onds[ind+1:]:
                return True
        return False
    
    def fragmentweight(self, noway=[], full=True, withH=False):
        """Evaluation of the weight of a fragment of smiles
        """
        weight = Z(self.symbol) # on ne compte pas les H
        if withH:
            weight += self.truehcount
        if full:
            tokold = None # pour eviter de coppter plusieurs fois les liaisons multiples
            for tok in list(self.bonds):
                if tok and (tokold != tok) and not (tok in noway):
                    tokold = tok
                    weight += tok.fragmentweight(noway + [self], full, withH)
        return weight
    
    def setcbondto(self, target=None, closure=0, index=-1, iso=0, bondtype=SINGLE_BOND, message=""):
        """create a bond toward to target token
        """
        assert target or closure, "target or closure must exists to be linked"
        bond = None
        if message:
            if target:
                if target.numero > self.numero:
                    print(message, self.numero, target.numero , "=")
                else:
                    print(message, self.numero, target.numero)
            else:
                print(message, "closure %s" % closure)
        #if target:
        if closure:
            #self._b rokenbondindex.append(len(self._cbonds))
            
            if isinstance(target, SmiToken):
                #found = False
                for bond in target._cbonds:                    
                    if isinstance(bond.linked[1], int) and (bond.linked[1] == closure):
                        #founded = True
                        if self._aromatic and target._aromatic:
                            bond._bondType = AROMATIC_BOND
                        bond.linkTo(self, closure) 
                        self._cbonds.append(bond) 
                        break             
            else:
                bond = Bond(self, None, closure, iso=iso, bondType=bondtype)
                self._cbonds.append(bond)
        elif target:
            alreadyaromatic = (len(self.cbonds)==2) and (self.cbonds[0].bondType == self.cbonds[1].bondType == AROMATIC_BOND)
            alreadyaromatic = alreadyaromatic or (len(target.cbonds)==2) and (target.cbonds[0].bondType == target.cbonds[1].bondType == AROMATIC_BOND)
            if not alreadyaromatic and self._aromatic and target._aromatic and (bondtype in [NO_BOND, SINGLE_BOND]):
                bondtype = AROMATIC_BOND
            bond = Bond(self, target, iso=iso, bondType=bondtype)
            if index >= 0:
                self._cbonds.insert(index, bond)
            else:
                self._cbonds.append(bond) 
            #if indextarget < 0:
            target._cbonds.append(bond) 
            #else:
            #    target._cbonds.insert(indextarget, bond) 
        return bond
    
    def hasbondto(self, target, multi=1):
        """boolean has a bon-d toiward the target token
        """
        count = 0
        for bond in self._cbonds:
            if bond.linkedto(self) == target:
                return bond.bondType
#         for tg in self._b onds:
#             if tg.numero == target.numero:
#                 count += 1
        return count >= multi

    def neighbours(self, excluded=[]):
        """list of neighbouring tokens
        """
        return (bond.linkedto(self) for bond in self.cbonds if (bond.linkedto(self) not in excluded) and (bond.linkedto(self).symbol not in excluded))
    
    def groupedNeigbours(self, excluded=[]):
        res = defaultdict(lambda x: [])
#         for tok in (tok for tok in self.neighbours(excluded)):
        for tok in self.neighbours(excluded):
            if tok.symbol in res:
                res[tok.symbol].append(tok)
            else:
                res[tok.symbol] = [tok]
        return res
    
    def neighbours2(self, excluded1=[]):
        """list of the neubouring to 2nd order tokens
        """
        neighbours = self.neighbours(excluded1) #[tok for tok in self.neighbours(excluded1)]
        res = []
        for tok in neighbours:
            res.extend(list(tok.neighbours([self])))
        return res
    
    def neighbours3(self, excluded1=[]):
        """list of the neubouring to 3rd order tokens
        """
#         neighbours = [tok for tok in self.neighbours2(excluded1)]
#         res = []
#         for tok in list(neighbours):
#             res.extend(list(tok.neighbours([self])))
        neighbours = self.neighbours(excluded1)  #[tok for tok in self.neighbours2(excluded1)]
        res = []
        for tok in list(neighbours):
            res.extend(list(tok.neighbours2([self])))
        return res
    
    def bondNeighbours(self, atomexcluded=[]):
        """generator of bonded neighbouring tokens
        """
        symbolexcluded = [val for val in atomexcluded if isinstance(val, str)]
        #res = (bond for bond in self.cbonds if bond.linkedto(self) not in atomexcluded)
        for bond in self.cbonds:
            if bond.linkedto(self) in atomexcluded:
                continue
            if bond.linkedto(self).symbol in symbolexcluded:
                continue
            yield bond
    
    def bondNeighbours2(self, atomexcluded1=[]):
        """generator of bonded neighbouring to 2nd order tokens
        """
        neighbours = self.neighbours(atomexcluded1)  #[bond.linkedto(self) for bond in self.bondNeighbours(atomexcluded1)]
        res = []
        for tok in neighbours:
            res.extend(list(tok.bondNeighbours([self])))
        return res
        
    def alphagen(self, withoutduplicate=False, modelbrkexcluded=False, excluded=[]): # SmiToken
        """generator for the alpha atoms
        """
        # générateur de la liste des atomes alpha
        # excluded est une liste de jetons a exclure de la liste, pour éviter les 
        # retours en arrière
        exc = list(excluded)
        exc.append(self)
        for bond in list(self.cbonds):
            isbroken = bond._modelbroken
            val = bond.linkedto(self)
            if not (val in exc) and  not (modelbrkexcluded and isbroken):
                if withoutduplicate:
                    exc.append(val)
                yield val
            continue
#         for i, val in enumerate(lst):
#             isbroken = i in self._b rokenbondindex
#             if not (val in exc) and  not (smibrkexcluded and isbroken):
#                 if withoutduplicate:
#                     exc.add(val)
#                 yield val
#             continue
    
    def betagen(self, withoutduplicate=False, excluded=[]): # SmiToken
        """generator for the beta atoms.
        """
        mem = set([self])
        for val in self.alphagen(withoutduplicate):
            for val2 in val.alphagen(withoutduplicate, False, excluded):
                if not val2 in mem:
                    mem.add(val2)
                    yield val2
    
    def gettreeoutofgroup(self, acceptedgroups=[]): # SmiToken
        """building trees out of neighbouring group.
        """
        connectedleaves = []
        res = []
        for child in self.alphagen(True):
            if (not child.group):
                if not child in res:
                    res.append(child)
                child.group = res
                res2, connected2 = child.gettreeoutofgroup(acceptedgroups)
                for tok in res2:
                    if not tok in res:
                        res.append(tok)
                for tok in connected2:
                    if not tok in connectedleaves:
                        connectedleaves.append(tok)
            elif  (child.group != self.group) and child.group in acceptedgroups:
                if not child in res:
                    res.append(child)
                if not child in connectedleaves:
                    connectedleaves.append(child)
        return res, connectedleaves
    
    @Property
    def distances(self, index): # SmiToken
        """vector of distances
        """
        # distance est une propriété vectorielle donnant lesq distances 
        # aux autres jetons de la liste.
        # La liste dont est membre self est référencée par "parent"
        return 0 if self._distances is None else self._distances[index]
    
    @lengetter(distances)
    def ldistances(self): # SmiToken
        return 0 if self.parent is None else len(self.parent)
    
    @setter(distances)
    def setdistances(self, index, value): # SmiToken
        if self._distances is None:
            self._distances = np.zeros((len(self.parent)), dtype=int)
        self._distances[index] = value
    
    def setAutoDistance(self): # SmiToken
        self._distances[self._numero] = 0
    
    def distance2token(self, target, smibrkexcluded=False, covered=[], 
                       withpath=False):   # SmiToken
        """computing the distance toward target troken
         - target: target token
         - smibrkexcluded: exclusion of the broken bonds of the smiles
         - covered: list of the already examined tokens
         - withpath: return also the path toward the targezrt
        """
        if target.numero == self.numero:
            return 0
        dist = self.distances[target.numero]
        if dist and not (self.temppath is None and withpath):
            if withpath:
                if (self.temppath is None) and (dist==1):
                    # ce cas apparait dans la recherche des chemeins de 
                    # cycles lorsque un cycle a une arrête communer avec 
                    # un cycle déjà traité
                    self.temppath = [self, target]
                return dist, self.temppath
            return dist
        if self in covered:
            if withpath:
                return len(self.parent), None
            return len(self.parent)
        searchlist = list(self.alphagen(withoutduplicate=True, 
                        smibrkexcluded=smibrkexcluded, excluded=covered)) 
        if target in searchlist:
            dist = 1
            self.temppath = [self, target]
        else:
            dist = len(self.parent)
            for voisin in searchlist:
                if withpath:
                    dloc, pathloc = voisin.distance2token(target, 
                                smibrkexcluded, [self] + covered, withpath=True) 
                    if (dloc + 1 < dist) and pathloc is not None:
                        dist = dloc + 1
                        self.temppath = [self] + pathloc
                else:
                    dloc = voisin.distance2token(target, smibrkexcluded,
                                [self] + covered) 
                    dist = min(dist, dloc + 1)
        if dist < len(self.parent):
            self.distances[target.numero] = dist
            target.distances[self.numero] = dist
        if withpath:
            return dist, self.temppath
        return dist
    
    def computedistances2list(self, tokenlist, smibrkexcluded=False): # SmiToken
        """compute distances toward a list of tokens
        """
        lst = [val for val in tokenlist 
               if (val != self) and not val.distances[self.numero]]
        for target in lst:
            self.distance2token(target, smibrkexcluded=smibrkexcluded)
            
    def bestof(self, target, withdistance=True): # SmiToken
        """best of the two tokens
        """
#         if self.compare(target, withdistance) > 0:
        if tokenKeyValue(self, withdistance) >= tokenKeyValue(target, withdistance):
            return self
        return target
            
#     def compareForChiral(self, target):        
#         # A - comparaison du numéro atromique
#         res = cmp(self.atomicNumber, target.atomicNumber)
#         if res: return res
#         # B - compa    raison des masses atomiques des isotopes
#         
#         # C - comparaison du nombre d'atomes en alpha
#         alphabond = list(self.alphagen(True))  #[val for val in self.alphagen()]
#         alphaatom = list(target.alphagen(True))  #[val for val in target.alphagen()]
#         res = cmp(len(alphabond), len(alphaatom))
#         if res: return res
#         
#         # D - comparaison du numéro atomique max des atomes en alpha
#         Z1 = max([val.atomicNumber for val in alphabond])
#         Z2 = max([val.atomicNumber for val in alphaatom])
#         res = cmp(Z1, Z2)
#         if res: return res
#         
#         # F - comparaison de l'ordre des liaisons avec les atomes en alpha
#         val1 = max([list(self.bonds).count(tok) for tok in self.alphagen()])
#         val2 = max([list(target.bonds).count(tok) for tok in target.alphagen()])
#         res = cmp(val1, val2)
#         if res: return res
#         
#         # G - comparaison du nombre d'atomes en beta
#         betabond = list(self.betagen(True))  #[val for val in self.betagen()]
#         betaatom = list(target.betagen(True))  #[val for val in target.betagen()]
#         res = cmp(len(betabond), len(betaatom))
#         if res: return res
#         
#         # H - comparaison du numéro atromique des atomes en beta
#         Z1 = max([val.atomicNumber for val in betabond])
#         Z2 = max([val.atomicNumber for val in betaatom])
#         res = cmp(Z1, Z2)
#         if res: return res
#         
#         # J - comparaison de l'ordre des liaisons avec les atomes en beta        
#         val1 = max([list(self.bonds).count(tok) for tok in self.betagen()])
#         val2 = max([list(target.bonds).count(tok) for tok in target.betagen()])
#         res = cmp(val1, val2)
#         return res
#                 
#     def keyValue(self, withdistance=True):
#         alphabond = list(self.alphagen(True))
#         if withdistance:
#             return (self.distanceIndex, self.atomicNumber, self.freeelectrons, 
#                 len(alphabond), max([val.atomicNumber for val in alphabond]), 
#                 max([val.freeelectrons for val in alphabond]))
    
    def compare(self, target, withdistance=True): # SmiToken
        """comparing current token with target token.
         - withdistance -> include the distance in the comparison
        """
        # 0 - comparaison des index de classes
        def cmp(a, b): return (a > b) - (a < b)
        
        if withdistance:
            res = cmp(self.distanceIndex, target.distanceIndex)
            if res: return res
        
        # A - comparaison du numéro atromique
        res = cmp(self.atomicNumber, target.atomicNumber)
        if res: return res
        
        # B - comparaison du nombres d'électrons libres
        res = cmp(self.freeelectrons, target.freeelectrons)
        if res: return res
        
        # C - comparaison du nombre d'atomes en alpha
        alphabond = list(self.alphagen(True))  #[val for val in self.alphagen()]
        alphaatom = list(target.alphagen(True))  #[val for val in target.alphagen()]
        res = cmp(len(alphabond), len(alphaatom))
        if res: return res
        
        # D - comparaison du numéro atomique max des atomes en alpha
        Z1 = max([val.atomicNumber for val in alphabond])
        Z2 = max([val.atomicNumber for val in alphaatom])
        res = cmp(Z1, Z2)
        if res: return res
        
        # E - comparaison du nombres d'élections libres des atomes en alpha
        E1 = max([val.freeelectrons for val in alphabond])
        E2 = max([val.freeelectrons for val in alphaatom])
        res = cmp(E1, E2)
        if res: return res
        
        # F - comparaison de l'ordre des liaisons avec les atomes en alpha
        val1 = max([list(self.bonds).count(tok) for tok in self.alphagen()])
        val2 = max([list(target.bonds).count(tok) for tok in target.alphagen()])
        res = cmp(val1, val2)
        if res: return res
        
        # G - comparaison du nombre d'atomes en beta
        betabond = list(self.betagen(True))  #[val for val in self.betagen()]
        betaatom = list(target.betagen(True))  #[val for val in target.betagen()]
        res = cmp(len(betabond), len(betaatom))
        if res: return res
        
        # H - comparaison du numéro atromique des atomes en beta
        Z1 = max([val.atomicNumber for val in betabond])
        Z2 = max([val.atomicNumber for val in betaatom])
        res = cmp(Z1, Z2)
        if res: return res
        
        # I - comparaison du nombres d'élections libres des atomes en beta
        E1 = max([val.freeelectrons for val in betabond])
        E2 = max([val.freeelectrons for val in betaatom])
        res = cmp(E1, E2)
        if res: return res
        
        # J - comparaison de l'ordre des liaisons avec les atomes en beta        
        val1 = max([list(self.bonds).count(tok) for tok in self.betagen()])
        val2 = max([list(target.bonds).count(tok) for tok in target.betagen()])
        res = cmp(val1, val2)
        return res
    
    def bondTo(self, target):# SmiToken
        for bond in self.cbonds:
            if bond.linkedto(self) == target:
                return bond
        return None
    
    def getPriority(self, withbondtype= False, origin=None):# SmiToken
        k00 = 0
        if withbondtype and origin:
            bond = self.bondTo(origin)
            if not bond is None:
                k00 = bond.bondOrder
        k0 = self.atomicNumber
        
        alphabond = list(self.bondNeighbours())
        alphaatom = [bond.linkedto(self) for bond in alphabond]
        k1 = 0 #len(alphabond)
        k2 = 0  #max([val.atomicNumber for val in alphaatom])
        k3 = sum(atom.atomicNumber for atom in alphaatom)
        k4 = max(bond.bondOrder for bond in alphabond)
        
        betabond = list(self.bondNeighbours2())
        betaatom = list(self.neighbours2())
        k5 = 0 #len(betaatom)
        k6 = sum([val.atomicNumber for val in betaatom])
        if k5:
            k7 =  max(bond.bondOrder for bond in betabond)
        else: k7 = 0
        gamma2 = list(self.neighbours3())
        gamma = []
        for bond in gamma2:
            if not bond in gamma:
                gamma.append(bond)
        k8 = len(gamma)
        k9 = sum([val.atomicNumber for val in gamma])
        k10 = sum(self.distances)
        self._priority = k00, k0, k3, k4, k6, k7, k8, k9, k10    #k1, k2, k5, 
        return self._priority
    
    def equivalent(self, target, excluded=[]):
        if self == target:
            return True
        if (not isinstance(target, SmiToken) or
            not self.symbol == target.symbol or
            not len(self.cbonds) == len(target.cbonds)):
            return False
        sdiclist = self.groupedNeigbours(excluded=excluded)
        tdiclist = target.groupedNeigbours(excluded=excluded)
        if len(sdiclist) != len(tdiclist):
            return False
#         sdiclist = self.groupedNeigbours(excluded=excluded)
#         tdiclist = target.groupedNeigbours(excluded=excluded)
        for key, item in sdiclist.items():
            if not key in tdiclist:
                return False
            targetitem = tdiclist[key] 
            if len(item) != len(targetitem):
                return False
            explored = []
            for tok in item:
                targetlist = [tval for tval in targetitem if not tval in explored]
                
                for toktarget in targetlist:
                    newexcluded = excluded[:]
                    newexcluded.extend([self, target])
                    res = tok.equivalent(toktarget, excluded=newexcluded)
                    res = res and (self.getBondTo(tok).bondType == target.getBondTo(toktarget).bondType)
                    if res:
                        explored.append(toktarget)
                        break
                
                if not res:
                    return False
        return True
        
def _12absolute(value, parity):
    if parity:
        return value
    return (3 -((2 * value) - 3)) // 2
    
def keyForChiral(tok):
    return tok.getPriority()

def keyForRing(origin, bond):
    return bond.keyForRing(origin, True, False, False)
#         
def atomCompare(tok1, tok2):
    return tok1.compareForChiral(tok2)

def inversionCount(p1, p2):
    '''
    Using algorithm from http://stackoverflow.com/questions/337664/counting-inversions-in-an-array/6424847#6424847
    But substituting Pythons in-built TimSort.
    p1 and p2 must be shuffle of each other.'''

    a = list(p1)
    b = list(p2)
    inversions = 0
    while a:
        first = a.pop(0)
        inversions += b.index(first)
        b.remove(first)
    return inversions

def equalParity(p1, p2):
    return not bool(inversionCount(p1, p2) % 2)

#--------------------------------------------------------------------------
if __name__ == "__main__":
    pass
    
    #print SmiToken.__doc__
    #print equalParity([5,3,10,7], [7,5,10,3])   
    #print equalParity([5,10,3,7], [7,5,10,3])
