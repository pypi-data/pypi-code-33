from abc import ABCMeta
import json
import pandas as pd

from boto3.dynamodb.conditions import Key

from metagenomi.base import MgObj
from metagenomi.logger import logger
from metagenomi.helpers import get_time


class MgTask(MgObj):
    '''
    MgTask - base class for all tasks
    '''
    __metaclass__ = ABCMeta

    def __init__(self, mgid, **data):
        MgObj.__init__(self, mgid, key=self.whoami(), **data)

        self.jobid = self.d.get('jobid', 'None')
        self.updated = get_time()
        self.cmd_run = self.d.get('cmd_run', 'None')
        # self.not_required.append += ['...', ]

        self.schema = {
            **self.schema, **{
                'cmd_run': {'type': 'string', 'required': True, 'minlength': 1},
                'jobid': {'type': 'string', 'required': True, 'minlength': 1},
                'updated': {'type': 'datestring', 'required': True}
            }
        }

    def write(self):
        '''
        Write this opject to the database - over-ridden in other derived
        classes when needed
        '''
        self._create(self.whoami(), self.to_dict(validate=True, clean=True))

    def run(self):
        # Given the appropriate inputs, run the container
        # Implemented in the derived classes
        pass

    def _create(self, key, value):
        response = self.db.table.query(
            KeyConditionExpression=Key('mgid').eq(self.mgid))

        # Add to them
        if len(response['Items']) < 1:
            raise ValueError(f'{self.mgid} does not exist in DB')

        else:
            if key in response['Items'][0]:
                print(f'{key} is already in the DynamoDB, overwriting')

            # TODO: check response?
            response = self.db.table.update_item(
                Key={'mgid': self.mgid},
                UpdateExpression=f"set {key} = :r",
                ExpressionAttributeValues={':r': value},
                ReturnValues="UPDATED_NEW"
            )

    # Internal method only called by base class
    def _update(self, key, value):
        response = self.db.table.query(
            KeyConditionExpression=Key('mgid').eq(self.mgid))
        if len(response['Items']) < 1:
            raise ValueError(f'{self.mgid} does not exist in DB')

        else:
            if key in response['Items'][0]:
                print(f'{key} is already in the DynamoDB')

                # TODO: do something with the result?
                result = self.db.table.update_item(
                    Key={
                        'mgid': self.mgid
                    },
                    UpdateExpression="SET #mg = list_append(#mg, :i)",
                    ExpressionAttributeValues={
                        ':i': [value],
                    },
                    ExpressionAttributeNames={
                     '#mg': key
                     },
                    ReturnValues="UPDATED_NEW"
                )
            else:
                print(f'{key} is not in the DynamoDB, adding...')
                # TODO: do something with the result?
                result = self.db.table.update_item(
                    Key={
                        'mgid': self.mgid
                    },
                    UpdateExpression="SET #mg = :i",
                    ExpressionAttributeValues={
                        ':i': [value],
                    },
                    ExpressionAttributeNames={
                     '#mg': key
                     },
                    ReturnValues="UPDATED_NEW"
                )
