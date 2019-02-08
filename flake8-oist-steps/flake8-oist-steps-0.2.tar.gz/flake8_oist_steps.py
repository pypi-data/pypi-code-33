# -*- coding: utf-8 -*-
"""Flake8 Plugin that check usage of STEPS simulator
"""
import ast


try:
    from flake8.engine import pep8 as stdin_utils
except ImportError:
    from flake8 import utils as stdin_utils


FUNC_RETURNING_TET = {"findTetByPoint", "getTetTetNeighb", "getTetTetNeighb"}
FUNC_RETURNING_TRI = {"getTetTriNeighb", "getTriTriNeighbs"}


class CheckVisitor(ast.NodeTransformer):
    """Traverse source code AST and check usage of STEPS functions
    """

    def __init__(self):
        self.steps_ids = dict()
        self.errors = []
        super(CheckVisitor, self).__init__()

    def visit_Assign(self, node):  # pylint: disable=C0103
        """Visit Python assignments

        track variables that store results STEPS functions
        returning identifiers
        """
        self.visit(node.value)
        steps_id = getattr(node.value, "steps_id", False)
        for target in node.targets:
            if steps_id:
                if isinstance(target, ast.Name):
                    self.steps_ids[target.id] = steps_id
                elif isinstance(target, ast.Subscript):
                    if isinstance(target.value, ast.Name):
                        self.steps_ids[target.value.id] = steps_id

    def visit_Compare(self, node):  # pylint: disable=C0103
        """visit Python comparison

        Ensure that variable containing STEPS identifiers are not compared to -1
        """
        self.visit(node.left)
        for operation in node.ops:
            if isinstance(operation, (ast.Eq, ast.NotEq)):
                for comp in node.comparators:
                    self.visit(comp)
                if isinstance(node.left, ast.Name):
                    if node.left.id in self.steps_ids:
                        if len(node.comparators) == 1:
                            if getattr(node.comparators[0], "is_minus_one", False):
                                self.errors.append(
                                    [
                                        node.lineno,
                                        node.col_offset,
                                        self.steps_ids[node.left.id],
                                        IdChecker,
                                    ]
                                )

    def visit_Num(self, node):  # pylint: disable=C0103,R0201
        """Visit number (Python 2)

        Mark node if value is -1
        """
        if node.n == -1:
            node.is_minus_one = True

    def visit_UnaryOp(self, node):  # pylint: disable=C0103,R0201
        """Visit number (Python 3)

        Mark node if value is -1
        """
        if isinstance(node.op, ast.USub):
            if isinstance(node.operand, ast.Num):
                if node.operand.n == 1:
                    node.is_minus_one = True

    def visit_Call(self, node):  # pylint: disable=C0103,R0201
        """visit function call

        Identify possible error according to called STEPS function
        """
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in FUNC_RETURNING_TET:
                node.steps_id = IdChecker.tet_id_mesg
            elif node.func.attr in FUNC_RETURNING_TRI:
                node.steps_id = IdChecker.tri_id_mesg


class IdChecker:
    """Flake8 checker to enforce usage of STEPS simulator"""

    name = "flake8_oist_steps"
    version = "0.0.1"
    tet_id_mesg = (
        "E421 consider using steps.geom.UNKNOWN_TET" " constant instead of -1."
    )
    tri_id_mesg = (
        "E422 consider using steps.geom.UNKNOWN_TRI" " constant instead of -1."
    )

    def __init__(self, tree, filename):
        self._tree = tree
        self._filename = filename

    @property
    def tree(self):
        """get source code Abstract Syntax Tree"""
        return self._tree

    @property
    def filename(self):
        """get source code filename"""
        return self._filename

    def run(self):
        """check the code"""
        tree = self.tree

        if self.filename == "stdin":
            lines = stdin_utils.stdin_get_value()
            tree = ast.parse(lines)

        visitor = CheckVisitor()
        visitor.visit(tree)
        for error in visitor.errors:
            yield error
