#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 13:01:33 2019

@author: Maria Climent-Pommeret
"""

import ply.yacc as yacc

from parsetabtolatex.parsetabtolatex_lex import tokens
import parsetabtolatex.parsetabtolatex_ast as AST

def p_relevantdata(p):
    """RelevantData : DataLines"""
    p[0] = AST.RelevantDataNode(p[1])

def p_datalines(p):
    """DataLines : DataLine
                 | DataLines DataLine"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_dataline(p):
    """DataLine : LPAREN GRAMMARRULE RPAREN"""
    p[0] = AST.GrammarRuleNode(p[2])

def p_error(p):
    """
    Error handling.
    """
    if p:
        print("Syntax error at token ", p)
        parser.errok()
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()