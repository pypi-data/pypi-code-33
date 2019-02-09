#!/usr/bin/env python3
from jinja2 import Environment, PackageLoader
import os, pathlib
import yaml
import logging

from pathlib import Path

logger = logging.getLogger('canni')


class Settings:
    def __init__(self, path_to_settings_file: str):
        with open(path_to_settings_file, 'r') as f:
            self._yaml_settings = yaml.safe_load(f)

        self._config_root_dir = Path(path_to_settings_file).parent

    @property
    def sources(self):
        return self._config_root_dir / Path(self._yaml_settings['sources'])

    @property
    def bundlers(self):
        return self._config_root_dir / Path(self._yaml_settings['bundlers'])

    @property
    def html_index_render_path(self):
        return Path(self._yaml_settings.get('html_index_render_path', 'index.html'))

    @property
    def html_index_pagetitle(self):
        return Path(self._yaml_settings.get('html_index_pagetitle', 'Canni Demo!'))


class Message:
    def __init__(self, name: str, text: list, title: str, checkbox: bool = False, keybind=None):
        self.name = name

        # Should the text be a single text line and not a list, make it a list.
        if type(text) == str:
            text = [text]

        self.text = text
        self.title = title
        self.checkbox = checkbox
        self.keybind = keybind

    @classmethod
    def from_yaml(cls, message):
        # Define "required" and optional parameters here. If access is by key value the value is required and parsing
        # will fail if it is not there. If access is by `.get()` then the value is optional, as it'll not fail parsing.
        return cls(
            message["name"],
            message["text"],
            message["title"],
            message.get("checkbox", False),
            message.get("keybind", None)
        )


class Tab:
    def __init__(self, name: str, sources: list, sources_directory: Path, with_items: dict = None, app: str = None):
        logger.debug('creating tab with name %s, sources: %s, sources directory %s, with items %s, app %s' %
                     (name, sources, sources_directory, with_items, app))

        self.name = name
        self.sources = []

        for src in sources:
            self.sources.append(sources_directory / Path(src))
        logger.debug('sources added as: %s' % self.sources)

        self._with_items = with_items
        self._app = app
        self._messages = []

        self._populate()

    def _populate(self):
        for src in self.sources:
            with open(str(src), 'r') as f:
                yaml_source = yaml.safe_load(f)
            logger.debug(yaml_source)
            for msg in yaml_source.get('messages'):
                # TODO: implement the with_items here.
                self._messages.append(Message.from_yaml(message=msg))

    @property
    def messages(self):
        return self._messages


class Bundle:
    def __init__(self, title: str, tabs: list, descriptive_title: str = None, render_path: str = None):
        self.title = title
        self.tabs = tabs

        # Since it's optional we'll just make it the normal title if required.
        if descriptive_title is None:
            descriptive_title = title
        self.descriptive_title = descriptive_title

        # Since it's optinal, we'll just generate a path based on the title.
        if render_path is None:
            render_path = "empty-render-paths/%s.html" % title
        self.render_path = render_path

    @classmethod
    def from_file(cls, bundle_path: Path, sources_directory: Path):
        tabs = []
        with open(str(bundle_path), 'r') as f:
            yaml_bundle = yaml.safe_load(f)

        for tab in yaml_bundle.get('tabs', []):
            tabs.append(
                Tab(tab['title'], tab['sources'], sources_directory, tab.get('with', None), tab.get('app', None))
            )

        return cls(yaml_bundle['title'], tabs, yaml_bundle.get('descriptive_title', None),
                   yaml_bundle.get('render_path'))


class XuttReader:
    def __init__(self, config_path: str):
        logger.debug('starting app, config_path: %s' % config_path)
        self.settings = Settings(config_path)
        self.bundles = []
        self._load_bundles(self.settings.bundlers, self.settings.sources)

    def _load_bundles(self, bundles_directory: Path, sources_directory: Path):
        for bundle_path in [x for x in bundles_directory.iterdir() if x.is_file() and x.suffix == '.yml']:
            logger.debug('loading bundle from %s' % bundle_path)
            self.bundles.append(Bundle.from_file(bundle_path, sources_directory))


class StaticHtmlGenerator:
    def __init__(self, output_directory, print_before_write=False, conf_path='xutt-data/xutt.yml'):
        """
        Initialises the StaticHtmlGenerator
        :param output_directory: directory where the html files should be generated/written in.
        :param print_before_write: print html to stdout before writing to file.
        """
        self.output_directory = output_directory
        self.print_before_write = print_before_write
        self.xutt_reader = XuttReader(conf_path)
        self.rendered_things = []
        self.jinja2_env = Environment(loader=PackageLoader('canni', 'templates'))  # this doesn't seem right (package)

    def render(self):
        for bundle in self.xutt_reader.bundles:
            self.render_bundle(bundle, pagetitle=bundle.title, output_filename=bundle.render_path)

        self.render_index(
            output_filename=self.xutt_reader.settings.html_index_render_path,
            pagetitle=self.xutt_reader.settings.html_index_pagetitle
        )

    def render_index(self, *, output_filename, pagetitle):
        """
        Renders an index page which links to all rendered switch-pages.
        :param output_filename: name of the file to be rendered.
        :param pagetitle: html-title for the page.
        """
        rendered = self.jinja2_env.get_template('index.html').render(things=self.rendered_things, pagetitle=pagetitle)
        self._write_to_file(rendered, output_filename)

    def render_bundle(self, bundle, *, output_filename, pagetitle):
        """
        Renders a specific Switch of a configuration as html page.
        :param bundle: The bundle to be rendered.
        :param output_filename: name of the file to be rendered.
        :param pagetitle: html-title for the page.
        """
        rendered = self.jinja2_env.get_template('switch.html').render(bundle=bundle, pagetitle=pagetitle)
        self._write_to_file(rendered, output_filename)
        self.rendered_things.append({'filename': output_filename, 'pagetitle': pagetitle})

    def _write_to_file(self, content, output_filename):
        """
        Write content into a file, which path is determined based on the set output_directory and the output_filename parameter.
        :param content: content to be written into the file.
        :param output_filename: name of the file to be written.
        """
        if self.print_before_write:
            print(content)
        fullpath = pathlib.Path(self.output_directory, output_filename)
        fullpath.parent.mkdir(parents=True, exist_ok=True)
        with fullpath.open('w') as f:
            f.write(content)


if __name__ == '__main__':
    shg = StaticHtmlGenerator(output_directory='gitlab-pagesX')
    shg.render()
