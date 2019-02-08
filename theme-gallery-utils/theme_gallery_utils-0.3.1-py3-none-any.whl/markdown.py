# -*- coding: utf-8 -*-

"""
Methods to produce markdown that matches the wiki.
"""

import os
from . import paths


def wiki_table(themes, video_modes):
    """Return the themes in a sorted and formatted wiki table."""

    template = "|{}| {:<{system}}| {:<{gamelist}}| {:<{mode}}|"

    spacings = {
        "name": 31,
        "system": 125,
        "gamelist": 134,
        "mode": 14,
    }

    system_url = ("<img src=\""
                  "https://raw.githubusercontent.com/"
                  "wetriner/es-theme-gallery/master/{}.png\""
                  " width=\"500\">")
    gamelist_url = ("<img src=\""
                    "https://raw.githubusercontent.com/"
                    "wetriner/es-theme-gallery/master/{}-gamelist.png\""
                    " width=\"500\">")

    output_file = os.path.join(paths.DATA, "wiki_table.md")
    with open(output_file, "w") as buf:

        for theme in themes:

            video_mode = video_modes.get(theme, "yes")
            row = template.format(
                pad_name(theme, spacings["name"]),
                system_url.format(theme),
                gamelist_url.format(theme),
                video_mode,
                **spacings
            )
            buf.write(row + "\n")


def pad_name(text, pad_length):
    """Pad text to the pad length with the character."""
    # since python prefers to pad left to be larger, deliberately reverse it
    if len(text) % 2 == 0:
        return "{:^{length}}".format(" " + text, length=pad_length)
    else:
        return "{:^{length}}".format(text, length=pad_length)
