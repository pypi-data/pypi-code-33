"""Automatically document class hierarchy"""
import re

import networkx as nx
import properties

GRAPH_OPTS = {
    'rankdir': 'RL',
    'splines': 'spline',
    'labeljust': 'l',
}
NODE_OPTS = {
    'shape': 'Mrecord',
    'fontname': 'Liberation Mono',
}
ABSTRACT_NODE_OPTS = NODE_OPTS.copy()
ABSTRACT_NODE_OPTS.update({
    'style': 'filled',
    'fillcolor': 'lightgray',
})
NODE_OPTS_EXT = NODE_OPTS.copy()
NODE_OPTS_EXT.update({
    'style': 'dashed',
})
ABSTRACT_NODE_OPTS_EXT = ABSTRACT_NODE_OPTS.copy()
ABSTRACT_NODE_OPTS_EXT.update({
    'style': 'dashed, filled',
})
EDGE_OPTS = {
    'color': 'gray',
}
EDGE_OPTS_EXT = EDGE_OPTS.copy()
EDGE_OPTS_EXT.update({
    'style': 'dashed',
})


def make_graph(
        registry=None,
        expand_props=None,
        only_new_props=False,
        abstract_regex='^_.*',
        ext_base=None,
        graph_opts=None,
        node_opts=None,
        abstract_node_opts=None,
        node_opts_ext=None,
        abstract_node_opts_ext=None,
        edge_opts=None,
        edge_opts_ext=None
):
    """Generate a graph showing HasProperties inheritance

    The generated graph includes all HasProperties classes defined in a
    registry (assuming they have one common ancestor). Optionally, it may
    include "external" classes not in the registry to show additional
    inheritance. There are different display options for classes in the
    registry and external classes, as well as abstract and non-abstract
    classes.

    Parameters
    ----------
    registry : dict
        Registry of HasProperties classes; keys are HasProperties class
        names and values are corresponding classes. If registry is not
        provided, :code:`properties.HasProperties._REGISTRY` is used by
        default
    expand_props : bool
        If True, Property names are listed for each HasProperties class
    only_new_props : bool
        If True, Properties are only listed if they are newly defined on
        the class. If False (the default), all Properties are listed on
        each class.
    abstract_regex : str
        If class name matches this regex, it is considered an abstract class
        and uses abstract class display options. Default: '^_.*'
    ext_base : class
        If specified, this HasProperties class becomes the base node of
        the graph, even if it is not in the registry. If not specified,
        the first common ancestor in the registry is used.
    graph_opts : dict
        Additional graph options. Default options are
        :code:`{'rankdir': 'RL', 'splines': 'spline', 'labeljust': 'l'}`
    node_opts : dict
        Additional options for nodes corresponding to non-abstract
        classes in the registry. Default options are
        :code:`{'shape': 'Mrecord', 'fontname': 'Liberation Mono'}`
    abstract_node_opts : dict
        Additional options for nodes corresponding to abstract classes
        in the registry. Default options include the same defaults as
        node_opts plus :code:`{'style': 'filled', 'fillcolor': 'lightgray'}`
    node_opts_ext : dict
        Additional options for nodes corresponding to non-abstract
        classes not in the registry. Default options include the same
        defaults as node_opts plus :code:`{'style': 'dashed'}`
    abstract_node_opts_ext : dict
        Additional options for nodes corresponding to abstract classes
        not in the registry. Default options in clude the same defaults as
        node_opts plus
        :code:`{'style': 'dashed, filled', 'fillcolor': 'lightgray'}`
    edge_opts : dict
        Additional options for edges connecting classes in the registry.
        Default options are :code:`{'color': 'gray'}`
    edge_opts_ext : dict
        Additional options for edges that connect to classes not in the
        registry. Default options are
        :code:`{'color': 'gray', 'style': 'dashed'}`

    Returns
    -------
    tuple
        The first item in the tuple is the output :code:`networkx.DiGraph`
        object; the second item is the output registry, a copy of the
        input registry with all classes in the graph present. This
        includes any external classes as well as the original classes
        in the registry.
    """

    abstract_matcher = re.compile(abstract_regex)

    # Update graph options based on defaults and input keyword arguments
    gopts = GRAPH_OPTS.copy()
    if graph_opts:
        gopts.update(graph_opts)
    nopts = NODE_OPTS.copy()
    if node_opts:
        nopts.update(node_opts)
    anopts = ABSTRACT_NODE_OPTS.copy()
    if abstract_node_opts:
        anopts.update(abstract_node_opts)
    eopts = EDGE_OPTS.copy()
    if edge_opts:
        eopts.update(edge_opts)
    if ext_base:
        nopts_ext = NODE_OPTS_EXT.copy()
        if node_opts_ext:
            nopts_ext.update(node_opts_ext)
        anopts_ext = ABSTRACT_NODE_OPTS_EXT.copy()
        if abstract_node_opts_ext:
            anopts_ext.update(abstract_node_opts_ext)
        eopts_ext = EDGE_OPTS_EXT.copy()
        if edge_opts_ext:
            eopts_ext.update(edge_opts_ext)

    # Copy the registry so it is not mutated
    if registry is None:
        registry = properties.HasProperties._REGISTRY
    output_registry = registry.copy()

    # If an external base is provided, use that.
    base = ext_base

    # If an external base is not provided, use the most distant ancestor
    # still present in the registry
    #
    # Note: This assumes all classes in the registry contain one common
    #       ancestor, which is also present in the registry.
    if not base:
        for parent in next(iter(output_registry.values())).__mro__:
            if parent.__name__ in output_registry:
                base = parent
                continue
            break

    # Extras dictionary is used to hold classes that are not in the
    # registry but required by inheritance to the external base.
    # Unused if ext_base is None.
    extras = {}
    if ext_base:
        for key in output_registry:
            for cls in output_registry[key].__mro__:
                if not issubclass(cls, base) or cls.__name__ == key:
                    continue
                if cls.__name__ not in output_registry:
                    extras.update({cls.__name__: cls})
        output_registry.update(extras)

    # Construct the class dictionary with ancestor names for values
    cls_dict = {
        key: tuple(
            cls.__name__
            for cls in output_registry[key].__mro__
            if issubclass(cls, base) and cls is not output_registry[key]
        )
        for key in output_registry
    }
    # Construct the class graph from the class_dictionary
    cls_graph = {
        key: set(
            cls for cls in cls_dict[key] if cls not in sum(
                [cls_dict[subkey] for subkey in cls_dict[key]],
                tuple(),
            ),
        )
        for key in cls_dict
    }

    def process_node(output_graph, name, cls):
        """Add a node and edges to the graph with appropriate options"""
        if expand_props:
            try:
                props = getattr(cls, expand_props)
            except TypeError:
                props = cls._props
            propnames = list(props.keys())
            # If only_new_props is specified, only show properties that
            # are defined on a class, rather than all properties.
            if only_new_props and cls is not base:
                for parent in cls.__mro__:
                    if parent is cls:
                        continue
                    try:
                        parent_props = getattr(parent, expand_props, {})
                    except TypeError:
                        parent_props = getattr(parent, '_props', {})
                    for key, val in parent_props.items():
                        if key in propnames and props[key] is val:
                            propnames.remove(key)
            propnames.sort()
            propnames += ['']
            seps = output_graph.graph.get('rankdir', '').upper() != 'RL'
            label = '{lsep}{name}|{props}{rsep}'.format(
                name=name,
                props='\\l'.join(propnames),
                lsep='{' if seps else '',
                rsep='}' if seps else '',
            )
        else:
            label = name
        abstract = abstract_matcher.match(name)
        extra = name in extras
        if abstract and extra:
            opts = anopts_ext
        elif abstract and not extra:
            opts = anopts
        elif not abstract and extra:
            opts = nopts_ext
        else:
            opts = nopts
        output_graph.add_node(name, label=label, **opts)
        for parent in cls_graph[name]:
            if parent in extras:
                opts = eopts_ext
            else:
                opts = eopts
            output_graph.add_edge(name, parent, **opts)

    # Draw the graph and each node
    output_graph = nx.DiGraph()
    output_graph.graph.update(gopts)
    for name, cls in iter(output_registry.items()):
        process_node(output_graph, name, cls)
    return output_graph, output_registry
