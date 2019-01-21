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
from ssbjkadmos.config import root_tag, x_h, x_M, x_ESF, x_D, x_Temp, x_SFC, x_WE, x_DT, x_WBE, x_T
from ssbjkadmos.tools.SsbjDiscipline import SsbjDiscipline
from ssbjkadmos.utils.execution import run_tool
from kadmos.utilities.xml_utils_openlego import xml_safe_create_element

from ssbjkadmos.utils.math import polynomial_function, get_d_dict


class Propulsion(SsbjDiscipline):  # AbstractDiscipline

    @property
    def description(self):
        return u'Propulsion analysis discipline of the SSBJ test case.'

    @property
    def supplies_partials(self):
        return True

    def generate_input_xml(self):
        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)

        xml_safe_create_element(doc, x_h, 45000.0)
        xml_safe_create_element(doc, x_M, 1.6)
        xml_safe_create_element(doc, x_T, 0.3126)
        xml_safe_create_element(doc, x_D, 12193.7018)
        xml_safe_create_element(doc, x_WBE, 4360.)

        return etree.tostring(doc, encoding='utf-8', pretty_print=True, xml_declaration=True)

    def generate_output_xml(self):
        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)

        xml_safe_create_element(doc, x_Temp, 1.0)
        xml_safe_create_element(doc, x_ESF, 1.0)
        xml_safe_create_element(doc, x_SFC, 1.12328)
        xml_safe_create_element(doc, x_WE, 5748.915355)
        xml_safe_create_element(doc, x_DT, 0.278366)

        return etree.tostring(doc, encoding='utf-8', pretty_print=True, xml_declaration=True)

    def generate_partials_xml(self):
        partials = Partials()
        partials.declare_partials(x_Temp, [x_h, x_M, x_T, x_D, x_WBE])
        partials.declare_partials(x_ESF, [x_h, x_M, x_T, x_D, x_WBE])
        partials.declare_partials(x_SFC, [x_h, x_M, x_T, x_D, x_WBE])
        partials.declare_partials(x_WE, [x_h, x_M, x_T, x_D, x_WBE])
        partials.declare_partials(x_DT, [x_h, x_M, x_T, x_D, x_WBE])
        return partials.get_string()

    @staticmethod
    def execute(in_file, out_file):
        doc = etree.parse(in_file)
        z1 = float(doc.xpath(x_h)[0].text)
        z2 = float(doc.xpath(x_M)[0].text)
        Xpro = float(doc.xpath(x_T)[0].text)
        D = float(doc.xpath(x_D)[0].text)
        WBE = float(doc.xpath(x_WBE)[0].text)

        Temp, ESF, SFC, WE, DT = propulsion(Xpro, np.array([0.0, z1, z2, 0.0, 0.0, 0.0]), D, WBE)

        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)
        xml_safe_create_element(doc, x_Temp, Temp)
        xml_safe_create_element(doc, x_ESF, ESF)
        xml_safe_create_element(doc, x_SFC, SFC)
        xml_safe_create_element(doc, x_WE, WE)
        xml_safe_create_element(doc, x_DT, DT)
        doc.write(out_file, encoding='utf-8', pretty_print=True, xml_declaration=True)

    @staticmethod
    def linearize(in_file, partials_file):
        doc = etree.parse(in_file)
        z1 = float(doc.xpath(x_h)[0].text)
        z2 = float(doc.xpath(x_M)[0].text)
        Xpro = float(doc.xpath(x_T)[0].text)
        D = float(doc.xpath(x_D)[0].text)
        WBE = float(doc.xpath(x_WBE)[0].text)

        # Execute ONERA partials function
        J_Temp, J_ESF, J_SFC, J_WE, J_DT = propulsion_partials(dict(z=np.array([0.0, z1, z2, 0.0, 0.0, 0.0]),
                                                                    x_pro=Xpro,
                                                                    D=D,
                                                                    WBE=WBE))

        # Declare and write partials
        partials = Partials()
        partials.declare_partials(x_Temp,
                                  [x_h, x_M, x_T, x_D, x_WBE],
                                  [J_Temp['z'][0, 1], J_Temp['z'][0, 2], J_Temp['x_pro'], J_Temp['D'], J_Temp['WBE']])
        partials.declare_partials(x_ESF,
                                  [x_h, x_M, x_T, x_D, x_WBE],
                                  [J_ESF['z'][0, 1], J_ESF['z'][0, 2], J_ESF['x_pro'], J_ESF['D'], J_ESF['WBE']])  # TODO: Add values
        partials.declare_partials(x_SFC,
                                  [x_h, x_M, x_T, x_D, x_WBE],
                                  [J_SFC['z'][0, 1], J_SFC['z'][0, 2], J_SFC['x_pro'], J_SFC['D'], J_SFC['WBE']])  # TODO: Add values
        partials.declare_partials(x_WE,
                                  [x_h, x_M, x_T, x_D, x_WBE],
                                  [J_WE['z'][0, 1], J_WE['z'][0, 2], J_WE['x_pro'], J_WE['D'], J_WE['WBE']])  # TODO: Add values
        partials.declare_partials(x_DT,
                                  [x_h, x_M, x_T, x_D, x_WBE],
                                  [J_DT['z'][0, 1], J_DT['z'][0, 2], J_DT['x_pro'], J_DT['D'], J_DT['WBE']])  # TODO: Add values
        partials.write(partials_file)


