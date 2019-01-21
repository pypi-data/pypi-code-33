# -*- coding: utf8 -*-
from ..scam import MLQueryVisitor


# noinspection PyClassicStyleClass
class LimitVisitor(MLQueryVisitor):
    def __init__(self):
        self.limit = None

    def generic_visit(self, node, parents=None, context=None):
        pass

    def visit_function_limit(self, node, parents=None, context=None):
        self.limit = node.limit
