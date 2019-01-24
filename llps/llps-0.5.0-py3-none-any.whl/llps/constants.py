
CURRENT_SPEC_VERSION = 'v0.1.0'
REQUIRED_KEYS = [
    'project_name',
    'project_description',
    'version',
    'sources',
    'files',
    'spec_version'
]
OPTIONAL_KEYS = [
    'project_long_description',
    'author',
    'author_email',
    'project_website',
]
CHARACTERS = set('abcdefghijklmnopqrstuvwxyz_-')
RESERVED_KEYS = set(REQUIRED_KEYS + OPTIONAL_KEYS + [
    'path',
    'bucket_name',
    'endpoint_url',
    'remote_path',
    's3',
    'file',
    'hostname',
    'root_dir',
    'md5',
])
