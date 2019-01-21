#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SSBJ test case - http://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19980234657.pdf
Original Python implementation for OpenMDAO integration developed by
Sylvain Dubreuil and Remi Lafage of ONERA, the French Aerospace Lab.
Original files taken from: https://github.com/OneraHub/SSBJ-OpenMDAO
The files were adjusted for optimal use in KADMOS by Imco van Gent of TU Delft.
"""
from __future__ import absolute_import, division, print_function

import sys

import numpy as np
from lxml import etree

from kadmos.utilities.xml_utils_openlego import xml_safe_create_element
from openlego.partials.partials import Partials

from ssbjkadmos.config import root_tag, x_tc, x_h, x_M, x_AR, x_Lambda, x_Sref, x_WT, x_ESF, x_Theta, x_CDmin, x_Cf, \
    x_L, x_D, x_fin, x_dpdx
from ssbjkadmos.tools.SsbjDiscipline import SsbjDiscipline
from ssbjkadmos.utils.execution import run_tool
from ssbjkadmos.utils.math import polynomial_function, get_d_dict


class Aerodynamics(SsbjDiscipline):  # AbstractDiscipline

    @property
    def description(self):
        return u'Aerodynamic analysis discipline of the SSBJ test case.'

    @property
    def supplies_partials(self):
        return True

    def generate_input_xml(self):
        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)

        xml_safe_create_element(doc, x_tc, 0.05)
        xml_safe_create_element(doc, x_h, 45000.0)
        xml_safe_create_element(doc, x_M, 1.6)
        xml_safe_create_element(doc, x_AR, 5.5)
        xml_safe_create_element(doc, x_Lambda, 55.0)
        xml_safe_create_element(doc, x_Sref, 1000.0)
        xml_safe_create_element(doc, x_WT, 49909.58578)
        xml_safe_create_element(doc, x_ESF, 1.0)
        xml_safe_create_element(doc, x_Theta, 0.950978)
        xml_safe_create_element(doc, x_CDmin, 0.01375)
        xml_safe_create_element(doc, x_Cf, 0.75)

        return etree.tostring(doc, encoding='utf-8', pretty_print=True, xml_declaration=True)

    def generate_output_xml(self):
        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)

        xml_safe_create_element(doc, x_L, 49909.58578)
        xml_safe_create_element(doc, x_D, 12193.7018)
        xml_safe_create_element(doc, x_fin, 4.093062)
        xml_safe_create_element(doc, x_dpdx, 1.0)

        return etree.tostring(doc, encoding='utf-8', pretty_print=True, xml_declaration=True)

    def generate_partials_xml(self):
        partials = Partials()
        partials.declare_partials(x_L, [x_tc, x_h, x_M, x_AR, x_Lambda, x_Sref, x_WT, x_ESF, x_Theta, x_CDmin, x_Cf])
        partials.declare_partials(x_D, [x_tc, x_h, x_M, x_AR, x_Lambda, x_Sref, x_WT, x_ESF, x_Theta, x_CDmin, x_Cf])
        partials.declare_partials(x_fin, [x_tc, x_h, x_M, x_AR, x_Lambda, x_Sref, x_WT, x_ESF, x_Theta, x_CDmin, x_Cf])
        partials.declare_partials(x_dpdx, [x_tc, x_h, x_M, x_AR, x_Lambda, x_Sref, x_WT, x_ESF, x_Theta, x_CDmin, x_Cf])
        return partials.get_string()

    @staticmethod
    def execute(in_file, out_file):
        doc = etree.parse(in_file)
        z0 = float(doc.xpath(x_tc)[0].text)
        z1 = float(doc.xpath(x_h)[0].text)
        z2 = float(doc.xpath(x_M)[0].text)
        z3 = float(doc.xpath(x_AR)[0].text)
        z4 = float(doc.xpath(x_Lambda)[0].text)
        z5 = float(doc.xpath(x_Sref)[0].text)
        WT = float(doc.xpath(x_WT)[0].text)
        ESF = float(doc.xpath(x_ESF)[0].text)
        Theta = float(doc.xpath(x_Theta)[0].text)
        CDMIN = float(doc.xpath(x_CDmin)[0].text)
        x_aer = float(doc.xpath(x_Cf)[0].text)

        L, D, fin, dpdx = aerodynamics(x_aer, np.array([z0, z1, z2, z3, z4, z5]), WT, ESF, Theta, CDMIN)

        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)
        xml_safe_create_element(doc, x_L, L)
        xml_safe_create_element(doc, x_D, D)
        xml_safe_create_element(doc, x_fin, fin)
        xml_safe_create_element(doc, x_dpdx, dpdx)
        doc.write(out_file, encoding='utf-8', pretty_print=True, xml_declaration=True)

    @staticmethod
    def linearize(in_file, partials_file):
        doc = etree.parse(in_file)
        z0 = float(doc.xpath(x_tc)[0].text)
        z1 = float(doc.xpath(x_h)[0].text)
        z2 = float(doc.xpath(x_M)[0].text)
        z3 = float(doc.xpath(x_AR)[0].text)
        z4 = float(doc.xpath(x_Lambda)[0].text)
        z5 = float(doc.xpath(x_Sref)[0].text)
        WT = float(doc.xpath(x_WT)[0].text)
        ESF = float(doc.xpath(x_ESF)[0].text)
        Theta = float(doc.xpath(x_Theta)[0].text)
        CDMIN = float(doc.xpath(x_CDmin)[0].text)
        x_aer = float(doc.xpath(x_Cf)[0].text)

        # Execute ONERA partials function
        J_L, J_D, J_fin, J_dpdx = aerodynamics_partials(dict(z=np.array([z0, z1, z2, z3, z4, z5]),
                                                             x_aer=x_aer,
                                                             WT=WT, ESF=ESF, Theta=Theta, CDMIN=CDMIN))

        # Declare and write partials
        partials = Partials()
        partials.declare_partials(x_L,
                                  [x_tc, x_h, x_M, x_AR, x_Lambda, x_Sref, x_WT, x_ESF, x_Theta, x_CDmin, x_Cf],
                                  [J_L['z'][0,0],J_L['z'][0,1],J_L['z'][0,2],J_L['z'][0,3],J_L['z'][0,4],J_L['z'][0,5],
                                   J_L['WT'],J_L['ESF'],J_L['Theta'], J_L['CDMIN'], J_L['x_aer']])
        partials.declare_partials(x_D,
                                  [x_tc, x_h, x_M, x_AR, x_Lambda, x_Sref, x_WT, x_ESF, x_Theta, x_CDmin, x_Cf],
                                  [J_D['z'][0, 0], J_D['z'][0, 1], J_D['z'][0, 2], J_D['z'][0, 3], J_D['z'][0, 4],
                                   J_D['z'][0, 5],
                                   J_D['WT'], J_D['ESF'], J_D['Theta'], J_D['CDMIN'], J_D['x_aer']])
        partials.declare_partials(x_fin,
                                  [x_tc, x_h, x_M, x_AR, x_Lambda, x_Sref, x_WT, x_ESF, x_Theta, x_CDmin, x_Cf],
                                  [J_fin['z'][0, 0], J_fin['z'][0, 1], J_fin['z'][0, 2], J_fin['z'][0, 3], J_fin['z'][0, 4],
                                   J_fin['z'][0, 5],
                                   J_fin['WT'], J_fin['ESF'], J_fin['Theta'], J_fin['CDMIN'], J_fin['x_aer']])
        partials.declare_partials(x_dpdx,
                                  [x_tc, x_h, x_M, x_AR, x_Lambda, x_Sref, x_WT, x_ESF, x_Theta, x_CDmin, x_Cf],
                                  [J_dpdx['z'][0, 0], J_dpdx['z'][0, 1], J_dpdx['z'][0, 2], J_dpdx['z'][0, 3], J_dpdx['z'][0, 4],
                                   J_dpdx['z'][0, 5],
                                   J_dpdx['WT'], J_dpdx['ESF'], J_dpdx['Theta'], J_dpdx['CDMIN'], J_dpdx['x_aer']])
        partials.write(partials_file)


def aerodynamics(x_aer, Z, WT, ESF, Theta, CDMIN):
    # Aerodynamics calculation as taken from the ONERA repository
    # Removed "pf" input and added "CDMIN" input
    if Z[1] <= 36089.0:
        V = 1116.39 * Z[2] * np.sqrt(abs(1.0 - 6.875E-6*Z[1]))
        rho = 2.377E-3 * (1. - 6.875E-6*Z[1])**4.2561
    else:
        V = 968.1 * abs(Z[2])
        rho = 2.377E-3 * 0.2971 * np.exp((36089.0 - Z[1]) / 20806.7)
    CL = WT / (0.5*rho*(V**2)*Z[5])
    Fo2 = polynomial_function([ESF, abs(x_aer)], [1, 1], [.25]*2, "Fo2")

    CDmin = CDMIN*Fo2 + 3.05*abs(Z[0])**(5.0/3.0) \
            * abs(np.cos(Z[4]*np.pi/180.0))**1.5
    if Z[2] >= 1:
        k = abs(Z[3]) * (abs(Z[2])**2-1.0) * np.cos(Z[4]*np.pi/180.) \
        / (4.* abs(Z[3])* np.sqrt(abs(Z[4]**2 - 1.) - 2.))
    else:
        k = (0.8 * np.pi * abs(Z[3]))**-1

    Fo3 = polynomial_function([Theta], [5], [.25], "Fo3")
    CD = (CDmin + k * CL**2) * Fo3
    D = CD * 0.5 * rho * V**2 * Z[5]
    fin = WT/D
    L = WT
    dpdx = polynomial_function([Z[0]], [1], [.25], "dpdx")

    return L, D, fin, dpdx


def aerodynamics_partials(inputs):
    # Aerodynamics partial calculation from ONERA repository
    # Removed self, J, scalers
    # Replaced pf for polynomial_function
    # Get d dictionary as static value
    Z = inputs['z']
    WT = inputs['WT']
    ESF = inputs['ESF']
    Theta = inputs['Theta']
    CDMIN = inputs['CDMIN']
    pf_d = get_d_dict()

    # auxiliary computations
    if Z[1] <= 36089.0:
        V = 1116.39 * Z[2] * np.sqrt(abs(1.0 - 6.875E-6 * Z[1]))
        rho = 2.377E-3 * (1. - 6.875E-6 * Z[1]) ** 4.2561
    else:
        V = 968.1 * abs(Z[2])
        rho = 2.377E-3 * 0.2971 * np.exp((36089.0 - Z[1]) / 20806.7)
    CL = WT / (0.5 * rho * (V ** 2) * Z[5])
    s_new = [ESF, abs(inputs['x_aer'])]
    Fo2 = polynomial_function(s_new, [1, 1], [.25] * 2, "Fo2")

    CDmin = CDMIN * Fo2 + 3.05 * abs(Z[0]) ** (5.0 / 3.0) \
            * abs(np.cos(Z[4] * np.pi / 180.0)) ** 1.5
    if Z[2] >= 1.:
        k = abs(Z[3]) * (abs(Z[2]) ** 2 - 1.0) * np.cos(Z[4] * np.pi / 180.) \
            / (4. * abs(Z[3]) * np.sqrt(abs(Z[4] ** 2 - 1.) - 2.))
    else:
        k = (0.8 * np.pi * abs(Z[3])) ** -1

    Fo3 = polynomial_function([Theta], [5], [.25], "Fo3")
    CD = (CDmin + k * CL ** 2) * Fo3
    D = CD * 0.5 * rho * V ** 2 * Z[5]

    # dL #################################################################
    J_L = dict()
    J_L['x_aer'] = np.array([[0.0]])
    J_L['z'] = np.zeros((1, 6))
    J_L['WT'] = np.array([[1.0]])
    J_L['Theta'] = np.array([[0.0]])
    J_L['ESF'] = np.array([[0.0]])
    J_L['CDMIN'] = np.array([[0.0]])

    # dD #################################################################
    J_D = dict()
    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [1, 1], [.25] * 2, "Fo2", deriv=True)
    if abs(inputs['x_aer']) / pf_d['Fo2'][1] >= 0.75 and \
            abs(inputs['x_aer']) / pf_d['Fo2'][1] <= 1.25:
        dSCfdCf = 1.0 / pf_d['Fo2'][1]
    else:
        dSCfdCf = 0.0
    dSCfdCf2 = 2.0 * S_shifted[0, 1] * dSCfdCf
    dFo1dCf = Ai[1] * dSCfdCf + 0.5 * Aij[1, 1] * dSCfdCf2 + Aij[0, 1] * S_shifted[0, 1] * dSCfdCf
    dDdCf = 0.5 * rho * V ** 2 * Z[5] * Fo3 * CDMIN * dFo1dCf
    J_D['x_aer'] = np.array([[dDdCf]]).reshape((1, 1))
    dDdtc = 0.5 * rho * V ** 2 * Z[5] * 5.0 / 3.0 * 3.05 * Fo3 * Z[0] ** (2. / 3.) * np.cos(Z[4] * np.pi / 180.) ** (
                3. / 2.)
    if Z[1] <= 36089.0:
        drhodh = 2.377E-3 * 4.2561 * 6.875E-6 * (1. - 6.875E-6 * Z[1]) ** 3.2561
        dVdh = 6.875E-6 * 1116.39 * Z[2] / 2 * (1.0 - 6.875E-6 * Z[1]) ** -0.5
    else:
        drhodh = 2.377E-3 * 0.2971 * (-1.0) / 20806.7 * np.exp((36089.0 - Z[1]) / 20806.7)
        dVdh = 0.0
    dVdh2 = 2.0 * dVdh * V
    dCDdh = -k * Fo3 * CL * WT / (0.5 * Z[5]) * (V ** -2 * rho ** -2 * drhodh + rho ** -1 * V ** -3 * dVdh)
    dDdh = 0.5 * Z[5] * (drhodh * CDmin * V ** 2 + rho * dCDdh * V ** 2 + rho * CDmin * dVdh2)
    if Z[1] <= 36089.0:
        dVdM = 1116.39 * (1.0 - 6.875E-6 * Z[1]) ** -0.5
    else:
        dVdM = 968.1
    if Z[2] >= 1:
        dkdM = abs(Z[3]) * (2.0 * abs(Z[2])) * np.cos(Z[4] * np.pi / 180.) \
               / (4. * abs(Z[3]) * np.sqrt(abs(Z[4] ** 2 - 1.) - 2.))
    else:
        dkdM = 0.0
    dVdM2 = 2.0 * V * dVdM
    dCLdM = -2.0 * WT / (0.5 * Z[5]) * rho ** -1 * V ** -3 * dVdM
    dCDdM = Fo3 * (2.0 * k * CL * dCLdM + CL ** 2 * dkdM)
    dDdM = 0.5 * rho * Z[5] * (CD * dVdM2 + V ** 2 * dCDdM)
    if Z[2] >= 1:
        dkdAR = 0.0
    else:
        dkdAR = -1.0 / (0.8 * np.pi * abs(Z[3]) ** 2)
    dCDdAR = Fo3 * CL ** 2 * dkdAR
    dDdAR = 0.5 * rho * Z[5] * V ** 2 * dCDdAR
    dCDmindLambda = -3.05 * 3.0 / 2.0 * Z[0] ** (5.0 / 3.0) \
                    * np.cos(Z[4] * np.pi / 180.) ** 0.5 * np.pi / 180. * np.sin(Z[4] * np.pi / 180.)
    if Z[2] >= 1:
        u = (Z[2] ** 2 - 1.) * np.cos(Z[4] * np.pi / 180.)
        up = -np.pi / 180.0 * (Z[2] ** 2 - 1.) * np.sin(Z[4] * np.pi / 180.)
        v = 4.0 * np.sqrt(Z[4] ** 2 - 1.0) - 2.0
        vp = 4.0 * Z[4] * (Z[4] ** 2 - 1.0) ** -0.5
        dkdLambda = (up * v - u * vp) / v ** 2
    else:
        dkdLambda = 0.0
    dCDdLambda = Fo3 * (dCDmindLambda + CL ** 2 * dkdLambda)
    dDdLambda = 0.5 * rho * Z[5] * V ** 2 * dCDdLambda
    dCLdSref2 = 2.0 * CL * -WT / (0.5 * rho * V ** 2 * Z[5] ** 2)
    dCDdSref = Fo3 * k * dCLdSref2
    dDdSref = 0.5 * rho * V ** 2 * (CD + Z[5] * dCDdSref)
    J_D['z'] = np.array([np.append(dDdtc, [dDdh,
                                           dDdM,
                                           dDdAR,
                                           dDdLambda,
                                           dDdSref])])
    dDdWT = Fo3 * k * 2.0 * WT / (0.5 * rho * V ** 2 * Z[5])
    dDdCDMIN = Fo3 * 0.5 * rho * V ** 2 * Z[5]
    J_D['WT'] = np.array([[dDdWT]])
    J_D['CDMIN'] = np.array([[dDdCDMIN]])
    S_shifted, Ai, Aij = polynomial_function([Theta], [5], [.25], "Fo3", deriv=True)
    if Theta / pf_d['Fo3'][0] >= 0.75 and Theta / pf_d['Fo3'][0] <= 1.25:
        dSThetadTheta = 1.0 / pf_d['Fo3'][0]
    else:
        dSThetadTheta = 0.0
    dSThetadTheta2 = 2.0 * S_shifted[0, 0] * dSThetadTheta
    dFo3dTheta = Ai[0] * dSThetadTheta + 0.5 * Aij[0, 0] * dSThetadTheta2
    dCDdTheta = dFo3dTheta * (CDmin + k * CL ** 2)
    dDdTheta = 0.5 * rho * V ** 2 * Z[5] * dCDdTheta
    J_D['Theta'] = np.array(
        [[dDdTheta]]).reshape((1, 1))
    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [1, 1], [.25] * 2, "Fo2", deriv=True)
    if ESF / pf_d['Fo2'][0] >= 0.75 and ESF / pf_d['Fo2'][0] <= 1.25:
        dSESFdESF = 1.0 / pf_d['Fo2'][0]
    else:
        dSESFdESF = 0.0
    dSESFdESF2 = 2.0 * S_shifted[0, 0] * dSESFdESF
    dFo2dESF = Ai[0] * dSESFdESF + 0.5 * Aij[0, 0] * dSESFdESF2 \
               + Aij[1, 0] * S_shifted[0, 1] * dSESFdESF
    dCDdESF = Fo3 * CDMIN * dFo2dESF
    dDdESF = 0.5 * rho * V ** 2 * Z[5] * dCDdESF
    J_D['ESF'] = np.array(
        [[dDdESF]]).reshape((1, 1))

    # dpdx ################################################################
    J_dpdx = dict()
    J_dpdx['x_aer'] = np.array([[0.0]])
    J_dpdx['z'] = np.zeros((1, 6))
    S_shifted, Ai, Aij = polynomial_function([Z[0]], [1], [.25], "dpdx", deriv=True)
    if Z[0] / pf_d['dpdx'][0] >= 0.75 and Z[0] / pf_d['dpdx'][0] <= 1.25:
        dStcdtc = 1.0 / pf_d['dpdx'][0]
    else:
        dStcdtc = 0.0
    dStcdtc2 = 2.0 * S_shifted[0, 0] * dStcdtc
    ddpdxdtc = Ai[0] * dStcdtc + 0.5 * Aij[0, 0] * dStcdtc2
    J_dpdx['z'][0, 0] = ddpdxdtc
    J_dpdx['WT'] = np.array([[0.0]])
    J_dpdx['Theta'] = np.array([[0.0]])
    J_dpdx['ESF'] = np.array([[0.0]])
    J_dpdx['CDMIN'] = np.array([[0.0]])

    # dfin ###############################################################
    J_fin = dict()
    J_fin['x_aer'] = np.array([[-dDdCf * WT / D ** 2]]).reshape((1, 1))
    J_fin['z'] = np.array([-J_D['z'][0] * WT/ D ** 2])
    J_fin['WT'] = np.array([[(D - dDdWT * WT) / D ** 2]]).reshape((1, 1))
    J_fin['Theta'] = np.array([[(-dDdTheta * WT) / D ** 2]]).reshape((1, 1))
    J_fin['ESF'] = np.array([[(-dDdESF * WT) / D ** 2]]).reshape((1, 1))
    J_fin['CDMIN'] = np.array([[(-dDdCDMIN * WT) / D ** 2]]).reshape((1, 1))
    return J_L, J_D, J_fin, J_dpdx


if __name__ == "__main__":

    analysis = Aerodynamics()
    run_tool(analysis, sys.argv)
