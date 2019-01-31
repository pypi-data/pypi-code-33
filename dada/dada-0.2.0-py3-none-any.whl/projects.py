from dataclasses import dataclass
from os import environ
from pathlib import Path
from shutil import copy, copytree, move
from subprocess import run, Popen, DEVNULL
from typing import List

import toml
from click import secho, confirm, echo, launch

PROJECT_CONFIG_FILENAME = '.dadaproject.toml'
KIND_CONFIG_FILENAME = 'config.toml'

APP_CONFIG_DIR = Path(__file__).parent / 'config'
APP_BASE_CONFIG_PATH = APP_CONFIG_DIR / 'base.toml'
APP_KINDS_CONFIG_PATH = APP_CONFIG_DIR / 'kinds.toml'
APP_KINDS_DIR = Path(__file__).parent / 'kinds'

USER_CONFIG_DIR = environ.get('$XDG_CONFIG_HOME', Path.home() / '.config' / 'dada')
if not USER_CONFIG_DIR.exists():
    USER_CONFIG_DIR.mkdir(parents=True)
USER_BASE_CONFIG_PATH = USER_CONFIG_DIR / 'base.toml'
if not USER_BASE_CONFIG_PATH.exists():
    USER_BASE_CONFIG_PATH.touch()
USER_KINDS_DIR = USER_CONFIG_DIR / 'kinds'

STARTER_SYMBOL = '==> '
PRIMARY_COLOR = 'yellow'


class BaseConfig:
    with APP_BASE_CONFIG_PATH.open() as f:
        base_config = toml.load(f)

    if USER_BASE_CONFIG_PATH.exists():
        with USER_BASE_CONFIG_PATH.open() as f:
            user_base_config = toml.load(f)
    else:
        USER_BASE_CONFIG_PATH.touch()
        user_base_config = {}

    @classmethod
    def keys(cls):
        app_config_keys = list(cls.base_config)
        user_config_keys = list(cls.user_base_config)
        return app_config_keys + user_config_keys

    @classmethod
    def get(cls, key: str):
        if key in cls.user_base_config:
            return cls.user_base_config[key]
        elif key in cls.base_config:
            return cls.base_config[key]

    @classmethod
    def print(cls):
        for key in cls.keys():
            print(f'{key}: {cls.get(key)}')


