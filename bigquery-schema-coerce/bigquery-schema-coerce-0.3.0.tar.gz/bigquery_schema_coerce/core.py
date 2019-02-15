import json
import re
import warnings

from dateutil.parser import parse as parse_date

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from google.cloud.bigquery.schema import SchemaField


def convert_fields(candidate, schema):
    """ Type convert each attribute in the candidate object to match
    the given schema
    :param dict candidate: Object we want to type convert to ensure we
    match bigquery's expected type
    :param generator schema: schema of bigquery table given as SchemaFields
    :return Converted object
    :rtype: dict
    """
    for schema_field in schema:
        candidate_attribute = candidate.get(schema_field.name, None)
        if candidate_attribute:
            if schema_field.field_type == "FLOAT":
                if isinstance(candidate_attribute, str):
                    candidate_attribute = re.sub("[^0-9.]", "", candidate_attribute)
                candidate[schema_field.name] = float(candidate_attribute)
            elif schema_field.field_type == "INTEGER":
                if isinstance(candidate_attribute, str):
                    candidate_attribute = re.sub("[^0-9.]", "", candidate_attribute)
                candidate[schema_field.name] = int(candidate_attribute)
            elif schema_field.field_type == "STRING":
                candidate[schema_field.name] = str(candidate_attribute)
            elif schema_field.field_type == "TIMESTAMP":
                candidate[schema_field.name] = parse_date(
                    candidate_attribute
                ).isoformat()
            elif schema_field.field_type == "RECORD":
                if schema_field.mode == "REPEATED":
                    for child in candidate_attribute:
                        convert_fields(child, schema_field.fields)
                else:
                    convert_fields(candidate_attribute, schema_field.fields)
    return candidate


def parse_schema(schema=None, text=None, path=None):
    """ Parse a schema at the given path.
    Caller may pass a path to the schema using the path argument,
    the text of a schema using the text argument, or the parsed
    schema in the form of a dict to the schema argument.

    :param dict schema: Parsed schema, like from json.loads('...')
    :param str text: Schema as a json string
    :param str path: Path to a json schema
    :return: a list of SchemaFields
    :rtype: generator of SchemaFields
    """
    if path:
        with open(path) as schema_file:
            text = schema_file.read()
    if text:
        schema = json.loads(text)
    for field in schema:
        yield SchemaField.from_api_repr(field)
