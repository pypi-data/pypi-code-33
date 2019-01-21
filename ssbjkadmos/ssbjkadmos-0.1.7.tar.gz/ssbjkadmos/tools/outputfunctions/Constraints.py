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

from lxml import etree

from kadmos.utilities.xml_utils_openlego import xml_safe_create_element
from ssbjkadmos.config import *
from ssbjkadmos.tools.SsbjDiscipline import SsbjDiscipline
from ssbjkadmos.utils.execution import run_tool


class Constraints(SsbjDiscipline):

    @property
    def description(self):
        return u'Constraint determination (scaled) for the SSBJ test case.'

    def generate_input_xml(self):
        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)

        # Sigmas and Theta
        xml_safe_create_element(doc, x_sigma1, 1.12255)
        xml_safe_create_element(doc, x_sigma2, 1.08170213)
        xml_safe_create_element(doc, x_sigma3, 1.0612766)
        xml_safe_create_element(doc, x_sigma4, 1.04902128)
        xml_safe_create_element(doc, x_sigma5, 1.04085106)
        xml_safe_create_element(doc, x_Theta, 0.950978)
        xml_safe_create_element(doc, x_sigma1__scr, 1.0)
        xml_safe_create_element(doc, x_sigma2__scr, 1.0)
        xml_safe_create_element(doc, x_sigma3__scr, 1.0)
        xml_safe_create_element(doc, x_sigma4__scr, 1.0)
        xml_safe_create_element(doc, x_sigma5__scr, 1.0)
        xml_safe_create_element(doc, x_Theta__scr, 1.0)

        # dpdx
        xml_safe_create_element(doc, x_dpdx, 1.0)
        xml_safe_create_element(doc, x_dpdx__scr, 1.0)

        # ESF, DT, Temp
        xml_safe_create_element(doc, x_ESF, 1.0)
        xml_safe_create_element(doc, x_ESF__scr, 1.0)
        xml_safe_create_element(doc, x_DT, 0.278366)
        xml_safe_create_element(doc, x_DT__scr, 1.0)
        xml_safe_create_element(doc, x_Temp, 1.0)
        xml_safe_create_element(doc, x_Temp__scr, 1.0)

        return etree.tostring(doc, encoding='utf-8', pretty_print=True, xml_declaration=True)

    def generate_output_xml(self):
        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)

        # Sigmas and Theta
        xml_safe_create_element(doc, x_sigma1__val, 1.12255)
        xml_safe_create_element(doc, x_sigma2__val, 1.08170213)
        xml_safe_create_element(doc, x_sigma3__val, 1.0612766)
        xml_safe_create_element(doc, x_sigma4__val, 1.04902128)
        xml_safe_create_element(doc, x_sigma5__val, 1.04085106)
        xml_safe_create_element(doc, x_Theta__val, 0.950978)

        # dpdx
        xml_safe_create_element(doc, x_dpdx__val, 1.0)

        # ESF, DT, Temp
        xml_safe_create_element(doc, x_ESF__val, 1.0)
        xml_safe_create_element(doc, x_DT__val, 0.278366)
        xml_safe_create_element(doc, x_Temp__val, 1.0)

        return etree.tostring(doc, encoding='utf-8', pretty_print=True, xml_declaration=True)

    @staticmethod
    def execute(in_file, out_file):
        doc_in = etree.parse(in_file)

        terms = ['sigma1', 'sigma2', 'sigma3', 'sigma4', 'sigma5', 'Theta',
                 'dpdx',
                 'ESF', 'DT', 'Temp']

        root = etree.Element(root_tag)
        doc_out = etree.ElementTree(root)

        for term in terms:
            val = float(doc_in.xpath(globals()["x_" + term])[0].text)
            scaler = float(doc_in.xpath(globals()["x_" + term+"__scr"])[0].text)
            scaled_value = val/scaler
            xml_safe_create_element(doc_out, globals()["x_" + term + "__val"], scaled_value)
        doc_out.write(out_file, encoding='utf-8', pretty_print=True, xml_declaration=True)


if __name__ == "__main__":

    analysis = Constraints()
    run_tool(analysis, sys.argv)
