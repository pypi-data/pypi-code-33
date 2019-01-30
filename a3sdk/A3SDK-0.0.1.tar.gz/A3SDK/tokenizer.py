# coding: utf-8

import json
import os
from uuid import uuid4
import requests
from .log import log


class Tokenizer(object):
    def __init__(self):
        self.is_test = False

    def get_token(self, systemId, **args):
        """
        curl -X POST https://devpfront.a-3.ru/token/api/v1 \
            -H 'content-type: application/json' \
            -d '{
                "systemId": "EXAMPLE",
                "cardNumber": "5500000000000000",
                "cardCVV": "000",
                "cardExp": "1111",
                "cardHolder": "CARD OWNER",
                "orderId": "1"
            }'
        """
        data = {
            "systemId": systemId,
        }
        if args.get('cardNumber'):
            data["cardNumber"] = args.get('cardNumber')
        if args.get('cardCVV'):
            data["cardCVV"] = args.get('cardCVV')
        if args.get('cardExp'):
            data["cardExp"] = args.get('cardExp')
        if args.get('cardHolder'):
            data["cardHolder"] = args.get('cardHolder')
        if args.get('orderId'):
            data["orderId"] = args.get('orderId')
        if args.get('userId'):
            data["userId"] = args.get('userId')

        resource = 'https://pfront.a-3.ru/token/api/v1'
        if self.is_test:
            resource = 'https://devpfront.a-3.ru/token/api/v1'
        res = requests.post(resource, json=data)

        return res.json()
