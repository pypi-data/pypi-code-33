from __future__ import division, print_function, absolute_import, unicode_literals
#*****************************************************************
#    pyGSTi 0.9:  Copyright 2015 Sandia Corporation
#    This Software is released under the GPL license detailed
#    in the file "license.txt" in the top-level pyGSTi directory
#*****************************************************************
"""
Variables for working with the a model containing Idle, Z(pi/2) and rot(X=pi/2, Y=sqrt(3)/2) gates.
"""

import sys as _sys
from . import circuitconstruction as _strc
from . import modelconstruction as _setc
from . import stdtarget as _stdtarget


_target_model = _setc.build_explicit_model([('Q0',)], ['Gz','Gn'],
                                [ "Z(pi/2,Q0)", "N(pi/2, sqrt(3)/2, 0, -0.5, Q0)"])


prepStrs = _strc.circuit_list([(),
                                       ('Gn',),
                                       ('Gn','Gn'),
                                       ('Gn','Gz','Gn'),
                                       ('Gn','Gn','Gn',),
                                       ('Gn','Gz','Gn','Gn','Gn')]) # for 1Q MUB

effectStrs = _strc.circuit_list([(),
                                       ('Gn',),
                                       ('Gn','Gn'),
                                       ('Gn','Gz','Gn'),
                                       ('Gn','Gn','Gn',),
                                       ('Gn','Gn','Gn','Gz','Gn')]) # for 1Q MUB

germs = _strc.circuit_list([ ('Gz',),
                                ('Gn',),
                                ('Gz','Gn'),
                                ('Gz','Gz','Gn'),
                                ('Gz','Gn','Gn'),
                                ('Gz','Gz','Gn','Gz','Gn','Gn') ])
germs_lite = germs[:] #same list!


_gscache = { ("full","auto"): _target_model }
def target_model(parameterization_type="full", sim_type="auto"):
    """ 
    Returns a copy of the target model in the given parameterization.

    Parameters
    ----------
    parameterization_type : {"TP", "CPTP", "H+S", "S", ... }
        The gate and SPAM vector parameterization type. See 
        :function:`Model.set_all_parameterizations` for all allowed values.
        
    sim_type : {"auto", "matrix", "map", "termorder:X" }
        The simulator type to be used for model calculations (leave as
        "auto" if you're not sure what this is).
    
    Returns
    -------
    Model
    """
    return _stdtarget._copy_target(_sys.modules[__name__],parameterization_type,
                                   sim_type, _gscache)



global_fidPairs =  [
    (0, 0), (2, 3), (5, 2), (5, 4)]

pergerm_fidPairsDict = {
  ('Gz',): [
        (0, 0), (2, 3), (5, 2), (5, 4)],
  ('Gn',): [
        (0, 0), (2, 3), (5, 2), (5, 4)],
  ('Gz', 'Gn'): [
        (0, 0), (2, 3), (5, 2), (5, 4)],
  ('Gz', 'Gn', 'Gn'): [
        (0, 0), (2, 3), (5, 2), (5, 4)],
  ('Gz', 'Gz', 'Gn'): [
        (0, 0), (2, 3), (5, 2), (5, 4)],
  ('Gz', 'Gz', 'Gn', 'Gz', 'Gn', 'Gn'): [
        (0, 0), (0, 2), (1, 1), (4, 0), (4, 2), (5, 5)],
}


global_fidPairs_lite =  [
    (0, 0), (2, 3), (5, 2), (5, 4)]

pergerm_fidPairsDict_lite = {
  ('Gz',): [
        (0, 0), (2, 3), (5, 2), (5, 4)],
  ('Gn',): [
        (0, 0), (2, 3), (5, 2), (5, 4)],
  ('Gz', 'Gn'): [
        (0, 0), (2, 3), (5, 2), (5, 4)],
  ('Gz', 'Gn', 'Gn'): [
        (0, 0), (2, 3), (5, 2), (5, 4)],
  ('Gz', 'Gz', 'Gn'): [
        (0, 0), (2, 3), (5, 2), (5, 4)],
  ('Gz', 'Gz', 'Gn', 'Gz', 'Gn', 'Gn'): [
        (0, 0), (0, 2), (1, 1), (4, 0), (4, 2), (5, 5)],
}
