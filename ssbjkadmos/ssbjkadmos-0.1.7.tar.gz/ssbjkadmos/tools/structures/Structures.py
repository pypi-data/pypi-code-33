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

from openlego.partials.partials import Partials
from ssbjkadmos.config import root_tag, x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, \
    x_L, x_Nz, x_WT, x_WF, x_sigma1, x_sigma2, x_sigma3, x_sigma4, x_sigma5, x_Theta
from ssbjkadmos.tools.SsbjDiscipline import SsbjDiscipline
from ssbjkadmos.utils.math import polynomial_function, get_d_dict
from ssbjkadmos.utils.execution import run_tool
from kadmos.utilities.xml_utils_openlego import xml_safe_create_element


class Structures(SsbjDiscipline):  # AbstractDiscipline

    @property
    def description(self):
        return u'Structural analysis discipline of the SSBJ test case.'

    @property
    def supplies_partials(self):
        return True

    def generate_input_xml(self):
        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)

        xml_safe_create_element(doc, x_tc, 0.05)
        xml_safe_create_element(doc, x_AR, 5.5)
        xml_safe_create_element(doc, x_Lambda, 55.0)
        xml_safe_create_element(doc, x_Sref, 1000.0)
        xml_safe_create_element(doc, x_lambda, 0.25)
        xml_safe_create_element(doc, x_section, 1.0)
        xml_safe_create_element(doc, x_WO, 25000.)
        xml_safe_create_element(doc, x_WE, 5748.915355)
        xml_safe_create_element(doc, x_WFO, 2000.)
        xml_safe_create_element(doc, x_L, 49909.58578)
        xml_safe_create_element(doc, x_Nz, 6.0)

        return etree.tostring(doc, encoding='utf-8', pretty_print=True, xml_declaration=True)

    def generate_output_xml(self):
        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)

        xml_safe_create_element(doc, x_WT, 49909.58578)
        xml_safe_create_element(doc, x_WF, 7306.20261)
        xml_safe_create_element(doc, x_sigma1, 1.12255)
        xml_safe_create_element(doc, x_sigma2, 1.08170213)
        xml_safe_create_element(doc, x_sigma3, 1.0612766)
        xml_safe_create_element(doc, x_sigma4, 1.04902128)
        xml_safe_create_element(doc, x_sigma5, 1.04085106)
        xml_safe_create_element(doc, x_Theta, 0.950978)

        return etree.tostring(doc, encoding='utf-8', pretty_print=True, xml_declaration=True)

    def generate_partials_xml(self):
        partials = Partials()
        partials.declare_partials(x_WT,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz])
        partials.declare_partials(x_WF,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz])
        partials.declare_partials(x_sigma1,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz])
        partials.declare_partials(x_sigma2,
                                  [x_sigma3, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz])
        partials.declare_partials(x_sigma4,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz])
        partials.declare_partials(x_sigma5,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz])
        partials.declare_partials(x_Theta,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz])
        return partials.get_string()

    def execute(self, in_file, out_file):
        doc = etree.parse(in_file)
        z0 = float(doc.xpath(x_tc)[0].text)
        z3 = float(doc.xpath(x_AR)[0].text)
        z4 = float(doc.xpath(x_Lambda)[0].text)
        z5 = float(doc.xpath(x_Sref)[0].text)
        x0 = float(doc.xpath(x_lambda)[0].text)
        x1 = float(doc.xpath(x_section)[0].text)
        L = float(doc.xpath(x_L)[0].text)
        WE = float(doc.xpath(x_WE)[0].text)
        NZ = float(doc.xpath(x_Nz)[0].text)
        WO = float(doc.xpath(x_WO)[0].text)
        WFO = float(doc.xpath(x_WFO)[0].text)

        Theta, WF, WT, sigma = structure(np.array([x0, x1]), np.array([z0, 0., 0., z3, z4, z5]),
                                         L, WE, NZ, WFO, WO)

        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)
        xml_safe_create_element(doc, x_WF, WF)
        xml_safe_create_element(doc, x_WT, WT)

        xml_safe_create_element(doc, x_sigma1, sigma[0])
        xml_safe_create_element(doc, x_sigma2, sigma[1])
        xml_safe_create_element(doc, x_sigma3, sigma[2])
        xml_safe_create_element(doc, x_sigma4, sigma[3])
        xml_safe_create_element(doc, x_sigma5, sigma[4])

        xml_safe_create_element(doc, x_Theta, Theta)

        doc.write(out_file, encoding='utf-8', pretty_print=True, xml_declaration=True)

    @staticmethod
    def linearize(in_file, partials_file):
        doc = etree.parse(in_file)
        z0 = float(doc.xpath(x_tc)[0].text)
        z3 = float(doc.xpath(x_AR)[0].text)
        z4 = float(doc.xpath(x_Lambda)[0].text)
        z5 = float(doc.xpath(x_Sref)[0].text)
        x0 = float(doc.xpath(x_lambda)[0].text)
        x1 = float(doc.xpath(x_section)[0].text)
        L = float(doc.xpath(x_L)[0].text)
        NZ = float(doc.xpath(x_Nz)[0].text)

        J_WT, J_WF, J_sigma, J_Theta = structure_partials(dict(z=np.array([z0, 0., 0., z3, z4, z5]),
                                                               x_str=np.array([x0, x1]),
                                                               L=L, NZ=NZ))

        partials = Partials()
        partials.declare_partials(x_WT,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz],
                                  [J_WT['z'][0,0], J_WT['z'][0,3], J_WT['z'][0,4], J_WT['z'][0,5],
                                   J_WT['x_str'][0, 0], J_WT['x_str'][0, 1],
                                   J_WT['WO'], J_WT['WE'], J_WT['WFO'], J_WT['L'], J_WT['NZ']])
        partials.declare_partials(x_WF,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz],
                                  [J_WF['z'][0, 0], J_WF['z'][0, 3], J_WF['z'][0, 4], J_WF['z'][0, 5],
                                   J_WF['x_str'][0, 0], J_WF['x_str'][0, 1],
                                   J_WF['WO'], J_WF['WE'], J_WF['WFO'], J_WF['L'], J_WF['NZ']])
        partials.declare_partials(x_sigma1,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz],
                                  [J_sigma['z'][0, 0], J_sigma['z'][0, 3], J_sigma['z'][0, 4], J_sigma['z'][0, 5],
                                   J_sigma['x_str'][0, 0], J_sigma['x_str'][0, 1],
                                   J_sigma['WO'][0], J_sigma['WE'][0], J_sigma['WFO'][0], J_sigma['L'][0], J_sigma['NZ'][0]])
        partials.declare_partials(x_sigma2,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz],
                                  [J_sigma['z'][1, 0], J_sigma['z'][1, 3], J_sigma['z'][1, 4], J_sigma['z'][1, 5],
                                   J_sigma['x_str'][1, 0], J_sigma['x_str'][1, 1],
                                   J_sigma['WO'][1], J_sigma['WE'][1], J_sigma['WFO'][1], J_sigma['L'][1], J_sigma['NZ'][1]])
        partials.declare_partials(x_sigma3,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz],
                                  [J_sigma['z'][2, 0], J_sigma['z'][2, 3], J_sigma['z'][2, 4], J_sigma['z'][2, 5],
                                   J_sigma['x_str'][2, 0], J_sigma['x_str'][2, 1],
                                   J_sigma['WO'][2], J_sigma['WE'][2], J_sigma['WFO'][2], J_sigma['L'][2], J_sigma['NZ'][2]])
        partials.declare_partials(x_sigma4,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz],
                                  [J_sigma['z'][3, 0], J_sigma['z'][3, 3], J_sigma['z'][3, 4], J_sigma['z'][3, 5],
                                   J_sigma['x_str'][3, 0], J_sigma['x_str'][3, 1],
                                   J_sigma['WO'][3], J_sigma['WE'][3], J_sigma['WFO'][3], J_sigma['L'][3], J_sigma['NZ'][3]])
        partials.declare_partials(x_sigma5,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz],
                                  [J_sigma['z'][4, 0], J_sigma['z'][4, 3], J_sigma['z'][4, 4], J_sigma['z'][4, 5],
                                   J_sigma['x_str'][4, 0], J_sigma['x_str'][4, 1],
                                   J_sigma['WO'][4], J_sigma['WE'][4], J_sigma['WFO'][4], J_sigma['L'][4], J_sigma['NZ'][4]])
        partials.declare_partials(x_Theta,
                                  [x_tc, x_AR, x_Lambda, x_Sref, x_lambda, x_section, x_WO, x_WE, x_WFO, x_L, x_Nz],
                                  [J_Theta['z'][0, 0], J_Theta['z'][0, 3], J_Theta['z'][0, 4], J_Theta['z'][0, 5],
                                   J_Theta['x_str'][0, 0], J_Theta['x_str'][0, 1],
                                   J_Theta['WO'], J_Theta['WE'], J_Theta['WFO'], J_Theta['L'], J_Theta['NZ']])
        partials.write(partials_file)


