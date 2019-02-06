import json
import os
import uuid
from enum import auto, unique
from typing import Any, Optional, Callable

import ipywidgets as widgets
import psutil
from IPython.core.display import display, HTML
from IPython.display import display_javascript, display_html, JSON, Javascript
from cortex_profiles.utils import EnumWithNamesAsDefaultValue


def map_object(object:Optional[Any], method:Callable[[Any], Any], default:Optional[Any]=None) -> Any:
    return method(object) if object is not None else default


# def default(value:Optional[Any], default:Optional[Any]=None, default_factory:Callable[[Any], Any]=None) -> Any:
#     if default:
#         return value if value is not None else default
#     if default_factory:
#         return value if value


def button(text):
    return widgets.Checkbox(
        value=False,
        description=text,
        disabled=False
    )


def container(stuff):
    return widgets.VBox(stuff)


def to_output(content):
    """
    returns how ipython displays content by default
    """
    x = widgets.Output()
    with x:
        display(content)
    return x


def tab_with_content(content_dict):
    """
    Creates a tab with dicts where keys are tabnames and content are the content of the tab ...
    """
    tab = widgets.Tab()
    keys = list(content_dict.keys())
    tab.children = [content_dict[k] for k in keys]
    for (i,title) in enumerate(keys):
        tab.set_title(i, title)
    return tab


def set_id_for_dom_element_of_output_for_current_cell(_id):
    display(Javascript('console.log(element.get(0)); element.get(0).id = "{}";'.format(_id)))


class InteractableJsonForNotebooks(object):
    def __init__(self, json_data):
        if isinstance(json_data, (dict, list)):
            self.json_str = json.dumps(json_data)
        elif isinstance(json_data, JSON):
            self.json_str = json.dumps(json_data.data)
        else:
            self.json_str = json_data
        self.uuid = str(uuid.uuid4())

    def _ipython_display_(self):
        display_html('<div id="{}" style="height: 600px; width:100%;"></div>'.format(self.uuid), raw=True)

        js = """
            require(["https://rawgit.com/caldwell/renderjson/master/renderjson.js"], function() {{
                renderjson.set_icons('+', '-');
                renderjson.set_show_to_level("2");
                document.getElementById('{}').appendChild(renderjson({}))
            }});
        """

        display_javascript(js.format(self.uuid, self.json_str), raw=True)


def widescreen():
    return display(HTML("<style>.container { width:90% !important; }</style>"))

@unique
class Runtimes(EnumWithNamesAsDefaultValue):
    LAB = auto()
    NOTEBOOK = auto()
    SKILL = auto()


# TODO - This is NOT CLEAN!
#   - we are detecting if jupyter lab is running based on the name of the parent binary that kicked off the notebook ...
def detect_runtime() -> Runtimes:
    parent_pid = os.getppid()
    if parent_pid == 0:
        return Runtimes.SKILL
    parent_process = psutil.Process(parent_pid)
    if any(["jupyter-lab" in x for x in parent_process.cmdline()]):
        return Runtimes.LAB
    return Runtimes.NOTEBOOK


def return_json_based_on_runtime(runtime:Runtimes=detect_runtime()):
    if runtime == Runtimes.SKILL:
        return lambda x: x # return json as is ...
    elif runtime == Runtimes.LAB:
        return JSON
    elif runtime == Runtimes.NOTEBOOK:
        return InteractableJsonForNotebooks


InteractableJson = return_json_based_on_runtime()