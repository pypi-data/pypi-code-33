'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

This file is part of StruPy.
StruPy structural engineering design Python package.
https://bitbucket.org/struthonteam/strupy

StruPy is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

StruPy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with StruPy; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
'''

import math

import strupy.units as u

'''
Elastic max deflection for bending member
'''

def w_max (M=100.0*u.kNm, L=4.0*u.m, alpha_k=1.0/48, I=300.0*u.cm4,  E=210.0*u.GPa):
    B = E * I
    w_max = alpha_k * M * L**2.0 / B
    return w_max.asUnit(u.mm)

# Test if main
if __name__ == '__main__':
    print ('test element_deflection')
    print w_max()