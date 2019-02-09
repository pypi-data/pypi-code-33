#!/usr/local/bin/python
# coding: utf-8
from pyparsing import empty

from util import constants

"""
This module provide the necessary functions to perform the compression
on object from ProofGraph class.

Exported functions
------------------
get_nodes_repeated_formulas: return a list of lists with all repeated
    occurrences of nodes with identical labels in same level of
    derivation tree.

identify_rule: identifies the rule and return the corresponding
    function that perform the rule.

exec_rule: performs two-node collapse.
"""

ATGT = "ancestor_target_feature"
CPS = "collapsed_feature"
HYP = "hypothesis_feature"


def get_nodes_repeated_formulas(proof_graph):
    """
    Return a list with all nodes selected for compression. Each member
    list is a list with nodes that have identical formulas in the same
    level of derivation tree.

    The ProofGraph object has a attribute 'nodes_level', a
    dictionary-like object that stores nodes per level in derivation
    tree.

    Parameters
    ----------
    proof_graph: ProofGraph object

    Returns
    -------
    repeated_formulas: List
        A List of list of nodes with repeated formulas in same level of
        derivation tree.
    """
    level = 0
    repeated_formulas = {}
    nodes_level = proof_graph.get_nodes_level()
    for level, nodes in nodes_level.items():
        repeated_formulas[level] = []
        nodes_formula = {}
        for node in nodes:
            formula = proof_graph.get_node_attribute(node,
                                                     constants.FORMULA)
            if formula in nodes_formula:
                nodes_formula[formula].append(node)
            else:
                nodes_formula[formula] = [node]
        for formula, nodes2 in nodes_formula.items():
            if len(nodes2) > 1:
                repeated_formulas[level].append(nodes2)
        level += 1
    return repeated_formulas


def identify_rule(graph, node_u, node_v):
    """
    Returns the appropriate function that performs the collapse of
    nodes node_u and node_v.

    Parameters
    ----------
    graph: ProofGraph object

    node_u, node_v: nodes
        Nodes in proof graph

    Returns
    -------
    function: function
        Function that performs the collapse of nodes
    """
    in_degree_u = graph.get_deductive_in_degree(node_u)
    in_degree_v = graph.get_deductive_in_degree(node_v)

    out_degree_u = graph.get_deductive_out_degree(node_u)
    out_degree_v = graph.get_deductive_out_degree(node_v)

    ancestor_target_u = graph.get_node_attribute(node_u, graph.ANCESTOR_TARGET)
    ancestor_target_v = graph.get_node_attribute(node_v, graph.ANCESTOR_TARGET)

    is_collapsed_u = graph.get_node_attribute(node_u, graph.COLLAPSED)
    is_collapsed_v = graph.get_node_attribute(node_v, graph.COLLAPSED)

    is_hypothesis_u = False
    is_hypothesis_v = False

    if in_degree_u == 0:
        is_hypothesis_u = True
    if in_degree_v == 0:
        is_hypothesis_v = True

    collapse_edge = common_out_neighbor(graph, node_v, node_u)

    formula_u = graph.get_node_attribute(node_u, "formula")
    formula_v = graph.get_node_attribute(node_v, "formula")

    # print "node_u: [ id: ", node_u, "formula: ", formula_u, ", ancestor: ", ancestor_target_u, "]"
    # print "node_v: [ id: ", node_v, "formula: ", formula_v, ", ancestor: ", ancestor_target_v, "]"

    features_u = get_node_features(graph, node_u)
    features_v = get_node_features(graph, node_v)

    if not collapse_edge:
        if not features_u and not features_v:
            return rule_1
        elif features_u == {HYP} and not features_v:
            return rule_2
        elif not features_u and features_v == {HYP}:
            return rule_3
        elif features_u == {HYP} and features_v == {HYP}:
            return rule_4
        elif features_u == {CPS} and not features_v:
            return rule_5
        elif features_u == {CPS} and features_v == {HYP}:
            return rule_6
        elif features_u == {ATGT} and features_v == {ATGT}:
            return rule_11
        elif (features_u == {ATGT} and not features_v) or \
                (not features_u and features_v == {ATGT}):
            return rule_11a
        elif (features_u == {ATGT} and features_v == {HYP}) or \
                (features_u == {HYP} and features_v == {ATGT}):
            return rule_11b
        elif (features_u == {ATGT, HYP} and not features_v) or \
                (not features_u and features_v == {ATGT, HYP}):
            return rule_11c
        elif (features_u == {ATGT, HYP} and features_v == {HYP}) or \
                (features_u == {HYP} and features_v == {ATGT, HYP}):
            return rule_11d
        elif features_u == {CPS, HYP} and features_v == {ATGT, HYP}:
            return rule_11d
        elif features_u == {ATGT} and features_v == {ATGT, HYP}:
            return rule_12
        elif features_u == {ATGT, HYP} and features_v == {ATGT}:
            return rule_13
        elif features_u == {ATGT, HYP} and features_v == {ATGT, HYP}:
            return rule_14
        elif features_u == {CPS} and features_v == {ATGT}:
            return rule_17
        elif features_u == {CPS} and features_v == {ATGT, HYP}:
            return rule_18
        elif features_u == {CPS, HYP} and features_v == {HYP}:
            return rule_11f
        else:
            raise Exception("0 - Regra desconhecida: ftu: {}, ftv: {}".format(
                features_u, features_v))
    else:
        if features_u == {ATGT} and features_v == {ATGT}:
            return rule_7
        elif features_u == {ATGT} and features_v == {ATGT, HYP}:
            return rule_8
        elif features_u == {ATGT, HYP} and features_v == {ATGT}:
            return rule_9
        elif features_u == {ATGT, HYP} and features_v == {ATGT, HYP}:
            return rule_10
        elif features_u == {CPS} and features_v == {ATGT}:
            return rule_15
        elif features_u == {ATGT} and features_v == {ATGT, HYP}:
            return rule_16
        elif features_u == {HYP, CPS} and features_v == {HYP, ATGT}:
            return rule_11e
        elif features_u == {CPS} and not features_v:
            return rule_11g
        else:
            raise Exception("1 - Regra desconhecida: ftu: {}, ftv: {}".format(
                features_u, features_v))


