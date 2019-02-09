
from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import (to_int, to_decimal, to_datetime)


class SampleInfo(MgTask):
    '''
    TODO: write me
    '''
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)

        # REQUIRED
        self.collection_date = to_datetime(self.d.get('collection_date', 'None'))
        self.depth_cm = to_decimal(self.d.get('depth_cm', 'None'))
        self.description = self.d.get('description', 'None')
        self.geographic_location = self.d.get('geographic_location', 'None')
        self.isolation_source = self.d.get('isolation_source', 'None')
        self.latlon = self.d.get('latlon', 'None')

        self.ph = to_decimal(self.d.get('ph', 'None'))
        self.plant_associated = self.d.get('plant_associated', 'None')
        self.sample_id = self.d.get('sample_id', 'None')
        self.sample_color = self.d.get('sample_color', 'None')

        # TODO: make it pull this from **data
        self.extra_metadata = {k: v for k, v in self.d.items() if k not in self.__dict__.keys()}
        # self.extra_metadata = self.d.get('extra_metadata', None)

        self.schema = {**self.schema, **{
            'collection_date': {
                'required': True, 'type': ['datestring', 'nonestring']},
            'depth_cm': {
                'required': True, 'type': ['decimal', 'nonestring']},
            'description': {
                'required': True, 'type': 'string', 'minlength': 1},
            'geographic_location': {
                'required': True, 'type': 'string', 'minlength': 1},
            'isolation_source': {
                'required': True, 'type': 'string', 'minlength': 1},
            'latlon': {
                'required': True, 'type': 'latlon'},
            'ph': {
                'required': True, 'type': ['decimal', 'nonestring']},
            'plant_associated': {
                'required': True, 'type': ['boolean', 'nonestring']},
            'sample_id': {
                'required': True, 'type': 'string', 'minlength': 1},
            'sample_color': {
                'required': True, 'type': 'string', 'minlength': 1},
            'extra_metadata': {
                'required': False, 'type': 'dict'}
            }
        }

        if self.check:
            self.validate()
