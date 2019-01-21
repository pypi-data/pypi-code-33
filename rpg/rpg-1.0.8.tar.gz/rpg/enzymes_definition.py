# -*- coding: utf-8 -*-

########################################################################
# Author: Nicolas Maillet                                              #
# Copyright © 2018 Institut Pasteur, Paris.                            #
# See the COPYRIGHT file for details                                   #
#                                                                      #
# This file is part of Rapid Peptide Generator (RPG) software.         #
#                                                                      #
# RPG is free software: you can redistribute it and/or modify          #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or    #
# any later version.                                                   #
#                                                                      #
# RPG is distributed in the hope that it will be useful,               #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public license    #
# along with RPG (LICENSE file).                                       #
# If not, see <http://www.gnu.org/licenses/>.                          #
########################################################################

"""Definition of default enzymes in RPG"""
from rpg import enzyme
from rpg import rule

AVAILABLE_ENZYMES = []

CPT_ENZ = 1

### ENZYMES DELCARATION ###

# Arg-C proteinase
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#ArgC
# RULES: after R
ENZ = []
ENZ.append(rule.Rule(0, "R", True, 1))
ENZYME = enzyme.Enzyme(CPT_ENZ, "Arg-C", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Asp-N Sequencing Grade
# https://france.promega.com/resources/pubhub/using-endoproteinases-asp-n-and-glu-c-to-improve-protein-characterization/
# RULES: before C or D
ENZ = []
ENZ.append(rule.Rule(0, "C", True, 0))
ENZ.append(rule.Rule(0, "D", True, 0))
ENZYME = enzyme.Enzyme(CPT_ENZ, "Asp-N", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# BNPS-Skatole
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#BNPS
# RULES: after W
ENZ = []
ENZ.append(rule.Rule(0, "W", True, 1))
ENZYME = enzyme.Enzyme(CPT_ENZ, "BNPS-Skatole", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Bromelain
# https://www.sigmaaldrich.com/life-science/biochemicals/biochemical-products.html?TablePage=16410479
# RULES: after K, A or Y
ENZ = []
ENZ.append(rule.Rule(0, "K", True, 1))
ENZ.append(rule.Rule(0, "A", True, 1))
ENZ.append(rule.Rule(0, "Y", True, 1))
ENZYME = enzyme.Enzyme(CPT_ENZ, "Bromelain", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Caspase 1
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Casp1
# RULES: cleaves after D if prev1 is H, A or T and prev3 F, W, Y or L.
# Do not cleaves if followed by P, E, D, Q, K or R
ENZ = []

# Cutting rule
AFTER_D = rule.Rule(0, "D", False, 1) # Never cleaves after D, except...

# Exceptions
EXECPT_HD = rule.Rule(-1, "H", False, -1) # Never cleaves after D, preceded by H
EXECPT_AD = rule.Rule(-1, "A", False, -1) # Never cleaves after D, preceded by A
EXECPT_TD = rule.Rule(-1, "T", False, -1) # Never cleaves after D, preceded by T

EXECPT_HATD__F = rule.Rule(-3, "F", True, -1) # Always cleaves after D, preceded by H, A or T, preceded by F
EXECPT_HATD__L = rule.Rule(-3, "L", True, -1) # Always cleaves after D, preceded by H, A or T, preceded by L
EXECPT_HATD__W = rule.Rule(-3, "W", True, -1) # Always cleaves after D, preceded by H, A or T, preceded by W
EXECPT_HATD__Y = rule.Rule(-3, "Y", True, -1) # Always cleaves after D, preceded by H, A or T, preceded by Y

EXECPT_HATD__FLWY_P = rule.Rule(1, "P", False, -1) # Never cleaves after D, preceded by H, A or T, preceded by F, l, W, Y and followed by P
EXECPT_HATD__FLWY_E = rule.Rule(1, "E", False, -1) # Never cleaves after D, preceded by H, A or T, preceded by F, l, W, Y and followed by E
EXECPT_HATD__FLWY_D = rule.Rule(1, "D", False, -1) # Never cleaves after D, preceded by H, A or T, preceded by F, l, W, Y and followed by D
EXECPT_HATD__FLWY_Q = rule.Rule(1, "Q", False, -1) # Never cleaves after D, preceded by H, A or T, preceded by F, l, W, Y and followed by Q
EXECPT_HATD__FLWY_K = rule.Rule(1, "K", False, -1) # Never cleaves after D, preceded by H, A or T, preceded by F, l, W, Y and followed by K
EXECPT_HATD__FLWY_R = rule.Rule(1, "R", False, -1) # Never cleaves after D, preceded by H, A or T, preceded by F, l, W, Y and followed by R

# Add exception to cutting rules: ...followed by PEDQKR
EXECPT_HATD__F.rules.append(EXECPT_HATD__FLWY_P)
EXECPT_HATD__L.rules.append(EXECPT_HATD__FLWY_P)
EXECPT_HATD__W.rules.append(EXECPT_HATD__FLWY_P)
EXECPT_HATD__Y.rules.append(EXECPT_HATD__FLWY_P)

EXECPT_HATD__F.rules.append(EXECPT_HATD__FLWY_E)
EXECPT_HATD__L.rules.append(EXECPT_HATD__FLWY_E)
EXECPT_HATD__W.rules.append(EXECPT_HATD__FLWY_E)
EXECPT_HATD__Y.rules.append(EXECPT_HATD__FLWY_E)

EXECPT_HATD__F.rules.append(EXECPT_HATD__FLWY_D)
EXECPT_HATD__L.rules.append(EXECPT_HATD__FLWY_D)
EXECPT_HATD__W.rules.append(EXECPT_HATD__FLWY_D)
EXECPT_HATD__Y.rules.append(EXECPT_HATD__FLWY_D)

EXECPT_HATD__F.rules.append(EXECPT_HATD__FLWY_Q)
EXECPT_HATD__L.rules.append(EXECPT_HATD__FLWY_Q)
EXECPT_HATD__W.rules.append(EXECPT_HATD__FLWY_Q)
EXECPT_HATD__Y.rules.append(EXECPT_HATD__FLWY_Q)

EXECPT_HATD__F.rules.append(EXECPT_HATD__FLWY_K)
EXECPT_HATD__L.rules.append(EXECPT_HATD__FLWY_K)
EXECPT_HATD__W.rules.append(EXECPT_HATD__FLWY_K)
EXECPT_HATD__Y.rules.append(EXECPT_HATD__FLWY_K)

EXECPT_HATD__F.rules.append(EXECPT_HATD__FLWY_R)
EXECPT_HATD__L.rules.append(EXECPT_HATD__FLWY_R)
EXECPT_HATD__W.rules.append(EXECPT_HATD__FLWY_R)
EXECPT_HATD__Y.rules.append(EXECPT_HATD__FLWY_R)

# Add exception to cutting rules: ...preceded by FLWY
EXECPT_HD.rules.append(EXECPT_HATD__F)
EXECPT_AD.rules.append(EXECPT_HATD__F)
EXECPT_TD.rules.append(EXECPT_HATD__F)

EXECPT_HD.rules.append(EXECPT_HATD__L)
EXECPT_AD.rules.append(EXECPT_HATD__L)
EXECPT_TD.rules.append(EXECPT_HATD__L)

EXECPT_HD.rules.append(EXECPT_HATD__W)
EXECPT_AD.rules.append(EXECPT_HATD__W)
EXECPT_TD.rules.append(EXECPT_HATD__W)

EXECPT_HD.rules.append(EXECPT_HATD__Y)
EXECPT_AD.rules.append(EXECPT_HATD__Y)
EXECPT_TD.rules.append(EXECPT_HATD__Y)

# Add exception to cutting rules
AFTER_D.rules.append(EXECPT_HD)
AFTER_D.rules.append(EXECPT_AD)
AFTER_D.rules.append(EXECPT_TD)

# Add rules to enzyme
ENZ.append(AFTER_D)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Caspase-1", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Caspase 2
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Casp2
# RULES: cleaves after DVAD, or DEHD,.
# Do not cleaves if followed by P, E, D, Q, K or R
ENZ = []

# Cutting rule
AFTER_D = rule.Rule(0, "D", False, 1) # Never cleaves after D, except...

# Exceptions
EXECPT_HD = rule.Rule(-1, "H", False, -1) # Never cleaves after D, preceded by H
EXECPT_AD = rule.Rule(-1, "A", False, -1) # Never cleaves after D, preceded by A

EXECPT_EHD = rule.Rule(-2, "E", False, -1) # Never cleaves after D, preceded by H, preceded by E
EXECPT_VAD = rule.Rule(-2, "V", False, -1) # Never cleaves after D, preceded by A, preceded by V

EXECPT_DXXD = rule.Rule(-3, "D", True, -1) # Always cleaves after D, preceded by H (A), preceded by E (V), preceded by D

EXECPT_P = rule.Rule(1, "P", False, -1) # Never cleaves after D followed by P
EXECPT_E = rule.Rule(1, "E", False, -1) # Never cleaves after D followed by E
EXECPT_D = rule.Rule(1, "D", False, -1) # Never cleaves after D followed by D
EXECPT_Q = rule.Rule(1, "Q", False, -1) # Never cleaves after D followed by Q
EXECPT_K = rule.Rule(1, "K", False, -1) # Never cleaves after D followed by K
EXECPT_R = rule.Rule(1, "R", False, -1) # Never cleaves after D followed by R

# Add exception to cutting rules: ...followed by PEDQKR
EXECPT_DXXD.rules.append(EXECPT_P)
EXECPT_DXXD.rules.append(EXECPT_E)
EXECPT_DXXD.rules.append(EXECPT_D)
EXECPT_DXXD.rules.append(EXECPT_Q)
EXECPT_DXXD.rules.append(EXECPT_K)
EXECPT_DXXD.rules.append(EXECPT_R)

# Add exception to cutting rules: ...preceded by E (V)
EXECPT_EHD.rules.append(EXECPT_DXXD)
EXECPT_VAD.rules.append(EXECPT_DXXD)


EXECPT_HD.rules.append(EXECPT_EHD)
EXECPT_AD.rules.append(EXECPT_VAD)

# Add exception to cutting rules
AFTER_D.rules.append(EXECPT_HD)
AFTER_D.rules.append(EXECPT_AD)

# Add rules to enzyme
ENZ.append(AFTER_D)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Caspase-2", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Caspase 3
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Casp3
# RULES: cleaves after DMQD, or DEVD,.
# Do not cleaves if followed by P, E, D, Q, K or R
ENZ = []

# Cutting rule
AFTER_D = rule.Rule(0, "D", False, 1) # Never cleaves after D, except...

# Exceptions
EXECPT_VD = rule.Rule(-1, "V", False, -1) # Never cleaves after D, preceded by V
EXECPT_QD = rule.Rule(-1, "Q", False, -1) # Never cleaves after D, preceded by Q

EXECPT_EVD = rule.Rule(-2, "E", False, -1) # Never cleaves after D, preceded by V, preceded by E
EXECPT_MQD = rule.Rule(-2, "M", False, -1) # Never cleaves after D, preceded by Q, preceded by M

EXECPT_DXXD = rule.Rule(-3, "D", True, -1) # Always cleaves after D, preceded by H (A), preceded by E (V), preceded by D

EXECPT_P = rule.Rule(1, "P", False, -1) # Never cleaves after D followed by P
EXECPT_E = rule.Rule(1, "E", False, -1) # Never cleaves after D followed by E
EXECPT_D = rule.Rule(1, "D", False, -1) # Never cleaves after D followed by D
EXECPT_Q = rule.Rule(1, "Q", False, -1) # Never cleaves after D followed by Q
EXECPT_K = rule.Rule(1, "K", False, -1) # Never cleaves after D followed by K
EXECPT_R = rule.Rule(1, "R", False, -1) # Never cleaves after D followed by R

# Add exception to cutting rules: ...followed by PEDQKR
EXECPT_DXXD.rules.append(EXECPT_P)
EXECPT_DXXD.rules.append(EXECPT_E)
EXECPT_DXXD.rules.append(EXECPT_D)
EXECPT_DXXD.rules.append(EXECPT_Q)
EXECPT_DXXD.rules.append(EXECPT_K)
EXECPT_DXXD.rules.append(EXECPT_R)

# Add exception to cutting rules: ...preceded by E (V)
EXECPT_EVD.rules.append(EXECPT_DXXD)
EXECPT_MQD.rules.append(EXECPT_DXXD)


EXECPT_VD.rules.append(EXECPT_EVD)
EXECPT_QD.rules.append(EXECPT_MQD)

# Add exception to cutting rules
AFTER_D.rules.append(EXECPT_VD)
AFTER_D.rules.append(EXECPT_QD)

# Add rules to enzyme
ENZ.append(AFTER_D)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Caspase-3", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Caspase 4
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Casp4
# RULES: cleaves after LEVD, or (W/L)EHD,.
# Do not cleaves if followed by P, E, D, Q, K or R
ENZ = []

# Cutting rule
AFTER_D = rule.Rule(0, "D", False, 1) # Never cleaves after D, except...

# Exceptions
EXECPT_VD = rule.Rule(-1, "V", False, -1) # Never cleaves after D, preceded by V
EXECPT_HD = rule.Rule(-1, "H", False, -1) # Never cleaves after D, preceded by H

EXECPT_EVD = rule.Rule(-2, "E", False, -1) # Never cleaves after D, preceded by V, preceded by E
EXECPT_EHD = rule.Rule(-2, "E", False, -1) # Never cleaves after D, preceded by H, preceded by E

EXECPT_LEVD = rule.Rule(-3, "L", True, -1) # Always cleaves after D, preceded by V/H, preceded by E, preceded by L
EXECPT_WEHD = rule.Rule(-3, "W", True, -1) # Always cleaves after D, preceded by H, preceded by E, preceded by W

EXECPT_P = rule.Rule(1, "P", False, -1) # Never cleaves after D followed by P
EXECPT_E = rule.Rule(1, "E", False, -1) # Never cleaves after D followed by E
EXECPT_D = rule.Rule(1, "D", False, -1) # Never cleaves after D followed by D
EXECPT_Q = rule.Rule(1, "Q", False, -1) # Never cleaves after D followed by Q
EXECPT_K = rule.Rule(1, "K", False, -1) # Never cleaves after D followed by K
EXECPT_R = rule.Rule(1, "R", False, -1) # Never cleaves after D followed by R

# Add exception to cutting rules: ...followed by PEDQKR
EXECPT_LEVD.rules.append(EXECPT_P)
EXECPT_LEVD.rules.append(EXECPT_E)
EXECPT_LEVD.rules.append(EXECPT_D)
EXECPT_LEVD.rules.append(EXECPT_Q)
EXECPT_LEVD.rules.append(EXECPT_K)
EXECPT_LEVD.rules.append(EXECPT_R)

EXECPT_WEHD.rules.append(EXECPT_P)
EXECPT_WEHD.rules.append(EXECPT_E)
EXECPT_WEHD.rules.append(EXECPT_D)
EXECPT_WEHD.rules.append(EXECPT_Q)
EXECPT_WEHD.rules.append(EXECPT_K)
EXECPT_WEHD.rules.append(EXECPT_R)

# Add exception to cutting rules: ...preceded by L/W
EXECPT_EVD.rules.append(EXECPT_LEVD)
EXECPT_EHD.rules.append(EXECPT_LEVD)
EXECPT_EHD.rules.append(EXECPT_WEHD)

EXECPT_VD.rules.append(EXECPT_EVD)
EXECPT_HD.rules.append(EXECPT_EHD)

# Add exception to cutting rules
AFTER_D.rules.append(EXECPT_VD)
AFTER_D.rules.append(EXECPT_HD)

# Add rules to enzyme
ENZ.append(AFTER_D)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Caspase-4", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Caspase 5
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Casp5
# RULES: cleaves after (W/L)EHD,
ENZ = []

# Cutting rule
AFTER_D = rule.Rule(0, "D", False, 1) # Never cleaves after D, except...

# Exceptions
EXECPT_HD = rule.Rule(-1, "H", False, -1) # Never cleaves after D, preceded by H

EXECPT_EHD = rule.Rule(-2, "E", False, -1) # Never cleaves after D, preceded by H, preceded by E

EXECPT_LEHD = rule.Rule(-3, "L", True, -1) # Always cleaves after D, preceded by H, preceded by E, preceded by L
EXECPT_WEHD = rule.Rule(-3, "W", True, -1) # Always cleaves after D, preceded by H, preceded by E, preceded by W

# Add exception to cutting rules: ...preceded by L/W
EXECPT_EHD.rules.append(EXECPT_LEHD)
EXECPT_EHD.rules.append(EXECPT_WEHD)

EXECPT_HD.rules.append(EXECPT_EHD)

# Add exception to cutting rules
AFTER_D.rules.append(EXECPT_HD)

# Add rules to enzyme
ENZ.append(AFTER_D)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Caspase-5", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Caspase 6
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Casp6
# RULES: cleaves after VEID, or VEHD,.
# Do not cleaves if followed by P, E, D, Q, K or R
ENZ = []

# Cutting rule
AFTER_D = rule.Rule(0, "D", False, 1) # Never cleaves after D, except...

# Exceptions
EXECPT_ID = rule.Rule(-1, "I", False, -1) # Never cleaves after D, preceded by I
EXECPT_HD = rule.Rule(-1, "H", False, -1) # Never cleaves after D, preceded by H

EXECPT_EID = rule.Rule(-2, "E", False, -1) # Never cleaves after D, preceded by I, preceded by E
EXECPT_EHD = rule.Rule(-2, "E", False, -1) # Never cleaves after D, preceded by H, preceded by E

EXECPT_VEID = rule.Rule(-3, "V", True, -1) # Always cleaves after D, preceded by I, preceded by E, preceded by V
EXECPT_VEHD = rule.Rule(-3, "V", True, -1) # Always cleaves after D, preceded by H, preceded by E, preceded by V

EXECPT_P = rule.Rule(1, "P", False, -1) # Never cleaves after D followed by P
EXECPT_E = rule.Rule(1, "E", False, -1) # Never cleaves after D followed by E
EXECPT_D = rule.Rule(1, "D", False, -1) # Never cleaves after D followed by D
EXECPT_Q = rule.Rule(1, "Q", False, -1) # Never cleaves after D followed by Q
EXECPT_K = rule.Rule(1, "K", False, -1) # Never cleaves after D followed by K
EXECPT_R = rule.Rule(1, "R", False, -1) # Never cleaves after D followed by R

# Add exception to cutting rules: ...followed by PEDQKR
EXECPT_VEID.rules.append(EXECPT_P)
EXECPT_VEID.rules.append(EXECPT_E)
EXECPT_VEID.rules.append(EXECPT_D)
EXECPT_VEID.rules.append(EXECPT_Q)
EXECPT_VEID.rules.append(EXECPT_K)
EXECPT_VEID.rules.append(EXECPT_R)

EXECPT_VEHD.rules.append(EXECPT_P)
EXECPT_VEHD.rules.append(EXECPT_E)
EXECPT_VEHD.rules.append(EXECPT_D)
EXECPT_VEHD.rules.append(EXECPT_Q)
EXECPT_VEHD.rules.append(EXECPT_K)
EXECPT_VEHD.rules.append(EXECPT_R)

# Add exception to cutting rules: ...preceded by L/W
EXECPT_EID.rules.append(EXECPT_VEID)
EXECPT_EHD.rules.append(EXECPT_VEHD)

EXECPT_ID.rules.append(EXECPT_EID)
EXECPT_HD.rules.append(EXECPT_EHD)

# Add exception to cutting rules
AFTER_D.rules.append(EXECPT_ID)
AFTER_D.rules.append(EXECPT_HD)

# Add rules to enzyme
ENZ.append(AFTER_D)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Caspase-6", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Caspase 7
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Casp7
# RULES: cleaves after DEVD,.
# Do not cleaves if followed by P, E, D, Q, K or R
ENZ = []

# Cutting rule
AFTER_D = rule.Rule(0, "D", False, 1) # Never cleaves after D, except...

# Exceptions
EXECPT_VD = rule.Rule(-1, "V", False, -1) # Never cleaves after D, preceded by V

EXECPT_EVD = rule.Rule(-2, "E", False, -1) # Never cleaves after D, preceded by V, preceded by E

EXECPT_DEVD = rule.Rule(-3, "D", True, -1) # Always cleaves after D, preceded by V, preceded by E, preceded by D

EXECPT_P = rule.Rule(1, "P", False, -1) # Never cleaves after D followed by P
EXECPT_E = rule.Rule(1, "E", False, -1) # Never cleaves after D followed by E
EXECPT_D = rule.Rule(1, "D", False, -1) # Never cleaves after D followed by D
EXECPT_Q = rule.Rule(1, "Q", False, -1) # Never cleaves after D followed by Q
EXECPT_K = rule.Rule(1, "K", False, -1) # Never cleaves after D followed by K
EXECPT_R = rule.Rule(1, "R", False, -1) # Never cleaves after D followed by R

# Add exception to cutting rules: ...followed by PEDQKR
EXECPT_DEVD.rules.append(EXECPT_P)
EXECPT_DEVD.rules.append(EXECPT_E)
EXECPT_DEVD.rules.append(EXECPT_D)
EXECPT_DEVD.rules.append(EXECPT_Q)
EXECPT_DEVD.rules.append(EXECPT_K)
EXECPT_DEVD.rules.append(EXECPT_R)

# Add exception to cutting rules: ...preceded by L/W
EXECPT_EVD.rules.append(EXECPT_DEVD)

EXECPT_VD.rules.append(EXECPT_EVD)

# Add exception to cutting rules
AFTER_D.rules.append(EXECPT_VD)

# Add rules to enzyme
ENZ.append(AFTER_D)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Caspase-7", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Caspase 8
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Casp8
# RULES: cleaves after (I/L)ETD,
# Do not cleaves if followed by P, E, D, Q, K or R
ENZ = []

# Cutting rule
AFTER_D = rule.Rule(0, "D", False, 1) # Never cleaves after D, except...

# Exceptions
EXECPT_TD = rule.Rule(-1, "T", False, -1) # Never cleaves after D, preceded by T

EXECPT_ETD = rule.Rule(-2, "E", False, -1) # Never cleaves after D, preceded by T, preceded by E

EXECPT_IETD = rule.Rule(-3, "I", True, -1) # Always cleaves after D, preceded by T, preceded by E, preceded by I
EXECPT_LETD = rule.Rule(-3, "L", True, -1) # Always cleaves after D, preceded by T, preceded by E, preceded by L

EXECPT_P = rule.Rule(1, "P", False, -1) # Never cleaves after D followed by P
EXECPT_E = rule.Rule(1, "E", False, -1) # Never cleaves after D followed by E
EXECPT_D = rule.Rule(1, "D", False, -1) # Never cleaves after D followed by D
EXECPT_Q = rule.Rule(1, "Q", False, -1) # Never cleaves after D followed by Q
EXECPT_K = rule.Rule(1, "K", False, -1) # Never cleaves after D followed by K
EXECPT_R = rule.Rule(1, "R", False, -1) # Never cleaves after D followed by R

# Add exception to cutting rules: ...followed by PEDQKR
EXECPT_IETD.rules.append(EXECPT_P)
EXECPT_IETD.rules.append(EXECPT_E)
EXECPT_IETD.rules.append(EXECPT_D)
EXECPT_IETD.rules.append(EXECPT_Q)
EXECPT_IETD.rules.append(EXECPT_K)
EXECPT_IETD.rules.append(EXECPT_R)

EXECPT_LETD.rules.append(EXECPT_P)
EXECPT_LETD.rules.append(EXECPT_E)
EXECPT_LETD.rules.append(EXECPT_D)
EXECPT_LETD.rules.append(EXECPT_Q)
EXECPT_LETD.rules.append(EXECPT_K)
EXECPT_LETD.rules.append(EXECPT_R)

# Add exception to cutting rules: ...preceded by L/W
EXECPT_ETD.rules.append(EXECPT_IETD)
EXECPT_ETD.rules.append(EXECPT_LETD)

EXECPT_TD.rules.append(EXECPT_ETD)

# Add exception to cutting rules
AFTER_D.rules.append(EXECPT_TD)

# Add rules to enzyme
ENZ.append(AFTER_D)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Caspase-8", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Caspase 9
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Casp9
# RULES: cleaves after LEHD,
ENZ = []

# Cutting rule
AFTER_D = rule.Rule(0, "D", False, 1) # Never cleaves after D, except...

# Exceptions
EXECPT_HD = rule.Rule(-1, "H", False, -1) # Never cleaves after D, preceded by H

EXECPT_EHD = rule.Rule(-2, "E", False, -1) # Never cleaves after D, preceded by H, preceded by E

EXECPT_LEHD = rule.Rule(-3, "L", True, -1) # Always cleaves after D, preceded by H, preceded by E, preceded by L

# Add exception to cutting rules: ...preceded by L/W
EXECPT_EHD.rules.append(EXECPT_LEHD)

EXECPT_HD.rules.append(EXECPT_EHD)

# Add exception to cutting rules
AFTER_D.rules.append(EXECPT_HD)

# Add rules to enzyme
ENZ.append(AFTER_D)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Caspase-9", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Caspase 10
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Casp10
# RULES: cleaves after IEAD,
ENZ = []

# Cutting rule
AFTER_D = rule.Rule(0, "D", False, 1) # Never cleaves after D, except...

# Exceptions
EXECPT_AD = rule.Rule(-1, "A", False, -1) # Never cleaves after D, preceded by A

EXECPT_EAD = rule.Rule(-2, "E", False, -1) # Never cleaves after D, preceded by A, preceded by E

EXECPT_IEAD = rule.Rule(-3, "I", True, -1) # Always cleaves after D, preceded by A, preceded by E, preceded by I

# Add exception to cutting rules: ...preceded by L/W
EXECPT_EAD.rules.append(EXECPT_IEAD)

EXECPT_AD.rules.append(EXECPT_EAD)

# Add exception to cutting rules
AFTER_D.rules.append(EXECPT_AD)

# Add rules to enzyme
ENZ.append(AFTER_D)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Caspase-10", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Chymotrypsin-high specificity
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Chym
# RULES: after F, Y except if next aa is P
# RULES: after W except if next aa is M or P
ENZ = []

# Cutting rules
AFTER_F = rule.Rule(0, "F", True, 1)
AFTER_Y = rule.Rule(0, "Y", True, 1)
AFTER_W = rule.Rule(0, "W", True, 1)

# Exceptions
EXCEPT_P = rule.Rule(1, "P", False, -1) #-1 for unused
EXCEPT_M = rule.Rule(1, "M", False, -1) #-1 for unused

# Add exception to cutting rules
AFTER_F.rules.append(EXCEPT_P)
AFTER_Y.rules.append(EXCEPT_P)
AFTER_W.rules.append(EXCEPT_M)
AFTER_W.rules.append(EXCEPT_P)

# Add rules to enzyme
ENZ.append(AFTER_F)
ENZ.append(AFTER_Y)
ENZ.append(AFTER_W)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Chymotrypsin-high", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Chymotrypsin-low specificity
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Chym
# RULES: after F, L or Y except if next aa is P
# RULES: after W except if next aa is M or P
# RULES: after M except if next aa is P or Y
# RULES: after H except if next aa is D, M, P or W
ENZ = []

# Cutting rules
AFTER_F = rule.Rule(0, "F", True, 1)
AFTER_L = rule.Rule(0, "L", True, 1)
AFTER_Y = rule.Rule(0, "Y", True, 1)
AFTER_W = rule.Rule(0, "W", True, 1)
AFTER_M = rule.Rule(0, "M", True, 1)
AFTER_H = rule.Rule(0, "H", True, 1)

# Exceptions
EXCEPT_D = rule.Rule(1, "D", False, -1) #-1 for unused
EXCEPT_M = rule.Rule(1, "M", False, -1) #-1 for unused
EXCEPT_P = rule.Rule(1, "P", False, -1) #-1 for unused
EXCEPT_Y = rule.Rule(1, "Y", False, -1) #-1 for unused
EXCEPT_W = rule.Rule(1, "W", False, -1) #-1 for unused

# Add exception to cutting rules
AFTER_F.rules.append(EXCEPT_P)
AFTER_L.rules.append(EXCEPT_P)
AFTER_Y.rules.append(EXCEPT_P)
AFTER_W.rules.append(EXCEPT_M)
AFTER_W.rules.append(EXCEPT_P)
AFTER_M.rules.append(EXCEPT_P)
AFTER_M.rules.append(EXCEPT_Y)
AFTER_H.rules.append(EXCEPT_D)
AFTER_H.rules.append(EXCEPT_M)
AFTER_H.rules.append(EXCEPT_P)
AFTER_H.rules.append(EXCEPT_W)

# Add rules to enzyme
ENZ.append(AFTER_F)
ENZ.append(AFTER_L)
ENZ.append(AFTER_Y)
ENZ.append(AFTER_W)
ENZ.append(AFTER_M)
ENZ.append(AFTER_H)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Chymotrypsin-low", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Clostripain
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Clost
# RULES: after R
ENZ = []
ENZ.append(rule.Rule(0, "R", True, 1))
ENZYME = enzyme.Enzyme(CPT_ENZ, "Clostripain", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# CNBr
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#CNBr
# RULES: after M
ENZ = []
ENZ.append(rule.Rule(0, "M", True, 1))
ENZYME = enzyme.Enzyme(CPT_ENZ, "CNBr", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Enterokinase
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Enter
# RULES: after K if preceded by D/E D/E D/E D/E (P5 not in expasy)
ENZ = []
# Cutting rule
AFTER_K = rule.Rule(0, "K", False, 1) # Never cleaves after K, except...

# Exceptions
EXECPT_DK = rule.Rule(-1, "D", False, -1) # Never cleaves after K, preceded by D
EXECPT_EK = rule.Rule(-1, "E", False, -1) # Never cleaves after K, preceded by E

EXECPT_DDK = rule.Rule(-2, "D", False, -1) # Never cleaves after K, preceded by D, preceded by D
EXECPT_DEK = rule.Rule(-2, "D", False, -1) # Never cleaves after K, preceded by E, preceded by D
EXECPT_EDK = rule.Rule(-2, "E", False, -1) # Never cleaves after K, preceded by D, preceded by E
EXECPT_EEK = rule.Rule(-2, "E", False, -1) # Never cleaves after K, preceded by E, preceded by E

EXECPT_DDDK = rule.Rule(-3, "D", False, -1) # Never cleaves after K, preceded by D, preceded by D, preceded by D
EXECPT_DDEK = rule.Rule(-3, "D", False, -1) # Never cleaves after K, preceded by E, preceded by D, preceded by D
EXECPT_DEDK = rule.Rule(-3, "D", False, -1) # Never cleaves after K, preceded by D, preceded by E, preceded by D
EXECPT_DEEK = rule.Rule(-3, "D", False, -1) # Never cleaves after K, preceded by E, preceded by E, preceded by D
EXECPT_EDDK = rule.Rule(-3, "E", False, -1) # Never cleaves after K, preceded by D, preceded by D, preceded by E
EXECPT_EDEK = rule.Rule(-3, "E", False, -1) # Never cleaves after K, preceded by E, preceded by D, preceded by E
EXECPT_EEDK = rule.Rule(-3, "E", False, -1) # Never cleaves after K, preceded by D, preceded by E, preceded by E
EXECPT_EEEK = rule.Rule(-3, "E", False, -1) # Never cleaves after K, preceded by E, preceded by E, preceded by E

# Fifth level
EXECPT_DDDDK = rule.Rule(-4, "D", True, -1) # Always cleaves after K, preceded by D, preceded by D, preceded by D, preceded by D
EXECPT_DDDEK = rule.Rule(-4, "D", True, -1) # Always cleaves after K, preceded by E, preceded by D, preceded by D, preceded by D
EXECPT_DDEDK = rule.Rule(-4, "D", True, -1) # Always cleaves after K, preceded by D, preceded by E, preceded by D, preceded by D
EXECPT_DDEEK = rule.Rule(-4, "D", True, -1) # Always cleaves after K, preceded by E, preceded by E, preceded by D, preceded by D
EXECPT_DEDDK = rule.Rule(-4, "D", True, -1) # Always cleaves after K, preceded by D, preceded by D, preceded by E, preceded by D
EXECPT_DEDEK = rule.Rule(-4, "D", True, -1) # Always cleaves after K, preceded by E, preceded by D, preceded by E, preceded by D
EXECPT_DEEDK = rule.Rule(-4, "D", True, -1) # Always cleaves after K, preceded by D, preceded by E, preceded by E, preceded by D
EXECPT_DEEEK = rule.Rule(-4, "D", True, -1) # Always cleaves after K, preceded by E, preceded by E, preceded by E, preceded by D

EXECPT_EDDDK = rule.Rule(-4, "E", True, -1) # Always cleaves after K, preceded by D, preceded by D, preceded by D, preceded by E
EXECPT_EDDEK = rule.Rule(-4, "E", True, -1) # Always cleaves after K, preceded by E, preceded by D, preceded by D, preceded by E
EXECPT_EDEDK = rule.Rule(-4, "E", True, -1) # Always cleaves after K, preceded by D, preceded by E, preceded by D, preceded by E
EXECPT_EDEEK = rule.Rule(-4, "E", True, -1) # Always cleaves after K, preceded by E, preceded by E, preceded by D, preceded by E
EXECPT_EEDDK = rule.Rule(-4, "E", True, -1) # Always cleaves after K, preceded by D, preceded by D, preceded by E, preceded by E
EXECPT_EEDEK = rule.Rule(-4, "E", True, -1) # Always cleaves after K, preceded by E, preceded by D, preceded by E, preceded by E
EXECPT_EEEDK = rule.Rule(-4, "E", True, -1) # Always cleaves after K, preceded by D, preceded by E, preceded by E, preceded by E
EXECPT_EEEEK = rule.Rule(-4, "E", True, -1) # Always cleaves after K, preceded by E, preceded by E, preceded by E, preceded by E
# Add exception to cutting rules: ...preceded by L/W ICI
EXECPT_DDDK.rules.append(EXECPT_DDDDK)
EXECPT_DDDK.rules.append(EXECPT_EDDDK)
EXECPT_DDEK.rules.append(EXECPT_DDDEK)
EXECPT_DDEK.rules.append(EXECPT_EDDEK)
EXECPT_DEDK.rules.append(EXECPT_DDEDK)
EXECPT_DEDK.rules.append(EXECPT_EDEDK)
EXECPT_DEEK.rules.append(EXECPT_DDEEK)
EXECPT_DEEK.rules.append(EXECPT_EDEEK)

EXECPT_EDDK.rules.append(EXECPT_DEDDK)
EXECPT_EDDK.rules.append(EXECPT_EEDDK)
EXECPT_EDEK.rules.append(EXECPT_DEDEK)
EXECPT_EDEK.rules.append(EXECPT_EEDEK)
EXECPT_EEDK.rules.append(EXECPT_DEEDK)
EXECPT_EEDK.rules.append(EXECPT_EEEDK)
EXECPT_EEEK.rules.append(EXECPT_DEEEK)
EXECPT_EEEK.rules.append(EXECPT_EEEEK)

EXECPT_DDK.rules.append(EXECPT_DDDK)
EXECPT_DDK.rules.append(EXECPT_EDDK)

EXECPT_DEK.rules.append(EXECPT_DDEK)
EXECPT_DEK.rules.append(EXECPT_EDEK)

EXECPT_EDK.rules.append(EXECPT_DEDK)
EXECPT_EDK.rules.append(EXECPT_EEDK)

EXECPT_EEK.rules.append(EXECPT_DEEK)
EXECPT_EEK.rules.append(EXECPT_EEEK)

EXECPT_DK.rules.append(EXECPT_DDK)
EXECPT_DK.rules.append(EXECPT_EDK)

EXECPT_EK.rules.append(EXECPT_DEK)
EXECPT_EK.rules.append(EXECPT_EEK)

# Add exception to cutting rules
AFTER_K.rules.append(EXECPT_DK)
AFTER_K.rules.append(EXECPT_EK)

# Add rules to enzyme
ENZ.append(AFTER_K)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Enterokinase", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Factor Xa
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Xa
# RULES: After R on A/F/I/L/V/W/G/T D/E G R
ENZ = []

# Cutting rules
AFTER_R = rule.Rule(0, "R", False, 1) # Never cleaves after R, except...
# Exceptions
EXCEPT_GR = rule.Rule(-1, "G", False, -1) # Never cleaves after R preceded by G

EXCEPT_DGR = rule.Rule(-2, "D", False, -1) # Never cleaves after R preceded by G, preceded by D
EXCEPT_EGR = rule.Rule(-2, "E", False, -1) # Never cleaves after R preceded by G, preceded by E

#A/F/I/L/V/W/G/T in -3
EXCEPT_AXGR = rule.Rule(-3, "A", True, -1) # Always cleaves after R preceded by G, preceded by X, preceded by A
EXCEPT_FXGR = rule.Rule(-3, "F", True, -1) # Always cleaves after R preceded by G, preceded by X, preceded by F
EXCEPT_IXGR = rule.Rule(-3, "I", True, -1) # Always cleaves after R preceded by G, preceded by X, preceded by I
EXCEPT_LXGR = rule.Rule(-3, "L", True, -1) # Always cleaves after R preceded by G, preceded by X, preceded by L
EXCEPT_VXGR = rule.Rule(-3, "V", True, -1) # Always cleaves after R preceded by G, preceded by X, preceded by V
EXCEPT_WXGR = rule.Rule(-3, "W", True, -1) # Always cleaves after R preceded by G, preceded by X, preceded by W
EXCEPT_GXGR = rule.Rule(-3, "G", True, -1) # Always cleaves after R preceded by G, preceded by X, preceded by G
EXCEPT_TXGR = rule.Rule(-3, "T", True, -1) # Always cleaves after R preceded by G, preceded by X, preceded by T

# Add exception to cutting rules
EXCEPT_DGR.rules.append(EXCEPT_AXGR)
EXCEPT_DGR.rules.append(EXCEPT_FXGR)
EXCEPT_DGR.rules.append(EXCEPT_IXGR)
EXCEPT_DGR.rules.append(EXCEPT_LXGR)
EXCEPT_DGR.rules.append(EXCEPT_VXGR)
EXCEPT_DGR.rules.append(EXCEPT_WXGR)
EXCEPT_DGR.rules.append(EXCEPT_GXGR)
EXCEPT_DGR.rules.append(EXCEPT_TXGR)

EXCEPT_EGR.rules.append(EXCEPT_AXGR)
EXCEPT_EGR.rules.append(EXCEPT_FXGR)
EXCEPT_EGR.rules.append(EXCEPT_IXGR)
EXCEPT_EGR.rules.append(EXCEPT_LXGR)
EXCEPT_EGR.rules.append(EXCEPT_VXGR)
EXCEPT_EGR.rules.append(EXCEPT_WXGR)
EXCEPT_EGR.rules.append(EXCEPT_GXGR)
EXCEPT_EGR.rules.append(EXCEPT_TXGR)

EXCEPT_GR.rules.append(EXCEPT_DGR)
EXCEPT_GR.rules.append(EXCEPT_EGR)

AFTER_R.rules.append(EXCEPT_GR)
ENZ.append(AFTER_R)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Factor-Xa", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Ficin
# https://www.sigmaaldrich.com/life-science/biochemicals/biochemical-products.html?TablePage=16410578
# RULES: cleaves after G/S/E/Y preceded by A/V/I/L/F/Y or W.
ENZ = []

# Cutting rule
AFTER_G = rule.Rule(0, "G", False, 1) # Never cleaves after G, except...
AFTER_S = rule.Rule(0, "S", False, 1) # Never cleaves after S, except...
AFTER_E = rule.Rule(0, "E", False, 1) # Never cleaves after E, except...
AFTER_Y = rule.Rule(0, "Y", False, 1) # Never cleaves after Y, except...

# Exceptions
EXECPT_Ax = rule.Rule(-1, "A", True, -1) # Always cleaves after G/S/E/Y, preceded by A
EXECPT_Vx = rule.Rule(-1, "V", True, -1) # Always cleaves after G/S/E/Y, preceded by V
EXECPT_Ix = rule.Rule(-1, "I", True, -1) # Always cleaves after G/S/E/Y, preceded by I
EXECPT_Lx = rule.Rule(-1, "L", True, -1) # Always cleaves after G/S/E/Y, preceded by L
EXECPT_Fx = rule.Rule(-1, "F", True, -1) # Always cleaves after G/S/E/Y, preceded by F
EXECPT_Yx = rule.Rule(-1, "Y", True, -1) # Always cleaves after G/S/E/Y, preceded by Y
EXECPT_Wx = rule.Rule(-1, "W", True, -1) # Always cleaves after G/S/E/Y, preceded by W

# Add exception to cutting rules
AFTER_G.rules.append(EXECPT_Ax)
AFTER_G.rules.append(EXECPT_Vx)
AFTER_G.rules.append(EXECPT_Ix)
AFTER_G.rules.append(EXECPT_Lx)
AFTER_G.rules.append(EXECPT_Fx)
AFTER_G.rules.append(EXECPT_Yx)
AFTER_G.rules.append(EXECPT_Wx)

AFTER_S.rules.append(EXECPT_Ax)
AFTER_S.rules.append(EXECPT_Vx)
AFTER_S.rules.append(EXECPT_Ix)
AFTER_S.rules.append(EXECPT_Lx)
AFTER_S.rules.append(EXECPT_Fx)
AFTER_S.rules.append(EXECPT_Yx)
AFTER_S.rules.append(EXECPT_Wx)

AFTER_E.rules.append(EXECPT_Ax)
AFTER_E.rules.append(EXECPT_Vx)
AFTER_E.rules.append(EXECPT_Ix)
AFTER_E.rules.append(EXECPT_Lx)
AFTER_E.rules.append(EXECPT_Fx)
AFTER_E.rules.append(EXECPT_Yx)
AFTER_E.rules.append(EXECPT_Wx)

AFTER_Y.rules.append(EXECPT_Ax)
AFTER_Y.rules.append(EXECPT_Vx)
AFTER_Y.rules.append(EXECPT_Ix)
AFTER_Y.rules.append(EXECPT_Lx)
AFTER_Y.rules.append(EXECPT_Fx)
AFTER_Y.rules.append(EXECPT_Yx)
AFTER_Y.rules.append(EXECPT_Wx)


# Add rules to enzyme
ENZ.append(AFTER_G)
ENZ.append(AFTER_S)
ENZ.append(AFTER_E)
ENZ.append(AFTER_Y)
ENZYME = enzyme.Enzyme(CPT_ENZ, "Ficin", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Formic acid
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#HCOOH
# RULES: after D
ENZ = []
ENZ.append(rule.Rule(0, "D", True, 1))
ENZYME = enzyme.Enzyme(CPT_ENZ, "Formic-acid", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Glu-C Sequencing Grade
# https://france.promega.com/resources/pubhub/using-endoproteinases-asp-n-and-glu-c-to-improve-protein-characterization/
# RULES: after D or E
ENZ = []
ENZ.append(rule.Rule(0, "D", True, 1)) # Before in expasy
ENZ.append(rule.Rule(0, "E", True, 1)) # Before in expasy
ENZYME = enzyme.Enzyme(CPT_ENZ, "Glu-C", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Glutamyl endopeptidase
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Glu
# RULES: cleave after E
ENZ = []
ENZ.append(rule.Rule(0, "E", True, 1))
ENZYME = enzyme.Enzyme(CPT_ENZ, "Glutamyl-endopeptidase", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Granzyme B
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#GranB
# RULES: cleaves after IEPD,
ENZ = []

# Cutting rule
AFTER_D = rule.Rule(0, "D", False, 1) # Never cleaves after D, except...

# Exceptions
EXECPT_PD = rule.Rule(-1, "P", False, -1) # Never cleaves after D, preceded by P

EXECPT_EPD = rule.Rule(-2, "E", False, -1) # Never cleaves after D, preceded by P, preceded by E

EXECPT_IEPD = rule.Rule(-3, "I", True, -1) # Always cleaves after D, preceded by P, preceded by E, preceded by I

# Add exception to cutting rules: ...preceded by L/W
EXECPT_EPD.rules.append(EXECPT_IEPD)

EXECPT_PD.rules.append(EXECPT_EPD)

# Add exception to cutting rules
AFTER_D.rules.append(EXECPT_PD)

# Add rules to enzyme
ENZ.append(AFTER_D)
ENZYME = enzyme.Enzyme(CPT_ENZ, "Granzyme-B", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Hydroxylamine (NH2OH)
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Hydro
# RULES: cleaves after N (P1) followed by G (P1')
ENZ = []

# Cutting rule
AFTER_N = rule.Rule(0, "N", False, 1) # Never cleaves after N, except...

# Exceptions
EXECPT_NG = rule.Rule(1, "G", True, -1) # Always cleaves after N, followed by G

# Add exception to cutting rules
AFTER_N.rules.append(EXECPT_NG)

# Add rules to enzyme
ENZ.append(AFTER_N)
ENZYME = enzyme.Enzyme(CPT_ENZ, "Hydroxylamine", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Iodosobenzoic acid
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Iodo
# RULES: cleaves after W (P1)
ENZ = []
# Add rules to enzyme
ENZ.append(rule.Rule(0, "W", True, 1))
ENZYME = enzyme.Enzyme(CPT_ENZ, "Iodosobenzoic-acid", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# LysC
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#LysC
# Cleaves at Lys in position P1
# RULES: after K
ENZ = []
ENZ.append(rule.Rule(0, "K", True, 1))
ENZYME = enzyme.Enzyme(CPT_ENZ, "Lys-C", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# LysN
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#LysN
# Cleaves at Lys in position P1'
# RULES: before K
ENZ = []
ENZ.append(rule.Rule(0, "K", True, 0))
ENZYME = enzyme.Enzyme(CPT_ENZ, "Lys-N", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Neutrophil elastase
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Elast
# RULES: after A or V (P1)
ENZ = []
ENZ.append(rule.Rule(0, "A", True, 1))
ENZ.append(rule.Rule(0, "V", True, 1))
ENZYME = enzyme.Enzyme(CPT_ENZ, "Neutrophil-elastase", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# NTCB +Ni (2-nitro-5-thiocyanobenzoic acid)
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#NTCB
# Cleaves at Cys in position P1'
# RULES: before C
ENZ = []
ENZ.append(rule.Rule(0, "C", True, 0))
ENZYME = enzyme.Enzyme(CPT_ENZ, "NTCB", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Papain
# https://www.sigmaaldrich.com/life-science/biochemicals/biochemical-products.html?TablePage=16410606
# RULES: cleaves after R/K preceded by A/V/I/L/F/Y or W. Do not cleaves if followed by V
ENZ = []

# Cutting rule
AFTER_K = rule.Rule(0, "K", False, 1) # Never cleaves after K, except...
AFTER_R = rule.Rule(0, "R", False, 1) # Never cleaves after R, except...

# Exceptions
EXECPT_Ax = rule.Rule(-1, "A", True, -1) # Always cleaves after K/R, preceded by A
EXECPT_Vx = rule.Rule(-1, "V", True, -1) # Always cleaves after K/R, preceded by V
EXECPT_Ix = rule.Rule(-1, "I", True, -1) # Always cleaves after K/R, preceded by I
EXECPT_Lx = rule.Rule(-1, "L", True, -1) # Always cleaves after K/R, preceded by L
EXECPT_Fx = rule.Rule(-1, "F", True, -1) # Always cleaves after K/R, preceded by F
EXECPT_Yx = rule.Rule(-1, "Y", True, -1) # Always cleaves after K/R, preceded by Y
EXECPT_Wx = rule.Rule(-1, "W", True, -1) # Always cleaves after K/R, preceded by W

EXECPT_xxV = rule.Rule(1, "V", False, -1) # Never cleaves after K/R, preceded by A/V/I/L/F/Y/W, followed by V

# Add exception to cutting rules: ...preceded by L/W
EXECPT_Ax.rules.append(EXECPT_xxV)
EXECPT_Vx.rules.append(EXECPT_xxV)
EXECPT_Ix.rules.append(EXECPT_xxV)
EXECPT_Lx.rules.append(EXECPT_xxV)
EXECPT_Fx.rules.append(EXECPT_xxV)
EXECPT_Yx.rules.append(EXECPT_xxV)
EXECPT_Wx.rules.append(EXECPT_xxV)

# Add exception to cutting rules
AFTER_K.rules.append(EXECPT_Ax)
AFTER_K.rules.append(EXECPT_Vx)
AFTER_K.rules.append(EXECPT_Ix)
AFTER_K.rules.append(EXECPT_Lx)
AFTER_K.rules.append(EXECPT_Fx)
AFTER_K.rules.append(EXECPT_Yx)
AFTER_K.rules.append(EXECPT_Wx)

AFTER_R.rules.append(EXECPT_Ax)
AFTER_R.rules.append(EXECPT_Vx)
AFTER_R.rules.append(EXECPT_Ix)
AFTER_R.rules.append(EXECPT_Lx)
AFTER_R.rules.append(EXECPT_Fx)
AFTER_R.rules.append(EXECPT_Yx)
AFTER_R.rules.append(EXECPT_Wx)

# Add rules to enzyme
ENZ.append(AFTER_K)
ENZ.append(AFTER_R)
ENZYME = enzyme.Enzyme(CPT_ENZ, "Papain", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Pepsin pH 1.3
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Peps
# RULES: before F or L except if next aa is P or prev is R, 2prev is P or 3prev is H, K or R
# RULES: after F or L except if next2 is P or prev is P or 2prev is H, K or R
ENZ = []

# Cutting rules
BEFORE_F = rule.Rule(0, "F", True, 0) # Always cleaves before F, except...
BEFORE_L = rule.Rule(0, "L", True, 0) # Always cleaves before L, except...

AFTER_F = rule.Rule(0, "F", True, 1) # Always cleaves after F, except...
AFTER_L = rule.Rule(0, "L", True, 1) # Always cleaves after L, except...

# Exceptions
EXCEPT_FLP = rule.Rule(1, "P", False, -1) # Never cleaves before F or L followed by P
EXECPT_RFL = rule.Rule(-1, "R", False, -1) # Never cleaves before F or L, preceded by R
EXECPT_P_FL = rule.Rule(-2, "P", False, -1) # Never cleaves before F or L, preceded by P
EXECPT_H__FL = rule.Rule(-3, "H", False, -1) # Never cleaves before F or L, preceded by H
EXECPT_K__FL = rule.Rule(-3, "K", False, -1) # Never cleaves before F or L, preceded by K
EXECPT_R__FL = rule.Rule(-3, "R", False, -1) # Never cleaves before F or L, preceded by R

EXCEPT_FL_P = rule.Rule(2, "P", False, -1) # Never cleaves after F or L followed by P
EXECPT_PFL = rule.Rule(-1, "P", False, -1) # Never cleaves after F or L, preceded by P
EXECPT_H_FL = rule.Rule(-2, "H", False, -1) # Never cleaves after F or L, preceded by H
EXECPT_K_FL = rule.Rule(-2, "K", False, -1) # Never cleaves after F or L, preceded by K
EXECPT_R_FL = rule.Rule(-2, "R", False, -1) # Never cleaves after F or L, preceded by R

# Add exception to cutting rules
BEFORE_F.rules.append(EXCEPT_FLP)
BEFORE_F.rules.append(EXECPT_RFL)
BEFORE_F.rules.append(EXECPT_P_FL)
BEFORE_F.rules.append(EXECPT_H__FL)
BEFORE_F.rules.append(EXECPT_K__FL)
BEFORE_F.rules.append(EXECPT_R__FL)

BEFORE_L.rules.append(EXCEPT_FLP)
BEFORE_L.rules.append(EXECPT_RFL)
BEFORE_L.rules.append(EXECPT_P_FL)
BEFORE_L.rules.append(EXECPT_H__FL)
BEFORE_L.rules.append(EXECPT_K__FL)
BEFORE_L.rules.append(EXECPT_R__FL)

AFTER_F.rules.append(EXCEPT_FL_P)
AFTER_F.rules.append(EXECPT_PFL)
AFTER_F.rules.append(EXECPT_H_FL)
AFTER_F.rules.append(EXECPT_K_FL)
AFTER_F.rules.append(EXECPT_R_FL)

AFTER_L.rules.append(EXCEPT_FL_P)
AFTER_L.rules.append(EXECPT_PFL)
AFTER_L.rules.append(EXECPT_H_FL)
AFTER_L.rules.append(EXECPT_K_FL)
AFTER_L.rules.append(EXECPT_R_FL)

# Add rules to enzyme
ENZ.append(BEFORE_F)
ENZ.append(BEFORE_L)
ENZ.append(AFTER_F)
ENZ.append(AFTER_L)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Pepsin-pH1.3", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Pepsin pH >=2
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Peps
# RULES: before F, L, W or Y except if next aa is P or prev is R, 2prev is P or 3prev is H, K or R
# RULES: after F, L, W or Y except if next2 is P or prev is P or 2prev is H, K or R
ENZ = []

# Cutting rules
BEFORE_F = rule.Rule(0, "F", True, 0) # Always cleaves before F, except...
BEFORE_L = rule.Rule(0, "L", True, 0) # Always cleaves before L, except...
BEFORE_W = rule.Rule(0, "W", True, 0) # Always cleaves before W, except...
BEFORE_Y = rule.Rule(0, "Y", True, 0) # Always cleaves before Y, except...

AFTER_F = rule.Rule(0, "F", True, 1) # Always cleaves after F, except...
AFTER_L = rule.Rule(0, "L", True, 1) # Always cleaves after L, except...
AFTER_W = rule.Rule(0, "W", True, 1) # Always cleaves after W, except...
AFTER_Y = rule.Rule(0, "Y", True, 1) # Always cleaves after Y, except...

# Exceptions
EXCEPT_FLWYP = rule.Rule(1, "P", False, -1) # Never cleaves before F, L, W or Y followed by P
EXECPT_RFLWY = rule.Rule(-1, "R", False, -1) # Never cleaves before F, L, W or Y, preceded by R
EXECPT_P_FLWY = rule.Rule(-2, "P", False, -1) # Never cleaves before F, L, W or Y, preceded by P
EXECPT_H__FLWY = rule.Rule(-3, "H", False, -1) # Never cleaves before F, L, W or Y, preceded by H
EXECPT_K__FLWY = rule.Rule(-3, "K", False, -1) # Never cleaves before F, L, W or Y, preceded by K
EXECPT_R__FLWY = rule.Rule(-3, "R", False, -1) # Never cleaves before F, L, W or Y, preceded by R

EXCEPT_FLWY_P = rule.Rule(2, "P", False, -1) # Never cleaves after F, L, W or Y followed by P
EXECPT_PFLWY = rule.Rule(-1, "P", False, -1) # Never cleaves after F, L, W or Y, preceded by P
EXECPT_H_FLWY = rule.Rule(-2, "H", False, -1) # Never cleaves after F, L, W or Y, preceded by H
EXECPT_K_FLWY = rule.Rule(-2, "K", False, -1) # Never cleaves after F, L, W or Y, preceded by K
EXECPT_R_FLWY = rule.Rule(-2, "R", False, -1) # Never cleaves after F, L, W or Y, preceded by R

# Add exception to cutting rules
BEFORE_F.rules.append(EXCEPT_FLWYP)
BEFORE_F.rules.append(EXECPT_RFLWY)
BEFORE_F.rules.append(EXECPT_P_FLWY)
BEFORE_F.rules.append(EXECPT_H__FLWY)
BEFORE_F.rules.append(EXECPT_K__FLWY)
BEFORE_F.rules.append(EXECPT_R__FLWY)

BEFORE_L.rules.append(EXCEPT_FLWYP)
BEFORE_L.rules.append(EXECPT_RFLWY)
BEFORE_L.rules.append(EXECPT_P_FLWY)
BEFORE_L.rules.append(EXECPT_H__FLWY)
BEFORE_L.rules.append(EXECPT_K__FLWY)
BEFORE_L.rules.append(EXECPT_R__FLWY)

BEFORE_W.rules.append(EXCEPT_FLWYP)
BEFORE_W.rules.append(EXECPT_RFLWY)
BEFORE_W.rules.append(EXECPT_P_FLWY)
BEFORE_W.rules.append(EXECPT_H__FLWY)
BEFORE_W.rules.append(EXECPT_K__FLWY)
BEFORE_W.rules.append(EXECPT_R__FLWY)

BEFORE_Y.rules.append(EXCEPT_FLWYP)
BEFORE_Y.rules.append(EXECPT_RFLWY)
BEFORE_Y.rules.append(EXECPT_P_FLWY)
BEFORE_Y.rules.append(EXECPT_H__FLWY)
BEFORE_Y.rules.append(EXECPT_K__FLWY)
BEFORE_Y.rules.append(EXECPT_R__FLWY)

AFTER_F.rules.append(EXCEPT_FLWY_P)
AFTER_F.rules.append(EXECPT_PFLWY)
AFTER_F.rules.append(EXECPT_H_FLWY)
AFTER_F.rules.append(EXECPT_K_FLWY)
AFTER_F.rules.append(EXECPT_R_FLWY)

AFTER_L.rules.append(EXCEPT_FLWY_P)
AFTER_L.rules.append(EXECPT_PFLWY)
AFTER_L.rules.append(EXECPT_H_FLWY)
AFTER_L.rules.append(EXECPT_K_FLWY)
AFTER_L.rules.append(EXECPT_R_FLWY)

AFTER_W.rules.append(EXCEPT_FLWY_P)
AFTER_W.rules.append(EXECPT_PFLWY)
AFTER_W.rules.append(EXECPT_H_FLWY)
AFTER_W.rules.append(EXECPT_K_FLWY)
AFTER_W.rules.append(EXECPT_R_FLWY)

AFTER_Y.rules.append(EXCEPT_FLWY_P)
AFTER_Y.rules.append(EXECPT_PFLWY)
AFTER_Y.rules.append(EXECPT_H_FLWY)
AFTER_Y.rules.append(EXECPT_K_FLWY)
AFTER_Y.rules.append(EXECPT_R_FLWY)

# Add rules to enzyme
ENZ.append(BEFORE_F)
ENZ.append(BEFORE_L)
ENZ.append(BEFORE_W)
ENZ.append(BEFORE_Y)
ENZ.append(AFTER_F)
ENZ.append(AFTER_L)
ENZ.append(AFTER_W)
ENZ.append(AFTER_Y)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Pepsin-pH>=2", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Proline-endopeptidase
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Pro
# RULES: after P (P1) if preceded by H,K or R in P2 and not followed by another P in P1'
ENZ = []

# Cutting rules
AFTER_P = rule.Rule(0, "P", False, 1) # Never cleaves after P, except...

# Exceptions
EXCEPT_HP = rule.Rule(-1, "H", True, -1) # Always cleaves after P preceded by H
EXCEPT_KP = rule.Rule(-1, "K", True, -1) # Always cleaves after P preceded by K
EXCEPT_RP = rule.Rule(-1, "R", True, -1) # Always cleaves after P preceded by R

EXCEPT_PP = rule.Rule(1, "P", False, -1) # Never cleaves after P followed by P

# Add exception to cutting rules
EXCEPT_HP.rules.append(EXCEPT_PP)
EXCEPT_KP.rules.append(EXCEPT_PP)
EXCEPT_RP.rules.append(EXCEPT_PP)

AFTER_P.rules.append(EXCEPT_HP)
AFTER_P.rules.append(EXCEPT_KP)
AFTER_P.rules.append(EXCEPT_RP)

# Add rules to enzyme
ENZ.append(AFTER_P)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Proline-endopeptidase", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Proteinase K
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#ProtK
# The predominant site of cleavage is the peptide bond adjacent to the carboxyl
# group of aliphatic and aromatic amino acids with blocked alpha amino groups.
# RULES: after F, W, Y, T, E, A, V, L or I (peptidcutter)
ENZ = []
ENZ.append(rule.Rule(0, "F", True, 1))
ENZ.append(rule.Rule(0, "W", True, 1))
ENZ.append(rule.Rule(0, "Y", True, 1))
ENZ.append(rule.Rule(0, "T", True, 1))
ENZ.append(rule.Rule(0, "E", True, 1))
ENZ.append(rule.Rule(0, "A", True, 1))
ENZ.append(rule.Rule(0, "V", True, 1))
ENZ.append(rule.Rule(0, "L", True, 1))
ENZ.append(rule.Rule(0, "I", True, 1))
ENZYME = enzyme.Enzyme(CPT_ENZ, "Proteinase-K", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Staphylococcal peptidase I
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Staph
# RULES: cleaves after E (P1) not preceded by E (P2)
ENZ = []

# Cutting rule
AFTER_E = rule.Rule(0, "E", True, 1) # Always cleaves after E, except...

# Exceptions
EXECPT_EE = rule.Rule(-1, "E", False, -1) # Never cleaves after E, preceded by E

# Add exception to cutting rules
AFTER_E.rules.append(EXECPT_EE)

# Add rules to enzyme
ENZ.append(AFTER_E)
ENZYME = enzyme.Enzyme(CPT_ENZ, "Staphylococcal-peptidase-I", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Thermolysin
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Therm
# RULES: cleaves before A,F,I,L,M or V (P1') not preceded by D or E in P1 and not followed by P in P2'
ENZ = []

# Cutting rule
BEFORE_A = rule.Rule(0, "A", True, 0) # Always cleaves before A, except...
BEFORE_F = rule.Rule(0, "F", True, 0) # Always cleaves before F, except...
BEFORE_I = rule.Rule(0, "I", True, 0) # Always cleaves before I, except...
BEFORE_L = rule.Rule(0, "L", True, 0) # Always cleaves before L, except...
BEFORE_M = rule.Rule(0, "M", True, 0) # Always cleaves before M, except...
BEFORE_V = rule.Rule(0, "V", True, 0) # Always cleaves before V, except...

# Exceptions
EXECPT_xP = rule.Rule(1, "P", False, -1) # Never cleaves before x, followed by P
EXECPT_Dx = rule.Rule(-1, "D", False, -1) # Never cleaves before x, preceded by D
EXECPT_Ex = rule.Rule(-1, "E", False, -1) # Never cleaves before x, preceded by D

# Add exception to cutting rules:
BEFORE_A.rules.append(EXECPT_xP)
BEFORE_A.rules.append(EXECPT_Dx)
BEFORE_A.rules.append(EXECPT_Ex)

BEFORE_F.rules.append(EXECPT_xP)
BEFORE_F.rules.append(EXECPT_Dx)
BEFORE_F.rules.append(EXECPT_Ex)

BEFORE_I.rules.append(EXECPT_xP)
BEFORE_I.rules.append(EXECPT_Dx)
BEFORE_I.rules.append(EXECPT_Ex)

BEFORE_L.rules.append(EXECPT_xP)
BEFORE_L.rules.append(EXECPT_Dx)
BEFORE_L.rules.append(EXECPT_Ex)

BEFORE_M.rules.append(EXECPT_xP)
BEFORE_M.rules.append(EXECPT_Dx)
BEFORE_M.rules.append(EXECPT_Ex)

BEFORE_V.rules.append(EXECPT_xP)
BEFORE_V.rules.append(EXECPT_Dx)
BEFORE_V.rules.append(EXECPT_Ex)

# Add rules to enzyme
ENZ.append(BEFORE_A)
ENZ.append(BEFORE_F)
ENZ.append(BEFORE_I)
ENZ.append(BEFORE_L)
ENZ.append(BEFORE_M)
ENZ.append(BEFORE_V)
ENZYME = enzyme.Enzyme(CPT_ENZ, "Thermolysin", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Thrombin as defined in PeptideCutter
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Throm
# Good to look: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3288055/
# RULES: (G)(R,)(G)
# RULES: (A or F or I or L or V or W or G or T)(A or F or I or L or V or W or G or T)(P)(R,)(not D or E)(not D or E)
ENZ = []

# SIMPLE CASE
# Cutting rules
AFTER_R = rule.Rule(0, "R", False, 1) # Never cleaves after R, except...
# Exceptions
EXCEPT_GR = rule.Rule(-1, "G", False, -1) # Never cleaves after R preceded by G
EXCEPT_GRG = rule.Rule(1, "G", True, -1) # Always cleaves after R preceded by G and followed by G
# Add exception to cutting rules
EXCEPT_GR.rules.append(EXCEPT_GRG)
AFTER_R.rules.append(EXCEPT_GR)

# MUCH COMPLEXE CASE
EXCEPT_PR = rule.Rule(-1, "P", False, -1) # Never cleaves after R preceded by P
#A/F/I/L/V/W/G/T in -2
EXCEPT_APR = rule.Rule(-2, "A", False, -1) # Never cleaves after R preceded by P, preceded by A
EXCEPT_FPR = rule.Rule(-2, "F", False, -1) # Never cleaves after R preceded by P, preceded by F
EXCEPT_IPR = rule.Rule(-2, "I", False, -1) # Never cleaves after R preceded by P, preceded by I
EXCEPT_LPR = rule.Rule(-2, "L", False, -1) # Never cleaves after R preceded by P, preceded by L
EXCEPT_VPR = rule.Rule(-2, "V", False, -1) # Never cleaves after R preceded by P, preceded by V
EXCEPT_WPR = rule.Rule(-2, "W", False, -1) # Never cleaves after R preceded by P, preceded by W
EXCEPT_GPR = rule.Rule(-2, "G", False, -1) # Never cleaves after R preceded by P, preceded by G
EXCEPT_TPR = rule.Rule(-2, "T", False, -1) # Never cleaves after R preceded by P, preceded by T
#A/F/I/L/V/W/G/T in -3
EXCEPT_AXPR = rule.Rule(-3, "A", True, -1) # Always cleaves after R preceded by P, preceded by X, preceded by A
EXCEPT_FXPR = rule.Rule(-3, "F", True, -1) # Always cleaves after R preceded by P, preceded by X, preceded by F
EXCEPT_IXPR = rule.Rule(-3, "I", True, -1) # Always cleaves after R preceded by P, preceded by X, preceded by I
EXCEPT_LXPR = rule.Rule(-3, "L", True, -1) # Always cleaves after R preceded by P, preceded by X, preceded by L
EXCEPT_VXPR = rule.Rule(-3, "V", True, -1) # Always cleaves after R preceded by P, preceded by X, preceded by V
EXCEPT_WXPR = rule.Rule(-3, "W", True, -1) # Always cleaves after R preceded by P, preceded by X, preceded by W
EXCEPT_GXPR = rule.Rule(-3, "G", True, -1) # Always cleaves after R preceded by P, preceded by X, preceded by G
EXCEPT_TXPR = rule.Rule(-3, "T", True, -1) # Always cleaves after R preceded by P, preceded by X, preceded by T
# non acidic in P1
EXCEPT_nD = rule.Rule(1, "D", False, -1) # Never cleaves after R preceded by P, preceded by X, preceded by X, followed by D
EXCEPT_nE = rule.Rule(1, "E", False, -1) # Never cleaves after R preceded by P, preceded by X, preceded by X, followed by E
# non acidic in P2
EXCEPT_nXD = rule.Rule(2, "D", False, -1) # Never cleaves after R preceded by P, preceded by X, preceded by X, followed by X, followed by D
EXCEPT_nXE = rule.Rule(2, "E", False, -1) # Never cleaves after R preceded by P, preceded by X, preceded by X, followed by X, followed by E

# Adding rules and exceptions
EXCEPT_AXPR.rules.append(EXCEPT_nD)
EXCEPT_AXPR.rules.append(EXCEPT_nE)
EXCEPT_FXPR.rules.append(EXCEPT_nD)
EXCEPT_FXPR.rules.append(EXCEPT_nE)
EXCEPT_IXPR.rules.append(EXCEPT_nD)
EXCEPT_IXPR.rules.append(EXCEPT_nE)
EXCEPT_LXPR.rules.append(EXCEPT_nD)
EXCEPT_LXPR.rules.append(EXCEPT_nE)
EXCEPT_VXPR.rules.append(EXCEPT_nD)
EXCEPT_VXPR.rules.append(EXCEPT_nE)
EXCEPT_WXPR.rules.append(EXCEPT_nD)
EXCEPT_WXPR.rules.append(EXCEPT_nE)
EXCEPT_GXPR.rules.append(EXCEPT_nD)
EXCEPT_GXPR.rules.append(EXCEPT_nE)
EXCEPT_TXPR.rules.append(EXCEPT_nD)
EXCEPT_TXPR.rules.append(EXCEPT_nE)

EXCEPT_AXPR.rules.append(EXCEPT_nXD)
EXCEPT_AXPR.rules.append(EXCEPT_nXE)
EXCEPT_FXPR.rules.append(EXCEPT_nXD)
EXCEPT_FXPR.rules.append(EXCEPT_nXE)
EXCEPT_IXPR.rules.append(EXCEPT_nXD)
EXCEPT_IXPR.rules.append(EXCEPT_nXE)
EXCEPT_LXPR.rules.append(EXCEPT_nXD)
EXCEPT_LXPR.rules.append(EXCEPT_nXE)
EXCEPT_VXPR.rules.append(EXCEPT_nXD)
EXCEPT_VXPR.rules.append(EXCEPT_nXE)
EXCEPT_WXPR.rules.append(EXCEPT_nXD)
EXCEPT_WXPR.rules.append(EXCEPT_nXE)
EXCEPT_GXPR.rules.append(EXCEPT_nXD)
EXCEPT_GXPR.rules.append(EXCEPT_nXE)
EXCEPT_TXPR.rules.append(EXCEPT_nXD)
EXCEPT_TXPR.rules.append(EXCEPT_nXE)

EXCEPT_APR.rules.append(EXCEPT_AXPR)
EXCEPT_APR.rules.append(EXCEPT_FXPR)
EXCEPT_APR.rules.append(EXCEPT_IXPR)
EXCEPT_APR.rules.append(EXCEPT_LXPR)
EXCEPT_APR.rules.append(EXCEPT_VXPR)
EXCEPT_APR.rules.append(EXCEPT_WXPR)
EXCEPT_APR.rules.append(EXCEPT_GXPR)
EXCEPT_APR.rules.append(EXCEPT_TXPR)

EXCEPT_FPR.rules.append(EXCEPT_AXPR)
EXCEPT_FPR.rules.append(EXCEPT_FXPR)
EXCEPT_FPR.rules.append(EXCEPT_IXPR)
EXCEPT_FPR.rules.append(EXCEPT_LXPR)
EXCEPT_FPR.rules.append(EXCEPT_VXPR)
EXCEPT_FPR.rules.append(EXCEPT_WXPR)
EXCEPT_FPR.rules.append(EXCEPT_GXPR)
EXCEPT_FPR.rules.append(EXCEPT_TXPR)

EXCEPT_IPR.rules.append(EXCEPT_AXPR)
EXCEPT_IPR.rules.append(EXCEPT_FXPR)
EXCEPT_IPR.rules.append(EXCEPT_IXPR)
EXCEPT_IPR.rules.append(EXCEPT_LXPR)
EXCEPT_IPR.rules.append(EXCEPT_VXPR)
EXCEPT_IPR.rules.append(EXCEPT_WXPR)
EXCEPT_IPR.rules.append(EXCEPT_GXPR)
EXCEPT_IPR.rules.append(EXCEPT_TXPR)

EXCEPT_LPR.rules.append(EXCEPT_AXPR)
EXCEPT_LPR.rules.append(EXCEPT_FXPR)
EXCEPT_LPR.rules.append(EXCEPT_IXPR)
EXCEPT_LPR.rules.append(EXCEPT_LXPR)
EXCEPT_LPR.rules.append(EXCEPT_VXPR)
EXCEPT_LPR.rules.append(EXCEPT_WXPR)
EXCEPT_LPR.rules.append(EXCEPT_GXPR)
EXCEPT_LPR.rules.append(EXCEPT_TXPR)

EXCEPT_VPR.rules.append(EXCEPT_AXPR)
EXCEPT_VPR.rules.append(EXCEPT_FXPR)
EXCEPT_VPR.rules.append(EXCEPT_IXPR)
EXCEPT_VPR.rules.append(EXCEPT_LXPR)
EXCEPT_VPR.rules.append(EXCEPT_VXPR)
EXCEPT_VPR.rules.append(EXCEPT_WXPR)
EXCEPT_VPR.rules.append(EXCEPT_GXPR)
EXCEPT_VPR.rules.append(EXCEPT_TXPR)

EXCEPT_WPR.rules.append(EXCEPT_AXPR)
EXCEPT_WPR.rules.append(EXCEPT_FXPR)
EXCEPT_WPR.rules.append(EXCEPT_IXPR)
EXCEPT_WPR.rules.append(EXCEPT_LXPR)
EXCEPT_WPR.rules.append(EXCEPT_VXPR)
EXCEPT_WPR.rules.append(EXCEPT_WXPR)
EXCEPT_WPR.rules.append(EXCEPT_GXPR)
EXCEPT_WPR.rules.append(EXCEPT_TXPR)

EXCEPT_GPR.rules.append(EXCEPT_AXPR)
EXCEPT_GPR.rules.append(EXCEPT_FXPR)
EXCEPT_GPR.rules.append(EXCEPT_IXPR)
EXCEPT_GPR.rules.append(EXCEPT_LXPR)
EXCEPT_GPR.rules.append(EXCEPT_VXPR)
EXCEPT_GPR.rules.append(EXCEPT_WXPR)
EXCEPT_GPR.rules.append(EXCEPT_GXPR)
EXCEPT_GPR.rules.append(EXCEPT_TXPR)

EXCEPT_TPR.rules.append(EXCEPT_AXPR)
EXCEPT_TPR.rules.append(EXCEPT_FXPR)
EXCEPT_TPR.rules.append(EXCEPT_IXPR)
EXCEPT_TPR.rules.append(EXCEPT_LXPR)
EXCEPT_TPR.rules.append(EXCEPT_VXPR)
EXCEPT_TPR.rules.append(EXCEPT_WXPR)
EXCEPT_TPR.rules.append(EXCEPT_GXPR)
EXCEPT_TPR.rules.append(EXCEPT_TXPR)

EXCEPT_PR.rules.append(EXCEPT_APR)
EXCEPT_PR.rules.append(EXCEPT_FPR)
EXCEPT_PR.rules.append(EXCEPT_IPR)
EXCEPT_PR.rules.append(EXCEPT_LPR)
EXCEPT_PR.rules.append(EXCEPT_VPR)
EXCEPT_PR.rules.append(EXCEPT_WPR)
EXCEPT_PR.rules.append(EXCEPT_GPR)
EXCEPT_PR.rules.append(EXCEPT_TPR)

AFTER_R.rules.append(EXCEPT_PR)
ENZ.append(AFTER_R)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Thrombin", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Thrombin Sequencing Grade (defined in several kit)
# http://www.merckmillipore.com/FR/fr/life-science-research/protein-sample-preparation/protein-purification/cleavage-enzymes/0Uqb.qB.V5gAAAFBOFJlvyyv,nav#thrombin
# https://www.biovision.com/documentation/datasheets/K377.pdf
# http://www.abcam.com/thrombin-cleavage-kit-ab207000.html
# http://wolfson.huji.ac.il/purification/PDF/Protease_fusion_cleavage/NOVAGEN_Thrombin_kit.pdf
# RULES: After R on LVPR,GS
ENZ = []

# Cutting rules
AFTER_R = rule.Rule(0, "R", False, 1) # Never cleaves after R, except...
# Exceptions
EXCEPT_PR = rule.Rule(-1, "P", False, -1) # Never cleaves after R preceded by P
EXCEPT_VPR = rule.Rule(-2, "V", False, -1) # Never cleaves after R preceded by P, preceded by V
EXCEPT_LVPR = rule.Rule(-3, "L", False, -1) # Never cleaves after R preceded by P, preceded by V, preceded by L
EXCEPT_LVPRG = rule.Rule(1, "G", False, -1) # Never cleaves after R preceded by P, preceded by V, preceded by L, followed by G
EXCEPT_LVPRGS = rule.Rule(2, "S", True, -1) # Always cleaves after R preceded by P, preceded by V, preceded by L, followed by G followed by S

# Add exception to cutting rules
EXCEPT_LVPRG.rules.append(EXCEPT_LVPRGS)
EXCEPT_LVPR.rules.append(EXCEPT_LVPRG)
EXCEPT_VPR.rules.append(EXCEPT_LVPR)
EXCEPT_PR.rules.append(EXCEPT_VPR)
AFTER_R.rules.append(EXCEPT_PR)
ENZ.append(AFTER_R)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Thrombin-SG", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Tobacco etch virus protease
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#TEV
# RULES: cleaves between Q (P1) and G or S in P1' when Y in P3 and E in P6.
# RULES: cleaves after E-Xaa-Xaa-Y-Xaa-Q-(G/S)
ENZ = []

# Cutting rule
AFTER_Q = rule.Rule(0, "Q", False, 1) # Never cleaves after Q, except...

# Exceptions
EXECPT_QG = rule.Rule(1, "G", False, -1) # Never cleaves after Q, followed by G
EXECPT_QS = rule.Rule(1, "S", False, -1) # Never cleaves after Q, followed by S

EXECPT_Y_Qx = rule.Rule(-2, "Y", False, -1) # Never cleaves after Q, followed by G/S, preceded by Y

EXECPT_E__Y_Qx = rule.Rule(-5, "E", True, -1) # Always cleaves after Q, followed by G/S, preceded by Y and preceded by E

# Add exception to cutting rules:
EXECPT_Y_Qx.rules.append(EXECPT_E__Y_Qx)

EXECPT_QG.rules.append(EXECPT_Y_Qx)
EXECPT_QS.rules.append(EXECPT_Y_Qx)

# Add exception to cutting rules
AFTER_Q.rules.append(EXECPT_QG)
AFTER_Q.rules.append(EXECPT_QS)

# Add rules to enzyme
ENZ.append(AFTER_Q)
ENZYME = enzyme.Enzyme(CPT_ENZ, "Tobacco-Etch-Virus", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1



# Trypsin
# https://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html#Tryps
# RULES: after K except if next aa is P. This rule doesn't apply if W is before K
# RULES: after R except if next aa is P. This rule doesn't apply if M is before R
# RULES: don't cleaves CKD, DKD, CKH, CKY, CRK, RRH nor RRR
# Other way to see it: cleaves after K|R except if P after, but cleaves WKP and MRP. Don't cleaves CKD, DKD, CKH, CKY, CRK, RRH nor RRR
ENZ = []

# Cutting rules
AFTER_K = rule.Rule(0, "K", True, 1) # Always cleaves after K, except...
AFTER_R = rule.Rule(0, "R", True, 1) # Always cleaves after R, except...

# Exceptions
EXCEPT_KP = rule.Rule(1, "P", False, -1) # Never cleaves after K followed by P, except...
EXCEPT_KD = rule.Rule(1, "D", True, -1) # Always cleaves after K followed by D, except...
EXCEPT_KH = rule.Rule(1, "H", True, -1) # Always cleaves after K followed by H, except...
EXCEPT_KY = rule.Rule(1, "Y", True, -1) # Always cleaves after K followed by Y, except...

EXCEPT_RP = rule.Rule(1, "P", False, -1) # Never cleaves after R followed by P, except...
EXCEPT_RK = rule.Rule(1, "K", True, -1) # Always cleaves after R followed by K, except...
EXCEPT_RH = rule.Rule(1, "H", True, -1) # Always cleaves after R followed by H, except...
EXCEPT_RR = rule.Rule(1, "R", True, -1) # Always cleaves after R followed by R, except...

# Counter-exceptions
UNEXCEPT_WKP = rule.Rule(-1, "W", True, -1) # Always cleaves after K followed by P and preceded by W
UNEXCEPT_CKD = rule.Rule(-1, "C", False, -1) # Never cleaves after K followed by D and preceded by C
UNEXCEPT_DKD = rule.Rule(-1, "D", False, -1) # Never cleaves after K followed by D and preceded by D
UNEXCEPT_CKH = rule.Rule(-1, "C", False, -1) # Never cleaves after K followed by H and preceded by C
UNEXCEPT_CKY = rule.Rule(-1, "C", False, -1) # Never cleaves after K followed by Y and preceded by C

UNEXCEPT_MRP = rule.Rule(-1, "M", True, -1) # Always cleaves after R followed by P and preceded by M
UNEXCEPT_CRK = rule.Rule(-1, "C", False, -1) # Never cleaves after R followed by K and preceded by C
UNEXCEPT_RRH = rule.Rule(-1, "R", False, -1) # Never cleaves after R followed by H and preceded by R
UNEXCEPT_RRR = rule.Rule(-1, "R", False, -1) # Never cleaves after R followed by R and preceded by R

# Add counter-exceptions to exceptions
EXCEPT_KP.rules.append(UNEXCEPT_WKP)
EXCEPT_KD.rules.append(UNEXCEPT_CKD)
EXCEPT_KD.rules.append(UNEXCEPT_DKD)
EXCEPT_KH.rules.append(UNEXCEPT_CKH)
EXCEPT_KY.rules.append(UNEXCEPT_CKY)

EXCEPT_RP.rules.append(UNEXCEPT_MRP)
EXCEPT_RK.rules.append(UNEXCEPT_CRK)
EXCEPT_RH.rules.append(UNEXCEPT_RRH)
EXCEPT_RR.rules.append(UNEXCEPT_RRR)

# Add exception to cutting rules
AFTER_K.rules.append(EXCEPT_KP)
AFTER_K.rules.append(EXCEPT_KD)
AFTER_K.rules.append(EXCEPT_KH)
AFTER_K.rules.append(EXCEPT_KY)

AFTER_R.rules.append(EXCEPT_RP)
AFTER_R.rules.append(EXCEPT_RK)
AFTER_R.rules.append(EXCEPT_RH)
AFTER_R.rules.append(EXCEPT_RR)

# Add rules to enzyme
ENZ.append(AFTER_K)
ENZ.append(AFTER_R)

ENZYME = enzyme.Enzyme(CPT_ENZ, "Trypsin", ENZ, 0)
# Add it to available enzymes
AVAILABLE_ENZYMES.append(ENZYME)
CPT_ENZ += 1