class Project:
    store = {}
    ready = False

    @classmethod
    def init(cls):
        config_paths = cls.project_config_paths()
        for path in config_paths:
            cls.add_from_config_path(path)
        cls.ready = True

    @classmethod
    def project_config_paths(cls):
        if not BaseConfig.get('dadapath'):
            print_warning('Could not look for projects because no project directories are defined.')
            return []
        config_paths = []
        dirs = [Path(dir).expanduser() for dir in BaseConfig.get('dadapath')]
        for dir in dirs:
            for config in dir.glob(f'*/{PROJECT_CONFIG_FILENAME}'):
                config_paths.append(config)
        return config_paths

    @staticmethod
    def local():
        potential_project_dirs = (Path('.'), Path('..'))
        for dir in potential_project_dirs:
            config_file = dir / PROJECT_CONFIG_FILENAME
            if config_file.exists():
                with config_file.open() as f:
                    config_dict = toml.load(f)
                    return Project(config_dict, path=dir)
        return None

    @classmethod
    def from_shortcut(cls, shortcut):
        if shortcut == 'local':
            return Project.local()
        else:
            return cls.store.get(shortcut, None)

    @classmethod
    def shortcuts(cls):
        return cls.store.keys()

    @classmethod
    def add_from_config_path(cls, config_path: Path):
        with config_path.open() as f:
            try:
                dictionary = toml.load(f)
            except Exception:
                print(f'Could not read config file {config_path}.')
                return
        project_path = config_path.parent
        project = Project(dictionary, project_path)
        shortcut = project.get_config('shortcut')
        Project.store[shortcut] = project

    @classmethod
    def all(cls):
        return Project.store.values()

    @classmethod
    def from_path(cls, path: Path):
        with open(path / PROJECT_CONFIG_FILENAME) as f:
            dictionary = toml.load(f)
        return Project(dictionary, path=path)

    def __init__(self, config_dictionary: dict, path: Path):

        if not config_dictionary:
            echo(f'Problem with reading project config from {path}')
            return
        else:
            self._config_dictionary = config_dictionary

        if 'kind' in config_dictionary:
            self.kind = Kind.get(config_dictionary['kind'])
        else:
            self.kind = 'undefined'

        self.path = path.absolute()

        if self.get_config('code-path'):
            self.code_path = self.path / self.get_config('code-path')
        else:
            self.code_path = self.path

        if self.get_config('web-path'):
            self.web_path = self.path / self.get_config('web-path')
        else:
            self.web_path = self.path

        self.config_path = self.path / PROJECT_CONFIG_FILENAME

        self.title = config_dictionary.get('title', None)

    def get_config(self, key):
        if key in self._config_dictionary:
            return self._config_dictionary[key]
        elif hasattr(self, 'kind') and self.kind and self.kind.get_config(key):
            return self.kind.get_config(key)
        elif BaseConfig.get(key):
            return BaseConfig.get(key)
        else:
            return None

    def build(self):
        build_commands = self.get_config('build').split(' ')
        if 'grunt' in build_commands:
            run(['dkill', 'grunt'])  # todo: change
        Popen(build_commands, cwd=self.code_path, stdout=DEVNULL)

    def serve(self):
        if self.kind == 'harp':
            run(['dkill', 'harp'])  # todo: change
        command = self.get_config('serve').split(' ') + [str(self.web_path)]
        url = self.get_config('de-url')
        print_info(f'Serving {self.title} with command', f'{command}', f'Development server at {url}')
        Popen(command, stdout=DEVNULL)

    def show_in_browser(self):
        old = self.get_config('dev-url')
        if not old:
            print_error('No local development URL defined. Cannot show page.')
            return
        elif old.startswith('htt'):
            url = old
        else:
            url = 'http://' + old

        browser = self.get_config('browser')
        if browser:
            run(['open', '-a', browser, url])  # todo: only macos
        else:
            launch(url)

    def open_document(self):
        document_path = self.path / 'document.pdf'
        print(document_path)
        if self.get_config('pdf-viewer'):
            command = ['open', '-a', self.get_config('pdf-viewer'), document_path]
            print_info(command)
            run(command)
        else:
            launch(str(document_path))

    def update(self, key: str):
        component = self.kind.component(key)
        source = self.kind.template_dir / component.template
        destination = self.path / component.path

        if destination.exists():
            if confirm('Do you want to override existing files?'):
                move(destination, destination.with_suffix('.backup' + destination.suffix))
            else:
                print_info('Dada does nothing but watching the sun')
                exit()
        copy(source, destination)

    def upstream(self, key: str):
        component = self.kind.component(key)
        installed = self.path / component.path
        template = self.kind.template_dir / component.template

        if confirm(f'Do you want to override {template}?'):
            copy(template, template.with_suffix('.backup'+ template.suffix))
            copy(installed, template)

    def edit(self):
        workspaces = list(self.path.glob('*.code-workspace'))
        edit = self.get_config('edit')

        if edit == 'code' and workspaces:
            path = workspaces[0]

        elif self.get_config('edit-path'):
            path = self.code_path / self.get_config('edit-path')

        else:
            path = self.code_path

        if edit:
            print_info(f'Edit {path} with configured editor {edit}')
            run([edit, path])
        else:
            print_info(f'Edit {path} with standard editor')
            launch(str(path))

    def start(self):
        self.edit()
        self.build()
        if self.kind.category == 'web':
            self.serve()
        self.show_output()

    def show_output(self):
        if self.kind.category == 'web':
            self.show_in_browser()
        elif self.kind.category == 'document':
            self.open_document()
        else:
            raise Exception('')


@dataclass
class Component():
    path: Path
    template: Path

    @staticmethod
    def from_dict(dictionary: dict):
        return Component(**dictionary)


