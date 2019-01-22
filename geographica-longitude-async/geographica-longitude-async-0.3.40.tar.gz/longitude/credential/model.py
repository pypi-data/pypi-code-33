from marshmallow import fields
from longitude.models.sql import SQLCRUDModel
from longitude.validators import max_length, not_blank, combine_validations, choices_in
from longitude.schemas import bind_uniqueness_schema_validator, ModelSchema
from longitude import config


class CredentialSchema(ModelSchema):

    active = fields.Boolean()

    type = fields.String(
        validate=combine_validations(
            max_length(32),
            not_blank,
            choices_in(config.CREDENTIALS_TYPES)
        ),
        required=True
    )

    auth_name = fields.String(allow_none=True)
    key = fields.String(required=True)
    expires = fields.DateTime(allow_none=True) # default iso8601
    name = fields.String(32, required=True)
    description = fields.String(default='')


bind_uniqueness_schema_validator(CredentialSchema, 'name')


class CredentialModel(SQLCRUDModel):
    table_name = 'longitude_credential'

    encoded_columns = (
        'auth_name',
        'key'
    )

    select_columns = (
        "id",
        "active",
        "type",
        "auth_name",
        "created_at",
        "updated_at",
        "expires",
        "name",
        "description"
    )

    filters = (
        'name',
    )


