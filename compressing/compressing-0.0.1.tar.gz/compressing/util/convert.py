#!/usr/local/bin/python
# coding: utf-8

import networkx as nx
import re


def convert_input(file_path):
    """
    Converts input graph
    """
    graph = nx.nx_agraph.read_dot(file_path)
    converted_graph = nx.DiGraph(graph)

    find_discharges(converted_graph)

    return converted_graph


def raw_formula(formula):
    if re.match(r'^.*[0-9]+$', formula):
        st = formula.split("  ")
        print formula
        print st
        print "\n"
    else:
        print formula
        print "\n"


def find_discharges(graph):
    nodes_key = {}
    for node in graph.nodes():
        label = graph.node[node]["label"]
        if re.match(r'\[(.+)\]([0-9][0-9]*)', label):
            match = re.search(r'\[(.+)\]([0-9][0-9]*)', label)
            # print match.group(0), "|", match.group(1), "|", match.group(2)
            if match.group(2) not in nodes_key:
                nodes_key[match.group(2)] = [node]
            else:
                nodes_key[match.group(2)].append(node)
        elif re.match(r'(.+) ([0-9][0-9a-z]*)', label):
            match = re.match(r'(.+) ([0-9][0-9a-z]*)', label)
            # print match.group(0), "|", match.group(1), "|", match.group(2)
            if match.group(2) not in nodes_key:
                nodes_key[match.group(2)] = [node]
            else:
                nodes_key[match.group(2)].append(node)

    for key, nodes in nodes_key.items():
        target, = get_non_hypothesis(graph, nodes)
        nodes.remove(target)
        for node in nodes:
            graph.add_edge(node, target, color="green")

    return graph


def get_non_hypothesis(graph, nodes):
    non_hypothesis = []
    for node in nodes:
        if graph.in_degree(node) > 0:
            non_hypothesis.append(node)
    return non_hypothesis
