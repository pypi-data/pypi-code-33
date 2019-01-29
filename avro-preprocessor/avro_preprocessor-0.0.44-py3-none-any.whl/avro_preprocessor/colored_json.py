"""
A module to pretty print colored JSON
"""
import json
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, cast, Optional, Union

from pygments import highlight
from pygments.formatters.terminal256 import TerminalTrueColorFormatter
from pygments.lexers.data import JsonLexer

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


@dataclass
class ColoredJson:
    """
    Pretty prints JSON on the terminal
    """
    lexer = JsonLexer()
    formatter = TerminalTrueColorFormatter(style='monokai')

    json_indent = 4

    @classmethod
    def highlight_json(cls, data: Union[Dict, OrderedDict], indent: Optional[int] = json_indent) \
            -> str:
        """
        Get a colored, highlighted version of a JSON string.
        :param data: The json to highlight
        :param indent: How much to indent fields in the JSON
        """
        json_text = json.dumps(data, indent=indent)
        return cast(str, highlight(json_text, cls.lexer, cls.formatter))