def get_node_features(graph, node):
    features = set()

    ancestor_target = graph.get_node_attribute(node, graph.ANCESTOR_TARGET)
    collapsed = graph.get_node_attribute(node, graph.COLLAPSED)
    in_deductive_degree = graph.get_deductive_in_degree(node)

    if ancestor_target:
        features.add(ATGT)

    if collapsed:
        features.add(CPS)

    if in_deductive_degree == 0:
        features.add(HYP)

    return features


def exec_rule(rule_function, graph, node_u, node_v):
    """
    Performs the collapse of nodes and returns the collapsed node.

    Parameters
    ----------
    rule_function: function
        Function that performs the collapse

    graph: ProofGraph object.

    node_u, node_v: nodes
        Nodes in graph

    Returns
    -------
    collapsed_node: node
        Collapsed node.
    """
    global seq_collapse
    collapsed_node = rule_function(graph, node_u, node_v)
    graph.set_node_attribute(collapsed_node, graph.COLLAPSED, True)
    seq_collapse += 1
    return collapsed_node


def rule_1(graph, node_u, node_v):
    prepare_collapse(graph, node_u, color=1)
    prepare_collapse(graph, node_v, color=2)
    collapse_nodes(graph, node_u, node_v)
    return node_u


def rule_2(graph, node_u, node_v):
    prepare_collapse(graph, node_v, color=1)
    collapse_nodes(graph, node_u, node_v)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_3(graph, node_u, node_v):
    prepare_collapse(graph, node_u, color=1)
    collapse_nodes(graph, node_u, node_v)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_4(graph, node_u, node_v):
    collapse_nodes(graph, node_u, node_v)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_5(graph, node_u, node_v):
    if graph.get_deductive_out_degree(node_u) > 1:
        max_color_u = maximal_color(graph, node_u)
        prepare_collapse(graph, node_v, color=max_color_u + 1)
        collapse_nodes(graph, node_u, node_v)
        return node_u
    else:
        max_color_v = maximal_color(graph, node_v)
        prepare_collapse(graph, node_u, color=max_color_v + 1)
        collapse_nodes(graph, node_v, node_u)
        return node_v


