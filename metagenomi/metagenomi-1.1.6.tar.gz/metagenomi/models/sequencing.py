from metagenomi.models.base import MgObj
# from metagenomi.tasks.cleaning import Cleaning
# from metagenomi.tasks.nonpareil import Nonpareil
# from metagenomi.tasks.sequencing_info import SequencingInfo


class Sequencing(MgObj):
    # Possible tasks:
    # Nonpareil, Bbmap, SequencingInfo
    def __init__(self, mgid, **kwargs):
        MgObj.__init__(self, mgid, **kwargs)

        self.mgtype = 'sequencing'
        self.cleaning = None
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
