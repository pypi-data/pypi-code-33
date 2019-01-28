#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""This file is a simple script to convert a xodr file
to a lanelet .xml file."""

import sys
import matplotlib.pyplot as plt
from lxml import etree
from commonroad.scenario.scenario import Scenario
from commonroad.visualization.draw_dispatch_cr import draw_object

from opendrive2lanelet.opendriveparser.elements.opendrive import OpenDrive
from opendrive2lanelet.opendriveparser.parser import parse_opendrive
from opendrive2lanelet.network import Network
from opendrive2lanelet.io.extended_file_writer import ExtendedCommonRoadFileWriter

__author__ = "Benjamin Orthen, Stefan Urban"
__copyright__ = "TUM Cyber-Physical Systems Group"
__credits__ = ["Priority Program SPP 1835 Cooperative Interacting Automobiles"]
__version__ = "1.0a0"
__maintainer__ = "Benjamin Orthen"
__email__ = "commonroad-i06@in.tum.de"
__status__ = "In Development"


# TODO: include --debug option
# TODO: include click command line options: --help, (maybe --verbose)
# TODO: include check-validity option
# TODO: add option --visualize to show output


def visualize(scenario: Scenario):
    """Visualize a created scenario by plotting it
    with matplotlib.

    Args:
      scenario: The scenario which should be plotted.

    Returns:
      None

    """

    # set plt settings
    plt.style.use("classic")
    plt.figure(figsize=(8, 4.5))
    plt.gca().axis("equal")
    # plot_limits = [-80, 80, -60, 30]
    # plot scenario
    # TODO: bug, type checking in draw_object
    draw_object(scenario)
    plt.show()


def convert_opendrive(opendrive: OpenDrive) -> Scenario:
    """Convert an existing OpenDrive object to a CommonRoad Scenario.

    Args:
      opendrive: Parsed in OpenDrive map.
    Returns:
      A commonroad scenario with the map represented by lanelets.
    """
    road_network = Network()
    road_network.load_opendrive(opendrive)

    return road_network.export_commonroad_scenario()


def main():
    """Helper function to convert an xodr to a lanelet file
    script uses sys.argv[1] as file to be converted

    Note:
      This is still under development.

    """
    if len(sys.argv) == 1 or sys.argv[1] == "--help":
        print(
            """Usage: convert.py input_file output_name.
        If no output_name is specified, output_file has name of input_file."""
        )
        exit(0)

    with open("{}".format(sys.argv[1]), "r") as file_in:
        opendrive = parse_opendrive(etree.parse(file_in).getroot())

    scenario = convert_opendrive(opendrive)

    writer = ExtendedCommonRoadFileWriter(
        scenario, source="OpenDRIVE 2 Lanelet Converter"
    )
    if len(sys.argv) == 3:
        output_name = sys.argv[2]
    else:
        output_name = sys.argv[1].rpartition(".")[0]  # only name of file

    with open("{}.xml".format(output_name), "w") as file_out:
        writer.write_scenario_to_file_io(file_out)


if __name__ == "__main__":
    main()
