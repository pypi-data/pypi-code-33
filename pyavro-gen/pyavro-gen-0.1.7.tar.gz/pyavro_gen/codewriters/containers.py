"""
Codewriters for container classes.
"""

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

from typing import List

from pyavro_gen.codewriters.core import ClassWriter, WritingMode, Dependency
from pyavro_gen.codewriters.utils import j


class UnionClassWriter(ClassWriter):
    """
    Codewriter for Union and Optionals.
    """

    def __init__(self, writers: List[ClassWriter]) -> None:
        if len(writers) == 2 and any(t.name == 'None' for t in writers):
            self.class_writers = [w for w in writers if w.name != 'None']
            self.type_prefix = 'Optional'
            self.dep = ClassWriter('typing.Optional')
        else:
            self.class_writers = writers
            self.type_prefix = 'Union'
            self.dep = ClassWriter('typing.Union')

        super().__init__(self.write(WritingMode.GENERATION))

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        if mode == WritingMode.TEST_ATTRIBUTE:
            ta_str = [w.write(WritingMode.TEST_ATTRIBUTE) for w in self.class_writers]
            rand_len = len(self.class_writers) - 1
            if self.type_prefix == 'Optional':
                ta_str.append('None')
                rand_len += 1
            test_attribute = ", ".join(ta_str)
            return f'[{test_attribute}][randint(0, {rand_len})]'

        union_arguments = ", ".join(w.write(WritingMode.TYPE) for w in self.class_writers)
        return f'{self.type_prefix}[{union_arguments}]'

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        deps = [dep for writer in self.class_writers for dep in writer.as_dependency(mode)]
        if mode == WritingMode.TEST:
            return deps + ClassWriter('random.randint').as_dependency(mode)
        return deps + self.dep.as_dependency(mode)


class ListClassWriter(ClassWriter):
    """
    Codewriter for Lists.
    """

    def __init__(self, writer: ClassWriter) -> None:
        self.class_writer: ClassWriter = writer
        self.dep = ClassWriter('typing.List')

        super().__init__(self.write(WritingMode.GENERATION))

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        if mode == WritingMode.TEST_ATTRIBUTE:
            test_attribute = self.class_writer.write(WritingMode.TEST_ATTRIBUTE)
            return f'[{test_attribute} for _ in range(randint(1, 5))]'
        return f'List[{self.class_writer.write(WritingMode.TYPE)}]'

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        if mode == WritingMode.TEST:
            return self.class_writer.as_dependency(mode) + \
                   ClassWriter('random.randint').as_dependency(mode)
        return self.class_writer.as_dependency(mode) + self.dep.as_dependency(mode)


class MapClassWriter(ClassWriter):
    """
    Codewriter for Maps.
    """

    def __init__(self, writer: ClassWriter) -> None:
        self.class_writer: ClassWriter = writer
        self.dep = ClassWriter('typing.Dict')

        super().__init__(self.write(WritingMode.GENERATION))

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        if mode == WritingMode.TEST_ATTRIBUTE:
            test_attribute = self.class_writer.write(WritingMode.TEST_ATTRIBUTE)
            return j('{', f'fake.pystr(): {test_attribute} for _ in range(randint(3, 10))', '}')
        # All Avro Map keys are strings
        return f'Dict[str, {self.class_writer.write(WritingMode.TYPE)}]'

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        if mode == WritingMode.TEST:
            return self.class_writer.as_dependency(mode) + \
                   ClassWriter('random.randint').as_dependency(mode)
        return self.class_writer.as_dependency(mode) + self.dep.as_dependency(mode)
