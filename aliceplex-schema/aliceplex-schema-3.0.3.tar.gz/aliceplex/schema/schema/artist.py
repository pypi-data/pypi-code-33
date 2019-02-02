from marshmallow import fields
from marshmallow.validate import Length

from aliceplex.schema.model import Artist
from aliceplex.schema.schema.base import DataClassSchema

__all__ = ["ArtistSchema", "ArtistStrictSchema"]


class ArtistSchema(DataClassSchema):
    """
    Schema for :class:`aliceplex.schema.model.Artist`
    """

    summary = fields.Str(allow_none=True)
    similar = fields.List(fields.Str(allow_none=False), allow_none=False)
    genres = fields.List(fields.Str(allow_none=False), allow_none=False)
    collections = fields.List(fields.Str(allow_none=False), allow_none=False)

    @property
    def data_class(self) -> type:
        return Artist


class ArtistStrictSchema(ArtistSchema):
    """
    Strict schema for :class:`aliceplex.schema.model.Artist`
    """

    summary = fields.Str(allow_none=False, required=True)
    similar = fields.List(
        fields.Str(allow_none=False),
        allow_none=False,
        required=True
    )
    genres = fields.List(
        fields.Str(allow_none=False),
        validate=Length(min=1),
        required=True
    )
    collections = fields.List(
        fields.Str(allow_none=False),
        allow_none=False,
        required=True
    )
