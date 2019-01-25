from metagenomi.models.base import MgObj
from metagenomi.helpers import to_decimal


class Nonpareil(MgObj):
    def __init__(self, mgid, **kwargs):
        MgObj.__init__(self, mgid, **kwargs)

        self.c = to_decimal(kwargs['C'])
        self.diversity = to_decimal(kwargs['diversity'])
        self.input = kwargs['input']
        self.kappa = kwargs['kappa']
        self.lr = kwargs['lr']
        self.lr_star = to_decimal(kwargs['lr_star'])
        self.modelr = to_decimal(kwargs['modelr'])
        self.output = kwargs['output']
        self.pdf = kwargs['pdf']
        self.tsv = kwargs['tsv']

        self.schema = {**self.schema, **{
            'c': {'type': 'decimal'},
            'diversity': {'required': True, 'type': 'decimal'},
            'input': {'required': True, 'type': 's3object'},
            'kappa': {'required': True, 'type': 'decimal'},
            'lr': {'required': True, 'type': 'decimal'},
            'lr_star': {'required': True, 'type': 'decimal'},
            'modelr': {'required': True, 'type': 'decimal'},
            'output': {'required': True, 'type': 's3path'},
            'pdf': {'required': True, 'type': 's3object'},
            'tsv': {'required': True, 'type': 's3object'}
        }}

    # def write(self):
    #     '''
    #     fill in
    #     '''
    #     # TODO: audra?
    #     key = 'nonpareil_metadata'
    #     value = self.to_dict()
    #
    #     self.write_new(key, value)
