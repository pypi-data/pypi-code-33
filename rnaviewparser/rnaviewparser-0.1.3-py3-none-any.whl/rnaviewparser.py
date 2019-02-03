#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 19:42:38 2019

@author: Maria Climent-Pommeret
"""

import rnaviewparser.rnaview_yacc as rnaview_yacc

class RnaviewParser:
    """
    A parser for out files of RNAVIEW.

    It uses ply to do the lexing and the parsing and dataclasses to store
    the data.
    """
    def __init__(self, filepath):
        self.filepath = filepath

    def parse(self):
        """
        Parses and returns a BasePairs object.
        """
        with open(self.filepath, "r") as input_file:
            input_data = input_file.read()
            ast_data = rnaview_yacc.parser.parse(input_data)
            real_data = ast_data.rewrite()
            return real_data