def rule_6(graph, node_u, node_v):
    if graph.get_deductive_out_degree(node_u) > 1:
        collapse_nodes(graph, node_u, node_v)
        graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
        return node_u
    else:
        collapse_nodes(graph, node_v, node_u)
        graph.set_node_attribute(node_v, graph.HYPOTHESIS, True)
        return node_v


def rule_7(graph, node_u, node_v):
    prepare_collapse(graph, node_u)
    prepare_collapse(graph, node_v)
    collapse_nodes(graph, node_u, node_v, collapse_edge=True)
    return node_u


def rule_8(graph, node_u, node_v):
    prepare_collapse(graph, node_u)
    common_node = get_same_connected_node(graph, node_u, node_v)
    redirect_ancestor_edges_to(graph, node_v, common_node)
    collapse_nodes(graph, node_u, node_v, collapse_edge=True)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_9(graph, node_u, node_v):
    prepare_collapse(graph, node_v)
    common_node = get_same_connected_node(graph, node_u, node_v)
    redirect_ancestor_edges_to(graph, node_u, common_node)
    collapse_nodes(graph, node_u, node_v, collapse_edge=True)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_10(graph, node_u, node_v):
    common_node = get_same_connected_node(graph, node_u, node_v)
    redirect_ancestor_edges_to(graph, node_u, common_node)
    redirect_ancestor_edges_to(graph, node_v, common_node)
    collapse_nodes(graph, node_u, node_v, collapse_edge=True)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_11(graph, node_u, node_v):
    prepare_collapse(graph, node_u, color=1)
    prepare_collapse(graph, node_v, color=2)
    collapse_nodes(graph, node_u, node_v)
    return node_u


def rule_11a(graph, node_u, node_v):
    prepare_collapse(graph, node_u, color=1)
    prepare_collapse(graph, node_v, color=2)
    collapse_nodes(graph, node_u, node_v)
    return node_u


def rule_11b(graph, node_u, node_v):
    ancestor_target_u = graph.get_node_attribute(node_u, graph.ANCESTOR_TARGET)
    if ancestor_target_u:
        prepare_collapse(graph, node_u, color=1)
    else:
        prepare_collapse(graph, node_v, color=1)
    collapse_nodes(graph, node_u, node_v)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_11c(graph, node_u, node_v):
    ancestor_target_u = graph.get_node_attribute(node_u, graph.ANCESTOR_TARGET)
    if ancestor_target_u:
        out_neighbor_u, = graph.get_out_neighbors(node_u)
        redirect_ancestor_edges_to(graph, node_u, out_neighbor_u)
        prepare_collapse(graph, node_v, color=1)
        collapse_nodes(graph, node_u, node_v)
        graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
        return node_u
    else:
        out_neighbor_v, = graph.get_out_neighbors(node_v)
        redirect_ancestor_edges_to(graph, node_v, out_neighbor_v)
        prepare_collapse(graph, node_u, color=1)
        collapse_nodes(graph, node_v, node_u)
        graph.set_node_attribute(node_v, graph.HYPOTHESIS, True)
        return node_v


def rule_11d(graph, node_u, node_v):
    ancestor_target_u = graph.get_node_attribute(node_u, graph.ANCESTOR_TARGET)
    if ancestor_target_u:
        out_neighbor_u, = graph.get_out_neighbors(node_u)
        redirect_ancestor_edges_to(graph, node_u, out_neighbor_u)
        collapse_nodes(graph, node_u, node_v)
        graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
        return node_u
    else:
        out_neighbor_v, = graph.get_out_neighbors(node_v)
        redirect_ancestor_edges_to(graph, node_v, out_neighbor_v)
        collapse_nodes(graph, node_v, node_u)
        graph.set_node_attribute(node_v, graph.HYPOTHESIS, True)
        return node_v


def rule_11e(graph, node_u, node_v):
    common_node = get_same_connected_node(graph, node_u, node_v)
    redirect_ancestor_edges_to(graph, node_v, common_node)
    collapse_nodes(graph, node_u, node_v, collapse_edge=True)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_11f(graph, node_u, node_v):
    collapsed_u = graph.get_node_attribute(node_u, graph.COLLAPSED)
    if collapsed_u:
        collapse_nodes(graph, node_u, node_v)
        graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
        return node_u
    else:
        collapse_nodes(graph, node_v, node_u)
        graph.set_node_attribute(node_v, graph.HYPOTHESIS, True)
        return node_v


