from metagenomi.models.modelbase import MgModel

from metagenomi.tasks.sampleinfo import SampleInfo


class Sample(MgModel):
    # Possible tasks:
    def __init__(self, mgid, **data):
        MgModel.__init__(self, mgid, **data)

        self.mgtype = 'sample'
        if 'mgtype' in self.d:
            self.mgtype = self.d['mgtype']

        self.sample_info = None
        if 'SampleInfo' in self.d:
            self.sample_info = SampleInfo(self.mgid, db=self.db, **self.d['SampleInfo'])

        self.schema = {**self.schema, **{
            'SampleInfo': {'type': 'dict'}
        }}

        if self.check:
            self.validate()
