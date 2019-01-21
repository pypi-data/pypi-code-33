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
from ssbjkadmos.config import root_tag, x_R, x_R__scr, x_R__val
from ssbjkadmos.tools.SsbjDiscipline import SsbjDiscipline
from ssbjkadmos.utils.execution import run_tool


class Objective(SsbjDiscipline):  # AbstractDiscipline

    @property
    def description(self):
        return u'Objective determination (scaled) for the SSBJ test case.'

    def generate_input_xml(self):
        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)

        xml_safe_create_element(doc, x_R, 528.91363)
        xml_safe_create_element(doc, x_R__scr, 528.91363)

        return etree.tostring(doc, encoding='utf-8', pretty_print=True, xml_declaration=True)

    def generate_output_xml(self):
        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)

        xml_safe_create_element(doc, x_R__val, 1.0)

        return etree.tostring(doc, encoding='utf-8', pretty_print=True, xml_declaration=True)

    @staticmethod
    def execute(in_file, out_file):
        doc = etree.parse(in_file)
        val = float(doc.xpath(x_R)[0].text)
        scaler = float(doc.xpath(x_R__scr)[0].text)
        scaled_value = val/scaler

        root = etree.Element(root_tag)
        doc = etree.ElementTree(root)
        xml_safe_create_element(doc, x_R__val, scaled_value)
        doc.write(out_file, encoding='utf-8', pretty_print=True, xml_declaration=True)


if __name__ == "__main__":

    analysis = Objective()
    run_tool(analysis, sys.argv)