def structure(x_str, Z, L, WE, NZ, WFO, WO):
    # Structure calculation as taken from the ONERA repository
    # Removed "pf" input and added "NZ", "WFO" and "WO" input
    t = Z[0]*Z[5]/(np.sqrt(abs(Z[5]*Z[3])))
    b = np.sqrt(abs(Z[5]*Z[3]))/2.0
    R = (1.0+2.0*x_str[0])/(3.0*(1.0+x_str[0]))
    Theta = polynomial_function([abs(x_str[1]), b, R, L],
                         [2, 4, 4, 3], [0.25]*4, "twist")

    Fo1 = polynomial_function([x_str[1]], [1], [.008], "Fo1")

    WT_hat = L
    WW = Fo1 * (0.0051 * abs(WT_hat*NZ)**0.557 * \
                abs(Z[5])**0.649 * abs(Z[3])**0.5 * abs(Z[0])**(-0.4) \
                * abs(1.0+x_str[0])**0.1 * (0.1875*abs(Z[5]))**0.1 \
                / abs(np.cos(Z[4]*np.pi/180.)))
    WFW = 5.0/18.0 * abs(Z[5]) * 2.0/3.0 * t * 42.5
    WF = WFW + WFO
    WT = WO + WW + WF + WE
    sigma = 5*[0.]
    sigma[0] = polynomial_function([Z[0], L, x_str[1], b, R], [4, 1, 4, 1, 1], [0.1]*5, "sigma[1]")
    sigma[1] = polynomial_function([Z[0], L, x_str[1], b, R], [4, 1, 4, 1, 1], [0.15]*5, "sigma[2]")
    sigma[2] = polynomial_function([Z[0], L, x_str[1], b, R], [4, 1, 4, 1, 1], [0.2]*5, "sigma[3]")
    sigma[3] = polynomial_function([Z[0], L, x_str[1], b, R], [4, 1, 4, 1, 1], [0.25]*5, "sigma[4]")
    sigma[4] = polynomial_function([Z[0], L, x_str[1], b, R], [4, 1, 4, 1, 1], [0.30]*5, "sigma[5]")
    return Theta, WF, WT, sigma


