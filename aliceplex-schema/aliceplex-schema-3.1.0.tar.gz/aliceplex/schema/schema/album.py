from marshmallow import fields
from marshmallow.validate import Length

from aliceplex.schema.model import Album
from aliceplex.schema.schema.base import DataClassSchema

__all__ = ["AlbumSchema", "AlbumStrictSchema"]


class AlbumSchema(DataClassSchema):
    """
    Schema for :class:`aliceplex.schema.model.Album`
    """

    summary = fields.Str(allow_none=True)
    aired = fields.Date(allow_none=True)
    genres = fields.List(fields.Str(allow_none=True), allow_none=True)
    collections = fields.List(fields.Str(allow_none=True), allow_none=True)

    @property
    def data_class(self) -> type:
        return Album


class AlbumStrictSchema(AlbumSchema):
    """
    Strict schema for :class:`aliceplex.schema.model.Album`
    """

    summary = fields.Str(allow_none=False, required=True)
    aired = fields.Date(allow_none=False, required=True)
    genres = fields.List(
        fields.Str(allow_none=False),
        validate=Length(min=1),
        allow_none=False,
        required=True)
    collections = fields.List(
        fields.Str(allow_none=False),
        allow_none=False,
        required=True
    )
