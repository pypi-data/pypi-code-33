default_filename = 'octohot.yml'
default_config = {
    'repositories': [],
    'github_token': None,
    'github_organization': None

}

repositories = config = None

import os
config_file = os.path.join(os.getcwd(), default_filename)


def load():
    global config
    global repositories

    import os.path
    if os.path.isfile(config_file):
        import yaml
        config = yaml.load(open(config_file, "r"))
    else:
        config = default_config

    from octohot.cli.git.repository import Repository
    repositories = [Repository(repo_name) for repo_name in
                    config['repositories']]


def save():
    import yaml
    yaml.dump(config, open(config_file, "w"), default_flow_style=False)


load()
