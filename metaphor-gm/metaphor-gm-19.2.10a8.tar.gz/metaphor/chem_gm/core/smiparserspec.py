# -*- coding: ISO-8859-15 -*-
# $Id: smiparserspec.py 4238 2016-09-27 11:27:39Z jeanluc $
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
# from boto import exception
'''
Created on 25 febrr. 2015
use SMILES specification in "opensmiles.org"

@author: jeanluc
'''
# A CFG for SMILES.  Uses Ply 
#   http://www.dabeaz.com/ply/ply.html

# Written by Andrew Dalke <dalke@dalkescientific.com>
# 2 October 2007, Gothenburg, Sweden
# and released into the public domain.

# Partially rewritten by Jean-Luc Ploix, 23 february 2015
# adapted to the Graph Machine use.

from .smitokens import SmiToken
from .import smilexer
from .smilexer import tokens#, _bond_types
from .bonds import bondTypeFromSymbol, SINGLE_BOND

verbose = 0
#setH = 1

######## Utilities

def last_atom(p):
    #ll = len(p)
    #for ind in range(ll):
    #    index = ll - 1 - ind
    for index in range(len(p)-1, -1, -1):
        if p[index][0] in ['ATOM', 'ORGANIC']:
            return p[index]

def getTok(p, ind):
    try:
        tok = p[ind]
        return tok
    except:
        return None

def preceedingtokens(p):
    result = []
    ind = -1
    test = getTok(p, ind)
    while test:
        if isinstance(test, tuple):
            result.append(test)
        elif isinstance(test, list):
            result.extend(test)
        ind -= 1
        test = getTok(p, ind)
    return result

def ruler(st=""):
    print("0123456789012345678901234567890123456789012345678901234567890")
    print("0         1         2         3         4         5         6")
    if st: print(st)

######## The grammar rules

# Consider "" as a valid SMILES string
def p_smiles(p):
    """smiles : chain
              | empty
              """
    p[0] = p[1]

def p_empty(p):
    'empty :'
    p[0] = []

def p_branch_with_bond(p):
    "branch : OPEN BOND chain CLOSE"
    if verbose > 1:
        print(p.lexer.lineno, "branch_with_bond", p[:])
#     ql, iso = p[2]
#     iso2 = 2 if iso == -1 else iso
        
    p[0] = [("BRANCH", [("BOND", p[2])] + p[3])]

def p_branch(p):
    "branch : OPEN chain CLOSE"
    if verbose > 1:
        print(p.lexer.lineno, "branch", p[:])
    p[0] = [("BRANCH", p[2])]

def p_branch_with_dot(p):
    "branch : OPEN DOT chain CLOSE"
    p[0] = [("BRANCH", [("DOT",)] + p[3])]


# A "chain" is a list of 1 or more "connected_atom"s.
#   The "connection" is a bond or a dot.

def p_chain_start(p):
    "chain : connected_atom"
    if verbose > 1:
        print(p.lexer.lineno, "chain_start", p[:])
    p[0] = p[1]

def p_chain_implicit_bond(p):
    "chain : chain connected_atom"
    if verbose > 1:
        print(p.lexer.lineno, "chain_implicit_bond", p[:])
    curSmiToken = p[2][0][1]
    last = last_atom(p[1])
    if last and last[1]:
        message = "implicit bond" if verbose else ""
        target = last[1]
        if target.numero < curSmiToken.numero:
            indexself = 0
        else:
            indexself = -1
        #curSmiToken.setbondto(target, selfindex=indexself, message=message)
        curSmiToken.setcbondto(target, index=indexself, message=message)
    p[0] = p[1] + p[2]

def p_chain_explicit_bond(p):
    "chain : chain BOND connected_atom"
    if verbose > 1:
        print(p.lexer.lineno, "chain_explicit_bond", p[:])
    # nb de liaisons, valeur isomerie
    bondtype, iso = p[2]
    curSmiToken = p[3][0][1]
    last = last_atom(p[1])
    target = last[1]
    if iso:
        target._iso = 2 if iso == -1 else iso
        target._rawiso = iso
        if curSmiToken:
            curSmiToken._rawiso = iso
            curSmiToken._iso = target._iso
        else:
            target._isolatediso = 1
    message = "explicit bond" if verbose else ""
    index = 0 if target.numero < curSmiToken.numero else -1

    curSmiToken.setcbondto(target, index=index, iso=iso, bondtype=bondtype, message=message)
    
    p[0] = p[1] + [("BOND", p[2])] + p[3]

