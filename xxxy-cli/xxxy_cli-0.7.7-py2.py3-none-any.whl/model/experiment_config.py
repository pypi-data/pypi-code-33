from marshmallow import Schema, fields, post_load

from russell.model.base import BaseModel


class ExperimentConfigSchema(Schema):

    name = fields.Str()
    version = fields.Integer()
    family_id = fields.Str()
    project_id = fields.Str()
    module_predecessor = fields.Str(allow_none=True)
    ignore_copy_list = fields.Str(allow_none=True)
    old_module_id = fields.Str(allow_none=True)
    experiment_predecessor = fields.Str(allow_none=True)

    @post_load
    def make_access_token(self, data):
        return ExperimentConfig(**data)


class ExperimentConfig(BaseModel):

    schema = ExperimentConfigSchema(strict=True)

    def __init__(self,
                 name,
                 version=0,
                 family_id=None,
                 ignore_copy_list=None,
                 old_module_id=None,
                 project_id=None,
                 module_predecessor=None,
                 experiment_predecessor=None):
        self.name = name
        self.version = version
        self.family_id = family_id
        self.ignore_copy_list = ignore_copy_list
        self.old_module_id = old_module_id
        self.project_id = project_id
        self.module_predecessor = module_predecessor
        self.experiment_predecessor = experiment_predecessor

    def set_version(self, version):
        if isinstance(version, int):
            self.version = version

    def set_module_predecessor(self, module_predecessor):
        self.module_predecessor = module_predecessor

    def set_experiment_predecessor(self, experiment_predecessor):
        self.experiment_predecessor = experiment_predecessor
