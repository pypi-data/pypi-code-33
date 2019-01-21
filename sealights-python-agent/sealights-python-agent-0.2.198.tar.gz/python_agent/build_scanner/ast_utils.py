import ast
import logging

from python_agent.common import constants
from python_agent.common.constants import AST_ARGUMENTS_EMPTY_VALUES

log = logging.getLogger(__name__)


def get_last_node(node):
    last_node = node
    body = getattr(node, "body", None)
    if body:
        if isinstance(body, list):
            last_node = node.body[-1] if node.body else node
        else:
            last_node = node.body
    max_lineno = node.lineno
    for child in ast.walk(last_node):
        if getattr(child, "lineno", -1) > max_lineno:
            last_node = child
            max_lineno = child.lineno
    return last_node


def clean_functiondef_body(node):
    if hasattr(node, "name"):
        node.name = ""
    if hasattr(node, "args"):
        node.args = clean_args(node)
    if hasattr(node, "body"):
        node.body = []
    if hasattr(node, "decorator_list"):
        node.decorator_list = []
    if hasattr(node, "returns"):
        node.returns = None


def clean_lambda_body(node):
    if hasattr(node, "name"):
        node.name = ""
    if hasattr(node, "args"):
        node.args = clean_args(node)
    if hasattr(node, "body"):
        node.body = []


def clean_args(node):
    kwargs = {}
    for field in ast.arguments._fields:
        if field in AST_ARGUMENTS_EMPTY_VALUES:
            kwargs[field] = AST_ARGUMENTS_EMPTY_VALUES.get(field)
    return ast.arguments(**kwargs)


def parse(source, filename='<unknown>', mode='exec', flags=ast.PyCF_ONLY_AST, is_apply_future=True):
    """
    Parse the source into an AST node.
    Equivalent to compile(source, filename, mode, PyCF_ONLY_AST).
    """
    try:
        return compile(source, filename, mode, flags)
    except SyntaxError as e:
        if "print" in e.text and is_apply_future:
            compile_flags = flags | constants.FUTURE_STATEMENTS["print_function"]
            return parse(source, filename, mode, flags=compile_flags, is_apply_future=False)
        around_source = source.split("\n")
        start = max(0, e.lineno - 4)
        end = min(len(around_source) - 1, e.lineno + 4)
        msg = "Failed parsing source code into ast. source=%s. args=%s" % ("\n".join(around_source[start:end]), e.args)
        error = SyntaxError(msg)
        error.text = e.text
        raise error