def p_chain_dot_disconnect(p):
    "chain : chain DOT connected_atom"
    p[0] = p[1] + [("DOT",)] + p[3]

# An "atom" is an atom in [] or an ORGANIC
# A "ringed_atom" is an atom followed by 1 or more ring connections
# A "branched_atom" is an atom or ringed_atom followed by one or more branches
# A "connected_atom" is any of an atom, ringed_atom, or branched_atom
def p_connected_atom(p):
#     """connected_atom : branched_atom
#                       | ringed_atom
#                       | atom """
    """connected_atom : atom
                      | ringed_atom
                      | branched_atom"""
                      
    if verbose > 1:
        print(p.lexer.lineno, "connected_atom", p[:])
    p[0] = p[1]

def p_branched_atom(p):  # OK
    """branched_atom : atom branch
                     | ringed_atom branch
                     | branched_atom branch """
    if verbose > 1:
        print(p.lexer.lineno, "branched_atom", p[:])
    message = "branched atom" if verbose else ""
    curSmiTok = p[1][0][1]
    for tok in p[2]:
        if tok and tok[1]:
            target = tok[1][0][1]
            if target and not isinstance(target, SmiToken):
                # cas des branches avec bnond explicite
                ql, iso = target
                target = tok[1][1][1]
            else:
                ql, iso = 1, 0
            target.setcbondto(curSmiTok, index=0, bondtype=ql, iso=iso, 
                    message=message)
            # target est la tete de branche
            if iso:
                target._rawiso = iso
                curSmiTok._rawiso = iso
    p[0] = p[1] + p[2]

def p_ringed_atom(p): # OK
    """ringed_atom : atom RNUM
                   | ringed_atom RNUM 
                   | branched_atom RNUM """
    if verbose > 1:
        print(p.lexer.lineno, "ringed_atom", p[:])
    if len(p) == 3:
        try:
            dct = p.lexer.tokringdict
        except AttributeError:
            p.lexer.tokringdict = {}
            dct = p.lexer.tokringdict
        curSmiToken = p[1][0][1]
        linkstr, bindex = p[2]    
        if not bindex in dct:
            message = "ringed atom 1" if verbose else ""
            dct[bindex] = curSmiToken #p[1][0][1]
            bondtype = bondTypeFromSymbol[linkstr]
            curSmiToken.setcbondto(closure=bindex, bondtype=bondtype, message=message)
        else:
            candidate = dct.pop(bindex)
            try:
                message = "ringed atom 2" if verbose else ""
                curSmiToken.setcbondto(candidate, closure=bindex, message=message)
            except: 
                raise
        p[0] = p[1] + [("RING", p[2])]
    
