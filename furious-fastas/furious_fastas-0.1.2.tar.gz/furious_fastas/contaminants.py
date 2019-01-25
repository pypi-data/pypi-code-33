"""Get the frequently occurring contaminants.

These reflect the state of hygienne of people in Stefan Tenzer's lab, mostly Rubens'."""

from os.path import join as pjoin, abspath, dirname

from .fastas import Fastas
from .tenzer_contaminants import tenzer_contaminants
from .parse.fastas import parse

# def get_tenzer_contaminants():

#     # path = pjoin(abspath(dirname(__file__)),
#     #              "data/contaminants.fasta")
#     # conts.read(path)
#     # return conts
#     return 

conts = Fastas(parse(tenzer_contaminants))