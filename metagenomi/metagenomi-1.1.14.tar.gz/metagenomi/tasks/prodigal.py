from metagenomi.tasks.taskbase import MgTask


class Prodigal(MgTask):
    '''
    RULES
    '''
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)
        # self.key = 'prodigal_metadata'

        self.proteins_predicted = int(self.d['proteins_predicted'])
        self.min_sequence_length = int(self.d['min_sequence_length'])
        self.contigs_above_cutoff = int(self.d['contigs_above_cutoff'])
        self.contigs_below_cutoff = int(self.d['contigs_below_cutoff'])
        self.mode = self.d['mode']
        self.protein_file = self.d['protein_file']
        self.pullseq_contigs = self.d['pullseq_contigs']

        self.schema = {
            **self.schema, **{
                "proteins_predicted": {"required": True, "type": "integer"},
                "min_sequence_length": {"required": True, "type": "integer"},
                "contigs_above_cutoff": {"required": True, "type": "integer"},
                "contigs_below_cutoff": {"required": True, "type": "integer"},
                "pullseq_contigs": {'required': True, 'type': 's3file'},
                "mode": {'required': True,
                         'type': 'string',
                         'allowed': ['single', 'meta']
                         }
                    },
                "protein_file": {'required': True, 'type': 's3file'}
            }

        if self.check:
            self.validate()