# The full combinitorics.
def p_atom(p):
    """atom : BEGIN_ATOM         SYMBOL                            END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL                            END_ATOM
            | BEGIN_ATOM         SYMBOL CHIRAL                     END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL CHIRAL                     END_ATOM
            | BEGIN_ATOM         SYMBOL        HCOUNT              END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL        HCOUNT              END_ATOM
            | BEGIN_ATOM         SYMBOL CHIRAL HCOUNT              END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL CHIRAL HCOUNT              END_ATOM
            | BEGIN_ATOM         SYMBOL               CHARGE       END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL               CHARGE       END_ATOM
            | BEGIN_ATOM         SYMBOL CHIRAL        CHARGE       END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL CHIRAL        CHARGE       END_ATOM
            | BEGIN_ATOM         SYMBOL        HCOUNT CHARGE       END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL        HCOUNT CHARGE       END_ATOM
            | BEGIN_ATOM         SYMBOL CHIRAL HCOUNT CHARGE       END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL CHIRAL HCOUNT CHARGE       END_ATOM
            | BEGIN_ATOM         SYMBOL                      CLASS END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL                      CLASS END_ATOM
            | BEGIN_ATOM         SYMBOL CHIRAL               CLASS END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL CHIRAL               CLASS END_ATOM
            | BEGIN_ATOM         SYMBOL        HCOUNT        CLASS END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL        HCOUNT        CLASS END_ATOM
            | BEGIN_ATOM         SYMBOL CHIRAL HCOUNT        CLASS END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL CHIRAL HCOUNT        CLASS END_ATOM
            | BEGIN_ATOM         SYMBOL               CHARGE CLASS END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL               CHARGE CLASS END_ATOM
            | BEGIN_ATOM         SYMBOL CHIRAL        CHARGE CLASS END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL CHIRAL        CHARGE CLASS END_ATOM
            | BEGIN_ATOM         SYMBOL        HCOUNT CHARGE CLASS END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL        HCOUNT CHARGE CLASS END_ATOM
            | BEGIN_ATOM         SYMBOL CHIRAL HCOUNT CHARGE CLASS END_ATOM
            | BEGIN_ATOM ISOTOPE SYMBOL CHIRAL HCOUNT CHARGE CLASS END_ATOM"""
    try:
        pi = p[2:len(p)-1]
    except:
        pi = [pp for pp in range(2, len(p))]
        #p.slice[2:len(p)-1]
    chiral = charge = mass = hcount = 0
    applidata = None
    tlen = 2
    for tok in pi:
        try:
            tok = tok.value  # python 3.x
        except AttributeError: pass  # Python 2.x
        if tok[0] == "SYMBOL":
            symbol = tok[1]
            tlen += len(symbol)
        elif tok[0] == "CHIRAL":
            chiral = tok[2]
            tlen += chiral
        elif tok[0] == "ISOTOPE":
            mass = int(tok[1])
            tlen += len(tok[1])
        elif tok[0] == "HCOUNT":
            hcount = tok[1]
            tlen += tok[1]
        elif tok[0] == "CHARGE":
            charge = tok[1]
            if charge == 1:
                tlen += 1
            elif charge > 1:
                tlen += 2
        elif tok[0] == "CLASS":
            applidata = tok[1]
            tlen += 2
    numero = p.lexer.lineno - 1
    index = p.lexer.lexpos - tlen
    if verbose > 1:
        print(numero, "atom", pi)
    #if (symbol != "H") or setH:
    if symbol == "H":
        hcount = 1 # le 17/09/15
    tok = SmiToken(p.lexer.MetaMolecule, numero, symbol, index=index, 
        chiral=chiral, charge=charge, mass=mass, hcount=hcount, 
        applidata=applidata)
    p.lexer.MetaMolecule.append(tok)
    p[0] = [("ATOM", tok)]
    p.lexer.lineno += 1
#     else:
#         # pour l'hydrogene, pas de creation de SmiToken
#         if chiral or charge or mass or hcount or applidata:
#             raise SyntaxError()
#         p[0] = [("ATOM", None)]
    #p[0] = [("ATOM", p[2:len(p)-1], tok)]

def p_organic_atom(p):
    """atom : ORGANIC"""
    if verbose > 1:
        print(p.lexer.lineno, "organic_atom", p[:])
    symbol = p[1]
    if 1:#symbol != "H":
        numero = p.lexer.lineno-1
        index=p.lexer.lexpos-len(p)
        tok = SmiToken(p.lexer.MetaMolecule, numero, symbol, index=index)
        p.lexer.MetaMolecule.append(tok)
        p.lexer.lineno += 1
        p[0] = [("ORGANIC", tok)]
    else:
        # pour l'hydrogene, pas de creation de SmiToken
        p[0] = [('ORGANIC', None)]
    #p[0] = [("ORGANIC", p[1], tok)]

def p_error(p):
    # For debugging, print a simple ruler
    #print "Syntax error in input!", p
