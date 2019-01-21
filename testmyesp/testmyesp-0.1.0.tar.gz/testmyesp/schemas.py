
import json
import re

from colibris import settings
from colibris.schemas import ModelSchema, Schema, ValidationError
from colibris.schemas import fields, validate, validates_schema, post_dump

from testmyesp import constants
from testmyesp import instructions
from testmyesp import models
from testmyesp import schemafields


class InstructionParamsField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        instruction_class = instructions.get_instruction_class(obj['name'])
        if instruction_class is None:
            return ''

        schema_class = instruction_class.get_schema_class()
        schema = schema_class()

        return schema.dump(obj['params'])

    def _deserialize(self, value, attr, data, **kwargs):
        instruction_class = instructions.get_instruction_class(data['name'])
        if instruction_class is None:
            return None

        schema_class = instruction_class.get_schema_class()
        schema = schema_class()

        return schema.load(data['params'])


class ClientSchema(ModelSchema):
    class Meta:
        model = models.Client
        exclude = ('secret',)


class FlashImageSchema(Schema):
    name = fields.String(required=True, validate=validate.Regexp(r'^[.\w_-]+$', re.IGNORECASE))
    address = fields.String(validate=validate.Regexp('^[x0-9a-fA-F]+$'), required=True)
    content = schemafields.Base64Field()
    url = fields.URL()
    fill = fields.Integer(validate=validate.Range(0, 255))
    size = fields.Integer(validate=validate.Range(0, settings.FLASH['size'] * 1024))

    @validates_schema
    def validate_content_size(self, data):
        if 'content' in data:
            if int(data['address'], 0) + len(data['content']) > settings.FLASH['size'] * 1024:
                raise ValidationError('Content is out of memory range.')

    @validates_schema
    def validate_some_content(self, data):
        if 'content' not in data and 'url' not in data and 'fill' not in data:
            raise ValidationError('Either content, URL or fill must be supplied.')

    @validates_schema
    def validate_fill(self, data):
        if 'fill' in data and 'size' not in data:
            raise ValidationError('Size is required when fill is supplied.')


class AssetSchema(Schema):
    name = fields.String(required=True, validate=validate.Regexp(r'^[.\w_-]+$', re.IGNORECASE))
    content = schemafields.Base64Field()


class InstructionSchema(Schema):
    name = fields.String(validate=validate.OneOf(instructions.all_instructions.keys()), required=True)
    params = InstructionParamsField()


class TestCaseSchema(Schema):
    name = fields.String(required=True, validate=validate.Regexp(r'^[.\w_-]+$', re.IGNORECASE))
    instructions = fields.Nested(InstructionSchema, many=True, required=True)
    serial_baud = fields.Integer(validate=validate.OneOf(constants.SERIAL_BAUD_RATES),
                                 missing=settings.SERIAL['normal_baud'])
    ensure_flash_images = fields.List(fields.String(validate=validate.Regexp(r'^[.\w_-]+$', re.IGNORECASE)))
    reset_before = fields.Boolean(missing=False)
    restart_before = fields.Boolean(missing=False)


class ShowJobSchema(ModelSchema):
    @post_dump
    def load_results_json(self, data):
        results_json = data.pop('results_json')
        if results_json:
            data['results'] = json.loads(results_json)

        else:
            data['results'] = None

        return data

    @post_dump
    def error_set_null(self, data):
        if not data['error']:
            data['error'] = None

        return data

    class Meta:
        model = models.Job
        fields = ('id', 'client', 'state', 'added_moment', 'started_moment', 'ended_moment', 'timeout', 'error',
                  'continue_on_failure', 'results_json')


class AddJobSchema(Schema):
    flash_images = fields.Nested(FlashImageSchema, many=True, missing=[])
    assets = fields.Nested(AssetSchema, many=True, missing=[])
    test_cases = fields.Nested(TestCaseSchema, many=True, required=True)
    continue_on_failure = fields.Boolean(missing=False)
    timeout = fields.Integer(validate=validate.Range(min=1, max=settings.MAX_JOB_TIME), required=True)

    @validates_schema
    def validate_flash_image_names(self, data):
        names = [d['name'] for d in data['flash_images']]
        if len(names) != len(set(names)):
            raise ValidationError('Duplicate flash image name.')

        for test_case_dict in data['test_cases']:
            for name in test_case_dict.get('ensure_flash_images', []):
                if name not in names:
                    raise ValidationError('Unknown flash image name: {}.'.format(name))

    @validates_schema
    def validate_asset_names(self, data):
        names = [d['name'] for d in data['assets']]
        if len(names) != len(set(names)):
            raise ValidationError('Duplicate asset name.')

        for flash_image_dict in data['flash_images']:
            if flash_image_dict['name'] in names:
                raise ValidationError('Asset name cannot be one of the flash image names: {}.'
                                      .format(flash_image_dict['name']))

    @validates_schema
    def validate_test_case_names(self, data):
        names = [d['name'] for d in data['test_cases']]
        if len(names) != len(set(names)):
            raise ValidationError('Duplicate test case name.')


class AddJobSchemaQuery(Schema):
    wait = fields.Boolean(missing=True)
