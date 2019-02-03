#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 14:48:09 2019

@author: Maria Climent-Pommeret
"""

class Node:
    """
    Basic Node Class

    Takes into parameter either:
        - a list of children
        - a single child
    """

    def __init__(self, children=None):
        self.pretty = "Basic Node"
        if not children:
            self.children = []
        elif hasattr(children, "__len__"):
            self.children = children[:]
        else:
            self.children = [children]

    def __str__(self):
        return "Node"

    def __repr__(self):
        return self.pretty


class RelevantDataNode(Node):
    """
    A node that contains all grammar rules.
    """
    pretty = "Relevant Data"

    def rewrite(self):
        code = "\\documentclass{article}\n"
        code += "\\usepackage{syntax}\n"
        code += "\\begin{document}\n"
        code += "\\begin{grammar}\n"

        previous_left = "S"
        for child in self.children:
            if child.left_member() == previous_left:
                code += child.rewrite_end()
            else:
                previous_left = child.left_member()
                code += child.rewrite_full()
        code += "\\end{grammar}\n\\end{document}\n"
        
        return code


class GrammarRuleNode(Node):
    """
    A node that contains a grammer rule.
    """
    pretty = "Grammar Rule"
    
    def left_member(self):
        return self.children.strip("'").strip('"').split(" ")[0]

    def rewrite_full(self):
        data = self.children.strip("'").strip('"').split(" ")
        if data[0].isupper() and data[0] != "S'":
            code = '\n\n    "%s" ::=' % data[0]
        else:
            code = '\n\n    <%s> ::= ' % data[0]

        for child in data[2:]:
            if child.isupper():
                code += ' "%s"' % child
            else:
                code += " <%s>" % child

        code += "\n"
        return code

    def rewrite_end(self):
        data = self.children.strip("'").strip('"').split(" ")
        code = "        \\alt"

        for child in data[2:]:
            if child.isupper():
                code += ' "%s"' % child
            else:
                code += " <%s>" % child

        code += "\n"
        return code