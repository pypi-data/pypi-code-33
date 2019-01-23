import os
import json
import pkg_resources
import subprocess as sp
from textwrap import dedent
from PyInquirer import prompt
from ..common.logging import error, success, info


def check_docker_installed():
    try:
        sp.check_call(["docker"], stdout=sp.PIPE, stderr=sp.PIPE)
    except (FileNotFoundError, sp.CalledProcessError) as e:
        print(e)
        error(
            dedent(
                """\
            Docker could not be used (is it installed?)
            I need Docker to create a database.

            Install Docker here: https://docs.docker.com/install/
            """
            )
        )


def start_database(database_name, database_port, database_username, database_password):
    check_docker_installed()
    try:
        sp.check_call(
            [
                "docker",
                "run",
                "-p",
                "{:d}:5432".format(int(database_port)),
                "--name",
                database_name,
                "-e",
                "POSTGRES_USER={}".format(database_username),
                "-e",
                "POSTGRES_PASSWORD={}".format(database_password),
                "-e",
                "POSTGRES_DB={}".format(database_name),
                "-d",
                "postgres",
            ]
        )
    except sp.CalledProcessError:
        error(
            dedent(
                """\
            I could not start the database for some reason :(
            
            Check above for logs from the Docker daemon.
            """
            )
        )
    success("Started the database {}".format(database_name))


def kill_database(database_name):
    check_docker_installed()
    try:
        sp.check_call(["docker", "rm", "-f", database_name])
    except sp.CalledProcessError:
        error(
            dedent(
                """\
            I could not kill the database for some reason :(
            
            Check above for logs from the Docker daemon.
            """
            )
        )
    success("Killed the database {}".format(database_name))


def migrate_database(
    database_name, database_host, database_port, database_username, database_password
):
    conf_path = ".tmp.config.json"
    info(
        "I need to write a temporary file called {} to do this. "
        "I will delete it when I am done.".format(conf_path)
    )
    with open(conf_path, "w") as f:
        json.dump(
            {
                "database": database_name,
                "host": database_host,
                "port": database_port,
                "username": database_username,
                "password": database_password,
                "dialect": "postgres",
            },
            f,
        )
    migrations_path = pkg_resources.resource_filename(
        "ioexplorer_dataloader", "ioexplorer-database-migrations"
    )
    try:
        sp.check_call(
            [
                "sequelize",
                "db:migrate",
                "--config",
                conf_path,
                "--migrations-path",
                migrations_path,
            ]
        )
    except (FileNotFoundError, sp.CalledProcessError):
        error(
            dedent(
                """\
            I could not migrate the database. Is `sequelize-cli` installed?
            """
            )
        )
    finally:
        info(
            "I am now removing the {} file. Sorry for mucking up your system!".format(
                conf_path
            )
        )
        os.remove(conf_path)


def shell_database(database_name, database_username, database_password):
    check_docker_installed()
    try:
        sp.check_call(
            [
                "docker",
                "exec",
                "-it",
                "-e",
                "POSTGRES_USER={}".format(database_username),
                "-e",
                "POSTGRES_PASSWORD={}".format(database_password),
                database_name,
                "psql",
                "-d",
                database_name,
            ]
        )
    except sp.CalledProcessError:
        error(
            dedent(
                """\
            I could not shell into the database. Is `docker` installed?
            """
            )
        )
