#!/usr/bin/python3

"""
Output methods that use dot syntax to represent dependency information.
"""

import re
import sys

import devpipeline_core.resolve


def _dotify(string):
    """This function swaps '-' for '_'."""
    return re.sub("-", lambda m: "_", string)


def _do_dot(targets, components, layer_fn):
    def _handle_layer_dependencies(resolved_dependencies, indent, attributes):
        for attribute in attributes:
            print(indent + attribute)
        for component in resolved_dependencies:
            stripped_name = _dotify(component)
            print(indent + stripped_name)
            component_dependencies = components.get(component).get_list("depends")
            for dep in component_dependencies:
                print("{}{} -> {}".format(indent, stripped_name, _dotify(dep)))

    print("digraph dependencies {")
    try:
        devpipeline_core.resolve.process_dependencies(
            targets,
            components,
            lambda rd: layer_fn(
                rd, lambda rd, indent: _handle_layer_dependencies(rd, indent, [])
            ),
        )
    except devpipeline_core.resolve.CircularDependencyException as cde:
        layer_fn(
            cde.components,
            lambda rd, indent: _handle_layer_dependencies(
                rd, indent, ['edge [color="red"]', 'node [color="red"]']
            ),
        )
    print("}")


def _print_layers(targets, components):
    """
    Print dependency information, grouping components based on their position
    in the dependency graph.  Components with no dependnecies will be in layer
    0, components that only depend on layer 0 will be in layer 1, and so on.

    If there's a circular dependency, those nodes and their dependencies will
    be colored red.

    Arguments
    targets - the targets explicitly requested
    components - full configuration for all components in a project
    """
    layer = 0

    def _add_layer(resolved_dependencies, dep_fn):
        nonlocal layer

        indentation = " " * 4
        print("{}subgraph cluster_{} {{".format(indentation, layer))
        print('{}label="Layer {}"'.format(indentation * 2, layer))
        dep_fn(resolved_dependencies, indentation * 2)
        print("{}}}".format(indentation))
        layer += 1

    _do_dot(targets, components, _add_layer)


_LAYERS_TOOL = (
    _print_layers,
    "Print a dot graph that groups components by their position in a layered "
    "architecture.  Components are only permitted to depend on layers with a "
    "lower number.",
)


def _print_graph(targets, components):
    """
    Print dependency information using a dot directed graph.  The graph will
    contain explicitly requested targets plus any dependencies.

    If there's a circular dependency, those nodes and their dependencies will
    be colored red.

    Arguments
    targets - the targets explicitly requested
    components - full configuration for all components in a project
    """
    indentation = " " * 4
    _do_dot(targets, components, lambda rd, dep_fn: dep_fn(rd, indentation))


_GRAPH_TOOL = (
    _print_graph,
    "Print a dot graph where each " "component points at its dependnet components.",
)


def _print_dot(targets, components):
    """
    Deprecated function; use print_graph.

    Arguments
    targets - the targets explicitly requested
    components - full configuration for all components in a project
    """
    print("Warning: dot option is deprecated.  Use graph instead.", file=sys.stderr)
    _print_graph(targets, components)


_DOT_TOOL = (_print_dot, 'Deprecated -- use the "graph" option instead.')