def rule_11g(graph, node_u, node_v):
    prepare_collapse(graph, node_v, color=-1)
    collapse_nodes(graph, node_u, node_v, collapse_edge=True)
    return node_u


def rule_12(graph, node_u, node_v):
    prepare_collapse(graph, node_u, color=1)
    out_neighbor_v, = graph.get_out_neighbors(node_v)
    redirect_ancestor_edges_to(graph, node_v, out_neighbor_v)
    collapse_nodes(graph, node_u, node_v)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_13(graph, node_u, node_v):
    prepare_collapse(graph, node_v, color=1)
    out_neighbor_u, = graph.get_out_neighbors(node_u)
    redirect_ancestor_edges_to(graph, node_u, out_neighbor_u)
    collapse_nodes(graph, node_u, node_v)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_14(graph, node_u, node_v):
    out_neighbor_u, = graph.get_out_neighbors(node_u)
    out_neighbor_v, = graph.get_out_neighbors(node_v)
    redirect_ancestor_edges_to(graph, node_u, out_neighbor_u)
    redirect_ancestor_edges_to(graph, node_v, out_neighbor_v)
    collapse_nodes(graph, node_u, node_v)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_15(graph, node_u, node_v):
    if graph.get_node_attribute(node_u, graph.ANCESTOR_TARGET):
        prepare_collapse(graph, node_u)
        collapse_nodes(graph, node_v, node_u, collapse_edge=True)
        return node_v
    else:
        prepare_collapse(graph, node_v)
        collapse_nodes(graph, node_u, node_v, collapse_edge=True)
        return node_u


def rule_16(graph, node_u, node_v):
    if graph.get_node_attribute(node_u, graph.ANCESTOR_TARGET):
        out_neighbor_u, = graph.get_out_neighbors(node_u)
        redirect_ancestor_edges_to(graph, node_u, out_neighbor_u)
        collapse_nodes(graph, node_v, node_u, collapse_edge=True)
        graph.set_node_attribute(node_v, graph.HYPOTHESIS, True)
        return node_v
    else:
        out_neighbor_v, = graph.get_out_neighbors(node_v)
        redirect_ancestor_edges_to(graph, node_v, out_neighbor_v)
        collapse_nodes(graph, node_u, node_v, collapse_edge=True)
        graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
        return node_u


def rule_17(graph, node_u, node_v):
    if graph.get_node_attribute(node_u, graph.ANCESTOR_TARGET):
        next_color_v = maximal_color(graph, node_v) + 1
        prepare_collapse(graph, node_u, color=next_color_v)
        update_lambda_color(graph, node_v, next_color_v)
        collapse_nodes(graph, node_v, node_u)

        return node_v
    else:
        next_color_u = maximal_color(graph, node_u) + 1
        prepare_collapse(graph, node_v, color=next_color_u)
        update_lambda_color(graph, node_u, next_color_u)
        collapse_nodes(graph, node_u, node_v)
        return node_u


def rule_18(graph, node_u, node_v):
    if graph.get_node_attribute(node_u, graph.ANCESTOR_TARGET):
        out_neighbor_u, = graph.get_out_neighbors(node_u)
        redirect_ancestor_edges_to(graph, node_u, out_neighbor_u)
        collapse_nodes(graph, node_v, node_u)
        graph.set_node_attribute(node_v, graph.HYPOTHESIS, True)
        return node_v
    else:
        out_neighbor_v, = graph.get_out_neighbors(node_v)
        redirect_ancestor_edges_to(graph, node_v, out_neighbor_v)
        collapse_nodes(graph, node_u, node_v)
        graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
        return node_u


