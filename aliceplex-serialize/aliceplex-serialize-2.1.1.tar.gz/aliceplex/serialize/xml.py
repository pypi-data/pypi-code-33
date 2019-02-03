from dataclasses import Field, fields
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type
from xml.etree.ElementTree import parse

from aliceplex.schema import Album, Artist, Episode, Movie, Show

from aliceplex.serialize.base import Model, Serializer
from aliceplex.serialize.util import etree_to_dict

__all__ = ["XmlSerializer"]

show_mapping = {
    "original_title": "originaltitle",
    "sort_title": "sorttitle",
    "collections": "set",
    "content_rating": "mpaa",
    "summary": "plot",
    "aired": "premiered",
    "genres": "genre",
    "actors": "actor"
}

movie_mapping = {
    "original_title": "originaltitle",
    "sort_title": "sorttitle",
    "collections": "set",
    "content_rating": "mpaa",
    "summary": "plot",
    "aired": "releasedate",
    "directors": "director",
    "writers": "writer",
    "genres": "genre",
    "actors": "actor"
}

episode_mapping = {
    "content_rating": "mpaa",
    "summary": "plot",
    "directors": "director",
    "writers": "writer"
}

actor_mapping = {
    "photo": "thumb"
}

artist_mapping = {
    "genres": "genre",
    "collections": "set"
}

album_mapping = {
    "genres": "genre",
    "collections": "set"
}


class XmlSerializer(Serializer):
    """
    Deserialize model to XML for AvalonXmlAgent.bundle to read.
    """

    def _serialize(self, path: Path,
                   model: Dict[str, Any],
                   model_type: Type[Model]):
        pass

    def _deserialize(self, path: Path) \
            -> Optional[Tuple[Dict[str, Any], Type[Model]]]:
        root = parse(path).getroot()
        model = etree_to_dict(root)[root.tag]

        if root.tag == "episodedetails":
            mapping = _inverse_map(episode_mapping)
            return _map_fields(model, mapping, Episode)
        if root.tag == "tvshow":
            mapping = _inverse_map(show_mapping)
            return _map_fields(model, mapping, Show)
        if root.tag == "movie":
            mapping = _inverse_map(movie_mapping)
            return _map_fields(model, mapping, Movie)
        if root.tag == "artist":
            mapping = _inverse_map(artist_mapping)
            return _map_fields(model, mapping, Artist)
        if root.tag == "album":
            mapping = _inverse_map(album_mapping)
            return _map_fields(model, mapping, Album)
        return None


def _map_fields(model: Dict[str, Any],
                mapping: Dict[str, str],
                model_type: Type[Model]) -> Tuple[Dict[str, Any], Type[Model]]:
    new_model = {}
    model_fields: List[Field] = fields(model_type)
    fields_map = {}
    for field in model_fields:
        fields_map[field.name] = field
    for key, value in model.items():
        if key in mapping:
            new_key = mapping[key]
        else:
            new_key = key
        if new_key in fields_map.keys():
            new_model[new_key] = _cast_field(fields_map[new_key], value)
    return new_model, model_type


def _cast_field(field: Field, value: str) -> Any:
    field_type = field.type  # Handle normal type
    origin = getattr(field_type, "__origin__", None)  # Handle list
    args = getattr(field_type, "__args__", ())  # Handle Union
    if list in (field_type, origin):
        new_value = value if isinstance(value, list) else [value]
        if len(args) == 1 and args[0] in (float, int):
            return [args[0](v) for v in new_value]
        return new_value
    if value == "" or value is None:
        return None
    if int in (field_type, origin) or (len(args) == 1 and int in args):
        return int(value)
    if float in (field_type, origin) or (len(args) == 1 and float in args):
        return float(value)
    return value


def _inverse_map(mapping: Dict[str, Any]) -> Dict[str, Any]:
    return {v: k for k, v in mapping.items()}
