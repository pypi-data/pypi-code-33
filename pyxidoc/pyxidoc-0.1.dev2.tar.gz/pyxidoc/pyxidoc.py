#! /usr/bin/env python3
"""Simple documentation tool - collects all docstrings from given module."""

import ast
import fnmatch
import sys
from pathlib import Path


TYPES = [ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module]
EXPR = {
    ast.BoolOp: "bool",
    ast.BinOp: "binary op result",
    ast.UnaryOp: "unary op result",
    ast.Lambda: "lambda expression",
    ast.IfExp: "if-else expression",
    ast.Dict: "dict",
    ast.Set: "set",
    ast.ListComp: "list",
    ast.SetComp: "set",
    ast.DictComp: "dict",
    ast.GeneratorExp: "generator object",
    ast.Await: "await object",
    ast.Yield: "yield object",
    ast.YieldFrom: "yield object",
    ast.Compare: "bool",
    ast.Call: "function call result",
    ast.Num: "number",
    ast.Str: "string",
    ast.FormattedValue: "string",
    ast.JoinedStr: "string",
    ast.Bytes: "byte-string",
    ast.NameConstant: "name constant string",
    ast.Ellipsis: "ellipsis",
    ast.Constant: "constant",
    ast.Attribute: "attribute",
    ast.Subscript: "subscript",
    ast.Starred: "starred",
    ast.Name: "name string",
    ast.List: "list",
    ast.Tuple: "tuple",
}
VALUES = (
    ast.Await,
    ast.Yield,
    ast.YieldFrom,
    ast.FormattedValue,
    ast.NameConstant,
    ast.Constant,
    ast.Attribute,
    ast.Subscript,
    ast.Starred,
)


class PyxidocError(Exception):
    """Base class for all pyxidoc exceptions."""

    def __init__(self, prefix, message):
        """Create templated error."""
        self.message = "ERROR({}):{}".format(prefix, message)
        super().__init__()


class Node:
    """Base class for all relevant AST nodes."""

    def __init__(self, node, fname=None, level=0):
        """Instantiate generic node."""
        if not isinstance(node, tuple(TYPES)):
            raise PyxidocError("Node", "Irrelevant type ...")
        self._node = node
        self._fname = fname
        self._name = ""
        self._type = ""
        self._level = level
        self._prefix = "\t" * self._level
        self._children = []
        self._collect_children(self._level + 1)

    def name(self):
        """Define placeholder for the node name."""
        return self._name

    def type(self):
        """Return node type."""
        return self._type

    def descr(self):
        """Provide short description."""
        return "{} {}".format(self.type(), self.name())

    def docstr(self):
        """Return node docstring."""
        return str(ast.get_docstring(self._node))

    def summary(self):
        """Return the first line of the docstring."""
        return self.docstr().split("\n")[0]

    def level(self):
        """Return nesting level of the node."""
        return self._level

    def children(self):
        """Return all nested nodes."""
        return self._children

    def _collect_children(self, level):
        res = [node2class(i, level=level) for i in self._node.body]
        self._children += filter(None, res)

    def __str__(self):
        """Return repr result for conversion to string."""
        return self.__repr__()

    def __repr__(self):
        """Return string representation of the node."""
        hdr = self._prefix + "{} {}:\n".format(self.type(), self.name())
        info = self._prefix + "\tdocstring: {}\n".format(
            self.docstr().replace("\n", "\n\t" + self._prefix, -1)
        )
        if self._children != []:
            children = "\n" + "\n".join([str(i) for i in self._children])
        else:
            children = ""
        return hdr + info + children


class Mod(Node):
    """Specialised class for the ast.module."""

    def __init__(self, node, fname):
        """Instantiate module."""
        super().__init__(node, fname=fname, level=0)
        self._type = "Module"
        self._name = Path(self._fname).relative_to(BASEPATH)
        if self._name.stem == "__init__":
            self._name = self._name.parent
            self._type = "Package"

    def __repr__(self):
        """Return formatted basic file information."""
        sep = "=" * 70 + "\n"
        hdr = "{} {}:\n".format(self.type(), self.name())
        info = "\tdocstring: {}\n".format(
            self.docstr().replace("\n", "\n\t" + self._prefix, -1)
        )
        if self._children != []:
            children = "\n" + "\n".join([str(i) for i in self._children])
        else:
            children = "\tchildren: None\n"
        return sep + hdr + info + children


