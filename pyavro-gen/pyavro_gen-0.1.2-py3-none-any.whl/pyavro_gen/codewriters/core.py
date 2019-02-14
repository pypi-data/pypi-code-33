"""
Module that define the core classes for codewriters performing python classes generation
from Avro schemas.
"""

import textwrap
from abc import ABC
from dataclasses import dataclass, field as dataclasses_field
from enum import Enum
from typing import List, Optional, Set, Callable, cast

from isort import SortImports

from pyavro_gen.codewriters.utils import class_name, namespace_name, j, ind, to_snake_case


class WritingMode(Enum):
    """
    Writing mode for all codewriters
    """
    GENERATION = 'GENERATION'
    GENERATION_INDEPENDENT = 'GENERATION_INDEPENDENT'
    TYPE = 'TYPE'
    TEST = 'TEST'
    TEST_ATTRIBUTE = 'TEST_ATTRIBUTE'
    PARAMETER = 'PARAMETER'
    DOCSTRING_PARAM = 'DOCSTRING_PARAM'
    DOCSTRING_RAISES = 'DOCSTRING_RAISES'
    INIT = 'INIT'


@dataclass(frozen=True)
class Dependency:  # pylint: disable=R0903
    """
    A codewriter to express dependencies
    """
    where: str
    what: str
    prefix: Optional[str]

    def write(self, mode: WritingMode = WritingMode.GENERATION) -> str:
        """
        Returns this dependency as str, using the specified writing mode

        :param mode: The writing mode
        :return: The str form of the dependency
        """
        if mode == WritingMode.INIT:
            return \
                f'from {self.prefix}.{self.where}.{to_snake_case(self.what)} import {self.what}\n'
        if self.prefix:
            return f'from {self.prefix}.{self.where} import {self.what}\n'

        return f'from {self.where} import {self.what}\n'


class Writer(ABC):
    """
    Base class for all codewriters.
    """
    output_prefix: str = ''

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        """
        Returns this entity as str, using the specified writing mode

        :param mode: The writing mode
        :param with_indentation: How much to indent
        :return: The str form of the entity
        """

    # pylint: disable=R0201,W0613
    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        """
        Return this entity as a list of dependencies, using the specified writing mode.

        :param mode: The writing mode
        :return: A list of dependencies
        """
        return []


@dataclass
class Comment(Writer):
    """
    A codewriter for code comments.
    """
    value: Optional[str] = None

    def _optional_write(self, func: Callable[[str], str]) -> str:
        if self.value:
            return func(self.value)

        return ''

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        return self._optional_write(lambda s: '  # ' + self.value)  # type: ignore


@dataclass
class Docstring(Comment):
    """
    A codewriter for docstrings.
    """
    value: Optional[str] = None

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        if mode == WritingMode.TYPE:
            return self._optional_write(lambda s: j('\n', f'#: {self.value}', '\n'))

        return self._optional_write(lambda s:
                                    j('\n',
                                      '"""', '\n',
                                      self.value, '\n',
                                      '"""', '\n'
                                      )
                                    )


