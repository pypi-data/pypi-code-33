# -*- coding: ISO-8859-15 -*-
# $Id: smilexer.py 4238 2016-09-27 11:27:39Z jeanluc $
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

#import components.lex as lex

strict_opensmiles = 1
# Strict OpenSmiles specification follow-up
# if False, extended specification - no "organic subset" 

tokens = ("ISOTOPE",
          "SYMBOL",
          "HCOUNT",
          "CHARGE",
          "CHIRAL",
          "END_ATOM",
          "BEGIN_ATOM",
          "BOND",
          "ORGANIC",
          "OPEN",
          "CLOSE",
          "DOT",
          "CLASS",
          "RNUM")

# Using three lexing states: the default ("INITIAL") is for tokens
# outside of [atoms] in square brackets.  After '[' the state is
# "pre", meaning "before parsing the atomic symbol", whereby the
# state becomes "post" until reaching the ']'.

# There is a different parsing state inside of [] because that's the
# easiest way to distinguish between "123" the atomic weight and "1",
# "2", "3" meaning 3 ring closures.

# Inside of [] there are two different parsing states because "H" is
# both an atomic symbol and the lead character for the implicit
# hydrogen count.

organic_list = [r"Cl?",
                r"Br?",
                r"[cnospNOFPSIH]"]  # organic subset

organic_re = "|".join(organic_list)

atoms_list = [r"C[laroudsemf]?",
              r"Os?",
              r"N[eaibdpos]?",
              r"S[icernbmg]?",
              r"P[drmtboau]?",
              r"H[eofgas]?",
              r"[cnop]",
              r"se?",
              r"as",
              r"A[lrsgutcm]",
              r"B[eraik]?",
              r"D[ys]?",
              r"E[urs]",
              r"F[erm]?",
              r"G[aed]",
              r"I[nr]?",
              r"Kr?",
              r"L[iaur]",
              r"M[gnodt]",
              r"R[buhenafg]",
              r"T[icebmalh]",
              r"[UVW]",
              r"Xe",
              r"Yb?",
              r"Z[nr]"]

atoms_re = "|".join(atoms_list)

symbol_re = atoms_re + r"|\*" 

states = (
    ('pre', 'exclusive'),
    ('post', 'exclusive'),
)

def t_error(t):
    #st = 'Unknown character "%s" in position %d'%(t.value[0], t.lexpos)
    st = "Lexer error: %s; %s; %d; %d" %(t.lexer.lexdata, t.value, t.lexpos, t.lexer.lineno)
    raise SyntaxError(st)
t_pre_error = t_post_error = t_error

#### The section parses the terms inside of []s

def t_BEGIN_ATOM(t):
    r"\["
    t.lexer.begin("pre")
    return t

# First are the terms which are possible before the
# atomic symbol is parsed.

def t_pre_ISOTOPE(t):
    r"\d+"
    t.value = ("ISOTOPE", t.value)
    return t

def t_pre_SYMBOL(t):
    # The terms are written so that C, O, N, S, P, H come
    # first, followed by the aromatics, followed by the remaining
    # elements, then "*".  Terms like "N[eaibdpos]?" are written
    # so that the second letter is in atomic number order: Ne
    # comes before Na.
    # My thought is to match commonly seen elements more quickly.
    # I've not tested to see if it is actually any better.
    t.lexer.begin("post")
    t.value = ("SYMBOL", t.value)
    return t
t_pre_SYMBOL.__doc__ = symbol_re

# Then come the terms which occur after the atomic symbol.

def t_post_HCOUNT(t):
    r"H\d?"
    if t.value == "H":
        hcount = 1
    else:
        hcount = int(t.value[1])
    t.value = ("HCOUNT", hcount)
    return t

_charge_values = {
    "+": 1,
    "++": 2,
    "-": -1,
    "--": -2,
}

def t_post_CHARGE(t):
    r"\+([0-9]|\+)?|-([0-9]|-)?"
    if t.value in _charge_values:
        charge = _charge_values[t.value]
    else:
        charge = int(t.value)
    t.value = ("CHARGE", charge)
    return t

