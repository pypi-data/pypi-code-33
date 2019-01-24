import helm_template_generator.args as args
import os
import sys
import json
from mako.template import Template


arg_opts = args.arg_options()


def check_dir(dir_path):
    """Get directory path for template."""
    dir = dir_path
    if dir == '.':
        dir = os.getcwd()
    if not os.path.exists(dir):
        print("directory does not exist, exiting")
        os._exit(1)
    return dir


def load_envs(arg_opts):
    env_file = arg_opts['envfile']
    envs = None
    if os.path.isfile(env_file):
        with open(env_file, 'r') as f:
            envs = json.load(f)
    return envs


def get_templates_path():
    """Template loader."""
    for path in sys.path:
        template_path = os.path.join(path, 'helm_template_generator', 'templates')
        if os.path.isdir(template_path):
            return template_path


def write_to_file(content, filepath, arg_opts):
    """Write out templates"""
    project = arg_opts['project']
    output = arg_opts['output']

    filename = os.path.basename(filepath).split('.')[0]
    ext = os.path.basename(filepath).split('.')[2]

    if filename == 'Chart':
        file_builder = "{}/{}.{}".format(project, filename, ext)
    else:
        file_builder = "{}/{}/{}.{}".format(project,
                                            'templates', filename, ext)

    outputpath = os.path.join(check_dir(output), file_builder)

    print(outputpath)

    directory = os.path.dirname(outputpath)

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(outputpath, 'w') as f:
        f.write(content)


def render_template(envs, filepath):
    template = open(filepath, 'r').read()

    rendered_template = Template(template).render(envs=envs)
    write_to_file(rendered_template, filepath, arg_opts)


def main():
    envs = load_envs(arg_opts)
    template_path = get_templates_path()
    for dirpath, _, filenames in os.walk(template_path):
        for f in filenames:
            filepath = os.path.join(dirpath, f)
            render_template(envs, filepath)


if __name__ == '__main__':
    main()
