"""
Codewriter for Python modules
"""

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

from dataclasses import dataclass
from typing import List, Dict, Set

from isort import SortImports

from pyavro_gen.codewriters.core import ClassWriter, Dependency, WritingMode
from pyavro_gen.codewriters.utils import j, ind, to_snake_case


@dataclass
class ClassItem:
    """
    A dataclass to associate a class with its namespace, testing class, and testing class namespace.
    """
    namespace: str
    name: str
    namespace_test: str
    factory_name: str


class NamespaceWriter:
    """
    Codewriter for Python modules.
    It deals with stringifying all the classes.
    """

    def __init__(self, namespace: str):
        self.namespace = namespace
        self.class_writers: List[ClassWriter] = []

    def get_all_testing_classes(self) -> List[ClassItem]:
        """
        Returns a list of ClassItems to be written in the root module of the testing package
        to be generated.
        :return: A list of ClassItems
        """
        deps: List[Dependency] = [
            dep for writer in self.class_writers
            for dep in writer.as_dependency(WritingMode.GENERATION_INDEPENDENT)
        ]
        test_deps: List[Dependency] = [
            dep for writer in self.class_writers
            for dep in writer.as_dependency(WritingMode.TEST)
        ]

        return [
            ClassItem(
                j(dep.prefix, '.', dep.where),
                dep.what,
                j(test_deps[idx].prefix, '.', dep.where),
                test_deps[idx].what
            )
            for idx, dep in enumerate(deps)
        ]

    def write(self, mode: WritingMode = WritingMode.GENERATION) -> Dict[str, str]:
        """
        Returns this namespace as a Dict of str, using the specified writing mode.
        Keys are filenames; Values are file contents.

        :param mode: The writing mode
        :return: A dict of filenames-file contents
        """

        self.class_writers: List[ClassWriter] = \
            sorted(self.class_writers, key=lambda w: len(
                w.external_dependencies
            ))

        if mode == WritingMode.GENERATION:
            classes = (writer.write() for writer in self.class_writers)
            all_deps: Set[str] = set(
                dep.write()
                for writer in self.class_writers for dep in writer.all_dependencies(mode)
                if dep.where != self.namespace
            )

            content = j(
                j(*all_deps),
                j(*classes)
            )

            return {'__init__.py': SortImports(file_contents=content).output}

        # common content
        deps: List[str] = [
            dep.write(WritingMode.INIT)
            for writer in self.class_writers for dep in writer.as_dependency(mode)
        ]

        content = j(*deps)

        # NOTE: DO NOT SORT!
        #
        # It is important to let the interpreter read the files in the correct order.
        # E.g. the following won't work:
        # contents = {'__init__.py': SortImports(file_contents=content).output}
        contents = {'__init__.py': content}

        for writer in self.class_writers:
            if mode == WritingMode.GENERATION_INDEPENDENT:
                contents[f'{to_snake_case(writer.name)}.py'] = writer.write(mode)
            elif mode == WritingMode.TEST:
                contents[f'{to_snake_case(writer.name)}_factory.py'] = writer.write(mode)

        return contents


def get_testing_base() -> str:
    """
    Header for testing package __init__.py
    """
    return j(
        'import faker\n\n',
        'from pyavro_gen.enum_with_schema_provider import EnumWithSchemaProvider\n',
        'from .testing_classes import test_classes\n\n'
        'fake = faker.Faker()\n',
        'fake.add_provider(EnumWithSchemaProvider)\n',
    )


def get_testing_class_list(classes: List[ClassItem]) -> str:
    """
    Converts the list of testing classitems to a string.
    :param classes: The testing class items
    """
    return j(
        'from pyavro_gen.codewriters.namespace import ClassItem\n\n'
        'test_classes = [\n',
        *(
            f"{ ind(1)}ClassItem("
            f"'{c.namespace}', '{c.name}', '{c.namespace_test}', '{c.factory_name}'"
            f"),\n"
            for c in classes
        ),
        ']\n'
    )
