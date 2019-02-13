from .model import Model

class OutMessageStrex(Model):


    def _accepted_params(self):
        return [
            'merchantId',
            'serviceCode',
            'invoiceText',
            'price',
            'billed',
        ]
