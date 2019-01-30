from jinja2 import Environment, FileSystemLoader
import sys, os
from qualifyr.utility import include_file


def create_html_report(json_data, output_dir = '.'):
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'html_report', 'templates')
    env = Environment( loader = FileSystemLoader(templates_dir) )
    env.globals['include_file'] = include_file
    env.globals['os'] = os
    template = env.get_template('main.html')
    
    
    filename = os.path.join(output_dir, 'qualifyr_report.html')
    with open(filename, 'w') as fh:
        fh.write(template.render(
            asset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html_report', 'assets'),
            json_data = json_data,
            h1 = "Overall Quality Report"
        ))
    