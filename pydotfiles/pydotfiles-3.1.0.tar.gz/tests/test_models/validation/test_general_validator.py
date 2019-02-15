import pytest
import uuid
from pydotfiles.models.validator import Validator
from pydotfiles.models.exceptions import ValidationError


"""
Validator tests
"""


def test_invalid_directory_none():
    # Setup
    validator = Validator()

    # System under test
    with pytest.raises(ValidationError):
        validator.validate_directory(None)


def test_invalid_directory_name():
    # Setup
    validator = Validator()
    invalid_directory_name = str(uuid.uuid4())

    # System under test
    with pytest.raises(ValidationError):
        validator.validate_directory(invalid_directory_name)


def test_valid_directory(tmpdir):
    # Setup
    validator = Validator()
    valid_file = tmpdir.join("settings.json")
    valid_file_content = "{\"version\": \"alpha\", \"schema\": \"core\"}"
    valid_file.write(valid_file_content)

    # System under test
    validator.validate_directory(tmpdir.strpath)


def test_valid_directory_multiple_modules(tmpdir):
    # Setup
    validator = Validator()
    modules_settings_file_a = tmpdir.mkdir("a_directory").join("settings.json")
    modules_settings_file_a_content = "{\"version\": \"alpha\", \"schema\": \"core\"}"
    modules_settings_file_a.write(modules_settings_file_a_content)

    modules_settings_file_b = tmpdir.mkdir("b_directory").join("settings.yaml")
    modules_settings_file_b_content = "version: \"alpha\"\nschema: \"core\""
    modules_settings_file_b.write(modules_settings_file_b_content)

    # System under test
    validator.validate_directory(tmpdir.strpath)


def test_invalid_file_none():
    # Setup
    validator = Validator()

    # System under test
    with pytest.raises(ValidationError):
        validator.validate_file(None)


def test_invalid_file_name():
    # Setup
    validator = Validator()
    invalid_file_name = str(uuid.uuid4())

    # System under test
    with pytest.raises(ValidationError):
        validator.validate_file(invalid_file_name)


def test_invalid_file_empty_file(tmpdir):
    # Setup
    validator = Validator()
    invalid_file = tmpdir.join("invalid_json.json")
    invalid_file_content = ""
    invalid_file.write(invalid_file_content)

    # System under test
    with pytest.raises(ValidationError):
        validator.validate_file(invalid_file.strpath)


def test_invalid_file_invalid_json(tmpdir):
    # Setup
    validator = Validator()
    invalid_file = tmpdir.join("invalid_json.json")
    invalid_file_content = "{\"version\": \"alpha,}"
    invalid_file.write(invalid_file_content)

    # System under test
    with pytest.raises(ValidationError):
        validator.validate_file(invalid_file.strpath)


def test_valid_file(tmpdir):
    # Setup
    validator = Validator()
    valid_file = tmpdir.join("valid_json.json")
    valid_file_content = "{\"version\": \"alpha\", \"schema\": \"core\"}"
    valid_file.write(valid_file_content)

    # System under test
    validator.validate_file(valid_file.strpath)


def test_invalid_data_none():
    # Setup
    validator = Validator()

    # System under test
    with pytest.raises(ValidationError):
        validator.validate_data(None)
