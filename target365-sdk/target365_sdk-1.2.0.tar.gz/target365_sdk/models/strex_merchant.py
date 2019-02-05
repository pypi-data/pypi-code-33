from .model import Model

class StrexMerchant(Model):

    def _accepted_params(self):
        return [
            'merchantId',
            'shortNumberId',
            'password',
        ]
