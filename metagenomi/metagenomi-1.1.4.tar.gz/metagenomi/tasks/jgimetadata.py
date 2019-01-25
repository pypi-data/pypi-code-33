from metagenomi.tasks.taskbase import MgTask


class JgiMetadata(MgTask):
    '''
    TODO: write me
    '''
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)

        self.project_name = data['project_name']
        self.principal_investigator = data['principal_investigator']
        self.scientific_program = data['scientific_program']
        self.product_name = data['product_name']
        self.status = data['status']
        self.status_date = data['status_date']
        self.user_program = data['user_program']
        self.proposal = data['proposal']

        self.jgi_project_id = data['jgi_project_id']
        self.taxonomy_id = data['taxonomy_id']
        self.ncbi_project_id = data['ncbi_project_id']

        self.genbank = data['genbank']

        self.ena = data['ena']
        self.sra = data['sra']
        self.sequencing_project_id = data['sequencing_project_id']
        self.analysis_project_id = data['analysis_project_id']
        self.project_manager = data['project_manager']
        self.portal_id = data['portal_id']
        self.img_portal = data['img_portal']

        self.schema = {**self.schema, **{
            "project_name": {'required': True, 'type': 'string'},
            "principal_investigator": {'required': True, 'type': 'string'},
            "scientific_program": {'required': True, 'type': 'string'},
            "product_name": {'required': True, 'type': 'string'},
            "status": {'required': True, 'type': 'string'},
            "status_date": {'required': True, 'type': 'string'},
            "user_program": {'required': True, 'type': 'string'},
            "proposal": {'required': True, 'type': 'string'},
            "jgi_project_id": {'required': True, 'type': 'string'},
            "taxonomy_id": {'required': True, 'type': 'string'},
            "ncbi_project_id": {'required': True, 'type': 'string'},
            "genbank": {'required': True, 'type': 'string'},
            "ena": {'required': True, 'type': 'string'},
            "sra": {'required': True, 'type': 'string'},
            "sequencing_project_id": {'required': True, 'type': 'string'},
            "analysis_project_id": {'required': True, 'type': 'string'},
            "project_manager": {'required': True, 'type': 'string'},
            "portal_id": {'required': True, 'type': 'string'},
            "img_portal": {'required': True, 'type': 'string'}
            }
        }