class Fun(Node):
    """Specialised function (and asyncfunction) class."""

    def __init__(self, node, level):
        """Instantiate function."""
        super().__init__(node, level=level)
        self._type = "Function"
        returns = set()
        self._get_returns(self._node, returns)
        exceptions = set()
        self._get_exceptions(self._node, exceptions)
        decors = self._get_decorators()
        if self._node.name == "__init__":
            self._name = "Constructor"
        elif self._node.name == "__del__":
            self._name = "Destructor"
        elif self._node.name == "__str__":
            self._name = "As_String"
        elif self._node.name == "__repr__":
            self._name = "As_Text"
        else:
            self._name = self._node.name
            if self._name.startswith("_"):
                self._type = "Private " + self._type
        self._name += "({}) -> {}".format(
            ", ".join([i.arg for i in self._node.args.args]),
            tuple(returns),
        )
        if exceptions:
            self._name += ", raises: {}".format(tuple(exceptions))
        if decors:
            self._name += ", annotated as: {}".format(tuple(decors))

        self._level = level

    def _get_returns(self, node, res):
        """Collect and evaluate ast.return statements."""
        for i in ast.iter_child_nodes(node):
            if isinstance(i, ast.Return):
                if isinstance(i.value, VALUES):
                    res.add(EXPR.get(type(i.value.value), None))
                else:
                    if isinstance(i.value, ast.Call):
                        call = "result of {}()"
                        if getattr(i.value.func, "id", None) is not None:
                            res.add(call.format(i.value.func.id))
                        else:
                            res.add(call.format(i.value.func.attr))
                    else:
                        res.add(EXPR[type(i.value)])
            else:
                self._get_returns(i, res)

    def _get_exceptions(self, node, errors):
        """Collect and evaluate ast.raise statements."""
        for i in ast.iter_child_nodes(node):
            if isinstance(i, ast.Raise):
                errors.add(i.exc.func.id)
            else:
                self._get_exceptions(i, errors)

    def _get_decorators(self):
        """Collect function decorators."""
        return [i.id for i in self._node.decorator_list]


class Cls(Node):
    """Specialised class for ast.class information."""

    def __init__(self, node, level):
        """Instantiate class."""
        super().__init__(node, level=level)
        if self._node.bases != []:
            bases = ", ".join([i.id for i in self._node.bases])
        else:
            bases = "Object"
        self._name = "{} (base: {})".format(self._node.name, bases)
        self._type = "Class"
        if self._node.name.startswith("_"):
            self._type = "Private " + self._type
        self._level = level


def node2class(node, fname=None, level=0):
    """Create class from AST node."""
    kind = type(node)
    if kind == ast.Module:
        return Mod(node, fname)
    if kind == ast.ClassDef:
        return Cls(node, level=level)
    if kind in [ast.FunctionDef, ast.AsyncFunctionDef]:
        return Fun(node, level=level)
    return None


def collect_files(path, result, pattern="*.py"):
    """Collect file list according to pattern."""
    if isinstance(path, (Path, str)):
        folder = Path(path).resolve().expanduser()
        for entry in folder.iterdir():
            if entry.is_dir():
                collect_files(entry, result, pattern)
            elif entry.is_file():
                if fnmatch.fnmatch(entry, pattern):
                    result.append(entry)


def md_escape_underscores(text):
    """Prepend underscores with backslashes."""
    return text.replace("_", r"\_")


def md_heading(text, level=0):
    """
    Create title/heading.

    Level 0 means document title, level 1-3 - heading 1-3.
    """
    if level >= 3:
        return text
    if level == 0:
        return "{} {}".format("#", text)
    return "\n{} {}\n".format((level + 1) * "#", text)


def md_nested_list(datalist, res, level=0):
    """Create MD list from python list."""
    prefix = level * "  "
    if datalist is not None and isinstance(datalist, list) and datalist != []:
        res.append("")
        for i in datalist:
            if isinstance(i, list):
                md_nested_list(i, res, level + 1)
            else:
                res.append(
                    prefix + "- " + md_escape_underscores(i.descr()) + "  "
                )
                if i.summary() != "None":
                    res.append("  " + prefix + i.summary())
                else:
                    res.append("  " + prefix + "has no docstring")
                md_nested_list(i.children(), res, level + 1)


def result2md(nodes):
    """Convert result to Markdown."""
    res = []
    res.append(md_heading("API docs for " + BASEPATH.name))
    for node in nodes:
        res.append(
            md_heading(md_escape_underscores(node.descr()), node.level() + 1)
        )
        summary = node.summary()
        if summary != "None":
            res.append(summary)
        else:
            res.append("{} has no docstring.".format(node.type()))
        md_nested_list(node.children(), res, node.level())
    return "\n".join(res)


def result2string(nodes):
    """Convert result list to string."""
    return "\n".join([str(i) for i in nodes])


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Missing module path .. ")
        sys.exit(1)
    BASEPATH = Path(sys.argv[1]).expanduser().resolve()
    RES = []
    collect_files(BASEPATH, RES)
    RES2 = []
    for f in RES:
        with open(f, "r") as infile:
            RES2.append(node2class(ast.parse(infile.read()), fname=f, level=0))
    print(result2md(sorted(RES2, key=lambda x: x.name())))
