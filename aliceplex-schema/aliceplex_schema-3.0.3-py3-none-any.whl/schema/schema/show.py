from marshmallow import fields
from marshmallow.validate import Length, Range

from aliceplex.schema.model import Show
from aliceplex.schema.schema.actor import ActorSchema
from aliceplex.schema.schema.base import DataClassSchema

__all__ = ["ShowSchema", "ShowStrictSchema"]


class ShowSchema(DataClassSchema):
    """
    Schema for :class:`aliceplex.schema.model.Show`
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
    season_summary = fields.Dict(
        keys=fields.Int(),
        values=fields.Str(allow_none=False),
        allow_none=False
    )

    @property
    def data_class(self) -> type:
        return Show


class ShowStrictSchema(ShowSchema):
    """
    Strict schema for :class:`aliceplex.schema.model.Show`
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
    rating = fields.Float(validate=Range(min=0, max=10), allow_none=True)
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
    season_summary = fields.Dict(
        keys=fields.Int(),
        values=fields.Str(allow_none=False),
        allow_none=False,
        required=True
    )
