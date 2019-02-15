import pytest
from jinja2 import UndefinedError


def test_can_write_summary(summary):
    summary.write(test=1)


def test_missing_values_in_templates_raise(summary):
    with pytest.raises(UndefinedError):
        summary.write()


def test_summary_includes_parameters(summary, fgprocess):
    summary.write(test=1)
    text = summary.output.read_text()

    assert "### Parameters" in text

    # check the str_value
    assert "str_value" in text
    assert "hello from parameters.json" in text
    assert "The column denoting the batches" in text

    # check the int_value
    assert "int_value" in text
    assert "150" in text
    assert "Number of Dimensions" in text
