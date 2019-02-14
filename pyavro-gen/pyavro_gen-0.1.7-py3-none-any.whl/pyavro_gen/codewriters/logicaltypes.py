"""
Codewriters for Avro logical types.
"""

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

from typing import Optional, List

from pyavro_gen.codewriters.core import ClassWriter, WritingMode, Dependency


class DatetimeClassWriter(ClassWriter):
    """
    Codewriter for datetime/timestamps.
    Can deal with Avro's millis and micros.
    """

    def __init__(self, timespec: Optional[str] = None):
        self.dep = ClassWriter('datetime.datetime')
        self.timespec = timespec

        super().__init__(self.write(WritingMode.GENERATION))

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        if mode == WritingMode.TEST_ATTRIBUTE:
            if self.timespec:
                return 'datetime.fromisoformat(datetime.now(tz=UTCTzinfo())' \
                       '.isoformat(timespec="milliseconds"))'
            return 'datetime.now(tz=UTCTzinfo())'
        return f'datetime'

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        if mode == WritingMode.TEST:
            return ClassWriter('fastavro._timezone.UTCTzinfo').as_dependency(mode) + \
                   self.dep.as_dependency(mode)
        return self.dep.as_dependency(mode)


class DateClassWriter(ClassWriter):
    """
    Codewriter for dates.
    """

    def __init__(self) -> None:
        self.dep = ClassWriter('datetime.date')
        super().__init__(self.write(WritingMode.GENERATION))

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        if mode == WritingMode.TEST_ATTRIBUTE:
            return 'datetime.now(tz=UTCTzinfo()).date()'
        return 'date'

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        if mode == WritingMode.TEST:
            return ClassWriter('fastavro._timezone.UTCTzinfo').as_dependency(mode) + \
                   self.dep.as_dependency(mode) + \
                   ClassWriter('datetime.datetime').as_dependency(mode)
        return self.dep.as_dependency(mode)


class UUIDClassWriter(ClassWriter):
    """
    Codewriter for UUIDs
    """

    def __init__(self) -> None:
        self.dep = ClassWriter('uuid.UUID')

        super().__init__(self.write(WritingMode.GENERATION))

    def write(self, mode: WritingMode = WritingMode.GENERATION, with_indentation: int = 0) -> str:
        if mode == WritingMode.TEST_ATTRIBUTE:
            return 'uuid4()'
        return f'UUID'

    def as_dependency(self, mode: WritingMode) -> List[Dependency]:
        if mode == WritingMode.TEST:
            return ClassWriter('uuid.uuid4').as_dependency(mode)
        return self.dep.as_dependency(mode)
