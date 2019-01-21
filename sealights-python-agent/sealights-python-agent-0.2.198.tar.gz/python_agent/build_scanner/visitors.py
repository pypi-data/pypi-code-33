import ast

from python_agent.build_scanner import ast_utils
from python_agent.build_scanner.method_hasher import MethodHasher


class SealightsVisitor(ast.NodeVisitor):

    def __init__(self, file_data):
        self.file_data = file_data
        self.method_hasher = MethodHasher(MethodCleanerVisitor)

    def visit_FunctionDef(self, node):
        self.file_data.methods.append(self.method_hasher.build_method(self.file_data, node.name, node))
        self.generic_visit(node)

    def visit_Lambda(self, node):
        if not hasattr(node, "name"):
            node.name = "(Anonymous)"
        self.file_data.methods.append(self.method_hasher.build_method(self.file_data, node.name, node))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.file_data.methods.append(self.method_hasher.build_method(self.file_data, node.name, node))
        self.generic_visit(node)

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Lambda):
            # klass.__str__ = lambda self: self.__unicode__().encode('utf-8') doesn't work
            if node.targets and hasattr(node.targets[-1], "id"):
                setattr(node.value, "name", node.targets[-1].id)
        self.generic_visit(node)


class MethodCleanerVisitor(ast.NodeVisitor):

    def __init__(self):
        self.traverse_node = None

    def visit_FunctionDef(self, node):
        if not self.traverse_node:
            self.traverse_node = node
        if node != self.traverse_node:
            ast_utils.clean_functiondef_body(node)
        self.generic_visit(node)

    def visit_Lambda(self, node):
        if not self.traverse_node:
            self.traverse_node = node
        if node != self.traverse_node:
            ast_utils.clean_lambda_body(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        if not self.traverse_node:
            self.traverse_node = node
        if node != self.traverse_node:
            ast_utils.clean_functiondef_body(node)
        self.generic_visit(node)
