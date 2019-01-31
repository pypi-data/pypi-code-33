from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import to_decimal


class Mapping(MgTask):
    def __init__(self, mgid, **data):
        if not len(data):
            raise ValueError('Cannot initialize a mapping with no data')

        MgTask.__init__(self, mgid, **data)

        self.aligned_mapq_greaterequal_10 = int(self.d['aligned_mapq_greaterequal_10'])
        self.aligned_mapq_less_10 = int(self.d['aligned_mapq_less_10'])
        self.percent_pairs = to_decimal(self.d['percent_pairs'])
        self.reads_per_sec = int(self.d['reads_per_sec'])
        self.seed_size = int(self.d['seed_size'])
        self.time_in_aligner_seconds = int(self.d['time_in_aligner_seconds'])

        self.too_short_or_too_many_nns = int(self.d['too_short_or_too_many_nns'])
        self.total_bases = int(self.d['total_bases'])
        self.total_reads = int(self.d['total_reads'])
        self.unaligned = int(self.d['unaligned'])
        self.reads_mapped = dict(self.d['reads_mapped'])

        self.reference = str(self.d['reference'])

        self.schema = {**self.schema, **{
            'aligned_mapq_greaterequal_10': {'required': True, 'type': 'integer'},
            'aligned_mapq_less_10': {'required': True, 'type': 'integer'},
            'percent_pairs': {'required': True, 'type': 'decimal'},
            'reads_per_sec': {'required': True, 'type': 'integer'},
            'seed_size': {'required': True, 'type': 'integer'},
            'time_in_aligner_seconds': {'required': True, 'type': 'integer'},
            'too_short_or_too_many_nns': {'required': True, 'type': 'integer'},
            'total_bases': {'required': True, 'type': 'integer'},
            'total_reads': {'required': True, 'type': 'integer'},
            'unaligned': {'required': True, 'type': 'integer'},
            'reads_mapped': {
                'required': True, 'type': 'dict', 'schema': {
                    'fwd': {'required': True, 'type': 's3file'},
                    'rev': {'required': True, 'type': 's3file'}
                }
            },
            'reference': {'required': True, 'type': 's3file'}
        }}

        if self.check:
            self.validate()

    def write(self):
        '''
        Create new Mapping entry
        '''
        self._update(self.whoami(), self.to_dict(validate=True, clean=True))
