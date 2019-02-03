from dataclasses import fields
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from aliceplex.schema import Actor
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

from aliceplex.serialize.base import Model, Serializer
from aliceplex.serialize.util import guess_model_type

__all__ = ["YmlSerializer"]


class YmlSerializer(Serializer):
    """
    Serialize model to YML.
    It supports `Show`, `Movie` and `Episode`, `Artist` and `Album`.
    """

    def _serialize(self, path: Path,
                   model: Dict[str, Any],
                   model_type: Type[Model]):
        convert_to_literal(model)
        model = sort(model, model_type)
        with open(path, "w", encoding="utf-8") as file:
            yaml = YAML()
            yaml.default_flow_style = False
            yaml.indent(mapping=2, sequence=4, offset=2)
            yaml.dump(model, file)

    def _deserialize(self, path: Path) \
            -> Optional[Tuple[Dict[str, Any], Type[Model]]]:
        with open(path, "r", encoding="utf-8") as file:
            yaml = YAML(typ="safe")
            model: Dict[str, Any] = yaml.load(file)

        model_type = guess_model_type(model)
        if model_type is not None:
            return model, model_type
        return None


def sort(model: Dict[str, Any], model_type: Type[Model]) -> Dict[str, Any]:
    """
    Sort the field order before serializing.
    If the type is not support model will be return directly.

    :param model: Model to be sort.
    :type model: Dict[str, Any]
    :param model_type: Type of the model.
    :type model_type: Type[Model]
    :return: Sorted model
    :rtype: Dict[str, Any]
    """
    if not isinstance(model, (dict, list)):
        return model

    order = [f.name for f in fields(model_type)]

    if model_type == Actor:
        order.remove("photo")
        order.append("photo")

    sort_model = {}
    for field in order:
        if field not in model:
            continue
        value = model[field]
        if isinstance(value, dict):
            model_type = guess_model_type(value)
            if model_type is not None:
                value = sort(value, model_type)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                model_type = guess_model_type(item)
                if model_type is not None:
                    value[i] = sort(item, model_type)
        sort_model[field] = value
    return sort_model


def convert_to_literal(model: Union[Dict[str, Any], List[str]]):
    """
    If a string in the model has linebreak, use literal string instead of
    escaping.

    :param model:  Model to be handle.
    :type model: Union[Dict[str, Any], List[str]]
    """
    if isinstance(model, dict):
        for key, value in model.items():
            if isinstance(value, str):
                if "\n" in value or key == "summary":
                    model[key] = LiteralScalarString(value)
            elif isinstance(value, (dict, list)):
                convert_to_literal(model[key])
    elif isinstance(model, list):
        for value, i in enumerate(model):
            if isinstance(value, str):
                if "\n" in value:
                    model[i] = LiteralScalarString(value)
            elif isinstance(value, (dict, list)):
                convert_to_literal(model[i])
