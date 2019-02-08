from metagenomi.models.modelbase import MgModel

from metagenomi.tasks.sampleinfo import SampleInfo


class Sample(MgModel):
    # Possible tasks:
    def __init__(self, mgid, **data):
        MgModel.__init__(self, mgid, **data)

        self.mgtype = 'sample'
        if 'mgtype' in self.d:
            self.mgtype = self.d['mgtype']

        self.environment = self.d.get('environment', 'None')

        self.sample_info = None
        if 'SampleInfo' in self.d:
            self.sample_info = SampleInfo(
                                    self.mgid, db=self.db,
                                    **self.d['SampleInfo']
                                    )

        self.schema = {**self.schema, **{
            'SampleInfo': {'type': 'dict'},
            'associated': {'type': 'dict', 'required': True, 'schema': {
                'sequencing': {'type': 'list', 'schema': {
                    'type': ['mgid', 'nonestring']}}
                }},
            'environment': {
                'type': 'string', 'required': False,
                'allowed': [
                            'Soil',
                            'Thermophilic',
                            'Ocean',
                            'Fresh water',
                            'Human stool',
                            'Human saliva',
                            'Human other',
                            'Salt-water associated sediment',
                            'Fresh-water associated sediment',
                            'Non-human stool',
                            'Non-human other',
                            'None'
                            ]}}}

        if self.check:
            self.validate()

    def set_environment(self, environment, write=True):
        self.environment = environment

        if write:
            self.write(force=True)
