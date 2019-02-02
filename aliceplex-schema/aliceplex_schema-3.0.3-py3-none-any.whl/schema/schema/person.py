from marshmallow import fields

from aliceplex.schema.model import Person
from aliceplex.schema.schema.base import DataClassSchema

__all__ = ["PersonSchema", "PersonStrictSchema"]


class PersonSchema(DataClassSchema):
    """
    Schema for :class:`aliceplex.schema.model.Person`
    """

    name = fields.Str(allow_none=True)
    photo = fields.Str(allow_none=True)

    @property
    def data_class(self) -> type:
        return Person


class PersonStrictSchema(PersonSchema):
    """
    Strict schema for :class:`aliceplex.schema.model.Person`
    """

    name = fields.Str(allow_none=False, required=True)
    photo = fields.Str(allow_none=True)
