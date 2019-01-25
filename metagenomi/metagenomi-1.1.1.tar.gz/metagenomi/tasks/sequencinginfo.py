import pandas as pd

from metagenomi.models.base import MgObj
from metagenomi.helpers import to_decimal


class SequencingInfo(MgObj):
    '''
    TODO: write me
    '''
    def __init__(self, mgid, **kwargs):
        MgObj.__init__(self, mgid, **kwargs)
        # self.key = 'megahit_metadata'

        self.avg_length = int(kwargs['avg_length'])
        self.bases = int(kwargs['bases'])
        self.insert_size = int(kwargs['insert_size'])
        self.library_layout = kwargs['library_layout']
        self.library_selection = kwargs['library_selection']
        self.library_source = kwargs['library_source']
        self.library_strategy = kwargs['library_strategy']
        self.model = kwargs['model']

        self.platform = kwargs['platform']
        self.raw_read_paths = kwargs['raw_read_paths']
        self.sample_name = kwargs['sample_name']

        self.size_mb = kwargs['size_mb']

        self.spots = kwargs['spots']
        self.spots_with_mates = kwargs['spots_with_mates']

        self.schema = {**self.schema, **{
            "avg_length": {'type': 'integer', 'min': 0},
            "bases": {'type': 'integer', 'required': True, 'min': 0},
            "insert_size": {'type': ['integer', 'nonestring'], 'min': 0},
            "library_layout": {'type': 'string', 'allowed': ['PAIRED', 'UNPAIRED'],
                               'required': True},
            "library_selection": {'type': 'string', 'allowed': ['RANDOM'],
                                  'required': True},
            "library_source": {'type': 'string',
                               'allowed': ['METAGENOMIC', 'METATRANSCRIPTOMIC'],
                               'required': True},
            "library_strategy": {'type': 'string', 'allowed': ['WGS'], 'required': True},
            "model": {'type': 'string', 'required': True},
            "platform": {'type': 'string', 'required': True},
            "raw_read_paths": {'type': 'dict', 'required': True, 'schema': {
                "fwd": {"type": "s3object"},
                "rev": {"type": "s3object"},
                }
            },
            "sample_name": {"type": "string", "required": True},
            "size_mb": {"type": "dict", "required": True, "schema": {
              "fwd": {"type": "decimal", "required": True},
              "rev": {"type": "decimal", "required": True},
              }
            },
            "spots": {'type': ['integer', 'nonestring'], "required": True},
            "spots_with_mates": {'type': ['integer', 'nonestring'], "required": True},
            "cmd_run": {'type': 'nonestring', "required": True}
        }}
