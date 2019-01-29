from jinja2 import Environment, FileSystemLoader
from hamlish_jinja import HamlishExtension


class EngineHaml(object):
    def __init__(self, template_dirs):
        self.template_dirs = template_dirs
        self.jj2_env = Environment(
            loader=FileSystemLoader(template_dirs),
            extensions=[HamlishExtension]
        )
        # self.jj2_env.hamlish_mode = 'debug'

    def get_template(self, template_file):
        template = self.jj2_env.get_template(template_file)
        return template

    def apply_template(self, template, data, _):
        print("hello")
        rendered_content = template.render(**data)
        return rendered_content
