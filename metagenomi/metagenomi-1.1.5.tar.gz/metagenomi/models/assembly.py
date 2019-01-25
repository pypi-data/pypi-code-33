from metagenomi.models.modelbase import MgModel
from metagenomi.tasks.megahit import Megahit
from metagenomi.tasks.prodigal import Prodigal
from metagenomi.tasks.mapping import Mapping
from metagenomi.tasks.jgimetadata import JgiMetadata

from metagenomi.logger import logger


class Assembly(MgModel):
    # Possible tasks:
    # Mapping, Megahit, TODO:Prodigal
    def __init__(self, mgid, **data):
        MgModel.__init__(self, mgid, **data)

        self.mgtype = 'assembly'
        if 'mgtype' in self.d:
            self.mgtype = self.d['mgtype']

        self.mappings = None
        if 'Mappings' in self.d:
            self.mappings = []
            for m in self.d['Mappings']:
                self.mappings.append(Mapping(self.mgid, **m))

        self.megahit = None
        if 'Megahit' in self.d:
            self.megahit = Megahit(self.mgid, **self.d['Megahit'])

        self.prodigal = None
        if 'Prodigal' in self.d:
            self.prodigal = Prodigal(self.mgid, **self.d['Prodigal'])

        self.jgi_metadata = None
        if 'JgiMetadata' in self.d:
            self.jgi_metadata = JgiMetadata(self.mgid, **self.d['JgiMetadata'])

        # No MgTasks are required. TODO: Except perhaps mapping?
        self.schema = {**self.schema, **{
            'Prodigal': {'type': 'dict'},
            'Megahit': {'type': 'dict'},
            'Mappings': {'type': 'list'},
            'Jgi_metadata': {'type': 'dict'},
            'mgtype': {'type': 'string',
                       'allowed': ['assembly'],
                       'required': True}
            },
            'associated': {'type': 'dict', 'required': True, 'schema': {
                'sequencing': {'type': ['mgid', 'nonestring'], 'required': True},
                }
            }
        }

        self.to_dict(validate=True)
