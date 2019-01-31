from metagenomi.models.modelbase import MgModel
# from metagenomi.tasks.cleaning import Cleaning
# from metagenomi.tasks.nonpareil import Nonpareil
from metagenomi.tasks.sequencinginfo import SequencingInfo
from metagenomi.tasks.nonpareil import Nonpareil
from metagenomi.tasks.cleaning import (QualityTrimming, AdapterRemoval, ContaminantRemoval)


class Sequencing(MgModel):
    # Possible tasks:
    # Nonpareil, Cleaning, sequencingInfo
    def __init__(self, mgid, **data):
        MgModel.__init__(self, mgid, **data)

        self.s3path = self.d['s3path']

        self.mgtype = 'sequencing'
        if 'mgtype' in self.d:
            self.mgtype = self.d['mgtype']

        self.sequencing_info = None
        if 'SequencingInfo' in self.d:
            self.assembly_stats = SequencingInfo(
                self.mgid, **self.d['sequencingInfo']
                )

        self.nonpareil = None
        if 'Nonpareil' in self.d:
            self.nonpareil = Nonpareil(
                self.mgid, **self.d['Nonpareil']
                )

        self.sequencing_info = None
        self.nonpareil = []

        if 'QualityTrimming' in self.d:
            self.quality_trimming = QualityTrimming(self.mgid, db=self.db, **self.d['QualityTrimming'])

        if 'AdapterRemoval' in self.d:
            self.adapter_removal = AdapterRemoval(self.mgid, db=self.db, **self.d['AdapterRemoval'])

        if 'ContaminantRemoval' in self.d:
            self.contaminant_removal = ContaminantRemoval(self.mgid, db=self.db, **self.d['ContaminantRemoval'])

        if 'SequencingInfo' in self.d:
            self.sequencing_info = SequencingInfo(self.mgid, db=self.db, **self.d['SequencingInfo'])
            # self.sequencing_info = SequencingInfo(**self.d['SequencingInfo'])

        if 'Nonpareil' in self.d:
            self.nonpareil = Nonpareil(self.mgid, db=seld.db, **self.d['Nonpareil'])
            # self.nonpareil = Nonpareil(**self.d['Nonpareil'])

        self.schema = {**self.schema, **{
            's3path': {'type': 's3file', 'required': True}
            }
        }
