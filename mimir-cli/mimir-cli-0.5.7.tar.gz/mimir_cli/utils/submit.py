"""
submission related util functions
"""
import click
import json
import os
import requests
import shutil
from mimir_cli.strings import (
    API_SUBMIT_URL,
    ERR_INVALID_FILE,
    SUB_CONFIRM_FORCE,
    SUB_SUCCESS_URL,
    SUB_WARNING,
    ZIP_LOC,
)
from mimir_cli.utils.state import debug


def collect_submission_file(filename):
    """tries to collect the submission file and zip if need be"""
    submission_file = False
    if filename.lower().endswith(".zip"):
        submission_file = open(filename, "rb")
    else:
        if os.path.isdir(filename):
            try:
                os.remove(ZIP_LOC)
            except OSError:
                pass
            shutil.make_archive(os.path.splitext(ZIP_LOC)[0], "zip", filename)
            submission_file = open(ZIP_LOC, "rb")
        else:
            submission_file = open(filename, "rb")
    if not submission_file:
        click.echo(ERR_INVALID_FILE.format(filename))
    return submission_file


def _submit_post(
    url, filename, project_id, credentials, on_behalf_of=None, custom_penalty=0
):
    """actually perform the submit"""
    data = {"projectSubmission[projectId]": project_id}

    if on_behalf_of and isinstance(on_behalf_of, str):
        data["submitting_on_behalf"] = True
        data["submitting_as_email"] = on_behalf_of
        data["custom_penalty"] = custom_penalty

    submission_file = collect_submission_file(filename)
    files = {"zip_file[]": submission_file}
    debug(data)
    click.echo("submitting...")
    submission_request = requests.post(url, files=files, data=data, cookies=credentials)
    submission_file.close()
    result = json.loads(submission_request.text)
    debug(result)
    if "projectSubmission" in result:
        click.echo(SUB_SUCCESS_URL.format(result["projectSubmission"]["id"]))
    return result


def submit_to_mimir(
    filename, project_id, credentials, on_behalf_of=None, custom_penalty=0
):
    """submits file(s) to the mimir platform"""
    url = API_SUBMIT_URL.format(project_id)
    force_url = "{url}?ignore_filenames=true".format(url=url)
    result = _submit_post(url, filename, project_id, credentials)
    if "submitErrorMessage" in result:
        click.echo(SUB_WARNING)
        click.echo(result["submitErrorMessage"])
        if click.confirm(SUB_CONFIRM_FORCE):
            result = _submit_post(
                force_url,
                filename,
                project_id,
                credentials,
                on_behalf_of=on_behalf_of,
                custom_penalty=custom_penalty,
            )
        else:
            click.echo("\nsubmission canceled\n")
