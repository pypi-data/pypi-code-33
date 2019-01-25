# coding=utf-8
"""Module for handling workflow definition objects.

Intended for registering a new workflow type with the Configuration database.
"""
import ast
import json
import os
from os.path import abspath, dirname, isdir, isfile, join

import jsonschema
import yaml

from .. import ConfigDb

DB = ConfigDb()
GROUP_KEY = 'workflow_definition'


def load(filename: str):
    """Load and register a workflow definition.

    Args:
        filename (str): Full filename path to a workflow definition file.

    Raises:
        ValueError,
        jsonschema.ValidationError,

    """
    if not isfile(filename):
        raise ValueError("Specified workflow path does not exist! {}"
                         .format(filename))

    if filename.lower().endswith(('.json', '.json.j2')):
        with open(filename, 'r') as file:
            workflow_definition = json.loads(file.read())
    elif filename.lower().endswith(('.yaml', '.yml', '.yaml.j2', '.yml.j2')):
        with open(filename, 'r') as file:
            workflow_definition = yaml.safe_load(file.read())
    else:
        raise ValueError("Unexpected file extension. Allowed values: "
                         "(.json, .yaml, .yml).")

    stages_dir = join(abspath(dirname(filename)), 'stages')

    if not isdir(stages_dir):
        raise ValueError("Stages directory does not exist! {}"
                         .format(stages_dir))

    add(workflow_definition, stages_dir)
    return workflow_definition


def get_workflow(workflow_id: str, workflow_version: str) -> dict:
    """Get a workflow definition from the Configuration Database.

    Args:
        workflow_id (str): Workflow identifier
        workflow_version (str): Workflow version

    Returns:
        dict, Workflow definition dictionary

    Raises:
        KeyError, if the specified workflow does not exist

    """
    name = "{}:{}:{}".format(GROUP_KEY, workflow_id, workflow_version)
    if not DB.key_exists(name):
        raise KeyError('Workflow definition {}:{} not found!'
                       .format(workflow_id, workflow_version))
    workflow = DB.get_hash_dict(name)
    workflow['stages'] = ast.literal_eval(workflow['stages'])
    return workflow


def get_workflows() -> dict:
    """Get dict of ALL known workflow definitions.

    Returns
        dict,

    """
    keys = DB.get_keys("{}:*".format(GROUP_KEY))
    known_workflows = dict()
    for key in keys:
        values = key.split(':')
        if values[1] not in known_workflows:
            known_workflows[values[1]] = list()
        known_workflows[values[1]].append(values[2])
    return known_workflows


def delete(workflow_id: str = None, workflow_version: str = None):
    """Delete workflow definitions.

    Args:
        workflow_id (str, optional): Workflow identifier
        workflow_version (str, optional): Workflow version

    - If the workflow_version is None, delete all versions of the specified
      workflow.
    - If workflow_id and workflow_version are None, delete all workflow
      definitions.

    """
    if workflow_id is None:
        keys = DB.get_keys("{}:*".format(GROUP_KEY))
        DB.delete(*keys)
    elif workflow_version is None:
        keys = DB.get_keys("{}:{}:*".format(GROUP_KEY, workflow_id))
        DB.delete(*keys)
    else:
        name = "{}:{}:{}".format(GROUP_KEY, workflow_id, workflow_version)
        DB.delete(name)


def add(workflow_definition: dict, stages_dir: str = None):
    """Add a workflow definition to the Configuration Database.

    Args:
        workflow_definition (dict): Workflow definition dictionary
        stages_dir (str): Stages directory.

    """
    # TODO(BMo) check that the workflow does not already exist in the db!
    _validate_schema(workflow_definition)
    key = '{}:{}:{}'.format(GROUP_KEY, workflow_definition['id'],
                            workflow_definition['version'])
    if DB.get_keys(key):
        raise KeyError('Workflow definition already exists: {}'.format(key))

    if stages_dir is not None:
        for index, stage in enumerate(workflow_definition['stages']):
            stage_dir = join(stages_dir, stage['id'], stage['version'])
            stage_files = os.listdir(stage_dir)
            compose_str = _load_stage_compose_file(stage_dir, stage_files)
            args_str = _load_stage_args(stage_dir, stage_files)
            parameters = _load_stage_parameters(stage_dir, stage_files)
            workflow_definition['stages'][index]['parameters'] = parameters
            workflow_definition['stages'][index]['compose_file'] = compose_str
            workflow_definition['stages'][index]['args'] = args_str

    DB.save_dict(key, workflow_definition, hierarchical=False)