# pylint: disable=R0902
class ClassWriter(Writer):
    """
    The main codewriter. It is an abstraction for an entity that writes Python classes.
    """

    def __init__(self,
                 fully_qualified_name: str,
                 doc: Optional[str] = None,
                 prefix: Optional[str] = None):

        self.name: str = class_name(fully_qualified_name)
        self.namespace: str = namespace_name(fully_qualified_name)
        self.doc: Docstring = Docstring(doc)
        self.prefix: Optional[str] = prefix
        self.comment: Comment = Comment()

        self.external_dependencies: List[str] = []
        self.decorators: List[Decorator] = []
        self.extensions: List[Extension] = []
        self.attributes: List[Attribute] = []
        self.methods: List[Method] = []

    def all_dependencies(self, mode: WritingMode) -> Set[Dependency]:
        """
        Return the set of dependencies this class depends on.

        :param mode: The writing mode
        """
        if mode == WritingMode.TEST:
            return {dep for a in self.attributes for dep in a.as_dependency(mode)}
        return set(
            # [d for dep in self.external_dependencies
            #  for d in ClassWriter(dep, prefix=self.prefix).as_dependency(mode)]
            [dep for d in self.decorators for dep in d.as_dependency(mode)]
            + [dep for e in self.extensions for dep in e.as_dependency(mode)]
            + [dep for a in self.attributes for dep in a.as_dependency(mode)]
            + [dep for m in self.methods for dep in m.as_dependency(mode)]
        )

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        if mode == WritingMode.TEST and self.prefix:
            return [Dependency(self.namespace, self.name + 'Factory', self.prefix + '_test')]

        return [Dependency(self.namespace, self.name, self.prefix)]

    # pylint: disable=R0911
    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:

        if mode == WritingMode.TYPE:
            return self.name

        if mode == WritingMode.DOCSTRING_RAISES:
            return f':raises {".".join((self.namespace, self.name))}'

        if mode == WritingMode.GENERATION:
            if not self.attributes:
                if not self.methods:
                    attributes = j("\n", ind(1), "pass")
                else:
                    attributes = ''
            else:
                attributes = '\n'.join(a.write(mode) for a in self.attributes)

            methods = '\n'.join(m.write(mode) for m in self.methods) if self.methods else ''

            extensions = f"({', '.join(e.write(mode) for e in self.extensions)})" \
                if self.extensions else ''

            decorators = '\n'.join(dec.write(mode) for dec in self.decorators) + '\n' \
                if self.decorators else ''

            return textwrap.indent(
                j(
                    '\n\n',
                    decorators,
                    f'class {self.name}{extensions}:',
                    textwrap.indent(
                        j(
                            self.doc.write(mode),
                            attributes,
                            methods,
                            '\n'
                        ),
                        ind(1)
                    )
                ),
                ind(with_indentation)
            )

        if mode == WritingMode.GENERATION_INDEPENDENT:
            all_deps = {dep.write() for dep in self.all_dependencies(mode)}

            content = j(
                j(*all_deps),
                self.write(WritingMode.GENERATION, with_indentation)
            )

            return cast(str, SortImports(file_contents=content).output)

        if mode == WritingMode.TEST_ATTRIBUTE:
            return f'{self.name}Factory()'

        if mode == WritingMode.TEST:
            all_deps = {
                dep.write() for dep in self.all_dependencies(mode)
            }.union({
                # Factory boy dependencies
                Dependency('factory', 'Factory', None).write(),
                Dependency('factory', 'lazy_attribute', None).write(),
            }).union({
                # Itself in its standard (non-factory) form
                dep.write(WritingMode.TEST)
                for dep in self.as_dependency(WritingMode.GENERATION)
            })

            class_content = textwrap.indent(
                j(
                    '\n\n',
                    f'class {self.name}Factory(Factory):',
                    textwrap.indent(
                        j(
                            f'\nclass Meta:\n{ ind(1)}model = {self.name}\n',
                            self.get_testing_attributes(),
                            '\n'
                        ),
                        ind(1)
                    )
                ),
                ind(with_indentation)
            )

            content = j(
                j(*all_deps),
                class_content
            )

            return cast(str, SortImports(file_contents=content).output)

        return ''

    def get_testing_attributes(self) -> str:
        """
        Returns the string version of attributes of this class for writing mode == TEST.
        NOTE: Enums redefine it.
        """
        if not self.attributes:
            return j("\n", ind(1), "pass")

        return '\n'.join(
            a.write(WritingMode.TEST) for a in self.attributes
            if not a.name.startswith('_')  # filtering schema class variable
        )


@dataclass
class Decorator(Writer):
    """
    Codewriter for decorators.
    """
    value: str
    dependency: Optional[ClassWriter] = None

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        if mode == WritingMode.GENERATION:
            return self.value
        return ''

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        if self.dependency:
            return self.dependency.as_dependency(mode)
        return []


class Extension(Writer):
    """
    Codewriter for classes extending other classes.
    """

    def __init__(self, fully_qualified_name: str):
        self.dependency: ClassWriter = ClassWriter(fully_qualified_name)

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        return self.dependency.write(WritingMode.TYPE)

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        return self.dependency.as_dependency(mode)