def prepare_collapse(graph, node, color=None):
    """
    Prepare the node for collapse.

    Adds ancestor edges or redirects them.

    Update the path of ancestor edge.

    Coloring the edge if node is not None.

    Parameters
    ----------
    graph: GraphAdapter object

    node: node
        Node in graph

    color: int
        If color is given, set color of out edge with it.
    """
    is_ancestor_target = graph.get_node_attribute(node, graph.ANCESTOR_TARGET)
    if is_ancestor_target:
        redirect_ancestor_edges(graph, node, color)
    else:
        add_ancestor_edges(graph, node, color)

    if color:
        out_neighbor, = graph.get_deductive_out_neighbors(node)
        graph.set_edge_attribute(node, out_neighbor, graph.COLOR, color)


def get_same_connected_node(graph, node_u, node_v):
    for out_neighbor_u in graph.get_deductive_out_neighbors(node_u):
        for out_neighbor_v in graph.get_deductive_out_neighbors(node_v):
            if out_neighbor_u == out_neighbor_v:
                return out_neighbor_u
    return None


def common_out_neighbor(graph, node_u, node_v):
    for out_neighbor_u in graph.get_deductive_out_neighbors(node_u):
        for out_neighbor_v in graph.get_deductive_out_neighbors(node_v):
            if out_neighbor_u == out_neighbor_v:
                return True
    return False


def collapse_nodes(graph, node_u, node_v, collapse_edge=None):
    """
    Collapses node_u and node_v.

    Redirects in and out edges of node_v to node_v.

    Remove node_v.

    Parameters
    ----------
    graph: GraphAdapter object

    node_u, node_v: nodes
        Nodes in the graph

    collapse_edge: boolean
        If True, collapse edges
    """
    if collapse_edge:
        for (s_u, t_u) in graph.get_out_edges(node_u):
            for (s_v, t_v) in graph.get_out_edges(node_v):
                if t_u == t_v:
                    colors = colors_consistency(graph, node_u, node_v, t_u)
                    graph.collapse_edges(node_u, node_v, t_u, colors)

    graph.redirect_in_edges(node_v, node_u)
    graph.redirect_out_edges(node_v, node_u)
    graph.remove_node(node_v)


def redirect_ancestor_edges_to(graph, node, target):
    in_edges = graph.get_ancestor_in_edges(node)
    old_ancestor_edges = []
    for (s, t) in in_edges:
        old_ancestor_edges.append((s, t))
        path = graph.get_edge_attribute(s, t, "path")
        graph.add_ancestor_edge(s, target, path=path[1:])
    graph.set_node_attribute(node, "ancestor_target", False)
    graph.remove_edges(old_ancestor_edges)


def redirect_ancestor_edges(graph, node, color):
    """
    Redirect in ancestor edges of node node to predecessor nodes.

    Parameters
    ----------
    graph: GraphAdapter object

    node: node
        Node in the graph

    color: int
        If color is given, add it in edge path.
    """
    ancestor_edges = graph.get_ancestor_in_edges(node)
    deductive_edges = graph.get_deductive_in_edges(node)

    for (ancestor_source, ancestor_target) in ancestor_edges:
        path = graph.get_edge_attribute(ancestor_source, ancestor_target,
                                        graph.PATH)
        for (deductive_source, deductive_target) in deductive_edges:
            if color:
                graph.add_ancestor_edge(ancestor_source, deductive_source,
                                        path=list(path), new_color=0,
                                        change_color=(1, color))
            else:
                graph.add_ancestor_edge(ancestor_source, deductive_source,
                                        path=list(path), new_color=0)
            graph.set_node_attribute(deductive_source, graph.ANCESTOR_TARGET,
                                     True)
    graph.remove_edges(ancestor_edges)
    graph.set_node_attribute(node, graph.ANCESTOR_TARGET, False)


def add_ancestor_edges(graph, node, color):
    """
    Add ancestor edges between out_neighbor and in_neighbor(s) of the
    node.

    Parameters
    ----------
    graph: GraphAdapter object

    node: node
        Node in the graph

    color: int
        Color is added to edge path
    """
    out_neighbor, = graph.get_deductive_out_neighbors(node)
    for in_neighbor in graph.get_deductive_in_neighbors(node):
        graph.add_ancestor_edge(out_neighbor, in_neighbor, path=[0, color])
        graph.set_node_attribute(in_neighbor, graph.ANCESTOR_TARGET, True)


