from fastgenomics import deprecated
import pytest
import pathlib


def test_can_read_input_file(local):
    # can get path
    with pytest.deprecated_call():
        to_test = deprecated.get_input_path("some_input")

    # path exists
    assert to_test.exists()


def test_can_read_optional_input_file(local):
    with pytest.deprecated_call():
        to_test = deprecated.get_input_path("some_optional_input")
    assert to_test.exists()


def test_cannot_read_undefined_input(local):
    with pytest.deprecated_call():
        with pytest.raises(KeyError):
            deprecated.get_input_path("i_don't_exist")


def test_left_out_optional_is_none(app_dir, data_root_2):
    with pytest.deprecated_call():
        deprecated.set_paths(app_dir, data_root_2)
        assert None is deprecated.get_input_path("some_optional_input")


def test_can_write_summary(local, clear_output):
    with pytest.deprecated_call():
        sum_file = deprecated.get_summary_path()
    with sum_file.open("w", encoding="utf-8") as out:
        out.write("test")
    assert sum_file.exists()


def test_can_write_output(local, clear_output):
    with pytest.deprecated_call():
        out_path = deprecated.get_output_path("some_output")
    assert out_path.name == "some_output.csv"
    with out_path.open("w", encoding="utf-8") as out:
        out.write("test")
    assert out_path.exists()


def test_cannot_write_undefined_output(local):
    with pytest.deprecated_call():
        with pytest.raises(KeyError):
            deprecated.get_output_path("i_don't_exist")


# test things, imported from fastgenomics.common, are available
def test_import_from_common(app_dir, data_root):
    with pytest.deprecated_call():
        deprecated.set_paths(app_dir=app_dir, data_root=data_root)
        assert len(deprecated.get_parameters()) > 0
        deprecated.get_parameter("int_value")


def test_paths_are_initialized(local):
    with pytest.deprecated_call():
        deprecated.get_paths()


def test_custom_init_paths(app_dir, data_root):
    with pytest.deprecated_call():
        deprecated.set_paths(app_dir, data_root)
        deprecated.get_paths()


def test_paths_from_env(fg_env):
    with pytest.deprecated_call():
        deprecated.get_paths()


def test_cannot_init_nonexisting_paths():
    with pytest.deprecated_call():
        with pytest.raises(FileNotFoundError):
            deprecated.set_paths("i_don't_exist", "me_neither")


def test_get_app_manifest(local):
    with pytest.deprecated_call():
        deprecated.get_app_manifest()


def test_can_get_parameters(local):
    with pytest.deprecated_call():
        parameters = deprecated.get_parameters()
        assert len(parameters) > 0


def test_parameters(local):
    with pytest.deprecated_call():
        parameters = deprecated.get_parameters()

    assert "str_value" in parameters
    assert parameters["str_value"] == "hello from parameters.json"

    assert "int_value" in parameters
    assert parameters["int_value"] == 150

    assert "float_value" in parameters
    assert parameters["float_value"] == float(100)

    assert "bool_value" in parameters
    assert parameters["bool_value"] is True

    assert "list_value" in parameters
    assert parameters["list_value"] == [1, 2, 3]

    assert "dict_value" in parameters
    assert parameters["dict_value"] == {"foo": 42, "bar": "answer to everything"}

    assert "optional_int_value_concrete" in parameters
    assert parameters["optional_int_value_concrete"] == 4

    assert "optional_int_value_null" in parameters
    assert parameters["optional_int_value_null"] is None

    assert "enum_value" in parameters
    assert parameters["enum_value"] == "X"

    # moved to test_app_checker because logs are printed at a different time now
    # assert any(["Parameters" in x.message for x in caplog.records]), "Parameter logs are not set"


def test_can_get_specific_parameter(local):
    with pytest.deprecated_call():
        assert deprecated.get_parameter("int_value") == 150


def test_can_get_null_parameter(local):
    with pytest.deprecated_call():
        assert deprecated.get_parameter("optional_int_value_null") is None


def test_parameters_2(app_dir, data_root, data_root_2):
    with pytest.deprecated_call():
        deprecated.set_paths(app_dir, data_root)
        assert deprecated.get_parameter("int_value") == 150
        assert deprecated.get_parameter("str_value") == "hello from parameters.json"

        deprecated.set_paths(app_dir, data_root_2)
        assert (
            deprecated.get_parameter("str_value")
            == "hello from app 2's parameters.json"
        )


def test_input_file_mapping(app_dir, data_root, data_root_2):
    with pytest.deprecated_call():
        deprecated.set_paths(app_dir, data_root)
        assert deprecated.get_input_path("some_input").name == "expression_matrix.csv"

        deprecated.set_paths(app_dir, data_root_2)
        assert deprecated.get_input_path("some_input").name == "data"