#     st = """Syntax error in input!   
#     position : %d
# %s"""%(p.lexer.lexpos, p.lexer.lexdata)
#     st = ""
    st = "%s;%s;%d;%d;%s" %(p.lexer.lexdata, p.value, p.lexpos, p.lineno, "Parser error")
    raise SyntaxError(st)

######## Presentation functions

def show_SmiList(smilst):
    for smt in smilst:
        print(smt)  
    
def show_grammar(terms, depth=0):
    prefix = "   " * depth
    if not terms: 
        print(prefix, "empty")
        return
    for term in terms:
        if term[0] == "BRANCH":
            print(prefix, "BRANCH:")
            show_grammar(term[1], depth+1)
        else:
            print(prefix, term)

if __name__ == "__main__":
    from ... import monal
    from ...monal.util.utils import appdatadir
    from ... import chem_gm
    from ..components import yacc
    import os
    # compile the lexer
    lexer = smilexer.lex.lex(module=smilexer)
    outputdir = appdatadir("parser", APPNAME="graphmachine", docreate=True)
    picklefile = os.path.join(outputdir, "testsmiparsetab.pyl")
    
    # Used for testing/proving that things work
    data = "C13=C(C2=C(C4=C3C=CC=C4)C=CC=C2)C=CC=C1"
    #data = "O=C1c=C[C@@]2(C)C(CCC3[C@@]2(F)C(O)C[C@@]4(C)C3C[C@H](C)[C@@](O)4[C@](CO)=O)=C1"
    
    data = r"O=C1C=C[C@@]2(C)C(CC[C@]3([H])[C@@]2(F)[C@@H](O)C[C@@]4(C)[C@]([H])3C[C@@H](C)[C@@](O)4[C@](CO)=O)=C1"
    data = r"C1C(C1)C1CCC1C"
    data = "C(N(H)(OCl(=O)(=O)=O)(C1)C)C(C)C1C"
    data = "CSc2ccc1nc(cn1c2)c3ccc(cc3)N(C)[11CH3]"
    data = "[H][C@@](N4CC3)(C[C@@]([C@H](C(O)=O)[C@@H](OC)[C@H](O)C5)([H])[C@@]5([H])C4)C2=C3C1=C(N2)C=C(OC)C=C1"
    data = "c(ccc1)c(c1)[Si](O[Si](OSi2(c(ccc3)cc3)C)(c(ccc4)cc4)C)(O[Si](O2)(c(ccc5)cc5)C)C"
    #data = "CN1C(C2)CCC1CC2OC(\C(C)=C(C)/[H])=O"
    data = "C=CCSb"
    data = "CN1C(C2)CCC1CC2OC(\C(C)=C(C)/[H])=O"
    data = r"[H+].N.[Cl-][Te]1([Cl-])([Cl-])[OH+]CC[OH+]1"
    data = "O[C@H]1[C@@H](C)CCCC1"
    
#    data = r"N.OB1OB(O1)OB2OB(O)O2"
    #data = "CN1C(C2)CCC1CC2OC(\C(C)=C(C)/[H])=O"
    #data = r"CCCCC[C@H](O)/C=C/[C@@H]1[C@H]([14C@@H](O)C[C@H]1O)C\C=C/CCCC(O)=O"
    #data = r"C(CC#C)(Cc1ccccc1)c2cccnc2 Stupidane"
    #data = "C1.c1ccccc1O[12CH2+4]N[C@H]"
    #data = "C1=CC=CC=C1"
    print("data")
    print(data)
    print()
    # A test expression used during development.
    #data = "[CH]C12(O)(P)(B(N)).C=1(C)NO.P1P23B=%92.C(C).[As][238U][CH4+][12C@H][C:1]"
    #data = "c1ccccc1"
    print()
    #print "Parsing"
    #print data
    #print
    yacc.yacc(picklefile=picklefile)
    
    #lex = yacc.load_ply_lex()
    #lexer = lex.lexer
    lexer.MetaMolecule = []

#     par = yacc.parse(data, lexer=lexer)
#     print()
#     #show_grammar(par)
#     print()
#     if par[0][1]:
#         show_SmiList(par[0][1].parent)
    #raise SystemExit("the next part does not work")