def _validate_schema(workflow_definition: dict):
    """Validate the workflow definition.

    Args:
        workflow_definition (dict): workflow definition dictionary.
    """
    schema_version = workflow_definition['schema_version']
    schema_path = join(dirname(__file__), 'schema',
                       'workflow_definition_{}.json'.format(schema_version))
    with open(schema_path, 'r') as file:
        schema = json.loads(file.read())
    jsonschema.validate(workflow_definition, schema)


def _load_stage_compose_file(stage_dir: str, item_list: list):
    """Load Docker Compose file for workflow stage.

    Args:
        stage_dir (str):  Directory for the stage.
        item_list (list): Directory listing for the stage.
    """
    matched = [item for item in item_list if item.startswith('args')]
    compose_str = ""
    if not matched:
        return compose_str
    if len(matched) > 1:
        raise FileNotFoundError('Unknown parameters file in {}'
                                .format(stage_dir))
    with open(join(stage_dir, matched[0]), 'r') as file:
        compose_str = file.read()

    if matched[0].endswith(('.yaml', '.yml')):
        return yaml.load(compose_str)

    if matched[0].endswith(('.json',)):
        return json.loads(compose_str)

    if matched[0].endswith(('.j2',)):
        return compose_str

    raise RuntimeError('Unable to load args file {}'.format(matched[0]))


def _load_stage_args(stage_dir: str, item_list: list):
    """Load args file for workflow stage.

    Args:
        stage_dir (str):  Directory for the stage.
        item_list (list): Directory listing for the stage.
    """
    matched = [item for item in item_list if item.startswith('args')]
    args_str = ""
    if not matched:
        return args_str
    if len(matched) > 1:
        raise FileNotFoundError('Unknown parameters file in {}'
                                .format(stage_dir))
    with open(join(stage_dir, matched[0]), 'r') as file:
        args_str = file.read()

    if matched[0].endswith(('.yaml', '.yml')):
        return yaml.load(args_str)

    if matched[0].endswith(('.json',)):
        return json.loads(args_str)

    if matched[0].endswith(('.j2',)):
        return args_str

    raise RuntimeError('Unable to load args file {}'.format(matched[0]))


def _load_stage_parameters(stage_dir: str, item_list: list) -> dict:
    """Load defaults file for workflow stage.

    Args:
        stage_dir (str):  Directory for the stage.
        item_list (list): Directory listing for the stage.
    """
    matched = [item for item in item_list if item.startswith('parameters')]
    if not matched:
        return dict()

    if len(matched) > 1:
        raise FileNotFoundError('Unknown parameters file in {}'
                                .format(stage_dir))
    with open(join(stage_dir, matched[0]), 'r') as file:
        parameters_str = file.read()

    if matched[0].endswith(('.yaml', '.yml')):
        return yaml.load(parameters_str)

    if matched[0].endswith(('.json',)):
        return json.loads(parameters_str)

    raise RuntimeError('Unable to load parameters file {}'
                       .format(matched[0]))


def _load_template_files(workflow: dict, templates_root: str):
    """Load workflow templates files.

    Loads workflow templates files specified in the workflow definition
    dictionary by the following keys:

    - ee_config:args_template
    - app_config:compose_template

    If these keys are found, this function attempts to replace their values
    by the contents of files found in the templates_root directory.
    Files are expected to be found a folder named after the workflow
    and workflow stage according to the pattern:

        <workflow_id>/<workflow_version>/<stage_id>/<stage_version>

    This folder pattern is expected to reside as a sub-folder of the
    specified templates_root directory.

    As a result of this action, the specified workflow dictionary is modified.

    Note: hyphens are used to separate id's and versions of workflows
        and workflow stages as colons are not a generally safe
        character to use in folder paths. Colons however are still used
        for keys in the dictionary as this is considered easier to read.

    Args:
         workflow (dict): Workflow definition dictionary.
         templates_root (str): Root directory to look for templates.

    """
    assert workflow['schema_version'] == '1.0'

    workflow_path = join(templates_root, workflow['id'], workflow['version'])

    for stage in workflow['stages']:
        stage_path = join(workflow_path, stage['id'], stage['version'])
        for config_type in ['ee_config', 'app_config']:
            for key, value in stage[config_type].items():
                if '_template' in key:
                    template_file = join(stage_path, value)
                    with open(template_file, 'r') as file:
                        stage[config_type][key] = file.read()
