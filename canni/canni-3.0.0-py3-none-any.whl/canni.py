from jinja2 import Environment, PackageLoader
import importlib
import shutil, os


class StaticHtmlGenerator:
    def __init__(self, switch_name, output_path=None):
        self.switch_name = switch_name
        if output_path is not None:
            self.output_path = output_path
        else:
            self.output_path = 'output/{}.html'.format(self.switch_name)
        self._clear_output_directory()
        env = Environment(loader=PackageLoader('canni','templates'))
        self.index_template = env.get_template('index.html')
        self._import_switch(switch_name)

    def _import_switch(self, conf_name):
        conf_module = importlib.import_module("configurations.{}".format(conf_name))
        self.switch = conf_module.Switch()

    def render(self):
        for tab in self.switch.get_tabinfos():
            tab.zipped_choices=self._zip_choices(tab)
        rendered = self.index_template.render(switch=self.switch)
        print(rendered)
        self._write_to_file(rendered)

    def render_tab(self, tab):
        rendered = self.index_template.render(seq=self._zip_choices(tab))
        print(rendered)
        self._write_to_file(rendered, 'output/{}.html'.format(tab.name))

    def _write_to_file(self, content, output_path=None):
        if output_path is None:
            output_path = self.output_path
        with open(output_path, 'w') as f:
            f.write(content)

    def _clear_output_directory(self):
        shutil.rmtree('output')
        os.makedirs('output')

    def _zip_choices(self, tab):
        zipped_choices = []
        for oc in tab.ordered_choices:
            zipped_choices.append((oc, tab.choices[oc]['text']))
        return zipped_choices


if __name__ == '__main__':
    shg = StaticHtmlGenerator('tripletrouble', output_path='gitlab-pages/index.html')
    shg.render()
