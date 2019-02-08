
import sys
import os
import re
import jinja2 as jj

dir_file = os.path.dirname(os.path.abspath(__file__))
dir_template = os.path.join(dir_file, 'templates')

loader = jj.FileSystemLoader(dir_template)

env = jj.Environment(loader=loader,
                     variable_start_string='__$',
                     variable_end_string='$__',
                     block_start_string='{%',
                     block_end_string='%}'
                     )


def build(data=None,
          save=True,
          save_path='saved',
          save_name='index.html',
          server_port=8081,
          verbose=True):
    """
    TBD
    """
    template_name = 'dashboard.template.html'
    template = env.get_template(template_name)
    content = template.render(data=data)

    if not save:
        return content

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # save dasboard
    file_path = os.path.join(save_path, save_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    if verbose:
        print('file {} created on disk'.format(file_path))
    dashboard_path = file_path

    # determine OS
    if sys.platform in ['darwin', 'linux']:
        suffix = 'sh'
    elif sys.platform == 'win32':
        suffix = 'bat'
    else:
        raise Exception('OS unknown: No web server launch script created')

    # launch web server script content
    content = 'python -m http.server {}'.format(server_port)

    # save script
    file_path = os.path.join(save_path, 'server.' + suffix)
    with open(file_path, 'w') as f:
        f.write(content)
    if verbose:
        print('file {} created on disk:'.format(file_path))
        print('\t{}'.format(content))
        print('Run it to launch web server and test dashboard')

    return dashboard_path


def minify(content):
    # remove js or css /* blah */ comments
    output = re.sub('/\*(.|\n)*?\*/', ' ', content)

    # remove js // blah comments
    output = re.sub('//\s.*?\n', ' ', output)

    # substitute all tabs, newlines and other
    # whitespace-like characters with single space
    # .strip() in the end will cut off any trailing whitespace
    output = re.sub('\s+', ' ', output).strip()

    return output
