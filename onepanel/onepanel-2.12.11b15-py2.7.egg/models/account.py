class Account:
    def __init__(self):
        self.uid = None

    def api_json(self):
        return {
            'uid': self.uid,
        }

    @classmethod
    def from_json(cls, dct):
        account = cls()

        account.uid = dct['uid']

        return account