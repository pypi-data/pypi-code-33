import os
import datetime

from boto3.dynamodb.conditions import Key, Attr
from metagenomi.db import (olddb, testdb, dbconn)
from metagenomi.helpers import (to_int, to_decimal, to_latlon)
from metagenomi.helpers import in_db
from metagenomi.tasks.mapping import Mapping
from metagenomi.tasks.assemblystats import AssemblyStats
from metagenomi.tasks.sampleinfo import SampleInfo
from metagenomi.tasks.prodigal import Prodigal
from metagenomi.tasks.nonpareil import Nonpareil
from metagenomi.tasks.cleaning import (QualityTrimming, AdapterRemoval, ContaminantRemoval)
from metagenomi.tasks.sequencinginfo import SequencingInfo

from metagenomi.models.assembly import Assembly
from metagenomi.models.sample import Sample
from metagenomi.models.sequencing import Sequencing

from metagenomi.helpers import download_file

import pandas as pd
import numpy as np


class MgSummary():
    def __init__(self, db=dbconn):
        self.db = db
        self.assemblies = self.scan(filter_key='mgtype',
                                    filter_value='assembly')
        self.samples = self.scan(filter_key='mgtype',
                                 filter_value='sample')
        self.sequencings = self.scan(filter_key='mgtype',
                                     filter_value='sequencing')

    def scan(self, filter_key=None, filter_value=None, comparison='equals'):
        """

        """

        if filter_key and filter_value:
            if comparison == 'equals':
                filtering_exp = Key(filter_key).eq(filter_value)
            elif comparison == 'contains':
                filtering_exp = Attr(filter_key).contains(filter_value)

            response = self.db.table.scan(
                        FilterExpression=filtering_exp)

        else:
            response = self.db.table.scan()

            items = response['Items']
            while True:
                print(len(items))
                if response.get('LastEvaluatedKey'):
                    response = self.db.table.scan(
                                    ExclusiveStartKey=response['LastEvaluatedKey'],
                                    FilterExpression=filtering_exp
                                    )
                    items += response['Items']
                else:
                    break

            return items

    def count_objects(self, mgtype):
        if mgtype == 'assembly':
            items = self.assemblies
        elif mgtype == 'sample':
            items = self.samples
        elif mgtype == 'sequencing':
            items = self.sequencings

        count = {}
        for i in items:
            proj = i['mgproject']
            if proj in count:
                count[proj] = count[proj] + 1
            else:
                count[proj] = 1

        return count

    def count_proteins(self):
        count = {}
        for i in self.assemblies:
            proj = i['mgproject']
            if 'Prodigal' in i:
                if proj in count:
                    count[proj] = count[proj] + i['Prodigal']['proteins_predicted']
                else:
                    count[proj] = count[proj] + i['Prodigal']['proteins_predicted']
            else:
                print(f'Prodigal has not yet been run on {i["mgid"]}')

        return count


# def main():
#
#
# if __name__ == '__main__':
#     main()
