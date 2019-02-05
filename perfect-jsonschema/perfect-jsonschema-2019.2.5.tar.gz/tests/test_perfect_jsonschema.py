import perfect_jsonschema.perfect_jsonschema as ps
from jsonschema.exceptions import SchemaError
import pytest


bad_schema = {
    "required": ["company"],
    "type": "error_here",
    "properties": {"company": {"pattern": "^(HP|Dell|Lenovo|Asus|Acer|Apple)$"}},
}


good_schema = {
    "definitions": {"unicode_number": {"pattern": "^-?[0-9]{1,7}\\.[0-9]{2}$"}},
    "required": ["company"],
    "properties": {"company": {"pattern": "^Dell$"}},
    "dependencies": {"wage_max": {"required": ["wage_min"]}},
}


@pytest.mark.parametrize(
    "schema, extended_keywords, exception, message",
    [
        (good_schema, None, None, None),
        (
            bad_schema,
            None,
            SchemaError,
            """'error_here' is not valid under any of the given schemas

Failed validating 'anyOf' in metaschema['properties']['type']:
    {'anyOf': [{'$ref': '#/definitions/simpleTypes'},
               {'items': {'$ref': '#/definitions/simpleTypes'},
                'minItems': 1,
                'type': 'array',
                'uniqueItems': True}]}

On schema['type']:
    'error_here'""",
        ),
        ("", None, SchemaError, "Schema is empty"),
        (None, None, SchemaError, "Schema is empty"),
        (
            {"properties": {"address": {"rege": "*.^"}}},
            None,
            SchemaError,
            (
                "Schema contains invalid keywords for http://json-schema.org/draft-07/schema#"
                ":\n{'rege'}"
            ),
        ),
        (
            {"properties": {"address": {"rege": "*.^", "tag": ["unique"]}}},
            {"tag"},
            SchemaError,
            (
                "Schema contains invalid keywords for http://json-schema.org/draft-07/schema#"
                ":\n{'rege'}"
            ),
        ),
        (
            {
                "$schema": "http://json-schema.org/draft-06/schema#",
                "if": {"required": ["name"]},
            },
            None,
            SchemaError,
            (
                "Schema contains invalid keywords for http://json-schema.org/draft-06/schema#"
                ":\n{'if'}"
            ),
        ),
        (
            {"if": {"format": "url"}},
            None,
            SchemaError,
            ("Schema contains invalid format values:\n{'url'}"),
        ),
    ],
)
def test_check(schema, extended_keywords, exception, message):
    if not exception:
        ps.check(schema, extended_keywords)
    else:
        with pytest.raises(exception) as excinfo:
            ps.check(schema, extended_keywords)
        assert str(excinfo.value) == message


@pytest.mark.parametrize(
    "schema, extended_keywords, expected_keywords",
    [
        (
            {"$schema": "v", "required": ["s"], "properties": {"s": {"typ": "number"}}},
            set(),
            {"typ"},
        ),
        (
            {"definition": {"name": {"type": "string", "tag": ["unique"]}}},
            {"tag"},
            {"definition", "name"},
        ),
        (
            {"patternPropertie": {"^.*": {"type": "number"}}},
            set(),
            {"patternPropertie", "^.*"},
        ),
        (good_schema, set(), set()),
    ],
)
def test_get_invalid_keywords(schema, extended_keywords, expected_keywords):
    assert ps.get_invalid_keywords(schema, extended_keywords) == expected_keywords


@pytest.mark.parametrize(
    "schema, expected_keywords",
    [
        (
            {
                "$schema": "v",
                "required": ["s"],
                "properties": {"s": {"type": "number"}, "b": {"regex": "*^"}},
            },
            {"$schema", "required", "properties", "type", "regex"},
        ),
        ({"definitions": {"name": {"type": "string"}}}, {"definitions", "type"}),
        (
            {"patternProperties": {"^.*": {"type": "number"}}},
            {"patternProperties", "type"},
        ),
        (
            {"propertie": {"s": {}}, "patternProp": {"^.*": {"typ": "number"}}},
            {"propertie", "patternProp", "s", "^.*", "typ"},
        ),
        (
            {"items": [{"type": "string"}, {"enum": ["NW", "NE"]}]},
            {"items", "type", "enum"},
        ),
    ],
)
def test_get_filtered_keys(schema, expected_keywords):
    assert ps.get_filtered_keys(schema, set()) == expected_keywords


@pytest.mark.parametrize(
    "schema, expected_values",
    [
        (
            {
                "$schema": "v",
                "required": ["s"],
                "properties": {"s": {"format": "date-time"}, "b": {"regex": "*^"}},
            },
            {"date-time"},
        ),
        (
            {
                "$schema": "v",
                "required": ["s"],
                "properties": {"format": {"format": "email"}, "b": {"regex": "*^"}},
            },
            {"email"},
        ),
        ({"definitions": {"name": {"format": "ipv4"}}}, {"ipv4"}),
        ({"items": [{"format": "time"}, {"format": "regex"}]}, {"time", "regex"}),
    ],
)
def test_get_formats(schema, expected_values):
    assert ps.get_formats(schema) == expected_values


@pytest.mark.parametrize(
    "schema, expected_keywords",
    [
        (
            {
                "format": "datetime",
                "required": ["s"],
                "properties": {"s": {"format": "uri"}},
            },
            {"datetime"},
        ),
        (
            [
                {"format": "relative-json-pointer"},
                {"format": "idn-hostname"},
                {"format": "json-pointer"},
            ],
            set(),
        ),
    ],
)
def test_get_invalid_formats(schema, expected_keywords):
    assert ps.get_invalid_formats(schema) == expected_keywords
