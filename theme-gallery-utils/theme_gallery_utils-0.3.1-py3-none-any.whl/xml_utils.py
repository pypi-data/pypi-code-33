# -*- coding: utf-8 -*-

"""
Module intended for creation of opml files from the theme list.
"""

import datetime
import logging
import os
import urllib.parse
import lxml.etree as ET
from . import paths

logger = logging.getLogger(__name__)


def create_opml_tree(theme_list):
    """Generate opml text from the theme list."""

    root = ET.Element("opml", {"version": "2.0"})
    body = ET.SubElement(root, "body")

    for user, repo in theme_list:

        # change branch for repos that don't use master as main
        if user == "InsecureSpike":
            branch = "v3.0-update"
        else:
            branch = "master"

        # create a path following the following format
        # https://github.com/user/repo/commits/branch.atom
        url_parts = [user, repo, "commits", branch + ".atom"]
        url = urllib.parse.urljoin("https://github.com", "/".join(url_parts))

        title = "{}:{}".format(user, repo)

        ET.SubElement(
            body, "outline",
            {
                "text": title,
                "type": "rss",
                "xmlUrl": url,
            }
        )

    tree = ET.ElementTree(root)

    return tree


def create_opml_file(themes_list):
    """Create an opml file from the opml text."""
    logger.info("Creating opml file")

    tree = create_opml_tree(themes_list)

    opml_path = os.path.join(paths.DATA, "commits.opml")

    # ensure directory exists
    os.makedirs(paths.DATA, exist_ok=True)

    tree.write(
        opml_path, encoding="utf-8", xml_declaration=True, pretty_print=True)


def update_gamelist_date(gamelist):
    """Update the release date in the passed gamelist file."""

    tree = ET.parse(gamelist)
    root = tree.getroot()

    today = datetime.datetime.today()
    for element in root.iterfind(".//releasedate"):
        element.text = today.strftime("%Y%m%dT%H%M%S")

    tree.write(
        gamelist, encoding="utf-8", xml_declaration=True, pretty_print=True)


def update_es_systems(config, theme_name):
    """Update es_systems to match the passed theme configuration."""

    # retrieve resolution name if it is defined
    try:
        system_name = config["theme_systems"][theme_name]
    except KeyError:
        system_name = config["defaults"]["system"]

    # update es_systems file with the system name
    systems_file = os.path.join(paths.EMULATIONSTATION, "es_systems.cfg")
    tree = ET.parse(systems_file)
    root = tree.getroot()

    for element in root:
        logger.debug("Iterating over root {}".format(element))
        if element.find("name").text == "atari2600":
            logger.debug("Found atari2600 name element")
            theme = element.find("theme")

            # only update the file if it is different
            if theme.text != system_name:
                logger.debug("theme text is different")
                theme.text = system_name

                tree.write(
                    systems_file,
                    encoding="utf-8",
                    xml_declaration=True,
                    pretty_print=True,
                )
            else:
                logger.debug("theme text is same")
