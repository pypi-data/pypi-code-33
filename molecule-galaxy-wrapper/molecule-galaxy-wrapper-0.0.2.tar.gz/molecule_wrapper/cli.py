import sys
import os
from .yaml import load, dump


def load_or_die(file_path):
    try:
        return load(file_path)
    except FileNotFoundError:
        print("{} file does not exists".format(file_path))
        sys.exit(1)


def main():
    meta_requirements_path = "meta/{}".format("main.yml")
    requirements_path = "requirements.yml"

    requirements = load_or_die(requirements_path)
    meta_requirements = load_or_die(meta_requirements_path)

    if requirements is None:
        print("No dependencies defined inside requirements.yml")
        requirements = []

    if 'dependencies' not in meta_requirements:
        print(
            "Format Error - Ansible Galaxy {} file does not contain main dependencies list".format(meta_requirements_path))
        sys.exit(1)

    print("Appending {} content into {} dependencies".format(
        requirements_path, meta_requirements_path))
    meta_requirements['dependencies'] = requirements
    dump(meta_requirements_path, meta_requirements)

    # Role with no dependencies, successfully exit, no need to run ansible-galaxy install
    if requirements == []:
        sys.exit(0)

    ephemeral_dir = os.getenv("MOLECULE_EPHEMERAL_DIRECTORY")
    debug_mode = os.getenv("MOLECULE_DEBUG") == "True"

    if ephemeral_dir is None:
        print("This tool should be used with molecule. The variable MOLECULE_EPHEMERAL_DIRECTORY is not defined")
        sys.exit(1)

    roles_path = "{}/roles".format(ephemeral_dir)
    command = ["ansible-galaxy", "install", "--role-file",
               requirements_path, "--roles-path", roles_path, "--force"]

    if debug_mode:
        command.append("-vvv")

    import subprocess

    subprocess.call(command)


if __name__ == "__main__":
    main()
