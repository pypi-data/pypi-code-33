"""
A module to find dependencies among all records in all schemas.
"""
__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

from collections import OrderedDict
from typing import cast

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.modules.schema_dependencies_checker import SchemaDependenciesChecker

from pyavro_gen.codewriters.utils import namespace_name


class AvscSchemaDependenciesChecker(SchemaDependenciesChecker):  # type: ignore
    """
    Stores schema dependencies - exception thrown if it detects cycles.

    NOTE: Also all Records defined within schemas are considered.
    """

    def store_dependencies_of_field(self, node: Avro.Node) -> None:
        """
        Store external_dependencies of other records in a node in a private dict
        :param node: The input node
        """

        if isinstance(node, str):
            if self.ancestors and '.' in node:

                # it has to be a 'name' field or part of a list
                anc = self.ancestors[-1].key
                if anc == Avro.Name or isinstance(anc, int):

                    dependent_ancestor = self._find_ancestor()
                    if dependent_ancestor:
                        self.record_dependencies_graph.add_edge(dependent_ancestor, node)

        if isinstance(node, OrderedDict):
            if Avro.Name in node:
                if Avro.Namespace in node:
                    dep = node[Avro.Namespace] + '.' + node[Avro.Name]
                elif '.' in node[Avro.Name]:
                    dep = node[Avro.Name]
                elif Avro.Fields in node or Avro.Symbols in node:
                    dep = namespace_name(self.current_schema_name) + '.' + node[Avro.Name]
                else:
                    return

                dependent_ancestor = self._find_ancestor()
                self.record_dependencies_graph.add_edge(dependent_ancestor, dep)

    def _find_ancestor(self) -> str:
        dependent_ancestor = None
        for ancestor in reversed(self.ancestors):

            if Avro.Name in ancestor.node \
                    and ancestor.node[Avro.Type] == Avro.Record \
                    and isinstance(ancestor.node, OrderedDict):

                if Avro.Namespace in ancestor.node:
                    dependent_ancestor = \
                        ancestor.node[Avro.Namespace] + '.' + ancestor.node[Avro.Name]
                elif '.' in ancestor.node[Avro.Name]:
                    dependent_ancestor = ancestor.node[Avro.Name]
                else:
                    dependent_ancestor = \
                        namespace_name(self.current_schema_name) \
                        + '.' + ancestor.node[Avro.Name]
                break

        if not dependent_ancestor:
            return cast(str, self.current_schema_fully_qualified_name)

        return cast(str, dependent_ancestor)