class Kind:
    _store = {}
    ready = False

    @classmethod
    def init(cls):
        for kind_dir in USER_KINDS_DIR.iterdir():
            key = kind_dir.name
            kind_config = kind_dir / KIND_CONFIG_FILENAME
            if kind_config.exists():
                with kind_config.open() as f:
                    config_dict = toml.load(f)
            else:
                config_dict = {}
            kind = Kind(key=key, config_dictionary=config_dict)
            cls._store[key] = kind
        cls.ready = True

    @staticmethod
    def get(key):
        return Kind._store.get(key, None)

    @classmethod
    def all(cls):
        return cls._store.values()

    def __init__(self, config_dictionary: dict, key: str):
        self.key = key
        self._config_dict = config_dictionary
        if 'category' in config_dictionary:
            category_key = config_dictionary['category']
            self.category = Category.get(category_key)
        self.config_dir = USER_KINDS_DIR / key
        self.template_dir = self.config_dir / 'template'
        self.config_file = self.config_dir / KIND_CONFIG_FILENAME

    def __eq__(self, other):
        return str(self) == str(other)

    def __str__(self):
        return self.key

    def get_config(self, key):
        if key in self._config_dict:
            return self._config_dict[key]
        elif hasattr(self, 'category') and self.category.get_config(key):
            return self.category.get_config(key)
        else:
            return None

    def component(self, key):
        if 'components' in self._config_dict:
            if key in self._config_dict['components']:
                component_dict = self._config_dict['components'][key]
                return Component.from_dict(component_dict)
        else:
            return None

    def edit(self):
        edit = BaseConfig.get('dir-edit')
        if not edit:
            print_error('No dir-edit defined: command to edit directories')
        run([edit, self.config_dir])


class Category:
    _store = {}
    ready = False

    @classmethod
    def init(cls):
        with USER_BASE_CONFIG_PATH.open() as f:
            config = toml.load(f)
            categories_dict = config['categories']
        for key, category_dict in categories_dict.items():
            cls._store[key] = Category(dictionary=category_dict, key=key)
        cls.ready = True

    @classmethod
    def all(cls):
        return cls._store.values()

    @classmethod
    def get(cls, key):
        if key in cls._store:
            return cls._store[key]
        else:
            raise KeyError

    def __init__(self, dictionary: dict, key: str):
        self._config_dictionary = dictionary
        self.key = key

    def get_config(self, key):
        if key in self._config_dictionary:
            return self._config_dictionary[key]
        else:
            return None

    def __eq__(self, other):
        return str(self) == str(other)

    def __str__(self):
        return self.key


def create_project(kind: str, title: str):
    kind = Kind.get(kind)
    root = Path('.')

    directory_name = title.replace(' ', '-')

    template_path = kind.template_dir
    project_path = root / directory_name
    copytree(template_path, project_path)

    if hasattr(kind, 'subkinds'):
        subkinds = kind.subkinds
        for key, config in subkinds.items():
            subkind = Kind.get(key)
            source: Path = subkind.template_dir / config['template-path']
            destination = project_path / config['project-path']
            if source.is_dir():
                copytree(source, destination)
            else:
                copy(source, destination)

    save_project_config(path=project_path / PROJECT_CONFIG_FILENAME, kind_key=kind.key, title=title)
    secho(STARTER_SYMBOL, nl=False, fg=PRIMARY_COLOR)
    echo(f'Dada created a new project of kind {kind} for you!')


def save_project_config(path: Path, kind_key: str = None, title: str = None, shortcut: str = None):
    data = {}
    if kind_key:
        data['kind'] = kind_key
    if title:
        data['title'] = title
    if shortcut:
        data['shortcut'] = shortcut
    with path.open('w') as f:
        toml.dump(data, f)


def print_info(*strings):
    for string in strings:
        secho(STARTER_SYMBOL, fg='green', nl=False)
        echo(string)


def print_error(string, color='red'):
    secho(STARTER_SYMBOL + 'PROBLEM: ', fg=color, nl=False)
    echo(string)


def print_warning(string):
    secho(STARTER_SYMBOL + ' Warning: ', fg='blue', nl=False)
    echo(string)


def print_summary(object, additional_keys: List[str] = None, primary_color=PRIMARY_COLOR):
    secho('------------------------------------------------------------------------', fg=primary_color)
    if hasattr(object, 'title') and object.title:
        secho('title: ', nl=False, fg=primary_color)
        secho(object.title.upper(), bold=True)

    if additional_keys:
        keys = additional_keys + BaseConfig.get('keys')
    else:
        keys = BaseConfig.get('keys')

    for key in keys:
        if key in ['title']: continue
        snake_cased_key = key.replace('-', '_')
        if hasattr(object, snake_cased_key) and getattr(object, snake_cased_key) \
                and not callable(getattr(object, snake_cased_key)):
            value = getattr(object, snake_cased_key)
        elif object.get_config(key):
            value = object.get_config(key)
        else:
            continue
        secho(f'{key.replace("_", "-")}: ', nl=False, fg=primary_color)
        echo(f'{value}')
    secho('------------------------------------------------------------------------', fg=primary_color)


for cls in (Category, Kind, Project):
    if not cls.ready:
        cls.init()
