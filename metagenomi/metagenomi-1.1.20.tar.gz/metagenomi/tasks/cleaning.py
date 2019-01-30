from metagenomi.tasks.taskbase import MgTask


class QualityTrimming(MgTask):
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)
        self.total_removed_reads = int(self.d['total_removed_reads'])

        self.schema = {**self.schema, **{
            'total_removed_reads': {'type': 'integer', 'required': True},
            'output': {'type': 's3file', 'required': True}
        }}

        if self.validate:
            self.validate()


class AdapterRemoval(MgTask):
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)
        self.ftrimmed_reads = data['ftrimmed_reads']
        self.ktrimmed_reads = data['ktrimmed_reads']
        self.total_removed_reads = data['total_removed_reads']
        self.trimmed_by_overlap_reads = data['trimmed_by_overlap_reads']

        self.schema = {**self.schema, **{
            'ftrimmed_reads': {'type': 'integer', 'required': True},
            'ktrimmed_reads': {'type': 'integer', 'required': True},
            'total_removed_reads': {'type': 'integer', 'required': True},
            'trimmed_by_overlap_reads': {'type': 'integer', 'required': True},
            'output': {'type': 's3file', 'required': True}
        }}

        if self.validate:
            self.validate()


class ContaminantRemoval(MgTask):
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)
        self.total_removed_reads = data['total_removed_reads']

        self.schema = {**self.schema, **{
            'total_removed_reads': {'type': 'integer', 'required': True},
            'output': {'type': 's3file', 'required': True}
        }}

        if self.validate:
            self.validate()
