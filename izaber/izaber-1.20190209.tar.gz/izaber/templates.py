# Adds support for various templates
import jinja2
import datetime

from izaber.startup import initializer, request_initialize, app_config
from izaber.paths import paths
from izaber import config

compiled_templates = {}

template_loader = jinja2.FileSystemLoader(searchpath=[".","/"])
template_env = jinja2.Environment(loader=template_loader)

def tags_common():
    now = datetime.datetime.now()
    return {
        'now': now,
        'date': now.strftime('%Y-%m-%d'),
        'date_iso': now.isoformat(),
        'time': now.strftime('%H:%M:%S'),
        'dt': now.strftime('%Y-%m-%d_%H-%M-%S'),
        'config': config,
    }

def parse(template,**tags):
    template_fpath = paths.full_fpath(template)
    tags.update(tags_common())
    if template_fpath not in compiled_templates:
        compiled_templates[template_fpath] = \
            template_env.get_template(template_fpath)
    return compiled_templates[template_fpath].render(**tags)

def parsestr(template,**tags):
    now = datetime.datetime.now()
    tags.update(tags_common())
    return jinja2.Template(template).render(**tags)

@initializer('templates')
def initialize(**kwargs):
    request_initialize('config',**kwargs)

