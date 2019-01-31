from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import to_decimal


class Nonpareil(MgTask):
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid,  **data)

        self.c = to_decimal(self.d['c'])
        self.diversity = to_decimal(self.d['diversity'])
        self.input = self.d['input']
        self.kappa = self.d['kappa']
        self.lr = self.d['lr']
        self.lr_star = to_decimal(self.d['lr_star'])
        self.modelr = to_decimal(self.d['modelr'])
        self.output = self.d['output']
        self.pdf = self.d['pdf']
        self.tsv = self.d['tsv']

        self.schema = {**self.schema, **{
            'c': {'required': True, 'type': 'decimal'},
            'diversity': {'required': True, 'type': 'decimal'},
            'input': {'required': True, 'type': 's3file'},
            'kappa': {'required': True, 'type': 'decimal'},
            'lr': {'required': True, 'type': 'decimal'},
            'lr_star': {'required': True, 'type': 'decimal'},
            'modelr': {'required': True, 'type': 'decimal'},
            'output': {'required': True, 'type': 's3path'},
            'pdf': {'required': True, 'type': 's3file'},
            'tsv': {'required': True, 'type': 's3file'}
        }}

        if self.check:
            self.validate()

    # def write(self):
    #     '''
    #     fill in
    #     '''
    #     # TODO: audra?
    #     key = 'nonpareil_metadata'
    #     value = self.to_dict()
    #
    #     self.write_new(key, value)
