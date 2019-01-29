from abc import ABCMeta

from boto3.dynamodb.conditions import Key

from metagenomi.base import MgObj
from metagenomi.logger import logger
from metagenomi.helpers import get_time


class MgModel(MgObj):
    '''
    MgModel - base class for all models
    '''
    __metaclass__ = ABCMeta

    def __init__(self, mgid, **data):
        MgObj.__init__(self, mgid, **data)

        # If data not passed, object is loaded in the MgObj base class
        self.associated = self.d['associated']

        if 'created' in self.d:
            self.created = self.d['created']
        else:
            self.created = get_time()

        self.s3path = self.d['s3path']

        if 'mgproject' in self.d:
            self.mgproject = self.d['mgproject'].upper()
        else:
            self.mgproject = self.mgid[:4].upper()

        self.schema = {
            **self.schema, **{
                'mgtype': {'type': 'string', 'required': True,
                           'allowed': ['sequencing', 'assembly', 'sample']},
                's3path': {'type': 's3file', 'required': True},
                'associated': {'type': 'dict', 'required': True, 'schema': {
                    'sequencing': {'type': 'list', 'schema': {'type': 'mgid'}},
                    'assembly':  {'type': 'list', 'schema': {'type': 'mgid'}},
                    'sample':  {'type': 'list', 'schema': {'type': 'mgid'}},
                    }
                },
                'created': {'type': 'datestring', 'required': True},
                'mgproject': {'type': 'string', 'required': True,
                              'maxlength': 4, 'minlength': 4}
            }
        }

    def write(self, force=False, ignore_exceptions=True):
        '''
        Write this object to the database - over-ridden in other derived
        classes when needed
        '''
        # Delete 'mgid' from task documents after validation
        # dict = self.to_dict()
        # calidate
        # remove mgid

        d = self.to_dict(validate=True, clean=True)
        # Add it back in at the appropriate spot
        d['mgid'] = self.mgid

        response = self.db.table.query(
            KeyConditionExpression=Key('mgid').eq(self.mgid))

        if len(response['Items']) < 1:
            # new document
            response = self.db.table.put_item(
                Item=d
            )
            # TODO: validate we got a good response from db
            logger.info(f'Wrote {response} to db')

        else:
            if force:
                response = self.db.table.put_item(
                    Item=d
                )
                # TODO: validate we got a good response from db
                logger.info(f'Wrote {response} to db')
            else:
                msg = f'{self.mgid} is already in DB - cannot re-write'
                logger.debug(msg)
                if ignore_exceptions:
                    print(f'WARNING: {msg}')
                else:
                    raise ValueError(msg)