@dataclass
class Attribute(Writer):
    """
    Codewriter for an attribute of a class.
    An attribute has a type, which is expressed by a ClassWriter.
    """
    name: str
    type: ClassWriter
    default_value: Optional[str] = None
    doc: Docstring = Docstring()

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:

        default = f' = {self.default_value}' if self.default_value else ''

        if mode == WritingMode.TEST:
            test_attribute = self.type.write(WritingMode.TEST_ATTRIBUTE)
            return f'{self.name} = lazy_attribute(lambda x: {test_attribute})'

        if mode == WritingMode.PARAMETER:
            return f'{self.name}: {self.type.write(WritingMode.TYPE)}{default}'

        if mode == WritingMode.DOCSTRING_PARAM:
            return f':param {self.name}: {self.doc}'

        if isinstance(self.type, EnumValueWriter):
            name = self.name
            if self.name.startswith('_'):
                # enums names cannot start with '_'
                while name.startswith('_'):
                    name = name[1:]
            str_attribute = f'{name} = {self.type.write(WritingMode.TYPE)}{default}'
        else:
            str_attribute = f'{self.name}: {self.type.write(WritingMode.TYPE)}{default}'

        return textwrap.indent(
            j(
                self.doc.write(WritingMode.TYPE, with_indentation),
                str_attribute,
                self.type.comment.write(WritingMode.TYPE)
            ),
            ind(with_indentation)
        )

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        return self.type.as_dependency(mode)


@dataclass
class Method(Writer):
    """
    Codewriter for a method of a class.
    """

    name: str
    parameters: List[Attribute]
    return_type: ClassWriter
    doc: Docstring = Docstring()
    errors: List[ClassWriter] = dataclasses_field(default_factory=list)

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        if mode == WritingMode.GENERATION:
            str_doc = j(self.doc.value, '\n\n') if self.doc else ''

            return j(
                # spacer
                '\n',

                # begin definition
                j(f'def { to_snake_case(self.name)}(', '\n'),

                # arguments
                textwrap.indent(
                    ',\n'.join(
                        ['self'] + [p.write(WritingMode.PARAMETER) for p in self.parameters]),
                    ind(2)
                ),

                # definition_end
                j('\n) -> ', self.return_type.write(WritingMode.TYPE), ':\n'),

                # doc begin
                textwrap.indent(j('"""\n', str_doc), ind(1)),

                # doc params
                textwrap.indent(
                    '\n'.join(
                        (f'{p.write(WritingMode.DOCSTRING_PARAM)}' for p in self.parameters)),
                    ind(1)
                ),

                # doc raises
                textwrap.indent(
                    '\n' + '\n'.join(
                        (f'{p.write(WritingMode.DOCSTRING_RAISES)}'
                         for p in self.errors)),  # pylint: disable=E1133
                    ind(1)
                ),

                # doc end
                textwrap.indent(j('\n"""\npass'), ind(1)),
            )

        return ''

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        return [dep for parameter in self.parameters for dep in parameter.as_dependency(mode)] + \
               self.return_type.as_dependency(mode)


class EnumClassWriter(ClassWriter):
    """
    Codewriter for enum classe.
    """

    def __init__(self,
                 fully_qualified_name: str,
                 doc: Optional[str] = None,
                 prefix: Optional[str] = None):
        super().__init__(fully_qualified_name, doc, prefix)

        self.extensions = [
            Extension('enum.Enum')
        ]

    def get_testing_attributes(self) -> str:
        return f'value = lazy_attribute(lambda x: fake.enum_with_schema({self.name}))'

    def all_dependencies(self, mode: WritingMode) -> Set[Dependency]:
        if mode == WritingMode.TEST:
            return {Dependency(self.output_prefix, 'fake', None)}

        return super().all_dependencies(mode)


class EnumValueWriter(ClassWriter):
    """
    Codewriter for enum values.
    """

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        return f"'{self.name}'"

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        return []


class SimpleTypeClassWriter(ClassWriter):
    """
    Codewriter for simple types such as int, str, bool, etc.
    """

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        if mode == WritingMode.TEST_ATTRIBUTE:
            if self.name == 'None':
                return 'None'
            return f'fake.py{self.name}()'
        return self.name

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        if mode == WritingMode.TEST:
            return [Dependency(self.output_prefix, 'fake', None)]
        return []


class ClassVarClassWriter(ClassWriter):
    """
    Codewriter for class variables (e.g. the _schema property for Avro schemas (str))
    """

    def __init__(self, writer: ClassWriter):
        self.class_writer: ClassWriter = writer
        self.dep = ClassWriter('typing.ClassVar')

        super().__init__(self.write(WritingMode.GENERATION))

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        return f'ClassVar[{self.class_writer.write(WritingMode.TYPE)}]'

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        if mode == WritingMode.TEST:
            return []
        return self.class_writer.as_dependency(mode) + self.dep.as_dependency(mode)
