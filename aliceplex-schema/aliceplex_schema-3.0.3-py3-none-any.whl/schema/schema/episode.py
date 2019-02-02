from marshmallow import fields
from marshmallow.validate import Length, Range

from aliceplex.schema.model import Episode
from aliceplex.schema.schema.base import DataClassSchema
from aliceplex.schema.schema.person import PersonSchema, PersonStrictSchema

__all__ = ["EpisodeSchema", "EpisodeStrictSchema"]


class EpisodeSchema(DataClassSchema):
    """
    Schema for :class:`aliceplex.schema.model.Episode`
    """

    title = fields.List(fields.Str(allow_none=False), allow_none=False)
    aired = fields.Date(allow_none=True)
    content_rating = fields.Str(allow_none=True)
    summary = fields.Str(allow_none=True)
    directors = fields.List(
        fields.Pluck(PersonSchema, "name", allow_none=False),
        allow_none=False
    )
    writers = fields.List(
        fields.Pluck(PersonSchema, "name", allow_none=False),
        allow_none=False
    )
    rating = fields.Float(validate=Range(min=0, max=10), allow_none=True)

    @property
    def data_class(self) -> type:
        return Episode


class EpisodeStrictSchema(EpisodeSchema):
    """
    Strict schema for :class:`aliceplex.schema.model.Episode`
    """

    title = fields.List(
        fields.Str(allow_none=False),
        validate=Length(min=1),
        allow_none=False,
        required=True
    )
    aired = fields.Date(allow_none=True)
    content_rating = fields.Str(allow_none=False, required=True)
    summary = fields.Str(allow_none=False, required=True)
    directors = fields.List(
        fields.Pluck(PersonStrictSchema, "name", allow_none=False),
        allow_none=False,
        required=True
    )
    writers = fields.List(
        fields.Pluck(PersonStrictSchema, "name", allow_none=False),
        allow_none=False,
        required=True
    )
    rating = fields.Float(validate=Range(min=0, max=10), allow_none=True)