def propulsion(x_pro, Z, D, WBE):
    # Propulsion function from ONERA repository
    # Removed "pf" input and added "WBE" input
    Tbar = abs(x_pro) * 16168.6
    Temp = polynomial_function([Z[2], Z[1], abs(x_pro)], [2, 4, 2], [.25] * 3, "Temp")
    ESF = (D / 3.0) / Tbar
    SFC = 1.1324 + 1.5344 * Z[2] - 3.2956E-05 * Z[1] - 1.6379E-04 * Tbar \
          - 0.31623 * Z[2] ** 2 + 8.2138E-06 * Z[2] * Z[1] - 10.496E-5 * Tbar * Z[2] \
          - 8.574E-11 * Z[1] ** 2 + 3.8042E-9 * Tbar * Z[1] + 1.06E-8 * Tbar ** 2
    WE = 3.0 * WBE * abs(ESF) ** 1.05
    TUAbar = 11484.0 + 10856.0 * Z[2] - 0.50802 * Z[1] \
             + 3200.2 * (Z[2] ** 2) - 0.29326 * Z[2] * Z[1] + 6.8572E-6 * Z[1] ** 2
    DT = Tbar / TUAbar - 1.0
    return Temp, ESF, SFC, WE, DT


def propulsion_partials(inputs):
    # Propulsion partial calculation from ONERA repository
    # Removed self, J, scalers
    # Replaced pf for polynomial_function
    # Get d dictionary as static value

    # Changement de variable
    Z = inputs['z']
    Xpro = inputs['x_pro']
    WBE = inputs['WBE']
    Tbar = abs(Xpro) * 16168.6
    ESF = (inputs['D'] / 3.0) / Tbar
    TUAbar = 11484.0 + 10856.0 * Z[2] - 0.50802 * Z[1] \
             + 3200.2 * Z[2] ** 2 - 0.29326 * Z[2] * Z[1] + 6.8572E-6 * Z[1] ** 2
    pf_d = get_d_dict()
    ##############SFC
    J_SFC = dict()
    dSFCdT = -1.6379e-4 * 16168.6 - 10.496e-5 * 16168.6 * Z[2] \
             + 3.8042e-9 * 16168.6 * Z[1] + 2.0 * 1.06e-8 * 16168.6 ** 2 * Xpro
    J_SFC['x_pro'] = dSFCdT
    dSFCdh = -3.2956e-5 + 8.2138e-6 * Z[2] - 2.0 * 8.574e-11 * Z[1] + 3.8042e-9 * Tbar
    dSFCdM = 1.5344 - 2.0 * 0.31623 * Z[2] + 8.2138e-6 * Z[1] - 10.496e-5 * Tbar
    J_SFC['z'] = np.zeros((1, 6))
    J_SFC['z'][0, 1] = dSFCdh
    J_SFC['z'][0, 2] = dSFCdM
    J_SFC['D'] = np.array([[0]])
    J_SFC['WBE'] = np.array([[0.]])
    ###############ESF
    J_ESF = dict()
    dESFdT = (-inputs['D'] / 3.0) / (16168.6 * Xpro ** 2)
    J_ESF['x_pro'] = np.array(
        [[dESFdT]])
    J_ESF['z'] = np.zeros((1, 6))
    dESFdD = (1.0 / 3.0) / Tbar
    J_ESF['D'] = np.array([[dESFdD]])
    J_ESF['WBE'] = np.array([[0.]])
    ###############WE
    J_WE = dict()
    dWEdT = 3.0 * WBE * 1.05 * ESF ** 0.05 * dESFdT
    J_WE['x_pro'] = np.array([[dWEdT]])
    J_WE['z'] = np.zeros((1, 6))
    dWEdD = 3.0 * WBE * 1.05 * ESF ** 0.05 * dESFdD
    J_WE['D'] = np.array([[dWEdD]])
    J_WE['WBE'] = 3.0 * 1.05 * abs(ESF) ** 0.05
    ##############DT
    J_DT = dict()
    dDTdT = 16168.6 / TUAbar
    J_DT['x_pro'] = np.array([[dDTdT]])
    dDTdh = -(-0.50802 - 0.29326 * Z[2] + 2.0 * 6.8572e-6 * Z[1]) * TUAbar ** -2 * Tbar
    dDTdM = -(10856.0 + 2.0 * 3200.2 * Z[2] - 0.29326 * Z[1]) * TUAbar ** -2 * Tbar
    J_DT['z'] = np.zeros((1, 6))
    J_DT['z'][0, 1] = dDTdh
    J_DT['z'][0, 2] = dDTdM
    J_DT['D'] = np.array([[0.0]])
    J_DT['WBE'] = np.array([[0.0]])
    #############Temp
    J_Temp = dict()
    S_shifted, Ai, Aij = polynomial_function([Z[2], Z[1], abs(Xpro)], [2, 4, 2],
                                             [.25] * 3, "Temp", deriv=True)
    if abs(Xpro) / pf_d['Temp'][2] <= 1.25 and abs(Xpro) / pf_d['Temp'][2] >= 0.75:
        dSTdT = 1.0 / pf_d['Temp'][2]
    else:
        dSTdT = 0.0
    dSTdT2 = 2.0 * S_shifted[0, 2] * dSTdT
    dTempdT = Ai[2] * dSTdT + 0.5 * Aij[2, 2] * dSTdT2 \
              + Aij[0, 2] * S_shifted[0, 0] * dSTdT + Aij[1, 2] * S_shifted[0, 1] * dSTdT
    J_Temp['x_pro'] = np.array(
        [[dTempdT]]).reshape((1, 1))
    J_Temp['z'] = np.zeros((1, 6))
    if Z[1] <= 1.25 and Z[1] / pf_d['Temp'][1] >= 0.75:
        dShdh = 1.0 / pf_d['Temp'][1]
    else:
        dShdh = 0.0
    dShdh2 = 2.0 * S_shifted[0, 1] * dShdh
    dTempdh = Ai[1] * dShdh + 0.5 * Aij[1, 1] * dShdh2 \
              + Aij[0, 1] * S_shifted[0, 0] * dShdh + Aij[2, 1] * S_shifted[0, 2] * dShdh
    if Z[2] / pf_d['Temp'][0] <= 1.25 and Z[2] / pf_d['Temp'][0] >= 0.75:
        dSMdM = 1.0 / pf_d['Temp'][0]
    else:
        dSMdM = 0.0
    dSMdM2 = 2.0 * S_shifted[0, 0] * dSMdM
    dTempdM = Ai[0] * dSMdM + 0.5 * Aij[0, 0] * dSMdM2 \
              + Aij[1, 0] * S_shifted[0, 1] * dSMdM + Aij[2, 0] * S_shifted[0, 2] * dSMdM
    J_Temp['z'][0, 1] = dTempdh
    J_Temp['z'][0, 2] = dTempdM
    J_Temp['D'] = np.array([[0.0]])
    J_Temp['WBE'] = np.array([[0.0]])
    return J_Temp, J_ESF, J_SFC, J_WE, J_DT


if __name__ == "__main__":
    analysis = Propulsion()
    run_tool(analysis, sys.argv)
