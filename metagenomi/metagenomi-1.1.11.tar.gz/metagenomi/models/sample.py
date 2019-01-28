from metagenomi.models.modelbase import MgObj


class Sample(MgObj):
    # Possible tasks:
    def __init__(self, mgid, **data):
        MgObj.__init__(self, mgid, **data)

        self.mgtype = 'sample'