def structure_partials(inputs):
    # Aerodynamics partial calculation from ONERA repository
    # Removed self, J, scalers
    # Replaced pf for polynomial_function
    # Get d dictionary as static value

    Z = inputs['z']
    Xstr = inputs['x_str']
    L = inputs['L']
    NZ = inputs['NZ']
    pf_d = get_d_dict()

    # dWT ################################################################
    J_WT = dict()
    Fo1 = polynomial_function([Xstr[1]], [1], [.008], "Fo1")

    dWtdlambda = 0.1 * Fo1 / np.cos(Z[4] * np.pi / 180.) * 0.0051 \
                 * (abs(L) * NZ) ** 0.557 * abs(Z[5]) ** 0.649 \
                 * abs(Z[3]) ** 0.5 * abs(Z[0]) ** (-0.4) \
                 * (1.0 + Xstr[0]) ** -0.9 * (0.1875 * abs(Z[5])) ** 0.1
    A = (0.0051 * abs(L * NZ) ** 0.557 * abs(Z[5]) ** 0.649 \
         * abs(Z[3]) ** 0.5 * abs(Z[0]) ** (-0.4) * abs(1.0 + Xstr[0]) ** 0.1 \
         * (0.1875 * abs(Z[5])) ** 0.1 / abs(np.cos(Z[4] * np.pi / 180.)))

    S_shifted, Ai, Aij = polynomial_function([Xstr[1]], [1], [.008],
                                 "Fo1", deriv=True)
    if Xstr[1] / pf_d['Fo1'][0] >= 0.75 and Xstr[1] / pf_d['Fo1'][0] <= 1.25:
        dSxdx = 1.0 / pf_d['Fo1'][0]
    else:
        dSxdx = 0.0

    dWtdx = A * (Ai[0] * dSxdx \
                 + Aij[0, 0] * dSxdx * S_shifted[0, 0])

    val = np.append(dWtdlambda, dWtdx)
    J_WT['x_str'] = np.array([val])
    dWTdtc = -0.4 * Fo1 / np.cos(Z[4] * np.pi / 180.) * 0.0051 \
             * abs(L * NZ) ** 0.557 * abs(Z[5]) ** 0.649 \
             * abs(Z[3]) ** 0.5 * abs(Z[0]) ** (-1.4) * abs(1.0 + Xstr[0]) ** 0.1 \
             * (0.1875 * abs(Z[5])) ** 0.1 + 212.5 / 27. * Z[5] ** (3.0 / 2.0) / np.sqrt(Z[3])
    dWTdh = 0.0
    dWTdM = 0.0
    dWTdAR = 0.5 * Fo1 / np.cos(Z[4] * np.pi / 180.) * 0.0051 \
             * abs(L * NZ) ** 0.557 * abs(Z[5]) ** 0.649 \
             * abs(Z[3]) ** -0.5 * abs(Z[0]) ** (-0.4) * abs(1.0 + Xstr[0]) ** 0.1 \
             * (0.1875 * abs(Z[5])) ** 0.1 + 212.5 / 27. * Z[5] ** (3.0 / 2.0) \
             * Z[0] * -0.5 * Z[3] ** (-3.0 / 2.0)
    dWTdLambda = Fo1 * np.pi / 180. * np.sin(Z[4] * np.pi / 180.) / np.cos(Z[4] * np.pi / 180.) ** 2 \
                 * 0.0051 * abs(L * NZ) ** 0.557 * abs(Z[5]) ** 0.649 \
                 * abs(Z[3]) ** 0.5 * abs(Z[0]) ** (-0.4) * abs(1.0 + Xstr[0]) ** 0.1 \
                 * (0.1875 * abs(Z[5])) ** 0.1
    dWTdSref = 0.749 * Fo1 / np.cos(Z[4] * np.pi / 180.) * 0.1875 ** (0.1) * 0.0051 \
               * abs(L * NZ) ** 0.557 * abs(Z[5]) ** -0.251 \
               * abs(Z[3]) ** 0.5 * abs(Z[0]) ** (-0.4) * abs(1.0 + Xstr[0]) ** 0.1 \
               + 637.5 / 54. * Z[5] ** (0.5) * Z[0] / np.sqrt(Z[3])
    val = np.append(dWTdtc,
                    [dWTdh,
                     dWTdM,
                     dWTdAR,
                     dWTdLambda,
                     dWTdSref])
    J_WT['z'] = np.array([val])
    dWTdL = 0.557 * Fo1 / np.cos(Z[4] * np.pi / 180.) * 0.0051 * abs(L) ** -0.443 \
            * NZ ** 0.557 * abs(Z[5]) ** 0.649 * abs(Z[3]) ** 0.5 \
            * abs(Z[0]) ** (-0.4) * abs(1.0 + Xstr[0]) ** 0.1 * (0.1875 * abs(Z[5])) ** 0.1
    J_WT['L'] = np.array([[dWTdL]])
    dWTdWE = 1.0
    J_WT['WE'] = np.array([[dWTdWE]])
    dWTdNZ = 0.557 * Fo1 * (0.0051 * abs(NZ)**-0.443 * abs(L) ** 0.557 * \
                abs(Z[5])**0.649 * abs(Z[3])**0.5 * abs(Z[0])**(-0.4) \
                * abs(1.0+Xstr[0])**0.1 * (0.1875*abs(Z[5]))**0.1 \
                / abs(np.cos(Z[4]*np.pi/180.)))
    J_WT['NZ'] = np.array([dWTdNZ])
    J_WT['WO'] = np.array([1.])
    J_WT['WFO'] = np.array([1.])

    # dWF ################################################################
    J_WF = dict()
    dWFdlambda = 0.0
    dWFdx = 0.0
    val = np.append(dWFdlambda, dWFdx)
    J_WF['x_str'] = np.array([val])
    dWFdtc = 212.5 / 27. * Z[5] ** (3.0 / 2.0) / np.sqrt(Z[3])
    dWFdh = 0.0
    dWFdM = 0.0
    dWFdAR = 212.5 / 27. * Z[5] ** (3.0 / 2.0) * Z[0] * -0.5 * Z[3] ** (-3.0 / 2.0)
    dWFdLambda = 0.0
    dWFdSref = 637.5 / 54. * Z[5] ** (0.5) * Z[0] / np.sqrt(Z[3])
    val = np.append(dWFdtc,
                    [dWFdh,
                     dWFdM,
                     dWFdAR,
                     dWFdLambda,
                     dWFdSref])
    J_WF['z'] = np.array([val])
    dWFdL = 0.0
    J_WF['L'] = np.array([[dWFdL]])
    dWFdWE = 0.0
    J_WF['WE'] = np.array([[dWFdWE]])
    J_WF['NZ'] = np.array([0.])
    J_WF['WO'] = np.array([0.])
    J_WF['WFO'] = np.array([1.])

    ### dTheta ###########################################################
    J_Theta = dict()
    b = np.sqrt(abs(Z[5] * Z[3])) / 2.0
    R = (1.0 + 2.0 * Xstr[0]) / (3.0 * (1.0 + Xstr[0]))
    S_shifted, Ai, Aij = polynomial_function([abs(Xstr[1]), b, R, L],
                                 [2, 4, 4, 3],
                                 [0.25] * 4, "twist", deriv=True)
    if R / pf_d['twist'][2] >= 0.75 and R / pf_d['twist'][2] <= 1.25:
        dSRdlambda = 1.0 / pf_d['twist'][2] * 1.0 / (3.0 * (1.0 + Xstr[0]) ** 2)
    else:
        dSRdlambda = 0.0

    dSRdlambda2 = 2.0 * S_shifted[0, 2] * dSRdlambda
    dThetadlambda = Ai[2] * dSRdlambda + 0.5 * Aij[2, 2] * dSRdlambda2 \
                    + Aij[0, 2] * S_shifted[0, 0] * dSRdlambda \
                    + Aij[1, 2] * S_shifted[0, 1] * dSRdlambda \
                    + Aij[3, 2] * S_shifted[0, 3] * dSRdlambda
    if abs(Xstr[1]) / pf_d['twist'][0] >= 0.75 and abs(Xstr[1]) / pf_d['twist'][0] <= 1.25:
        dSxdx = 1.0 / pf_d['twist'][0]
    else:
        dSxdx = 0.0
    dSxdx2 = 2.0 * S_shifted[0, 0] * dSxdx
    dThetadx = Ai[0] * dSxdx + 0.5 * Aij[0, 0] * dSxdx2 \
               + Aij[1, 0] * S_shifted[0, 1] * dSxdx \
               + Aij[2, 0] * S_shifted[0, 2] * dSxdx \
               + Aij[3, 0] * S_shifted[0, 3] * dSxdx
    J_Theta['x_str'] = np.array([np.append(dThetadlambda[0, 0],
                                              dThetadx[0, 0])])
    dThetadtc = 0.0
    dThetadh = 0.0
    dThetadM = 0.0
    if b / pf_d['twist'][1] >= 0.75 and b / pf_d['twist'][1] <= 1.25:
        dSbdAR = 1.0 / pf_d['twist'][1] * (np.sqrt(Z[5]) / 4.0 * Z[3] ** -0.5)
    else:
        dSbdAR = 0.0
    dSbdAR2 = 2.0 * S_shifted[0, 1] * dSbdAR
    dThetadAR = Ai[1] * dSbdAR + 0.5 * Aij[1, 1] * dSbdAR2 \
                + Aij[0, 1] * S_shifted[0, 0] * dSbdAR \
                + Aij[2, 1] * S_shifted[0, 2] * dSbdAR \
                + Aij[3, 1] * S_shifted[0, 3] * dSbdAR
    dThetadLambda = 0.0
    if b / pf_d['twist'][1] >= 0.75 and b / pf_d['twist'][1] <= 1.25:
        dSbdSref = 1.0 / pf_d['twist'][1] * (np.sqrt(Z[3]) / 4.0 * Z[5] ** -0.5)
    else:
        dSbdSref = 0.0
    dSbdSref2 = 2.0 * S_shifted[0, 1] * dSbdSref
    dThetadSref = Ai[1] * dSbdSref + 0.5 * Aij[1, 1] * dSbdSref2 \
                  + Aij[0, 1] * S_shifted[0, 0] * dSbdSref \
                  + Aij[2, 1] * S_shifted[0, 2] * dSbdSref \
                  + Aij[3, 1] * S_shifted[0, 3] * dSbdSref

    J_Theta['z'] = np.array([np.append(dThetadtc,
                                          [dThetadh,
                                           dThetadM,
                                           dThetadAR,
                                           dThetadLambda,
                                           dThetadSref])])
    if L / pf_d['twist'][3] >= 0.75 and L / pf_d['twist'][3] <= 1.25:
        dSLdL = 1.0 / pf_d['twist'][3]
    else:
        dSLdL = 0.0
    dSLdL2 = 2.0 * S_shifted[0, 3] * dSLdL
    dThetadL = Ai[3] * dSLdL + 0.5 * Aij[3, 3] * dSLdL2 \
               + Aij[0, 3] * S_shifted[0, 0] * dSLdL \
               + Aij[1, 3] * S_shifted[0, 1] * dSLdL \
               + Aij[2, 3] * S_shifted[0, 2] * dSLdL
    J_Theta['L'] = (np.array([[dThetadL]])).reshape((1, 1))
    dThetadWE = 0.0
    J_Theta['WE'] = np.array([[dThetadWE]])
    J_Theta['NZ'] = np.array([0.])
    J_Theta['WO'] = np.array([0.])
    J_Theta['WFO'] = np.array([0.])

    # dsigma #############################################################
    J_sigma = dict()
    b = np.sqrt(abs(Z[5] * Z[3])) / 2.0
    R = (1.0 + 2.0 * Xstr[0]) / (3.0 * (1.0 + Xstr[0]))
    s_new = [Z[0], L, Xstr[1], b, R]
    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.1] * 5,
                                 "sigma[1]", deriv=True)
    if R / pf_d['sigma[1]'][4] >= 0.75 and R / pf_d['sigma[1]'][4] <= 1.25:
        dSRdlambda = 1.0 / pf_d['sigma[1]'][4] * 1.0 / (3.0 * (1.0 + Xstr[0]) ** 2)
    else:
        dSRdlambda = 0.0
    dSRdlambda2 = 2.0 * S_shifted[0, 4] * dSRdlambda
    dsigma1dlambda = Ai[4] * dSRdlambda + 0.5 * Aij[4, 4] * dSRdlambda2 \
                     + Aij[0, 4] * S_shifted[0, 0] * dSRdlambda \
                     + Aij[1, 4] * S_shifted[0, 1] * dSRdlambda \
                     + Aij[2, 4] * S_shifted[0, 2] * dSRdlambda \
                     + Aij[3, 4] * S_shifted[0, 3] * dSRdlambda
    if Xstr[1] / pf_d['sigma[1]'][2] >= 0.75 and Xstr[1] / pf_d['sigma[1]'][2] <= 1.25:
        dSxdx = 1.0 / pf_d['sigma[1]'][2]
    else:
        dSxdx = 0.0
    dSxdx2 = 2.0 * S_shifted[0, 2] * dSxdx
    dsigma1dx = Ai[2] * dSxdx + 0.5 * Aij[2, 2] * dSxdx2 \
                + Aij[0, 2] * S_shifted[0, 0] * dSxdx \
                + Aij[1, 2] * S_shifted[0, 1] * dSxdx \
                + Aij[3, 2] * S_shifted[0, 3] * dSxdx \
                + Aij[4, 2] * S_shifted[0, 4] * dSxdx

    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.15] * 5,
                                 "sigma[2]", deriv=True)
    if R / pf_d['sigma[2]'][4] >= 0.75 and R / pf_d['sigma[2]'][4] <= 1.25:
        dSRdlambda = 1.0 / pf_d['sigma[2]'][4] * 1.0 / (3.0 * (1.0 + Xstr[0]) ** 2)
    else:
        dSRdlambda = 0.0
    dSRdlambda2 = 2.0 * S_shifted[0, 4] * dSRdlambda
    dsigma2dlambda = Ai[4] * dSRdlambda \
                     + 0.5 * Aij[4, 4] * dSRdlambda2 \
                     + Aij[0, 4] * S_shifted[0, 0] * dSRdlambda \
                     + Aij[1, 4] * S_shifted[0, 1] * dSRdlambda \
                     + Aij[2, 4] * S_shifted[0, 2] * dSRdlambda \
                     + Aij[3, 4] * S_shifted[0, 3] * dSRdlambda
    if Xstr[1] / pf_d['sigma[2]'][2] >= 0.75 and Xstr[1] / pf_d['sigma[2]'][2] <= 1.25:
        dSxdx = 1.0 / pf_d['sigma[2]'][2]
    else:
        dSxdx = 0.0
    dSxdx2 = 2.0 * S_shifted[0, 2] * dSxdx
    dsigma2dx = Ai[2] * dSxdx + 0.5 * Aij[2, 2] * dSxdx2 \
                + Aij[0, 2] * S_shifted[0, 0] * dSxdx \
                + Aij[1, 2] * S_shifted[0, 1] * dSxdx \
                + Aij[3, 2] * S_shifted[0, 3] * dSxdx \
                + Aij[4, 2] * S_shifted[0, 4] * dSxdx

    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.2] * 5,
                                 "sigma[3]", deriv=True)
    if R / pf_d['sigma[3]'][4] >= 0.75 and R / pf_d['sigma[3]'][4] <= 1.25:
        dSRdlambda = 1.0 / pf_d['sigma[3]'][4] * 1.0 / (3.0 * (1.0 + Xstr[0]) ** 2)
    else:
        dSRdlambda = 0.0
    dSRdlambda2 = 2.0 * S_shifted[0, 4] * dSRdlambda
    dsigma3dlambda = Ai[4] * dSRdlambda + 0.5 * Aij[4, 4] * dSRdlambda2 \
                     + Aij[0, 4] * S_shifted[0, 0] * dSRdlambda \
                     + Aij[1, 4] * S_shifted[0, 1] * dSRdlambda \
                     + Aij[2, 4] * S_shifted[0, 2] * dSRdlambda \
                     + Aij[3, 4] * S_shifted[0, 3] * dSRdlambda
    if Xstr[1] / pf_d['sigma[3]'][2] >= 0.75 and Xstr[1] / pf_d['sigma[3]'][2] <= 1.25:
        dSxdx = 1.0 / pf_d['sigma[3]'][2]
    else:
        dSxdx = 0.0
    dSxdx2 = 2.0 * S_shifted[0, 2] * dSxdx
    dsigma3dx = Ai[2] * dSxdx + 0.5 * Aij[2, 2] * dSxdx2 \
                + Aij[0, 2] * S_shifted[0, 0] * dSxdx \
                + Aij[1, 2] * S_shifted[0, 1] * dSxdx \
                + Aij[3, 2] * S_shifted[0, 3] * dSxdx \
                + Aij[4, 2] * S_shifted[0, 4] * dSxdx

    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.25] * 5,
                                 "sigma[4]", deriv=True)
    if R / pf_d['sigma[4]'][4] >= 0.75 and R / pf_d['sigma[4]'][4] <= 1.25:
        dSRdlambda = 1.0 / pf_d['sigma[4]'][4] * 1.0 / (3.0 * (1.0 + Xstr[0]) ** 2)
    else:
        dSRdlambda = 0.0
    dSRdlambda2 = 2.0 * S_shifted[0, 4] * dSRdlambda
    dsigma4dlambda = Ai[4] * dSRdlambda \
                     + 0.5 * Aij[4, 4] * dSRdlambda2 \
                     + Aij[0, 4] * S_shifted[0, 0] * dSRdlambda \
                     + Aij[1, 4] * S_shifted[0, 1] * dSRdlambda \
                     + Aij[2, 4] * S_shifted[0, 2] * dSRdlambda \
                     + Aij[3, 4] * S_shifted[0, 3] * dSRdlambda
    if Xstr[1] / pf_d['sigma[4]'][2] >= 0.75 and Xstr[1] / pf_d['sigma[4]'][2] <= 1.25:
        dSxdx = 1.0 / pf_d['sigma[4]'][2]
    else:
        dSxdx = 0.0
    dSxdx2 = 2.0 * S_shifted[0, 2] * dSxdx
    dsigma4dx = Ai[2] * dSxdx + 0.5 * Aij[2, 2] * dSxdx2 \
                + Aij[0, 2] * S_shifted[0, 0] * dSxdx \
                + Aij[1, 2] * S_shifted[0, 1] * dSxdx \
                + Aij[3, 2] * S_shifted[0, 3] * dSxdx \
                + Aij[4, 2] * S_shifted[0, 4] * dSxdx
    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.3] * 5,
                                 "sigma[5]", deriv=True)
    if R / pf_d['sigma[5]'][4] >= 0.75 and R / pf_d['sigma[5]'][4] <= 1.25:
        dSRdlambda = 1.0 / pf_d['sigma[5]'][4] * 1.0 / (3.0 * (1.0 + Xstr[0]) ** 2)
    else:
        dSRdlambda = 0.0
    dSRdlambda2 = 2.0 * S_shifted[0, 4] * dSRdlambda
    dsigma5dlambda = Ai[4] * dSRdlambda + 0.5 * Aij[4, 4] * dSRdlambda2 \
                     + Aij[0, 4] * S_shifted[0, 0] * dSRdlambda \
                     + Aij[1, 4] * S_shifted[0, 1] * dSRdlambda \
                     + Aij[2, 4] * S_shifted[0, 2] * dSRdlambda \
                     + Aij[3, 4] * S_shifted[0, 3] * dSRdlambda
    if Xstr[1] / pf_d['sigma[5]'][2] >= 0.75 and Xstr[1] / pf_d['sigma[5]'][2] <= 1.25:
        dSxdx = 1.0 / pf_d['sigma[5]'][2]
    else:
        dSxdx = 0.0
    dSxdx2 = 2.0 * S_shifted[0, 2] * dSxdx
    dsigma5dx = Ai[2] * dSxdx + 0.5 * Aij[2, 2] * dSxdx2 \
                + Aij[0, 2] * S_shifted[0, 0] * dSxdx \
                + Aij[1, 2] * S_shifted[0, 1] * dSxdx \
                + Aij[3, 2] * S_shifted[0, 3] * dSxdx \
                + Aij[4, 2] * S_shifted[0, 4] * dSxdx

    J_sigma['x_str'] = np.array(
        [[dsigma1dlambda[0, 0],
          dsigma1dx[0, 0]],
         [dsigma2dlambda[0, 0],
          dsigma2dx[0, 0]],
         [dsigma3dlambda[0, 0],
          dsigma3dx[0, 0]],
         [dsigma4dlambda[0, 0],
          dsigma4dx[0, 0]],
         [dsigma5dlambda[0, 0],
          dsigma5dx[0, 0]]])

    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.1] * 5,
                                 "sigma[1]", deriv=True)
    if Z[0] / pf_d['sigma[1]'][0] >= 0.75 and Z[0] / pf_d['sigma[1]'][0] <= 1.25:
        dStcdtc = 1.0 / pf_d['sigma[1]'][0]
    else:
        dStcdtc = 0.0
    dStcdtc2 = 2.0 * S_shifted[0, 0] * dStcdtc
    dsigma1dtc = Ai[0] * dStcdtc + 0.5 * Aij[0, 0] * dStcdtc2 \
                 + Aij[1, 0] * S_shifted[0, 1] * dStcdtc \
                 + Aij[2, 0] * S_shifted[0, 2] * dStcdtc \
                 + Aij[3, 0] * S_shifted[0, 3] * dStcdtc \
                 + Aij[4, 0] * S_shifted[0, 4] * dStcdtc
    dsigma1dh = 0.0
    dsigma1dM = 0.0
    if b / pf_d['sigma[1]'][3] >= 0.75 and b / pf_d['sigma[1]'][3] <= 1.25:
        dSbdAR = 1.0 / pf_d['sigma[1]'][3] * (np.sqrt(Z[5]) / 4.0 * Z[3] ** -0.5)
        dSbdSref = 1.0 / pf_d['sigma[1]'][3] * (np.sqrt(Z[3]) / 4.0 * Z[5] ** -0.5)
    else:
        dSbdAR = 0.0
        dSbdSref = 0.0
    dSbdAR2 = 2.0 * S_shifted[0, 3] * dSbdAR
    dsigma1dAR = Ai[3] * dSbdAR + 0.5 * Aij[3, 3] * dSbdAR2 \
                 + Aij[0, 3] * S_shifted[0, 0] * dSbdAR \
                 + Aij[1, 3] * S_shifted[0, 1] * dSbdAR \
                 + Aij[2, 3] * S_shifted[0, 2] * dSbdAR \
                 + Aij[4, 3] * S_shifted[0, 4] * dSbdAR
    dsigma1dLambda = 0.0
    dSbdSref2 = 2.0 * S_shifted[0, 3] * dSbdSref
    dsigma1dSref = Ai[3] * dSbdSref + 0.5 * Aij[3, 3] * dSbdSref2 \
                   + Aij[0, 3] * S_shifted[0, 0] * dSbdSref \
                   + Aij[1, 3] * S_shifted[0, 1] * dSbdSref \
                   + Aij[2, 3] * S_shifted[0, 2] * dSbdSref \
                   + Aij[4, 3] * S_shifted[0, 4] * dSbdSref
    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.15] * 5,
                                 "sigma[2]", deriv=True)

    if Z[0] / pf_d['sigma[2]'][0] >= 0.75 and Z[0] / pf_d['sigma[2]'][0] <= 1.25:
        dStcdtc = 1.0 / pf_d['sigma[2]'][0]
    else:
        dStcdtc = 0.0
    dStcdtc2 = 2.0 * S_shifted[0, 0] * dStcdtc
    dsigma2dtc = Ai[0] * dStcdtc + 0.5 * Aij[0, 0] * dStcdtc2 \
                 + Aij[1, 0] * S_shifted[0, 1] * dStcdtc \
                 + Aij[2, 0] * S_shifted[0, 2] * dStcdtc \
                 + Aij[3, 0] * S_shifted[0, 3] * dStcdtc \
                 + Aij[4, 0] * S_shifted[0, 4] * dStcdtc
    dsigma2dh = 0.0
    dsigma2dM = 0.0
    if b / pf_d['sigma[2]'][3] >= 0.75 and b / pf_d['sigma[2]'][3] <= 1.25:
        dSbdAR = 1.0 / pf_d['sigma[2]'][3] * (np.sqrt(Z[5]) / 4.0 * Z[3] ** -0.5)
        dSbdSref = 1.0 / pf_d['sigma[2]'][3] * (np.sqrt(Z[3]) / 4.0 * Z[5] ** -0.5)
    else:
        dSbdAR = 0.0
        dSbdSref = 0.0
    dSbdAR2 = 2.0 * S_shifted[0, 3] * dSbdAR
    dsigma2dAR = Ai[3] * dSbdAR + 0.5 * Aij[3, 3] * dSbdAR2 \
                 + Aij[0, 3] * S_shifted[0, 0] * dSbdAR \
                 + Aij[1, 3] * S_shifted[0, 1] * dSbdAR \
                 + Aij[2, 3] * S_shifted[0, 2] * dSbdAR \
                 + Aij[4, 3] * S_shifted[0, 4] * dSbdAR
    dsigma2dLambda = 0.0
    dSbdSref2 = 2.0 * S_shifted[0, 3] * dSbdSref
    dsigma2dSref = Ai[3] * dSbdSref + 0.5 * Aij[3, 3] * dSbdSref2 \
                   + Aij[0, 3] * S_shifted[0, 0] * dSbdSref \
                   + Aij[1, 3] * S_shifted[0, 1] * dSbdSref \
                   + Aij[2, 3] * S_shifted[0, 2] * dSbdSref \
                   + Aij[4, 3] * S_shifted[0, 4] * dSbdSref

    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.20] * 5,
                                 "sigma[3]", deriv=True)
    if Z[0] / pf_d['sigma[3]'][0] >= 0.75 and Z[0] / pf_d['sigma[3]'][0] <= 1.25:
        dStcdtc = 1.0 / pf_d['sigma[3]'][0]
    else:
        dStcdtc = 0.0
    dStcdtc2 = 2.0 * S_shifted[0, 0] * dStcdtc
    dsigma3dtc = Ai[0] * dStcdtc + 0.5 * Aij[0, 0] * dStcdtc2 \
                 + Aij[1, 0] * S_shifted[0, 1] * dStcdtc \
                 + Aij[2, 0] * S_shifted[0, 2] * dStcdtc \
                 + Aij[3, 0] * S_shifted[0, 3] * dStcdtc \
                 + Aij[4, 0] * S_shifted[0, 4] * dStcdtc
    dsigma3dh = 0.0
    dsigma3dM = 0.0
    if b / pf_d['sigma[3]'][3] >= 0.75 and b / pf_d['sigma[3]'][3] <= 1.25:
        dSbdAR = 1.0 / pf_d['sigma[3]'][3] * (np.sqrt(Z[5]) / 4.0 * Z[3] ** -0.5)
        dSbdSref = 1.0 / pf_d['sigma[3]'][3] * (np.sqrt(Z[3]) / 4.0 * Z[5] ** -0.5)
    else:
        dSbdAR = 0.0
        dSbdSref = 0.0
    dSbdAR2 = 2.0 * S_shifted[0, 3] * dSbdAR
    dsigma3dAR = Ai[3] * dSbdAR + 0.5 * Aij[3, 3] * dSbdAR2 \
                 + Aij[0, 3] * S_shifted[0, 0] * dSbdAR \
                 + Aij[1, 3] * S_shifted[0, 1] * dSbdAR \
                 + Aij[2, 3] * S_shifted[0, 2] * dSbdAR \
                 + Aij[4, 3] * S_shifted[0, 4] * dSbdAR
    dsigma3dLambda = 0.0
    dSbdSref2 = 2.0 * S_shifted[0, 3] * dSbdSref
    dsigma3dSref = Ai[3] * dSbdSref + 0.5 * Aij[3, 3] * dSbdSref2 \
                   + Aij[0, 3] * S_shifted[0, 0] * dSbdSref \
                   + Aij[1, 3] * S_shifted[0, 1] * dSbdSref \
                   + Aij[2, 3] * S_shifted[0, 2] * dSbdSref \
                   + Aij[4, 3] * S_shifted[0, 4] * dSbdSref

    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.25] * 5,
                                 "sigma[4]", deriv=True)
    if Z[0] / pf_d['sigma[4]'][0] >= 0.75 and Z[0] / pf_d['sigma[4]'][0] <= 1.25:
        dStcdtc = 1.0 / pf_d['sigma[4]'][0]
    else:
        dStcdtc = 0.0
    dStcdtc2 = 2.0 * S_shifted[0, 0] * dStcdtc
    dsigma4dtc = Ai[0] * dStcdtc + 0.5 * Aij[0, 0] * dStcdtc2 \
                 + Aij[1, 0] * S_shifted[0, 1] * dStcdtc \
                 + Aij[2, 0] * S_shifted[0, 2] * dStcdtc \
                 + Aij[3, 0] * S_shifted[0, 3] * dStcdtc \
                 + Aij[4, 0] * S_shifted[0, 4] * dStcdtc
    dsigma4dh = 0.0
    dsigma4dM = 0.0
    if b / pf_d['sigma[4]'][3] >= 0.75 and b / pf_d['sigma[4]'][3] <= 1.25:
        dSbdAR = 1.0 / pf_d['sigma[4]'][3] * (np.sqrt(Z[5]) / 4.0 * Z[3] ** -0.5)
        dSbdSref = 1.0 / pf_d['sigma[4]'][3] * (np.sqrt(Z[3]) / 4.0 * Z[5] ** -0.5)
    else:
        dSbdAR = 0.0
        dSbdSref = 0.0
    dSbdAR2 = 2.0 * S_shifted[0, 3] * dSbdAR
    dsigma4dAR = Ai[3] * dSbdAR + 0.5 * Aij[3, 3] * dSbdAR2 \
                 + Aij[0, 3] * S_shifted[0, 0] * dSbdAR \
                 + Aij[1, 3] * S_shifted[0, 1] * dSbdAR \
                 + Aij[2, 3] * S_shifted[0, 2] * dSbdAR \
                 + Aij[4, 3] * S_shifted[0, 4] * dSbdAR
    dsigma4dLambda = 0.0
    dSbdSref2 = 2.0 * S_shifted[0, 3] * dSbdSref
    dsigma4dSref = Ai[3] * dSbdSref + 0.5 * Aij[3, 3] * dSbdSref2 \
                   + Aij[0, 3] * S_shifted[0, 0] * dSbdSref \
                   + Aij[1, 3] * S_shifted[0, 1] * dSbdSref \
                   + Aij[2, 3] * S_shifted[0, 2] * dSbdSref \
                   + Aij[4, 3] * S_shifted[0, 4] * dSbdSref

    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.3] * 5,
                                 "sigma[5]", deriv=True)
    if Z[0] / pf_d['sigma[5]'][0] >= 0.75 and Z[0] / pf_d['sigma[5]'][0] <= 1.25:
        dStcdtc = 1.0 / pf_d['sigma[5]'][0]
    else:
        dStcdtc = 0.0
    dStcdtc2 = 2.0 * S_shifted[0, 0] * dStcdtc
    dsigma5dtc = Ai[0] * dStcdtc + 0.5 * Aij[0, 0] * dStcdtc2 \
                 + Aij[1, 0] * S_shifted[0, 1] * dStcdtc \
                 + Aij[2, 0] * S_shifted[0, 2] * dStcdtc \
                 + Aij[3, 0] * S_shifted[0, 3] * dStcdtc \
                 + Aij[4, 0] * S_shifted[0, 4] * dStcdtc
    dsigma5dh = 0.0
    dsigma5dM = 0.0
    if b / pf_d['sigma[5]'][3] >= 0.75 and b / pf_d['sigma[5]'][3] <= 1.25:
        dSbdAR = 1.0 / pf_d['sigma[5]'][3] * (np.sqrt(Z[5]) / 4.0 * Z[3] ** -0.5)
        dSbdSref = 1.0 / pf_d['sigma[5]'][3] * (np.sqrt(Z[3]) / 4.0 * Z[5] ** -0.5)
    else:
        dSbdAR = 0.0
        dSbdSref = 0.0
    dSbdAR2 = 2.0 * S_shifted[0, 3] * dSbdAR
    dsigma5dAR = Ai[3] * dSbdAR + 0.5 * Aij[3, 3] * dSbdAR2 \
                 + Aij[0, 3] * S_shifted[0, 0] * dSbdAR \
                 + Aij[1, 3] * S_shifted[0, 1] * dSbdAR \
                 + Aij[2, 3] * S_shifted[0, 2] * dSbdAR \
                 + Aij[4, 3] * S_shifted[0, 4] * dSbdAR
    dsigma5dLambda = 0.0
    dSbdSref2 = 2.0 * S_shifted[0, 3] * dSbdSref
    dsigma5dSref = Ai[3] * dSbdSref + 0.5 * Aij[3, 3] * dSbdSref2 \
                   + Aij[0, 3] * S_shifted[0, 0] * dSbdSref \
                   + Aij[1, 3] * S_shifted[0, 1] * dSbdSref \
                   + Aij[2, 3] * S_shifted[0, 2] * dSbdSref \
                   + Aij[4, 3] * S_shifted[0, 4] * dSbdSref

    J_sigma['z'] = np.array(
        [[dsigma1dtc[0, 0],
          dsigma1dh,
          dsigma1dM,
          dsigma1dAR[0, 0],
          dsigma1dLambda,
          dsigma1dSref[0, 0]],
         [dsigma2dtc[0, 0],
          dsigma2dh,
          dsigma2dM,
          dsigma2dAR[0, 0],
          dsigma2dLambda,
          dsigma2dSref[0, 0]],
         [dsigma3dtc[0, 0],
          dsigma3dh,
          dsigma3dM,
          dsigma3dAR[0, 0],
          dsigma3dLambda,
          dsigma3dSref[0, 0]],
         [dsigma4dtc[0, 0],
          dsigma4dh,
          dsigma4dM,
          dsigma4dAR[0, 0],
          dsigma4dLambda,
          dsigma4dSref[0, 0]],
         [dsigma5dtc[0, 0],
          dsigma5dh,
          dsigma5dM,
          dsigma5dAR[0, 0],
          dsigma5dLambda,
          dsigma5dSref[0, 0]]])

    # dS #################################################################
    S_shifted, Ai, Aij = polynomial_function([Z[0], L, Xstr[1], b, R],
                                 [4, 1, 4, 1, 1], [0.1] * 5,
                                 "sigma[1]", deriv=True)
    if L / pf_d['sigma[1]'][1] >= 0.75 and L / pf_d['sigma[1]'][1] <= 1.25:
        dSLdL = 1.0 / pf_d['sigma[1]'][1]
    else:
        dSLdL = 0.0
    dSLdL2 = 2.0 * S_shifted[0, 1] * dSLdL
    dsigma1dL = Ai[1] * dSLdL + 0.5 * Aij[1, 1] * dSLdL2 \
                + Aij[0, 1] * S_shifted[0, 0] * dSLdL \
                + Aij[2, 1] * S_shifted[0, 2] * dSLdL \
                + Aij[3, 1] * S_shifted[0, 3] * dSLdL \
                + Aij[4, 1] * S_shifted[0, 4] * dSLdL

    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.15] * 5,
                                 "sigma[2]", deriv=True)
    if L / pf_d['sigma[2]'][1] >= 0.75 and L / pf_d['sigma[2]'][1] <= 1.25:
        dSLdL = 1.0 / pf_d['sigma[2]'][1]
    else:
        dSLdL = 0.0
    dSLdL2 = 2.0 * S_shifted[0, 1] * dSLdL
    dsigma2dL = Ai[1] * dSLdL + 0.5 * Aij[1, 1] * dSLdL2 \
                + Aij[0, 1] * S_shifted[0, 0] * dSLdL \
                + Aij[2, 1] * S_shifted[0, 2] * dSLdL \
                + Aij[3, 1] * S_shifted[0, 3] * dSLdL \
                + Aij[4, 1] * S_shifted[0, 4] * dSLdL

    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.2] * 5,
                                 "sigma[3]", deriv=True)
    if L / pf_d['sigma[3]'][1] >= 0.75 and L / pf_d['sigma[3]'][1] <= 1.25:
        dSLdL = 1.0 / pf_d['sigma[3]'][1]
    else:
        dSLdL = 0.0
    dSLdL2 = 2.0 * S_shifted[0, 1] * dSLdL
    dsigma3dL = Ai[1] * dSLdL + 0.5 * Aij[1, 1] * dSLdL2 \
                + Aij[0, 1] * S_shifted[0, 0] * dSLdL \
                + Aij[2, 1] * S_shifted[0, 2] * dSLdL \
                + Aij[3, 1] * S_shifted[0, 3] * dSLdL \
                + Aij[4, 1] * S_shifted[0, 4] * dSLdL

    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.25] * 5,
                                 "sigma[4]", deriv=True)
    if L / pf_d['sigma[4]'][1] >= 0.75 and L / pf_d['sigma[4]'][1] <= 1.25:
        dSLdL = 1.0 / pf_d['sigma[4]'][1]
    else:
        dSLdL = 0.0
    dSLdL2 = 2.0 * S_shifted[0, 1] * dSLdL
    dsigma4dL = Ai[1] * dSLdL + 0.5 * Aij[1, 1] * dSLdL2 \
                + Aij[0, 1] * S_shifted[0, 0] * dSLdL \
                + Aij[2, 1] * S_shifted[0, 2] * dSLdL \
                + Aij[3, 1] * S_shifted[0, 3] * dSLdL \
                + Aij[4, 1] * S_shifted[0, 4] * dSLdL

    S_shifted, Ai, Aij = polynomial_function(s_new,
                                 [4, 1, 4, 1, 1], [0.3] * 5,
                                 "sigma[5]", deriv=True)
    if L / pf_d['sigma[5]'][1] >= 0.75 and L / pf_d['sigma[5]'][1] <= 1.25:
        dSLdL = 1.0 / pf_d['sigma[5]'][1]
    else:
        dSLdL = 0.0
    dSLdL2 = 2.0 * S_shifted[0, 1] * dSLdL
    dsigma5dL = Ai[1] * dSLdL + 0.5 * Aij[1, 1] * dSLdL2 \
                + Aij[0, 1] * S_shifted[0, 0] * dSLdL \
                + Aij[2, 1] * S_shifted[0, 2] * dSLdL \
                + Aij[3, 1] * S_shifted[0, 3] * dSLdL \
                + Aij[4, 1] * S_shifted[0, 4] * dSLdL

    J_sigma['L'] = np.array(
        [[dsigma1dL],
         [dsigma2dL],
         [dsigma3dL],
         [dsigma4dL],
         [dsigma5dL]]).reshape((5, 1))

    J_sigma['WE'] = np.zeros((5, 1))
    J_sigma['NZ'] = np.zeros((5, 1))
    J_sigma['WO'] = np.zeros((5, 1))
    J_sigma['WFO'] = np.zeros((5, 1))

    return J_WT, J_WF, J_sigma, J_Theta


if __name__ == "__main__":

    analysis = Structures()
    run_tool(analysis, sys.argv)
