import jinja2

from tpyl.filters import load_filters


def render(content, context, filters=None):
    jinja2.filters.FILTERS.update(load_filters(filters) or {})
    return jinja2.Template(content).render(**context)


def template(file_path, context, filters=None):
    with open(file_path, 'r') as f:
        return render(f.read(), context, filters=filters)
