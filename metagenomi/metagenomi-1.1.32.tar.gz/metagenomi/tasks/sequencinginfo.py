

from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import (to_decimal, to_int)


class SequencingInfo(MgTask):
    '''
    TODO: write me
    '''
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)
        # self.key = 'megahit_metadata'

        self.avg_length = to_decimal(self.d['avg_length'])
        self.bases = to_int(self.d['bases'])
        self.reads = to_int(self.d['reads'])
        self.insert_size = to_int(self.d['insert_size'])

        self.library_layout = self.d['library_layout']
        self.library_selection = self.d['library_selection']
        self.library_source = self.d['library_source']
        self.library_strategy = self.d['library_strategy']
        self.model = self.d['model']

        self.platform = self.d['platform']
        self.raw_read_paths = self.d['raw_read_paths']
        self.sample_name = self.d['sample_name']

        self.size_mb = {'fwd': to_decimal(self.d['size_mb']['fwd']),
                        'rev': to_decimal(self.d['size_mb']['rev'])}

        self.spots = to_int(self.d['spots'])
        self.spots_with_mates = to_int(self.d['spots_with_mates'])

        self.extra_metadata = None
        if 'extra_metadata' in self.d:
            self.extra_metadata = self.d['extra_metadata']

        self.schema = {**self.schema, **{
            'avg_length': {'type': 'decimal', 'required': True, 'min': 0},
            'bases': {'type': 'integer', 'required': True, 'min': 0},
            'reads': {'type': 'integer', 'required': True, 'min': 0},
            'insert_size': {'type': ['integer', 'nonestring'], 'min': 0},
            'library_layout': {'type': 'string',
                               'allowed': ['PAIRED', 'UNPAIRED'],
                               'required': True},
            'library_selection': {'type': 'string',
                                  'required': True},
            'library_source': {'type': 'string',
                               'allowed': ['METAGENOMIC',
                                           'METATRANSCRIPTOMIC'],
                               'required': True},
            'library_strategy': {'type': 'string',
                                 'required': True},
            'model': {'type': 'string', 'required': True},
            'platform': {'type': 'string', 'required': True},
            'raw_read_paths': {'type': 'dict', 'required': True, 'schema': {
                'fwd': {'type': ['s3file', 'nonestring']},
                'rev': {'type': ['s3file', 'nonestring']},
                }
            },
            'sample_name': {'type': 'string', 'required': True},
            'size_mb': {'type': 'dict', 'required': True, 'schema': {
              'fwd': {'type': 'decimal', 'required': True},
              'rev': {'type': 'decimal', 'required': True}
              }
            },
            'spots': {'type': ['integer', 'nonestring'], 'required': True},
            'spots_with_mates': {'type': ['integer', 'nonestring'],
                                 'required': True},
            'cmd_run': {'type': 'nonestring', 'required': True},
            'extra_metadata': {'type': 'dict'}
        }}

        if self.check:
            self.validate()
