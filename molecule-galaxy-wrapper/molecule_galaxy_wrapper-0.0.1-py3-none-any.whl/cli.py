import sys
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

    if 'dependencies' not in meta_requirements:
        print(
            "Format Error - Ansible Galaxy {} file does not contain main dependencies list".format(meta_requirements_path))
        sys.exit(1)

    print("Appending {} content into {} dependencies".format(
        requirements_path, meta_requirements_path))
    meta_requirements['dependencies'] = requirements
    dump(meta_requirements_path, meta_requirements)


if __name__ == "__main__":
    main()