def update_lambda_color(graph, node, max_color):
    out_edges = graph.get_deductive_out_edges(node)
    color = max_color + 1
    for (s, t) in out_edges:
        lambda_colors = graph.get_edge_attribute(s, t, graph.LAMBDA_COLORS)
        if lambda_colors == [0]:
            graph.set_edge_attribute(s, t, graph.LAMBDA_COLORS, [color])
            update_path_ancestor_edge(graph, node, color, 1)
            color += 1


def update_path_ancestor_edge(graph, node, color, index):
    for (s_in, t_in) in graph.get_deductive_in_edges(node):
        ancestor_target = graph.get_node_attribute(s_in, graph.ANCESTOR_TARGET)
        if ancestor_target:
            (a_s, a_t), = graph.get_ancestor_in_edges(s_in)
            old_path = graph.get_edge_attribute(a_s, a_t, graph.PATH)
            graph.remove_edge(a_s, a_t)
            graph.add_ancestor_edge(a_s, a_t, path=list(old_path),
                                    change_color=(index, color))


def colors_consistency(graph, node_u, node_v, target):
    collapsed_u = graph.get_node_attribute(node_u, graph.COLLAPSED)
    colors_u = get_node_colors(graph, node_u)
    colors_v = get_node_colors(graph, node_v)
    color_edge_u = get_edge_color(graph, node_u, target)
    color_edge_v = get_edge_color(graph, node_v, target)

    if set(color_edge_u) != set(color_edge_v):
        if collapsed_u:
            color_v, = colors_v
            if color_v in colors_u and color_v not in color_edge_u:
                color = maximal_color(graph, node_u) + 1
                graph.set_edge_attribute(node_v, target, graph.COLOR, color)
                update_path_ancestor_edge(graph, node_v, color, 1)
        else:
            color_u, = colors_u
            if color_u in colors_v and color_u not in color_edge_v:
                color = maximal_color(graph, node_v) + 1
                graph.set_edge_attribute(node_u, target, graph.COLOR, color)
                update_path_ancestor_edge(graph, node_u, color, 1)

    color_u = get_edge_color(graph, node_u, target)
    color_v = get_edge_color(graph, node_v, target)

    return list(set(color_u + color_v))


def is_connected_same_node(graph, node_u, node_v):
    """
    Return True if exists a node that is out_neighbor of node_u and
    node_v. Return False if this node not exists.

    Parameters
    ----------
    graph: GraphAdapter object

    node_u, node_v: nodes
        Nodes in the graph
    """
    for out_neighbor_u in graph.get_deductive_out_neighbors(node_u):
        for out_neighbor_v in graph.get_deductive_out_neighbors(node_v):
            if out_neighbor_u == out_neighbor_v:
                return True
    return False


def maximal_color(graph, node):
    """
    Return the maximal color of out_edges of node.

    Parameters
    ----------
    graph: GraphAdapter object

    node: node
        Node in the graph
    """
    return max(get_node_colors(graph, node))


def get_edge_color(graph, s, t):
    is_collapsed = graph.get_edge_attribute(s, t, graph.COLLAPSED)
    if is_collapsed:
        color = graph.get_edge_attribute(s, t, graph.LAMBDA_COLORS)
    else:
        color = [graph.get_edge_attribute(s, t, graph.COLOR)]

    return color


def get_node_colors(graph, node):
    colors = []
    for (s, t) in graph.get_deductive_out_edges(node):
        is_collapsed = graph.get_edge_attribute(s, t, graph.COLLAPSED)
        if is_collapsed:
            colors += graph.get_edge_attribute(s, t, graph.LAMBDA_COLORS)
        else:
            colors += [graph.get_edge_attribute(s, t, graph.COLOR)]

    return colors


def redirect_multi_ancestor_edges(graph):
    nodes_level = graph.get_nodes_level()
    max_level = max(nodes_level.keys())

    for level in range(max_level, -1, -1):
        for node in nodes_level[level]:
            multi_edges = graph.get_node_attribute(node, graph.MULTI_A_TARGET)
            if multi_edges:
                paths_colors = get_paths_single_colors(multi_edges)
                for source, path, index in paths_colors:
                    demote_ancestor_edge(graph, source, node, path, index + 1)


