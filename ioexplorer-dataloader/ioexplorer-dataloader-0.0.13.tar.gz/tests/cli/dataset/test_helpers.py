import pprint
import io
import yaml
from unittest import mock
from textwrap import dedent
from ioexplorer_dataloader.cli.common.constants import DATATYPE_NAMES
from ioexplorer_dataloader.cli.dataset.helpers import (
    ExplicitDumper,
    ask_for_dataset_info,
    create_default_ui_config,
)


def _prompt(questions):
    return {q["name"]: "Hello World" for q in questions}


mock.patch("ioexplorer_dataloader.cli.dataset.helpers.prompt", _prompt).start()


def test_explicit_dumper():
    """"
    Test that the ExplicitDumper Dumper class causes yaml
    to dump with no references for repeated arrays.

    """
    data = ["hello", "world"]
    data_to_dump = {"key1": data, "key2": data}

    # Without ExplicitDumper to demonstrate issue
    f = io.StringIO()
    yaml.dump(data_to_dump, f, default_flow_style=False)
    assert f.getvalue() == dedent(
        """\
    key1: &id001
    - hello
    - world
    key2: *id001
    """
    )

    # With ExplicitDumper
    f = io.StringIO()
    yaml.dump(data_to_dump, f, default_flow_style=False, Dumper=ExplicitDumper)
    assert f.getvalue() == dedent(
        """\
    key1:
    - hello
    - world
    key2:
    - hello
    - world
    """
    )


def test_ask_for_dataset_info():
    "Test the ask for dataset info prompt."
    res = ask_for_dataset_info()
    assert res == {
        "dataset_name": "Hello World",
        "description": "Hello World",
        "paper_url": "Hello World",
        "available_data": "Hello World",
        "cancer_types": "Hello World",
        "treatment": "Hello World",
    }


def test_create_default_ui_config():
    dataset_info = {
        "data_type_summaries": {
            x: {"variables": ["var1", "var2"]} for x in DATATYPE_NAMES
        }
    }
    assert create_default_ui_config(dataset_info) == {
        "Correlation": {
            "ClinicalSample": ["var1", "var2"],
            "ClinicalSubject": ["var1", "var2"],
            "Expression": ["var1", "var2"],
            "Fusion": ["var1", "var2"],
            "Mutation": ["var1", "var2"],
            "SV": ["var1", "var2"],
            "Timeline": ["var1", "var2"],
        },
        "Expression": {
            "ClinicalSample": ["var1", "var2"],
            "ClinicalSubject": ["var1", "var2"],
            "Expression": ["var1", "var2"],
            "Fusion": ["var1", "var2"],
            "Mutation": ["var1", "var2"],
            "SV": ["var1", "var2"],
            "Timeline": ["var1", "var2"],
        },
        "FilterVariables": {
            "ClinicalSample": ["var1", "var2"],
            "ClinicalSubject": ["var1", "var2"],
            "Expression": ["var1", "var2"],
            "Fusion": ["var1", "var2"],
            "Mutation": ["var1", "var2"],
            "SV": ["var1", "var2"],
            "Timeline": ["var1", "var2"],
        },
        "Survival": {
            "ClinicalSample": ["var1", "var2"],
            "ClinicalSubject": ["var1", "var2"],
            "Expression": ["var1", "var2"],
            "Fusion": ["var1", "var2"],
            "Mutation": ["var1", "var2"],
            "SV": ["var1", "var2"],
            "Timeline": ["var1", "var2"],
        },
    }
