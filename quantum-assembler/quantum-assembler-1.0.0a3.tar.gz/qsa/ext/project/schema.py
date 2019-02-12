import marshmallow
import marshmallow.fields

from qsa.schema import Schema


class ProjectConfigSchema(Schema):
    name = marshmallow.fields.String()
    type = marshmallow.fields.String(
        validate=[marshmallow.validate.OneOf(['application','library'])]
    )
    language = marshmallow.fields.String(required=False)


class ConfigSchema(Schema):
    project = marshmallow.fields.Nested(ProjectConfigSchema,
        missing=ProjectConfigSchema.defaults)
