
from pathlib import Path
from subprocess import run

import toml
from click import echo, group, prompt, argument, option, secho, edit, style, Choice, launch, pass_context
from dada import projects
from dada.projects import Project, Kind, create_project, PROJECT_CONFIG_FILENAME, BaseConfig, print_summary, Category, \
    save_project_config, USER_BASE_CONFIG_PATH, print_error, print_info, print_warning
from pick import pick

PRIMARY_COLOR = 'blue'


@group()
def cli():
    pass


@cli.command()
@argument('shortcut', required=False)
def docs(shortcut):
    project = get_project(shortcut)
    documentation = project.get_config('documentation')
    if documentation:
        launch(documentation)
    else:
        print_warning('No documentation defined for {project}')


@cli.group(invoke_without_command=True)
@pass_context
def config(context):
    if context.invoked_subcommand is None:
        local_config_path = Path('.', PROJECT_CONFIG_FILENAME)
        if local_config_path.is_file():
            project = Project.local()
            config_path = project.path / PROJECT_CONFIG_FILENAME
            edit_command = BaseConfig.get('config-edit-command')
            run([edit_command, config_path])
        else:
            print(f'Creating new project config file {PROJECT_CONFIG_FILENAME}')
            converter = lambda kind: str(kind)
            kind_key = prompt(style('Kind', fg=PRIMARY_COLOR), type=Choice(Kind.all()), default=None, value_proc=converter)
            title = prompt('Title?')
            shortcut = prompt('Shortcut?')
            save_project_config(path=local_config_path, title=title, kind_key=kind_key, shortcut=shortcut)



@config.command()
@argument('shortcut', required=False)
def project(shortcut):
    local_config_path = Path('.', PROJECT_CONFIG_FILENAME)
    if shortcut or local_config_path.is_file():
        project = get_project(shortcut)
        config_path = project.path / PROJECT_CONFIG_FILENAME
        edit_command = BaseConfig.get('config-edit-command')
        run([edit_command, config_path])
    else:
        print(f'Creating new project config file {PROJECT_CONFIG_FILENAME}')
        converter = lambda kind: str(kind)
        kind_key = prompt(style('Kind', fg=PRIMARY_COLOR), type=Choice(Kind.all()), default=None, value_proc=converter)
        title = prompt('Title?')
        shortcut = prompt('Shortcut?')
        save_project_config(path=local_config_path, title=title, kind_key=kind_key, shortcut=shortcut)


@config.command()
def list():
    BaseConfig.print()


@config.command()
@argument('key', required=False)
def kind(key):
    if key:
        kind = Kind.get(key)
    else:
        project = Project.local()
        kind = project.kind
    editor = BaseConfig.get('edit-config')
    run([editor, kind.config_file])



@config.command()
def base():
    path = USER_BASE_CONFIG_PATH
    editor = BaseConfig.get('edit-config')
    if editor:
        run([editor, path])
    else:
        launch(str(path))


@cli.command()
@argument('shortcut', required=False)
def output(shortcut):
    project = get_project(shortcut)
    project.show_output()


@cli.command()
@argument('kind')
@option('--title', prompt=True)
def new(kind, title):
    create_project(kind=kind, title=title)


@cli.command()
@argument('shortcut')
def debug(shortcut):
    project = get_project(shortcut)
    print(project.__dict__)


@cli.command()
@argument('shortcut', required=False)
def build(shortcut):
    project = get_project(shortcut)
    project.build()


@cli.command()
@argument('shortcut', required=False)
def serve(shortcut):
    project = get_project(shortcut)
    project.serve()


@cli.group(invoke_without_command=True)
@pass_context
def edit(context):
    if context.invoked_subcommand is None:
        Project.local().edit()


@edit.command()
@argument('shortcut', required=False)
def project(shortcut):
    project = get_project(shortcut)
    project.edit()


@edit.command()
@argument('key', required=False)
def kind(key):
    if key:
        kind = Kind.get(key)
    else:
        project = Project.local()
        kind = project.kind
    kind.edit()


@cli.command()
@argument('shortcut', required=False)
def start(shortcut):
    project = get_project(shortcut)
    project.start()


@cli.command()
@argument('component')
def update(component):
    project = Project.local()
    if not project:
        print_error('No project config file found in current directory')
        exit()
    print_info(f'Updating component "{component}" of project {project.title}')
    project.update(component)


@cli.command()
@argument('component')
def upstream(component):
    project = Project.local()
    project.upstream(component)


@cli.group(invoke_without_command=True)
@pass_context
def info(context):
    if context.invoked_subcommand is None:
        project = Project.local()
        print_summary(project)



@info.command()
@argument('shortcut', required=False)
def project(shortcut):
    project = get_project(shortcut)
    print_summary(project)


@info.command()
@argument('key')
def kind(key):
    kind = Kind.get(key)
    print_summary(kind, additional_keys=BaseConfig.get('kind-keys'))


@cli.command()
def init():
    title = prompt(text='Title')
    shortcut = prompt(text='Shortcut')
    kind, _ = pick([str(kind) for kind in Kind.all()], 'Please choose kind of project:')
    data = {
        'title': title,
        'shortcut': shortcut,
        'kind': kind
    }
    with Path(projects.PROJECT_CONFIG_FILENAME).open('w') as f:
        toml.dump(data, f)


@cli.group(invoke_without_command=True)
@pass_context
def list(context):
    if context.invoked_subcommand is None:
        for project in Project.all():
            shortcut = project.get_config('shortcut')
            if shortcut:
                echo(f'{shortcut}\t{project.title}')


@list.command()
def kinds():
    for kind in Kind.all():
        print(kind)


@list.command()
def categories():
    for category in Category.all():
        print(category)


def get_project(shortcut):
    if shortcut:
        return Project.from_shortcut(shortcut)
    elif Project.local():
        return Project.local()
    else:
        print_error(f'No project found')
        exit()


