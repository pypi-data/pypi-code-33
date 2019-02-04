import os
import yaml
import click
from psycopg2 import DataError

from .helpers import init_dataset, ingest_dataset, delete_dataset

from ..common.constants import CONF_PATH
from ..common.decorators import connect_to_db, add_env_variables
from ..common.logging import info, error, success


@click.group()
def dataset():
    pass


@dataset.command(help="Initialize a dataset")
@add_env_variables
@connect_to_db
def init(conn, engine, _env):
    return init_dataset(conn, engine)


@dataset.command(help="Ingest a dataset")
@add_env_variables
@connect_to_db
def ingest(conn, engine, _env):
    if os.path.exists(CONF_PATH):
        success("Found a config.yaml file! Ingesting...")
    else:
        error("Could not find a config.yaml file in this directory! Exiting...")
    with open(CONF_PATH, "r") as file_handle:
        dataset_config = yaml.load(file_handle)
    try:
        return ingest_dataset(_env["name"], conn, engine, dataset_config)
    except DataError as e:
        delete_dataset(conn, dataset_config["info"]["name"])
        error(
            "\n\n===START SQL ERROR LOGS===\n\n{}\n===END SQL ERROR LOGS===\n\n".format(
                e
            ),
            exit=False,
        )
        error(
            "Oh no! Something bad happened during ingestion. "
            "SQL logs should be above to help you debug! "
            "I am deleting everything that was ingested prior to the error!",
            exit=False,
        )
    except Exception as e:
        delete_dataset(conn, dataset_config["info"]["name"])
        error(
            "Oh no! Something bad happened during ingestion. "
            "SQL logs should be above to help you debug! "
            "I am deleting everything that was ingested prior to the error!",
            exit=False,
        )
        raise e


@dataset.command(help="Delete the dataset with name DATASET.")
@click.argument("dataset")
@add_env_variables
@connect_to_db
@click.confirmation_option(
    prompt=click.style("Are you sure you want to delete the dataset?", fg="red"),
    help="Confirm the deletion (will not confirm before deletion if set!)",
)
def delete(dataset, conn, engine, _env):
    deleted = delete_dataset(conn, dataset)
    if deleted:
        success("Successfully deleted the `{}` dataset.".format(dataset))
    else:
        error(
            "Could not delete the `{}` dataset. Are you sure it exists?".format(dataset)
        )
