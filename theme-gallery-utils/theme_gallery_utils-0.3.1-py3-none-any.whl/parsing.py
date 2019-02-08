# -*- coding: utf-8 -*-

"""
Download and parse esthemes into an organized list.
"""

import logging
import re
import urllib.request

logger = logging.getLogger(__name__)


def download_esthemes():
    """Download esthemes from github."""
    url = (
        "https://raw.githubusercontent.com/RetroPie/RetroPie-Setup/master/"
        "scriptmodules/supplementary/esthemes.sh"
    )
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode("utf-8")

    return text


def parse_esthemes(
            config,
            esthemes_text,
            full_repo_name=True,
            theme_names=None,
            sort=True,
        ):
    """Parse themes into an organized list."""

    # regex pattern for retrieving repo info from file text
    re_themes = r"""
    (?s)               # dot match newlines
    local\sthemes=\(\n # start matching at themes definition including newline
    (.+?\n)            # remember group for matching section and end on newline
    \s+\)              # end at first closing parenthesis including whitespace
    """

    # retrieve section of text that defines the theme repos
    themes_group = re.search(re_themes, esthemes_text, re.VERBOSE).group(1)

    # strip whitespace and quotes, split, fix name and append into a list
    themes_list = []
    for line in themes_group.splitlines():
        user_name, repo_name = line.strip(" '").split()

        if repo_name in config["ignored_themes"]:
            continue

        if full_repo_name:
            full_repo_name = "es-theme-" + repo_name

        if not theme_names:
            themes_list.append((user_name, full_repo_name))
        elif theme_names and repo_name in theme_names:
            themes_list.append((user_name, full_repo_name))

    if sort:
        return sorted(themes_list, key=lambda tup: tup[1])
    else:
        return themes_list


def get_esthemes(config, file=None, theme_names=None, sort=True):
    """Download and parse esthemes into a sorted list."""
    # read the file into a list of theme names
    if file:
        with open(file, "r") as buf:
            theme_names = [line.rstrip() for line in buf if line != "\n"]

    esthemes_script = download_esthemes()
    esthemes = parse_esthemes(
        config, esthemes_script, theme_names=theme_names, sort=sort)

    return esthemes


def get_esthemes_names(config, sort=True, **kwargs):
    """Download and parse esthemes into a sorted list of names only."""
    esthemes = get_esthemes(config, sort=sort, **kwargs)
    repo_names = tuple(zip(*esthemes))[1]
    return [n.replace("es-theme-", "") for n in repo_names]


if __name__ == "__main__":
    pass
