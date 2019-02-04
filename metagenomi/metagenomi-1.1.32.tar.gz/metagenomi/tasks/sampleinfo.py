
from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import (to_int, to_decimal, to_datetime)


class SampleInfo(MgTask):
    '''
    TODO: write me
    '''
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)

        # REQUIRED
        self.collection_date = to_datetime(self.d['collection_date'])
        self.depth_cm = to_decimal(self.d['depth_cm'])
        self.description = self.d['description']
        self.geographic_location = self.d['geographic_location']
        self.isolation_source = self.d['isolation_source']
        self.latlon = self.d['latlon']
        self.ph = to_decimal(self.d['ph'])
        self.plant_associated = self.d['plant_associated']
        self.sample_id = self.d['sample_id']
        self.sample_color = self.d['sample_color']

        # TODO: make it pull this from **data
        if 'extra_metadata' in self.d:
            self.extra_metadata = self.d['extra_metadata']
        else:
            self.extra_metadata = None

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
