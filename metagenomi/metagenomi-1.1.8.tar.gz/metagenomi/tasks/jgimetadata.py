from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import to_int


class Jgi_metadata(MgTask):
    '''
    TODO: write me
    '''
    def __init__(self, mgid, validate=True, **data):
        MgTask.__init__(self, mgid, **data)

        self.project_name = self.d['project_name']
        self.principal_investigator = self.d['principal_investigator']
        self.scientific_program = self.d['scientific_program']
        self.product_name = self.d['product_name']
        self.status = self.d['status']
        self.status_date = self.d['status_date']
        self.user_program = self.d['user_program']
        self.proposal = self.d['proposal']

        self.jgi_project_id = to_int(self.d['jgi_project_id'])
        self.taxonomy_id = to_int(self.d['taxonomy_id'])
        self.ncbi_project_id = to_int(self.d['ncbi_project_id'])
        self.sequencing_project_id = to_int(self.d['sequencing_project_id'])
        self.analysis_project_id = to_int(self.d['analysis_project_id'])

        self.genbank = self.d['genbank']

        self.ena = self.d['ena']
        self.sra = self.d['sra']

        self.project_manager = self.d['project_manager']
        self.portal_id = self.d['portal_id']
        self.img_portal = self.d['img_portal']

        self.schema = {**self.schema, **{
            "project_name": {'required': True, 'type': 'string'},
            "principal_investigator": {'required': True, 'type': 'string'},
            "scientific_program": {'required': True, 'type': 'string'},
            "product_name": {'required': True, 'type': 'string'},
            "status": {'required': True, 'type': 'string'},
            "status_date": {'required': True, 'type': 'string'},
            "user_program": {'required': True, 'type': 'string'},
            "proposal": {'required': True, 'type': 'string'},
            "jgi_project_id": {'required': True,
                               'type': ['integer', 'nonestring']},
            "taxonomy_id": {'required': True,
                            'type': ['integer', 'nonestring']},
            "ncbi_project_id": {'required': True,
                                'type': ['integer', 'nonestring']},
            "sequencing_project_id": {'required': True,
                                      'type': ['integer', 'nonestring']},
            "analysis_project_id": {'required': True,
                                    'type': ['integer', 'nonestring']},
            "genbank": {'required': True, 'type': 'string'},
            "ena": {'required': True, 'type': 'string'},
            "sra": {'required': True, 'type': 'string'},
            "project_manager": {'required': True, 'type': 'string'},
            "portal_id": {'required': True, 'type': 'string'},
            "img_portal": {'required': True, 'type': 'string'}
            }
        }

        if validate:
            self.validate()
