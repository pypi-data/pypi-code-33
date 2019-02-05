from jinja2 import Environment, FileSystemLoader
import sys, os, datetime
from qualifyr.utility import include_file


def create_html_report(json_data, output_dir = '.', extra_columns = [], title = "Overall Quality Report"):
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'html_report', 'templates')
    env = Environment( loader = FileSystemLoader(templates_dir) )
    env.globals['include_file'] = include_file
    env.globals['os'] = os
    template = env.get_template('main.html')

    column_data =  '{ title: "Sample Name", data: "sample_name"}'
    if len(extra_columns) > 0:
        column_data = column_data + ', ' + ','.join(
            ['{{title: "{0}", data: "checks.{1}.{0}.metric_value" }}'.format(column['metric_name'], column['quality_file']) for column in extra_columns]
        )
    column_data = column_data + ', { title: "Result", data: "result" }'

    
    
    filename = os.path.join(output_dir, 'qualifyr_report.html')
    with open(filename, 'w') as fh:
        fh.write(template.render(
            asset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html_report', 'assets'),
            json_data = json_data,
            title = title,
            report_time = datetime.datetime.now().strftime("%H:%M %A %d-%m-%Y"),
            sample_numbers = len(json_data),
            num_of_pass_samples = len([sample for sample in json_data if sample['result'] == 'PASS']),
            num_of_warning_samples = len([sample for sample in json_data if sample['result'] == 'WARNING']),
            num_of_failure_samples = len([sample for sample in json_data if sample['result'] == 'FAILURE']),
            column_data = column_data,
            sort_column = len(extra_columns) + 2 # 2 default columns + extra columns
        ))
    