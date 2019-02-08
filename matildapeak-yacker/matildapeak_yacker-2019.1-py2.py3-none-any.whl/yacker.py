#!/usr/bin/env python3

"""A utility to drive packer with a YAML files. It's a packer YAML wrapper.

Alan Christie
February 2019
"""

import json
import os
import subprocess
import sys
import yaml

# What does a var-file argument look like?
VAR_FILE_ARG = '-var-file'

# A global list fo JSON files that were created.
# The list is used to remove files when there's been an error.
json_file_names = []


def error(msg):
    """Removes any converted files, prints an error message
    and exits with a non-zero exit code.

    :param msg: The error message
    :type msg: ``str``
    """
    remove_converted()

    print('ERROR: %s' % msg)
    sys.exit(1)


def remove_converted():
    """Removes all the converted files.
    """
    global json_file_names

    for json_file_name in json_file_names:
        if os.path.isfile(json_file_name):
            os.remove(json_file_name)


def convert(yaml_file_name):
    """Converts the named YAML file to JSON, creating
    a corresponding .json file in the same directory. The
    global list of converted filename is appended to as each
    file is processed.

    :param yaml_file_name: A full path and filename of a YAML file
    :type yaml_file_name: ``str``
    :return: The corresponding JSON file name
    :rtype: ``str``
    """
    global json_file_names

    if not os.path.isfile(yaml_file_name):
        error('%s does not exist' % yaml_file_name)

    json_file_name = os.path.splitext(yaml_file_name)[0] + '.json'
    json_file_names.append(json_file_name)

    yaml_content = None
    try:
        with open(yaml_file_name, 'r') as stream:
            try:
                yaml_content = yaml.load(stream)
            except yaml.YAMLError as exception:
                error(exception)
    except PermissionError as p_err:
        error(p_err)
    if not yaml_content:
        error('No content loaded from %s' % yaml_file_name)

    # Write as a JSON file...
    try:
        with open(json_file_name, 'w') as json_file:
            json.dump(yaml_content, json_file, indent=2)
    except PermissionError as p_err:
        error(p_err)

    return json_file_name


# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
def main():
    """The console script entry-point. Called when yacker is executed
    or from __main__.py, which is used by the installed console script.
    """
    global json_file_names

    # Find the yaml file. If there isn't one, assume it's
    # called 'template.yml'.
    # then convert to JSON.
    yaml_file_name = None
    json_file_name = None
    yaml_arg_num = 0
    # Also, be prepared to handle YAML-based var-files.
    # We keep a dictionary of argument positions and YAML file references.
    # Each file will be converted to a corresponding JSON file and the
    # the JSON file passed to packer.
    var_file_names = {}

    for arg_num in range(1, len(sys.argv)):

        arg = sys.argv[arg_num]
        if arg.startswith(VAR_FILE_ARG):

            if arg.endswith('.yml') or arg.endswith('.yaml'):
                # A YAML-based variable file.
                # Keep the (converted) file part.
                var_yaml_file_name = arg.split('=')[1]
                var_file_names[arg_num] = convert(var_yaml_file_name)

        elif arg.endswith('.yml') or arg.endswith('.yaml'):

            if yaml_file_name:
                error('Sorry, only 1 YAML file allowed')

            yaml_file_name = arg
            yaml_arg_num = arg_num
            json_file_name = convert(yaml_file_name)

    # Is YACKER_PACKER_PATH defined?
    # If so then expect ans use the packer that's there.
    packer_path = os.environ.get('YACKER_PACKER_PATH', None)
    if packer_path:

        full_packer_path = os.path.expandvars(
            os.path.expanduser(packer_path))
        packer = os.path.join(full_packer_path, 'packer')
        if not os.path.isfile(packer):
            error('Could not find packer (%s)' % packer)
        cmd = packer

    else:

        cmd = 'packer'

    # Now, just re-construct the command-line,
    # replacing all the YAML-based file names with their JSON counterparts...
    for arg_num in range(1, len(sys.argv)):

        if arg_num == yaml_arg_num:
            # The template file
            cmd += ' %s' % json_file_name
        elif arg_num in var_file_names:
            # A variable file
            cmd += ' %s=%s' % (VAR_FILE_ARG, var_file_names[arg_num])
        else:
            cmd += ' %s' % sys.argv[arg_num]

    # ...and run packer...
    status = subprocess.call(cmd.split())

    # Regardless of the outcome, remove all the JSON files.
    # This avoids the user accidentally trying to edit it/them.
    remove_converted()

    # Exit with packer's exit code...
    sys.exit(status)


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
