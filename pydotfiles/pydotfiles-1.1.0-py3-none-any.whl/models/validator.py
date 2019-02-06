import logging
import os
import json
import yaml
import jsonschema
from pkg_resources import resource_stream

from .utils import set_logging, load_data_from_file
from .exceptions import ValidationError, ValidationErrorReason

logger = logging.getLogger(__name__)


class ConfigMapper:
    """
    Maps a given configuration file with a set
    schema to an internal configuration data
    structure
    """

    @staticmethod
    def get_schema(version):
        schema_file = resource_stream("pydotfiles.resources.schemas", f"{version}.json")
        return json.load(schema_file)


class Validator:
    """
    Validates that a given directory, module,
    or file is pydotfiles-compliant
    """

    def __init__(self, is_quiet=False, is_verbose=False):
        set_logging(is_quiet, is_verbose)

    def validate_directory(self, directory):
        if directory is None:
            raise ValidationError(ValidationErrorReason.INVALID_TARGET, "The passed in directory is invalid [directory=None]")

        # Sanity check: Does the directory exist
        if not os.path.isdir(directory):
            raise ValidationError(ValidationErrorReason.INVALID_TARGET, f"The passed in directory is invalid [directory={directory}]")

        logger.info(f"Validator: Validating directory [directory={directory}]")

        # Generates a set of files that we need to validate from a tree structure
        files_to_validate = set()
        for path_prefix, directory_names, file_names in os.walk(directory):
            file_name_set = set(file_names)
            if "settings.json" in file_name_set:
                files_to_validate.add(os.path.join(path_prefix, "settings.json"))
            elif "settings.yaml" in file_name_set:
                files_to_validate.add(os.path.join(path_prefix, "settings.yaml"))
            elif "settings.yml" in file_name_set:
                files_to_validate.add(os.path.join(path_prefix, "settings.yml"))

        validation_exceptions = []
        for file_to_validate in files_to_validate:
            try:
                self.validate_file(file_to_validate)
            except ValidationError as e:
                logger.exception(f"The passed in file's schema is invalid [file={file_to_validate}]")
                validation_exceptions.append(e)

        number_of_validation_errors = len(validation_exceptions)
        if number_of_validation_errors == 0:
            logger.info(f"Validator: Successfully validated directory [directory={directory}]")
        else:
            logger.critical(f"Validator: Directory failed validation [directory={directory}, number_of_validation_errors={number_of_validation_errors}]")
            exit(1)

    def validate_file(self, file):
        if file is None:
            raise ValidationError(ValidationErrorReason.INVALID_TARGET, "The passed in file is invalid [file=None]")

        # Sanity check: Does the file exist
        if not os.path.isfile(file):
            raise ValidationError(ValidationErrorReason.INVALID_TARGET, f"The passed in file is invalid [file={file}]")

        logger.info(f"Validator: Validating file [file={file}]")

        # Validates the format
        try:
            file_data = load_data_from_file(file)
        except json.JSONDecodeError as e:
            raise ValidationError(ValidationErrorReason.INVALID_SYNTAX, f"An invalid JSON syntax error was detected [file={file}]") from e
        except yaml.YAMLError as e:
            raise ValidationError(ValidationErrorReason.INVALID_SYNTAX, f"An invalid YAML syntax error was detected [file={file}]") from e

        # Validates the schema
        self.validate_data(file_data)
        logger.info(f"Validator: Successfully validated file [file={file}]")

    def validate_data(self, data):
        if data is None:
            raise ValidationError(ValidationErrorReason.INVALID_SCHEMA, "The parsed config data is invalid [data=None]")

        # Isolates for which schema we need to get
        schema_version = data.get("version")
        if schema_version is None:
            raise ValidationError(ValidationErrorReason.INVALID_SCHEMA, f"The schema version value is invalid [version={schema_version}]")

        # Retrieves the required schema
        schema = ConfigMapper.get_schema(schema_version)

        # Validates the given data to the schema
        try:
            jsonschema.validate(data, schema)
        except jsonschema.exceptions.ValidationError as e:
            raise ValidationError(ValidationErrorReason.INVALID_SCHEMA) from e
