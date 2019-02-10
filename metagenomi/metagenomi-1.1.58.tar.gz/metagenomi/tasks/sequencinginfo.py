

from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import (to_decimal, to_int)


class SequencingInfo(MgTask):
    '''
    TODO: write me
    '''
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)
        # self.key = 'megahit_metadata'

        self.avg_length = to_decimal(self.d.get('avg_length', 'None'))
        self.bases = to_int(self.d.get('bases', 'None'))
        self.reads = to_int(self.d.get('reads', 'None'))
        self.insert_size = to_int(self.d.get('insert_size', 'None'))

        self.library_layout = self.d.get('library_layout', 'None')
        self.library_selection = self.d.get('library_selection', 'None')
        self.library_source = self.d.get('library_source', 'None')
        self.library_strategy = self.d.get('library_strategy', 'None')
        self.model = self.d.get('model', 'None')

        self.platform = self.d.get('platform', 'None')
        self.raw_read_paths = self.d.get('raw_read_paths', 'None')
        self.sample_name = self.d.get('sample_name', 'None')

        self.size_mb = 'None'
        if 'size_mb' in self.d:
            self.size_mb = {'fwd': to_decimal(self.d['size_mb']['fwd']),
                            'rev': to_decimal(self.d['size_mb']['rev'])}

        self.spots = to_int(self.d.get('spots', 'None'))
        self.spots_with_mates = to_int(self.d.get('spots_with_mates', 'None'))

        self.extra_metadata = self.d.get('extra_metadata', None)

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
