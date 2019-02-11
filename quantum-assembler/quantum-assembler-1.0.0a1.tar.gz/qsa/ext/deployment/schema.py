import marshmallow
import marshmallow.fields

from qsa.schema import Schema


class EnvironmentConfigSchema(Schema):
    name = marshmallow.fields.String(required=True)


class DeploymentConfigSchema(Schema):
    environments = marshmallow.fields.Nested(
        EnvironmentConfigSchema,
        many=True,
        missing=list
    )


class ConfigSchema(Schema):
    deployment = marshmallow.fields.Nested(DeploymentConfigSchema,
        missing=DeploymentConfigSchema.defaults)

