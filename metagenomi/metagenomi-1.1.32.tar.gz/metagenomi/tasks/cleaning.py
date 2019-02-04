from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import to_int


class CleaningBase(MgTask):
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)
        self.total_removed_reads = to_int(self.d['total_removed_reads'])
        self.output = self.d['output']

        self.schema = {**self.schema, **{
            'total_removed_reads': {'type': 'integer', 'required': True},
            'output': {'type': 'dict', 'required': True, 'schema': {
                'fwd': {'type': 's3file', 'required': True},
                'rev': {'type': 's3file', 'required': True},
            }}
        }}


class QualityTrimming(CleaningBase):
    def __init__(self, mgid, **data):
        CleaningBase.__init__(self, mgid, **data)

        if self.check:
            self.validate()


class AdapterRemoval(CleaningBase):
    def __init__(self, mgid, **data):
        CleaningBase.__init__(self, mgid, **data)
        self.ftrimmed_reads = to_int(self.d['ftrimmed_reads'])
        self.ktrimmed_reads = to_int(self.d['ktrimmed_reads'])
        self.trimmed_by_overlap_reads = to_int(self.d['trimmed_by_overlap_reads'])

        self.schema = {**self.schema, **{
            'ftrimmed_reads': {'type': 'integer', 'required': True},
            'ktrimmed_reads': {'type': 'integer', 'required': True},
            'trimmed_by_overlap_reads': {'type': 'integer', 'required': True}
        }}

        if self.check:
            self.validate()


class ContaminantRemoval(CleaningBase):
    def __init__(self, mgid, **data):
        CleaningBase.__init__(self, mgid, **data)
        if self.check:
            self.validate()
