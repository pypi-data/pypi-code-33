import pandas as pd
import numpy as np

from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import (to_decimal, to_int)


class AssemblyStats(MgTask):
    '''
    TODO: write me
    '''
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)
        # self.key = 'megahit_metadata'

        self.avg_sequence_len = to_decimal(self.d['avg_sequence_len'])
        self.n50 = int(self.d['n50'])

        # sequence parameters
        df = pd.DataFrame(self.d['sequence_parameters']).replace([np.nan, ''],
                                                                 'None')
        df = to_int(df, ['length', 'non_ns', 'seq_num'])
        self.sequence_parameters = to_decimal(df, c=['gc'])

        # length distribution
        df = pd.DataFrame(self.d['length_distribution']).replace([np.nan, ''],
                                                                 'None')
        df = to_int(df, ['num_sequences', 'num_bps', 'start', 'end'])
        self.length_distribution = to_decimal(df, c=['num_sequences_percent',
                                                     'num_bps_percent'])

        self.total_bps = int(self.d['total_bps'])
        self.total_seqs = int(self.d['total_seqs'])
        self.assembler = self.d['assembler']

        ld_schema = {
            "num_sequences": {'required': True, 'type': 'list', 'schema': {
                'type': 'integer'}},
            "num_sequences_percent": {'required': True,
                                      'type': 'list',
                                      'schema': {'type': 'decimal'}},
            "num_bps": {'required': True, 'type': 'list', 'schema': {
                'type': 'integer'}},
            "num_bps_percent": {'required': True,
                                'type': 'list',
                                'schema': {'type': 'decimal'}},
            "start": {'required': True, 'type': 'list', 'schema': {
                'type': 'integer'}},
            "end": {'required': True, 'type': 'list', 'schema': {
                'type': 'integer'}}}

        sp_schema = {
            "length": {'required': True, 'type': 'list', 'schema': {
                'type': 'integer'}},
            "gc": {'required': True, 'type': 'list', 'schema': {
                'type': 'decimal'}},
            "description": {'required': True, 'type': 'list', 'schema': {
                'type': 'string', 'minlength': 1}},
            "sequence": {'required': True, 'type': 'list', 'schema': {
                'type': 'string', 'minlength': 1}},
            "non_ns": {'required': True, 'type': 'list', 'schema': {
                'type': 'integer'}},
            "seq_num": {'required': True, 'type': 'list', 'schema': {
                'type': 'integer'}}}

        self.schema = {**self.schema, **{
            'sequence_parameters': {'required': True,
                                    'type': 'dict',
                                    'schema': sp_schema},
            "length_distribution": {'required': True,
                                    'type': 'dict',
                                    'schema': ld_schema},
            'total_seqs': {'required': True, 'type': 'integer'},
            'total_bps': {'required': True, 'type': 'integer'},
            'n50': {'required': True, 'type': 'integer'},
            'avg_sequence_len': {'required': True, 'type': 'decimal'},
            'assembler': {'required': True, 'type': 'string', 'minlength': 1}}}

        if self.check:
            self.validate()
