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
from ssbjkadmos.config import root_tag, x_WT, x_h, x_M, x_fin, x_SFC, x_WF, x_R
from ssbjkadmos.tools.SsbjDiscipline import SsbjDiscipline
from ssbjkadmos.utils.execution import run_tool
from kadmos.utilities.xml_utils_openlego import xml_safe_create_element


class Performance(SsbjDiscipline):  # AbstractDiscipline

    @property
    def description(self):
        return u'Performance analysis discipline of the SSBJ test case.'

    @property
    def supplies_partials(self):
        return True

    def generate_input_xml(self):
        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)

        xml_safe_create_element(doc, x_h, 45000.0)
        xml_safe_create_element(doc, x_M, 1.6)
        xml_safe_create_element(doc, x_fin, 4.093062)
        xml_safe_create_element(doc, x_SFC, 1.12328)
        xml_safe_create_element(doc, x_WT, 49909.58578)
        xml_safe_create_element(doc, x_WF, 7306.20261)

        return etree.tostring(doc, encoding='utf-8', pretty_print=True, xml_declaration=True)

    def generate_output_xml(self):
        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)

        xml_safe_create_element(doc, x_R, 528.91363)

        return etree.tostring(doc, encoding='utf-8', pretty_print=True, xml_declaration=True)

    def generate_partials_xml(self):
        partials = Partials()
        partials.declare_partials(x_R, [x_h, x_M, x_fin, x_SFC, x_WT, x_WF])
        return partials.get_string()

    @staticmethod
    def execute(in_file, out_file):
        doc = etree.parse(in_file)
        z1 = float(doc.xpath(x_h)[0].text)
        z2 = float(doc.xpath(x_M)[0].text)
        fin = float(doc.xpath(x_fin)[0].text)
        SFC = float(doc.xpath(x_SFC)[0].text)
        WT = float(doc.xpath(x_WT)[0].text)
        WF = float(doc.xpath(x_WF)[0].text)

        # Execute ONERA performance function
        R = performance(np.array([0.0, z1, z2, 0.0, 0.0, 0.0]), fin, SFC, WT, WF)

        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)
        xml_safe_create_element(doc, x_R, R)
        doc.write(out_file, encoding='utf-8', pretty_print=True, xml_declaration=True)

    @staticmethod
    def linearize(in_file, partials_file):
        doc = etree.parse(in_file)
        z1 = float(doc.xpath(x_h)[0].text)
        z2 = float(doc.xpath(x_M)[0].text)
        fin = float(doc.xpath(x_fin)[0].text)
        SFC = float(doc.xpath(x_SFC)[0].text)
        WT = float(doc.xpath(x_WT)[0].text)
        WF = float(doc.xpath(x_WF)[0].text)

        # Execute ONERA partials function
        J_R = performance_partials(dict(z=np.array([0.0, z1, z2, 0.0, 0.0, 0.0]),
                                        fin =fin,
                                        SFC=SFC,
                                        WT=WT,
                                        WF=WF))

        # Declare and write partials
        partials = Partials()
        partials.declare_partials(x_R,
                                  [x_h, x_M, x_fin, x_SFC, x_WT, x_WF],
                                  [J_R['z'][0, 1], J_R['z'][0, 2], J_R['fin'], J_R['SFC'], J_R['WT'], J_R['WF']])
        partials.write(partials_file)


def performance(Z, fin, SFC, WT, WF):
    # Performance calculation as taken from the ONERA repository
    if Z[1] <= 36089.:
        theta = 1.0 - 6.875E-6 * Z[1]
    else:
        theta = 0.7519
    R = 661.0 * np.sqrt(theta) * Z[2] * fin / SFC * np.log(abs(WT / (WT - WF)))
    return R


def performance_partials(inputs):
    # Performance partials calculation as taken from the ONERA repository
    # Adjustments: removed "self" and "scalers" and replaced "J" for "J_R"
    Z = inputs['z']
    fin = inputs['fin']
    SFC = inputs['SFC']
    WT = inputs['WT']
    WF = inputs['WF']

    if Z[1] <= 36089:
        theta = 1.0 - 6.875E-6 * Z[1]
        dRdh = -0.5 * 661.0 * theta ** -0.5 * 6.875e-6 * Z[2] * fin \
               / SFC * np.log(abs(WT / (WT - WF)))
    else:
        theta = 0.7519
        dRdh = 0.0

    dRdM = 661.0 * np.sqrt(theta) * fin / SFC * np.log(abs(WT / (WT - WF)))

    J_R = dict()
    J_R['z'] = np.zeros((1, 6))
    J_R['z'][0, 1] = np.array([dRdh])
    J_R['z'][0, 2] = np.array([dRdM])
    dRdfin = 661.0 * np.sqrt(theta) * Z[2] / SFC * np.log(abs(WT / (WT - WF)))
    J_R['fin'] = np.array([dRdfin])
    dRdSFC = -661.0 * np.sqrt(theta) * Z[2] * fin / SFC ** 2 * np.log(abs(WT / (WT - WF)))
    J_R['SFC'] = np.array([dRdSFC])
    dRdWT = 661.0 * np.sqrt(theta) * Z[2] * fin / SFC * -WF / (WT * (WT - WF))
    J_R['WT'] = np.array([dRdWT])
    dRdWF = 661.0 * np.sqrt(theta) * Z[2] * fin / SFC * 1.0 / (WT - WF)
    J_R['WF'] = np.array([dRdWF])
    return J_R


if __name__ == "__main__":
    analysis = Performance()
    run_tool(analysis, sys.argv)
