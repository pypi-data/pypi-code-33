import networkx as nx

#TODO DevMaster: need a clear name for the parameters the purpose is to be understood by everyone missing documentation
def create_edges_from_xy_df(df, from_x_key, from_y_key, to_x_key, to_y_key, dict_attr_key=None, g=None):
    if not g:
        g = nx.Graph()

    if not dict_attr_key:
        dict_attr_key = {}

    for _, row in df.iterrows():
        dict_attr_val = {a: row[k] for a, k in dict_attr_key}
        g.add_edge((row[from_x_key], row[from_y_key]), (row[to_x_key], row[to_y_key]), **dict_attr_val)

    return g


def transfer_nodes_attribute(from_g, to_g, attr):
    dict_of_attr = nx.get_node_attributes(from_g, attr)
    nx.set_node_attributes(to_g, dict_of_attr, attr)
    return to_g


def transfer_edges_attributes(from_g, to_g, attr, both_dir=False):
    dict_of_attr = nx.get_edge_attributes(from_g, attr)

    # Same direction
    for e, v in dict_of_attr.items():
        nx.set_edge_attributes(to_g, {(e[0], e[1]): v}, attr)

    # Opposite direction
    if both_dir:
        for e, v in dict_of_attr.items():
            nx.set_edge_attributes(to_g, {(e[1], e[0]): v}, attr)
    return to_g


def create_directed_tree_from_source(g, source, edges_attributes_to_keep=None, nodes_attributes_to_keep=None):
    paths = nx.single_source_shortest_path(g, source)
    g_dir = nx.DiGraph()

    for n, p in paths.items():
        for i in range(1, len(p)):
            g_dir.add_edge(p[i - 1], p[i])

    if edges_attributes_to_keep:
        for attr in edges_attributes_to_keep:
            transfer_edges_attributes(g, g_dir, attr, both_dir=True)

    if nodes_attributes_to_keep:
        for attr in nodes_attributes_to_keep:
            transfer_nodes_attribute(g, g_dir, attr)

    return g_dir


def get_leaves(g, data=False):
    if data:
        return [(n, d) for n, d in g.nodes(data=True) if len(nx.descendants(g, n)) == 0]
    else:
        return [n for n in g.nodes if len(nx.descendants(g, n)) == 0]
