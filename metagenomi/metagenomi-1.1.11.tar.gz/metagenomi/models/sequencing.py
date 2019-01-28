from metagenomi.models.modelbase import MgModel
# from metagenomi.tasks.cleaning import Cleaning
# from metagenomi.tasks.nonpareil import Nonpareil
from metagenomi.tasks.sequencinginfo import Sequencing_info
from metagenomi.tasks.nonpareil import Nonpareil


class Sequencing(MgModel):
    # Possible tasks:
    # Nonpareil, Cleaning, Sequencing_info
    def __init__(self, mgid, **data):
        MgModel.__init__(self, mgid, **data)

        self.mgtype = 'sequencing'
        if 'mgtype' in self.d:
            self.mgtype = self.d['mgtype']

        self.sequencing_info = None
        if 'Sequencing_info' in self.d:
            self.assembly_stats = Sequencing_info(
                self.mgid, **self.d['sequencing_info']
                )

        self.nonpareil = None
        if 'Nonpareil' in self.d:
            self.nonpareil = Nonpareil(
                self.mgid, **self.d['Nonpareil']
                )

        # self.cleaning = None

        self.sequencing_info = None
        self.nonpareil = []

        if 'Cleaning' in self.d:
            self.cleaning = self.d['Cleaning']

        if 'SequencingInfo' in self.d:
            self.sequencing_info = self.d['SequencingInfo']
            # self.sequencing_info = SequencingInfo(**self.d['SequencingInfo'])

        if 'Nonpareil' in self.d:
            self.nonpareil = self.d['Nonpareil']
            # self.nonpareil = Nonpareil(**self.d['Nonpareil'])
