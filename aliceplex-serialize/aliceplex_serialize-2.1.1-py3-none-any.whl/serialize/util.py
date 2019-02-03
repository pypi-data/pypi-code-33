from collections import defaultdict
from typing import Any, Dict, Optional, Type
from xml.etree.ElementTree import Element

from aliceplex.schema import Actor, Album, Artist, Episode, Movie, Person, Show

from aliceplex.serialize.base import Model


def etree_to_dict(element: Element) -> Dict[str, Any]:
    """
    Convert a Element to dict

    :param element: Tree to be converted.
    :type element: ElementTree
    :return: Converted dict.
    :rtype: Dict[str, Any]
    """
    model = {element.tag: {} if element.attrib else None}
    children = list(element)
    if children:
        new_dict = defaultdict(list)
        for child in map(etree_to_dict, children):
            for key, value in child.items():
                new_dict[key].append(value)
        model = {element.tag: {key: value[0] if len(value) == 1 else value
                               for key, value in new_dict.items()}}
    if element.attrib:
        model[element.tag].update(("@" + key, value)
                                  for key, value in element.attrib.items())
    if element.text:
        text = element.text.strip()
        if children or element.attrib:
            if text:
                model[element.tag]["#text"] = text
        else:
            model[element.tag] = text
    return model


def guess_model_type(model: Dict[str, Any]) -> Optional[Type[Model]]:
    """
    Guess the model type by the fields in the model.
    Return no if it failed to guesses.

    :param model: Model to be guessed.
    :type model: Dict[str, Any]
    :return: Guessed model type.
    :rtype: Optional[Type[Model]]
    """
    model_type = None
    if "actors" in model and "directors" not in model:
        model_type = Show
    elif "actors" in model and "directors" in model:
        model_type = Movie
    elif "actors" not in model and "directors" in model:
        model_type = Episode
    elif "role" in model:
        model_type = Actor
    elif "photo" in model:
        model_type = Person
    elif "similar" in model:
        model_type = Artist
    elif "role" not in model and "similar" not in model and "aired" in model:
        model_type = Album
    return model_type
