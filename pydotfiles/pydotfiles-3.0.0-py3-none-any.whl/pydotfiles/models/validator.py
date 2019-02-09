import logging
import os
import json
import yaml
import jsonschema
from pathlib import Path
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
    def get_schema(version, schema):
        schema_file = resource_stream(f"pydotfiles.resources.schemas.{version}", f"{schema}.json")
        return json.load(schema_file)


class Validator:
    """
    Validates that a given directory, module,
    or file is pydotfiles-compliant
    """

    def __init__(self, is_quiet=False, is_verbose=False):
        self.is_quiet = is_quiet
        self.is_verbose = is_verbose
        set_logging(is_quiet, is_verbose)

    def validate_directory(self, directory):
        if directory is None:
            raise ValidationError(ValidationErrorReason.INVALID_TARGET, "The passed in directory is invalid [directory=None]")

        # Sanity check: Does the directory exist
        if not os.path.isdir(directory):
            raise ValidationError(ValidationErrorReason.INVALID_TARGET, f"The passed in directory is invalid [directory={directory}]")

        # Sanity check: Converts to a Path object if not one already
        if type(directory) is str:
            directory = Path(directory)

        logger.info(f"Validator: Validating directory [directory={directory}]")

        # Generates a set of files that we need to validate from a tree structure
        initial_files_to_validate = set()
        for path_prefix, directory_names, file_names in os.walk(directory):
            file_name_set = set(file_names)
            if "settings.json" in file_name_set:
                initial_files_to_validate.add(os.path.join(path_prefix, "settings.json"))
            elif "settings.yaml" in file_name_set:
                initial_files_to_validate.add(os.path.join(path_prefix, "settings.yaml"))
            elif "settings.yml" in file_name_set:
                initial_files_to_validate.add(os.path.join(path_prefix, "settings.yml"))

        validation_exceptions = []
        for file_to_validate in initial_files_to_validate:
            try:
                self.validate_file(file_to_validate)
            except ValidationError as e:
                if self.is_verbose:
                    logger.exception(e.help_message)
                validation_exceptions.append(e)

        number_of_validation_errors = len(validation_exceptions)
        if number_of_validation_errors == 0:
            logger.info(f"Validator: Successfully validated directory [directory={directory}]")
        else:
            logger.error(f"Validator: Directory failed validation [directory={directory}, number_of_validation_errors={number_of_validation_errors}]")
            raise validation_exceptions[0]

    def validate_file(self, file):
        if file is None:
            raise ValidationError(ValidationErrorReason.INVALID_TARGET, "Validator: No file was passed in")

        # Sanity check: Does the file exist
        if not os.path.isfile(file):
            validation_error = ValidationError(ValidationErrorReason.INVALID_TARGET, f"Validator: The passed in file is invalid")
            validation_error.context_map['file'] = file
            raise validation_error

        # Sanity check: Converts to a Path object if not one already
        if type(file) is str:
            file = Path(file)

        logger.info(f"Validator: Validating file [file={file}]")

        # Validates the format
        try:
            file_data = load_data_from_file(file)
        except json.JSONDecodeError as e:
            validation_error = ValidationError(ValidationErrorReason.INVALID_SYNTAX, f"Validator: An invalid JSON syntax error was detected")
            validation_error.context_map['file'] = file
            raise validation_error from e
        except yaml.YAMLError as e:
            validation_error = ValidationError(ValidationErrorReason.INVALID_SYNTAX, f"Validator: An invalid YAML syntax error was detected")
            validation_error.context_map['file'] = file
            raise validation_error from e

        # Validates the schema
        try:
            self.validate_data(file_data)
        except ValidationError as e:
            e.context_map['file_name'] = file
            raise e

        # Recursively dispatches to validate other files if needed
        if file_data.get('schema') == 'core':
            defaults_setting_file_name = file_data.get('os', {}).get('default_settings_file')
            if defaults_setting_file_name is not None:
                defaults_settings_file_path = Path.joinpath(file.parent, defaults_setting_file_name)
                self.validate_file(defaults_settings_file_path)

        logger.info(f"Validator: Successfully validated file [file={file}]")

    @staticmethod
    def validate_data(data):
        if data is None:
            raise ValidationError(ValidationErrorReason.INVALID_DATA, "Validator: No parsed config data was returned")

        # Isolates for which version we need to get
        version = data.get("version")
        if version is None:
            raise ValidationError(ValidationErrorReason.INVALID_SCHEMA_VERSION, "Validator: The schema version was not found (is there a 'version' field?)")

        # Isolates for which schema type we need to get
        schema = data.get("schema")
        if schema is None:
            raise ValidationError(ValidationErrorReason.INVALID_SCHEMA_TYPE, "Validator: The schema type was not found (is there a 'schema' field?)")

        # Retrieves the required schema
        schema = ConfigMapper.get_schema(version, schema)

        # Validates the given data to the schema
        try:
            jsonschema.validate(data, schema)
        except jsonschema.exceptions.ValidationError as e:
            validator_error = ValidationError(ValidationErrorReason.INVALID_SCHEMA)
            validator_error.context_map['reason'] = e.message
            raise validator_error from e
