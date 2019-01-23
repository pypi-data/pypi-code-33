from unittest import TestCase

from reliabilly.components.models.base import BaseModel, Field, SchemaTypeMappings


class CustomTestModel(BaseModel):
    test: str
    val: int
    dub: float
    lis: list
    dict: dict


class SchemaTestModel(BaseModel):
    test: Field(str, required=True)
    test_int: Field(int, required=True)
    test_not_required: Field(str, required=False)


class NotSchemaTestModel(BaseModel):
    test: str


class ModelTests(TestCase):
    def test_json_serialization(self):
        model = CustomTestModel()
        self.assertIsNotNone(model)
        self.assertEqual(model.to_json(model), '{}')
        self.assertEqual(type(model.from_json('{}')), BaseModel)
        result = model.from_json('{"test": "jjb", "val": 123}')
        self.assertEqual(type(result), BaseModel)
        self.assertEqual(result.test, 'jjb')
        self.assertEqual(result.val, 123)

    def test_model_validation(self):
        model = SchemaTestModel()
        model.test = 'blerch'
        model.test_int = 10
        self.assertTrue(model.validate())

    def test_model_validation_failure(self):
        model = SchemaTestModel()
        self.assertFalse(model.validate())

    def test_validation_with_schema(self):
        model = SchemaTestModel()
        model.test = 'blerch'
        self.assertTrue(model.validate(
            None, {'test': {'required': True, 'type': 'string'}}))

    def test_schema_mapping(self):
        self.assertEqual(SchemaTypeMappings['str'], "string")
        self.assertEqual(SchemaTypeMappings['int'], "integer")
        self.assertEqual(SchemaTypeMappings['bool'], "boolean")
        self.assertEqual(SchemaTypeMappings['datetime.date'], "date")
        self.assertEqual(SchemaTypeMappings['datetime.datetime'], "datetime")
        self.assertEqual(SchemaTypeMappings['float'], "float")
        self.assertEqual(SchemaTypeMappings['list'], "list")
        self.assertEqual(SchemaTypeMappings['set'], "set")

    def test_field_init(self):
        field = Field(str, required=True)
        self.assertEqual(field.schema, {'required': True})
        self.assertEqual(field.type, str)

    def test_to_schema(self):
        schema = BaseModel.to_schema(SchemaTestModel)
        self.assertEqual(schema, {
            'test': {'required': True, 'type': 'string'},
            'test_int': {'required': True, 'type': 'integer'},
            'test_not_required': {'required': False, 'type': 'string'}
        })

    def test_with_json_payload(self):
        model = SchemaTestModel()
        payload = {"test": "things"}
        self.assertFalse(model.validate(payload))

    def test_with_json_payload_pass(self):
        model = SchemaTestModel()
        payload = {"test": "things", "test_int": 10}
        self.assertTrue(model.validate(payload))

    def test_with_json_payload_empty(self):
        model = BaseModel()
        payload = {}
        self.assertTrue(model.validate(payload))

    def test_to_schema_no_field(self):
        schema = BaseModel.to_schema(NotSchemaTestModel)
        self.assertFalse(schema)

    def test_validation_without_schema(self):
        model = NotSchemaTestModel()
        self.assertTrue(model.validate())
