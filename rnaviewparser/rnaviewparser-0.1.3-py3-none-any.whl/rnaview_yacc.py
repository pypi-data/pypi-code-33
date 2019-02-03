#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 09:40:06 2019

@author: Maria Climent-Pommeret
"""

import ply.lex as lex
import ply.yacc as yacc

import rnaviewparser.rnaview_ast as ast
from rnaviewparser.rnaview_lex import tokens

def p_relevantdata(p):
    """RelevantData : DataLines"""
    p[0] = ast.RelevantDataNode(p[1])

def p_datalines(p):
    """DataLines : DataLine
                 | DataLines DataLine"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_dataline(p):
    """DataLine : BPPOSITIONS SEPARATOR POSITION BASEPAIR POSITION SEPARATOR TYPE ORIENTATION GARBAGE
                | BPPOSITIONS SEPARATOR POSITION BASEPAIR POSITION SEPARATOR TYPE ORIENTATION SYN GARBAGE
                | BPPOSITIONS SEPARATOR POSITION BASEPAIR POSITION SEPARATOR STACKED"""
    if len(p) > 8:
        p[0] = ast.DataLineNode([
                ast.TypeNode(p[7]),
                ast.OrientationNode(p[8]),
                ast.BPPositionNode(p[1]),
                ast.BasePairNode(p[4]),
                ])
    else:
        p[0] = ast.StackedLine([
                ast.StackedNode(p[7]),
                ast.BPPositionNode(p[1]),
                ast.BasePairNode(p[4]),
                ])

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
