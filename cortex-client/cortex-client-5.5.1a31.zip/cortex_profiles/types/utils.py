import copy
from typing import Tuple, Union

import attr
import pydash


ID_DESCRIPTION = "What is the id of this peice of data?"
CONTEXT_DESCRIPTION = "What is the type of this piece of data?"
VERSION_DESCRIPTION = "What version of the CAMEL spec is this piece of data based on?"
ATTRIBUTE_SUMMARY_DESCRIPTION = "How can the value of this attribute be concisely expressed?"


def describableAttrib(description:str=None, **kwargs) -> dict:
    attrib_args = copy.deepcopy(kwargs)
    if description:
        attrib_args["metadata"] = pydash.merge(attrib_args.get("metadata", {}), {"description": description})
    return attr.attrib(**attrib_args)


def get_types_of_union(union:Union) -> Tuple[type]:
    return union.__args__


def str_or_context(input:Union[str,type]) -> str:
    return input if isinstance(input, str) else attr.fields(input).context.default
