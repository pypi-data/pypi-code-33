import io
import os

import requests

from tpyl import parse, rendering, utils


def load_context(var=None, context=None, env=True):
    ctx = {}
    context = utils.to_tuple(context or ())
    var = utils.to_tuple(var or ())
    env = True if env in (None, True,) else False

    # Populate environment to context
    if env:
        ctx.update(os.environ)

    # Read context files
    for c in context:
        ctx.update(parse.parse_context(c) or {})

    # Assign variables to context
    for v in var:
        key, value = parse.split_var(v)
        ctx[key] = value

    return ctx


def render_template(path, ctx, filters=None, stream=None):
    filters = utils.to_tuple(filters or ())
    stream = stream or io.StringIO()
    # Render the template
    if path == '-':
        tpl = rendering.render(stream.read(), ctx, filters=filters)
    elif utils.is_url(path):
        response = requests.get(path)
        response.raise_for_status()
        tpl = rendering.render(response.text, ctx, filters=filters)
    else:
        tpl = rendering.template(path, ctx, filters=filters)
    return tpl


def write_render(template, output=None, stream=None):
    if output:
        # Write to a file
        with open(output, 'w') as f:
            f.write(template)
    elif stream:
        # Print the template
        stream.write(template)
