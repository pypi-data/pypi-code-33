from dataclasses import fields, replace
from logging import getLogger
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Type, Union

from aliceplex.schema import Actor, ActorSchema, ActorStrictSchema, Album, \
    AlbumSchema, AlbumStrictSchema, Artist, ArtistSchema, ArtistStrictSchema, \
    Episode, EpisodeSchema, EpisodeStrictSchema, Movie, MovieSchema, \
    MovieStrictSchema, Person, PersonSchema, PersonStrictSchema, Show, \
    ShowSchema, ShowStrictSchema
from aliceplex.schema.format import normalize
from marshmallow import Schema

__all__ = ["Serializer", "Model"]
logger = getLogger(__name__)
Model = Union[Actor, Show, Episode, Movie, Album, Artist, Person]

convert_mapping = {
    Show: ["tagline", "studio", "genres", "collections"],
    Episode: ["title", "directors", "writers"],
    Movie: [
        "tagline", "studio", "genres", "collections", "directors", "writers"
    ],
    Artist: ["similar", "genres", "collections"],
    Album: ["genres", "collections"]
}


class Serializer:
    """
    Serializer interface for serializing and deserializing Plex model
    """

    schema_mapping = {
        Actor: ActorSchema,
        Episode: EpisodeSchema,
        Movie: MovieSchema,
        Show: ShowSchema,
        Album: AlbumSchema,
        Artist: ArtistSchema,
        Person: PersonSchema
    }

    strict_schema_mapping = {
        Actor: ActorStrictSchema,
        Episode: EpisodeStrictSchema,
        Movie: MovieStrictSchema,
        Show: ShowStrictSchema,
        Album: AlbumStrictSchema,
        Artist: ArtistStrictSchema,
        Person: PersonStrictSchema
    }

    @staticmethod
    def _normal(model: Model) -> Model:
        changes = {}
        for field in fields(model):
            value = getattr(model, field.name)
            if isinstance(value, str):
                value = normalize(value)
                changes[field.name] = value
            elif isinstance(value, list):
                changes[field.name] = []
                for item in value:
                    new_value = item
                    if isinstance(item, str):
                        new_value = normalize(item)
                    changes[field.name].append(new_value)
            elif isinstance(model, Show) and field.name == "season_summary":
                for season in value:
                    value[season] = normalize(value[season])
        return replace(model, **changes)

    def serialize(self, path: Union[Path, str],
                  model: Model,
                  validate: bool = False,
                  normal: bool = True):
        """
        Serialize a model object into a file.

        :param path: Serialized file path.
        :type path: Union[Path, str]
        :param model: Data model to be serialized.
        :type model: Union[Actor, Show, Episode, Movie]
        :param validate: Validate the data model with strict schema before
            serialization.
        :type validate: bool
        :param normal: Normalize string fields in model.
        :type normal: bool
        :raise ValueError: If model is either Actor, Show, Episode, Movie
        :raise ValidationError: If model fail validation
        """
        if isinstance(path, str):
            path = Path(path)
        model_type = type(model)
        schema = self._create_schema(model_type, validate)
        if normal:
            model = self._normal(model)
        dump = schema.dump(model)
        if validate:
            schema.validate(dump)
        self._serialize(path, dump, model_type)

    def _serialize(self, path: Path,
                   model: Dict[str, Any],
                   model_type: Type[Model]):
        raise NotImplementedError()

    def deserialize(self, path: Union[Path, str],
                    validate: bool = False,
                    normal: bool = False) -> Optional[Model]:
        """
        deserialize a file into a model object.

        :param path: File path to be deserialized.
        :type path: Union[Path, str]
        :param validate: Validate the data model with strict schema after
            deserialization.
        :type validate: bool
        :param normal: Normalize string fields in model.
        :type normal: bool
        :return: Data model if it successful deserialize the file.
        :rtype: Optional[Union[Actor, Show, Episode, Movie]]
        :raise ValidationError: If model fail validation
        """
        if isinstance(path, str):
            path = Path(path)
        result = self._deserialize(path)
        if result is None:
            return None
        model_dict, model_type = result
        schema = self._create_schema(model_type, validate)
        model = schema.load(model_dict)
        if normal:
            model = self._normal(model)
        return model

    def _deserialize(self, path: Path) \
            -> Optional[Tuple[Dict[str, Any], Type[Model]]]:
        raise NotImplementedError()

    def _create_schema(self, model_type: Type[Model],
                       strict: bool = True) -> Schema:
        if strict:
            schema = self._strict_schema(model_type)
        else:
            schema = self._schema(model_type)
        if schema is None:
            raise NotImplementedError("Not support model type")
        return schema()

    def _schema(self, model_type: Type[Model]) -> Optional[Type[Schema]]:
        return self.schema_mapping.get(model_type)

    def _strict_schema(self, model_type: Type[Model]) \
            -> Optional[Type[Schema]]:
        return self.strict_schema_mapping.get(model_type)
