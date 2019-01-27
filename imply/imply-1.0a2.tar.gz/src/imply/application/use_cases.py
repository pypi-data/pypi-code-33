import itertools
import tempfile

from graphviz import Digraph  # type: ignore
import grimp  # type: ignore


def draw_graph(module_name: str) -> None:
    """
    Create a file showing a graph of the supplied package.
    Args:
        module_name: the package or subpackage name of any importable Python package.
    """
    module = grimp.Module(module_name)
    graph = grimp.build_graph(module.package_name)
    module_children = graph.find_children(module.name)

    dot = Digraph(
        format='png',
        node_attr={'fontname': 'helvetica'}
    )
    dot.attr(
        concentrate='true',  # Merge lines together.
    )
    for module_child in module_children:
        dot.node(module_child)

    # Dependencies between children.
    for upstream, downstream in itertools.permutations(module_children, r=2):
        if graph.chain_exists(imported=upstream, importer=downstream,
                              as_packages=True):
            dot.edge(downstream, upstream)

    source_filename = tempfile.mkstemp()[1]
    dot.view(filename=source_filename, cleanup=True)
