import os
import sys
import yaml
import json

import ioexplorer_dataloader.loaders as loaders

from ..common.constants import (
    DATATYPE_NAMES,
    REQUIRED_DATATYPES,
    CONF_PATH,
    MODULE_NAMES,
)
from ..common.logging import error, info, success
from ..common.prompts import ask_continue_on_invalid
from toolz import get_in
from PyInquirer import prompt


class ExplicitDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def ask_for_dataset_info():
    questions = [
        {
            "type": "input",
            "name": "dataset_name",
            "message": "What is the dataset name?",
        },
        {
            "type": "input",
            "name": "description",
            "message": "What is a description of the dataset?",
        },
        {"type": "input", "name": "paper_url", "message": "Enter link to paper."},
        {
            "type": "input",
            "name": "cancer_types",
            "message": "What cancer types are available?"
        },
        {
            "type": "input",
            "name": "available_data",
            "message": "What data types are available?"
        },
        {
            "type": "input",
            "name": "treatment",
            "message": "What IO treatment(s) were used?"
        },
    ]
    return prompt(questions)


def create_default_ui_config(dataset_info):
    _ = lambda x: get_in(
        ["data_type_summaries", x, "variables"], dataset_info, default=[]
    )
    default_variables = {n: _(n) for n in DATATYPE_NAMES}
    default_variables = {k: v for k, v in default_variables.items() if v}
    return {x: default_variables for x in MODULE_NAMES}


def init_dataset(conn, engine):
    if os.path.exists("config.yaml"):
        error(
            "A `config.yaml` file already exists in this directory. "
            "Delete it (if you really want to) and re-run to try again."
        )
    info("Initializing new dataset!")
    summaries = {}
    for data_name in DATATYPE_NAMES:
        loader = getattr(loaders, data_name + "Loader")(conn=conn, engine=engine)
        if not loader.validate():
            if data_name in REQUIRED_DATATYPES:
                message = (
                    "Could not validate `{0}` data, (errors are shown above). "
                    "This data type is required, so I am exiting!".format(data_name)
                )
                error(message)
            ask_continue_on_invalid(data_name)
        else:
            success(
                "I was able to find the `{}` data! Please wait while I load it...".format(
                    data_name
                )
            )
        summaries[data_name] = loader.inspect()

    dataset_info = ask_for_dataset_info()
    dataset_info["data_type_summaries"] = summaries
    ui_config = create_default_ui_config(dataset_info)
    config = {"dataset_info": dataset_info, "ui_config": ui_config}
    with open("config.yaml", "w") as file_handle:
        yaml.dump(config, file_handle, default_flow_style=False, Dumper=ExplicitDumper)
    success(
        "Thanks! I made a file called `config.yaml` in this directory! "
        "Check it out and make sure everything looks OK!"
    )


def create_dataset(dataset_info, conn):
    transaction = conn.begin()
    result = conn.execute(
        """
        INSERT INTO datasets (name, description, url, available_data, treatment, cancer_types, config)
        VALUES ('{name}',
                '{description}',
                '{url}',
                '{available_data}',
                '{treatment}',
                '{cancer_types}',
                '{config}') RETURNING id;
    """.format(
            **dataset_info
        )
    )
    transaction.commit()
    return next(result)["id"]


def ingest_dataset(name, conn, engine, dataset_config):
    dataset_info = {
        "name": get_in(["dataset_info", "dataset_name"], dataset_config, default=""),
        "description": get_in(
            ["dataset_info", "description"], dataset_config, default=""
        ),
        "url": get_in(["dataset_info", "paper_url"], dataset_config, default=""),
        "cancer_types": get_in(["dataset_info", "cancer_types"], dataset_config, default=""),
        "treatment": get_in(["dataset_info", "treatment"], dataset_config, default=""),
        "available_data": get_in(["dataset_info", "available_data"], dataset_config, default=""),
        "config": json.dumps(get_in(["ui_config"], dataset_config, default="{}")),
    }
    if not dataset_info["name"]:
        error(
            'config.yaml had no conf["dataset_info"]["dataset_name"] entry. This is required!'
        )

    dataset_id = create_dataset(dataset_info, conn)
    subject_label_to_id = None
    sample_label_to_id = None
    for datatype_name in DATATYPE_NAMES:
        loader_class = getattr(loaders, datatype_name + "Loader")
        if datatype_name == "ClinicalSubject":
            loader = loader_class(conn=conn, engine=engine, dataset_id=dataset_id)
        elif datatype_name == "ClinicalSample":
            loader = loader_class(
                conn=conn, engine=engine, subject_label_to_id=subject_label_to_id
            )
        else:
            loader = loader_class(
                conn=conn, engine=engine, sample_label_to_id=sample_label_to_id
            )
        if not loader.validate():
            if datatype_name in REQUIRED_DATATYPES:
                error(
                    "Could not validate {}. "
                    "This is a required data type, so I am exiting!".format(
                        datatype_name
                    )
                )
                sys.exit(1)
        else:
            if datatype_name == "ClinicalSubject":
                subject_label_to_id = loader.pipeline()
            elif datatype_name == "ClinicalSample":
                sample_label_to_id = loader.pipeline()
            else:
                loader.pipeline()  # Ingest all the data


def delete_dataset(conn, dataset_name):
    transaction = conn.begin()
    result = conn.execute(
        """
        DELETE FROM datasets
        WHERE name='{}';
    """.format(
            dataset_name
        )
    )
    transaction.commit()
    if result.rowcount > 0:
        return True
    else:
        return False
