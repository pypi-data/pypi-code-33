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

        self.avg_sequence_len = to_decimal(self.d.get('avg_sequence_len',
                                                      'None'))
        self.n50 = to_int(self.d.get('n50', 'None'))

        # sequence parameters
        if 'sequence_parameters' in self.d:
            df = pd.DataFrame(self.d['sequence_parameters']).replace([np.nan, ''], 'None')
        else:
            df = None

        df = to_int(df, ['length', 'non_ns', 'seq_num'])
        self.sequence_parameters = to_decimal(df, c=['gc'])

        # length distribution
        if 'length_distribution' in self.d:
            df = pd.DataFrame(self.d['length_distribution']).replace([np.nan, ''], 'None')
        else:
            df = None
            # raise ValueError('Input not in proper dataframe format')

        df = to_int(df, ['num_sequences', 'num_bps', 'start', 'end'])
        self.length_distribution = to_decimal(df, c=['num_sequences_percent',
                                                     'num_bps_percent'])

        self.total_bps = to_int(self.d.get('total_bps', 'None'))
        self.total_seqs = to_int(self.d.get('total_seqs', 'None'))
        self.assembler = self.d.get('assembler', 'None')

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
