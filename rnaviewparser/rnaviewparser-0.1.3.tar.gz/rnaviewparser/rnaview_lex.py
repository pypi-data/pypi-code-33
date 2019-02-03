#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 23:16:43 2019

@author: Maria Climent-Pommeret
"""

import ply.lex as lex


tokens = [
    "BPPOSITIONS",
    "POSITION",
    "BASEPAIR",
    "SEPARATOR",
    "STACKED",
    "TYPE",
    "ORIENTATION",
    "SYN",
    "GARBAGE",
    ]

states = [
    ("data", "exclusive"),
    ]

t_ignore_PREAMBLE = r"PDB.*"
t_ignore_UNCOMMON = r"uncommon.*"
t_ignore_CONCLUSION = r"Summary.*"
t_ignore_MULTIPLETSB = r"BEGIN_Multiplets"
t_ignore_STARTNUMBER = r"(\s)*[0-9].+"
t_ignore_STARTSCHAR = r"\s*[A-Z].+"
t_ignore_LINE = "-+"
t_ignore_MULTIPLETSE = r"END_Multiplets"

t_ignore = "\n"


def t_begin_data(t):
    r"BEGIN_base-pair\n"
    t.lexer.push_state("data")

def t_data_end(t):
    r"END_base-pair"
    t.lexer.pop_state()

t_data_ignore = " \t\n\r"

t_data_BPPOSITIONS = r"\d+_\d+,"
t_data_POSITION = r"\d+"
t_data_BASEPAIR = r"[\w]-[\w]"
t_data_SEPARATOR = r"A:"
t_data_STACKED = r"stacked"
t_data_TYPE = r"\+/\+|-/-|[W|H|S|\.]/[W|H|S|\.]"
t_data_ORIENTATION = r"cis|tran"
t_data_SYN = r"syn"
t_data_GARBAGE = r"[X|V|I].*|n.*|\!.*"

def t_error(t):
    """
    Error handling in INITIAL state.
    """
    print("Illegal INITIAL character '%s'" % t.value[0])
    t.lexer.skip(1)

def t_data_error(t):
    """
    Error handling in data state.
    """
    print("Illegal data character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()
