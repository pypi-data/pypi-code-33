import asyncio
import operator
import typing
import collections.abc

from anji_orm import core, orm_register
from anji_orm.core.context import CONTEXT_MARKS

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.1"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['FileRecord', 'FileDictProxy']

FileContent = typing.Union[str, bytes]


class FileRecord:

    __slots__ = ('_name', '_content', '_changed', '_record', '_in_bytes')

    _name: str
    _content: typing.Optional[FileContent]
    _changed: bool
    _record: typing.Optional[core.Model]
    _in_bytes: bool

    def __init__(
            self, name: str, content: typing.Optional[FileContent] = None,
            record: typing.Optional[core.Model] = None, in_bytes: bool = False) -> None:
        self._name = name
        self._content = content
        self._record = record
        self._changed = False
        self._in_bytes = in_bytes

    @property
    def name(self) -> str:
        return self._name

    @property
    def content(self) -> typing.Optional[FileContent]:
        if not self._content and not orm_register.async_mode:
            orm_register.shared.file_extension.download_file(self)
        return self._content

    @content.setter
    def content(self, value: FileContent) -> None:
        self._changed = self._content != value
        self._content = value

    @property
    def record(self) -> typing.Optional[core.Model]:
        return self._record

    @property
    def changed(self) -> bool:
        return self._changed

    @property
    def in_bytes(self) -> bool:
        if self._content is None:
            return self._in_bytes
        return isinstance(self._content, bytes)

    def reset(self) -> None:
        self._changed = False

    async def ensure(self) -> None:
        if not self._content:
            await orm_register.shared.file_extension.async_download_file(self)

    def __str__(self) -> str:
        return f'FileRecord[{self.name}]'

    def __repr__(self) -> str:
        return self.__str__()


class FileDictProxy(collections.abc.MutableMapping):

    __slots__ = (
        'internal_dict', 'old_values',
        'record_link', 'changed_keys'
    )

    internal_dict: typing.Dict[str, FileRecord]
    old_values: typing.List[FileRecord]
    changed_keys: typing.Set[str]
    record_link: core.Model

    def __init__(self, record: core.Model) -> None:
        self.internal_dict = {}
        self.old_values = []
        self.changed_keys = set()
        self.record_link = record

    @property
    def changed(self):
        if self.old_values:
            return True
        if self.changed_keys:
            return True
        return any(map(operator.attrgetter('changed'), self.internal_dict.values()))

    async def ensure(self):
        await asyncio.gather(*[
            file_record.ensure()
            for file_record in self.internal_dict.values()
        ])

    def __setitem__(self, key, value: FileRecord) -> None:
        if not isinstance(value, FileRecord):
            raise TypeError("You can set only file record type!")
        value._record = self.record_link
        if key in self.internal_dict:
            self.old_values.append(self.internal_dict.pop(key))
        self.internal_dict[key] = value
        if not getattr(CONTEXT_MARKS, 'load', False):
            self.changed_keys.add(key)

    def __contains__(self, key):
        return key in self.internal_dict

    def __delitem__(self, key):
        old_value = self.internal_dict.pop(key)
        if old_value is not None:
            self.old_values.append(old_value)

    def __getitem__(self, key):
        return self.internal_dict[key]

    def __iter__(self):
        return iter(self.internal_dict)

    def __len__(self):
        return len(self.internal_dict)

    @classmethod
    def from_dict(
            cls, dict_value: typing.Dict[str, typing.Union[FileRecord, typing.Dict]],
            record_link: core.Model) -> 'FileDictProxy':
        base = FileDictProxy(record_link)
        for file_name, file in dict_value.items():
            if isinstance(file, dict):
                file = FileRecord(file['name'], in_bytes=file['in_bytes'])
            base[file_name] = file
        return base
