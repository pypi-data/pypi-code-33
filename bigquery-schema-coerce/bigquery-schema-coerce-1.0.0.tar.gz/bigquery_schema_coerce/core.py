import json
import re
import warnings

from dateutil.parser import parse as parse_date

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from google.cloud.bigquery.schema import SchemaField


def coerce(candidate, schema):
    """ Convert and project fields in candidate against schema """
    schema = list(schema)
    convert(candidate, schema)
    project(candidate, schema)
    return candidate


def convert(candidate, schema):
    """ Type convert each attribute in the candidate object to match
    the given schema
    :param dict candidate: Object we want to type convert to ensure we
    match bigquery's expected type
    :param generator schema: schema of bigquery table given as SchemaFields
    :return Converted object
    :rtype: dict
    """
    for schema_field in schema:
        candidate_attribute = candidate.get(schema_field.name)
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
                        convert(child, schema_field.fields)
                else:
                    convert(candidate_attribute, schema_field.fields)
    return candidate


def project(candidate, schema):
    """ Remove any keys that are not represented in the schema
    :return Converted object
    :rtype: dict
    """
    schema_keys = set()
    for schema_field in schema:
        candidate_attribute = candidate.get(schema_field.name)
        if not candidate_attribute:
            continue
        if schema_field.field_type == "RECORD":
            if schema_field.mode == "REPEATED":
                for child in candidate_attribute:
                    project(child, schema_field.fields)
            else:
                project(candidate_attribute, schema_field.fields)
        schema_keys.add(schema_field.name)
    for removal in set(candidate.keys()) - schema_keys:
        del candidate[removal]
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