def get_paths_single_colors(multi_edges):
    paths_single_colors = []
    for source, paths in multi_edges.items():
        paths2 = list(paths)
        for index in range(0, len(paths[0])):
            single_paths, paths2 = get_paths_single_color_node(paths2, index)
            for path in single_paths:
                paths_single_colors.append((source, path, index))

    return paths_single_colors


def get_paths_single_color_node(paths, index):
    dict_color = {}
    for path in paths:
        index_color = path[index]
        if index_color not in dict_color:
            dict_color[index_color] = 1
        else:
            dict_color[index_color] += 1

    single_colors = []

    for color, qty in dict_color.items():
        if qty == 1:
            single_colors.append(color)

    single_paths = []
    copy_paths = list(paths)

    for color in single_colors:
        for path in list(paths):
            if color == path[index]:
                single_paths.append(path)
                copy_paths.remove(path)

    return single_paths, copy_paths


def demote_ancestor_edge(graph, source, node, path, index):
    new_path = path[index:]
    removed_path = path[:index]

    node_aux = node
    for color in removed_path:
        node_aux, = get_out_neighbors_color(graph, node_aux, color)

    graph.add_ancestor_edge(source, node_aux, path=new_path)


def get_out_neighbors_color(graph, node, color):
    out_edges = graph.get_deductive_out_edges(node)

    out_neighbors = []
    for (s, t) in out_edges:
        colors = get_edge_color(graph, s, t)
        if color in colors:
            out_neighbors.append(t)

    return out_neighbors


def remove_unused_colors(graph):
    nodes_level = graph.get_nodes_level()
    max_level = max(nodes_level.keys())

    for level in range(max_level, -1, -1):
        for node in nodes_level[level]:
            check_active_colors(graph, node)
            remove_colors_node(graph, node)


def check_active_colors(graph, node):
    ancestor_edges = graph.get_ancestor_in_edges(node)
    for (s, t) in ancestor_edges:
        path = graph.get_edge_attribute(s, t, graph.PATH)
        mark_active_colors(graph, node, path)


def mark_active_colors(graph, node, path):
    aux_node = node
    for color in path:
        graph.add_active_color(aux_node, color)
        aux_node, = get_out_neighbors_color(graph, aux_node, color)


def remove_colors_node(graph, node):
    out_edges = graph.get_deductive_out_edges(node)
    for (s, t) in out_edges:
        active_colors = graph.get_node_attribute(node, graph.ACTIVE_COLORS)
        collapsed = graph.get_edge_attribute(s, t, graph.COLLAPSED)
        if collapsed:
            lambda_colors = graph.get_edge_attribute(s, t, graph.LAMBDA_COLORS)
            removed_colors = []
            for color in lambda_colors:
                if color not in active_colors:
                    removed_colors.append(color)
            lambda_colors = list(set(lambda_colors) - set(removed_colors))
            if not lambda_colors:
                graph.set_edge_attribute(s, t, graph.LAMBDA_COLORS, [0])
            else:
                graph.set_edge_attribute(s, t, graph.LAMBDA_COLORS,
                                         lambda_colors)
        else:
            color = graph.get_edge_attribute(s, t, graph.COLOR)
            if color not in active_colors:
                graph.set_edge_attribute(s, t, graph.COLOR, 0)


def demote_ancestor_edges(graph):
    nodes_level = graph.get_nodes_level()
    max_level = max(nodes_level.keys())

    for level in range(max_level, -1, -1):
        for node in nodes_level[level]:
            deductive_out_degree = graph.get_deductive_out_degree(node)
            if deductive_out_degree == 1:
                (s, t), = graph.get_deductive_out_edges(node)
                collapsed = graph.get_edge_attribute(s, t, graph.COLLAPSED)
                lambda_colors = graph.get_edge_attribute(s, t,
                                                         graph.LAMBDA_COLORS)
                if collapsed and lambda_colors == [0]:
                    ancestor_edges = graph.get_ancestor_in_edges(node)
                    for (a_s, a_t) in ancestor_edges:
                        path = graph.get_edge_attribute(a_s, a_t, graph.PATH)
                        demote_ancestor_edge(graph, a_s, node, path, 1)
                        graph.remove_edge(a_s, a_t)


seq_collapse = 0
