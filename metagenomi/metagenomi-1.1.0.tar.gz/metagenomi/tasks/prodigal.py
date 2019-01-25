from metagenomi.tasks.taskbase import MgTask


class Prodigal(MgTask):
    '''
    RULES
    '''
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)
        # self.key = 'prodigal_metadata'

        self.proteins_predicted = self.d['proteins_predicted']
        self.min_sequence_length = self.d['min_sequence_length']
        self.contigs_above_cutoff = self.d['contigs_above_cutoff']
        self.contigs_below_cutoff = self.d['contigs_below_cutoff']
        self.mode = self.d['mode']
        self.proteins = self.d['proteins']

        self.schema = {
            **self.schema, **{
                "proteins_predicted": {"required": True, "type": "integer"},
                "min_sequence_length": {"required": True, "type": "integer"},
                "contigs_above_cutoff": {"required": True, "type": "integer"},
                "contigs_below_cutoff": {"required": True, "type": "integer"},
                "mode": {'required': True,
                         'type': 'string',
                         'allowed': ['single', 'meta']
                         }
                    },
                "proteins": {'required': True, 'type': 's3file'}
            }
