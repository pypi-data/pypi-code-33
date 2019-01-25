from metagenomi.models.base import MgObj

class Sample(MgObj):
    # Possible tasks:
    def __init__(self, mgid, **kwargs):
        MgObj.__init__(self, mgid, **kwargs)

        self.mgtype = 'sample'
