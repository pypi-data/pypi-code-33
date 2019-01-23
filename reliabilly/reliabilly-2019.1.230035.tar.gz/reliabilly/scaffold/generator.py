from os import path, walk, makedirs
from jinja2 import Environment, FileSystemLoader
from inflection import camelize
from reliabilly.settings import Constants


def camelcase(item):
    return camelize(item)


class Generator:
    def __init__(self, **kwargs):
        self.open = kwargs.get(Constants.OPEN, open)
        self.mkdirs = kwargs.get(Constants.MKDIRS, makedirs)

    def replace_template_file(self, template_path, template_file, destination, **kwargs):
        environment = Environment(autoescape=True, loader=FileSystemLoader(template_path))
        service_name = kwargs.get(Constants.SERVICE_KEY, Constants.EMPTY)
        final_destination = destination.replace(Constants.SERVICE_REPLACE, service_name)[:-3]
        if not any(substring in template_file for substring in Constants.IGNORED_FILES):
            environment.filters[Constants.CAMELCASE_FILTER] = camelcase
            template = environment.get_template(template_file)
            self.write_converted_file(environment, final_destination, kwargs, template)

    def write_converted_file(self, environment, final_destination, kwargs, template):
        with self.open(final_destination, Constants.WRITE_FLAG) as file:
            file.write(template.render(kwargs, environment=environment))

    def process_template_files(self, service_name, priority, destination_dir=Constants.CURRENT_DIR):
        destination = path.join(destination_dir, service_name)
        makedirs(destination, exist_ok=True)
        current_dir = path.dirname(path.realpath(__file__))
        template_dir = path.join(current_dir, Constants.TEMPLATE_DIR)
        for directory, _, file_list in walk(template_dir):
            for file in file_list:
                new_path = destination + path.join(directory, file).split(Constants.TEMPLATE_DIR)[1]
                self. mkdirs(path.dirname(new_path), exist_ok=True)
                self.replace_template_file(directory, file, new_path, service=service_name, priority=priority)
        return True

    def scaffold_up_service(self, service_name, priority):
        return self.process_template_files(service_name, priority)


def scaffold_up_service(service_name, priority, generator=Generator()):
    return generator.scaffold_up_service(service_name, priority)