def t_post_CHIRAL(t):
    r"@(@|TH[12]|AL[12]|SP[123]|TB(1[0-9]?|20?|[3-9])|OH(1[0-9]?|2[0-9]?|30?|[4-9]))?"
    if t.value == "@":
        t.value = ("CHIRAL", "TH", 1)
    elif t.value == "@@":
        t.value = ("CHIRAL", "TH", 2)
    else:
        t.value = ("CHIRAL", t.value[:2], int(t.value[2:]))
    return t

def t_post_CLASS(t):
    r":\d+"
    t.value = ("CLASS", t.value[1:])
    return t

def t_post_END_ATOM(t):
    r"\]"
    t.lexer.begin("INITIAL")
    return t

####### 

# These are the atoms in the "organic subset"

def t_ORGANIC(t):
    return t
if strict_opensmiles:
    t_ORGANIC.__doc__ = organic_re
else:
    # JLP modif: option "organic subset" is extended to all atoms
    t_ORGANIC.__doc__ = atoms_re

# open and close branch
t_OPEN = r"\("
t_CLOSE = r"\)"

# I merged the bond and ring closure number terms into
# a single token.  Otherwise I had problems with the
# ambiguity between <BOND> <RNUM> and <BOND> <ATOM> .
# as in C=1 vs. C=C  .  It can't be resolved with a
# single token lookahead.
#
# This solution seemed the easiest way to resolve it,
# though it makes for an ugly pattern.

def t_RNUM(t):
    r"[/\\=#$~-]?(\d|%\d\d)"
    #r"[/\=#$~-]?(\d|%\d\d)"
    N = len(t.value)
    if N == 1:
        t.value = ("imp", int(t.value))
    elif N == 2:
#         val = ord(t.value[0])
#         val2 = int(t.value[1])
#         t.value = (chr(val), val2)
        t.value = t.value[0], int(t.value[1])
    elif N == 3:
        t.value = ("imp", int(t.value[1:]))
    elif N == 4:
        t.value = (t.value[0], int(t.value[2:]))
    else:
        raise AssertionError(t.value)
    return t


# The bond definition must come after t_RNUM.
# The lexer uses first-match-wins, and if the
# order was reversed then the bond would always
# match instead of rnum.
# bond types are tuples. first element represent
# the chemical bond type; secobd element represent
# the cis-trans isomeric state (-1, 0, 1)
_bond_types = {
    "-": (1, 0),
    "=": (2, 0),
    "#": (3, 0),
    "$": (4, 0),
    "/": (1, 1),
    "\\": (1, -1),
    "~": (1.5, 0), # aromatis bond second choice (opensmiles specify ":")
    }

def t_BOND(t):
    r"[/\\=#$~-]"
    t.value = _bond_types[t.value]
    return t

t_DOT = r"\."

#  everything after a whitespace (space or tab)
# This is the common practice, and is specified in the
# original SMILES paper
def t_COMMENT(t):
    r"[ \t](.|\n)*"
    pass

def set_strict_opensmiles(value):
    strict_opensmiles = value
    if value:
        t_ORGANIC.__doc__ = organic_re
        # JLP modif: organic subset is extended to all atoms
    else:
        t_ORGANIC.__doc__ = atoms_re

if __name__ == "__main__":
    from ...monal.util.utils import appdatadir
    from ..components import lex

    outputdir=appdatadir("parser", APPNAME="graphmachine", docreate=True)
     
    # compile the lexer
    lexer = lex.lex(outputdir=outputdir, lextab="smilextab", optimize=0)
     
    data = r"CCCCC[C@H](O)/C=C/[C@@H]1[C@H]([14C@@H](O)C[C@H]1O)C\C=C/CCCC(O)=O"
    data = r"SiC[*]Cl"
    data = "[H+].N.[Cl-][Te]1([Cl-])([Cl-])[OH+]CC[OH+]1"
    #data= "N.OB1OB(O1)OB2OB(O)O2"
    #data = "[CH]C12(O)(P)(B(N)).C=1(C)NO.P1P23B=%92.C(C).[As][238U][CH4+][12C@H][C:15]"
    print("data")
    print(data)
    print()
    result = lexer.input(data)
#     for value in result:
#         print ">>", value
    while 1:
        tok = lexer.token()
        if not tok:
            break
        print(">>", tok)
        
