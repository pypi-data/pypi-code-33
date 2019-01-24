
from ruamel import yaml

from .exceptions import InvalidLLPSException
from .constants import (
    REQUIRED_KEYS,
    OPTIONAL_KEYS,
    CHARACTERS,
    RESERVED_KEYS,
)


def validate_version_str(to_validate):
    """Validate a SemVer style version string."""
    exc = InvalidLLPSException(f'Bad version string "{to_validate}"')
    if to_validate[0] != 'v':
        raise exc
    tkns = to_validate[1:].split('.')
    if len(tkns) != 3:
        raise exc
    try:
        [int(val) for val in tkns]
    except ValueError:
        raise exc


class ProjectSchema:
    """Represent a project schema."""

    def __init__(self, **kwargs):
        for key in REQUIRED_KEYS:
            try:
                setattr(self, key, kwargs[key])
            except KeyError:
                raise InvalidLLPSException(f'Missing required key "{key}"')
        for key in OPTIONAL_KEYS:
            setattr(self, key, kwargs.get(key, None))

        self.validate_str('project_name', charset=CHARACTERS, max_len=128)
        self.validate_str('project_description', max_len=256)
        self.validate_str('author', max_len=256)
        validate_version_str(self.version)
        validate_version_str(self.spec_version)
        self.source_names = self.validate_sources()

    def validate_str(self, key, charset=None, max_len=0):
        """Raise an exception if the string does not validate."""
        try:
            to_validate = getattr(self, key).lower()
        except AttributeError:
            return
        if max_len and len(to_validate) > max_len:
            raise InvalidLLPSException(f'{key} is too long. {len(to_validate)} > {max_len}')
        if not charset:
            return
        for char in to_validate:
            if char not in charset:
                raise InvalidLLPSException(f'"{char}" is not a valid character for {key}')

    def validate_sources(self):
        """Validate sources and return a set of valid source names."""
        source_names = set()
        for source_name, source_definition in self.sources.items():
            if source_name in source_names:
                raise InvalidLLPSException(f'Duplicate source "{source_name}"')
            if not source_name or source_name.lower() in RESERVED_KEYS:
                raise InvalidLLPSException(f'Source name "{source_name}" is invalid.')
            try:
                source_type = source_definition['type'].lower()
                if source_type == 's3':
                    source_definition['bucket_name']
                elif source_type == 'local':
                    source_definition['hostname']
                    source_definition['root_dir']
                elif source_type == 'tarball':
                    source_definition['file']
            except KeyError:
                raise InvalidLLPSException(f'Invalid source definition for source {source_name}.')
            source_names.add(source_name)
        return source_names

    def validate_file(self, file_schema):
        """Validate a file schema."""
        try:
            filepath = file_schema['path']
            file_schema['md5']
        except KeyError:
            raise InvalidLLPSException('Missing a required key in a file schema')

        num_sources = 0
        for source_name in self.source_names:
            if source_name in file_schema:
                num_sources += 1
        if not num_sources:
            raise InvalidLLPSException(f'No valid sources present for file {filepath}')

    def add_file(self, file_schema):
        """Validate and add a file to this ProjectSchema."""
        self.validate_file(file_schema)
        self.files.append(file_schema)

    def dump(self):
        """Dump this Project Schema to YAML."""
        my_dict = yaml.comments.CommentedMap()
        for key in REQUIRED_KEYS:
            if key in ['files', 'sources']:
                continue
            my_dict[key] = getattr(self, key)
        for key in OPTIONAL_KEYS:
            try:
                val = getattr(self, key)
                if val:
                    my_dict[key] = val
            except KeyError:
                pass
        my_dict['sources'] = self.sources
        my_dict['files'] = self.files
        return yaml.round_trip_dump(my_dict)

    @classmethod
    def from_file(cls, filename):
        return cls(**yaml.load(open(filename).read(), Loader=yaml.Loader))
