#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 11:53:19 2019

@author: Maria Climent-Pommeret
"""

import ply.lex as lex


tokens = [
    "GRAMMARRULE",
    "LPAREN",
    "RPAREN",
    ]

states = [
    ("grammar", "exclusive"),
    ]

t_ignore = "\n"
t_ignore_COMMENT = r"\#.*"
t_ignore_TABVERSION = r"_tabversion.*"
t_ignore_LRMETHOD = r"_lr_method.*"
t_ignore_LRSIGNATURE = r"_lr_signature.*"
t_ignore_SPACES = r"\ +"
t_ignore_CODE = r"[A-Za-z_0-9\\n].*"
t_ignore_LRACTIONS = r"_lr_action.*"
t_ignore_LISTS = r"\[.*"
t_ignore_DEL = r"del.*"
t_ignore_LRGOTO = r"_lr_goto.*"
t_ignore_TEXT = r"[A-Za-z\|\\n]+"

def t_error(t):
    print("Illegal character in INITIAL state '%s'" % t.value[0])
    t.lexer.skip(1)

def t_begin_grammar(t):
    r"_lr_productions\ =\ \["
    t.lexer.push_state("grammar")

def t_grammar_end(t):
    r"\]"
    t.lexer.pop_state()

def t_grammar_error(t):
    print("Illegal character in GRAMMAR state '%s'" % t.value[0])
    t.lexer.skip(1)

t_grammar_ignore = "\n\r\t ,"
t_grammar_GRAMMARRULE = r"(\"|\')[A-Za-z][a-zA-Z0-9_\']*\ ->\ .+?(?=,)"
t_grammar_ignore_QUOTEDGARBAGE = r"(\"|\').+(\"|\')(?=,)"
t_grammar_ignore_NONE = "None"
t_grammar_ignore_NUMBER = r"[0-9]+"
t_grammar_LPAREN = r"\("
t_grammar_RPAREN = r"\)"
lexer = lex.lex()