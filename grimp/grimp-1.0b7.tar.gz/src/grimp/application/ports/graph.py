import abc
from typing import Set, Tuple, Optional, Dict, Union, List


class AbstractImportGraph(abc.ABC):
    """
    A Directed Graph of imports between Python modules.
    """
    # Mechanics
    # ---------

    @property
    @abc.abstractmethod
    def modules(self) -> Set[str]:
        """
        The names of all the modules in the graph.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_module(self, module: str, is_squashed: bool = False) -> None:
        """
        Add a module to the graph.

        If is_squashed is True, the module should be treated as a 'squashed module'. This means
        the module has a node in the graph that represents both itself and all its descendants.
        Using squashed modules allows you to simplify some parts of the graph, for example if you
        want to include an external package in the graph but don't care about all the dependencies
        within that package.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_import(
        self, *,
        importer: str,
        imported: str,
        line_number: Optional[int] = None,
        line_contents: Optional[str] = None
    ) -> None:
        """
        Add a direct import between two modules to the graph. If the modules are not already
        present, they will be added to the graph.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def remove_import(self, *, importer: str, imported: str) -> None:
        """
        Remove a direct import between two modules. Does not remove the modules themselves.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def count_imports(self) -> int:
        """
        Return the number of imports in the graph.
        """
        raise NotImplementedError

    # Descendants
    # -----------

    @abc.abstractmethod
    def find_children(self, module: str) -> Set[str]:
        """
        Find all modules one level below the module. For example, the children of
        foo.bar might be foo.bar.one and foo.bar.two, but not foo.bar.two.green.

        Raises:
            ValueError if attempted on a squashed module.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def find_descendants(self, module: str) -> Set[str]:
        """
        Find all modules below the module. For example, the descendants of
        foo.bar might be foo.bar.one and foo.bar.two and foo.bar.two.green.

        Raises:
            ValueError if attempted on a squashed module.
        """
        raise NotImplementedError

    # Direct imports
    # --------------

    @abc.abstractmethod
    def direct_import_exists(self, *, importer: str, imported: str) -> bool:
        """
        Whether or not the importer module directly imports the imported module.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def find_modules_directly_imported_by(self, module: str) -> Set[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def find_modules_that_directly_import(self, module: str) -> Set[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_import_details(
        self,
        *,
        importer: str,
        imported: str
    ) -> List[Dict[str, Union[str, int]]]:
        """
        Returns a list of the details of every direct import between two modules, in the form:
        [
            {
                'importer': 'mypackage.importer',
                'imported': 'mypackage.imported',
                'line_number': 5,
                'line_contents': 'from mypackage import imported',
            },
            (additional imports here)
        ]
        """
        raise NotImplementedError

    # Indirect imports
    # ----------------

    @abc.abstractmethod
    def find_downstream_modules(
        self, module: str, as_package: bool = False
    ) -> Set[str]:
        """
        Return a set of the names of all the modules that import (even indirectly) the
        supplied module name.
        Args:
            module:        The absolute name of the upstream Module.
            as_package: Whether or not to treat the supplied module as an individual module,
                           or as an entire subpackage (including any descendants). If
                           treating it as a subpackage, the result will include downstream
                           modules *external* to the subpackage, and won't include modules within
                           the subpackage.
        Usage:

            # Returns the modules downstream of mypackage.foo.
            import_graph.find_downstream_modules('mypackage.foo')

            # Returns the modules downstream of mypackage.foo, mypackage.foo.one and
            # mypackage.foo.two.
            import_graph.find_downstream_modules('mypackage.foo', as_package=True)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def find_upstream_modules(self, module: str, as_package: bool = False) -> Set[str]:
        """
        Return a set of the names of all the modules that are imported (even indirectly) by the
        supplied module.

        Args:
            module:        The name of the downstream module.
            as_package:    Whether or not to treat the supplied module as an individual module,
                           or as a package (i.e. including any descendants, if there ary any). If
                           treating it as a subpackage, the result will include upstream
                           modules *external* to the subpackage, and won't include modules within
                           the subpackage.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def find_shortest_chain(
        self, importer: str, imported: str,
    ) -> Optional[Tuple[str, ...]]:
        """
        Attempt to find the shortest chain of imports between two modules, in the direction
        of importer to imported.

        Returns:
            Tuple of module names, from importer to imported, or None if no chain exists.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def chain_exists(
        self, importer: str, imported: str, as_packages=False,
    ) -> bool:
        """
        Return whether any chain of imports exists between the two modules, in the direction
        of importer to imported. In other words, does the importer depend on the imported?

        Optional args:
            as_packages: Whether to treat the supplied modules as individual modules,
                         or as packages (including any descendants, if there are any). If
                         treating them as subpackages, all descendants of the supplied modules
                         will be checked too.
        """
        raise NotImplementedError

    def __repr__(self):
        """
        Display the instance in one of the following ways:

            <ImportGraph: empty>
            <ImportGraph: 'one', 'two', 'three', 'four', 'five'>
            <ImportGraph: 'one', 'two', 'three', 'four', 'five', ...>
        """
        modules = self.modules
        if modules:
            repr_output_size = 5
            module_list = list(modules)[:repr_output_size]
            stringified_modules = ', '.join(repr(m) for m in module_list)
            if len(modules) > repr_output_size:
                stringified_modules += ", ..."
        else:
            stringified_modules = 'empty'
        return f'<{self.__class__.__name__}: {stringified_modules}>'
