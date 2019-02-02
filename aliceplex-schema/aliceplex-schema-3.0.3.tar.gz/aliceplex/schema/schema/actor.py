from marshmallow import fields

from aliceplex.schema.model import Actor
from aliceplex.schema.schema.person import PersonSchema

__all__ = ["ActorSchema", "ActorStrictSchema"]


class ActorSchema(PersonSchema):
    """
    Schema for :class:`aliceplex.schema.model.Actor`
    """

    role = fields.Str(allow_none=True)

    @property
    def data_class(self) -> type:
        return Actor


class ActorStrictSchema(ActorSchema):
    """
    Strict schema for :class:`aliceplex.schema.model.Actor`
    """

    name = fields.Str(allow_none=False, required=True)
    role = fields.Str(allow_none=False, required=True)
    photo = fields.Str(allow_none=True)
