from abc import ABCMeta
import json
import pandas as pd

from boto3.dynamodb.conditions import Key

from metagenomi.logger import logger
from metagenomi.db import dbconn
from metagenomi.mgvalidator import MgValidator
from metagenomi.helpers import delete_keys_from_dict


class MgObj:
    '''
    MgObj - base class for all models and tasks
    '''
    __metaclass__ = ABCMeta

    def __init__(self, mgid, check=True, db=dbconn, key=None, **data):

        self.db = db
        self.mgid = mgid  # required
        self.check = check

        if not len(data):
            self.d = self.load(key)  # TODO: what if load fails?
        else:
            self.d = data

        self.not_required = ['dynamodb', 'table', 's3', 'd',
                             'not_required', 'schema', 'db', 'check', ]

        self.schema = {'mgid': {'type': 'mgid', 'required': True}}

        self.validate({'mgid': self.mgid})

    def __str__(self):
        '''
        Default to just dumping data as json
        '''
        # TODO: Decimal() class handling. Cannot dump Decimal() into a json
        return str(json.dumps(self.d))

    # TODO: confirm that
    def to_dict(self, validate=True, clean=True):
        newdict = {}
        for k, v in vars(self).items():
            if k not in self.not_required and v is not None:
                if isinstance(v, list):
                    if v[0].whoami() == 'Mapping':
                        k = 'Mappings'

                    newdict[k] = []
                    for i in v:
                        newdict[k] = newdict[k] + [i.to_dict(
                                                   validate=validate,
                                                   clean=clean)]

                elif isinstance(v, pd.DataFrame):
                    newdict[k] = v.to_dict(orient='list')

                else:
                    try:
                        newdict[v.whoami()] = v.to_dict(validate=validate,
                                                        clean=clean)
                    except AttributeError:
                        newdict[k] = v

        if validate:
            if self.validate(newdict):
                if clean:
                    return delete_keys_from_dict(newdict, ['mgid'])
                return newdict

        if clean:
            return delete_keys_from_dict(newdict, ['mgid'])

        return newdict

    def validate(self, d=None):
        if d is None:
            d = self.to_dict(validate=False, clean=False)

        v = MgValidator(self.schema)
        if v.validate(d):
            return True
        else:
            logger.debug(v.errors)
            raise(ValueError(v.errors))

    # Loads entire model from the database
    def load(self, key):
        k = 'mgid'
        v = self.mgid
        response = self.db.table.query(KeyConditionExpression=Key(k).eq(v))

        if len(response['Items']) > 1:
            e = f'Multiple database entries associated with {v}'
            logger.info(e)
            raise ValueError(e)

        if len(response['Items']) < 1:
            e = f'No database entries associated with {v}'
            logger.info(e)
            raise ValueError(e)

        if key is None:
            return response['Items'][0]
        return response['Items'][0][key]

    def whoami(self):
        return(self.__class__.__name__)
