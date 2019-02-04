from metagenomi.models.modelbase import MgModel
from metagenomi.tasks.assemblystats import AssemblyStats
from metagenomi.tasks.prodigal import Prodigal
from metagenomi.tasks.mapping import Mapping
from metagenomi.tasks.jgimetadata import JgiMetadata

from metagenomi.logger import logger


class Assembly(MgModel):
    # Possible tasks:
    # Mapping, Megahit, TODO:Prodigal
    def __init__(self, mgid, **data):
        MgModel.__init__(self, mgid, **data)

        self.s3path = self.d['s3path']

        self.mgtype = 'assembly'
        if 'mgtype' in self.d:
            self.mgtype = self.d['mgtype']

        self.mappings = None
        if 'Mappings' in self.d:
            self.mappings = []
            for m in self.d['Mappings']:
                self.mappings.append(Mapping(self.mgid, db=self.db, **m))

        self.assembly_stats = None
        if 'AssemblyStats' in self.d:
            self.assembly_stats = AssemblyStats(self.mgid,
                                                db=self.db, **self.d['AssemblyStats'])

        self.prodigal = None
        if 'Prodigal' in self.d:
            self.prodigal = Prodigal(self.mgid, db=self.db, **self.d['Prodigal'])

        self.jgi_metadata = None
        if 'JgiMetadata' in self.d:
            self.jgi_metadata = JgiMetadata(self.mgid, db=self.db, **self.d['JgiMetadata'])

        # No MgTasks are required. TODO: Except perhaps mapping?
        self.schema = {**self.schema, **{
            'Prodigal': {'type': 'dict'},
            'AssemblyStats': {'type': 'dict'},
            'Mappings': {'type': 'list'},
            'JgiMetadata': {'type': 'dict'},
            'mgtype': {'type': 'string',
                       'allowed': ['assembly'],
                       'required': True}
            },
            's3path': {'type': 's3file', 'required': True},
            'associated': {'type': 'dict',
                           'required': True,
                           'schema': {'sequencing': {
                                'type': 'list',
                                'schema': {'type': ['mgid',
                                                    'nonestring']},
                                'required': True
                                },
                            }
                        }
            }

        if self.check:
            self.validate()

    def generate_prodigal_cmd(self, cutoff=1000):
        genes = f"{self.s3path}.genes"
        faa = f"{self.s3path}.genes.faa"
        minx = self.s3path.split('.')[0]+f'_min{cutoff}.fa'

        cmd = f'python submit_prodigal_job.py --input {self.s3path} '
        cmd += f'--output {minx} --outgenes {genes} --outfaa {faa}'

        return(cmd)
