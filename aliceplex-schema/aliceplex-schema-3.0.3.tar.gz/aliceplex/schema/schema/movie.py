from marshmallow import fields
from marshmallow.validate import Length, Range

from aliceplex.schema.model import Movie
from aliceplex.schema.schema.actor import ActorSchema
from aliceplex.schema.schema.base import DataClassSchema
from aliceplex.schema.schema.person import PersonSchema, PersonStrictSchema

__all__ = ["MovieSchema", "MovieStrictSchema"]


class MovieSchema(DataClassSchema):
    """
    Schema for :class:`aliceplex.schema.model.Movie`
    """

    title = fields.Str(allow_none=True)
    sort_title = fields.Str(allow_none=True)
    original_title = fields.Str(allow_none=True)
    content_rating = fields.Str(allow_none=True)
    tagline = fields.List(fields.Str(allow_none=False), allow_none=False)
    studio = fields.List(fields.Str(allow_none=False), allow_none=False)
    aired = fields.Date(allow_none=True)
    summary = fields.Str(allow_none=True)
    rating = fields.Float(validate=Range(min=0, max=10), allow_none=True)
    genres = fields.List(fields.Str(allow_none=False), allow_none=False)
    collections = fields.List(fields.Str(allow_none=False), allow_none=False)
    actors = fields.List(
        fields.Nested(ActorSchema, allow_none=False),
        allow_none=False
    )
    writers = fields.List(
        fields.Pluck(PersonSchema, "name", allow_none=False),
        allow_none=False
    )
    directors = fields.List(
        fields.Pluck(PersonSchema, "name", allow_none=False),
        allow_none=False
    )

    @property
    def data_class(self) -> type:
        return Movie


class MovieStrictSchema(MovieSchema):
    """
    Strict schema for :class:`aliceplex.schema.model.Movie`
    """

    title = fields.Str(allow_none=False, required=True)
    sort_title = fields.Str(allow_none=False, required=True)
    original_title = fields.Str(allow_none=False, required=True)
    content_rating = fields.Str(allow_none=False, required=True)
    tagline = fields.List(
        fields.Str(allow_none=False),
        allow_none=False,
        required=True
    )
    studio = fields.List(
        fields.Str(allow_none=False),
        validate=Length(min=1),
        allow_none=False,
        required=True
    )
    aired = fields.Date(allow_none=False, required=True)
    summary = fields.Str(allow_none=False, required=True)
    rating = fields.Float(validate=Range(min=0, max=10), allow_none=False)
    genres = fields.List(
        fields.Str(allow_none=False),
        validate=Length(min=1),
        allow_none=False,
        required=True
    )
    collections = fields.List(
        fields.Str(allow_none=False),
        validate=Length(min=1),
        allow_none=False,
        required=True
    )
    actors = fields.List(
        fields.Nested(ActorSchema, allow_none=False),
        validate=Length(min=1),
        allow_none=False,
        required=True
    )
    writers = fields.List(
        fields.Pluck(PersonStrictSchema, "name", allow_none=False),
        allow_none=False,
        required=True
    )
    directors = fields.List(
        fields.Pluck(PersonStrictSchema, "name", allow_none=False),
        allow_none=False,
        required=True
    )
