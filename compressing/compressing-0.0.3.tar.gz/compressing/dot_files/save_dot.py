#!/usr/local/bin/python
# coding: utf-8


def save_dot(graph):
    """
    Parameters
    ----------
    graph: ProofGraph object
    """
    graph.save_dot("dot/output.dot")
